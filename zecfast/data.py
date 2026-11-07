"""ZEC-Kerzen von Hyperliquid (öffentlich, kein Schlüssel). Eigener Cache unter .cache/, pro Datei die letzten 5000 Kerzen.
Achtung: Cache-Dateien nie mit kleinerem n überschreiben (Lehre aus dem ersten Repo): der Dateiname enthält deshalb n."""
import json
import os
import time
import urllib.request

HL = "https://api.hyperliquid.xyz/info"
MS = {"1m": 60_000, "5m": 300_000, "15m": 900_000, "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}
CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cache")


def post(body, tries=6):
    req = urllib.request.Request(HL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    for a in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except Exception:
            time.sleep(2.5 * (a + 1))
    raise RuntimeError("Hyperliquid nicht erreichbar")


def candles(coin, interval, n=5000, max_age=6 * 3600):
    """Letzte n GESCHLOSSENE Kerzen als Liste von Dicts {t,T,o,h,l,c,v}."""
    path = os.path.join(CACHE, f"{coin}_{interval}_{n}.json")
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < max_age:
        return json.load(open(path))
    now = int(time.time() * 1000)
    rows = post({"type": "candleSnapshot", "req": {"coin": coin, "interval": interval, "startTime": now - n * MS[interval], "endTime": now}})
    out = [{"t": r["t"], "T": r["T"], "o": float(r["o"]), "h": float(r["h"]), "l": float(r["l"]), "c": float(r["c"]), "v": float(r["v"])} for r in rows if r["T"] < now]
    os.makedirs(CACHE, exist_ok=True)
    json.dump(out, open(path, "w"))
    time.sleep(0.6)
    return out
