# Messprotokoll

## 2026-11-07: Machbarkeit schneller ZEC-Strategien
Daten: ZEC-Perp, 5m (17 Tage), 15m (52 Tage). Kosten je Seite 0,045 % Gebühr + 0,03 % Slippage. 5 Strategien (Ausbruch 20/40 mit Volumen, Umkehr bei RSI/Bollinger-Extrem, Pullback im Trend, Dauer-Wechsel EMA9/21), 10 Versuche, Training 50 % / Validierung 25 % / Test 25 %.

- Keine Variante hat Validierung **und** Test im Plus. Die beiden positiven Testwerte (5m-Ausbruch +0,15 R und +0,10 R) folgen auf negatives Training (−0,41 R) und Validierung (−0,33 R): Zufall, kein Befund.
- „Immer long oder short“ (EMA-Wechsel) verliert: Test −0,17 R (5m) bzw. −0,13 R (15m); mehr Trades bedeuten nur mehr Kosten.
- Kosten: 5m-ATR ist 0,48 % des Kurses, eine Rundreise 0,31 ATR; bei Hebel 10 ist jede Rundreise 1,5 % des Margin-Geldes. Dauerhaftes Gewinnen braucht also einen Vorteil von mehr als etwa 0,1 bis 0,2 R je Trade vor Kosten, den die Daten nicht zeigen.
- Vorbehalte: nur 17 bzw. 52 Tage, ein Marktumfeld; weitere Ideen brauchen längere Daten (1h: 208 Tage) oder einen Vorwärtstest.
