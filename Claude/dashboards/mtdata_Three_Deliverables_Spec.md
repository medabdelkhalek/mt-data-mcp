# mtdata Analytics — Three Deliverables

Three tools built on the mtdata MCP, each tied to a decision. If a piece of any
of them doesn't change a trade you take, an EA parameter you set, or a strategy
you build or kill — it's decoration, cut it.

**Hard boundary (all three).** Completely separate from the confirmed estate
(Fast-Pass, XAU Alligator, US500 MondayRange, BTC Alligator) and the Event-Risk
Guardian. Read-only against the demo/data MT5 login. No `trade_*` tools. B
*analyses* the live EAs' trade history; it never connects to them, signals them,
or touches their accounts.

**Honest framing.** These are decision-support tools, not edge. They remove
unforced errors and show where to look. The money still comes from the strategy
and the discipline. None of them "makes money" on its own.

**Shared conventions.**
- Timeframes: default H4; H1 and D1 as toggles/inputs; nothing below H1.
  (Regime reads flip to noise on low timeframes; costs dominate low-timeframe
  edge — see C.)
- Symbols: prove each tool on EURUSD first, then scale to the watchlist
  (BTCUSD, ETH, EURUSD, GBPUSD, AUDUSD, USDJPY, USDCHF, USDCAD, DXY, XAUUSD,
  XAGUSD, USOIL, US500, NAS100, US30, GER40, UK100, EU50).
- Session/clock note for scale-up: indices/commodities have session breaks,
  crypto is 24/7 — the "D1 boundary" is not one clock across all symbols.
  Fine for EURUSD now; handle explicitly when scaling.

---

# A — Pre-Trade Context Panel  (LIVE dashboard)

**What it is.** A small live screen you glance at before taking a *manual*
trade. It does not tell you when to enter — it stops you entering into a
headwind and sizes you sanely.

**The decision it changes:** take / skip / size a manual trade.

**Tiles (each must change that decision, or it's cut):**
1. **Regime** (`regime_detect`, H4 + D1): trending / ranging / crisis, per the
   symbol you're about to trade. Rule of thumb surfaced on the tile: don't fade
   a trending market; don't trend-chase a ranging one.
2. **Volatility** (`forecast_volatility_estimate` / ATR, H1 + D1): current vs.
   recent range. Drives stop distance and position size — a violent day needs a
   wider stop and smaller size; a dead day may have no range to capture.
3. **Event proximity** (`news`): what restricted/high-impact events are near, so
   a manual trade isn't opened into one. (Read-only awareness — NOT the
   Guardian; this never enforces anything.)

**Explicitly excluded:** price forecasts, pattern signals, anything predictive.
The panel gives *context*, not calls — a forecast tile would invite you to
outsource the entry decision to a model that can't make it.

**Build path.** EURUSD, three tiles, H4 default with H1/D1 toggle. Use the
bundled Web UI where it already covers a tile; build only the gaps on top of
the Web API. Prove it, then parameterise symbol and scale.

**Done when:** you can pull up EURUSD before a manual trade and, in one glance,
know the regime, whether volatility argues for a different size, and whether an
event is too close. Nothing more.

---

# B — EA-Refinement Report  (periodic ANALYSIS, not live)

**What it is.** A report you run periodically (monthly, or after a losing
stretch) over the *historical* trades of your live EAs, to find conditions where
each EA systematically bleeds — so the *next version* of that EA can filter them
out. This is the highest-expectancy use: improving proven EAs beats hunting new
ones.

**The decision it changes:** what filter/parameter goes into the next version of
an existing EA.

**Inputs.** Your EAs' historical trade list (from your own records / MT5 history
export — provided to the analysis, not pulled live from the running EAs).
Per trade: symbol, direction, open/close time, entry, exit, P/L, R-multiple.

**Analysis steps (per EA):**
1. **Regime tagging** (`regime_detect` on the EA's symbol/timeframe): label each
   historical trade with the regime *at the moment it opened*.
2. **Loss clustering:** win rate, avg R, and expectancy split by regime. The
   money question: does this EA's expectancy go negative in a specific regime
   (e.g. Alligator trend-follower losing in "ranging")?
3. **Session/temporal split** (`temporal_analyze`): same expectancy breakdown by
   session and day-of-week. (Directly relevant to MondayRange — is the
   day-of-week edge still there, or decaying?)
4. **Volatility bucket:** expectancy in low / normal / high vol at entry — does
   the EA only work in a vol band?

**Output.** A short table per EA: expectancy by regime / session / vol bucket,
with the losing clusters flagged.

**Decision rule (when a filter is worth adding):**
- The losing cluster must be **material** (enough trades to be significant — a
  handful proves nothing) AND
- expectancy in that cluster is **clearly negative** while positive elsewhere AND
- filtering it out would have **improved out-of-sample expectancy** (check on a
  holdout slice of the trade history, not the whole thing) AND
- the filter is a rule the EA can evaluate live (regime/session/vol at entry).
- If all four hold → candidate filter for the next EA version. Otherwise →
  leave the EA alone. Do NOT curve-fit a filter to erase every past loss.

**Critical guardrail.** Any filter this suggests goes into a **new version of
the EA, re-validated from scratch** — never hot-patched into a running live EA,
never applied without its own backtest. B *identifies*; it does not *modify*.

**Done when:** for each live EA you have a regime/session/vol expectancy table
and a clear yes/no on whether a filter is justified — with the evidence to back
it.

---

# C — New-Strategy Research Funnel  (the discovery pipeline)

**What it is.** The funnel from `mtdata_EA_Research_Plan.md`, with the primary
first hypothesis fixed to the idea you raised from your own market read.

**The decision it changes:** build a new EA, or kill the idea.

**Primary hypothesis (hypothesis #1): regime-gated intraday mean-reversion.**
Your observation — indices and FX majors range most of the time, so clean swings
are rare and reversals are more catchable on lower timeframes. The strategy that
expresses this is *not* "trade a low timeframe" (low timeframes have worse
signal-to-noise and higher relative costs) — it's **mean-reversion that only
fires when a regime filter confirms the market is actually ranging, and stands
aside when it's trending** (trending is when reversals get run over).

**Stage 2 first test (the go/kill gate for this hypothesis):**
1. **Quantify the claim** (`regime_detect`, EURUSD, H1 vs H4): what fraction of
   time is EURUSD actually in a ranging regime? If it's as high as the
   hypothesis assumes, proceed. If it's mostly trending, the premise is wrong —
   kill or pivot.
2. If ranging fraction is high: define a falsifiable mean-reversion rule
   (e.g. fade stretched moves — z-score / band distance — only while
   `regime_detect` says ranging; flat/stand-aside otherwise).

**Then the standard funnel (unchanged from the research plan):**
- Stage 3 — split-sample: does the ranging fraction AND the reversion edge hold
  out-of-sample? Most ideas die here; that's the point.
- Stage 4 — honest backtest (mtdata's is SMA/EMA/RSI only, so use a real
  library: **Backtesting.py** for the single-hypothesis test, **VectorBT** only
  for parameter sweeps — its speed makes curve-fitting easy, so the holdout
  matters more, not less): realistic spread+commission+slippage, walk-forward,
  enough trades, parameter ±20% sensitivity. **This is where low-timeframe cost
  drag gets exposed** — a reversal system positive before costs and negative
  after is dead (kill-criterion 5). These libraries are **screening only**: they
  test a Python sketch, not a real EA.
- Stage 5 — only a survivor becomes a new standalone EA, built and validated
  from scratch in the **MT5 Strategy Tester** (Every tick based on real ticks,
  FTMO-matched data, forward-test split) — a Python backtest never validates a
  funded EA. Its own magic, its own separate compliance decision.

**Secondary hypotheses (only if #1 dies or after it resolves):** cointegration
pairs; temporal/seasonal edges. One target family per pass.

**Kill-criteria (pinned):** in-sample only → dead; breaks on split-half → dead;
too few trades → dead; dies under ±20% param nudge → dead; positive only before
costs → dead; "a detector shows a pattern" with no OOS expectancy → dead.

**Done when:** hypothesis #1 has either produced a costed, out-of-sample-positive
backtest worth turning into an EA, or been cleanly killed with the reason
recorded.

---

## Sequencing note (building in parallel)

The three share one tool and one demo login but are three separate tracks with
three separate goals — don't let a session drift between them. Suggested
priority if attention is limited: **B is the shortest path to money** (sharpens
assets you already trust), **A is quick and reduces unforced manual errors**,
**C is the highest-upside but longest and most likely to end in a justified
"no."** All obey the same hard boundary: read-only, demo/data login, nothing
wires back into the live estate.
