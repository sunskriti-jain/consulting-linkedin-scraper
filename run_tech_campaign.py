"""
Full pipeline for Tech Startup campaign:
  1. Insert 16 companies
  2. Discover email patterns
  3. Harvest 20 LinkedIn profiles per company
  4. personalize_once_per_company
  5. fast_send
"""
import sys, time, random
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from db import get_db, new_id, init_db
import email_fallback
from linkedin_scraper import harvest_profiles
from linkedin_ingest import ingest_profiles
from personalize_once import personalize_once_per_company
from gmail_client import GmailClient
from datetime import datetime
import sqlite3

init_db()

# ── Company manifest ──────────────────────────────────────────────────────────
COMPANIES = [
    {"name": "Cursor",             "domain": "cursor.com",              "industry": "AI Code Editor",           "email_pattern": "first.last"},
    {"name": "Clay",               "domain": "clay.com",                "industry": "Sales Intelligence SaaS",  "email_pattern": "first.last"},
    {"name": "Supabase",           "domain": "supabase.com",            "industry": "Developer Tools",          "email_pattern": "first.last"},
    {"name": "Zip",                "domain": "ziphq.com",               "industry": "Procurement SaaS",         "email_pattern": "first.last"},
    {"name": "Applied Intuition",  "domain": "appliedintuition.com",    "industry": "Autonomous Vehicles",      "email_pattern": "first.last"},
    {"name": "DoorDash",           "domain": "doordash.com",            "industry": "Food Delivery",            "email_pattern": "first.last"},
    {"name": "Sony",               "domain": "sony.com",                "industry": "Technology/Entertainment", "email_pattern": "first.last"},
    {"name": "Headway",            "domain": "headway.app",             "industry": "Mental Health Tech",       "email_pattern": "first.last"},
    {"name": "MongoDB",            "domain": "mongodb.com",             "industry": "Database / Dev Tools",     "email_pattern": "first.last"},
    {"name": "Amazon",             "domain": "amazon.com",              "industry": "E-commerce / Cloud",       "email_pattern": "first.last"},
    {"name": "Vercel",             "domain": "vercel.com",              "industry": "Developer Tools",          "email_pattern": "first.last"},
    {"name": "Scale AI",           "domain": "scale.com",               "industry": "AI Data Platform",         "email_pattern": "first.last"},
    {"name": "Kalshi",             "domain": "kalshi.com",              "industry": "Prediction Markets",       "email_pattern": "first.last"},
    {"name": "Discord",            "domain": "discord.com",             "industry": "Communications",           "email_pattern": "first.last"},
    {"name": "GitHub",             "domain": "github.com",              "industry": "Developer Tools",          "email_pattern": "first.last"},
    {"name": "Mercor",             "domain": "mercor.com",              "industry": "AI Hiring",                "email_pattern": "first.last"},
]

TARGET_CONTACTS = 20
CAMPAIGN_NAME   = "Tech Startup Outreach - May 2026"

SENDER_VALUE_PROP = """We're a consulting club at UC Berkeley that partners with companies on semester-long projects. \
Our past teams have delivered market research, product roadmaps, and strategic analyses that companies find genuinely useful. \
We work with a handful of partners each semester and customize every engagement."""

# ── Step 1: Insert companies ──────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 1: Inserting companies")
print("="*60)
with get_db() as conn:
    for c in COMPANIES:
        try:
            conn.execute(
                "INSERT INTO companies (id, name, domain, industry, email_pattern, email_pattern_confidence) VALUES (?,?,?,?,?,?)",
                (new_id(), c["name"], c["domain"], c["industry"], c["email_pattern"], 70.0),
            )
            print(f"  [+] {c['name']} ({c['domain']})")
        except Exception as e:
            if "UNIQUE" in str(e).upper():
                # Update pattern if blank
                conn.execute(
                    "UPDATE companies SET email_pattern=?, email_pattern_confidence=? WHERE domain=? AND (email_pattern IS NULL OR email_pattern='')",
                    (c["email_pattern"], 70.0, c["domain"]),
                )
                print(f"  [=] {c['name']} already exists")
            else:
                print(f"  [!] {c['name']}: {e}")

# ── Step 2: Harvest LinkedIn profiles ────────────────────────────────────────
print("\n" + "="*60)
print("STEP 2: Harvesting LinkedIn profiles (20 per company)")
print("="*60)

for c in COMPANIES:
    with get_db() as conn:
        company_row = conn.execute("SELECT id FROM companies WHERE domain=?", (c["domain"],)).fetchone()
        if not company_row:
            print(f"  [!] {c['name']}: company not found in DB, skipping")
            continue
        existing_count = conn.execute(
            "SELECT COUNT(*) as n FROM contacts WHERE company_id=?", (company_row["id"],)
        ).fetchone()["n"]

    if existing_count >= TARGET_CONTACTS:
        print(f"\n  [{c['name']}] already has {existing_count} contacts — skipping harvest")
        continue

    print(f"\n  [{c['name']}] (have {existing_count}, need {TARGET_CONTACTS})")
    try:
        profiles = harvest_profiles(c["name"], num_searches=7)
        print(f"    scraped {len(profiles)} raw profiles")

        # Convert harvest_profiles output → ingest_profiles input format
        profile_list = []
        for p in profiles:
            slug = p.get("linkedin_slug", "")
            url  = f"https://www.linkedin.com/in/{slug}" if slug else ""
            title_str = f"{p['first_name']} {p['last_name']} - {p['title'] or 'Professional'} - {c['name']} | LinkedIn"
            profile_list.append({"title": title_str, "url": url})

        inserted = ingest_profiles(c["name"], profile_list, min_required=3, max_keep=TARGET_CONTACTS)
        print(f"    inserted {inserted} contacts")
    except Exception as e:
        print(f"    [ERROR] {e}")

    time.sleep(random.uniform(3, 5))   # gentle on search engines

# ── Contact count summary ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("Contact counts after harvest:")
print("="*60)
with get_db() as conn:
    for c in COMPANIES:
        row = conn.execute(
            """SELECT COUNT(*) as n FROM contacts ct
               JOIN companies co ON ct.company_id=co.id
               WHERE co.domain=? AND ct.primary_email IS NOT NULL""",
            (c["domain"],),
        ).fetchone()
        status = "OK" if row["n"] >= 10 else "LOW"
        print(f"  [{status}] {c['name']}: {row['n']} contacts with email")

# ── Step 3: Create campaign ───────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 3: Creating campaign")
print("="*60)
with get_db() as conn:
    existing = conn.execute("SELECT id FROM campaigns WHERE name=?", (CAMPAIGN_NAME,)).fetchone()
    if existing:
        campaign_id = existing["id"]
        print(f"  Campaign already exists: {campaign_id}")
    else:
        campaign_id = new_id()
        conn.execute(
            "INSERT INTO campaigns (id, name, daily_cap) VALUES (?,?,?)",
            (campaign_id, CAMPAIGN_NAME, 100),
        )
        print(f"  Created: {CAMPAIGN_NAME} (id: {campaign_id})")

print(f"  Campaign ID: {campaign_id}")

# ── Step 4: Personalize (once-per-company) ───────────────────────────────────
print("\n" + "="*60)
print("STEP 4: Personalizing (once per company, clone for rest)")
print("="*60)
personalize_once_per_company(campaign_id, SENDER_VALUE_PROP, num_steps=3)

# ── Step 5: Send ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 5: Sending queued emails")
print("="*60)

with get_db() as conn:
    queued = conn.execute(
        "SELECT COUNT(*) as n FROM send_records WHERE campaign_id=? AND status='queued'",
        (campaign_id,),
    ).fetchone()["n"]
print(f"  {queued} emails queued — starting fast send...")

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
        print(f"[*] No queued emails yet — waiting 30s for personalization...")
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
            if total_sent % 10 == 0:
                print(f"[{total_sent} sent] {row['company_name']} - {row['first_name']} {row['last_name']}")
        except Exception as e:
            safe_exec(
                "UPDATE send_records SET status='failed', error=? WHERE id=?",
                (str(e)[:500], row["sr_id"]),
            )
            total_failed += 1
            print(f"[FAIL] {row['primary_email']}: {str(e)[:100]}")

        time.sleep(random.uniform(2.0, 4.0))

conn_s.close()
print(f"\n[ALL DONE] Campaign '{CAMPAIGN_NAME}'")
print(f"  Sent: {total_sent} | Failed: {total_failed}")
print(f"  Campaign ID: {campaign_id}")
