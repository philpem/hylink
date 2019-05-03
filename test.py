#!/usr/bin/env python3

import logging

#from HyteraADK.packet import *
from HyteraADK.ports import ADKDefaultPorts
from HyteraADK.socket import ADKSocket


if __name__ == '__main__':

    # configure logging
    logging.basicConfig(format='%(asctime)s [%(levelname)-7s] (%(threadName)s) %(message)s', level=logging.DEBUG)

    socks = {}
    for p in ADKDefaultPorts:
        # start ADK socket server
        socks[p] = ADKSocket(port = p)

    # run for 60 seconds and stop
    import time
    time.sleep(90)

    logging.info("Shutting down...")

    for s in socks:
        socks[s].stop()

