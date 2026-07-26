"""DataUpdateCoordinator for solix_charger_modbus."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SolixModbusCommunicationError
from .data import SolixCoordinatorData

if TYPE_CHECKING:
    from .data import SolixConfigEntry


class SolixDataUpdateCoordinator(DataUpdateCoordinator[SolixCoordinatorData]):
    """Coordinator that polls charger data via Modbus."""

    config_entry: SolixConfigEntry

    async def _async_update_data(self) -> SolixCoordinatorData:
        """Fetch fresh data from the charger."""
        try:
            return await self.config_entry.runtime_data.client.async_get_data()
        except SolixModbusCommunicationError as exception:
            raise UpdateFailed(exception) from exception
