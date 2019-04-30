#!/usr/bin/env python3

import socket
import threading
import logging

from HyteraADK.packet import *


class ADKSocket(object):

    def __init__(self, name="ADKSocket", port=30007, host=''):
        self.__seq = 0

        # Open the socket
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind((host, port))

        # Start the receive thread
        self.__rxthread = threading.Thread(target=self.__rxThreadProc, name="%s-rx.%d" % (name,port))
        self.__rxthread.start()

    def __txThreadProc(self):


    def __rxThreadProc(self):
        l = logging.getLogger("ADKSocket.rxThreadProc")

        # state = "waiting for SYN"
        state = 0

        # Wait for announcement
        l.debug("RxThread running")
        while True:
            # Receive a packet
            data,addr = self.__sock.recvfrom(1024)
            p = HYTPacket.decode(data)
            l.debug("Packet received, addr='%s', data=%s" % (addr, p))

            # Is this a SYN?


logging.basicConfig(format='%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s', level=logging.DEBUG)

s = ADKSocket()


import time
time.sleep(120)

"""
p = HYTPacket()

# print the packet
print(p)
# print the bytes
print(bytes(p))
# convert bytes back into a packet
print(HYTPacket(bytes(p)))
"""

"""
p = HYTAnnounce()
print(bytes(p))
print(p)
"""

d = b'\x32\x42\x00\x24\x00\x00\x83\x04\x00\x01\x86\x9F\x04\x01\x01\x00\x00\x00'
p = HYTPacket.decode(d)

print(p)
print(' '.join(['%02X'%x for x in p.hytPayload]))

print()

p = HYTPacket.decode(bytearray.fromhex('324200050100'))
print(p)
print(' '.join(['%02X'%x for x in p.hytPayload]))

