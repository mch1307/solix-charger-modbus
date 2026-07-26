"""Shared entity helpers for solix_charger_modbus."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SolixDataUpdateCoordinator


class SolixEntity(CoordinatorEntity[SolixDataUpdateCoordinator]):
    """Base entity bound to the integration coordinator."""

    def __init__(
        self,
        coordinator: SolixDataUpdateCoordinator,
        key: str,
    ) -> None:
        """Initialize the shared entity fields."""
        super().__init__(coordinator)

        data = coordinator.data or {}
        serial = data.get("serial_number")
        identifiers = {(DOMAIN, serial or coordinator.config_entry.entry_id)}

        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers=identifiers,
            manufacturer="Anker SOLIX",
            model=data.get("model_name") or "V1 Smart EV Charger",
            serial_number=serial,
            sw_version=data.get("software_version"),
            hw_version=data.get("hardware_version"),
            name=coordinator.config_entry.title,
        )
