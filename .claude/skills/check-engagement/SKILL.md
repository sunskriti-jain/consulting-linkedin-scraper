---
name: check-engagement
description: >
  Use this skill whenever the user wants to check email engagement — replies,
  bounces, open rates — for any outreach campaign. Trigger on phrases like
  "check engagement", "any replies?", "how are the emails doing", "check
  bounces", "poll Gmail", "what's the response rate", "update the engagement
  data", or "check the campaigns". Also use this skill before any analytics
  export to ensure the data is current. Always use this skill — not a raw Bash
  command — when the user wants fresh engagement metrics from Gmail.
---

# Check Engagement Skill

This skill polls Gmail for new replies and bounces on all sent campaigns (or a
specific named one), updates the database, and prints a live summary.

## Working directory and Python path
- **Working directory:** `C:\Users\admin\linkedin-scraper`
- **Python:** `.\venv\Scripts\python.exe`

## Checking engagement

### All campaigns (default)
Run `run_master_analytics.py` — it automatically finds all campaigns with
unchecked emails, polls Gmail for each, then exports the CSV:

```bash
cd "C:\Users\admin\linkedin-scraper"
.\venv\Scripts\python.exe -u run_master_analytics.py 2>&1
```

### Specific campaign
If the user names a campaign, run inline Python to target just that campaign:

```bash
.\venv\Scripts\python.exe -u -c "
import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from campaign import track_engagement
import sqlite3
conn = sqlite3.connect('outreach.db'); conn.row_factory = __import__('sqlite3').Row
camp = conn.execute(\"SELECT id FROM campaigns WHERE name LIKE ?\",
                    ('%<CAMPAIGN_SUBSTRING>%',)).fetchone()
if not camp:
    print('Campaign not found'); exit(1)
result = track_engagement(camp['id'], recheck=False)
print(result)
conn.close()
" 2>&1
```

Replace `<CAMPAIGN_SUBSTRING>` with a substring of the campaign name (e.g.
`Tech Startup`, `Fortune 500`, `Batch 3`).

## What the engagement check does
- Calls `gmail_client.check_thread_engagement()` for each sent email (one
  `threads.get` API call per email — reply + bounce in one request)
- **Bounce detection:** looks for NDR messages in the thread (from
  `mailer-daemon`, `postmaster`, etc.) with bounce subject keywords. Requires
  BOTH a bounce sender AND a bounce subject to avoid false positives.
- **Reply detection:** any inbound message in the thread that isn't from the
  sender and isn't an NDR counts as a reply.
- Updates `send_records.status`, `bounced_at`, `reply_detected_at`,
  `last_checked_at` in the database.
- Skips emails already marked bounced or replied (idempotent).

## Reading the output
The script prints progress every 50 emails:
```
[50/257] opened=0 replied=0 bounced=17
```
And a summary at the end:
```
[OK] Checked 257 emails
  Replied: 4  Bounced: 74  New status changes: 78
```

## Reporting to the user
After the check completes, summarise:
- Total emails checked
- New replies (with company names if >0)
- New bounces
- Companies with 100% bounce rate (email security — unlikely to get through)
- Companies with 0% bounce (clean delivery — best candidates for follow-up)
- Suggest running `export-analytics` if the user wants the full CSV

## Failure handling
- **Gmail API rate limit:** the check already uses 0.1 s delays between calls;
  if you see 429 errors, wait 60 s and retry from where it left off.
- **`last_checked_at IS NOT NULL` skipping all emails:** run with `recheck=True`
  to force re-check all sent emails.
- **No campaigns found:** print the list of campaign names from
  `SELECT name FROM campaigns`.
