"""
ADK transport layer (HYT)
"""

import logging
import struct
from .types import *
from .exceptions import *
from .utils import *


log = logging.getLogger(__name__)


# Return 'None' if there isn't an ADK handler for this packet class
# If False -- raises a HYTUnhandledType exception
CFG_RETURN_NONE_ON_UNKNOWN_PCLASS = False

# Return 'None' if there isn't a factory for this TxCtrl packet opcode
# If False -- raises a HYTUnhandledType exception
CFG_RETURN_NONE_ON_UNKNOWN_TXCTRL_OPCODE = False


class HYTPacket(object):

    """ Root Hytera HYT packet """

    # HYT signature prefix
    __HYTSIG = b'\x32\x42\x00'

    def __init__(self, data=None):
        """
        Convert a block of bytes into a new HYTPacket.

        If data == None or not provided, an empty packet will be created
        """
        if data is None:
            self.hytPktType = 0xFF
            self.hytSeqID   = 1
            self.hytPayload = b''
            return

        # Unpack the packet data
        signature = data[0:3]
        pktType, seqid = struct.unpack_from('>BH', data, 3)

        # Check the initial signature is correct
        if signature != self.__HYTSIG:
            raise HYTBadSignature("Bad header signature")

        # De-encapsulate the fields -- TODO refactor and do this with struct.decode
        self.hytPktType = pktType
        self.hytSeqID   = seqid
        self.hytPayload = data[6:]

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        return self.__HYTSIG + struct.pack('>BH', self.hytPktType, self.hytSeqID) + self.hytPayload

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: type 0x%02X, seqid %d, %d payload bytes>" % (type(self).__name__, self.hytPktType, self.hytSeqID, len(self.hytPayload))

    @staticmethod
    def decode(data):
        """ Decode an arbitrary HYTPacket into its lowest-level subclass """

        # First decode as a raw ADK packet to get the packet type
        p = HYTPacket(data)

        # Scan subclasses to find one which handles this packet type
        for sc in HYTPacket.__subclasses__():
            if sc.TYPE == p.hytPktType:
                return sc(data)

        # Couldn't find an ADK packet handler which handles this type of packet
        if CFG_RETURN_NONE_ON_UNKNOWN_PCLASS:
            return None
        else:
            raise HYTUnhandledType("Unhandled HYT packet class 0x%02X" % p.hytPktType)


####################################
#
# HSTRP packet subtypes
#
####################################

class HSTRPToRadio(HYTPacket):
    """ HYT Transmitter Control packet """
    TYPE = 0x00

    def __init__(self, data=None):
        # Decode the packet as HYT first. We work on the payload data.
        super().__init__(data)
        self.hytPktType = self.TYPE

        # Decode the payload -- it's a TxCtrl block
        self.txCtrl = TxCtrlBase.factory(self.hytPayload)

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        # A heartbeat has no payload.
        self.hytPayload = bytes(self.txCtrl)
        return super().__bytes__()

    def __repr__(self):
        """ Convert this packet into a string representation """
        if self.txCtrl is not None:
            return "<%s: type 0x%02X, seqid %d, payload: %s >" % (type(self).__name__, self.hytPktType, self.hytSeqID, self.txCtrl)
        else:
            return "<%s: type 0x%02X, seqid %d, %d payload bytes>" % (type(self).__name__, self.hytPktType, self.hytSeqID, len(self.hytPayload))


class HSTRPAck(HYTPacket):
    """ HYT ACK packet, sent by IPDIS or the repeater to acknowledge receipt of a packet """
    TYPE = 0x01

    def __init__(self, data=None):
        # Decode the packet as HYT first. We work on the payload data.
        super().__init__(data)

        # No-args constructor
        if data is None:
            self.hytPktType = self.TYPE
            return

        # An ACK has no payload.

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        # An ACK has no payload.
        self.hytPayload = b''
        return super().__bytes__()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: type 0x%02X, seqid %d, %d payload bytes>" % (type(self).__name__, self.hytPktType, self.hytSeqID, len(self.hytPayload))


class HSTRPHeartbeat(HYTPacket):
    """ HYT Heartbeat / Keepalive packet, sent by IPDIS or the repeater to keep the connection alive. """
    TYPE = 0x02

    def __init__(self, data=None):
        # Decode the packet as HYT first. We work on the payload data.
        super().__init__(data)

        # No-args constructor
        if data is None:
            self.hytPktType = self.TYPE
            return

        # A heartbeat has no payload.

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        # A heartbeat has no payload.
        self.hytPayload = b''
        return super().__bytes__()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: type 0x%02X, seqid %d, %d payload bytes>" % (type(self).__name__, self.hytPktType, self.hytSeqID, len(self.hytPayload))


class HSTRPSynAck(HYTPacket):
    """ HYT SYN-ACK packet, sent by IPDIS to repeater when a HSTRPSyn packet is received """
    TYPE = 0x05

    def __init__(self, data=None):
        # Decode the packet as HYT first. We work on the payload data.
        super().__init__(data)

        # No-args constructor
        if data is None:
            self.hytPktType = self.TYPE
            return

        # A SYN-ACK has no payload.

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        # A SYN-ACK has no payload.
        self.hytPayload = b''
        return super().__bytes__()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: type 0x%02X, seqid %d, %d payload bytes>" % (type(self).__name__, self.hytPktType, self.hytSeqID, len(self.hytPayload))


class HSTRPFromRadio(HYTPacket):
    """ HYT Repeater Reply/Broadcast packet """
    TYPE = 0x20

    def __init__(self, data=None):
        # Decode the packet as HYT first. We work on the payload data.
        super().__init__(data)

        # Handle no-args constructor
        if data is None:
            self.hytPktType = self.TYPE
            # Cannot create no-args SYN packets, they're only supposed to be
            # sent by the repeater
            raise NotImplementedError("It is not possible to create an empty FromRadio packet")

        # This is a broadcast header followed by a TxCtrlBase subclass
        self.rptHeader = RepeaterHeader(self.hytPayload)
        self.txCtrl = TxCtrlBase.factory(self.hytPayload[len(self.rptHeader):])

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        # Throw an exception because user code shouldn't be trying to send SYN packets?
        raise NotImplementedError("It is not possible to serialize a FromRadio packet")

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: type 0x%02X, seqid %d -- rptHeader %s, txctrl %s >" % \
               (type(self).__name__, self.hytPktType, self.hytSeqID, self.rptHeader, self.txCtrl)


class HSTRPSyn(HYTPacket):
    """ HYT Repeater Announcement (SYN) packet """
    TYPE = 0x24

    def __init__(self, data=None):
        # Decode the packet as HYT first. We work on the payload data.
        super().__init__(data)

        # Handle no-args constructor
        if data is None:
            self.hytPktType = self.TYPE
            # Cannot create no-args SYN packets, they're only supposed to be
            # sent by the repeater
            raise NotImplementedError("It is not possible to create an announcement packet with the no-args constructor")

        # The ADK log calls this NetworkDescriptor / "syn packet"

        # Decode the payload
        self.rptHeader = RepeaterHeader(self.hytPayload)

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        # Throw an exception because user code shouldn't be trying to send SYN packets?
        raise NotImplementedError("It is not possible to serialize a SYN packet for transmission")

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: type 0x%02X, seqid %d, rptHeader %s >" % (type(self).__name__, self.hytPktType, self.hytSeqID, self.rptHeader)


###################################################
#
# Repeater broadcast header
#
###################################################

class RepeaterHeader(object):

    def __init__(self, data):
        # No-args constructor
        if data is None or len(data) == 0:
            # No-args is not allowed
            raise NotImplementedError("It is not possible to create a RepeaterHeader with the no-args constructor")

        # The Repeater Header is a sequence of tag-length-value blocks.
        # Tag OR 0x80 means further TLVs follow

        tlv = {}
        ofs = 0
        tag = 0x80
        while (tag & 0x80) != 0:
            # read tag,length
            tag, length = struct.unpack_from('BB', data, ofs)
            ofs += 2

            # read payload
            tlv[tag & 0x7F] = data[ofs:ofs+length]
            ofs += length

        # Decode TLVs
        self.hasRTP = False
        self.synRepeaterRadioID = None
        self.synTimeslot = None

        if 1 in tlv:
            # Tag 1 is zero length and only sent if RTP is available
            self.hasRTP = True
        if 3 in tlv:
            # Tag 3 is Repeater ID
            self.synRepeaterRadioID = struct.unpack_from('>L', tlv[3])[0]
        if 4 in tlv:
            # Tag 4 is Timeslot
            self.synTimeslot = struct.unpack_from('B', tlv[4])[0]

        self.tlvData = tlv
        self._tlvLen = ofs

    def __len__(self):
        """ Return the number of bytes this repeater header occupied """
        return self._tlvLen

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        raise NotImplemented("It is not reasonable to convert a RepeaterHeader to bytes")

    def __repr__(self):
        """ Convert this packet into a string representation """
        if self.hasRTP:
            hasRTP = ", has RTP"
        else:
            hasRTP = ""

        return "<%s: repeater ID %s, timeslot %s%s>" % \
               (type(self).__name__, self.synRepeaterRadioID, self.synTimeslot, hasRTP)


###################################################
#
# TxCtrl payload types
#
###################################################


class TxCtrlBase(object):

    def __init__(self, data):
        # No-args constructor
        if data is None or len(data) == 0:
            self.txcReliable = False
            self.txcOpcode = None
            self.txcPayload = []
            return

        # Not no-args -- decode the payload

        # Check packet length is reasonable
        if len(data) < 7:
            raise HYTPacketDataError()

        # Check Message End byte
        if data[-1] != 0x03:
            raise HYTPacketDataError()

        # Begin decoding
        self.txcMsgHdr = MessageHeader(data[0] & 0x7F)
        self.txcReliable = (data[0] & 0x80) != 0

        # For some unknown reason, RCP is little-endian while every other protocol is big-endian
        if self.txcMsgHdr == MessageHeader.RCP:
            self.txcOpcode, numBytes = struct.unpack_from("<HH", data[1:])
        else:
            self.txcOpcode, numBytes = struct.unpack_from(">HH", data[1:])

        self.txcPayload = data[5:5+numBytes]

        # Check the message checksum
        csum = (~(sum(data[1:5]) + sum(self.txcPayload)) + 0x33) & 0xFF
        checksum = data[-2]
        if csum != checksum:
            raise HYTPacketDataError("Invalid packet checksum")

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        # For some unknown reason, RCP is little-endian while every other protocol is big-endian
        if self.txcReliable:
            reliable = 0x80
        else:
            reliable = 0

        if self.txcMsgHdr == MessageHeader.RCP:
            data = struct.pack("<BHH", self.txcMsgHdr | reliable, self.txcOpcode, len(self.txcPayload)) + self.txcPayload
        else:
            data = struct.pack(">BHH", self.txcMsgHdr | reliable, self.txcOpcode, len(self.txcPayload)) + self.txcPayload

        # Calculate the message checksum
        csum = (~(sum(data[1:5]) + sum(self.txcPayload)) + 0x33) & 0xFF

        # Append checksum and trailer byte
        data += struct.pack("BB", csum, 0x03)

        return data

    @staticmethod
    def factory(data):
        # Decode as a TxCtrl base packet first
        txcp = TxCtrlBase(data)

        if txcp.txcOpcode is None:
            return

        # Scan subclasses to find one which handles this packet type
        for sc in TxCtrlBase.__subclasses__():
            if sc.MSGHDR == txcp.txcMsgHdr and sc.OPCODE == txcp.txcOpcode:
                return sc(data)

        # Couldn't find a TxCtrl packet handler which handles this type of packet
        if CFG_RETURN_NONE_ON_UNKNOWN_TXCTRL_OPCODE:
            return None
        else:
            raise HYTUnhandledType("Unhandled TxCtrl payload, msghdr %s opcode 0x%04X" % (txcp.txcMsgHdr, txcp.txcOpcode))


#############################################################################
#
# RCP packet types
#
#############################################################################


class RCPButtonRequest(TxCtrlBase):

    MSGHDR = MessageHeader.RCP
    OPCODE = 0x0041

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            # empty packet
            self.result = 0
            return

        # valid packet
        self.pttTarget, self.pttOperation = struct.unpack('<BB', self.txcPayload)
        self.pttTarget    = ButtonTarget(self.pttTarget)
        self.pttOperation = ButtonOperation(self.pttOperation)

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        self.txcPayload = struct.pack('<BB', self.pttTarget, self.pttOperation)
        return super().__bytes__()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: target %s, operation %s>" % (type(self).__name__, self.pttTarget, self.pttOperation)


class RCPButtonResponse(TxCtrlBase):

    MSGHDR = MessageHeader.RCP
    OPCODE = 0x8041

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            # empty packet
            raise NotImplemented()

        # valid packet
        self.result = SuccessFailResult(int(self.txcPayload[0]))

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        raise NotImplemented()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: result %s>" % (type(self).__name__, self.result)


class RCPChannelStatusOrParameterCheckRequest(TxCtrlBase):

    MSGHDR = MessageHeader.RCP
    OPCODE = 0x00E7

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            # empty packet
            self.target = 0
            self.valueType = 0
            return

        # valid packet
        self.target, self.valueType = struct.unpack('<BB', self.txcPayload)
        self.target = StatusParameter(self.target)
        self.valueType = StatusValueType(self.valueType)

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        self.txcPayload = struct.pack('<BB', self.target, self.valueType)
        return super().__bytes__()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: target %s, valuetype %s>" % (type(self).__name__, self.target, self.valueType)


class RCPChannelStatusOrParameterCheckResponse(TxCtrlBase):

    MSGHDR = MessageHeader.RCP
    OPCODE = 0x80E7

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            raise NotImplemented()

        # valid packet
        self.result, targetNum = struct.unpack_from('<BB', self.txcPayload)
        self.result = SuccessFailResult(self.result)
        self.response = []

        # decode target values
        for ofs in range(2, 2+(5*targetNum), 5):
            target, value = struct.unpack_from('<Bi', self.txcPayload, ofs)
            target = StatusParameter(target)
            self.response.append((target, value))

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        raise NotImplemented()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: result %s, responses: %s >" % (type(self).__name__, self.result, self.response)


class RCPCallRequest(TxCtrlBase):

    MSGHDR = MessageHeader.RCP
    OPCODE = 0x0841

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            # empty packet
            self.callType = 0
            self.destId = 0
            return

        # valid packet
        self.callType, self.destId = struct.unpack_from('<BI', self.txcPayload)
        self.callType = CallType(self.callType)

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        self.txcPayload = struct.pack('<BI', self.callType, self.destId)
        return super().__bytes__()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: callType %s, destId %d>" % (type(self).__name__, self.callType, self.destId)


class RCPCallResponse(TxCtrlBase):

    MSGHDR = MessageHeader.RCP
    OPCODE = 0x8841

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            # empty packet
            self.result = 0
            return

        # valid packet
        self.result = int(self.txcPayload[0])

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        self.txcPayload = struct.pack('<B', self.result)
        return super().__bytes__()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: result %d>" % (type(self).__name__, self.result)


class RCPBroadcastTransmitStatus(TxCtrlBase):

    MSGHDR = MessageHeader.RCP
    OPCODE = 0xB843

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            # empty packet
            raise NotImplemented()

        # valid packet
        self.process, self.source, self.callType, self.targetID = \
            struct.unpack_from("<HHHI", self.txcPayload)

        self.process = ProcessType(self.process)
        # TODO source: RCPResultCode?
        self.callType = CallType(self.callType)

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        raise NotImplemented()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: process %s, source %s, calltype %s, target %d>" % \
               (type(self).__name__, self.process, self.source, self.callType, self.targetID)


class RCPRepeaterBroadcastTransmitStatus(TxCtrlBase):

    MSGHDR = MessageHeader.RCP
    OPCODE = 0xB845

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            # empty packet
            raise NotImplemented()

        # valid packet
        self.mode, self.status, self.serviceType, self.callType, self.targetID, self.senderID = \
            struct.unpack_from("<HHHHII", self.txcPayload)
        self.mode = TxCallMode(self.mode)
        self.status = TxCallStatus(self.status)
        self.serviceType = TxServiceType(self.serviceType)
        self.callType = CallType(self.callType)

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        raise NotImplemented()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: mode %s, status %s, svctype %s, calltype %s, target %d, sender %d>" % \
               (type(self).__name__, self.mode, self.status, self.serviceType, self.callType, self.targetID, self.senderID)


#############################################################################
#
# RRS packet types
#
#############################################################################

class RRSOffline(TxCtrlBase):
    """ RRS_OFFLINE: RRS Radio Offline request """

    MSGHDR = MessageHeader.RRS
    OPCODE = 0x0001

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            # empty packet
            raise NotImplemented()

        # valid packet
        self.radioIP = struct.unpack_from('>I', self.txcPayload)[0]
        self.radioID = dmrIPtoID(self.radioIP)

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        raise NotImplemented()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: radioIP=%s, radioID=%s>" % (type(self).__name__, dmrIPtoStr(self.radioIP), self.radioID)


class RRSRegister(TxCtrlBase):
    """ RRS_REGIST: RRS Registration request """

    MSGHDR = MessageHeader.RRS
    OPCODE = 0x0003

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            # empty packet
            raise NotImplemented()

        # valid packet
        self.radioIP = struct.unpack_from('>I', self.txcPayload)[0]
        self.radioID = dmrIPtoID(self.radioIP)

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        raise NotImplemented()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: radioIP=%s, radioID=%s>" % (type(self).__name__, dmrIPtoStr(self.radioIP), self.radioID)


# TODO list for RRS:
#
#   RRS Opcode 128, Register Ack
#
#   - OnlineAnswerRequest aka CRRSOnlineAnswerRequest (from ADKCoreEngine_CLR/ServiceBase.cs) --
#        - Result
#        - Valid time
#        - Target ID   (+12)


#############################################################################
#
# TMP packet types
#
#############################################################################

class TMPPrivateMessageNeedAck(TxCtrlBase):
    # Hytera API: TMP_PRIVATE_NEED_ACK_REQUEST

    MSGHDR = MessageHeader.TMP
    OPCODE = 0x00A1

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            # empty packet
            raise NotImplemented()

        # valid packet
        self.msgSeq, self.destIP, self.srcIP = struct.unpack_from('>III', self.txcPayload)
        self.destID  = dmrIPtoID(self.destIP)
        self.srcID   = dmrIPtoID(self.srcIP)
        self.message = self.txcPayload[12:].decode('utf-16le')

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        raise NotImplemented()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: msgseq=%d, from %d to %d, text '%s'>" % (type(self).__name__, self.msgSeq, self.srcID, self.destID, self.message)


class TMPPrivateMessageAnswer(TxCtrlBase):
    # Hytera API: TMP_PRIVATE_ANSWER

    MSGHDR = MessageHeader.TMP
    OPCODE = 0x00A2

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            # empty packet
            raise NotImplemented()

        # valid packet
        self.msgSeq, self.destIP, self.srcIP = struct.unpack_from('>III', self.txcPayload)
        self.destID  = dmrIPtoID(self.destIP)
        self.srcID   = dmrIPtoID(self.srcIP)
 
    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        raise NotImplemented()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: msgseq=%d, from %d to %d>" % (type(self).__name__, self.msgSeq, self.srcID, self.destID)


class TMPGroupMessage(TxCtrlBase):
    # Hytera API: TMP_GROUP_REQUEST

    MSGHDR = MessageHeader.TMP
    OPCODE = 0x00B1

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            # empty packet
            raise NotImplemented()

        # valid packet
        self.msgSeq, self.destIP, self.srcIP = struct.unpack_from('>III', self.txcPayload)
        self.destID  = dmrIPtoID(self.destIP)
        self.srcID   = dmrIPtoID(self.srcIP)
        self.message = self.txcPayload[12:].decode('utf-16le')

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        raise NotImplemented()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: msgseq=%d, from %d to %d, text '%s'>" % (type(self).__name__, self.msgSeq, self.srcID, self.destID, self.message)


class TMPGroupMessageAnswer(TxCtrlBase):
    # Hytera API: TMP_GROUP_ANSWER

    MSGHDR = MessageHeader.TMP
    OPCODE = 0x00B2

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            # empty packet
            raise NotImplemented()

        # valid packet
        self.msgSeq, self.destIP, self.srcIP = struct.unpack_from('>III', self.txcPayload)
        self.destID  = dmrIPtoID(self.destIP)
        self.srcID   = dmrIPtoID(self.srcIP)
 
    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        raise NotImplemented()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: msgseq=%d, from %d to %d>" % (type(self).__name__, self.msgSeq, self.srcID, self.destID)


class TMPPrivateMessageNoAck(TxCtrlBase):
    # Hytera API: TMP_PRIVATE_NO_NEED_ACK_REQUEST

    MSGHDR = MessageHeader.TMP
    OPCODE = 0x80A1

    def __init__(self, txc=None):
        # Decode the Tx Call payload first
        super().__init__(txc)

        self.txcOpcode = self.OPCODE
        self.txcMsgHdr = self.MSGHDR

        if txc is None:
            # empty packet
            raise NotImplemented()

        # valid packet
        self.msgSeq, self.destIP, self.srcIP = struct.unpack_from('>III', self.txcPayload)
        self.destID  = dmrIPtoID(self.destIP)
        self.srcID   = dmrIPtoID(self.srcIP)
        self.message = self.txcPayload[12:].decode('utf-16le')

    def __bytes__(self):
        """ Convert this packet into a byte sequence """
        raise NotImplemented()

    def __repr__(self):
        """ Convert this packet into a string representation """
        return "<%s: msgseq=%d, from %d to %d, text '%s'>" % (type(self).__name__, self.msgSeq, self.srcID, self.destID, self.message)


