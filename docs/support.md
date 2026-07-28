# Support and Diagnostics

Use Home Assistant's native diagnostics download when reporting a Humidity Intelligence issue. This is the preferred GitHub support bundle for v2.0.5 and later.

## Download Diagnostics

1. Open **Settings -> Devices & services**.
2. Open **Humidity Intelligence**.
3. Use the entry menu and select **Download diagnostics**.
4. Attach the downloaded file to your GitHub issue.

This helps maintainers understand your setup without asking lots of follow-up questions.

Please review the bundle before attaching if you are concerned about privacy. The bundle is designed to redact sensitive values, but you remain in control of what you upload.

## What It Contains

- Humidity Intelligence version
- Home Assistant version
- sanitized config entry and options summaries
- configuration counts and selected-entity category/status summaries
- enabled feature areas
- Home Assistant Area/Label setup-assist status, including sanitized counts for
  advisory metadata context and saved-room mismatches
- current runtime mode/lane and reason availability/truncation
- gate states
- output state summary
- active alert resolution
- compact local HI-only snapshot status
- house humidity drift 7d statistics dependency status, including helper readiness
  fields such as `age_coverage_ratio`, `required_age_coverage_ratio`,
  `source_value_valid`, `repair_required`, and `repair_kind` when available
- optional frontend dependency status when Home Assistant exposes Lovelace resources
- generated UI/card summary
- generated-card entity reference availability
- unavailable or unknown configured entities
- diagnostics warnings

## What Is Redacted

The diagnostics platform uses Home Assistant `async_redact_data` plus HI's own URL and token sanitising.

It redacts sensitive keys and values such as:

- tokens and bearer credentials
- credential-style keys
- secrets and passwords
- API keys
- webhook URLs
- URLs and URL query credentials
- latitude, longitude, and address-style location fields
- usernames, email, phone, host, IP, MAC, SSID, device ID, and unique ID fields

Native diagnostics prefer structure, counts, and statuses over raw entity IDs, room
names, Area names, Label names, entity maps, and state dumps. Selected mapping and
local-name evidence is generally reduced, but user-configured display and level labels may remain.
Review the complete file before uploading it to a public issue.

## Optional Public Inspector Preflight

The public
[HI Support Bundle Inspector](https://senyo888.github.io/humidity-intelligence/inspector/)
processes a supported diagnostics file in the browser tab and can generate a short
`HI-SUPPORT-HANDOFF/1` block. Bug reports and configuration-help issues provide a
separate optional field for that text.

The handoff is a reduced, unsigned advisory snapshot. Native Home Assistant
diagnostics remain the preferred attachment. Runtime decisions, source
authentication, live-state verification, reason and lane selection remain with Home
Assistant and HI; correctness and anonymity remain separate user assessments.

The Inspector is an optional preflight; repository and Wiki guidance remain canonical
support documentation. Parsing and handoff generation stay in the browser tab.
GitHub Pages receives normal page-request metadata while selected diagnostic contents
remain in the tab. Copying occurs only when the user activates Copy; pasting the
result into a GitHub issue creates normal GitHub retention. The handoff field accepts
only the generated handoff text. Full `dump_diagnostics` exports remain local unless
a maintainer explicitly requests one.

## If You Cannot Download Diagnostics

Open the issue anyway and fill in the fallback fields:

- Humidity Intelligence version
- Home Assistant version
- affected area
- what happened
- checks already tried
- redacted logs or screenshots if useful

## Community Ideas & Proposals

Use the Community Ideas & Proposals issue form for ideas, dashboard suggestions, documentation
improvements, compatibility requests, diagnostics/support-flow improvements, and
automation/control suggestions that are not immediate bug reports.

Community ideas do not require a diagnostics bundle unless the idea depends on a
specific runtime, dashboard, or integration behavior. If a proposal is really a bug or
configuration problem, maintainers may reclassify it and ask for the native Home
Assistant diagnostics download.

Community interest helps maintainers understand visibility and demand. Implementation
approval stays with maintainer review, deterministic runtime behavior, UI truth, Home
Assistant compatibility, and maintainability.

Idea submission is an intake signal rather than an implementation, release-scheduling,
or acceptance commitment. The usual path is:

```text
Community idea issue -> maintainer triage -> formal HI proposal only if warranted
```

Public status wording should stay expectation-safe:

- Submitted
- Needs Info
- Triaged
- Accepted for Review
- Proposal Drafted
- Planned
- Not Accepted
- Archived

## Maintainer Notes

Native diagnostics are the preferred GitHub attachment. The existing `humidity_intelligence.dump_diagnostics` service remains useful for local Home Assistant validation and writes a fuller JSON export to `/config`, but users should attach the native Home Assistant diagnostics download unless asked otherwise. Review any full `dump_diagnostics` export before sharing it publicly because it intentionally contains more local troubleshooting context than the native issue bundle.
