# ESPuino Home Assistant Integration

<img src="https://raw.githubusercontent.com/DexXxter007/ESPuino_HA_Integration/main/custom_components/espuino/icon.png" width="100" align="right" />

Integriere deinen [ESPuino](https://github.com/biologist79/ESPuino) RFID-Audioplayer vollständig in Home Assistant! Diese benutzerdefinierte Integration ermöglicht es dir, den ESPuino über MQTT direkt aus Home Assistant zu steuern und Statusinformationen zu überwachen.

---

## 🔧 Features

- Mediensteuerung (Play, Pause, Nächstes/Vorheriges Lied, Lautstärke)
- Anzeige von Titelinformationen über MQTT
- Steuerung von Sperre, Sleep-Timer und weiteren Funktionen
- UI-Integration über Config Flow
- Kompatibel mit Home Assistant 2023.x+

---

## 📦 Voraussetzungen

- Ein laufender MQTT-Broker
- Ein konfigurierter [ESPuino](https://github.com/ESPuino/ESPuino), der MQTT verwendet
- Home Assistant mit aktivierter MQTT-Integration

---

## 🚀 Installation

### Über HACS (empfohlen)

1. HACS öffnen → **Integrationen** → Drei-Punkte-Menü → **Benutzerdefiniertes Repository hinzufügen**
2. Repository-URL: `https://github.com/DexXxter007/ESPuino_HA_Integration`
3. Kategorie: `Integration`
4. Nach dem Hinzufügen: In HACS nach `ESPuino Integration` suchen und installieren
5. Home Assistant neustarten

### Manuell

1. Lade [das ZIP-Archiv](https://github.com/DexXxter007/ESPuino_HA_Integration/archive/refs/heads/main.zip) herunter
2. Entpacke es nach:  
   `<config>/custom_components/espuino/`
3. Home Assistant neustarten

---

## ⚙️ Einrichtung

Nach dem Neustart:

1. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. Suche nach **ESPuino Integratin**
3. Wähle deinen MQTT-basierten ESPuino aus oder gib die Topic-Informationen manuell ein
4. Fertig – deine Entitäten werden automatisch erstellt

---

## 🧪 Beispiel-Entitäten

Nach der Einrichtung stehen dir unter anderem folgende Entitäten zur Verfügung:

- `media_player.espuino`
- `sensor.espuino_track`
- `switch.espuino_sleep`
- `button.espuino_play_next`
- `number.espuino_volume`

---

## 🛠️ Fehlerbehebung

- **Integration wird nicht erkannt:** Stelle sicher, dass `custom_components/espuino` korrekt im config-Verzeichnis liegt
- **MQTT funktioniert nicht:** Überprüfe deine MQTT-Topics und Broker-Verbindung
- **HACS-Warnung:** Stelle sicher, dass du ein [Release mit Tag](https://github.com/DexXxter007/ESPuino_HA_Integration/releases) verwendest (`v1.0.0`, etc.)

---

## 🗒️ Changelog

### v1.0.0
- Initiale Version mit Mediensteuerung und MQTT-Support

---

## 👤 Credits

- [DexXxter007](https://github.com/DexXxter007) – Entwicklung
- [biologist79](https://github.com/biologist79/ESPuino) – ESPUino Projekt Hardware & Firmware

---

## 🪪 Lizenz

MIT License – frei zur Verwendung, Modifikation und Verbreitung.
