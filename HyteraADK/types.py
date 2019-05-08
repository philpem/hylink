from enum import Enum

class CallType(Enum):           # ADKCoreEngine_CLR/CallType.cs
    PRIVATE             = 0             # Private call
    GROUP               = 1             # Group call
    ALL                 = 2             # All call
    EMERGENCY_GROUP     = 3             # Emergency group call
    REMOTE_MONITOR      = 4             # Remote monitor call
    PRIORITY_PRIVATE    = 5             # Priority private call
    PRIORITY_GROUP      = 6             # Priority group call
    PRIORITY_ALL        = 7             # Priority all call

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
    NORMAL = 0                  # Normal, single-connection mode
    SELECTIVE = 1               # Selective, multi-connection mode


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


class ButtonTarget(Enum):
    # See Buttons.cs for more
    FRONT_PTT       = 0x03  # Front PTT switch (Internal PTT)
    BACK_PTT        = 0x1E  # Back PTT switch (External PTT)
    CHANNEL_UP      = 0x22  # Channel Up
    CHANNEL_DOWN    = 0x23  # Channel Down


class ButtonOperation(Enum):
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


class SuccessFailResult(Enum):
    SUCCESS     = 0
    FAILURE     = 1


class ResultCode(Enum):
    # see dmrsvr.lua, line 395, "result_codes"
    OK                      = 0
    CHANNEL_BUSY            = 1
    RX_ONLY                 = 2
    LOW_BATTERY             = 3
    PLL_UNLOCK              = 4
    PRIVATE_CALL_NO_ACK     = 5
    REPEATER_WAKEUP_FAIL    = 6
    NO_CONTACT              = 7
    IGNITION_PTT_DISABLE    = 8
    TOT_REKEY               = 9
    TX_DENY                 = 10
    TX_INTERRUPTED          = 11
    INVALID_PARAMETER       = 12


class TMSResultCode(Enum):
    OK                      = 0
    FAIL                    = 1
    # 2 unknown
    INVALID_PARAMETER       = 3
    CHANNEL_BUSY            = 4
    RX_ONLY                 = 5
    LOW_BATTERY             = 6
    PLL_UNLOCK              = 7
    PRIVATE_CALL_NO_ACK     = 8
    REPEATER_WAKEUP_FAIL    = 9
    NO_CONTACT              = 10
    TX_DENY                 = 11
    TX_INTERRUPTED          = 12
