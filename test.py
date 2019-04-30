#!/usr/bin/env python3

import logging
import queue
import socket
import threading

from HyteraADK.packet import *

log = logging.getLogger(__name__)

class ADKSocket(object):

    def __init__(self, name="ADKSocket", port=30007, host=''):
        # Initialise sequence ID and repeater ID
        self.__seq = 0
        self.__repeaterAddr = None

        # Create the transmit queue
        self.__txqueue = queue.Queue()

        # Open the socket
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind((host, port))

        # TODO heartbeat timer

        # Create and start the receive and transmit threads
        self.__rxthread = threading.Thread(target=self.__rxThreadProc, name="%s-rx.%d" % (name,port))
        self.__txthread = threading.Thread(target=self.__txThreadProc, name="%s-tx.%d" % (name,port))
        self.__rxthread.start()
        self.__txthread.start()


    def stop(self):
        """ Shut down the tx/rx threads """
        # Shut down the tx thread
        self.__txqueue.put(None)

        # Shut down the rx thread and join it
        self.__running = False
        self.__sock.close()
        self.__rxthread.join()


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
                log.info("TxThread received None, shutting down...")
                break

            # Don't allow send if we're not connected to the repeater
            if self.__repeaterAddr is None:
                log.warning("Can't send -- not connected to repeater. Packet dropped.")
                continue

            log.debug("TxThread send: %s" % p)

            # Send the packet
            self.__sock.sendto(bytes(p), self.__repeaterAddr)


    def __rxThreadProc(self):
        self.__running = True

        log.debug("RxThread running")

        while self.__running:
            # Receive a packet
            data,addr = self.__sock.recvfrom(1024)
            p = HYTPacket.decode(data)
            log.debug("Packet received, addr='%s', data=%s" % (addr, p))

            # TODO reset the disconnect timer

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

            # Is this a Heartbeat?
            elif isinstance(p, HSTRPHeartbeat):
                # Sequence ID always seems to be zero
                # TODO flag the connection as "alive" and reset the connection-death timer?
                #       (death timer expiry: disconnect repeater and mark as disconnected)

                # FIXME If we have an app crash and restart, the repeater will keep sending
                #       us Heartbeats, expecting us to reciprocate. We should ignore them
                #       here until the repeater gives up and goes back to sending SYNs

                # Don't respond to heartbeats if we're not connected
                if self.__repeaterAddr is None:
                    log.info("Heartbeat ignored, not connected")
                    break

                # Respond to a heartbeat with a heartbeat
                log.debug("   Heartbeat received, responding with a heartbeat...")
                p = HSTRPHeartbeat()
                p.hytSeqID = 0      # FIXME really zero?
                self.__txqueue.put(p)


logging.basicConfig(format='%(asctime)s [%(levelname)-7s] (%(threadName)s) %(message)s', level=logging.DEBUG)

s = ADKSocket()


import time
time.sleep(60)

logging.info("Shutting down...")

s.stop()

