"""Kern des schnellen ZEC-Paper-Handels: Indikatoren, Strategien und ein virtuelles Konto, das Kerze für Kerze arbeitet.

Dieselbe Datei läuft (1) im Backtest (Wiederholung der Historie, siehe tests/test_replay.py: ergibt dieselben Trades wie research/zec_test.py)
und (2) live im Bot (Kopie als app/claude1/zeccore.py). Reines Python ohne Abhängigkeiten, KEINE Börsenanbindung: hier wird nur gerechnet,
es werden nie Orders gesendet. Das Konto ist rein virtuell (Paper).

Ablauf je geschlossener Kerze i (on_candle): zuerst eine offene Position prüfen (Stop vor Ziel, Nachziehen, Wechsel, Zeitstopp), danach, wenn keine
Position offen ist, ein neues Signal prüfen. Einstieg zum Eröffnungskurs der nächsten Kerze (live: Schlusskurs von i, praktisch derselbe Preis).
Kosten je Seite: Gebühr 0,045 % + Slippage 0,03 %, Funding 0,00125 % je Stunde. Risiko 2 % des virtuellen Kontos bis zum Stop, Hebel höchstens 10.
"""
FEE, SLIP, FUND_H, LEV, RISK = 0.00045, 0.0003, 0.0000125, 10, 0.02
MAX_STOP_FRAC = 0.08          # Stop weiter als 8 % weg: bei Hebel 10 würde vorher die Liquidation greifen, Signal wird übersprungen
MAXBARS = {"trail": 96, "mean": 24, "flip": 400}
TF_MS = {"5m": 300_000, "15m": 900_000}


# ---------------------------------------------------------------- Indikatoren (Position i nutzt nur Kerzen bis i)
def ema(x, n):
    k, e, out = 2 / (n + 1), x[0], []
    for v in x:
        e = v * k + e * (1 - k)
        out.append(e)
    return out


def rsi(c, n=14):
    out, g, l = [50.0] * len(c), 0.0, 0.0
    for i in range(1, len(c)):
        d = c[i] - c[i - 1]
        if i <= n:
            g, l = g + max(d, 0), l + max(-d, 0)
            if i == n:
                g, l = g / n, l / n
        else:
            g, l = (g * (n - 1) + max(d, 0)) / n, (l * (n - 1) + max(-d, 0)) / n
        if i >= n:
            out[i] = 100.0 if l == 0 else 100 - 100 / (1 + g / l)
    return out


def atr(h, l, c, n=14):
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, len(c))]
    out, a = [0.0] * len(c), 0.0
    for i in range(len(c)):
        a = sum(tr[:i + 1]) / (i + 1) if i < n else (a * (n - 1) + tr[i]) / n
        out[i] = a
    return out


def bollinger(c, n=20, k=2.0):
    up, lo = [], []
    for i in range(len(c)):
        w = c[max(0, i - n + 1):i + 1]
        m = sum(w) / len(w)
        sd = (sum((x - m) ** 2 for x in w) / len(w)) ** 0.5
        up.append(m + k * sd)
        lo.append(m - k * sd)
    return up, lo


class Series:
    """Kerzenreihe mit allen Indikatoren. Kerzen: Liste von Dicts {t, o, h, l, c, v} (t = Beginn der Kerze in ms)."""

    def __init__(self, cs):
        self.t = [c["t"] for c in cs]
        self.o, self.h, self.l = [c["o"] for c in cs], [c["h"] for c in cs], [c["l"] for c in cs]
        self.c, self.v = [c["c"] for c in cs], [c["v"] for c in cs]
        self.n = len(cs)
        self.step = self.t[1] - self.t[0] if self.n > 1 else 300_000
        self.atr = atr(self.h, self.l, self.c, 14)
        self.rsi7 = rsi(self.c, 7)
        self.e9, self.e21, self.e20, self.e50, self.e200 = (ema(self.c, k) for k in (9, 21, 20, 50, 200))
        self.bb_up, self.bb_lo = bollinger(self.c, 20, 2.5)
        self.vr = [1.0] * self.n
        for i in range(self.n):
            w = self.v[max(0, i - 20):i]
            self.vr[i] = self.v[i] / (sum(w) / len(w)) if w and sum(w) > 0 else 1.0


# ---------------------------------------------------------------- Signale: (Seite, Stop in ATR, Art) oder None
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


# Name -> (Zeitrahmen, Signalfunktion, Beschreibung). Diese fünf laufen im Vorwärtstest parallel, jede mit eigenem virtuellen Konto.
STRATS = {
    "b20_5m": ("5m", sig_breakout(20), "Ausbruch 20 Kerzen + Volumen 1,5x (5m)"),
    "f_5m": ("5m", sig_flip, "Dauer-Wechsel EMA9/21, immer long oder short (5m)"),
    "f_15m": ("15m", sig_flip, "Dauer-Wechsel EMA9/21, immer long oder short (15m)"),
    "p_15m": ("15m", sig_pullback, "Pullback am EMA20 im Trend (15m)"),
    "b20_15m": ("15m", sig_breakout(20), "Ausbruch 20 Kerzen + Volumen 1,5x (15m)"),
}


# ---------------------------------------------------------------- virtuelles Konto
def new_state(strat, eq=1000.0):
    return {"strat": strat, "eq": eq, "pos": None, "last_t": 0}


def _open(st, s, i, next_open, g):
    side, sm, kind = g
    long = side == "long"
    entry = next_open * (1 + SLIP if long else 1 - SLIP)
    a = s.atr[i]
    if a <= 0:
        return None
    d = sm * a
    stop = entry - d if long else entry + d
    target = s.e20[i] if kind == "mean" else None
    if target is not None and ((long and target <= entry) or (not long and target >= entry)):
        return None
    if d / entry > MAX_STOP_FRAC:
        return None
    notional = min(RISK * st["eq"] / (d / entry), LEV * st["eq"])
    return {"side": side, "kind": kind, "entry": entry, "d": d, "stop": stop, "trail": stop, "extreme": entry, "target": target,
            "bars": 0, "t_open": s.t[i] + s.step, "notional": notional}


def _check_exit(p, s, k):
    """Eine Kerze k gegen die offene Position prüfen. Gibt (Ausstiegskurs, Grund) oder None; verändert Trail/Zähler."""
    long = p["side"] == "long"
    if (s.l[k] <= p["trail"]) if long else (s.h[k] >= p["trail"]):
        return (min(p["trail"], s.o[k]) if long else max(p["trail"], s.o[k])), "stop"
    tg = p["target"]
    if tg is not None and ((s.h[k] >= tg) if long else (s.l[k] <= tg)):
        return tg, "ziel"
    if p["kind"] == "trail":
        p["extreme"] = max(p["extreme"], s.h[k]) if long else min(p["extreme"], s.l[k])
        new = p["extreme"] - 2.0 * s.atr[k] if long else p["extreme"] + 2.0 * s.atr[k]
        p["trail"] = max(p["trail"], new) if long else min(p["trail"], new)
    if p["kind"] == "flip":
        g2 = sig_flip(s, k)
        if g2 and g2[0] != p["side"]:
            return s.c[k], "wechsel"
    if p["bars"] >= MAXBARS[p["kind"]]:
        return s.c[k], "zeit"
    p["bars"] += 1
    return None


def _close(st, p, s, k, ex, why):
    long = p["side"] == "long"
    ex *= (1 - SLIP if long else 1 + SLIP)
    hours = (p["bars"] + 1) * s.step / 3_600_000
    gross = ((ex - p["entry"]) if long else (p["entry"] - ex)) / p["d"]
    r = gross - (2 * FEE + FUND_H * hours) * p["entry"] / p["d"]
    pnl = r * p["notional"] * p["d"] / p["entry"]
    st["eq"] += pnl
    st["pos"] = None
    return {"strat": st["strat"], "side": p["side"], "t_open": p["t_open"], "t_close": s.t[k] + s.step, "entry": p["entry"], "exit": ex,
            "r": r, "pnl": pnl, "eq": st["eq"], "why": why, "notional": p["notional"]}


def on_candle(st, s, i, next_open):
    """Die gerade geschlossene Kerze i verarbeiten. Gibt die dabei geschlossenen Trades zurück (Liste von Dicts)."""
    sig = STRATS[st["strat"]][1]
    out, exited, reenter = [], False, False
    p = st["pos"]
    if p:
        res = _check_exit(p, s, i)
        if res:
            out.append(_close(st, p, s, i, *res))
            exited, reenter = True, res[1] == "wechsel"
    if st["pos"] is None and (not exited or reenter) and st["eq"] > 0:
        g = sig(s, i)
        if g:
            st["pos"] = _open(st, s, i, next_open, g)
    st["last_t"] = s.t[i]
    return out
