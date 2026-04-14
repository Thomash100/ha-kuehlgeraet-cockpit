Kuehlgeraet Cockpit exported files

The integration can export these files into the Home Assistant config folder:

- /config/blueprints/automation/kuehlgeraet_cockpit/kuehlgeraet_tibber_shelly_kurzfristtrend.yaml
- /config/kuehlgeraet_cockpit/dashboard/kuehlgeraet_status_sensor.yaml
- /config/kuehlgeraet_cockpit/dashboard/kuehlgeraet_cockpit_visual_button_card_sensor.yaml
- /config/kuehlgeraet_cockpit/dashboard/kuehlgeraet_technikpanel_sensor.yaml

Live entity:
- sensor.kuehlgeraet_cockpit_status

Service used by the blueprint:
- kuehlgeraet_cockpit.set_dashboard_status

Publish this folder as its own repository before adding it to HACS.
