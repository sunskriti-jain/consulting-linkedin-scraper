"""Resume batch 4 send — personalization already done, 137 emails queued."""
import sys, time, random, sqlite3
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from gmail_client import GmailClient
from datetime import datetime

CAMPAIGN_ID = "074554f4-7be6-4686-bd78-f5fa1e499afd"
CAMPAIGN_NAME = "Batch 4 Outreach - June 2026"

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

queued = conn_s.execute(
    "SELECT COUNT(*) as n FROM send_records WHERE campaign_id=? AND status='queued'",
    (CAMPAIGN_ID,),
).fetchone()["n"]
print(f"Resuming '{CAMPAIGN_NAME}' — {queued} emails queued")

gmail = GmailClient()
total_sent = total_failed = 0

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
    """, (CAMPAIGN_ID,)).fetchall()

    if not rows:
        print(f"\n[ALL DONE] Campaign '{CAMPAIGN_NAME}'")
        print(f"  Sent: {total_sent} | Failed: {total_failed}")
        print(f"  Campaign ID: {CAMPAIGN_ID}")
        break

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
