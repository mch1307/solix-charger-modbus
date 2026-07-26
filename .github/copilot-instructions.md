# Copilot Instructions for solix-charger-modbus

## Project identity
- This repository is a Home Assistant custom integration for the Anker Solix smart EV charger using the Modbus protocol.
- Treat the project name as `solix-charger-modbus`.
- Follow Home Assistant naming rules for code and files: use snake_case for Python identifiers and integration domains, avoid hyphens in module/domain names, and keep the user-facing project name consistent with the repository name.
- Remove or replace any leftover `integration_blueprint` references when touching related code.

## Sources of truth
- The product documentation in the `doc/` folder is the authoritative source for charger behavior, register mapping, protocol details, limits, and naming.
- Home Assistant integration architecture, async patterns, config flow behavior, entity design, translations, and diagnostics should follow the official Home Assistant custom integration guidelines and best practices.
- If the product docs and the Home Assistant patterns conflict, preserve the Home Assistant integration pattern and adapt the Modbus implementation around it.

## Implementation principles
- Prefer a `ConfigFlow`-first setup and keep the integration fully async.
- Use `DataUpdateCoordinator` for all Modbus polling and shared device state.
- Keep network and Modbus I/O out of entity methods; entities should expose state from coordinator data only.
- Use stable `unique_id` values for entities and never derive identity from display names.
- Use `EntityDescription` patterns where they reduce duplication across sensors, binary sensors, and switches.
- Translate user-facing text through `translations/` and avoid hard-coded strings in entity names, titles, or descriptions.
- Surface errors through `ConfigEntryNotReady`, `UpdateFailed`, and config-flow errors that match the failure mode.
- Prefer `hass` services, coordinators, and entities over custom background threads or blocking helpers.

## Modbus-specific guidance
- Treat the charger as the only source of protocol truth; do not guess register behavior when the docs are incomplete.
- Keep register addresses, scaling, endian handling, bit masks, and value conversions centralized so they can be audited and tested.
- Validate every read and write against the documented range, units, and allowed values.
- Make write paths defensive: check support, clamp or reject invalid values, and report clear errors.
- Separate read-only telemetry from control entities, and expose only capabilities the charger actually supports.

## Code quality expectations
- Prefer small, focused modules with explicit typing and clear dataclasses or typed dicts for coordinator payloads.
- Keep constants in `const.py` and avoid scattering magic strings or register numbers across platforms.
- Use Home Assistant test patterns where possible for config flows, entity setup, coordinator refresh, and service/write behavior.
- When adding or changing features, update translations, manifest metadata, and documentation together.
- Do not add dependencies unless they are necessary and justified by the integration design.

## When changing the repo
- Keep the codebase aligned with the current project rename: `solix-charger-modbus`.
- Prefer incremental refactors that move the repo away from the sample blueprint structure without changing unrelated behavior.
- Before introducing new functionality, check whether the existing docs or manifest already define the supported charger capabilities.
