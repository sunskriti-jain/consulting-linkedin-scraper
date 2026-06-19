"""
BBS Expansion Batch 1 — Berkeley Business Society template on 15 new companies
from the prospect expansion list (Tech Giants, Consulting, Enterprise SaaS).
exclude_contacted=True ensures no person receives a duplicate email.
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
    {"name": "Meta",                       "domain": "meta.com",          "industry": "Social Media / AI / Advertising",    "email_pattern": "first.last"},
    {"name": "Oracle",                     "domain": "oracle.com",        "industry": "Enterprise Cloud / Database",        "email_pattern": "first.last"},
    {"name": "IBM",                        "domain": "ibm.com",           "industry": "Enterprise IT / AI / Consulting",    "email_pattern": "first.last"},
    {"name": "Nvidia",                     "domain": "nvidia.com",        "industry": "AI Chips / Semiconductors",          "email_pattern": "first.last"},
    {"name": "Intel",                      "domain": "intel.com",         "industry": "Semiconductors / Data Center",       "email_pattern": "first.last"},
    {"name": "Cisco",                      "domain": "cisco.com",         "industry": "Networking / Cybersecurity",         "email_pattern": "first.last"},
    {"name": "HP Inc.",                    "domain": "hp.com",            "industry": "Consumer Electronics / Printing",    "email_pattern": "first.last"},
    {"name": "Hewlett Packard Enterprise", "domain": "hpe.com",           "industry": "Enterprise IT / Hybrid Cloud",       "email_pattern": "first.last"},
    {"name": "Adobe",                      "domain": "adobe.com",         "industry": "Creative Cloud / Digital Marketing", "email_pattern": "first.last"},
    {"name": "Accenture",                  "domain": "accenture.com",     "industry": "Management Consulting / Tech Services","email_pattern": "first.last"},
    {"name": "Deloitte",                   "domain": "deloitte.com",      "industry": "Professional Services / Consulting", "email_pattern": "first.last"},
    {"name": "Booz Allen Hamilton",        "domain": "boozallen.com",     "industry": "Defense / Government Consulting",    "email_pattern": "first.last"},
    {"name": "ServiceNow",                 "domain": "servicenow.com",    "industry": "Enterprise SaaS / Workflow Automation","email_pattern": "first.last"},
    {"name": "Workday",                    "domain": "workday.com",       "industry": "HR & Finance Cloud / Enterprise SaaS","email_pattern": "first.last"},
    {"name": "Intuit",                     "domain": "intuit.com",        "industry": "Financial Software / SMB / Consumer","email_pattern": "first.last"},
]

COMPANY_DOMAINS = [c["domain"] for c in COMPANIES]
CAMPAIGN_NAME = "BBS Expansion Batch 1 - June 2026"
SENDER_VALUE_PROP = (
    "Berkeley Business Society is UC Berkeley's oldest and most selective consulting club, "
    "founded in 1999. Our alumni have gone on to lead at McKinsey, Bain, BCG, Goldman Sachs, "
    "Google, Apple, and hundreds of venture-backed startups. We work with companies on "
    "semester-long consulting engagements — market research, growth strategy, product analysis, "
    "and go-to-market planning — delivering Fortune 500-quality work from Berkeley's top "
    "analytical and business talent."
)

print("\n" + "="*60); print("STEP 1: Inserting companies"); print("="*60)
with get_db() as conn:
    for c in COMPANIES:
        try:
            conn.execute(
                "INSERT INTO companies (id,name,domain,industry,email_pattern,email_pattern_confidence) VALUES (?,?,?,?,?,?)",
                (new_id(), c["name"], c["domain"], c["industry"], c["email_pattern"], 70.0))
            print(f"  [+] {c['name']}")
        except Exception as e:
            print(f"  [=] {c['name']} already exists" if "UNIQUE" in str(e).upper() else f"  [!] {e}")

print("\n" + "="*60); print("STEP 2: Ingesting profiles (10 per company)"); print("="*60)

print("Meta:", ingest_profiles("Meta", [
    {"title": "Mark Zuckerberg - Founder and Chief Executive Officer - Meta | LinkedIn",         "url": "https://www.linkedin.com/in/zuck/"},
    {"title": "Javier Olivan - Chief Operating Officer - Meta | LinkedIn",                      "url": "https://www.linkedin.com/in/javierolivan/"},
    {"title": "Susan Li - Chief Financial Officer - Meta | LinkedIn",                           "url": "https://www.linkedin.com/in/susanli-meta/"},
    {"title": "Andrew Bosworth - Chief Technology Officer - Meta | LinkedIn",                   "url": "https://www.linkedin.com/in/andrewbosworth/"},
    {"title": "Chris Cox - Chief Product Officer - Meta | LinkedIn",                            "url": "https://www.linkedin.com/in/chris-cox/"},
    {"title": "Nick Clegg - President Global Affairs - Meta | LinkedIn",                        "url": "https://www.linkedin.com/in/nickclegg/"},
    {"title": "Tom Alison - Head of Facebook - Meta | LinkedIn",                                "url": "https://www.linkedin.com/in/tomalison/"},
    {"title": "Adam Mosseri - Head of Instagram - Meta | LinkedIn",                             "url": "https://www.linkedin.com/in/adammosseri/"},
    {"title": "Naomi Gleit - VP Product and Head of Social Impact - Meta | LinkedIn",           "url": "https://www.linkedin.com/in/naomigleit/"},
    {"title": "Nicola Mendelsohn - VP Global Business Group - Meta | LinkedIn",                 "url": "https://www.linkedin.com/in/nicolamendelsohn/"},
], min_required=3, max_keep=10))

print("Oracle:", ingest_profiles("Oracle", [
    {"title": "Safra Catz - Chief Executive Officer - Oracle | LinkedIn",                        "url": "https://www.linkedin.com/in/safra-catz/"},
    {"title": "Larry Ellison - Chairman and Chief Technology Officer - Oracle | LinkedIn",       "url": "https://www.linkedin.com/in/larry-ellison/"},
    {"title": "Ken Glueck - Executive Vice President - Oracle | LinkedIn",                      "url": "https://www.linkedin.com/in/kenglueck/"},
    {"title": "Clay Magouyrk - Executive Vice President Oracle Cloud Infrastructure - Oracle | LinkedIn","url": "https://www.linkedin.com/in/claymagouyrk/"},
    {"title": "Steve Miranda - Executive Vice President Applications Development - Oracle | LinkedIn","url": "https://www.linkedin.com/in/stevemiranda/"},
    {"title": "Mike Sicilia - Executive Vice President Industries - Oracle | LinkedIn",          "url": "https://www.linkedin.com/in/mikesicilia/"},
    {"title": "Dorian Daley - Executive Vice President General Counsel - Oracle | LinkedIn",    "url": "https://www.linkedin.com/in/doriandaley/"},
    {"title": "Juan Loaiza - Executive Vice President Mission Critical DB Technologies - Oracle | LinkedIn","url": "https://www.linkedin.com/in/juanloaiza/"},
    {"title": "Doug Kehring - Executive Vice President Operations - Oracle | LinkedIn",          "url": "https://www.linkedin.com/in/dougkehring/"},
    {"title": "Reggie Bradford - SVP Product Development - Oracle | LinkedIn",                  "url": "https://www.linkedin.com/in/reggiebradford/"},
], min_required=3, max_keep=10))

print("IBM:", ingest_profiles("IBM", [
    {"title": "Arvind Krishna - Chairman and Chief Executive Officer - IBM | LinkedIn",         "url": "https://www.linkedin.com/in/arvind-krishna/"},
    {"title": "Jim Kavanaugh - Senior Vice President and Chief Financial Officer - IBM | LinkedIn","url": "https://www.linkedin.com/in/jim-kavanaugh-ibm/"},
    {"title": "Rob Thomas - Senior Vice President Software and Chief Commercial Officer - IBM | LinkedIn","url": "https://www.linkedin.com/in/rob-thomas-ibm/"},
    {"title": "Dinesh Nirmal - Senior Vice President IBM Software - IBM | LinkedIn",            "url": "https://www.linkedin.com/in/dineshnirmal/"},
    {"title": "Dario Gil - Senior Vice President Research - IBM | LinkedIn",                   "url": "https://www.linkedin.com/in/dariogil/"},
    {"title": "Nickle LaMoreaux - Chief Human Resources Officer - IBM | LinkedIn",             "url": "https://www.linkedin.com/in/nicklela/"},
    {"title": "Howard Boville - Senior Vice President IBM Cloud - IBM | LinkedIn",             "url": "https://www.linkedin.com/in/howardboville/"},
    {"title": "Jonathan Adashek - Senior Vice President Marketing and Communications - IBM | LinkedIn","url": "https://www.linkedin.com/in/jonathanadashek/"},
    {"title": "Gary Cohn - Vice Chairman - IBM | LinkedIn",                                    "url": "https://www.linkedin.com/in/gary-cohn/"},
    {"title": "Bridget van Kralingen - Former Senior Vice President - IBM | LinkedIn",          "url": "https://www.linkedin.com/in/bridgetvankralingen/"},
], min_required=3, max_keep=10))

print("Nvidia:", ingest_profiles("Nvidia", [
    {"title": "Jensen Huang - Founder and Chief Executive Officer - Nvidia | LinkedIn",         "url": "https://www.linkedin.com/in/jenhsunhuang/"},
    {"title": "Colette Kress - Executive Vice President and CFO - Nvidia | LinkedIn",          "url": "https://www.linkedin.com/in/coletteakress/"},
    {"title": "Debora Shoquist - Executive Vice President Operations - Nvidia | LinkedIn",     "url": "https://www.linkedin.com/in/debora-shoquist/"},
    {"title": "Jay Puri - Executive VP Worldwide Field Operations - Nvidia | LinkedIn",        "url": "https://www.linkedin.com/in/jaypuri/"},
    {"title": "Bill Dally - Chief Scientist and SVP Research - Nvidia | LinkedIn",             "url": "https://www.linkedin.com/in/billdally/"},
    {"title": "Jeff Fisher - Senior VP Gaming - Nvidia | LinkedIn",                            "url": "https://www.linkedin.com/in/jeff-fisher-nvidia/"},
    {"title": "Manuvir Das - Vice President Enterprise Computing - Nvidia | LinkedIn",         "url": "https://www.linkedin.com/in/manuvirdas/"},
    {"title": "Ian Buck - Vice President Hyperscale and HPC - Nvidia | LinkedIn",             "url": "https://www.linkedin.com/in/ianbuck/"},
    {"title": "Ali Kani - Vice President and GM Automotive - Nvidia | LinkedIn",              "url": "https://www.linkedin.com/in/alikani/"},
    {"title": "Marc Hamilton - Vice President Solutions Architecture - Nvidia | LinkedIn",     "url": "https://www.linkedin.com/in/marchamilton/"},
], min_required=3, max_keep=10))

print("Intel:", ingest_profiles("Intel", [
    {"title": "Lip-Bu Tan - Chief Executive Officer - Intel | LinkedIn",                       "url": "https://www.linkedin.com/in/lipbu-tan/"},
    {"title": "David Zinsner - Executive Vice President and CFO - Intel | LinkedIn",           "url": "https://www.linkedin.com/in/david-zinsner/"},
    {"title": "Michelle Johnston Holthaus - CEO Intel Products - Intel | LinkedIn",            "url": "https://www.linkedin.com/in/michelle-holthaus/"},
    {"title": "Greg Lavender - Chief Technology Officer and SVP - Intel | LinkedIn",           "url": "https://www.linkedin.com/in/greg-lavender/"},
    {"title": "Keyvan Esfarjani - Executive Vice President Manufacturing - Intel | LinkedIn",  "url": "https://www.linkedin.com/in/keyvanesfarjani/"},
    {"title": "Ann Kelleher - Executive Vice President Technology Development - Intel | LinkedIn","url": "https://www.linkedin.com/in/ann-kelleher/"},
    {"title": "Sandra Rivera - Executive Vice President and GM Data Center - Intel | LinkedIn","url": "https://www.linkedin.com/in/sandrarivera/"},
    {"title": "Nick McKeown - Senior Vice President Network and Edge - Intel | LinkedIn",     "url": "https://www.linkedin.com/in/nickmckeown/"},
    {"title": "Christoph Schell - Chief Commercial Officer - Intel | LinkedIn",               "url": "https://www.linkedin.com/in/christophschell/"},
    {"title": "Stuart Pann - Chief People Officer - Intel | LinkedIn",                        "url": "https://www.linkedin.com/in/stuartpann/"},
], min_required=3, max_keep=10))

print("Cisco:", ingest_profiles("Cisco", [
    {"title": "Chuck Robbins - Chair and Chief Executive Officer - Cisco | LinkedIn",           "url": "https://www.linkedin.com/in/chuckrobbins/"},
    {"title": "Scott Herren - Executive Vice President and CFO - Cisco | LinkedIn",            "url": "https://www.linkedin.com/in/scott-herren/"},
    {"title": "Jeetu Patel - President and Chief Product Officer - Cisco | LinkedIn",          "url": "https://www.linkedin.com/in/jeetupatel1/"},
    {"title": "Mark Patterson - Executive Vice President and COO - Cisco | LinkedIn",          "url": "https://www.linkedin.com/in/mark-patterson-cisco/"},
    {"title": "Francine Katsoudas - EVP and Chief People Policy Officer - Cisco | LinkedIn",   "url": "https://www.linkedin.com/in/fkatsoudas/"},
    {"title": "Tom Gillis - Senior Vice President Security Business Group - Cisco | LinkedIn", "url": "https://www.linkedin.com/in/tom-gillis/"},
    {"title": "Jonathan Davidson - EVP Networking - Cisco | LinkedIn",                         "url": "https://www.linkedin.com/in/jonathan-davidson-cisco/"},
    {"title": "Liz Centoni - EVP Chief Strategy Officer - Cisco | LinkedIn",                   "url": "https://www.linkedin.com/in/lizcentoni/"},
    {"title": "Jeff Sharritts - EVP Chief Customer and Partner Officer - Cisco | LinkedIn",    "url": "https://www.linkedin.com/in/jeffsharritts/"},
    {"title": "Todd Nightingale - EVP Cisco Networking - Cisco | LinkedIn",                    "url": "https://www.linkedin.com/in/toddnightingale/"},
], min_required=3, max_keep=10))

print("HP Inc.:", ingest_profiles("HP Inc.", [
    {"title": "Enrique Lores - President and Chief Executive Officer - HP Inc. | LinkedIn",    "url": "https://www.linkedin.com/in/enrique-lores/"},
    {"title": "Karen Parkhill - Executive Vice President and CFO - HP Inc. | LinkedIn",        "url": "https://www.linkedin.com/in/karenparkhill/"},
    {"title": "Alex Cho - President Personal Systems - HP Inc. | LinkedIn",                    "url": "https://www.linkedin.com/in/alexcho-hp/"},
    {"title": "Tuan Tran - President Imaging Printing and Solutions - HP Inc. | LinkedIn",     "url": "https://www.linkedin.com/in/tuantran-hp/"},
    {"title": "Tolga Kurtoglu - Chief Technology Officer - HP Inc. | LinkedIn",               "url": "https://www.linkedin.com/in/tolgakurtoglu/"},
    {"title": "Julie Jacobs - Executive Vice President and General Counsel - HP Inc. | LinkedIn","url": "https://www.linkedin.com/in/juliejacobs-hp/"},
    {"title": "Dave Shull - President HP Services - HP Inc. | LinkedIn",                      "url": "https://www.linkedin.com/in/daveshull/"},
    {"title": "Kristen Ludgate - Chief People Officer - HP Inc. | LinkedIn",                  "url": "https://www.linkedin.com/in/kristenludgate/"},
    {"title": "Erin Nealon - Chief Communications Officer - HP Inc. | LinkedIn",              "url": "https://www.linkedin.com/in/erinnealon/"},
    {"title": "Roz Ho - Senior Vice President AI and Analytics - HP Inc. | LinkedIn",         "url": "https://www.linkedin.com/in/rozho/"},
], min_required=3, max_keep=10))

print("Hewlett Packard Enterprise:", ingest_profiles("Hewlett Packard Enterprise", [
    {"title": "Antonio Neri - President and Chief Executive Officer - HPE | LinkedIn",          "url": "https://www.linkedin.com/in/antonioneri/"},
    {"title": "Marie Myers - Chief Financial Officer - HPE | LinkedIn",                        "url": "https://www.linkedin.com/in/mariemyers/"},
    {"title": "Fidelma Russo - EVP and CTO Hybrid Cloud - HPE | LinkedIn",                    "url": "https://www.linkedin.com/in/fidelmarusso/"},
    {"title": "Neil MacDonald - Chief Technology Officer - HPE | LinkedIn",                    "url": "https://www.linkedin.com/in/neilmacdonald-hpe/"},
    {"title": "Phil Davis - President HPE Server Business - HPE | LinkedIn",                   "url": "https://www.linkedin.com/in/phil-davis-hpe/"},
    {"title": "Tom Black - Senior Vice President Compute - HPE | LinkedIn",                    "url": "https://www.linkedin.com/in/tom-black-hpe/"},
    {"title": "Simon Ewington - VP Global Channel and Partner Ecosystem - HPE | LinkedIn",     "url": "https://www.linkedin.com/in/simonewington/"},
    {"title": "Alain Andreoli - Board Chair - HPE | LinkedIn",                                "url": "https://www.linkedin.com/in/alainandreoliboard/"},
    {"title": "Dirk Van den Berghe - Chief Revenue Officer - HPE | LinkedIn",                 "url": "https://www.linkedin.com/in/dirkvandenberghe/"},
    {"title": "Gerd Cordes - Senior VP Intelligent Edge - HPE | LinkedIn",                    "url": "https://www.linkedin.com/in/gerd-cordes/"},
], min_required=3, max_keep=10))

print("Adobe:", ingest_profiles("Adobe", [
    {"title": "Shantanu Narayen - Chair and Chief Executive Officer - Adobe | LinkedIn",        "url": "https://www.linkedin.com/in/shantanunarayen/"},
    {"title": "Dan Durn - Executive VP and Chief Financial Officer - Adobe | LinkedIn",        "url": "https://www.linkedin.com/in/dandurn/"},
    {"title": "David Wadhwani - President Digital Media Business - Adobe | LinkedIn",          "url": "https://www.linkedin.com/in/david-wadhwani/"},
    {"title": "Anil Chakravarthy - President Digital Experience Business - Adobe | LinkedIn",  "url": "https://www.linkedin.com/in/anilchakravarthy/"},
    {"title": "Scott Belsky - Chief Strategy Officer and EVP Design - Adobe | LinkedIn",       "url": "https://www.linkedin.com/in/scottbelsky/"},
    {"title": "Ashley Still - Senior Vice President Creative Cloud - Adobe | LinkedIn",        "url": "https://www.linkedin.com/in/ashleystill/"},
    {"title": "Ann Lewnes - Executive Vice President and CMO - Adobe | LinkedIn",              "url": "https://www.linkedin.com/in/annlewnes/"},
    {"title": "Gloria Chen - Chief People Officer - Adobe | LinkedIn",                        "url": "https://www.linkedin.com/in/gloriachen-adobe/"},
    {"title": "Dana Rao - Executive VP General Counsel and CLO - Adobe | LinkedIn",           "url": "https://www.linkedin.com/in/dana-rao/"},
    {"title": "Anjul Bhambhri - Senior Vice President Artificial Intelligence - Adobe | LinkedIn","url": "https://www.linkedin.com/in/anjulbhambhri/"},
], min_required=3, max_keep=10))

print("Accenture:", ingest_profiles("Accenture", [
    {"title": "Julie Sweet - Chair and Chief Executive Officer - Accenture | LinkedIn",        "url": "https://www.linkedin.com/in/julie-sweet/"},
    {"title": "KC McClure - Chief Financial Officer - Accenture | LinkedIn",                  "url": "https://www.linkedin.com/in/kcmcclure/"},
    {"title": "Paul Daugherty - Chief Technology and Innovation Officer - Accenture | LinkedIn","url": "https://www.linkedin.com/in/paul-r-daugherty/"},
    {"title": "Jack Azagury - Group Chief Executive North America - Accenture | LinkedIn",    "url": "https://www.linkedin.com/in/jackazagury/"},
    {"title": "Manish Sharma - Group Chief Executive Products - Accenture | LinkedIn",        "url": "https://www.linkedin.com/in/manish-sharma-accenture/"},
    {"title": "Ellyn Shook - Chief Leadership and Human Resources Officer - Accenture | LinkedIn","url": "https://www.linkedin.com/in/ellynshook/"},
    {"title": "Jean-Marc Ollagnier - Group Chief Executive Europe - Accenture | LinkedIn",    "url": "https://www.linkedin.com/in/jean-marc-ollagnier/"},
    {"title": "Karthik Narain - Group Chief Executive Technology - Accenture | LinkedIn",     "url": "https://www.linkedin.com/in/karthiknarain/"},
    {"title": "Omar Abbosh - Chief Strategy Officer - Accenture | LinkedIn",                  "url": "https://www.linkedin.com/in/omarabbosh/"},
    {"title": "Bhaskar Ghosh - Group Chief Executive Accenture Strategy - Accenture | LinkedIn","url": "https://www.linkedin.com/in/bhaskar-ghosh/"},
], min_required=3, max_keep=10))

print("Deloitte:", ingest_profiles("Deloitte", [
    {"title": "Joe Ucuzoglu - Global Chief Executive Officer - Deloitte | LinkedIn",           "url": "https://www.linkedin.com/in/joeucuzoglu/"},
    {"title": "Janet Truncale - Chief Executive Officer Deloitte US - Deloitte | LinkedIn",   "url": "https://www.linkedin.com/in/janet-truncale/"},
    {"title": "Lara Abrash - Chair Deloitte US - Deloitte | LinkedIn",                        "url": "https://www.linkedin.com/in/labrash/"},
    {"title": "Dan Helfrich - Chairman Deloitte Consulting - Deloitte | LinkedIn",            "url": "https://www.linkedin.com/in/danhelfrich/"},
    {"title": "Anthony Stephan - Chief AI Officer - Deloitte | LinkedIn",                     "url": "https://www.linkedin.com/in/anthony-stephan/"},
    {"title": "Michele Parmelee - Global Chief People and Purpose Officer - Deloitte | LinkedIn","url": "https://www.linkedin.com/in/micheleparmelee/"},
    {"title": "Punit Renjen - Former Global CEO - Deloitte | LinkedIn",                       "url": "https://www.linkedin.com/in/punitrenjen/"},
    {"title": "Diana Kearns-Manolatos - Center for Technology Media - Deloitte | LinkedIn",   "url": "https://www.linkedin.com/in/diana-kearns-manolatos/"},
    {"title": "Eamonn Kelly - Senior Managing Director - Deloitte | LinkedIn",                "url": "https://www.linkedin.com/in/eamonnkelly/"},
    {"title": "Deborah Golden - US Cyber and Strategic Risk Leader - Deloitte | LinkedIn",    "url": "https://www.linkedin.com/in/deborahgolden/"},
], min_required=3, max_keep=10))

print("Booz Allen Hamilton:", ingest_profiles("Booz Allen Hamilton", [
    {"title": "Horacio Rozanski - President and Chief Executive Officer - Booz Allen Hamilton | LinkedIn","url": "https://www.linkedin.com/in/horaciorozanski/"},
    {"title": "Matthew Calderone - Executive Vice President and CFO - Booz Allen Hamilton | LinkedIn","url": "https://www.linkedin.com/in/matthewcalderone/"},
    {"title": "Karen Dahut - President Government Services - Booz Allen Hamilton | LinkedIn", "url": "https://www.linkedin.com/in/karen-dahut/"},
    {"title": "Susan Penfield - Executive Vice President and CTO - Booz Allen Hamilton | LinkedIn","url": "https://www.linkedin.com/in/susanpenfield/"},
    {"title": "Elizabeth Church - EVP and Chief People Officer - Booz Allen Hamilton | LinkedIn","url": "https://www.linkedin.com/in/elizabeth-church-bah/"},
    {"title": "Jed Dolson - Executive Vice President Defense - Booz Allen Hamilton | LinkedIn","url": "https://www.linkedin.com/in/jeddolson/"},
    {"title": "Patrick McGinnis - EVP National Security - Booz Allen Hamilton | LinkedIn",   "url": "https://www.linkedin.com/in/patrick-mcginnis-bah/"},
    {"title": "Henry Canty - Chief Operating Officer - Booz Allen Hamilton | LinkedIn",      "url": "https://www.linkedin.com/in/henrycanty/"},
    {"title": "Gary Labovich - Senior VP and AI Leader - Booz Allen Hamilton | LinkedIn",    "url": "https://www.linkedin.com/in/garylabovich/"},
    {"title": "Brad Medairy - Executive Vice President - Booz Allen Hamilton | LinkedIn",    "url": "https://www.linkedin.com/in/bradmedairy/"},
], min_required=3, max_keep=10))

print("ServiceNow:", ingest_profiles("ServiceNow", [
    {"title": "Bill McDermott - President and Chief Executive Officer - ServiceNow | LinkedIn","url": "https://www.linkedin.com/in/billmcdermott/"},
    {"title": "Gina Mastantuono - Chief Financial Officer - ServiceNow | LinkedIn",           "url": "https://www.linkedin.com/in/ginamastantuono/"},
    {"title": "CJ Desai - President and Chief Operating Officer - ServiceNow | LinkedIn",    "url": "https://www.linkedin.com/in/cjdesai/"},
    {"title": "Chirantan Desai - Executive VP and Chief Product Officer - ServiceNow | LinkedIn","url": "https://www.linkedin.com/in/chirantandesai/"},
    {"title": "Lara Caimi - Chief Customer and Partner Officer - ServiceNow | LinkedIn",     "url": "https://www.linkedin.com/in/laracaimi/"},
    {"title": "Dave Schneider - President Americas - ServiceNow | LinkedIn",                  "url": "https://www.linkedin.com/in/dave-schneider-servicenow/"},
    {"title": "Paul Smith - President EMEA - ServiceNow | LinkedIn",                         "url": "https://www.linkedin.com/in/paulsmith-servicenow/"},
    {"title": "Amy Lokey - SVP Global Head of People - ServiceNow | LinkedIn",               "url": "https://www.linkedin.com/in/amylokey/"},
    {"title": "Jon Sigler - SVP Platform Engineering - ServiceNow | LinkedIn",               "url": "https://www.linkedin.com/in/jonsigler/"},
    {"title": "Pat Casey - SVP DevOps and IT Operations - ServiceNow | LinkedIn",            "url": "https://www.linkedin.com/in/patcasey/"},
], min_required=3, max_keep=10))

print("Workday:", ingest_profiles("Workday", [
    {"title": "Carl Eschenbach - Chief Executive Officer - Workday | LinkedIn",               "url": "https://www.linkedin.com/in/carleschenbach/"},
    {"title": "Zane Rowe - Chief Financial Officer - Workday | LinkedIn",                    "url": "https://www.linkedin.com/in/zanerowe/"},
    {"title": "Sayan Chakraborty - President Products and Technology - Workday | LinkedIn",  "url": "https://www.linkedin.com/in/sayanchakraborty/"},
    {"title": "Pete Schlampp - EVP and Chief Strategy Officer - Workday | LinkedIn",         "url": "https://www.linkedin.com/in/peteschlampp/"},
    {"title": "Ashley Goldsmith - Chief People Officer - Workday | LinkedIn",                "url": "https://www.linkedin.com/in/ashleygoldsmith/"},
    {"title": "Jim Stratton - Chief Technology Officer - Workday | LinkedIn",                "url": "https://www.linkedin.com/in/jim-stratton-workday/"},
    {"title": "Emma Chalwin - Chief Marketing Officer - Workday | LinkedIn",                 "url": "https://www.linkedin.com/in/emmachalwin/"},
    {"title": "Chandler Morse - VP Corporate Affairs - Workday | LinkedIn",                  "url": "https://www.linkedin.com/in/chandlermorse/"},
    {"title": "Barbry McGann - VP Business Technology - Workday | LinkedIn",                 "url": "https://www.linkedin.com/in/barbry-mcgann/"},
    {"title": "Rich Sauer - Chief Legal Officer - Workday | LinkedIn",                       "url": "https://www.linkedin.com/in/rich-sauer-workday/"},
], min_required=3, max_keep=10))

print("Intuit:", ingest_profiles("Intuit", [
    {"title": "Sasan Goodarzi - Chief Executive Officer - Intuit | LinkedIn",                 "url": "https://www.linkedin.com/in/sasan-goodarzi/"},
    {"title": "Sandeep Aujla - Chief Financial Officer - Intuit | LinkedIn",                 "url": "https://www.linkedin.com/in/sandeep-aujla/"},
    {"title": "Marianna Tessel - EVP and GM Small Business and Self-Employed - Intuit | LinkedIn","url": "https://www.linkedin.com/in/mariannatessel/"},
    {"title": "Alex Balazs - Executive VP and Chief Technology Officer - Intuit | LinkedIn", "url": "https://www.linkedin.com/in/alexbalazs/"},
    {"title": "Mark Notarainni - Executive VP Consumer Group - Intuit | LinkedIn",           "url": "https://www.linkedin.com/in/marknotarainni/"},
    {"title": "Kerry McLean - EVP and General Counsel - Intuit | LinkedIn",                  "url": "https://www.linkedin.com/in/kerry-mclean/"},
    {"title": "Nhung Ho - VP Artificial Intelligence - Intuit | LinkedIn",                   "url": "https://www.linkedin.com/in/nhungho/"},
    {"title": "Humera Malik - VP Data and AI Engineering - Intuit | LinkedIn",               "url": "https://www.linkedin.com/in/humeramalik/"},
    {"title": "Rania Succar - Senior VP and GM Mailchimp - Intuit | LinkedIn",               "url": "https://www.linkedin.com/in/raniasuccar/"},
    {"title": "David Talach - Senior VP Finance TurboTax - Intuit | LinkedIn",               "url": "https://www.linkedin.com/in/davidtalach/"},
], min_required=3, max_keep=10))

# ── Contact availability summary ─────────────────────────────────────────────
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
            print(f"  [{'OK' if cnt >= 5 else 'LOW'}] {row['name']}: {cnt} unused")
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
    queued = conn.execute("SELECT COUNT(*) as n FROM send_records WHERE campaign_id=? AND status='queued'",
        (campaign_id,)).fetchone()["n"]
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
