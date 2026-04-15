# Kuehlgeraet Cockpit

Kuehlgeraet Cockpit ist eine ueber HACS installierbare Home-Assistant-Custom-Integration fuer die strompreisbewusste Steuerung von Kuehlschrank und Kuehltruhe mit Tibber, Shelly-Schaltung, leistungsbasierter Kompressorerkennung und sofort nutzbaren Dashboard-Snippets.

Enthalten sind:
- ein Kuehlgeraete-Blueprint fuer Tibber und Shelly mit Kurzfristtrend-Logik
- eine Live-Entitaet: `sensor.kuehlgeraet_cockpit_status`
- exportierbare Dashboard-Dateien fuer Statuskarte, visuelles Cockpit und Technikpanel
- Dienste zum Export der mitgelieferten Ressourcen und zur Aktualisierung des Dashboard-Status aus der Automation

Installationsablauf:
1. Dieses Repository in HACS als benutzerdefinierte Integration hinzufuegen.
2. `Kuehlgeraet Cockpit` installieren.
3. Die Integration in Home Assistant hinzufuegen.
4. Blueprint und Dashboard-Dateien exportieren lassen.
5. Eine Automation aus dem exportierten Kuehlgeraete-Blueprint erstellen.
6. Die exportierten YAML-Dateien aus `/config/kuehlgeraet_cockpit/dashboard/` in Lovelace einbinden.

Die visuellen Cockpit-Karten benoetigen `custom:button-card` aus HACS.