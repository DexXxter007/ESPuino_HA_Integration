from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.typing import DiscoveryInfoType, ConfigType
from typing import Any, Dict, Optional

import voluptuous as vol
from .const import DOMAIN, CONF_DEVICE_NAME, DEFAULT_MQTT_BASE_TOPIC

class EspuinoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            # Use the configured device name as unique ID for this config entry
            await self.async_set_unique_id(user_input[CONF_DEVICE_NAME])
            self._abort_if_unique_id_configured()

            # You could add validation here to check if the ESPuino is reachable
            # or if MQTT is correctly configured, if desired.

            return self.async_create_entry(
                title=f"ESPuino ({user_input[CONF_DEVICE_NAME]})",
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_NAME): str,
                }
            ),
            errors=errors,
        )
