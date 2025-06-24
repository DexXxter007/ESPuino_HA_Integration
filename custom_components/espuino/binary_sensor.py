# c:\Users\claud\Desktop\espuino_integration\custom_components\espuino\binary_sensor.py
"""Platform for ESPuino binary sensor entities."""
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import EntityCategory

from .const import STATE_SUFFIX_ONLINE_STATE, PAYLOAD_ONLINE, PAYLOAD_OFFLINE
from .entity import EspuinoMqttEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ESPuino binary sensors from a config entry."""
    entities = [
        EspuinoOnlineStateBinarySensor(entry)
    ]
    async_add_entities(entities)


class EspuinoOnlineStateBinarySensor(EspuinoMqttEntity, BinarySensorEntity):
    """Representation of an ESPuino Online State binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, entry: ConfigEntry):
        """Initialize the binary sensor."""
        super().__init__(entry, "online_state")
        self._attr_name = "Status" # Oder "Verbindungsstatus"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._topic_suffix = STATE_SUFFIX_ONLINE_STATE
        self._attr_is_on = None # Initial state is unknown

    async def async_added_to_hass(self) -> None:
        """Subscribe to MQTT events when entity is added to hass."""
        # The base class `async_added_to_hass` subscribes to the online topic
        # and calls our overridden `_mqtt_device_online_state_received`.
        # We don't need to subscribe to anything else.
        await super().async_added_to_hass()

    @callback
    def _mqtt_device_online_state_received(self, msg):
        """Handle new MQTT messages for the device's online state.
        
        This overrides the base class method to set both availability and state.
        """
        payload = msg.payload
        _LOGGER.debug(
            "EspuinoOnlineStateBinarySensor (%s) received online state: %s", self.entity_id, payload
        )
        if payload == PAYLOAD_ONLINE:
            self._attr_available = True
            self._attr_is_on = True
        elif payload == PAYLOAD_OFFLINE:
            self._attr_available = False
            self._attr_is_on = False
        self.async_write_ha_state()