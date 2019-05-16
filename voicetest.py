#!/usr/bin/env python3

import logging
import queue
import time

#from HyteraADK.packet import *
from HyteraADK.ports import ADKDefaultPorts
from HyteraADK.socket import ADKSocket
from HyteraADK.packet import *
from HyteraADK.types import *
from HyteraADK.rtp import RTPPacket


if __name__ == '__main__':

    # configure logging
    logging.basicConfig(format='%(asctime)s [%(levelname)-7s] (%(threadName)-20s) %(message)s', level=logging.DEBUG)

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


    logging.info("Sending some silence")
    import sys
    import audioop
    W=2
    sampToSignedBin = lambda data: b''.join(b.to_bytes(W, sys.byteorder, signed=True) for b in data)

    SRATE = 8000        # sample rate Hz
    NSAMPS = 160        # number of samples per packet, is 20ms at 8kHz

    pkt = RTPPacket()
    pkt.payload = audioop.lin2ulaw(sampToSignedBin([0]*NSAMPS), W)
    pkt.payloadType = 0   # PCM u-LAW

    for i in range(round(SRATE / NSAMPS)): # generate one second worth of RTP frames
        pkt.seq += 1
        pkt.timestamp += NSAMPS
        rtpPort.send(pkt)
        time.sleep(NSAMPS / SRATE)


    logging.info("Keying down...")
    htcButton.txCtrl.pttOperation = ButtonOperation.RELEASE
    seqn = rcpPort.send(htcButton)

    # Wait for the last few packets to arrive
    time.sleep(5)

    logging.info("Shutting down...")

    rcpPort.stop()
    rtpPort.stop()

