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
- config entry and options summary
- selected telemetry, gate, zone, AQ, humidifier, alert, and output entities
- enabled feature areas
- Home Assistant Area/Label setup-assist status, including sanitized counts for
  advisory metadata context and saved-room mismatches
- current runtime mode/lane and reason text
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
names, Area names, Label names, entity maps, and state dumps. Review the file before
uploading if your local names contain personal information.

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

Native diagnostics are the preferred GitHub attachment. The existing
`humidity_intelligence.dump_diagnostics` service remains useful for local Home
Assistant validation and writes a fuller JSON export under
`<config>/humidity_intelligence/exports/`. The service requires an authenticated
admin user context; non-admin and contextless background calls are rejected. Users
should attach the native Home Assistant diagnostics download unless asked otherwise.
Review any full `dump_diagnostics` export before sharing it publicly because it
intentionally contains more local troubleshooting context than the native issue
bundle.

The v2.0.9 path change is non-destructive. Existing report and card files in the
config root are not moved, copied, symlinked, dual-written, or deleted. The fixed
self-check report now lives at
`<config>/humidity_intelligence/exports/humidity_intelligence_self_check.json`;
generated card YAML lives under `<config>/humidity_intelligence/ui/`. Registered
dashboard YAML remains at `<config>/dashboards/<url_path>.yaml`.

Update file sensors, shell commands, support tools, or other consumers from
`<config>/<report filename>` to
`<config>/humidity_intelligence/exports/<report filename>` and from
`<config>/<card filename>` to
`<config>/humidity_intelligence/ui/<card filename>` only after verifying a newly
generated owned-directory artifact. Then disable or remove the stale root consumer
explicitly so old JSON/YAML cannot silently remain authoritative. Multi-entry
installations must use the entry-qualified card filename reported by the service
notification. Adding a second entry re-exports every loaded entry with qualified
names; removing back to one re-exports the remaining entry with unqualified names.
HI no longer refreshes superseded owned-UI files, but external consumers can still
read their stale content. Do not treat an older inferred filename as current truth;
follow the newest notification and remove stale defaults through an explicit
previewed purge when desired. Config-entry removal deletes only the removed entry's
exact default/release-test UI exports and registered dashboard. It retains reports,
custom card exports, legacy root files, and the remaining entry's superseded
qualified files after a multi-entry installation returns to one entry.

External `self_check`, `dump_cards`, and `view_cards` calls now require an
authenticated admin user context, matching the existing report-writer authority
boundary. Contextless automations/scripts are rejected. HI-owned first-run, options,
and release-check test-card regeneration continues through its trusted internal path.
Startup refresh remains cache-only and does not claim that files were written.

Keep a backup of every external consumer definition before changing it. A full Home
Assistant restart is required after installing or rolling back the package; a
config-entry reload is suitable only for exercising already-loaded updated code.
Rollback restores the complete prior integration package and backed-up consumer
paths, then requires another full restart. Files already written in either owned
directory are retained and are not moved back to the config root. Rolling back also
restores the older root-writer and external caller-authority behavior.
