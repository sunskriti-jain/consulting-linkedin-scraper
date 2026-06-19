import sqlite3
conn = sqlite3.connect('outreach.db')
conn.row_factory = sqlite3.Row
camp = conn.execute("SELECT id, name FROM campaigns WHERE name LIKE '%Fortune 500%'").fetchone()
print(f"Campaign: {camp['name']} ({camp['id']})")
rows = conn.execute("""
    SELECT co.name, co.domain,
           COUNT(DISTINCT sr.id) as sent,
           COUNT(DISTINCT ct.id) as contacts
    FROM send_records sr
    JOIN contacts ct ON sr.contact_id = ct.id
    JOIN companies co ON ct.company_id = co.id
    WHERE sr.campaign_id = ?
    GROUP BY co.id ORDER BY co.name
""", (camp['id'],)).fetchall()
for r in rows:
    print(f"  {r['name']:<30} {r['domain']:<30} sent={r['sent']}  contacts={r['contacts']}")
print(f"\nTotal companies: {len(rows)}")
conn.close()
