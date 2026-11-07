"""Kern des schnellen ZEC-Paper-Handels: Indikatoren, Strategien und ein virtuelles Konto, das Kerze für Kerze arbeitet.

Dieselbe Datei läuft (1) im Backtest (Wiederholung der Historie, siehe tests/test_replay.py: ergibt dieselben Trades wie research/zec_test.py)
und (2) live im Bot (Kopie als app/claude1/zeccore.py). Reines Python ohne Abhängigkeiten, KEINE Börsenanbindung: hier wird nur gerechnet,
es werden nie Orders gesendet. Das Konto ist rein virtuell (Paper).

Ablauf je geschlossener Kerze i (on_candle): zuerst eine offene Position prüfen (Stop vor Ziel, Nachziehen, Wechsel, Zeitstopp), danach, wenn keine
Position offen ist, ein neues Signal prüfen. Einstieg zum Eröffnungskurs der nächsten Kerze (live: Schlusskurs von i, praktisch derselbe Preis).
Kosten je Seite: Gebühr 0,045 % + Slippage 0,03 %, Funding 0,00125 % je Stunde. Risiko 2 % des virtuellen Kontos bis zum Stop, Hebel höchstens 10.
"""
FEE, SLIP, FUND_H, LEV, RISK = 0.00045, 0.0003, 0.0000125, 10, 0.02
MAX_STOP_FRAC = 0.5           # Stop weiter als 50 % weg: unsinnig, Signal wird übersprungen. (Liquidation ist nie vorher dran: bei 2 % Risiko liegt sie 50 Stop-Abstände entfernt.)
TF_MS = {"5m": 300_000, "15m": 900_000, "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}
# Ausstiegsarten: Nachzieh-Abstand in ATR (None = kein Trail), längste Haltedauer in Kerzen, Ziel (None, EMA20, VWAP oder festes Vielfaches des Stop-Abstands)
KINDS = {"trail": dict(trail=2.0, maxbars=96, target=None), "mean": dict(trail=None, maxbars=24, target="ema20"),
         "vwap": dict(trail=None, maxbars=24, target="vwap"), "flip": dict(trail=None, maxbars=400, target=None),
         "slow": dict(trail=3.0, maxbars=300, target=None), "slow5": dict(trail=5.0, maxbars=600, target=None), "slow7": dict(trail=7.0, maxbars=800, target=None),
         "scalp": dict(trail=None, maxbars=12, target=1.5)}


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


def supertrend(h, l, c, n=10, m=3.0):
    """Richtung des Supertrend (+1 aufwärts, -1 abwärts) je Kerze; nutzt nur Kerzen bis i."""
    a, N = atr(h, l, c, n), len(c)
    up, dn, d = [0.0] * N, [0.0] * N, [1] * N
    for i in range(N):
        mid = (h[i] + l[i]) / 2
        bu, bl = mid + m * a[i], mid - m * a[i]
        if i == 0:
            up[i], dn[i] = bu, bl
            continue
        up[i] = bu if (bu < up[i - 1] or c[i - 1] > up[i - 1]) else up[i - 1]
        dn[i] = bl if (bl > dn[i - 1] or c[i - 1] < dn[i - 1]) else dn[i - 1]
        d[i] = -1 if (d[i - 1] == 1 and c[i] < dn[i]) else 1 if (d[i - 1] == -1 and c[i] > up[i]) else d[i - 1]
    return d


def adx_series(h, l, c, n=14):
    """ADX (EMA-Glättung wie im Plugin trading-skills); nutzt nur Kerzen bis i."""
    N = len(c)
    pdm, mdm, tr = [0.0] * N, [0.0] * N, [0.0] * N
    for i in range(1, N):
        up, dn = h[i] - h[i - 1], l[i - 1] - l[i]
        p, m = max(up, 0.0), max(dn, 0.0)
        pdm[i], mdm[i] = (0.0 if p < m else p), (0.0 if m < p else m)
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    pe, me, te = ema(pdm, 2 * n - 1), ema(mdm, 2 * n - 1), ema(tr, 2 * n - 1)
    dx = []
    for i in range(N):
        pdi, mdi = (100 * pe[i] / te[i], 100 * me[i] / te[i]) if te[i] > 0 else (0.0, 0.0)
        dx.append(100 * abs(pdi - mdi) / (pdi + mdi) if pdi + mdi > 0 else 0.0)
    return ema(dx, 2 * n - 1)


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
        self.rsi2 = rsi(self.c, 2)
        self.adx = adx_series(self.h, self.l, self.c, 14)
        self.htf, self.hmap = {}, {}                                          # höhere Zeitrahmen (siehe link)
        self.st_dir = supertrend(self.h, self.l, self.c, 10, 3.0)
        u2, l2 = bollinger(self.c, 20, 2.0)                                  # Bollinger-Breite relativ zur Mitte und ihr Rang in den letzten 100 Kerzen
        bw = [(u - lo) / ((u + lo) / 2) if (u + lo) else 0.0 for u, lo in zip(u2, l2)]
        self.bbw_pr = [sum(1 for v in bw[max(0, i - 100):i] if v <= bw[i]) / max(1, len(bw[max(0, i - 100):i])) for i in range(self.n)]
        cum_pv, cum_v, self.vwap = [0.0], [0.0], []                           # gleitender VWAP über 96 Kerzen
        for i in range(self.n):
            cum_pv.append(cum_pv[-1] + (self.h[i] + self.l[i] + self.c[i]) / 3 * self.v[i])
            cum_v.append(cum_v[-1] + self.v[i])
            a0 = max(0, i - 95)
            vv = cum_v[i + 1] - cum_v[a0]
            self.vwap.append((cum_pv[i + 1] - cum_pv[a0]) / vv if vv > 0 else self.c[i])
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


def link(s, name, H):
    """Höheren Zeitrahmen H an die Reihe s hängen: s.hmap[name][i] = Index der letzten bei Schluss von Kerze i schon GESCHLOSSENEN H-Kerze (-1 = keine)."""
    ends = [t + H.step for t in H.t]
    m, j = [], -1
    for i in range(s.n):
        end = s.t[i] + s.step
        while j + 1 < H.n and ends[j + 1] <= end:
            j += 1
        m.append(j)
    s.htf[name], s.hmap[name] = H, m


def _trend(s, name, i):
    """Trend im höheren Zeitrahmen: +1 (Schluss > EMA50 > EMA200), -1 (spiegelbildlich), sonst 0."""
    H, j = s.htf[name], s.hmap[name][i]
    if j < 200:
        return 0
    if H.c[j] > H.e50[j] > H.e200[j]:
        return 1
    if H.c[j] < H.e50[j] < H.e200[j]:
        return -1
    return 0


def sig_aligned_breakout(htf, N, vr_min, stop):
    def f(s, i):
        if i < N + 1 or s.vr[i] < vr_min:
            return None
        t = _trend(s, htf, i)
        if t == 1 and s.c[i] > max(s.h[i - N:i]):
            return "long", stop, "trail"
        if t == -1 and s.c[i] < min(s.l[i - N:i]):
            return "short", stop, "trail"
    return f


def sig_aligned_pullback(htf):
    def f(s, i):
        if i < 30:
            return None
        t = _trend(s, htf, i)
        if t == 1 and s.l[i] <= s.e20[i] and s.c[i] > s.e20[i] and s.c[i - 1] < s.e20[i - 1] * 1.002:
            return "long", 1.5, "trail"
        if t == -1 and s.h[i] >= s.e20[i] and s.c[i] < s.e20[i] and s.c[i - 1] > s.e20[i - 1] * 0.998:
            return "short", 1.5, "trail"
    return f


def sig_aligned_supertrend(htf):
    def f(s, i):
        if i < 30:
            return None
        t = _trend(s, htf, i)
        if t == 1 and s.st_dir[i] == 1 and s.st_dir[i - 1] == -1:
            return "long", 2.5, "slow"
        if t == -1 and s.st_dir[i] == -1 and s.st_dir[i - 1] == 1:
            return "short", 2.5, "slow"
    return f


def sig_ema_cross(s, i):
    if i < 60:
        return None
    if s.e20[i] > s.e50[i] and s.e20[i - 1] <= s.e50[i - 1]:
        return "long", 3.0, "flip"
    if s.e20[i] < s.e50[i] and s.e20[i - 1] >= s.e50[i - 1]:
        return "short", 3.0, "flip"


def sig_adx_breakout(s, i):
    if i < 40 or s.adx[i] < 25 or s.vr[i] < 1.2:
        return None
    if s.c[i] > max(s.h[i - 20:i]):
        return "long", 1.5, "trail"
    if s.c[i] < min(s.l[i - 20:i]):
        return "short", 1.5, "trail"


def sig_donchian(N, stop, kind, sides="both", htf=None):
    """Ausbruch über das N-Kerzen-Hoch/-Tief; sides: both, long oder short; htf: Tagestrend o. ä. als Filter (Richtung des höheren Zeitrahmens)."""
    def f(s, i):
        if i < N + 1:
            return None
        t = _trend(s, htf, i) if htf else 0
        if sides != "short" and s.c[i] > max(s.h[i - N:i]) and (not htf or t == 1):
            return "long", stop, kind
        if sides != "long" and s.c[i] < min(s.l[i - N:i]) and (not htf or t == -1):
            return "short", stop, kind
    return f


def sig_cross(fast, slow, stop, start=210):
    """Kreuz zweier EMAs (Attribute der Reihe, z. B. e50/e200), immer im Markt (Art flip)."""
    def f(s, i):
        a, b = getattr(s, fast), getattr(s, slow)
        if i < start:
            return None
        if a[i] > b[i] and a[i - 1] <= b[i - 1]:
            return "long", stop, "flip"
        if a[i] < b[i] and a[i - 1] >= b[i - 1]:
            return "short", stop, "flip"
    return f


def sig_pullback_own(stop, kind):
    """Rücksetzer an den EMA20 im Trend des eigenen Zeitrahmens (Schluss > EMA50 > EMA200)."""
    def f(s, i):
        if i < 210:
            return None
        if s.c[i] > s.e50[i] > s.e200[i] and s.l[i] <= s.e20[i] and s.c[i] > s.e20[i] and s.c[i - 1] < s.e20[i - 1] * 1.002:
            return "long", stop, kind
        if s.c[i] < s.e50[i] < s.e200[i] and s.h[i] >= s.e20[i] and s.c[i] < s.e20[i] and s.c[i - 1] > s.e20[i - 1] * 0.998:
            return "short", stop, kind
    return f


def sig_tsm(L, stop):
    """Zeitreihen-Momentum: Vorzeichen der Rendite über L Kerzen wechselt, immer im Markt (Art flip)."""
    def f(s, i):
        if i < L + 2:
            return None
        r, r0 = s.c[i] / s.c[i - L] - 1, s.c[i - 1] / s.c[i - 1 - L] - 1
        if r > 0 and r0 <= 0:
            return "long", stop, "flip"
        if r < 0 and r0 >= 0:
            return "short", stop, "flip"
    return f


def sig_squeeze_4h(s, i):
    if i < 130 or s.bbw_pr[i] > 0.20 or s.vr[i] < 1.2:
        return None
    if s.c[i] > max(s.h[i - 20:i]):
        return "long", 3.0, "slow5"
    if s.c[i] < min(s.l[i - 20:i]):
        return "short", 3.0, "slow5"


def sig_supertrend(s, i):
    if i < 30:
        return None
    if s.st_dir[i] == 1 and s.st_dir[i - 1] == -1:
        return "long", 2.5, "flip"
    if s.st_dir[i] == -1 and s.st_dir[i - 1] == 1:
        return "short", 2.5, "flip"


def sig_rsi2(s, i):
    if i < 210:
        return None
    if s.c[i] > s.e200[i] and s.rsi2[i] < 8:
        return "long", 1.5, "mean"
    if s.c[i] < s.e200[i] and s.rsi2[i] > 92:
        return "short", 1.5, "mean"


def sig_squeeze(s, i):
    if i < 130 or s.bbw_pr[i] > 0.20 or s.vr[i] < 1.2:
        return None
    if s.c[i] > max(s.h[i - 20:i]):
        return "long", 1.5, "trail"
    if s.c[i] < min(s.l[i - 20:i]):
        return "short", 1.5, "trail"


def sig_momentum(s, i):
    if i < 30 or s.atr[i] <= 0 or s.vr[i] < 2.0:
        return None
    rng = s.h[i] - s.l[i]
    if rng < 2.2 * s.atr[i]:
        return None
    pos = (s.c[i] - s.l[i]) / rng
    if pos >= 0.75:
        return "long", 1.0, "scalp"
    if pos <= 0.25:
        return "short", 1.0, "scalp"


def sig_vwap(s, i):
    if i < 100 or s.atr[i] <= 0:
        return None
    dev = (s.c[i] - s.vwap[i]) / s.atr[i]
    if dev <= -2.5 and s.rsi7[i] < 25:
        return "long", 1.5, "vwap"
    if dev >= 2.5 and s.rsi7[i] > 75:
        return "short", 1.5, "vwap"


# Name -> (Zeitrahmen, Signalfunktion, Beschreibung). Alle laufen im Vorwärtstest parallel, jede mit eigenem virtuellen Konto.
STRATS = {
    "b20_5m": ("5m", sig_breakout(20), "Ausbruch 20 Kerzen + Volumen 1,5x (5m)"),
    "f_5m": ("5m", sig_flip, "Dauer-Wechsel EMA9/21, immer long oder short (5m)"),
    "f_15m": ("15m", sig_flip, "Dauer-Wechsel EMA9/21, immer long oder short (15m)"),
    "p_15m": ("15m", sig_pullback, "Pullback am EMA20 im Trend (15m)"),
    "b20_15m": ("15m", sig_breakout(20), "Ausbruch 20 Kerzen + Volumen 1,5x (15m)"),
    # --- zweite Welle (2026-11-07, vorab festgelegt) ---
    "dc55_1h": ("1h", sig_donchian(55, 3.0, "slow"), "Trendfolge: Ausbruch 55 Stunden, Stop/Trail 3 ATR (1h)"),
    "dc100_4h": ("4h", sig_donchian(100, 4.0, "slow5"), "Trendfolge: Ausbruch 100 Kerzen, Stop 4 / Trail 5 ATR (4h)"),
    "st_15m": ("15m", sig_supertrend, "Supertrend(10,3) Wechsel, immer im Markt (15m)"),
    "st_1h": ("1h", sig_supertrend, "Supertrend(10,3) Wechsel, immer im Markt (1h)"),
    "rsi2_5m": ("5m", sig_rsi2, "RSI(2)-Rücksetzer im Trend (EMA200), Ziel EMA20 (5m)"),
    "rsi2_15m": ("15m", sig_rsi2, "RSI(2)-Rücksetzer im Trend (EMA200), Ziel EMA20 (15m)"),
    "sq_15m": ("15m", sig_squeeze, "Bollinger-Verengung, dann Ausbruch mit Volumen (15m)"),
    "mom_5m": ("5m", sig_momentum, "Momentum-Kerze mit Volumen, Scalp Ziel 1,5 R (5m)"),
    "mom_15m": ("15m", sig_momentum, "Momentum-Kerze mit Volumen, Scalp Ziel 1,5 R (15m)"),
    "vwap_15m": ("15m", sig_vwap, "Rückkehr zum VWAP nach Überdehnung (15m)"),
    # --- dritte Welle (2026-11-07, vorab festgelegt): Einstiege nur in Richtung des höheren Zeitrahmens, langsame Trendfolge als Parameterfamilie ---
    "a4_15m_dc": ("15m", sig_aligned_breakout("4h", 20, 1.2, 1.5), "4h-Trend + 15m-Ausbruch 20 (Volumen 1,2x)"),
    "a4_15m_pb": ("15m", sig_aligned_pullback("4h"), "4h-Trend + 15m-Pullback am EMA20"),
    "a1_5m_dc": ("5m", sig_aligned_breakout("1h", 20, 1.5, 1.5), "1h-Trend + 5m-Ausbruch 20 (Volumen 1,5x)"),
    "a4_1h_st": ("1h", sig_aligned_supertrend("4h"), "4h-Trend + 1h-Supertrend-Wechsel, Trail 3 ATR"),
    "dc50_4h": ("4h", sig_donchian(50, 4.0, "slow5"), "Trendfolge: Ausbruch 50 Kerzen, Stop 4 / Trail 5 ATR (4h)"),
    "dc75_4h": ("4h", sig_donchian(75, 4.0, "slow5"), "Trendfolge: Ausbruch 75 Kerzen, Stop 4 / Trail 5 ATR (4h)"),
    "dc150_4h": ("4h", sig_donchian(150, 4.0, "slow5"), "Trendfolge: Ausbruch 150 Kerzen, Stop 4 / Trail 5 ATR (4h)"),
    "st_4h": ("4h", sig_supertrend, "Supertrend(10,3) Wechsel, immer im Markt (4h)"),
    "ema_4h": ("4h", sig_ema_cross, "EMA20/50-Kreuz, immer im Markt, Stop 3 ATR (4h)"),
    "adx_15m": ("15m", sig_adx_breakout, "Ausbruch 20 nur bei ADX >= 25 und Volumen 1,2x (15m)"),
    # --- vierte Welle (2026-11-07, vorab festgelegt): weitere 4h-Mechanismen, nur ZEC ---
    "dcL_100_4h": ("4h", sig_donchian(100, 4.0, "slow5", "long"), "4h Ausbruch 100 nur LONG, Stop 4 / Trail 5 ATR"),
    "dcS_100_4h": ("4h", sig_donchian(100, 4.0, "slow5", "short"), "4h Ausbruch 100 nur SHORT, Stop 4 / Trail 5 ATR"),
    "dc100_t3_4h": ("4h", sig_donchian(100, 4.0, "slow"), "4h Ausbruch 100, enger Trail 3 ATR"),
    "dc100_t7_4h": ("4h", sig_donchian(100, 4.0, "slow7"), "4h Ausbruch 100, weiter Trail 7 ATR"),
    "dc100_d1_4h": ("4h", sig_donchian(100, 4.0, "slow5", "both", "1d"), "4h Ausbruch 100 nur in Richtung des Tagestrends (EMA50/200)"),
    "pb_4h": ("4h", sig_pullback_own(3.0, "slow5"), "4h Pullback am EMA20 im Trend (EMA50/200), Stop 3 / Trail 5 ATR"),
    "gc_4h": ("4h", sig_cross("e50", "e200", 4.0), "4h Golden/Death Cross EMA50/200, immer im Markt"),
    "dc30_4h": ("4h", sig_donchian(30, 3.5, "slow"), "4h Ausbruch 30 (schneller), Stop 3,5 / Trail 3 ATR"),
    "tsm120_4h": ("4h", sig_tsm(120, 4.0), "4h Zeitreihen-Momentum (20-Tage-Rendite), immer im Markt"),
    "sq_4h": ("4h", sig_squeeze_4h, "4h Bollinger-Verengung, dann Ausbruch mit Volumen, Trail 5 ATR"),
}
# Strategien, die höhere Zeitrahmen als Filter brauchen
NEEDS = {"a4_15m_dc": ("4h",), "a4_15m_pb": ("4h",), "a1_5m_dc": ("1h",), "a4_1h_st": ("4h",), "dc100_d1_4h": ("1d",)}


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
    tg = KINDS[kind]["target"]
    target = s.e20[i] if tg == "ema20" else s.vwap[i] if tg == "vwap" else (entry + tg * d if long else entry - tg * d) if tg else None
    if target is not None and ((long and target <= entry) or (not long and target >= entry)):
        return None
    if d / entry > MAX_STOP_FRAC:
        return None
    notional = min(RISK * st["eq"] / (d / entry), LEV * st["eq"])
    return {"side": side, "kind": kind, "entry": entry, "d": d, "stop": stop, "trail": stop, "extreme": entry, "target": target,
            "bars": 0, "t_open": s.t[i] + s.step, "notional": notional}


def _check_exit(p, s, k, sig):
    """Eine Kerze k gegen die offene Position prüfen. Gibt (Ausstiegskurs, Grund) oder None; verändert Trail/Zähler."""
    long = p["side"] == "long"
    if (s.l[k] <= p["trail"]) if long else (s.h[k] >= p["trail"]):
        return (min(p["trail"], s.o[k]) if long else max(p["trail"], s.o[k])), "stop"
    tg = p["target"]
    if tg is not None and ((s.h[k] >= tg) if long else (s.l[k] <= tg)):
        return tg, "ziel"
    tm = KINDS[p["kind"]]["trail"]
    if tm:
        p["extreme"] = max(p["extreme"], s.h[k]) if long else min(p["extreme"], s.l[k])
        new = p["extreme"] - tm * s.atr[k] if long else p["extreme"] + tm * s.atr[k]
        p["trail"] = max(p["trail"], new) if long else min(p["trail"], new)
    if p["kind"] == "flip":
        g2 = sig(s, k)
        if g2 and g2[0] != p["side"]:
            return s.c[k], "wechsel"
    if p["bars"] >= KINDS[p["kind"]]["maxbars"]:
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
        res = _check_exit(p, s, i, sig)
        if res:
            out.append(_close(st, p, s, i, *res))
            exited, reenter = True, res[1] == "wechsel"
    if st["pos"] is None and (not exited or reenter) and st["eq"] > 0:
        g = sig(s, i)
        if g:
            st["pos"] = _open(st, s, i, next_open, g)
    st["last_t"] = s.t[i]
    return out
