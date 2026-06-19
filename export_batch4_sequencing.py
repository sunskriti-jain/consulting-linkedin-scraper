import sys, csv, sqlite3
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CAMPAIGN_ID = "074554f4-7be6-4686-bd78-f5fa1e499afd"

conn = sqlite3.connect("outreach.db")
conn.row_factory = sqlite3.Row

# Contact-level sequencing
rows = conn.execute("""
    SELECT co.name as company, co.domain,
           ct.first_name, ct.last_name, ct.title, ct.primary_email,
           sr.status, sr.sent_at
    FROM send_records sr
    JOIN contacts ct ON sr.contact_id = ct.id
    JOIN companies co ON ct.company_id = co.id
    WHERE sr.campaign_id = ?
    ORDER BY co.name, ct.last_name, ct.first_name
""", (CAMPAIGN_ID,)).fetchall()

with open("batch4_sequencing.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Company", "Contact_First", "Contact_Last", "Title", "Email", "Status", "Sent_At"])
    for r in rows:
        w.writerow([r["company"], r["first_name"], r["last_name"], r["title"],
                    r["primary_email"], r["status"], r["sent_at"] or ""])

print(f"Wrote {len(rows)} rows to batch4_sequencing.csv")

# Summary
summary = conn.execute("""
    SELECT co.name as company, co.domain, COUNT(sr.id) as total_sent
    FROM send_records sr
    JOIN contacts ct ON sr.contact_id = ct.id
    JOIN companies co ON ct.company_id = co.id
    WHERE sr.campaign_id = ?
    GROUP BY co.id ORDER BY co.name
""", (CAMPAIGN_ID,)).fetchall()

with open("batch4_summary.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Company", "Total_Sent", "Domain"])
    for r in summary:
        w.writerow([r["company"], r["total_sent"], r["domain"]])

conn.close()

# Print tables
print("\n=== BATCH 4 SUMMARY ===")
print(f"{'Company':<25} {'Sent':>6}  {'Domain'}")
print("-" * 60)
for r in summary:
    print(f"{r['company']:<25} {r['total_sent']:>6}  {r['domain']}")
print(f"\n{'TOTAL':<25} {sum(r['total_sent'] for r in summary):>6}")

print("\n=== BATCH 4 SEQUENCING (first 20 rows) ===")
print(f"{'Company':<20} {'First':<12} {'Last':<16} {'Title':<35} {'Email'}")
print("-" * 110)
for r in rows[:20]:
    title = (r['title'] or '')[:33]
    print(f"{r['company']:<20} {r['first_name']:<12} {r['last_name']:<16} {title:<35} {r['primary_email']}")
print(f"... {len(rows)} total rows in batch4_sequencing.csv")
