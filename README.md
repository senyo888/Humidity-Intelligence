<!-- Logo and Banner -->

![Humidity Intelligence banner](assets/header.png)

# Humidity Intelligence

## Domestic Environmental Stabilisation Engine for Home Assistant

[![Latest Release](https://img.shields.io/github/v/release/senyo888/Humidity-Intelligence?display_name=tag&sort=semver)](https://github.com/senyo888/Humidity-Intelligence/releases)
[![Project Site](https://img.shields.io/badge/Project%20Site-GitHub%20Pages-5aa8d6)](https://senyo888.github.io/humidity-intelligence/)
[![HACS](https://img.shields.io/badge/HACS-Custom%20Integration-orange)](https://hacs.xyz)
[![Manifest Version](https://img.shields.io/badge/dynamic/json?label=Manifest%20Version&query=%24.version&url=https%3A%2F%2Fraw.githubusercontent.com%2Fsenyo888%2FHumidity-Intelligence%2Fsenyo888-patch-1%2Fmanifest.json&color=blue)](manifest.json)
[![License](https://img.shields.io/github/license/senyo888/Humidity-Intelligence)](LICENSE)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-ea4aaa?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/senyo888)

## Contents

- [TL;DR](#tldr)
- [Project Site and Search Discovery](#project-site-and-search-discovery)
- [Wiki and Support Manual](#wiki-and-support-manual)
- [What Is Humidity Intelligence](#what-is-humidity-intelligence)
- [V2 UI Example](#v2-ui-example)
- [Support Humidity Intelligence](#support-humidity-intelligence)
- [Why Environmental Stability Matters](#why-environmental-stability-matters)
- [Air Quality and Environmental Stability](#air-quality-and-environmental-stability)
- [Season-Aware Environmental Control](#season-aware-environmental-control)
- [Design Philosophy](#design-philosophy)
- [Architecture Overview](#architecture-overview)
- [Public Architecture Contract](#public-architecture-contract)
- [Current Release Highlights](#current-release-highlights)
- [Installation](#installation)
- [Frontend Dependencies](#frontend-dependencies)
- [Migration Guide - v1 to v2](#migration-guide---v1-to-v2)
- [Full Configuration Flow](#full-configuration-flow)
- [UI Gallery](#ui-gallery)
- [Post-Configuration Workflow](#post-configuration-workflow)
- [How to Use Services](#how-to-use-services)
- [Documentation and Support Manual](#documentation-and-support-manual)
- [Support, Diagnostics, and Issue Triage](#support-diagnostics-and-issue-triage)
- [Runtime Simulation Validation](#runtime-simulation-validation)
- [Release Notes](#release-notes)

---

## TL;DR

Humidity Intelligence is a domestic environmental control engine for Home Assistant. It watches the conditions inside a home, decides which environmental problem needs attention first, and explains that decision in plain Home Assistant entities and dashboard text.

It reads humidity, temperature, air quality, condensation, mould-risk, carbon monoxide (CO), presence, time, pause, and override signals, then resolves **one explainable control decision per evaluation cycle**.

It gives you:

- season-aware humidity targets
- deterministic lane priority
- safe degraded behavior when inputs are missing
- generated Lovelace dashboards backed by runtime truth
- native Home Assistant diagnostics for support and triage
- services for dashboard export, self-check, diagnostics, pause/resume, and release validation

Current manifest version: **v2.0.9-beta.1**.

For publication status, installed packages, and release tags, use
[GitHub Releases](https://github.com/senyo888/Humidity-Intelligence/releases) and
HACS as the user-facing record.

v2.0.9-beta.1 completes the HI-owned runtime-artifact namespace: report JSON writes
under `<config>/humidity_intelligence/exports/`, generated card YAML writes under
`<config>/humidity_intelligence/ui/`, and external writer services require an
authenticated admin context. The latest published stable release remains v2.0.8.

The deterministic runtime contract stays intact: one selected control lane per cycle,
the same public entity meanings, and output writing only through the established
runtime paths. No stored HI data migration is required, but external file consumers
must be deliberately moved to the new owned-directory paths.

---

## Project Site and Search Discovery

Humidity Intelligence now has a lightweight GitHub Pages project site:

- [Open the project site](https://senyo888.github.io/humidity-intelligence/)

The site exists to help Home Assistant users find Humidity Intelligence through
search and quickly understand what the project does. It includes crawl-friendly
metadata, a canonical URL, sitemap/robots files, and structured data for search
engines.

The project site is a project overview. The living support and runtime record stays
here: installation guidance, release notes, migration notes, diagnostics, the Wiki
support manual, GitHub releases, and the canonical `ui-gallery/` files.

---

## Wiki and Support Manual

The Wiki is the practical support manual for setup, services, diagnostics, generated
dashboards, and user-safe release checks. It exists early here so users do not have to
dig through the README before finding the longer guides.

Useful Wiki pages:

- [Home](https://github.com/senyo888/humidity-intelligence/wiki)
- [Configuration Walkthrough](https://github.com/senyo888/humidity-intelligence/wiki/Configuration-Walkthrough)
- [Services Reference](https://github.com/senyo888/humidity-intelligence/wiki/Services-Reference)
- [Generated Dashboards](https://github.com/senyo888/humidity-intelligence/wiki/Generated-Dashboards)
- [UI Gallery](https://github.com/senyo888/humidity-intelligence/wiki/UI-Gallery)
- [Diagnostics and Support Bundle](https://github.com/senyo888/humidity-intelligence/wiki/Diagnostics-and-Support-Bundle)
- [HACS and Updates](https://github.com/senyo888/humidity-intelligence/wiki/HACS-and-Updates)
- [Air Quality and CO Safety](https://github.com/senyo888/humidity-intelligence/wiki/Air-Quality-and-CO-Safety)
- [Troubleshooting Generated UI](https://github.com/senyo888/humidity-intelligence/wiki/Troubleshooting-Generated-UI)
- [Release Validation for Users](https://github.com/senyo888/humidity-intelligence/wiki/Release-Validation-for-Users)
- [Understanding Control Decisions](https://github.com/senyo888/humidity-intelligence/wiki/Understanding-Control-Decisions)
- [Getting Help](https://github.com/senyo888/humidity-intelligence/wiki/Getting-Help)

The Wiki is support guidance. Runtime behavior, entity semantics, service schemas,
generated dashboard logic, migration requirements, and release state stay owned by the
repository source, release notes, GitHub releases, and `manifest.json`.

---

## What Is Humidity Intelligence

Humidity Intelligence is designed to help stabilise the environment inside a home using real sensor telemetry and carefully coordinated smart-home control.

Most Home Assistant dashboards show readings. Humidity Intelligence turns those readings into a single, explainable control decision. It watches humidity, temperature, temperature drift, air quality, condensation risk, mould risk, and seasonal comfort patterns, then uses configured devices to guide the home back toward a more stable state.

Using sensors placed around the property, Humidity Intelligence can intelligently control devices such as:

- air purifiers
- dehumidifiers
- extractor fans
- humidifiers
- ventilation systems
- smart lighting alerts

The system works as a coordinated environmental control layer for everyday household conditions. For example:

- rising bathroom humidity can trigger extractor and ventilation behaviour before condensation settles
- poor air quality from cooking or occupancy can activate configured purification or ventilation zones
- unstable overnight humidity can be corrected gradually to improve comfort and reduce moisture stress
- dangerous conditions such as mould-risk humidity or carbon monoxide escalation can trigger higher-priority safety responses

Humidity Intelligence is intentionally deterministic. Every decision is based on visible telemetry, defined environmental rules, and priority logic rather than opaque AI behaviour or unpredictable automation chains. The goal is long-term environmental stability, comfort, and property protection rather than automation for its own sake.

The project also places strong emphasis on transparency. Users can see why actions are happening, what environmental conditions triggered them, which zone is active, and what the system is trying to achieve at any given moment. Seasonal context, comfort targets, active alerts, and runtime reasoning are surfaced directly into the UI so the system feels understandable rather than mysterious.

At its core, Humidity Intelligence is about creating a calmer, more stable living environment through continuous environmental awareness and accountable smart-home control.

<details>
<summary><strong>Quick Demo</strong></summary>


![Humidity Intelligence quick demo](assets/readme/hi_quick_demo.gif)

<p><em>Sanitized HA Lab runtime playback with output isolation enabled. The clip shows backend-owned mode, reason, chip, and badge changes across normal, Zone 1, Zone 2, AQ, alert, manual override, and unavailable-telemetry states.</em></p>

</details>

---

## V2 UI Example

<p>
  <img src="assets/v2_ui_gallery/v204_presence_gate_reason.png" width="320" alt="V2 mobile Current Air Control presence gate active state">
</p>

<details>
<summary><strong>More UI Examples</strong></summary>

Additional screenshots and layout comparisons live in the Wiki so the front page stays focused.

- [Browse the UI Gallery](https://github.com/senyo888/humidity-intelligence/wiki/UI-Gallery)
- [Open the canonical gallery source](ui-gallery/README.md)

</details>

---

## Support Humidity Intelligence

### Enjoying Humidity Intelligence?

If you're finding Humidity Intelligence useful, insightful, or just interesting to explore, consider giving the repository a star.

It helps others discover the project, supports ongoing development, and shows that this kind of deterministic, explainable approach to Home Assistant has community value.

[Star Humidity Intelligence on GitHub](https://github.com/senyo888/Humidity-Intelligence)

Optional sponsorship is also available through GitHub Sponsors:

[Support the project on GitHub Sponsors](https://github.com/sponsors/senyo888)

Sponsorship is optional and separate from support SLAs, private support obligations,
feature guarantees, release commitments, and Home Assistant / HACS behavior.

---

## Why Environmental Stability Matters

Homes rarely become damp, dry, stale, or uncomfortable because of one isolated reading. Problems usually build as patterns: a bathroom that stays wet too long, a bedroom that drifts away from the rest of the house, a winter profile that needs a lower humidity target, or an air-quality spike that lingers after cooking.

Humidity Intelligence is built for those patterns. It treats environmental stability as the goal rather than a single perfect number.

The important signal goes beyond "humidity is high" or "humidity is low." It is the shape of the problem:

- drift
- imbalance
- duration
- recurring spread patterns

That is where environmental control becomes more personal. A house can look fine in the daytime, then become uncomfortable in the evening when real life happens: dinner is cooked, showers run, baths are taken, laundry dries, doors close, bedrooms cool, and every person in the home keeps adding moisture simply by breathing. By the time everyone is trying to sleep, the air can feel heavier, bedding can feel clammy, windows can start to mist, and the room can feel unstable even if the dashboard is only showing a number.

High humidity can make sleep feel broken and heavy. It can also help condensation settle on cold surfaces, support mould and dust-mite conditions, damage finishes, and stress timber or other moisture-sensitive materials over repeated cycles.

Low humidity is quieter, but it can still be uncomfortable. Dry winter air can mean irritated airways, dry throat, coughing, itchy skin, gritty eyes, and natural materials that shrink, creak, or crack as they repeatedly dry out.

Humidity Intelligence is designed for that domestic rhythm. It can see rooms rising or falling away from the active seasonal target, explain the condition, and use configured ventilation, dehumidification, or humidification before short-lived discomfort becomes repeated instability.

For the fuller explanation, including property impact, health comfort, sleep, night-time humidity sources, dry-air effects, plant health, and research context, see the Wiki guide: [Why Environmental Stability Matters](https://github.com/senyo888/humidity-intelligence/wiki/Why-Environmental-Stability-Matters).

---

## Air Quality and Environmental Stability

Humidity Intelligence is broader than humidity alone. It contributes to environmental stability by surfacing indoor air-quality signals from configured Home Assistant entities and, where users have configured suitable outputs, using available devices such as air purifiers or ventilation fans to respond to poor air-quality conditions.

Air-quality support is telemetry-driven. Humidity Intelligence reflects configured sensors, entities, thresholds, and output devices; the UI and reason panel stay aligned with backend/entity truth.

The wider air-quality (AQ) telemetry family in the current configuration flow includes indoor air quality (IAQ), fine particulate matter (PM2.5), volatile organic compounds (VOCs), carbon dioxide (CO2), and carbon monoxide (CO), depending on what the user configures.

Where an AQ lane is configured, it remains below safety and moisture-risk alert lanes in the deterministic priority order. Carbon monoxide emergency handling remains the highest-priority runtime lane, while normal AQ responses are deferred when higher-priority alert or zone lanes are active.

Carbon-monoxide safety deserves primary, certified protection. Humidity Intelligence can reflect configured CO telemetry as an additional Home Assistant awareness layer, while certified carbon-monoxide alarms remain the primary detection and alerting system.

Detailed AQ and CO guidance lives in the support manual:

- [Air Quality and CO Safety](https://github.com/senyo888/humidity-intelligence/wiki/Air-Quality-and-CO-Safety)
- [Understanding Control Decisions](https://github.com/senyo888/humidity-intelligence/wiki/Understanding-Control-Decisions)

---

## Season-Aware Environmental Control

`56%` can mean different things.

The same humidity reading can mean different things in January and July. A home that feels stable in summer may be too damp for a cold winter envelope, while an aggressive winter target may be unnecessarily dry in warmer months.

Humidity Intelligence evaluates humidity **relative to the active target profile**:

- Winter defaults to a lower comfort band than summer
- Spring and autumn use intermediate bands
- Custom target profiles are supported when configured

Interpretation now follows target-relative states:

- `below_target` -> dry for the active profile
- `in_target` -> stable band for the active profile
- `above_target` -> elevated for the active profile
- `high_risk` -> materially above the active profile's safe limit

This keeps stability as the primary goal while making evaluation season-correct and explainable.

Temperature comfort uses the same source-of-truth approach for display, so dashboard colours and chips follow backend comfort sensors rather than card-only assumptions:

- Automatic mode resolves the active seasonal comfort band and warm boundary
- Custom mode allows a fixed lower/upper comfort band and derives the warm boundary as custom high + `1.0°C`
- Temperature chips use HI comfort sensors, not card-only thresholds

Default temperature comfort bands:

- Winter: blue below `20°C`, green `20-21°C`, yellow `21-21.5°C`, red above `21.5°C`
- Spring: blue below `20.5°C`, green `20.5-22°C`, yellow `22-23.5°C`, red above `23.5°C`
- Summer: blue below `21°C`, green `21-24°C`, yellow `24-26.5°C`, red above `26.5°C`
- Autumn: blue below `20°C`, green `20-21.5°C`, yellow `21.5-23°C`, red above `23°C`

---

## Design Philosophy

Humidity Intelligence is built around a simple premise: a home works better with one visible environmental controller than with a loose pile of automations competing for control. That controller should read configured telemetry, apply a stable priority hierarchy, and resolve one explainable outcome per evaluation cycle.

The engine is deterministic by design. It avoids guesses and hidden preferences. It evaluates season-aware humidity targets, safety gates, alert conditions, zone demand, air quality state, and humidifier needs through explicit rules so runtime behavior can be inspected, predicted, and explained.

The UI is a truth surface. Current Air Control, chips, diagnostics, and exported cards reflect backend telemetry, entity mappings, runtime mode, and degraded-state reasons. If an input is missing or an output is unavailable, Humidity Intelligence shows that condition and falls back safely without pretending the home is stable.

The architectural preference is calm regulation over automation chaos:

- one selected ventilation lane per evaluation cycle
- CO emergency and alert hierarchy before comfort correction
- humidifier lanes kept independent from ventilation resolution
- global gates and overrides visible when they suppress control
- generated dashboards aligned with backend truth only
- safe degraded behavior before blind output writes

The result should feel steady in a domestic environment: readable, conservative, and accountable when conditions change.

---

## Architecture Overview

Humidity Intelligence operates across three defined layers. Each layer has a clear job: turn readings into meaning, decide which lane has authority, and show the result without inventing extra logic.

### 1) Intelligence Layer - Environmental Physics

This layer turns raw telemetry into structured environmental signals:

- dynamic house average humidity
- 7-day mean and drift tracking, using the canonical `sensor.house_humidity_mean_7d` statistics dependency
- Magnus dew point calculation
- condensation spread (`temperature - dew_point`)
- mould risk normalization
- worst-room detection
- binary danger states

This layer models risk. Control happens in the deterministic priority engine.

### 2) Control Layer - Deterministic Priority Engine

This layer decides which single lane gets control authority during the current evaluation cycle.

Canonical runtime order:

1. CO Emergency: highest-priority safety lane
2. Humidity Danger
3. Mould Danger
4. Mould Risk
5. Condensation Danger
6. Condensation Risk
7. Zone 1 / Zone 2
8. Air Quality
9. Normal

Alert lanes resolve the originating sensor to a configured room/zone, then use that zone's boost fan level as the single deterministic control path. Once an actionable alert is selected, HI holds that boost path until the originating alert clears unless a higher-priority alert appears.

If an alert candidate cannot be mapped to a safe zone output, HI skips blind boosts. The reason panel reports the unmapped/degraded alert and automation continues to the next eligible priority.

Built-in humidity, mould, and condensation risk states are treated as alert candidates when they can be traced back to telemetry. This keeps zone boost behavior and the companion alert chip aligned even if a matching explicit alert row has not been added.

Humidity Danger alerts follow the active target profile's high-risk threshold at runtime. Legacy saved humidity threshold values are ignored for that alert type, so seasonal/custom profile changes immediately affect alert evaluation.

Custom trigger entities and custom binary sensors are not part of the alert flow. Optional alert configuration is for enabling HI alert handling and adding visual indicator rules only; the alert source remains HI's deterministic intelligence layer.

Boost settings should normally be higher than the standard zone fan level. Zone control handles normal correction; boost is reserved for danger escalation such as condensation, mould risk, or humidity danger.

Humidifier lanes operate independently where safe.

Each evaluation cycle:

1. global gates evaluated
2. lanes resolved top-down
3. first valid lane wins
4. lower lanes remain blocked

Only one comfort/control lane drives outputs at a time.

This keeps control ownership explicit and prevents lower-priority comfort responses from fighting safety or risk responses.

### 3) Presentation Layer - UI Truth Contract

This layer makes the engine understandable. It reflects runtime truth:

- active lane
- gate blocks
- override state
- reason text
- output stage transparency

The engine decides; the UI renders.

Generated V2 control-row colours separate selected command lanes from environmental risk: red row styling is reserved for selected alert/CO runtime truth. Degraded or unmapped alert candidates remain visible in reason text instead of occupying primary Current Air Control chip-row space.

## Public Architecture Contract

The tracked public architecture contract lives in [ARCHITECTURE.md](ARCHITECTURE.md).
It records the durable runtime, UI-truth, Home Assistant compatibility, and release
authority rules used for public review.

Maintainer-only planning notes may exist locally, but public contributor correctness
must be reviewable from tracked repository files.

---

## Current Release Highlights

- working-branch integration metadata is `2.0.9-beta.1`; GitHub Releases and HACS
  remain the user-facing record for the latest published stable release, v2.0.8
- diagnostics and release-check report writers now accept only exact lowercase
  `humidity_intelligence_*.json` custom filenames, preserve their existing defaults,
  and write only under `<config>/humidity_intelligence/exports/`
- the fixed self-check report now shares that secure export directory, and generated
  card YAML now writes under `<config>/humidity_intelligence/ui/`; registered
  dashboard YAML remains under `<config>/dashboards/`
- every external `dump_diagnostics`, `self_check`, `v205_release_check`, `dump_cards`,
  and `view_cards` call now requires an authenticated admin user context; trusted
  setup/options/release-check regeneration calls the internal exporter directly,
  while startup refresh remains cache-only
- first-run setup now starts with a welcome/setup-strategy page before Frontend
  Dependencies, so users can save a small initial sensor set and return through
  Options for deeper tuning
- Temperature Slope setup/options now handles collapsed Advanced source lists safely:
  empty submitted source lists fall back to the configured temperature sensors or
  saved source defaults instead of hiding a required-source validation loop
- default generated V2 dashboards lean into status and review: pause/resume and
  standalone View Cards workflows live in explicit service/admin paths, while the
  default runtime card surfaces stay calm and inspection-focused
- the generated V2 Pause LIVE tile is replaced with a passive compact Stability
  preview badge that reads future v2.1 diagnostics when present; score calculation,
  sensor creation, lane selection, and runtime control stay backend-owned
- the Stability preview badge uses a 10 BPM shimmer cadence: one 6-second animation
  cycle for current/complete states
- every `pause_control` / `resume_control` call now requires admin user context;
  `entry_id` still limits the action to the supplied config entry
- explicit `create_dashboard` and `purge_files` service calls now require admin user
  context; first-run dashboard setup uses a trusted internal path, and purge presents
  an exact blocking target preview before deletion and reports partial failures
- the V1 Mobile skin remains available through the v2.0.9 line but is deprecated for
  new dashboards; its dynamic room/risk/profile HTML is escaped, and V2 Mobile is the
  recommended replacement ahead of a separately reviewed v2.1 removal
- native diagnostics and support-oriented exports now favor sanitized structure,
  counts, statuses, and summaries instead of raw entity maps, state dumps, room
  names, or Lovelace resource URLs; validation reports may still include configured
  or generated entity IDs needed to debug missing mappings
- local issue-triage private report writing is confined through the private atomic
  writer, keeping public issue/support flows separate from local report output
- the tracked secret scan now fails closed when no tracked files are selected
- `v205_release_check` preserves its service name while accepting the v2.0.9
  beta/rc/stable line for generated-card and release-validation support checks
- Home Assistant Area/Label setup assistance can suggest defaults from registry
  metadata, but saved HI telemetry, zone, AQ, humidifier, and alert mappings remain
  the only runtime truth
- release-prep service usage: run `self_check` or `v205_release_check` for support
  validation; use `refresh_ui` to rebuild the rendered in-memory cache, then
  `dump_cards` or `view_cards` to write fresh YAML. Already-pasted Manual cards remain
  static and must be re-copied from the latest export
- runtime contract: deterministic lane ordering, output-writer boundaries, entity
  semantics, migration shape, and UI truth stay aligned with the existing backend
  model

Upgrade note: after updating HI through HACS or file replacement, restart Home
Assistant so Home Assistant reloads the manifest version and updated services. Use
config-entry reload after option changes once the updated code is already loaded.
Run `humidity_intelligence.dump_cards` and paste the updated YAML into existing Manual
cards if you use generated Current Air Control cards, the default V2 control row, or
output-detail surfaces; already-pasted Manual cards are static and do not inherit
backend template changes automatically. Users retaining V1 Mobile must also re-export
and re-copy that card to receive the v2.0.9 HTML-escaping fix.

---

## Installation

### Option A - HACS (Recommended)

Requires Home Assistant **2026.5.1** or newer.

1. Add custom repository:
   `https://github.com/senyo888/Humidity-Intelligence`
   Category: Integration
2. Install **Humidity Intelligence**
3. Restart Home Assistant
4. Go to Settings -> Devices & Services -> Add Integration
5. Search for **Humidity Intelligence**
6. Begin configuration

---

## Frontend Dependencies

Humidity Intelligence runs fully at the backend level. The richer dashboard experience depends on a small set of frontend cards.

You can complete setup without them, but if you want the **full visual system (badges, charts, reason panel, mobile/tablet layouts)**, these are strongly recommended.

### Core Recommendation

Install via HACS before anything else.

### Frontend Dependencies (UI Layer)

The following projects power the visual layer of Humidity Intelligence:

- [card-mod](https://github.com/thomasloven/lovelace-card-mod)
  Advanced styling engine used for dynamic visuals, glow states, and conditional UI rendering.
- [button-card](https://github.com/custom-cards/button-card)
  Core building block for badges, status indicators, and interactive UI elements.
- [mod-card](https://github.com/thomasloven/lovelace-card-mod)
  Structural wrapper used to apply styling cleanly across complex card layouts.
- [apexcharts-card](https://github.com/RomRider/apexcharts-card)
  Powers historical graphs, trend analysis, and environmental visualisation.

### Installation Notes

- All frontend dependencies can be installed via HACS (**Frontend** section).
- After installing, hard refresh your browser or use a new session to avoid caching issues.
- If you skip these, the system still runs, but UI elements may not render correctly.

### Acknowledgements

Huge respect and thanks to the creators of these projects. Humidity Intelligence builds on top of their work:

- **Thomas Loven** for card-mod and mod-card
- **Custom Cards Community** for button-card
- **RomRider** for apexcharts-card

These tools are foundational to the Home Assistant ecosystem and give the dashboard layer its polish.

### Suggested Setup Approach

If you are unsure:

1. Install HACS
2. Install the frontend dependencies above
3. Continue with the configuration flow

Or:

- Skip for now
- Complete backend setup first
- Add the UI layer afterwards

### Configuration Method

Recommended: staged setup. Add a small core sensor set first, complete setup,
save the integration, then return through Options to add the remaining sensors,
rooms, zones, air-quality inputs, humidifiers, alerts, and dashboard exports.
This gives you a saved baseline before the configuration grows.

Advanced: full setup. If your sensor layout is already mapped, add every sensor
during first setup and continue through the whole flow in one pass.


---

## Migration Guide - v1 to v2

V1 was template-based.
V2 is a structured integration with configuration flow and runtime validation.

Migration is required.

---

### Important - HACS Repository Type Change

V1 was installed as a **Template** in HACS.
V2 is a **Custom Integration**.

If you skip this step, HACS may continue installing files to:

```text
/config/custom_templates/
```

This will break updates and prevent V2 from loading correctly.

### Step 0 - Remove V1 from HACS (Required)

1. Go to **HACS -> Humidity Intelligence**
2. Open the menu (three dots)
3. Click **Remove**
4. Restart Home Assistant

### Step 0.1 - Re-add Repository as Integration

1. Go to **HACS -> Menu -> Custom repositories**
2. Add:

   ```text
   https://github.com/senyo888/Humidity-Intelligence
   ```

3. Set category to:

   ```text
   Integration
   ```

4. Install **Humidity Intelligence**
5. Restart Home Assistant

Correct install path should now be:

```text
/config/custom_components/humidity_intelligence/
```

---

### Step 1 - Remove v1 Backend

Delete:

```text
/config/custom_templates/humidity_intelligence.jinja
/config/packages/humidity_intelligence.yaml
```

Remove any related includes from `configuration.yaml`.
Restart Home Assistant.

### House Humidity Drift 7d

V2 preserves the existing drift meaning:

```text
HI House Humidity Drift 7d = current HI house average humidity - sensor.house_humidity_mean_7d
```

V1 created `sensor.house_humidity_mean_7d` with Home Assistant's Statistics helper. Clean V2 installs need the same helper unless it already exists.

Create or verify the Statistics helper:

- Name: `House Humidity Mean 7d`
- Source entity: the actual registered `HI House Average Humidity` entity
- State characteristic: `mean`
- Max age: `7 days`
- Entity ID: `sensor.house_humidity_mean_7d`

```yaml
sensor:
  - platform: statistics
    name: "House Humidity Mean 7d"
    entity_id: <actual registered HI House Average Humidity entity>
    state_characteristic: mean
    max_age:
      days: 7
```

Since v2.0.6, HI reports missing-helper guidance through the drift sensor attributes, diagnostics, `self_check`, `v205_release_check`, and Home Assistant Repairs. The setup/options Frontend Dependencies pages remain frontend-only; drift helper truth belongs on diagnostics and repair surfaces.

Do not fabricate history. If the helper is missing, warming up, unavailable, or not numeric, HI reports that dependency state instead of synthesizing a drift value.

If the helper exists but reports `unknown`, `unavailable`, a non-numeric state, low `age_coverage_ratio`, or `source_value_valid: false`, HI treats the helper as still warming up or awaiting usable recorder data.

Let Home Assistant build real history. Drift becomes numeric automatically once the helper has enough recorder/statistics samples for a usable 7-day mean.

### Step 2 - Remove v1 UI YAML

Delete:

```text
/config/www/.../v1_mobile.yaml
/config/lovelace/v1_mobile.yaml
```

Restart if using YAML dashboards.

This cleanup step applies only to the retired pre-integration V1 files listed above.
It does not remove the V2-generated `v1_mobile` compatibility skin described below.

### v1 UI Compatibility And Deprecation

The classic four-badge + Comfort Band layout remains compatible on the V2 engine
through the v2.0.9 line, but it is deprecated for new dashboards. Use V2 Mobile for
new installs. V1 Mobile removal is proposed for v2.1 and requires a separate approved
migration; it is not removed by v2.0.9.

- V1 UI = presentation skin
- V2 = runtime engine

Classic visual layouts remain available during v2.0.9. Re-export and re-copy the V1
card after updating so existing pasted dashboards receive the dynamic-text HTML
escaping fix.

### Post-Migration Check

After install, verify:

- Integration loads in **Settings -> Devices & Services**
- `/custom_templates/` references are gone
- UI renders correctly

If needed, refresh UI:

```yaml
service: humidity_intelligence.refresh_ui
```

### Summary

- V1 = Template system (`custom_templates`)
- V2 = Integration (`custom_components`)
- HACS must be reconfigured to recognise the new structure

This keeps HACS updates, install location, and integration loading aligned with the V2 package layout.


---

## Full Configuration Flow

First install follows a staged setup path. Essentials stay visible first; expert controls sit inside live **Show advanced tuning** sections so normal setup stays approachable.

Setup shape:

1. Welcome and setup strategy
2. Frontend Dependencies
3. Global Gates
4. Telemetry Inputs
5. Temperature Slope
6. Zones
7. Humidifiers
8. Air Quality
9. Alerts and CO Emergency
10. UI Deployment

Key setup guidance:

- add humidity and temperature telemetry for active levels
- use the first-run welcome page as the high-level setup strategy: save the smallest
  useful initial sensor set, then return through Options for detailed tuning
- assign telemetry to stable, readable rooms and levels
- review any Home Assistant Area/Label setup suggestions before saving them as
  explicit HI room or level values; Area and Label metadata is advisory only
- let HI calculate Temperature Slope from configured temperature sensors unless you
  already have trusted slope entities; if the collapsed Advanced source list submits
  empty, HI falls back to the configured/saved temperature sources instead of
  inventing a hidden source or re-rendering a confusing validation error
- optionally set Level 1 / Level 2 display labels from Zones before Zone 1 / Zone 2 setup; labels are display-only and fall back to `Level 1` / `Level 2`
- keep zone labels and output mappings clear enough for reason text and diagnostics
- use recommended thresholds first, then tune from options after observing behavior
- keep AQ and CO telemetry grounded in configured Home Assistant entities
- use zone boost levels for alert escalation where alerts resolve to a mapped zone
- use the generated dashboard export after setup or option changes

The default first UI export is `v2_tablet`. `show_output_entity_details` is display-only and controls whether generated cards include the expandable output details panel.
Level display labels are also display-only. Changing them updates generated-card/config-flow/support text after options are saved and cards are refreshed. Entity IDs, helpers, levels, zones, outputs, and runtime lanes keep their existing identities.

Home Assistant Area and Label setup assistance is read-only. HI may suggest room or
level defaults from registry metadata, and diagnostics may report sanitized mismatch
counts, but runtime control keeps using saved HI telemetry, zone, AQ, humidifier, and
alert mappings.

Detailed manual:

- [Configuration Walkthrough](https://github.com/senyo888/humidity-intelligence/wiki/Configuration-Walkthrough)
- [Air Quality and CO Safety](https://github.com/senyo888/humidity-intelligence/wiki/Air-Quality-and-CO-Safety)
- [Generated Dashboards](https://github.com/senyo888/humidity-intelligence/wiki/Generated-Dashboards)

---

## UI Gallery

The browseable UI Gallery lives in the Wiki:

- [UI Gallery](https://github.com/senyo888/humidity-intelligence/wiki/UI-Gallery)

Canonical YAML, preview assets, and contribution rules remain versioned in this repository:

- [Gallery source](ui-gallery/README.md)
- [Default V2 Mobile AQ](ui-gallery/default-v2-mobile-aq/README.md)
- [Default V2 Tablet Zone 2](ui-gallery/default-v2-tablet-zone-2/README.md)
- [Default V1 Mobile (deprecated)](ui-gallery/default-v1-mobile/README.md)
- [Contributing UI Gallery examples](ui-gallery/CONTRIBUTING.md)

The Wiki is a visual navigation layer. Repository files remain the source of truth
for dashboard YAML, generated-card compatibility, entity semantics, and contribution
review.

For new gallery submissions, open a repository pull request. Do not treat Wiki-only
YAML as canonical install guidance.

---

## Post-Configuration Workflow

When modifying options:

1. change one section at a time
2. save
3. run `humidity_intelligence.refresh_ui` or export cards where the current release guidance calls for it
4. verify Current Air Control mode, gate chips, reason text, and output behavior

Common post-configuration areas:

- `Sensors`: add, edit, or delete telemetry rows; Area/Label suggestions are
  advisory defaults only and become HI truth only if saved into explicit fields
- `Global Gates`: edit time, presence, alert-only, and target-profile behavior
- `Zones`: edit display-only Level 1 / Level 2 labels before Zone 1 / Zone 2 configuration
- `Thresholds & Comfort`: review comfort mode and zone thresholds
- `Humidifiers`: add or edit per-level humidifier lanes
- `Air Quality`: add or edit AQ lanes, triggers, outputs, and thresholds
- generated UI: run `humidity_intelligence.dump_cards` and paste refreshed YAML into existing Manual cards when card visibility, template, backend entity mapping, or generated-card options change

Detailed manual:

- [Configuration Walkthrough](https://github.com/senyo888/humidity-intelligence/wiki/Configuration-Walkthrough)
- [Generated Dashboards](https://github.com/senyo888/humidity-intelligence/wiki/Generated-Dashboards)
- [Troubleshooting Generated UI](https://github.com/senyo888/humidity-intelligence/wiki/Troubleshooting-Generated-UI)

---

## How to Use Services

Use Home Assistant Developer Tools:
1. Go to **Developer Tools -> Actions**.
2. Select service domain: `humidity_intelligence`.
3. Pick a service.
4. Fill service data (YAML or UI fields).
5. Run and verify result in UI/notifications/files.

Notes:
- `entry_id` is optional for most services. If omitted, HI uses all entries or first valid entry based on service behavior.
- `dump_diagnostics`, `self_check`, and `v205_release_check` JSON is written under
  `<config>/humidity_intelligence/exports/`. Generated card YAML is written under
  `<config>/humidity_intelligence/ui/`. Registered dashboard YAML remains under
  `<config>/dashboards/<url_path>.yaml`.
- Single-entry card exports retain unqualified names such as
  `humidity_intelligence_cards_v2_mobile.yaml`. Multi-entry installations add an
  entry-qualified token before the layout to prevent one entry overwriting another.
  Adding a second entry re-exports all loaded entries with qualified names; removing
  back to one re-exports the remaining entry with unqualified names. HI no longer
  refreshes superseded owned-UI names, but external consumers can still read their
  stale content. Follow the latest notification rather than inferring a path.
- Default generated V2 dashboards are read-only status surfaces. Runtime-changing
  actions such as pause/resume, dashboard creation, and file cleanup belong in
  Home Assistant service/admin workflows. System and Manual buttons keep the
  v2.0.7 helper-toggle behavior.
- The generated V2 control row uses a passive Stability preview badge instead of
  a Pause LIVE control tile. It reflects future v2.1 diagnostics when available
  while score calculation, lane selection, and runtime control stay backend-owned.
  The current/complete shimmer uses a slow 10 BPM cadence, one pulse every 6 seconds.
- Every `pause_control` / `resume_control` call requires an admin user context.
  Supplying `entry_id` scopes the action to that config entry; it does not bypass the
  authorization check. Background automations/scripts whose action context has no
  `user_id` are intentionally rejected, even when configured by an admin. Invoke
  these services from an authenticated admin UI or API session.
- Explicit `create_dashboard` and `purge_files` calls require an admin user context.
  First-run dashboard creation remains available only through the trusted setup path.
  A created dashboard is still registered with its normal non-admin viewing setting;
  the new gate controls creation, not later visibility.
- Every external `dump_diagnostics`, `self_check`, `v205_release_check`, `dump_cards`,
  and `view_cards` call also requires an admin user context. Contextless background
  automations/scripts cannot invoke these writers; use an authenticated admin UI,
  REST, or WebSocket session. There is no YAML option that manufactures an admin
  context for a background automation. HI-owned setup/options and release-check
  test-card regeneration remains available through the trusted internal exporter;
  startup refresh remains cache-only.
- `purge_files` validates the complete fixed HI-generated target set, posts the exact
  existing-file/dashboard preview with a blocking notification, then deletes. Any
  file or dashboard deletion failure is surfaced as an incomplete purge instead of
  being silently treated as success. An `entry_id`-scoped purge does not remove
  report exports. Only an unscoped all-entry purge may remove the exact default
  diagnostics and fixed self-check reports. Exact default/per-entry card and
  release-test card exports plus registered dashboards are purge-owned. Custom card
  exports, custom reports, release-check reports, and all legacy config-root JSON/YAML
  remain retained.
- Config-entry removal separately removes that entry's exact default/release-test card
  exports and registered dashboard, but does not remove reports, custom card exports,
  or legacy root files. When a multi-entry installation returns to one entry, the
  remaining entry is re-exported with unqualified names; its superseded qualified
  files stay externally readable until an exact previewed purge.
- `v205_release_check` is the backward-compatible validation service name. In v2.0.8
  and v2.0.9 it accepts the v2.0.5-v2.0.9 beta/rc/stable line and is runtime/device
  read-only: it writes its validation report, and `write_test_exports: true`
  additionally writes card-export test files.
- `dump_diagnostics` and native diagnostics are support surfaces; support exports are
  sanitized for public/private boundary safety where possible, but
  `self_check` / `v205_release_check` validation reports may include entity IDs
  needed for mapping support. Treat those validation reports as local/private until
  reviewed or sanitized before public sharing.
- Custom filenames for `dump_diagnostics` and `v205_release_check` must use the
  exact lowercase `humidity_intelligence_*.json` pattern. The defaults are
  unchanged. JSON report services now write under
  `<config>/humidity_intelligence/exports/`; existing root-level reports are not
  moved, copied, or deleted. Generated card consumers must similarly move from the
  config-root filename to `<config>/humidity_intelligence/ui/<filename>`. HI does not
  dual-write, copy, symlink, move, or delete legacy root JSON/YAML, so verify a fresh
  owned-directory artifact before updating file sensors, shell commands, scripts, or
  support tools; then disable the stale root consumer explicitly. Update callers that
  supply another custom report filename. Fully restart Home
  Assistant after installing this package update; a config-entry reload alone does
  not load the changed service code or schema. Concurrent writes are serialized
  inside HI and each replacement is atomic; the last atomic replacement wins, but
  callers must not rely on invocation order.

- Rollback restores the complete prior integration package and any backed-up consumer
  paths, followed by a full Home Assistant restart. Files already written under
  `<config>/humidity_intelligence/exports/` or
  `<config>/humidity_intelligence/ui/` remain in place and are not moved back to the
  config root. Reverting package code alone does not refresh a legacy root artifact;
  consumers must be deliberately pointed at the restored path.

Common service groups:

| Service | Use |
| --- | --- |
| `dump_cards` | admin-only export of generated card YAML for static Manual dashboards |
| `refresh_ui` | rebuild placeholder mappings and refresh cached rendered UI output |
| `view_cards` | admin-only render/export plus an exact file-path notification |
| `create_dashboard` | admin-only creation of a Lovelace dashboard from a rendered HI layout |
| `flash_lights` | test configured visual alert behavior |
| `pause_control` / `resume_control` | admin-only pause or resume for one supplied entry or all entries |
| `self_check` | admin-only fixed export of mapping, generated-card entity, telemetry, drift-helper, and frontend-dependency checks |
| `v205_release_check` | admin-only runtime-safe v2.0.5-v2.0.9 generated-card and release-validation support checks |
| `create_local_backup` / `list_saved_versions` | manage package-local HI snapshots for advanced validation |
| `dump_diagnostics` | admin-only export of fuller local diagnostics for maintainer/debug workflows |
| `purge_files` | admin-only, previewed removal of fixed generated HI artifacts with partial-failure reporting |

Example card export:

```yaml
service: humidity_intelligence.dump_cards
data:
  filename: humidity_intelligence_cards
  layout: v2_mobile
```

Example release validation export:

```yaml
service: humidity_intelligence.v205_release_check
data:
  filename: humidity_intelligence_v205_release_check.json
```

### Finding A Newly Dumped Card

Existing users should expect the location to change in v2.0.9:

- `dump_cards` writes under `<config>/humidity_intelligence/ui/` but does not post a
  completion path notification. Open that directory in File Editor after the action.
- `view_cards` writes the selected layout to the same directory and posts the exact
  path in a persistent notification. Use it when file discovery is the priority.
- first-run and relevant options regeneration also post every exact written path.
- `refresh_ui` only rebuilds the rendered in-memory cache; it does not write YAML.

For a single-entry installation using the default basename, a mobile export is
`<config>/humidity_intelligence/ui/humidity_intelligence_cards_v2_mobile.yaml`.
Multi-entry installations insert an entry-qualified token, and custom basenames
produce different filenames. Always use the path reported by `view_cards` or the
setup/options notification when either applies.

If File Editor was already open, refresh its file tree or reopen it after export. If
the file still does not appear, confirm that the action was run from an authenticated
admin UI/API session and check the Home Assistant log for an export error. There is
no config-root fallback.

An older file such as
`<config>/humidity_intelligence_cards_v2_mobile.yaml` is retained for migration
safety but is no longer refreshed. A newer modification time on that legacy file does
not prove that v2.0.9 wrote it; do not copy it after upgrading.

### Manually Removing Files Purge Intentionally Retains

`purge_files` deliberately leaves legacy config-root JSON/YAML, custom card exports,
custom reports, and release-check reports in place. Remove one manually only after
confirming that no file sensor, shell command, script, support tool, or other consumer
still uses it:

1. Generate and validate the replacement in
   `<config>/humidity_intelligence/exports/` or
   `<config>/humidity_intelligence/ui/`.
2. Back up the exact consumer definition and any artifact that must be retained.
3. Update or disable the old consumer, then verify it no longer reads the retained
   path.
4. In File Editor, Studio Code Server, Samba, or SSH, delete only the exact regular
   file you have identified. Do not delete either owned directory, use wildcard
   deletion, or follow a symlink/non-regular object.
5. Refresh the file view and confirm that the new owned-directory artifact and active
   Manual card remain correct.

Do not manually delete registered dashboard YAML from
`<config>/dashboards/<url_path>.yaml`; use the previewed HI cleanup path or Home
Assistant dashboard management so registration state and the file stay aligned.
Deleting an unused retained artifact alone does not require a Home Assistant restart.
Changing a consumer may require that consumer's normal reload.

For GitHub support issues, prefer the native Home Assistant diagnostics download from the Humidity Intelligence integration entry. Diagnostics and `dump_diagnostics` exports favor sanitized structure, counts, statuses, and redaction over raw maps or state dumps. `self_check` and release-validation reports can include configured/generated entity IDs needed to debug missing mappings, so treat those exports as local/private until reviewed or sanitized before public sharing. Use `dump_diagnostics` for fuller local maintainer/debug workflows after reviewing the export.

Detailed manual:

- [Services Reference](https://github.com/senyo888/humidity-intelligence/wiki/Services-Reference)
- [Generated Dashboards](https://github.com/senyo888/humidity-intelligence/wiki/Generated-Dashboards)
- [Troubleshooting Generated UI](https://github.com/senyo888/humidity-intelligence/wiki/Troubleshooting-Generated-UI)
- [Diagnostics and Support Bundle](https://github.com/senyo888/humidity-intelligence/wiki/Diagnostics-and-Support-Bundle)
- [Release Validation for Users](https://github.com/senyo888/humidity-intelligence/wiki/Release-Validation-for-Users)

---

## Documentation and Support Manual

The early [Wiki and Support Manual](#wiki-and-support-manual) section links the main
manual pages. This section keeps the deeper support and background references in one
place without making the README duplicate the full manual.

The README covers installation, current release highlights, core usage, screenshots,
services, support entry points, and release notes.

For longer support guidance, see the Humidity Intelligence Wiki:

- [Getting Help](https://github.com/senyo888/humidity-intelligence/wiki/Getting-Help)
- [Diagnostics and Support Bundle](https://github.com/senyo888/humidity-intelligence/wiki/Diagnostics-and-Support-Bundle)
- [Generated Dashboards](https://github.com/senyo888/humidity-intelligence/wiki/Generated-Dashboards)
- [UI Gallery](https://github.com/senyo888/humidity-intelligence/wiki/UI-Gallery)
- [HACS and Updates](https://github.com/senyo888/humidity-intelligence/wiki/HACS-and-Updates)
- [Configuration Walkthrough](https://github.com/senyo888/humidity-intelligence/wiki/Configuration-Walkthrough)
- [Understanding Control Decisions](https://github.com/senyo888/humidity-intelligence/wiki/Understanding-Control-Decisions)
- [Why Environmental Stability Matters](https://github.com/senyo888/humidity-intelligence/wiki/Why-Environmental-Stability-Matters)
- [Air Quality and CO Safety](https://github.com/senyo888/humidity-intelligence/wiki/Air-Quality-and-CO-Safety)
- [Troubleshooting Generated UI](https://github.com/senyo888/humidity-intelligence/wiki/Troubleshooting-Generated-UI)
- [Release Validation for Users](https://github.com/senyo888/humidity-intelligence/wiki/Release-Validation-for-Users)
- [FAQ](https://github.com/senyo888/humidity-intelligence/wiki/FAQ)

The Wiki is a support manual. Runtime behavior, entity semantics, generated dashboard
logic, diagnostics, release state, and migration requirements live in the repository
source and release documentation.

---

## Support, Diagnostics, and Issue Triage

When reporting a bug or asking for configuration help, attach the native Home Assistant diagnostics file where possible.

Download it from:

```text
Settings -> Devices & services -> Humidity Intelligence -> Download diagnostics
```

Then drag the downloaded file into the GitHub issue.

Diagnostics help maintainers see:

- Humidity Intelligence and Home Assistant versions
- sanitized config entry/options summaries
- configuration counts and selected-entity category/status summaries
- enabled feature areas
- current runtime lane/mode, gate state, output state, and reason availability/truncation
- active alert resolution
- house humidity drift dependency status
- frontend dependency status when Home Assistant exposes Lovelace resources
- generated UI/card summary
- unavailable/unknown configured entities and support warnings

Sensitive keys and values such as tokens, passwords, API keys, webhook URLs,
credential-bearing URLs, location fields, usernames, host/IP/MAC/SSID values,
device IDs, unique IDs, and private entity IDs are redacted. Selected
entity/mapping/room/Area/Label evidence is generally reduced to counts and status
categories, but user-configured display and level labels may remain. Review the
complete file before uploading it to a public issue.

The public [HI Support Bundle Inspector](https://senyo888.github.io/humidity-intelligence/inspector/)
is an optional browser-local preflight for a supported diagnostics file. It can
produce a short, unsigned advisory handoff for the bug-report and configuration-help
forms. Native Home Assistant diagnostics remain the preferred attachment and
repository/Wiki guidance remains support truth. Live runtime evidence, source
correctness and anonymity remain separate assessments. Copying occurs only when the
user activates Copy, and pasting the handoff into GitHub creates normal GitHub issue
retention. Full `dump_diagnostics` exports remain local unless a maintainer explicitly
requests one.

Issue triage works best with diagnostics-first reports. For wider ideas, dashboard suggestions, compatibility requests, documentation improvements, or automation/control suggestions, use the Community Ideas & Proposals issue form. Community comments and reactions are useful interest signals; maintainer review and the proposal/release process carry approval and scheduling authority.

More detail:

- [Getting Help](https://github.com/senyo888/humidity-intelligence/wiki/Getting-Help)
- [Diagnostics and Support Bundle](https://github.com/senyo888/humidity-intelligence/wiki/Diagnostics-and-Support-Bundle)
- [Support and diagnostics](docs/support.md)
- [Issue triage workflow](docs/issue-triage.md)

---

## Runtime Simulation Validation

Maintainer runtime validation includes a backend-consumed fake telemetry harness
for `HI Air Control Mode` and `HI Air Control Reason` truth. It is test-only:
no Home Assistant helpers, services, dashboards, automations, or fake fan output
writes are created by default.

Run it from the repository root:

```bash
python3 "tests 2/test_air_control_mode_simulation.py"
```

The harness covers normal, telemetry unavailable, zone pressure, AQ pressure,
disabled/manual/global gates, baseline-clear CO telemetry, and explicit opt-in
CO emergency pressure. Details are in
[Runtime Simulation Validation](docs/runtime-simulation-validation.md).

---

## Release Notes

### v2.0.9-beta.1

- moved working-branch integration metadata to `2.0.9-beta.1`; v2.0.8 remains the
  latest published stable release
- restricted `dump_diagnostics` and `v205_release_check` custom filenames to the
  exact lowercase `humidity_intelligence_*.json` namespace, preserving both defaults
- moved caller-selectable diagnostics and release-check reports from the config root
  into `<config>/humidity_intelligence/exports/`, without automatically migrating or
  deleting legacy root reports
- moved the fixed `humidity_intelligence_self_check.json` report into the same secure
  exports directory and all generated card YAML into
  `<config>/humidity_intelligence/ui/`; registered dashboards remain under
  `<config>/dashboards/<url_path>.yaml`
- added no-follow, descriptor-relative, same-directory atomic YAML writes, exact
  purge ownership, and entry-qualified filenames for multi-entry installations
- required an authenticated admin user context for every external `dump_diagnostics`,
  `self_check`, `v205_release_check`, `dump_cards`, and `view_cards` call; contextless
  background callers and non-admin users are rejected before work begins, while
  trusted HI setup/options/release-test generation uses the internal exporter and
  startup refresh remains cache-only
- extended the backward-compatible `v205_release_check` manifest contract through
  the v2.0.9 beta/rc/stable line
- privacy-filtered local issue-triage body summaries before report escaping, removing
  private HA endpoints, credentials, device IDs, local paths, and entity IDs
- admin-gated targeted and all-entry `pause_control` / `resume_control` calls plus
  explicit dashboard creation and generated-file/dashboard purge
- made purge target truth blocking and exact before deletion, with unsafe filesystem
  candidates rejected and partial file/dashboard failures reported
- escaped dynamic HTML in the retained V1 Mobile source/gallery templates and
  deprecated that layout for new dashboards while preserving it through v2.0.9;
  planned removal remains a separate v2.1 proposal
- migration impact: no stored-data migration. Report consumers must move from
  `<config>/<filename>` to `<config>/humidity_intelligence/exports/<filename>`;
  card consumers must move to `<config>/humidity_intelligence/ui/<filename>`. Legacy
  root JSON/YAML remains untouched with no dual-write, copy, symlink, move, or
  automatic deletion. Verify fresh owned-directory output before switching consumers.
  Callers using another custom report filename must rename it. Contextless background
  automations/scripts can no longer invoke the external writer services; use an
  authenticated admin UI or API call. Any future automated trusted route requires
  separate design approval
- runtime/UI impact: entity semantics, deterministic lane ordering, and output
  selection are unchanged. Generated-card logic and rendered backend-truth semantics
  are unchanged, while export paths and multi-entry filename qualification change.
  V1 users must re-export and re-copy their card to receive the escaped template
- restart impact: fully restart Home Assistant after installing updated package code;
  a config-entry reload alone is insufficient
- recorded advisory HA Lab evidence for package commit `c54e9e1`: full-package backup
  and source/remote hash verification passed, the maintainer completed the restart,
  post-restart diagnostics/service/runtime checks passed, and approved single-entry
  admin write smoke produced valid owned-directory JSON/YAML with expected
  permissions and post-write continuity
- HA Lab did not live-test non-admin rejection, multi-entry naming, purge removal,
  concurrent/fault-injected writes, legacy-root retention, or rendered Lovelace UI;
  those boundaries remain covered by local tests or require separate live evidence

### v2.0.8

- set integration metadata to stable `2.0.8`; GitHub Releases and HACS remain the
  user-facing publication record
- added first-run welcome/setup guidance before Frontend Dependencies, keeping setup
  staged and making it safer to save a small initial telemetry set before later
  Options tuning
- fixed Temperature Slope setup/options fallback when collapsed Advanced source lists
  submit empty values
- made default generated V2 dashboards status-safe where appropriate: default card
  surfaces focus on inspection, while pause/resume and standalone View Cards workflows
  live in explicit service/admin paths
- replaced the generated V2 Pause LIVE tile with a passive Stability preview badge
  that reads future diagnostics when present and stays display-only
- kept missing/null future Stability scores in the future/default badge state instead
  of rendering them as score `0`, and aligned tablet/gallery System and Manual card
  glow with the mobile layout
- paced current/complete Stability shimmer at 10 BPM with a 6-second animation cycle
- made Home Assistant setup-assist suggestions reachable through an explicit
  telemetry preview action before saving advisory Area/Label-derived defaults
- admin-gated global all-entry `pause_control` / `resume_control`; scoped `entry_id`
  calls remain available
- tightened diagnostics/support export sanitization and confined issue-triage private
  report writing; `self_check` and release-validation reports remain local/private
  validation exports until reviewed or sanitized because they may include entity IDs
  needed for mapping diagnostics
- bucketed mapped diagnostics entity state into privacy-safe availability categories
  and expanded issue-triage local-path rejection across macOS, Linux, and Windows
- hardened the tracked secret scan so an empty tracked-file selection fails closed
- extended `v205_release_check` to accept the v2.0.8 beta/rc/stable line while
  preserving the backward-compatible service name
- runtime impact: deterministic lane ordering, output-writer boundaries, entity
  semantics, migration shape, and generated UI truth remain anchored to the existing
  backend contract
- restart/dashboard impact: restart Home Assistant after updating package code; refresh
  or re-export generated cards and update pasted Manual-card YAML for the new default
  V2 card surfaces

<details>
<summary>Previous Releases</summary>

### v2.0.7

- promoted integration metadata to stable `2.0.7`
- added a GitHub Pages SEO landing site for search discovery, with public copy, logo/hero artwork, crawl helpers, structured metadata, pinned Pages workflow actions, README routing, and explicit repository source-of-truth boundaries
- documented HA Lab as advisory Operational Beta Validation Infrastructure for sanitized beta deploy, runtime-readiness, diagnostics, and generated-card/entity-map evidence without making HA Lab release authority
- hardened visual-alert service validation, diagnostics credential-key redaction, generated V2 card HTML rendering, and local issue-triage report escaping without changing deterministic lane ordering, entity semantics, or migration behavior
- fixed PM2.5 aggregate runtime truth so configured PM2.5 telemetry exposes canonical backend-owned PM25 aggregate entities instead of relying on Home Assistant's dotted `pm2_5` name slug
- hardened generated-card AQ output details so unresolved optional AQ aggregate rows are pruned instead of rendering stale `Entity not found` rows, with generated-card entity reference checks in `self_check` and `v205_release_check`
- expanded generated-card entity reference checks so stale IDs embedded inside generated-card JavaScript/string expressions are reported, and PM2.5 aggregate entity-ID normalization conflicts are surfaced through diagnostics, `self_check`, and `v205_release_check`
- filtered generated-card release-validation extraction so JavaScript service names, predicate prefixes, object properties, and entity-prefix strings no longer fail generated-card entity availability checks
- recorded HA Lab advisory validation for commit `55dc2b9`: lab identity, HI presence/diagnostics, scenario-matrix read-only baseline, and Stage 3 six-sensor runtime-readiness checks passed after lab-only deploy and manual restart; no stable-instance access, HA service calls, helper mutation, dashboard mutation, restart, reload, or output writes were performed by Codex
- changed generated V2 Current Air Control cards so red control-row styling follows selected alert/CO runtime truth, while degraded or unmapped alert candidates remain in reason text instead of primary chip-row space
- fixed generated V2 Current Air Control cards so missing or unavailable Air Control Mode telemetry no longer renders as normal/ready, and backend `telemetry_unavailable` is shown as degraded UI truth ahead of stale helper-derived alert or AQ state
- moved optional Level 1 / Level 2 display-label editing into setup Zones and post-configuration Zone Options before Zone 1 / Zone 2 editing, with diagnostics and generated cards using the same sanitized fallback-aware label source
- sanitized generated V2 card templates, gallery exports, and test fixtures so public artifacts use canonical HI placeholders instead of maintainer-local presence, alarm, tracker, or room-sensor entity IDs
- kept startup UI refresh deterministic: startup follows `auto_refresh_ui_on_startup`, while explicit UI install, option-visibility changes, and manual `dump_cards` still write card files
- added Configuration Walkthrough links to setup Frontend Dependencies, post-configuration Frontend Dependencies, and final UI export guidance
- added GitHub Wiki support-manual routing from the README, including configuration, services, diagnostics, generated dashboard, HACS/update, AQ/CO safety, troubleshooting, and release-validation guidance
- added release/PR checklist support for recording Wiki update status as `updated`, `no-op`, or `blocked` when public manual guidance is affected
- added a Wiki Services Reference, footer navigation across public Wiki content pages, and a Wiki banner asset for a clearer support-manual experience
- migration impact: existing PM2.5 aggregate entity IDs using `pm2_5` are normalized to `pm25` during HI setup; restart Home Assistant after updating so the new package and registry normalization run, then regenerate/re-copy generated cards if your dashboard uses PM2.5 aggregate surfaces or the Current Air Control UI change

### v2.0.6

- promoted integration metadata to stable `2.0.6`
- added degraded `telemetry_unavailable` runtime mode when required humidity or configured temperature telemetry is unavailable, so HI stands down safely instead of reporting normal/all-clear
- fixed global gate preemption so a running humidity-danger alert lane clears its alert context and Current Air Control refreshes away from stale alert-running state after the gate takes over
- migration impact: standard restart/refresh only for the global gate preemption fix. After updating HI through HACS or file replacement, restart Home Assistant. Use config-entry reload after option changes once the updated code is already loaded. Then run `humidity_intelligence.dump_cards` or re-copy any pasted dashboard YAML and refresh dashboard/browser cache to see the Current Air Control card update
- fixed CO emergency clear timing so the engine schedules a recheck at the two-minute clear deadline instead of waiting for the next periodic control interval
- added direct backend simulation validation for `HI Air Control Mode` and `HI Air Control Reason`, including normal, telemetry unavailable, zone, AQ, gate, and opt-in CO pressure scenarios
- fixed setup/options telemetry add and edit Cancel handling so users can return to the previous telemetry page without losing already-saved flow data
- added explicit close-without-saving confirmation for HI-controlled setup/options Cancel actions
- fixed Zone 2 setup/options defaults and trigger labels so Zone 2 trigger ownership is shown and stored as Zone 2 / Level 2 unless explicitly changed
- added explicit local HI-only snapshot services for advanced maintenance: `create_local_backup` and `list_saved_versions`
- exposed compact local snapshot status through diagnostics, `self_check`, and optional `v205_release_check` freshness inputs
- kept local snapshot support manual and package-local only; no restore flow, automatic rollback, HACS interception, startup snapshotting, or whole-instance backup behavior is included
- added a Community Ideas & Proposals issue form for ideas, dashboard suggestions, compatibility requests, documentation improvements, diagnostics/support-flow ideas, and automation/control suggestions
- updated contributor, support, and report-only triage wording so community ideas remain manual intake signals, not implementation authority
- added clean-install setup/repair guidance for the `HI House Humidity Drift 7d` Statistics helper dependency
- added a non-blocking Home Assistant Repairs issue only when `sensor.house_humidity_mean_7d` is missing
- differentiated missing helper, not ready or unavailable helper, non-numeric helper, low history coverage, and invalid source states without fabricating drift values
- refined optional Current Air Control temperature chip colours to use backend-owned seasonal cold, comfort, warm, and hot boundaries
- retuned Spring and Summer temperature chip comfort/warm bands while keeping the backend-owned seasonal boundary model unchanged
- exposed the resolved temperature warm boundary through comfort sensor attributes and diagnostics so generated cards do not hard-code seasonal thresholds
- kept the setup/options Frontend Dependencies pages frontend-only; drift dependency truth remains on the drift sensor, diagnostics, `self_check`, `v205_release_check`, and Repairs
- preserved the existing drift calculation and legacy `sensor.house_humidity_mean_7d` compatibility
- kept lane ordering, AQ, humidifier, alert, output, migration, restore, HACS update, and runtime-control behavior unchanged except for the explicit `telemetry_unavailable` mode/entity truth correction

### v2.0.5

- reorganised setup and options around essentials first, with tuning controls behind Advanced sections that open/retract immediately without an extra Submit cycle
- added recommended-default guidance to setup and post-configuration pages
- added native Home Assistant diagnostics for redacted GitHub issue attachments and updated issue templates to prefer the downloaded diagnostics file
- surfaced missing/unavailable/non-numeric house humidity 7-day drift dependency status in the drift sensor, `self_check`, `v205_release_check`, and diagnostics
- fixed calculated room temperature slope sensors so they publish a seeded startup state instead of staying restored-but-unavailable until the next source update
- fixed calculated temperature slope diagnostics mapping so registered Home Assistant entity IDs are preferred over predicted fallback IDs
- kept control loop interval, startup UI mapping refresh, custom humidity targets, slope source selection, temperature chips, fan levels, thresholds, lane removal, and alert visual tuning available as advanced controls
- made `Thresholds & Comfort` easier to scan by keeping temperature comfort mode visible and moving custom comfort values plus zone thresholds into Advanced
- added `show_output_entity_details` / `Show output entity details` as a UI-only option for generated V2 cards
- defaulted new generated V2 cards to hide the expandable output details panel unless the option is enabled
- changed first-install UI export default to `v2_tablet`
- kept deterministic runtime behavior, lane ordering, alert hierarchy, CO emergency handling, humidifier independence, public entity semantics, and `dump_cards` unchanged
- promoted integration metadata to stable `2.0.5`; branch/version governance now allows beta, rc, or stable labels on `senyo888-patch-1`, rc or stable labels on `develop`, and stable releases on `main`

### v2.0.4

- added alert-to-zone binding for humidity, mould, and condensation alerts so the originating room resolves to its configured zone boost level
- added mould risk and condensation risk alert trigger types alongside existing danger triggers
- enforced alert hierarchy: CO emergency, humidity danger, mould danger, mould risk, condensation danger, condensation risk, zones, AQ, normal
- added deterministic multi-alert conflict reporting in the reason panel and debug logs
- changed humidity danger alert evaluation to use the active profile high-risk threshold instead of any legacy saved static threshold
- removed custom trigger entities and custom binary sensors from alert configuration; alerts are internally calculated from HI telemetry and risk logic
- removed CO output-device selection from the main alert flow; CO emergency uses configured CO telemetry and existing ventilation outputs
- clarified zone boost guidance so boost levels are presented as danger/alert escalation and should normally exceed normal zone fan levels
- fixed alert boost hold behavior so selected zone outputs are not returned to auto while the alert lane remains active
- fixed alert helper switch churn so active alerts no longer flip their UI helper switches off/on during every evaluation cycle
- added single-flight automation evaluation and stopped internal status helper switches from retriggering evaluation when alert state changes
- clarified global gate target-profile labels and added explicit alert visual rule removal in setup/options
- added upgrade guidance that users must run `humidity_intelligence.dump_cards` and paste the updated YAML into existing Manual dashboard cards to see v2.0.4 UI changes
- added user-friendly headers to V2 card YAML exports with Manual-card paste instructions and frontend dependency reminders
- changed unmapped/degraded alert candidates to report in reason text and continue to the next eligible priority instead of blocking automation
- fixed built-in humidity, mould, and condensation alert candidates so they enter the alert lane, resolve zone boost, and populate the companion alert chip without requiring a duplicate explicit alert row
- fixed V2 alert chip detection for generated alert switch entity IDs and active alert context fallback
- added `HI Active Alert Context` telemetry for UI chips and diagnostics
- added degraded-mode handling when alert sensor, room, zone, or output mapping is incomplete
- added `auto_refresh_ui_on_startup` option, enabled by default, to refresh HI UI mapping shortly after Home Assistant startup without blocking startup
- fixed startup UI refresh scheduling/cleanup to use Home Assistant's thread-safe task creator without assuming a task handle is returned
- removed the HACS URL from frontend dependency flow output while keeping HACS detection
- added seasonal/custom temperature comfort configuration and runtime comfort sensors for truth-based temperature chip colouring
- added post-configuration editing for all zone thresholds: humidity high, air quality, condensation risk, and mould risk
- fixed temperature slope chip mapping fallback so calculated slope chips use Home Assistant slug-compatible entity IDs and configured slope sources
- renamed Global Gates labels to `Humidity Intelligence target profile mode` and `Humidity custom target`
- changed alert chipsets to show only lane/status plus the resolved alert source context, with redundant helper-switch chips removed
- visual humidity/mould/condensation alerts now flash 10 times, restore prior light state, wait 30 minutes, and repeat only while the same alert remains active
- diagnostics now include a support-focused summary for target profile mode, active profile/season/custom target, zone mappings, alert mappings, visual alert configuration, active alert resolution, unavailable entities, and configuration warnings
- bumped integration version to `2.0.4`

### v2.0.3

- bumped integration version to `2.0.3`
- documented minimum Home Assistant version as `2026.4.3`
- frontend dependency status output now includes direct repository links (`card-mod`, `button-card`, `mod-card`, `apexcharts-card`)
- added post-configuration Frontend Dependencies options step so frontend dependency checks are accessible after initial setup
- reordered options menu for setup flow clarity (`Frontend Dependencies`, then `Sensors`, then `Global Gates`)
- refreshed README frontend dependency section with clearer HACS-first install guidance and acknowledgements
- updated top badges: HACS badge wording now `Custom Integration`, and Home Assistant compatibility is shown directly

### v2.0.2

- humidity badge semantics corrected to target-relative states (`below_target`, `in_target`, `above_target`, `high_risk`)
- active target season/profile surfaced in UI target display
- condensation and mould risk evaluation updated to season-aware deterministic thresholds
- humidifier telemetry reason expanded with lane scope, trigger condition, measured values vs thresholds, and recovery logic
- runtime debug logs added for active target profile, seasonal adjustments, humidity badge classification, and humidifier trigger/stop events

### v2.0.1 fixes

- fixed Fahrenheit telemetry normalization by converting all internal temperature math to Celsius before averages, spreads, deltas, and thresholds
- fixed aggregate behavior so IAQ/AQ averages ignore `unknown`, `unavailable`, and non-numeric states and only return unknown when no valid values exist
- added aggregate exclusion debug logging with explicit reasons (`unknown`, `unavailable`, `non_numeric`, `unit_mismatch`)
- added zone mapping duplicate warnings in setup/options and new duplicate diagnostics sensor state
- added `alert_only_mode` (monitor + alerts only) to suppress automation control lanes for users without output hardware
- improved UI placeholder pruning so optional outputs/controls are hidden when not configured, including alert-only control suppression
- fixed alert-only card rendering edge case by pruning invalid leftover `conditional` blocks after entity pruning
- updated Current Air Control reason field behavior for alert-only mode so it reports monitoring/alerts context while keeping output-control wording separate
- options changes that flip `alert_only_mode` now trigger UI card refresh/export regeneration and a notification
- expanded options flow editing so users can revisit skipped lanes and add/edit alerts later
- expanded post-configuration lane management so humidifier and AQ lanes can be re-added after removal, and telemetry changes log explicit add/update/remove actions
- alert target lights are now fully optional end-to-end (config/options/service/runtime); alerts still trigger without flash entities
- hardened service input validation (safe filename/url path/layout checks), bounded flash parameters, and diagnostics attribute redaction for sensitive keys

### Migration notes

- `alert_only_mode` is now available in Global Gates (setup and options). Disable it later to restore normal control entities/lane behavior.
- new computed sensor: `HI Zone Mapping Duplicates` (`hi_<entry_id>_zone_mapping_duplicates`) exposes duplicate zone mapping status and details.
- new computed sensors:
  - `HI Active Target Season` (`hi_<entry_id>_target_season`)
  - `HI House Humidity State` (`hi_<entry_id>_house_humidity_state`)
- generated V2 cards now prune unresolved optional control/output entities instead of leaving stale references.
- if your dashboard uses Manual cards, re-copy/paste the latest exported YAML after changing `alert_only_mode` so the UI and reason panel match the selected mode.

</details>
