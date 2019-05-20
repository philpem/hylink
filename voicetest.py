#!/usr/bin/env python3

import audioop
import sys
import time
import librosa

from hylink.ports import ADKDefaultPorts
from hylink.socket import ADKSocket
from hylink.packet import *
from hylink.types import *
from hylink.rtp import RTPPacket, RTPPayloadType

# Private Call the target radio
CFG_PRIV_CALL = True

# List of WAV files to play
CFG_DEMO_WAVS = ('wavfiles/hello.txt.wav',
                 'wavfiles/brownfox.txt.wav',
                 'wavfiles/ops.txt.wav',
                 'wavfiles/glados.txt.wav',
                 'wavfiles/announce.txt.wav'
                 )


# Set up call parameters
if CFG_PRIV_CALL:
    RADIOID = 9000
    CALLTYPE = CallType.PRIVATE
else:
    RADIOID = 10000
    CALLTYPE = CallType.GROUP

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
while (not rtpPort.is_connected()) or (not rcpPort.is_connected()):
    time.sleep(2)
logging.info("Repeater connected!")

# send txctrl call request
logging.info("Sending Call request...")
htc = HSTRPToRadio()
htc.txCtrl = RCPCallRequest()
htc.txCtrl.callType = CALLTYPE
htc.txCtrl.destId = RADIOID
seqn = rcpPort.send(htc)
time.sleep(2)

logging.info("Keying up...")
htcButton = HSTRPToRadio()
htcButton.txCtrl = RCPButtonRequest()
htcButton.txCtrl.pttTarget = ButtonTarget.FRONT_PTT
htcButton.txCtrl.pttOperation = ButtonOperation.PRESS
seqn = rcpPort.send(htcButton)
time.sleep(2)

logging.info("Sending some silence")


def samp_to_signed_bin(data, width=2):
    return b''.join(b.to_bytes(width, sys.byteorder, signed=True) for b in data)


SAMPLE_RATE = 8000        # sample rate Hz
RTP_FRAMESZ = 160        # number of samples per packet, is 20ms at 8kHz

_rtpseq = int(time.time() * SAMPLE_RATE)
_rtptstamp = _rtpseq


def silence(nsecs=1.0):
    """
    send <nsecs> seconds of silence over RTP

    :param nsecs: number of seconds of silence
    :return: nothing
    """

    global _rtpseq, _rtptstamp

    pkt = RTPPacket()
    pkt.payload = audioop.lin2ulaw(samp_to_signed_bin([0] * RTP_FRAMESZ), 2)
    pkt.payloadType = RTPPayloadType.HYTERA_PCMU
    # NOTE: Extension must be correct or the repeater won't repeat the audio
    pkt.extension = {'type': 0x15, 'data': [0, 0, 0]}

    # generate some RTP frames
    for i in range(round((SAMPLE_RATE / RTP_FRAMESZ) * nsecs)):
        _rtpseq += 1
        _rtptstamp += RTP_FRAMESZ
        pkt.seq = _rtpseq
        pkt.timestamp = _rtptstamp
        rtpPort.send(pkt)
        time.sleep(RTP_FRAMESZ / SAMPLE_RATE)


def wavfile(filename):
    """
    Play a wave file over RTP

    :param filename:
    :return:
    """

    global _rtpseq, _rtptstamp

    # load the wav file, using librosa to convert to mono at the repeater's RTP sample rate
    data, sr = librosa.load(filename, sr=SAMPLE_RATE, mono=True)

    # create an RTP packet
    pkt = RTPPacket()
    pkt.payloadType = RTPPayloadType.HYTERA_PCMU    # ITU-T G.711 mu-law
    # NOTE: Extension must be correct or the repeater won't repeat the audio
    pkt.extension = {'type': 0x15, 'data': [0, 0, 0]}

    next_time = time.time()
    pace = RTP_FRAMESZ / SAMPLE_RATE
    log.debug("Starting WAV playback, pace=%.2f ms" % (pace * 1000.))
    for i in range(0, len(data), RTP_FRAMESZ):
        # process audio in chunks of the RTP frame size
        chunk = data[i:i+160]

        # update sequence number and timestamp
        _rtpseq += 1
        _rtptstamp += RTP_FRAMESZ
        pkt.seq = _rtpseq
        pkt.timestamp = _rtptstamp

        def _sx(x):
            """ float32-to-signed16 with saturation clipping """
            r = int(round(32767*x))
            if r > 32767:
                return 32767
            elif r < -32767:
                return -32767
            else:
                return r

        # convert from float32 to signed16
        chunk = [_sx(x) for x in chunk]

        # we now have <= 160 bytes, pad with silence if needed
        if len(chunk) < RTP_FRAMESZ:
            padding = [0] * (RTP_FRAMESZ - len(chunk))
            chunk += padding

        # convert to ITU G.711 mu-law
        pkt.payload = audioop.lin2ulaw(samp_to_signed_bin(chunk), 2)

        # send packet
        rtpPort.send(pkt)

        # wait for next interval
        next_time += pace
        time.sleep(max(0., next_time - time.time()))


# slight delay so we don't lose the start of the audio
# e.g. due to the target radio keying up
silence(0.2)

for wav in CFG_DEMO_WAVS:
    wavfile(wav)
    silence(1.0)

# slight delay to avoid losing the end of the audio
silence(0.2)

logging.info("Keying down...")
htcButton.txCtrl.pttOperation = ButtonOperation.RELEASE
seqn = rcpPort.send(htcButton)

# Wait for the last few packets to arrive
time.sleep(5)

logging.info("Shutting down...")

rcpPort.stop()
rtpPort.stop()
