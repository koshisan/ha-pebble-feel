from __future__ import annotations

DOMAIN = "pebble_feel"
PLATFORMS = ["switch", "select"]

PF_SERVICE_UUID = "5df89308-0b98-11eb-adc1-0242ac120002"
WRITE_UUID_ALT = "8eb21104-0b98-11eb-adc1-0242ac120002"  # manufacturer example uses this for writes
PIPE_UUID_MAIN = "8eb20e7a-0b98-11eb-adc1-0242ac120002"  # write+notify pipe for reads

# Polling
DEFAULT_POLL_INTERVAL = 30  # seconds
CONF_POLL_INTERVAL = "poll_interval"
CONF_MODE_POLLING = "mode_polling"

# Modes (7 states)
MODES = [
    "cool_low",
    "cool_mid",
    "cool_high",
    "cool_rapid",
    "hot_low",
    "hot_mid",
    "hot_high",
]

MODE_TO_VALUE = {
    "cool_low": 0x0002,
    "cool_mid": 0x0003,
    "cool_high": 0x0004,
    "cool_rapid": 0x0005,
    "hot_low": 0x0006,
    "hot_mid": 0x0007,
    "hot_high": 0x0008,
}

VALUE_TO_MODE = {v: k for k, v in MODE_TO_VALUE.items()}

# Raw ASCII-hex frames from spec (write commands)
CMD_ENABLE = bytes.fromhex("353561306530383030303031303061610D0A")
CMD_DISABLE = bytes.fromhex("353561306530383030303030303061620D0A")

CMD_SET_MODE = {
    "cool_low": bytes.fromhex("353561306530393030303032303039390D0A"),
    "cool_mid": bytes.fromhex("353561306530393030303033303039380D0A"),
    "cool_high": bytes.fromhex("353561306530393030303034303039370D0A"),
    "cool_rapid": bytes.fromhex("353561306530393030303035303039360D0A"),
    "hot_low": bytes.fromhex("353561306530393030303036303039350D0A"),
    "hot_mid": bytes.fromhex("353561306530393030303037303039340D0A"),
    "hot_high": bytes.fromhex("353561306530393030303038303039330D0A"),
}
