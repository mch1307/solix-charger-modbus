"""Sensor platform for solix_charger_modbus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfElectricCurrent, UnitOfEnergy, UnitOfPower

from .entity import SolixEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SolixDataUpdateCoordinator
    from .data import SolixConfigEntry, SolixCoordinatorData


@dataclass(frozen=True, kw_only=True)
class SolixSensorEntityDescription(SensorEntityDescription):
    """Extended sensor description with a value extractor."""

    value_fn: Callable[[SolixCoordinatorData], str | int | float | None]


ENTITY_DESCRIPTIONS: tuple[SolixSensorEntityDescription, ...] = (
    SolixSensorEntityDescription(
        key="charging_status",
        translation_key="charging_status",
        icon="mdi:ev-station",
        value_fn=lambda data: data.get("charging_status"),
    ),
    SolixSensorEntityDescription(
        key="total_active_power",
        translation_key="total_active_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("total_active_power_w"),
    ),
    SolixSensorEntityDescription(
        key="charging_capacity",
        translation_key="charging_capacity",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("charging_capacity_kwh"),
    ),
    SolixSensorEntityDescription(
        key="max_current_setting",
        translation_key="max_current_setting",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("max_current_setting_a"),
    ),
    SolixSensorEntityDescription(
        key="product_number",
        translation_key="product_number",
        entity_category="diagnostic",
        value_fn=lambda data: data.get("product_number"),
    ),
    SolixSensorEntityDescription(
        key="model_name",
        translation_key="model_name",
        entity_category="diagnostic",
        value_fn=lambda data: data.get("model_name"),
    ),
    SolixSensorEntityDescription(
        key="serial_number",
        translation_key="serial_number",
        entity_category="diagnostic",
        value_fn=lambda data: data.get("serial_number"),
    ),
    SolixSensorEntityDescription(
        key="software_version",
        translation_key="software_version",
        entity_category="diagnostic",
        value_fn=lambda data: data.get("software_version"),
    ),
    SolixSensorEntityDescription(
        key="hardware_version",
        translation_key="hardware_version",
        entity_category="diagnostic",
        value_fn=lambda data: data.get("hardware_version"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: SolixConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from the config entry."""
    async_add_entities(
        SolixSensor(entry.runtime_data.coordinator, description)
        for description in ENTITY_DESCRIPTIONS
    )


class SolixSensor(SolixEntity, SensorEntity):
    """SOLIX sensor backed by coordinator data."""

    entity_description: SolixSensorEntityDescription

    def __init__(
        self,
        coordinator: SolixDataUpdateCoordinator,
        description: SolixSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> str | int | float | None:
        """Return the sensor value from coordinator data."""
        return self.entity_description.value_fn(self.coordinator.data)
