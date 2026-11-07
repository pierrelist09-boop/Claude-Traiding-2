# Claude-Traiding-2: schnelles ZEC-Trading (Paper, Hebel 10)

Ziel des Besitzers: Ein Claude-Agent handelt ZEC auf Hyperliquid ständig schnell, long und short, mit Hebel 10 (das ist bei ZEC der von Hyperliquid erlaubte Höchstwert), und wird fortlaufend verbessert. Erst Paper, Echtgeld nur nach Freigabe des Besitzers im Panel.

## Stand (2026-11-07)
Machbarkeitstest (`research/zec_test.py`, Ergebnis `research/ergebnis_zec_test.md`): **keine der 10 getesteten schnellen Varianten hat nach Kosten einen Vorteil** (Validierung und Test gleichzeitig im Plus bei mindestens 30 Test-Trades: 0 von 10). Haupthindernis sind die Kosten: eine Rundreise kostet 0,15 % des Positionswerts, bei Hebel 10 sind das **1,5 % des eingesetzten Geldes je Trade**, ein 5m-Kerzenschritt bewegt ZEC im Schnitt nur 0,48 %.

## Aufbau
- `zecfast/core.py` **Kern**: Indikatoren, 5 Strategien, virtuelles Paper-Konto (Kerze für Kerze). Reines Python, keine Börsenanbindung, sendet nie Orders. Dieselbe Datei läuft im Backtest und live im Bot (Kopie `app/claude1/zeccore.py` im Bot-Repo, bei Änderungen beide ersetzen).
- `zecfast/data.py` Datenabruf (Hyperliquid, öffentlich), eigener Cache `.cache/` (Dateiname enthält n).
- `research/zec_test.py` Backtest mit Training/Validierung/Test, Kosten und Hebel 10. `tests/test_replay.py` beweist, dass die Live-Maschine auf der Historie exakt dieselben Trades liefert wie der Backtest.
- `LEARNINGS.md` Messprotokoll.

## Live (nur Paper)
Das Projekt **Claude-1** im Bot-Panel (autrionex.com/claude1) ist seit 2026-11-07 der ZEC-Vorwärtstest; der frühere Claude-1 (Trading-Konto, Limits, Live-Anbindung, Trendfolge E) wurde entfernt (Git-Tag `claude1-alt-2026-11-07` im Bot-Repo). `app/claude1/zec.py` holt alle 20 s bei Bedarf öffentliche ZEC-Kerzen (5m/15m) und rechnet 5 virtuelle Konten à 1.000 $ weiter (b20_5m, f_5m, f_15m, p_15m, b20_15m; 2 % Risiko je Trade, Hebel bis 10). Eigene Tabellen `zec_acct`/`zec_trades`, keine Orders, keine Börsenanbindung außer dem öffentlichen Kerzenabruf. Die Seite zeigt Konten mit Kurve, offene Positionen und letzte Trades und aktualisiert sich selbst; Kennzahlen auch unter `/claude1/api/state` (Token, nur lokal).

## Verbesserungsschleife
1. `tools/zec_review.py` (im Bot-Repo) liest die Konten: Urteil erst ab 30 Trades je Konto (Ø R, Standardfehler, Profit-Faktor, long/short getrennt, Rückgang, Ausstiegsgründe).
2. Eine Änderung ist immer eine NEUE Variante mit eigenem Konto, vorab festgelegt und erst im Backtest (`research/zec_test.py`) geprüft; laufende Konten werden nie verändert. Schlechte Varianten werden abgeschaltet, gute weiter beobachtet.
3. Erst wenn ein Konto über genug Trades einen Vorteil nach Kosten zeigt, kommt überhaupt die Frage nach echtem Geld auf; das entscheidet nur der Besitzer.
