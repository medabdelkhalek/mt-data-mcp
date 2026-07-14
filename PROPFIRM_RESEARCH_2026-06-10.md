# Prop-firm selection for the validated MT5 EA suite — research report

**Verified 2026-06-10.** Researcher context: Moroccan passport, swap-free (Islamic) account REQUIRED.
Method: every rule claim checked against the firm's own FAQ/help-center pages where reachable
(marked **[P]** = primary source fetched/quoted, **[S]** = secondary/review source, needs the
support-chat confirmation in §4 before paying). Web evidence as of today; the landscape changes
monthly — re-verify anything older than ~60 days before acting.

> **What I could not do:** open live support chats. §4 is the exact script to run yourself
> (~20 min per firm) before purchase. Treat every **[S]** fact as "probable, unconfirmed".

> **2026-06-14 update:** verdicts below are written for the **full suite** (BTC+XAU+US500). For
> per-bot rosters (suite vs gold-only) and the expansion plan, see the companion
> [FIRM_ROSTER_by_bot.md](FIRM_ROSTER_by_bot.md). Key revision: **FundedNext** is blacklisted for the
> SUITE (no weekend BTC) but **whitelisted for the gold-only bot** (gold needs no weekend crypto;
> news = quantifiable haircut, not breach; new 3%-risk/70%-margin/1:10-gold rules don't bind 0.30%
> risk; most payout-proven firm at $284.6M). WSFunded and Lark added to the rejected list.

---

## 0. TL;DR

- **Morocco is not restricted at any surviving firm.** Swap-free exists at all three survivors.
- **11 of 14 candidates die on hard requirements** — mostly funded-stage news bans, daily DD < 4.5%,
  trailing drawdown, or no weekend BTC.
- Survivors: **FTMO (Swing)** — known-good baseline; **BrightFunded (2-Step Classic)** — only firm
  offering a single $200k with FTMO-shaped DD semantics + swap-free + weekend BTC, but it's a
  Sept-2023 firm with a funded-stage news *profit-deduction* rule (soft breach, quantifiable);
  **City Traders Imperium** — dark-horse backup (founded 2018, MT5, Islamic accounts, 5%/10% static),
  under-verified.
- **Recommended structure: B** — FTMO Swing $100k (swap-free) + BrightFunded 2-Step Classic $100k
  (+swap-free add-on), suite mirrored at identical %-risk on both. ≈ **€1,085 now**; FastPass's
  $100k account later goes to whichever of BrightFunded/CTI has behaved (≈ €545). Detail in §2.

---

## 1. Comparison table — hard requirements

Hard requirements: (1) MT5 today, (2) self-written EAs both stages, (3) swap-free, (4) news trading
both stages, (5) weekend holding + weekend BTC, (6) FTMO-compatible DD semantics (≥4.5% usable daily,
static ≥5.3% total), (7) US500+XAU+BTC, (8) no profit-clustering consistency rule.

| Firm | MT5 | EAs | Swap-free | News (funded) | Weekend + BTC wknd | DD semantics | Instruments | Consistency | VERDICT |
|---|---|---|---|---|---|---|---|---|---|
| **FTMO (Swing)** | ✅ [P] | ✅ self-written OK [P] | ✅ (held already) | ✅ Swing: unrestricted [P¹] | ✅ + crypto wknd (maint. windows) [P¹·S] | ✅ user-validated baseline | ✅ | ✅ none | **PASS** |
| **BrightFunded (2-Step Classic)** | ✅ since 2025-09, not US/UAE [S] | ✅ no pre-approval; no HFT/grid/latency [P²] | ✅ add-on +10% fee, checkout-only [P³] | ⚠️ eval: free; funded: ±5 min red-news executions → profit deducted, soft breach, 48 h-TP exempt [P⁴] | ✅ holding [P⁵]; no o/n close [P⁶]; BTC 24/7 [S] | ✅ daily 5% of initial, anchor = max(bal,eq) @ EOD 23:30–23:59 CET; total 10% static [P⁷] | ✅ incl. 35+ crypto [S] | ✅ none [P⁸] | **PASS w/ caveat** (news rule = quantifiable haircut, not breach) |
| **City Traders Imperium** | ✅ (jurisdiction-dep.) [S] | ✅ ownership proof on 2-step [S] | ✅ Islamic accounts [S] | ✅ unrestricted [S] | ✅ wknd OK [S]; BTC wknd **unverified** | ✅ 5% daily (SoD balance) / 10% static [S] | ⚠️ lev 1:10 idx, 1:2 crypto (OK for swing sizing) | ✅ none [S] | **BACKUP** — needs full §4 pass |
| FundedNext | ✅ | ⚠️ no manual↔EA switching | ✅ +10% | ⚠️ funded: ±5 min → keep only 40% of profit, SL/TP included, no hold-time exemption [P⁹] | ❌ **crypto is 24/5 — closed Sat/Sun** [P¹⁰] | ✅ 5%/10% static | ✅ | ✅ none | **FAIL #5** |
| Funding Pips | ✅ (back after MT5 purge) | ✅ | ✅ add-on $10/lot RT | ❌ funded: news profits not counted | ❌ **weekend holds banned on Master, auto-close Friday** [S¹¹] | 5%/10% | ✅ | — | **FAIL #4+#5** |
| The5ers | ✅ | ✅ | ✅ | ❌ High Stakes: no orders ±2 min around red news [P¹²] | ✅ | OK | ✅ | — | **FAIL #4** |
| Alpha Capital Group | ✅ | ❌ pre-approval **with MQ5 source submission** [S] | ? | ⚠️ Swing plan only | ✅ | ⚠️ trailing reported [S] | ✅ | 40% best-day rule reported | **FAIL #2** |
| E8 Markets | ✅ | ✅ | ? | ❌ ±2 min red-news ban | ✅ | ❌ 4% daily / 8% (≤ stress numbers) | ✅ | profit-day rule | **FAIL #4+#6** |
| ThinkCapital | ✅ | ✅ both stages [P¹³] | ? | ❌ banned everywhere except Dual-Step-Swing / paid add-on [P¹⁴] | ✅ | ❌ **daily DD ≤4% on every plan** (Swing 4%, Nexus 4%, Lightning 3%+6% trailing) [P¹⁵] | ✅ | — | **FAIL #6** |
| Goat Funded Trader | ✅ | ✅ | ? | ⚠️ ±5 min profit cap 1%/event | ✅ | ❌ 4% daily; trailing on most models | ✅ | — | **FAIL #6** |
| FunderPro | ✅ (back) | ✅ | ❌ not in primary docs (listicles only) | ⚠️ funded: needs Swing add-on | ⚠️ needs Swing add-on, −50% leverage | 5% daily @ 5 pm EST snapshot | ✅ | none (Swing) | **FAIL #3 (unproven)** |
| Lark Funding | ❌ (cTrader-first) | ✅ | ? | ⚠️ "volatility abuse" 3-strikes discretion | ❌ weekend = +10% fee | $-capped daily | ? | — | **FAIL #1+#5** |
| Aqua Funded | ⚠️ listed | ✅ | ? | unverified | unverified | 5%/10% claimed | ✅ | — | **FAIL (longevity/verification)** — 2023 TradeLocker-first, semantics unverifiable |
| Blueberry Funded | ✅ | ✅ | ? | ✅ claimed | ✅ | ❌ 4% daily (Prime) | ✅ | none | **FAIL #6** |

Primary sources: ¹[ftmo.com Swing FAQ](https://ftmo.com/en/faq/ftmo-swing-account-type/), [overnight FAQ](https://ftmo.com/en/faq/do-i-have-to-close-my-positions-overnight/) ²[BF: Can I use EA?](https://help.brightfunded.com/en/articles/9241699-can-i-use-ea) ³[BF help: swap fees on MT5](https://help.brightfunded.com/en/articles/12320307-how-to-check-the-swap-fees-on-mt5) ⁴[BF: Can I trade news?](https://help.brightfunded.com/en/articles/9241694-can-i-trade-news) ⁵[BF: weekend holding](https://help.brightfunded.com/en/articles/9268323-is-it-allowed-to-hold-positions-over-the-weekend) ⁶[BF: overnight](https://help.brightfunded.com/en/articles/9268424-do-i-need-to-close-my-positions-overnight) ⁷[BF: daily permitted loss](https://help.brightfunded.com/en/articles/12291765-how-does-my-daily-permitted-loss-work) ⁸[BF: consistency rule](https://help.brightfunded.com/en/articles/12577176-does-brightfunded-have-a-consistency-rule) ⁹[FN: news trading](https://help.fundednext.com/en/articles/10701447-is-news-trading-allowed-at-fundednext) ¹⁰[FN: crypto](https://help.fundednext.com/en/articles/8925010-can-i-trade-cryptocurrencies-with-fundednext) + [session times](https://help.fundednext.com/en/articles/9857265-trading-session-time) ¹¹[FundingPips: news & weekend](https://help.fundingpips.com/hc/en-us/articles/34504137479441-News-Trading-Weekend-Holding) ¹²[The5ers: news](https://help.the5ers.com/can-i-trade-during-news/) ¹³[TC: EAs](https://www.thinkcapital.com/faqs/general-faqs/are-expert-advisors-eas-allowed-at-thinkcapital/) ¹⁴[TC: news policy](https://www.thinkcapital.com/tc-faqs/funded-accounts/news-trading-policy-rule-and-restriction/) ¹⁵[TC: Dual Step rules](https://www.thinkcapital.com/faqs/dual-step-program-rules/), [Nexus DD](https://www.thinkcapital.com/faqs/nexus-progam-rules/how-is-the-daily-simulated-drawdown-calculated-in-the-nexus-challenge-funded/)

**Morocco eligibility:** FTMO restricted list does not include Morocco ([FTMO FAQ](https://ftmo.com/en/faq/who-can-join-ftmo/)). BrightFunded restricts only Cuba/Iran/N-Korea/Syria/Vietnam + occupied-UA regions; MT5 unavailable to US/UAE only — Morocco unaffected ([BF restricted countries](https://help.brightfunded.com/en/articles/9286630-what-countries-are-restricted-at-brightfunded)). CTI: not on any restricted list found — confirm in chat.

### Drawdown-semantics detail (hard req #6)

| | FTMO (validated baseline) | BrightFunded 2-Step Classic | CTI |
|---|---|---|---|
| Daily limit | 5% of initial size | 5% of initial size (Classic only — "Bright"=4%, 1-Step=3%) | 5% |
| Daily anchor | balance/equity snapshot, midnight CE(S)T | **max(balance, equity)** at EOD rollover **23:30–23:59 CET** (accounts after 2025-09-22) | start-of-day **balance** [S] |
| Total DD | 10% static from initial | 10% static from initial | 10% static from initial |
| Re-sim needed? | no | **small** — same shape, snapshot ~30 min earlier; overlay news-haircut | yes — reset time/timezone unverified |

BrightFunded's rollover note says trading during the 23:30–23:59 CET window is *"not recommended"* —
it is **not** a flatten requirement (the overnight article explicitly says positions never have to be
closed). Several affiliate sites wrongly claim positions must be closed in this window; the primary
source contradicts them. Confirm in chat anyway (§4 Q7).

---

## 2. Recommendation — Top-2 and account structure

### Structure verdict: **B** (two firms, 2×$100k now), prior confirmed — with one nuance

- **C (2×$100k same firm) is impossible**: your FTMO Swing access caps at $100k, and FTMO Standard
  restricts overnight/weekend holding on the funded stage, so a second FTMO account can't host the
  suite. BrightFunded-only C would just be A with extra steps and no diversification.
- **A (1×$200k BrightFunded)** is the cheapest *now* (≈ €1,073) and operationally simplest, but it
  concentrates the entire lead system on a 2.7-year-old firm whose headline payout volume
  ($7–12M claimed) has only ~$0.8M third-party verification. Your 0%-breach system's main residual
  risk IS counterparty default/denial — A maximizes exposure to it.
- **B**: run the suite **mirrored at identical %-risk** on FTMO Swing $100k + BrightFunded $100k.
  Percent-based risk math is size-invariant, so the validated FTMO numbers carry over per account;
  the BrightFunded leg needs only the small re-sim (snapshot time + news-haircut overlay — your
  existing trade CSVs + `ftmo_fastpass_tester_sim.py` infrastructure can answer both). Mirroring
  your own strategy across two *different* firms breaks neither firm's rules (FTMO's identical-
  strategy clause only polices its own $400k cap; BrightFunded has no such cross-firm clause —
  confirm §4 Q10). If BrightFunded defaults or denies, half the suite allocation survives; you also
  get a live read on BrightFunded's funded-stage behavior with $100k at stake **before** committing
  FastPass's account there.

**End-state (after FastPass launch):** FTMO $100k (suite-half) + BrightFunded $100k (suite-half) +
$100k for FastPass at BrightFunded *if* the first payout cycle ran clean, else CTI after a full §4
pass. Note the end-state BrightFunded exposure equals structure A's ($200k) — B's advantage is that
the *suite* itself is never single-firm.

### Cost table (challenge fees, EUR, swap-free included)

| | Now | FastPass later | Total |
|---|---|---|---|
| **B (recommended)** | FTMO $100k €540 [S, official price page] + BF Saturn $100k €495+€49.50 add-on = **€1,084.50** | BF/CTI $100k ≈ €545 | ≈ €1,630 |
| A | BF Jupiter $200k €975+€97.50 = **€1,072.50** | FTMO $100k €540 | ≈ €1,613 |

Costs are within €20 of each other — fee economics are a non-factor; the decision is pure
counterparty/diversification. FTMO refunds the €540 with the first payout; BrightFunded pays a 15%
bonus on evaluation-phase profits [S] — both shrink effective cost further.

### Payout terms of the chosen two

| | FTMO | BrightFunded |
|---|---|---|
| Split | 80/20 → 90/10 (scaling) | 80/20 → 90 → 100 (scaling +30% size/4 mo) |
| First payout | on demand ≥14 days after first trade | 30 days after first funded trade |
| Cadence after | on demand (typ. bi-weekly) | bi-weekly; weekly = checkout add-on; no minimum amount |
| Processing | ~8 h | <24 h (avg ~17 h reported) |
| Longevity | 2015, the industry benchmark, survived MT5 purge with MT5 intact | Sept 2023, Amsterdam+Warsaw, Trustpilot 4.3/500+; **payout volume largely unverified** |

---

## 3. Per-finalist gotcha list (payout-denial vectors for an EA holding weekend BTC through news)

### FTMO Swing $100k
1. **Payout request reportedly requires no open/pending orders at request time** [S] — for an
   always-in-market suite this forces timing payouts to flat windows. Verify (§4 Q12); if true,
   schedule requests after the suite's flatten points (you already have Friday-close infrastructure).
2. Weekend crypto pauses for **platform maintenance windows** — BTC EA must tolerate a dead feed
   for some weekend hours ([FTMO×OANDA trading-hours FAQ](https://ftmo.oanda.com/faq/what-are-the-trading-hours-and-where-can-i-check-them/)).
3. $400k/trader-or-strategy cap — not binding at your sizes.
4. Swing has **no** news/overnight/weekend restrictions — your known baseline; nothing else found.

### BrightFunded 2-Step Classic (+swap-free add-on)
1. **Funded news rule** [P⁴]: any execution (open/close/SL/TP/pending fill) within ±5 min of a
   red-folder event on the affected instrument → that trade's **profit is deducted** (losses stand);
   soft breach only. The 48 h exemption textually covers **take-profits** — *stop-losses* on ≥48 h
   trades are NOT explicitly exempt. A news-spike stop-out in profit on a <48 h XAU/US500 trade
   loses that trade's profit. **Pre-check:** count historical exits within ±5 min of red-folder
   events in your trade CSVs to price this haircut before buying. Ask Q8 about SLs.
2. **Daily anchor includes floating equity at EOD** — carrying large floating profit overnight
   raises your own daily line (same as your FTMO math, but confirm the max(bal,eq) reading, Q6).
3. Rollover window 23:30–23:59 CET: trading "not recommended" — give the BTC EA a no-new-orders
   filter for that window; cheap insurance.
4. **Add-ons are checkout-only, non-retroactive** (swap-free 10%, weekly payouts) — buy at purchase
   or never. Min 5 trading days/phase (irrelevant for multi-week swing; skip the +15% removal add-on).
5. EA fine print [S]: 60-second minimum hold time for automated trades; no grid/latency/HFT/tick
   scalping — your swing logic clears all; confirm 60 s claim (Q9).
6. First payout only 30 days after first funded trade; plan cash-flow expectations.
7. Young firm (Sept 2023). Treat max exposure as a budget line, not an investment.
8. MT5 not offered to US/UAE accounts — irrelevant for Morocco but means a region change mid-account
   could force a platform switch.

### City Traders Imperium (backup only — do not buy without full §4 pass)
1. Crypto weekend availability **unverified**; leverage 1:2 crypto / 1:10 indices — margin fine for
   your sizing, but confirm weekend BTC execution explicitly.
2. EA "proof of ownership" requirement on 2-step — self-written source suffices, but get the
   acceptance in writing *before* paying.
3. Daily-DD reset time/timezone not documented publicly — required for your sim.
4. MT5 access "depends on jurisdiction" — confirm MT5 for Morocco specifically.

---

## 4. Pre-purchase verification checklist (support-chat script, ~20 min/firm)

Ask in writing, save transcripts/screenshots. Expected answers in brackets — any deviation = stop.

1. "I'm a Moroccan resident. Can I purchase, get funded, and receive payouts?" [yes, no conditions]
2. "Do you offer MT5 for my region today?" [yes]
3. "Are **self-written** MT5 EAs allowed on BOTH evaluation and funded, without pre-approval or
   source-code submission?" [yes — BF: yes; CTI: ownership proof only]
4. "Is a swap-free/Islamic option available on the exact account I'm buying ($100k 2-Step
   Classic / $100k Swing)? Price? Can it be added later?" [BF: +10% at checkout only; FTMO: included]
5. "Is news trading allowed on evaluation AND funded? Exact rule, window, penalty?"
   [FTMO Swing: no restriction; BF: ±5 min profit-deduction soft breach, 48 h TP exemption]
6. "Daily drawdown: exact formula — balance or equity or max of both? Snapshot time + timezone?
   Static or trailing? Total DD: anchored to initial balance forever?" [must match §1 table]
7. "Can positions and pending orders stay open through the daily reset window and weekend? Any
   forced flatten, ever?" [no forced flatten — BF rollover window is advisory only]
8. (BF) "If a trade older than 48 h is closed by **stop-loss** (in profit) inside the news window,
   is the profit deducted?" [get explicit answer — undocumented]
9. (BF) "Is there a minimum hold time for automated trades?" [confirm/deny 60 s]
10. "May I run the same strategy I also run at a different prop firm? Same strategy on multiple
    accounts within YOUR firm?" [cross-firm: yes; within-firm: state limits]
11. "BTCUSD: tradable Saturday/Sunday on MT5? Scheduled maintenance windows?" [yes; list windows]
12. (FTMO) "Can I request a payout while positions are open?" [resolve gotcha #1]
13. "Max capital allocation per trader, and does passing two challenges of the same type merge?"
    [FTMO $400k; BF $400k funded, unlimited evals]
14. "Any consistency rule, best-day rule, or profit-distribution requirement on any stage?" [none]
15. "Challenge fee refund and/or evaluation-profit bonus terms?" [FTMO: fee refund at first payout;
    BF: 15% eval bonus]

---

## 5. Rejected firms (do not re-research)

| Firm | One-line kill reason |
|---|---|
| FundedNext | Crypto is 24/5 — no weekend BTC execution; plus funded ±5 min news = keep only 40% of profit (SL/TP included). |
| Funding Pips | News trading effectively banned on funded; weekend holding currently banned on Master accounts (Friday auto-flatten). |
| The5ers | High Stakes bans orders ±2 min around red news on both stages. |
| Alpha Capital Group | EA pre-approval requires submitting MQ5 source; trailing-DD reports. |
| E8 Markets | ±2 min news ban + 4%/8% drawdowns below your 4.5%/5.3% stress numbers. |
| ThinkCapital | Daily DD ≤4% on every plan (Lightning 3% + 6% trailing) — breaches on your worst correlated day. |
| Goat Funded Trader | 4% daily DD, trailing total on most models, 1%-per-event news profit cap. |
| FunderPro | Swap-free absent from primary docs; funded news/weekend only via Swing add-on that halves leverage. |
| Lark Funding | No MT5; weekend holding paywalled (+10%); discretionary 3-strikes "volatility abuse" rule. |
| Aqua Funded | 2023 TradeLocker-first firm; rule semantics and payout claims unverifiable at the required depth. |
| Blueberry Funded | 4% daily drawdown (Prime) below stress numbers despite real-broker backing. |
| FTMO Standard (non-Swing) | Funded stage restricts overnight/weekend holding — only Swing variant qualifies. |

---

## Next actions

1. Run §4 chat scripts at FTMO + BrightFunded (and CTI if you want the backup pre-cleared).
2. Re-run the challenge sim on the BrightFunded leg: 23:30 CET snapshot + max(bal,eq) daily anchor
   + news-haircut overlay (±5 min red-folder windows against your historical exit timestamps).
3. If both pass: buy FTMO Swing $100k (swap-free) + BrightFunded Saturn $100k 2-Step Classic
   (+swap-free add-on at checkout — cannot be added later).
4. Add a 23:25–00:05 CET no-new-orders filter to the BTC EA config for the BrightFunded terminal.
