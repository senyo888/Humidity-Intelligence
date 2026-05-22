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
- current runtime mode/lane and reason text
- gate states
- output state summary
- active alert resolution
- house humidity drift 7d statistics dependency status
- optional frontend dependency status when Home Assistant exposes Lovelace resources
- generated UI/card summary
- unavailable or unknown configured entities
- diagnostics warnings

## What Is Redacted

The diagnostics platform uses Home Assistant `async_redact_data` plus HI's own URL and token sanitising.

It redacts sensitive keys and values such as:

- tokens and bearer credentials
- secrets and passwords
- API keys
- webhook URLs
- URLs and URL query credentials
- latitude, longitude, and address-style location fields
- usernames, email, phone, host, IP, MAC, SSID, device ID, and unique ID fields

Entity IDs are intentionally included because they are usually needed to debug mappings and unavailable entities. Review the file before uploading if your entity names contain personal information.

## If You Cannot Download Diagnostics

Open the issue anyway and fill in the fallback fields:

- Humidity Intelligence version
- Home Assistant version
- affected area
- what happened
- checks already tried
- redacted logs or screenshots if useful

## Maintainer Notes

Native diagnostics are the preferred GitHub attachment. The existing `humidity_intelligence.dump_diagnostics` service remains useful for local Home Assistant validation and writes a fuller JSON export to `/config`, but users should attach the native Home Assistant diagnostics download unless asked otherwise. Review any full `dump_diagnostics` export before sharing it publicly because it intentionally contains more local troubleshooting context than the native issue bundle.
