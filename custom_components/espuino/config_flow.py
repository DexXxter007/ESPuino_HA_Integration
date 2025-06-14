from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.typing import DiscoveryInfoType, ConfigType
from typing import Any, Dict, Optional

import voluptuous as vol
from .const import DOMAIN, CONF_DEVICE_NAME, CONF_FRIENDLY_NAME, DEFAULT_MQTT_BASE_TOPIC

class EspuinoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            # Use the configured technical device name (for MQTT) as unique ID
            await self.async_set_unique_id(user_input[CONF_DEVICE_NAME])
            self._abort_if_unique_id_configured()

            # You could add validation here to check if the ESPuino is reachable
            # or if MQTT is correctly configured, if desired.
            # You might also want to validate the format of CONF_DEVICE_NAME (e.g., no spaces)

            return self.async_create_entry(
                title=user_input[CONF_FRIENDLY_NAME], # Use friendly name for the entry title
                data=user_input
            )

        # Prepare default values for the form
        # If user_input is None (initial form display), use empty strings or predefined defaults.
        # If user_input is not None (form re-displayed after an attempt), use previous values.
        device_name_default = "ESPunio"
        friendly_name_default = ""

        if user_input is not None:
            device_name_default = user_input.get(CONF_DEVICE_NAME, "")
            friendly_name_default = user_input.get(CONF_FRIENDLY_NAME, "")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    # Technical name for MQTT topics, should be unique
                    vol.Required(CONF_DEVICE_NAME, default=device_name_default): str,
                    # User-friendly name for display in Home Assistant
                    vol.Required(CONF_FRIENDLY_NAME, default=friendly_name_default): str,
                }
            ),
            errors=errors,
        )
