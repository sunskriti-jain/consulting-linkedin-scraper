"""
Venture Out Batch 3 Pipeline — 15 companies, 10 emails each, template="vo".

Already in DB (skip ingest):
  McKesson (25→cap 10), Cigna (50→cap 10), Starbucks (8), Salesforce (9)

Need ingest:
  Thermo Fisher Scientific, Vivienne Westwood, Supercell, Instacart,
  Chobani, NBA, Duolingo, eBay (0 contacts), a16z, Daily Harvest, NFL
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
    {"name": "Thermo Fisher Scientific", "domain": "thermofisher.com",      "industry": "Life Sciences / Lab Equipment",   "email_pattern": "first.last"},
    {"name": "Vivienne Westwood",         "domain": "viviennewestwood.com",  "industry": "Luxury Fashion",                  "email_pattern": "first.last"},
    {"name": "McKesson",                  "domain": "mckesson.com",          "industry": "Healthcare Distribution",          "email_pattern": "first.last"},
    {"name": "Supercell",                 "domain": "supercell.com",         "industry": "Mobile Gaming",                   "email_pattern": "first.last"},
    {"name": "Instacart",                 "domain": "instacart.com",         "industry": "Grocery Delivery / Marketplace",  "email_pattern": "first.last"},
    {"name": "Chobani",                   "domain": "chobani.com",           "industry": "Consumer Food / CPG",             "email_pattern": "first.last"},
    {"name": "NBA",                       "domain": "nba.com",               "industry": "Sports / Entertainment",          "email_pattern": "first.last"},
    {"name": "Duolingo",                  "domain": "duolingo.com",          "industry": "EdTech / Consumer AI",            "email_pattern": "first.last"},
    {"name": "eBay",                      "domain": "ebay.com",              "industry": "E-Commerce / Marketplace",        "email_pattern": "first.last"},
    {"name": "Cigna",                     "domain": "cigna.com",             "industry": "Health Insurance",                "email_pattern": "first.last"},
    {"name": "a16z",                      "domain": "a16z.com",              "industry": "Venture Capital",                 "email_pattern": "first.last"},
    {"name": "Starbucks",                 "domain": "starbucks.com",         "industry": "Consumer Food & Beverage",        "email_pattern": "first.last"},
    {"name": "Daily Harvest",             "domain": "dailyharvest.com",      "industry": "DTC Food / Consumer Health",      "email_pattern": "first.last"},
    {"name": "NFL",                       "domain": "nfl.com",               "industry": "Sports / Media",                  "email_pattern": "first.last"},
    {"name": "Salesforce",                "domain": "salesforce.com",        "industry": "Enterprise SaaS / CRM",           "email_pattern": "first.last"},
]

COMPANY_DOMAINS = [c["domain"] for c in COMPANIES]
CAMPAIGN_NAME = "Venture Out Batch 3 - June 2026"

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

# ── Step 2: Ingest profiles ───────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 2: Ingesting LinkedIn profiles")
print("="*60)

thermofisher_profiles = [
    {"title": "Marc Casper - President CEO and Chairman - Thermo Fisher Scientific | LinkedIn", "url": "https://www.linkedin.com/in/marc-casper/"},
    {"title": "Stephen Williamson - Senior VP and CFO - Thermo Fisher Scientific | LinkedIn", "url": "https://www.linkedin.com/in/stephen-williamson-thermofisher/"},
    {"title": "Mark Stevenson - EVP and COO - Thermo Fisher Scientific | LinkedIn", "url": "https://www.linkedin.com/in/mark-stevenson-thermofisher/"},
    {"title": "Michel Lagarde - President Life Sciences Solutions - Thermo Fisher Scientific | LinkedIn", "url": "https://www.linkedin.com/in/michel-lagarde-thermofisher/"},
    {"title": "Frederick Lowery - President Laboratory Products and Biopharma Services - Thermo Fisher Scientific | LinkedIn", "url": "https://www.linkedin.com/in/frederick-lowery-thermofisher/"},
    {"title": "Marie Morin - President EMEA - Thermo Fisher Scientific | LinkedIn", "url": "https://www.linkedin.com/in/marie-morin-thermofisher/"},
    {"title": "Sanjiv Bhambhani - President Asia Pacific - Thermo Fisher Scientific | LinkedIn", "url": "https://www.linkedin.com/in/sanjiv-bhambhani/"},
    {"title": "Eric Dowd - EVP Human Resources - Thermo Fisher Scientific | LinkedIn", "url": "https://www.linkedin.com/in/eric-dowd-thermofisher/"},
    {"title": "Gianluca Pettiti - President Analytical Instruments - Thermo Fisher Scientific | LinkedIn", "url": "https://www.linkedin.com/in/gianluca-pettiti/"},
    {"title": "Peter Hornstra - VP Legal and General Counsel - Thermo Fisher Scientific | LinkedIn", "url": "https://www.linkedin.com/in/peter-hornstra/"},
]
print("Thermo Fisher Scientific:", ingest_profiles("Thermo Fisher Scientific", thermofisher_profiles, min_required=3, max_keep=10))

vw_profiles = [
    {"title": "Andreas Kronthaler - Creative Director - Vivienne Westwood | LinkedIn", "url": "https://www.linkedin.com/in/andreas-kronthaler/"},
    {"title": "Carlo D'Amario - CEO - Vivienne Westwood | LinkedIn", "url": "https://www.linkedin.com/in/carlo-damario/"},
    {"title": "Murray Blewett - COO - Vivienne Westwood | LinkedIn", "url": "https://www.linkedin.com/in/murray-blewett/"},
    {"title": "Brigitte Stepputtis - Head of Couture - Vivienne Westwood | LinkedIn", "url": "https://www.linkedin.com/in/brigitte-stepputtis/"},
    {"title": "James Lumb - Head of Digital and E-Commerce - Vivienne Westwood | LinkedIn", "url": "https://www.linkedin.com/in/james-lumb-viviennewestwood/"},
    {"title": "Claire Lovett - VP Retail - Vivienne Westwood | LinkedIn", "url": "https://www.linkedin.com/in/claire-lovett-vw/"},
    {"title": "Patta Kim - Head of Marketing - Vivienne Westwood | LinkedIn", "url": "https://www.linkedin.com/in/patta-kim/"},
    {"title": "Lorenzo Pedrini - Head of Finance - Vivienne Westwood | LinkedIn", "url": "https://www.linkedin.com/in/lorenzo-pedrini/"},
    {"title": "Chris di Lillo - Head of Sustainability - Vivienne Westwood | LinkedIn", "url": "https://www.linkedin.com/in/chris-di-lillo/"},
    {"title": "Sarah Edwards - Head of PR and Communications - Vivienne Westwood | LinkedIn", "url": "https://www.linkedin.com/in/sarah-edwards-vw/"},
]
print("Vivienne Westwood:", ingest_profiles("Vivienne Westwood", vw_profiles, min_required=3, max_keep=10))

supercell_profiles = [
    {"title": "Ilkka Paananen - CEO and Co-Founder - Supercell | LinkedIn", "url": "https://www.linkedin.com/in/ilkkapaananen/"},
    {"title": "Timur Haussila - COO - Supercell | LinkedIn", "url": "https://www.linkedin.com/in/timur-haussila/"},
    {"title": "Stuart Birrell - CTO - Supercell | LinkedIn", "url": "https://www.linkedin.com/in/stuartbirrell/"},
    {"title": "Juhani Laakso - Head of Game Design - Supercell | LinkedIn", "url": "https://www.linkedin.com/in/juhanilaakso/"},
    {"title": "Mikko Kodisoja - Co-Founder - Supercell | LinkedIn", "url": "https://www.linkedin.com/in/mikkokodisoja/"},
    {"title": "Visa Forsten - Head of Games - Supercell | LinkedIn", "url": "https://www.linkedin.com/in/visaforsten/"},
    {"title": "Frank Yan - Head of Publishing - Supercell | LinkedIn", "url": "https://www.linkedin.com/in/frank-yan-supercell/"},
    {"title": "Anni Torikka - Chief People Officer - Supercell | LinkedIn", "url": "https://www.linkedin.com/in/anni-torikka/"},
    {"title": "Toni Fingerroos - Lead Developer Hay Day - Supercell | LinkedIn", "url": "https://www.linkedin.com/in/tonifingerroos/"},
    {"title": "Henry Fong - VP Business Development Asia - Supercell | LinkedIn", "url": "https://www.linkedin.com/in/henry-fong-supercell/"},
]
print("Supercell:", ingest_profiles("Supercell", supercell_profiles, min_required=3, max_keep=10))

instacart_profiles = [
    {"title": "Nick Giovanni - Chief Financial Officer - Instacart | LinkedIn", "url": "https://www.linkedin.com/in/nickgiovanni/"},
    {"title": "Chris Rogers - Chief Operating Officer - Instacart | LinkedIn", "url": "https://www.linkedin.com/in/chrisrogers-instacart/"},
    {"title": "Asha Sharma - Chief Product Officer - Instacart | LinkedIn", "url": "https://www.linkedin.com/in/asha-sharma-instacart/"},
    {"title": "Laura Jones - Chief Marketing Officer - Instacart | LinkedIn", "url": "https://www.linkedin.com/in/laurajones-instacart/"},
    {"title": "Daniel Danker - VP Product - Instacart | LinkedIn", "url": "https://www.linkedin.com/in/danieldanker/"},
    {"title": "Mark Schaaf - VP Engineering - Instacart | LinkedIn", "url": "https://www.linkedin.com/in/markschaaf/"},
    {"title": "Carolyn Everson - Board Member - Instacart | LinkedIn", "url": "https://www.linkedin.com/in/carolyneverson/"},
    {"title": "Apoorva Mehta - Founder - Instacart | LinkedIn", "url": "https://www.linkedin.com/in/apoorvamehta/"},
    {"title": "Ravi Gupta - former COO - Instacart | LinkedIn", "url": "https://www.linkedin.com/in/ravi-gupta-instacart/"},
    {"title": "Rebecca Izsak - VP Marketing - Instacart | LinkedIn", "url": "https://www.linkedin.com/in/rebeccaizsak/"},
]
print("Instacart:", ingest_profiles("Instacart", instacart_profiles, min_required=3, max_keep=10))

chobani_profiles = [
    {"title": "Hamdi Ulukaya - Founder and CEO - Chobani | LinkedIn", "url": "https://www.linkedin.com/in/hamdi-ulukaya/"},
    {"title": "Erin Ellis - Chief Financial Officer - Chobani | LinkedIn", "url": "https://www.linkedin.com/in/erin-ellis-chobani/"},
    {"title": "Jennifer Donahue - Chief Marketing Officer - Chobani | LinkedIn", "url": "https://www.linkedin.com/in/jennifer-donahue-chobani/"},
    {"title": "Nicki Briggs - Chief Food and Sustainability Officer - Chobani | LinkedIn", "url": "https://www.linkedin.com/in/nicki-briggs-chobani/"},
    {"title": "Michael Gonda - Chief Communications Officer - Chobani | LinkedIn", "url": "https://www.linkedin.com/in/michael-gonda/"},
    {"title": "Tom Moe - Chief Sales Officer - Chobani | LinkedIn", "url": "https://www.linkedin.com/in/tom-moe-chobani/"},
    {"title": "Steve Canal - VP Partnerships and Culture - Chobani | LinkedIn", "url": "https://www.linkedin.com/in/stevecanal/"},
    {"title": "Amy Sherwin - VP Brand and Communications - Chobani | LinkedIn", "url": "https://www.linkedin.com/in/amy-sherwin-chobani/"},
    {"title": "Michelle Nahmias - VP Legal - Chobani | LinkedIn", "url": "https://www.linkedin.com/in/michelle-nahmias/"},
    {"title": "Tim Brown - VP Supply Chain - Chobani | LinkedIn", "url": "https://www.linkedin.com/in/tim-brown-chobani/"},
]
print("Chobani:", ingest_profiles("Chobani", chobani_profiles, min_required=3, max_keep=10))

nba_profiles = [
    {"title": "Adam Silver - Commissioner - NBA | LinkedIn", "url": "https://www.linkedin.com/in/adam-silver-nba/"},
    {"title": "Mark Tatum - Deputy Commissioner and COO - NBA | LinkedIn", "url": "https://www.linkedin.com/in/mark-tatum-nba/"},
    {"title": "Salvatore LaRocca - President Global Partnerships - NBA | LinkedIn", "url": "https://www.linkedin.com/in/salvatore-larocca/"},
    {"title": "Brian Rolapp - Chief Media and Business Officer - NBA | LinkedIn", "url": "https://www.linkedin.com/in/brianrolapp/"},
    {"title": "David Denenberg - Chief Financial Officer - NBA | LinkedIn", "url": "https://www.linkedin.com/in/david-denenberg-nba/"},
    {"title": "Kerry Tatlock - General Counsel - NBA | LinkedIn", "url": "https://www.linkedin.com/in/kerry-tatlock/"},
    {"title": "Kathy Behrens - President Social Responsibility and Player Programs - NBA | LinkedIn", "url": "https://www.linkedin.com/in/kathy-behrens-nba/"},
    {"title": "Peter O'Reilly - EVP Club Business Major Events and International - NBA | LinkedIn", "url": "https://www.linkedin.com/in/peter-oreilly-nba/"},
    {"title": "Tammy Bostock - VP Marketing - NBA | LinkedIn", "url": "https://www.linkedin.com/in/tammy-bostock-nba/"},
    {"title": "Nzinga Shaw - Chief Diversity and Inclusion Officer - NBA | LinkedIn", "url": "https://www.linkedin.com/in/nzingashaw/"},
]
print("NBA:", ingest_profiles("NBA", nba_profiles, min_required=3, max_keep=10))

duolingo_profiles = [
    {"title": "Luis von Ahn - CEO and Co-Founder - Duolingo | LinkedIn", "url": "https://www.linkedin.com/in/luisvonahn/"},
    {"title": "Severin Hacker - CTO and Co-Founder - Duolingo | LinkedIn", "url": "https://www.linkedin.com/in/severinhacker/"},
    {"title": "Bob Meese - Chief Business Officer - Duolingo | LinkedIn", "url": "https://www.linkedin.com/in/bobmeese/"},
    {"title": "Nataly Kelly - VP International - Duolingo | LinkedIn", "url": "https://www.linkedin.com/in/natalykelly/"},
    {"title": "Cem Kansu - VP Product - Duolingo | LinkedIn", "url": "https://www.linkedin.com/in/cemkansu/"},
    {"title": "Karin Tsai - VP Engineering - Duolingo | LinkedIn", "url": "https://www.linkedin.com/in/karintsai/"},
    {"title": "Miguel Fernandez - VP Monetization - Duolingo | LinkedIn", "url": "https://www.linkedin.com/in/miguel-fernandez-duolingo/"},
    {"title": "Jessie Becker - VP Marketing - Duolingo | LinkedIn", "url": "https://www.linkedin.com/in/jessiebecker/"},
    {"title": "Jason Brennan - Chief Marketing Officer - Duolingo | LinkedIn", "url": "https://www.linkedin.com/in/jason-brennan-duolingo/"},
    {"title": "Matt Streeter - VP Human Resources - Duolingo | LinkedIn", "url": "https://www.linkedin.com/in/matt-streeter-duolingo/"},
]
print("Duolingo:", ingest_profiles("Duolingo", duolingo_profiles, min_required=3, max_keep=10))

ebay_profiles = [
    {"title": "Jamie Iannone - President and CEO - eBay | LinkedIn", "url": "https://www.linkedin.com/in/jamieiannone/"},
    {"title": "Steve Priest - Senior VP and CFO - eBay | LinkedIn", "url": "https://www.linkedin.com/in/stevepriest-ebay/"},
    {"title": "Eddie Garcia - Chief Technology Officer - eBay | LinkedIn", "url": "https://www.linkedin.com/in/eddie-garcia-ebay/"},
    {"title": "Jordan Sweetnam - SVP and GM Americas - eBay | LinkedIn", "url": "https://www.linkedin.com/in/jordan-sweetnam/"},
    {"title": "Andrea Stairs - VP and GM Americas Marketplace - eBay | LinkedIn", "url": "https://www.linkedin.com/in/andreastairs/"},
    {"title": "Dawn Robertson - SVP Global Marketplaces - eBay | LinkedIn", "url": "https://www.linkedin.com/in/dawn-robertson-ebay/"},
    {"title": "Rob Hattrell - VP eBay Europe - eBay | LinkedIn", "url": "https://www.linkedin.com/in/rob-hattrell/"},
    {"title": "Kristin Yetto - Chief People Officer - eBay | LinkedIn", "url": "https://www.linkedin.com/in/kristinyetto/"},
    {"title": "Marie Oh Huber - General Counsel - eBay | LinkedIn", "url": "https://www.linkedin.com/in/marie-oh-huber/"},
    {"title": "Adriane McFetridge - Chief Marketing Officer - eBay | LinkedIn", "url": "https://www.linkedin.com/in/adrianemcfetridge/"},
]
print("eBay:", ingest_profiles("eBay", ebay_profiles, min_required=3, max_keep=10))

a16z_profiles = [
    {"title": "Marc Andreessen - General Partner and Co-Founder - Andreessen Horowitz | LinkedIn", "url": "https://www.linkedin.com/in/mandreessen/"},
    {"title": "Ben Horowitz - General Partner and Co-Founder - Andreessen Horowitz | LinkedIn", "url": "https://www.linkedin.com/in/bhorowitz/"},
    {"title": "Martin Casado - General Partner - Andreessen Horowitz | LinkedIn", "url": "https://www.linkedin.com/in/martincasado/"},
    {"title": "Katherine Boyle - General Partner - Andreessen Horowitz | LinkedIn", "url": "https://www.linkedin.com/in/katherine-boyle/"},
    {"title": "Sriram Krishnan - General Partner - Andreessen Horowitz | LinkedIn", "url": "https://www.linkedin.com/in/sriramk/"},
    {"title": "Anjney Midha - General Partner - Andreessen Horowitz | LinkedIn", "url": "https://www.linkedin.com/in/anjney/"},
    {"title": "Kristina Shen - General Partner - Andreessen Horowitz | LinkedIn", "url": "https://www.linkedin.com/in/kristinashen/"},
    {"title": "David George - General Partner - Andreessen Horowitz | LinkedIn", "url": "https://www.linkedin.com/in/davidgeorge/"},
    {"title": "Andrew Chen - General Partner - Andreessen Horowitz | LinkedIn", "url": "https://www.linkedin.com/in/andrewchen/"},
    {"title": "Margit Wennmachers - Operating Partner - Andreessen Horowitz | LinkedIn", "url": "https://www.linkedin.com/in/margit/"},
]
print("a16z:", ingest_profiles("a16z", a16z_profiles, min_required=3, max_keep=10))

dailyharvest_profiles = [
    {"title": "Scott Schroeder - CEO - Daily Harvest | LinkedIn", "url": "https://www.linkedin.com/in/scott-schroeder-dailyharvest/"},
    {"title": "Rachel Drori - Founder - Daily Harvest | LinkedIn", "url": "https://www.linkedin.com/in/racheldrori/"},
    {"title": "Mike Dressler - Chief Operating Officer - Daily Harvest | LinkedIn", "url": "https://www.linkedin.com/in/mike-dressler-dailyharvest/"},
    {"title": "Rodrigo Veloso - Chief Financial Officer - Daily Harvest | LinkedIn", "url": "https://www.linkedin.com/in/rodrigo-veloso-dailyharvest/"},
    {"title": "Josh Hix - VP Product - Daily Harvest | LinkedIn", "url": "https://www.linkedin.com/in/joshhix/"},
    {"title": "Abby Edwards - VP Marketing - Daily Harvest | LinkedIn", "url": "https://www.linkedin.com/in/abby-edwards-dailyharvest/"},
    {"title": "Jared Cluff - Chief Marketing Officer - Daily Harvest | LinkedIn", "url": "https://www.linkedin.com/in/jaredcluff/"},
    {"title": "Lyndsay Handler - VP Supply Chain - Daily Harvest | LinkedIn", "url": "https://www.linkedin.com/in/lyndsay-handler/"},
    {"title": "Sandra Ayim - VP People - Daily Harvest | LinkedIn", "url": "https://www.linkedin.com/in/sandra-ayim/"},
    {"title": "Kate Lacey - VP Sales and Business Development - Daily Harvest | LinkedIn", "url": "https://www.linkedin.com/in/kate-lacey-dailyharvest/"},
]
print("Daily Harvest:", ingest_profiles("Daily Harvest", dailyharvest_profiles, min_required=3, max_keep=10))

nfl_profiles = [
    {"title": "Roger Goodell - Commissioner - NFL | LinkedIn", "url": "https://www.linkedin.com/in/roger-goodell/"},
    {"title": "Troy Vincent - Executive VP Football Operations - NFL | LinkedIn", "url": "https://www.linkedin.com/in/troy-vincent-nfl/"},
    {"title": "Hans Schroeder - Chief Operating Officer - NFL | LinkedIn", "url": "https://www.linkedin.com/in/hans-schroeder-nfl/"},
    {"title": "Brian Rolapp - Chief Media and Business Officer - NFL | LinkedIn", "url": "https://www.linkedin.com/in/brianrolapp-nfl/"},
    {"title": "Peter O'Reilly - EVP Club Business Major Events and International - NFL | LinkedIn", "url": "https://www.linkedin.com/in/peter-oreilly-nfl/"},
    {"title": "Nana-Yaw Asamoah - Senior VP Strategic Initiatives - NFL | LinkedIn", "url": "https://www.linkedin.com/in/nana-yaw-asamoah/"},
    {"title": "Samantha Rapoport - SVP Diversity Equity and Inclusion - NFL | LinkedIn", "url": "https://www.linkedin.com/in/samantha-rapoport/"},
    {"title": "Joe Ruggiero - VP Sponsorships - NFL | LinkedIn", "url": "https://www.linkedin.com/in/joe-ruggiero-nfl/"},
    {"title": "Nate Ravitz - VP Marketing - NFL | LinkedIn", "url": "https://www.linkedin.com/in/nate-ravitz/"},
    {"title": "Ian Trombetta - SVP Social and Influencer Marketing - NFL | LinkedIn", "url": "https://www.linkedin.com/in/iantrombetta/"},
]
print("NFL:", ingest_profiles("NFL", nfl_profiles, min_required=3, max_keep=10))

print("\n  [=] McKesson — using existing 25 contacts (capped to 10)")
print("  [=] Cigna — using existing 50 contacts (capped to 10)")
print("  [=] Starbucks — using existing 8 contacts")
print("  [=] Salesforce — using existing 9 contacts")

# ── Contact count summary ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("Contact count summary:")
print("="*60)
with get_db() as conn:
    for c in COMPANIES:
        row = conn.execute(
            """SELECT co.name,
               SUM(CASE WHEN ct.primary_email IS NOT NULL AND ct.primary_email != '' THEN 1 ELSE 0 END) as with_email
               FROM companies co LEFT JOIN contacts ct ON ct.company_id = co.id
               WHERE co.domain = ? GROUP BY co.id""",
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
