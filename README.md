# Solix Charger Modbus

Home Assistant custom integration for the Anker SOLIX V1 Smart EV Charger over Modbus TCP.

This repository now contains the active Modbus integration under the domain `solix_charger_modbus`. The old blueprint scaffold has been removed.

## Current Features

- Configurable Modbus TCP connection using charger IP address or hostname, port, and slave ID.
- Config flow validation that checks the charger is reachable before the entry is created.
- Coordinator-based polling so all entities update from a single shared Modbus read cycle.
- Automatic reconnect handling through Home Assistant config entry setup and refresh flow.
- Read-only charger telemetry surfaced in Home Assistant.
- Charging control buttons for start and stop commands.
- Writable charging current limit control exposed as a number entity.
- Local polling only; no cloud account is required.

## Configured Fields

When you add the integration from Home Assistant, you can set:

- Name
- Host
- Port, default `502`
- Slave ID, default `1` (supported range `0` to `255`)
- Poll interval, default `10` seconds

## Available Entities

### Sensors

- Charging status
- Charging active power
- Current session energy
- Max current setting
- Product number
- Model name
- Serial number
- Software version
- Hardware version

### Buttons

- Start charging
- Stop charging

### Numbers

- Charging current limit

### Binary sensors

- Connected
- PWM enabled
- OCPP connected
- MQTT connected

## Data Read From The Charger

The integration currently reads the documented Modbus registers for:

- Device identity and firmware information
- Total charging active power
- Current charging session capacity
- PWM enable status
- Charging status code
- OCPP and MQTT connection state
- Max current setting
- Charging start/stop commands
- Charging current limit writes

## Modbus Notes

- The charger must have Modbus TCP enabled in the Anker app.
- The documentation indicates Modbus TCP uses port `502`.
- If setup reports that register reads fail, verify the charger's Slave ID in the app. The integration validates using the configured ID and also probes common IDs (`1`, `255`, `0`) during setup.
- The protocol document was used as the source for the current register mapping.

## Project Status

This is the first working slice of the integration. It is focused on configuration, synchronized telemetry, and basic charging control writes.

## Development

The integration code lives in [custom_components/solix_charger_modbus](custom_components/solix_charger_modbus).

The product protocol reference is in [doc/Anker SOLIX V1 Smart EV Charger Modbus Protocol.pdf](doc/Anker%20SOLIX%20V1%20Smart%20EV%20Charger%20Modbus%20Protocol.pdf).
