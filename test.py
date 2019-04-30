#!/usr/bin/env python3

import logging
import os
import queue
import select
import socket
import threading

from HyteraADK.packet import *

log = logging.getLogger(__name__)


HEARTBEAT_TIMEOUT = 30  # seconds


class Watchdog(object):
    def __init__(self, timeout, userHandler=None):  # timeout in seconds
        """ Create a Watchdog Timer """
        self.timeout = timeout
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = threading.Timer(self.timeout, self.handler)

    def start(self):
        """ Start the Watchdog Timer """
        self.timer.start()

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

    def __init__(self, name="ADKSocket", port=30007, host=''):
        # Initialise sequence ID and repeater ID
        self.__seq = 0
        self.__repeaterAddr = None

        # Create a pipe to use for killing the rx thread
        self._r_pipe, self._w_pipe = os.pipe()

        # Create the transmit queue
        self.__txqueue = queue.Queue()

        # Open the socket
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind((host, port))

        # Set up the Heartbeat timer
        self._wdt = Watchdog(HEARTBEAT_TIMEOUT, self.heartbeatExpired)

        # Create and start the receive and transmit threads
        self.__rxthread = threading.Thread(target=self.__rxThreadProc, name="%s-rx.%d" % (name,port))
        self.__txthread = threading.Thread(target=self.__txThreadProc, name="%s-tx.%d" % (name,port))
        self.__rxthread.start()
        self.__txthread.start()


    def heartbeatExpired(self):
        """
        Called by the Watchdog task when we haven't received a packet in a while.
        """
        log.error("WATCHDOG: No packets in %d seconds -- disconnecting" % HEARTBEAT_TIMEOUT)
        self.__repeaterAddr = None


    def stop(self):
        """ Shut down the tx/rx threads """
        # Stop the watchdog timer
        self._wdt.stop()

        # Shut down the tx thread
        self.__txqueue.put(None)

        # Shut down the rx thread and join it
        self.__running = False
        os.write(self._w_pipe, "I".encode())    # data isn't important
        self.__rxthread.join()

    # FIXME Shutdown method is a bit of a faff. Twisted might work better, see:
    #    https://stackoverflow.com/questions/2912245/python-how-to-close-a-udp-socket-while-is-waiting-for-data-in-recv
    #    https://twistedmatrix.com/documents/current/core/howto/udp.html
    #
    # For now we use a pipe, see https://stackoverflow.com/questions/7449247/how-do-i-abort-a-socket-recvfrom-from-another-thread-in-python

    def __getSeq(self):
        """ Get the sequence ID then increment it """
        x = self.__seq
        self.__seq += 1
        return x


    def __txThreadProc(self):
        log.debug("TxThread running")

        while True:
            p = self.__txqueue.get()

            # Quit if there was a null/None in the queue
            if p is None:
                break

            # Don't allow send if we're not connected to the repeater
            if self.__repeaterAddr is None:
                log.warning("Can't send -- not connected to repeater. Packet dropped.")
                continue

            log.debug("TxThread send: %s" % p)

            # Send the packet
            self.__sock.sendto(bytes(p), self.__repeaterAddr)

        log.info("TxThread shutting down...")


    def __rxThreadProc(self):
        self.__running = True

        log.debug("RxThread running")

        while self.__running:
            # trigger on either a byte in the pipe or a received packet
            # if no packet is received, go around again. If we're exiting,
            # then self.__running won't be set.
            read, _w, errors = select.select([self._r_pipe, self.__sock], [], [self.__sock])
            if self.__sock not in read:
                continue

            # Receive a packet
            data,addr = self.__sock.recvfrom(1024)
            if data is None or len(data) == 0:
                log.warn("Null Packet received -- %s from %s" % (data, addr))
                continue
            p = HYTPacket.decode(data)
            log.debug("Packet received, addr='%s', data=%s" % (addr, p))

            # Is this a SYN?
            if isinstance(p, HSTRPSyn):
                log.debug("SYN... Repeater is id %d, sockaddr %s" % (p.synRepeaterRadioID, addr))

                # Save the repeater address
                self.__repeaterAddr = addr

                # SYN means we need to reset the sequence id
                self.__seq = p.hytSeqID

                # Acknowledge the SYN with a SYN-ACK
                log.debug("   Sending SynAck...")
                p = HSTRPSynAck()
                p.hytSeqID = self.__getSeq()
                self.__txqueue.put(p)

                # At this point, the repeater will begin sending Heartbeat messages
                #
                # The repeater will give up and go back to sening SYNs when
                # it's sent ten heartbeats on a 6-sec interval, without
                # receiving a heartbeat from us.

                # Start the heartbeat watchdog
                self._wdt.start()

            # Is this a Heartbeat?
            elif isinstance(p, HSTRPHeartbeat):
                # Sequence ID always seems to be zero

                # TODO flag the connection as "alive" and reset the connection-death timer?
                #       (death timer expiry: disconnect repeater and mark as disconnected)

                # If we have an app crash and restart, the repeater will keep sending
                # us Heartbeats, expecting us to reciprocate.
                # As we don't know the repeater's identity (which is in the SYN)
                # we ignore it until it times out and reverts to sending SYNs.

                # Don't respond to heartbeats if we're not connected
                if self.__repeaterAddr is None:
                    log.info("   Heartbeat ignored, not connected")
                    continue

                # Respond to a heartbeat with a heartbeat
                log.debug("   Heartbeat received, responding with a heartbeat...")
                p = HSTRPHeartbeat()
                p.hytSeqID = 0      # FIXME really zero?
                self.__txqueue.put(p)

            # Reset the watchdog timer (rx'd packet)
            self._wdt.reset()

        log.info("RxThread shutting down...")

logging.basicConfig(format='%(asctime)s [%(levelname)-7s] (%(threadName)s) %(message)s', level=logging.DEBUG)

s = ADKSocket()


import time
time.sleep(60)

logging.info("Shutting down...")

s.stop()

