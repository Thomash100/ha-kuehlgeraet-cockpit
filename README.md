# Kuehlgeraet Cockpit

Kuehlgeraet Cockpit is a Home Assistant custom integration for Tibber-aware fridge and freezer automation with Shelly switching, compressor-safe logic, and cockpit-style dashboard snippets.

It packages a complete cooling blueprint, exports dashboard views into the correct Home Assistant folders, and exposes a live status sensor that the blueprint updates on every run.

## Features

- Tibber-aware cooling automation for Shelly relay + power metering
- Temperatur-based control with compressor protection
- Kurzfristtrend logic for the next cheapest hours
- Live dashboard entity: `sensor.kuehlgeraet_cockpit_status`
- Markdown and `custom:button-card` dashboard snippets
- One-click resource export into the Home Assistant config folder

## Repository note

This project folder is intended to become its own repository. HACS works best when one repository ships one integration domain.

## Install

1. Publish this folder as its own GitHub repository, for example `HA-Kuehlgeraet-Cockpit`.
2. Add that repository to HACS as a custom integration.
3. Install `Kuehlgeraet Cockpit`.
4. Restart Home Assistant.
5. Add the `Kuehlgeraet Cockpit` integration.
6. Create an automation from the exported cooling blueprint.
7. Add the exported dashboard snippets from `/config/kuehlgeraet_cockpit/dashboard/` to Lovelace.

The visual cockpit cards use `custom:button-card`, which should be installed through HACS.

## What gets exported

- the cooling blueprint to `/config/blueprints/automation/kuehlgeraet_cockpit/`
- dashboard snippets to `/config/kuehlgeraet_cockpit/dashboard/`
- installation notes to `/config/kuehlgeraet_cockpit/README.txt`

## Dashboard files

| View | File | Purpose |
| --- | --- | --- |
| Markdown status | `kuehlgeraet_status_sensor.yaml` | Lightweight overview without custom cards |
| Visual cockpit | `kuehlgeraet_cockpit_visual_button_card_sensor.yaml` | Frosted single-card cockpit with trend and compressor status |
| Technical panel | `kuehlgeraet_technikpanel_sensor.yaml` | Multi-panel technical dashboard with pricing and cooling logic |

## Services

### `kuehlgeraet_cockpit.install_resources`

Exports the packaged blueprint and dashboard snippets into the Home Assistant config folder.

### `kuehlgeraet_cockpit.set_dashboard_status`

Updates the live cockpit sensor from the automation using a compact JSON payload.

## Files in this project

- `custom_components/kuehlgeraet_cockpit/` contains the integration code
- `custom_components/kuehlgeraet_cockpit/resources/` contains the packaged blueprint and dashboard files

## Notes

- Update the documentation and issue tracker URLs in `manifest.json` if you publish under a different repository name.
- The packaged blueprint is based on the Tibber + Shelly kurzfristtrend fridge control created in this workspace.
