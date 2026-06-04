#!/usr/bin/env python3
"""Fast email sender with minimal delays (2-4 seconds between sends)."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import sqlite3
import time
import random
from datetime import datetime
from gmail_client import GmailClient

def main():
    # Get campaign ID from command line, or use default
    if len(sys.argv) > 1:
        CAMPAIGN_ID = sys.argv[1]
    else:
        CAMPAIGN_ID = "9471ce89-6106-49b5-8e07-ff83755c9fc9"
    gmail = GmailClient()
    conn = sqlite3.connect('outreach.db', timeout=60.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout=60000")
    try:
        conn.execute("PRAGMA journal_mode=WAL")
    except sqlite3.OperationalError:
        pass

    def safe_exec(sql, params, retries=10):
        for i in range(retries):
            try:
                conn.execute(sql, params)
                conn.commit()
                return True
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and i < retries - 1:
                    time.sleep(2 + i)
                    continue
                raise

    total_sent = 0
    total_failed = 0

    while True:
        cur = conn.cursor()
        rows = cur.execute("""
            SELECT sr.id as sr_id, sr.message_id, ct.primary_email, ct.first_name, ct.last_name,
                   pm.subject, pm.body, c.name as company_name
            FROM send_records sr
            JOIN contacts ct ON sr.contact_id = ct.id
            JOIN companies c ON ct.company_id = c.id
            JOIN personalized_messages pm ON sr.message_id = pm.id
            WHERE sr.campaign_id = ? AND sr.status = 'queued'
            ORDER BY sr.id
            LIMIT 50
        """, (CAMPAIGN_ID,)).fetchall()

        if not rows:
            # Check if personalization is still adding new queued records
            queued_count = cur.execute(
                "SELECT COUNT(*) FROM send_records WHERE campaign_id = ? AND status = 'queued'",
                (CAMPAIGN_ID,)
            ).fetchone()[0]
            if queued_count == 0:
                print(f"[*] No more queued emails. Waiting 30s for more from personalization...")
                time.sleep(30)
                queued_count = cur.execute(
                    "SELECT COUNT(*) FROM send_records WHERE campaign_id = ? AND status = 'queued'",
                    (CAMPAIGN_ID,)
                ).fetchone()[0]
                if queued_count == 0:
                    print(f"[OK] All done. Sent: {total_sent}, Failed: {total_failed}")
                    break
            continue

        for row in rows:
            try:
                result = gmail.send_email(
                    to=row['primary_email'],
                    subject=row['subject'],
                    body=row['body']
                )
                safe_exec(
                    "UPDATE send_records SET status='sent', gmail_message_id=?, gmail_thread_id=?, sent_at=? WHERE id=?",
                    (result.get('id'), result.get('threadId'), datetime.now().isoformat(), row['sr_id'])
                )
                total_sent += 1
                if total_sent % 10 == 0:
                    print(f"[{total_sent} sent] {row['company_name']} - {row['first_name']} {row['last_name']}")
            except Exception as e:
                safe_exec(
                    "UPDATE send_records SET status='failed', error=? WHERE id=?",
                    (str(e)[:500], row['sr_id'])
                )
                total_failed += 1
                print(f"[FAIL] {row['primary_email']}: {str(e)[:100]}")

            # Fast delay: 2-4 seconds
            time.sleep(random.uniform(2.0, 4.0))

    conn.close()

if __name__ == "__main__":
    main()
