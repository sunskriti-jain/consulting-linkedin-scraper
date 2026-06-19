"""
Re-ingest Nvidia, Cisco, and HP Inc. profiles under the correct existing company records
(NVIDIA / Cisco Systems / HP) that own those domains in the DB.
Then verify contacts are available for the BBS expansion campaign.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from db import get_db
from linkedin_ingest import ingest_profiles

# Confirm the stored names
with get_db() as conn:
    for domain in ['nvidia.com', 'cisco.com', 'hp.com']:
        rows = conn.execute('SELECT id, name FROM companies WHERE domain=?', (domain,)).fetchall()
        print(f"{domain}: {[r['name'] for r in rows]}")

print()

# Re-ingest under the names the DB actually stores
print("Nvidia (stored as NVIDIA):", ingest_profiles("NVIDIA", [
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

print("Cisco (stored as Cisco Systems):", ingest_profiles("Cisco Systems", [
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

print("HP (stored as HP):", ingest_profiles("HP", [
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

# Verify
print("\nVerification:")
with get_db() as conn:
    for domain in ['nvidia.com', 'cisco.com', 'hp.com']:
        rows = conn.execute('SELECT id, name FROM companies WHERE domain=?', (domain,)).fetchall()
        for r in rows:
            cnt = conn.execute('SELECT COUNT(*) as n FROM contacts ct WHERE ct.company_id=? AND ct.primary_email IS NOT NULL AND ct.primary_email!="""',(r['id'],)).fetchone()['n']
            print(f"  {r['name']}: {cnt} contacts with email")
