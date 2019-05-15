#!/usr/bin/env python3

import logging
import queue
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


    # run for a while
    # TODO -- packet -- make this event driven (wait on an event queue)
    logging.info("Waiting for repeater connection")
    while (not rtpPort.isConnected()) or (not rcpPort.isConnected()):
        time.sleep(2)
    logging.info("Repeater connected!")


    # send txctrl call request
    logging.info("Sending Call request...")
    htc = HSTRPToRadio()
    htc.txCtrl = RCPCallRequest()
    htc.txCtrl.callType = CallType.PRIVATE
    htc.txCtrl.destId = 1234
    seqn = rcpPort.send(htc)


    logging.info("Keying up...")
    htcButton = HSTRPToRadio()
    htcButton.txCtrl = RCPButtonRequest()
    htcButton.txCtrl.pttTarget = ButtonTarget.FRONT_PTT
    htcButton.txCtrl.pttOperation = ButtonOperation.PRESS
    seqn = rcpPort.send(htcButton)


    logging.info("Waiting for a while...")
    time.sleep(10)


    logging.info("Keying down...")
    htcButton.txCtrl.pttOperation = ButtonOperation.RELEASE
    seqn = rcpPort.send(htcButton)

    logging.info("Shutting down...")

    rcpPort.stop()
    rtpPort.stop()

