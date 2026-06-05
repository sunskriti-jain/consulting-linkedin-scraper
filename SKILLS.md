# LinkedIn Scraper — Skills Index

Four Claude Code skills that automate the full outreach pipeline.
Skills live in `.claude/skills/` and activate automatically when you describe
what you want in plain English.

---

## `outreach-campaign`
**When to use:** You have a list of companies and want emails sent to real
senior employees at each one.

**What it does:**
1. Inserts companies into the database
2. Finds 10 real LinkedIn profiles per company (C-suite / VP / Director)
3. Generates `first.last@domain.com` emails from the company email pattern
4. Creates a named campaign
5. Personalizes once per company via LLM, clones for all other contacts
6. Sends everything via Gmail

**Example triggers:**
- *"Send 10 emails per company to Stripe, Databricks, and Anthropic"*
- *"Run the full pipeline for these 5 companies: …"*
- *"Launch an outreach campaign to the companies on this list"*

---

## `check-engagement`
**When to use:** You want to know how your sent emails are performing —
replies, bounces, delivery rates.

**What it does:**
1. Polls Gmail threads for all campaigns with unchecked emails
2. Detects replies (any inbound non-NDR message in the thread)
3. Detects bounces (NDR messages from mailer-daemon with bounce subject)
4. Updates the database with timestamps and delivery status
5. Prints a live summary of new replies and bounces per campaign

**Example triggers:**
- *"Check engagement on the Fortune 500 campaign"*
- *"Any replies yet?"*
- *"Update the bounce data for all campaigns"*

---

## `export-analytics`
**When to use:** You want a spreadsheet showing per-company engagement stats
across all campaigns.

**What it does:**
1. Optionally runs a fresh engagement check first
2. Queries all sent emails across every campaign
3. Aggregates by company: sent count, replies, bounces, reply%, bounce%
4. Writes `master_analytics_all_campaigns.csv`
5. Prints the full table inline sorted by reply rate

**Example triggers:**
- *"Make me a master sequencing spreadsheet"*
- *"Export the analytics for all campaigns"*
- *"Show me the engagement stats for all companies"*

---

## `personalize-template`
**When to use:** You have a custom email template with `[Placeholder]` tags
and want it filled in for specific companies or contacts.

**What it does:**
1. Detects static tags (`[First Name]`, `[Company Name]`, etc.) and fills
   them from data — no LLM needed
2. Detects dynamic tags (`[Personalization for company]`, `[Custom hook]`,
   etc.) and generates 1–2 sentences per company via LLM (once per company)
3. Clones + swaps names/titles for all other contacts at the same company
4. Returns completed emails ready to review or send

**Example triggers:**
- *"Personalize this template for Stripe and OpenAI"*
- *"Here's my email template — fill it in for these contacts"*
- *"Use this template with the existing contacts for Databricks"*

---

## Architecture notes

| Component | File |
|---|---|
| Template utilities | `template_personalizer.py` |
| LLM client (Anthropic → Perplexity fallback) | `claude_client.py` |
| DB-coupled personalization orchestrator | `personalize_once.py` |
| Gmail send + engagement tracking | `gmail_client.py` |
| Engagement check + CSV export | `campaign.py`, `run_master_analytics.py` |
| Example pipeline scripts | `run_fortune500_pipeline.py`, `run_batch3_pipeline.py` |
| Database | `outreach.db` (SQLite) |
