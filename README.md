# Kuehlgeraet Cockpit

Kuehlgeraet Cockpit ist eine Home-Assistant-Custom-Integration mit offener Regel-Engine und eigener Webapp als Cockpit. Die Integration ist nicht auf Shelly begrenzt: Das Ziel kann jede Home-Assistant-Entitaet sein, die `homeassistant.turn_on` und `homeassistant.turn_off` akzeptiert.

Der aktive Pfad arbeitet ohne Blueprint. Temperatur, Leistung, Strompreis, Preis-Minimum, Preis-Maximum und ein optionales Guenstig-Fenster werden als normale Home-Assistant-Entitaeten konfiguriert. Darauf berechnet die Engine eine Schaltentscheidung und zeigt sie im Sidebar-Panel `/kuehlgeraet-cockpit` an.

## Funktionen

- echte Entity-Auswahl im Config-Flow statt Textfelder
- eindeutig beschriftete und nach Aufgabe gefilterte Auswahllisten
- mehrere Ziel-Entitaeten statt Shelly-Festlegung
- konfigurierbare Ein- und Ausschalt-Dienste
- komplette Home-Assistant-Action-Sequenzen fuer mehrere Dienste pro Richtung
- zusaetzliche Ein-/Ausschalt-Aktionsentitaeten fuer Skripte, Szenen oder Helper mit `turn_on`
- Strompreis wirkt direkt auf die Ein- und Ausschaltgrenzen
- Preisbewertung ueber Preis-Min/Max oder eine beliebige Guenstig-Entitaet
- temperaturbasierte Hysterese mit guenstig/teuer-Grenzen
- Mindest-Ein- und Mindest-Aus-Zeiten
- Kompressorschutz ueber optionale Leistungs-Entitaet
- Simulationsmodus ohne Schaltbefehle
- Web-Cockpit als Home-Assistant-Sidebar-Panel
- eigenes Brand-Icon und Logo fuer Home Assistant ab 2026.3
- Sensoren, Binary-Sensoren, Switches und Number-Entitaeten fuer offene Weiterverarbeitung

## Preislogik

Die Engine berechnet eine Preisposition von `0.0` guenstig bis `1.0` teuer.

- Mit Preis-, Min- und Max-Wert: `(aktueller Preis - Minimum) / (Maximum - Minimum)`
- Mit Guenstig-Entitaet: `0.0`, wenn guenstig, sonst `1.0`
- Ohne gueltige Preisdaten: `0.5` als neutraler Fallback

Diese Position verschiebt die Temperaturgrenzen kontinuierlich:

- guenstig: frueher einschalten und tiefer kuehlen
- teuer: spaeter einschalten und weniger aggressiv kuehlen

## Installation

[![In HACS hinzufuegen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Thomash100&repository=ha-kuehlgeraet-cockpit&category=integration)

HACS Custom Repository URL: `https://github.com/Thomash100/ha-kuehlgeraet-cockpit`

1. Link oben oeffnen oder in HACS `Benutzerdefinierte Repositories` waehlen.
2. Repository-URL eintragen und Kategorie `Integration` auswaehlen.
3. `Kuehlgeraet Cockpit` in HACS installieren.
4. Home Assistant neu starten.
5. Die Integration `Kuehlgeraet Cockpit` hinzufuegen.
6. Schaltziele, Temperaturquelle und optionale Preis-/Leistungsquellen auswaehlen.
7. Das Cockpit in der Sidebar unter `/kuehlgeraet-cockpit` oeffnen.

## Ziele und Dienste

Die Ziel-Entitaeten werden im Home-Assistant-Dropdown gewaehlt. Die erste Ziel-Entitaet dient als primaerer Status fuer Ein/Aus-Zustand und Mindestlaufzeiten; geschaltet werden alle ausgewaehlten Ziel-Entitaeten.

Die Auswahlfelder sind bewusst nach Aufgabe benannt und gefiltert:

- Schaltziele: typische schaltbare Entitaeten wie `switch.*`, `input_boolean.*`, `light.*`, `fan.*`, `climate.*`, `cover.*` oder `script.*`
- Messquellen: numerische `sensor.*`, `number.*` oder `input_number.*`
- Guenstig-Fenster: `binary_sensor.*`, `input_boolean.*` oder `switch.*`
- Zusatz-Aktionsentitaeten: `script.*`, `scene.*`, `automation.*`, `input_boolean.*`, `switch.*` oder `light.*`

Falls ein Sonderfall nicht in einer gefilterten Liste auftaucht, kann er ueber die Action-Sequenz mit einem eigenen Home-Assistant-Dienst angebunden werden.

Standarddienste:

- Einschalten: `homeassistant.turn_on`
- Ausschalten: `homeassistant.turn_off`

Diese Dienste koennen in den Optionen geaendert werden, z. B. auf `switch.turn_on` / `switch.turn_off`. Fuer komplexere Ablaeufe koennen pro Richtung Home-Assistant-Action-Sequenzen konfiguriert werden. Damit lassen sich mehrere Dienste, Szenen, Scripts oder andere Automation-Aktionen nacheinander ausfuehren.

Zusaetzlich gibt es einfache Ein- und Ausschalt-Aktionsentitaeten, etwa `script.*`, `scene.*` oder Helper mit `turn_on`. Diese werden bei der jeweiligen Entscheidung per `homeassistant.turn_on` ausgeloest.

## Entitaeten

- `sensor.kuehlgeraet_cockpit_status`
- `sensor.kuehlgeraet_cockpit_temperatur`
- `sensor.kuehlgeraet_cockpit_leistung`
- `sensor.kuehlgeraet_cockpit_strompreis`
- `sensor.kuehlgeraet_cockpit_preisfaktor`
- `sensor.kuehlgeraet_cockpit_einschaltgrenze`
- `sensor.kuehlgeraet_cockpit_ausschaltgrenze`
- `binary_sensor.kuehlgeraet_cockpit_preisfenster_guenstig`
- `binary_sensor.kuehlgeraet_cockpit_kompressor_laeuft`
- `binary_sensor.kuehlgeraet_cockpit_preisdaten_aktiv`
- `switch.kuehlgeraet_cockpit_regel_engine`
- `switch.kuehlgeraet_cockpit_simulation`
- mehrere `number.*`-Entitaeten fuer Temperaturgrenzen, Mindestzeiten und Kompressorschwelle

## Dienste

### `kuehlgeraet_cockpit.evaluate_now`

Bewertet die Regeln sofort. Mit `apply: true` wird eine geplante Aktion ueber den konfigurierten Dienst, optionale Aktionsentitaeten und optionale Action-Sequenzen ausgefuehrt.

### `kuehlgeraet_cockpit.set_enabled`

Aktiviert oder deaktiviert die Regel-Engine.

### `kuehlgeraet_cockpit.set_simulation`

Aktiviert oder deaktiviert den Simulationsmodus.

### `kuehlgeraet_cockpit.set_setting`

Setzt eine numerische Laufzeit-Einstellung wie `cheap_on_temp`, `expensive_off_temp`, `min_on_seconds` oder `compressor_running_watts`.

## Projektstruktur

- `engine.py`: reine Regel-Engine ohne Home-Assistant-Abhaengigkeit
- `runtime.py`: liest Home-Assistant-Zustaende, verfolgt Aenderungen und fuehrt Aktionen aus
- `frontend/`: Web-Cockpit als Custom Panel
- `brand/`: lokales Integrations-Icon und Logo fuer Home Assistant
- `sensor.py`, `binary_sensor.py`, `switch.py`, `number.py`: offene HA-Entitaeten fuer Dashboard und Automationen

## Hinweis

Die fruehere Blueprint-Idee ist nicht mehr der aktive Steuerpfad. Dashboard-YAML-Dateien im Ressourcenordner sind nur noch optionale/legacy Snippets; die Bedienung laeuft ueber das integrierte Web-Cockpit.

<!-- SYSTEMMEDIA_LEGAL_START -->
## Rechtliche Hinweise

- Impressum: https://systemmedia.de/impressum/
- Datenschutz / DSGVO-Hinweise: https://systemmedia.de/datenschutz/
- Nutzungsbedingungen und Haftungsausschluss: https://systemmedia.de/nutzungsbedingungen/

Dieses Repository enthaelt, sofern nicht ausdruecklich anders gekennzeichnet, Test-, Entwicklungs-, Demonstrations- oder Evaluierungsinhalte. Nutzung auf eigene Verantwortung.

Soweit eine `LICENSE`-Datei vorhanden ist, gelten die dort genannten Lizenzbedingungen fuer die eingeraeumten Nutzungsrechte. Ergaenzend gelten die Status-, Gewaehrleistungs- und Haftungshinweise in `LEGAL.md`.
<!-- SYSTEMMEDIA_LEGAL_END -->
