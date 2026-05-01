# Contributing to Humidity Intelligence

Thanks for helping improve Humidity Intelligence. This repository is maintained as a Home Assistant custom integration intended for HACS users, so changes should preserve a clear integration layout, predictable behavior, and safe public examples.

## Branches and pull requests

Open pull requests against `develop`. The `main` branch is reserved for stable release history unless the maintainer says otherwise.

Before opening a PR:

- Install or update the integration in a Home Assistant test instance.
- Restart Home Assistant and confirm the integration loads cleanly.
- Check Home Assistant logs for new warnings or errors.
- Validate the config flow when setup behavior changes.
- Run `humidity_intelligence.refresh_ui` when dashboard output or generated UI changes.
- Update documentation when behavior, setup steps, services, or UI examples change.

## HACS custom integration context

Humidity Intelligence is a structured Home Assistant custom integration. HACS integration repositories should contain one integration per repository, with runtime files under:

```text
custom_components/humidity_intelligence/
```

Do not add unrelated integrations to this repository. Keep HACS metadata, integration metadata, and documentation aligned with the current release.

## UI Gallery submissions

Reusable dashboard examples should live under:

```text
/ui-gallery/<card-id>/
```

Each Gallery submission should include:

- `README.md`
- `card.yaml` or `dashboard.yaml`
- `preview.png`

Use [ui-gallery/CONTRIBUTING.md](ui-gallery/CONTRIBUTING.md) and [ui-gallery/reference.txt](ui-gallery/reference.txt) for the required gallery format.

Gallery examples must preserve canonical Humidity Intelligence backend entities/helpers. Do not publish private entity IDs, secrets, addresses, personal data, or screenshots that reveal sensitive home information. Add or update the matching entry in [ui-gallery/README.md](ui-gallery/README.md) when adding a gallery example.

## Privacy and redaction

Before submitting an issue, PR, YAML file, screenshot, or log excerpt, remove:

- Private entity IDs
- Home Assistant tokens
- API keys
- Internal URLs
- Home addresses
- Device IDs
- Personal names or other personal data

Use generic examples such as `sensor.redacted_bedroom_humidity` when needed.

## Coding style

Humidity Intelligence favors deterministic environmental-control logic. Contributions should keep behavior predictable and explainable:

- Prefer explicit decision paths over implicit side effects.
- Preserve reason telemetry so users can understand why a state or action was selected.
- Use safe fallbacks when entities are unavailable or optional configuration is missing.
- Keep runtime behavior stable across Home Assistant restarts.
- Avoid changing dashboard logic or backend semantics as part of unrelated maintenance.

## Documentation expectations

Update `README.md`, docs, services documentation, or UI Gallery README files whenever a change affects setup, entities, services, generated UI, release behavior, or HACS installation. Documentation should be practical, current, and safe to publish.

## Bug reports and review process

Use the GitHub issue forms for bugs, feature requests, configuration help, and UI Gallery submissions. A good bug report includes the Humidity Intelligence version, Home Assistant version, install method, logs, expected behavior, actual behavior, and steps to reproduce.

Pull requests are reviewed for correctness, Home Assistant compatibility, HACS readiness, privacy safety, and documentation quality. The maintainer may ask for a smaller scope, additional testing, or clearer docs before merging.
