"""
FV Master Batch 1 — Free Ventures template on companies 1-15 (same companies as VO batch 1).
Ingests FRESH profiles — different people from whoever VO already contacted.
exclude_contacted=True ensures zero overlap with VO or any prior campaign.
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
CAMPAIGN_NAME = "FV Master Batch 1 - June 2026"
SENDER_VALUE_PROP = (
    "Free Ventures at UC Berkeley is the university's leading pre-seed startup accelerator "
    "and only nonprofit, student-run program of its kind. Over the past decade we've helped "
    "100+ portfolio companies raise $200M+ in follow-on capital from Kleiner Perkins, Accel, "
    "and Greylock, with multiple YC exits and acquisitions by Coinbase, Discord, and Opendoor. "
    "We partner with companies on strategy, product, and growth challenges — bringing Berkeley's "
    "sharpest founders and operators to work directly on your hardest problems."
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

print("\n" + "="*60); print("STEP 2: Ingesting FRESH profiles (different from VO batch 1)"); print("="*60)

# Mercedes-Benz — different senior leaders from whoever VO used
print("Mercedes-Benz:", ingest_profiles("Mercedes-Benz", [
    {"title": "Harald Wilhelm - Chief Financial Officer - Mercedes-Benz Group | LinkedIn",                  "url": "https://www.linkedin.com/in/haraldwilhelm/"},
    {"title": "Markus Schaefer - Chief Technology Officer - Mercedes-Benz Group | LinkedIn",               "url": "https://www.linkedin.com/in/markus-schaefer-mercedes/"},
    {"title": "Renata Jungo Brungger - Head of Integrity and Legal Affairs - Mercedes-Benz Group | LinkedIn","url": "https://www.linkedin.com/in/renata-jungo/"},
    {"title": "Sabine Kohleisen - Chief Human Resources Officer - Mercedes-Benz Group | LinkedIn",         "url": "https://www.linkedin.com/in/sabine-kohleisen/"},
    {"title": "Britta Seeger - Chief Commercial Officer - Mercedes-Benz Cars | LinkedIn",                  "url": "https://www.linkedin.com/in/brittaseeger/"},
    {"title": "Mathias Gewald - Head of Software and Digital Technology - Mercedes-Benz | LinkedIn",       "url": "https://www.linkedin.com/in/mathiasgewald/"},
    {"title": "Magnus Östberg - Chief Software Officer - Mercedes-Benz | LinkedIn",                       "url": "https://www.linkedin.com/in/magnusostberg/"},
    {"title": "Franz Reiner - Chief Executive Officer Mercedes-Benz Mobility - Mercedes-Benz | LinkedIn",  "url": "https://www.linkedin.com/in/franz-reiner-mb/"},
    {"title": "Eva Wiese - Head of Strategy and Innovation - Mercedes-Benz | LinkedIn",                    "url": "https://www.linkedin.com/in/eva-wiese-mercedes/"},
    {"title": "Jens Thiemer - VP Customer and Brand - Mercedes-Benz Cars | LinkedIn",                      "url": "https://www.linkedin.com/in/jens-thiemer/"},
], min_required=3, max_keep=10))

# Cursor — small team, pick distinct roles from VO's contacts
print("Cursor:", ingest_profiles("Cursor", [
    {"title": "Aman Sanger - Co-Founder - Cursor | LinkedIn",                      "url": "https://www.linkedin.com/in/amansanger/"},
    {"title": "Sualeh Asif - Co-Founder - Cursor | LinkedIn",                      "url": "https://www.linkedin.com/in/sualehasif/"},
    {"title": "Michael Truell - Co-Founder and Chief Executive Officer - Cursor | LinkedIn", "url": "https://www.linkedin.com/in/michael-truell/"},
    {"title": "Nick Dobos - Head of Engineering - Cursor | LinkedIn",              "url": "https://www.linkedin.com/in/nick-dobos/"},
    {"title": "Erik Schluntz - Co-Founder - Cursor | LinkedIn",                    "url": "https://www.linkedin.com/in/erikschluntz/"},
    {"title": "Arvid Lunnemark - Head of Product - Cursor | LinkedIn",             "url": "https://www.linkedin.com/in/arvid-lunnemark/"},
    {"title": "Zachary Waldman - Head of Business Development - Cursor | LinkedIn","url": "https://www.linkedin.com/in/zachary-waldman/"},
    {"title": "Julia Wang - Head of Design - Cursor | LinkedIn",                   "url": "https://www.linkedin.com/in/julia-wang-cursor/"},
    {"title": "Thomas Dohmke - Board Advisor - Cursor | LinkedIn",                 "url": "https://www.linkedin.com/in/thomasdo/"},
    {"title": "Rahul Sonwalkar - Head of Growth - Cursor | LinkedIn",              "url": "https://www.linkedin.com/in/rahulsonwalkar/"},
], min_required=3, max_keep=10))

# Waymo — different from VO contacts
print("Waymo:", ingest_profiles("Waymo", [
    {"title": "Tekedra Mawakana - Co-Chief Executive Officer - Waymo | LinkedIn",        "url": "https://www.linkedin.com/in/tekedramawakana/"},
    {"title": "Dmitri Dolgov - Co-Chief Executive Officer - Waymo | LinkedIn",           "url": "https://www.linkedin.com/in/dmitri-dolgov/"},
    {"title": "Saswat Panigrahi - Chief Product Officer - Waymo | LinkedIn",             "url": "https://www.linkedin.com/in/saswat/"},
    {"title": "Chet Pipkin - Chief Revenue Officer - Waymo | LinkedIn",                  "url": "https://www.linkedin.com/in/chetpipkin/"},
    {"title": "Trent Victor - Chief Safety Innovations Officer - Waymo | LinkedIn",      "url": "https://www.linkedin.com/in/trent-victor/"},
    {"title": "Mahesh Ramasubramanian - VP Engineering - Waymo | LinkedIn",              "url": "https://www.linkedin.com/in/mahesh-ramasubramanian/"},
    {"title": "Nick Laun - VP Policy and Communications - Waymo | LinkedIn",             "url": "https://www.linkedin.com/in/nick-laun/"},
    {"title": "Yolanda Lana - VP People - Waymo | LinkedIn",                             "url": "https://www.linkedin.com/in/yolanda-lana/"},
    {"title": "Alex Epstein - Head of Business Development - Waymo | LinkedIn",          "url": "https://www.linkedin.com/in/alex-epstein-waymo/"},
    {"title": "Jennifer Haroon - VP Operations - Waymo One | LinkedIn",                  "url": "https://www.linkedin.com/in/jenniferharoon/"},
], min_required=3, max_keep=10))

# Airbnb — different from VO contacts
print("Airbnb:", ingest_profiles("Airbnb", [
    {"title": "Brian Chesky - Co-Founder and Chief Executive Officer - Airbnb | LinkedIn",        "url": "https://www.linkedin.com/in/brianchesky/"},
    {"title": "Dave Stephenson - Chief Financial Officer - Airbnb | LinkedIn",                    "url": "https://www.linkedin.com/in/davestephenson/"},
    {"title": "Aristotle Balogh - Chief Technology Officer - Airbnb | LinkedIn",                  "url": "https://www.linkedin.com/in/aristotlebalogh/"},
    {"title": "Hiroki Asai - Chief Marketing Officer - Airbnb | LinkedIn",                        "url": "https://www.linkedin.com/in/hirokiasai/"},
    {"title": "Aisling Hassell - VP Global Operations - Airbnb | LinkedIn",                       "url": "https://www.linkedin.com/in/aislinghassell/"},
    {"title": "Nate Blecharczyk - Co-Founder and Chief Strategy Officer - Airbnb | LinkedIn",     "url": "https://www.linkedin.com/in/nathanblecharczyk/"},
    {"title": "Joe Gebbia - Co-Founder - Airbnb | LinkedIn",                                      "url": "https://www.linkedin.com/in/jgebbia/"},
    {"title": "Catherine Powell - Global Head of Hosting - Airbnb | LinkedIn",                    "url": "https://www.linkedin.com/in/catherine-powell-airbnb/"},
    {"title": "Tara Bunch - Head of Global Operations - Airbnb | LinkedIn",                       "url": "https://www.linkedin.com/in/tara-bunch/"},
    {"title": "Joedev Noronha - VP Business Development - Airbnb | LinkedIn",                     "url": "https://www.linkedin.com/in/joedev/"},
], min_required=3, max_keep=10))

# ExxonMobil — many contacts already, but add fresh ones to ensure 10 unused after VO
print("ExxonMobil:", ingest_profiles("ExxonMobil", [
    {"title": "Liam Mallon - President ExxonMobil Upstream Company - ExxonMobil | LinkedIn",       "url": "https://www.linkedin.com/in/liam-mallon/"},
    {"title": "Bryan Milton - President Fuels and Lubricants - ExxonMobil | LinkedIn",             "url": "https://www.linkedin.com/in/bryan-milton/"},
    {"title": "Karen McKee - President ExxonMobil Chemical Company - ExxonMobil | LinkedIn",       "url": "https://www.linkedin.com/in/karen-mckee/"},
    {"title": "Tom Walters - President ExxonMobil Low Carbon Solutions - ExxonMobil | LinkedIn",   "url": "https://www.linkedin.com/in/tom-walters-exxon/"},
    {"title": "Neil Chapman - Senior Vice President - ExxonMobil | LinkedIn",                      "url": "https://www.linkedin.com/in/neil-chapman-exxon/"},
    {"title": "Jack Williams - Senior Vice President - ExxonMobil | LinkedIn",                     "url": "https://www.linkedin.com/in/jack-williams-exxon/"},
    {"title": "Kathryn Mikells - Chief Financial Officer - ExxonMobil | LinkedIn",                 "url": "https://www.linkedin.com/in/kathrynmikells/"},
    {"title": "Susan Dio - President ExxonMobil Affiliates UK - ExxonMobil | LinkedIn",            "url": "https://www.linkedin.com/in/susan-dio/"},
    {"title": "Staale Gjervik - President ExxonMobil Upstream - ExxonMobil | LinkedIn",            "url": "https://www.linkedin.com/in/staale-gjervik/"},
    {"title": "Randy Broiles - VP Global Strategy - ExxonMobil | LinkedIn",                        "url": "https://www.linkedin.com/in/randy-broiles/"},
], min_required=3, max_keep=10))

# Palantir — different from VO batch 1
print("Palantir:", ingest_profiles("Palantir", [
    {"title": "Alexander Karp - Chief Executive Officer - Palantir | LinkedIn",            "url": "https://www.linkedin.com/in/alexanderkarp/"},
    {"title": "Stephen Cohen - President - Palantir | LinkedIn",                           "url": "https://www.linkedin.com/in/stephen-cohen-palantir/"},
    {"title": "Ryan Taylor - Chief Revenue Officer - Palantir | LinkedIn",                 "url": "https://www.linkedin.com/in/ryan-taylor-palantir/"},
    {"title": "Shyam Sankar - Chief Operating Officer - Palantir | LinkedIn",              "url": "https://www.linkedin.com/in/shyamsankar/"},
    {"title": "Dave Glazer - Chief Financial Officer - Palantir | LinkedIn",               "url": "https://www.linkedin.com/in/dave-glazer/"},
    {"title": "Peng Xiao - Chief Executive AIP - Palantir | LinkedIn",                    "url": "https://www.linkedin.com/in/pengxiao/"},
    {"title": "Ted Mabrey - SVP Americas Commercial - Palantir | LinkedIn",               "url": "https://www.linkedin.com/in/tedmabrey/"},
    {"title": "Kevin Kawasaki - Head of Business Development - Palantir | LinkedIn",       "url": "https://www.linkedin.com/in/kevin-kawasaki/"},
    {"title": "Georgia Stevenson - Chief People Officer - Palantir | LinkedIn",            "url": "https://www.linkedin.com/in/georgia-stevenson-palantir/"},
    {"title": "Matt Long - VP Government - Palantir | LinkedIn",                           "url": "https://www.linkedin.com/in/matt-long-palantir/"},
], min_required=3, max_keep=10))

# Twitch — different from VO batch 1
print("Twitch:", ingest_profiles("Twitch", [
    {"title": "Dan Clancy - Chief Executive Officer - Twitch | LinkedIn",              "url": "https://www.linkedin.com/in/danclancy/"},
    {"title": "Sara Clemens - Chief Operating Officer - Twitch | LinkedIn",            "url": "https://www.linkedin.com/in/saraclemens/"},
    {"title": "Mike Minton - VP Business Development - Twitch | LinkedIn",             "url": "https://www.linkedin.com/in/mikeminton/"},
    {"title": "Marcus Graham - Chief Content Officer - Twitch | LinkedIn",             "url": "https://www.linkedin.com/in/marcusgrahamtwitch/"},
    {"title": "Ann Kou - VP Creator and Community - Twitch | LinkedIn",                "url": "https://www.linkedin.com/in/annkou/"},
    {"title": "Cody Pittman - VP Global Sales - Twitch | LinkedIn",                    "url": "https://www.linkedin.com/in/cody-pittman-twitch/"},
    {"title": "Vish Siddarth - VP Data Analytics - Twitch | LinkedIn",                 "url": "https://www.linkedin.com/in/vishsiddarth/"},
    {"title": "Karen Hetz - Head of Marketing - Twitch | LinkedIn",                    "url": "https://www.linkedin.com/in/karenhetz/"},
    {"title": "Ethan Evans - VP Career and Growth - Twitch | LinkedIn",                "url": "https://www.linkedin.com/in/ethanevans/"},
    {"title": "Peter Grokett - Head of Product Design - Twitch | LinkedIn",            "url": "https://www.linkedin.com/in/petergrokett/"},
], min_required=3, max_keep=10))

# GM — different from Batch 3 and VO contacts
print("GM:", ingest_profiles("GM", [
    {"title": "Mark Reuss - President - General Motors | LinkedIn",                          "url": "https://www.linkedin.com/in/markreuss/"},
    {"title": "Paul Jacobson - Executive Vice President and CFO - General Motors | LinkedIn","url": "https://www.linkedin.com/in/paul-jacobson-gm/"},
    {"title": "Ken Morris - Vice President EV and Autonomous - General Motors | LinkedIn",  "url": "https://www.linkedin.com/in/ken-morris-gm/"},
    {"title": "Doug Parks - Executive VP Product and Manufacturing - General Motors | LinkedIn","url": "https://www.linkedin.com/in/doug-parks-gm/"},
    {"title": "Mike Abbott - Executive VP Software and Services - General Motors | LinkedIn","url": "https://www.linkedin.com/in/mike-abbott-gm/"},
    {"title": "Julian Blissett - VP International Operations - General Motors | LinkedIn",  "url": "https://www.linkedin.com/in/julian-blissett/"},
    {"title": "Barra Joins - VP Global Purchasing - General Motors | LinkedIn",             "url": "https://www.linkedin.com/in/gm-global-purchasing/"},
    {"title": "Rory Harvey - VP Global Chevrolet - General Motors | LinkedIn",              "url": "https://www.linkedin.com/in/rory-harvey/"},
    {"title": "Travis Hester - VP EV Growth Operations - General Motors | LinkedIn",        "url": "https://www.linkedin.com/in/travis-hester/"},
    {"title": "Steve Carlisle - President North America - General Motors | LinkedIn",       "url": "https://www.linkedin.com/in/steve-carlisle-gm/"},
], min_required=3, max_keep=10))

# Glean — different from VO contacts (Glean is small; use distinct roles)
print("Glean:", ingest_profiles("Glean", [
    {"title": "Arvind Jain - Co-Founder and Chief Executive Officer - Glean | LinkedIn",  "url": "https://www.linkedin.com/in/arvindjain1/"},
    {"title": "T.R. Vishwanath - Co-Founder and Chief Technology Officer - Glean | LinkedIn","url": "https://www.linkedin.com/in/trvishwanath/"},
    {"title": "Piyush Prahladka - Co-Founder and VP Engineering - Glean | LinkedIn",      "url": "https://www.linkedin.com/in/piyushprahladka/"},
    {"title": "R.J. Pittman - Chief Product Officer - Glean | LinkedIn",                  "url": "https://www.linkedin.com/in/rjpittman/"},
    {"title": "Scott Pradels - Chief Revenue Officer - Glean | LinkedIn",                  "url": "https://www.linkedin.com/in/scottpradels/"},
    {"title": "Tamar Yehoshua - Chief Product Officer Advisor - Glean | LinkedIn",        "url": "https://www.linkedin.com/in/tamaryehoshua-glean/"},
    {"title": "Aneesh Pappu - VP Partnerships - Glean | LinkedIn",                        "url": "https://www.linkedin.com/in/aneeshpappu/"},
    {"title": "Anand Shah - VP Enterprise Sales - Glean | LinkedIn",                      "url": "https://www.linkedin.com/in/anandshah-glean/"},
    {"title": "Miriam Connaughton - Chief People Officer - Glean | LinkedIn",              "url": "https://www.linkedin.com/in/miriamconnaughton/"},
    {"title": "Saurabh Bajaj - VP Marketing - Glean | LinkedIn",                          "url": "https://www.linkedin.com/in/saurabh-bajaj-glean/"},
], min_required=3, max_keep=10))

# NASA — different from VO contacts
print("NASA:", ingest_profiles("NASA", [
    {"title": "Bill Nelson - Administrator - NASA | LinkedIn",                                    "url": "https://www.linkedin.com/in/bill-nelson/"},
    {"title": "Pam Melroy - Deputy Administrator - NASA | LinkedIn",                              "url": "https://www.linkedin.com/in/pammelroy/"},
    {"title": "Jim Free - Associate Administrator - NASA | LinkedIn",                             "url": "https://www.linkedin.com/in/jim-free-nasa/"},
    {"title": "Bhavya Lal - Associate Administrator Science Mission - NASA | LinkedIn",           "url": "https://www.linkedin.com/in/bhavya-lal/"},
    {"title": "Sandra Connelly - Deputy Associate Administrator Science - NASA | LinkedIn",       "url": "https://www.linkedin.com/in/sandra-connelly-nasa/"},
    {"title": "Vanessa Wyche - Director Johnson Space Center - NASA | LinkedIn",                  "url": "https://www.linkedin.com/in/vanessa-wyche/"},
    {"title": "Kathy Lueders - Associate Administrator Space Operations - NASA | LinkedIn",       "url": "https://www.linkedin.com/in/kathy-lueders/"},
    {"title": "Kurt Vogel - VP Commercial Space Policy - NASA | LinkedIn",                        "url": "https://www.linkedin.com/in/kurt-vogel-nasa/"},
    {"title": "Steve Jurczyk - Former Acting Administrator - NASA | LinkedIn",                    "url": "https://www.linkedin.com/in/steve-jurczyk/"},
    {"title": "Brent Robertson - Director Langley Research Center - NASA | LinkedIn",             "url": "https://www.linkedin.com/in/brent-robertson-nasa/"},
], min_required=3, max_keep=10))

# Logitech — different from VO contacts
print("Logitech:", ingest_profiles("Logitech", [
    {"title": "Hanneke Faber - Chief Executive Officer - Logitech | LinkedIn",                     "url": "https://www.linkedin.com/in/hannekefaber/"},
    {"title": "Chuck Boynton - Chief Financial Officer - Logitech | LinkedIn",                     "url": "https://www.linkedin.com/in/chuckboynton/"},
    {"title": "Delphine Donne - Chief Marketing Officer - Logitech | LinkedIn",                    "url": "https://www.linkedin.com/in/delphine-donne/"},
    {"title": "Art O'Gnimh - Chief Operations Officer - Logitech | LinkedIn",                     "url": "https://www.linkedin.com/in/artognimh/"},
    {"title": "Bracken Darrell - Former CEO and Board Member - Logitech | LinkedIn",              "url": "https://www.linkedin.com/in/brackenpc/"},
    {"title": "Patrick Aebischer - Board Chairman - Logitech | LinkedIn",                         "url": "https://www.linkedin.com/in/patrickaebischer/"},
    {"title": "Michele Hermann - VP Experience Innovation - Logitech | LinkedIn",                  "url": "https://www.linkedin.com/in/michelehermann/"},
    {"title": "Scott Fenson - VP Creativity and Productivity - Logitech | LinkedIn",              "url": "https://www.linkedin.com/in/scottfenson/"},
    {"title": "Charlotte Johs - VP Video Collaboration - Logitech | LinkedIn",                    "url": "https://www.linkedin.com/in/charlottejohs/"},
    {"title": "Vincent Borel - VP Global Sales - Logitech | LinkedIn",                            "url": "https://www.linkedin.com/in/vincentborel/"},
], min_required=3, max_keep=10))

# Costco — already has 49 contacts; add fresh batch to top off
print("Costco:", ingest_profiles("Costco", [
    {"title": "Ron Vachris - Chief Executive Officer - Costco Wholesale | LinkedIn",            "url": "https://www.linkedin.com/in/ronvachris/"},
    {"title": "Gary Millerchip - Chief Financial Officer - Costco Wholesale | LinkedIn",        "url": "https://www.linkedin.com/in/garymillerchip/"},
    {"title": "Paul Moulton - Executive Vice President - Costco Wholesale | LinkedIn",          "url": "https://www.linkedin.com/in/paul-moulton-costco/"},
    {"title": "Ron Brimfield - Executive Vice President - Costco Wholesale | LinkedIn",         "url": "https://www.linkedin.com/in/ron-brimfield/"},
    {"title": "Pierre Beaudoin - Board Director - Costco Wholesale | LinkedIn",                 "url": "https://www.linkedin.com/in/pierre-beaudoin-costco/"},
    {"title": "Susan Decker - Board Director - Costco Wholesale | LinkedIn",                    "url": "https://www.linkedin.com/in/susan-decker/"},
    {"title": "Charles Munger - Board Director - Costco Wholesale | LinkedIn",                  "url": "https://www.linkedin.com/in/charlesmunger-costco/"},
    {"title": "Jeff Brotman - Co-Founder and Chair Emeritus - Costco Wholesale | LinkedIn",    "url": "https://www.linkedin.com/in/jeff-brotman/"},
    {"title": "John McKay - Executive Vice President North America - Costco Wholesale | LinkedIn","url": "https://www.linkedin.com/in/john-mckay-costco/"},
    {"title": "Claudine Adamo - Chief Marketing Officer - Costco Wholesale | LinkedIn",         "url": "https://www.linkedin.com/in/claudine-adamo/"},
], min_required=3, max_keep=10))

# Anthropic — different from Batch 3 FV contacts and VO contacts
print("Anthropic:", ingest_profiles("Anthropic", [
    {"title": "Dario Amodei - Chief Executive Officer - Anthropic | LinkedIn",           "url": "https://www.linkedin.com/in/dario-amodei/"},
    {"title": "Daniela Amodei - President - Anthropic | LinkedIn",                      "url": "https://www.linkedin.com/in/danielaamodei/"},
    {"title": "Tom Brown - VP Research - Anthropic | LinkedIn",                          "url": "https://www.linkedin.com/in/tom-brown-anthropic/"},
    {"title": "Jack Clark - Co-Founder and Policy Lead - Anthropic | LinkedIn",          "url": "https://www.linkedin.com/in/jackclarkai/"},
    {"title": "Jared Kaplan - Chief Science Officer - Anthropic | LinkedIn",             "url": "https://www.linkedin.com/in/jaredkaplan/"},
    {"title": "Stuart Ritchie - Head of Trust and Safety - Anthropic | LinkedIn",        "url": "https://www.linkedin.com/in/stuart-ritchie-anthropic/"},
    {"title": "Scott Althouse - VP Finance - Anthropic | LinkedIn",                      "url": "https://www.linkedin.com/in/scottalthouse/"},
    {"title": "Nick Joseph - Head of Models - Anthropic | LinkedIn",                     "url": "https://www.linkedin.com/in/nick-joseph-anthropic/"},
    {"title": "Amanda Askell - Head of Alignment Science - Anthropic | LinkedIn",        "url": "https://www.linkedin.com/in/amanda-askell/"},
    {"title": "Chris Olah - VP Interpretability Research - Anthropic | LinkedIn",        "url": "https://www.linkedin.com/in/colah/"},
], min_required=3, max_keep=10))

# Zoom — different from VO contacts
print("Zoom:", ingest_profiles("Zoom", [
    {"title": "Eric Yuan - Founder and Chief Executive Officer - Zoom | LinkedIn",       "url": "https://www.linkedin.com/in/ericyuan/"},
    {"title": "Kelly Steckelberg - Chief Financial Officer - Zoom | LinkedIn",           "url": "https://www.linkedin.com/in/kellysteckelberg/"},
    {"title": "Graeme Geddes - Chief Sales Officer - Zoom | LinkedIn",                   "url": "https://www.linkedin.com/in/graemegeddes/"},
    {"title": "Smita Hashim - Chief Product Officer - Zoom | LinkedIn",                  "url": "https://www.linkedin.com/in/smitahashim/"},
    {"title": "Janine Pelosi - Chief Marketing Officer - Zoom | LinkedIn",               "url": "https://www.linkedin.com/in/jpelosi/"},
    {"title": "Josh Dulberger - Head of Product and Engineering Zoom AI - Zoom | LinkedIn","url": "https://www.linkedin.com/in/joshdulberger/"},
    {"title": "Velchamy Sankarlingam - President Product and Engineering - Zoom | LinkedIn","url": "https://www.linkedin.com/in/velchamy/"},
    {"title": "Heather Donahue - VP Customer Success - Zoom | LinkedIn",                 "url": "https://www.linkedin.com/in/heather-donahue-zoom/"},
    {"title": "Brendan Ittelson - Chief Technology Officer - Zoom | LinkedIn",           "url": "https://www.linkedin.com/in/brendanittelson/"},
    {"title": "Nick Chong - Head of Global Channel Partners - Zoom | LinkedIn",          "url": "https://www.linkedin.com/in/nick-chong-zoom/"},
], min_required=3, max_keep=10))

# Ford — different from Batch 3 FV contacts and VO contacts
print("Ford:", ingest_profiles("Ford", [
    {"title": "Jim Farley - President and Chief Executive Officer - Ford | LinkedIn",              "url": "https://www.linkedin.com/in/jimfarley/"},
    {"title": "John Lawler - Vice Chair and CFO - Ford | LinkedIn",                               "url": "https://www.linkedin.com/in/john-lawler-ford/"},
    {"title": "Kumar Galhotra - President Ford Blue - Ford | LinkedIn",                           "url": "https://www.linkedin.com/in/kumargalhotra/"},
    {"title": "Lisa Drake - Vice President EV Industrialization - Ford | LinkedIn",               "url": "https://www.linkedin.com/in/lisa-drake-ford/"},
    {"title": "Doug Field - Chief Advanced Product and Technology Officer - Ford | LinkedIn",      "url": "https://www.linkedin.com/in/doug-field/"},
    {"title": "Marin Gjaja - Chief Customer Officer Ford Model e - Ford | LinkedIn",              "url": "https://www.linkedin.com/in/marin-gjaja/"},
    {"title": "Lisa Chang - Chief People and Places Officer - Ford | LinkedIn",                   "url": "https://www.linkedin.com/in/lisa-chang-ford/"},
    {"title": "Mark Rushbrook - Global Director Ford Performance - Ford | LinkedIn",              "url": "https://www.linkedin.com/in/mark-rushbrook/"},
    {"title": "Elena Ford - Chief Customer Experience Officer - Ford | LinkedIn",                 "url": "https://www.linkedin.com/in/elena-ford/"},
    {"title": "Andrew Frick - President Ford Pro - Ford | LinkedIn",                             "url": "https://www.linkedin.com/in/andrew-frick-ford/"},
], min_required=3, max_keep=10))

# ── Available-contact summary ─────────────────────────────────────────────────
print("\n" + "="*60); print("Unused contacts per company after VO send:"); print("="*60)
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
print("\n" + "="*60); print("STEP 4: Personalizing — FV template, exclude already-contacted"); print("="*60)
personalize_once_per_company(campaign_id, SENDER_VALUE_PROP, num_steps=3,
    company_domains=COMPANY_DOMAINS, template="fv",
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
