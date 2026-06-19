import sqlite3
conn = sqlite3.connect('outreach.db')
conn.row_factory = sqlite3.Row
domains = ['rtx.com','travelers.com','anthem.com','conocophillips.com','xpo.com','sysco.com',
           'disney.com','nike.com','3m.com','plaid.com','linear.app','brex.com',
           'retool.com','cohere.com','amplitude.com']
ph = ','.join('?' * len(domains))
sql = (
    "SELECT co.name, co.domain, COUNT(ct.id) as total, "
    "SUM(CASE WHEN ct.primary_email IS NOT NULL AND ct.primary_email != '' THEN 1 ELSE 0 END) as with_email "
    "FROM companies co LEFT JOIN contacts ct ON ct.company_id=co.id "
    f"WHERE co.domain IN ({ph}) GROUP BY co.id ORDER BY co.name"
)
rows = conn.execute(sql, domains).fetchall()
for r in rows:
    print(dict(r))
conn.close()
