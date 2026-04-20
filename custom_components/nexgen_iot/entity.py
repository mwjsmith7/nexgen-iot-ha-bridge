from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NexGenCoordinator


class NexGenEntity(CoordinatorEntity[NexGenCoordinator]):
    """Base entity for all NexGen IoT entities."""

    def __init__(self, coordinator: NexGenCoordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._device_id = device_id

    @property
    def _device_data(self) -> dict:
        return self.coordinator.data.get(self._device_id, {})

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and self._device_data.get(
            "isOnline", True
        )

    @property
    def device_info(self) -> DeviceInfo:
        data = self._device_data
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=data.get("name", f"NexGen {self._device_id}"),
            manufacturer="NexGen IoT",
            model=data.get("deviceType", "Smart Device"),
        )
