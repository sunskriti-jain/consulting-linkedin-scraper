"""
Batch 1 FV Pipeline — Free Ventures template on the original 19 Fortune 500 companies.
All contacts already in DB — skip ingest, go straight to personalize + send.
"""
import sys, time, random, sqlite3
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from db import get_db, new_id, init_db
from personalize_once import personalize_once_per_company
from gmail_client import GmailClient
from datetime import datetime

init_db()

COMPANY_DOMAINS = [
    "abbott.com",
    "anduril.com",
    "apple.com",
    "boeing.com",
    "johndeere.com",
    "ford.com",
    "gm.com",
    "google.com",
    "jnj.com",
    "lmco.com",
    "microsoft.com",
    "netflix.com",
    "openai.com",
    "palantir.com",
    "pg.com",
    "rtx.com",
    "salesforce.com",
    "stripe.com",
    "walmart.com",
]

CAMPAIGN_NAME = "Batch 1 FV Outreach - June 2026"

SENDER_VALUE_PROP = (
    "Free Ventures at UC Berkeley is the university's leading pre-seed startup "
    "accelerator and only nonprofit, student-run program of its kind. Over the past "
    "decade, we've helped 100+ portfolio companies raise $200M+ in follow-on capital "
    "from Kleiner Perkins, Accel, and Greylock, with multiple YC exits and acquisitions "
    "by Coinbase, Discord, and Opendoor. We partner with companies on strategy, product, "
    "and growth challenges — bringing Berkeley's sharpest founders and operators to work "
    "directly on your hardest problems."
)

# ── Verify contacts are present ───────────────────────────────────────────────
print("\n" + "="*60)
print("Contact counts (existing):")
print("="*60)
with get_db() as conn:
    for domain in COMPANY_DOMAINS:
        row = conn.execute(
            """SELECT co.name,
               SUM(CASE WHEN ct.primary_email IS NOT NULL AND ct.primary_email != '' THEN 1 ELSE 0 END) as with_email
               FROM companies co
               LEFT JOIN contacts ct ON ct.company_id = co.id
               WHERE co.domain = ?
               GROUP BY co.id""",
            (domain,)
        ).fetchone()
        if row:
            status = "OK" if (row["with_email"] or 0) >= 5 else "LOW"
            print(f"  [{status}] {row['name']}: {row['with_email'] or 0} with email")
        else:
            print(f"  [MISSING] {domain}")

# ── Create campaign ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 1: Creating campaign")
print("="*60)
with get_db() as conn:
    existing = conn.execute("SELECT id FROM campaigns WHERE name=?", (CAMPAIGN_NAME,)).fetchone()
    if existing:
        campaign_id = existing["id"]
        print(f"  Already exists: {campaign_id}")
    else:
        campaign_id = new_id()
        conn.execute(
            "INSERT INTO campaigns (id, name, daily_cap) VALUES (?,?,?)",
            (campaign_id, CAMPAIGN_NAME, 100),
        )
        print(f"  Created: {CAMPAIGN_NAME}")
print(f"  Campaign ID: {campaign_id}")

# ── Personalize ───────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 2: Personalizing with Free Ventures template")
print("="*60)
personalize_once_per_company(
    campaign_id,
    SENDER_VALUE_PROP,
    num_steps=3,
    company_domains=COMPANY_DOMAINS,
    template="fv",
)

# ── Send ──────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 3: Sending queued emails")
print("="*60)

with get_db() as conn:
    queued = conn.execute(
        "SELECT COUNT(*) as n FROM send_records WHERE campaign_id=? AND status='queued'",
        (campaign_id,),
    ).fetchone()["n"]
print(f"  {queued} emails queued — sending...")

gmail  = GmailClient()
conn_s = sqlite3.connect("outreach.db", timeout=60)
conn_s.row_factory = sqlite3.Row
conn_s.execute("PRAGMA foreign_keys = ON")
conn_s.execute("PRAGMA busy_timeout=60000")
try:
    conn_s.execute("PRAGMA journal_mode=WAL")
except Exception:
    pass

def safe_exec(sql, params, retries=10):
    for i in range(retries):
        try:
            conn_s.execute(sql, params)
            conn_s.commit()
            return
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and i < retries - 1:
                time.sleep(2 + i)
            else:
                raise

total_sent = total_failed = 0
wait_rounds = 0

while True:
    rows = conn_s.execute("""
        SELECT sr.id as sr_id, ct.primary_email, ct.first_name, ct.last_name,
               pm.subject, pm.body, co.name as company_name
        FROM send_records sr
        JOIN contacts  ct ON sr.contact_id  = ct.id
        JOIN companies co ON ct.company_id  = co.id
        JOIN personalized_messages pm ON sr.message_id = pm.id
        WHERE sr.campaign_id=? AND sr.status='queued'
        ORDER BY sr.id LIMIT 50
    """, (campaign_id,)).fetchall()

    if not rows:
        if wait_rounds >= 2:
            print(f"\n[DONE] Sent: {total_sent}  Failed: {total_failed}")
            break
        print("[*] Waiting 30s for personalization...")
        time.sleep(30)
        wait_rounds += 1
        continue
    wait_rounds = 0

    for row in rows:
        try:
            result = gmail.send_email(to=row["primary_email"], subject=row["subject"], body=row["body"])
            safe_exec(
                "UPDATE send_records SET status='sent', gmail_message_id=?, gmail_thread_id=?, sent_at=? WHERE id=?",
                (result["id"], result["threadId"], datetime.now().isoformat(), row["sr_id"]),
            )
            total_sent += 1
            print(f"  [{total_sent}] {row['company_name']} - {row['first_name']} {row['last_name']} <{row['primary_email']}>")
        except Exception as e:
            safe_exec("UPDATE send_records SET status='failed', error=? WHERE id=?", (str(e)[:500], row["sr_id"]))
            total_failed += 1
            print(f"  [FAIL] {row['primary_email']}: {str(e)[:80]}")
        time.sleep(random.uniform(2.0, 4.0))

conn_s.close()
print(f"\n[ALL DONE] Campaign '{CAMPAIGN_NAME}'")
print(f"  Sent: {total_sent} | Failed: {total_failed}")
print(f"  Campaign ID: {campaign_id}")
