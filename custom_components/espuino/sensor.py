import logging
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    EntityCategory,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfElectricPotential,
)

from .const import (
    DOMAIN, # DOMAIN wird in EspuinoMqttEntity verwendet, aber hier nicht direkt
    STATE_SUFFIX_TRACK,
    STATE_SUFFIX_LOUDNESS,
    STATE_SUFFIX_BATTERY_SOC,
    STATE_SUFFIX_BATTERY_VOLTAGE,
    STATE_SUFFIX_WIFI_RSSI,
    STATE_SUFFIX_SREVISION,
    STATE_SUFFIX_PLAYMODE,
    STATE_SUFFIX_SLEEP_TIMER,
    STATE_SUFFIX_RFID,
    STATE_SUFFIX_CURRENT_IP,
    STATE_SUFFIX_LED_BRIGHTNESS, # Hinzugefügt für den Helligkeitssensor
    # STATE_SUFFIX_ONLINE_STATE, # Für Online/Offline Status, eher ein Binary Sensor
    # STATE_SUFFIX_LOCK_CONTROLS, # Eher ein Binary Sensor oder Switch-State
    # TOPIC_REPEAT_MODE_STATE, # Eher ein Select-State oder Sensor
    # TOPIC_LED_BRIGHTNESS_STATE, # Eher ein Number-State oder Sensor
)
from .entity import EspuinoMqttEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the ESPuino sensor platform."""
    entities = [
        EspuinoTrackSensor(entry),
        EspuinoLoudnessSensor(entry),
        EspuinoBatterySOCSensor(entry),
        EspuinoBatteryVoltageSensor(entry),
        EspuinoWifiRssiSensor(entry),
        EspuinoSoftwareRevisionSensor(entry),
        EspuinoPlaymodeSensor(entry),
        EspuinoSleepTimerStateSensor(entry),
        EspuinoRfidStateSensor(entry),
        EspuinoCurrentIpSensor(entry),
        EspuinoLedBrightnessStateSensor(entry), # Neuer Sensor hinzugefügt
        # Hier könnten weitere Sensoren hinzugefügt werden, z.B. für LED Helligkeit, Repeat Mode etc.
        # wenn sie als reine Sensoren und nicht als steuerbare Entitäten (Number, Select) dargestellt werden sollen.
    ]
    async_add_entities(entities)


class EspuinoTrackSensor(EspuinoMqttEntity, SensorEntity):
    """Representation of an ESPuino Track Sensor."""

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(entry, "track_state") # entity_description_key
        self._attr_name = "Track"
        self._attr_icon = "mdi:music-note"
        self._topic_suffix = STATE_SUFFIX_TRACK # Verwende den Suffix
        self._attr_native_value = None


    async def async_added_to_hass(self):
        """Subscribe to MQTT events when entity is added to hass."""
        await self.async_subscribe_to_topic(self._topic_suffix)

    @callback
    def mqtt_message_received(self, msg):
        """Handle new MQTT messages."""
        _LOGGER.debug(
            "EspuinoTrackSensor (%s) received MQTT message on topic %s: %s",
            self.entity_id, msg.topic, msg.payload
        )
        self._attr_native_value = msg.payload
        self.async_write_ha_state()


# Basisklasse für einfache Text/Zahlen-Sensoren
class EspuinoSimpleSensor(EspuinoMqttEntity, SensorEntity):
    """Base for simple ESPuino sensors that read a string/number payload."""
    def __init__(self, 
                 entry: ConfigEntry, 
                 entity_key: str, 
                 name: str, 
                 topic_suffix: str, 
                 icon: str = None, 
                 device_class: SensorDeviceClass = None, 
                 state_class: SensorStateClass = None, 
                 unit: str = None,
                 entity_category: EntityCategory = None):
        super().__init__(entry, entity_key)
        self._attr_name = name
        self._topic_suffix = topic_suffix
        if icon:
            self._attr_icon = icon
        if device_class:
            self._attr_device_class = device_class
        if state_class:
            self._attr_state_class = state_class
        if unit:
            self._attr_native_unit_of_measurement = unit
        if entity_category:
            self._attr_entity_category = entity_category
        self._attr_native_value = None

    async def async_added_to_hass(self):
        """Subscribe to MQTT events when entity is added to hass."""
        await self.async_subscribe_to_topic(self._topic_suffix)

    @callback
    def mqtt_message_received(self, msg):
        """Handle new MQTT messages."""
        _LOGGER.debug(
            "EspuinoSimpleSensor (%s) received MQTT message on topic %s: %s",
            self.entity_id, msg.topic, msg.payload
        )
        payload = msg.payload
        # Versuch, den Payload in eine Zahl umzuwandeln, falls es sich um einen numerischen Sensor handelt

        # Prüfen, ob die Attribute existieren und die entsprechenden Werte haben
        is_measurement = hasattr(self, '_attr_state_class') and \
                         self._attr_state_class == SensorStateClass.MEASUREMENT
        is_numeric_device_class = hasattr(self, '_attr_device_class') and \
                                  self._attr_device_class in [
                                      SensorDeviceClass.BATTERY,
                                      SensorDeviceClass.VOLTAGE,
                                      SensorDeviceClass.SIGNAL_STRENGTH,
                                      SensorDeviceClass.POWER_FACTOR, # Beispiel für andere numerische Klassen
                                      SensorDeviceClass.TEMPERATURE,
                                      SensorDeviceClass.HUMIDITY]

        if is_measurement or is_numeric_device_class:
            try:
                payload = float(payload)
            except ValueError:
                _LOGGER.warning(
                    "Could not convert payload to float for %s: %s", self.entity_id, payload
                )
                payload = None # Set to None if conversion fails for numeric sensors
        self._attr_native_value = payload
        _LOGGER.debug(
            "EspuinoSimpleSensor (%s) new native_value: %s", self.entity_id, self._attr_native_value
        )
        self.async_write_ha_state()

class EspuinoLoudnessSensor(EspuinoSimpleSensor):
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry, 
                         "loudness_state", 
                         "Lautstärke", 
                         STATE_SUFFIX_LOUDNESS, 
                         "mdi:volume-high", 
                         state_class=SensorStateClass.MEASUREMENT) # Lautstärke ist eine Messung

class EspuinoBatterySOCSensor(EspuinoSimpleSensor):
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry, 
                         "battery_soc", 
                         "Battery SOC", 
                         STATE_SUFFIX_BATTERY_SOC, 
                         device_class=SensorDeviceClass.BATTERY, 
                         state_class=SensorStateClass.MEASUREMENT, 
                         unit=PERCENTAGE)

class EspuinoBatteryVoltageSensor(EspuinoSimpleSensor):
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry, 
                         "battery_voltage", 
                         "Battery Voltage", 
                         STATE_SUFFIX_BATTERY_VOLTAGE, 
                         device_class=SensorDeviceClass.VOLTAGE, 
                         state_class=SensorStateClass.MEASUREMENT, 
                         unit=UnitOfElectricPotential.VOLT)

class EspuinoWifiRssiSensor(EspuinoSimpleSensor):
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry, 
                         "wifi_rssi", 
                         "WiFi RSSI", 
                         STATE_SUFFIX_WIFI_RSSI, 
                         device_class=SensorDeviceClass.SIGNAL_STRENGTH, 
                         state_class=SensorStateClass.MEASUREMENT, 
                         unit=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
                         entity_category=EntityCategory.DIAGNOSTIC)

class EspuinoSoftwareRevisionSensor(EspuinoSimpleSensor):
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry, 
                         "software_revision", 
                         "Software Revision", 
                         STATE_SUFFIX_SREVISION, 
                         "mdi:information-outline",
                         entity_category=EntityCategory.DIAGNOSTIC)

class EspuinoPlaymodeSensor(EspuinoSimpleSensor):
    def __init__(self, entry: ConfigEntry):
        # Playmode ist numerisch, aber die Bedeutung der Zahlen ist spezifisch.
        # Könnte auch als Select-Entität implementiert werden, wenn die Modi bekannt sind.
        super().__init__(entry, 
                         "playmode", 
                         "Playmode", 
                         STATE_SUFFIX_PLAYMODE, 
                         "mdi:play-box-multiple-outline")

class EspuinoSleepTimerStateSensor(EspuinoSimpleSensor):
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry, 
                         "sleep_timer_state", 
                         "Sleep Timer", 
                         STATE_SUFFIX_SLEEP_TIMER, 
                         "mdi:timer-sand")

class EspuinoRfidStateSensor(EspuinoSimpleSensor):
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry, 
                         "rfid_state", 
                         "RFID", 
                         STATE_SUFFIX_RFID, 
                         "mdi:nfc-variant")

class EspuinoCurrentIpSensor(EspuinoSimpleSensor):
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry, 
                         "current_ip", 
                         "Reported IP Address", 
                         STATE_SUFFIX_CURRENT_IP, 
                         "mdi:ip-network-outline",
                         entity_category=EntityCategory.DIAGNOSTIC)

class EspuinoLedBrightnessStateSensor(EspuinoSimpleSensor):
    def __init__(self, entry: ConfigEntry):
        super().__init__(entry,
                         "led_brightness_state",
                         "LED Brightness State",
                         STATE_SUFFIX_LED_BRIGHTNESS,
                         "mdi:brightness-6",
                         state_class=SensorStateClass.MEASUREMENT, # Helligkeit ist eine Messung
                         # Kein Unit of Measurement, da es ein Wert von 0-255 ist
                         entity_category=EntityCategory.DIAGNOSTIC) # Oder None, wenn es nicht als Diagnose gilt
