"""
Suite Regime Detector (CLI)
---------------------------
Daily read on whether XAU / BTC / US500 are TRENDING (favorable) or
CONSOLIDATING (sit-out), in the language the EAs use (Alligator on the EA
trend timeframe + D1 ADX/direction).

Uses: 1) DEPLOY timing — start a challenge when XAU+BTC are trending.
      2) FUNDED easy-mode hint — which markets are in chop.

Run via regime_detector.bat or: python regime_detector.py
Reads the running MetaTrader 5 terminal directly (FTMO-Demo). Shared logic in
regime_core.py (also powers the MrUnderdog Cockpit web dashboard in cockpit/).
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from datetime import datetime
import MetaTrader5 as mt5
from regime_core import MARKETS, classify, suite_light, monday_status


def main():
    if not mt5.initialize():
        print("ERROR: could not connect to MetaTrader 5 terminal. Open MT5 and retry.")
        return
    ai = mt5.account_info()
    print("=" * 74)
    print(f"  MRUNDERDOG COCKPIT · REGIME    {datetime.now():%Y-%m-%d %H:%M}   "
          f"acct {ai.login if ai else '?'} {ai.server if ai else ''}")
    print("=" * 74)
    print(f"  {'Mkt':<6}{'Verdict':<14}Gate stack")
    print("  " + "-" * 70)
    rows = []
    for label, sym, ttf, _magic, _desc in MARKETS:
        if label == "US500":
            ms = monday_status(sym)
            if ms and ms["forming"]:
                print(f"  US500 {ms['verdict']:<14}Mon {ms['monday']} building "
                      f"({ms['rng_pts']:.0f}pts so far) · {ms['status']}")
            elif ms:
                q = "OK" if ms["qualifies"] else "<min"
                print(f"  US500 {ms['verdict']:<14}Mon {ms['monday']} {ms['low']:.0f}-{ms['high']:.0f} "
                      f"({ms['rng_pts']:.0f}pts {q}) · {ms['status']}")
            continue
        r = classify(label, sym, ttf)
        if r is None:
            print(f"  {label:<6}(no data)"); continue
        rows.append(r)
        gs = (f"allig={r['allig']} bias={r['bias_dir']}"
              + (f" alma={r['alma_dir']}" if r['alma_dir'] else "")
              + f" ao={r['ao_dir']}")
        print(f"  {label:<6}{r['verdict']:<14}{gs}")
    print("  " + "-" * 70)

    light, n, msg = suite_light(rows)
    print(f"  SUITE: {light}  - {msg}   (XAU+BTC armed: {n}/2)")
    waits = [r["label"] for r in rows if not r["favorable"]]
    runs = [r["label"] for r in rows if r["favorable"]]
    if waits:
        print(f"  Deploy: hold until {', '.join(waits)} arm (all gates aligned: "
              f"Alligator open + D1 bias + ALMA agree).")
    else:
        print("  Deploy: XAU+BTC armed - green light (still clear the DD gate).")
    print(f"  Funded easy-mode: RUN [{', '.join(runs) or 'none'}]  "
          f"consider PAUSE [{', '.join(waits) or 'none'}]")
    print("=" * 74)
    mt5.shutdown()


if __name__ == "__main__":
    main()
