Kuehlgeraet Cockpit

Die Integration arbeitet jetzt mit einer eigenen offenen Regel-Engine.
Der aktive Pfad benoetigt kein Home-Assistant-Blueprint mehr.

Wichtige Entitaeten:
- sensor.kuehlgeraet_cockpit_status
- switch.kuehlgeraet_cockpit_regel_engine
- switch.kuehlgeraet_cockpit_simulation
- number.kuehlgeraet_cockpit_guenstig_einschalten_ab
- number.kuehlgeraet_cockpit_guenstig_ausschalten_bei
- number.kuehlgeraet_cockpit_teuer_einschalten_ab
- number.kuehlgeraet_cockpit_teuer_ausschalten_bei
- number.kuehlgeraet_cockpit_mindest_ein_zeit
- number.kuehlgeraet_cockpit_mindest_aus_zeit
- number.kuehlgeraet_cockpit_kompressor_aktiv_ab

Web-Cockpit:
- Sidebar-Pfad: /kuehlgeraet-cockpit
- JavaScript-Modul: custom_components/kuehlgeraet_cockpit/frontend/kuehlgeraet-cockpit-panel.js

Regellogik:
- Ein Ziel kann jede Home-Assistant-Entitaet sein, die homeassistant.turn_on und homeassistant.turn_off akzeptiert.
- Temperatur, Leistung, Strompreis, Preis-Minimum, Preis-Maximum und Guenstig-Fenster sind frei konfigurierbare Entitaeten.
- Der Strompreis verschiebt die Ein- und Ausschaltgrenzen zwischen guenstig und teuer.
- Bei guenstigem Preis wird frueher und tiefer gekuehlt, bei teurem Preis spaeter und weniger aggressiv.
- Mindest-Ein- und Mindest-Aus-Zeiten schuetzen vor zu haeufigem Schalten.
- Leistungsdaten koennen das Ausschalten blockieren, wenn der Kompressor gerade laeuft.
