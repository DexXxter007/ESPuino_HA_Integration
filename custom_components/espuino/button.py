# button.py
"""Platform for ESPuino button entities."""
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import TOPIC_SLEEP_CMND # Der Befehl zum Aktivieren des Sleep-Timers/Ausschaltens
from .entity import EspuinoMqttEntity

_LOGGER = logging.getLogger(__name__)

# Der Payload, der gesendet wird, um den Sleep-Timer zu aktivieren.

PAYLOAD_ACTIVATE_SLEEP = "0"

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ESPuino buttons from a config entry."""
    entities = [
        EspuinoSleepButton(entry)
    ]
    async_add_entities(entities)


class EspuinoSleepButton(EspuinoMqttEntity, ButtonEntity):
    """Representation of an ESPuino Sleep Timer button."""

    def __init__(self, entry: ConfigEntry):
        """Initialize the button."""
        super().__init__(entry, "sleep_button") # Eindeutiger Key für die Entität
        self._attr_name = "Sleep" # Der Name, der in HA angezeigt wird
        self._attr_icon = "mdi:sleep" # Passendes Icon

        # Command-Topic Suffix
        self._command_topic_suffix = TOPIC_SLEEP_CMND

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug(
            "EspuinoSleepButton (%s) pressed, sending command to %s with payload %s",
            self.entity_id, self._command_topic_suffix, PAYLOAD_ACTIVATE_SLEEP
        )
        await self.async_publish_mqtt(self._command_topic_suffix, PAYLOAD_ACTIVATE_SLEEP)
