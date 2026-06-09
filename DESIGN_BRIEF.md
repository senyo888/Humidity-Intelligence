# Humidity Intelligence V2: Minimum-Expectation Design Brief

## 0. Launch Status and V2 Release Addendum
- Official release status: **Launched to GitHub (main)**.
- Launch date: **February 23, 2026**.
- This brief remains the baseline implementation contract.
- V2 release includes the following confirmed upgrades:
  - canonical lane order enforced: CO emergency -> alerts -> zone 1 -> zone 2 -> AQ
  - humidifier lanes remain independent
  - global gates surfaced in runtime mode (`GLOBAL GATE`) and Current Air Control visuals
  - post-configuration editing expanded across sensors, gates, zones, zone thresholds, humidifiers, AQ, alerts, slope
  - threshold guardrails and fan stage normalization (`auto`, `33`, `66`, `100`)
  - dynamic alert/output mapping and legacy hardcoded placeholder removal
  - runtime/card sanity test committed as regression coverage

### 0.2 V2.0.4 Alert Binding Addendum (May 1, 2026)
- Alert hierarchy is expanded but remains deterministic: CO emergency -> humidity danger -> mould danger -> mould risk -> condensation danger -> condensation risk -> zone 1 -> zone 2 -> AQ -> normal.
- Humidity, mould, and condensation alerts must resolve originating sensor -> room -> zone before applying control.
- Humidity danger alerts must use the active target profile high-risk threshold at runtime; legacy saved static humidity threshold values must be ignored.
- Alert control uses the resolved zone's configured boost fan level; it must not introduce a separate hidden output path.
- Zone boost settings are the escalation path for alerts and should normally be higher than the standard zone fan level. Equal/lower boost values are allowed only as user choice and must be surfaced as guidance/warning, not blocked.
- If multiple alerts are active, resolution is by alert hierarchy first and zone priority second (`zone1` before `zone2`).
- If sensor, room, zone, or output mapping is incomplete, HI must enter degraded alert mode, log the issue, expose it in reason/telemetry, and avoid blind boost.
- Alert configuration must not expose custom trigger entities or custom binary sensor alert sources. Humidity, mould, condensation, and CO alert sources are derived from HI telemetry/risk logic.
- CO emergency remains independent and top priority. It uses configured CO telemetry plus existing configured ventilation outputs; separate CO output-device selection is not part of the main alert flow.
- Design-brief conflict resolved: the older generic `alerts` lane is retained as the lane category, but its internal ordering is now explicit and zone-bound.

### 0.3 V2.0.4 Air Control Chipset Addendum (May 6, 2026)
- Current Air Control chip rows are UI truth surfaces only. They must reflect backend/config/diagnostics truth and must not create or alter lane decisions.
- The AQ chip row remains independent unless AQ telemetry or AQ runtime logic changes.
- The humidity chip row order is: house average humidity -> configured level average humidity chips in configured display order -> enabled-zone room humidity chips alphabetically by configured room label -> room humidity delta chips alphabetically by configured room label.
- Zone, level, and room labels must be derived from configured telemetry, level mappings, enabled zone room assignments, diagnostics, or output mappings. They must not be hard-coded as Bathroom/Kitchen/Upstairs/Downstairs public placeholders.
- Static section/category copy such as `Current Air Control`, `Air Quality`, `Humidity`, `Temperature`, and `Outputs` may be part of the visual shell. Context labels such as levels, zones, rooms, outputs, and attributed alert sources must be backend/config-derived display truth.
- Room humidity delta chips must require real room attribution and must not include bespoke legacy `air_control_*_humidity_delta` helper chips.
- A third temperature chip row is optional, defaults disabled, and is configured from the Temperature Slope setup/options area.
- The optional temperature chip row order is: house average temperature -> configured level average temperature chips in configured display order -> enabled-zone room temperature chips alphabetically by configured room label -> room temperature slope chips alphabetically by configured room label.
- Temperature chip colours must use HI runtime comfort sensors: below band blue, in band green, up to 1°C above band yellow, more than 1°C above band red.
- Temperature slope chips must use the diagnostics/backend slope mapping source of truth, with configured-source fallback only for HI-generated or provided slope entities.
- Generated UI must degrade by hiding unavailable optional chip values rather than inventing data or shipping unresolved placeholders.

### 0.4 V2.0.5 Adoption-Friendly Configuration Addendum (May 11, 2026)
- V2.0.5 is the completed adoption-friendly configuration UX and support-readiness release with stable runtime semantics.
- Setup and options must present essential environmental control settings first, then expose tuning through Advanced sections.
- Advanced sections must expand and retract immediately in the form UI without requiring a Submit cycle just to reveal or hide fields.
- Recommended defaults must be used unless customised; hiding a tuning field must not remove the stored behavior or make it unavailable.
- Control loop interval, startup UI mapping refresh, custom humidity target bounds, custom temperature comfort bounds, slope source overrides, optional chip rows, zone fan levels, threshold tuning, lane removal, and visual-alert tuning are advanced controls.
- Advanced sections are limited to tuning, diagnostics, expert controls, and optional overrides. They must not become a dumping ground for unrelated settings.
- `show_output_entity_details` is a UI visibility option only. It may hide or show the expandable generated-card output details panel, but it must not affect runtime outputs, lane selection, manual override behavior, isolation switches, diagnostics, or entity names.
- New installs should default generated V2 cards to the cleaner output display unless output entity details are enabled.
- `dump_cards` remains the supported dashboard update flow after UI visibility changes. Unscoped calls export all cached/generated layouts; scoped `layout` calls export only the specified layout.
- `v205_release_check` is allowed as a read-only release-validation service for confirming generated-card visibility, cached layouts, placeholders, entity availability, and scoped/unscoped `dump_cards` behavior in a Home Assistant test environment. It must not change runtime outputs, lane selection, helper state, or entity semantics.
- Native Home Assistant diagnostics are the preferred user-facing GitHub support bundle. `dump_diagnostics` remains the fuller local JSON export path for maintainer/debug workflows and must stay privacy-conscious.
- House humidity drift 7d must preserve the existing calculation: current HI house average humidity minus `sensor.house_humidity_mean_7d`. Missing, unknown, unavailable, or non-numeric dependency states must be explicit in the drift sensor, diagnostics, `self_check`, and release checks rather than silently blank or synthesized.
- Calculated temperature slope diagnostics and UI mapping should prefer Home Assistant's registered entity ID when it differs from the predicted fallback entity ID.
- Setup/options parity must be preserved when moving controls behind Advanced sections.
- Deterministic runtime lane order, alert hierarchy, CO emergency behavior, humidifier independence, and public semantics remain unchanged.
- V2.0.5 must not imply that V2.1 Environmental Stability Intelligence outcome, prediction, or stability-score features are implemented.

### 0.5 V2.0.6 Stable Runtime and Maintenance Addendum (June 2026)
- V2.0.6 is the current stable maintenance release in the canonical release-source checkout.
- `telemetry_unavailable` is a backend-owned degraded runtime mode. If required humidity telemetry, or configured temperature telemetry, is unavailable while control is otherwise enabled, HI must publish `telemetry_unavailable`, return outputs to the safe normal state, and skip lower-priority alert, humidifier, zone, and AQ lane evaluation until required telemetry is usable again. Temperature must only be required when temperature telemetry is configured.
- Global gates must preempt lower-priority alert runtime truth. When a gate takes authority, stale humidity-danger alert helper state, active alert context, alert telemetry, and Current Air Control alert display truth must clear or suppress immediately.
- CO emergency clearing remains time-bounded: once CO telemetry is below the clear threshold, HI must schedule a recheck for the clear-hold deadline rather than waiting for the next normal periodic control interval.
- Backend air-control-mode simulation coverage is release-relevant validation. It must not create runtime fake telemetry entities, fake output paths, or frontend-inferred mode truth in user installs.
- V2.0.6 local snapshot support is explicit, manual, and package-local only: `create_local_backup` and `list_saved_versions` are not restore, automatic rollback, HACS interception, startup snapshotting, arbitrary deletion, or whole-instance backup features.
- Drift helper ownership remains explicit. HI consumes `sensor.house_humidity_mean_7d`, reports readiness/repair status, and must not create helper history or synthesize drift values.
- Temperature chip colour semantics are backend-owned. Generated cards must consume resolved comfort/warm boundary truth from runtime sensors or diagnostics rather than hard-coded seasonal threshold tables.
- V2.0.6 does not implement V2.1 Environmental Stability Intelligence, Stability Score, prediction, dashboard strategy, or Harmonic control behavior.

### 0.1 V2.0.1 Stabilization Addendum (February 23, 2026)
- Temperature normalization contract:
  - all internal temperature math is canonicalized to `°C`
  - each source sensor `unit_of_measurement` is respected
  - missing unit falls back to HA configured unit system
  - averages/deltas/threshold paths must use normalized units consistently
- IAQ aggregation contract:
  - `unknown`/`unavailable`/non-numeric inputs are excluded from aggregates
  - aggregate state returns `unknown` only when no numeric inputs remain
  - debug logs must include excluded entities and reason category
- Zone mapping safety:
  - duplicate sensor mappings across zones must be validated and surfaced
  - diagnostics/log output must call out duplicate assignments explicitly
- Optional outputs + alert-only behavior:
  - all output controls are optional and must not be hard-required by UI generation
  - `alert_only_mode` suppresses control/output helpers and control UI sections
  - disabling `alert_only_mode` restores control entities and card controls
- Post-configuration editability:
  - options flow must support adding, editing, and removing telemetry sensors after setup
  - options flow must support adding, editing, and removing humidifier and AQ lanes after setup
  - lane removal and re-addition must not require reinstall/reconfigure from scratch
- UI generation hardening:
  - generated cards must prune unresolved optional entities safely
  - empty `cards:` containers must be removed
  - invalid `conditional` cards (missing condition items/card body after pruning) must be removed
  - toggling `alert_only_mode` in options must trigger card refresh/export regeneration
  - Current Air Control reason field must adapt in alert-only mode and must not imply output-control actions/entities that are intentionally suppressed

## 1. Purpose
Define the minimum acceptable engineering standard for building and maintaining a production-grade Home Assistant custom integration that combines:

- Config-flow driven setup
- Runtime sensor computation
- Automation orchestration
- Generated dashboard YAML
- Diagnostics, migration, and cleanup tooling

This brief is the baseline contract for implementation quality, not an aspirational wishlist.

## 2. Product Scope
The integration must deliver these capabilities:

- Multi-step config flow for frontend dependencies, telemetry inputs, gates, zones, humidifiers, AQ, alerts, temperature slope, and UI choices
- Runtime-created entities with stable unique IDs and `hi_` namespacing
- Internal automation engine replacing external YAML automations
- Generated Lovelace card YAML per layout with strict entity mapping
- Operational services for refresh, diagnostics, card export, dashboard creation, pause/resume, and purge
- Safe migration path from legacy YAML/package setup

Out of scope:

- Hard dependency on optional frontend cards
- Direct mutation of user-owned non-HI entities
- Hidden behavior requiring manual script stubs

## 3. Core Principles

1. Reliability over novelty
All features must fail safe and keep core humidity control operational.

2. Deterministic behavior
Entity IDs, thresholds, and automation precedence must be predictable across restarts.

3. Backward-compatible rollout
v2 must coexist with v1 during transition with clear guidance and no forced cutover.

4. Operational transparency
Users must be able to inspect config, mappings, cards, and runtime status without debugging code.

5. Non-blocking HA compliance
No blocking file/network operations in event loop paths.

## 4. Architecture Baseline

Integration layers:

- Config layer: `config_flow.py`, validation helpers, translation strings
- Domain/runtime layer: computed sensors and binary sensors
- Control layer: automation engine with priority lanes
- UI layer: template cards + mapping/render services
- Ops layer: diagnostics, self-check, refresh, cleanup, migration

Data flow:

- Telemetry entities enter via config entry
- Core computations generate house/level/room derived metrics
- Automation engine consumes source and derived state
- UI mapping resolves placeholders to actual generated entities
- Services expose controlled lifecycle operations

### 4.1 Seasonal Target System and Environmental Context

- Humidity targets are dynamic and season-dependent by default.
- Runtime may also use an explicitly selected seasonal profile or a custom target band.
- Stability remains the primary goal, now contextualized by active environmental profile.
- **All environmental interpretation is relative to the active target profile.**
- **Seasonal context is a first-class input into risk evaluation.**
- Deterministic zone balancing is a separate control concern from environmental risk interpretation.
- The `humidity_high` zone trigger is intentionally defined as room-vs-house humidity delta (imbalance control), not a target-risk classifier.
- This separation is canonical and preserves deterministic lane behavior while avoiding semantic overlap with condensation/mould/humidity risk paths.

### 4.2 Target-relative state model

Minimum canonical humidity state model:

- `below_target`
- `in_target`
- `above_target`
- `high_risk`

State resolution must be deterministic and derived from the active profile's low/high/high-risk bounds.

## 5. Functional Requirements (Minimum)

### 5.1 Configuration

- Config flow must validate all user input before commit.
- Duplicate telemetry entity selection must be prevented.
- Users must be able to edit/delete telemetry rows before progressing.
- Optional dependencies must never block backend operation.
- Back navigation between config steps must preserve state safely.
- Setup and options must use progressive disclosure: essentials visible first, tuning controls available from Advanced sections.
- Advanced tuning visibility must be controlled by live form/section state, not by saved config or a submit-gated reveal step.
- Recommended defaults must remain safe and bounded when advanced tuning fields are left untouched.

### 5.2 Entity Model

- Every generated entity must have:
  - Stable `unique_id`
  - `hi_` prefix
  - Clear semantic name
- Collisions must be resolved without crash.
- Canonical-to-actual entity mapping must be persisted for UI rendering.
- Target/profile entities must expose active season/profile and target-relative humidity state for UI/runtime parity.

### 5.3 Automation Engine

- Priority order must be enforced: CO emergency > humidity danger > mould danger > mould risk > condensation danger > condensation risk > zone 1 > zone 2 > AQ.
- Humidity danger alert thresholds are profile-driven and must not be treated as static alert configuration values.
- Humidifier lanes must remain independent.
- Global gates must be respected: enabled/manual override/time/presence/pause.
- When any global gate takes authority, lower-priority alert runtime state must be cleared or suppressed, including active alert helper switches, held alert context, and alert telemetry.
- Missing output entities/services must be tolerated without engine crash.
- Engine loop interval must be bounded and configurable.
- Condensation and mould interpretation must use deterministic season-aware thresholds.
- `humidity_high` zone triggering remains deterministic room-vs-house delta logic for operational balancing and must not be reinterpreted as a direct risk classifier.
- Humidifier reason telemetry must include lane, trigger condition, readings vs thresholds, and recovery behavior.

### 5.4 UI Generation

- One generated file per layout, not a bundled blob.
- Placeholder mapping must be strict: no unresolved self-mapped placeholders shipped silently.
- Mappings must include AQ aggregates, deltas, configured level averages, and controls.
- Expand/collapse controls must map to real switch entities and behave consistently.
- Current Air Control panel must sync chips + border with runtime mode, including gate-active state.
- Current Air Control chipsets must keep a consistent scan order: house -> configured level placeholders -> room-level chips.
- Current Air Control visual redesigns may change iconography, typography, grouping, spacing, and section hierarchy, but must keep static shell copy separate from backend/config-derived context labels.
- Humidity chipsets must derive zone-associated room humidity values from configured telemetry and enabled zone assignments.
- Room humidity delta chips must require attributed room/source mapping; unattributed bespoke helper chips must be excluded from generated chip rows.
- Optional temperature chipsets are controlled by `show_temperature_chips`, default disabled, and must use configured telemetry plus diagnostics slope mapping.
- Temperature chipsets must mirror the humidity chipset order: house/configured-level averages first, then zone-associated room temperatures, then room temperature slopes.
- Temperature comfort mode is configured during setup and edited post-config from the dedicated `Thresholds & Comfort` options page. Auto mode resolves seasonal comfort bands; custom mode stores explicit lower/upper comfort limits.
- Post-config zone threshold editing belongs in `Thresholds & Comfort`, separate from zone mapping/output editing.
- Default temperature comfort bands are Winter 20-21°C with warm to 21.5°C, Spring 20.5-22°C with warm to 23.5°C, Summer 21-24°C with warm to 26.5°C, and Autumn 20-21.5°C with warm to 23°C.
- Alert chipsets must show only the active lane/status chip and the resolved alert source/context chip; do not add redundant helper-switch chips that repeat the same context.
- Alert source/context chips must be hidden unless backend runtime mode or alert activity state says an alert lane is currently active.
- Horizontal chip rows must avoid aggressive reset behavior on mobile/touch layouts and expose any reset delay as a clear constant.
- Generated dashboard YAML must be re-exported with `dump_cards` after chip-row visibility or mapping options change.
- Generated V2 cards may hide the expandable output details panel when `show_output_entity_details` is false; this is display-only and must not remove output entities or runtime controls.
- The output detail chevron/expand action is a passive visibility toggle only. It may open or close the generated-card output detail panel when that panel is enabled, but it must not call services, change output helpers, select lanes, imply command success, or alter runtime state.
- New installs default to the cleaner V2 output display unless output entity details are enabled.
- Optional output/control placeholders must prune cleanly when not configured.
- No generated layout may contain malformed Lovelace blocks after pruning (for example empty `cards:` containers or invalid `type: conditional` blocks).
- `alert_only_mode` option changes must regenerate mapped cards so exported YAML reflects current control visibility.
- In alert-only mode, reason/status UI copy must remain truthful for monitoring/alerts-only operation and avoid output-control wording.

### 5.5 Services and Tooling

- Required services:
  - `refresh_ui`
  - `dump_cards`
  - `view_cards`
  - `create_dashboard`
  - `dump_diagnostics`
  - `self_check`
  - `pause_control`
  - `resume_control`
  - `purge_files`
  - `flash_lights`
- `dump_cards` contract is canonical: omit `layout` to export every cached/generated layout; supply `layout` to export only that layout.
- Each service must have schema validation and explicit error messages.
- Any new optional frontend dependency required by generated HI dashboards must be added to HI's tracked frontend dependency list so `self_check`, `v205_release_check`, diagnostics, and user-facing dependency guidance report the same Lovelace resource expectations.
- `purge_files` must show exactly what will be removed before deletion.
- Native Home Assistant config-entry diagnostics must be provided through `diagnostics.py` for user-downloadable, redacted issue attachments.
- Native diagnostics must be read-only and must not alter runtime outputs, lane selection, generated dashboards, helper state, or entity semantics.

## 6. Non-Functional Requirements (Minimum)

### 6.1 Performance and Stability

- No blocking filesystem calls in async paths.
- No unbounded event spam in recorder/websocket.
- No serialization of non-JSON-safe types in state attributes.

### 6.2 Fault Tolerance

- Integration setup must not fail due to optional components.
- Service call failures to optional outputs must be logged and skipped.
- Unavailable sensors must degrade behavior, not crash control loop.

### 6.3 Security and Safety

- Services must not execute arbitrary file operations outside scoped paths.
- Destructive actions must be explicit and user-triggered.
- Humidity, mould, and condensation visual alert rules must flash configured lights 10 times, restore the prior light state best-effort, wait 30 minutes, and repeat only while the same alert remains active.
- Visual alert repeat tasks must avoid overlapping loops and must be cancelled when the alert clears, when a higher-priority CO emergency takes over, or when runtime control is blocked.

## 7. UX Requirements

- Integration page must provide recognizable branding assets.
- Config text must clearly explain:
  - What users must provide
  - What HI auto-generates
  - Why thresholds are in given units
- UI install step must warn that backend works without optional cards, while dashboard visuals may degrade.
- Card-loading instructions must be explicit and reproducible.
- Post-configuration options must remain editable without forcing optional fields.
- Alert-only UX must clearly communicate that monitoring and alerts remain active while output controls are intentionally hidden.

## 8. Testing and Verification Baseline

Minimum verification before release:

1. Fresh install and config flow completion on supported HA version
2. Restart persistence of all generated entities and mapping
3. Pause/resume behavior from both service call and card button
4. AQ, humidity delta, condensation, mould entities visible and non-empty when source telemetry exists
5. No blocking-call warnings in logs
6. No JSON serialization errors in recorder/websocket
7. Cleanup path removes generated files and dashboard references safely
8. Reconfigure after delete works cleanly without orphaned helpers
9. Runtime/card sanity regression test passes (`tests 2/test_runtime_card_sanity.py`)
10. Alert-only toggling regenerates card exports and resulting YAML has no configuration errors from pruned control sections
11. Alert-only reason field renders monitor+alerts context and does not include stale output-control/timer lines that rely on suppressed entities
12. V2 card sanity asserts the humidity chip row excludes bespoke legacy air-control delta helpers and only includes attributed room delta chips
13. V2 card sanity asserts the optional temperature chip row appears only when configured and uses mapped house, level, room, and slope sources
14. Config/options coverage confirms `show_temperature_chips` defaults disabled and remains user-configurable from the Temperature Slope area
15. Config/options coverage confirms zone thresholds remain editable after setup for humidity high, AQ, condensation risk, and mould risk
16. Temperature comfort sensors and V2 chip colours follow seasonal/custom comfort bands
17. Backend air-control-mode simulation validates `HI Air Control Mode` and `HI Air Control Reason` from backend-consumed fake telemetry without adding runtime fake telemetry paths

## 9. Diagnostics Contract

The system must expose enough data to debug without source edits:

- Native Home Assistant config-entry diagnostics for GitHub issue attachments
- Config entry snapshot
- Resolved entity mapping
- Generated card list and outputs
- Missing entities list
- Dependency resource detection
- House humidity drift 7d dependency status for the canonical statistics source `sensor.house_humidity_mean_7d`
- Live counters (telemetry count, mapped entities, cards)
- Temperature slope source mapping for UI rendering (`slope_map` or equivalent backend-owned mapping)
- Enough telemetry, zone, option, and entity-map context for generated cards to resolve room chipsets without private hard-coded entities
- Redacted support data covering HI version, Home Assistant version, selected entities, enabled feature areas, runtime lane/mode, gates, outputs, reason text, frontend dependency status when available, generated UI summary, unavailable entities, and warnings

`HI House Humidity Drift 7d` preserves the legacy semantics of current HI house average humidity minus the canonical 7-day statistics mean. If `sensor.house_humidity_mean_7d` is missing, unknown, unavailable, or non-numeric, the drift entity must remain unavailable rather than synthesize history, and the dependency status must be exposed in sensor attributes, `self_check`, release checks, and diagnostics.

Native diagnostics must use Home Assistant redaction utilities and HI's own URL/token sanitising for sensitive fields such as tokens, secrets, passwords, API keys, webhook URLs, credential-bearing URLs, coordinates, addresses, usernames, device IDs, and unique IDs.

Dump files must be written atomically and be valid JSON.

## 10. Release Management Baseline

- Version bump and changelog entry for behavior changes
- Migration notes when entity IDs or mappings change
- Explicit "breaking change" callout if user action is required
- Tested rollback path for critical regressions
- Pull requests target `develop`; stable release history is promoted from reviewed changes.
- HACS metadata, integration metadata, README, and release notes must remain aligned.
- Release validation must confirm `hacs.json`, README, and integration manifest version before publishing.
- The GitHub Wiki is a public support manual layer. It may explain configuration,
  services, diagnostics, generated dashboards, HACS/update guidance, troubleshooting,
  AQ/CO safety, and release validation, but it must not become authority for runtime
  behavior, entity semantics, service schemas, generated dashboard logic, diagnostics,
  HACS metadata, migration requirements, release state, or deterministic lane ordering.
- HA Lab is permitted as Operational Beta Validation Infrastructure for beta package
  deploy evidence, runtime activation evidence, read-only soak/diagnostics checks,
  Stage 3 six-sensor runtime-readiness checks, and generated-card/entity-map sanity
  review. HA Lab evidence is advisory and must stay subordinate to repository source
  truth, Bella coherence review, Aetherwing runtime/risk validation, AetherCore
  governance consistency review, release-candidate validation, and Senyo approval.
  It must not become release authority, runtime authority, stable Home Assistant
  authority, or permission for autonomous mutation.
- Version release, GitHub release creation, and release tagging are not permitted until all hard release gates have passed:
  - full Bella verification for source-of-truth, release-boundary, and UI truth alignment
  - full AetherCore verification for governance, role-boundary, and release-process coherence
  - release sanity validation, including version governance and the relevant Home Assistant/runtime or direct sanity checks for the change scope
  - README approval by Senyo
- Branch/version state must be explicit and deterministic:
  - `senyo888-patch-1` may carry beta, release-candidate, or stable version labels while work is being prepared and reviewed.
  - `develop` may carry release-candidate or stable version labels only.
  - `main` carries stable production versions only, for example `2.0.6`.
  - Short-lived testing/development branches must not carry stable manifest versions.
- Stable GitHub releases must be created only from `main` after all hard release gates pass.
- Version-governance checks must run before release promotion so Codex, CI, or manual edits cannot silently promote an unstable manifest as stable.
- Accepted source, documentation, metadata, UI, or release-note changes must be made and validated in the canonical local GitHub checkout or an active worktree created from it. If a retired reference folder was used to draft or inspect work, import only the applicable files path-preservingly and validate from the canonical checkout before calling the work complete.
- At the end of every working session, report the canonical checkout branch/status. Compare the retired HI work folder only if it was used as an input or mirror during that session.
- Local-only planning docs may be mirrored for continuity, but must stay ignored, unstaged, uncommitted, and unpushed unless the user explicitly asks to publish them. Current local-only planning docs are `DESIGN_BRIEF.md`, `PROJECT_SUMMARY.md`, `ROADMAP.md`, and `PROPOSALS.md`.
- `ROADMAP.md` must be kept current as the local planning source of truth: add accepted future plans, move completed work out of active buckets, and mark deferred or rejected plans clearly instead of leaving stale roadmap items behind.
- Any import from a retired reference folder must compare target checkout state first and preserve GitHub-checkout-only files or newer workflow metadata unless the change explicitly covers those files.
- Import checks must be path-preserving and must not flatten subdirectory files into the repository root.
- After importing, run the relevant validation in the canonical checkout and report its git status/branch state.
- Commits must include both a clear title and a meaningful non-empty description/body covering what changed, why, and validation performed.
- Commit titles and descriptions must not include local filesystem paths, local checkout names, user folder names, private workspace names, or machine-specific locations.
- Public repo files, release notes, and changelog entries must not include local absolute paths, usernames, private checkout locations, secrets, device IDs, or other machine-specific details.

### 10.1 Compulsory End-of-Session Canonical Checkout Check

Every working session that changes source, documentation, metadata, tests, UI templates, services, or release notes must end with this process:

1. Confirm the canonical local GitHub checkout or active worktree with `git status --short --branch`.
2. Run the relevant validation in that canonical checkout or active worktree.
3. If a retired reference folder was used, compare only the touched applicable files and import them path-preservingly before validation.
4. Mirror local-only planning files only when needed for continuity, but do not stage, commit, or push them unless the user explicitly asks to publish them:
   - `DESIGN_BRIEF.md`
   - `PROJECT_SUMMARY.md`
   - `ROADMAP.md`
   - `PROPOSALS.md`
5. Exclude cache, temp, legacy-output, lab-private, credential, generated-noise, and machine-noise files unless the change explicitly targets them.
6. Confirm local-only planning files remain ignored before staging.
7. Stage only intended public/repo files.
8. Commit public/repo work on the active GitHub checkout branch with a clear title and a non-empty description/body that records scope, rationale, and validation.
9. Do not commit ignored local-only planning files unless the user explicitly approved publishing that exact path.
10. Report:
   - commit hash
   - branch name
   - validation results
   - whether the branch is ahead/behind origin
   - whether the work was pushed or only committed locally

If any step cannot be completed, the final response must say exactly which step failed and what remains unsynced, uncommitted, or unpushed. Do not describe repo work as complete if the canonical checkout has not been checked.

### 10.2 Repository Readiness

Humidity Intelligence should keep a lightweight GitHub setup for contributors and HACS users:

- PRs target `develop`.
- Issues use simple forms for bugs, feature requests, configuration help, and UI Gallery submissions.
- CI checks metadata, Python syntax, YAML when available, SAST/security scans, HACS validation, and Hassfest validation.
- Security scans include a required Gitleaks full-history secret scan, Bandit for
  Python, Semgrep Python rules, and a high-confidence secret pattern scan.
- Maintainer secret scanning uses redacted output, narrow false-positive handling, and
  credential rotation before any remediation claim when a real secret is found.
- Bandit excludes test-only assertions/noise so production findings remain visible.
- `hacs.json` must stay limited to HACS-supported keys; integration domain metadata belongs in `manifest.json`, not `hacs.json`.
- Hassfest is part of the repository validation baseline for Home Assistant-specific custom integration checks.
- Because the HACS package is stored in repository root (`content_in_root: true`), Hassfest CI stages files into `custom_components/humidity_intelligence` before validation.
- Manifest metadata must remain compatible with Home Assistant's integration manifest schema; release/README badges must not depend on non-schema manifest keys.
- Community files must not change runtime behavior by themselves.

### 10.3 UI Gallery Publication Standard

Gallery examples are public documentation artifacts, not private dashboard backups. Every Gallery submission must use:

```text
/ui-gallery/<card-id>/
```

Required files:

- `README.md`
- `card.yaml` or `dashboard.yaml`
- `preview.png`

Gallery content must preserve canonical backend entities/helpers and must not include private entity IDs, secrets, addresses, device IDs, tokens, or personal data.
Default generated layouts should be represented as first-party gallery examples when their screenshots or canonical card templates materially change.

### 10.4 Version Promotion Model

The canonical version-label path is:

```text
senyo888-patch-1: beta -> rc -> stable
develop: rc -> stable
main: stable release
```

Beta versions are valid for local Home Assistant validation and HACS prerelease testing.
Release-candidate versions are valid on `senyo888-patch-1` and `develop` when the
implementation is frozen except for release-blocking fixes. Stable version labels may
be staged on `senyo888-patch-1` and `develop`, but release tagging and GitHub release
creation remain blocked until final Home Assistant validation, Bella verification,
AetherCore verification, release sanity validation, README approval by Senyo, and
promotion to `main`.

For v2.0.5 and v2.0.6, this gate is completed release history. The same gate applies
again to any future version release or release tag.

The manifest version is the release-state source of truth. README badges, changelog
headings, GitHub release notes, HACS metadata checks, and release-validation services
must not imply a stable production release while the manifest carries a prerelease
suffix.

## 11. Definition of Done

A change is done only when:

1. Code compiles and integration loads with no import/runtime setup errors
2. Feature works from HA UI, not only from isolated test code
3. Logs contain no new warnings/errors related to the change
4. Services and docs are updated together
5. Generated UI output is validated against current mapping data
6. Cleanup/reconfigure path still succeeds
7. Repository guidance and changelog are updated when the change affects contributor workflow, HACS readiness, or release process
8. This design brief is updated in the same change whenever implementation, product behavior, security posture, contributor workflow, release process, or documentation expectations materially change
9. Applicable changed files have been made or imported into the canonical local GitHub checkout or active worktree, with `DESIGN_BRIEF.md`, `PROJECT_SUMMARY.md`, `ROADMAP.md`, and `PROPOSALS.md` mirrored only as ignored local-only files unless explicitly approved for publication
10. `ROADMAP.md` has been updated when future plans, completed milestones, deferred work, or release sequencing changed
11. End-of-session canonical checkout branch/status has been checked and reported
12. If public repo files changed, the canonical local GitHub checkout has been validated, staged, and committed, or the blocker has been reported explicitly

## 12. Immediate Project-Level Gaps to Watch

- Any card action that still calls legacy script names
- Any v1/v2 placeholder left unmapped to real entities
- Any event-loop blocking warning
- Any state attribute carrying non-serializable objects
- Any engine branch that assumes service availability without guard checks
- Any Current Air Control chip that lacks backend attribution or is hard-coded to a private room/entity
- Any Home Assistant entity-domain mismatch or deprecation warning introduced by newer HA releases
- Any dashboard delivery experiment that removes or weakens `dump_cards` before a backwards-compatible replacement is proven

## 13. Working Rule for Future Changes

If a change touches config flow, entity model, engine logic, or card generation, it must include:

- Code change
- Service/schema impact review
- Mapping impact review
- Diagnostics impact review
- User-facing instruction update

No partial delivery across those layers.

This brief is a living implementation contract. Future maintainers and assistants must update it proactively when an important change would otherwise leave the documented architecture, quality bar, security posture, release process, or product expectations out of date.

## 14. Roadmap Guardrails

### 14.1 V2.0.4 Stabilization Boundary

- V2.0.4 remains focused on alert binding, boost hold behavior, crash prevention, startup UI refresh, and Current Air Control UI truth.
- Home Assistant 2026.5-only dashboard strategy work must not be pulled into V2.0.4.
- Do not bump the minimum Home Assistant version unless a required feature makes it unavoidable.

### 14.2 V2.0.5 Compatibility Pass

- Treat V2.0.5 as an adoption-friendly configuration UX and support-readiness release with stable runtime semantics.
- Validate runtime behavior against Home Assistant 2026.5.
- Audit entity-domain registration warnings, frontend dependency wording, and generated card rendering.
- Keep canonical `dump_cards` behavior unchanged: unscoped exports all layouts, scoped exports one specified layout.
- Treat compatibility findings as targeted fixes, not architecture rewrites.
- Keep V2.1 Environmental Stability Intelligence work out of V2.0.5.

### 14.3 V2.0.6 Maintenance Boundary

- Treat V2.0.6 as the current stable maintenance line.
- Runtime fixes in this line may correct unsafe or misleading backend truth, including
  degraded telemetry, gate preemption, and CO clear timing, but must preserve
  deterministic lane order.
- `telemetry_unavailable` is allowed as explicit degraded runtime truth and must not be
  hidden behind normal/all-clear copy.
- Local snapshot services remain manual package-local maintenance tools only.
- V2.0.6 must not be used to pull in V2.1 Stability Score, prediction, Harmonic
  orchestration, dashboard strategy, or frontend-inferred intelligence.

### 14.4 V2.1 Dashboard Strategy Exploration

- Explore native Home Assistant dashboard strategy support as an optional UI delivery path.
- The deterministic backend engine remains authoritative and unchanged.
- `dump_cards` remains the fallback/export path.
- Any dashboard strategy must use entity mapping and diagnostics truth, avoid private entities, and never invent backend state.
