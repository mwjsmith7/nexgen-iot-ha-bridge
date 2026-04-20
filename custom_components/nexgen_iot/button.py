from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    entities: list[NexGenTriggerButton] = []

    for device_id, device in coordinator.data.items():
        for index in range(1, _relay_count(device) + 1):
            entities.append(NexGenTriggerButton(coordinator, device_id, index))

    async_add_entities(entities)


class NexGenTriggerButton(NexGenEntity, ButtonEntity):
    """Momentary pulse on one relay channel (3-second pulse)."""

    def __init__(self, coordinator: NexGenCoordinator, device_id: str, relay_index: int) -> None:
        super().__init__(coordinator, device_id)
        self._relay_index = relay_index
        self._attr_unique_id = f"{device_id}_relay_{relay_index}_trigger"

    @property
    def name(self) -> str:
        return f"{self._device_data.get('name', 'NexGen')} Trigger {self._relay_index}"

    async def async_press(self) -> None:
        await self.coordinator.client.send_command(
            self._device_id,
            {"command": "relay", "relay": self._relay_index, "state": "pulse", "pulse_s": 3},
        )
