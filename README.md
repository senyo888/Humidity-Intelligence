<!-- Logo and Banner -->

![Humidity Intelligence banner](assets/header.png)

# Humidity Intelligence

## Domestic Environmental Stabilisation Engine for Home Assistant

[![Latest Release](https://img.shields.io/github/v/release/senyo888/Humidity-Intelligence?display_name=tag&sort=semver)](https://github.com/senyo888/Humidity-Intelligence/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom%20Integration-orange)](https://hacs.xyz)
[![Manifest Version](https://img.shields.io/badge/dynamic/json?label=Manifest%20Version&query=%24.version&url=https%3A%2F%2Fraw.githubusercontent.com%2Fsenyo888%2FHumidity-Intelligence%2Fsenyo888-patch-1%2Fmanifest.json&color=blue)](manifest.json)
[![License](https://img.shields.io/github/license/senyo888/Humidity-Intelligence)](LICENSE)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-ea4aaa?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/senyo888)

## Contents

- [TL;DR](#tldr)
- [What Is Humidity Intelligence](#what-is-humidity-intelligence)
- [V2 UI Example](#v2-ui-example)
- [Support Humidity Intelligence](#support-humidity-intelligence)
- [Why Environmental Stability Matters](#why-environmental-stability-matters)
- [Air Quality and Environmental Stability](#air-quality-and-environmental-stability)
- [Season-Aware Environmental Control](#season-aware-environmental-control)
- [Design Philosophy](#design-philosophy)
- [Architecture Overview](#architecture-overview)
- [Current Release Highlights](#current-release-highlights)
- [Installation](#installation)
- [Frontend Dependencies](#frontend-dependencies)
- [Migration Guide - v1 to v2](#migration-guide---v1-to-v2)
- [Full Configuration Flow](#full-configuration-flow)
- [Configuration Screenshots (Visual Guide)](#configuration-screenshots-visual-guide)
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

Current release: **v2.0.6**.

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

Humidity Intelligence is intentionally deterministic. Every decision is based on visible telemetry, defined environmental rules, and priority logic rather than opaque AI behaviour or unpredictable automation chains. The goal is not automation for its own sake; it is long-term environmental stability, comfort, and property protection.

The project also places strong emphasis on transparency. Users can see why actions are happening, what environmental conditions triggered them, which zone is active, and what the system is trying to achieve at any given moment. Seasonal context, comfort targets, active alerts, and runtime reasoning are surfaced directly into the UI so the system feels understandable rather than mysterious.

At its core, Humidity Intelligence is about creating a calmer, more stable living environment through continuous environmental awareness and accountable smart-home control.

<details>
<summary><strong>Quick Demo</strong></summary>


![Humidity Intelligence quick demo](assets/readme/hi_quick_demo.gif)

</details>

---

## V2 UI Example

<p>
  <img src="assets/v2_ui_gallery/v204_presence_gate_reason.png" width="320" alt="V2 mobile Current Air Control presence gate active state">
</p>

<details>
<summary><strong>More UI Examples</strong></summary>

Additional screenshots are kept collapsed so the front page stays focused.

- [Open the full V2 UI image folder](assets/v2_ui_gallery/)
- [Open the reusable UI Gallery](ui-gallery/README.md)

Additional image files:

- [Current Air Control ready state](assets/v2_ui_gallery/v204_current_air_control_ready.png)
- [Zone-bound alert boost state](assets/v2_ui_gallery/v204_zone_alert_boost.png)
- [V2 mobile air quality lane state](assets/v2_ui_gallery/ui_v2_mobile_aq.png)
- [V2 mobile Zone 2 moisture stabilisation state](assets/v2_ui_gallery/IMG_0323.png)
- [Expanded output details example](assets/v2_ui_gallery/IMG_0324.png)
- [Unmapped alert degraded context](assets/v2_ui_gallery/v204_unmapped_alert_context.png)
- [Zone 2 temperature chip state](assets/v2_ui_gallery/v204_zone2_temperature_chips.png)
- [V2 gallery image 5665](assets/v2_ui_gallery/IMG_5665.png)
- [V2 gallery image 5672](assets/v2_ui_gallery/IMG_5672.png)
- [V2 gallery image 5673](assets/v2_ui_gallery/IMG_5673.png)
- [V2 gallery image 5674](assets/v2_ui_gallery/IMG_5674.png)
- [V2 gallery image 5675](assets/v2_ui_gallery/IMG_5675.png)
- [Legacy-compatible V1 mobile skin](assets/v2_ui_gallery/ui_v1_mobile.png)
- [V2 tablet Zone 2 compact example](assets/v2_ui_gallery/ui_v2_tablet_zone_2.png)

</details>

---

## Support Humidity Intelligence

### Enjoying Humidity Intelligence?

If you're finding Humidity Intelligence useful, insightful, or just interesting to explore, consider giving the repository a star.

It helps others discover the project, supports ongoing development, and shows that this kind of deterministic, explainable approach to Home Assistant has community value.

[Star Humidity Intelligence on GitHub](https://github.com/senyo888/Humidity-Intelligence)

Optional sponsorship is also available through GitHub Sponsors:

[Support the project on GitHub Sponsors](https://github.com/sponsors/senyo888)

Sponsorship is optional. It does not create a support SLA, private support obligation, feature guarantee, release commitment, or change to Home Assistant / HACS behaviour.

---

## Why Environmental Stability Matters

Homes rarely become damp, dry, stale, or uncomfortable because of one isolated reading. Problems usually build as patterns: a bathroom that stays wet too long, a room that drifts away from the rest of the house, a winter profile that needs a lower humidity target, or an air-quality spike that lingers after cooking.

Humidity Intelligence is built for those patterns. It treats environmental stability as the goal, not a single perfect number.

Instability can appear as:

- drift
- imbalance
- duration
- recurring spread patterns

### High Humidity Related Issues

- condensation formation
- mould growth risk
- dust mite proliferation
- sleep disruption
- structural degradation over time

### Low Humidity Related Issues

- irritated airways
- dry throat and coughing
- worsened asthma symptoms
- dry skin and eye irritation
- reduced respiratory resilience

### Indoor Plant Health Problems

- low humidity: leaf browning, stress, slowed growth
- excess humidity: fungal growth and pest vulnerability

Most homes oscillate between both extremes seasonally.

V2 models that instability directly, then explains what it is seeing instead of hiding the reasoning in disconnected automations.

---

## Air Quality and Environmental Stability

Humidity Intelligence is not only humidity-focused. It contributes to environmental stability by surfacing indoor air-quality signals from configured Home Assistant entities and, where users have configured suitable outputs, using available devices such as air purifiers or ventilation fans to respond to poor air-quality conditions.

Air-quality support is telemetry-driven. Humidity Intelligence only reflects the sensors, entities, thresholds, and output devices configured in Home Assistant. The UI and reason panel must mirror backend/entity truth only; they must not invent thresholds, health categories, alert levels, or control logic.

The wider air-quality (AQ) telemetry family in the current configuration flow includes indoor air quality (IAQ), fine particulate matter (PM2.5), volatile organic compounds (VOCs), carbon dioxide (CO2), and carbon monoxide (CO), depending on what the user configures.

Where an AQ lane is configured, it remains below safety and moisture-risk alert lanes in the deterministic priority order. Carbon monoxide emergency handling remains the highest-priority runtime lane, while normal AQ responses are deferred when higher-priority alert or zone lanes are active.

### Carbon monoxide (CO)

Carbon monoxide is a dangerous combustion-related gas. In homes it can be produced by faulty, damaged, or poorly ventilated fuel-burning appliances, blocked flues or chimneys, attached garages, fireplaces, boilers, stoves, unvented heaters, generators, charcoal grills, vehicle exhaust, or similar combustion sources.

Humidity Intelligence can surface configured carbon monoxide readings and can use configured carbon monoxide telemetry in its emergency lane and reason output. It reflects existing Home Assistant entities; it does not create certified detection hardware.

> **Carbon monoxide safety warning:** Humidity Intelligence must not be relied on as the only carbon monoxide detection or alerting system. It only reflects existing Home Assistant entities and is not a certified carbon monoxide alarm, life-safety device, or compliance system. Users must install and maintain certified carbon monoxide alarms according to local regulations, manufacturer guidance, and applicable building/fire safety requirements. If a carbon monoxide alarm sounds or CO exposure is suspected, users must follow local emergency guidance.

### Volatile organic compounds (VOCs)

Volatile organic compounds are airborne chemicals released by many household materials and products. Practical sources include cleaning products, aerosols and sprays, paints, varnishes, adhesives, solvents, new furniture, carpets, building materials, scented products, hobby supplies, stored fuels, and dry-cleaned items.

In everyday household terms, elevated VOC readings can correspond with odours, stale or chemically loaded air, irritation for sensitive occupants, and general indoor-air-quality degradation.

Humidity Intelligence can display VOC-related readings when suitable sensors are configured. It can help correlate VOC changes with room conditions and reason-panel output, and it may trigger configured purification or ventilation responses where supported. It does not promise full removal of VOCs; the practical goal is to surface, reduce, mitigate, respond to, or help clear poor-air-quality conditions using the configured sensors and devices available to Home Assistant.

### Fine particulate matter (PM2.5)

Fine particulate matter (PM2.5) refers to very small airborne particles. Indoor examples include cooking, frying, candles, fireplaces, smoke, wildfire or smog ingress, dust disturbance, vacuuming, combustion sources, and outdoor pollution entering the home.

Fine particles can linger in indoor air, affect perceived air quality, aggravate respiratory sensitivity, and make a room feel polluted even when humidity is stable.

Humidity Intelligence can surface PM2.5 readings from configured sensors and use those readings as part of air-quality awareness. Where a compatible air purifier or fan output is configured, Humidity Intelligence can drive a response that supports particle reduction. It does not promise medical outcomes, certified purification, or guaranteed removal.

### Indoor air quality (IAQ)

In Humidity Intelligence, indoor air quality (IAQ) is a configured telemetry type (`iaq`) supplied by the user's Home Assistant sensor entities. The integration can expose house and level IAQ average sensors from configured numeric IAQ inputs, excluding `unknown`, `unavailable`, and non-numeric readings from aggregates. If no numeric IAQ readings remain, the aggregate reports unknown rather than inventing a value.

IAQ is intended to provide a readable air-quality summary when the user's sensor already provides that kind of signal. It can help the UI and reason panel communicate air-quality state, including configured AQ trigger details, but it does not replace the underlying sensor entities or certify the meaning of a vendor-specific IAQ scale.

IAQ wording in generated dashboards and documentation must reflect backend truth only: configured entities, aggregate values, deterministic AQ trigger state, and reason-panel output. It must not diagnose health risk or add frontend-only categories that the backend does not produce.

---

## Season-Aware Environmental Control

`56%` is not always "high."

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

Humidity Intelligence is built around a simple premise: a home should not be regulated by a loose pile of automations competing for control. It should have one visible environmental controller that reads configured telemetry, applies a stable priority hierarchy, and resolves one explainable outcome per evaluation cycle.

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

This layer models risk and does not control hardware.

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

If an alert candidate cannot be mapped to a safe zone output, HI does not boost blindly. The reason panel reports the unmapped/degraded alert and automation continues to the next eligible priority.

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

The UI does not compute logic. The engine decides; the UI renders.

---

## Current Release Highlights

- required humidity telemetry, or configured temperature telemetry, now degrades explicitly to `telemetry_unavailable` instead of falling through to lower lanes or all-clear wording
- CO emergency clearing now schedules a recheck at the two-minute clear deadline instead of waiting for the next normal control interval
- global gates now clear lower-priority active alert switch/context/telemetry state so Current Air Control cannot keep showing stale humidity-danger activity after a gate takes authority
- setup/options telemetry Cancel actions now return through an explicit confirmation path without losing already-saved flow data
- Zone 2 setup/options defaults and trigger labels now preserve Zone 2 / Level 2 ownership unless explicitly changed
- advanced local HI-only snapshot services, `create_local_backup` and `list_saved_versions`, support maintainer validation without adding restore, rollback, HACS interception, or runtime-control behavior
- house humidity drift helper readiness is clearer across sensor attributes, diagnostics, `self_check`, `v205_release_check`, and Repairs
- optional temperature chip colours now use backend-owned seasonal cold, comfort, warm, and hot boundaries
- deterministic lane ordering, alert hierarchy, CO emergency priority, humidifier independence, output writes, migration behavior, and `dump_cards` remain unchanged

Upgrade note: **v2.0.6 concentrates on runtime truth, missing-telemetry fail-safe behavior, release validation support, and configuration/support polish.** After updating HI through HACS or file replacement, restart Home Assistant. Use config-entry reload only after option changes once the updated code is already loaded. Run `humidity_intelligence.dump_cards` and paste the updated YAML into existing Manual cards if you use generated Current Air Control cards.

---

## Installation

### Option A - HACS (Recommended)

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

In v2.0.6, HI reports missing-helper guidance through the drift sensor attributes, diagnostics, `self_check`, `v205_release_check`, and Home Assistant Repairs. The setup/options Frontend Dependencies pages remain frontend-only; drift helper truth belongs on diagnostics and repair surfaces.

If the helper exists but reports `unknown`, `unavailable`, a non-numeric state, low `age_coverage_ratio`, or `source_value_valid: false`, HI reports it as not ready or unavailable instead of telling you to recreate the helper.

Do not fabricate history. Drift remains unavailable until Home Assistant reports enough recorder/statistics samples for a numeric 7-day mean. Once the helper is numeric and ready, `HI House Humidity Drift 7d` becomes numeric automatically.

### Step 2 - Remove v1 UI YAML

Delete:

```text
/config/www/.../v1_mobile.yaml
/config/lovelace/v1_mobile.yaml
```

Restart if using YAML dashboards.

### v1 UI Compatibility

The classic four-badge + Comfort Band layout remains compatible on the V2 engine.

- V1 UI = presentation skin
- V2 = runtime engine

No forced visual migration.

### Post-Migration Check

After install, verify:

- Integration loads in **Settings -> Devices & Services**
- no references remain to `/custom_templates/`
- UI renders correctly

If needed, refresh UI:

```yaml
service: humidity_intelligence.refresh_ui
```

### Summary

- V1 = Template system (`custom_templates`)
- V2 = Integration (`custom_components`)
- HACS must be reconfigured to recognise the new structure

Skipping this step will result in:

- failed updates
- incorrect install location
- integration not loading


---

## Full Configuration Flow

Follow this sequence on first install. Essentials stay visible; expert controls sit inside live collapsible **Show advanced tuning** sections. Opening or closing an Advanced section does not wipe saved values.

Advanced placement summary:

| Area | Visible by default | Inside Advanced |
| --- | --- | --- |
| Global Gates | time gate, outside action, alert-only mode, target profile, presence entities | control loop interval, startup UI mapping refresh, generated-card output details, custom humidity target, custom temperature comfort bounds |
| Temperature Slope | slope mode | slope source overrides, provided slope sensors, optional temperature chip row |
| Zones | enablement, level, rooms, triggers, outputs | normal fan level, boost fan level, Current Air Control label |
| Zone Thresholds | selected trigger context | humidity delta, AQ, condensation risk, and mould risk thresholds |
| Humidifiers | enablement and outputs | band adjustment, lane removal in options |
| Air Quality | enablement, triggers, outputs | lane removal, run duration, fan level, trigger thresholds |
| Alerts | alert handling, source, room scope, target lights | CO threshold, power entity, flash mode, flash duration |

The default first UI export is `v2_tablet`. `show_output_entity_details` is display-only and only changes whether generated cards include the expandable output details panel.

### 1) Frontend Dependencies

What to do:
- open the Frontend Dependencies step in config flow
- review installed/not detected/not inspectable status and repository links
- continue even if some are not installed

Reference:
- see [Frontend Dependencies](#frontend-dependencies) for install guidance and acknowledgements


### 2) Global Gates

What to do:
- set time gate window (optional)
- select presence/alarm entities (optional)
- define explicit present and away state values
- set Humidity Intelligence target profile mode
- leave recommended defaults in place unless you have a clear reason to customise
- open Advanced in-place only for control loop interval, startup UI mapping refresh, custom humidity targets, custom temperature comfort limits, or generated-card output details visibility

Example baseline:
- time gate enabled: `06:00` to `23:30`
- outside action: `safe_state`
- presence entities: `person.adam`, `person.eve`, or alarm panel
- present states: `home`, `on`, `disarmed`
- away states: `not_home`, `off`, `armed_away`, `away`
- target profile mode: `auto`
- generated-card output details: off for a cleaner dashboard unless you want the expandable output panel

Example:
- if everyone is away, HI enters gate hold
- Current Air Control shows gate-active mode/chips
- outputs are held or reset based on selected outside action

### 3) Telemetry Inputs

What to do:
- add source entities for humidity and temperature
- add optional AQ telemetry (`iaq`, `pm25`, `voc`, `co2`, `co`)
- added sensors will appear in the UI Chip
- assign EVERY sensor to level and room regardless of intended use

Rules:
- minimum one humidity + one temperature sensor per active level
- use `level1` and `level2` consistently
- keep room labels stable and human-readable
- in v2.0.6, Cancel on setup/options telemetry add and edit pages returns
  through an explicit confirmation step so already-saved flow data is preserved

Example baseline:
- Level 1: kitchen humidity, hallway humidity, kitchen temperature
- Level 2: bedroom humidity, landing humidity, bedroom temperature
- AQ: one IAQ + one PM2.5 per level if available

Example row:
- entity: `sensor.kitchen_humidity`
- type: `humidity`
- level: `level1`
- room: `Kitchen`

### 4) Temperature Slope Mode

What to do:
- choose whether HI calculates slope automatically or uses provided slope sensors
- open Advanced only for slope source overrides, provided slope sensors, or the optional Air Control temperature chip row
- use `Thresholds & Comfort` after setup for post-configuration temperature comfort adjustments

Suggested baseline:
- use HI-generated slope if you do not already publish stable slope entities
- use external slope entities only when they are already validated
- use automatic temperature comfort unless your household has a fixed comfort policy
- leave the temperature chip row disabled unless you want temperature and slope telemetry shown under Current Air Control

Example (external):
- `sensor.kitchen_temp_slope`
- `sensor.bedroom_temp_slope`

Example (HI-generated):
- source sensors selected: `sensor.kitchen_temp`, `sensor.bedroom_temp`
- slope calculated, mapped through HI diagnostics to the registered Home Assistant entity ID, then displayed and used

### 5) Zones (Zone 1 and Zone 2)

What to do:
- assign each zone to a level and room set
- configure output entities
- choose triggers
- use recommended thresholds first; tune later from `Thresholds & Comfort` if observed behaviour needs adjustment
- open Advanced for normal output stage, boost output stage, and Current Air Control label
- keep boost higher than the normal zone fan level where possible
- in v2.0.6, Zone 2 setup/options defaults to `level2` and trigger labels
  show `Zone 2 / Level 2` ownership unless you explicitly choose a different level

Example baseline:
- Zone 1 label: `Cooking`
- Zone 1 level: `level1`
- Zone 1 normal output level: `66`
- Zone 1 boost output level: `100`
- Zone 1 trigger: humidity delta high
- Zone 2 label: `Bathroom`
- zone 2 trigger: humidity delta high, temp slope delta...
- Zone 2 level: `level2`
- Zone 2 normal output level: `66`
- Zone 2 boost output level: `100`

Example:
- Zone 1 outputs: `fan.kitchen_air`, `fan.living_room_air`
- Zone 2 outputs: `fan.upstairs_air`
- fan stages: `auto`, `33`, `66`, `100`

### 6) Humidifiers

What to do:
- configure per-level humidifier outputs
- confirm on/off behavior against target band
- open Advanced only when you need a target band adjustment

Suggested baseline:
- enable humidifier lanes only on levels with real humidifier hardware
- validate activation below target low
- validate recovery shutoff inside the normal band

Example:
- Level 1 output: `humidifier.downstairs_humidifier`
- turns on when below low target
- turns off when humidity recovers to low target + 3%

### 7) Air Quality

What to do:
- enable AQ per level if AQ telemetry is present
- assign triggers and outputs
- open Advanced for run duration, fan level, and per-trigger thresholds

Suggested baseline:
- AQ output level: `66`
- run duration: `15` to `30` minutes
- IAQ threshold aligned to your sensor scale and household tolerance

Example:
- Level 1 AQ output: `fan.purifier_living`
- trigger: IAQ below threshold
- if Zone or Alert lane is active, AQ is deferred
- if two AQ levels share one output, last trigger update wins output setting

### 8) Alerts and CO Emergency

What to do:
- enable or disable HI-calculated humidity, mould, and condensation alert handling
- add, edit, or remove optional alert visual rules for internally calculated alert sources
- open Advanced on a visual rule for CO threshold, flash mode, duration, or power entity
- CO uses configured CO telemetry and existing ventilation outputs
- set zone boost levels in the Zone pages because alert boost is zone-bound

Suggested baseline:
- keep CO thresholds realistic and bounded
- keep zone boost levels higher than normal zone fan levels
- use dedicated lights for alerts when possible
- use optional `power_entity` only for visual indicator hardware that needs separate power enable
- assign alert rooms to zones; humidity, mould, and condensation alerts use the mapped zone boost level
- avoid tuning humidity danger as a fixed number; change the target profile/custom band when the house-wide high-risk line needs moving
- check the reason panel and `HI Active Alert Context` for originating sensor, room, resolved zone, and degraded mapping warnings

Example visual indicator rule:
- internal alert source: mould risk
- room: `Bathroom`
- lights: `light.bathroom_alert`
- power entity: `switch.bathroom_light_power` (optional)

Example CO:
- internal alert source: CO emergency
- threshold: `15`
- outputs: existing configured zone/AQ ventilation outputs

### 9) UI Deployment

What to do:
- finish setup
- select the card layout to generate; new installs default to `v2_tablet`
- use the notification path to find generated YAML under `/config`
- use services later when you need a fresh export or a generated dashboard


Suggested baseline:
- start with the default initial `v2_tablet` layout, then add mobile if needed
- verify Current Air Control, chips, and outputs
- re-run `humidity_intelligence.dump_cards` after changing the optional temperature chip row or output-details visibility option
- paste refreshed YAML into existing Manual cards after UI visibility, template, or mapping changes
- hard-refresh the browser or Home Assistant app if the old card remains cached

Service options:
- `humidity_intelligence.create_dashboard`
- `humidity_intelligence.view_cards`
- `humidity_intelligence.dump_cards`

Example service usage:
- create dashboard with `layout: v2_mobile`, `title: Humidity Intelligence`, `url_path: humidity-intelligence`

---

## Configuration Screenshots (Visual Guide)

These images are a visual orientation aid. The current V2 flow uses live
collapsible Advanced sections, so the exact visible fields depend on which section is
expanded.

<details>
<summary>Open configuration screenshots</summary>

### 1) Frontend Dependencies
<img src="assets/readme/config_dependencies.png" width="760" alt="Frontend dependencies step">

### 2) Global Gates
<img src="assets/readme/config_global_gate.png" width="460" alt="Global gate settings">
<img src="assets/readme/config_presence_states.png" width="760" alt="Presence state mapping">

### 3) Telemetry Inputs
<img src="assets/readme/config_Telemetry_input.png" width="760" alt="Telemetry input table">
<img src="assets/readme/config_telemetry_input_dropdown.png" width="760" alt="Telemetry input selectors">

### 4) Zones
<img src="assets/readme/config_zone_1_config.png" width="560" alt="Zone 1 configuration">
<img src="assets/readme/config_zone_2_config.png" width="560" alt="Zone 2 configuration">
<img src="assets/readme/config_zone_thershold.png" width="560" alt="Zone threshold configuration">

### 5) Humidifiers
<img src="assets/readme/config_humidifier.png" width="760" alt="Humidifier configuration">

### 6) Air Quality
<img src="assets/readme/config_AQ.png" width="460" alt="AQ setup menu">
<img src="assets/readme/config_aq_settings.png" width="460" alt="AQ settings form">

### 7) Alerts
<img src="assets/readme/config_add_alert.png" width="460" alt="Add alert configuration">

### 8) Sensor Management (Options)
<img src="assets/readme/config_add_sensors.png" width="460" alt="Add sensors in options">

</details>

---

## UI Gallery

Reusable default UI examples live in [ui-gallery](ui-gallery/README.md).

Included examples:

- [Default V2 Mobile AQ](ui-gallery/default-v2-mobile-aq/README.md)
- [Default V2 Tablet Zone 2](ui-gallery/default-v2-tablet-zone-2/README.md)
- [Default V1 Mobile](ui-gallery/default-v1-mobile/README.md)

For new gallery submissions, follow [ui-gallery/CONTRIBUTING.md](ui-gallery/CONTRIBUTING.md).

---

## Post-Configuration Workflow

When modifying options:

1. change one section at a time
2. save
3. run `humidity_intelligence.refresh_ui`
4. verify:
   - Current Air Control mode
   - gate chips
   - reason text
   - output behavior

Post-config sensor/lane management:

1. use `Sensors` to add, edit, or delete any telemetry row (humidity, temperature, IAQ, PM2.5, VOC, CO2, CO)
2. use `Global Gates` to edit time gate, presence gate, alert-only mode, and target profile; open Advanced for control loop interval, startup UI mapping refresh, custom humidity band, and generated-card output details visibility
3. use `Thresholds & Comfort` to review temperature comfort mode; open Advanced for custom comfort values and per-zone humidity high, AQ, condensation risk, and mould risk thresholds
4. use `Humidifiers` to add or edit humidifier lanes per level and update output entities; open Advanced for lane removal or band adjustment
5. use `Air Quality` to add or edit AQ lanes per level and update triggers/outputs; open Advanced for lane removal, run duration, fan level, and AQ thresholds
6. lane selections marked as `not configured - select to add` can be used to create missing lanes later without reinstalling

UI visibility options:

1. keep `Show output entity details` off for the cleaner default V2 display
2. enable it only when you want the generated-card output details panel for deeper troubleshooting
3. after changing it, run `humidity_intelligence.dump_cards`
4. paste the refreshed YAML into existing Manual card(s)

Alert-only toggle workflow:

1. toggle `alert_only_mode` in options and save
2. HI reloads and regenerates exported cards automatically
3. open the updated `/config/humidity_intelligence_cards_<layout>.yaml`
4. re-paste YAML into Manual card(s) so control visibility and reason text match mode

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
- File outputs are written into your HA config folder.

### `create_dashboard`
Purpose:
- create a Lovelace dashboard from a rendered HI layout.

Example:
```yaml
service: humidity_intelligence.create_dashboard
data:
  layout: v2_mobile
  title: Humidity Intelligence
  url_path: humidity-intelligence
```

### `view_cards`
Purpose:
- render cards and write them to file, then push a notification with file path.

Example:
```yaml
service: humidity_intelligence.view_cards
data:
  filename: humidity_intelligence_cards
  layout: v2_tablet
```

### `dump_cards`
Purpose:
- render and export card YAML to file without dashboard creation.
- use this after upgrading or changing options when an existing Manual dashboard card needs the latest HI YAML.
- omit `layout` to export all cached/generated layouts.
- supply `layout` to export only one layout.
- paste the generated YAML from `/config/humidity_intelligence_cards_<layout>.yaml` back into the relevant Dashboard Manual card.

Example:
```yaml
service: humidity_intelligence.dump_cards
data:
  filename: humidity_intelligence_cards
  layout: v2_mobile
```

### `refresh_ui`
Purpose:
- rebuild placeholder mapping and refresh rendered UI output after config changes.
- runs automatically shortly after Home Assistant startup when `auto_refresh_ui_on_startup` is enabled in options.

Example:
```yaml
service: humidity_intelligence.refresh_ui
data: {}
```

### `flash_lights`
Purpose:
- run alert flash behavior manually for testing.
- runtime humidity/mould/condensation visual alert rules flash configured lights 10 times, restore the prior light state, wait 30 minutes, then repeat only if the same alert source is still active.
- CO emergency remains the top-priority safety lane and is not demoted by humidity visual-alert repeats.

Example:
```yaml
service: humidity_intelligence.flash_lights
data:
  power_entity: switch.alert_power
  lights:
    - light.bathroom_alert
  color: [255, 0, 0]
  duration: 12
  flash_count: 8
```

### `pause_control`
Purpose:
- pause automation engine for a set duration.

Example:
```yaml
service: humidity_intelligence.pause_control
data:
  minutes: 60
```

### `resume_control`
Purpose:
- clear pause state and resume runtime immediately.

Example:
```yaml
service: humidity_intelligence.resume_control
data: {}
```

### `self_check`
Purpose:
- run mapping, telemetry, house humidity drift dependency, and optional frontend dependency resource checks and write report JSON.
- frontend dependency status is read from the same Lovelace resource inspection path used by setup/options, `v205_release_check`, and diagnostics.

Example:
```yaml
service: humidity_intelligence.self_check
data: {}
```

### `v205_release_check`
Purpose:
- run a read-only v2.0.5/v2.0.6 release-validation report in Home Assistant.
- verify generated-card output-details visibility, cached layout coverage, unresolved placeholders, card text sanity, configured entity availability, house humidity drift dependency status, and optional frontend dependency status.
- with `write_test_exports: true`, write test card exports proving unscoped `dump_cards` exports all layouts and scoped export writes only `v2_tablet`.
- reports optional local HI-only snapshot status; `require_local_hi_snapshot` can be enabled for maintainer validation when a fresh package-local snapshot is required.
- no runtime outputs, helpers, lanes, or configured entities are changed.

Example:
```yaml
service: humidity_intelligence.v205_release_check
data:
  write_test_exports: true
  filename: humidity_intelligence_v205_release_check.json
```

### `create_local_backup`
Purpose:
- create a local HI-only snapshot of the installed `/config/custom_components/humidity_intelligence` package.
- support beta validation and rollback preparation for advanced maintainers.
- this is not a Home Assistant backup, does not intercept HACS updates, does not restore code, and does not change running code until Home Assistant is restarted after any separate manual file work.

Example:
```yaml
service: humidity_intelligence.create_local_backup
data:
  retain_count: 2
  max_total_bytes: 52428800
```

### `list_saved_versions`
Purpose:
- list finalized local HI-only snapshots and invalid snapshot folders.
- report snapshot metadata without changing running code.

Example:
```yaml
service: humidity_intelligence.list_saved_versions
data: {}
```

### `dump_diagnostics`
Purpose:
- export runtime diagnostics, mapping, active target profile, visual alert rules, alert source resolution, house humidity drift dependency status, local HI-only snapshot status, optional frontend dependency resource status, unavailable entities, and card info to JSON.
- `HI Diagnostics` keeps only a compact recorder-safe summary in live state attributes; use this service for a full local support export.
- For GitHub issues, prefer the native Home Assistant diagnostics download from the Humidity Intelligence integration entry.

Example:
```yaml
service: humidity_intelligence.dump_diagnostics
data:
  filename: humidity_intelligence_diagnostics.json
```

### `purge_files`
Purpose:
- remove generated HI files and attempt dashboard cleanup.

Example:
```yaml
service: humidity_intelligence.purge_files
data: {}
```

Safety guidance:
- use `purge_files` only when intentionally resetting generated artifacts
- run `dump_diagnostics` before purge if you want a snapshot for troubleshooting

---

## Documentation and Support Manual

The README covers installation, current release highlights, core usage, screenshots,
services, support entry points, and release notes.

For longer support guidance, see the Humidity Intelligence Wiki:

- [Getting Help](https://github.com/senyo888/humidity-intelligence/wiki/Getting-Help)
- [Diagnostics and Support Bundle](https://github.com/senyo888/humidity-intelligence/wiki/Diagnostics-and-Support-Bundle)
- [Generated Dashboards](https://github.com/senyo888/humidity-intelligence/wiki/Generated-Dashboards)
- [HACS and Updates](https://github.com/senyo888/humidity-intelligence/wiki/HACS-and-Updates)
- [Configuration Walkthrough](https://github.com/senyo888/humidity-intelligence/wiki/Configuration-Walkthrough)
- [Understanding Control Decisions](https://github.com/senyo888/humidity-intelligence/wiki/Understanding-Control-Decisions)
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

The diagnostics file includes:

- Humidity Intelligence and Home Assistant versions
- config entry/options summary
- selected telemetry, gate, zone, AQ, humidifier, alert, and output entities
- enabled feature areas
- current runtime lane/mode, gate state, output state, and reason text
- active alert resolution
- house humidity drift dependency status
- frontend dependency status when Home Assistant exposes Lovelace resources
- generated UI/card summary
- unavailable/unknown configured entities and support warnings

Sensitive keys and values such as tokens, passwords, API keys, webhook URLs, credential-bearing URLs, location fields, usernames, host/IP/MAC/SSID values, device IDs, and unique IDs are redacted. Entity IDs are included because they are needed to debug mappings; review the file before uploading if your entity names contain personal details.

Issue triage expects diagnostics-first reports where practical. Issues with native diagnostics are faster to classify and usually need fewer follow-up questions; issues without diagnostics may be marked as needing a support bundle.

For wider ideas, dashboard suggestions, compatibility requests, documentation improvements, or automation/control suggestions, use the Community Ideas & Proposals issue form. These issues are intake signals only: reactions and comments may inform visibility, but they do not approve implementation, runtime changes, release scope, or Home Assistant behavior changes. Submitting an idea does not guarantee implementation, release scheduling, or acceptance.

More detail:

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

### v2.0.6

- promoted integration metadata to stable `2.0.6`
- added degraded `telemetry_unavailable` runtime mode when required humidity or configured temperature telemetry is unavailable, so HI stands down safely instead of reporting normal/all-clear
- fixed global gate preemption so a running humidity-danger alert lane clears its alert context and Current Air Control does not keep showing stale alert-running state after the gate takes over
- no migration is required for the global gate preemption fix; after updating HI through HACS or file replacement, restart Home Assistant. Use config-entry reload only after option changes once the updated code is already loaded. Then run `humidity_intelligence.dump_cards` or re-copy any pasted dashboard YAML and refresh dashboard/browser cache to see the Current Air Control card update
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

<details>
<summary>Previous Releases</summary>

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
- updated Current Air Control reason field behavior for alert-only mode so it reports monitoring/alerts context and does not imply missing output controls
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
