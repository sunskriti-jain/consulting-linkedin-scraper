"""
Master engagement analytics across ALL campaigns.
Runs engagement check on any unchecked emails, then exports
a single CSV with per-company stats aggregated across all campaigns.
"""
import sys, csv, time
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from db import get_db
from campaign import track_engagement

OUTPUT_FILE = "master_analytics_all_campaigns.csv"

# ── Step 1: Check which campaigns have unchecked emails ───────────────────────
print("="*60)
print("Checking engagement on all campaigns...")
print("="*60)

with get_db() as conn:
    campaigns = conn.execute("""
        SELECT c.id, c.name,
            SUM(CASE WHEN sr.status IN ('sent','opened') AND sr.last_checked_at IS NULL THEN 1 ELSE 0 END) as unchecked
        FROM campaigns c
        LEFT JOIN send_records sr ON sr.campaign_id=c.id
        GROUP BY c.id
        HAVING unchecked > 0
        ORDER BY c.created_at DESC
    """).fetchall()

if not campaigns:
    print("  All emails already checked — skipping to export.")
else:
    for camp in campaigns:
        print(f"\n  Campaign: {camp['name']} ({camp['unchecked']} unchecked)")
        result = track_engagement(camp['id'], recheck=False)
        print(f"  -> Replied: {result['replied_count']}  Bounced: {result['bounced_count']}  New changes: {result['new_status_changes']}")
        time.sleep(1)

# ── Step 2: Export master CSV ─────────────────────────────────────────────────
print("\n" + "="*60)
print("Exporting master analytics CSV...")
print("="*60)

with get_db() as conn:
    rows = conn.execute("""
        SELECT
            co.name                                                              AS Company,
            COUNT(DISTINCT sr.id)                                               AS Total_Sent,
            SUM(CASE WHEN sr.reply_detected_at IS NOT NULL THEN 1 ELSE 0 END)  AS Replies,
            SUM(CASE WHEN sr.status='bounced' OR sr.delivery_status='bounced' THEN 1 ELSE 0 END) AS Bounces,
            ROUND(
                CAST(SUM(CASE WHEN sr.reply_detected_at IS NOT NULL THEN 1 ELSE 0 END) AS FLOAT)
                / NULLIF(COUNT(DISTINCT sr.id), 0) * 100, 1
            )                                                                   AS Reply_Pct,
            ROUND(
                CAST(SUM(CASE WHEN sr.status='bounced' OR sr.delivery_status='bounced' THEN 1 ELSE 0 END) AS FLOAT)
                / NULLIF(COUNT(DISTINCT sr.id), 0) * 100, 1
            )                                                                   AS Bounce_Pct,
            MIN(sr.reply_detected_at)                                           AS First_Reply_Date,
            GROUP_CONCAT(DISTINCT ca.name)                                      AS Campaigns
        FROM send_records sr
        JOIN contacts  ct ON sr.contact_id  = ct.id
        JOIN companies co ON ct.company_id  = co.id
        JOIN campaigns ca ON sr.campaign_id = ca.id
        WHERE sr.status IN ('sent','bounced','replied')
           OR sr.reply_detected_at IS NOT NULL
        GROUP BY co.id, co.name
        ORDER BY Replies DESC, Total_Sent DESC, co.name
    """).fetchall()

total_sent    = sum(r["Total_Sent"] for r in rows)
total_replies = sum(r["Replies"]    for r in rows)
total_bounces = sum(r["Bounces"]    for r in rows)

reply_pct  = round(total_replies / total_sent * 100, 1) if total_sent else 0
bounce_pct = round(total_bounces / total_sent * 100, 1) if total_sent else 0

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["# Master Outreach Analytics — All Campaigns (Opens require tracking pixels, not available via Gmail API)"])
    writer.writerow([f"TOTAL,{total_sent},{total_replies},{total_bounces},{reply_pct}%,{bounce_pct}%"])
    writer.writerow([])
    writer.writerow(["Company", "Total_Sent", "Replies", "Bounces", "Reply_%", "Bounce_%", "First_Reply_Date", "Campaigns"])
    for r in rows:
        writer.writerow([
            r["Company"],
            r["Total_Sent"],
            r["Replies"],
            r["Bounces"],
            f"{r['Reply_Pct'] or 0.0}%",
            f"{r['Bounce_Pct'] or 0.0}%",
            r["First_Reply_Date"] or "",
            r["Campaigns"] or "",
        ])

print(f"\nWrote {len(rows)} companies to {OUTPUT_FILE}")
print(f"\nTOTAL: {total_sent} sent | {total_replies} replies ({reply_pct}%) | {total_bounces} bounces ({bounce_pct}%)")
print()
print(f"{'Company':<35} {'Sent':>6} {'Replies':>8} {'Bounces':>8} {'Reply%':>7} {'Bounce%':>8}  First Reply")
print("-"*90)
for r in rows:
    if r['Replies'] > 0 or r['Total_Sent'] > 0:
        fr = (r['First_Reply_Date'] or '')[:16]
        print(f"{r['Company']:<35} {r['Total_Sent']:>6} {r['Replies']:>8} {r['Bounces']:>8} {str(r['Reply_Pct'] or 0.0)+'%':>7} {str(r['Bounce_Pct'] or 0.0)+'%':>8}  {fr}")

print(f"\n[DONE] Saved: {OUTPUT_FILE}")
