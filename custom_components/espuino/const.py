DOMAIN = "espuino"
CONF_DEVICE_NAME = "device_name" # Neuer Name für die Konfiguration
CONF_FRIENDLY_NAME = "friendly_name" # Anzeigename in Home Assistant

DEFAULT_MQTT_BASE_TOPIC = "Cmnd" # Basis für Command-Topics, z.B. Cmnd/<device_name>/...
# This will be the first segment for COMMAND topics: espuino/<device_name>/...


STATE_SUFFIX_LOUDNESS = "Loudness"
STATE_SUFFIX_WIFI_RSSI = "WifiRssi"
STATE_SUFFIX_RFID = "Rfid"
STATE_SUFFIX_PLAYMODE = "Playmode"
STATE_SUFFIX_REPEAT_MODE = "RepeatMode" 
STATE_SUFFIX_TRACK = "Track"
STATE_SUFFIX_BATTERY_SOC = "BatterySOC" # Annahme, basierend auf vorherigen Infos
STATE_SUFFIX_BATTERY_VOLTAGE = "BatteryVoltage" # Annahme
STATE_SUFFIX_SREVISION = "SoftwareRevision" # Annahme
STATE_SUFFIX_SLEEP_TIMER = "SleepTimer" # Annahme
STATE_SUFFIX_CURRENT_IP = "IP"
STATE_SUFFIX_ONLINE_STATE = "State" # Annahme für topicState (Online/Offline)
STATE_SUFFIX_SLEEP_STATE = "Sleep" # Annahme für topicSleepState (ON/OFF)
STATE_SUFFIX_LOCK_CONTROLS = "LockControls" # Annahme
STATE_SUFFIX_PLAYBACK_STATE = "PlaybackState" # Für Play, Pause, Stop Status

PAYLOAD_ONLINE = "Online"
PAYLOAD_OFFLINE = "Offline"
STATE_SUFFIX_LED_BRIGHTNESS = "LedBrightness" # Annahme

# --- Suffixes for COMMAND topics (will be prefixed with CONF_MQTT_BASE_TOPIC) ---
TOPIC_SLEEP_CMND = "Sleep"
TOPIC_RFID_CMND = "Rfid"
TOPIC_TRACK_CONTROL_CMND = "TrackControl"
TOPIC_LOUDNESS_CMND = "Loudness"
TOPIC_SLEEP_TIMER_CMND = "SleepTimer"
TOPIC_LOCK_CONTROLS_CMND = "LockControls"
TOPIC_REPEAT_MODE_CMND = "RepeatMode"
COMMAND_SUFFIX_LED_BRIGHTNESS = "LedBrightness" # Befehl zum Setzen der LED Helligkeit
