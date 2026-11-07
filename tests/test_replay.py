"""Die Kerze-für-Kerze-Maschine (zecfast.core.on_candle) muss auf der Historie dieselben Trades liefern wie die Schleife in research/zec_test.py.
Läuft offline mit dem Cache unter .cache/ (vorher einmal research/zec_test.py ausführen)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from research import zec_test as T
from zecfast import core, data


class Replay(unittest.TestCase):
    def check(self, strat):
        tf, sig, _ = core.STRATS[strat]
        cs = data.candles("ZEC", tf, 5000, max_age=10 ** 12)
        s = core.Series(cs)
        ref = T.simulate(s, 210, s.n, sig)                       # (t_entry, R, t_exit, stop_anteil, cost, gross)
        st = core.new_state(strat)
        got = []
        for i in range(210, s.n):
            nxt = s.o[i + 1] if i + 1 < s.n else s.c[i]
            if i < s.n - 2 or st["pos"]:                          # die Referenz bricht Signale in den letzten 2 Kerzen ab
                got += core.on_candle(st, s, i, nxt)
        self.assertGreater(len(ref), 5, "zu wenig Referenz-Trades für einen Vergleich")
        self.assertEqual(len(got), len(ref), f"{strat}: Trades {len(got)} statt {len(ref)}")
        for a, b in zip(got, ref):
            self.assertEqual(a["t_open"], b[0])
            self.assertAlmostEqual(a["r"], b[1], places=9)

    def test_b20_5m(self):
        self.check("b20_5m")

    def test_f_5m(self):
        self.check("f_5m")

    def test_f_15m(self):
        self.check("f_15m")

    def test_p_15m(self):
        self.check("p_15m")

    def test_b20_15m(self):
        self.check("b20_15m")


class PaperOnly(unittest.TestCase):
    def test_kein_orderzugriff(self):
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "zecfast", "core.py")) as fh:
            src = fh.read().lower()
        for word in ("import urllib", "import requests", "import ccxt", "httpx", "socket", "api_key", "wallet", "private"):
            self.assertNotIn(word, src)


if __name__ == "__main__":
    unittest.main()
