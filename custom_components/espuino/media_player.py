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
    TOPIC_TRACK_CONTROL_CMND,
    TOPIC_LOUDNESS_CMND,
    # Deine State-Topic Suffixe
    STATE_SUFFIX_TRACK,
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
        # | MediaPlayerEntityFeature.VOLUME_MUTE # Wenn unterstützt
        # | MediaPlayerEntityFeature.SELECT_SOURCE # Wenn Playlists unterstützt
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
        self._attr_media_playlist_position = None # Alias für media_track
        # Weitere Attribute...

        # Topic-Konstanten direkt verwenden (wenn sie volle Pfade sind)
        self._state_suffix_track = STATE_SUFFIX_TRACK # Suffix
        self._state_suffix_loudness = STATE_SUFFIX_LOUDNESS # Suffix
        self._state_suffix_playback_state = STATE_SUFFIX_PLAYBACK_STATE # Suffix

        self._topic_track_control_cmnd = TOPIC_TRACK_CONTROL_CMND # Suffix
        self._topic_loudness_cmnd = TOPIC_LOUDNESS_CMND # Suffix


    async def async_added_to_hass(self) -> None:
        """Subscribe to MQTT events."""
        await super().async_added_to_hass() # Ruft ggf. Basis-Logik auf

        @callback
        def track_state_message_received(msg):
            payload = msg.payload
            _LOGGER.debug("MediaPlayer: Track state received on topic '%s': %s", msg.topic, payload)
            # Diese Funktion aktualisiert jetzt primär die Metadaten des Tracks.
            # Der _attr_state wird hauptsächlich durch playback_state_message_received gesetzt.
            # Dies ist der komplexe Teil ohne expliziten Playback-Status-Topic
            if payload and payload.strip(): # Prüfen, ob Payload nicht leer oder nur Whitespace ist
                # Verbessertes, aber immer noch beispielhaftes Parsen
                try:
                    # Beispiel: "(1/12): Song Title.mp3" oder "/path/to/Song Title.mp3"
                    # oder "1 - Song Title" (wenn Nummer und Titel anders getrennt sind)
                    
                    # Versuche, Track-Nummer und Gesamt-Tracks zu extrahieren, falls vorhanden
                    import re
                    match_numbers = re.match(r'\((\d+)/(\d+)\):\s*(.*)', payload)
                    
                    if match_numbers:
                        self._attr_media_track = int(match_numbers.group(1))
                        # self._attr_media_playlist_size = int(match_numbers.group(2)) # Wenn benötigt
                        remaining_payload = match_numbers.group(3)
                    else:
                        self._attr_media_track = None
                        remaining_payload = payload

                    # Extrahiere den Titel (oft der Dateiname ohne Pfad)
                    if '/' in remaining_payload:
                        self._attr_media_title = remaining_payload.split('/')[-1]
                        # Entferne .mp3 oder andere Erweiterungen, falls gewünscht
                        title_parts = self._attr_media_title.rsplit('.', 1)
                        if len(title_parts) > 1 and title_parts[1].lower() in ['mp3', 'wav', 'ogg', 'flac']:
                            self._attr_media_title = title_parts[0]
                    else:
                        self._attr_media_title = remaining_payload

                except Exception as e:
                    _LOGGER.error("Error parsing track state '%s': %s", payload, e)
                    self._attr_media_title = payload # Fallback

                # Wenn der Status IDLE war und nun Track-Infos kommen,
                # und der PlaybackState noch nicht PLAYING gemeldet hat,
                # können wir optimistisch auf PLAYING setzen.
                if self._attr_state == HA_STATE_IDLE:
                    self._attr_state = HA_STATE_PLAYING

            else: # Leerer Payload für Track
                self._attr_media_title = None
                self._attr_media_artist = None
                self._attr_media_album_name = None
                self._attr_media_track = None
                # Wenn keine Track-Info mehr da ist und der Status nicht explizit PAUSED ist,
                # dann ist es wahrscheinlich IDLE (oder der PlaybackState wird es bald bestätigen).
                if self._attr_state not in [HA_STATE_PAUSED, HA_STATE_OFF]:
                    self._attr_state = HA_STATE_IDLE
            _LOGGER.debug(
                "MediaPlayer: New media_title: %s, new media_track: %s, new state: %s",
                self._attr_media_title, self._attr_media_track, self._attr_state
            )
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

        @callback
        def playback_state_message_received(msg):
            """Handle new MQTT messages for playback state."""
            payload = msg.payload.lower() # Umwandlung in Kleinbuchstaben für einfacheren Vergleich
            _LOGGER.debug("MediaPlayer: Playback state received on topic '%s': %s", msg.topic, payload)

            new_state = None
            if payload == "playing" or payload == "play": # ESPuino könnte "play" oder "playing" senden
                new_state = HA_STATE_PLAYING
            elif payload == "paused" or payload == "pause":
                new_state = HA_STATE_PAUSED
            elif payload == "stopped" or payload == "stop" or payload == "idle":
                new_state = HA_STATE_IDLE
                # Bei "stopped" oder "idle" auch Metadaten löschen
                self._attr_media_title = None
                self._attr_media_artist = None
                self._attr_media_album_name = None
                self._attr_media_track = None
            else:
                _LOGGER.warning("MediaPlayer: Unknown playback state payload: %s", msg.payload)
                return # Nichts tun bei unbekanntem Payload

            if self._attr_state != new_state:
                self._attr_state = new_state
                _LOGGER.debug("MediaPlayer: New playback state: %s", self._attr_state)
                self.async_write_ha_state()

        # Abonnieren der State-Topics
        # async_subscribe_to_topic erwartet jetzt den Suffix (STATE_SUFFIX_...)
        await self.async_subscribe_to_topic(self._state_suffix_track, track_state_message_received)
        await self.async_subscribe_to_topic(self._state_suffix_loudness, loudness_state_message_received)
        await self.async_subscribe_to_topic(self._state_suffix_playback_state, playback_state_message_received)
        
        # Wenn du mqtt_async_subscribe direkt verwenden würdest, müsstest du den vollen Topic hier bauen:
        # full_track_topic = self._get_full_state_topic(self._state_suffix_track)
        # await mqtt_async_subscribe(self.hass, full_track_topic, track_state_message_received)


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

    # Weitere Methoden wie async_mute_volume, async_select_source etc.
    # müssten implementiert werden, wenn _attr_supported_features dies anzeigt.
