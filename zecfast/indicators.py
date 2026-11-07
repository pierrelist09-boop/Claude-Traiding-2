"""Grundbausteine: EMA, RSI (Wilder), ATR (Wilder), Bollinger-Breite. Alle Werte an Position i nutzen nur Kerzen bis i."""


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
    """Wilder-ATR; die ersten n Werte sind Einschwingzeit und tragen den ersten gültigen Wert."""
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, len(c))]
    out, a = [0.0] * len(c), 0.0
    for i in range(len(c)):
        if i < n:
            a = sum(tr[:i + 1]) / (i + 1)
        else:
            a = (a * (n - 1) + tr[i]) / n
        out[i] = a
    return out


def bollinger(c, n=20, k=2.0):
    """(obere Band, untere Band, Breite relativ zur Mitte) je Position."""
    up, lo, width = [], [], []
    for i in range(len(c)):
        w = c[max(0, i - n + 1):i + 1]
        m = sum(w) / len(w)
        sd = (sum((x - m) ** 2 for x in w) / len(w)) ** 0.5
        up.append(m + k * sd), lo.append(m - k * sd), width.append((2 * k * sd) / m if m else 0.0)
    return up, lo, width


def pct_rank(series, i, look=100):
    """Anteil der letzten `look` Werte vor i, die kleiner oder gleich series[i] sind (0..1)."""
    w = series[max(0, i - look):i]
    return sum(1 for v in w if v <= series[i]) / len(w) if w else 0.5
