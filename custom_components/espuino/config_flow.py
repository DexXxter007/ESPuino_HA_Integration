from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.typing import DiscoveryInfoType, ConfigType
from typing import Any, Dict, Optional

import logging
import voluptuous as vol
from .const import DOMAIN, CONF_DEVICE_NAME, CONF_FRIENDLY_NAME, CONF_TOPIC_PREFIX, DEFAULT_MQTT_TOPIC_PREFIX
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import device_registry as dr

_LOGGER = logging.getLogger(__name__)

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
        device_name_default = "ESPuino"
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
                    # Optional topic prefix override (e.g., media/ESP32)
                    vol.Optional(CONF_TOPIC_PREFIX, default=DEFAULT_MQTT_TOPIC_PREFIX): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Return an options flow handler for this config entry."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for the ESPuino integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        # Avoid assigning to the base class' `config_entry` attribute which may be a read-only property.
        self._config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> config_entries.FlowResult:
        """Manage the options flow."""
        try:
            if user_input is not None:
                # Validate device_name uniqueness against other entries
                new_device = user_input.get(CONF_DEVICE_NAME, "").strip()
                for entry in self.hass.config_entries.async_entries(DOMAIN):
                    if entry.entry_id == self._config_entry.entry_id:
                        continue
                    if entry.data.get(CONF_DEVICE_NAME) == new_device:
                        return self.async_show_form(
                            step_id="init",
                            data_schema=vol.Schema(
                                {
                                    vol.Required(CONF_DEVICE_NAME, default=new_device): str,
                                    vol.Required(CONF_FRIENDLY_NAME, default=user_input.get(CONF_FRIENDLY_NAME, "")): str,
                                    vol.Optional(CONF_TOPIC_PREFIX, default=user_input.get(CONF_TOPIC_PREFIX, DEFAULT_MQTT_TOPIC_PREFIX)): str,
                                }
                            ),
                            errors={CONF_DEVICE_NAME: "already_configured"},
                        )

                # Persist data and options: update data (device_name/friendly_name) and options (topic_prefix)
                old_device = self._config_entry.data.get(CONF_DEVICE_NAME)

                new_data = dict(self._config_entry.data)
                new_data[CONF_DEVICE_NAME] = user_input.get(CONF_DEVICE_NAME, new_data.get(CONF_DEVICE_NAME)).strip()
                new_data[CONF_FRIENDLY_NAME] = user_input.get(CONF_FRIENDLY_NAME, new_data.get(CONF_FRIENDLY_NAME))

                # Normalize topic prefix: trim whitespace and any leading/trailing slashes
                raw_prefix = user_input.get(CONF_TOPIC_PREFIX, self._config_entry.options.get(CONF_TOPIC_PREFIX, DEFAULT_MQTT_TOPIC_PREFIX))
                if raw_prefix is None:
                    normalized_prefix = DEFAULT_MQTT_TOPIC_PREFIX
                else:
                    normalized_prefix = raw_prefix.strip().strip('/')
                    if normalized_prefix == "":
                        normalized_prefix = DEFAULT_MQTT_TOPIC_PREFIX

                new_options = dict(self._config_entry.options)
                new_options[CONF_TOPIC_PREFIX] = normalized_prefix

                # If the device name changed, migrate entity unique_ids and device registry identifiers so
                # Home Assistant renames the existing entities/devices instead of creating new ones.
                new_device = new_data.get(CONF_DEVICE_NAME)
                if new_device and old_device and new_device != old_device:
                    try:
                        entity_registry = er.async_get(self.hass)
                        # Iterate over all entries and migrate those belonging to this config entry
                        for ent in list(entity_registry.entities.values()):
                            if ent.config_entry_id != self._config_entry.entry_id:
                                continue
                            if ent.unique_id and ent.unique_id.startswith(f"{old_device}_"):
                                new_unique_id = ent.unique_id.replace(f"{old_device}_", f"{new_device}_", 1)
                                entity_registry.async_update_entity(ent.entity_id, new_unique_id=new_unique_id)
                                _LOGGER.info("Migrated entity unique_id %s -> %s", ent.unique_id, new_unique_id)

                        device_registry = dr.async_get(self.hass)
                        device = device_registry.async_get_device(identifiers={(DOMAIN, old_device)})
                        if device:
                            device_registry.async_update_device(device.id, new_identifiers={(DOMAIN, new_device)})
                            _LOGGER.info("Updated device registry identifiers %s -> %s", old_device, new_device)

                        # Also update the config entry unique_id to match the new device name
                        self.hass.config_entries.async_update_entry(self._config_entry, unique_id=new_device)
                    except Exception as err:
                        _LOGGER.exception("Error migrating device/entities for rename %s -> %s: %s", old_device, new_device, err)

                # Apply updates
                self.hass.config_entries.async_update_entry(
                    self._config_entry, data=new_data, options=new_options
                )
                _LOGGER.info("Updated ESPuino config entry %s: device_name=%s, topic_prefix=%s", self._config_entry.entry_id, new_data.get(CONF_DEVICE_NAME), new_options.get(CONF_TOPIC_PREFIX))

                # Refresh local reference to the updated entry and reload
                updated_entry = self.hass.config_entries.async_get_entry(self._config_entry.entry_id)
                if updated_entry is not None:
                    self._config_entry = updated_entry

                await self.hass.config_entries.async_reload(self._config_entry.entry_id)

                # Return an options create_entry that contains the saved options so the options store matches what we saved
                return self.async_create_entry(title="", data={CONF_TOPIC_PREFIX: new_options.get(CONF_TOPIC_PREFIX, DEFAULT_MQTT_TOPIC_PREFIX)})

            # Safely compute the current values for display in the form
            current_prefix = self._config_entry.options.get(
                CONF_TOPIC_PREFIX,
                self._config_entry.data.get(CONF_TOPIC_PREFIX, DEFAULT_MQTT_TOPIC_PREFIX),
            )
            current_device = self._config_entry.data.get(CONF_DEVICE_NAME, "")
            current_friendly = self._config_entry.data.get(CONF_FRIENDLY_NAME, "")

            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_DEVICE_NAME, default=current_device): str,
                        vol.Required(CONF_FRIENDLY_NAME, default=current_friendly): str,
                        vol.Optional(CONF_TOPIC_PREFIX, default=current_prefix): str,
                    }
                ),
            )
        except Exception as err:  # Defensive: don't let exceptions bubble up to HA resulting in HTTP 500
            _LOGGER.exception("Error showing options flow for %s: %s", getattr(self._config_entry, "entry_id", "unknown"), err)
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_DEVICE_NAME, default=self._config_entry.data.get(CONF_DEVICE_NAME, "")): str,
                        vol.Required(CONF_FRIENDLY_NAME, default=self._config_entry.data.get(CONF_FRIENDLY_NAME, "")): str,
                        vol.Optional(CONF_TOPIC_PREFIX, default=DEFAULT_MQTT_TOPIC_PREFIX): str,
                    }
                ),
                errors={"base": "unknown"},
            )



