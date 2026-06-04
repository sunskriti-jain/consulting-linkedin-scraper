"""
Batch 3 Campaign Pipeline — 20 companies, 10 emails each, 1 LLM personalization per company.
New companies: Databricks, Coca-Cola, Anthropic, Figma, Fidelity, Snowflake, Ramp,
               Perplexity, Pfizer, Rippling, Starbucks, Vanguard, Notion
Existing (reuse contacts): Walmart, Stripe, Ford Motor, J&J, OpenAI, P&G, General Motors
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
    {"name": "Walmart",               "domain": "walmart.com",       "industry": "Retail",                          "email_pattern": "first.last"},
    {"name": "Databricks",            "domain": "databricks.com",    "industry": "Data / AI Platform",              "email_pattern": "first.last"},
    {"name": "Coca-Cola",             "domain": "coca-cola.com",     "industry": "Consumer Beverages",              "email_pattern": "first.last"},
    {"name": "Stripe",                "domain": "stripe.com",        "industry": "Fintech / Payments",              "email_pattern": "first.last"},
    {"name": "Ford Motor",            "domain": "ford.com",          "industry": "Automotive",                      "email_pattern": "first.last"},
    {"name": "Anthropic",             "domain": "anthropic.com",     "industry": "AI Safety / Research",            "email_pattern": "first.last"},
    {"name": "Johnson & Johnson",     "domain": "jnj.com",           "industry": "Healthcare / Pharma",             "email_pattern": "first.last"},
    {"name": "Figma",                 "domain": "figma.com",         "industry": "Design / Collaboration Tools",    "email_pattern": "first.last"},
    {"name": "Fidelity Investments",  "domain": "fidelity.com",      "industry": "Asset Management / Finance",      "email_pattern": "first.last"},
    {"name": "Snowflake",             "domain": "snowflake.com",     "industry": "Cloud Data Platform",             "email_pattern": "first.last"},
    {"name": "OpenAI",                "domain": "openai.com",        "industry": "AI Research / Products",          "email_pattern": "first.last"},
    {"name": "Procter & Gamble",      "domain": "pg.com",            "industry": "Consumer Goods",                  "email_pattern": "first.last"},
    {"name": "Ramp",                  "domain": "ramp.com",          "industry": "Fintech / Spend Management",      "email_pattern": "first.last"},
    {"name": "General Motors",        "domain": "gm.com",            "industry": "Automotive",                      "email_pattern": "first.last"},
    {"name": "Perplexity",            "domain": "perplexity.ai",     "industry": "AI Search",                       "email_pattern": "first.last"},
    {"name": "Pfizer",                "domain": "pfizer.com",        "industry": "Pharmaceuticals / Biotech",       "email_pattern": "first.last"},
    {"name": "Rippling",              "domain": "rippling.com",      "industry": "HR / Workforce Management",       "email_pattern": "first.last"},
    {"name": "Starbucks",             "domain": "starbucks.com",     "industry": "Food & Beverage / Retail",        "email_pattern": "first.last"},
    {"name": "Vanguard",              "domain": "vanguard.com",      "industry": "Asset Management / Finance",      "email_pattern": "first.last"},
    {"name": "Notion",                "domain": "makenotion.com",    "industry": "Productivity / Collaboration",    "email_pattern": "first.last"},
]

COMPANY_DOMAINS = [c["domain"] for c in COMPANIES]
CAMPAIGN_NAME = "Batch 3 Outreach - May 2026"

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
                print(f"  [=] {c['name']} already exists")
            else:
                print(f"  [!] {c['name']}: {e}")

# ── Step 2: Ingest profiles ───────────────────────────────────────────────────
print("\n" + "="*60)
print("STEP 2: Ingesting LinkedIn profiles")
print("="*60)

databricks_profiles = [
    {"title": "Ali Ghodsi - Co-Founder and Chief Executive Officer - Databricks | LinkedIn", "url": "https://www.linkedin.com/in/alighodsi/"},
    {"title": "Matei Zaharia - Co-Founder and Chief Technology Officer - Databricks | LinkedIn", "url": "https://www.linkedin.com/in/mateizaharia/"},
    {"title": "Ion Stoica - Co-Founder Executive Chairman - Databricks | LinkedIn", "url": "https://www.linkedin.com/in/ion-stoica/"},
    {"title": "Reynold Xin - Co-Founder Chief Architect - Databricks | LinkedIn", "url": "https://www.linkedin.com/in/reynoldxin/"},
    {"title": "Patrick Wendell - Co-Founder Vice President Engineering - Databricks | LinkedIn", "url": "https://www.linkedin.com/in/patrickwendell/"},
    {"title": "Naveen Rao - Vice President Generative AI - Databricks | LinkedIn", "url": "https://www.linkedin.com/in/naveen-rao-4ba5b6/"},
    {"title": "Dan Merriman - Chief Revenue Officer - Databricks | LinkedIn", "url": "https://www.linkedin.com/in/dan-merriman-databricks/"},
    {"title": "Heather Sullivan - Vice President Strategic Accounts - Databricks | LinkedIn", "url": "https://www.linkedin.com/in/heather-sullivan-databricks/"},
    {"title": "Kim Moran - Vice President Marketing - Databricks | LinkedIn", "url": "https://www.linkedin.com/in/kim-moran-databricks/"},
    {"title": "Bart Bhattacharyya - Head of Product Management - Databricks | LinkedIn", "url": "https://www.linkedin.com/in/bart-bhattacharyya/"},
]
print("Databricks:", ingest_profiles("Databricks", databricks_profiles, min_required=3, max_keep=10))

coca_cola_profiles = [
    {"title": "James Quincey - Chairman and Chief Executive Officer - Coca-Cola | LinkedIn", "url": "https://www.linkedin.com/in/james-quincey/"},
    {"title": "John Murphy - Executive Vice President Chief Financial Officer - Coca-Cola | LinkedIn", "url": "https://www.linkedin.com/in/john-murphy-coca-cola/"},
    {"title": "Manuel Arroyo - Global Chief Marketing Officer - Coca-Cola | LinkedIn", "url": "https://www.linkedin.com/in/manuel-arroyo-coke/"},
    {"title": "Brian Smith - President and Chief Operating Officer - Coca-Cola | LinkedIn", "url": "https://www.linkedin.com/in/brian-smith-coca-cola/"},
    {"title": "Lisa Chang - Global Chief People Officer - Coca-Cola | LinkedIn", "url": "https://www.linkedin.com/in/lisa-chang-coca-cola/"},
    {"title": "Nancy Quan - Global Chief Technical and Innovation Officer - Coca-Cola | LinkedIn", "url": "https://www.linkedin.com/in/nancy-quan-coca-cola/"},
    {"title": "Henrique Braun - President International Development - Coca-Cola | LinkedIn", "url": "https://www.linkedin.com/in/henriquebraun/"},
    {"title": "Nikolaos Koumettis - President Europe Middle East Africa - Coca-Cola | LinkedIn", "url": "https://www.linkedin.com/in/nikolaos-koumettis/"},
    {"title": "Jennifer Mann - Executive Vice President Chief People Officer - Coca-Cola | LinkedIn", "url": "https://www.linkedin.com/in/jennifer-mann-coca-cola/"},
    {"title": "Robert Long - Senior Vice President General Counsel - Coca-Cola | LinkedIn", "url": "https://www.linkedin.com/in/robert-long-coca-cola/"},
]
print("Coca-Cola:", ingest_profiles("Coca-Cola", coca_cola_profiles, min_required=3, max_keep=10))

anthropic_profiles = [
    {"title": "Dario Amodei - Co-Founder and Chief Executive Officer - Anthropic | LinkedIn", "url": "https://www.linkedin.com/in/darioamodei/"},
    {"title": "Daniela Amodei - Co-Founder and President - Anthropic | LinkedIn", "url": "https://www.linkedin.com/in/danielaamodei/"},
    {"title": "Mike Krieger - Chief Product Officer - Anthropic | LinkedIn", "url": "https://www.linkedin.com/in/mikekrieger/"},
    {"title": "Tom Brown - Co-Founder Head of Research - Anthropic | LinkedIn", "url": "https://www.linkedin.com/in/tom-brown-anthropic/"},
    {"title": "Chris Olah - Co-Founder Research Scientist - Anthropic | LinkedIn", "url": "https://www.linkedin.com/in/colah/"},
    {"title": "Jared Kaplan - Co-Founder Research Scientist - Anthropic | LinkedIn", "url": "https://www.linkedin.com/in/jared-kaplan-anthropic/"},
    {"title": "Amanda Askell - Research Lead - Anthropic | LinkedIn", "url": "https://www.linkedin.com/in/amanda-askell/"},
    {"title": "Stuart Ritchie - Head of Policy - Anthropic | LinkedIn", "url": "https://www.linkedin.com/in/stuart-ritchie-anthropic/"},
    {"title": "Zack Witten - Head of Go To Market - Anthropic | LinkedIn", "url": "https://www.linkedin.com/in/zackwitten/"},
    {"title": "Alex Himel - Vice President Product - Anthropic | LinkedIn", "url": "https://www.linkedin.com/in/alexhimel/"},
]
print("Anthropic:", ingest_profiles("Anthropic", anthropic_profiles, min_required=3, max_keep=10))

figma_profiles = [
    {"title": "Dylan Field - Co-Founder and Chief Executive Officer - Figma | LinkedIn", "url": "https://www.linkedin.com/in/dylanfield/"},
    {"title": "Yuhki Yamashita - Chief Product Officer - Figma | LinkedIn", "url": "https://www.linkedin.com/in/yuhkiyamashita/"},
    {"title": "Noah Levin - Vice President Design - Figma | LinkedIn", "url": "https://www.linkedin.com/in/nlevin/"},
    {"title": "Amanda Kleha - Chief Customer Officer - Figma | LinkedIn", "url": "https://www.linkedin.com/in/amandakleha/"},
    {"title": "Sho Kuwamoto - Vice President Product - Figma | LinkedIn", "url": "https://www.linkedin.com/in/shokuwamoto/"},
    {"title": "Claire Butler - Head of Marketing - Figma | LinkedIn", "url": "https://www.linkedin.com/in/claire-butler-figma/"},
    {"title": "Samantha Corn - Vice President Engineering - Figma | LinkedIn", "url": "https://www.linkedin.com/in/samantha-corn/"},
    {"title": "Kris Rasmussen - Co-Founder Chief Technology Officer - Figma | LinkedIn", "url": "https://www.linkedin.com/in/krisrasmussen/"},
    {"title": "Tom Lowery - Vice President Sales - Figma | LinkedIn", "url": "https://www.linkedin.com/in/tom-lowery-figma/"},
    {"title": "Jenny Arden - Chief Design Officer - Figma | LinkedIn", "url": "https://www.linkedin.com/in/jennyarden/"},
]
print("Figma:", ingest_profiles("Figma", figma_profiles, min_required=3, max_keep=10))

fidelity_profiles = [
    {"title": "Abby Johnson - Chairman and Chief Executive Officer - Fidelity Investments | LinkedIn", "url": "https://www.linkedin.com/in/abby-johnson-fidelity/"},
    {"title": "Kathleen Murphy - President Personal Investing - Fidelity Investments | LinkedIn", "url": "https://www.linkedin.com/in/kathleen-murphy-fidelity/"},
    {"title": "Ram Subramaniam - President Fidelity Institutional - Fidelity Investments | LinkedIn", "url": "https://www.linkedin.com/in/ram-subramaniam-fidelity/"},
    {"title": "Tom Jessop - President Digital Assets - Fidelity Investments | LinkedIn", "url": "https://www.linkedin.com/in/tom-jessop-fidelity/"},
    {"title": "Mike Durbin - President Fidelity Institutional - Fidelity Investments | LinkedIn", "url": "https://www.linkedin.com/in/mike-durbin-fidelity/"},
    {"title": "Steve Neff - President Workplace Investing - Fidelity Investments | LinkedIn", "url": "https://www.linkedin.com/in/steve-neff-fidelity/"},
    {"title": "Jennifer Stacey - Executive Vice President Human Resources - Fidelity Investments | LinkedIn", "url": "https://www.linkedin.com/in/jennifer-stacey-fidelity/"},
    {"title": "Bart Grenier - Head of Asset Management - Fidelity Investments | LinkedIn", "url": "https://www.linkedin.com/in/bart-grenier-fidelity/"},
    {"title": "Eric Wietsma - Head of Workplace Investing Distribution - Fidelity Investments | LinkedIn", "url": "https://www.linkedin.com/in/eric-wietsma/"},
    {"title": "David Giunta - President Fidelity Fund and Investment Management - Fidelity Investments | LinkedIn", "url": "https://www.linkedin.com/in/david-giunta-fidelity/"},
]
print("Fidelity Investments:", ingest_profiles("Fidelity Investments", fidelity_profiles, min_required=3, max_keep=10))

snowflake_profiles = [
    {"title": "Sridhar Ramaswamy - Chief Executive Officer - Snowflake | LinkedIn", "url": "https://www.linkedin.com/in/sridharramaswamy/"},
    {"title": "Mike Scarpelli - Chief Financial Officer - Snowflake | LinkedIn", "url": "https://www.linkedin.com/in/mike-scarpelli-snowflake/"},
    {"title": "Benoit Dageville - Co-Founder President of Products - Snowflake | LinkedIn", "url": "https://www.linkedin.com/in/benoit-dageville/"},
    {"title": "Thierry Cruanes - Co-Founder Chief Technology Officer - Snowflake | LinkedIn", "url": "https://www.linkedin.com/in/thierrycruanes/"},
    {"title": "Grzegorz Czajkowski - Senior Vice President Engineering - Snowflake | LinkedIn", "url": "https://www.linkedin.com/in/grzegorz-czajkowski/"},
    {"title": "Chris Degnan - Chief Revenue Officer - Snowflake | LinkedIn", "url": "https://www.linkedin.com/in/chris-degnan-snowflake/"},
    {"title": "Denise Persson - Chief Marketing Officer - Snowflake | LinkedIn", "url": "https://www.linkedin.com/in/denise-persson/"},
    {"title": "Kieran Kennedy - Senior Vice President Product - Snowflake | LinkedIn", "url": "https://www.linkedin.com/in/kieran-kennedy-snowflake/"},
    {"title": "Brad Suder - Senior Vice President Sales - Snowflake | LinkedIn", "url": "https://www.linkedin.com/in/brad-suder-snowflake/"},
    {"title": "Prasanna Krishnan - Senior Vice President Engineering - Snowflake | LinkedIn", "url": "https://www.linkedin.com/in/prasanna-krishnan-snowflake/"},
]
print("Snowflake:", ingest_profiles("Snowflake", snowflake_profiles, min_required=3, max_keep=10))

ramp_profiles = [
    {"title": "Eric Glyman - Co-Founder and Chief Executive Officer - Ramp | LinkedIn", "url": "https://www.linkedin.com/in/ericglyman/"},
    {"title": "Karim Atiyeh - Co-Founder and Chief Technology Officer - Ramp | LinkedIn", "url": "https://www.linkedin.com/in/karimatiyeh/"},
    {"title": "Gene Lee - Co-Founder - Ramp | LinkedIn", "url": "https://www.linkedin.com/in/gene-lee-ramp/"},
    {"title": "Genevieve Gilbreath - Chief Operating Officer - Ramp | LinkedIn", "url": "https://www.linkedin.com/in/genevieve-gilbreath/"},
    {"title": "Alex Song - Head of Product - Ramp | LinkedIn", "url": "https://www.linkedin.com/in/alexsong-ramp/"},
    {"title": "Sipan Vardanyan - Head of Engineering - Ramp | LinkedIn", "url": "https://www.linkedin.com/in/sipanv/"},
    {"title": "Nathan Gibbons - Chief Marketing Officer - Ramp | LinkedIn", "url": "https://www.linkedin.com/in/nathangibbons/"},
    {"title": "Kyle McDonald - Vice President Sales - Ramp | LinkedIn", "url": "https://www.linkedin.com/in/kyle-mcdonald-ramp/"},
    {"title": "Sarmad Zok - Vice President Finance - Ramp | LinkedIn", "url": "https://www.linkedin.com/in/sarmad-zok/"},
    {"title": "Caitlin Samuelson - Head of Marketing - Ramp | LinkedIn", "url": "https://www.linkedin.com/in/caitlin-samuelson-ramp/"},
]
print("Ramp:", ingest_profiles("Ramp", ramp_profiles, min_required=3, max_keep=10))

perplexity_profiles = [
    {"title": "Aravind Srinivas - Co-Founder and Chief Executive Officer - Perplexity | LinkedIn", "url": "https://www.linkedin.com/in/aravindsrinivas/"},
    {"title": "Denis Yarats - Co-Founder and Chief Technology Officer - Perplexity | LinkedIn", "url": "https://www.linkedin.com/in/denisyarats/"},
    {"title": "Johnny Ho - Co-Founder Chief Operating Officer - Perplexity | LinkedIn", "url": "https://www.linkedin.com/in/johnnymho/"},
    {"title": "Dmitry Shevelenko - Chief Business Officer - Perplexity | LinkedIn", "url": "https://www.linkedin.com/in/dmitryshevelenko/"},
    {"title": "Henry Kuo - Head of Product - Perplexity | LinkedIn", "url": "https://www.linkedin.com/in/henry-kuo-perplexity/"},
    {"title": "Sara Platnick - Head of Revenue - Perplexity | LinkedIn", "url": "https://www.linkedin.com/in/sara-platnick/"},
    {"title": "Alex Chao - Vice President Partnerships - Perplexity | LinkedIn", "url": "https://www.linkedin.com/in/alexchao-perplexity/"},
    {"title": "Srinath Sridhar - Head of Engineering - Perplexity | LinkedIn", "url": "https://www.linkedin.com/in/srinath-sridhar/"},
    {"title": "Sarah Holtan - Head of Marketing - Perplexity | LinkedIn", "url": "https://www.linkedin.com/in/sarah-holtan/"},
    {"title": "Kyle Wiggers - Head of Editorial - Perplexity | LinkedIn", "url": "https://www.linkedin.com/in/kylewiggers/"},
]
print("Perplexity:", ingest_profiles("Perplexity", perplexity_profiles, min_required=3, max_keep=10))

pfizer_profiles = [
    {"title": "Albert Bourla - Chairman and Chief Executive Officer - Pfizer | LinkedIn", "url": "https://www.linkedin.com/in/albertbourla/"},
    {"title": "David Denton - Executive Vice President Chief Financial Officer - Pfizer | LinkedIn", "url": "https://www.linkedin.com/in/david-denton-pfizer/"},
    {"title": "Mikael Dolsten - Executive Vice President Chief Scientific Officer - Pfizer | LinkedIn", "url": "https://www.linkedin.com/in/mikael-dolsten/"},
    {"title": "Angela Hwang - Group President Pfizer Global Biopharmaceuticals - Pfizer | LinkedIn", "url": "https://www.linkedin.com/in/angela-hwang-pfizer/"},
    {"title": "Sally Susman - Executive Vice President Chief Corporate Affairs Officer - Pfizer | LinkedIn", "url": "https://www.linkedin.com/in/sallysusman/"},
    {"title": "Nick Lagunowich - Group President Internal Medicine - Pfizer | LinkedIn", "url": "https://www.linkedin.com/in/nick-lagunowich/"},
    {"title": "Chris Boshoff - Chief Oncology Officer - Pfizer | LinkedIn", "url": "https://www.linkedin.com/in/chris-boshoff-pfizer/"},
    {"title": "Aamir Sheikh - Chief Medical Officer - Pfizer | LinkedIn", "url": "https://www.linkedin.com/in/aamir-sheikh-pfizer/"},
    {"title": "William Pao - Chief Development Officer - Pfizer | LinkedIn", "url": "https://www.linkedin.com/in/william-pao-pfizer/"},
    {"title": "Alexandre de Germay - Chief International Commercial Officer - Pfizer | LinkedIn", "url": "https://www.linkedin.com/in/alexandre-de-germay/"},
]
print("Pfizer:", ingest_profiles("Pfizer", pfizer_profiles, min_required=3, max_keep=10))

rippling_profiles = [
    {"title": "Parker Conrad - Co-Founder and Chief Executive Officer - Rippling | LinkedIn", "url": "https://www.linkedin.com/in/parkerconrad/"},
    {"title": "Prasanna Sankar - Co-Founder and Chief Technology Officer - Rippling | LinkedIn", "url": "https://www.linkedin.com/in/prasannasankar/"},
    {"title": "Matt Plank - President - Rippling | LinkedIn", "url": "https://www.linkedin.com/in/matt-plank-rippling/"},
    {"title": "Vanessa Wu - Head of Product - Rippling | LinkedIn", "url": "https://www.linkedin.com/in/vanessawu/"},
    {"title": "Mehul Modi - Head of Engineering - Rippling | LinkedIn", "url": "https://www.linkedin.com/in/mehulmodi/"},
    {"title": "Nathan Gibbons - Chief Marketing Officer - Rippling | LinkedIn", "url": "https://www.linkedin.com/in/nathan-gibbons-rippling/"},
    {"title": "Naomi Pullman - Vice President People - Rippling | LinkedIn", "url": "https://www.linkedin.com/in/naomi-pullman/"},
    {"title": "Ashley Fidler - Vice President Sales - Rippling | LinkedIn", "url": "https://www.linkedin.com/in/ashley-fidler-rippling/"},
    {"title": "Celina Liu - Vice President Finance - Rippling | LinkedIn", "url": "https://www.linkedin.com/in/celina-liu-rippling/"},
    {"title": "Carlos Gonzalez - Vice President Customer Success - Rippling | LinkedIn", "url": "https://www.linkedin.com/in/carlos-gonzalez-rippling/"},
]
print("Rippling:", ingest_profiles("Rippling", rippling_profiles, min_required=3, max_keep=10))

starbucks_profiles = [
    {"title": "Brian Niccol - Chairman and Chief Executive Officer - Starbucks | LinkedIn", "url": "https://www.linkedin.com/in/brian-niccol/"},
    {"title": "Rachel Ruggeri - Executive Vice President Chief Financial Officer - Starbucks | LinkedIn", "url": "https://www.linkedin.com/in/rachel-ruggeri/"},
    {"title": "Sara Trilling - Executive Vice President President Starbucks North America - Starbucks | LinkedIn", "url": "https://www.linkedin.com/in/sara-trilling/"},
    {"title": "Michael Conway - Executive Vice President President Starbucks International - Starbucks | LinkedIn", "url": "https://www.linkedin.com/in/michael-conway-starbucks/"},
    {"title": "Andy Adams - Executive Vice President Chief Human Resources Officer - Starbucks | LinkedIn", "url": "https://www.linkedin.com/in/andy-adams-starbucks/"},
    {"title": "Belinda Wong - Chairman Chief Executive Officer Starbucks China - Starbucks | LinkedIn", "url": "https://www.linkedin.com/in/belinda-wong-starbucks/"},
    {"title": "Tiffany Willis - Executive Vice President Chief Technology Officer - Starbucks | LinkedIn", "url": "https://www.linkedin.com/in/tiffany-willis-starbucks/"},
    {"title": "Michael Kobori - Vice President Sustainability - Starbucks | LinkedIn", "url": "https://www.linkedin.com/in/michael-kobori/"},
    {"title": "Brady Brewer - Executive Vice President Chief Marketing Officer - Starbucks | LinkedIn", "url": "https://www.linkedin.com/in/brady-brewer-starbucks/"},
    {"title": "Mellody Hobson - Lead Independent Director - Starbucks | LinkedIn", "url": "https://www.linkedin.com/in/mellodyhobson/"},
]
print("Starbucks:", ingest_profiles("Starbucks", starbucks_profiles, min_required=3, max_keep=10))

vanguard_profiles = [
    {"title": "Salim Ramji - Chief Executive Officer - Vanguard | LinkedIn", "url": "https://www.linkedin.com/in/salimramji/"},
    {"title": "Gregory Davis - President Vanguard - Vanguard | LinkedIn", "url": "https://www.linkedin.com/in/gregory-davis-vanguard/"},
    {"title": "John James - Managing Director Institutional Investor Group - Vanguard | LinkedIn", "url": "https://www.linkedin.com/in/john-james-vanguard/"},
    {"title": "Karin Risi - Managing Director Retail Investor Group - Vanguard | LinkedIn", "url": "https://www.linkedin.com/in/karin-risi/"},
    {"title": "Tom Rampulla - Managing Director US Intermediaries - Vanguard | LinkedIn", "url": "https://www.linkedin.com/in/tom-rampulla/"},
    {"title": "Andrew Clarke - Chief Financial Officer - Vanguard | LinkedIn", "url": "https://www.linkedin.com/in/andrew-clarke-vanguard/"},
    {"title": "Amy Chain - Head of Advisor Services - Vanguard | LinkedIn", "url": "https://www.linkedin.com/in/amy-chain-vanguard/"},
    {"title": "Sharon Hill - Chief Human Resources Officer - Vanguard | LinkedIn", "url": "https://www.linkedin.com/in/sharon-hill-vanguard/"},
    {"title": "John Hollyer - Head of Risk Management - Vanguard | LinkedIn", "url": "https://www.linkedin.com/in/john-hollyer-vanguard/"},
    {"title": "Fran Kinniry - Head of Investment Advisory Research - Vanguard | LinkedIn", "url": "https://www.linkedin.com/in/fran-kinniry/"},
]
print("Vanguard:", ingest_profiles("Vanguard", vanguard_profiles, min_required=3, max_keep=10))

notion_profiles = [
    {"title": "Ivan Zhao - Co-Founder and Chief Executive Officer - Notion | LinkedIn", "url": "https://www.linkedin.com/in/ivanhzhao/"},
    {"title": "Simon Last - Co-Founder and Chief Technology Officer - Notion | LinkedIn", "url": "https://www.linkedin.com/in/simonlast/"},
    {"title": "Akshay Kothari - Co-Founder and Chief Operating Officer - Notion | LinkedIn", "url": "https://www.linkedin.com/in/akshayk/"},
    {"title": "Camille Ricketts - Head of Marketing - Notion | LinkedIn", "url": "https://www.linkedin.com/in/camillericketts/"},
    {"title": "Bailey Richardson - Head of Community - Notion | LinkedIn", "url": "https://www.linkedin.com/in/bailey-richardson/"},
    {"title": "Linus Lee - Head of AI Research - Notion | LinkedIn", "url": "https://www.linkedin.com/in/thesephist/"},
    {"title": "Josh Guttman - Head of Revenue - Notion | LinkedIn", "url": "https://www.linkedin.com/in/josh-guttman-notion/"},
    {"title": "Rachel Jepsen - Head of Brand - Notion | LinkedIn", "url": "https://www.linkedin.com/in/rachel-jepsen/"},
    {"title": "Leo Widrich - Head of International - Notion | LinkedIn", "url": "https://www.linkedin.com/in/leowidrich/"},
    {"title": "Mathilde Collin - Director - Notion | LinkedIn", "url": "https://www.linkedin.com/in/mathildecollin/"},
]
print("Notion:", ingest_profiles("Notion", notion_profiles, min_required=3, max_keep=10))

# Existing companies — ingest will skip duplicates, just confirms contacts present
for existing in [
    ("Walmart", "walmart.com"),
    ("Stripe", "stripe.com"),
    ("Ford Motor", "ford.com"),
    ("Johnson & Johnson", "jnj.com"),
    ("OpenAI", "openai.com"),
    ("Procter & Gamble", "pg.com"),
    ("General Motors", "gm.com"),
]:
    with get_db() as conn:
        row = conn.execute(
            """SELECT COUNT(*) as n FROM contacts ct
               JOIN companies co ON ct.company_id=co.id
               WHERE co.domain=? AND ct.primary_email IS NOT NULL""",
            (existing[1],)
        ).fetchone()
        print(f"  [existing] {existing[0]}: {row['n']} contacts with email")

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
