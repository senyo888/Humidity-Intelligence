# Changelog

All notable changes to Humidity Intelligence will be documented in this file.

This project follows a practical changelog format for Home Assistant and HACS users. Add new entries under `Unreleased` before publishing a release.

## Unreleased

- Added README v2.0.4 upgrade guidance to run `humidity_intelligence.dump_cards` and paste the generated YAML into existing Manual dashboard cards for UI changes.
- Enlarged the HI icon/logo artwork within the required 256x256 canvas so it appears larger in Home Assistant and HACS surfaces.
- Clarified Global Gates target-profile labels as HI target/custom targets and added explicit alert visual rule removal in setup and options flows.
- Fixed alert helper switch churn so active alerts no longer flip their UI helper switches off/on during every evaluation cycle.
- Added single-flight automation evaluation and stopped internal status helper switches from retriggering evaluation, preventing alert-clear dogpiles when humidity returns to normal.
- Fixed startup UI refresh scheduling to use Home Assistant's thread-safe task creator, preventing unsafe `hass.async_create_task` calls during startup.
- Fixed startup UI refresh cleanup so Home Assistant builds where `hass.create_task` returns no task handle do not raise during the startup event.
- Removed custom trigger entities and custom binary sensor alert configuration so alerts remain internally calculated from HI telemetry, risk logic, and room/zone resolution; legacy custom alert rows are stripped from config-flow saves.
- Removed CO output-device selection from the main alert flow; CO Emergency now uses configured CO telemetry and existing configured ventilation outputs.
- Added clearer zone boost guidance and warnings when boost levels are not higher than normal zone fan levels.
- Added an alert handling setting for internally calculated humidity, mould, and condensation alert handling while keeping CO Emergency independent.
- Fixed alert boost hold behavior so selected alert zone outputs are not returned to auto while the alert lane is active.
- Changed alert conflict handling to keep the current actionable alert boost until that originating alert clears, unless a higher-priority alert appears.
- Changed unmapped/degraded alert handling so unsafe alert candidates are reported in the reason text while automation continues to the next eligible priority.
- Fixed built-in humidity, mould, and condensation alert candidates so they enter the alert lane, resolve to the mapped zone boost level, and populate `HI Active Alert Context` even when no matching explicit alert row is configured.
- Fixed V2 alert chip detection so generated cards recognise real alert switch entity IDs and the active alert context companion chip.
- Changed Humidity Danger alerts to use the active target profile high-risk threshold instead of any saved static humidity threshold.
- Updated alert metadata/reason text so Humidity Danger reports its active profile threshold source while CO Emergency keeps its configured ppm threshold.
- Fixed CO emergency evaluation so it remains the absolute top-priority lane before gates, pause, manual override, and normal control locks.
- Added GitHub community health files, issue forms, validation workflows, and contributor guidance.
- Added CI SAST/security checks, Bandit configuration, broader diagnostics redaction, and cleanup error logging.
- Added Hassfest validation workflow for Home Assistant custom integration checks.
- Updated Hassfest compatibility by staging the root-content HACS layout as `custom_components/humidity_intelligence`, aligning manifest keys, shared flow errors, and Lovelace after-dependency metadata.
- Added pre-Hassfest staged metadata normalization and verification so CI validates the generated custom component tree, not stale root metadata.
- Added a V2 UI Gallery with default mobile, tablet, and legacy mobile examples plus contributor/reference documentation.

## 2.0.3

- Current documented release in the integration manifest.
