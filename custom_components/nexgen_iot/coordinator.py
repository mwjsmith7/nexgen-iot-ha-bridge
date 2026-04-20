from __future__ import annotations
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NexGenApiClient, CannotConnect, InvalidAuth
from .const import UPDATE_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


class NexGenCoordinator(DataUpdateCoordinator[dict[str, dict]]):
    """Polls all device states from the NexGen IoT API."""

    def __init__(self, hass: HomeAssistant, client: NexGenApiClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="NexGen IoT",
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, dict]:
        try:
            devices = await self.client.get_devices()
        except InvalidAuth as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except CannotConnect as err:
            raise UpdateFailed(f"Cannot reach NexGen IoT API: {err}") from err

        data: dict[str, dict] = {}
        for device in devices:
            device_id: str = device["deviceId"]
            try:
                state = await self.client.get_device_state(device_id)
                data[device_id] = {**device, **state}
            except Exception:
                # Keep device in data with no state so entities remain visible
                data[device_id] = device

        return data
