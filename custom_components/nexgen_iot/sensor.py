from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature, CONCENTRATION_PARTS_PER_MILLION
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
    entities: list[SensorEntity] = []

    for device_id, device in coordinator.data.items():
        if device.get("tempEnabled") or device.get("hasTemp"):
            entities.append(NexGenTemperatureSensor(coordinator, device_id))
        if device.get("humidityEnabled") or device.get("hasHumidity"):
            entities.append(NexGenHumiditySensor(coordinator, device_id))
        if device.get("aqEnabled") or device.get("airQualityEnabled"):
            entities.append(NexGenAQISensor(coordinator, device_id))
            entities.append(NexGenCO2Sensor(coordinator, device_id))

    async_add_entities(entities)


class NexGenTemperatureSensor(NexGenEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: NexGenCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_temperature"

    @property
    def name(self) -> str:
        return f"{self._device_data.get('name', 'NexGen')} Temperature"

    @property
    def native_value(self) -> float | None:
        val = self._device_data.get("temperature")
        return float(val) if val is not None else None


class NexGenHumiditySensor(NexGenEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: NexGenCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_humidity"

    @property
    def name(self) -> str:
        return f"{self._device_data.get('name', 'NexGen')} Humidity"

    @property
    def native_value(self) -> float | None:
        val = self._device_data.get("humidity")
        return float(val) if val is not None else None


class NexGenAQISensor(NexGenEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.AQI
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: NexGenCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_aqi"

    @property
    def name(self) -> str:
        return f"{self._device_data.get('name', 'NexGen')} Air Quality"

    @property
    def native_value(self) -> int | None:
        val = self._device_data.get("aqi") or self._device_data.get("airQuality")
        return int(val) if val is not None else None


class NexGenCO2Sensor(NexGenEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.CO2
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION

    def __init__(self, coordinator: NexGenCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_co2"

    @property
    def name(self) -> str:
        return f"{self._device_data.get('name', 'NexGen')} CO\u2082"

    @property
    def native_value(self) -> int | None:
        val = (
            self._device_data.get("co2")
            or self._device_data.get("co2_ppm")
            or self._device_data.get("carbonDioxide")
        )
        return int(val) if val is not None else None
