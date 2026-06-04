"""
Fortune 500 + High Growth Campaign Pipeline:
  1. Insert 20 companies
  2. Ingest real LinkedIn profiles (10 per company)
  3. Create campaign
  4. Personalize (once per company, clone for rest) — scoped to these 20 domains
  5. Send
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
    {"name": "Microsoft",              "domain": "microsoft.com",       "industry": "Technology / Cloud",          "email_pattern": "first.last"},
    {"name": "Apple",                  "domain": "apple.com",           "industry": "Consumer Technology",         "email_pattern": "first.last"},
    {"name": "Google",                 "domain": "google.com",          "industry": "Technology / Advertising",    "email_pattern": "first.last"},
    {"name": "Johnson & Johnson",      "domain": "jnj.com",             "industry": "Healthcare / Pharma",         "email_pattern": "first.last"},
    {"name": "Procter & Gamble",       "domain": "pg.com",              "industry": "Consumer Goods",              "email_pattern": "first.last"},
    {"name": "Walmart",                "domain": "walmart.com",         "industry": "Retail",                      "email_pattern": "first.last"},
    {"name": "Boeing",                 "domain": "boeing.com",          "industry": "Aerospace / Defense",         "email_pattern": "first.last"},
    {"name": "Lockheed Martin",        "domain": "lmco.com",            "industry": "Defense / Aerospace",         "email_pattern": "first.last"},
    {"name": "RTX",                    "domain": "rtx.com",             "industry": "Defense / Aerospace",         "email_pattern": "first.last"},
    {"name": "Abbott Laboratories",    "domain": "abbott.com",          "industry": "Healthcare / MedTech",        "email_pattern": "first.last"},
    {"name": "Deere & Company",        "domain": "johndeere.com",       "industry": "Industrial / AgriTech",       "email_pattern": "first.last"},
    {"name": "Caterpillar",            "domain": "cat.com",             "industry": "Industrial / Construction",   "email_pattern": "first.last"},
    {"name": "General Motors",         "domain": "gm.com",              "industry": "Automotive",                  "email_pattern": "first.last"},
    {"name": "Ford Motor",             "domain": "ford.com",            "industry": "Automotive",                  "email_pattern": "first.last"},
    {"name": "Salesforce",             "domain": "salesforce.com",      "industry": "Enterprise SaaS / CRM",       "email_pattern": "first.last"},
    {"name": "Netflix",                "domain": "netflix.com",         "industry": "Streaming / Entertainment",   "email_pattern": "first.last"},
    {"name": "Stripe",                 "domain": "stripe.com",          "industry": "Fintech / Payments",          "email_pattern": "first.last"},
    {"name": "Palantir",               "domain": "palantir.com",        "industry": "Data Analytics / Defense",    "email_pattern": "first.last"},
    {"name": "OpenAI",                 "domain": "openai.com",          "industry": "AI Research / Products",      "email_pattern": "first.last"},
    {"name": "Anduril Industries",     "domain": "anduril.com",         "industry": "Defense Technology",          "email_pattern": "first.last"},
]

COMPANY_DOMAINS = [c["domain"] for c in COMPANIES]
CAMPAIGN_NAME = "Fortune 500 & High Growth Outreach - May 2026"

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
                conn.execute(
                    "UPDATE companies SET email_pattern=?, email_pattern_confidence=? WHERE domain=? AND (email_pattern IS NULL OR email_pattern='')",
                    (c["email_pattern"], 70.0, c["domain"]),
                )
                print(f"  [=] {c['name']} already exists")
            else:
                print(f"  [!] {c['name']}: {e}")

# ── Step 2: Ingest profiles ───────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 2: Ingesting LinkedIn profiles (10 per company)")
print("="*60)

microsoft_profiles = [
    {"title": "Satya Nadella - Chairman and Chief Executive Officer - Microsoft | LinkedIn", "url": "https://www.linkedin.com/in/satyanadella/"},
    {"title": "Brad Smith - Vice Chair and President - Microsoft | LinkedIn", "url": "https://www.linkedin.com/in/bradsmi/"},
    {"title": "Scott Guthrie - Executive Vice President Cloud and AI - Microsoft | LinkedIn", "url": "https://www.linkedin.com/in/guthriescott/"},
    {"title": "Kevin Scott - Executive Vice President and Chief Technology Officer - Microsoft | LinkedIn", "url": "https://www.linkedin.com/in/jkevinscott/"},
    {"title": "Kathleen Hogan - Executive Vice President Chief Strategy Officer - Microsoft | LinkedIn", "url": "https://www.linkedin.com/in/kathleenthogan/"},
    {"title": "Judson Althoff - Executive Vice President Chief Commercial Officer - Microsoft | LinkedIn", "url": "https://www.linkedin.com/in/judsonalthoff/"},
    {"title": "Amy Hood - Executive Vice President and Chief Financial Officer - Microsoft | LinkedIn", "url": "https://www.linkedin.com/in/amyhood1/"},
    {"title": "Rajesh Jha - Executive Vice President Experiences and Devices - Microsoft | LinkedIn", "url": "https://www.linkedin.com/in/rajesh-jha-90010b4/"},
    {"title": "Chris Capossela - Executive Vice President Chief Marketing Officer - Microsoft | LinkedIn", "url": "https://www.linkedin.com/in/chriscapossela/"},
    {"title": "Frank Shaw - Corporate Vice President Communications - Microsoft | LinkedIn", "url": "https://www.linkedin.com/in/frankshaw/"},
]
print("Microsoft:", ingest_profiles("Microsoft", microsoft_profiles, min_required=3, max_keep=10))

apple_profiles = [
    {"title": "Tim Cook - Chief Executive Officer - Apple | LinkedIn", "url": "https://www.linkedin.com/in/timcookapple/"},
    {"title": "Jeff Williams - Chief Operating Officer - Apple | LinkedIn", "url": "https://www.linkedin.com/in/jeff-williams-apple/"},
    {"title": "Craig Federighi - Senior Vice President Software Engineering - Apple | LinkedIn", "url": "https://www.linkedin.com/in/craig-federighi/"},
    {"title": "Johny Srouji - Senior Vice President Hardware Technologies - Apple | LinkedIn", "url": "https://www.linkedin.com/in/johny-srouji/"},
    {"title": "Greg Joswiak - Senior Vice President Worldwide Marketing - Apple | LinkedIn", "url": "https://www.linkedin.com/in/greg-joswiak/"},
    {"title": "Eddy Cue - Senior Vice President Services - Apple | LinkedIn", "url": "https://www.linkedin.com/in/eddy-cue/"},
    {"title": "Deirdre O'Brien - Senior Vice President Retail and People - Apple | LinkedIn", "url": "https://www.linkedin.com/in/deirdre-obrien-apple/"},
    {"title": "John Giannandrea - Senior Vice President Machine Learning and AI Strategy - Apple | LinkedIn", "url": "https://www.linkedin.com/in/john-giannandrea/"},
    {"title": "Kevan Parekh - Senior Vice President and Chief Financial Officer - Apple | LinkedIn", "url": "https://www.linkedin.com/in/kevan-parekh/"},
    {"title": "Phil Schiller - Apple Fellow - Apple | LinkedIn", "url": "https://www.linkedin.com/in/phil-schiller/"},
]
print("Apple:", ingest_profiles("Apple", apple_profiles, min_required=3, max_keep=10))

google_profiles = [
    {"title": "Sundar Pichai - Chief Executive Officer Alphabet and Google - Google | LinkedIn", "url": "https://www.linkedin.com/in/sundarpichai/"},
    {"title": "Ruth Porat - President and Chief Investment Officer Alphabet - Google | LinkedIn", "url": "https://www.linkedin.com/in/ruth-porat/"},
    {"title": "Thomas Kurian - Chief Executive Officer Google Cloud - Google | LinkedIn", "url": "https://www.linkedin.com/in/thomas-kurian-469b6219/"},
    {"title": "Lorraine Twohill - Senior Vice President Chief Marketing Officer - Google | LinkedIn", "url": "https://www.linkedin.com/in/lorraine-twohill-ba3a56185/"},
    {"title": "Neal Mohan - Chief Executive Officer YouTube - Google | LinkedIn", "url": "https://www.linkedin.com/in/nealmohan/"},
    {"title": "Prabhakar Raghavan - Senior Vice President Google Search - Google | LinkedIn", "url": "https://www.linkedin.com/in/prabhakar-raghavan/"},
    {"title": "Jeff Dean - Chief Scientist Google DeepMind and Google Research - Google | LinkedIn", "url": "https://www.linkedin.com/in/jeff-dean-8b12a/"},
    {"title": "Demis Hassabis - Chief Executive Officer Google DeepMind - Google | LinkedIn", "url": "https://www.linkedin.com/in/demishassabis/"},
    {"title": "Nick Fox - Vice President Consumer Products - Google | LinkedIn", "url": "https://www.linkedin.com/in/nick-fox-google/"},
    {"title": "Philipp Schindler - Senior Vice President Chief Business Officer - Google | LinkedIn", "url": "https://www.linkedin.com/in/philippschindler/"},
]
print("Google:", ingest_profiles("Google", google_profiles, min_required=3, max_keep=10))

jnj_profiles = [
    {"title": "Joaquin Duato - Chairman and Chief Executive Officer - Johnson & Johnson | LinkedIn", "url": "https://www.linkedin.com/in/joaquinduato/"},
    {"title": "Joseph Wolk - Executive Vice President Chief Financial Officer - Johnson & Johnson | LinkedIn", "url": "https://www.linkedin.com/in/josephwolk/"},
    {"title": "Jennifer Taubert - Executive Vice President Worldwide Chairman Innovative Medicine - Johnson & Johnson | LinkedIn", "url": "https://www.linkedin.com/in/jennifer-taubert/"},
    {"title": "Tim Schmid - Executive Vice President MedTech - Johnson & Johnson | LinkedIn", "url": "https://www.linkedin.com/in/tim-schmid-jnj/"},
    {"title": "Peter Fasolo - Executive Vice President Chief Human Resources Officer - Johnson & Johnson | LinkedIn", "url": "https://www.linkedin.com/in/peter-fasolo/"},
    {"title": "Michael Sneed - Executive Vice President Global Corporate Affairs - Johnson & Johnson | LinkedIn", "url": "https://www.linkedin.com/in/michael-sneed-jnj/"},
    {"title": "Kathryn Wengel - Executive Vice President Chief Technical Officer - Johnson & Johnson | LinkedIn", "url": "https://www.linkedin.com/in/kathryn-wengel/"},
    {"title": "Vanessa Broadhurst - Executive Vice President Global Corporate Affairs - Johnson & Johnson | LinkedIn", "url": "https://www.linkedin.com/in/vanessa-broadhurst/"},
    {"title": "John Reed - Chief Scientific Officer Innovative Medicine - Johnson & Johnson | LinkedIn", "url": "https://www.linkedin.com/in/john-reed-jnj/"},
    {"title": "Erik Haas - Vice President Litigation - Johnson & Johnson | LinkedIn", "url": "https://www.linkedin.com/in/erik-haas-jnj/"},
]
print("Johnson & Johnson:", ingest_profiles("Johnson & Johnson", jnj_profiles, min_required=3, max_keep=10))

pg_profiles = [
    {"title": "Jon Moeller - Executive Chairman - Procter & Gamble | LinkedIn", "url": "https://www.linkedin.com/in/jon-moeller-pg/"},
    {"title": "Shailesh Jejurikar - President and Chief Executive Officer - Procter & Gamble | LinkedIn", "url": "https://www.linkedin.com/in/shailesh-jejurikar-0b961018/"},
    {"title": "Andre Schulten - Executive Vice President Chief Financial Officer - Procter & Gamble | LinkedIn", "url": "https://www.linkedin.com/in/andre-schulten-57b38614/"},
    {"title": "Marc Pritchard - Chief Brand Officer - Procter & Gamble | LinkedIn", "url": "https://www.linkedin.com/in/marc-pritchard-pg/"},
    {"title": "Carolyn Tastad - Group President North America - Procter & Gamble | LinkedIn", "url": "https://www.linkedin.com/in/carolyn-tastad/"},
    {"title": "Sundar Raman - President Fabric and Home Care - Procter & Gamble | LinkedIn", "url": "https://www.linkedin.com/in/sundar-raman-pg/"},
    {"title": "Alexandra Keith - President Skin and Personal Care - Procter & Gamble | LinkedIn", "url": "https://www.linkedin.com/in/alexandra-keith-pg/"},
    {"title": "Fama Francisco - President Baby Feminine and Family Care - Procter & Gamble | LinkedIn", "url": "https://www.linkedin.com/in/fama-francisco/"},
    {"title": "Virginie Helias - Chief Sustainability Officer - Procter & Gamble | LinkedIn", "url": "https://www.linkedin.com/in/virginie-helias/"},
    {"title": "Katie Schiavone - Senior Vice President Chief Customer Officer - Procter & Gamble | LinkedIn", "url": "https://www.linkedin.com/in/katie-schiavone/"},
]
print("Procter & Gamble:", ingest_profiles("Procter & Gamble", pg_profiles, min_required=3, max_keep=10))

walmart_profiles = [
    {"title": "John Furner - President and Chief Executive Officer - Walmart | LinkedIn", "url": "https://www.linkedin.com/in/furner/"},
    {"title": "Doug McMillon - Executive Chairman - Walmart | LinkedIn", "url": "https://www.linkedin.com/in/dougmcmillon/"},
    {"title": "John Rainey - Executive Vice President Chief Financial Officer - Walmart | LinkedIn", "url": "https://www.linkedin.com/in/john-rainey-walmart/"},
    {"title": "Suresh Kumar - Executive Vice President Chief Technology Officer - Walmart | LinkedIn", "url": "https://www.linkedin.com/in/suresh-kumar-1488b21/"},
    {"title": "Tom Ward - Executive Vice President Chief eCommerce Officer - Walmart | LinkedIn", "url": "https://www.linkedin.com/in/tom-ward-walmart/"},
    {"title": "Latriece Watkins - Executive Vice President Chief Merchandising Officer - Walmart | LinkedIn", "url": "https://www.linkedin.com/in/latriece-watkins/"},
    {"title": "Chris Nicholas - President and Chief Executive Officer Walmart US - Walmart | LinkedIn", "url": "https://www.linkedin.com/in/chris-nicholas-walmart/"},
    {"title": "Cedric Clark - Executive Vice President US Operations - Walmart | LinkedIn", "url": "https://www.linkedin.com/in/cedric-clark-walmart/"},
    {"title": "Donna Morris - Executive Vice President Chief People Officer - Walmart | LinkedIn", "url": "https://www.linkedin.com/in/donna-morris-walmart/"},
    {"title": "Dan Bartlett - Executive Vice President Corporate Affairs - Walmart | LinkedIn", "url": "https://www.linkedin.com/in/dan-bartlett-walmart/"},
]
print("Walmart:", ingest_profiles("Walmart", walmart_profiles, min_required=3, max_keep=10))

boeing_profiles = [
    {"title": "Kelly Ortberg - President and Chief Executive Officer - Boeing | LinkedIn", "url": "https://www.linkedin.com/in/kelly-ortberg/"},
    {"title": "Ziad Ojakli - Executive Vice President Government Operations - Boeing | LinkedIn", "url": "https://www.linkedin.com/in/ziadojakli/"},
    {"title": "Brian West - Executive Vice President Chief Financial Officer - Boeing | LinkedIn", "url": "https://www.linkedin.com/in/brian-west-boeing/"},
    {"title": "Stephanie Pope - Executive Vice President Chief Operating Officer - Boeing | LinkedIn", "url": "https://www.linkedin.com/in/stephanie-pope-boeing/"},
    {"title": "Ted Colbert - President and Chief Executive Officer Defense Space Security - Boeing | LinkedIn", "url": "https://www.linkedin.com/in/ted-colbert-boeing/"},
    {"title": "Dana Deasy - Executive Vice President Chief Digital and Information Officer - Boeing | LinkedIn", "url": "https://www.linkedin.com/in/dana-deasy/"},
    {"title": "Brett Gerry - Executive Vice President Chief Legal Officer - Boeing | LinkedIn", "url": "https://www.linkedin.com/in/brett-gerry-boeing/"},
    {"title": "Michael Arthur - President Boeing International - Boeing | LinkedIn", "url": "https://www.linkedin.com/in/michael-arthur-boeing/"},
    {"title": "Erin Pipkin - Vice President Communications - Boeing | LinkedIn", "url": "https://www.linkedin.com/in/erin-pipkin-boeing/"},
    {"title": "Uma Amuluru - Chief Human Resources Officer - Boeing | LinkedIn", "url": "https://www.linkedin.com/in/uma-amuluru/"},
]
print("Boeing:", ingest_profiles("Boeing", boeing_profiles, min_required=3, max_keep=10))

lockheed_profiles = [
    {"title": "James Taiclet - Chairman President and Chief Executive Officer - Lockheed Martin | LinkedIn", "url": "https://www.linkedin.com/in/james-taiclet/"},
    {"title": "Jesus Malave - Executive Vice President Chief Financial Officer - Lockheed Martin | LinkedIn", "url": "https://www.linkedin.com/in/jesus-malave/"},
    {"title": "Frank St John - Executive Vice President Chief Operating Officer - Lockheed Martin | LinkedIn", "url": "https://www.linkedin.com/in/frank-st-john/"},
    {"title": "Robert Lightfoot - President Lockheed Martin Space - Lockheed Martin | LinkedIn", "url": "https://www.linkedin.com/in/robert-lightfoot-lm-space/"},
    {"title": "Mark Lazarra - Senior Vice President Aeronautics - Lockheed Martin | LinkedIn", "url": "https://www.linkedin.com/in/mark-lazarra/"},
    {"title": "Richard Ambrose - Executive Vice President Space - Lockheed Martin | LinkedIn", "url": "https://www.linkedin.com/in/richard-ambrose-lm/"},
    {"title": "Maryanne Lavan - Senior Vice President General Counsel - Lockheed Martin | LinkedIn", "url": "https://www.linkedin.com/in/maryanne-lavan/"},
    {"title": "Greg Ulmer - Vice President F-35 Program - Lockheed Martin | LinkedIn", "url": "https://www.linkedin.com/in/greg-ulmer-lm/"},
    {"title": "Maria Ricciardone - Vice President Investor Relations - Lockheed Martin | LinkedIn", "url": "https://www.linkedin.com/in/maria-ricciardone-0b427b99/"},
    {"title": "Richard Vitek - Vice President Analytics and Technology - Lockheed Martin | LinkedIn", "url": "https://www.linkedin.com/in/richard-vitek-b7b8a785/"},
]
print("Lockheed Martin:", ingest_profiles("Lockheed Martin", lockheed_profiles, min_required=3, max_keep=10))

rtx_profiles = [
    {"title": "Christopher Calio - Chairman and Chief Executive Officer - RTX | LinkedIn", "url": "https://www.linkedin.com/in/christopher-calio/"},
    {"title": "Neil Mitchill - Executive Vice President Chief Financial Officer - RTX | LinkedIn", "url": "https://www.linkedin.com/in/neil-mitchill-412b6213/"},
    {"title": "Gregory Hayes - Former Chairman and Chief Executive Officer - RTX | LinkedIn", "url": "https://www.linkedin.com/in/gregory-hayes-rtx/"},
    {"title": "Wesley Kremer - President Raytheon - RTX | LinkedIn", "url": "https://www.linkedin.com/in/wesley-kremer-rtx/"},
    {"title": "Chris Kubasik - President Collins Aerospace - RTX | LinkedIn", "url": "https://www.linkedin.com/in/chris-kubasik/"},
    {"title": "Amy Johnson - Senior Vice President Chief Human Resources Officer - RTX | LinkedIn", "url": "https://www.linkedin.com/in/amy-johnson-rtx/"},
    {"title": "Sean Stackley - Executive Vice President Government Relations - RTX | LinkedIn", "url": "https://www.linkedin.com/in/sean-stackley/"},
    {"title": "Roy Azevedo - President Raytheon Intelligence Space - RTX | LinkedIn", "url": "https://www.linkedin.com/in/roy-azevedo-rtx/"},
    {"title": "Jennifer Reed - Senior Vice President Chief Financial Officer Collins Aerospace - RTX | LinkedIn", "url": "https://www.linkedin.com/in/jennifer-reed-rtx/"},
    {"title": "Michael Dumais - Senior Vice President General Counsel - RTX | LinkedIn", "url": "https://www.linkedin.com/in/michael-dumais-rtx/"},
]
print("RTX:", ingest_profiles("RTX", rtx_profiles, min_required=3, max_keep=10))

abbott_profiles = [
    {"title": "Robert Ford - Chairman and Chief Executive Officer - Abbott Laboratories | LinkedIn", "url": "https://www.linkedin.com/in/robert-ford-abbott/"},
    {"title": "Philip Boudreau - Executive Vice President Chief Financial Officer - Abbott Laboratories | LinkedIn", "url": "https://www.linkedin.com/in/philip-boudreau-8367543/"},
    {"title": "Mary Moreland - Executive Vice President Human Resources - Abbott Laboratories | LinkedIn", "url": "https://www.linkedin.com/in/mary-moreland-4604551/"},
    {"title": "Hubert Allen - Executive Vice President General Counsel - Abbott Laboratories | LinkedIn", "url": "https://www.linkedin.com/in/hubert-allen-abbott/"},
    {"title": "Robert Funck - Executive Vice President Finance - Abbott Laboratories | LinkedIn", "url": "https://www.linkedin.com/in/robert-funck-abbott/"},
    {"title": "Jared Watkin - Executive Vice President Diabetes Care - Abbott Laboratories | LinkedIn", "url": "https://www.linkedin.com/in/jared-watkin/"},
    {"title": "Andrew Lane - Senior Vice President and President Established Pharmaceuticals - Abbott Laboratories | LinkedIn", "url": "https://www.linkedin.com/in/andrew-lane-abbott/"},
    {"title": "Michael Pederson - Senior Vice President and President Medical Devices - Abbott Laboratories | LinkedIn", "url": "https://www.linkedin.com/in/michael-pederson-abbott/"},
    {"title": "Randel Woodgrift - Senior Vice President Quality Regulatory - Abbott Laboratories | LinkedIn", "url": "https://www.linkedin.com/in/randel-woodgrift/"},
    {"title": "Lester Knight - Chairman Board of Directors - Abbott Laboratories | LinkedIn", "url": "https://www.linkedin.com/in/lester-knight-abbott/"},
]
print("Abbott Laboratories:", ingest_profiles("Abbott Laboratories", abbott_profiles, min_required=3, max_keep=10))

deere_profiles = [
    {"title": "John May - Chairman and Chief Executive Officer - Deere & Company | LinkedIn", "url": "https://www.linkedin.com/in/john-c-may/"},
    {"title": "Joshua Jepsen - Senior Vice President Chief Financial Officer - Deere & Company | LinkedIn", "url": "https://www.linkedin.com/in/joshua-jepsen-47668279/"},
    {"title": "Jahmy Hindman - Senior Vice President Chief Technology Officer - Deere & Company | LinkedIn", "url": "https://www.linkedin.com/in/jahmy-hindman-57965533/"},
    {"title": "Cory Reed - President Worldwide Agriculture - Deere & Company | LinkedIn", "url": "https://www.linkedin.com/in/cory-reed/"},
    {"title": "Mark von Pentz - President Crop Care and Worldwide Parts - Deere & Company | LinkedIn", "url": "https://www.linkedin.com/in/mark-von-pentz/"},
    {"title": "Mary K. W. Jones - Senior Vice President General Counsel - Deere & Company | LinkedIn", "url": "https://www.linkedin.com/in/mary-jones-deere/"},
    {"title": "Brent Norwood - Director Investor Relations - Deere & Company | LinkedIn", "url": "https://www.linkedin.com/in/brent-norwood-deere/"},
    {"title": "Domitille Doat - Senior Vice President Chief People Officer - Deere & Company | LinkedIn", "url": "https://www.linkedin.com/in/domitille-doat/"},
    {"title": "Marc Howze - Senior Vice President Lifecycle Solutions - Deere & Company | LinkedIn", "url": "https://www.linkedin.com/in/marc-howze/"},
    {"title": "Ryan Campbell - Senior Vice President Chief Financial Officer Precision Technology - Deere & Company | LinkedIn", "url": "https://www.linkedin.com/in/ryan-campbell-deere/"},
]
print("Deere & Company:", ingest_profiles("Deere & Company", deere_profiles, min_required=3, max_keep=10))

caterpillar_profiles = [
    {"title": "Joe Creed - President and Chief Executive Officer - Caterpillar | LinkedIn", "url": "https://www.linkedin.com/in/joe-creed-caterpillar/"},
    {"title": "Jim Umpleby - Executive Chairman - Caterpillar | LinkedIn", "url": "https://www.linkedin.com/in/jim-umpleby/"},
    {"title": "Andrew Bonfield - Chief Financial Officer - Caterpillar | LinkedIn", "url": "https://www.linkedin.com/in/andrew-bonfield-cat/"},
    {"title": "Rob Charter - Group President Services Distribution Digital - Caterpillar | LinkedIn", "url": "https://www.linkedin.com/in/rob-charter-caterpillar/"},
    {"title": "Tony Fassino - Group President Construction Industries - Caterpillar | LinkedIn", "url": "https://www.linkedin.com/in/tony-fassino/"},
    {"title": "Bob De Lange - Group President Resource Industries - Caterpillar | LinkedIn", "url": "https://www.linkedin.com/in/bob-de-lange-caterpillar/"},
    {"title": "Steph Lundberg - Chief Marketing Officer - Caterpillar | LinkedIn", "url": "https://www.linkedin.com/in/steph-lundberg-cat/"},
    {"title": "Denise Johnson - Group President Resource Industries - Caterpillar | LinkedIn", "url": "https://www.linkedin.com/in/denise-johnson-caterpillar/"},
    {"title": "Kyle Epley - Vice President Technology and Solutions - Caterpillar | LinkedIn", "url": "https://www.linkedin.com/in/kyle-epley-cat/"},
    {"title": "David Bozeman - Group President Energy Transportation - Caterpillar | LinkedIn", "url": "https://www.linkedin.com/in/david-bozeman-caterpillar/"},
]
print("Caterpillar:", ingest_profiles("Caterpillar", caterpillar_profiles, min_required=3, max_keep=10))

gm_profiles = [
    {"title": "Mary Barra - Chair and Chief Executive Officer - General Motors | LinkedIn", "url": "https://www.linkedin.com/in/mary-barra/"},
    {"title": "Paul Jacobson - Executive Vice President Chief Financial Officer - General Motors | LinkedIn", "url": "https://www.linkedin.com/in/paul-jacobson-gm/"},
    {"title": "Mark Reuss - President - General Motors | LinkedIn", "url": "https://www.linkedin.com/in/mark-reuss/"},
    {"title": "Doug Parks - Executive Vice President Global Product Programs - General Motors | LinkedIn", "url": "https://www.linkedin.com/in/doug-parks-gm/"},
    {"title": "Steve Carlisle - Executive Vice President President GMNA - General Motors | LinkedIn", "url": "https://www.linkedin.com/in/steve-carlisle-gm/"},
    {"title": "Shilpan Amin - Vice President Global Purchasing Supply Chain - General Motors | LinkedIn", "url": "https://www.linkedin.com/in/shilpan-amin/"},
    {"title": "Pam Fletcher - Executive Chief Engineer Global Electric Vehicles - General Motors | LinkedIn", "url": "https://www.linkedin.com/in/pam-fletcher-gm/"},
    {"title": "Mike Abbott - Executive Vice President Software and Services - General Motors | LinkedIn", "url": "https://www.linkedin.com/in/mike-abbott-gm/"},
    {"title": "Julian Blissett - Executive Vice President Global Manufacturing Quality - General Motors | LinkedIn", "url": "https://www.linkedin.com/in/julian-blissett/"},
    {"title": "Ken Morris - Vice President EV Autonomous Vehicle Programs - General Motors | LinkedIn", "url": "https://www.linkedin.com/in/ken-morris-gm/"},
]
print("General Motors:", ingest_profiles("General Motors", gm_profiles, min_required=3, max_keep=10))

ford_profiles = [
    {"title": "Jim Farley - President and Chief Executive Officer - Ford Motor | LinkedIn", "url": "https://www.linkedin.com/in/jim-farley/"},
    {"title": "John Lawler - Vice Chair and Chief Financial Officer - Ford Motor | LinkedIn", "url": "https://www.linkedin.com/in/john-lawler-ford/"},
    {"title": "Jim Baumbick - President Ford Europe - Ford Motor | LinkedIn", "url": "https://www.linkedin.com/in/jim-baumbick/"},
    {"title": "Lisa Drake - Vice President EV Industrialization - Ford Motor | LinkedIn", "url": "https://www.linkedin.com/in/lisa-drake-ford/"},
    {"title": "Andrew Frick - President Ford Blue - Ford Motor | LinkedIn", "url": "https://www.linkedin.com/in/andrew-frick-ford/"},
    {"title": "Marin Gjaja - Chief Customer Officer Ford Model e - Ford Motor | LinkedIn", "url": "https://www.linkedin.com/in/marin-gjaja/"},
    {"title": "Jim Farley - CEO at Ford Motor Company - Ford Motor | LinkedIn", "url": "https://www.linkedin.com/in/jim-farley-ford/"},
    {"title": "Kumar Galhotra - President Ford Blue Americas - Ford Motor | LinkedIn", "url": "https://www.linkedin.com/in/kumar-galhotra/"},
    {"title": "Doug Field - Chief Advanced Product and Technology Officer - Ford Motor | LinkedIn", "url": "https://www.linkedin.com/in/doug-field-ford/"},
    {"title": "Liz Tail - Vice President Connected Services - Ford Motor | LinkedIn", "url": "https://www.linkedin.com/in/liz-tail-ford/"},
]
print("Ford Motor:", ingest_profiles("Ford Motor", ford_profiles, min_required=3, max_keep=10))

salesforce_profiles = [
    {"title": "Marc Benioff - Chair and Chief Executive Officer - Salesforce | LinkedIn", "url": "https://www.linkedin.com/in/marc-benioff-4a5646117/"},
    {"title": "Parker Harris - Co-Founder and Chief Technology Officer - Salesforce | LinkedIn", "url": "https://www.linkedin.com/in/parker-harris-451040211/"},
    {"title": "Robin Washington - President Chief Operating and Financial Officer - Salesforce | LinkedIn", "url": "https://www.linkedin.com/in/robin-washington-salesforce/"},
    {"title": "Srinivas Tallapragada - President Chief Engineering Officer - Salesforce | LinkedIn", "url": "https://www.linkedin.com/in/srini-tallapragada/"},
    {"title": "David Schmaier - President Chief Product Officer - Salesforce | LinkedIn", "url": "https://www.linkedin.com/in/david-schmaier/"},
    {"title": "Clara Shih - Chief Executive Officer Salesforce AI - Salesforce | LinkedIn", "url": "https://www.linkedin.com/in/clarashih/"},
    {"title": "Ariel Kelman - President Chief Marketing Officer - Salesforce | LinkedIn", "url": "https://www.linkedin.com/in/ariel-kelman/"},
    {"title": "Nathalie Scardino - President Chief People Officer - Salesforce | LinkedIn", "url": "https://www.linkedin.com/in/nathalie-scardino/"},
    {"title": "Miguel Milano - President Salesforce International - Salesforce | LinkedIn", "url": "https://www.linkedin.com/in/miguel-milano-salesforce/"},
    {"title": "Sabastian Niles - President Chief Legal Officer - Salesforce | LinkedIn", "url": "https://www.linkedin.com/in/sabastian-niles/"},
]
print("Salesforce:", ingest_profiles("Salesforce", salesforce_profiles, min_required=3, max_keep=10))

netflix_profiles = [
    {"title": "Ted Sarandos - Co-Chief Executive Officer - Netflix | LinkedIn", "url": "https://www.linkedin.com/in/tedsarandos/"},
    {"title": "Greg Peters - Co-Chief Executive Officer - Netflix | LinkedIn", "url": "https://www.linkedin.com/in/greg-peters-netflix/"},
    {"title": "Spencer Neumann - Chief Financial Officer - Netflix | LinkedIn", "url": "https://www.linkedin.com/in/spencer-neumann-592b6b148/"},
    {"title": "Bela Bajaria - Chief Content Officer - Netflix | LinkedIn", "url": "https://www.linkedin.com/in/bela-bajaria/"},
    {"title": "Marian Lee - Chief Marketing Officer - Netflix | LinkedIn", "url": "https://www.linkedin.com/in/marian-lee-bb27843/"},
    {"title": "Elizabeth Stone - Chief Technology Officer - Netflix | LinkedIn", "url": "https://www.linkedin.com/in/elizabeth-stone-608a754/"},
    {"title": "Rachel Whetstone - Chief Communications Officer - Netflix | LinkedIn", "url": "https://www.linkedin.com/in/rachel-whetstone/"},
    {"title": "Sergio Ezama - Chief Human Resources Officer - Netflix | LinkedIn", "url": "https://www.linkedin.com/in/sergio-ezama/"},
    {"title": "Eunice Kim - Vice President Product - Netflix | LinkedIn", "url": "https://www.linkedin.com/in/eunice-kim-netflix/"},
    {"title": "Dan Lin - Head of Films - Netflix | LinkedIn", "url": "https://www.linkedin.com/in/dan-lin-netflix/"},
]
print("Netflix:", ingest_profiles("Netflix", netflix_profiles, min_required=3, max_keep=10))

stripe_profiles = [
    {"title": "Patrick Collison - Chief Executive Officer - Stripe | LinkedIn", "url": "https://www.linkedin.com/in/patrickcollison/"},
    {"title": "John Collison - President - Stripe | LinkedIn", "url": "https://www.linkedin.com/in/johnbcollison/"},
    {"title": "Will Gaybrick - President Product and Technology - Stripe | LinkedIn", "url": "https://www.linkedin.com/in/wgaybrick/"},
    {"title": "Tomer London - Co-Founder Chief Product Officer - Stripe | LinkedIn", "url": "https://www.linkedin.com/in/tomer-london/"},
    {"title": "Mike Clayville - Chief Revenue Officer - Stripe | LinkedIn", "url": "https://www.linkedin.com/in/mikeclayville/"},
    {"title": "Eileen O'Mara - Chief Revenue Officer - Stripe | LinkedIn", "url": "https://www.linkedin.com/in/eileenomara/"},
    {"title": "Jeff Weinstein - Head of Product Growth - Stripe | LinkedIn", "url": "https://www.linkedin.com/in/jeffweinstein/"},
    {"title": "Emily Glassberg - Vice President Data Science - Stripe | LinkedIn", "url": "https://www.linkedin.com/in/emily-glassberg/"},
    {"title": "Cristina Cordova - Head of Platform and Partnerships - Stripe | LinkedIn", "url": "https://www.linkedin.com/in/cristina-cordova/"},
    {"title": "Vivek Sharma - Vice President Engineering - Stripe | LinkedIn", "url": "https://www.linkedin.com/in/vivek-sharma-stripe/"},
]
print("Stripe:", ingest_profiles("Stripe", stripe_profiles, min_required=3, max_keep=10))

palantir_profiles = [
    {"title": "Alex Karp - Chief Executive Officer - Palantir | LinkedIn", "url": "https://www.linkedin.com/in/alex-karp-palantir/"},
    {"title": "Shyam Sankar - Chief Technology Officer - Palantir | LinkedIn", "url": "https://www.linkedin.com/in/shyamsankar/"},
    {"title": "Ryan Taylor - Chief Revenue Officer and Chief Legal Officer - Palantir | LinkedIn", "url": "https://www.linkedin.com/in/ryan-taylor-palantir/"},
    {"title": "Kevin Kawasaki - Chief Business Development Officer - Palantir | LinkedIn", "url": "https://www.linkedin.com/in/kevin-kawasaki-3b09852/"},
    {"title": "Dave Glazer - Chief Revenue Officer - Palantir | LinkedIn", "url": "https://www.linkedin.com/in/dave-glazer-palantir/"},
    {"title": "Ted Mabrey - Chief Commercial Officer - Palantir | LinkedIn", "url": "https://www.linkedin.com/in/ted-mabrey/"},
    {"title": "Nikos Michalakis - Senior Vice President Product - Palantir | LinkedIn", "url": "https://www.linkedin.com/in/nikos-michalakis/"},
    {"title": "Ana Fuentes - Vice President Platform - Palantir | LinkedIn", "url": "https://www.linkedin.com/in/ana-fuentes-palantir/"},
    {"title": "Chelsea Robinson - Vice President Federal Operations - Palantir | LinkedIn", "url": "https://www.linkedin.com/in/chelsea-robinson-palantir/"},
    {"title": "Akash Jain - President Palantir US Commercial - Palantir | LinkedIn", "url": "https://www.linkedin.com/in/akash-jain-palantir/"},
]
print("Palantir:", ingest_profiles("Palantir", palantir_profiles, min_required=3, max_keep=10))

openai_profiles = [
    {"title": "Sam Altman - Chief Executive Officer - OpenAI | LinkedIn", "url": "https://www.linkedin.com/in/sam-altman/"},
    {"title": "Greg Brockman - President - OpenAI | LinkedIn", "url": "https://www.linkedin.com/in/thegdb/"},
    {"title": "Brad Lightcap - Chief Operating Officer - OpenAI | LinkedIn", "url": "https://www.linkedin.com/in/brad-lightcap/"},
    {"title": "Jason Kwon - Chief Strategy Officer - OpenAI | LinkedIn", "url": "https://www.linkedin.com/in/jasonkwon/"},
    {"title": "Chris Lehane - Vice President Global Affairs - OpenAI | LinkedIn", "url": "https://www.linkedin.com/in/chris-lehane/"},
    {"title": "Srinivas Narayanan - Vice President Research - OpenAI | LinkedIn", "url": "https://www.linkedin.com/in/srinivas-narayanan-openai/"},
    {"title": "Anna Makanju - Vice President Global Affairs - OpenAI | LinkedIn", "url": "https://www.linkedin.com/in/anna-makanju/"},
    {"title": "Fidji Simo - Chief Executive Officer Applications - OpenAI | LinkedIn", "url": "https://www.linkedin.com/in/fidjisimo/"},
    {"title": "Sarah Friar - Chief Financial Officer - OpenAI | LinkedIn", "url": "https://www.linkedin.com/in/sarah-friar/"},
    {"title": "Kevin Weil - Chief Product Officer - OpenAI | LinkedIn", "url": "https://www.linkedin.com/in/kevinweil/"},
]
print("OpenAI:", ingest_profiles("OpenAI", openai_profiles, min_required=3, max_keep=10))

anduril_profiles = [
    {"title": "Palmer Luckey - Founder - Anduril Industries | LinkedIn", "url": "https://www.linkedin.com/in/palmer-luckey-21a16959/"},
    {"title": "Brian Schimpf - Co-Founder and Chief Executive Officer - Anduril Industries | LinkedIn", "url": "https://www.linkedin.com/in/bschimpf/"},
    {"title": "Matt Grimm - Co-Founder and Chief Operating Officer - Anduril Industries | LinkedIn", "url": "https://www.linkedin.com/in/mttgrmm/"},
    {"title": "Christian Brose - President and Chief Strategy Officer - Anduril Industries | LinkedIn", "url": "https://www.linkedin.com/in/christian-brose/"},
    {"title": "Trae Stephens - Co-Founder Executive Chairman - Anduril Industries | LinkedIn", "url": "https://www.linkedin.com/in/trae-stephens/"},
    {"title": "Jason Levin - Chief Revenue Officer - Anduril Industries | LinkedIn", "url": "https://www.linkedin.com/in/jason-levin-anduril/"},
    {"title": "Joseph Chen - Co-Founder - Anduril Industries | LinkedIn", "url": "https://www.linkedin.com/in/joseph-chen-anduril/"},
    {"title": "Matthew Steckman - Chief Revenue Officer - Anduril Industries | LinkedIn", "url": "https://www.linkedin.com/in/matthew-steckman/"},
    {"title": "Linden Fowler - Chief of Staff - Anduril Industries | LinkedIn", "url": "https://www.linkedin.com/in/linden-fowler/"},
    {"title": "Vinnie Moss - Vice President Business Development - Anduril Industries | LinkedIn", "url": "https://www.linkedin.com/in/vinnie-moss-anduril/"},
]
print("Anduril Industries:", ingest_profiles("Anduril Industries", anduril_profiles, min_required=3, max_keep=10))

# ── Contact summary ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("Contact counts after ingest:")
print("="*60)
with get_db() as conn:
    for c in COMPANIES:
        row = conn.execute(
            """SELECT co.name, COUNT(ct.id) as total,
               SUM(CASE WHEN ct.primary_email IS NOT NULL AND ct.primary_email != '' THEN 1 ELSE 0 END) as with_email
               FROM companies co
               LEFT JOIN contacts ct ON ct.company_id = co.id
               WHERE co.domain = ?
               GROUP BY co.id""",
            (c["domain"],)
        ).fetchone()
        if row:
            status = "OK" if row["with_email"] >= 5 else "LOW"
            print(f"  [{status}] {row['name']}: {row['with_email']} with email")

# ── Step 3: Create campaign ───────────────────────────────────────────────────
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

# ── Step 4: Personalize ───────────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 4: Personalizing (once per company, clone for rest)")
print("="*60)
personalize_once_per_company(
    campaign_id,
    SENDER_VALUE_PROP,
    num_steps=3,
    company_domains=COMPANY_DOMAINS,
)

# ── Step 5: Send ─────────────────────────────────────────────────────────────
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
