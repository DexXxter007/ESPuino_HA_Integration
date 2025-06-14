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

from .const import STATE_SUFFIX_ONLINE_STATE
from .entity import EspuinoMqttEntity

_LOGGER = logging.getLogger(__name__)

PAYLOAD_ONLINE = "Online"
PAYLOAD_OFFLINE = "Offline"

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
        await super().async_added_to_hass()
        await self.async_subscribe_to_topic(self._topic_suffix, self._mqtt_message_received_state)

    @callback
    def _mqtt_message_received_state(self, msg):
        """Handle new MQTT messages for the binary sensor state."""
        payload = msg.payload
        _LOGGER.debug(
            "EspuinoOnlineStateBinarySensor (%s) received state: %s", self.entity_id, payload
        )
        if payload == PAYLOAD_ONLINE:
            self._attr_is_on = True
        elif payload == PAYLOAD_OFFLINE:
            self._attr_is_on = False
        self.async_write_ha_state()
