from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    entities: list[NexGenTriggerButton] = []

    for device_id, device in coordinator.data.items():
        if device.get("triggerEnabled") or device.get("hasTrigger"):
            entities.append(NexGenTriggerButton(coordinator, device_id))

    async_add_entities(entities)


class NexGenTriggerButton(NexGenEntity, ButtonEntity):
    """Momentary trigger button (e.g. door bell / gate pulse)."""

    def __init__(self, coordinator: NexGenCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_trigger"

    @property
    def name(self) -> str:
        return f"{self._device_data.get('name', 'NexGen')} Trigger"

    async def async_press(self) -> None:
        await self.coordinator.client.send_command(
            self._device_id,
            {"trigger": True},
        )
