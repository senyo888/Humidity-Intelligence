# Changelog

All notable changes to Humidity Intelligence will be documented in this file.

This project follows a practical changelog format for Home Assistant and HACS users. Add new entries under `Unreleased` before publishing a release.

## Unreleased

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
