import json, subprocess, urllib.request, urllib.error

# get token from git credential helper
p = subprocess.run(["git","credential","fill"],
                   input="protocol=https\nhost=github.com\n\n",
                   capture_output=True, text=True)
token = None
for line in p.stdout.splitlines():
    if line.startswith("password="):
        token = line[len("password="):]
if not token:
    print("NO_TOKEN"); raise SystemExit(1)

body = (
"## What\n"
"Lowers `RiskPercent` on the BTC Alligator EA from **1.0% -> 0.9%** per trade.\n\n"
"## Why\n"
"From the FTMO combined-account analysis (4 EAs on one $200k account):\n"
"- FTMO's daily loss limit is a **fixed $10k**, but per-trade risk is **% of current balance** "
"- as the account compounds, absolute risk grows toward the fixed limit. Trimming BTC's 1.0% adds headroom.\n"
"- BTC runs over the weekend (`CloseBeforeFridayClose=false`), so its stop can be gapped through. "
"A slightly smaller size softens that tail.\n\n"
"## Notes for reviewer\n"
"- One-line input default change; no logic change. Version not bumped.\n"
"- The rest of this session's work (Friday features, deployment guide, safety-block alignment) is already on `main`.\n"
"- Recompile in MetaEditor to pick up the new default.\n\n"
"Generated with [Claude Code](https://claude.com/claude-code)"
)
payload = json.dumps({
    "title": "Reduce BTC per-trade risk to 0.9%",
    "head": "tune/btc-risk-0.9",
    "base": "main",
    "body": body,
}).encode()

req = urllib.request.Request(
    "https://api.github.com/repos/medabdelkhalek/MetaTrader-5-EAs/pulls",
    data=payload, method="POST",
    headers={"Authorization": f"token {token}",
             "Accept": "application/vnd.github+json",
             "User-Agent": "claude-code"})
try:
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
        print("PR_URL:", data["html_url"])
except urllib.error.HTTPError as e:
    msg = e.read().decode()
    print("HTTP", e.code)
    print(msg[:800])
