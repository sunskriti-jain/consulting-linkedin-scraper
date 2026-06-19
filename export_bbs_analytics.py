"""Export BBS-only master sequencing analytics to bbs_master_sequencing.csv."""
import sys, csv, sqlite3
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

OUTPUT_FILE = "bbs_master_sequencing.csv"

conn = sqlite3.connect("outreach.db")
conn.row_factory = sqlite3.Row

# All campaigns — then filter out FV and VO
all_campaigns = conn.execute("SELECT id, name FROM campaigns ORDER BY created_at").fetchall()

bbs_campaigns = [
    c for c in all_campaigns
    if not any(kw in c["name"] for kw in ["FV", "Free Ventures", "Venture Out", " VO "])
    and not c["name"].startswith("VO ")
    and not c["name"].startswith("Venture Out")
]

bbs_ids = [c["id"] for c in bbs_campaigns]
print(f"BBS campaigns ({len(bbs_campaigns)}):")
for c in bbs_campaigns:
    cnt = conn.execute("SELECT COUNT(*) as n FROM send_records WHERE campaign_id=? AND status IN ('sent','bounced','replied')", (c["id"],)).fetchone()["n"]
    print(f"  {c['name']} — {cnt} sent")

if not bbs_ids:
    print("No BBS campaigns found.")
    conn.close()
    sys.exit(1)

placeholders = ",".join("?" * len(bbs_ids))

rows = conn.execute(f"""
    SELECT
        co.name                                                         AS Company,
        co.domain                                                       AS Domain,
        COUNT(sr.id)                                                    AS Total_Sent,
        SUM(CASE WHEN sr.reply_detected_at IS NOT NULL THEN 1 ELSE 0 END) AS Replies,
        SUM(CASE WHEN sr.bounced_at        IS NOT NULL OR
                      sr.delivery_status = 'bounced'  THEN 1 ELSE 0 END) AS Bounces,
        MIN(sr.reply_detected_at)                                       AS First_Reply_Raw,
        GROUP_CONCAT(DISTINCT ca.name)                                  AS Campaigns
    FROM send_records sr
    JOIN contacts  ct ON sr.contact_id  = ct.id
    JOIN companies co ON ct.company_id  = co.id
    JOIN campaigns ca ON sr.campaign_id = ca.id
    WHERE sr.campaign_id IN ({placeholders})
      AND sr.status IN ('sent', 'bounced', 'replied')
    GROUP BY co.id, co.name, co.domain
    ORDER BY Replies DESC, Total_Sent DESC
""", bbs_ids).fetchall()

conn.close()

total_sent = sum(r["Total_Sent"] for r in rows)
total_replies = sum(r["Replies"] for r in rows)
total_bounces = sum(r["Bounces"] for r in rows)

def pct(n, d):
    return f"{n/d*100:.1f}%" if d else "0.0%"

def fmt_date(raw):
    if not raw:
        return ""
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(raw).strftime("%a, %-d %b %Y")
    except Exception:
        return str(raw)[:16]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        f"BBS Master Sequencing — {len(bbs_campaigns)} campaigns — "
        f"{total_sent} sent | {total_replies} replies ({pct(total_replies,total_sent)}) | "
        f"{total_bounces} bounces ({pct(total_bounces,total_sent)})"
    ])
    writer.writerow([])
    writer.writerow(["Company","Domain","Total Sent","Replies","Bounces","Reply %","Bounce %","First Reply Date","Campaign(s)"])
    for r in rows:
        writer.writerow([
            r["Company"], r["Domain"],
            r["Total_Sent"], r["Replies"], r["Bounces"],
            pct(r["Replies"], r["Total_Sent"]),
            pct(r["Bounces"], r["Total_Sent"]),
            fmt_date(r["First_Reply_Raw"]),
            r["Campaigns"],
        ])

print(f"\n[DONE] Wrote {len(rows)} companies to {OUTPUT_FILE}")
print(f"\nSummary: {total_sent} sent | {total_replies} replies ({pct(total_replies,total_sent)}) | {total_bounces} bounces ({pct(total_bounces,total_sent)})")

# Print table to console
print(f"\n{'Company':<35} {'Sent':>5} {'Replies':>7} {'Reply%':>7} {'Bounces':>8} {'Bounce%':>8}  First Reply")
print("-" * 100)
for r in rows:
    print(f"  {r['Company']:<33} {r['Total_Sent']:>5} {r['Replies']:>7} {pct(r['Replies'],r['Total_Sent']):>7} {r['Bounces']:>8} {pct(r['Bounces'],r['Total_Sent']):>8}  {fmt_date(r['First_Reply_Raw'])}")
