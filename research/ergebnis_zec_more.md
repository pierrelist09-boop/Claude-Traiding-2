# ZEC: Strategien im Vergleich (alle Wellen) (2026-11-07)

Kosten je Seite 0,045 % Gebühr + 0,03 % Slippage, Funding, Hebel 10, 2 % Risiko je Trade, Einstieg zur Eröffnung der Folgekerze, Stop vor Ziel. Training 50 % / Validierung 25 % / Test 25 % (chronologisch je Zeitrahmen). Kandidat nur bei Ø R > 0 in Validierung UND Test und mindestens 30 Test-Trades. Bei 25 Versuchen ist mit einigen Zufallstreffern zu rechnen (Bonferroni: ein einzelner Treffer müsste deutlich stärker sein): ein einzelner Kandidat ist noch kein Beleg.

| Konto | Zeitraum (Tage) | Training n / Ø R | Validierung n / Ø R | Test n / Ø R | Test PF | Test-Konto (Rückgang) | Urteil |
|---|---|---|---|---|---|---|---|
| b20_5m (Ausbruch 20 Kerzen + Volumen 1,5x (5m)) | 17 | 76 / -0.41 | 42 / -0.33 | 41 / +0.15 | 1.28 | +11 % (13 %) | kein Vorteil |
| f_5m (Dauer-Wechsel EMA9/21, immer long oder short (5m)) | 17 | 95 / -0.35 | 50 / -0.38 | 57 / -0.26 | 0.52 | -27 % (34 %) | kein Vorteil |
| f_15m (Dauer-Wechsel EMA9/21, immer long oder short (15m)) | 52 | 92 / -0.23 | 35 / +0.56 | 44 / +0.10 | 1.18 | +7 % (12 %) | **Kandidat** |
| p_15m (Pullback am EMA20 im Trend (15m)) | 52 | 108 / +0.06 | 45 / -0.22 | 55 / -0.33 | 0.40 | -31 % (32 %) | kein Vorteil |
| b20_15m (Ausbruch 20 Kerzen + Volumen 1,5x (15m)) | 52 | 76 / -0.18 | 43 / +0.19 | 41 / -0.04 | 0.93 | -5 % (15 %) | kein Vorteil |
| dc55_1h (Trendfolge: Ausbruch 55 Stunden, Stop/Trail 3 ATR (1h)) | 208 | 45 / +0.11 | 20 / +0.28 | 21 / -0.13 | 0.51 | -5 % (7 %) | kein Vorteil |
| dc100_4h (Trendfolge: Ausbruch 100 Kerzen, Stop 4 / Trail 5 ATR (4h)) | 567 | 12 / +1.15 | 8 / +0.53 | 7 / +1.34 | 4.69 | +18 % (2 %) | positiv, aber zu wenig Test-Trades |
| st_15m (Supertrend(10,3) Wechsel, immer im Markt (15m)) | 52 | 43 / -0.19 | 23 / +0.45 | 28 / -0.04 | 0.92 | -3 % (11 %) | kein Vorteil |
| st_1h (Supertrend(10,3) Wechsel, immer im Markt (1h)) | 208 | 39 / +0.61 | 25 / +0.65 | 27 / +0.01 | 1.02 | -0 % (9 %) | positiv, aber zu wenig Test-Trades |
| rsi2_5m (RSI(2)-Rücksetzer im Trend (EMA200), Ziel EMA20 (5m)) | 17 | 62 / -0.27 | 36 / -0.34 | 46 / -0.14 | 0.65 | -12 % (14 %) | kein Vorteil |
| rsi2_15m (RSI(2)-Rücksetzer im Trend (EMA200), Ziel EMA20 (15m)) | 52 | 76 / -0.27 | 50 / -0.28 | 35 / -0.25 | 0.44 | -16 % (18 %) | kein Vorteil |
| sq_15m (Bollinger-Verengung, dann Ausbruch mit Volumen (15m)) | 52 | 17 / -0.18 | 11 / +0.28 | 4 / +0.80 | 4.15 | +6 % (2 %) | positiv, aber zu wenig Test-Trades |
| mom_5m (Momentum-Kerze mit Volumen, Scalp Ziel 1,5 R (5m)) | 17 | 28 / -0.58 | 13 / -0.37 | 14 / -0.14 | 0.79 | -4 % (14 %) | kein Vorteil |
| mom_15m (Momentum-Kerze mit Volumen, Scalp Ziel 1,5 R (15m)) | 52 | 27 / -0.05 | 18 / +0.39 | 14 / -0.43 | 0.48 | -12 % (12 %) | kein Vorteil |
| vwap_15m (Rückkehr zum VWAP nach Überdehnung (15m)) | 52 | 61 / +0.09 | 47 / -0.51 | 40 / -0.16 | 0.75 | -13 % (20 %) | kein Vorteil |
| a4_15m_dc (4h-Trend + 15m-Ausbruch 20 (Volumen 1,2x)) | 52 | 19 / +0.27 | 15 / -0.03 | 11 / -0.25 | 0.52 | -6 % (6 %) | kein Vorteil |
| a4_15m_pb (4h-Trend + 15m-Pullback am EMA20) | 52 | 51 / +0.15 | 34 / -0.14 | 26 / -0.32 | 0.38 | -15 % (19 %) | kein Vorteil |
| a1_5m_dc (1h-Trend + 5m-Ausbruch 20 (Volumen 1,5x)) | 17 | 25 / -0.56 | 6 / -0.73 | 15 / -0.16 | 0.74 | -5 % (11 %) | kein Vorteil |
| a4_1h_st (4h-Trend + 1h-Supertrend-Wechsel, Trail 3 ATR) | 208 | 13 / -0.04 | 8 / +0.68 | 8 / +0.09 | 1.37 | +1 % (1 %) | positiv, aber zu wenig Test-Trades |
| dc50_4h (Trendfolge: Ausbruch 50 Kerzen, Stop 4 / Trail 5 ATR (4h)) | 567 | 20 / +0.44 | 14 / +0.09 | 10 / +0.91 | 3.38 | +17 % (6 %) | positiv, aber zu wenig Test-Trades |
| dc75_4h (Trendfolge: Ausbruch 75 Kerzen, Stop 4 / Trail 5 ATR (4h)) | 567 | 15 / +0.82 | 10 / +0.26 | 8 / +1.15 | 4.04 | +17 % (4 %) | positiv, aber zu wenig Test-Trades |
| dc150_4h (Trendfolge: Ausbruch 150 Kerzen, Stop 4 / Trail 5 ATR (4h)) | 567 | 10 / +1.43 | 7 / +0.32 | 4 / +2.55 | 9.16 | +20 % (2 %) | positiv, aber zu wenig Test-Trades |
| st_4h (Supertrend(10,3) Wechsel, immer im Markt (4h)) | 567 | 35 / -0.28 | 20 / -0.22 | 20 / -0.44 | 0.34 | -16 % (19 %) | kein Vorteil |
| ema_4h (EMA20/50-Kreuz, immer im Markt, Stop 3 ATR (4h)) | 567 | 19 / +4.35 | 14 / -0.22 | 9 / +3.57 | 9.14 | +62 % (6 %) | kein Vorteil |
| adx_15m (Ausbruch 20 nur bei ADX >= 25 und Volumen 1,2x (15m)) | 52 | 36 / -0.24 | 27 / +0.33 | 22 / -0.16 | 0.71 | -7 % (9 %) | kein Vorteil |
