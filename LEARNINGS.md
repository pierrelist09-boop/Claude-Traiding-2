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
