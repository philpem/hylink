from enum import IntEnum


class ADKDefaultPorts(IntEnum):
    RRS1    = 30001         # Radio Registration Service, ts1   http://www.hytera.com/mena/navigation.htm?newsId=9089&columnType=news
    RRS2    = 30002         # Radio Registration Service, ts2
    LP1     = 30003         # Location Protocol (GPS), ts1      http://www.hytera.com/mena/navigation.htm?newsId=9084&columnType=news
    LP2     = 30004         # Location Protocol (GPS), ts2
    TP1     = 30005         # Telemetry Protocol, ts1           http://www.hytera.com/mena/navigation.htm?newsId=9088&columnType=news
    TP2     = 30006         # Telemetry Protocol, ts2
    TMP1    = 30007         # Text Message Protocol (TMP/TMS), ts1        http://www.hytera.com/mena/navigation.htm?newsId=9086&columnType=news
    TMP2    = 30008         # Text Message Protocol (TMP/TMS), ts2
    RCP1    = 30009         # Radio Control Protocol, ts1  http://www.hytera.com/mena/navigation.htm?newsId=9085&columnType=news
    RCP2    = 30010         # Radio Control Protocol, ts2
            # DTP 1 not specified       Data Transfer Protocol      http://www.hytera.com/mena/navigation.htm?newsId=9087&columnType=news
            # DTP 2 not specified       Data Transfer Protocol
            # Self Defined Data 1 not specified
            # Self Defined Data 2 not specified
    RTP1    = 30012         # Real Time Protocol, ts1   -- audio data, G.711 uLAW, including Hytera ping packets (!)
    RTP2    = 30014         # Real Time Protocol, ts2   -- ""
    RCPAnalog = 30015       # Radio Call Control Protocol, analog audio
    RTPAnalog = 30016       # Real Time Protocol, analog
    E2E1    = 30017         # E2E = ???
    E2E2    = 30018         # E2E = ???
    SDM1    = 3017          # Short Data Messaging / Self-Defined Message (Works Order)
    SDM2    = 3018          # Short Data Messaging / Self-Defined Message (Works Order)

    # RRS Port ID       115
    # GPS Port ID       116
    # Telemetry Port ID 117
    # SDM Port ID       118
    # RCP Port ID       119

