"""Binary sensor platform for solix_charger_modbus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import SolixEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SolixDataUpdateCoordinator
    from .data import SolixConfigEntry, SolixCoordinatorData


@dataclass(frozen=True, kw_only=True)
class SolixBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Extended binary sensor description with a value extractor."""

    value_fn: Callable[[SolixCoordinatorData, SolixDataUpdateCoordinator], bool]


ENTITY_DESCRIPTIONS: tuple[SolixBinarySensorEntityDescription, ...] = (
    SolixBinarySensorEntityDescription(
        key="connected",
        translation_key="connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda _data, coordinator: coordinator.last_update_success,
    ),
    SolixBinarySensorEntityDescription(
        key="pwm_enabled",
        translation_key="pwm_enabled",
        value_fn=lambda data, _coordinator: bool(data.get("pwm_enabled", False)),
    ),
    SolixBinarySensorEntityDescription(
        key="ocpp_connected",
        translation_key="ocpp_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda data, _coordinator: bool(data.get("ocpp_connected", False)),
    ),
    SolixBinarySensorEntityDescription(
        key="mqtt_connected",
        translation_key="mqtt_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda data, _coordinator: bool(data.get("mqtt_connected", False)),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: SolixConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors from the config entry."""
    async_add_entities(
        SolixBinarySensor(entry.runtime_data.coordinator, description)
        for description in ENTITY_DESCRIPTIONS
    )


class SolixBinarySensor(SolixEntity, BinarySensorEntity):
    """SOLIX binary sensor backed by coordinator data."""

    entity_description: SolixBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: SolixDataUpdateCoordinator,
        description: SolixBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool:
        """Return the binary sensor state."""
        return self.entity_description.value_fn(self.coordinator.data, self.coordinator)
