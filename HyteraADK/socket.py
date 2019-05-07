import logging
import os
import queue
import socket
import select
import threading

from .packet import *

log = logging.getLogger(__name__)


# Log packets being tx'd/rx'd
LOG_PACKET_RX = True
LOG_PACKET_TX = False
# Log heartbeats
LOG_HEARTBEATS = False
# Log non-SYN packets in DISCONNECTED state
LOG_NONSYN = False

HEARTBEAT_TIMEOUT = 30  # seconds

class Watchdog(object):
    def __init__(self, timeout, userHandler=None):  # timeout in seconds
        """ Create a Watchdog Timer """
        self.timeout = timeout
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = threading.Timer(self.timeout, self.handler)

    def reset(self):
        """ Restart the timer """
        self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self.handler)
        self.timer.start()

    def stop(self):
        """ Stop the watchdog """
        self.timer.cancel()

    def defaultHandler(self):
        """ Default watchdog handler """
        raise self


class ADKSocket(object):

    def __init__(self, port, name="ADKSocket", host=''):
        # Initialise sequence ID and repeater ID
        self._seq = 0
        self._repeaterAddr = None

        # Create a pipe to use for killing the rx thread
        self._r_pipe, self._w_pipe = os.pipe()

        # Create the transmit queue
        self._txqueue = queue.Queue()

        # Open the socket
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((host, port))

        # Set up the Heartbeat timer
        self._wdt = Watchdog(HEARTBEAT_TIMEOUT, self._heartbeatExpired)

        # Create and start the receive and transmit threads
        self._rxthread = threading.Thread(target=self._rxThreadProc, name="%s-rx.%d" % (name,port))
        self._txthread = threading.Thread(target=self._txThreadProc, name="%s-tx.%d" % (name,port))
        self._rxthread.start()
        self._txthread.start()


    def isConnected(self):
        """ Returns true if the repeater is connected, otherwise false """
        return self._repeaterAddr is not None


    def send(self, packet):
        """ Send a packet to the repeater and wait for a reply """
        if packet is None:
            raise ValueError("Cannot send a null packet")
        packet.hytSeqID = self._getSeq()
        self._txqueue.put(packet)


    def _heartbeatExpired(self):
        """
        Called by the Watchdog task when we haven't received a packet in a while.
        """
        log.error("WATCHDOG: No packets in %d seconds -- disconnecting" % HEARTBEAT_TIMEOUT)
        self._repeaterAddr = None


    def stop(self):
        """ Shut down the tx/rx threads """
        # Stop the watchdog timer
        self._wdt.stop()

        # Shut down the tx thread
        self._txqueue.put(None)

        # Shut down the rx thread and join it
        self._running = False
        os.write(self._w_pipe, "I".encode())    # data isn't important
        self._rxthread.join()

    # FIXME Shutdown method is a bit of a faff. Twisted might work better, see:
    #    https://stackoverflow.com/questions/2912245/python-how-to-close-a-udp-socket-while-is-waiting-for-data-in-recv
    #    https://twistedmatrix.com/documents/current/core/howto/udp.html
    #
    # For now we use a pipe, see https://stackoverflow.com/questions/7449247/how-do-i-abort-a-socket-recvfrom-from-another-thread-in-python

    def _getSeq(self):
        """ Get the sequence ID then increment it """
        x = self._seq
        self._seq = (self._seq + 1) & 0xFFFF
        return x


    def _txThreadProc(self):
        log.debug("TxThread running")

        while True:
            p = self._txqueue.get()

            # Quit if there was a null/None in the queue
            if p is None:
                break

            # Don't allow send if we're not connected to the repeater
            if self._repeaterAddr is None:
                log.warning("Can't send -- not connected to repeater. packet=%s" % p)
                continue

            if LOG_PACKET_TX:
                log.debug("Packet send: %s" % p)

            # Send the packet
            self._sock.sendto(bytes(p), self._repeaterAddr)

        log.info("TxThread shutting down...")


    def _rxThreadProc(self):
        self._running = True

        log.debug("RxThread running")

        while self._running:
            # trigger on either a byte in the pipe or a received packet
            # if no packet is received, go around again. If we're exiting,
            # then self._running won't be set.
            read, _w, errors = select.select([self._r_pipe, self._sock], [], [self._sock])
            if self._sock not in read:
                continue

            # Receive a packet
            data,addr = self._sock.recvfrom(1024)
            if data is None or len(data) == 0:
                log.warn("Null Packet received -- %s from %s" % (data, addr))
                continue
            p = HYTPacket.decode(data)
            if LOG_PACKET_RX:
                if (not isinstance(p, HSTRPHeartbeat) and not isinstance(p, HSTRPSyn)) or LOG_HEARTBEATS:
                    log.debug("Packet received, addr='%s', data=%s" % (addr, p))

            # Non-SYN packet while disconnected? If so, ignore it.
            if self._repeaterAddr is None and not isinstance(p, HSTRPSyn) and LOG_NONSYN:
                log.warning("Ignored non-SYN packet while disconnected: %s" % p)
                continue

            # Is this a SYN?
            if isinstance(p, HSTRPSyn):
                log.debug("SYN... Repeater is id %d, sockaddr %s" % (p.synRepeaterRadioID, addr))

                # Save the repeater address
                self._repeaterAddr = addr

                # SYN means we need to reset the sequence id
                self._seq = p.hytSeqID

                # Acknowledge the SYN with a SYN-ACK
                p = HSTRPSynAck()
                p.hytSeqID = self._getSeq()
                self._txqueue.put(p)

                # At this point, the repeater will begin sending Heartbeat messages
                #
                # The repeater will give up and go back to sening SYNs when
                # it's sent ten heartbeats on a 6-sec interval, without
                # receiving a heartbeat from us.

            # Is this a Heartbeat?
            elif isinstance(p, HSTRPHeartbeat):
                # Sequence ID always seems to be zero

                # TODO flag the connection as "alive" and reset the connection-death timer?
                #       (death timer expiry: disconnect repeater and mark as disconnected)

                # If we have an app crash and restart, the repeater will keep sending
                # us Heartbeats, expecting us to reciprocate.
                # As we don't know the repeater's identity (which is in the SYN)
                # we ignore it until it times out and reverts to sending SYNs.

                if self._repeaterAddr is not None:
                    # Respond to a heartbeat with a heartbeat
                    if LOG_HEARTBEATS:
                        log.debug("   Heartbeat received, responding with a heartbeat...")
                    p = HSTRPHeartbeat()
                    p.hytSeqID = 0      # Heartbeats always have a zero sequence ID
                    self._txqueue.put(p)

            # Some other packet type?
            else:
                log.warn("Rx packet, unrecognised: %s" % p)

            # Start/Reset the watchdog timer (rx'd packet)
            self._wdt.reset()

        log.info("RxThread shutting down...")

