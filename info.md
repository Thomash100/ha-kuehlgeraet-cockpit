# Kuehlgeraet Cockpit

Kuehlgeraet Cockpit is a HACS-installable Home Assistant custom integration for Tibber-aware fridge and freezer control with Shelly switching, power-based compressor protection, and ready-to-use dashboard snippets.

What it includes:
- a Tibber + Shelly cooling blueprint with kurzfristiger price trend logic
- a live entity: `sensor.kuehlgeraet_cockpit_status`
- exported dashboard snippets for markdown, visual cockpit, and technical panel views
- services to export packaged resources and update the dashboard status from the automation

Install flow:
1. Publish this folder as its own GitHub repository.
2. Add that repository to HACS as a custom integration.
3. Install `Kuehlgeraet Cockpit`.
4. Add the integration in Home Assistant.
5. Let it export the blueprint and dashboard snippets.
6. Create an automation from the exported cooling blueprint.
7. Add the exported dashboard YAML snippets from `/config/kuehlgeraet_cockpit/dashboard/` to Lovelace.

The visual cards require `custom:button-card` from HACS.
