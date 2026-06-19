from db import get_db
with get_db() as conn:
    for domain in ['nvidia.com','cisco.com','hp.com']:
        rows = conn.execute('SELECT id, name, domain FROM companies WHERE domain=?', (domain,)).fetchall()
        for r in rows:
            cnt = conn.execute('SELECT COUNT(*) as n FROM contacts WHERE company_id=?',(r['id'],)).fetchone()['n']
            used = conn.execute('SELECT COUNT(*) as n FROM send_records sr JOIN contacts ct ON sr.contact_id=ct.id WHERE ct.company_id=?',(r['id'],)).fetchone()['n']
            print(f'{domain}: name="{r["name"]}" contacts={cnt} used={used} id={r["id"][:8]}')
