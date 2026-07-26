"""Home Assistant integration for Solix charger over Modbus TCP."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntryNotReady
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL, Platform
from homeassistant.loader import async_get_loaded_integration

from .api import SolixChargerModbusClient, SolixModbusCommunicationError
from .const import (
    CONF_SLAVE_ID,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DOMAIN,
    LOGGER,
)
from .coordinator import SolixDataUpdateCoordinator
from .data import SolixRuntimeData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SolixConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: SolixConfigEntry) -> bool:
    """Set up this integration from a config entry."""
    client = SolixChargerModbusClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        slave_id=entry.data[CONF_SLAVE_ID],
    )

    coordinator = SolixDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=entry.data.get(CONF_NAME, DOMAIN),
        update_interval=timedelta(
            seconds=entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_SECONDS)
        ),
        config_entry=entry,
    )

    entry.runtime_data = SolixRuntimeData(
        client=client,
        coordinator=coordinator,
        integration=async_get_loaded_integration(hass, entry.domain),
    )

    try:
        await client.async_validate_connection()
        await coordinator.async_config_entry_first_refresh()
    except SolixModbusCommunicationError as exception:
        await client.async_close()
        raise ConfigEntryNotReady(exception) from exception

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SolixConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    await entry.runtime_data.client.async_close()
    return unload_ok
