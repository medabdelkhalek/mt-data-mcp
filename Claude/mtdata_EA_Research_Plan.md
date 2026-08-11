# mtdata Research Plan — Hunting New EA Ideas

**Purpose.** Use mtdata (emerzon/mt-data-mcp) as an isolated research sandbox
to find, test, and mostly *reject* candidate strategies, so that only ideas
with demonstrated edge ever become new EAs. This is a discovery pipeline, not
a trading system.

**Hard boundary (non-negotiable).** This work is completely separate from the
confirmed four-EA estate (Fast-Pass, XAU Alligator, US500 MondayRange, BTC
Alligator) and the Event-Risk Guardian. Nothing here touches those EAs, their
accounts, their config, or their compliance path. Different machine, different
(demo) credentials, different repo. Any strategy that survives this pipeline
becomes a brand-new EA with its own validation and — if it ever goes live —
its own compliance treatment, decided separately.

---

## 0. Environment & isolation (do once)

- Dedicated Windows VM (or spare machine). Not the trading VPS.
- A **demo** MT5 login only. Never the funded/acct1/acct2 credentials.
- `.env`: demo login; set `MTDATA_TRADE_GUARDRAILS_ENABLED=1` as a belt-and-
  braces measure even though we will not use `trade_*` at all.
- **Read-only discipline:** this entire plan uses only `data_*`, `regime_*`,
  `temporal_*`, `correlation_*`, `cointegration_*`, `forecast_*`,
  `patterns_*`, `market_scan`, `report_*`. The `trade_*` family is off-limits
  for the whole plan.
- Python 3.14, install per the repo's Windows quick-start. Verify with
  `mtdata-cli symbols_list --limit 5` before anything else.

**Golden rule for every finding below:** a tool output is a *hypothesis*, never
an edge. An edge is only a strategy that survives an out-of-sample test with
realistic costs. mtdata's own `strategy_backtest` covers only simple SMA/EMA/
RSI rules — so for anything more complex, the backtest is something we build
ourselves (Stage 4), not something the toolkit hands us.

---

## 1. Guiding constraints (define the search space first)

Write these down before touching data, so we hunt for something *usable*:

- **Instruments:** liquid, demo-available, and ones you'd actually want on a
  prop account later (majors, XAUUSD, US500, BTCUSD, a few index/FX others).
- **Style budget:** what kind of EA do you want to *add* to your line-up?
  Prefer a family **uncorrelated** to what you run. You already have trend
  (Alligators), breakout (MondayRange) and pullback (Fast-Pass). The valuable
  gaps are **mean-reversion / pairs** and **session/seasonal** strategies.
- **Holding horizon:** intraday, swing (H4-ish, like your others), or multi-day.
- **Hard filters:** must be automatable, must have a falsifiable entry (rules a
  computer can evaluate the same way every time), must survive spread/commission.

> Decision gate before Stage 2: pick **one** target family for this pass.
> **First target (fixed): regime-gated intraday mean-reversion** — your own
> market read (indices/FX range most of the time, so reversals are catchable
> when a regime filter confirms ranging and stands aside when trending). It's a
> family uncorrelated to your trend/breakout/pullback line-up, and mtdata's
> `regime_detect` is exactly the tool it needs. Statistical pairs
> (cointegration) and temporal/seasonal edges are the **secondary** targets for
> later passes — see section C of `mtdata_Three_Deliverables_Spec.md`, which this
> plan is aligned with.

---

## 2. Idea sourcing — primary hypothesis first, then secondary scans

This pass leads with the fixed primary hypothesis (2a). Only run the secondary
scans (2b, 2c) if the primary is killed, or later once it has resolved. One
target family per pass — don't chase all three at once.

### 2a. PRIMARY — regime-gated intraday mean-reversion (`regime_detect`)
This is hypothesis #1 and the go/kill gate for the whole pass.
- **The claim (yours):** indices/FX majors range most of the time, so reversals
  are catchable — but only when a regime filter confirms ranging; stand aside
  when trending (trending is when reversals get run over).
- **The strategy is NOT "trade a low timeframe."** Low timeframes have worse
  signal-to-noise and higher relative costs. The strategy is mean-reversion
  *gated* by regime.
- **First test (do this before anything else):** run `regime_detect` on EURUSD,
  **H1 vs H4**, over a meaningful history, and measure the **fraction of time in
  a ranging regime**.
  - **Proceed if:** the ranging fraction is high enough to justify a
    mean-reversion strategy AND regimes are persistent (not flipping every few
    bars).
  - **Kill/pivot if:** EURUSD is mostly trending, or regime labels only make
    sense in hindsight. Say so plainly — do not force the hypothesis to survive.
- If it proceeds: state a falsifiable rule (e.g. "fade a move stretched > z on
  the band, only while `regime_detect` = ranging; flat otherwise; exit at mean")
  and carry it into Stage 3.

### 2b. SECONDARY — cross-asset structure (`correlation_matrix`, `cointegration_test`)
Only if 2a dies or after it resolves. Correlation matrix across the instrument
set, then pairwise cointegration on the most related pairs.
- **Hypothesis if:** a pair passes cointegration on a training window AND the
  spread's mean-reversion half-life is short enough to trade. **Kill if:**
  cointegration holds on the full sample but breaks on a split half (the classic
  pairs overfit trap).

### 2c. SECONDARY — temporal / seasonal edges (`temporal_analyze`)
Only if the above are exhausted. Persistent session, day-of-week, or
time-of-day effects.
- **Hypothesis if:** the effect is large, consistent across years, and holds in
  a holdout period. **Kill if:** it appears in one year only or vanishes
  out-of-sample.

Output of Stage 2: for the primary, either a proceed decision with a falsifiable
mean-reversion rule, or a recorded kill with the ranging-fraction numbers behind
it. (If you fall through to secondaries, a shortlist of **at most 3** falsifiable
hypotheses.)

---

## 3. Cheap validation — split-sample sanity (before any EA code)

For each shortlisted hypothesis, the single most decisive test:

- **Split the history** into train / holdout (e.g. first 70% / last 30%, or
  odd vs. even years). Establish the effect on train, then **check it survives
  on the holdout you never looked at.**
- For regime-gated mean-reversion (primary): confirm the ranging fraction AND
  the reversion behaviour repeat on the holdout — not just the training window.
- For pairs: re-run `cointegration_test` on the holdout window independently.
- For temporal: confirm the seasonal effect's sign and size hold out-of-sample.
- Use `forecast_barrier_prob` to sanity-check whether a plausible TP/SL pair
  even has a favourable hit-probability geometry before you design exits.

> **Most ideas die here, and that is the point.** Anything that only works
> in-sample is noise. Do not rationalise a survivor by loosening the test.
> Budget: expect 2 of 3 hypotheses to fail this stage. If all 3 survive, be
> *more* suspicious, not less.

---

## 4. Honest backtest — build it yourself (the real gate)

Only for hypotheses that survived Stage 3. mtdata gives you clean data and
indicators; the strategy backtest is your own small harness (Python, in the
sandbox), because the built-in one is SMA/EMA/RSI-only.

Minimum standard for a backtest you'll trust:
- Realistic **spread + commission + slippage** modelled per instrument.
- **Out-of-sample / walk-forward**, not a single fitted period.
- Position sizing consistent with how a prop account would run it.
- Report: expectancy per trade, profit factor, max drawdown, trade count
  (enough trades to matter — a handful of wins proves nothing), and the
  equity curve on the holdout.
- A **parameter-sensitivity** check: nudge each parameter ±20%. If the edge
  evaporates, it was curve-fit — kill it.

**Go criterion to become an EA candidate:** positive expectancy after costs,
on out-of-sample data, stable under parameter perturbation, with enough trades
to be statistically meaningful. Nothing softer than that.

### Tooling for this stage (screening only — not final validation)

Don't hand-roll the harness from zero; use a purpose-built library, but know
exactly what it is and isn't for.
- **Backtesting.py** — default for the first honest test of a *single*
  hypothesis. Simple, event-driven, easy to model costs; its small surface area
  means fewer ways to fool yourself. Use it for hypothesis #1.
- **VectorBT** — only when sweeping many parameter combinations for the ±20%
  sensitivity check or scanning thresholds across the watchlist. Very fast, but
  its speed makes curve-fitting trivially easy — testing 10,000 variants and
  keeping the best-looking one is exactly the trap. If you use it, the
  out-of-sample holdout and sensitivity check matter *more*, not less.
- (Backtrader is the more realistic, event-driven third option, but it's more
  engine than research needs. Skip it here.)

**Hard boundary — Python here is SCREENING, never final proof.** These
libraries test a Python *sketch* of the idea, not a real EA. They exist to
decide, cheaply, whether an idea is worth building at all. The moment a
hypothesis survives and becomes an actual MQL5 EA (Stage 5), it graduates to
the **MT5 Strategy Tester** for real validation: *Every tick based on real
ticks*, on **FTMO-matched data** (tuning on one broker and running on another
is a known failure mode), with a forward-test split. No idea reaches a funded
account on a Python backtest alone — Python explores cheaply; the Strategy
Tester proves the real artifact.

---

## 5. Promotion to a new EA (separate track)

If — and only if — a hypothesis clears Stage 4:

- It becomes a **new, standalone EA**, written from scratch, with its own
  magic number and its own validation, exactly the way your confirmed EAs were
  built. It is not merged into the existing suite.
- Decide separately whether it ever goes on a funded account. If it does, it
  gets its own compliance treatment (the Guardian's contract is firm-agnostic,
  so a future EA can adopt it — but that's a fresh decision, documented then).
- Keep the research artifacts (the surviving backtest, the sensitivity table,
  the out-of-sample equity curve) as the evidence file for that EA.

---

## 6. Dashboards (optional, parallel, zero-risk)

Because mtdata exposes a local Web API + MCP tools, any of the read-only views
below can be built alongside the research without ever placing an order:
- Regime monitor across your instrument set.
- Correlation / cointegration heatmap (updates the Stage 2c picture live).
- Volatility & forecast board.
- Market scanner for surfacing new instruments worth a research pass.

These are useful in their own right and make great portfolio/CV pieces, fully
decoupled from the trading estate.

---

## Kill-criteria summary (pin this above the desk)

1. Works in-sample only → **dead.**
2. Cointegration/effect breaks on a split half → **dead.**
3. Too few trades to be significant → **dead.**
4. Edge disappears under ±20% parameter nudge → **dead.**
5. Positive only *before* costs → **dead.**
6. "The detector shows a pattern" (Elliott, candlesticks) with no
   out-of-sample expectancy behind it → **not an edge; dead as a signal.**

Only what survives all six earns an EA.
