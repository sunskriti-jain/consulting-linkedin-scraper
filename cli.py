"""OutreachEngine CLI."""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import click
import config
from db import init_db, get_db
import campaign as C


@click.group()
def cli():
    """OutreachEngine - AI-personalized B2B cold email pipeline."""
    pass


def _get_campaign_id(campaign_name: str):
    with get_db() as conn:
        row = conn.execute("SELECT id FROM campaigns WHERE name = ?", (campaign_name,)).fetchone()
        if not row:
            print(f"Campaign '{campaign_name}' not found.")
            return None
        return row["id"]


@cli.command()
def init():
    """Initialize database."""
    init_db()
    print(f"Database initialized at {config.DB_PATH}")
    if not config.HUNTER_API_KEY or config.HUNTER_API_KEY == "your_hunter_key_here":
        print("[!] HUNTER_API_KEY not set in .env")
    if not config.ANTHROPIC_API_KEY or config.ANTHROPIC_API_KEY == "your_claude_key_here":
        print("[!] ANTHROPIC_API_KEY not set in .env")
    if not config.SENDER_EMAIL or config.SENDER_EMAIL == "you@gmail.com":
        print("[!] SENDER_EMAIL not set in .env")
    print("\nNext: `python cli.py gmail-auth` to connect your Gmail account")


@cli.command("gmail-auth")
def gmail_auth():
    """Run Gmail OAuth flow."""
    from gmail_client import authenticate
    authenticate()
    print("[OK] Gmail authenticated. Token saved.")


@cli.command("gmail-test")
@click.argument("to_email")
def gmail_test(to_email):
    """Send a test email to verify Gmail works."""
    from gmail_client import GmailClient
    g = GmailClient()
    result = g.send_test(to_email)
    print(f"[OK] Test sent. Message ID: {result['id']}")


@cli.command("import-companies")
@click.argument("csv_file")
def import_companies(csv_file):
    """Import companies from CSV (columns: name, domain, [industry])."""
    count = C.import_companies_csv(csv_file)
    print(f"Imported {count} companies.")


@cli.command("import-contacts")
@click.argument("csv_file")
def import_contacts(csv_file):
    """Import contacts (columns: first_name, last_name, title, company_domain, linkedin_url)."""
    count = C.import_contacts_csv(csv_file)
    print(f"Imported {count} contacts.")


@cli.command("create-campaign")
@click.argument("name")
@click.option("--daily-cap", type=int, default=None)
def create_campaign(name, daily_cap):
    """Create a campaign."""
    cid = C.create_campaign(name, daily_cap)
    print(f"Campaign '{name}' id: {cid}")


@cli.command()
@click.option("--domain-search/--no-domain-search", default=True, help="Use Hunter domain-search to discover contacts when none exist")
@click.option("--max-per-company", type=int, default=3)
@click.option("--no-hunter", is_flag=True, help="Skip Hunter; use only DDG pattern-guess fallback")
@click.option("--limit", type=int, default=None, help="Process at most N companies (in import order)")
def discover(domain_search, max_per_company, no_hunter, limit):
    """Discover emails for companies. Hunter-first, then DDG fallback."""
    C.discover_emails(
        max_contacts_per_company=max_per_company,
        use_domain_search=domain_search,
        use_hunter=not no_hunter,
        limit=limit,
    )


@cli.command("detect-pattern")
@click.argument("domain")
def detect_pattern_cmd(domain):
    """Scrape search engines for @domain emails and guess the company's email pattern."""
    import email_fallback
    pattern, conf, samples = email_fallback.discover_pattern(domain)
    print(f"\nDomain: {domain}")
    print(f"Pattern: {pattern}   Confidence: {conf:.1f}%")
    if samples:
        print(f"\nHarvested {len(samples)} emails (sample):")
        for s in samples[:10]:
            print(f"  {s}")
    else:
        print("\nNo emails harvested. Using default pattern.")


@cli.command()
@click.option("--limit", type=int, default=None, help="Max companies to research this run")
def research(limit):
    """Research un-researched companies via Claude."""
    C.research_companies(limit=limit)


@cli.command()
@click.argument("campaign_name")
@click.option("--value-prop", required=True, help="Your value prop")
@click.option("--steps", type=int, default=3)
@click.option("--limit", type=int, default=None, help="Max contacts to personalize")
def personalize(campaign_name, value_prop, steps, limit):
    """Generate personalized messages for campaign."""
    cid = _get_campaign_id(campaign_name)
    if not cid:
        return
    C.personalize(cid, value_prop, num_steps=steps, limit=limit)


@cli.command()
@click.argument("campaign_name")
@click.option("-n", type=int, default=5)
def preview(campaign_name, n):
    """Preview random personalized emails."""
    cid = _get_campaign_id(campaign_name)
    if not cid:
        return
    C.preview(cid, n)


@cli.command()
@click.argument("campaign_name")
@click.option("--force", is_flag=True, help="Ignore business hours check")
@click.option("--max", "max_sends", type=int, default=None, help="Max emails this batch")
def send(campaign_name, force, max_sends):
    """Send queued emails."""
    cid = _get_campaign_id(campaign_name)
    if not cid:
        return
    C.send_batch(cid, ignore_business_hours=force, max_sends=max_sends)


@cli.command("check-replies")
@click.argument("campaign_name")
def check_replies(campaign_name):
    """Poll Gmail for replies and pause those sequences."""
    cid = _get_campaign_id(campaign_name)
    if not cid:
        return
    C.check_replies(cid)


@cli.command("queue-next-step")
@click.argument("campaign_name")
@click.option("--from-step", type=int, required=True)
def queue_next(campaign_name, from_step):
    """Queue step N+1 for contacts who completed step N and haven't replied."""
    cid = _get_campaign_id(campaign_name)
    if not cid:
        return
    C.queue_next_step(cid, from_step)


@cli.command()
@click.argument("campaign_name")
def status(campaign_name):
    """Show campaign status."""
    cid = _get_campaign_id(campaign_name)
    if not cid:
        return
    C.status(cid)


@cli.command()
@click.argument("campaign_name")
@click.argument("output_file")
def export(campaign_name, output_file):
    """Export campaign results to CSV."""
    cid = _get_campaign_id(campaign_name)
    if not cid:
        return
    C.export_csv(cid, output_file)


if __name__ == "__main__":
    cli()
