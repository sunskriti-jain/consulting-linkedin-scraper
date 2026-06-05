---
name: export-analytics
description: >
  Use this skill whenever the user wants an analytics spreadsheet, engagement
  report, or summary of outreach performance across companies or campaigns.
  Trigger on: "make a spreadsheet", "export analytics", "show me the stats",
  "master sequencing spreadsheet", "create a CSV", "how are all the companies
  doing", "engagement report", "bounce rates", "reply rates", or any request
  to summarise or export email campaign data. Always use this skill — not raw
  SQL or a custom script — when the user wants an analytics file or table.
  Run check-engagement first if the user wants fresh data before exporting.
---

# Export Analytics Skill

This skill generates `master_analytics_all_campaigns.csv` — a per-company
engagement summary across every outreach campaign — and reports the results
to the user as a formatted table.

## Working directory and Python path
- **Working directory:** `C:\Users\admin\linkedin-scraper`
- **Python:** `.\venv\Scripts\python.exe`
- **Output file:** `master_analytics_all_campaigns.csv`

## When to run a fresh engagement check first
If the user says "latest", "up to date", "fresh", or if the most recent
campaign was sent within the last 48 hours, run `check-engagement` first
before exporting. Otherwise the CSV may reflect stale bounce/reply data.

## Running the export

```bash
cd "C:\Users\admin\linkedin-scraper"
.\venv\Scripts\python.exe -u run_master_analytics.py 2>&1
```

`run_master_analytics.py` does two things in one pass:
1. Checks engagement on any campaigns with unchecked emails
2. Exports the CSV

If you only want the export (no fresh check), run inline:

```bash
.\venv\Scripts\python.exe -u -c "
import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from campaign import export_master_analytics_csv
export_master_analytics_csv()
print('Exported.')
" 2>&1
```

## CSV schema
```
Company, Total_Sent, Reply_Count, Bounce_Count, Reply_%, Bounce_%, First_Reply_Date
```
- Sorted by Reply_Count DESC, then Total_Sent DESC
- Header row notes that opens require tracking pixels (not available via Gmail API)
- TOTAL summary row at top

## Reporting to the user
After the export, print the full per-company table inline — don't just say
"done". Format it as a markdown table with these columns:

| Company | Sent | Replies | Reply% | Bounces | Bounce% | First Reply |
|---|---|---|---|---|---|---|

Then highlight:
- **Top responders** (Reply% > 1%)
- **Clean delivery** (Bounce% = 0% and Sent ≥ 5) — best follow-up targets
- **Blocked domains** (Bounce% = 100%) — email security, skip follow-up
- **Overall totals** — total sent, total replies (with %), total bounces (with %)

Tell the user the file is saved at:
`C:\Users\admin\linkedin-scraper\master_analytics_all_campaigns.csv`

## Failure handling
- **File write error:** check that no other process has the CSV open (Excel
  locks it on Windows). Close Excel and retry.
- **Empty table:** no campaigns have `status IN ('sent','bounced','replied')`.
  Run `SELECT COUNT(*) FROM send_records WHERE status='sent'` to verify
  emails were actually sent.
- **Stale data:** if reply/bounce counts look too low, run check-engagement
  first with `recheck=False` to pick up any missed updates.
