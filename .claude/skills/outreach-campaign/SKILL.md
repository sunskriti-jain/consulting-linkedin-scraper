---
name: outreach-campaign
description: >
  Use this skill whenever the user wants to run a cold email outreach campaign
  to a list of companies — even if they just say "send emails to these companies",
  "reach out to X and Y", "do the full pipeline for these", "launch a campaign",
  or "send 10 emails per company to these". This skill handles the complete
  workflow: inserting companies into the database, ingesting real LinkedIn
  profiles (10 per company), creating a named campaign, personalizing once per
  company with LLM and cloning for the rest, and sending. Always use this skill
  when the user provides a list of company names and wants outreach emails sent.
---

# Outreach Campaign Skill

You are running the LinkedIn scraper outreach pipeline for the user. This skill
produces a complete, ready-to-run Python pipeline script and executes it.

## Working directory and Python path
- **Working directory:** `C:\Users\admin\linkedin-scraper`
- **Python:** `.\venv\Scripts\python.exe`
- **Database:** `outreach.db` (SQLite, already initialised)

## What you need from the user
Before writing any code, confirm you have:
1. **Company list** — names, domains, and industries (or infer domain/industry if
   the company is well-known)
2. **Campaign name** — suggest `"<Description> Outreach - <Month> <Year>"` if not given
3. **Contacts per company** — default is 10 unless the user says otherwise

If the user says "same as before" or "same setup", check the most recent
pipeline script in the working directory (`run_batch3_pipeline.py`,
`run_fortune500_pipeline.py`, etc.) for the sender value prop and template.

## How to build the pipeline script

Model your script exactly on `run_fortune500_pipeline.py` (read it first). The
script must:

1. **Insert companies** — `INSERT INTO companies` with name, domain, industry,
   email_pattern `first.last`, confidence 70.0. Use `INSERT OR IGNORE`-style
   handling: catch UNIQUE errors and print `[=] already exists`.

2. **Ingest profiles** — for each company, provide a list of 10 real senior
   employees (VP+, Director+, C-suite) as:
   ```python
   {"title": "Full Name - Title - Company | LinkedIn", "url": "https://www.linkedin.com/in/slug/"}
   ```
   Use your knowledge of well-known public figures at each company. For smaller
   or less-known companies, use WebSearch to find real profiles. Never invent
   people. Call `ingest_profiles(company_name, profiles, min_required=3, max_keep=10)`.

3. **Create campaign** — insert into `campaigns` table with `daily_cap=100`.
   Check for existing campaign by name first.

4. **Personalize** — call `personalize_once_per_company(campaign_id, SENDER_VALUE_PROP, num_steps=3, company_domains=COMPANY_DOMAINS)`.
   The `SENDER_VALUE_PROP` is:
   > "We're a consulting club at UC Berkeley that partners with companies on
   > semester-long projects. Our past teams have delivered market research,
   > product roadmaps, and strategic analyses that companies find genuinely
   > useful. We work with a handful of partners each semester and customize
   > every engagement."

5. **Send** — use the send loop from `run_fortune500_pipeline.py` verbatim
   (the `while True` loop with `GmailClient`, `safe_exec`, 2–4 second delays).

## Running the script

Save the script as `run_<slug>_pipeline.py` where `<slug>` is a short
lowercase identifier for the campaign. Then run:

```bash
cd "C:\Users\admin\linkedin-scraper"
.\venv\Scripts\python.exe -u run_<slug>_pipeline.py > logs\<slug>_pipeline.log 2>&1
```

Run in the background and tail the log to show progress. Report every 25 emails
sent and any `[FAIL]` lines.

## Success criteria
- Script exits with code 0
- Log ends with `[ALL DONE] ... Sent: N | Failed: 0`
- No `[ERROR]` lines in ingest output
- All companies show `[OK]` in contact count summary

## Failure handling
- **0 contacts for a company** → the company name may not match what's in the
  DB; check with `SELECT name FROM companies WHERE domain=?` and retry with the
  exact stored name.
- **LLM credits exhausted** → normal, Perplexity fallback activates automatically.
- **DB locked** → the send loop retries 10× with backoff; if it keeps failing,
  check for another running Python process.
- **UNIQUE constraint on company_research** → harmless (already researched);
  wrap the INSERT in a try/except and continue.

## Reporting to the user
When the pipeline finishes, report:
- Total sent / failed
- Per-company breakdown (sent count)
- Campaign ID (for future engagement checks)
- Any companies with high bounce rates (flagged after engagement check)
