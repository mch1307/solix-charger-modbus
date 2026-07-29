"""Config flow for solix_charger_modbus."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.helpers import selector

from .api import (
    SolixChargerModbusClient,
    SolixModbusCommunicationError,
    SolixModbusConnectionError,
    SolixModbusReadError,
)
from .const import (
    CONF_SLAVE_ID,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    LOGGER,
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
            normalized_input = self._normalize_user_input(user_input)
            client = SolixChargerModbusClient(
                host=normalized_input[CONF_HOST],
                port=normalized_input[CONF_PORT],
                slave_id=normalized_input[CONF_SLAVE_ID],
            )

            try:
                discovered_slave_id, _discovered_address_offset = (
                    await client.async_validate_connection()
                )
                normalized_input[CONF_SLAVE_ID] = discovered_slave_id
            except SolixModbusConnectionError:
                LOGGER.exception(
                    "Failed to connect to Modbus charger during setup"
                )
                errors["base"] = "cannot_connect"
            except SolixModbusReadError:
                LOGGER.warning(
                    "Connected to Modbus charger, but register validation failed"
                )
                errors["base"] = "cannot_read_registers"
            except SolixModbusCommunicationError:
                LOGGER.exception(
                    "General Modbus communication failure during setup"
                )
                errors["base"] = "modbus_error"
            else:
                unique_id = (
                    f"{normalized_input[CONF_HOST]}:"
                    f"{normalized_input[CONF_PORT]}:"
                    f"{normalized_input[CONF_SLAVE_ID]}"
                )
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                title = normalized_input.get(CONF_NAME) or normalized_input[CONF_HOST]
                return self.async_create_entry(title=title, data=normalized_input)
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
                        min=0,
                        max=255,
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

    @staticmethod
    def _normalize_user_input(user_input: dict) -> dict:
        """Normalize submitted form values to the expected runtime types."""
        normalized = dict(user_input)
        normalized[CONF_PORT] = int(normalized[CONF_PORT])
        normalized[CONF_SLAVE_ID] = int(normalized[CONF_SLAVE_ID])
        normalized[CONF_SCAN_INTERVAL] = int(normalized[CONF_SCAN_INTERVAL])
        return normalized
