"""Constants for solix_charger_modbus."""

from __future__ import annotations

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "solix_charger_modbus"

DEFAULT_NAME = "Anker SOLIX Charger"
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_SCAN_INTERVAL_SECONDS = 10

MAX_CHARGING_CURRENT_SETTING_A = 32

CONF_SLAVE_ID = "slave_id"

# Read-only information registers from the product Modbus specification.
REG_PRODUCT_NUMBER = 20000
REG_MODEL_NAME = 20001
REG_SERIAL_NUMBER = 20011
REG_SOFTWARE_VERSION = 20023
REG_HARDWARE_VERSION = 20029
REG_TOTAL_ACTIVE_POWER = 20068
REG_CURRENT_CHARGING_CAPACITY = 20086
REG_PWM_ENABLED = 20087
REG_CHARGING_STATUS = 20097
REG_OCPP_CONNECTION = 20098
REG_MQTT_CONNECTION = 20099
REG_CHARGING_COMMAND = 21000
REG_MAX_CURRENT_SETTING = 21005

CHARGING_COMMAND_START = 1
CHARGING_COMMAND_STOP = 2

CHARGING_STATUS_MAP: dict[int, str] = {
    0: "idle",
    1: "preparing",
    2: "charging",
    3: "charger_paused",
    4: "vehicle_paused",
    5: "charging_completed",
    6: "reserving",
    7: "disabled",
    8: "error",
}
