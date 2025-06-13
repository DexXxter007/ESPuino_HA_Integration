"""ESPuino Integration."""
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

# PLATFORMS = ["sensor", "button", "switch", "number", "select", "binary_sensor", "text"] # Füge hier neue Plattformen hinzu
# Lade nur Plattformen, für die auch .py Dateien existieren.
PLATFORMS = ["sensor", "media_player", "button", "switch", "number", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ESPuino from a config entry."""
    # Speichere die Entry-Daten zentral, falls von Plattformen benötigt, die nicht direkt die Entry bekommen
    # hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data

    # Forward setup to all platforms.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload components in reverse order of setup or as defined in PLATFORMS
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # if unload_ok:
    # hass.data[DOMAIN].pop(entry.entry_id) # Entferne die Daten, falls gespeichert

    return unload_ok
