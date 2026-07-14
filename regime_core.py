"""
regime_core.py — shared regime logic for the suite (CLI + dashboard).
Classifies XAU / BTC / US500 as trending vs consolidating in the EAs' own
language: Bill Williams Alligator on the EA trend timeframe + D1 ADX/direction.
Pure functions, no side effects. Caller must mt5.initialize() first.
"""
import numpy as np, talib, MetaTrader5 as mt5
from datetime import datetime, timezone

ADX_TREND = 22.0     # >= = real trend strength
ADX_CHOP  = 18.0     # <  = dead / consolidating
SEP_ATR   = 0.40     # Alligator "open" if line spread > this * ATR

# (label, symbol, trend timeframe, EA magic, description)
MARKETS = [
    ("XAU",   "XAUUSD",     mt5.TIMEFRAME_H4, 442288, "Alligator H4 trend-follower"),
    ("BTC",   "BTCUSD",     mt5.TIMEFRAME_H6, 888999, "Alligator H6 trend-follower"),
    ("US500", "US500.cash", mt5.TIMEFRAME_H4, 202500, "Monday-range weekly breakout"),
]


def smma(x, n):
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    out[n - 1] = x[:n].mean()
    for i in range(n, len(x)):
        out[i] = (out[i - 1] * (n - 1) + x[i]) / n
    return out


def alligator_lines(high, low):
    """Return forward-displaced Bill Williams Alligator lines, bar-aligned."""
    med = (high + low) / 2.0
    jaw, teeth, lips = smma(med, 13), smma(med, 8), smma(med, 5)
    aj = np.full(len(med), np.nan); at = np.full(len(med), np.nan); al = np.full(len(med), np.nan)
    aj[8:] = jaw[:-8]; at[5:] = teeth[:-5]; al[3:] = lips[:-3]
    return aj, at, al


def alligator_state(high, low, atr):
    aj, at, al = alligator_lines(high, low)
    j, t, l = aj[-1], at[-1], al[-1]
    if np.isnan([j, t, l]).any() or atr <= 0:
        return "n/a", 0.0
    spread = (max(j, t, l) - min(j, t, l)) / atr
    if l > t > j and spread > SEP_ATR:
        return "open(bull)", spread
    if l < t < j and spread > SEP_ATR:
        return "open(bear)", spread
    return "intertwined", spread


def rates(symbol, tf, n):
    r = mt5.copy_rates_from_pos(symbol, tf, 0, n)
    if r is None or len(r) < 60:
        return None
    return r


TF_NAME = {mt5.TIMEFRAME_H1: "H1", mt5.TIMEFRAME_H2: "H2", mt5.TIMEFRAME_H3: "H3",
           mt5.TIMEFRAME_H4: "H4", mt5.TIMEFRAME_H6: "H6", mt5.TIMEFRAME_D1: "D1"}

# Each Alligator EA's actual multi-timeframe gate stack (from the EA source).
EA_SPEC = {
    "XAU": dict(trend_tf=mt5.TIMEFRAME_H4, entry_tf=mt5.TIMEFRAME_H1,
                alma_tf=mt5.TIMEFRAME_H2, alma=(4, 0.80, 6.0),
                desc="Alligator H4→H1 · ALMA H2 · D1 bias"),
    "BTC": dict(trend_tf=mt5.TIMEFRAME_H6, entry_tf=mt5.TIMEFRAME_H3,
                alma_tf=None, alma=None, desc="Alligator H6→H3 · D1 bias"),
}


def alma(price, window=4, offset=0.80, sigma=6.0):
    if len(price) < window:
        return np.nan
    m = offset * (window - 1); s = window / sigma
    w = np.array([np.exp(-((i - m) ** 2) / (2 * s * s)) for i in range(window)])
    w /= w.sum()
    return float(np.dot(w, price[-window:]))


def awesome_osc(high, low):
    med = (high + low) / 2.0
    return talib.SMA(med, 5) - talib.SMA(med, 34)


def classify(label, symbol, ttf=None):
    spec = EA_SPEC.get(label, dict(trend_tf=ttf or mt5.TIMEFRAME_H4,
                                   entry_tf=mt5.TIMEFRAME_H1, alma_tf=None, alma=None, desc=""))
    d = rates(symbol, mt5.TIMEFRAME_D1, 120)
    tt = rates(symbol, spec["trend_tf"], 220)
    if d is None or tt is None:
        return None
    dc = d["close"].astype(float)
    sma5 = talib.SMA(dc, 5); ema50 = talib.EMA(dc, 50); rsi = talib.RSI(dc, 14)
    bias_dir = "up" if dc[-1] > sma5[-1] else "down"

    th, tl = tt["high"].astype(float), tt["low"].astype(float)
    atr = talib.ATR(th, tl, tt["close"].astype(float), 14)[-1]
    allig, spread = alligator_state(th, tl, atr)
    trend_open = allig in ("open(bull)", "open(bear)")
    allig_dir = "up" if allig == "open(bull)" else ("down" if allig == "open(bear)" else "none")

    alma_dir = None
    if spec["alma_tf"] is not None:
        ar = rates(symbol, spec["alma_tf"], 60)
        if ar is not None:
            ac = alma(ar["close"].astype(float), *spec["alma"])
            ao_ = alma(ar["open"].astype(float), *spec["alma"])
            alma_dir = "up" if ac > ao_ else "down"

    ao_dir = None; ao_val = 0.0
    et = rates(symbol, spec["entry_tf"], 120)
    if et is not None:
        ser = awesome_osc(et["high"].astype(float), et["low"].astype(float))
        ao_val = float(ser[-1]); ao_dir = "up" if ser[-1] > ser[-2] else "down"

    dirn = allig_dir if trend_open else bias_dir
    aligned = trend_open and (bias_dir == allig_dir) and (alma_dir is None or alma_dir == allig_dir)

    # gate checklist (each: name, shown value, agrees-with-trend?)
    gates = [(f"Trend {TF_NAME[spec['trend_tf']]} Alligator", allig,
              trend_open)]
    if alma_dir is not None:
        gates.append((f"ALMA {TF_NAME[spec['alma_tf']]}", alma_dir, alma_dir == allig_dir))
    gates.append(("D1 bias (SMA5)", bias_dir, bias_dir == allig_dir if trend_open else False))
    gates.append((f"Entry {TF_NAME[spec['entry_tf']]} AO",
                  f"{ao_dir or 'n/a'} ({ao_val:+.0f})", ao_dir == allig_dir if ao_dir else False))

    if not trend_open:
        verdict, regime = "NO TREND", "CONSOLIDATION"
    elif aligned:
        verdict = "ARMED " + ("LONG" if allig_dir == "up" else "SHORT")
        regime = "TREND_UP" if allig_dir == "up" else "TREND_DOWN"
    else:
        verdict, regime = "MIXED", "TRANSITION"

    return dict(label=label, symbol=symbol, regime=regime, direction=dirn, verdict=verdict,
                allig=allig, allig_dir=allig_dir, spread=float(spread), trend_open=trend_open,
                bias_dir=bias_dir, alma_dir=alma_dir, ao_dir=ao_dir, ao_val=ao_val,
                aligned=aligned, favorable=aligned, gates=gates,
                rsi=float(rsi[-1]), close=float(dc[-1]), sma5=float(sma5[-1]),
                ema50=float(ema50[-1]), desc=spec["desc"])


def suite_light(rows):
    drv = [r for r in rows if r["label"] in ("XAU", "BTC")]
    n = sum(1 for r in drv if r["favorable"])
    if n == 2:
        return "GREEN", n, "Drivers trending — favorable window to DEPLOY"
    if n == 1:
        return "AMBER", n, "One driver undecided — WAIT for both to define"
    return "RED", n, "Drivers in chop — HOLD (synchronized consolidation)"


def monday_status(symbol, min_range_pts=5200.0, rr=2.1):
    """MondayRange EA state: this week's Monday H/L, whether the range qualifies
    (>= MinRangePips), where price sits, and the setup verdict. Strategy-bound —
    no Alligator/ADX (those belong to the trend EAs).

    The range is only valid once Monday's daily bar CLOSES (the EA trades it
    Tue-Fri). If Monday is still the current forming bar, report FORMING instead
    of judging an incomplete range."""
    r = rates(symbol, mt5.TIMEFRAME_D1, 60)
    if r is None:
        return None
    si = mt5.symbol_info(symbol)
    point = si.point if si and si.point else 0.01

    def wd(bar):
        return datetime.fromtimestamp(int(bar["time"]), tz=timezone.utc).weekday()

    mon = None
    for bar in r:                       # most recent Monday in the window
        if wd(bar) == 0:
            mon = bar
    if mon is None:
        return None
    # Monday is still forming if its bar is the current (last) bar in the series.
    forming = int(mon["time"]) == int(r[-1]["time"])

    mh, ml = float(mon["high"]), float(mon["low"])
    rng = mh - ml; rng_pts = rng / point
    tick = mt5.symbol_info_tick(symbol)
    px = float(tick.bid) if tick and tick.bid else float(r["close"][-1])
    pos_in = max(0.0, min(100.0, (px - ml) / rng * 100 if rng > 0 else 50.0))
    mlabel = datetime.fromtimestamp(int(mon["time"]), tz=timezone.utc).strftime("%b %d")
    direction = "up" if px > (mh + ml) / 2 else "down"

    if forming:                          # range not established yet
        return dict(label="US500", symbol=symbol, high=mh, low=ml, close=px, rng=rng,
                    rng_pts=rng_pts, min_pts=min_range_pts, qualifies=None, rr=rr,
                    status="Monday session — range still building",
                    verdict="FORMING", favorable=False, pos_in=pos_in,
                    direction=direction, monday=mlabel, forming=True)

    qualifies = rng_pts >= min_range_pts
    if px > mh:
        status, zone = "ABOVE — breakout/sweep up", "trigger"
    elif px < ml:
        status, zone = "BELOW — breakout/sweep down", "trigger"
    else:
        status, zone = "inside range", "armed"
    if not qualifies:
        verdict, favorable = "NO SETUP (range < min)", False
    elif zone == "trigger":
        verdict, favorable = "TRIGGER ZONE", True
    else:
        verdict, favorable = "ARMED", False
    return dict(label="US500", symbol=symbol, high=mh, low=ml, close=px, rng=rng,
                rng_pts=rng_pts, min_pts=min_range_pts, qualifies=qualifies, rr=rr,
                status=status, verdict=verdict, favorable=favorable, pos_in=pos_in,
                direction=direction, monday=mlabel, forming=False)


def ohlc_frame(symbol, ttf, n=45):
    """Plain candlesticks for the breakout chart (no trend overlays)."""
    r = rates(symbol, ttf, max(n, 60))
    if r is None:
        return None
    return dict(time=r["time"][-n:], open=r["open"][-n:].astype(float),
                high=r["high"][-n:].astype(float), low=r["low"][-n:].astype(float),
                close=r["close"][-n:].astype(float))


def chart_frame(symbol, ttf, n=120):
    """Trend-TF candles + EMA50 + Alligator lines for plotting."""
    r = rates(symbol, ttf, n + 60)
    if r is None:
        return None
    h, l, c = r["high"].astype(float), r["low"].astype(float), r["close"].astype(float)
    aj, at, al = alligator_lines(h, l)
    ema50 = talib.EMA(c, 50)
    return dict(time=r["time"][-n:], open=r["open"][-n:].astype(float),
                high=h[-n:], low=l[-n:], close=c[-n:],
                jaw=aj[-n:], teeth=at[-n:], lips=al[-n:], ema50=ema50[-n:])
