# mtdata — Opening Prompts (one per deliverable)

Rules for all three sessions:
- Each deliverable gets its OWN session. Don't let one drift into another's work.
- The MCP is a confirmed demo account. Even though `trade_*` write tools exist,
  do NOT use any of them in any of these sessions — all findings come from
  historical/live *data*, never from placed trades.
- Read-only tools only: `data_*`, `regime_*`, `temporal_*`, `correlation_*`,
  `cointegration_*`, `forecast_*`, `patterns_*`, `market_scan`, `news`, `report_*`.
- Hard boundary: nothing here touches the confirmed estate (Fast-Pass, XAU
  Alligator, US500 MondayRange, BTC Alligator) or the Event-Risk Guardian.
- Timeframes: default H4; H1 and D1 as toggles; nothing below H1.
- Prove everything on EURUSD first, then scale.
- Effort: xhigh for the statistical/backtest reasoning (B's clustering, C's
  Stage 2–4); high is fine for A's setup and UI work.

---

## A — Pre-Trade Context Panel (live dashboard)

> Read `mtdata_Three_Deliverables_Spec.md`, section A, in full — it governs this
> session. Confirm you've read it by restating the one decision this panel is
> meant to change, and the three tiles it's allowed to have.
>
> This is a **read-only live context panel** for my own manual trading, isolated
> from my trading estate. Demo/data login only; no `trade_*` tools. It shows
> context before a manual trade — regime, volatility, event proximity — and must
> NOT show price forecasts or pattern "signals" (context, not calls).
>
> The repo ships a Web UI (`webui/`) and Web API (`docs/WEB_API.md`). First:
> 1. Tell me how to run the Web UI + Web API locally, and inventory which of the
>    three tiles (regime H4+D1 via `regime_detect`; volatility H1+D1;
>    event-proximity via `news`) the bundled UI already covers vs. what I'd need
>    to add on top of the Web API.
> 2. Build **EURUSD only**, H4 default with H1/D1 toggle, three tiles, nothing
>    else. Use what's already there; build only the gaps.
>
> **Stop after the EURUSD panel works** — don't scale to other symbols until I
> confirm it changes my take/skip/size decision cleanly.

---

## B — EA-Refinement Report (periodic analysis)  ← recommended first

> Read `mtdata_Three_Deliverables_Spec.md`, section B, in full — it governs this
> session. Confirm you've read it by restating the decision this report changes
> and the four-part rule for when a filter is justified.
>
> This is a **historical analysis**, not a live dashboard, and not connected to
> my running EAs in any way — I will provide exported trade history; you analyse
> it. Demo/data login only; no `trade_*` tools. Read-only.
>
> Goal: for one of my live EAs, find the conditions where it systematically
> loses, so a *future version* can filter them out. I'll give you the EA's
> historical trades (symbol, direction, open/close time, entry, exit, P/L,
> R-multiple). Start with **one EA on EURUSD-class data** to prove the method.
>
> Do this:
> 1. Tag each historical trade with the **regime at entry** (`regime_detect` on
>    the EA's symbol/timeframe).
> 2. Produce expectancy (win rate, avg R, expectancy) split by **regime**, by
>    **session/day-of-week** (`temporal_analyze`), and by **volatility bucket**
>    at entry.
> 3. Flag any losing cluster, and apply the spec's four-part decision rule
>    (material sample, clearly negative in-cluster vs positive elsewhere,
>    improves expectancy on a **holdout** slice, and is a rule an EA can evaluate
>    live) to say yes/no on whether a filter is justified.
>
> Any filter you find goes into a **re-validated new EA version**, never a
> hot-patch — say so in your output. **Stop after the one-EA report** and walk me
> through it before we generalise.

---

## C — New-Strategy Research Funnel (discovery)

> Read `mtdata_Three_Deliverables_Spec.md`, section C, AND
> `mtdata_EA_Research_Plan.md` in full — together they govern this session.
> Confirm by restating the six kill-criteria and the primary hypothesis.
>
> This is the **new-EA discovery funnel**. Demo/data login only; no `trade_*`
> tools; read-only. Anything that survives becomes a brand-new standalone EA
> built and validated separately — nothing here merges into my existing estate.
>
> Primary hypothesis #1: **regime-gated intraday mean-reversion** on FX/indices —
> markets range most of the time, so reversals are catchable, but only when a
> regime filter confirms ranging (stand aside when trending).
>
> Do **only Stage 2's first go/kill gate** this session:
> 1. Using `regime_detect` on **EURUSD, H1 vs H4**, quantify what fraction of
>    time EURUSD is actually in a ranging regime, over a meaningful history.
> 2. Tell me straight: is the ranging fraction high enough to justify a
>    mean-reversion strategy, or does the premise fail? If it fails, say so and
>    propose whether to kill or pivot — do not force the hypothesis to survive.
>
> **Stop there.** Do not define entry rules, backtest, or touch Stage 3+ until I
> see the ranging-fraction result and approve proceeding. One stage at a time.

---

## After each "stop"

Bring me the output — the panel behaviour (A), the expectancy tables (B), or the
ranging-fraction numbers (C) — and we'll decide together whether to proceed,
adjust, or kill. Every stage is behind a sign-off, same discipline as the whole
project. Nothing jumps from a tool output straight to a live account.
