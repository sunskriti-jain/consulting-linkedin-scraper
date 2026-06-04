"""
Personalize emails ONCE per company, then clone and substitute for remaining contacts.
This reduces LLM calls significantly while maintaining personalization variety through name/title swaps.
"""
import json
from typing import Dict, List
from db import get_db, new_id, now
from claude_client import ClaudeClient
from template_personalizer import clone_for_contact
import config


def personalize_once_per_company(campaign_id: str, sender_value_prop: str, num_steps: int = 3, max_companies: int = None, company_domains: list = None):
    """
    For each company:
    1. Research the company once
    2. Personalize email for the FIRST contact in that company
    3. Clone that email and substitute names/titles for all other contacts in the company

    company_domains: if provided, only process companies whose domain is in this list
    """
    claude = ClaudeClient()
    with get_db() as conn:
        # Get all companies that have contacts with emails, grouped
        if company_domains:
            placeholders = ",".join("?" * len(company_domains))
            q = f"""
            SELECT DISTINCT c.id, c.name, c.domain, c.industry, COUNT(ct.id) as contact_count
            FROM companies c
            JOIN contacts ct ON c.id = ct.company_id
            WHERE ct.primary_email IS NOT NULL AND ct.primary_email != ''
            AND c.domain IN ({placeholders})
            GROUP BY c.id, c.name, c.domain
            ORDER BY c.created_at
            """
            if max_companies:
                q += f" LIMIT {max_companies}"
            companies = conn.execute(q, company_domains).fetchall()
        else:
            q = """
            SELECT DISTINCT c.id, c.name, c.domain, c.industry, COUNT(ct.id) as contact_count
            FROM companies c
            JOIN contacts ct ON c.id = ct.company_id
            WHERE ct.primary_email IS NOT NULL AND ct.primary_email != ''
            GROUP BY c.id, c.name, c.domain
            ORDER BY c.created_at
            """
            if max_companies:
                q += f" LIMIT {max_companies}"
            companies = conn.execute(q).fetchall()
        print(f"Personalizing {len(companies)} companies with {num_steps} steps (once-per-company strategy)...")

        total_contacts = 0

        for company in companies:
            print(f"\n[{company['name']}] ({company['contact_count']} contacts)")

            # 1. RESEARCH THE COMPANY (once)
            existing_research = conn.execute(
                "SELECT * FROM company_research WHERE company_id = ?",
                (company['id'],)
            ).fetchone()

            if not existing_research:
                print(f"  Researching company...")
                research = claude.research_company(
                    company['name'], company['domain'], company['industry'] or ""
                )
                conn.execute(
                    """INSERT INTO company_research (id, company_id, summary, pain_points, value_prop)
                    VALUES (?, ?, ?, ?, ?)""",
                    (
                        new_id(),
                        company['id'],
                        research.get('summary', ''),
                        json.dumps({'pain_points': research.get('pain_points', []), 'hook': research.get('hook', '')}),
                        research.get('value_prop', ''),
                    ),
                )
                conn.commit()
            else:
                research = {
                    'summary': existing_research['summary'],
                    'pain_points': [],
                    'hook': '',
                    'value_prop': existing_research['value_prop'],
                }
                try:
                    pp = json.loads(existing_research['pain_points'])
                    research['pain_points'] = pp.get('pain_points', [])
                    research['hook'] = pp.get('hook', '')
                except:
                    pass

            # Get all contacts for this company
            contacts = conn.execute(
                """SELECT * FROM contacts
                   WHERE company_id = ? AND primary_email IS NOT NULL AND primary_email != ''
                   ORDER BY created_at""",
                (company['id'],)
            ).fetchall()

            if not contacts:
                print(f"  No contacts with emails.")
                continue

            # 2. PERSONALIZE FIRST CONTACT (once per company per step)
            first_contact = contacts[0]
            print(f"  LLM personalize: {first_contact['first_name']} {first_contact['last_name']} ({first_contact['title']})")

            for step in range(1, num_steps + 1):
                # Check if already personalized
                existing = conn.execute(
                    "SELECT id FROM personalized_messages WHERE contact_id = ? AND campaign_id = ? AND step_number = ?",
                    (first_contact['id'], campaign_id, step),
                ).fetchone()

                if existing:
                    continue

                # Call LLM for first contact
                msg = claude.personalize_email(
                    first_name=first_contact['first_name'],
                    last_name=first_contact['last_name'],
                    title=first_contact['title'] or '',
                    company_name=company['name'],
                    research=research,
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
                    (msg_id, first_contact['id'], campaign_id, step, msg['subject'], msg['body']),
                )

                # Queue send record for step 1 only
                if step == 1:
                    conn.execute(
                        """INSERT INTO send_records (id, campaign_id, contact_id, message_id, step_number, status)
                        VALUES (?, ?, ?, ?, ?, 'queued')""",
                        (new_id(), campaign_id, first_contact['id'], msg_id, step),
                    )

                conn.commit()

            # 3. CLONE FOR REMAINING CONTACTS (substitute names/titles)
            if len(contacts) > 1:
                print(f"  Cloning for {len(contacts) - 1} other contacts (name/title substitution)...")

                # Get the personalized messages for the first contact
                first_messages = conn.execute(
                    "SELECT * FROM personalized_messages WHERE contact_id = ? AND campaign_id = ?",
                    (first_contact['id'], campaign_id),
                ).fetchall()

                for contact in contacts[1:]:
                    for orig_msg in first_messages:
                        # Substitute names and titles in subject and body
                        # Uses clone_for_contact from template_personalizer —
                        # word-boundary safe, handles first + last + title.
                        new_subject = clone_for_contact(
                            orig_msg['subject'],
                            dict(first_contact),
                            dict(contact),
                        )

                        new_body = clone_for_contact(
                            orig_msg['body'],
                            dict(first_contact),
                            dict(contact),
                        )

                        # Check if already personalized
                        existing = conn.execute(
                            "SELECT id FROM personalized_messages WHERE contact_id = ? AND campaign_id = ? AND step_number = ?",
                            (contact['id'], campaign_id, orig_msg['step_number']),
                        ).fetchone()

                        if existing:
                            continue

                        msg_id = new_id()
                        conn.execute(
                            """INSERT INTO personalized_messages (id, contact_id, campaign_id, step_number, subject, body)
                            VALUES (?, ?, ?, ?, ?, ?)""",
                            (msg_id, contact['id'], campaign_id, orig_msg['step_number'], new_subject, new_body),
                        )

                        # Queue send record for step 1 only
                        if orig_msg['step_number'] == 1:
                            conn.execute(
                                """INSERT INTO send_records (id, campaign_id, contact_id, message_id, step_number, status)
                                VALUES (?, ?, ?, ?, ?, 'queued')""",
                                (new_id(), campaign_id, contact['id'], msg_id, orig_msg['step_number']),
                            )

                    total_contacts += 1

                conn.commit()

            total_contacts += 1  # Include first contact
            print(f"  Total for company: {len(contacts)} contacts personalized")

        print(f"\nTotal: {total_contacts} contacts queued for sending")



if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python personalize_once.py <campaign_id> [max_companies]")
        sys.exit(1)

    campaign_id = sys.argv[1]
    max_companies = int(sys.argv[2]) if len(sys.argv) > 2 else None

    sender_value_prop = """We're a consulting club at UC Berkeley that partners with companies on semester-long projects.
Our past teams have delivered market research, product roadmaps, and strategic analyses that clients find genuinely useful."""

    personalize_once_per_company(campaign_id, sender_value_prop, num_steps=3, max_companies=max_companies)
