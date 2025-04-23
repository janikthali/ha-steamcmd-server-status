import logging
import a2s
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)

async def async_setup_platform(hass: HomeAssistant, config, async_add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType | None = None):
    host = config.get("host")
    port = config.get("port", 27015)
    name = config.get("name", "Steam Server")

    if host is None:
        _LOGGER.error("Host must be specified")
        return

    async_add_entities([SteamServerSensor(host, port, name)], True)

class SteamServerSensor(SensorEntity):
    def __init__(self, host, port, name):
        self._host = host
        self._port = port
        self._name = name
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        try:
            info = a2s.info((self._host, self._port))
            players = a2s.players((self._host, self._port))

            self._state = len(players)
            self._attributes = {
                "server_name": info.server_name,
                "map": info.map_name,
                "max_players": info.max_players,
                "game": info.game,
                "players": [player.name for player in players]
            }
        except Exception as e:
            _LOGGER.error(f"Failed to query server: {e}")
            self._state = None
            self._attributes = {}
