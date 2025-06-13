"""Base entity for ESPuino."""
import logging # Import the logging module
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, Entity

from homeassistant.components.mqtt import (
    async_subscribe as mqtt_async_subscribe,
    async_publish as mqtt_async_publish
)
from .const import DOMAIN, CONF_DEVICE_NAME, DEFAULT_MQTT_BASE_TOPIC

_LOGGER = logging.getLogger(__name__) # Initialize logger for this module

class EspuinoMqttEntity(Entity):
    """Base class for ESPuino MQTT entities."""

    def __init__(self, entry: ConfigEntry, entity_description_key: str):
        """Initialize the ESPuino MQTT entity."""
        self._entry = entry
        self._attr_has_entity_name = True # For newer HA versions, uses entity_description.name

        # Get the configured device name
        self._device_name = entry.data[CONF_DEVICE_NAME]

        # entry.unique_id from config_flow is now self._device_name
        # entity_description_key should be unique per entity type (e.g., "track_state", "loudness")
        self._attr_unique_id = f"{self._device_name}_{entity_description_key}"

        self._attr_extra_state_attributes = {} # Initialize extra_state_attributes

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this ESPuino device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_name)},  # Use configured device name
            name=f"ESPuino ({self._device_name})",
            manufacturer="ESPuino Community",
            # model="ESPuino vX.Y", # Could be fetched via MQTT (e.g., from SRevisionState)
            # sw_version=... # Could be fetched via MQTT
        )

    def _get_full_state_topic(self, state_topic_suffix_const: str) -> str:
        """Construct the full MQTT state topic using the configured device name."""
        # state_topic_suffix_const is one of the STATE_SUFFIX_... from const.py
        return f"State/{self._device_name}/{state_topic_suffix_const}"

    def _get_full_command_topic(self, command_topic_suffix_const: str) -> str:
        """Construct the full MQTT command topic using the fixed base 'espuino' and configured device name."""
        # command_topic_suffix_const is one of the TOPIC_..._CMND from const.py
        return f"{DEFAULT_MQTT_BASE_TOPIC}/{self._device_name}/{command_topic_suffix_const}"

    async def async_subscribe_to_topic(self, topic_suffix: str, msg_callback=None):
        """Subscribe to a specific MQTT state topic suffix (from STATE_SUFFIX_... constants)."""
        if msg_callback is None:
            msg_callback = self.mqtt_message_received
        full_topic = self._get_full_state_topic(topic_suffix)
        _LOGGER.debug(
            "Entity %s (%s) attempting to subscribe to MQTT topic: %s (using suffix: %s)",
            self.entity_id, self._attr_unique_id, full_topic, topic_suffix
        )
        # Ensure _attr_extra_state_attributes is a dict before updating
        if not isinstance(self._attr_extra_state_attributes, dict):
            self._attr_extra_state_attributes = {}
            
        self._attr_extra_state_attributes.update({"mqtt_topic": full_topic})

        # Explicitly set qos=0. Defaults for encoding will be used.
        return await mqtt_async_subscribe(self.hass, full_topic, msg_callback, qos=0)

    @callback
    def mqtt_message_received(self, msg):
        """Handle new MQTT messages. To be overridden by subclasses."""
        # This base class logger will only be hit if a subclass doesn't override
        # and calls super().mqtt_message_received() or if it's directly used.
        _LOGGER.debug(
            "EspuinoMqttEntity (%s) received base MQTT message on topic %s: %s. This should typically be handled by a subclass.",
            self.entity_id, msg.topic, msg.payload
        )
        # Default implementation, subclasses should process msg.payload
        self.async_write_ha_state()

    async def async_publish_mqtt(self, topic_suffix: str, payload: str, qos: int = 0, retain: bool = False):
        """Publish a message to an MQTT command topic suffix (from TOPIC_..._CMND constants)."""
        full_topic = self._get_full_command_topic(topic_suffix)
        await mqtt_async_publish(
            self.hass, full_topic, payload, qos, retain
        )
