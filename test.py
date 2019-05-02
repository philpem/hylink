#!/usr/bin/env python3

import logging

#from HyteraADK.packet import *
from HyteraADK.ports import ADKDefaultPorts
from HyteraADK.socket import ADKSocket


if __name__ == '__main__':

    # configure logging
    logging.basicConfig(format='%(asctime)s [%(levelname)-7s] (%(threadName)s) %(message)s', level=logging.DEBUG)

    # start ADK socket server
    s = ADKSocket(port = ADKDefaultPorts.RCP1)

    # run for 60 seconds and stop
    import time
    time.sleep(60*10)

    logging.info("Shutting down...")

    s.stop()

