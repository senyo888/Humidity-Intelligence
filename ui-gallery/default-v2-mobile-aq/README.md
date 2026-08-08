# Default V2 Mobile AQ

- Style: mobile-first V2 control surface with air-quality lane active state
- Optimised for: phones and narrow dashboard panels
- Author: @senyo888
- Source template: `custom_components/humidity_intelligence/ui/cards/v2_mobile.yaml`
- Required custom cards: `card-mod`, `button-card`, `mod-card`, `apexcharts-card`

[![Default V2 Mobile AQ preview](preview.png)](preview.png)

## Notes

This example shows the default V2 mobile layout while the air-quality lane is active.
It demonstrates the compact badge row, Current Air Control panel, lane chips, and the
backend-owned plain-language reason headline and ordered explanation used by the generated
V2 mobile card.

The YAML keeps ventilation and humidifier chips in one horizontally scrollable
Current Air Control row. The preview predates beta.7 and is not beta.7 playback
evidence.

The YAML is copied from the canonical generated card template and should be treated as an example artifact. In a real installation, prefer the card YAML exported by `humidity_intelligence.dump_cards` so placeholders match your generated entities.

## Files

- [Preview](preview.png)
- [Card YAML](card.yaml)
