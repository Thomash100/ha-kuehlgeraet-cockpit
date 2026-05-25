# Kuehlgeraet Cockpit

Kuehlgeraet Cockpit ist eine HACS-installierbare Home-Assistant-Custom-Integration mit offener Regel-Engine und Web-Cockpit.

HACS-Installation:
- Direktlink: https://my.home-assistant.io/redirect/hacs_repository/?owner=Thomash100&repository=ha-kuehlgeraet-cockpit&category=integration
- Custom Repository URL: https://github.com/Thomash100/ha-kuehlgeraet-cockpit
- Kategorie: Integration

Enthalten sind:
- eine reine Python-Regel-Engine fuer Temperatur, Leistung und Strompreis
- ein Home-Assistant-Sidebar-Panel unter `/kuehlgeraet-cockpit`
- echte Entity-Auswahl im Config-Flow, auch fuer mehrere Ziel-Entitaeten
- eindeutig beschriftete und nach Aufgabe gefilterte Auswahllisten
- frei konfigurierbare Ein- und Ausschalt-Dienste
- Home-Assistant-Action-Sequenzen fuer mehrere Dienste pro Richtung
- zusaetzliche Ein-/Ausschalt-Aktionsentitaeten fuer Skripte, Szenen oder Helper mit `turn_on`
- Sensoren fuer Status, Preisfaktor, Schwellen und Messwerte
- Binary-Sensoren fuer Preisfenster, Kompressorstatus und Preisdaten
- Switches fuer Regel-Engine und Simulation
- Number-Entitaeten fuer Live-Anpassung der Regelgrenzen
- eigenes Brand-Icon und Logo fuer Home Assistant ab 2026.3

Die Integration ist nicht auf Shelly begrenzt. Das Ziel kann jede Home-Assistant-Entitaet sein, die `homeassistant.turn_on` und `homeassistant.turn_off` unterstuetzt, oder ueber eigene Dienste und Action-Sequenzen geschaltet werden. Strompreise koennen ueber Preis-Min/Max-Entitaeten, Preisattribute oder eine beliebige Guenstig-Entitaet einfliessen.

Die fruehere Blueprint-Variante ist nicht mehr der aktive Steuerpfad.
