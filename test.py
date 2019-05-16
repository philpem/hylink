#!/usr/bin/env python3

from HyteraADK.ports import ADKDefaultPorts
from HyteraADK.socket import ADKSocket
from HyteraADK.packet import *
from HyteraADK.types import *


if __name__ == '__main__':

    # configure logging
    logging.basicConfig(format='%(asctime)s [%(levelname)-7s] (%(threadName)s) %(message)s', level=logging.DEBUG)

    socks = {}
    for p in ADKDefaultPorts:
        # start ADK socket server
        socks[p] = ADKSocket(port=p)

    # run for a while
    import time
    time.sleep(20)

    # send txctrl call request
    htc = HSTRPToRadio()
    htc.txCtrl = RCPCallRequest()
    htc.txCtrl.callType = CallType.PRIVATE
    htc.txCtrl.destId = 1234
    socks[ADKDefaultPorts.RCP1].send(htc)

    time.sleep(10)

    logging.info("Shutting down...")

    for s in socks:
        socks[s].stop()

