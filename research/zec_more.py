#!/usr/bin/env python3
"""Zweite Welle: 10 weitere vorab festgelegte ZEC-Strategien (zecfast/core.py, STRATS) und die 5 ersten im Vergleich, mit derselben Prüfung:
chronologisch 50 % Training / 25 % Validierung / 25 % Test je Zeitrahmen, Kosten wie überall (0,045 % + 0,03 % je Seite, Funding), Hebel 10, 2 % Risiko.
Vorab festgelegt: 15 Versuche insgesamt, kein Nachjustieren. Kandidat nur, wenn Validierung UND Test Ø R > 0 und Test >= 30 Trades.
Aufruf: python3 research/zec_more.py [--write]"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from research import zec_test as T
from zecfast import core, data


def main():
    write = "--write" in sys.argv
    out = [f"# ZEC: Strategien im Vergleich (alle Wellen) ({time.strftime('%Y-%m-%d', time.gmtime())})\n",
           "Kosten je Seite 0,045 % Gebühr + 0,03 % Slippage, Funding, Hebel 10, 2 % Risiko je Trade, Einstieg zur Eröffnung der Folgekerze, Stop vor Ziel. "
           "Training 50 % / Validierung 25 % / Test 25 % (chronologisch je Zeitrahmen). Kandidat nur bei Ø R > 0 in Validierung UND Test und mindestens 30 Test-Trades. "
           "Bei 25 Versuchen ist mit einigen Zufallstreffern zu rechnen (Bonferroni: ein einzelner Treffer müsste deutlich stärker sein): ein einzelner Kandidat ist noch kein Beleg.\n",
           "| Konto | Zeitraum (Tage) | Training n / Ø R | Validierung n / Ø R | Test n / Ø R | Test PF | Test-Konto (Rückgang) | Urteil |", "|---|---|---|---|---|---|---|---|"]
    cache = {}
    for strat, (tf, sig, desc) in core.STRATS.items():
        for need in (tf,) + core.NEEDS.get(strat, ()):
            if need not in cache:
                cache[need] = core.Series(data.candles("ZEC", need, 5000, max_age=10 ** 12))
        s = core.Series(data.candles("ZEC", tf, 5000, max_age=10 ** 12)) if strat in core.NEEDS else cache[tf]
        for need in core.NEEDS.get(strat, ()):
            core.link(s, need, cache[need])
        a, b = int(s.n * 0.5), int(s.n * 0.75)
        days = (s.t[-1] - s.t[0]) / 86_400_000
        tr, va, te = T.simulate(s, 210, a, sig), T.simulate(s, a, b, sig), T.simulate(s, b, s.n, sig)
        st, sv, se = T.stats(tr), T.stats(va), T.stats(te)
        ac = T.account(te, s.t[b], s.t[-1])
        fm = lambda d: f"{d['n']} / {d['avg']:+.2f}" if d["n"] else "0 / –"
        ok = sv["n"] and se["n"] and sv["avg"] > 0 and se["avg"] > 0
        verdict = ("**Kandidat**" if ok and se["n"] >= 30 else "positiv, aber zu wenig Test-Trades" if ok else "kein Vorteil")
        out.append(f"| {strat} ({desc}) | {days:.0f} | {fm(st)} | {fm(sv)} | {fm(se)} | {se['pf']:.2f} | {ac['ret'] * 100:+.0f} % ({ac['dd'] * 100:.0f} %) | {verdict} |")
    text = "\n".join(out)
    print(text)
    if write:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ergebnis_zec_more.md"), "w") as fh:
            fh.write(text + "\n")


if __name__ == "__main__":
    main()
