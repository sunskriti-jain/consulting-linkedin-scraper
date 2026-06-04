"""Run engagement tracking on all campaigns, then export master analytics CSV."""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from db import get_db, init_db
import campaign as C

init_db()

print("=" * 60)
print("  Gmail Engagement Tracker")
print("=" * 60)

with get_db() as conn:
    campaigns = conn.execute(
        """SELECT DISTINCT ca.id, ca.name, COUNT(sr.id) as email_count
           FROM send_records sr
           JOIN campaigns ca ON sr.campaign_id = ca.id
           WHERE sr.status IN ('sent', 'opened')
             AND sr.last_checked_at IS NULL
           GROUP BY ca.id, ca.name
           ORDER BY email_count DESC"""
    ).fetchall()

if not campaigns:
    print("\nAll emails already checked. Exporting analytics...")
else:
    print(f"\nCampaigns to check ({sum(c['email_count'] for c in campaigns)} unchecked emails total):")
    for c in campaigns:
        print(f"  - {c['name']}: {c['email_count']} emails")
    print()

    for camp in campaigns:
        print(f"\n{'='*60}")
        print(f"Campaign: {camp['name']}")
        print(f"{'='*60}")
        C.track_engagement(camp["id"])

print("\n" + "=" * 60)
print("  Exporting master analytics spreadsheet...")
print("=" * 60)

output = C.export_master_analytics_csv("master_sequencing_analytics.csv")
print(f"\n[DONE] Spreadsheet saved: {output}")

# Print summary table
with get_db() as conn:
    rows = conn.execute("""
        SELECT co.name,
               COUNT(DISTINCT sr.id) as total,
               COUNT(CASE WHEN sr.opened_at IS NOT NULL THEN 1 END) as opened,
               COUNT(CASE WHEN sr.reply_detected_at IS NOT NULL THEN 1 END) as replied,
               COUNT(CASE WHEN sr.bounced_at IS NOT NULL THEN 1 END) as bounced
        FROM send_records sr
        JOIN contacts ct ON sr.contact_id = ct.id
        JOIN companies co ON ct.company_id = co.id
        WHERE sr.status IN ('sent', 'opened', 'replied', 'bounced')
        GROUP BY co.id, co.name
        HAVING opened > 0 OR replied > 0 OR bounced > 0
        ORDER BY replied DESC, opened DESC
    """).fetchall()

print("\n=== Companies with Engagement ===")
print(f"{'Company':<35} {'Sent':>6} {'Opened':>7} {'Replied':>8} {'Bounced':>8}")
print("-" * 70)
for r in rows:
    open_pct = round(r['opened'] / r['total'] * 100, 1) if r['total'] else 0
    print(f"{r['name']:<35} {r['total']:>6} {r['opened']:>4}({open_pct}%) {r['replied']:>7}  {r['bounced']:>7}")
