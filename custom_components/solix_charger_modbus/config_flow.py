"""Config flow for solix_charger_modbus."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.helpers import selector

from .api import SolixChargerModbusClient, SolixModbusCommunicationError
from .const import (
    CONF_SLAVE_ID,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DEFAULT_SLAVE_ID,
    DOMAIN,
)


class SolixConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solix charger via Modbus TCP."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle user-initiated setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            client = SolixChargerModbusClient(
                host=user_input[CONF_HOST],
                port=user_input[CONF_PORT],
                slave_id=user_input[CONF_SLAVE_ID],
            )

            try:
                await client.async_validate_connection()
            except SolixModbusCommunicationError:
                errors["base"] = "cannot_connect"
            else:
                unique_id = (
                    f"{user_input[CONF_HOST]}:"
                    f"{user_input[CONF_PORT]}:"
                    f"{user_input[CONF_SLAVE_ID]}"
                )
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                title = user_input.get(CONF_NAME) or user_input[CONF_HOST]
                return self.async_create_entry(title=title, data=user_input)
            finally:
                await client.async_close()

        return self.async_show_form(
            step_id="user",
            data_schema=self._build_schema(user_input),
            errors=errors,
        )

    @staticmethod
    def _build_schema(user_input: dict | None) -> vol.Schema:
        """Build the form schema with defaults."""
        current = user_input or {}

        return vol.Schema(
            {
                vol.Optional(
                    CONF_NAME,
                    default=current.get(CONF_NAME, DEFAULT_NAME),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    )
                ),
                vol.Required(
                    CONF_HOST,
                    default=current.get(CONF_HOST, vol.UNDEFINED),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    )
                ),
                vol.Required(
                    CONF_PORT,
                    default=current.get(CONF_PORT, DEFAULT_PORT),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=65535,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_SLAVE_ID,
                    default=current.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=247,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current.get(
                        CONF_SCAN_INTERVAL,
                        DEFAULT_SCAN_INTERVAL_SECONDS,
                    ),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=5,
                        max=300,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )
