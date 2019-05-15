from enum import IntEnum

class CallType(IntEnum):           # ADKCoreEngine_CLR/CallType.cs
    PRIVATE             = 0             # Private call
    GROUP               = 1             # Group call
    ALL                 = 2             # All call
    EMERGENCY_GROUP     = 3             # Emergency group call
    REMOTE_MONITOR      = 4             # Remote monitor call
    PRIORITY_PRIVATE    = 5             # Priority private call
    PRIORITY_GROUP      = 6             # Priority group call
    PRIORITY_ALL        = 7             # Priority all call

class ProcessType(IntEnum):
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


class TxCallMode(IntEnum):
    NORMAL = 0                  # Normal, single-connection mode
    SELECTIVE = 1               # Selective, multi-connection mode


class TxCallStatus(IntEnum):       # Only used by B845 (Broadcast status report), which ADK doesn't seem to use
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


class TxServiceType(IntEnum):
    NONE = 0
    VOICE = 1
    TMP = 2
    LP = 3
    RRS = 4
    TP = 5
    SUPPLEMENTARY = 6


class ButtonTarget(IntEnum):
    # See Buttons.cs for more
    FRONT_PTT       = 0x03  # Front PTT switch (Internal PTT)
    BACK_PTT        = 0x1E  # Back PTT switch (External PTT)
    CHANNEL_UP      = 0x22  # Channel Up
    CHANNEL_DOWN    = 0x23  # Channel Down


class ButtonOperation(IntEnum):
    RELEASE     = 0     # Release PRESS
    PRESS       = 1     # Press and hold
    SHORT_PUSH  = 2     # Short press then release
    LONG_PUSH   = 3     # Long press then release


class MessageHeader(IntEnum):
    RCP         = 0x02
    LP          = 0x08
    TMP         = 0x09
    RRS         = 0x11
    TP          = 0x12
    DTP         = 0x13
    DDS         = 0x14      # Data Delivery States


class SuccessFailResult(IntEnum):
    SUCCESS     = 0
    FAILURE     = 1


class ResultCode(IntEnum):
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


class StatusParameter(IntEnum):
    STATUS_OF_ALL_CHANNELS      = 0     # Status and parameter of all channels
    SQUELCH_LEVEL               = 1     # Squelch level for analog channel (0=open, 1=normal, 2=tight)
    CTCSS_CDCSS_MATCH_STATUS    = 2     # CDCSS/CTCSS match status (analog) (0=no match, 1=match)
    POWER_LEVEL                 = 3     # Power level (0=high, 2=low)
    TX_FREQUENCY                = 4     # Transmit frequency
    RX_FREQUENCY                = 5     # Receive frequency
    TX_ALLOW                    = 6     # TX Allow (0=always, 1=channel free, 2=colour free, 3=CTCSS/CDCSS correct, 4=CTCSS/CDCSS incorrect, 5=RX only)
    CHANNEL_MODE                = 7     # Channel mode (0=conventional digital, 1=conventional analog, 2=repeater digital, 3=repeater analog, 4=trunking digital, 5=trunking analog, 6=repeater mix_channel, 0xFFFFFFFF=invalid)
    TALKAROUND_STATUS           = 8     # Talkaround status on/off [off_on type]
    RSSI                        = 9     # RSSI
    CARRIER_STATUS              = 10    # Carrier status (0=not present, 1=present)


class StatusValueType(IntEnum):
    LEVEL                       = 0
    DB_VALUE                    = 1
    ABANDON                     = 2

class TMSResultCode(IntEnum):
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
