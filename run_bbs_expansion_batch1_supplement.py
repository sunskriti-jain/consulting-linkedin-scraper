"""
BBS Expansion Batch 1 supplement — adds NVIDIA, Cisco Systems, HP to the
existing campaign (contacts were ingested after the main pipeline already ran).
Reuses the same campaign ID so everything stays in one campaign.
"""
import sys, time, random, sqlite3
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from db import get_db, new_id
from personalize_once import personalize_once_per_company
from gmail_client import GmailClient
from datetime import datetime

CAMPAIGN_NAME = "BBS Expansion Batch 1 - June 2026"
COMPANY_DOMAINS = ["nvidia.com", "cisco.com", "hp.com"]
SENDER_VALUE_PROP = (
    "Berkeley Business Society is UC Berkeley's oldest and most selective consulting club, "
    "founded in 1999. Our alumni have gone on to lead at McKinsey, Bain, BCG, Goldman Sachs, "
    "Google, Apple, and hundreds of venture-backed startups. We work with companies on "
    "semester-long consulting engagements — market research, growth strategy, product analysis, "
    "and go-to-market planning — delivering Fortune 500-quality work from Berkeley's top "
    "analytical and business talent."
)

with get_db() as conn:
    row = conn.execute("SELECT id FROM campaigns WHERE name=?", (CAMPAIGN_NAME,)).fetchone()
    if not row:
        raise RuntimeError(f"Campaign '{CAMPAIGN_NAME}' not found — run main pipeline first")
    campaign_id = row["id"]
print(f"Campaign ID: {campaign_id}")

print("\nPersonalizing NVIDIA, Cisco Systems, HP...")
personalize_once_per_company(campaign_id, SENDER_VALUE_PROP, num_steps=3,
    company_domains=COMPANY_DOMAINS, template="bbs",
    max_contacts_per_company=10, exclude_contacted=True)

print("\nSending queued emails for supplement companies...")
with get_db() as conn:
    queued = conn.execute("SELECT COUNT(*) as n FROM send_records WHERE campaign_id=? AND status='queued'",
        (campaign_id,)).fetchone()["n"]
print(f"  {queued} emails queued — sending...")

gmail = GmailClient()
conn_s = sqlite3.connect("outreach.db", timeout=60)
conn_s.row_factory = sqlite3.Row
conn_s.execute("PRAGMA foreign_keys=ON"); conn_s.execute("PRAGMA busy_timeout=60000")
try: conn_s.execute("PRAGMA journal_mode=WAL")
except: pass

def safe_exec(sql, params, retries=10):
    for i in range(retries):
        try: conn_s.execute(sql, params); conn_s.commit(); return
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and i < retries-1: time.sleep(2+i)
            else: raise

total_sent = total_failed = wait_rounds = 0
while True:
    rows = conn_s.execute("""
        SELECT sr.id as sr_id, ct.primary_email, ct.first_name, ct.last_name,
               pm.subject, pm.body, co.name as company_name
        FROM send_records sr JOIN contacts ct ON sr.contact_id=ct.id
        JOIN companies co ON ct.company_id=co.id
        JOIN personalized_messages pm ON sr.message_id=pm.id
        WHERE sr.campaign_id=? AND sr.status='queued' ORDER BY sr.id LIMIT 50
    """, (campaign_id,)).fetchall()
    if not rows:
        if wait_rounds >= 2: print(f"\n[DONE] Sent: {total_sent}  Failed: {total_failed}"); break
        print("[*] Waiting 30s..."); time.sleep(30); wait_rounds += 1; continue
    wait_rounds = 0
    for row in rows:
        try:
            result = gmail.send_email(to=row["primary_email"], subject=row["subject"], body=row["body"])
            safe_exec("UPDATE send_records SET status='sent',gmail_message_id=?,gmail_thread_id=?,sent_at=? WHERE id=?",
                (result["id"], result["threadId"], datetime.now().isoformat(), row["sr_id"]))
            total_sent += 1
            print(f"  [{total_sent}] {row['company_name']} - {row['first_name']} {row['last_name']} <{row['primary_email']}>")
        except Exception as e:
            safe_exec("UPDATE send_records SET status='failed',error=? WHERE id=?", (str(e)[:500], row["sr_id"]))
            total_failed += 1; print(f"  [FAIL] {row['primary_email']}: {str(e)[:80]}")
        time.sleep(random.uniform(2.0, 4.0))

conn_s.close()
print(f"\n[ALL DONE] BBS Expansion Batch 1 (supplement: NVIDIA + Cisco + HP)")
print(f"  Sent: {total_sent} | Failed: {total_failed}")
print(f"  Campaign ID: {campaign_id}")
