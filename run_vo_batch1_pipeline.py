"""
Venture Out Batch 1 Pipeline — 15 companies, 10 emails each, 1 LLM personalization per company.
Template: "vo" (Venture Out)

Already in DB with contacts (skip ingest):
  Cursor (10), ExxonMobil (50→cap 10), Palantir (10), General Motors (10),
  Costco (49→cap 10), Anthropic (10), Ford Motor (9)

Need ingest (new to DB):
  Mercedes Benz, Waymo, Airbnb, Twitch, Glean, NASA, Logitech, Zoom
"""
import sys, time, random, sqlite3
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from db import get_db, new_id, init_db
from linkedin_ingest import ingest_profiles
from personalize_once import personalize_once_per_company
from gmail_client import GmailClient
from datetime import datetime

init_db()

COMPANIES = [
    {"name": "Mercedes Benz",  "domain": "mercedes-benz.com", "industry": "Automotive",                    "email_pattern": "first.last"},
    {"name": "Cursor",         "domain": "cursor.com",         "industry": "Dev Tooling / AI Editor",       "email_pattern": "first.last"},
    {"name": "Waymo",          "domain": "waymo.com",          "industry": "Autonomous Vehicles / AI",      "email_pattern": "first.last"},
    {"name": "Airbnb",         "domain": "airbnb.com",         "industry": "Travel / Marketplace",          "email_pattern": "first.last"},
    {"name": "ExxonMobil",     "domain": "exxonmobil.com",     "industry": "Energy / Oil & Gas",            "email_pattern": "first.last"},
    {"name": "Palantir",       "domain": "palantir.com",       "industry": "Data Analytics / Defense Tech", "email_pattern": "first.last"},
    {"name": "Twitch",         "domain": "twitch.tv",          "industry": "Live Streaming / Gaming",       "email_pattern": "first.last"},
    {"name": "General Motors", "domain": "gm.com",             "industry": "Automotive / EV",               "email_pattern": "first.last"},
    {"name": "Glean",          "domain": "glean.com",          "industry": "Enterprise AI Search",          "email_pattern": "first.last"},
    {"name": "NASA",           "domain": "nasa.gov",           "industry": "Aerospace / Government",        "email_pattern": "first.last"},
    {"name": "Logitech",       "domain": "logitech.com",       "industry": "Consumer Electronics / B2B",    "email_pattern": "first.last"},
    {"name": "Costco",         "domain": "costco.com",         "industry": "Retail / Wholesale",            "email_pattern": "first.last"},
    {"name": "Anthropic",      "domain": "anthropic.com",      "industry": "AI Safety / Foundation Models", "email_pattern": "first.last"},
    {"name": "Zoom",           "domain": "zoom.us",            "industry": "Enterprise Communications",     "email_pattern": "first.last"},
    {"name": "Ford Motor",     "domain": "ford.com",           "industry": "Automotive / EV",               "email_pattern": "first.last"},
]

COMPANY_DOMAINS = [c["domain"] for c in COMPANIES]
CAMPAIGN_NAME = "Venture Out Batch 1 - June 2026"

SENDER_VALUE_PROP = (
    "Venture Out is a collective of consultants, product managers, software engineers, "
    "and founders from Berkeley Business Society, Free Ventures, Web Development at Berkeley, "
    "Girls Who Venture and 180 Degrees Consulting at Duke, and ProductSC at USC. Together "
    "we've advised and helped scale startups that raised from Y Combinator, Greylock, and "
    "Kleiner Perkins — working directly with founders on strategy, product, software, and growth."
)

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
                print(f"  [=] {c['name']} already exists")
            else:
                print(f"  [!] {c['name']}: {e}")

# ── Step 2: Ingest profiles for new companies ────────────────────────────────
print("\n" + "="*60)
print("STEP 2: Ingesting LinkedIn profiles")
print("="*60)

mercedes_profiles = [
    {"title": "Ola Källenius - Chairman of the Board of Management and CEO - Mercedes-Benz Group | LinkedIn", "url": "https://www.linkedin.com/in/ola-k%C3%A4llenius/"},
    {"title": "Harald Wilhelm - Member of the Board of Management Finance & Controlling and Mercedes-Benz Mobility - Mercedes-Benz Group | LinkedIn", "url": "https://www.linkedin.com/in/haraldwilhelm/"},
    {"title": "Markus Schäfer - Member of the Board of Management Development and Procurement - Mercedes-Benz Group | LinkedIn", "url": "https://www.linkedin.com/in/markus-sch%C3%A4fer-mercedes-benz/"},
    {"title": "Britta Seeger - Member of the Board of Management Sales and Marketing - Mercedes-Benz Group | LinkedIn", "url": "https://www.linkedin.com/in/britta-seeger/"},
    {"title": "Renata Jungo Brüngger - Member of the Board of Management Integrity and Legal Affairs - Mercedes-Benz Group | LinkedIn", "url": "https://www.linkedin.com/in/renata-jungo-br%C3%BCngger/"},
    {"title": "Sabine Kohleisen - Member of the Board of Management Human Resources and Labor Director - Mercedes-Benz Group | LinkedIn", "url": "https://www.linkedin.com/in/sabine-kohleisen/"},
    {"title": "Dimitris Psillakis - President and CEO - Mercedes-Benz USA | LinkedIn", "url": "https://www.linkedin.com/in/dimitris-psillakis/"},
    {"title": "Franz Reiner - Chairman of the Board - Mercedes-Benz Mobility | LinkedIn", "url": "https://www.linkedin.com/in/franz-reiner/"},
    {"title": "Wilko Stark - Senior Vice President Strategy and Partnerships - Mercedes-Benz Group | LinkedIn", "url": "https://www.linkedin.com/in/wilko-stark/"},
    {"title": "Bettina Fetzer - Vice President Communications and Marketing - Mercedes-Benz Group | LinkedIn", "url": "https://www.linkedin.com/in/bettina-fetzer/"},
]
print("Mercedes Benz:", ingest_profiles("Mercedes Benz", mercedes_profiles, min_required=3, max_keep=10))

waymo_profiles = [
    {"title": "Dmitri Dolgov - Co-CEO - Waymo | LinkedIn", "url": "https://www.linkedin.com/in/dmitri-dolgov-waymo/"},
    {"title": "Tekedra Mawakana - Co-CEO - Waymo | LinkedIn", "url": "https://www.linkedin.com/in/tekedramawakana/"},
    {"title": "Cathy Kuo - Chief Financial Officer - Waymo | LinkedIn", "url": "https://www.linkedin.com/in/cathykuo/"},
    {"title": "Drago Anguelov - VP Research and Chief Scientist - Waymo | LinkedIn", "url": "https://www.linkedin.com/in/drago-anguelov/"},
    {"title": "Richard Rabbat - VP Product - Waymo | LinkedIn", "url": "https://www.linkedin.com/in/richardrabbat/"},
    {"title": "Satish Jeyachandran - Head of Waymo Via Trucking - Waymo | LinkedIn", "url": "https://www.linkedin.com/in/satishjeyachandran/"},
    {"title": "Jordan Sherb - Head of Strategy and Corporate Development - Waymo | LinkedIn", "url": "https://www.linkedin.com/in/jordan-sherb/"},
    {"title": "Rooz Ghaffari - VP Operations - Waymo | LinkedIn", "url": "https://www.linkedin.com/in/rooz-ghaffari/"},
    {"title": "Stephanie Ignacio - VP Communications - Waymo | LinkedIn", "url": "https://www.linkedin.com/in/stephanie-ignacio/"},
    {"title": "Clay Mowry - VP Government Affairs and Partnerships - Waymo | LinkedIn", "url": "https://www.linkedin.com/in/clay-mowry/"},
]
print("Waymo:", ingest_profiles("Waymo", waymo_profiles, min_required=3, max_keep=10))

airbnb_profiles = [
    {"title": "Brian Chesky - Co-Founder and CEO - Airbnb | LinkedIn", "url": "https://www.linkedin.com/in/brianchesky/"},
    {"title": "Dave Stephenson - Chief Financial Officer - Airbnb | LinkedIn", "url": "https://www.linkedin.com/in/davestephenson/"},
    {"title": "Nathan Blecharczyk - Co-Founder and Chief Strategy Officer - Airbnb | LinkedIn", "url": "https://www.linkedin.com/in/nathanblecharczyk/"},
    {"title": "Hiroki Asai - Global Head of Marketing - Airbnb | LinkedIn", "url": "https://www.linkedin.com/in/hiroki-asai/"},
    {"title": "Tara Bunch - VP Global Operations - Airbnb | LinkedIn", "url": "https://www.linkedin.com/in/tarabunch/"},
    {"title": "Shannon Stuckey - VP Human Resources - Airbnb | LinkedIn", "url": "https://www.linkedin.com/in/shannon-stuckey/"},
    {"title": "Joeban Phea - VP Strategy and Finance - Airbnb | LinkedIn", "url": "https://www.linkedin.com/in/joeban-phea/"},
    {"title": "Aisling Hassell - VP Global Community - Airbnb | LinkedIn", "url": "https://www.linkedin.com/in/aislinghassell/"},
    {"title": "Chris Lehane - VP Global Policy and Communications - Airbnb | LinkedIn", "url": "https://www.linkedin.com/in/chrislehane/"},
    {"title": "Mike Curtis - VP Engineering - Airbnb | LinkedIn", "url": "https://www.linkedin.com/in/curtismike/"},
]
print("Airbnb:", ingest_profiles("Airbnb", airbnb_profiles, min_required=3, max_keep=10))

twitch_profiles = [
    {"title": "Dan Clancy - President - Twitch | LinkedIn", "url": "https://www.linkedin.com/in/danclancy/"},
    {"title": "Sara Clemens - Chief Operating Officer - Twitch | LinkedIn", "url": "https://www.linkedin.com/in/sara-clemens/"},
    {"title": "Alison Gianotto - Chief Technology Officer - Twitch | LinkedIn", "url": "https://www.linkedin.com/in/snipe/"},
    {"title": "Mike Minton - VP Revenue - Twitch | LinkedIn", "url": "https://www.linkedin.com/in/mikeminton/"},
    {"title": "Robbie Hobbes - VP Product - Twitch | LinkedIn", "url": "https://www.linkedin.com/in/robbyhobbes/"},
    {"title": "Janet Xu - Head of Creator Growth - Twitch | LinkedIn", "url": "https://www.linkedin.com/in/janet-xu/"},
    {"title": "Manon Regnier - VP EMEA - Twitch | LinkedIn", "url": "https://www.linkedin.com/in/manon-regnier/"},
    {"title": "Kathy Watson - VP People - Twitch | LinkedIn", "url": "https://www.linkedin.com/in/kathy-watson-twitch/"},
    {"title": "Marcus Graham - VP Content - Twitch | LinkedIn", "url": "https://www.linkedin.com/in/marcus-graham-twitch/"},
    {"title": "Pat Dunne - VP Partnerships - Twitch | LinkedIn", "url": "https://www.linkedin.com/in/patdunne/"},
]
print("Twitch:", ingest_profiles("Twitch", twitch_profiles, min_required=3, max_keep=10))

glean_profiles = [
    {"title": "Arvind Jain - Co-Founder and CEO - Glean | LinkedIn", "url": "https://www.linkedin.com/in/arvind-jain-glean/"},
    {"title": "T.R. Vishwanath - Co-Founder and COO - Glean | LinkedIn", "url": "https://www.linkedin.com/in/trvishwanath/"},
    {"title": "Piyush Prahladka - Co-Founder and CTO - Glean | LinkedIn", "url": "https://www.linkedin.com/in/piyush-prahladka/"},
    {"title": "Bret Hann - Chief Financial Officer - Glean | LinkedIn", "url": "https://www.linkedin.com/in/brethann/"},
    {"title": "Tony Gentilcore - VP Sales - Glean | LinkedIn", "url": "https://www.linkedin.com/in/tony-gentilcore/"},
    {"title": "Monika Fahlbusch - Chief People Officer - Glean | LinkedIn", "url": "https://www.linkedin.com/in/monikafafahlbusch/"},
    {"title": "Kevin Ding - VP Product - Glean | LinkedIn", "url": "https://www.linkedin.com/in/kevin-ding-glean/"},
    {"title": "Sarah Dayan - VP Marketing - Glean | LinkedIn", "url": "https://www.linkedin.com/in/sarah-dayan-glean/"},
    {"title": "Sriram Rajagopalan - VP Engineering - Glean | LinkedIn", "url": "https://www.linkedin.com/in/sriramr/"},
    {"title": "Anu Bharadwaj - Chief Customer Officer - Glean | LinkedIn", "url": "https://www.linkedin.com/in/anu-bharadwaj/"},
]
print("Glean:", ingest_profiles("Glean", glean_profiles, min_required=3, max_keep=10))

nasa_profiles = [
    {"title": "Bill Nelson - Administrator - NASA | LinkedIn", "url": "https://www.linkedin.com/in/bill-nelson-nasa/"},
    {"title": "Pam Melroy - Deputy Administrator - NASA | LinkedIn", "url": "https://www.linkedin.com/in/pam-melroy/"},
    {"title": "Jim Free - Associate Administrator - NASA | LinkedIn", "url": "https://www.linkedin.com/in/jim-free-nasa/"},
    {"title": "Janet Petro - Director Kennedy Space Center - NASA | LinkedIn", "url": "https://www.linkedin.com/in/janet-petro/"},
    {"title": "Vanessa Wyche - Director Johnson Space Center - NASA | LinkedIn", "url": "https://www.linkedin.com/in/vanessa-wyche/"},
    {"title": "Bhavya Lal - Chief of Staff - NASA | LinkedIn", "url": "https://www.linkedin.com/in/bhavya-lal/"},
    {"title": "Kathy Lueders - Associate Administrator Space Operations - NASA | LinkedIn", "url": "https://www.linkedin.com/in/kathy-lueders/"},
    {"title": "Bob Cabana - Associate Administrator - NASA | LinkedIn", "url": "https://www.linkedin.com/in/bob-cabana/"},
    {"title": "Jim Bridenstine - Former Administrator - NASA | LinkedIn", "url": "https://www.linkedin.com/in/jimbridenstine/"},
    {"title": "Thomas Zurbuchen - Former Associate Administrator Science - NASA | LinkedIn", "url": "https://www.linkedin.com/in/thomas-zurbuchen/"},
]
print("NASA:", ingest_profiles("NASA", nasa_profiles, min_required=3, max_keep=10))

logitech_profiles = [
    {"title": "Hanneke Faber - President and CEO - Logitech | LinkedIn", "url": "https://www.linkedin.com/in/hannekefaber/"},
    {"title": "Chuck Boynton - Chief Financial Officer - Logitech | LinkedIn", "url": "https://www.linkedin.com/in/chuck-boynton/"},
    {"title": "Prakash Arunkundrum - COO and Head of Global Operations - Logitech | LinkedIn", "url": "https://www.linkedin.com/in/prakash-arunkundrum/"},
    {"title": "Art O'Gnimh - President Logitech for Business - Logitech | LinkedIn", "url": "https://www.linkedin.com/in/artognimh/"},
    {"title": "Delphine Donne - Chief People Officer - Logitech | LinkedIn", "url": "https://www.linkedin.com/in/delphine-donne/"},
    {"title": "Michele Hermann - Chief Marketing Officer - Logitech | LinkedIn", "url": "https://www.linkedin.com/in/michelehermann/"},
    {"title": "Marcel Stolk - President Gaming - Logitech | LinkedIn", "url": "https://www.linkedin.com/in/marcelstolk/"},
    {"title": "Ashish Arora - VP Enterprise - Logitech | LinkedIn", "url": "https://www.linkedin.com/in/ashish-arora-logitech/"},
    {"title": "Sanjay Mehta - VP Sales - Logitech | LinkedIn", "url": "https://www.linkedin.com/in/sanjay-mehta-logitech/"},
    {"title": "Nate Olmstead - VP Finance - Logitech | LinkedIn", "url": "https://www.linkedin.com/in/nate-olmstead/"},
]
print("Logitech:", ingest_profiles("Logitech", logitech_profiles, min_required=3, max_keep=10))

zoom_profiles = [
    {"title": "Eric Yuan - Founder and CEO - Zoom | LinkedIn", "url": "https://www.linkedin.com/in/ericyuan/"},
    {"title": "Kelly Steckelberg - Chief Financial Officer - Zoom | LinkedIn", "url": "https://www.linkedin.com/in/kellysteckelberg/"},
    {"title": "Aparna Bawa - Chief Operating Officer - Zoom | LinkedIn", "url": "https://www.linkedin.com/in/aparnabawa/"},
    {"title": "Velchamy Sankarlingam - President Product and Engineering - Zoom | LinkedIn", "url": "https://www.linkedin.com/in/velchamy/"},
    {"title": "Ryan Azus - Chief Revenue Officer - Zoom | LinkedIn", "url": "https://www.linkedin.com/in/ryanazus/"},
    {"title": "Janine Pelosi - Chief Marketing Officer - Zoom | LinkedIn", "url": "https://www.linkedin.com/in/janinepelosi/"},
    {"title": "Zeta Rodriguez - Chief People Officer - Zoom | LinkedIn", "url": "https://www.linkedin.com/in/zeta-rodriguez/"},
    {"title": "Graeme Geddes - Chief Customer Officer - Zoom | LinkedIn", "url": "https://www.linkedin.com/in/graemegeddes/"},
    {"title": "Ross Mayfield - VP Product - Zoom | LinkedIn", "url": "https://www.linkedin.com/in/rossmayfield/"},
    {"title": "Matt Cain - CTO - Zoom | LinkedIn", "url": "https://www.linkedin.com/in/mattcain/"},
]
print("Zoom:", ingest_profiles("Zoom", zoom_profiles, min_required=3, max_keep=10))

# Skip ingest for companies already in DB with contacts:
# Cursor (10), ExxonMobil (50), Palantir (10), General Motors (10),
# Costco (49), Anthropic (10), Ford Motor (9)
print("\n  [=] Cursor — using existing 10 contacts")
print("  [=] ExxonMobil — using existing contacts (capped to 10)")
print("  [=] Palantir — using existing 10 contacts")
print("  [=] General Motors — using existing 10 contacts")
print("  [=] Costco — using existing contacts (capped to 10)")
print("  [=] Anthropic — using existing 10 contacts")
print("  [=] Ford Motor — using existing 9 contacts")

# ── Contact count summary ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("Contact count summary:")
print("="*60)
with get_db() as conn:
    for c in COMPANIES:
        row = conn.execute(
            """SELECT co.name,
               SUM(CASE WHEN ct.primary_email IS NOT NULL AND ct.primary_email != '' THEN 1 ELSE 0 END) as with_email
               FROM companies co
               LEFT JOIN contacts ct ON ct.company_id = co.id
               WHERE co.domain = ?
               GROUP BY co.id""",
            (c["domain"],)
        ).fetchone()
        if row:
            cnt = row["with_email"] or 0
            status = "OK" if cnt >= 5 else "LOW"
            print(f"  [{status}] {row['name']}: {cnt} with email")
        else:
            print(f"  [MISSING] {c['name']}")

# ── Create campaign ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 3: Creating campaign")
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
print("STEP 4: Personalizing with Venture Out template")
print("="*60)
personalize_once_per_company(
    campaign_id,
    SENDER_VALUE_PROP,
    num_steps=3,
    company_domains=COMPANY_DOMAINS,
    template="vo",
    max_contacts_per_company=10,
)

# ── Send ──────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 5: Sending queued emails")
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
