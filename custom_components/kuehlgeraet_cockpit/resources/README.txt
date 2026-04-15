Kuehlgeraet Cockpit exportierte Dateien

Die Integration kann diese Dateien in den Home-Assistant-Konfigurationsordner exportieren:

- /config/blueprints/automation/kuehlgeraet_cockpit/kuehlgeraet_tibber_shelly_kurzfristtrend.yaml
- /config/kuehlgeraet_cockpit/dashboard/kuehlgeraet_status_sensor.yaml
- /config/kuehlgeraet_cockpit/dashboard/kuehlgeraet_cockpit_visual_button_card_sensor.yaml
- /config/kuehlgeraet_cockpit/dashboard/kuehlgeraet_technikpanel_sensor.yaml

Live-Entitaet:
- sensor.kuehlgeraet_cockpit_status

Vom Blueprint verwendeter Dienst:
- kuehlgeraet_cockpit.set_dashboard_status

Dieses Repository kann direkt in HACS als benutzerdefinierte Integration eingebunden werden.