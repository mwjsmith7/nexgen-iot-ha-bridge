from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import aiohttp_client

from .api import NexGenApiClient, InvalidAuth
from .coordinator import NexGenCoordinator
from .const import DOMAIN, CONF_API_URL, CONF_TOKEN

PLATFORMS = ["switch", "button", "binary_sensor", "sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = aiohttp_client.async_get_clientsession(hass)
    client = NexGenApiClient(
        api_url=entry.data[CONF_API_URL],
        token=entry.data[CONF_TOKEN],
        session=session,
    )
    coordinator = NexGenCoordinator(hass, client)
    try:
        await coordinator.async_config_entry_first_refresh()
    except InvalidAuth as err:
        raise ConfigEntryAuthFailed from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
