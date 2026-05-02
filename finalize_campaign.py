#!/usr/bin/env python3
"""
Finalize the campaign: send remaining emails and export CSVs with personalization.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import sqlite3
import csv
import subprocess
import time

def extract_personalization(body):
    """Extract the company-specific hook from email body."""
    lines = body.strip().split('\n')
    personalization_lines = []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Skip greeting
        if line.startswith('Hi ') and line.endswith(','):
            continue

        # Skip BBS intro
        if any(x in line for x in ['Berkeley Business Society', 'specializes in', 'consulting club']):
            continue

        # Stop at boilerplate
        if any(x in line for x in ["We're selecting", "Would you be", "open to a"]):
            break

        # Capture substantive lines
        if i > 0 and 'Berkeley' not in line and 'specializes' not in line:
            if line:
                personalization_lines.append(line)

    personalization = ' '.join(personalization_lines).strip()

    # Truncate to 200 chars
    if len(personalization) > 200:
        personalization = personalization[:197] + "..."

    return personalization

def get_queued_count():
    """Get count of queued emails."""
    conn = sqlite3.connect('outreach.db')
    cur = conn.cursor()
    count = cur.execute("SELECT COUNT(*) FROM send_records WHERE campaign_id = '9471ce89-6106-49b5-8e07-ff83755c9fc9' AND status = 'queued'").fetchone()[0]
    conn.close()
    return count

def send_remaining():
    """Send any remaining queued emails."""
    queued = get_queued_count()
    if queued > 0:
        print(f"[*] Sending {queued} queued emails...")
        result = subprocess.run(
            ["python3", "cli.py", "send", "bbs_outreach_1", "--force"],
            capture_output=True,
            text=True,
            timeout=3600
        )
        print(result.stdout if result.stdout else "[OK] Emails sent")
        if result.stderr:
            print(f"[WARN] {result.stderr}")
    else:
        print("[OK] No queued emails")

def export_csvs():
    """Export personalized messages to CSVs."""
    conn = sqlite3.connect('outreach.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    campaign_id = '9471ce89-6106-49b5-8e07-ff83755c9fc9'

    # Get first 10 companies (for reference)
    first_10 = ["UnitedHealth Group", "CVS Health", "Berkshire Hathaway", "McKesson", "ExxonMobil",
                "Chevron", "Costco", "Cardinal Health", "Cigna", "Marathon Petroleum"]

    # Get next 25 companies
    next_25_query = """
    SELECT DISTINCT c.id, c.name
    FROM companies c
    JOIN contacts ct ON c.id = ct.company_id
    JOIN personalized_messages pm ON ct.id = pm.contact_id
    WHERE pm.campaign_id = ? AND c.name NOT IN ({})
    ORDER BY c.created_at
    LIMIT 25
    """.format(','.join(['?']*len(first_10)))

    params = [campaign_id] + first_10
    next_25_ids = cur.execute(next_25_query, params).fetchall()
    next_25_names = [row['name'] for row in next_25_ids]

    print(f"\n[*] Exporting {len(next_25_names)} new companies...")
    print(f"    Companies: {', '.join(next_25_names[:5])}...")

    # Export CSV: 25 new companies with personalization
    output_file = 'bbs_outreach_25companies_personalization.csv'

    query = """
    SELECT
        c.name as company,
        ct.first_name,
        ct.last_name,
        ct.title as role,
        ct.primary_email as email,
        sr.status,
        pm.body
    FROM personalized_messages pm
    JOIN contacts ct ON pm.contact_id = ct.id
    JOIN companies c ON ct.company_id = c.id
    LEFT JOIN send_records sr ON sr.message_id = pm.id
    WHERE pm.campaign_id = ? AND pm.step_number = 1 AND c.name IN ({})
    ORDER BY c.created_at, ct.created_at
    """.format(','.join(['?']*len(next_25_names)))

    params = [campaign_id] + next_25_names
    rows = cur.execute(query, params).fetchall()

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Company', 'Contact Name', 'Role', 'First Name', 'Last Name', 'Email', 'Status', 'Personalization'])

        for row in rows:
            personalization = extract_personalization(row['body'])
            contact_name = f"{row['first_name']} {row['last_name']}"
            writer.writerow([
                row['company'],
                contact_name,
                row['role'] or '',
                row['first_name'],
                row['last_name'],
                row['email'],
                row['status'] or 'queued',
                personalization
            ])

    print(f"[OK] Exported {len(rows)} records to {output_file}")

    # Also export all 35 companies for completeness
    all_output = 'bbs_outreach_all35companies_personalization.csv'
    all_query = """
    SELECT
        c.name as company,
        ct.first_name,
        ct.last_name,
        ct.title as role,
        ct.primary_email as email,
        sr.status,
        pm.body
    FROM personalized_messages pm
    JOIN contacts ct ON pm.contact_id = ct.id
    JOIN companies c ON ct.company_id = c.id
    LEFT JOIN send_records sr ON sr.message_id = pm.id
    WHERE pm.campaign_id = ? AND pm.step_number = 1
    ORDER BY c.created_at, ct.created_at
    """

    all_rows = cur.execute(all_query, (campaign_id,)).fetchall()

    with open(all_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Company', 'Contact Name', 'Role', 'First Name', 'Last Name', 'Email', 'Status', 'Personalization'])

        for row in all_rows:
            personalization = extract_personalization(row['body'])
            contact_name = f"{row['first_name']} {row['last_name']}"
            writer.writerow([
                row['company'],
                contact_name,
                row['role'] or '',
                row['first_name'],
                row['last_name'],
                row['email'],
                row['status'] or 'queued',
                personalization
            ])

    print(f"[OK] Exported {len(all_rows)} records to {all_output}")

    conn.close()

if __name__ == "__main__":
    print("[*] Finalizing campaign...")

    # Send any remaining emails
    send_remaining()

    # Give Gmail API a moment
    time.sleep(2)

    # Export CSVs
    export_csvs()

    print("\n[OK] Campaign finalized!")
