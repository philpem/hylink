"""

ADK Repeater Interface

Socket protocol helper

TODO: Implement retry timer for HSTRPToRadio (dispatch -> radio message)
    The radio should ack these. Keep retrying every {T} seconds until it does, or until {R} retries
    (e.g. 2 seconds and 5 retries)

TODO: Review the log messages, log switches and other debugging code. Aim to reduce the log spam a bit.

TODO: Keep track of more than one repeater -- track them via Radio ID or IP address.
    Will need to refactor the socket interface to manage the state of more than one repeater.
    Possibly add a RepeaterConnection class on top of

TODO: Higher-level repeater interface to sit on top of this (and make programming easier and more Pythonic)

"""

import os
import queue
import socket
import select
import threading

from .packet import *
from .rtp import RTPPacket

log = logging.getLogger(__name__)

# Log packets being tx'd/rx'd
LOG_PACKET_RX = False
LOG_PACKET_TX = False
# Log heartbeats
LOG_HEARTBEATS = False
# Log non-SYN packets in DISCONNECTED state
LOG_NONSYN = False


# Terminate the connection if there are no packets received in this amount of time (seconds)
HEARTBEAT_TIMEOUT = 30

# Interval (in seconds) between heartbeats
HEARTBEAT_INTERVAL = 2


class Watchdog(object):
    """ Watchdog timer """

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

        # Initialise default ACK timeout
        self.ackTimeout = 2

        # Initialise callbacks
        self._rcpRxCallback = None
        self._rtpRxCallback = None

        # Create a pipe to use for killing the rx thread
        self._r_pipe, self._w_pipe = os.pipe()

        # Create the transmit queue
        self._txqueue = queue.Queue()

        # Create the ack queue and callback table
        self._ackqueue = queue.Queue()
        self._ackcallbacks = {}

        # Open the socket
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((host, port))

        # Set up the Heartbeat timer
        self._wdt = Watchdog(HEARTBEAT_TIMEOUT, self._heartbeatExpired)

        # Create and start the receive and transmit threads
        self._running = False
        self._rxthread = threading.Thread(target=self._rxThreadProc, name="%s-rx.%d" % (name, port))
        self._txthread = threading.Thread(target=self._txThreadProc, name="%s-tx.%d" % (name, port))
        self._rxthread.start()
        self._txthread.start()

    def isConnected(self):
        """ Returns true if the repeater is connected, otherwise false """
        return self._repeaterAddr is not None

    def send(self, packet, callback=None):
        """ Send a packet to the repeater """
        if packet is None:
            raise ValueError("Cannot send a null packet")

        # Is this an RTP packet?
        if isinstance(packet, RTPPacket):
            # RTP packet -- send as is. Doesn't require acknowledgement.
            self._txqueue.put(packet)
            return None

        # Will this packet result in an acknowledgement?
        ackReq = False
        if isinstance(packet, HSTRPToRadio):
            ackReq = True

        # Hytera form packet -- update the sequence ID
        packet.hytSeqID = self._getSeq()
        # If ack callback is needed, store it in the sequence list
        if ackReq and (callback is not None):
            self._ackcallbacks[packet.hytSeqID] = callback
        # Send the packet
        self._txqueue.put(packet)

        # If this is a blocking operation -- wait for the ack
        if ackReq and (callback is None):
            # Wait for the Ack
            ackn = self.waitAck(self.ackTimeout)
            log.debug("  Blocking send acknowledged, sent seq=%d, ack=%d" % (packet.hytSeqID, ackn))
            # TODO validate the sequence number of the acknowledgement

        return packet.hytSeqID

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

    # Shutdown method is from:
    # https://stackoverflow.com/questions/7449247/how-do-i-abort-a-socket-recvfrom-from-another-thread-in-python

    def _getSeq(self):
        """ Get the sequence ID then increment it """
        x = self._seq
        self._seq = (self._seq + 1) & 0xFFFF
        return x

    def _txThreadProc(self):
        """ Transmit thread function """
        log.debug("TxThread running")

        while True:
            try:
                p = self._txqueue.get(timeout=HEARTBEAT_INTERVAL)
            except queue.Empty:
                # Queue was empty for HEARTBEAT_INTERVAL, transmit a Heartbeat instead (but only if connected)
                # This means a packet will be sent at least once every HEARTBEAT_INTERVAL to keep the connection alive.
                if self._repeaterAddr is not None:
                    p = HSTRPHeartbeat()
                else:
                    # Repeater not connected, don't send a heartbeat!
                    continue

            # If there was a null/None in the queue, exit the loop and shut down the thread
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
        """ Receive thread function """
        self._running = True

        log.debug("RxThread running")

        while self._running:
            # Trigger on either a byte in the pipe or a received packet.
            # The data in the pipe is ignored, but _running will be False so the 'continue' breaks us out of the loop.
            read, _w, errors = select.select([self._r_pipe, self._sock], [], [self._sock])
            if self._sock not in read:
                continue

            # Receive a packet
            data, addr = self._sock.recvfrom(1024)
            if data is None or len(data) == 0:
                log.warning("Null Packet received -- %s from %s" % (data, addr))
                continue

            # noinspection PyBroadException
            try:
                p = HYTPacket.decode(data)
            except HYTBadSignature:
                # Bad Signature -- try to decode as RTP
                # TODO - check if the radio is advertising RTP support for this port
                p = RTPPacket(data)
                log.debug("RTP packet received, %s" % p)

                # Pass it onto the RTP callback, if any
                if self._rtpRxCallback is not None:
                    self._rtpRxCallback(p)
            except:
                # Garbage packet. Log it, then carry on
                log.exception('Exception in receive packet hander')
                log.error('Packet data for preceding exception: { %s }' % ' '.join(['%02X' % x for x in data]))
                continue

            if LOG_PACKET_RX:
                if (not isinstance(p, (HSTRPHeartbeat, HSTRPSyn, HSTRPAck))) or LOG_HEARTBEATS:
                    log.debug("Packet received, addr='%s', data=%s" % (addr, p))

            # Non-SYN packet while disconnected? If so, ignore it.
            if self._repeaterAddr is None and not isinstance(p, HSTRPSyn) and LOG_NONSYN:
                log.warning("Ignored non-SYN packet while disconnected: %s" % p)
                continue

            # Is this a SYN?
            if isinstance(p, HSTRPSyn):
                log.debug("SYN... Repeater is id %d, sockaddr %s" % (p.rptHeader.synRepeaterRadioID, addr))

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

                # If we have an app crash and restart, the repeater will keep sending
                # us Heartbeats, expecting us to reciprocate.
                # As we don't know the repeater's identity (which is in the SYN)
                # we ignore it until it times out and reverts to sending SYNs.

                if self._repeaterAddr is not None:
                    if LOG_HEARTBEATS:
                        log.debug("   Heartbeat/keepalive received.")

            # Is this an acknowledgement?
            elif isinstance(p, HSTRPAck):
                # Is there an ACK callback registered for this sequence ID?
                if p.hytSeqID in self._ackcallbacks:
                    # Callback registered, call it and remove it from the list
                    self._ackcallbacks[p.hytSeqID](p.hytSeqID)
                    del self._ackcallbacks[p.hytSeqID]
                else:
                    # No callback, put the ack in the queue (for waitAck)
                    self._ackqueue.put(p.hytSeqID)

            # Is this a message from the radio?
            elif isinstance(p, HSTRPFromRadio):
                # Don't ack the message if the repeater is not connected
                if self._repeaterAddr is not None:
                    # Acknowledge the message
                    ack = HSTRPAck()
                    ack.hytSeqID = p.hytSeqID
                    self._txqueue.put(ack)
                else:
                    # Repeater not connected, discard the message
                    log.debug("RX: Discarded packet (repeater not connected): %s" % p)
                    continue

                # Pass the message onto the callback if there is one
                if self._rcpRxCallback is not None:
                    self._rcpRxCallback(p)
                else:
                    log.info("RX: No callback registered for packet: %s" % p)

            # Some other packet type?
            else:
                log.warning("Rx packet, unrecognised: %s" % p)

            # Start/Reset the watchdog timer (rx'd packet)
            self._wdt.reset()

        log.info("RxThread shutting down...")

    def waitAck(self, timeout=None):
        """
        Wait for the next acknowledgement in the queue and return it

        Timeout = None is a blocking operation (returns when an ACK is received)
        Timeout = 0 is nonblocking (returns immediately)
        Timeout > 0 is blocking, with a timeout
        """
        if timeout is None or timeout > 0:
            return self._ackqueue.get(timeout=timeout)
        elif timeout == 0:
            return self._ackqueue.get(block=False)
        else:
            raise ValueError("Invalid timeout value, must be None or >= 0")

    def setMsgCallback(self, callback):
        """
        Set the broadcast callback.

        The receive callback is called whenever the repeater sends a broadcast
        or other unsolicited RCP packet (HSTRPFromRadio type).

        The callback should be defined as:

          def callback(packet):

        "packet" is the HSTRPFromRadio packet.
        """
        self._rcpRxCallback = callback

    def setRTPCallback(self, callback):
        """
        Set the RTP callback.

        The RTP callback is called whenever a packet of RTP audio data is
        received.

        The callback should be defined as:

          def callback(packet):

        "packet" is an rtp.RTPPacket instance.
        """
        self._rtpRxCallback = callback

