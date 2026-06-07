# Repository-Konsolidierung

Stand: 2026-06-08

## Hauptkopie

Dieses Repository ist die aktive Hauptkopie fuer das Home-Assistant-Kuehlgeraet-Cockpit:

- Repository: `Thomash100/ha-kuehlgeraet-cockpit`
- Branch: `main`
- HEAD: `fbbb136`
- Lokaler Status: sauber

## Abgrenzung

- Growatt-Daten, Wechselrichterlogik und Zero-Export gehoeren in `Thomash100/Growatt_Dat`.
- Aquarium-/weitere Home-Assistant-Integrationen werden erst nach geklaertem Hauptrepository angebunden.
- Keine Doppelpflege in lokalen Kopien.

## Sicherheitsregeln

- Keine Home-Assistant-Secrets, MQTT-Zugangsdaten, Tokens, `.env`, Datenbankdateien oder Logs committen.
- Lokale Altordner nur als Archiv verwenden und nicht parallel weiterentwickeln.

## Naechste Schritte

- Offene Altkopien suchen und bei Bedarf als Archiv kennzeichnen.
- Gemeinsame Energieplattform-Roadmap mit Growatt, EVCC und Home Assistant abstimmen.
