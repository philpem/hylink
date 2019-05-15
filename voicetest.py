#!/usr/bin/env python3

import logging
import time

#from HyteraADK.packet import *
from HyteraADK.ports import ADKDefaultPorts
from HyteraADK.socket import ADKSocket
from HyteraADK.packet import *
from HyteraADK.types import *


if __name__ == '__main__':

    # configure logging
    logging.basicConfig(format='%(asctime)s [%(levelname)-7s] (%(threadName)s) %(message)s', level=logging.DEBUG)

    """
    socks = {}
    for p in ADKDefaultPorts:
        # start ADK socket server
        socks[p] = ADKSocket(port = p)
    """

    # Start RCP and RTP for Slot 1
    rtpPort = ADKSocket(ADKDefaultPorts.RTP1)
    rcpPort = ADKSocket(ADKDefaultPorts.RCP1)


    # run for a while (TODO - wait for connection)
    logging.info("Waiting for repeater connection")
    time.sleep(90)


    # send txctrl call request
    logging.info("Sending Call request...")
    htc = HSTRPToRadio()
    htc.txCtrl = RCPCallRequest()
    htc.txCtrl.callType = CallType.PRIVATE
    htc.txCtrl.destId = 1234
    rcpPort.send(htc)


    logging.info("Keying up...")
    htcButton = HSTRPToRadio()
    htcButton.txCtrl = RCPButtonRequest()
    htcButton.txCtrl.pttTarget = ButtonTarget.FRONT_PTT
    htcButton.txCtrl.pttOperation = ButtonOperation.PRESS
    rcpPort.send(htcButton)

    logging.info("Waiting for a while...")
    time.sleep(10)


    logging.info("Keying down...")
    htcButton.txCtrl.pttOperation = ButtonOperation.RELEASE
    rcpPort.send(htcButton)

    logging.info("Shutting down...")

    rcpPort.stop()
    rtpPort.stop()

