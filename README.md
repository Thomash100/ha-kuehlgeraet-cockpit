# Kuehlgeraet Cockpit

Kuehlgeraet Cockpit ist eine Home-Assistant-Custom-Integration fuer die strompreisbewusste Steuerung von Kuehlschrank und Kuehltruhe mit Tibber, Shelly-Schaltrelais und Dashboard-Snippets im Cockpit-Stil.

Die Integration bringt ein komplettes Kuehlgeraete-Blueprint mit, exportiert Dashboard-Dateien in die passenden Home-Assistant-Ordner und stellt den Live-Statussensor `sensor.kuehlgeraet_cockpit_status` bereit, den das Blueprint bei jedem Lauf aktualisiert.

## Funktionen

- Tibber-basierte Kuehlgeraete-Automation fuer Shelly-Relais mit Leistungsmessung
- Temperaturbasierte Steuerung mit Kompressorschutz
- Kurzfristtrend-Logik fuer die naechsten guenstigen Stunden
- Live-Entitaet: `sensor.kuehlgeraet_cockpit_status`
- Dashboard-Snippets fuer Markdown und `custom:button-card`
- Ein-Klick-Export in den Home-Assistant-Konfigurationsordner

## Installation

1. Dieses Repository in HACS als benutzerdefinierte Integration hinzufuegen.
2. `Kuehlgeraet Cockpit` installieren.
3. Home Assistant neu starten.
4. Die Integration `Kuehlgeraet Cockpit` hinzufuegen.
5. Eine Automation aus dem exportierten Kuehlgeraete-Blueprint erstellen.
6. Die exportierten Dashboard-Dateien aus `/config/kuehlgeraet_cockpit/dashboard/` in Lovelace einbinden.

Die visuellen Cockpit-Karten verwenden `custom:button-card`. Diese Karte sollte ueber HACS installiert sein.

## Exportierte Dateien

- das Kuehlgeraete-Blueprint nach `/config/blueprints/automation/kuehlgeraet_cockpit/`
- Dashboard-Dateien nach `/config/kuehlgeraet_cockpit/dashboard/`
- Installationshinweise nach `/config/kuehlgeraet_cockpit/README.txt`

## Dashboard-Dateien

| Ansicht | Datei | Zweck |
| --- | --- | --- |
| Statuskarte | `kuehlgeraet_status_sensor.yaml` | Schlanke Uebersicht ohne Custom Cards |
| Visuelles Cockpit | `kuehlgeraet_cockpit_visual_button_card_sensor.yaml` | Kompakte Cockpit-Karte mit Trend- und Kompressorstatus |
| Technikpanel | `kuehlgeraet_technikpanel_sensor.yaml` | Technisches Dashboard mit Preis- und Kuehllogik |

## Dienste

### `kuehlgeraet_cockpit.install_resources`

Exportiert Blueprint und Dashboard-Dateien in den Home-Assistant-Konfigurationsordner.

### `kuehlgeraet_cockpit.set_dashboard_status`

Aktualisiert den Live-Statussensor aus der Automation mit einer kompakten JSON-Nutzlast.

## Projektstruktur

- `custom_components/kuehlgeraet_cockpit/` enthaelt den Integrationscode
- `custom_components/kuehlgeraet_cockpit/resources/` enthaelt Blueprint und Dashboard-Dateien

## Hinweise

- Passe die Links in `manifest.json` an, falls du das Projekt unter einem anderen Repository-Namen veroeffentlichst.
- Das mitgelieferte Blueprint basiert auf der hier entwickelten Tibber-, Shelly- und Kurzfristtrend-Logik fuer Kuehlgeraete.