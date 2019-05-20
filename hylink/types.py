from enum import IntEnum


class CallType(IntEnum):
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


class TxCallStatus(IntEnum):
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
    RCP         = 0x02      # Radio Control Protocol
    LP          = 0x08      # Location Protocol
    TMP         = 0x09      # Text Message Protocol
    RRS         = 0x11      # Radio Registration Service
    TP          = 0x12      # Telemetry Protocol
    DTP         = 0x13      # Data Transfer Protocol
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
    SQUELCH_LEVEL               = 1     # Squelch level for analog channel -- see StatusValueSquelchLevel
    CTCSS_CDCSS_MATCH_STATUS    = 2     # CDCSS/CTCSS match status (analog) -- see StatusValueCTCSSMatchStatus
    POWER_LEVEL                 = 3     # Power level -- see StatusValuePowerLevel
    TX_FREQUENCY                = 4     # Transmit frequency
    RX_FREQUENCY                = 5     # Receive frequency
    TX_ALLOW                    = 6     # TX Allow -- for valid values, see StatusValueTXAllow
    CHANNEL_MODE                = 7     # Channel mode -- see StatusValueChannelMode
    TALKAROUND_STATUS           = 8     # Talkaround status on/off [off_on type]
    RSSI                        = 9     # RSSI
    CARRIER_STATUS              = 10    # Carrier status (0=not present, 1=present)


class StatusValueSquelchLevel(IntEnum):
    """ Valid values when StatusParameter == SQUELCH_LEVEL """
    OPEN                    = 0
    NORMAL                  = 1
    TIGHT                   = 2


class StatusValueCTCSSMatchStatus(IntEnum):
    """ Valid values when StatusParameter == CTCSS_CDCSS_MATCH_STATUS """
    NO_MATCH                = 0
    MATCH                   = 1


class StatusValuePowerLevel(IntEnum):
    """ Valid values when StatusParameter == POWER_LEVEL """
    HIGH_POWER              = 0
    LOW_POWER               = 2


class StatusValueTXAllow(IntEnum):
    """ Valid values when StatusParameter == TX_ALLOW """
    ALWAYS                  = 0
    CHANNEL_FREE            = 1
    COLOUR_FREE             = 2
    CTCSS_CDCSS_CORRECT     = 3
    CTCSS_CDCSS_INCORRECT   = 4
    RECEIVE_ONLY            = 5


class StatusValueChannelMode:
    """ Valid values when StatusParameter == CHANNEL_MODE """
    CONVENTIONAL_DIGITAL    = 0
    CONVENTIONAL_ANALOG     = 1
    REPEATER_DIGITAL        = 2
    REPEATER_ANALOG         = 3
    TRUNKING_DIGITAL        = 4
    TRUNKING_ANALOG         = 5
    REPEATER_MIX            = 6
    INVALID                 = 0xFFFFFFFF


class StatusValueType(IntEnum):
    LEVEL                   = 0
    DB_VALUE                = 1
    ABANDON                 = 2


class TMSResultCode(IntEnum):
    """ Text Message Service (TMS) result code"""
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
