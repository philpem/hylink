#!/usr/bin/env python3

import dpkt
import sys
import socket
from hylink.packet import *
from hylink.exceptions import *
from hylink.ports import ADKDefaultPorts


# Suppress heartbeat packets
SUPPRESS_HEARTBEATS = True


# configure logging
logging.basicConfig(format='%(asctime)s [%(levelname)-7s] (%(threadName)s) %(message)s', level=logging.DEBUG)


def inet_to_str(inet):
    """Convert inet object to a string
        Args:
            inet (inet struct): inet network address
        Returns:
            str: Printable/readable IP address
    """
    # First try ipv4 and then ipv6
    try:
        return socket.inet_ntop(socket.AF_INET, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET6, inet)


if len(sys.argv) < 2:
    print("PCap reader for PyADK\n\n" +
          "Syntax:\n" +
          "\tptest.py <pcapfile>\n\n" +
          "Reads a Pcap packet trace from a file and plays it through PyADK.\n")
    sys.exit(1)


# Load pcap dump
pcap = dpkt.pcapng.Reader(open(sys.argv[1], 'rb'))

for ts, buf in pcap:
    # unpack the Ethernet frame
    eth = dpkt.ethernet.Ethernet(buf)

    # make sure the Ethernet frame contains an IP packet
    if not isinstance(eth.data, dpkt.ip.IP):
        continue

    # grab the data in the IP frame
    ip = eth.data

    # is this a UDP frame?
    if not isinstance(ip.data, dpkt.udp.UDP):
        print(ts, "Not UDP -- is %s" % eth.data.__class__.__name__)
        continue

    # unpack the UDP frame
    udp = ip.data

    try:
        # feed the packet to the decoder
        h = HYTPacket.decode(udp.data)

        if SUPPRESS_HEARTBEATS and isinstance(h, HSTRPHeartbeat):
            continue

        print('%15s:%5s(%-6s) %s' % (inet_to_str(ip.src), udp.dport, ADKDefaultPorts(udp.dport).name, h))
    except HYTBadSignature:
        # print('%15s:%5s %s   !!!BAD_SIG  d=%s' % (inet_to_str(ip.src), udp.dport, '???', ' '.join(['%02X'%x for x in udp.data])))
        pass

