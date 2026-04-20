from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
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
    entities: list[BinarySensorEntity] = []

    for device_id, device in coordinator.data.items():
        if device.get("doorStatusEnabled"):
            entities.append(NexGenDoorSensor(coordinator, device_id))

    async_add_entities(entities)


class NexGenDoorSensor(NexGenEntity, BinarySensorEntity):
    """Door/gate open-closed sensor."""

    _attr_device_class = BinarySensorDeviceClass.DOOR

    def __init__(self, coordinator: NexGenCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_door"

    @property
    def name(self) -> str:
        return f"{self._device_data.get('name', 'NexGen')} Door"

    @property
    def is_on(self) -> bool:
        return (self._device_data.get("doorState") or "").upper() == "OPEN"
