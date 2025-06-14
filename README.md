# ESPuino Home Assistant Integration

<img src="https://raw.githubusercontent.com/DexXxter007/ESPuino_HA_Integration/main/custom_components/espuino/icon.png" width="100" align="right" />

Fully integrate your [ESPuino](https://github.com/biologist79/ESPuino) RFID audio player into Home Assistant!  
This custom integration lets you control ESPuino via MQTT and monitor its status directly from Home Assistant.

---

## 🔧 Features

- Media control (play, pause, next/previous track, volume)
- Display current track information via MQTT
- Control lock, sleep timer, and other functions
- UI integration via Config Flow
- Compatible with Home Assistant 2023.x+

---

## 📦 Requirements

- A running MQTT broker
- A properly configured [ESPuino](https://github.com/biologist79/ESPuino) device with MQTT enabled
- Home Assistant with MQTT integration set up

---

## 🚀 Installation

### Via HACS (recommended)

1. Open HACS → **Integrations** → Three-dot menu → **Custom repositories**
2. Add the repository: `https://github.com/DexXxter007/ESPuino_HA_Integration`
3. Category: `Integration`
4. After adding, search for `ESPuino Integration` in HACS and install it
5. Restart Home Assistant

### Manual Installation

1. Download the [ZIP archive](https://github.com/DexXxter007/ESPuino_HA_Integration/archive/refs/heads/main.zip)
2. Extract it into:  
   `<config>/custom_components/espuino/`
3. Restart Home Assistant

---

## ⚙️ Setup

After restarting Home Assistant:

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **ESPuino Integration**
3. Select your MQTT-enabled ESPuino or enter the MQTT topic details manually
4. You're done – entities will be created automatically

---

## 🧪 Example Entities

Once set up, the following entities will be available:

- `media_player.espuino`
- `sensor.espuino_track`
- `switch.espuino_sleep`
- `button.espuino_play_next`
- `number.espuino_volume`

---

## 🛠️ Troubleshooting

- **Integration not found:** Make sure `custom_components/espuino` exists in your config folder
- **MQTT not working:** Check your MQTT topics and broker connection
- **HACS warning:** Ensure you're using a [tagged release](https://github.com/DexXxter007/ESPuino_HA_Integration/releases) (`v1.0.0`, etc.)

---

## 🗒️ Changelog

### v1.0.0
- Initial release with media player support and MQTT integration

---

## 👤 Credits

- [DexXxter007](https://github.com/DexXxter007) – Development
- [biologist79](https://github.com/biologist79/ESPuino) – ESPuino project (hardware & firmware)

---

## 🪪 License

MIT License – free to use, modify, and distribute.
