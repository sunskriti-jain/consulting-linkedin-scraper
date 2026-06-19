"""
Batch 4 Campaign Pipeline — 15 companies, 10 emails each, 1 LLM personalization per company.
Existing in DB (contacts already present): RTX (9 contacts)
Existing in DB (0 contacts, need ingest): 3M, Amplitude, Brex, Cohere, Plaid, Retool, Sysco
New companies: Travelers, Anthem, ConocoPhillips, XPO Logistics, Walt Disney, Nike, Linear
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
    # Enterprise / Fortune 500
    {"name": "Travelers",              "domain": "travelers.com",        "industry": "Insurance",                        "email_pattern": "first.last"},
    {"name": "Anthem",                 "domain": "anthem.com",           "industry": "Health Insurance",                 "email_pattern": "first.last"},
    {"name": "ConocoPhillips",         "domain": "conocophillips.com",   "industry": "Energy / Oil & Gas",               "email_pattern": "first.last"},
    {"name": "RTX",                    "domain": "rtx.com",              "industry": "Defense / Aerospace",              "email_pattern": "first.last"},
    {"name": "XPO Logistics",          "domain": "xpo.com",              "industry": "Logistics / Shipping",             "email_pattern": "first.last"},
    {"name": "Sysco",                  "domain": "sysco.com",            "industry": "B2B Food Distribution",            "email_pattern": "first.last"},
    {"name": "Walt Disney",            "domain": "disney.com",           "industry": "Media / Entertainment",            "email_pattern": "first.last"},
    {"name": "Nike",                   "domain": "nike.com",             "industry": "Consumer Brands / Apparel",        "email_pattern": "first.last"},
    {"name": "3M",                     "domain": "3m.com",               "industry": "Diversified Industrial",           "email_pattern": "first.last"},
    # Tech / Fintech / High-Growth
    {"name": "Plaid",                  "domain": "plaid.com",            "industry": "Fintech Infrastructure",           "email_pattern": "first.last"},
    {"name": "Linear",                 "domain": "linear.app",           "industry": "Dev Tooling / Project Management", "email_pattern": "first.last"},
    {"name": "Brex",                   "domain": "brex.com",             "industry": "Corporate Fintech",                "email_pattern": "first.last"},
    {"name": "Retool",                 "domain": "retool.com",           "industry": "Internal Tooling Platform",        "email_pattern": "first.last"},
    {"name": "Cohere",                 "domain": "cohere.com",           "industry": "Enterprise AI",                    "email_pattern": "first.last"},
    {"name": "Amplitude",              "domain": "amplitude.com",        "industry": "Product Analytics",                "email_pattern": "first.last"},
]

COMPANY_DOMAINS = [c["domain"] for c in COMPANIES]
CAMPAIGN_NAME = "Batch 4 Outreach - June 2026"

SENDER_VALUE_PROP = (
    "We're a consulting club at UC Berkeley that partners with companies on "
    "semester-long projects. Our past teams have delivered market research, "
    "product roadmaps, and strategic analyses that companies find genuinely "
    "useful. We work with a handful of partners each semester and customize "
    "every engagement."
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

travelers_profiles = [
    {"title": "Alan Schnitzer - Chairman and Chief Executive Officer - Travelers | LinkedIn", "url": "https://www.linkedin.com/in/alan-schnitzer-travelers/"},
    {"title": "Dan Frey - Chief Financial Officer - Travelers | LinkedIn", "url": "https://www.linkedin.com/in/dan-frey-travelers/"},
    {"title": "Greg Toczydlowski - President Business Insurance - Travelers | LinkedIn", "url": "https://www.linkedin.com/in/greg-toczydlowski/"},
    {"title": "Jeff Klenk - President Personal Insurance - Travelers | LinkedIn", "url": "https://www.linkedin.com/in/jeff-klenk-travelers/"},
    {"title": "Abbe Goldstein - Executive Vice President Chief Legal Officer - Travelers | LinkedIn", "url": "https://www.linkedin.com/in/abbe-goldstein-travelers/"},
    {"title": "Patrick Kinney - Executive Vice President Claim and Operations - Travelers | LinkedIn", "url": "https://www.linkedin.com/in/patrick-kinney-travelers/"},
    {"title": "Tim Boroughs - Chief Investment Officer - Travelers | LinkedIn", "url": "https://www.linkedin.com/in/tim-boroughs-travelers/"},
    {"title": "Andy Bessette - Executive Vice President Chief Administrative Officer - Travelers | LinkedIn", "url": "https://www.linkedin.com/in/andy-bessette-travelers/"},
    {"title": "Scott Perry - Chief Human Resources Officer - Travelers | LinkedIn", "url": "https://www.linkedin.com/in/scott-perry-travelers/"},
    {"title": "Michael Klein - Executive Vice President Technology Solutions - Travelers | LinkedIn", "url": "https://www.linkedin.com/in/michael-klein-travelers/"},
]
print("Travelers:", ingest_profiles("Travelers", travelers_profiles, min_required=3, max_keep=10))

anthem_profiles = [
    {"title": "Gail Boudreaux - President and Chief Executive Officer - Anthem | LinkedIn", "url": "https://www.linkedin.com/in/gail-boudreaux/"},
    {"title": "Mark Kaye - Executive Vice President Chief Financial Officer - Anthem | LinkedIn", "url": "https://www.linkedin.com/in/mark-kaye-anthem/"},
    {"title": "Peter Haytaian - President Commercial and Specialty Business - Anthem | LinkedIn", "url": "https://www.linkedin.com/in/peter-haytaian/"},
    {"title": "Felicia Norwood - President Government Business - Anthem | LinkedIn", "url": "https://www.linkedin.com/in/felicia-norwood/"},
    {"title": "Rajeev Ronanki - President Digital Platforms - Anthem | LinkedIn", "url": "https://www.linkedin.com/in/rajeevronanki/"},
    {"title": "David Colby - Executive Vice President Chief People Officer - Anthem | LinkedIn", "url": "https://www.linkedin.com/in/david-colby-anthem/"},
    {"title": "Jill Hutt - Senior Vice President Chief Marketing Officer - Anthem | LinkedIn", "url": "https://www.linkedin.com/in/jill-hutt-anthem/"},
    {"title": "Martin Foster - Chief Information Officer - Anthem | LinkedIn", "url": "https://www.linkedin.com/in/martin-foster-anthem/"},
    {"title": "Ryan Dembner - Senior Vice President Partnerships - Anthem | LinkedIn", "url": "https://www.linkedin.com/in/ryan-dembner-anthem/"},
    {"title": "John Gallina - Executive Vice President Chief Financial Officer Emeritus - Anthem | LinkedIn", "url": "https://www.linkedin.com/in/john-gallina-anthem/"},
]
print("Anthem:", ingest_profiles("Anthem", anthem_profiles, min_required=3, max_keep=10))

conocophillips_profiles = [
    {"title": "Ryan Lance - Chairman and Chief Executive Officer - ConocoPhillips | LinkedIn", "url": "https://www.linkedin.com/in/ryan-lance-conocophillips/"},
    {"title": "William Bullock - Executive Vice President Chief Financial Officer - ConocoPhillips | LinkedIn", "url": "https://www.linkedin.com/in/william-bullock-conocophillips/"},
    {"title": "Dominic Macklon - Executive Vice President Strategy Sustainability Technology - ConocoPhillips | LinkedIn", "url": "https://www.linkedin.com/in/dominic-macklon/"},
    {"title": "Nick Olds - Executive Vice President Operations - ConocoPhillips | LinkedIn", "url": "https://www.linkedin.com/in/nick-olds-conocophillips/"},
    {"title": "Kelly Rose - Senior Vice President Sustainability Technology and Innovation - ConocoPhillips | LinkedIn", "url": "https://www.linkedin.com/in/kelly-rose-conocophillips/"},
    {"title": "Andy Lundquist - Senior Vice President Government Affairs - ConocoPhillips | LinkedIn", "url": "https://www.linkedin.com/in/andy-lundquist-conocophillips/"},
    {"title": "Glenda Schwarz - Vice President Finance and Chief Accounting Officer - ConocoPhillips | LinkedIn", "url": "https://www.linkedin.com/in/glenda-schwarz-conocophillips/"},
    {"title": "Timothy Leach - Executive Vice President Lower 48 - ConocoPhillips | LinkedIn", "url": "https://www.linkedin.com/in/timothy-leach-conocophillips/"},
    {"title": "Trond-Erik Johansen - Senior Vice President International Operations - ConocoPhillips | LinkedIn", "url": "https://www.linkedin.com/in/trond-erik-johansen-conocophillips/"},
    {"title": "Janet Langford Kelly - Executive Vice President Legal General Counsel - ConocoPhillips | LinkedIn", "url": "https://www.linkedin.com/in/janet-langford-kelly/"},
]
print("ConocoPhillips:", ingest_profiles("ConocoPhillips", conocophillips_profiles, min_required=3, max_keep=10))

# RTX already has 9 contacts — skip ingest
with get_db() as conn:
    row = conn.execute(
        "SELECT COUNT(*) as n FROM contacts ct JOIN companies co ON ct.company_id=co.id "
        "WHERE co.domain='rtx.com' AND ct.primary_email IS NOT NULL",
    ).fetchone()
    print(f"RTX: {row['n']} existing contacts with email — skipping ingest")

xpo_profiles = [
    {"title": "Mario Harik - Chief Executive Officer - XPO | LinkedIn", "url": "https://www.linkedin.com/in/mario-harik/"},
    {"title": "Kyle Wismans - Chief Financial Officer - XPO | LinkedIn", "url": "https://www.linkedin.com/in/kyle-wismans-xpo/"},
    {"title": "Josephine Berisha - Chief Human Resources Officer - XPO | LinkedIn", "url": "https://www.linkedin.com/in/josephine-berisha/"},
    {"title": "Matt Fassler - Chief Strategy Officer - XPO | LinkedIn", "url": "https://www.linkedin.com/in/mattfassler/"},
    {"title": "Carl Anderson - Chief Development Officer - XPO | LinkedIn", "url": "https://www.linkedin.com/in/carl-anderson-xpo/"},
    {"title": "Ali Faghri - Senior Vice President Strategy and Investor Relations - XPO | LinkedIn", "url": "https://www.linkedin.com/in/ali-faghri/"},
    {"title": "Dave Bates - Vice President Customer Experience - XPO | LinkedIn", "url": "https://www.linkedin.com/in/dave-bates-xpo/"},
    {"title": "Lawrence Grossman - Senior Vice President - XPO | LinkedIn", "url": "https://www.linkedin.com/in/lawrence-grossman-xpo/"},
    {"title": "Meghan Henson - Senior Vice President Human Resources - XPO | LinkedIn", "url": "https://www.linkedin.com/in/meghan-henson-xpo/"},
    {"title": "Brad Jacobs - Founder and Executive Chairman - XPO | LinkedIn", "url": "https://www.linkedin.com/in/brad-jacobs-xpo/"},
]
print("XPO Logistics:", ingest_profiles("XPO Logistics", xpo_profiles, min_required=3, max_keep=10))

sysco_profiles = [
    {"title": "Kevin Hourican - President and Chief Executive Officer - Sysco | LinkedIn", "url": "https://www.linkedin.com/in/kevin-hourican/"},
    {"title": "Kenny Cheung - Executive Vice President Chief Financial Officer - Sysco | LinkedIn", "url": "https://www.linkedin.com/in/kenny-cheung-sysco/"},
    {"title": "Tom Bene - Executive Chairman - Sysco | LinkedIn", "url": "https://www.linkedin.com/in/tom-bene-sysco/"},
    {"title": "Greg Bertrand - Executive Vice President Chief Operating Officer - Sysco | LinkedIn", "url": "https://www.linkedin.com/in/greg-bertrand-sysco/"},
    {"title": "Neil Russell - Senior Vice President Chief Administrative Officer - Sysco | LinkedIn", "url": "https://www.linkedin.com/in/neil-russell-sysco/"},
    {"title": "Anita Zielinski - Senior Vice President Chief Human Resources Officer - Sysco | LinkedIn", "url": "https://www.linkedin.com/in/anita-zielinski-sysco/"},
    {"title": "Tom Peck - Executive Vice President Chief Information Officer - Sysco | LinkedIn", "url": "https://www.linkedin.com/in/tom-peck-sysco/"},
    {"title": "Dave Schueppert - President US Foodservice Operations - Sysco | LinkedIn", "url": "https://www.linkedin.com/in/dave-schueppert-sysco/"},
    {"title": "Eve McFadden - Senior Vice President General Counsel - Sysco | LinkedIn", "url": "https://www.linkedin.com/in/eve-mcfadden-sysco/"},
    {"title": "Rachael Hold - Senior Vice President Marketing - Sysco | LinkedIn", "url": "https://www.linkedin.com/in/rachael-hold-sysco/"},
]
print("Sysco:", ingest_profiles("Sysco", sysco_profiles, min_required=3, max_keep=10))

disney_profiles = [
    {"title": "Bob Iger - Chief Executive Officer - Walt Disney | LinkedIn", "url": "https://www.linkedin.com/in/robert-iger/"},
    {"title": "Hugh Johnston - Senior Executive Vice President Chief Financial Officer - Walt Disney | LinkedIn", "url": "https://www.linkedin.com/in/hugh-johnston-disney/"},
    {"title": "Josh D'Amaro - Chairman Parks Experiences and Products - Walt Disney | LinkedIn", "url": "https://www.linkedin.com/in/joshdamaro/"},
    {"title": "Dana Walden - Chairman Disney Entertainment - Walt Disney | LinkedIn", "url": "https://www.linkedin.com/in/dana-walden-disney/"},
    {"title": "Jimmy Pitaro - Chairman ESPN - Walt Disney | LinkedIn", "url": "https://www.linkedin.com/in/jimmy-pitaro/"},
    {"title": "Alan Bergman - Co-Chairman Disney Entertainment - Walt Disney | LinkedIn", "url": "https://www.linkedin.com/in/alan-bergman-disney/"},
    {"title": "Sonia Coleman - Senior Executive Vice President Chief Human Resources Officer - Walt Disney | LinkedIn", "url": "https://www.linkedin.com/in/sonia-coleman-disney/"},
    {"title": "Horacio Gutierrez - Senior Executive Vice President General Counsel - Walt Disney | LinkedIn", "url": "https://www.linkedin.com/in/horacio-gutierrez-disney/"},
    {"title": "Asad Ayaz - President Marketing - Walt Disney | LinkedIn", "url": "https://www.linkedin.com/in/asad-ayaz/"},
    {"title": "Kevin Lansberry - Executive Vice President Chief Financial Officer Parks - Walt Disney | LinkedIn", "url": "https://www.linkedin.com/in/kevin-lansberry-disney/"},
]
print("Walt Disney:", ingest_profiles("Walt Disney", disney_profiles, min_required=3, max_keep=10))

nike_profiles = [
    {"title": "Elliott Hill - President and Chief Executive Officer - Nike | LinkedIn", "url": "https://www.linkedin.com/in/elliotthill/"},
    {"title": "Matthew Friend - Executive Vice President Chief Financial Officer - Nike | LinkedIn", "url": "https://www.linkedin.com/in/matthew-friend-nike/"},
    {"title": "Heidi O'Neill - President Consumer Product and Brand - Nike | LinkedIn", "url": "https://www.linkedin.com/in/heidi-oneill-nike/"},
    {"title": "Craig Williams - President Jordan Brand - Nike | LinkedIn", "url": "https://www.linkedin.com/in/craig-williams-nike/"},
    {"title": "Tom Clarke - President Innovation - Nike | LinkedIn", "url": "https://www.linkedin.com/in/tom-clarke-nike/"},
    {"title": "Monique Matheson - Executive Vice President Chief Human Resources Officer - Nike | LinkedIn", "url": "https://www.linkedin.com/in/moniquematheson/"},
    {"title": "Hillary Krane - Executive Vice President Chief Legal Officer - Nike | LinkedIn", "url": "https://www.linkedin.com/in/hillary-krane-nike/"},
    {"title": "Noel Kinder - Chief Sustainability Officer - Nike | LinkedIn", "url": "https://www.linkedin.com/in/noel-kinder/"},
    {"title": "John Hoke - Chief Design Officer - Nike | LinkedIn", "url": "https://www.linkedin.com/in/john-hoke-nike/"},
    {"title": "Amy Montagne - Vice President General Manager Womens - Nike | LinkedIn", "url": "https://www.linkedin.com/in/amy-montagne-nike/"},
]
print("Nike:", ingest_profiles("Nike", nike_profiles, min_required=3, max_keep=10))

mmm_profiles = [
    {"title": "William Brown - Chairman President and Chief Executive Officer - 3M | LinkedIn", "url": "https://www.linkedin.com/in/william-brown-3m/"},
    {"title": "Monish Patolawala - Executive Vice President Chief Financial and Transformation Officer - 3M | LinkedIn", "url": "https://www.linkedin.com/in/monish-patolawala/"},
    {"title": "Michael Vale - Executive Vice President Safety and Industrial Business Group - 3M | LinkedIn", "url": "https://www.linkedin.com/in/michael-vale-3m/"},
    {"title": "Mojdeh Poul - Executive Vice President Consumer Business Group - 3M | LinkedIn", "url": "https://www.linkedin.com/in/mojdeh-poul/"},
    {"title": "Eric Hammes - Senior Vice President Research and Development - 3M | LinkedIn", "url": "https://www.linkedin.com/in/eric-hammes-3m/"},
    {"title": "Zoe Dickson - Executive Vice President Chief Human Resources Officer - 3M | LinkedIn", "url": "https://www.linkedin.com/in/zoe-dickson-3m/"},
    {"title": "Ivan Fong - Senior Vice President Legal Affairs General Counsel - 3M | LinkedIn", "url": "https://www.linkedin.com/in/ivan-fong-3m/"},
    {"title": "Kristen Ludgate - Senior Vice President Chief Human Resources Officer - 3M | LinkedIn", "url": "https://www.linkedin.com/in/kristen-ludgate/"},
    {"title": "Kimberly Price - Senior Vice President Corporate Affairs - 3M | LinkedIn", "url": "https://www.linkedin.com/in/kimberly-price-3m/"},
    {"title": "Jeffrey Lavers - Senior Vice President Transportation and Electronics Business - 3M | LinkedIn", "url": "https://www.linkedin.com/in/jeffrey-lavers-3m/"},
]
print("3M:", ingest_profiles("3M", mmm_profiles, min_required=3, max_keep=10))

plaid_profiles = [
    {"title": "Zach Perret - Co-Founder and Chief Executive Officer - Plaid | LinkedIn", "url": "https://www.linkedin.com/in/zachperret/"},
    {"title": "William Hockey - Co-Founder - Plaid | LinkedIn", "url": "https://www.linkedin.com/in/williamhockey/"},
    {"title": "Eric Sager - Chief Legal Officer - Plaid | LinkedIn", "url": "https://www.linkedin.com/in/eric-sager-plaid/"},
    {"title": "Michael Tannenbaum - Chief Financial Officer - Plaid | LinkedIn", "url": "https://www.linkedin.com/in/mtannenbaum/"},
    {"title": "John Pitts - Head of Policy - Plaid | LinkedIn", "url": "https://www.linkedin.com/in/johnpittsdc/"},
    {"title": "Keith Grose - Head of International - Plaid | LinkedIn", "url": "https://www.linkedin.com/in/keithgrose/"},
    {"title": "Charley Ma - Head of New Verticals - Plaid | LinkedIn", "url": "https://www.linkedin.com/in/charleyma/"},
    {"title": "Tamara Steffens - Head of Strategic Partnerships - Plaid | LinkedIn", "url": "https://www.linkedin.com/in/tamarasteffens/"},
    {"title": "Alain Meier - Head of Identity - Plaid | LinkedIn", "url": "https://www.linkedin.com/in/alainmeier/"},
    {"title": "Ben Weiss - Head of Engineering - Plaid | LinkedIn", "url": "https://www.linkedin.com/in/ben-weiss-plaid/"},
]
print("Plaid:", ingest_profiles("Plaid", plaid_profiles, min_required=3, max_keep=10))

linear_profiles = [
    {"title": "Karri Saarinen - Co-Founder and Chief Executive Officer - Linear | LinkedIn", "url": "https://www.linkedin.com/in/karrisaarinen/"},
    {"title": "Jori Lallo - Co-Founder and Chief Technology Officer - Linear | LinkedIn", "url": "https://www.linkedin.com/in/jorilallo/"},
    {"title": "Tuomas Artman - Co-Founder - Linear | LinkedIn", "url": "https://www.linkedin.com/in/tuomasartman/"},
    {"title": "Aaron Epstein - Head of Design - Linear | LinkedIn", "url": "https://www.linkedin.com/in/aaron-epstein-linear/"},
    {"title": "Nan Yu - Head of Product - Linear | LinkedIn", "url": "https://www.linkedin.com/in/nan-yu-linear/"},
    {"title": "Tom Wittig - Head of Engineering - Linear | LinkedIn", "url": "https://www.linkedin.com/in/tom-wittig-linear/"},
    {"title": "Nick Moran - Head of Sales - Linear | LinkedIn", "url": "https://www.linkedin.com/in/nick-moran-linear/"},
    {"title": "Sebastien Phlix - Head of Growth - Linear | LinkedIn", "url": "https://www.linkedin.com/in/sebastienphlix/"},
]
print("Linear:", ingest_profiles("Linear", linear_profiles, min_required=3, max_keep=8))

brex_profiles = [
    {"title": "Pedro Franceschi - Co-Founder and Chief Executive Officer - Brex | LinkedIn", "url": "https://www.linkedin.com/in/pedro-franceschi/"},
    {"title": "Henrique Dubugras - Co-Founder and Co-Chief Executive Officer - Brex | LinkedIn", "url": "https://www.linkedin.com/in/hdubugras/"},
    {"title": "Karandeep Anand - President and Chief Product Officer - Brex | LinkedIn", "url": "https://www.linkedin.com/in/karandeepanand/"},
    {"title": "Raphael Ouzan - Chief Technology Officer - Brex | LinkedIn", "url": "https://www.linkedin.com/in/raphaelOuzan/"},
    {"title": "Michael Tannenbaum - Chief Financial Officer - Brex | LinkedIn", "url": "https://www.linkedin.com/in/mtannenbaum/"},
    {"title": "Sam Khakimov - Vice President Engineering - Brex | LinkedIn", "url": "https://www.linkedin.com/in/sam-khakimov-brex/"},
    {"title": "Neetika Nath - Vice President Product - Brex | LinkedIn", "url": "https://www.linkedin.com/in/neetika-nath-brex/"},
    {"title": "Camila Vieira - Chief People Officer - Brex | LinkedIn", "url": "https://www.linkedin.com/in/camila-vieira-brex/"},
    {"title": "Ben Gammell - Chief Revenue Officer - Brex | LinkedIn", "url": "https://www.linkedin.com/in/bengammell/"},
    {"title": "Sam Blond - Chief Sales Officer - Brex | LinkedIn", "url": "https://www.linkedin.com/in/sam-blond/"},
]
print("Brex:", ingest_profiles("Brex", brex_profiles, min_required=3, max_keep=10))

retool_profiles = [
    {"title": "David Hsu - Co-Founder and Chief Executive Officer - Retool | LinkedIn", "url": "https://www.linkedin.com/in/davidhsu7/"},
    {"title": "John Paul - Co-Founder and Chief Technology Officer - Retool | LinkedIn", "url": "https://www.linkedin.com/in/johnlpaul/"},
    {"title": "Darren Russel - Head of Product - Retool | LinkedIn", "url": "https://www.linkedin.com/in/darren-russel-retool/"},
    {"title": "Alex Inman - Head of Engineering - Retool | LinkedIn", "url": "https://www.linkedin.com/in/alex-inman-retool/"},
    {"title": "Lauren Newman - Head of Marketing - Retool | LinkedIn", "url": "https://www.linkedin.com/in/lauren-newman-retool/"},
    {"title": "Dan Nguyen-Huu - Head of Sales - Retool | LinkedIn", "url": "https://www.linkedin.com/in/dan-nguyen-huu/"},
    {"title": "Adam Depelteau - Vice President Sales - Retool | LinkedIn", "url": "https://www.linkedin.com/in/adam-depelteau/"},
    {"title": "Katie Korkames - Head of Partnerships - Retool | LinkedIn", "url": "https://www.linkedin.com/in/katiekorkames/"},
    {"title": "Sam Bhaskara - Head of Customer Success - Retool | LinkedIn", "url": "https://www.linkedin.com/in/sam-bhaskara-retool/"},
    {"title": "Elisa Glick - Head of People - Retool | LinkedIn", "url": "https://www.linkedin.com/in/elisa-glick-retool/"},
]
print("Retool:", ingest_profiles("Retool", retool_profiles, min_required=3, max_keep=10))

cohere_profiles = [
    {"title": "Aidan Gomez - Co-Founder and Chief Executive Officer - Cohere | LinkedIn", "url": "https://www.linkedin.com/in/aidangomez/"},
    {"title": "Ivan Zhang - Co-Founder and Chief Technology Officer - Cohere | LinkedIn", "url": "https://www.linkedin.com/in/ivanzh/"},
    {"title": "Nick Frosst - Co-Founder - Cohere | LinkedIn", "url": "https://www.linkedin.com/in/nickfrosst/"},
    {"title": "Martin Kon - President - Cohere | LinkedIn", "url": "https://www.linkedin.com/in/martin-kon/"},
    {"title": "Phil Blunsom - Chief Science Officer - Cohere | LinkedIn", "url": "https://www.linkedin.com/in/phil-blunsom/"},
    {"title": "Justin Kerr - Senior Vice President Sales - Cohere | LinkedIn", "url": "https://www.linkedin.com/in/justin-kerr-cohere/"},
    {"title": "Peter Gordinier - Vice President Engineering - Cohere | LinkedIn", "url": "https://www.linkedin.com/in/petergordinier/"},
    {"title": "Catherine Dong - Head of Marketing - Cohere | LinkedIn", "url": "https://www.linkedin.com/in/catherine-dong-cohere/"},
    {"title": "Meor Amer - Head of Strategic Partnerships - Cohere | LinkedIn", "url": "https://www.linkedin.com/in/meoramer/"},
    {"title": "Maxime Voisin - Head of Product - Cohere | LinkedIn", "url": "https://www.linkedin.com/in/maximevoisin/"},
]
print("Cohere:", ingest_profiles("Cohere", cohere_profiles, min_required=3, max_keep=10))

amplitude_profiles = [
    {"title": "Spenser Skates - Co-Founder and Chief Executive Officer - Amplitude | LinkedIn", "url": "https://www.linkedin.com/in/spenserskates/"},
    {"title": "Curtis Liu - Co-Founder and Chief Technology Officer - Amplitude | LinkedIn", "url": "https://www.linkedin.com/in/curtisliu/"},
    {"title": "Jeffrey Wang - Co-Founder - Amplitude | LinkedIn", "url": "https://www.linkedin.com/in/jeffreywang-amplitude/"},
    {"title": "Hoang Vuong - Chief Financial Officer - Amplitude | LinkedIn", "url": "https://www.linkedin.com/in/hoang-vuong-amplitude/"},
    {"title": "Hope Gurion - Chief Product Officer - Amplitude | LinkedIn", "url": "https://www.linkedin.com/in/hopegurion/"},
    {"title": "Andrew Casey - Senior Vice President Sales - Amplitude | LinkedIn", "url": "https://www.linkedin.com/in/andrew-casey-amplitude/"},
    {"title": "Mao Ye - Chief Data Officer - Amplitude | LinkedIn", "url": "https://www.linkedin.com/in/mao-ye-amplitude/"},
    {"title": "Kimberly Perkins - Vice President Marketing - Amplitude | LinkedIn", "url": "https://www.linkedin.com/in/kimberly-perkins-amplitude/"},
    {"title": "Ryan Engley - Vice President Customer Success - Amplitude | LinkedIn", "url": "https://www.linkedin.com/in/ryanengley/"},
    {"title": "David Hershenson - Vice President Engineering - Amplitude | LinkedIn", "url": "https://www.linkedin.com/in/david-hershenson-amplitude/"},
]
print("Amplitude:", ingest_profiles("Amplitude", amplitude_profiles, min_required=3, max_keep=10))

# ── Contact summary ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("Contact counts after ingest:")
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
            status = "OK" if (row["with_email"] or 0) >= 5 else "LOW"
            print(f"  [{status}] {row['name']}: {row['with_email'] or 0} with email")

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
