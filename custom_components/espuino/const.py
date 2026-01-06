DOMAIN = "espuino"
CONF_DEVICE_NAME = "device_name" # Neuer Name für die Konfiguration
CONF_FRIENDLY_NAME = "friendly_name" # Anzeigename in Home Assistant
CONF_TOPIC_PREFIX = "topic_prefix" # Optional override for the MQTT topic prefix (defaults to empty - no prefix)

DEFAULT_MQTT_TOPIC_PREFIX = "" # Default: empty (no topic prefix). Set to e.g. "media/ESP32" to use that prefix.
# Command topics will be under <prefix>/<device>/<command>/set and state topics under <prefix>/<device>/<state>


STATE_SUFFIX_LOUDNESS = "loudness"
STATE_SUFFIX_WIFI_RSSI = "wifi_rssi"
STATE_SUFFIX_RFID = "rfid"
STATE_SUFFIX_PLAYMODE = "playmode"
STATE_SUFFIX_REPEAT_MODE = "repeatmode"
STATE_SUFFIX_TRACK = "track"
STATE_SUFFIX_BATTERY_SOC = "battery_soc"
STATE_SUFFIX_BATTERY_VOLTAGE = "battery_voltage"
STATE_SUFFIX_SREVISION = "software_revision"
STATE_SUFFIX_SLEEP_TIMER = "sleep_timer"
STATE_SUFFIX_CURRENT_IP = "ipv4"
STATE_SUFFIX_ONLINE_STATE = "state" # topic for Online/Offline
STATE_SUFFIX_SLEEP_STATE = "sleep"
STATE_SUFFIX_LOCK_CONTROLS = "lock_controls"
STATE_SUFFIX_PLAYBACK_STATE = "pauseplay" # pause/play topic
STATE_SUFFIX_COVER_CHANGED = "cover_changed"
STATE_SUFFIX_LED_BRIGHTNESS = "led_brightness"

PAYLOAD_ONLINE = "Online"
PAYLOAD_OFFLINE = "Offline"

# --- Names for COMMAND topics (used under <prefix>/<device>/<command>/set) ---
TOPIC_SLEEP_CMND = "sleep"
TOPIC_RFID_CMND = "rfid"
TOPIC_TRACK_CONTROL_CMND = "trackcontrol"
TOPIC_LOUDNESS_CMND = "loudness"
TOPIC_SLEEP_TIMER_CMND = "sleep_timer"
TOPIC_LOCK_CONTROLS_CMND = "lock_controls"
TOPIC_REPEAT_MODE_CMND = "repeatmode"
TOPIC_LED_BRIGHTNESS_CMND = "led_brightness" # command to set led brightness
