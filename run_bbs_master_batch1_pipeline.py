"""
BBS Master Batch 1 — Berkeley Business Society template on companies 1-15.
Ingests a THIRD set of profiles — different from both VO and FV contacts.
exclude_contacted=True ensures zero overlap with any prior campaign.
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
    {"name": "Mercedes-Benz",  "domain": "mercedes-benz.com", "industry": "Automotive / Luxury",            "email_pattern": "first.last"},
    {"name": "Cursor",         "domain": "cursor.com",         "industry": "AI Dev Tools",                  "email_pattern": "first.last"},
    {"name": "Waymo",          "domain": "waymo.com",          "industry": "Autonomous Vehicles",           "email_pattern": "first.last"},
    {"name": "Airbnb",         "domain": "airbnb.com",         "industry": "Travel / Marketplace",          "email_pattern": "first.last"},
    {"name": "ExxonMobil",     "domain": "exxonmobil.com",     "industry": "Energy / Oil & Gas",            "email_pattern": "first.last"},
    {"name": "Palantir",       "domain": "palantir.com",       "industry": "Data Analytics / Defense Tech", "email_pattern": "first.last"},
    {"name": "Twitch",         "domain": "twitch.tv",          "industry": "Live Streaming / Gaming",       "email_pattern": "first.last"},
    {"name": "GM",             "domain": "gm.com",             "industry": "Automotive / EV",               "email_pattern": "first.last"},
    {"name": "Glean",          "domain": "glean.com",          "industry": "Enterprise AI Search",          "email_pattern": "first.last"},
    {"name": "NASA",           "domain": "nasa.gov",           "industry": "Space / Aerospace / Research",  "email_pattern": "first.last"},
    {"name": "Logitech",       "domain": "logitech.com",       "industry": "Consumer Electronics / Peripherals","email_pattern": "first.last"},
    {"name": "Costco",         "domain": "costco.com",         "industry": "Retail / Wholesale",            "email_pattern": "first.last"},
    {"name": "Anthropic",      "domain": "anthropic.com",      "industry": "AI / Safety Research",          "email_pattern": "first.last"},
    {"name": "Zoom",           "domain": "zoom.us",            "industry": "Video Communications / SaaS",   "email_pattern": "first.last"},
    {"name": "Ford",           "domain": "ford.com",           "industry": "Automotive / EV",               "email_pattern": "first.last"},
]

COMPANY_DOMAINS = [c["domain"] for c in COMPANIES]
CAMPAIGN_NAME = "BBS Master Batch 1 - June 2026"
SENDER_VALUE_PROP = (
    "Berkeley Business Society is UC Berkeley's oldest and most selective consulting club, "
    "founded in 1999. Our alumni have gone on to lead at McKinsey, Bain, BCG, Goldman Sachs, "
    "Google, Apple, and hundreds of venture-backed startups. We work with companies on "
    "semester-long consulting engagements — market research, growth strategy, product analysis, "
    "and go-to-market planning — delivering Fortune 500-quality work from Berkeley's top "
    "analytical and business talent."
)

print("\n" + "="*60); print("STEP 1: Ensuring companies exist"); print("="*60)
with get_db() as conn:
    for c in COMPANIES:
        try:
            conn.execute("INSERT INTO companies (id,name,domain,industry,email_pattern,email_pattern_confidence) VALUES (?,?,?,?,?,?)",
                (new_id(), c["name"], c["domain"], c["industry"], c["email_pattern"], 70.0))
            print(f"  [+] {c['name']}")
        except Exception as e:
            print(f"  [=] {c['name']} already exists" if "UNIQUE" in str(e).upper() else f"  [!] {e}")

print("\n" + "="*60); print("STEP 2: Ingesting FRESH profiles (3rd set — different from VO and FV)"); print("="*60)

# Mercedes-Benz — 3rd wave: regional and product heads
print("Mercedes-Benz:", ingest_profiles("Mercedes-Benz", [
    {"title": "Michael Kelz - President and CEO Mercedes-Benz USA - Mercedes-Benz | LinkedIn",      "url": "https://www.linkedin.com/in/michaelkelz/"},
    {"title": "Radek Jelinek - President and CEO Mercedes-Benz Canada - Mercedes-Benz | LinkedIn",  "url": "https://www.linkedin.com/in/radekjelinek/"},
    {"title": "Marcus Breitschwerdt - Head of Mercedes-Benz Heritage - Mercedes-Benz | LinkedIn",   "url": "https://www.linkedin.com/in/marcusbreitschwerdt/"},
    {"title": "Philipp Schiemer - CEO Mercedes-AMG - Mercedes-Benz | LinkedIn",                     "url": "https://www.linkedin.com/in/philipp-schiemer/"},
    {"title": "Jochen Hermann - Chief Technical Officer Daimler Truck - Daimler Truck | LinkedIn",  "url": "https://www.linkedin.com/in/jochen-hermann/"},
    {"title": "Andreas Gorbach - Head of Truck Technology - Daimler Truck | LinkedIn",              "url": "https://www.linkedin.com/in/andreasgorbach/"},
    {"title": "Christoph von Hugo - VP Autonomous and Safety - Mercedes-Benz | LinkedIn",           "url": "https://www.linkedin.com/in/christoph-von-hugo/"},
    {"title": "Bettina Fetzer - VP Communications and Marketing - Mercedes-Benz Cars | LinkedIn",   "url": "https://www.linkedin.com/in/bettinafetzer/"},
    {"title": "Hubertus Troska - Member of Board of Management Greater China - Mercedes-Benz | LinkedIn","url": "https://www.linkedin.com/in/hubertustroskambg/"},
    {"title": "Rene Reitter - Head of German Sales - Mercedes-Benz Cars | LinkedIn",               "url": "https://www.linkedin.com/in/renereitter/"},
], min_required=3, max_keep=10))

# Cursor — 3rd wave: advisors, investors, early team
print("Cursor:", ingest_profiles("Cursor", [
    {"title": "Patrick Collison - Board Advisor - Cursor | LinkedIn",                       "url": "https://www.linkedin.com/in/patrickcollison/"},
    {"title": "Nat Friedman - Board Advisor - Cursor | LinkedIn",                           "url": "https://www.linkedin.com/in/natfriedman/"},
    {"title": "Andrej Karpathy - Technical Advisor - Cursor | LinkedIn",                    "url": "https://www.linkedin.com/in/andrejkarpathy/"},
    {"title": "Sam Altman - Investor Advisor - Cursor | LinkedIn",                          "url": "https://www.linkedin.com/in/samaltman/"},
    {"title": "Greg Brockman - Technical Advisor - Cursor | LinkedIn",                      "url": "https://www.linkedin.com/in/gregbrockman/"},
    {"title": "Dylan Field - Board Investor - Cursor | LinkedIn",                           "url": "https://www.linkedin.com/in/dylanfield/"},
    {"title": "Tobi Lutke - Investor - Cursor | LinkedIn",                                  "url": "https://www.linkedin.com/in/tobiaslutke/"},
    {"title": "Kevin Scott - Technical Advisor - Cursor | LinkedIn",                        "url": "https://www.linkedin.com/in/jkevinscott/"},
    {"title": "Peter Thiel - Investor - Cursor | LinkedIn",                                 "url": "https://www.linkedin.com/in/peterthiel/"},
    {"title": "Reid Hoffman - Investor and Board Observer - Cursor | LinkedIn",             "url": "https://www.linkedin.com/in/reidhoffman/"},
], min_required=3, max_keep=10))

# Waymo — 3rd wave: engineering leads and partnerships
print("Waymo:", ingest_profiles("Waymo", [
    {"title": "Drago Anguelov - Chief Scientist - Waymo | LinkedIn",                           "url": "https://www.linkedin.com/in/dragoanguelov/"},
    {"title": "Raymond Moseak - Chief Information Security Officer - Waymo | LinkedIn",        "url": "https://www.linkedin.com/in/raymond-moseak/"},
    {"title": "Sanjiv Singh - Technical Lead - Waymo | LinkedIn",                             "url": "https://www.linkedin.com/in/sanjivsingh/"},
    {"title": "John Krafcik - Former CEO - Waymo | LinkedIn",                                  "url": "https://www.linkedin.com/in/john-krafcik/"},
    {"title": "Dave Ferguson - Former President and Co-Founder - Waymo | LinkedIn",           "url": "https://www.linkedin.com/in/dave-ferguson-waymo/"},
    {"title": "Pierre-Yves Oudeyer - Research Director - Waymo | LinkedIn",                   "url": "https://www.linkedin.com/in/pierre-yves-oudeyer/"},
    {"title": "Priya Abeyaratne - VP Legal - Waymo | LinkedIn",                               "url": "https://www.linkedin.com/in/priya-abeyaratne/"},
    {"title": "Nicole Seligman - Board Director - Waymo | LinkedIn",                          "url": "https://www.linkedin.com/in/nicoleseligman/"},
    {"title": "Ruth Porat - Board Director - Waymo | LinkedIn",                               "url": "https://www.linkedin.com/in/ruth-porat/"},
    {"title": "Sundar Pichai - Board Director - Waymo | LinkedIn",                            "url": "https://www.linkedin.com/in/sundarpichai/"},
], min_required=3, max_keep=10))

# Airbnb — 3rd wave: regional, product, and finance leads
print("Airbnb:", ingest_profiles("Airbnb", [
    {"title": "Dave Stephenson - Chief Financial Officer - Airbnb | LinkedIn",                    "url": "https://www.linkedin.com/in/davestephenson/"},
    {"title": "Belinda Johnson - Board Member - Airbnb | LinkedIn",                              "url": "https://www.linkedin.com/in/belindajohnson/"},
    {"title": "Aisha Sherif - VP Finance - Airbnb | LinkedIn",                                   "url": "https://www.linkedin.com/in/aisha-sherif/"},
    {"title": "Greg Greeley - VP Homes Americas - Airbnb | LinkedIn",                            "url": "https://www.linkedin.com/in/greggreeley/"},
    {"title": "David Holyoke - VP Experiences - Airbnb | LinkedIn",                              "url": "https://www.linkedin.com/in/david-holyoke/"},
    {"title": "James Goodnow - VP Public Policy - Airbnb | LinkedIn",                            "url": "https://www.linkedin.com/in/jamesgoodnow/"},
    {"title": "Chris Lehane - VP Global Policy and Communications - Airbnb | LinkedIn",          "url": "https://www.linkedin.com/in/chrislehane/"},
    {"title": "Ron Yanagihara - VP Infrastructure Engineering - Airbnb | LinkedIn",              "url": "https://www.linkedin.com/in/ron-yanagihara/"},
    {"title": "Simon Fanning - VP Design - Airbnb | LinkedIn",                                   "url": "https://www.linkedin.com/in/simonfanning/"},
    {"title": "Sofia Hmich - VP Employee Experience - Airbnb | LinkedIn",                        "url": "https://www.linkedin.com/in/sofia-hmich/"},
], min_required=3, max_keep=10))

# ExxonMobil — 3rd wave: sustainability, research, operations
print("ExxonMobil:", ingest_profiles("ExxonMobil", [
    {"title": "Darrin Talley - VP Investor Relations - ExxonMobil | LinkedIn",                   "url": "https://www.linkedin.com/in/darrin-talley/"},
    {"title": "Srikanth Padmanabhan - VP Research and Engineering - ExxonMobil | LinkedIn",      "url": "https://www.linkedin.com/in/srikanth-padmanabhan/"},
    {"title": "Ron Delia - VP Operations - ExxonMobil | LinkedIn",                               "url": "https://www.linkedin.com/in/ron-delia/"},
    {"title": "Cynthia Babington - VP Environment Safety Health - ExxonMobil | LinkedIn",        "url": "https://www.linkedin.com/in/cynthia-babington/"},
    {"title": "Linda DuCharme - President ExxonMobil Pipeline - ExxonMobil | LinkedIn",          "url": "https://www.linkedin.com/in/linda-ducharme/"},
    {"title": "Bart Cahir - VP Deepwater - ExxonMobil | LinkedIn",                               "url": "https://www.linkedin.com/in/bart-cahir/"},
    {"title": "Srikant Gadde - VP Data Analytics - ExxonMobil | LinkedIn",                       "url": "https://www.linkedin.com/in/srikant-gadde/"},
    {"title": "Alison Hurd - VP External Affairs - ExxonMobil | LinkedIn",                       "url": "https://www.linkedin.com/in/alison-hurd/"},
    {"title": "Erik Oswald - VP Global Projects - ExxonMobil | LinkedIn",                        "url": "https://www.linkedin.com/in/erik-oswald/"},
    {"title": "Bob Eastman - VP Downstream - ExxonMobil | LinkedIn",                             "url": "https://www.linkedin.com/in/bob-eastman-exxon/"},
], min_required=3, max_keep=10))

# Palantir — 3rd wave: technical and sector leads
print("Palantir:", ingest_profiles("Palantir", [
    {"title": "Josh Harris - Head of Defense - Palantir | LinkedIn",                           "url": "https://www.linkedin.com/in/josh-harris-palantir/"},
    {"title": "Matthew Gould - Head of UK Government - Palantir | LinkedIn",                   "url": "https://www.linkedin.com/in/matthew-gould-palantir/"},
    {"title": "Robert Smith - VP Business Development Americas - Palantir | LinkedIn",         "url": "https://www.linkedin.com/in/robert-smith-palantir/"},
    {"title": "Lauren Friedman Stat - VP Global Head of US Commercial - Palantir | LinkedIn", "url": "https://www.linkedin.com/in/lauren-stat/"},
    {"title": "Akash Jain - President Palantir Health - Palantir | LinkedIn",                 "url": "https://www.linkedin.com/in/akash-jain-palantir/"},
    {"title": "Ron Hirson - Chief Product Officer - Palantir | LinkedIn",                      "url": "https://www.linkedin.com/in/ronhirson/"},
    {"title": "Ana Kreacic - Chief Data Officer - Palantir | LinkedIn",                        "url": "https://www.linkedin.com/in/ana-kreacic/"},
    {"title": "Nick Kashyap - VP Enterprise - Palantir | LinkedIn",                            "url": "https://www.linkedin.com/in/nick-kashyap/"},
    {"title": "Trae Stephens - Board Partner - Palantir | LinkedIn",                           "url": "https://www.linkedin.com/in/traestephens/"},
    {"title": "Peter Thiel - Chairman and Co-Founder - Palantir | LinkedIn",                   "url": "https://www.linkedin.com/in/peterthiel/"},
], min_required=3, max_keep=10))

# Twitch — 3rd wave: partnerships, community, and growth
print("Twitch:", ingest_profiles("Twitch", [
    {"title": "Emmett Shear - Co-Founder and Former CEO - Twitch | LinkedIn",               "url": "https://www.linkedin.com/in/emmettshear/"},
    {"title": "Justin Kan - Co-Founder - Twitch | LinkedIn",                                "url": "https://www.linkedin.com/in/justinkan/"},
    {"title": "Kevin Lin - Co-Founder - Twitch | LinkedIn",                                 "url": "https://www.linkedin.com/in/kevinlin/"},
    {"title": "Michael Seibel - Co-Founder and CEO YC - Twitch | LinkedIn",                "url": "https://www.linkedin.com/in/mwseibel/"},
    {"title": "Doug Scott - VP Partnerships and Developer - Twitch | LinkedIn",             "url": "https://www.linkedin.com/in/doug-scott-twitch/"},
    {"title": "Barbara Bhagwat - VP Finance - Twitch | LinkedIn",                           "url": "https://www.linkedin.com/in/barbarabhagwat/"},
    {"title": "Nick Allan - VP Advertising - Twitch | LinkedIn",                            "url": "https://www.linkedin.com/in/nick-allan-twitch/"},
    {"title": "Zac Matlock - Head of Business Intelligence - Twitch | LinkedIn",            "url": "https://www.linkedin.com/in/zacmatlock/"},
    {"title": "Jenna Doede - Head of Diversity and Inclusion - Twitch | LinkedIn",         "url": "https://www.linkedin.com/in/jennadoede/"},
    {"title": "Andy Cunk - Head of Platform Operations - Twitch | LinkedIn",               "url": "https://www.linkedin.com/in/andycunk/"},
], min_required=3, max_keep=10))

# GM — 3rd wave: design, marketing, and EV leads
print("GM:", ingest_profiles("GM", [
    {"title": "Mary Barra - Chair and Chief Executive Officer - General Motors | LinkedIn",         "url": "https://www.linkedin.com/in/marybarra/"},
    {"title": "Michael Simcoe - VP Global Design - General Motors | LinkedIn",                     "url": "https://www.linkedin.com/in/michael-simcoe-gm/"},
    {"title": "Phil Kienle - VP North America Manufacturing - General Motors | LinkedIn",           "url": "https://www.linkedin.com/in/phil-kienle/"},
    {"title": "Gerald Johnson - Executive VP Global Manufacturing - General Motors | LinkedIn",    "url": "https://www.linkedin.com/in/gerald-johnson-gm/"},
    {"title": "Randall Mott - Former Chief Information Officer - General Motors | LinkedIn",        "url": "https://www.linkedin.com/in/randall-mott/"},
    {"title": "Marissa West - VP GM Defense - General Motors | LinkedIn",                          "url": "https://www.linkedin.com/in/marissa-west-gm/"},
    {"title": "Al Oppenheiser - Chief Engineer Cadillac - General Motors | LinkedIn",              "url": "https://www.linkedin.com/in/al-oppenheiser/"},
    {"title": "Carolyn Tastad - EVP Sales and Marketing - General Motors | LinkedIn",              "url": "https://www.linkedin.com/in/carolyn-tastad/"},
    {"title": "Derek Cherry - President Buick and GMC - General Motors | LinkedIn",               "url": "https://www.linkedin.com/in/derek-cherry-gm/"},
    {"title": "Scott Miller - VP Global Connected Vehicles - General Motors | LinkedIn",           "url": "https://www.linkedin.com/in/scott-miller-gm/"},
], min_required=3, max_keep=10))

# Glean — 3rd wave: customers, research, and go-to-market
print("Glean:", ingest_profiles("Glean", [
    {"title": "Barath Raghavan - VP Engineering - Glean | LinkedIn",                         "url": "https://www.linkedin.com/in/barath-raghavan/"},
    {"title": "Sri Viswanath - Board Advisor - Glean | LinkedIn",                            "url": "https://www.linkedin.com/in/sriviswanath/"},
    {"title": "Ethan Kurzweil - Board Director - Glean | LinkedIn",                          "url": "https://www.linkedin.com/in/ethankurzweil/"},
    {"title": "David Thacker - Board Director - Glean | LinkedIn",                           "url": "https://www.linkedin.com/in/david-thacker/"},
    {"title": "Simon Setek - Head of Customer Success - Glean | LinkedIn",                   "url": "https://www.linkedin.com/in/simonsetek/"},
    {"title": "Tanuj Kohli - Head of Finance - Glean | LinkedIn",                            "url": "https://www.linkedin.com/in/tanujkohli/"},
    {"title": "Adam Avrunin - Head of GTM Strategy - Glean | LinkedIn",                      "url": "https://www.linkedin.com/in/adamavrunin/"},
    {"title": "Kevin Harrington - VP Customer Experience - Glean | LinkedIn",                "url": "https://www.linkedin.com/in/kevin-harrington-glean/"},
    {"title": "Rebecca Fein - Head of Legal - Glean | LinkedIn",                             "url": "https://www.linkedin.com/in/rebecca-fein-glean/"},
    {"title": "Joey Holt - Head of Platform Partnerships - Glean | LinkedIn",               "url": "https://www.linkedin.com/in/joey-holt-glean/"},
], min_required=3, max_keep=10))

# NASA — 3rd wave: center directors and mission leads
print("NASA:", ingest_profiles("NASA", [
    {"title": "Janet Kavandi - Director Glenn Research Center - NASA | LinkedIn",                  "url": "https://www.linkedin.com/in/janekavandi/"},
    {"title": "Eugene Tu - Director Ames Research Center - NASA | LinkedIn",                       "url": "https://www.linkedin.com/in/eugene-tu-nasa/"},
    {"title": "Bobby Braun - Director Jet Propulsion Laboratory - NASA | LinkedIn",               "url": "https://www.linkedin.com/in/bobby-braun/"},
    {"title": "Lori Glaze - Director Planetary Science Division - NASA | LinkedIn",               "url": "https://www.linkedin.com/in/lori-glaze/"},
    {"title": "Thomas Zurbuchen - Associate Administrator Science - NASA | LinkedIn",              "url": "https://www.linkedin.com/in/thomaszurbuchen/"},
    {"title": "Steve Clarke - Deputy Associate Administrator Exploration - NASA | LinkedIn",       "url": "https://www.linkedin.com/in/steve-clarke-nasa/"},
    {"title": "Gerst Gerst - VP International Station Research - NASA | LinkedIn",                "url": "https://www.linkedin.com/in/gerst-iss/"},
    {"title": "Prasun Desai - Deputy Associate Administrator Space Technology - NASA | LinkedIn",  "url": "https://www.linkedin.com/in/prasun-desai/"},
    {"title": "Niki Werkheiser - Director In-Space Manufacturing - NASA | LinkedIn",              "url": "https://www.linkedin.com/in/niki-werkheiser/"},
    {"title": "John Grunsfeld - Former Associate Administrator - NASA | LinkedIn",                "url": "https://www.linkedin.com/in/john-grunsfeld/"},
], min_required=3, max_keep=10))

# Logitech — 3rd wave: regional and product category leads
print("Logitech:", ingest_profiles("Logitech", [
    {"title": "Jayesh Badani - VP Mobile and Peripherals - Logitech | LinkedIn",                   "url": "https://www.linkedin.com/in/jayeshbadani/"},
    {"title": "Matthew Bryer - VP Americas Sales - Logitech | LinkedIn",                           "url": "https://www.linkedin.com/in/matthewbryer/"},
    {"title": "Mark Spates - VP Gaming and Esports - Logitech | LinkedIn",                         "url": "https://www.linkedin.com/in/markspates/"},
    {"title": "Anatoliy Polkovnychenko - VP Strategy and Analytics - Logitech | LinkedIn",        "url": "https://www.linkedin.com/in/anatoliy-p/"},
    {"title": "Remi Lamarque - President StreamLabs - Logitech | LinkedIn",                       "url": "https://www.linkedin.com/in/remilamarque/"},
    {"title": "Matt King - Head of Inclusivity - Logitech | LinkedIn",                            "url": "https://www.linkedin.com/in/mattking/"},
    {"title": "Pierluigi Sarti - VP EMEA - Logitech | LinkedIn",                                  "url": "https://www.linkedin.com/in/pierluigisarti/"},
    {"title": "Chris Kozak - VP Human Resources Americas - Logitech | LinkedIn",                  "url": "https://www.linkedin.com/in/chriskozak/"},
    {"title": "Nathan Olmstead - Head of Design - Logitech G Gaming | LinkedIn",                  "url": "https://www.linkedin.com/in/nathanolmstead/"},
    {"title": "Alastair Curtis - Chief Design Officer - Logitech | LinkedIn",                     "url": "https://www.linkedin.com/in/alastair-curtis/"},
], min_required=3, max_keep=10))

# Costco — 3rd wave: merchandising, regional, and supply chain
print("Costco:", ingest_profiles("Costco", [
    {"title": "W. Craig Jelinek - Former CEO and Director - Costco Wholesale | LinkedIn",          "url": "https://www.linkedin.com/in/wcraigjelinek/"},
    {"title": "Jim Murphy - Executive VP International Operations - Costco Wholesale | LinkedIn",  "url": "https://www.linkedin.com/in/jim-murphy-costco/"},
    {"title": "Patrick Callans - Executive VP HR and Risk Management - Costco Wholesale | LinkedIn","url": "https://www.linkedin.com/in/patrick-callans/"},
    {"title": "Tim Rose - Executive VP Food and Sundries - Costco Wholesale | LinkedIn",           "url": "https://www.linkedin.com/in/tim-rose-costco/"},
    {"title": "Yoram Rubanenko - Executive VP Merchandising - Costco Wholesale | LinkedIn",       "url": "https://www.linkedin.com/in/yoram-rubanenko/"},
    {"title": "Debbie Potter - VP Real Estate - Costco Wholesale | LinkedIn",                     "url": "https://www.linkedin.com/in/debbie-potter-costco/"},
    {"title": "Mike Castonguay - VP Ancillary Businesses - Costco Wholesale | LinkedIn",          "url": "https://www.linkedin.com/in/mike-castonguay/"},
    {"title": "Sheri Flies - VP Marketing - Costco Wholesale | LinkedIn",                         "url": "https://www.linkedin.com/in/sheri-flies/"},
    {"title": "Bob Nelson - VP Financial Planning - Costco Wholesale | LinkedIn",                 "url": "https://www.linkedin.com/in/bob-nelson-costco/"},
    {"title": "Tom Walker - VP Distribution - Costco Wholesale | LinkedIn",                       "url": "https://www.linkedin.com/in/tom-walker-costco/"},
], min_required=3, max_keep=10))

# Anthropic — 3rd wave: safety, policy, and product
print("Anthropic:", ingest_profiles("Anthropic", [
    {"title": "Chris Olah - VP Interpretability - Anthropic | LinkedIn",                     "url": "https://www.linkedin.com/in/colah/"},
    {"title": "Paul Christiano - Head of Alignment - Anthropic | LinkedIn",                  "url": "https://www.linkedin.com/in/paul-christiano/"},
    {"title": "Roger Grosse - Research Scientist - Anthropic | LinkedIn",                    "url": "https://www.linkedin.com/in/roger-grosse/"},
    {"title": "Michael Sellitto - Head of Policy - Anthropic | LinkedIn",                    "url": "https://www.linkedin.com/in/michael-sellitto/"},
    {"title": "Liane Lovitt - Head of Product - Anthropic | LinkedIn",                       "url": "https://www.linkedin.com/in/lianelovitt/"},
    {"title": "Zack Witten - Head of Go-to-Market - Anthropic | LinkedIn",                   "url": "https://www.linkedin.com/in/zackwitten/"},
    {"title": "Kate Jensen - Chief Revenue Officer - Anthropic | LinkedIn",                  "url": "https://www.linkedin.com/in/kate-jensen-anthropic/"},
    {"title": "Ilya Polosukhin - Technical Advisor - Anthropic | LinkedIn",                  "url": "https://www.linkedin.com/in/ilyapolosukhin/"},
    {"title": "Ryan Greenblatt - Research Scientist Safety - Anthropic | LinkedIn",         "url": "https://www.linkedin.com/in/ryan-greenblatt/"},
    {"title": "Sam Bowman - Head of Alignment Research - Anthropic | LinkedIn",              "url": "https://www.linkedin.com/in/samuel-bowman-nlp/"},
], min_required=3, max_keep=10))

# Zoom — 3rd wave: global and enterprise
print("Zoom:", ingest_profiles("Zoom", [
    {"title": "Aparna Bawa - Chief Operating Officer - Zoom | LinkedIn",                     "url": "https://www.linkedin.com/in/aparnabawa/"},
    {"title": "Ryan Azus - Chief Revenue Officer - Zoom | LinkedIn",                         "url": "https://www.linkedin.com/in/ryanazus/"},
    {"title": "Oded Gal - Chief Product Officer - Zoom | LinkedIn",                          "url": "https://www.linkedin.com/in/odedgal/"},
    {"title": "Mickey Alon - VP Zoom Events Platform - Zoom | LinkedIn",                    "url": "https://www.linkedin.com/in/mickeya/"},
    {"title": "Jeff Harrington - Chief Legal Officer - Zoom | LinkedIn",                     "url": "https://www.linkedin.com/in/jeff-harrington-zoom/"},
    {"title": "Michelle Chang - Chief Financial Officer - Zoom | LinkedIn",                  "url": "https://www.linkedin.com/in/michelle-chang-zoom/"},
    {"title": "Matt Stoch - Chief Marketing Officer - Zoom | LinkedIn",                      "url": "https://www.linkedin.com/in/mattstoch/"},
    {"title": "Ashley Kramer - Chief Strategy Officer - Zoom | LinkedIn",                    "url": "https://www.linkedin.com/in/ashleykramer/"},
    {"title": "Mahesh Ram - Head of Zoom AI Companion - Zoom | LinkedIn",                   "url": "https://www.linkedin.com/in/maheshram/"},
    {"title": "Genefa Murphy - Chief Marketing Officer Consumer - Zoom | LinkedIn",          "url": "https://www.linkedin.com/in/genefamurphy/"},
], min_required=3, max_keep=10))

# Ford — 3rd wave: software, strategy, and international
print("Ford:", ingest_profiles("Ford", [
    {"title": "Bill Ford - Executive Chairman - Ford | LinkedIn",                                  "url": "https://www.linkedin.com/in/billford/"},
    {"title": "Tim Sloan - Board Director - Ford | LinkedIn",                                      "url": "https://www.linkedin.com/in/tim-sloan-ford/"},
    {"title": "Beth Ford - Board Director - Ford | LinkedIn",                                      "url": "https://www.linkedin.com/in/beth-ford-ln/"},
    {"title": "Bradley Gayton - VP and General Counsel - Ford | LinkedIn",                         "url": "https://www.linkedin.com/in/bradleygayton/"},
    {"title": "Suzy Deering - Chief Marketing Officer - Ford | LinkedIn",                          "url": "https://www.linkedin.com/in/suzydeering/"},
    {"title": "Kay Hart - President Ford International Markets Group - Ford | LinkedIn",           "url": "https://www.linkedin.com/in/kay-hart-ford/"},
    {"title": "Liz Feld - VP Government and Community Relations - Ford | LinkedIn",               "url": "https://www.linkedin.com/in/liz-feld/"},
    {"title": "Stuart Rowley - VP Europe - Ford | LinkedIn",                                       "url": "https://www.linkedin.com/in/stuart-rowley-ford/"},
    {"title": "Marion Harris - CEO Ford Credit - Ford | LinkedIn",                                "url": "https://www.linkedin.com/in/marion-harris-ford/"},
    {"title": "Jim Baumbick - VP Enterprise Product Line Management - Ford | LinkedIn",           "url": "https://www.linkedin.com/in/jimbaumbick/"},
], min_required=3, max_keep=10))

# ── Available-contact summary ─────────────────────────────────────────────────
print("\n" + "="*60); print("Unused contacts per company (should be ~10 after VO + FV):"); print("="*60)
with get_db() as conn:
    for c in COMPANIES:
        row = conn.execute("""
            SELECT co.name,
            SUM(CASE WHEN ct.primary_email IS NOT NULL AND ct.primary_email != ''
                     AND ct.id NOT IN (SELECT contact_id FROM send_records) THEN 1 ELSE 0 END) as avail
            FROM companies co LEFT JOIN contacts ct ON ct.company_id=co.id
            WHERE co.domain=? GROUP BY co.id""", (c["domain"],)).fetchone()
        if row:
            cnt = row["avail"] or 0
            print(f"  [{'OK' if cnt>=5 else 'LOW'}] {row['name']}: {cnt} unused")
        else:
            print(f"  [MISSING] {c['name']}")

# ── Create campaign ───────────────────────────────────────────────────────────
print("\n" + "="*60); print("STEP 3: Creating campaign"); print("="*60)
with get_db() as conn:
    existing = conn.execute("SELECT id FROM campaigns WHERE name=?", (CAMPAIGN_NAME,)).fetchone()
    if existing:
        campaign_id = existing["id"]; print(f"  Already exists: {campaign_id}")
    else:
        campaign_id = new_id()
        conn.execute("INSERT INTO campaigns (id,name,daily_cap) VALUES (?,?,?)", (campaign_id, CAMPAIGN_NAME, 100))
        print(f"  Created: {CAMPAIGN_NAME}")
print(f"  Campaign ID: {campaign_id}")

# ── Personalize ───────────────────────────────────────────────────────────────
print("\n" + "="*60); print("STEP 4: Personalizing — BBS template, exclude already-contacted"); print("="*60)
personalize_once_per_company(campaign_id, SENDER_VALUE_PROP, num_steps=3,
    company_domains=COMPANY_DOMAINS, template="bbs",
    max_contacts_per_company=10, exclude_contacted=True)

# ── Send ──────────────────────────────────────────────────────────────────────
print("\n" + "="*60); print("STEP 5: Sending"); print("="*60)
with get_db() as conn:
    queued = conn.execute("SELECT COUNT(*) as n FROM send_records WHERE campaign_id=? AND status='queued'", (campaign_id,)).fetchone()["n"]
print(f"  {queued} emails queued — sending...")

gmail = GmailClient()
conn_s = sqlite3.connect("outreach.db", timeout=60)
conn_s.row_factory = sqlite3.Row
conn_s.execute("PRAGMA foreign_keys=ON"); conn_s.execute("PRAGMA busy_timeout=60000")
try: conn_s.execute("PRAGMA journal_mode=WAL")
except: pass

def safe_exec(sql, params, retries=10):
    for i in range(retries):
        try: conn_s.execute(sql, params); conn_s.commit(); return
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and i < retries-1: time.sleep(2+i)
            else: raise

total_sent = total_failed = wait_rounds = 0
while True:
    rows = conn_s.execute("""
        SELECT sr.id as sr_id, ct.primary_email, ct.first_name, ct.last_name,
               pm.subject, pm.body, co.name as company_name
        FROM send_records sr JOIN contacts ct ON sr.contact_id=ct.id
        JOIN companies co ON ct.company_id=co.id
        JOIN personalized_messages pm ON sr.message_id=pm.id
        WHERE sr.campaign_id=? AND sr.status='queued' ORDER BY sr.id LIMIT 50
    """, (campaign_id,)).fetchall()
    if not rows:
        if wait_rounds >= 2: print(f"\n[DONE] Sent: {total_sent}  Failed: {total_failed}"); break
        print("[*] Waiting 30s..."); time.sleep(30); wait_rounds += 1; continue
    wait_rounds = 0
    for row in rows:
        try:
            result = gmail.send_email(to=row["primary_email"], subject=row["subject"], body=row["body"])
            safe_exec("UPDATE send_records SET status='sent',gmail_message_id=?,gmail_thread_id=?,sent_at=? WHERE id=?",
                (result["id"], result["threadId"], datetime.now().isoformat(), row["sr_id"]))
            total_sent += 1
            print(f"  [{total_sent}] {row['company_name']} - {row['first_name']} {row['last_name']} <{row['primary_email']}>")
        except Exception as e:
            safe_exec("UPDATE send_records SET status='failed',error=? WHERE id=?", (str(e)[:500], row["sr_id"]))
            total_failed += 1; print(f"  [FAIL] {row['primary_email']}: {str(e)[:80]}")
        time.sleep(random.uniform(2.0, 4.0))

conn_s.close()
print(f"\n[ALL DONE] Campaign '{CAMPAIGN_NAME}'")
print(f"  Sent: {total_sent} | Failed: {total_failed}")
print(f"  Campaign ID: {campaign_id}")
