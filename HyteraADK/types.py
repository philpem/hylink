from enum import Enum

class CallType(Enum):           # ADKCoreEngine_CLR/CallType.cs
    PRIVATE             = 0             # Private call
    GROUP               = 1             # Group call
    ALL                 = 2             # All call
    EMERGENCY_GROUP     = 3
    REMOTE_MONITOR      = 4
    PRIORITY_PRIVATE    = 5
    PRIORITY_GROUP      = 6
    PRIORITY_ALL        = 7

class ProcessType(Enum):
    UNAVAILABLE         = 0
    VOICE_TX_OR_RX      = 1
    HANG_TIME           = 2
    CALL_END            = 3
    CALL_FAIL           = 4
    TOT                 = 5
    TOT_PRE_ALERT       = 6
    EMERGENCY_ALARM_TX  = 7
    EMERGENCY_STAY      = 8
    EMERGENCY_CALL_TX   = 9
    EMERGENCY_END       = 10


class TxCallMode(Enum):
    NORMAL = 0
    SELECTIVE = 1

class TxCallStatus(Enum):       # Only used by B845 (Broadcast status report), which ADK doesn't seem to use
    LOCAL_REPEATING = 0         # Repeating incoming traffic
    LOCAL_HANG_TIME = 1         # Repeating, in hang time
    IP_REPEATING = 2
    IP_HANG_TIME = 3
    CHANNEL_HANG_TIME = 4       # Channel hangtime (repeater is transmitting the idle burst)
    SLEEP = 5                   # Repeater idle/sleeping. Sent periodically every minute.
    REMOTE_PTT_TX = 6
    REMOTE_PTT_HANG_TIME = 7
    REMOTE_PTT_TX_END = 8
    REMOTE_PTT_WAIT_ACK = 9
    REMOTE_PTT_TOT = 10
    LOCAL_PTT_TX = 11
    LOCAL_PTT_HANG_TIME = 12
    LOCAL_PTT_TX_END = 13
    LOCAL_PTT_WAIT_ACK = 14
    LOCAL_PTT_TOT = 15


class TxServiceType(Enum):
    NONE = 0
    VOICE = 1
    TMP = 2
    LP = 3
    RRS = 4
    TP = 5
    SUPPLEMENTARY = 6


class PTTTarget(Enum):
    # See Buttons.cs for more
    FRONT_PTT   = 0x03  # Front PTT switch
    BACK_PTT    = 0x1E  # Back PTT switch


class PTTOperation(Enum):
    RELEASE     = 0     # Release PRESS
    PRESS       = 1     # Press and hold
    SHORT_PUSH  = 2     # Short press then release
    LONG_PUSH   = 3     # Long press then release


class MessageHeader(Enum):
    RCP         = 0x02
    LP          = 0x08
    TMP         = 0x09
    RRS         = 0x11
    TP          = 0x12
    DTP         = 0x13
    DDS         = 0x14      # Data Delivery States


