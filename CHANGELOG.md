# Changelog

All notable changes to Humidity Intelligence will be documented in this file.

This project follows a practical changelog format for Home Assistant and HACS users. Add new entries under `Unreleased` before publishing a release.

## Unreleased

- Synchronized roadmap, governance, support, and contributor documentation to treat v2.0.5 as a completed release milestone while keeping future v2.1 work explicitly staged.
- Kept `v205_release_check` compatible with v2.0.6 beta/rc/stable manifests so the v2.0.6 beta 1 validation path reuses the existing read-only release-check contract instead of renaming the service.

## 2.0.5

- Reorganised setup and options so essentials stay visible while tuning controls move behind Advanced sections.
- Changed Advanced tuning from submit-gated reveal toggles to in-form collapsible sections so tuning controls open and retract immediately without changing saved runtime behavior.
- Added recommended-default guidance across setup/options without changing deterministic runtime behavior.
- Added `show_output_entity_details` as a UI-only generated-card option; new installs default to the cleaner V2 output display unless it is enabled.
- Made `Thresholds & Comfort` easier to scan by keeping comfort mode visible and moving custom comfort/threshold tuning into Advanced.
- Changed first-install UI export default to `v2_tablet`.
- Kept custom humidity target bounds behind Advanced in post-configuration Global Gates and reviewed setup/options parity for the v2.0.5 UX flow.
- Preserved canonical `dump_cards` behavior: unscoped exports all cached/generated layouts; scoped `layout` exports only the specified layout.
- Preserved deterministic runtime lane ordering, alert hierarchy, CO emergency behavior, humidifier independence, and public entity semantics.
- Added `v205_release_check`, a read-only Home Assistant service for test-repo validation of the v2.0.5 generated-card and `dump_cards` contracts.
- Changed setup/options dependency display, `self_check`, `v205_release_check`, and `dump_diagnostics` frontend dependency reporting to use the same Lovelace resource inspection path via `LOVELACE_DATA.resources.async_items()`, returning detected URLs or a non-blocking `not_inspectable` status instead of legacy false negatives.
- Added native Home Assistant diagnostics for Humidity Intelligence config entries so users can download a redacted support file for GitHub issues.
- Updated issue templates and local issue triage to prefer attached native Home Assistant diagnostics, suggest `has-diagnostics` when present, and suggest `needs-bundle` for bug/support reports without one.
- Hardened `HI House Humidity Drift 7d` so missing or unavailable `sensor.house_humidity_mean_7d` statistics dependency is reported in sensor attributes, `self_check`, `v205_release_check`, and diagnostics instead of failing silently.
- Fixed calculated room temperature slope sensors so they publish a seeded state immediately after setup instead of waiting for a later source update, preventing restored-but-unavailable slope chips after HI restarts.
- Fixed calculated temperature slope diagnostics mapping so every configured slope source prefers Home Assistant's registered entity id when it differs from the predicted `sensor.hi_*` fallback.
- Promoted integration metadata to stable `2.0.5`; branch/version governance now allows beta, rc, or stable labels on `senyo888-patch-1`, rc or stable labels on `develop`, and stable releases on `main`.

## 2.0.4

- Fixed alert flash color payloads so internally triggered visual alerts send RGB lists accepted by Home Assistant service validation.
- Added user-friendly headers to V2 card YAML exports with Manual-card paste instructions, `dump_cards` refresh guidance, and frontend dependency reminders.
- Fixed alert flash payloads so optional visual-indicator power entities are omitted when unset, avoiding schema errors and repeated debug logs.
- Refined Air Control UI chips so AQ and humidity rows use House, Upstairs, Downstairs ordering and removed the Kitchen temperature-slope chip from the humidity row.
- Refined Air Control humidity chips to use configured zone-room humidity telemetry, skip legacy bespoke delta chips, and list room humidity deltas alphabetically.
- Added an optional Air Control temperature chip row controlled from Temperature Slope settings, showing house/level temperatures, configured zone-room temperatures, and room temperature slopes.
- Added automatic/custom temperature comfort configuration with runtime comfort sensors used by V2 temperature chip colours.
- Expanded post-configuration zone editing so humidity high, air quality, condensation risk, and mould risk thresholds remain editable per zone.
- Fixed calculated temperature slope chip fallback to use Home Assistant slug-compatible generated slope entity IDs and configured slope source checks.
- Renamed user-facing dependency wording to Frontend Dependencies across setup, options, services, self-check output, and docs.
- Added README v2.0.4 upgrade guidance to run `humidity_intelligence.dump_cards` and paste the generated YAML into existing Manual dashboard cards for UI changes.
- Enlarged the HI icon/logo artwork within the required 256x256 canvas so it appears larger in Home Assistant and HACS surfaces.
- Clarified Global Gates target-profile labels as `Humidity Intelligence target profile mode` and `Humidity custom target`, and added explicit alert visual rule removal in setup and options flows.
- Simplified alert chipsets so they render only the alert lane/status chip and the resolved alert source/context chip.
- Changed humidity/mould/condensation visual alerts to flash 10 times, restore prior light state, wait 30 minutes, and repeat only while the same alert remains active.
- Expanded diagnostics with target profile mode, active profile/season/custom target, zone/alert mappings, visual alert config, active alert resolution, unavailable entities, and warnings.
- Reduced live `HI Diagnostics` state attributes to a compact recorder-safe summary; full diagnostics remain available from `dump_diagnostics`.
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

<details>
<summary>Previous Releases</summary>

## 2.0.3

- Previous documented release.

</details>
