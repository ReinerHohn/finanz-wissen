# 💶 Finanz-Wissen

Eine durchsuchbare, verständliche Wissensbasis rund um Geldanlage – mit Fokus auf ETFs und sicheres, langfristiges Investieren. Gleiches Baumuster wie meine anderen Katalog-Repos: JSON-Karten → `build.py` → eine self-contained `dashboard.html` (nur Python-Standardbibliothek, keine externen Abhängigkeiten).

> **Bildung, keine Anlageberatung.** Diese Sammlung erklärt, wie Dinge funktionieren. Sie ist keine Anlage-, Steuer- oder Rechtsberatung. Investieren kann zu Verlusten bis zum Totalverlust führen.

## Aufbau

- `wissen/*.json` – eine Datei pro Wissenskarte (Thema).
- `build.py` – baut daraus `dashboard.html` (durchsuchbar, offline nutzbar) und `KATALOG.md`.
- `dashboard.html` – im Browser öffnen, suchen, Karten aufklappen.
- `KATALOG.md` – dieselben Inhalte als Text zum Nachlesen/Diffen.

## Nutzen

```bash
python3 build.py            # baut dashboard.html + KATALOG.md
python3 build.py --check    # nur validieren (nichts schreiben)
```

Dann `dashboard.html` im Browser öffnen.

## Eine Karte anlegen

Neue Datei `wissen/<id>.json`. Der Dateiname (ohne `.json`) muss der `id` entsprechen.

Pflichtfelder: `id`, `name`, `category`, `summary`, `kernidee`.
Optional: `aka`, `evidence_level` (A/B/C), `tags`, `deep_dive`, `key_facts` (`label`/`value`/`source`), `misconceptions`, `related` (ids), `sources` (`title`/`url`).

`evidence_level`: **A** = breiter Konsens / gut belegt, **B** = solide, **C** = Faustregel / kontextabhängig.

## Themen v1

Grundlagen (Was ist ein ETF, Gewichtung, Rebalancing, thesaurierend/ausschüttend), Risiko & Sicherheit (Diversifikation vs. Marktrisiko, langfristige Sicherheit), Kosten (TER, aktiv vs. passiv), Steuern DE (Abgeltungsteuer/Vorabpauschale), Praxis (Notgroschen, Sparplan vs. Einmalanlage, Welt-ETF auswählen).

## Leitfragen, die diese Sammlung beantwortet

- Wenn eine Firma im Index abstürzt – behält der ETF die Aktien oder verkauft er? → `marktkapitalisierung-gewichtung`, `index-aufnahme-und-ausschluss`
- Reagiert der ETF auf Umsatz/Wert einer Firma? → `marktkapitalisierung-gewichtung`
- Sind ETFs langfristig „sicher"? → `sind-etfs-sicher`, `diversifikation-vs-marktrisiko`
- Wie lege ich lange herumliegendes Geld sicher an? → `notgroschen-zuerst`, `sparplan-vs-einmalanlage`, `welt-etf-auswaehlen`
