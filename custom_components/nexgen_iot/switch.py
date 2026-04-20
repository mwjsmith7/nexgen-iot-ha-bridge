from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import NexGenCoordinator
from .entity import NexGenEntity


def _relay_count(device: dict) -> int:
    explicit = device.get("relayCount") or device.get("relay_count")
    if explicit is not None:
        return int(explicit)
    return 2 if device.get("relay2Enabled") else 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: NexGenCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[NexGenRelaySwitch] = []

    for device_id, device in coordinator.data.items():
        for index in range(1, _relay_count(device) + 1):
            entities.append(NexGenRelaySwitch(coordinator, device_id, index))

    async_add_entities(entities)


class NexGenRelaySwitch(NexGenEntity, SwitchEntity):
    """Represents one relay channel on a NexGen device (1-indexed to match API)."""

    def __init__(
        self, coordinator: NexGenCoordinator, device_id: str, relay_index: int
    ) -> None:
        super().__init__(coordinator, device_id)
        self._relay_index = relay_index  # 1-based
        self._attr_unique_id = f"{device_id}_relay_{relay_index}"

    @property
    def name(self) -> str:
        label = self._device_data.get(f"relay{self._relay_index}Label")
        if label:
            return label
        return f"{self._device_data.get('name', 'NexGen')} Relay {self._relay_index}"

    @property
    def is_on(self) -> bool:
        state_key = f"relay{self._relay_index}State"
        return (self._device_data.get(state_key) or "").upper() == "ON"

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.client.send_command(
            self._device_id,
            {"command": "relay", "relay": self._relay_index, "state": "on"},
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.client.send_command(
            self._device_id,
            {"command": "relay", "relay": self._relay_index, "state": "off"},
        )
        await self.coordinator.async_request_refresh()
