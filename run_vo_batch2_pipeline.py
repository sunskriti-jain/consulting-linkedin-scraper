"""
Venture Out Batch 2 — companies 16-30 from master list.
Uses exclude_contacted=True so no person gets a 2nd email from any org.
Ingests FRESH profiles (different from any prior campaign contacts).
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
    {"name": "Vercel",             "domain": "vercel.com",               "industry": "Dev Tooling / Cloud",           "email_pattern": "first.last"},
    {"name": "Perplexity",         "domain": "perplexity.ai",            "industry": "AI Search",                     "email_pattern": "first.last"},
    {"name": "PlayStation",        "domain": "playstation.com",          "industry": "Gaming / Consumer Electronics", "email_pattern": "first.last"},
    {"name": "CVS Health",         "domain": "cvshealth.com",            "industry": "Healthcare / Pharmacy",         "email_pattern": "first.last"},
    {"name": "Ramp",               "domain": "ramp.com",                 "industry": "Corporate Fintech",             "email_pattern": "first.last"},
    {"name": "Slack",              "domain": "slack.com",                "industry": "Enterprise Communications",     "email_pattern": "first.last"},
    {"name": "Applied Intuition",  "domain": "appliedintuition.com",     "industry": "Autonomous Vehicle Software",   "email_pattern": "first.last"},
    {"name": "Replit",             "domain": "replit.com",               "industry": "AI Dev Tools / Cloud IDE",      "email_pattern": "first.last"},
    {"name": "L'Oreal",            "domain": "loreal.com",               "industry": "Beauty / Consumer Goods",       "email_pattern": "first.last"},
    {"name": "American Express",   "domain": "americanexpress.com",      "industry": "Financial Services",            "email_pattern": "first.last"},
    {"name": "UnitedHealth Group", "domain": "unitedhealthgroup.com",    "industry": "Healthcare / Insurance",        "email_pattern": "first.last"},
    {"name": "OpenAI",             "domain": "openai.com",               "industry": "AI / Foundation Models",        "email_pattern": "first.last"},
    {"name": "Atlassian",          "domain": "atlassian.com",            "industry": "Dev Tooling / Enterprise SaaS", "email_pattern": "first.last"},
    {"name": "Mondelez",           "domain": "mondelezinternational.com", "industry": "Consumer Goods / Snacking",     "email_pattern": "first.last"},
    {"name": "Brex",               "domain": "brex.com",                 "industry": "Corporate Fintech",             "email_pattern": "first.last"},
]

COMPANY_DOMAINS = [c["domain"] for c in COMPANIES]
CAMPAIGN_NAME = "Venture Out Batch 2 - June 2026"
SENDER_VALUE_PROP = (
    "Venture Out is a collective of consultants, product managers, software engineers, "
    "and founders from Berkeley Business Society, Free Ventures, Web Development at Berkeley, "
    "Girls Who Venture and 180 Degrees Consulting at Duke, and ProductSC at USC. Together "
    "we've advised and helped scale startups that raised from Y Combinator, Greylock, and "
    "Kleiner Perkins — working directly with founders on strategy, product, software, and growth."
)

print("\n" + "="*60); print("STEP 1: Inserting companies"); print("="*60)
with get_db() as conn:
    for c in COMPANIES:
        try:
            conn.execute("INSERT INTO companies (id,name,domain,industry,email_pattern,email_pattern_confidence) VALUES (?,?,?,?,?,?)",
                (new_id(), c["name"], c["domain"], c["industry"], c["email_pattern"], 70.0))
            print(f"  [+] {c['name']}")
        except Exception as e:
            print(f"  [=] {c['name']} already exists" if "UNIQUE" in str(e).upper() else f"  [!] {e}")

print("\n" + "="*60); print("STEP 2: Ingesting FRESH profiles (unused people)"); print("="*60)

# Vercel — different from Tech Startup Outreach (Guillermo Rauch, Lee Robinson, Tom Occhino, Malte Ubl, etc.)
print("Vercel:", ingest_profiles("Vercel", [
    {"title": "Jared Palmer - VP Engineering Turborepo - Vercel | LinkedIn",       "url": "https://www.linkedin.com/in/jaredpalmer/"},
    {"title": "KC Gleeson - VP Revenue - Vercel | LinkedIn",                       "url": "https://www.linkedin.com/in/kcgleeson/"},
    {"title": "Ashley Smith - VP Marketing - Vercel | LinkedIn",                   "url": "https://www.linkedin.com/in/ashleysmith-vercel/"},
    {"title": "Hassan Djirdeh - VP Product - Vercel | LinkedIn",                   "url": "https://www.linkedin.com/in/hassandjirdeh/"},
    {"title": "Cody De Arkland - Head of Developer Relations - Vercel | LinkedIn", "url": "https://www.linkedin.com/in/codydearkland/"},
    {"title": "Ian Connolly - Chief Financial Officer - Vercel | LinkedIn",        "url": "https://www.linkedin.com/in/ian-connolly-vercel/"},
    {"title": "Tim Neutkens - Core Framework Lead - Vercel | LinkedIn",            "url": "https://www.linkedin.com/in/timneutkens/"},
    {"title": "Lydia Hallie - Head of Education - Vercel | LinkedIn",              "url": "https://www.linkedin.com/in/lydiahallie/"},
    {"title": "Zack Tanner - Head of Developer Experience - Vercel | LinkedIn",   "url": "https://www.linkedin.com/in/zacktanner/"},
    {"title": "Andrew Rhyne - VP Engineering Infrastructure - Vercel | LinkedIn",  "url": "https://www.linkedin.com/in/andrew-rhyne/"},
], min_required=3, max_keep=10))

# Perplexity — different from Batch 3 (Aravind Srinivas, Andy Konwinski, etc.)
print("Perplexity:", ingest_profiles("Perplexity", [
    {"title": "Denis Yarats - Co-Founder and CTO - Perplexity | LinkedIn",             "url": "https://www.linkedin.com/in/denisyarats/"},
    {"title": "Johnny Ho - Co-Founder - Perplexity | LinkedIn",                        "url": "https://www.linkedin.com/in/johnny-ho-perplexity/"},
    {"title": "Dmitry Shevelenko - Chief Business Officer - Perplexity | LinkedIn",    "url": "https://www.linkedin.com/in/dmitry-shevelenko/"},
    {"title": "Sara Platnick - Head of Brand - Perplexity | LinkedIn",                 "url": "https://www.linkedin.com/in/sara-platnick/"},
    {"title": "Gaurav Nemade - Head of Growth - Perplexity | LinkedIn",                "url": "https://www.linkedin.com/in/gauravnemade/"},
    {"title": "Srinath Sridhar - Head of Enterprise - Perplexity | LinkedIn",          "url": "https://www.linkedin.com/in/srinath-sridhar/"},
    {"title": "Drew Hess - VP Partnerships - Perplexity | LinkedIn",                   "url": "https://www.linkedin.com/in/drewhess/"},
    {"title": "Deepak Ramachandran - Head of Product - Perplexity | LinkedIn",         "url": "https://www.linkedin.com/in/deepak-ramachandran-perplexity/"},
    {"title": "Katie Boue - VP Communications - Perplexity | LinkedIn",                "url": "https://www.linkedin.com/in/katieboue/"},
    {"title": "Elad Gil - Board Member and Advisor - Perplexity | LinkedIn",           "url": "https://www.linkedin.com/in/eladgil/"},
], min_required=3, max_keep=10))

# PlayStation — brand new to DB
print("PlayStation:", ingest_profiles("PlayStation", [
    {"title": "Hideaki Nishino - Co-Chief Executive Officer - Sony Interactive Entertainment | LinkedIn",            "url": "https://www.linkedin.com/in/hideaki-nishino/"},
    {"title": "Hermen Hulst - Co-Chief Executive Officer Studio Business Group - Sony Interactive Entertainment | LinkedIn", "url": "https://www.linkedin.com/in/hermenhulst/"},
    {"title": "Veronica Rogers - Chief Revenue Officer - Sony Interactive Entertainment | LinkedIn",                "url": "https://www.linkedin.com/in/veronicarogers/"},
    {"title": "Nick Maguire - VP Global Digital Sales - Sony Interactive Entertainment | LinkedIn",                 "url": "https://www.linkedin.com/in/nick-maguire-sie/"},
    {"title": "Eric Lempel - VP Marketing and PlayStation Network - Sony Interactive Entertainment | LinkedIn",     "url": "https://www.linkedin.com/in/ericlempel/"},
    {"title": "Simon Rutter - Executive Vice President - Sony Interactive Entertainment Europe | LinkedIn",         "url": "https://www.linkedin.com/in/simon-rutter-sie/"},
    {"title": "Sid Shuman - VP Global Communications - Sony Interactive Entertainment | LinkedIn",                 "url": "https://www.linkedin.com/in/sidshuman/"},
    {"title": "Connie Booth - Chief People Officer - Sony Interactive Entertainment | LinkedIn",                   "url": "https://www.linkedin.com/in/conniebooth/"},
    {"title": "Nicolas Poirot - Head of PlayStation Productions - Sony Interactive Entertainment | LinkedIn",      "url": "https://www.linkedin.com/in/nicolas-poirot/"},
    {"title": "Mark Cerny - Lead System Architect - Sony Interactive Entertainment | LinkedIn",                    "url": "https://www.linkedin.com/in/mark-cerny/"},
], min_required=3, max_keep=10))

# CVS Health — different from Fortune 20 (Karen Lynch, Shawn Guertin, etc.)
print("CVS Health:", ingest_profiles("CVS Health", [
    {"title": "Alan Lotvin - Executive Vice President Transformation - CVS Health | LinkedIn",                          "url": "https://www.linkedin.com/in/alanlotvin/"},
    {"title": "Michelle Peluso - Executive Vice President and Chief Customer Officer - CVS Health | LinkedIn",          "url": "https://www.linkedin.com/in/michellepeluso/"},
    {"title": "Thomas Moriarty - Executive Vice President and Chief Policy Officer - CVS Health | LinkedIn",            "url": "https://www.linkedin.com/in/thomas-moriarty-cvs/"},
    {"title": "Prem Shah - Executive Vice President Pharmacy Services - CVS Health | LinkedIn",                        "url": "https://www.linkedin.com/in/prem-shah-cvs/"},
    {"title": "Sree Chaguturu - Executive Vice President and Chief Medical Officer - CVS Health | LinkedIn",            "url": "https://www.linkedin.com/in/sree-chaguturu/"},
    {"title": "Creagh Milford - President Health Care Delivery - CVS Health | LinkedIn",                               "url": "https://www.linkedin.com/in/creagh-milford/"},
    {"title": "Daniel Finke - Executive Vice President Pharmacy and Consumer Wellness - CVS Health | LinkedIn",        "url": "https://www.linkedin.com/in/daniel-finke-cvs/"},
    {"title": "Eileen Howard Boone - SVP Corporate Social Responsibility - CVS Health | LinkedIn",                     "url": "https://www.linkedin.com/in/eileen-howard-boone/"},
    {"title": "David Dossett - VP Corporate Communications - CVS Health | LinkedIn",                                   "url": "https://www.linkedin.com/in/david-dossett-cvs/"},
    {"title": "Christy Findlay - VP Government Affairs - CVS Health | LinkedIn",                                       "url": "https://www.linkedin.com/in/christy-findlay/"},
], min_required=3, max_keep=10))

# Ramp — different from Batch 3 (Eric Glyman, etc.)
print("Ramp:", ingest_profiles("Ramp", [
    {"title": "Gene Lee - Chief Operating Officer - Ramp | LinkedIn",           "url": "https://www.linkedin.com/in/gene-lee-ramp/"},
    {"title": "Andrew Rachmell - Chief Revenue Officer - Ramp | LinkedIn",      "url": "https://www.linkedin.com/in/andrewrachmell/"},
    {"title": "Karandeep Anand - President - Ramp | LinkedIn",                  "url": "https://www.linkedin.com/in/karandeepanand/"},
    {"title": "Kareem Amin - VP Engineering - Ramp | LinkedIn",                 "url": "https://www.linkedin.com/in/kareemamin/"},
    {"title": "Michael Tannenbaum - Chief Financial Officer - Ramp | LinkedIn", "url": "https://www.linkedin.com/in/michaeltannenbaum/"},
    {"title": "Samuel Blond - Chief Sales Officer - Ramp | LinkedIn",           "url": "https://www.linkedin.com/in/samuelblond/"},
    {"title": "Seun Kassim - Head of Marketing - Ramp | LinkedIn",              "url": "https://www.linkedin.com/in/seunkassim/"},
    {"title": "Alex Kladov - VP Product - Ramp | LinkedIn",                     "url": "https://www.linkedin.com/in/alex-kladov-ramp/"},
    {"title": "Genevieve Tetteh - Head of People - Ramp | LinkedIn",            "url": "https://www.linkedin.com/in/genevietettegh/"},
    {"title": "Nabeel Alamgir - VP Partnerships - Ramp | LinkedIn",             "url": "https://www.linkedin.com/in/nabeel-alamgir/"},
], min_required=3, max_keep=10))

# Slack — brand new to DB
print("Slack:", ingest_profiles("Slack", [
    {"title": "Denise Dresser - Chief Executive Officer - Slack | LinkedIn",          "url": "https://www.linkedin.com/in/denisedresser/"},
    {"title": "Tamar Yehoshua - President - Slack | LinkedIn",                        "url": "https://www.linkedin.com/in/tamaryehoshua/"},
    {"title": "Robert Frati - Chief Revenue Officer - Slack | LinkedIn",              "url": "https://www.linkedin.com/in/robertfrati/"},
    {"title": "Ali Rayl - VP Customer Experience - Slack | LinkedIn",                 "url": "https://www.linkedin.com/in/alirayl/"},
    {"title": "Steve Wood - SVP Engineering - Slack | LinkedIn",                      "url": "https://www.linkedin.com/in/steve-wood-slack/"},
    {"title": "Noah Weiss - Chief Product Officer - Slack | LinkedIn",                "url": "https://www.linkedin.com/in/noahweiss/"},
    {"title": "Robby Kwok - VP People Operations - Slack | LinkedIn",                 "url": "https://www.linkedin.com/in/robbykwok/"},
    {"title": "Brad Armstrong - VP Marketing - Slack | LinkedIn",                     "url": "https://www.linkedin.com/in/brad-armstrong-slack/"},
    {"title": "Jonathan Prince - VP Communications - Slack | LinkedIn",               "url": "https://www.linkedin.com/in/jonathanprince/"},
    {"title": "Brian Elliott - VP Future Forum - Slack | LinkedIn",                   "url": "https://www.linkedin.com/in/brianelliott/"},
], min_required=3, max_keep=10))

# Applied Intuition — different from Tech Startup (Qasar Younis, Peter Ludwig, etc.)
print("Applied Intuition:", ingest_profiles("Applied Intuition", [
    {"title": "Marin Tchakarov - Chief Product Officer - Applied Intuition | LinkedIn",       "url": "https://www.linkedin.com/in/marintegration/"},
    {"title": "Clint Schmidt - VP Sales - Applied Intuition | LinkedIn",                      "url": "https://www.linkedin.com/in/clint-schmidt/"},
    {"title": "Will Lagergren - VP Engineering - Applied Intuition | LinkedIn",               "url": "https://www.linkedin.com/in/will-lagergren/"},
    {"title": "Katherine Kan - Head of Marketing - Applied Intuition | LinkedIn",             "url": "https://www.linkedin.com/in/katherine-kan/"},
    {"title": "Vignesh Ganapathi - Head of Business Development - Applied Intuition | LinkedIn","url": "https://www.linkedin.com/in/vignesh-ganapathi/"},
    {"title": "Tyler Langsam - Head of Finance - Applied Intuition | LinkedIn",               "url": "https://www.linkedin.com/in/tylerlangsam/"},
    {"title": "Brendan Falk - Head of Simulation - Applied Intuition | LinkedIn",             "url": "https://www.linkedin.com/in/brendanfalk/"},
    {"title": "David Ibanez - VP Customer Success - Applied Intuition | LinkedIn",            "url": "https://www.linkedin.com/in/david-ibanez-ai/"},
    {"title": "Shyam Sundhar - VP Operations - Applied Intuition | LinkedIn",                 "url": "https://www.linkedin.com/in/shyam-sundhar/"},
    {"title": "Sarah Li - Head of People - Applied Intuition | LinkedIn",                     "url": "https://www.linkedin.com/in/sarah-li-appliedintuition/"},
], min_required=3, max_keep=10))

# Replit — 0 existing contacts
print("Replit:", ingest_profiles("Replit", [
    {"title": "Amjad Masad - Co-Founder and Chief Executive Officer - Replit | LinkedIn",     "url": "https://www.linkedin.com/in/amjadmasad/"},
    {"title": "Haya Odeh - Co-Founder and Chief Technology Officer - Replit | LinkedIn",      "url": "https://www.linkedin.com/in/hayaodeh/"},
    {"title": "Michele Catasta - President - Replit | LinkedIn",                              "url": "https://www.linkedin.com/in/pirroh/"},
    {"title": "Dave Sherwood - VP Business Development - Replit | LinkedIn",                  "url": "https://www.linkedin.com/in/dave-sherwood-replit/"},
    {"title": "Barret Ward - VP Operations - Replit | LinkedIn",                              "url": "https://www.linkedin.com/in/barretward/"},
    {"title": "Lena Sesardic - Head of Growth - Replit | LinkedIn",                           "url": "https://www.linkedin.com/in/lenasesardic/"},
    {"title": "Patrick Coleman - VP Engineering - Replit | LinkedIn",                         "url": "https://www.linkedin.com/in/patrick-coleman-replit/"},
    {"title": "Yev Barkalov - Head of Product - Replit | LinkedIn",                           "url": "https://www.linkedin.com/in/yevbarkalov/"},
    {"title": "Xiaoyin Che - Head of Design - Replit | LinkedIn",                             "url": "https://www.linkedin.com/in/xiaoyinche/"},
    {"title": "Soren Bjornstad - Head of Education - Replit | LinkedIn",                      "url": "https://www.linkedin.com/in/sorenbjornstad/"},
], min_required=3, max_keep=10))

# L'Oreal — brand new to DB
print("L'Oreal:", ingest_profiles("L'Oreal", [
    {"title": "Nicolas Hieronimus - Chief Executive Officer - L'Oreal | LinkedIn",                                 "url": "https://www.linkedin.com/in/nicolas-hieronimus/"},
    {"title": "Jean-Paul Agon - Chairman of the Board - L'Oreal | LinkedIn",                                      "url": "https://www.linkedin.com/in/jean-paul-agon/"},
    {"title": "Barbara Lavernos - Deputy Chief Executive Officer - L'Oreal | LinkedIn",                           "url": "https://www.linkedin.com/in/barbara-lavernos/"},
    {"title": "Nathalie Roos - President Consumer Products Division - L'Oreal | LinkedIn",                        "url": "https://www.linkedin.com/in/nathalie-roos/"},
    {"title": "Delphine Viguier-Hovasse - President L'Oreal Luxe - L'Oreal | LinkedIn",                          "url": "https://www.linkedin.com/in/delphine-viguier/"},
    {"title": "Frederic Roze - President of the Americas - L'Oreal | LinkedIn",                                   "url": "https://www.linkedin.com/in/frederic-roze/"},
    {"title": "Laurent Attal - Executive Vice President Research and Innovation - L'Oreal | LinkedIn",            "url": "https://www.linkedin.com/in/laurent-attal/"},
    {"title": "Vianney Mulliez - President Professional Products Division - L'Oreal | LinkedIn",                  "url": "https://www.linkedin.com/in/vianney-mulliez/"},
    {"title": "Brigitte Liberman - President Active Cosmetics Division - L'Oreal | LinkedIn",                     "url": "https://www.linkedin.com/in/brigitte-liberman/"},
    {"title": "Alexis Perakis-Valat - President Consumer Products Asia Pacific - L'Oreal | LinkedIn",            "url": "https://www.linkedin.com/in/alexis-perakis-valat/"},
], min_required=3, max_keep=10))

# American Express — different from Fortune 20 (Steve Squeri, Jeff Campbell, etc.)
print("American Express:", ingest_profiles("American Express", [
    {"title": "Howard Grosfield - President US Consumer Services - American Express | LinkedIn",           "url": "https://www.linkedin.com/in/howard-grosfield/"},
    {"title": "Anna Marrs - President Commercial Services - American Express | LinkedIn",                  "url": "https://www.linkedin.com/in/anna-marrs/"},
    {"title": "Raymond Joabar - EVP and General Counsel - American Express | LinkedIn",                    "url": "https://www.linkedin.com/in/raymond-joabar/"},
    {"title": "Monique Herena - Chief Colleague Experience Officer - American Express | LinkedIn",         "url": "https://www.linkedin.com/in/monique-herena/"},
    {"title": "Glenda McNeal - President Enterprise Strategic Partnerships - American Express | LinkedIn", "url": "https://www.linkedin.com/in/glenda-mcneal/"},
    {"title": "Denise Pickett - President American Express National Bank - American Express | LinkedIn",   "url": "https://www.linkedin.com/in/denise-pickett/"},
    {"title": "Rupert Keeley - Chief Executive EMEA - American Express | LinkedIn",                       "url": "https://www.linkedin.com/in/rupert-keeley/"},
    {"title": "Thomas Schick - EVP Corporate Affairs - American Express | LinkedIn",                      "url": "https://www.linkedin.com/in/thomas-schick-amex/"},
    {"title": "Kerri Sherrill - Executive Vice President and CTO - American Express | LinkedIn",           "url": "https://www.linkedin.com/in/kerri-sherrill/"},
    {"title": "Sanjay Khosla - President International - American Express | LinkedIn",                    "url": "https://www.linkedin.com/in/sanjay-khosla-amex/"},
], min_required=3, max_keep=10))

# UnitedHealth Group — different from Fortune 20 (Andrew Witty, etc.)
print("UnitedHealth Group:", ingest_profiles("UnitedHealth Group", [
    {"title": "Tim Noel - Chief Executive Officer UnitedHealthcare - UnitedHealth Group | LinkedIn",        "url": "https://www.linkedin.com/in/tim-noel-uhg/"},
    {"title": "Dirk McMahon - President and Chief Operating Officer - UnitedHealth Group | LinkedIn",      "url": "https://www.linkedin.com/in/dirk-mcmahon/"},
    {"title": "Heather Cianfrocco - Chief Executive Officer Optum Rx - UnitedHealth Group | LinkedIn",    "url": "https://www.linkedin.com/in/heather-cianfrocco/"},
    {"title": "Wyatt Decker - Chief Executive Officer Optum Health - UnitedHealth Group | LinkedIn",      "url": "https://www.linkedin.com/in/wyatt-decker/"},
    {"title": "Rebecca Madsen - Chief Consumer Officer - UnitedHealth Group | LinkedIn",                   "url": "https://www.linkedin.com/in/rebecca-madsen/"},
    {"title": "Kelley Aiken - CEO Medicare and Retirement UnitedHealthcare - UnitedHealth Group | LinkedIn","url": "https://www.linkedin.com/in/kelley-aiken/"},
    {"title": "Roger Connor - President Commercial and Individual - UnitedHealthcare | LinkedIn",          "url": "https://www.linkedin.com/in/roger-connor-uhg/"},
    {"title": "Dan Schumacher - Executive Vice President - UnitedHealth Group | LinkedIn",                 "url": "https://www.linkedin.com/in/dan-schumacher-uhg/"},
    {"title": "Adam Park - EVP Enterprise Operations - UnitedHealth Group | LinkedIn",                     "url": "https://www.linkedin.com/in/adam-park-uhg/"},
    {"title": "Greg Servello - VP Strategic Communications - UnitedHealth Group | LinkedIn",               "url": "https://www.linkedin.com/in/greg-servello/"},
], min_required=3, max_keep=10))

# OpenAI — different from Fortune 500 / FV / Batch 3 contacts (Sam Altman, Brad Lightcap, Greg Brockman, etc.)
print("OpenAI:", ingest_profiles("OpenAI", [
    {"title": "Jakub Pachocki - Chief Scientist - OpenAI | LinkedIn",                     "url": "https://www.linkedin.com/in/jakubpachocki/"},
    {"title": "Mark Chen - SVP Research - OpenAI | LinkedIn",                             "url": "https://www.linkedin.com/in/mark-chen-openai/"},
    {"title": "Peter Welinder - VP Product and Partnerships - OpenAI | LinkedIn",         "url": "https://www.linkedin.com/in/peterwelinder/"},
    {"title": "Lindsay McCallum - VP People - OpenAI | LinkedIn",                         "url": "https://www.linkedin.com/in/lindsay-mccallum/"},
    {"title": "Nick Turley - Head of ChatGPT Product - OpenAI | LinkedIn",                "url": "https://www.linkedin.com/in/nick-turley/"},
    {"title": "Lilian Weng - Head of Safety Systems - OpenAI | LinkedIn",                 "url": "https://www.linkedin.com/in/lilian-weng/"},
    {"title": "Evan Morikawa - Head of Engineering - OpenAI | LinkedIn",                  "url": "https://www.linkedin.com/in/evanmorikawa/"},
    {"title": "Joanne Jang - Head of Model Behavior - OpenAI | LinkedIn",                 "url": "https://www.linkedin.com/in/joanne-jang/"},
    {"title": "Josh Tobin - Head of Applied Research - OpenAI | LinkedIn",                "url": "https://www.linkedin.com/in/joshjtobin/"},
    {"title": "Matt Knight - VP Security - OpenAI | LinkedIn",                            "url": "https://www.linkedin.com/in/matt-knight-openai/"},
], min_required=3, max_keep=10))

# Atlassian — brand new to DB
print("Atlassian:", ingest_profiles("Atlassian", [
    {"title": "Mike Cannon-Brookes - Co-Chief Executive Officer and Co-Founder - Atlassian | LinkedIn", "url": "https://www.linkedin.com/in/mikecb/"},
    {"title": "Scott Farquhar - Co-Chief Executive Officer and Co-Founder - Atlassian | LinkedIn",     "url": "https://www.linkedin.com/in/scottfarquhar/"},
    {"title": "Anu Bharadwaj - President - Atlassian | LinkedIn",                                      "url": "https://www.linkedin.com/in/anubharadwaj/"},
    {"title": "Cameron Deatsch - Chief Revenue Officer - Atlassian | LinkedIn",                        "url": "https://www.linkedin.com/in/camerondeatsch/"},
    {"title": "Mike Tria - Chief Financial Officer - Atlassian | LinkedIn",                            "url": "https://www.linkedin.com/in/miketria/"},
    {"title": "Joe Thomas - Chief Technology Officer - Atlassian | LinkedIn",                          "url": "https://www.linkedin.com/in/joethomas-cto/"},
    {"title": "Jamil Valliani - Chief Product Officer - Atlassian | LinkedIn",                         "url": "https://www.linkedin.com/in/jamilvalliani/"},
    {"title": "Bryant Lee - Chief Legal Officer - Atlassian | LinkedIn",                               "url": "https://www.linkedin.com/in/bryantlee/"},
    {"title": "Megan Dillon - Chief People Officer - Atlassian | LinkedIn",                            "url": "https://www.linkedin.com/in/megandillon/"},
    {"title": "Rajeev Rajan - SVP Engineering - Atlassian | LinkedIn",                                 "url": "https://www.linkedin.com/in/rajeev-rajan-atlassian/"},
], min_required=3, max_keep=10))

# Mondelez — brand new to DB
print("Mondelez:", ingest_profiles("Mondelez", [
    {"title": "Dirk Van de Put - Chairman and Chief Executive Officer - Mondelez International | LinkedIn",          "url": "https://www.linkedin.com/in/dirk-van-de-put/"},
    {"title": "Luca Zaramella - Executive Vice President and CFO - Mondelez International | LinkedIn",               "url": "https://www.linkedin.com/in/luca-zaramella/"},
    {"title": "Paulette Alviti - Executive Vice President and CHRO - Mondelez International | LinkedIn",             "url": "https://www.linkedin.com/in/paulettealviti/"},
    {"title": "Gustavo Valle - President North America - Mondelez International | LinkedIn",                         "url": "https://www.linkedin.com/in/gustavo-valle-mondelez/"},
    {"title": "Vinzenz Gruber - President Europe - Mondelez International | LinkedIn",                               "url": "https://www.linkedin.com/in/vinzenz-gruber/"},
    {"title": "Maurizio Brusadelli - President Asia Pacific Middle East and Africa - Mondelez International | LinkedIn","url": "https://www.linkedin.com/in/maurizio-brusadelli/"},
    {"title": "Alejandro Lorenzo - President Latin America - Mondelez International | LinkedIn",                     "url": "https://www.linkedin.com/in/alejandro-lorenzo-mondelez/"},
    {"title": "Glen Walter - EVP Snacking North America - Mondelez International | LinkedIn",                        "url": "https://www.linkedin.com/in/glen-walter/"},
    {"title": "Sandra MacQuillan - Chief Supply Chain Officer - Mondelez International | LinkedIn",                  "url": "https://www.linkedin.com/in/sandra-macquillan/"},
    {"title": "Jonathan Adashek - Chief Communications Officer - Mondelez International | LinkedIn",                 "url": "https://www.linkedin.com/in/jonathanadashek/"},
], min_required=3, max_keep=10))

# Brex — different from Batch 4 (Henrique Dubugras, etc.)
print("Brex:", ingest_profiles("Brex", [
    {"title": "Pedro Franceschi - Co-Founder and President - Brex | LinkedIn",        "url": "https://www.linkedin.com/in/pedrofranceschi/"},
    {"title": "Cosmin Nicolaescu - Chief Technology Officer - Brex | LinkedIn",       "url": "https://www.linkedin.com/in/cosminnicolaescu/"},
    {"title": "Ben Mills - Chief Revenue Officer - Brex | LinkedIn",                  "url": "https://www.linkedin.com/in/benmills-brex/"},
    {"title": "Camila Victorino - Chief People Officer - Brex | LinkedIn",            "url": "https://www.linkedin.com/in/camilavictorino/"},
    {"title": "Ian Sefferman - VP Product - Brex | LinkedIn",                         "url": "https://www.linkedin.com/in/iansefferman/"},
    {"title": "Nikhil Krishnan - VP Engineering - Brex | LinkedIn",                   "url": "https://www.linkedin.com/in/nikhil-krishnan-brex/"},
    {"title": "Amy Sun - Head of Marketing - Brex | LinkedIn",                        "url": "https://www.linkedin.com/in/amysun-brex/"},
    {"title": "Karandeep Anand - President Products and Engineering - Brex | LinkedIn","url": "https://www.linkedin.com/in/karandeepanand/"},
    {"title": "Juan Pablo Montes - VP Finance - Brex | LinkedIn",                     "url": "https://www.linkedin.com/in/juanpablo-montes/"},
    {"title": "Riley Kaminer - Head of Communications - Brex | LinkedIn",             "url": "https://www.linkedin.com/in/rileykaminer/"},
], min_required=3, max_keep=10))

# ── Unused-contact summary ────────────────────────────────────────────────────
print("\n" + "="*60); print("Available unused contacts per company:"); print("="*60)
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
print("\n" + "="*60); print("STEP 4: Personalizing — VO template, exclude already-contacted"); print("="*60)
personalize_once_per_company(campaign_id, SENDER_VALUE_PROP, num_steps=3,
    company_domains=COMPANY_DOMAINS, template="vo",
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
