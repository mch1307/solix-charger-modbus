"""Modbus API client for the Solix charger."""

from __future__ import annotations

import asyncio
from typing import Any

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import (
    CHARGING_STATUS_MAP,
    REG_CHARGING_STATUS,
    REG_CURRENT_CHARGING_CAPACITY,
    REG_HARDWARE_VERSION,
    REG_MAX_CURRENT_SETTING,
    REG_MODEL_NAME,
    REG_MQTT_CONNECTION,
    REG_OCPP_CONNECTION,
    REG_PRODUCT_NUMBER,
    REG_PWM_ENABLED,
    REG_SERIAL_NUMBER,
    REG_SOFTWARE_VERSION,
    REG_TOTAL_ACTIVE_POWER,
)


class SolixModbusError(Exception):
    """General integration error."""


class SolixModbusCommunicationError(SolixModbusError):
    """Raised when communication with Modbus fails."""


class SolixChargerModbusClient:
    """Async Modbus client for the Anker SOLIX charger."""

    def __init__(self, host: str, port: int, slave_id: int) -> None:
        """Initialize client configuration."""
        self._host = host
        self._port = port
        self._slave_id = slave_id
        self._client: AsyncModbusTcpClient | None = None
        self._address_offset = 0

    async def async_validate_connection(self) -> None:
        """Validate Modbus connectivity and register addressing."""
        await self._async_ensure_connected()

        for offset in (0, -1):
            try:
                result = await self._read_holding_registers_raw(
                    address=REG_PRODUCT_NUMBER + offset,
                    count=1,
                )
            except SolixModbusCommunicationError:
                continue

            if result and result[0] >= 0:
                self._address_offset = offset
                return

        raise SolixModbusCommunicationError(
            "Could not read product register (20000/19999)."
        )

    async def async_get_data(self) -> dict[str, Any]:
        """Read the main telemetry and status data from the charger."""
        await self._async_ensure_connected()

        product_number = await self._read_u16(REG_PRODUCT_NUMBER)
        model_name = await self._read_string(REG_MODEL_NAME, 10)
        serial_number = await self._read_string(REG_SERIAL_NUMBER, 12)
        software_version = await self._read_string(REG_SOFTWARE_VERSION, 6)
        hardware_version = await self._read_string(REG_HARDWARE_VERSION, 6)

        total_active_power_w = await self._read_u32(REG_TOTAL_ACTIVE_POWER)
        charging_capacity_wh = await self._read_u32(REG_CURRENT_CHARGING_CAPACITY)
        pwm_enabled = bool(await self._read_u16(REG_PWM_ENABLED))
        charging_status_code = await self._read_u16(REG_CHARGING_STATUS)
        ocpp_connected = bool(await self._read_u16(REG_OCPP_CONNECTION))
        mqtt_connected = bool(await self._read_u16(REG_MQTT_CONNECTION))
        max_current_setting_a = await self._read_u16(REG_MAX_CURRENT_SETTING)

        return {
            "product_number": product_number,
            "model_name": model_name,
            "serial_number": serial_number,
            "software_version": software_version,
            "hardware_version": hardware_version,
            "total_active_power_w": float(total_active_power_w),
            "charging_capacity_wh": float(charging_capacity_wh),
            "charging_capacity_kwh": round(charging_capacity_wh / 1000.0, 3),
            "pwm_enabled": pwm_enabled,
            "charging_status_code": charging_status_code,
            "charging_status": CHARGING_STATUS_MAP.get(charging_status_code, "unknown"),
            "ocpp_connected": ocpp_connected,
            "mqtt_connected": mqtt_connected,
            "max_current_setting_a": float(max_current_setting_a),
        }

    async def async_close(self) -> None:
        """Close the underlying Modbus connection."""
        if self._client is not None:
            self._client.close()
            self._client = None

    async def _async_ensure_connected(self) -> None:
        """Connect to the charger if not already connected."""
        if self._client is None:
            self._client = AsyncModbusTcpClient(host=self._host, port=self._port)

        if self._client.connected:
            return

        try:
            connected = await self._client.connect()
        except Exception as exception:  # pylint: disable=broad-except
            raise SolixModbusCommunicationError(
                f"Failed connecting to charger at {self._host}:{self._port}: {exception}"
            ) from exception

        if not connected:
            raise SolixModbusCommunicationError(
                f"Unable to connect to charger at {self._host}:{self._port}."
            )

    async def _read_holding_registers_raw(self, address: int, count: int) -> list[int]:
        """Read raw holding register values from an absolute Modbus address."""
        if self._client is None:
            raise SolixModbusCommunicationError("Client is not connected.")

        try:
            async with asyncio.timeout(10):
                response = await self._client.read_holding_registers(
                    address=address,
                    count=count,
                    slave=self._slave_id,
                )
        except TimeoutError as exception:
            raise SolixModbusCommunicationError(
                f"Timeout reading address {address}."
            ) from exception
        except ModbusException as exception:
            raise SolixModbusCommunicationError(
                f"Modbus error reading address {address}: {exception}"
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise SolixModbusCommunicationError(
                f"Unexpected error reading address {address}: {exception}"
            ) from exception

        if response.isError():
            raise SolixModbusCommunicationError(
                f"Device returned Modbus exception while reading {address}."
            )

        return list(response.registers)

    async def _read_holding_registers(self, doc_address: int, count: int) -> list[int]:
        """Read registers using the detected 20000/19999 addressing offset."""
        return await self._read_holding_registers_raw(
            address=doc_address + self._address_offset,
            count=count,
        )

    async def _read_u16(self, doc_address: int) -> int:
        """Read an unsigned 16-bit value."""
        values = await self._read_holding_registers(doc_address, 1)
        return values[0]

    async def _read_u32(self, doc_address: int) -> int:
        """Read an unsigned 32-bit big-endian value from two registers."""
        values = await self._read_holding_registers(doc_address, 2)
        return (values[0] << 16) | values[1]

    async def _read_string(self, doc_address: int, register_count: int) -> str:
        """Read ASCII text packed as two bytes per register."""
        values = await self._read_holding_registers(doc_address, register_count)
        data = bytearray()
        for value in values:
            data.append((value >> 8) & 0xFF)
            data.append(value & 0xFF)
        return data.decode("ascii", errors="ignore").replace("\x00", "").strip()
