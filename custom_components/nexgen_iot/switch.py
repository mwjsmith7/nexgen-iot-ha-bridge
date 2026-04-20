from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import NexGenCoordinator
from .entity import NexGenEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: NexGenCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[NexGenRelaySwitch] = []

    for device_id, device in coordinator.data.items():
        relay_count = device.get("relayCount", 0)
        for index in range(relay_count):
            entities.append(NexGenRelaySwitch(coordinator, device_id, index))

    async_add_entities(entities)


class NexGenRelaySwitch(NexGenEntity, SwitchEntity):
    """Represents one relay channel on a NexGen device."""

    def __init__(
        self, coordinator: NexGenCoordinator, device_id: str, relay_index: int
    ) -> None:
        super().__init__(coordinator, device_id)
        self._relay_index = relay_index
        self._attr_unique_id = f"{device_id}_relay_{relay_index}"

    @property
    def name(self) -> str:
        data = self._device_data
        relays: list[dict] = data.get("relays", [])
        if relay_index_data := (relays[self._relay_index] if self._relay_index < len(relays) else None):
            label = relay_index_data.get("label") or relay_index_data.get("name")
            if label:
                return label
        return f"{data.get('name', 'NexGen')} Relay {self._relay_index + 1}"

    @property
    def is_on(self) -> bool:
        relays: list[dict] = self._device_data.get("relays", [])
        if self._relay_index < len(relays):
            return bool(relays[self._relay_index].get("state", False))
        return False

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.client.send_command(
            self._device_id,
            {"relay": self._relay_index, "state": True},
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.client.send_command(
            self._device_id,
            {"relay": self._relay_index, "state": False},
        )
        await self.coordinator.async_request_refresh()
