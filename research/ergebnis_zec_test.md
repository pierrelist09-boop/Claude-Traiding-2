# ZEC schnelle Strategien: Machbarkeitstest (2026-11-07)

Kosten je Seite 0.045 % Gebühr + 0.03 % Slippage = 0.15 % je Rundreise auf den Positionswert; bei Hebel 10 sind das 1.5 % des eingesetzten Geldes je Trade. Risiko 2 % je Trade, Hebel gedeckelt auf 10.


## 5m-Kerzen: 5000 Kerzen = 17 Tage (21.10.–07.11.2026), Ø ATR(14) = 0.48 % des Kurses. Eine Rundreise kostet 0.15 % = 0.31 ATR.

| Strategie | Training n / Ø R | Validierung n / Ø R | Test n / Ø R | Test PF | Test Treffer | Kosten je Trade (R) | Test-Konto (2 % Risiko, 10x) | Test Trades/Tag |
|---|---|---|---|---|---|---|---|---|
| B20 Ausbruch 20 Kerzen + Volumen 1,5x | 76 / -0.41 | 42 / -0.33 | 41 / +0.15 | 1.28 | 34 % | 0.12 | +11 % (Rückgang 13 %, bester Tag +9 %) | 10.2 |
| B40 Ausbruch 40 Kerzen + Volumen 1,5x | 55 / -0.35 | 34 / -0.31 | 29 / +0.10 | 1.19 | 31 % | 0.12 | +4 % (Rückgang 12 %, bester Tag +7 %) | 7.2 |
| M  Umkehr: RSI(7) Extrem + Bollinger 2,5 | 4 / -0.46 | 7 / -0.47 | 5 / -1.12 | 0.00 | 0 % | 0.09 | -11 % (Rückgang 11 %, bester Tag -2 %) | 1.2 |
| P  Pullback am EMA20 im Trend (EMA50/200) | 120 / -0.28 | 66 / -0.45 | 63 / -0.20 | 0.67 | 29 % | 0.12 | -24 % (Rückgang 26 %, bester Tag +4 %) | 15.8 |
| F  Dauer-Wechsel: EMA9/21-Kreuz immer long oder short | 57 / -0.08 | 31 / -0.24 | 33 / -0.17 | 0.66 | 27 % | 0.09 | -12 % (Rückgang 21 %, bester Tag +9 %) | 8.2 |

## 15m-Kerzen: 5000 Kerzen = 52 Tage (16.09.–07.11.2026), Ø ATR(14) = 0.84 % des Kurses. Eine Rundreise kostet 0.15 % = 0.18 ATR.

| Strategie | Training n / Ø R | Validierung n / Ø R | Test n / Ø R | Test PF | Test Treffer | Kosten je Trade (R) | Test-Konto (2 % Risiko, 10x) | Test Trades/Tag |
|---|---|---|---|---|---|---|---|---|
| B20 Ausbruch 20 Kerzen + Volumen 1,5x | 76 / -0.18 | 43 / +0.19 | 41 / -0.04 | 0.93 | 34 % | 0.08 | -5 % (Rückgang 15 %, bester Tag +5 %) | 3.2 |
| B40 Ausbruch 40 Kerzen + Volumen 1,5x | 56 / -0.12 | 34 / +0.30 | 32 / -0.13 | 0.78 | 31 % | 0.08 | -9 % (Rückgang 18 %, bester Tag +8 %) | 2.5 |
| M  Umkehr: RSI(7) Extrem + Bollinger 2,5 | 14 / -0.18 | 3 / -0.24 | 4 / -0.55 | 0.31 | 25 % | 0.05 | -4 % (Rückgang 6 %, bester Tag +2 %) | 0.3 |
| P  Pullback am EMA20 im Trend (EMA50/200) | 108 / +0.06 | 45 / -0.22 | 55 / -0.33 | 0.40 | 31 % | 0.08 | -31 % (Rückgang 32 %, bester Tag +2 %) | 4.2 |
| F  Dauer-Wechsel: EMA9/21-Kreuz immer long oder short | 57 / -0.39 | 21 / +0.89 | 27 / -0.13 | 0.78 | 30 % | 0.06 | -8 % (Rückgang 11 %, bester Tag +6 %) | 2.1 |

R = Gewinn in Vielfachen des Stop-Abstands, nach Kosten. Ein Vorteil gilt nur, wenn Validierung UND Test Ø R > 0 haben und der Test mindestens 30 Trades hat.
