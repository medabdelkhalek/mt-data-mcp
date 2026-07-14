"""
dashboard.py — MrUnderdog Cockpit (regime · risk · deploy · all EAs)
Run: streamlit run dashboard.py   (or double-click run_cockpit.bat)

Live localhost view of XAU / BTC / US500: regime (deploy light), per-pair
Alligator chart, open positions by EA magic, and recent EA performance.
Reads the running MetaTrader 5 terminal directly. Shared regime logic in
../regime_core.py.
"""
import os, sys
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import MetaTrader5 as mt5
import importlib, regime_core            # force-reload so edits to regime_core
importlib.reload(regime_core)            # propagate without a full server restart
from regime_core import (MARKETS, classify, suite_light, chart_frame,
                         monday_status, ohlc_frame, ADX_TREND)

st.set_page_config(page_title="MrUnderdog Cockpit", page_icon="📊", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown("""<style>
header[data-testid="stHeader"] { display:none; }
#MainMenu, footer { visibility:hidden; }
.block-container { padding: 1.7rem 2.2rem 3rem; background:#0a0b0f; }
html, body, [class*="css"] { font-family:'Inter',system-ui,sans-serif; }
.page-title { font-size:1.7rem; font-weight:700; color:#f1f5f9; letter-spacing:-.02em; }
.sub { color:#64748b; font-size:.85rem; }
.light { padding:.85rem 1.1rem; border-radius:12px; font-weight:700; font-size:1.15rem; }
.green { background:rgba(34,197,94,.13); color:#22c55e; border:1px solid rgba(34,197,94,.4);}
.amber { background:rgba(245,158,11,.13); color:#f59e0b; border:1px solid rgba(245,158,11,.4);}
.red   { background:rgba(239,68,68,.13); color:#ef4444; border:1px solid rgba(239,68,68,.4);}
.card { background:#11131a; border:1px solid #1e2230; border-radius:14px; padding:1rem 1.1rem; }
.badge { padding:.18rem .6rem; border-radius:7px; font-size:.78rem; font-weight:700; }
.kv { color:#94a3b8; font-size:.82rem; } .kvv { color:#e2e8f0; font-weight:600; }
</style>""", unsafe_allow_html=True)

COLOR = {True: "#22c55e", False: "#ef4444"}
REGIME_COLOR = {"TREND_UP": "#22c55e", "TREND_DOWN": "#22c55e",
                "TRANSITION": "#f59e0b", "CONSOLIDATION": "#ef4444", "n/a": "#64748b"}


@st.cache_data(ttl=120, show_spinner=False)
def load_all():
    if not mt5.initialize():
        return None
    ai = mt5.account_info()
    acct = dict(login=ai.login, server=ai.server, balance=ai.balance, equity=ai.equity,
                profit=ai.profit, margin_level=ai.margin_level) if ai else None
    rows, charts, posmap, perfmap = [], {}, {}, {}
    allpos = mt5.positions_get() or []
    to = datetime.now(); frm = to - timedelta(days=120)
    deals = mt5.history_deals_get(frm, to) or []

    # --- live suite risk (mirrors RiskLib + FTMO limits on $200k) ---
    INIT = 200000.0
    midnight = datetime(to.year, to.month, to.day)
    today = mt5.history_deals_get(midnight, to) or []
    today_real = sum(d.profit + d.swap + d.commission for d in today
                     if d.entry == mt5.DEAL_ENTRY_OUT)
    floating = acct["profit"] if acct else 0.0
    day_pl = today_real + floating
    conc = 0.0
    for p in allpos:
        if p.sl == 0:
            continue
        si = mt5.symbol_info(p.symbol)
        if not si or si.trade_tick_size == 0:
            continue
        dist = (p.price_current - p.sl) if p.type == 0 else (p.sl - p.price_current)
        if dist > 0:
            conc += dist * (si.trade_tick_value / si.trade_tick_size) * p.volume
    eq = acct["equity"] if acct else INIT
    risk = dict(day_pl=day_pl, daily_buffer=10000 + min(0, day_pl),
                halt_buffer=eq - INIT * 0.90, dd_pct=(eq - INIT) / INIT * 100,
                conc_pct=conc / acct["balance"] * 100 if acct and acct["balance"] else 0,
                n_open=len(allpos))
    us500, us500_chart = None, None
    for label, sym, ttf, magic, desc in MARKETS:
        if label == "US500":                          # weekly breakout — no Alligator/ADX
            us500 = monday_status(sym)
            if us500:
                us500["magic"] = magic; us500["desc"] = desc
            us500_chart = ohlc_frame(sym, mt5.TIMEFRAME_D1)
        else:                                         # XAU/BTC — Alligator trend EAs
            r = classify(label, sym, ttf)
            if r:
                r["desc"] = desc; r["magic"] = magic
                rows.append(r)
                charts[label] = chart_frame(sym, ttf)
        posmap[label] = [dict(type="BUY" if p.type == 0 else "SELL", vol=p.volume,
                              open=p.price_open, cur=p.price_current, profit=p.profit)
                         for p in allpos if p.magic == magic]
        pls = [d.profit + d.swap + d.commission for d in deals
               if d.entry == mt5.DEAL_ENTRY_OUT and d.magic == magic]
        wins = [x for x in pls if x > 0]; nz = [x for x in pls if x != 0]
        perfmap[label] = dict(n=len(pls), net=sum(pls),
                              wr=(len(wins) / len(nz) * 100 if nz else 0))
    # --- heartbeat: last closed-trade time per magic ---
    last_seen = {}
    for d in deals:
        if d.entry == mt5.DEAL_ENTRY_OUT:
            last_seen[d.magic] = max(last_seen.get(d.magic, 0), d.time)

    # --- other account EAs: FastPass (778801) + Governor-watched manual (magic 0) ---
    others = []
    for nm, mg, sym in [("FastPass", 778801, "XAUUSD"), ("Manual (Gov)", 0, "—")]:
        pls = [d.profit + d.swap + d.commission for d in deals
               if d.entry == mt5.DEAL_ENTRY_OUT and d.magic == mg]
        op = [p for p in allpos if p.magic == mg]
        wins = [x for x in pls if x > 0]; nz = [x for x in pls if x != 0]
        others.append(dict(name=nm, magic=mg, n=len(pls), net=sum(pls),
                           wr=(len(wins) / len(nz) * 100 if nz else 0),
                           open=len(op), floating=sum(p.profit for p in op),
                           last=last_seen.get(mg)))

    # --- equity/balance curve (60d realized) for the header sparkline ---
    rec = sorted([d for d in deals if d.entry == mt5.DEAL_ENTRY_OUT
                  and d.time >= (to - timedelta(days=60)).timestamp()], key=lambda d: d.time)
    curve = []
    if rec and acct:
        run = acct["balance"] - sum(d.profit + d.swap + d.commission for d in rec)
        for d in rec:
            run += d.profit + d.swap + d.commission
            curve.append((datetime.fromtimestamp(d.time), run))

    return dict(acct=acct, rows=rows, charts=charts, pos=posmap, perf=perfmap,
                risk=risk, last_seen=last_seen, us500=us500, us500_chart=us500_chart,
                others=others, curve=curve, ts=datetime.now())


def candle(label, cf, info):
    if cf is None:
        return None
    t = pd.to_datetime(cf["time"], unit="s")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=t, open=cf["open"], high=cf["high"], low=cf["low"],
                  close=cf["close"], name=label, increasing_line_color="#22c55e",
                  decreasing_line_color="#ef4444", showlegend=False))
    for key, col, nm in [("jaw", "#3b82f6", "Jaw"), ("teeth", "#ef4444", "Teeth"),
                         ("lips", "#22c55e", "Lips"), ("ema50", "#94a3b8", "EMA50")]:
        fig.add_trace(go.Scatter(x=t, y=cf[key], line=dict(width=1.2, color=col), name=nm))
    fig.update_layout(template="plotly_dark", height=240, margin=dict(l=4, r=4, t=6, b=4),
                      paper_bgcolor="#11131a", plot_bgcolor="#11131a",
                      xaxis_rangeslider_visible=False, showlegend=False,
                      font=dict(size=10))
    return fig


def ago(ts):
    if not ts:
        return "—"
    s = datetime.now().timestamp() - ts
    if s >= 86400:
        return f"{int(s/86400)}d ago"
    if s >= 3600:
        return f"{int(s/3600)}h ago"
    return f"{int(s/60)}m ago"


def spark(curve):
    if not curve or len(curve) < 2:
        return None
    xs = [c[0] for c in curve]; ys = [c[1] for c in curve]
    up = ys[-1] >= ys[0]
    fig = go.Figure(go.Scatter(x=xs, y=ys, mode="lines",
                    line=dict(color="#22c55e" if up else "#ef4444", width=1.6)))
    pad = (max(ys) - min(ys)) * 0.15 or 1
    fig.update_layout(template="plotly_dark", height=80,
                      margin=dict(l=0, r=0, t=2, b=0), paper_bgcolor="#0a0b0f",
                      plot_bgcolor="#0a0b0f", showlegend=False,
                      xaxis=dict(visible=False),
                      yaxis=dict(visible=False, range=[min(ys) - pad, max(ys) + pad]))
    return fig


# ── data ──
data = load_all()
if data is None:
    st.error("Could not connect to MetaTrader 5. Open the terminal and refresh.")
    st.stop()

# ── header ──
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div class="page-title">📊 MrUnderdog Cockpit '
                '<span style="font-size:.95rem;font-weight:500;color:#64748b;">'
                '· regime · risk · deploy</span></div>', unsafe_allow_html=True)
    a = data["acct"]
    if a:
        st.markdown(f'<span class="sub">acct {a["login"]} · {a["server"]} · '
                    f'updated {data["ts"]:%Y-%m-%d %H:%M:%S}</span>', unsafe_allow_html=True)
with c2:
    if st.button("🔄 Refresh", width='stretch'):
        st.cache_data.clear(); st.rerun()

if a := data["acct"]:
    m = st.columns(4)
    m[0].metric("Balance", f"${a['balance']:,.0f}")
    m[1].metric("Equity", f"${a['equity']:,.0f}", f"{a['equity']-a['balance']:+,.0f}")
    m[2].metric("Floating P/L", f"${a['profit']:,.0f}")
    m[3].metric("Margin level", f"{a['margin_level']:,.0f}%" if a['margin_level'] else "—")

sp = spark(data.get("curve"))
if sp:
    st.markdown('<span class="sub">Balance · last 60d (realized)</span>', unsafe_allow_html=True)
    st.plotly_chart(sp, width='stretch', config={"displayModeBar": False})

# ── deploy light ──
light, n, msg = suite_light(data["rows"])
cls = {"GREEN": "green", "AMBER": "amber", "RED": "red"}[light]
st.markdown(f'<div class="light {cls}">DEPLOY LIGHT: {light} — {msg} '
            f'&nbsp;(XAU+BTC armed {n}/2)</div>', unsafe_allow_html=True)
st.markdown('<span class="sub">Gate (validated): rolling per-challenge sim → 0% breach, '
            'worst DD 9.34% (&lt;10%), median ~11wk to P1. Deploy when GREEN.</span>',
            unsafe_allow_html=True)

# ── live risk cockpit (mirrors RiskLib + FTMO limits) ──
rk = data["risk"]
rcol = st.columns(4)
rcol[0].metric("Today P/L (real+float)", f"${rk['day_pl']:+,.0f}",
               help="Realized today + current floating, vs the FTMO −$10k daily limit")
rcol[1].metric("Daily-loss buffer", f"${rk['daily_buffer']:,.0f}", "of $10k",
               delta_color="off")
rcol[2].metric("Buffer to 10% halt", f"${rk['halt_buffer']:,.0f}", f"{rk['dd_pct']:+.1f}% vs $200k",
               delta_color="off")
rcol[3].metric("Concurrent SL-risk", f"{rk['conc_pct']:.2f}%", "cap 5.5%", delta_color="off")

# correlated-exposure flag: markets pointed the same way = elevated worst-day risk
dirs = [r["direction"] for r in data["rows"]]
if data.get("us500"):
    dirs.append(data["us500"]["direction"])
if dirs and len(set(dirs)) == 1:
    st.markdown(f'<span class="sub">⚠ All three markets pointed <b>{dirs[0]}</b> — '
                'elevated correlated-day risk (the suite\'s worst-case driver).</span>',
                unsafe_allow_html=True)
st.write("")

def card_footer(label, magic):
    pos = data["pos"].get(label, [])
    if pos:
        tot = sum(p["profit"] for p in pos)
        pc = "#22c55e" if tot >= 0 else "#ef4444"
        st.markdown(f"<span class='kv'>Open ({magic})</span> <span class='kvv'>{len(pos)} pos · "
                    f"<span style='color:{pc}'>${tot:+,.0f}</span></span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span class='kv'>Open ({magic})</span> <span class='kvv'>flat</span>",
                    unsafe_allow_html=True)
    pf = data["perf"][label]
    nc = "#22c55e" if pf["net"] >= 0 else "#ef4444"
    st.markdown(f"<span class='kv'>Last 120d</span> <span class='kvv'>{pf['n']} trades · "
                f"{pf['wr']:.0f}% WR · <span style='color:{nc}'>${pf['net']:+,.0f}</span></span> &nbsp; "
                f"<span class='kv'>last</span> <span class='kvv'>{ago(data['last_seen'].get(magic))}</span>",
                unsafe_allow_html=True)


# ── per-pair cards ──
cols = st.columns(3)

# XAU & BTC — Alligator trend EAs: show the actual multi-timeframe gate stack
for col, r in zip(cols[:2], data["rows"]):
    with col:
        v = r["verdict"]
        vcol = "#22c55e" if v.startswith("ARMED") else ("#f59e0b" if v == "MIXED" else "#ef4444")
        st.markdown(f"""<div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:1.15rem;font-weight:700;color:#f1f5f9;">{r['label']}</span>
          <span class="badge" style="background:{vcol}22;color:{vcol};">{v}</span>
        </div>
        <div class="sub" style="margin:.1rem 0 .4rem;">{r['desc']}</div>
        </div>""", unsafe_allow_html=True)

        gh = ""
        for name, val, ok in r["gates"]:
            gc = "#22c55e" if ok else "#64748b"
            mark = "✓" if ok else "·"
            gh += (f"<div style='margin:.06rem 0;'><span style='color:{gc};font-weight:700'>{mark}</span> "
                   f"<span class='kv'>{name}</span> &nbsp;<span class='kvv'>{val}</span></div>")
        st.markdown(gh, unsafe_allow_html=True)

        if r["aligned"]:
            st.markdown(f"<span class='sub' style='color:#22c55e'>→ all gates aligned — EA armed "
                        f"{'LONG' if r['allig_dir']=='up' else 'SHORT'}</span>", unsafe_allow_html=True)
        elif not r["trend_open"]:
            st.markdown("<span class='sub'>→ arms when the Alligator mouth opens</span>",
                        unsafe_allow_html=True)
        else:
            bad = [g[0].split(" (")[0] for g in r["gates"] if not g[2]]
            st.markdown(f"<span class='sub'>→ arms when {', '.join(bad)} align</span>",
                        unsafe_allow_html=True)

        fig = candle(r["label"], data["charts"].get(r["label"]), r)
        if fig:
            st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

        st.markdown(f"<span class='kv'>Close</span> <span class='kvv'>{r['close']:,.2f}</span> &nbsp; "
                    f"<span class='kv'>D1 SMA5</span> <span class='kvv'>{r['sma5']:,.2f}</span> &nbsp; "
                    f"<span class='kv'>mouth</span> <span class='kvv'>{r['spread']:.2f}×ATR</span>",
                    unsafe_allow_html=True)
        card_footer(r["label"], r["magic"])

# US500 — MondayRange weekly breakout (strategy-bound: Monday H/L, no Alligator/ADX)
with cols[2]:
    ms = data.get("us500")
    if not ms:
        st.markdown('<div class="card">US500 — no Monday range available yet</div>',
                    unsafe_allow_html=True)
    else:
        vcol = {"TRIGGER ZONE": "#22c55e", "ARMED": "#f59e0b",
                "FORMING": "#3b82f6"}.get(ms["verdict"], "#ef4444")
        st.markdown(f"""<div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:1.15rem;font-weight:700;color:#f1f5f9;">US500</span>
          <span class="badge" style="background:{vcol}22;color:{vcol};">{ms['verdict']}</span>
        </div>
        <div class="sub" style="margin:.1rem 0 .5rem;">{ms.get('desc','Monday-range weekly breakout')}</div>
        <div class="badge" style="background:{vcol}22;color:{vcol};">{ms['status']}</div>
        </div>""", unsafe_allow_html=True)

        if ms["forming"]:
            st.markdown(
                f"<span class='kv'>Mon {ms['monday']} range</span> "
                f"<span class='kvv' style='color:#3b82f6'>still building</span><br>"
                f"<span class='kv'>So far</span> <span class='kvv'>{ms['low']:,.1f} – {ms['high']:,.1f}</span> "
                f"<span class='kv'>({ms['rng_pts']:,.0f} pts)</span><br>"
                f"<span class='sub'>Range sets at Monday's close — EA trades it Tue–Fri.</span>",
                unsafe_allow_html=True)
        else:
            q = "✓ qualifies" if ms["qualifies"] else "✗ too small (skip week)"
            st.markdown(
                f"<span class='kv'>Mon {ms['monday']} range</span> "
                f"<span class='kvv'>{ms['low']:,.1f} – {ms['high']:,.1f}</span><br>"
                f"<span class='kv'>Size</span> <span class='kvv'>{ms['rng_pts']:,.0f} pts</span> "
                f"<span class='kv'>vs min {ms['min_pts']:,.0f}</span> <span class='kvv'>{q}</span><br>"
                f"<span class='kv'>RR target</span> <span class='kvv'>{ms['rr']}</span> &nbsp; "
                f"<span class='kv'>Close</span> <span class='kvv'>{ms['close']:,.1f}</span>",
                unsafe_allow_html=True)

        cf = data.get("us500_chart")
        if cf:
            t = pd.to_datetime(cf["time"], unit="s")
            fig = go.Figure(go.Candlestick(x=t, open=cf["open"], high=cf["high"], low=cf["low"],
                            close=cf["close"], increasing_line_color="#22c55e",
                            decreasing_line_color="#ef4444", showlegend=False))
            fig.add_hline(y=ms["high"], line=dict(color="#f59e0b", width=1.1, dash="dash"),
                          annotation_text="Mon H", annotation_position="top left")
            fig.add_hline(y=ms["low"], line=dict(color="#3b82f6", width=1.1, dash="dash"),
                          annotation_text="Mon L", annotation_position="bottom left")
            fig.update_layout(template="plotly_dark", height=240, margin=dict(l=4, r=4, t=6, b=4),
                              paper_bgcolor="#11131a", plot_bgcolor="#11131a",
                              xaxis_rangeslider_visible=False, showlegend=False, font=dict(size=10))
            st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

        st.markdown(f"<span class='kv'>Price in range</span> "
                    f"<span class='kvv'>{ms['pos_in']:.0f}%</span> "
                    f"<span class='kv'>(0 = Mon low · 100 = Mon high)</span>", unsafe_allow_html=True)
        st.progress(int(ms["pos_in"]))
        card_footer("US500", ms.get("magic", 202500))

st.write("")
st.markdown("<span class='kv' style='font-size:.95rem;font-weight:700;'>Other account EAs</span>",
            unsafe_allow_html=True)
ocols = st.columns(2)
for col, o in zip(ocols, data.get("others", [])):
    with col:
        nc = "#22c55e" if o["net"] >= 0 else "#ef4444"
        fc = "#22c55e" if o["floating"] >= 0 else "#ef4444"
        st.markdown(f"""<div class="card">
        <span style="font-weight:700;color:#f1f5f9;">{o['name']}</span>
        <span class="kv">magic {o['magic']}</span><br>
        <span class="kv">Open</span> <span class="kvv">{o['open']} pos · </span>
        <span class="kvv" style="color:{fc}">${o['floating']:+,.0f}</span> &nbsp;
        <span class="kv">last</span> <span class="kvv">{ago(o['last'])}</span><br>
        <span class="kv">120d</span> <span class="kvv">{o['n']} trades · {o['wr']:.0f}% WR · </span>
        <span class="kvv" style="color:{nc}">${o['net']:+,.0f}</span>
        </div>""", unsafe_allow_html=True)

st.write("")
st.caption("Deploy timing = one-time, legit edge. Funded 'easy-mode' (pausing EAs by regime) "
           "is the regime-filter the FastPass research rejected — validate before doing it live. "
           "Data via MetaTrader5; refresh for the latest (D1/H4 regime moves slowly).")
