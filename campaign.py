"""Campaign orchestration: discovery -> research -> personalize -> send."""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import csv
import time
import random
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional

import config
from db import get_db, new_id, now, init_db
from hunter_client import HunterClient
from claude_client import ClaudeClient
from gmail_client import GmailClient
import email_fallback


# --------------------------------------------------------------------------
# IMPORT
# --------------------------------------------------------------------------
def import_companies_csv(csv_path: str) -> int:
    """CSV columns: name, domain, [industry]"""
    count = 0
    with get_db() as conn:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("name") or row.get("company_name") or "").strip()
                domain = (row.get("domain") or "").strip().lower().replace("https://", "").replace("http://", "").rstrip("/")
                industry = (row.get("industry") or "").strip()
                if not name or not domain:
                    continue
                try:
                    conn.execute(
                        "INSERT INTO companies (id, name, domain, industry) VALUES (?, ?, ?, ?)",
                        (new_id(), name, domain, industry),
                    )
                    count += 1
                except Exception:
                    pass  # duplicate domain
    return count


def import_contacts_csv(csv_path: str) -> int:
    """Optional CSV to pre-seed contacts. Columns: first_name, last_name, title, company_domain, linkedin_url"""
    count = 0
    with get_db() as conn:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                domain = (row.get("company_domain") or row.get("domain") or "").strip().lower()
                if not domain:
                    continue
                company = conn.execute("SELECT id FROM companies WHERE domain = ?", (domain,)).fetchone()
                if not company:
                    continue
                conn.execute(
                    "INSERT INTO contacts (id, company_id, first_name, last_name, title, linkedin_url) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        new_id(),
                        company["id"],
                        row.get("first_name", "").strip(),
                        row.get("last_name", "").strip(),
                        row.get("title", "").strip(),
                        row.get("linkedin_url", "").strip(),
                    ),
                )
                count += 1
    return count


def create_campaign(name: str, daily_cap: int = None) -> str:
    daily_cap = daily_cap or config.DAILY_EMAIL_CAP
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM campaigns WHERE name = ?", (name,)).fetchone()
        if existing:
            return existing["id"]
        cid = new_id()
        conn.execute(
            "INSERT INTO campaigns (id, name, daily_cap) VALUES (?, ?, ?)",
            (cid, name, daily_cap),
        )
        return cid


# --------------------------------------------------------------------------
# DISCOVERY
# --------------------------------------------------------------------------
def _get_or_detect_pattern(conn, company) -> tuple:
    """Return (pattern, confidence). Cache on the company row."""
    if company["email_pattern"]:
        return company["email_pattern"], company["email_pattern_confidence"] or 0.0
    print(f"  [fallback] searching for pattern on {company['domain']}...")
    pattern, conf, _samples = email_fallback.discover_pattern(company["domain"])
    conn.execute(
        "UPDATE companies SET email_pattern = ?, email_pattern_confidence = ? WHERE id = ?",
        (pattern, conf, company["id"]),
    )
    conn.commit()
    return pattern, conf


def discover_emails(max_contacts_per_company: int = 3, use_domain_search: bool = True, use_hunter: bool = True, limit: Optional[int] = None):
    """For each company:
    - If contacts exist: try Hunter (if enabled), then fall back to pattern-guess via DDG search.
    - Else: use Hunter domain-search (if enabled) to discover contacts + emails.

    Set use_hunter=False to run purely on the free DDG fallback (requires pre-seeded contacts).
    """
    hunter = HunterClient() if use_hunter else None
    with get_db() as conn:
        if limit:
            companies = conn.execute("SELECT * FROM companies ORDER BY created_at LIMIT ?", (limit,)).fetchall()
        else:
            companies = conn.execute("SELECT * FROM companies ORDER BY created_at").fetchall()
        print(f"Processing {len(companies)} companies (hunter={'on' if use_hunter else 'off'})...")

        for company in companies:
            print(f"\n[{company['name']}] ({company['domain']})")

            existing_contacts = conn.execute(
                "SELECT * FROM contacts WHERE company_id = ?", (company["id"],)
            ).fetchall()

            if existing_contacts:
                for contact in existing_contacts:
                    if contact["primary_email"]:
                        continue

                    result = None
                    if hunter:
                        result = hunter.find_email(
                            contact["first_name"], contact["last_name"], company["domain"]
                        )

                    if result:
                        conn.execute(
                            "UPDATE contacts SET primary_email = ?, email_confidence = ?, status = 'email_found' WHERE id = ?",
                            (result["email"], result["confidence"], contact["id"]),
                        )
                        print(f"  + {contact['first_name']} {contact['last_name']} -> {result['email']} ({result['confidence']:.0f}%) [hunter]")
                    else:
                        # Fallback: pattern-guess
                        pattern, pat_conf = _get_or_detect_pattern(conn, company)
                        guessed = email_fallback.guess_email(
                            contact["first_name"], contact["last_name"],
                            company["domain"], pattern,
                        )
                        if guessed:
                            # Final confidence = pattern confidence, capped at 65
                            conf = min(pat_conf, 65.0)
                            conn.execute(
                                "UPDATE contacts SET primary_email = ?, email_confidence = ?, status = 'email_guessed' WHERE id = ?",
                                (guessed, conf, contact["id"]),
                            )
                            print(f"  ~ {contact['first_name']} {contact['last_name']} -> {guessed} ({conf:.0f}%) [guess, pattern={pattern}]")
                        else:
                            print(f"  - No email for {contact['first_name']} {contact['last_name']}")
                    time.sleep(1)
            elif use_domain_search and hunter:
                results = hunter.domain_search(company["domain"], limit=max_contacts_per_company)
                for r in results[:max_contacts_per_company]:
                    if not (r["first_name"] and r["last_name"] and r["email"]):
                        continue
                    conn.execute(
                        """INSERT INTO contacts
                        (id, company_id, first_name, last_name, title, linkedin_url, primary_email, email_confidence, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'email_found')""",
                        (
                            new_id(),
                            company["id"],
                            r["first_name"],
                            r["last_name"],
                            r["title"] or "",
                            r["linkedin_url"] or "",
                            r["email"],
                            r["confidence"],
                        ),
                    )
                    print(f"  + {r['first_name']} {r['last_name']} ({r['title']}) -> {r['email']} ({r['confidence']:.0f}%)")
                time.sleep(1)

            conn.execute(
                "UPDATE companies SET status = 'discovery_complete' WHERE id = ?",
                (company["id"],),
            )
            conn.commit()


# --------------------------------------------------------------------------
# RESEARCH
# --------------------------------------------------------------------------
def research_companies(limit: Optional[int] = None):
    claude = ClaudeClient()
    with get_db() as conn:
        q = """SELECT c.* FROM companies c
            LEFT JOIN company_research r ON c.id = r.company_id
            WHERE r.id IS NULL
            ORDER BY c.created_at"""
        if limit:
            q += " LIMIT ?"
            companies = conn.execute(q, (limit,)).fetchall()
        else:
            companies = conn.execute(q).fetchall()

        print(f"Researching {len(companies)} companies...")
        for company in companies:
            print(f"\n[{company['name']}]")
            research = claude.research_company(
                company["name"], company["domain"], company["industry"] or ""
            )
            conn.execute(
                """INSERT INTO company_research (id, company_id, summary, pain_points, value_prop)
                VALUES (?, ?, ?, ?, ?)""",
                (
                    new_id(),
                    company["id"],
                    research.get("summary", ""),
                    json.dumps({"pain_points": research.get("pain_points", []), "hook": research.get("hook", "")}),
                    research.get("value_prop", ""),
                ),
            )
            conn.execute("UPDATE companies SET status = 'researched' WHERE id = ?", (company["id"],))
            conn.commit()
            print(f"  hook: {research.get('hook', '')[:80]}")


# --------------------------------------------------------------------------
# PERSONALIZE
# --------------------------------------------------------------------------
def personalize(campaign_id: str, sender_value_prop: str, num_steps: int = 3, limit: Optional[int] = None):
    """Generate personalized messages for all contacts in campaign. Enrolls all contacts with emails."""
    claude = ClaudeClient()
    with get_db() as conn:
        q = """SELECT ct.*, c.name as company_name, c.domain,
                      r.summary, r.pain_points, r.value_prop
               FROM contacts ct
               JOIN companies c ON ct.company_id = c.id
               LEFT JOIN company_research r ON c.id = r.company_id
               WHERE ct.primary_email IS NOT NULL AND ct.primary_email != ''
               ORDER BY c.created_at, ct.created_at"""
        if limit:
            q += " LIMIT ?"
            contacts = conn.execute(q, (limit,)).fetchall()
        else:
            contacts = conn.execute(q).fetchall()

        print(f"Personalizing for {len(contacts)} contacts x {num_steps} steps...")

        for contact in contacts:
            research_data = {}
            if contact["pain_points"]:
                try:
                    pp = json.loads(contact["pain_points"])
                    research_data = {
                        "summary": contact["summary"] or "",
                        "pain_points": pp.get("pain_points", []),
                        "hook": pp.get("hook", ""),
                        "value_prop": contact["value_prop"] or "",
                    }
                except json.JSONDecodeError:
                    pass

            for step in range(1, num_steps + 1):
                existing = conn.execute(
                    "SELECT id FROM personalized_messages WHERE contact_id = ? AND campaign_id = ? AND step_number = ?",
                    (contact["id"], campaign_id, step),
                ).fetchone()
                if existing:
                    continue

                msg = claude.personalize_email(
                    first_name=contact["first_name"],
                    last_name=contact["last_name"],
                    title=contact["title"] or "",
                    company_name=contact["company_name"],
                    research=research_data,
                    sender_name=config.SENDER_NAME,
                    sender_title=config.SENDER_TITLE,
                    sender_company=config.SENDER_COMPANY,
                    value_prop_from_sender=sender_value_prop,
                    step_number=step,
                )
                msg_id = new_id()
                conn.execute(
                    """INSERT INTO personalized_messages (id, contact_id, campaign_id, step_number, subject, body)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (msg_id, contact["id"], campaign_id, step, msg["subject"], msg["body"]),
                )
                # Queue send_record for step 1 only; later steps added after prior sends
                if step == 1:
                    conn.execute(
                        """INSERT INTO send_records (id, campaign_id, contact_id, message_id, step_number, status)
                        VALUES (?, ?, ?, ?, ?, 'queued')""",
                        (new_id(), campaign_id, contact["id"], msg_id, step),
                    )
                conn.commit()
            print(f"  [{contact['company_name']}] {contact['first_name']} {contact['last_name']} x {num_steps}")


# --------------------------------------------------------------------------
# PREVIEW
# --------------------------------------------------------------------------
def preview(campaign_id: str, n: int = 5):
    with get_db() as conn:
        msgs = conn.execute(
            """SELECT pm.*, ct.first_name, ct.last_name, ct.primary_email, c.name as company_name
               FROM personalized_messages pm
               JOIN contacts ct ON pm.contact_id = ct.id
               JOIN companies c ON ct.company_id = c.id
               WHERE pm.campaign_id = ? AND pm.step_number = 1
               ORDER BY RANDOM() LIMIT ?""",
            (campaign_id, n),
        ).fetchall()

        for m in msgs:
            print("\n" + "=" * 70)
            print(f"TO: {m['first_name']} {m['last_name']} <{m['primary_email']}> @ {m['company_name']}")
            print(f"SUBJECT: {m['subject']}")
            print("-" * 70)
            print(m["body"])
        print("\n" + "=" * 70)


# --------------------------------------------------------------------------
# SEND
# --------------------------------------------------------------------------
def _is_business_hours() -> bool:
    now_local = datetime.now()
    h = now_local.hour
    return config.BUSINESS_HOURS_START <= h < config.BUSINESS_HOURS_END and now_local.weekday() < 5


def send_batch(campaign_id: str, ignore_business_hours: bool = False, max_sends: int = None):
    """Send queued emails for a campaign in a batch with delays."""
    if not ignore_business_hours and not _is_business_hours():
        print(f"Outside business hours ({config.BUSINESS_HOURS_START}:00-{config.BUSINESS_HOURS_END}:00 local, Mon-Fri). Use --force to override.")
        return

    gmail = GmailClient()
    with get_db() as conn:
        # Check daily cap
        daily_cap = conn.execute("SELECT daily_cap FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()["daily_cap"]
        sent_today = conn.execute(
            """SELECT COUNT(*) as c FROM send_records
               WHERE campaign_id = ? AND status = 'sent'
               AND date(sent_at) = date('now')""",
            (campaign_id,),
        ).fetchone()["c"]

        remaining_cap = max(0, daily_cap - sent_today)
        batch_size = min(config.BATCH_SIZE, remaining_cap, max_sends or 999)

        if batch_size <= 0:
            print(f"Daily cap reached ({sent_today}/{daily_cap}).")
            return

        queued = conn.execute(
            """SELECT sr.id as send_id, sr.step_number, pm.subject, pm.body,
                      ct.primary_email, ct.first_name, ct.last_name
               FROM send_records sr
               JOIN personalized_messages pm ON sr.message_id = pm.id
               JOIN contacts ct ON sr.contact_id = ct.id
               WHERE sr.campaign_id = ? AND sr.status = 'queued'
               LIMIT ?""",
            (campaign_id, batch_size),
        ).fetchall()

        if not queued:
            print("No queued sends.")
            return

        print(f"Sending {len(queued)} emails (cap: {sent_today}/{daily_cap})...")
        for i, send in enumerate(queued):
            print(f"\n[{i + 1}/{len(queued)}] {send['first_name']} {send['last_name']} <{send['primary_email']}>")
            try:
                result = gmail.send_email(
                    to=send["primary_email"],
                    subject=send["subject"],
                    body=send["body"],
                )
                conn.execute(
                    """UPDATE send_records
                       SET status = 'sent', gmail_message_id = ?, gmail_thread_id = ?, sent_at = ?
                       WHERE id = ?""",
                    (result["id"], result["threadId"], now(), send["send_id"]),
                )
                conn.commit()
                print(f"  [OK] sent (msg_id: {result['id']})")
            except Exception as e:
                conn.execute(
                    "UPDATE send_records SET status = 'failed', error = ? WHERE id = ?",
                    (str(e), send["send_id"]),
                )
                conn.commit()
                print(f"  [FAIL] {e}")

            if i < len(queued) - 1:
                delay = random.randint(config.MIN_DELAY_SECONDS, config.MAX_DELAY_SECONDS)
                print(f"  waiting {delay}s...")
                time.sleep(delay)


def check_replies(campaign_id: str):
    """Poll Gmail for replies on sent threads. Mark contacts replied and queue next steps for non-replied."""
    gmail = GmailClient()
    with get_db() as conn:
        sent_records = conn.execute(
            """SELECT sr.id, sr.contact_id, sr.step_number, sr.gmail_thread_id, sr.message_id
               FROM send_records sr
               WHERE sr.campaign_id = ? AND sr.status = 'sent' AND sr.gmail_thread_id IS NOT NULL""",
            (campaign_id,),
        ).fetchall()

        replied_contacts = set()
        for sr in sent_records:
            if gmail.check_thread_replied(sr["gmail_thread_id"], config.SENDER_EMAIL):
                replied_contacts.add(sr["contact_id"])
                conn.execute(
                    "UPDATE send_records SET status = 'replied' WHERE id = ?", (sr["id"],)
                )
                conn.execute(
                    "UPDATE contacts SET status = 'replied' WHERE id = ?", (sr["contact_id"],)
                )

        # Cancel queued sends for replied contacts
        if replied_contacts:
            placeholders = ",".join("?" * len(replied_contacts))
            conn.execute(
                f"UPDATE send_records SET status = 'skipped' WHERE campaign_id = ? AND contact_id IN ({placeholders}) AND status = 'queued'",
                (campaign_id, *replied_contacts),
            )
        conn.commit()
        print(f"Replies detected: {len(replied_contacts)}")


def queue_next_step(campaign_id: str, from_step: int):
    """Queue step (from_step+1) for contacts who completed from_step and have not replied."""
    with get_db() as conn:
        candidates = conn.execute(
            """SELECT sr.contact_id FROM send_records sr
               WHERE sr.campaign_id = ? AND sr.step_number = ? AND sr.status = 'sent'
               AND sr.contact_id NOT IN (
                   SELECT contact_id FROM send_records
                   WHERE campaign_id = ? AND status IN ('replied', 'skipped')
               )
               AND sr.contact_id NOT IN (
                   SELECT contact_id FROM send_records
                   WHERE campaign_id = ? AND step_number = ?
               )""",
            (campaign_id, from_step, campaign_id, campaign_id, from_step + 1),
        ).fetchall()

        count = 0
        for c in candidates:
            msg = conn.execute(
                "SELECT id FROM personalized_messages WHERE contact_id = ? AND campaign_id = ? AND step_number = ?",
                (c["contact_id"], campaign_id, from_step + 1),
            ).fetchone()
            if not msg:
                continue
            conn.execute(
                """INSERT INTO send_records (id, campaign_id, contact_id, message_id, step_number, status)
                VALUES (?, ?, ?, ?, ?, 'queued')""",
                (new_id(), campaign_id, c["contact_id"], msg["id"], from_step + 1),
            )
            count += 1
        conn.commit()
        print(f"Queued step {from_step + 1} for {count} contacts.")


# --------------------------------------------------------------------------
# STATUS / EXPORT
# --------------------------------------------------------------------------
def status(campaign_id: str):
    with get_db() as conn:
        campaign = conn.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
        if not campaign:
            print("Campaign not found")
            return
        print(f"\n=== Campaign: {campaign['name']} ===")
        print(f"Status: {campaign['status']}  Daily cap: {campaign['daily_cap']}")

        counts = conn.execute(
            """SELECT status, step_number, COUNT(*) as c FROM send_records
               WHERE campaign_id = ? GROUP BY status, step_number""",
            (campaign_id,),
        ).fetchall()
        print("\nSends by step/status:")
        for row in counts:
            print(f"  step {row['step_number']} / {row['status']}: {row['c']}")

        sent_today = conn.execute(
            "SELECT COUNT(*) as c FROM send_records WHERE campaign_id = ? AND status = 'sent' AND date(sent_at) = date('now')",
            (campaign_id,),
        ).fetchone()["c"]
        print(f"\nSent today: {sent_today}/{campaign['daily_cap']}")


def export_csv(campaign_id: str, path: str):
    with get_db() as conn:
        rows = conn.execute(
            """SELECT c.name as company, ct.first_name, ct.last_name, ct.title,
                      ct.primary_email, ct.email_confidence, sr.step_number, sr.status, sr.sent_at
               FROM send_records sr
               JOIN contacts ct ON sr.contact_id = ct.id
               JOIN companies c ON ct.company_id = c.id
               WHERE sr.campaign_id = ?
               ORDER BY c.name, ct.last_name, sr.step_number""",
            (campaign_id,),
        ).fetchall()

        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["company", "first_name", "last_name", "title", "email", "confidence", "step", "status", "sent_at"])
            for r in rows:
                w.writerow([r["company"], r["first_name"], r["last_name"], r["title"], r["primary_email"], r["email_confidence"], r["step_number"], r["status"], r["sent_at"]])
        print(f"Exported {len(rows)} rows to {path}")
