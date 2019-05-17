"""

RTP packet handler with Hytera specialisations

"""

from enum import IntEnum
import struct


class RTPPayloadType(IntEnum):
    """ Hytera RTP packet payload type codes """
    HYTERA_PCMU = 0                         # ITU-T G.711 mu-Law
    HYTERA_PCMA = 8                         # ITU-T G.711 a-Law


class RTPPacket(object):
    """ Serialise and deserialise RTP (Real-Time Protocol) stream data """

    def __init__(self, data=None):
        """
        Create an RTP packet
        """

        # If no data is passed in, create an empty default packet
        if data is None:
            self.rtpVersion     = 2         # "V" - RTP version
            self.extension      = None      # Extension words: {'type': format, 'data': sequence of 32bit uints}
            self.marker         = False     # "M" - Marker bit
            self.payloadType    = 0         # "PT" - Payload type
            self.seq            = 0         # Sequence number
            self.timestamp      = 0         # Timestamp
            self.ssrc           = 0         # Synchronising source
            self.csrc           = []        # CSRC
            self.payload        = bytes()
            return

        # RTP packet has a fixed 12-byte header followed by some optional fields.
        # Start by decoding the fixed header
        flags, timestamp, ssrc = struct.unpack_from('!LLL', data)

        self.rtpVersion     = (flags >> 30) & 0x03
        padding             = (flags & 0x200000) != 0
        extension           = (flags & 0x100000) != 0
        csrcCount           = (flags >> 24) & 0x0F
        self.marker         = (flags & 0x800000) != 0
        self.payloadType    = (flags >> 16) & 0x7F
        self.seq            = (flags & 0xFFFF)

        # Calculate payload start offset
        payloadStart = 12

        # Decode CSRC data
        if csrcCount > 0:
            fmt = '!' + 'L'*csrcCount
            self.csrc = struct.unpack_from(fmt, data, payloadStart)
            payloadStart += (csrcCount * 4)

        # Decode extension field, if any
        if extension:
            # Read the extension field and its length
            e = struct.unpack_from('!L', data, payloadStart)[0]
            payloadStart += 4

            # decode the initial extension word (format code and length)
            efmt = (e >> 16) & 0xFFFF
            elen = e & 0xFFFF

            # decode the extension data
            fmt = '!' + 'L'*elen
            edata = struct.unpack_from(fmt, data, payloadStart)
            payloadStart += (elen*4)

            self.extension = {'type': efmt, 'data': edata}

        # Figure out how much padding (if any) to remove
        if padding:
            # Last byte of the packet is the number of padding octets, including itself
            npadding = data[-1]
            self.payload = data[payloadStart:-npadding]
        else:
            self.payload = data[payloadStart:]

    def __bytes__(self):
        """ Convert the RTP packet to a byte representation """

        if self.rtpVersion > 3:
            raise ValueError("Invalid RTP version")
        if self.payloadType > 0x7F:
            raise ValueError("Invalid payload type")

        # Start with the RTP fixed header
        flags = (self.rtpVersion << 30) | (self.payloadType << 16) | (self.seq & 0xFFFF)

        if self.extension is not None:
            flags |= 0x10000000

        if self.marker:
            flags |= 0x800000

        if self.csrc is not None:
            if len(self.csrc) > 15:
                raise ValueError("CSRC length is limited to 15 entries")
            flags |= (len(self.csrc) << 24)

        buf = struct.pack('!LLL', flags, self.timestamp & 0xFFFFFFFF, self.ssrc)

        # Append the CSRCs
        fmt = '!' + 'L'*len(self.csrc)
        buf += struct.pack(fmt, *self.csrc)

        # Append the extension block, if any
        if self.extension is not None:
            if 'data' not in self.extension or 'type' not in self.extension:
                raise ValueError("Extension must be a dict: {'type': number, 'data':bytes}")

            fmt = '!L' + 'L'*len(self.extension['data'])
            buf += struct.pack(fmt,
                               (self.extension['type'] << 16) | len(self.extension['data']),
                               *self.extension['data'])

        # Payload!
        buf += bytes(self.payload)

        # We don't do padding -- perhaps that should be a TODO.
        return buf

    def __repr__(self):
        # Try to decode the payload type; set string to "???" if this fails
        try:
            rty = str(RTPPayloadType(self.payloadType))
        except:
            rty = "???"

        return "<RTP: version %d, pty %d (%s), seqid=%d, tm=%d, %d-byte payload>" % \
               (self.rtpVersion, self.payloadType, rty, self.seq, self.timestamp, len(self.payload))

