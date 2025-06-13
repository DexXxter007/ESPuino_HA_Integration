# c:\Users\claud\Desktop\espuino_integration\custom_components\espuino\number.py
"""Platform for ESPuino number entities."""
import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    STATE_SUFFIX_LED_BRIGHTNESS,
    COMMAND_SUFFIX_LED_BRIGHTNESS,
)
from .entity import EspuinoMqttEntity

_LOGGER = logging.getLogger(__name__)

DEFAULT_MIN_BRIGHTNESS = 0
DEFAULT_MAX_BRIGHTNESS = 255
DEFAULT_STEP_BRIGHTNESS = 1

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ESPuino numbers from a config entry."""
    entities = [
        EspuinoLedBrightnessNumber(entry)
    ]
    async_add_entities(entities)


class EspuinoLedBrightnessNumber(EspuinoMqttEntity, NumberEntity):
    """Representation of an ESPuino LED Brightness number entity."""

    _attr_mode = NumberMode.SLIDER  # Oder NumberMode.BOX

    def __init__(self, entry: ConfigEntry):
        """Initialize the number entity."""
        super().__init__(entry, "led_brightness") # Eindeutiger Key
        self._attr_name = "LED Brightness"
        self._attr_icon = "mdi:brightness-6"

        self._state_topic_suffix = STATE_SUFFIX_LED_BRIGHTNESS
        self._command_topic_suffix = COMMAND_SUFFIX_LED_BRIGHTNESS

        self._attr_native_min_value = DEFAULT_MIN_BRIGHTNESS
        self._attr_native_max_value = DEFAULT_MAX_BRIGHTNESS
        self._attr_native_step = DEFAULT_STEP_BRIGHTNESS
        # Kein _attr_native_unit_of_measurement für Helligkeit 0-255

        self._attr_native_value = None # Anfangswert ist unbekannt

    async def async_added_to_hass(self) -> None:
        """Subscribe to MQTT events when entity is added to hass."""
        await super().async_added_to_hass()
        await self.async_subscribe_to_topic(self._state_topic_suffix, self._mqtt_message_received_state)

    @callback
    def _mqtt_message_received_state(self, msg):
        """Handle new MQTT messages for the number state."""
        payload = msg.payload
        _LOGGER.debug(
            "EspuinoLedBrightnessNumber (%s) received state MQTT message on topic %s: %s",
            self.entity_id, msg.topic, payload
        )
        try:
            self._attr_native_value = int(float(payload)) # Sicherstellen, dass es eine Ganzzahl ist
        except ValueError:
            _LOGGER.warning(
                "Invalid payload for %s: %s. Expected a number.", self.entity_id, payload
            )
            self._attr_native_value = None # Zustand ist unklar
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        payload = str(int(value)) # ESPuino erwartet einen Integer-String
        await self.async_publish_mqtt(self._command_topic_suffix, payload)