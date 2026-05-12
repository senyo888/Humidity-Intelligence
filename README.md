<!-- Logo and Banner -->

![Humidity Intelligence banner](assets/header.png)

# Humidity Intelligence V2

## Deterministic Environmental Control for Home Assistant

[![Latest Release](https://img.shields.io/github/v/release/senyo888/Humidity-Intelligence?display_name=tag&sort=semver)](https://github.com/senyo888/Humidity-Intelligence/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom%20Integration-orange)](https://hacs.xyz)
[![Integration Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fsenyo888%2FHumidity-Intelligence%2Fmain%2Fmanifest.json&query=%24.version&label=Integration&prefix=v&color=blue)](manifest.json)
[![License](https://img.shields.io/github/license/senyo888/Humidity-Intelligence)](LICENSE)

## Contents

- [What Humidity Intelligence V2 Is](#what-humidity-intelligence-v2-is)
- [Support Humidity Intelligence](#support-humidity-intelligence)
- [Why Environmental Stability Matters](#why-environmental-stability-matters)
- [Season-Aware Environmental Control](#season-aware-environmental-control)
- [Architecture Overview](#architecture-overview)
- [v2.0.5 Highlights](#v205-highlights)
- [v2.0.4 Highlights](#v204-highlights)
- [Installation](#installation)
- [Frontend Dependencies](#frontend-dependencies)
- [Migration Guide - v1 to v2](#migration-guide---v1-to-v2)
- [Full Configuration Flow](#full-configuration-flow)
- [v2.0.4 UI Screenshots](#v204-ui-screenshots)
- [Configuration Screenshots (Visual Guide)](#configuration-screenshots-visual-guide)
- [UI Gallery](#ui-gallery)
- [Post-Configuration Workflow](#post-configuration-workflow)
- [How to Use Services](#how-to-use-services)
- [Release Notes](#release-notes)
- [Design Philosophy](#design-philosophy)

---

## What Humidity Intelligence V2 Is

Humidity Intelligence V2 is not a collection of automations.

It is a **deterministic environmental runtime engine**.

It replaces stacked triggers and conflicting scripts with:

- a lane-based priority architecture
- physics-aware environmental modelling
- global gating logic
- one authoritative control state per evaluation cycle

There is no "last automation wins."
There is no trigger race condition.
There is one resolved outcome, every time.

This is environmental control with structure.

Positioning: **environmental stability + seasonal context**.

<details>
<summary><strong>Quick Demo (GIF)</strong></summary>

<br>

![Humidity Intelligence quick demo](assets/readme/hi_quick_demo.gif)

</details>

<details>
<summary><strong>V2 UI Examples (PNG)</strong></summary>

<br>

<img src="assets/v2_ui_gallery/v204_zone_alert_boost.png" width="320" alt="v2.0.4 zone-bound alert boost context">
<img src="assets/v2_ui_gallery/v204_unmapped_alert_context.png" width="320" alt="v2.0.4 unmapped alert degraded context">
<img src="assets/v2_ui_gallery/v204_zone2_temperature_chips.png" width="320" alt="v2.0.4 Zone 2 with optional temperature chips">
<img src="assets/v2_ui_gallery/v204_current_air_control_ready.png" width="320" alt="v2.0.4 Current Air Control ready state">
<img src="assets/v2_ui_gallery/v204_presence_gate_reason.png" width="320" alt="v2.0.4 presence gate reason context">
<img src="assets/v2_ui_gallery/IMG_5665.png" width="320" alt="V2 UI gallery image 6">
<img src="assets/v2_ui_gallery/IMG_5672.png" width="320" alt="V2 UI gallery image 7">
<img src="assets/v2_ui_gallery/IMG_5673.png" width="320" alt="V2 UI gallery image 8">
<img src="assets/v2_ui_gallery/IMG_5674.png" width="320" alt="V2 UI gallery image 9">
<img src="assets/v2_ui_gallery/IMG_0323.png" width="320" alt="V2 UI gallery image 10">
<img src="assets/v2_ui_gallery/IMG_0324.png" width="320" alt="V2 UI gallery image 11">
<img src="assets/v2_ui_gallery/IMG_5675.png" width="320" alt="V2 UI gallery image 12">
<img src="assets/v2_ui_gallery/ui_v1_mobile.png" width="320" alt="V2 UI gallery image 13">
<img src="assets/v2_ui_gallery/ui_v2_mobile_aq.png" width="320" alt="V2 UI gallery image 14">
<img src="assets/v2_ui_gallery/ui_v2_tablet_zone_2.png" width="320" alt="V2 UI gallery image 15">

</details>

---

## Support Humidity Intelligence

### ⭐ Enjoying Humidity Intelligence?

If you're finding Humidity Intelligence useful, insightful, or just interesting to explore, consider giving the repository a star.

It helps others discover the project, supports ongoing development, and shows that this kind of deterministic, explainable approach to Home Assistant has community value.

[Star Humidity Intelligence on GitHub](https://github.com/senyo888/Humidity-Intelligence)

---

## Why Environmental Stability Matters

Most dashboards show a number.
Humidity Intelligence models behavior.

Humidity problems rarely appear as isolated spikes.
They emerge as:

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

V2 models that instability structurally.

---

## Season-Aware Environmental Control

`56%` is not always "high."

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

Temperature comfort uses the same source-of-truth approach for display:

- Automatic mode resolves the active seasonal comfort band
- Custom mode allows a fixed lower/upper comfort band
- Temperature chips use HI comfort sensors, not card-only thresholds

Default temperature comfort bands:

- Winter: `19.5°C` to `20.5°C`
- Spring: `20°C` to `21°C`
- Summer: `20°C` to `22.5°C`
- Autumn: `19.5°C` to `21°C`

---

## Architecture Overview

Humidity Intelligence V2 operates across three defined layers.

### 1) Intelligence Layer - Environmental Physics

Transforms raw telemetry into structured environmental signals:

- dynamic house average humidity
- 7-day mean and drift tracking
- Magnus dew point calculation
- condensation spread (`temperature - dew_point`)
- mould risk normalization
- worst-room detection
- binary danger states

This layer models risk
and does not control hardware.

### 2) Control Layer - Deterministic Priority Engine

Canonical runtime order:

1. CO Emergency: highest priority automation
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

This eliminates automation conflict entirely.

### 3) Presentation Layer - UI Truth Contract

The UI reflects runtime truth:

- active lane
- gate blocks
- override state
- reason text
- output stage transparency

The UI does not compute logic.
The engine decides.
The UI renders.

---

## v2.0.5 Highlights

- setup and options now present essentials first, with tuning controls behind Advanced sections
- HI applies recommended defaults unless you customise them
- control loop interval, startup UI mapping refresh, custom humidity targets, custom temperature comfort values, slope sources, fan levels, and threshold tuning remain available as advanced controls
- new installs default the generated V2 dashboard to a cleaner output display
- `Show output entity details` can re-enable the expandable output details panel when deeper runtime inspection is useful
- `v2_tablet` is selected by default during initial UI export; unscoped `dump_cards` still exports all cached/generated layouts unless `layout` is supplied
- deterministic runtime lane ordering, alert hierarchy, CO emergency behavior, humidifier independence, entity names, and `dump_cards` remain unchanged

Upgrade note: **v2.0.5 is a configuration UX reorganisation release, not a runtime feature release.**
After changing UI visibility options, run `humidity_intelligence.dump_cards` and paste the updated YAML into existing Manual cards.

---

## v2.0.4 Highlights

- humidity, mould, and condensation alerts now resolve originating room/sensor to the mapped zone
- alert control uses the resolved zone's boost fan level as the single deterministic output path
- alert reason text and UI chips expose alert type, severity, room, zone, and degraded mapping warnings
- multiple simultaneous alerts resolve by alert hierarchy first and zone priority second
- humidity danger alerts follow the active profile high-risk threshold instead of a saved static threshold
- HI UI mapping can refresh automatically shortly after Home Assistant startup
- dashboard YAML must be re-exported and pasted into existing Manual cards to see the new alert chips/reason-panel UI
- V2 exported YAML now includes a short header explaining where to paste it, when to re-run `dump_cards`, and which custom cards are required
- Air Control humidity chips now use configured zone-room telemetry, and an optional temperature chip row can be enabled from Temperature Slope settings

Upgrade note: **v2.0.4 focuses on alert attribution, zone-bound boost behavior, and startup UI refresh reliability.**
No breaking schema changes are introduced.

Manual dashboard update:
1. Call `humidity_intelligence.dump_cards`.
2. Open the generated `/config/humidity_intelligence_cards_<layout>.yaml` file.
3. Copy the updated YAML into the relevant Dashboard Manual card.
4. Save the dashboard and hard-refresh the browser/app if Home Assistant still shows the old card.

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

Humidity Intelligence V2 is designed to run **fully at the backend level**, but the **UI experience depends on a small set of frontend cards**.

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

These tools are foundational to the Home Assistant ecosystem, and this project would not hit the same level without them.

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

Follow this sequence on first install.

### 1) Frontend Dependencies

What to do:
- open the Frontend Dependencies step in config flow
- review installed/detected status and direct resource links where shown
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
- open Advanced only for control loop interval, startup UI mapping refresh, custom humidity targets, custom temperature comfort limits, or output entity details

Example baseline:
- time gate enabled: `06:00` to `23:30`
- outside action: `safe_state`
- presence entities: `person.adam`, `person.eve`, or alarm panel
- present states: `home`, `on`, `disarmed`
- away states: `not_home`, `off`, `armed_away`, `away`
- target profile mode: `auto`
- output entity details: off for a cleaner dashboard unless you want the expandable output panel

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
- slope calculated displayed and used 

### 5) Zones (Zone 1 and Zone 2)

What to do:
- assign each zone to a level and room set
- configure output entities
- choose triggers
- use recommended thresholds first; tune later from `Thresholds & Comfort` if observed behaviour needs adjustment
- open Advanced for normal output stage, boost output stage, and Current Air Control label
- keep boost higher than the normal zone fan level where possible

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
- click finish setup
- select card(s) you would like to generate
- card YAML dropped with notification of location  
- if not generate mapped cards through services


Suggested baseline:
- start with the default initial `v2_tablet` layout, then add mobile if needed
- verify Current Air Control, chips, and outputs
- re-run `humidity_intelligence.dump_cards` after changing the optional temperature chip row or output entity details option
- then add second layout if needed

Service options:
- `humidity_intelligence.create_dashboard`
- `humidity_intelligence.view_cards`
- `humidity_intelligence.dump_cards`

Example service usage:
- create dashboard with `layout: v2_mobile`, `title: Humidity Intelligence`, `url_path: humidity-intelligence`

---

## v2.0.4 UI Screenshots

These examples show the release UI truth surfaces: alert attribution, degraded/unmapped alert reporting, zone-bound alert boost, gate reason context, and optional runtime temperature comfort chips.

<p>
  <img src="assets/readme/v204_zone_alert_boost.png" width="320" alt="Zone-bound humidity danger alert boost">
  <br>
  <strong>Zone-bound alert boost:</strong> humidity danger resolves to the originating room and mapped zone before using that zone's boost level.
</p>

<p>
  <img src="assets/readme/v204_unmapped_alert_context.png" width="320" alt="Unmapped alert degraded context">
  <br>
  <strong>Degraded alert context:</strong> unmapped alert candidates are reported clearly instead of triggering a blind boost.
</p>

<p>
  <img src="assets/readme/v204_zone2_temperature_chips.png" width="320" alt="Optional temperature comfort chip row">
  <br>
  <strong>Temperature chip row:</strong> optional chips use HI runtime comfort sensors for blue, green, yellow, and red comfort colouring.
</p>

<p>
  <img src="assets/readme/v204_current_air_control_ready.png" width="320" alt="Current Air Control ready state">
  <br>
  <strong>Current Air Control:</strong> the reason panel and chips render backend truth, not card-only logic.
</p>

<p>
  <img src="assets/readme/v204_presence_gate_reason.png" width="320" alt="Presence gate reason context">
  <br>
  <strong>Gate reason context:</strong> gate holds show the blocking condition and snapshot so the paused lane is explainable.
</p>

Manual dashboard update after upgrading:

1. Run `humidity_intelligence.dump_cards`.
2. Open the generated `/config/humidity_intelligence_cards_<layout>.yaml` file.
3. Paste the YAML into your existing Dashboard Manual card for that layout.
4. Save, then hard-refresh the browser or Home Assistant app if the old card is still cached.

## Configuration Screenshots (Visual Guide)


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
2. use `Global Gates` to edit time gate, presence gate, alert-only mode, and target profile; open Advanced for control loop interval, startup UI mapping refresh, custom humidity band, and output entity details
3. use `Thresholds & Comfort` to review temperature comfort mode; open Advanced for custom comfort values and per-zone humidity high, AQ, condensation risk, and mould risk thresholds
4. use `Humidifiers` to add or edit humidifier lanes per level and update output entities; open Advanced for lane removal or band adjustment
5. use `Air Quality` to add or edit AQ lanes per level and update triggers/outputs; open Advanced for lane removal, run duration, fan level, and AQ thresholds
6. lane selections marked as `not configured - select to add` can be used to create missing lanes later without reinstalling

UI visibility options:

1. keep `Show output entity details` off for the cleaner default V2 display
2. enable it only when you want the expandable output details panel for deeper troubleshooting
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
- run mapping, frontend dependency, and telemetry health checks and write report JSON.

Example:
```yaml
service: humidity_intelligence.self_check
data: {}
```

### `v205_release_check`
Purpose:
- run a read-only v2.0.5 release-validation report in Home Assistant.
- verify generated-card output-details visibility, cached layout coverage, unresolved placeholders, card text sanity, configured entity availability, and optional frontend dependency status.
- with `write_test_exports: true`, write test card exports proving unscoped `dump_cards` exports all layouts and scoped export writes only `v2_tablet`.
- no runtime outputs, helpers, lanes, or configured entities are changed.

Example:
```yaml
service: humidity_intelligence.v205_release_check
data:
  write_test_exports: true
  filename: humidity_intelligence_v205_release_check.json
```

### `dump_diagnostics`
Purpose:
- export runtime diagnostics, mapping, active target profile, visual alert rules, alert source resolution, unavailable entities, and card info to JSON.
- `HI Diagnostics` keeps only a compact recorder-safe summary in live state attributes; use this service for the full support bundle.

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

## Release Notes

### v2.0.5

- reorganised setup and options around essentials first, with tuning controls behind Advanced sections
- added recommended-default guidance to setup and post-configuration pages
- kept control loop interval, startup UI mapping refresh, custom humidity targets, slope source selection, temperature chips, fan levels, thresholds, lane removal, and alert visual tuning available as advanced controls
- made `Thresholds & Comfort` easier to scan by keeping temperature comfort mode visible and moving custom comfort values plus zone thresholds into Advanced
- added `show_output_entity_details` / `Show output entity details` as a UI-only option for generated V2 cards
- defaulted new generated V2 cards to hide the expandable output details panel unless the option is enabled
- changed first-install UI export default to `v2_tablet`
- kept deterministic runtime behavior, lane ordering, alert hierarchy, CO emergency handling, humidifier independence, public entity semantics, and `dump_cards` unchanged
- bumped integration version to `2.0.5`

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

<details>
<summary>Previous Releases</summary>

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

---

## Design Philosophy

- determinism over cleverness
- transparency over magic
- one authoritative state
- explicit override hierarchy
- safe fallback over silent failure

Humidity Intelligence V2 your environmental runtime architecture.
