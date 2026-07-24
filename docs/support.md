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

The v2.0.9 path change is non-destructive. Existing report files in the config root
are not moved, copied, or deleted. Update file sensors, shell commands, support tools,
or other consumers from `<config>/<filename>` to
`<config>/humidity_intelligence/exports/<filename>` after verifying a new report.
Keep a backup of any external consumer definition before changing it. A full Home
Assistant restart is required after installing or rolling back the package.
Rollback restores the complete prior integration package and the backed-up consumer
paths, then requires another full restart. Files already written in the owned export
directory are retained; they are not moved back to the config root. Rolling back also
restores the older root-writer and caller-authority behavior.
