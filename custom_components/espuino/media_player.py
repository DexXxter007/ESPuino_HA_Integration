# custom_components/espuino/media_player.py
import logging

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState, # Ab HA 2025.1, vorher STATE_... direkt
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    # Deine Cmnd-Topics
    TOPIC_SLEEP_CMND,
    TOPIC_TRACK_CONTROL_CMND,
    TOPIC_LOUDNESS_CMND,
    # Deine State-Topic Suffixe
    STATE_SUFFIX_TRACK, # Hinzugefügt
    STATE_SUFFIX_LOUDNESS,
    STATE_SUFFIX_PLAYBACK_STATE, # Jetzt aus const.py
)
from .entity import EspuinoMqttEntity # Deine Basis-Entität

from homeassistant.components.mqtt import async_subscribe as mqtt_async_subscribe # Import here

_LOGGER = logging.getLogger(__name__)

# Versuche, die neuen Enums zu importieren, falle auf alte Konstanten zurück
try:
    from homeassistant.components.media_player import MediaPlayerState
    HA_STATE_PLAYING = MediaPlayerState.PLAYING
    HA_STATE_PAUSED = MediaPlayerState.PAUSED
    HA_STATE_IDLE = MediaPlayerState.IDLE
    HA_STATE_OFF = MediaPlayerState.OFF
except ImportError:
    from homeassistant.components.media_player import (
        STATE_PLAYING as HA_STATE_PLAYING,
        STATE_PAUSED as HA_STATE_PAUSED,
        STATE_IDLE as HA_STATE_IDLE,
        STATE_OFF as HA_STATE_OFF,
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ESPuino media_player from a config entry."""
    # Hier würdest du deine ESPuinoMediaPlayer-Instanz erstellen
    # und ggf. den ConfigEntry übergeben, um an den MQTT-Basis-Topic zu kommen
    # oder wenn die Topics fest sind, wie in deinem letzten Vorschlag,
    # dann werden sie direkt aus const.py verwendet.
    player = EspuinoMediaPlayer(entry)
    async_add_entities([player])


class EspuinoMediaPlayer(EspuinoMqttEntity, MediaPlayerEntity):
    """Representation of an ESPuino Media Player."""

    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.TURN_OFF  # <--- HIER HINZUFÜGEN
    )

    def __init__(self, entry: ConfigEntry):
        """Initialize the media player."""
        super().__init__(entry, "media_player") # Eindeutiger Key für die Entität
        self._attr_name = "ESPuino Player" # Oder dynamisch aus Config
        self._attr_state = HA_STATE_IDLE # Anfangszustand
        self._attr_volume_level = 0.5 # Anfangszustand (0.0 bis 1.0)
        self._attr_media_title = None
        self._attr_media_artist = None # Wenn verfügbar
        self._attr_media_album_name = None # Wenn verfügbar
        self._attr_media_track = None # Aktuelle Tracknummer
        # Weitere Attribute...

        # Topic-Konstanten direkt verwenden (wenn sie volle Pfade sind)
        self._state_suffix_track = STATE_SUFFIX_TRACK # Suffix
        self._state_suffix_loudness = STATE_SUFFIX_LOUDNESS # Suffix
        self._state_suffix_playback_state = STATE_SUFFIX_PLAYBACK_STATE # Suffix

        self._topic_track_control_cmnd = TOPIC_TRACK_CONTROL_CMND # Suffix
        self._topic_loudness_cmnd = TOPIC_LOUDNESS_CMND # Suffix
        self._topic_sleep_cmnd = TOPIC_SLEEP_CMND # Suffix für den Ausschalt-Befehl


    async def async_added_to_hass(self) -> None:
        """Subscribe to MQTT events."""
        await super().async_added_to_hass() # Ruft ggf. Basis-Logik auf

        @callback
        def playback_state_message_received(msg):
            """Handle new MQTT messages for playback state."""
            payload = msg.payload.lower() # Umwandlung in Kleinbuchstaben für einfacheren Vergleich
            _LOGGER.debug("MediaPlayer: Playback state received on topic '%s': %s", msg.topic, payload)

            new_state = None
            if payload == "playing" or payload == "play":
                new_state = HA_STATE_PLAYING
            elif payload == "paused" or payload == "pause":
                new_state = HA_STATE_PAUSED
            elif payload == "stopped" or payload == "stop" or payload == "idle":
                new_state = HA_STATE_IDLE
            else:
                _LOGGER.warning("MediaPlayer: Unknown playback state payload: %s", msg.payload)
                return 

            self._update_state(new_state)

        @callback
        def track_state_message_received(msg):
            payload = msg.payload
            _LOGGER.debug("MediaPlayer: Track state received on topic '%s': %s", msg.topic, payload)
            
            local_changes_made = False # Flag, um zu verfolgen, ob Metadaten direkt geändert wurden

            # Diese Funktion aktualisiert jetzt primär die Metadaten des Tracks.
            # Der _attr_state wird hauptsächlich durch playback_state_message_received gesetzt.
            # Dies ist der komplexe Teil ohne expliziten Playback-Status-Topic
            if payload and payload.strip(): # Prüfen, ob Payload nicht leer oder nur Whitespace ist
                # Verbessertes, aber immer noch beispielhaftes Parsen
                try:
                    # Beispiel: "(1/12): Song Title.mp3" oder "/path/to/Song Title.mp3"
                    # oder "1 - Song Title" (wenn Nummer und Titel anders getrennt sind)
                    
                    # Alte Werte speichern, um tatsächliche Änderungen zu erkennen
                    # old_media_title = self._attr_media_title # Nicht direkt benötigt, da wir direkt vergleichen
                    # old_media_track = self._attr_media_track # Nicht direkt benötigt

                    # Versuche, Track-Nummer und Gesamt-Tracks zu extrahieren, falls vorhanden
                    import re
                    match_numbers = re.match(r'\((\d+)/(\d+)\):\s*(.*)', payload)
                    
                    if match_numbers:
                        new_track_val = int(match_numbers.group(1))
                        if self._attr_media_track != new_track_val:
                            self._attr_media_track = new_track_val
                            local_changes_made = True
                        # self._attr_media_playlist_size = int(match_numbers.group(2)) # Wenn benötigt
                        remaining_payload = match_numbers.group(3)
                    else:
                        # Wenn keine Track-Nummer im Payload, aber vorher eine da war, zurücksetzen
                        if self._attr_media_track is not None:
                            self._attr_media_track = None
                            local_changes_made = True
                        remaining_payload = payload

                    # Extrahiere den Titel (oft der Dateiname ohne Pfad)
                    new_title_val = self._attr_media_title # Behalte alten Titel, falls nicht geändert
                    if '/' in remaining_payload:
                        new_title_val = remaining_payload.split('/')[-1]
                        # Entferne .mp3 oder andere Erweiterungen, falls gewünscht
                        title_parts = new_title_val.rsplit('.', 1)
                        if len(title_parts) > 1 and title_parts[1].lower() in ['mp3', 'wav', 'ogg', 'flac']:
                            new_title_val = title_parts[0]
                    else:
                        new_title_val = remaining_payload
                    
                    if self._attr_media_title != new_title_val:
                        self._attr_media_title = new_title_val
                        local_changes_made = True

                except Exception as e:
                    _LOGGER.error("Error parsing track state '%s': %s", payload, e)
                    # Fallback: Setze rohen Payload als Titel, wenn Parsing fehlschlägt und Titel sich ändert
                    if self._attr_media_title != payload:
                        self._attr_media_title = payload
                        local_changes_made = True
                
            else: # Leerer Payload für Track
                # Metadaten löschen, wenn sie vorher gesetzt waren
                if self._attr_media_title is not None: self._attr_media_title = None; local_changes_made = True
                if self._attr_media_artist is not None: self._attr_media_artist = None; local_changes_made = True # Auch wenn nicht oben geparst, sicherheitshalber
                if self._attr_media_album_name is not None: self._attr_media_album_name = None; local_changes_made = True # dito
                if self._attr_media_track is not None: self._attr_media_track = None; local_changes_made = True
                
                if self._attr_state not in [HA_STATE_PAUSED, HA_STATE_OFF]:
                    # Diese Methode kümmert sich um Statusänderung, Metadaten-Löschung, Cover-URL und async_write_ha_state
                    self._update_state(HA_STATE_IDLE)
                    return # Callback hier beenden, da _update_state_and_cover alles erledigt hat

            # Wenn in diesem Callback Änderungen vorgenommen wurden (und _update_state_and_cover nicht aufgerufen wurde),
            # dann den Home Assistant Status aktualisieren.
            if local_changes_made:
                self.async_write_ha_state()

        @callback
        def loudness_state_message_received(msg):
            payload = msg.payload
            _LOGGER.debug("MediaPlayer: Loudness state received on topic '%s': %s", msg.topic, payload)
            try:
                # ESPuino sendet 0-21, HA erwartet 0.0-1.0
                new_volume = min(1.0, max(0.0, int(payload) / 21.0))
                self._attr_volume_level = new_volume
                _LOGGER.debug("MediaPlayer: New volume_level: %s", self._attr_volume_level)
            except ValueError:
                _LOGGER.warning("MediaPlayer: Invalid loudness payload: %s", payload)
            except Exception as e:
                _LOGGER.error("MediaPlayer: Error processing loudness: %s", e)
            self.async_write_ha_state()

        # Abonnieren der State-Topics
        # async_subscribe_to_topic erwartet jetzt den Suffix (STATE_SUFFIX_...)
        await self.async_subscribe_to_topic(self._state_suffix_track, track_state_message_received)
        await self.async_subscribe_to_topic(self._state_suffix_loudness, loudness_state_message_received)
        await self.async_subscribe_to_topic(self._state_suffix_playback_state, playback_state_message_received)

    def _update_state(self, new_state: MediaPlayerState | None):
        """Update player state and associated metadata."""
        state_changed = False
        if new_state is not None and self._attr_state != new_state:
            self._attr_state = new_state
            _LOGGER.debug("MediaPlayer: New playback state: %s", self._attr_state)
            state_changed = True

        # Metadaten löschen, wenn der Zustand IDLE oder OFF ist
        if self._attr_state in [HA_STATE_IDLE, HA_STATE_OFF]:
            if self._attr_media_title is not None: # Nur löschen und loggen, wenn vorher was da war
                self._attr_media_title = None
                self._attr_media_artist = None
                self._attr_media_album_name = None
                self._attr_media_track = None
                _LOGGER.debug("MediaPlayer: Cleared media metadata due to state %s", self._attr_state)
                state_changed = True # Auch Metadatenänderung erfordert ein Update

        if state_changed:
            self.async_write_ha_state()

    @callback
    def _clear_entity_state(self):
        """Clear the media player's state attributes when the device goes offline."""
        _LOGGER.debug("MediaPlayer: Clearing entity state for %s due to device offline.", self.entity_id)
        self._attr_state = HA_STATE_OFF
        self._attr_volume_level = None # Reset volume to unknown
        self._attr_media_title = None
        self._attr_media_artist = None
        self._attr_media_album_name = None
        self._attr_media_track = None

    @callback
    def _restore_entity_state(self):
        """Restore the media player's state when the device comes online."""
        # If the player was OFF (because it was unavailable or turned off),
        # set it to IDLE. It will then update to PLAYING/PAUSED when a
        # playback state message is received.
        if self._attr_state == HA_STATE_OFF:
            self._attr_state = HA_STATE_IDLE


    # --- Implementierung der MediaPlayerEntity-Methoden ---
    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        # Konvertiere HA-Volumen (0.0-1.0) in ESPuino-Volumen (0-21)
        # int(x + 0.5) rundet .5 immer auf, was oft intuitiver ist.
        # Stelle sicher, dass das Ergebnis im Bereich 0-21 bleibt.
        espuino_volume = max(0, min(21, int(volume * 21 + 0.5)))
        _LOGGER.debug("Setting ESPuino volume to: %s (from HA: %s)", espuino_volume, volume)
        await self.async_publish_mqtt(self._topic_loudness_cmnd, str(espuino_volume)) # Suffix hier

    async def async_media_play(self) -> None:
        """Send play command."""
        await self.async_publish_mqtt(self._topic_track_control_cmnd, "3") # 3 = Play/Pause
        # Optimistisch den Status setzen oder auf Bestätigung via MQTT warten
        # self._attr_state = HA_STATE_PLAYING
        # self.async_write_ha_state()

    async def async_media_pause(self) -> None:
        """Send pause command."""
        await self.async_publish_mqtt(self._topic_track_control_cmnd, "3") # 3 = Play/Pause
        # self._attr_state = HA_STATE_PAUSED
        # self.async_write_ha_state()

    async def async_media_stop(self) -> None:
        """Send stop command."""
        await self.async_publish_mqtt(self._topic_track_control_cmnd, "1") # 1 = Stop
        # self._attr_state = HA_STATE_IDLE
        # self.async_write_ha_state()

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self.async_publish_mqtt(self._topic_track_control_cmnd, "4") # 4 = Next

    async def async_media_previous_track(self) -> None:
        """Send previous track command."""
        await self.async_publish_mqtt(self._topic_track_control_cmnd, "5") # 5 = Previous

    async def async_turn_off(self) -> None:
        """Schaltet den Player aus (sendet MQTT-Befehl)."""
        await self.async_publish_mqtt(self._topic_sleep_cmnd, "0")  # Beispiel: "1" = Stop/Aus
        # Optional: Status direkt setzen, falls keine Rückmeldung per MQTT kommt
        self._attr_state = HA_STATE_OFF
        self.async_write_ha_state()

    # Weitere Methoden wie async_mute_volume, async_select_source etc.
    # müssten implementiert werden, wenn _attr_supported_features dies anzeigt.
