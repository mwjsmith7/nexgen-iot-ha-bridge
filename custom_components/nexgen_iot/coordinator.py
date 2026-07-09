from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from datetime import timedelta

import aiohttp
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
        self._websocket_task: asyncio.Task | None = None

    def start_websocket(self) -> None:
        """Start receiving live state updates from the backend."""
        if self._websocket_task is None or self._websocket_task.done():
            self._websocket_task = self.hass.async_create_task(
                self._websocket_loop(), "NexGen IoT WebSocket"
            )

    async def async_shutdown(self) -> None:
        """Stop the live update task."""
        if self._websocket_task is None:
            return
        self._websocket_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._websocket_task
        self._websocket_task = None

    async def _websocket_loop(self) -> None:
        """Maintain the backend connection, reconnecting with bounded backoff."""
        retry_delay = 1
        while True:
            try:
                websocket = await self.client.websocket_connect()
                retry_delay = 1
                _LOGGER.debug("NexGen IoT live updates connected")
                try:
                    async for message in websocket:
                        if message.type == aiohttp.WSMsgType.TEXT:
                            self._handle_websocket_message(message.data)
                        elif message.type in (
                            aiohttp.WSMsgType.CLOSE,
                            aiohttp.WSMsgType.CLOSED,
                            aiohttp.WSMsgType.ERROR,
                        ):
                            break
                finally:
                    await websocket.close()
            except asyncio.CancelledError:
                raise
            except (aiohttp.ClientError, OSError, ValueError) as err:
                _LOGGER.warning(
                    "NexGen IoT live updates disconnected; retrying in %s seconds: %s",
                    retry_delay,
                    err,
                )

            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 30)

    def _handle_websocket_message(self, raw_message: str) -> None:
        """Merge a live backend event into coordinator data."""
        try:
            message = json.loads(raw_message)
        except (TypeError, ValueError):
            _LOGGER.debug("Ignoring invalid NexGen IoT WebSocket message")
            return

        message_type = message.get("type")
        device_id = message.get("deviceId")
        if not device_id or device_id not in self.data:
            return

        updates: dict = {}
        if message_type == "availability":
            updates["isOnline"] = message.get("status") == "online"
        elif message_type == "telemetry":
            event_data = message.get("data")
            if not isinstance(event_data, dict):
                return
            updates.update(event_data)
            field_aliases = {
                "door1State": "doorState",
                "relay1": "relay1State",
                "relay2": "relay2State",
                "tempC": "temp",
                "temperature": "temp",
            }
            for source, target in field_aliases.items():
                if source in event_data:
                    updates[target] = event_data[source]
            updates["isOnline"] = True
        else:
            return

        new_data = dict(self.data)
        new_data[device_id] = {**new_data[device_id], **updates}
        self.async_set_updated_data(new_data)

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
