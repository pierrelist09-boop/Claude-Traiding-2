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
Das Projekt **Claude-1** im Bot-Panel (autrionex.com/claude1) ist seit 2026-11-07 der ZEC-Vorwärtstest; der frühere Claude-1 (Trading-Konto, Limits, Live-Anbindung, Trendfolge E) wurde entfernt (Git-Tag `claude1-alt-2026-11-07` im Bot-Repo). `app/claude1/zec.py` holt alle 20 s bei Bedarf öffentliche ZEC-Kerzen (5m/15m) und rechnet 16 virtuelle Konten à 1.000 $ weiter (nach dem Aussortieren der Verlierer; die übrigen 24 stehen im Archiv `core.ARCHIVE`) (2 % Risiko je Trade, Hebel bis 10): b20_5m, f_5m, f_15m, p_15m, b20_15m und die zweite Welle dc55_1h, dc100_4h, st_15m, st_1h, rsi2_5m, rsi2_15m, sq_15m, mom_5m, mom_15m, vwap_15m sowie die dritte Welle a4_15m_dc, a4_15m_pb, a1_5m_dc, a4_1h_st, dc50_4h, dc75_4h, dc150_4h, st_4h, ema_4h, adx_15m und die vierte Welle (nur 4h) dcL_100_4h, dcS_100_4h, dc100_t3_4h, dc100_t7_4h, dc100_d1_4h, pb_4h, gc_4h, dc30_4h, tsm120_4h, sq_4h (Beschreibung in `zecfast/core.py`, STRATS; Mehr-Zeitrahmen-Filter über `NEEDS`), dazu die Profit-Auswahl x5_ema_4h, x5_tsm120_4h, x5_st_1h, x5_pb_4h, x5_dcL_100_4h mit 5 % Risiko. Eigene Tabellen `zec_acct`/`zec_trades`, keine Orders, keine Börsenanbindung außer dem öffentlichen Kerzenabruf. Die Seite zeigt Konten mit Kurve, offene Positionen und letzte Trades und aktualisiert sich selbst; Kennzahlen auch unter `/claude1/api/state` (Token, nur lokal).

## Verbesserungsschleife
1. `tools/zec_review.py` (im Bot-Repo) liest die Konten: Urteil erst ab 30 Trades je Konto (Ø R, Standardfehler, Profit-Faktor, long/short getrennt, Rückgang, Ausstiegsgründe).
2. Eine Änderung ist immer eine NEUE Variante mit eigenem Konto, vorab festgelegt und erst im Backtest (`research/zec_test.py`) geprüft; laufende Konten werden nie verändert. Schlechte Varianten werden abgeschaltet, gute weiter beobachtet.
3. Erst wenn ein Konto über genug Trades einen Vorteil nach Kosten zeigt, kommt überhaupt die Frage nach echtem Geld auf; das entscheidet nur der Besitzer.
