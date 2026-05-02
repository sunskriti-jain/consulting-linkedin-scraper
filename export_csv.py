#!/usr/bin/env python3
"""Export campaign results with real personalization extracts."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import sqlite3
import csv
import re

CAMPAIGN_ID = "9471ce89-6106-49b5-8e07-ff83755c9fc9"
OUTPUT_FILE = "bbs_outreach_all_personalization.csv"

def extract_personalization(body: str) -> str:
    """Extract the 2-3 middle sentences that are the actual company-specific personalization."""
    if not body:
        return ""
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    skip_keywords = [
        "Hi ", "Berkeley Business Society", "specializes in", "partners with",
        "lead Berkeley", "I'm a consultant", "My name is", "semester-long",
        "We're selecting", "Would you be open", "calendly", "Happy to share",
        "Best,", "Eleyn Xiong", "UC Berkeley", "Past teams",
    ]
    kept = []
    for line in lines:
        if any(kw.lower() in line.lower() for kw in skip_keywords):
            continue
        if len(line) < 10:
            continue
        kept.append(line)
    joined = " ".join(kept).strip()
    if len(joined) > 400:
        sentences = re.split(r'(?<=[.!?])\s+', joined)
        out = ""
        for s in sentences:
            if out and len(out) + len(s) > 400:
                break
            out += s + " "
        joined = out.strip()
    return joined

def main():
    conn = sqlite3.connect('outreach.db')
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT c.name as company, ct.first_name, ct.last_name, ct.title, ct.primary_email,
               sr.status, pm.body, pm.subject
        FROM send_records sr
        JOIN contacts ct ON sr.contact_id = ct.id
        JOIN companies c ON ct.company_id = c.id
        JOIN personalized_messages pm ON sr.message_id = pm.id
        WHERE sr.campaign_id = ? AND sr.step_number = 1
        ORDER BY c.name, ct.last_name
    """, (CAMPAIGN_ID,)).fetchall()

    print(f"Exporting {len(rows)} records to {OUTPUT_FILE}")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Company", "Contact Name", "Role", "First Name", "Last Name",
            "Email", "Status", "Subject", "Personalization"
        ])
        for r in rows:
            personalization = extract_personalization(r["body"])
            writer.writerow([
                r["company"],
                f"{r['first_name']} {r['last_name']}",
                r["title"] or "",
                r["first_name"],
                r["last_name"],
                r["primary_email"] or "",
                r["status"],
                r["subject"] or "",
                personalization,
            ])

    # Summary by company
    conn.row_factory = None
    cur = conn.execute("""
        SELECT c.name, sr.status, COUNT(*) as cnt
        FROM send_records sr
        JOIN contacts ct ON sr.contact_id = ct.id
        JOIN companies c ON ct.company_id = c.id
        WHERE sr.campaign_id = ?
        GROUP BY c.name, sr.status
        ORDER BY c.name
    """, (CAMPAIGN_ID,)).fetchall()
    print("\nPer-company:")
    current = None
    for name, status, cnt in cur:
        if name != current:
            print(f"\n  {name}:")
            current = name
        print(f"    {status}: {cnt}")

    conn.close()

if __name__ == "__main__":
    main()
