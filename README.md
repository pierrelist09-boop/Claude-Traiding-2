# Claude-Traiding-2: schnelles ZEC-Trading (Paper, Hebel 10)

Ziel des Besitzers: Ein Claude-Agent handelt ZEC auf Hyperliquid ständig schnell, long und short, mit Hebel 10 (das ist bei ZEC der von Hyperliquid erlaubte Höchstwert), und wird fortlaufend verbessert. Erst Paper, Echtgeld nur nach Freigabe des Besitzers im Panel.

## Stand (2026-11-07)
Machbarkeitstest (`research/zec_test.py`, Ergebnis `research/ergebnis_zec_test.md`): **keine der 10 getesteten schnellen Varianten hat nach Kosten einen Vorteil** (Validierung und Test gleichzeitig im Plus bei mindestens 30 Test-Trades: 0 von 10). Haupthindernis sind die Kosten: eine Rundreise kostet 0,15 % des Positionswerts, bei Hebel 10 sind das **1,5 % des eingesetzten Geldes je Trade**, ein 5m-Kerzenschritt bewegt ZEC im Schnitt nur 0,48 %.

## Aufbau
- `zecfast/` Datenabruf (Hyperliquid, öffentlich) und Indikatoren.
- `research/` Tests mit Training/Validierung/Test, Kosten und Hebel.
- `LEARNINGS.md` Messprotokoll: nur Gemessenes, jede neue Idee wird vorab festgelegt und einmal getestet.

## Geplante Architektur (noch nicht gebaut)
1. **Schnelle Regelmaschine** im Claude-1-Projekt auf dem Server (läuft im Bot-Prozess, entscheidet in Sekunden). Ein Sprachmodell in der Schleife wäre zu langsam und zu teuer.
2. **Claude-Agent als Aufseher** in festen Abständen: wertet das Handelsprotokoll aus, schlägt Regeländerungen vor, jede Änderung nur nach Test auf den Daten.
3. **Vorwärtstest zuerst**: Kandidaten laufen virtuell parallel und werden live nach Kosten gemessen, bevor eine davon Konto-Geld bewegt.
