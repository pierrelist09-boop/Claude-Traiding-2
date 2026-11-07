# Messprotokoll

## 2026-11-07: Machbarkeit schneller ZEC-Strategien
Daten: ZEC-Perp, 5m (17 Tage), 15m (52 Tage). Kosten je Seite 0,045 % Gebühr + 0,03 % Slippage. 5 Strategien (Ausbruch 20/40 mit Volumen, Umkehr bei RSI/Bollinger-Extrem, Pullback im Trend, Dauer-Wechsel EMA9/21), 10 Versuche, Training 50 % / Validierung 25 % / Test 25 %.

- Keine Variante hat Validierung **und** Test im Plus. Die beiden positiven Testwerte (5m-Ausbruch +0,15 R und +0,10 R) folgen auf negatives Training (−0,41 R) und Validierung (−0,33 R): Zufall, kein Befund.
- „Immer long oder short“ (EMA-Wechsel) verliert: Test −0,17 R (5m) bzw. −0,13 R (15m); mehr Trades bedeuten nur mehr Kosten.
- Kosten: 5m-ATR ist 0,48 % des Kurses, eine Rundreise 0,31 ATR; bei Hebel 10 ist jede Rundreise 1,5 % des Margin-Geldes. Dauerhaftes Gewinnen braucht also einen Vorteil von mehr als etwa 0,1 bis 0,2 R je Trade vor Kosten, den die Daten nicht zeigen.
- Vorbehalte: nur 17 bzw. 52 Tage, ein Marktumfeld; weitere Ideen brauchen längere Daten (1h: 208 Tage) oder einen Vorwärtstest.

## 2026-11-07 (später): Fehler im ersten Wechsel-Test, Live-Maschine gebaut
- **Fehler behoben:** Die „Dauer-Wechsel“-Strategie (EMA9/21) wechselte nach einem Kreuz nicht sofort in die Gegenrichtung, sondern erst am nächsten Kreuz, war also nicht „immer im Markt“. Korrigiert (Wechsel-Ausstieg prüft an derselben Kerze sofort das Gegensignal). Neue Zahlen: **5m** Training −0,35 R, Validierung −0,38, Test −0,26 R (n=57, −27 % Konto, 14 Trades/Tag): klar negativ. **15m** Training −0,23 R, **Validierung +0,56 R (n=35), Test +0,10 R (n=44, PF 1,18, +7 %)**: erfüllt formal die Hürden (beide positiv, ≥ 30 Test-Trades), aber Training negativ, 13 Tage Test, eine von 10 Versuchen: nur ein Kandidat für den Vorwärtstest, kein Befund.
- Konsequenz: `f_15m` zum Vorwärtstest hinzugefügt (5 virtuelle Konten). `zecfast/core.py` + `tests/test_replay.py` (Live-Maschine = Backtest, Trade für Trade).
- Kosten bleiben das Hauptproblem: Rundreise 0,15 %, bei Hebel 10 = 1,5 % des Margin-Geldes je Trade.

## 2026-11-07 (später): zweite Welle, 10 weitere Strategien (`research/zec_more.py`, Ergebnis `research/ergebnis_zec_more.md`)
Auf Wunsch des Besitzers weitere Ideen vorab festgelegt und als eigene Konten unter die laufenden gesetzt (insgesamt 15 virtuelle Konten): Trendfolge 1h (Donchian 55) und 4h (Donchian 100, Stop 4 / Trail 5 ATR), Supertrend(10,3) auf 15m und 1h, RSI(2)-Rücksetzer im Trend auf 5m und 15m, Bollinger-Verengung mit Ausbruch, Momentum-Kerze mit Volumen (Scalp 1,5 R) auf 5m und 15m, VWAP-Rückkehr. Gleiche Prüfung (50/25/25, Kosten, Hebel 10, 2 % Risiko), 15 Versuche insgesamt.
- **Formal Kandidat (Validierung und Test > 0, >= 30 Test-Trades):** nur `f_15m` (+0,10 R im Test, siehe oben).
- **Positiv, aber zu wenig Test-Trades:** `dc100_4h` (27 Trades in 567 Tagen: +1,15 / +0,53 / +1,34 R in Training/Validierung/Test, Test +18 % bei 2 % Rückgang; ZEC war in dieser Zeit in einem sehr starken Aufwärtstrend, also ein Marktumfeld), `st_1h` (Training +0,61, Validierung +0,65, Test +0,01 R), `sq_15m` (nur 4 Test-Trades).
- **Kein Vorteil:** `dc55_1h` (Test −0,13), `st_15m`, beide RSI(2)-Varianten (alle Abschnitte negativ), beide Momentum-Scalps, `vwap_15m` (Validierung −0,51).
- Bestätigt erneut das Muster aus dem ersten Repo: Langsame Trendfolge (4h) zeigt als Einziges stabil Plus, schnelle Muster verlieren an Kosten. Mit 15 Versuchen sind einzelne Zufallstreffer zu erwarten; entscheidend ist der Vorwärtstest.
- Technik: `MAX_STOP_FRAC` auf 50 % gelockert (bei 2 % Risiko liegt die Liquidation 50 Stop-Abstände entfernt, die 8-%-Grenze hätte 4h-Strategien grundlos verworfen). Der Replay-Test (`tests/test_replay.py`) bestätigt für alle 15 Strategien Trade für Trade dieselben Ergebnisse wie die Backtest-Schleife.

## 2026-11-07 (abends): dritte Welle, Mehr-Zeitrahmen und 4h-Trendfolge-Familie (25 Konten)
Neu im Kern: `link()` hängt einen höheren Zeitrahmen kausal an (nur schon geschlossene Kerzen), `NEEDS` nennt die Filter-Zeitrahmen. Zehn weitere vorab festgelegte Versuche, gleiche Prüfung (siehe `research/ergebnis_zec_more.md`).
- **Trendgefilterte Einstiege auf kleinem Zeitrahmen helfen nicht:** 4h-Trend + 15m-Ausbruch Test −0,25 R, 4h-Trend + 15m-Pullback −0,32 R, 1h-Trend + 5m-Ausbruch −0,16 R, ADX-Filter −0,16 R. Der Filter macht die Kosten-Struktur nicht besser: zu viele Trades mit zu kleinem Abstand.
- **Langsame 4h-Trendfolge: in allen drei Abschnitten positiv, über die ganze Parameterfamilie.** Donchian 50/75/100/150 (Stop 4, Trail 5 ATR): Training/Validierung/Test Ø R 50: +0,44/+0,09/+0,91, 75: +0,82/+0,26/+1,15, 100: +1,15/+0,53/+1,34, 150: +1,43/+0,32/+2,55; Test-Konto +17 bis +20 % bei 2 bis 6 % größtem Rückgang. Aber nur 21 bis 45 Trades in 567 Tagen je Variante (die Varianten teilen sich viele Trades, sind also keine unabhängigen Belege) und ZEC lief in diesem Zeitraum in einen extremen Aufwärtstrend (ein Marktumfeld). Deckt sich mit den Messungen im ersten Repo (Trendfolge E über 10 Coins: +0,19 R je Trade, kleiner), dort jedoch mit viel weniger Ausschlag: die +1 R auf ZEC sind nicht zu erwarten.
- EMA20/50-Kreuz 4h: Training +4,35, Validierung −0,22, Test +3,57 R (einzelne riesige Trend-Gewinne, Validierung negativ): kein Befund. Supertrend 4h und alle schnellen Varianten: kein Vorteil.
- Konsequenz fürs Vorwärts-Urteil: Bei 25 Konten gilt in `tools/zec_review.py` Bonferroni (Ø R minus 2,9 Standardfehler > 0), sonst werden Zufallstreffer gefunden. Das Problem der langsamen Konten: `dc100_4h` bringt etwa einen Trade alle 3 Wochen, 30 Trades dauern über ein Jahr. Schneller prüfen lässt sich nur mit mehr Coins (dieselbe Regel auf BTC/ETH/SOL ...) oder weiter Rückblick auf mehr Daten.

## 2026-11-07 (spät): vierte Welle, zehn weitere 4h-Mechanismen nur auf ZEC (35 Konten)
Auf Wunsch des Besitzers (erstmal nur ZEC, mehr 4h) zehn vorab festgelegte, bewusst verschiedene Mechanismen; gleiche Prüfung (`research/ergebnis_zec_more.md`). Kein Versuch hat >= 30 Test-Trades, formal ist also keiner ein Kandidat; aber:
- **Der ganze Vorteil liegt auf der Long-Seite.** Ausbruch 100 nur Long: Ø R +2,14 / +1,06 / +3,94 (7/4/3 Trades); nur Short: −0,25 / 0,00 / −0,61. Das ist ein Marktumfeld-Effekt (ZEC im extremen Aufwärtstrend), keine Fähigkeit: Wer in diesem Zeitraum long gehalten hat, hat gewonnen. Sollte ZEC drehen, ist die Long-Verzerrung der Verlierer. Der Vorwärtstest wird zeigen, was bei Seitwärts/Abwärts passiert.
- **Zeitreihen-Momentum 4h (20-Tage-Rendite, immer im Markt):** +2,83 / +0,03 / +1,15 R (21/32/22 Trades), Test +47 % bei 4 % Rückgang: der Kandidat mit den meisten Trades unter den Positiven.
- **Pullback am EMA20 im 4h-Trend:** +0,93 / +0,28 / +1,58 R (22/15/12), Test +35 %; **Ausbruch 30:** −0,05 / +0,24 / +0,25 R (44/24/22), mehr Trades, kleiner Vorteil. Weiter Trail (7 ATR) besser als enger (3 ATR: +0,07 im Test), Tagestrend-Filter ändert wenig.
- Kein Vorteil: Golden Cross 50/200 (nur 14 Trades, Test −0,83), Squeeze 4h, Short-only.
- Vorbehalt unverändert: kleine Stichproben, korrelierte Varianten, ein Marktumfeld, 35 Versuche gesamt (Bonferroni im Review-Tool: Ø R minus 3,0 Standardfehler > 0).
