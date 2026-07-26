"""Custom types for solix_charger_modbus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import SolixChargerModbusClient
    from .coordinator import SolixDataUpdateCoordinator


type SolixConfigEntry = ConfigEntry[SolixRuntimeData]


@dataclass
class SolixRuntimeData:
    """Runtime data for the integration."""

    client: SolixChargerModbusClient
    coordinator: SolixDataUpdateCoordinator
    integration: Integration


type SolixCoordinatorData = dict[str, Any]
