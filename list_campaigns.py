import sqlite3
conn = sqlite3.connect('outreach.db')
conn.row_factory = sqlite3.Row

campaigns = [
    ('Fortune 20 Tech & Consulting - May 2026', 'f87f5ec4-15f1-4c29-8776-6fb4b13144f2'),
    ('Fortune 40 Campaign - Round 3', '7a9fbfd0-4c04-4d48-9a21-038e8fd9abe2'),
    ('Tech Startup Outreach - May 2026', 'e73a7d98-ccde-4941-95f0-941ebaf0371b'),
    ('Fortune 500 & High Growth Outreach - May 2026', '096c1c9f-c1c1-4a1a-9dd0-7c89762db2c0'),
    ('Batch 3 Outreach - May 2026', '0c30cfee-a976-4f19-9a50-16d1a404ded3'),
]

for name, cid in campaigns:
    rows = conn.execute('''
        SELECT co.name as cname, co.domain as cdomain, COUNT(sr.id) as sent
        FROM send_records sr
        JOIN contacts ct ON sr.contact_id = ct.id
        JOIN companies co ON ct.company_id = co.id
        WHERE sr.campaign_id = ?
        GROUP BY co.id ORDER BY co.name
    ''', (cid,)).fetchall()
    print(f'\n=== {name} ({len(rows)} companies) ===')
    for r in rows:
        print(f'  {r["cname"]:<35} {r["cdomain"]:<30} sent={r["sent"]}')

conn.close()
