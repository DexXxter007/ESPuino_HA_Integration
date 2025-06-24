# c:\Users\claud\Desktop\espuino_integration\custom_components\espuino\switch.py
"""Platform for ESPuino switch entities."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.switch import SwitchEntity

from .const import (
    TOPIC_SLEEP_CMND,  # Ausschalt-Befehl
    STATE_SUFFIX_LOCK_CONTROLS,
    TOPIC_LOCK_CONTROLS_CMND,
    # TOPIC_SLEEP_TIMER_CMND, # Dieser ist "topicSleepTimerCmnd", wir brauchen "SleepTimer" für den Command-Pfad
)
from .entity import EspuinoMqttEntity

PAYLOAD_ON = "ON"
PAYLOAD_OFF = "OFF"
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ESPuino switches from a config entry."""
    entities = [
        # EspuinoSleepSwitch(entry) # Auskommentiert, da durch Button ersetzt
        EspuinoLockControlsSwitch(entry)
    ]
    async_add_entities(entities)




class EspuinoLockControlsSwitch(EspuinoMqttEntity, SwitchEntity):
    """Representation of an ESPuino Lock Controls switch."""

    def __init__(self, entry: ConfigEntry):
        """Initialize the switch."""
        super().__init__(entry, "lock_controls_switch")
        self._attr_name = "Tastensperre"
        self._attr_icon = "mdi:lock" # Oder mdi:lock-open

        self._state_topic_suffix = STATE_SUFFIX_LOCK_CONTROLS
        self._command_topic_suffix = TOPIC_LOCK_CONTROLS_CMND

        self._attr_is_on = None # Anfangszustand ist unbekannt

    async def async_added_to_hass(self) -> None:
        """Subscribe to MQTT events when entity is added to hass."""
        await super().async_added_to_hass()
        await self.async_subscribe_to_topic(self._state_topic_suffix, self._mqtt_message_received_state)

    @callback
    def _mqtt_message_received_state(self, msg):
        """Handle new MQTT messages for the switch state."""
        payload = msg.payload.upper() # Vereinheitlichung auf Großbuchstaben
        _LOGGER.debug(
            "EspuinoLockControlsSwitch (%s) received state: %s", self.entity_id, payload
        )
        if payload == PAYLOAD_ON:
            self._attr_is_on = True
        elif payload == PAYLOAD_OFF:
            self._attr_is_on = False
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        await self.async_publish_mqtt(self._command_topic_suffix, PAYLOAD_ON)

    async def async_turn_off(self, **kwargs) -> None:
        await self.async_publish_mqtt(self._command_topic_suffix, PAYLOAD_OFF)

    @callback
    def _clear_entity_state(self):
        self._attr_is_on = None
