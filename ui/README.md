# Humidity Intelligence V2 UI

## Canonical Runtime Presentation Layer

---

## Purpose

The UI exists to render runtime truth.

It must:

- present active lane state
- show gate blocks
- display reason context
- reflect output stage
- mirror engine behavior

Control logic and lane priority stay in the backend engine.


The engine governs.
The UI reflects.

---

## Included Layouts

- `cards/v2_mobile.yaml`
- `cards/v2_tablet.yaml`
- `cards/v1_mobile.yaml` (deprecated in v2.0.9; use V2 Mobile for new dashboards)
- `cards/view_cards_button.yaml`

Mobile and tablet share identical control logic.

Difference:

- mobile: rounded top badges
- tablet: squared top badges

Feature parity is maintained.

---

## UI Preview

### Canonical V2 Mobile Gate State
<img src="../assets/v2_ui_gallery/v204_presence_gate_reason.png" width="320" alt="HI v2 mobile Current Air Control presence gate active preview">

<details>
<summary>Additional layout previews</summary>

### v1 Mobile (Deprecated Legacy-Compatible Skin)
<img src="../assets/readme/ui_v1_mobile.png" width="320" alt="HI v1 mobile UI preview">

### v2 Mobile (AQ State Example)
<img src="../assets/readme/ui_v2_mobile_aq.png" width="320" alt="HI v2 mobile AQ UI preview">

### v2 Tablet (Zone State Example)
<img src="../assets/readme/ui_v2_tablet_zone_2.png" width="320" alt="HI v2 tablet zone UI preview">

</details>

---

## Deployment Workflow

### Step 1 - Complete Integration Setup First

Finish:

- telemetry
- zones
- humidifiers
- AQ
- alerts
- gates

The UI maps directly to your configuration, and HI notifies you where generated UI YAML is saved.

### Step 2 - Or Generate Cards via Services

Use:

- `humidity_intelligence.create_dashboard`
- `humidity_intelligence.view_cards`
- `humidity_intelligence.dump_cards`

These external services require an authenticated admin user context.
`dump_cards` and `view_cards` write generated YAML under
`/config/humidity_intelligence/ui/`; multi-entry installations add an entry-qualified
token to each filename. Adding a second entry re-exports all loaded entries with
qualified names; removing back to one re-exports the remaining entry with unqualified
names. HI no longer refreshes superseded owned-UI names, but external consumers can
still read their stale content until exact purge. Config-entry removal deletes only
the removed entry's exact default/release-test UI exports and registered dashboard;
reports, custom exports, legacy root files, and remaining-entry superseded qualified
files are retained. Trusted first-run, options, and release-check regeneration uses
the same internal exporter without routing through the public service handler.
Startup refresh remains cache-only.
Registered dashboard YAML remains under
`/config/dashboards/<url_path>.yaml`.

`dump_cards` writes files without a completion path notification. Open
`/config/humidity_intelligence/ui/` in File Editor after the action, or use
`view_cards` when you want the exact path in a persistent notification. First-run and
relevant options regeneration also report exact written paths. `refresh_ui` updates
the in-memory cache only.

If upgrading from the config-root writer, do not copy a retained file such as
`/config/humidity_intelligence_cards_v2_mobile.yaml`; HI no longer refreshes it.
Refresh File Editor and use the new owned-directory file. Before manually deleting a
retained root or custom export, back up and disable every consumer, then delete only
that exact regular file. Never delete the whole owned directory or registered
dashboard YAML by hand.

Avoid manual YAML drift.

### Step 3 - After Any Option Change

When modifying:

- sensors
- zones
- alerts
- gates
- slope

Do:

1. save options
2. run `humidity_intelligence.refresh_ui`
3. regenerate cards if required
4. verify Current Air Control panel

Temperature chips:

- render only when `show_temperature_chips` is enabled
- colour against HI runtime comfort sensors
- use blue below band, green in band, yellow up to the backend-owned warm boundary, red above that
- show room slope chips only for configured temperature slope sources or provided slope sensors
- resolve calculated slope chips through diagnostics/backend slope mapping so Home Assistant registry-assigned entity IDs stay truthful

Control row:

- preserve the v2.0.7 tap-to-toggle behavior for the System and Manual helper buttons
- keep the Stability Score badge passive; it must not pause/resume, select lanes, or create output writes

Output details:

- render the expandable output details panel only when `show_output_entity_details` is enabled
- tap the Outputs header to toggle the expander helper; this is UI-only, with device
  commands left to the runtime/service paths
- stay display-only; the option must not affect lane selection, output writes, isolation switches, or diagnostics
- prune unresolved optional AQ aggregate rows instead of leaving `Entity not found` rows
- require a fresh `humidity_intelligence.dump_cards` export after changing visibility, templates, or backend entity mappings

---

## Placeholder Mapping Model

`ui/register.py`:

1. builds placeholder to entity map
2. substitutes canonical templates
3. prunes optional rows
4. reports unresolved non-optional placeholders

Inventory files:

- `_sensor_ids.txt`
- `_binary_ids.txt`
- `_input_boolean_ids.txt`
- `_timer_ids.txt`

---

## Unresolved Placeholder

Occurs when:

- optional feature not configured
- telemetry missing
- template updated without mapping update

Impact:

- partial card degradation
- diagnostics report the issue
- `self_check` and release validation also report missing generated-card entity references

---

## Current Air Control Visual Contract

The panel must:

- match active lane
- reflect gate border color
- display correct chip state
- keep alert chipsets to the lane/status chip plus the resolved alert source/context chip only
- show alert source/context chips only while the backend runtime mode or alert activity state says an alert lane is active
- render backend `telemetry_unavailable` as degraded UI truth, not as normal/ready or unknown frontend failure
- treat missing, unavailable, or unrecognized Air Control Mode telemetry as `UNKNOWN` without inventing a normal lane
- show readable reason text
- stay synced with real hardware behavior

If mismatch occurs:

- run `humidity_intelligence.refresh_ui`
- re-export cards
- check diagnostics

---

## Versioned UI Contract Notes

### Unreleased v2.0.10 Beta Contract

- V2 Mobile and Tablet consume the backend `humidifier_status` attribute on the
  existing Air Control Reason entity; they do not calculate control demand.
- Humidifier chips distinguish Requested, Output on, Idle, Isolated, Retrying,
  Stopping, Unknown, Degraded, and Fault. `Output on` is Home Assistant-observed
  state, not proof of physical moisture production.
- The existing humidifier-active helpers are fallback demand truth for older rendered
  cards and no longer justify a “running” claim.
- Already-pasted Manual cards are static and require a fresh `refresh_ui` plus
  `dump_cards`/`view_cards` export and paste to receive this contract.
- V1 Mobile behavior and public entities are unchanged.

### v2.0.9 Current Contract

- V1 Mobile remains exportable through the v2.0.9 line but is deprecated for new
  dashboards; use V2 Mobile for new installs.
- Dynamic V1 room labels, target-profile labels, condensation context, and mould
  context are escaped before insertion into HTML.
- Already-pasted V1 Manual cards are static and must be re-exported and re-copied to
  receive the escaping fix.
- V1 Mobile removal is deferred to a separately approved v2.1 migration proposal.

### v2.0.5 Current Contract

- `show_output_entity_details` controls only the expandable generated-card output details panel.
- Hiding output details must not affect lane selection, output writes, isolation switches, diagnostics, or entity names.
- Optional Level 1 / Level 2 display labels are configured from setup Zones and post-configuration Zone Options before Zone 1 / Zone 2 editing. They are generated-card/config-flow/support text only. Empty labels fall back to `Level 1` / `Level 2`, and changing labels requires refreshed/exported card YAML for already-pasted Manual cards.
- New generated V2 cards default to the cleaner output display unless output details are enabled.
- `v2_tablet` is the default first-install UI export layout.
- `humidity_intelligence.dump_cards` remains the supported export path after UI visibility, template, or mapping changes.
- Generated-card consumers must use `/config/humidity_intelligence/ui/`; legacy
  config-root YAML is retained and is not refreshed, migrated, or purged.
- Already-pasted Manual cards are static; refresh/export updates HI output files, not the pasted card content.

### Historical v2.0.2 UI Contract Updates

- Humidity badge colors are now target-relative:
  - `below_target` = blue
  - `in_target` = green
  - `above_target` = yellow
  - `high_risk` = red
- Target humidity display includes the active season/profile label (`Spring`, `Summer`, `Autumn`, `Winter`, or `Custom`).
- Reason window includes expanded humidifier logic context from runtime telemetry (lane scope, trigger condition, thresholds, and recovery behavior).

### Historical v2.0.4 UI Contract Updates

- Alert chipsets must not add redundant helper-switch chips after the resolved alert context.
- Chip rows expose a longer scroll reset delay marker (`15000ms`) so mobile/touch layouts are not aggressively snapped back while being read.
- Alert source chips should use `HI Active Alert Context`, backed by runtime alert telemetry, rather than inventing display-only context.

---

## Legacy v1 UI Support

`v1_mobile.yaml` remains compatible with the V2 engine through v2.0.9, but is
deprecated for new dashboards. Prefer `v2_mobile.yaml`.

Legacy support keeps the V2 backend contract. V1 backend templates and packages stay
retired.

Backend must be fully removed before using V2 runtime. Removing the V1 presentation
skin is a separate proposed v2.1 change with an explicit user migration and rollback
plan; v2.0.9 does not remove it.

---

## UI PR Checklist

- no stale placeholders
- no hardcoded alert counts
- canonical badge names preserved
- gate border sync maintained
- reason text remains readable

Humidity Intelligence V2 UI is a structured runtime interface for a deterministic environmental engine.
