"""
regime_alert.py — silent daily check: Telegram-ping when the deploy light CHANGES.
Designed for Windows Task Scheduler (daily). No output unless something changed.
State persists in regime_alert_state.json so you're only pinged on transitions
(e.g. AMBER -> GREEN = deploy window opened). Uses the suite's Telegram bot.
"""
import json, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime
import MetaTrader5 as mt5
from regime_core import MARKETS, classify, suite_light, monday_status

TG_TOKEN = "8665176058:AAEfyKxwpRAzBWPx_EBR6YHj3Ujvlhi4TVQ"
TG_CHAT = "1150853781"
STATE = Path(__file__).with_name("regime_alert_state.json")


def telegram(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": TG_CHAT, "text": msg}).encode()
    try:
        urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=10)
    except Exception as e:
        print("telegram failed:", e)


def main():
    if not mt5.initialize():
        return  # MT5 not running — skip silently, try again tomorrow
    rows, verdicts = [], {}
    for label, sym, ttf, _m, _d in MARKETS:
        if label == "US500":
            ms = monday_status(sym)
            if ms:
                verdicts["US500"] = ms["verdict"]
            continue
        r = classify(label, sym, ttf)
        if r:
            rows.append(r); verdicts[label] = r["verdict"]
    light, n, msg = suite_light(rows)
    mt5.shutdown()

    prev = {}
    if STATE.exists():
        try:
            prev = json.loads(STATE.read_text())
        except Exception:
            prev = {}
    cur = dict(light=light, verdicts=verdicts)

    if cur != prev:
        lines = [f"[Cockpit] Deploy light: {prev.get('light','?')} -> {light}  ({msg})"]
        for k, v in verdicts.items():
            old = prev.get("verdicts", {}).get(k)
            lines.append(f"  {k}: {v}" + (f"  (was {old})" if old and old != v else ""))
        if light == "GREEN" and prev.get("light") != "GREEN":
            lines.append("XAU+BTC armed — favorable window to START the challenge.")
        telegram("\n".join(lines))
        print(f"{datetime.now():%Y-%m-%d %H:%M} alerted: {prev.get('light','?')} -> {light}")
    STATE.write_text(json.dumps(cur))


if __name__ == "__main__":
    main()
