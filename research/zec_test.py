#!/usr/bin/env python3
"""Machbarkeitstest: schnelle Long-/Short-Strategien auf ZEC (Hyperliquid-Perp, max. Hebel 10) mit echten Kosten.

Vorab festgelegt (kein Nachjustieren nach dem Test): 5 Strategien x 2 Zeitrahmen (5m, 15m) = 10 Versuche.
Chronologisch 50 % Training / 25 % Validierung / 25 % Test. Einstieg zur Eröffnung der Kerze NACH dem Signal, Stop vor Ziel in derselben Kerze.
Kosten je Seite: Gebühr 0,045 % + Slippage 0,03 % (ZEC ist liquide, aber nicht BTC), Funding 0,00125 %/h. Nur Standardbibliothek.
Konto-Rechnung: 2 % Risiko je Trade, höchstens 1 Position, Hebel auf 10x gedeckelt (größere Position wird verkleinert).
Aufruf: python3 research/zec_test.py [--write]"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from zecfast import data
from zecfast.indicators import atr, bollinger, ema, rsi

FEE, SLIP, FUND_H, LEV, RISK = 0.00045, 0.0003, 0.0000125, 10, 0.02
COIN = "ZEC"
TFMIN = {"5m": 5, "15m": 15}


class S:
    def __init__(self, cs):
        self.t = [c["t"] for c in cs]; self.o = [c["o"] for c in cs]; self.h = [c["h"] for c in cs]
        self.l = [c["l"] for c in cs]; self.c = [c["c"] for c in cs]; self.v = [c["v"] for c in cs]
        self.n = len(cs)
        self.atr = atr(self.h, self.l, self.c, 14)
        self.rsi7 = rsi(self.c, 7)
        self.e9, self.e21, self.e20, self.e50, self.e200 = (ema(self.c, k) for k in (9, 21, 20, 50, 200))
        self.bb_up, self.bb_lo, _ = bollinger(self.c, 20, 2.5)
        self.vr = [1.0] * self.n
        for i in range(self.n):
            w = self.v[max(0, i - 20):i]
            self.vr[i] = self.v[i] / (sum(w) / len(w)) if w and sum(w) > 0 else 1.0


# ---- Signale: nur Kerzen bis einschließlich i. Rückgabe (side, stop_mult, kind) kind: 'trail' | 'mean' | 'flip'
def sig_breakout(N):
    def f(s, i):
        if i < N + 1 or s.vr[i] < 1.5:
            return None
        if s.c[i] > max(s.h[i - N:i]):
            return "long", 1.5, "trail"
        if s.c[i] < min(s.l[i - N:i]):
            return "short", 1.5, "trail"
    return f


def sig_meanrev(s, i):
    if i < 30:
        return None
    if s.rsi7[i] <= 12 and s.c[i] < s.bb_lo[i]:
        return "long", 1.5, "mean"
    if s.rsi7[i] >= 88 and s.c[i] > s.bb_up[i]:
        return "short", 1.5, "mean"


def sig_pullback(s, i):
    if i < 210:
        return None
    if s.e50[i] > s.e200[i] and s.c[i] > s.e200[i] and s.l[i] <= s.e20[i] and s.c[i] > s.e20[i] and s.c[i - 1] < s.e20[i - 1] * 1.002:
        return "long", 1.5, "trail"
    if s.e50[i] < s.e200[i] and s.c[i] < s.e200[i] and s.h[i] >= s.e20[i] and s.c[i] < s.e20[i] and s.c[i - 1] > s.e20[i - 1] * 0.998:
        return "short", 1.5, "trail"


def sig_flip(s, i):
    if i < 30:
        return None
    if s.e9[i] > s.e21[i] and s.e9[i - 1] <= s.e21[i - 1]:
        return "long", 2.0, "flip"
    if s.e9[i] < s.e21[i] and s.e9[i - 1] >= s.e21[i - 1]:
        return "short", 2.0, "flip"


STRATS = [("B20 Ausbruch 20 Kerzen + Volumen 1,5x", sig_breakout(20)), ("B40 Ausbruch 40 Kerzen + Volumen 1,5x", sig_breakout(40)),
          ("M  Umkehr: RSI(7) Extrem + Bollinger 2,5", sig_meanrev), ("P  Pullback am EMA20 im Trend (EMA50/200)", sig_pullback),
          ("F  Dauer-Wechsel: EMA9/21-Kreuz immer long oder short", sig_flip)]
MAXBARS = {"trail": 96, "mean": 24, "flip": 400}


def simulate(s, lo, hi, sig):
    """Trades in [lo, hi). Einstieg Eröffnung Kerze i+1. Liste (t_entry, R, t_exit, stop_anteil)."""
    out, i = [], max(lo, 1)
    while i < hi - 2:
        g = sig(s, i)
        if not g or s.atr[i] <= 0:
            i += 1
            continue
        side, sm, kind = g
        long = side == "long"
        e = i + 1
        entry = s.o[e] * (1 + SLIP if long else 1 - SLIP)
        a = s.atr[i]
        d = sm * a
        stop = entry - d if long else entry + d
        target = (s.e20[i] if kind == "mean" else None)
        if target is not None and ((long and target <= entry) or (not long and target >= entry)):
            i += 1
            continue
        extreme, trail, k, ex, why = entry, stop, e, None, ""
        while k < min(hi, s.n):
            if (s.l[k] <= trail) if long else (s.h[k] >= trail):
                ex, why = (min(trail, s.o[k]) if long else max(trail, s.o[k])), "stop"
                break
            if target is not None and ((s.h[k] >= target) if long else (s.l[k] <= target)):
                ex, why = target, "ziel"
                break
            if kind == "trail":
                extreme = max(extreme, s.h[k]) if long else min(extreme, s.l[k])
                new = extreme - 2.0 * s.atr[k] if long else extreme + 2.0 * s.atr[k]
                trail = max(trail, new) if long else min(trail, new)
            if kind == "flip":
                g2 = sig_flip(s, k)
                if g2 and g2[0] != side:
                    ex, why = s.c[k], "wechsel"
                    break
            if k - e >= MAXBARS[kind]:
                ex, why = s.c[k], "zeit"
                break
            k += 1
        if ex is None:
            break
        ex *= (1 - SLIP if long else 1 + SLIP)
        hours = (k - e + 1) * (s.t[1] - s.t[0]) / 3_600_000
        gross = ((ex - entry) if long else (entry - ex)) / d
        cost = (2 * FEE + FUND_H * hours) * entry / d
        out.append((s.t[e], gross - cost, s.t[min(k, s.n - 1)], d / entry, cost, gross))
        i = k + 1
    return out


def stats(tr):
    if not tr:
        return dict(n=0, avg=float("nan"), pf=float("nan"), cost=float("nan"), win=float("nan"))
    w = sum(x[1] for x in tr if x[1] > 0); l = -sum(x[1] for x in tr if x[1] < 0)
    return dict(n=len(tr), avg=sum(x[1] for x in tr) / len(tr), pf=w / l if l else float("inf"), cost=sum(x[4] for x in tr) / len(tr), win=sum(1 for x in tr if x[1] > 0) / len(tr))


def account(tr, t0, t1, eq0=1000.0):
    eq, peak, dd, days = eq0, eq0, 0.0, {}
    for t, R, tx, d, _, _ in sorted(tr, key=lambda x: x[0]):
        notional = min(RISK * eq / d, LEV * eq)
        eq += R * notional * d
        peak = max(peak, eq); dd = max(dd, 1 - eq / peak)
        day = int(tx // 86_400_000)
        days[day] = days.get(day, 0.0) + R * notional * d
        if eq <= 0:
            break
    nd = max(1, int((t1 - t0) / 86_400_000))
    return dict(final=eq, ret=eq / eq0 - 1, dd=dd, best_day=max(days.values()) / eq0 if days else 0.0, days_pos=sum(1 for v in days.values() if v > 0), days_neg=sum(1 for v in days.values() if v < 0), nd=nd)


def main():
    write = "--write" in sys.argv
    out = [f"# ZEC schnelle Strategien: Machbarkeitstest ({time.strftime('%Y-%m-%d', time.gmtime())})\n",
           f"Kosten je Seite {FEE * 100:.3f} % Gebühr + {SLIP * 100:.2f} % Slippage = {2 * (FEE + SLIP) * 100:.2f} % je Rundreise auf den Positionswert; bei Hebel {LEV} sind das {2 * (FEE + SLIP) * LEV * 100:.1f} % des eingesetzten Geldes je Trade. "
           f"Risiko {RISK * 100:.0f} % je Trade, Hebel gedeckelt auf {LEV}.\n"]
    for tf in ("5m", "15m"):
        cs = data.candles(COIN, tf, 5000)
        s = S(cs)
        a, b = int(s.n * 0.5), int(s.n * 0.75)
        days = (s.t[-1] - s.t[0]) / 86_400_000
        pr = sum(s.atr[i] / s.c[i] for i in range(s.n)) / s.n * 100
        out.append(f"\n## {tf}-Kerzen: {s.n} Kerzen = {days:.0f} Tage ({time.strftime('%d.%m.', time.gmtime(s.t[0] / 1000))}–{time.strftime('%d.%m.%Y', time.gmtime(s.t[-1] / 1000))}), Ø ATR(14) = {pr:.2f} % des Kurses. "
                   f"Eine Rundreise kostet {2 * (FEE + SLIP) * 100:.2f} % = {2 * (FEE + SLIP) * 100 / pr:.2f} ATR.\n")
        out.append("| Strategie | Training n / Ø R | Validierung n / Ø R | Test n / Ø R | Test PF | Test Treffer | Kosten je Trade (R) | Test-Konto (2 % Risiko, 10x) | Test Trades/Tag |\n|---|---|---|---|---|---|---|---|---|")
        for name, f in STRATS:
            tr, va, te = simulate(s, 210, a, f), simulate(s, a, b, f), simulate(s, b, s.n, f)
            st, sv, se = stats(tr), stats(va), stats(te)
            ac = account(te, s.t[b], s.t[-1])
            fm = lambda d: f"{d['n']} / {d['avg']:+.2f}" if d["n"] else "–"
            out.append(f"| {name} | {fm(st)} | {fm(sv)} | {fm(se)} | {se['pf']:.2f} | {se['win'] * 100:.0f} % | {se['cost']:.2f} | {ac['ret'] * 100:+.0f} % (Rückgang {ac['dd'] * 100:.0f} %, bester Tag {ac['best_day'] * 100:+.0f} %) | {se['n'] / ac['nd']:.1f} |"
                       if se["n"] else f"| {name} | {fm(st)} | {fm(sv)} | – | – | – | – | – | 0 |")
    out.append("\nR = Gewinn in Vielfachen des Stop-Abstands, nach Kosten. Ein Vorteil gilt nur, wenn Validierung UND Test Ø R > 0 haben und der Test mindestens 30 Trades hat.")
    text = "\n".join(out)
    print(text)
    if write:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ergebnis_zec_test.md"), "w") as fh:
            fh.write(text + "\n")


if __name__ == "__main__":
    main()
