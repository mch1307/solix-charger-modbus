"""Number platform for solix_charger_modbus."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfElectricCurrent
from homeassistant.exceptions import HomeAssistantError

from .api import SolixModbusCommunicationError, SolixModbusError
from .const import MAX_CHARGING_CURRENT_SETTING_A
from .entity import SolixEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SolixDataUpdateCoordinator
    from .data import SolixConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: SolixConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up numbers from the config entry."""
    async_add_entities([SolixChargingCurrentLimitNumber(entry.runtime_data.coordinator)])


class SolixChargingCurrentLimitNumber(SolixEntity, NumberEntity):
    """Writable current-limit number for the charger."""

    _attr_translation_key = "charging_current_limit"
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_mode = NumberMode.BOX
    _attr_native_step = 1.0

    def __init__(self, coordinator: SolixDataUpdateCoordinator) -> None:
        """Initialize the number."""
        super().__init__(coordinator, "charging_current_limit")

    @property
    def native_min_value(self) -> float:
        """Return the minimum supported current limit."""
        return 0.0

    @property
    def native_max_value(self) -> float:
        """Return the maximum supported current limit."""
        data = self.coordinator.data or {}
        value = data.get("max_supported_current_a")
        if value is None:
            return float(MAX_CHARGING_CURRENT_SETTING_A)

        return float(value)

    @property
    def native_value(self) -> float | None:
        """Return the current limit from coordinator data."""
        data = self.coordinator.data or {}
        value = data.get("max_current_setting_a")
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Write a new charging current limit to the charger."""
        if not float(value).is_integer():
            raise HomeAssistantError("Charging current must be a whole number of amperes.")

        current_a = int(value)
        max_current_a = int(self.native_max_value)

        if current_a < 0 or current_a > max_current_a:
            raise HomeAssistantError(
                f"Charging current must be between 0 and {max_current_a} A."
            )

        try:
            await self.coordinator.config_entry.runtime_data.client.async_set_max_current(
                current_a
            )
        except (SolixModbusCommunicationError, SolixModbusError) as exception:
            raise HomeAssistantError(str(exception)) from exception

        await self.coordinator.async_request_refresh()