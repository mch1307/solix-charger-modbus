"""Button platform for solix_charger_modbus."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Awaitable, Callable

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from .entity import SolixEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SolixDataUpdateCoordinator
    from .data import SolixConfigEntry


@dataclass(frozen=True, kw_only=True)
class SolixButtonEntityDescription(ButtonEntityDescription):
    """Extended button description with a press action."""

    press_fn: Callable[[SolixDataUpdateCoordinator], Awaitable[None]]


async def _async_start_charging(coordinator: SolixDataUpdateCoordinator) -> None:
    await coordinator.config_entry.runtime_data.client.async_start_charging()


async def _async_stop_charging(coordinator: SolixDataUpdateCoordinator) -> None:
    await coordinator.config_entry.runtime_data.client.async_stop_charging()


ENTITY_DESCRIPTIONS: tuple[SolixButtonEntityDescription, ...] = (
    SolixButtonEntityDescription(
        key="start_charging",
        translation_key="start_charging",
        press_fn=_async_start_charging,
    ),
    SolixButtonEntityDescription(
        key="stop_charging",
        translation_key="stop_charging",
        press_fn=_async_stop_charging,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: SolixConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up buttons from the config entry."""
    async_add_entities(
        SolixButton(entry.runtime_data.coordinator, description)
        for description in ENTITY_DESCRIPTIONS
    )


class SolixButton(SolixEntity, ButtonEntity):
    """SOLIX button backed by coordinator data."""

    entity_description: SolixButtonEntityDescription

    def __init__(
        self,
        coordinator: SolixDataUpdateCoordinator,
        description: SolixButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Send the configured command to the charger."""
        await self.entity_description.press_fn(self.coordinator)
        await self.coordinator.async_request_refresh()