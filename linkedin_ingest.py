"""Parse LinkedIn search results (as JSON list of {title, url}) and insert
real contacts into the DB. Used after WebSearch harvests profile results.

Usage (as library):
    from linkedin_ingest import ingest_profiles
    ingest_profiles("Dell Technologies", [
        {"title": "Jane Doe - VP Strategy - Dell Technologies | LinkedIn",
         "url":   "https://www.linkedin.com/in/jane-doe-123/"},
        ...
    ])
"""
import re
import sqlite3
import sys
import uuid
from typing import List, Dict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = "outreach.db"

EXCLUDE_ROLE_KEYWORDS = [
    "recruiter", "recruiting", "talent acquisition", "hr specialist",
    "human resources", "people operations", "benefits", "payroll",
    "sales associate", "cashier", "teller",
    "intern", "student", "assistant store", "store associate",
    "barista", "driver at",
]

NAME_TOKEN_BLOCKLIST = {
    "linkedin", "profile", "sign", "login", "search", "jobs", "company",
    "the", "of", "at", "and",
}


def _parse_title_field(raw_title: str):
    """Take a LinkedIn SERP title like:
       'Jane Doe - VP Strategy - Dell Technologies | LinkedIn'
       return (first_name, last_name, title_or_empty)
    """
    s = raw_title.replace("\u2013", "-").replace("\u2014", "-").strip()
    # strip trailing " | LinkedIn" and similar
    s = re.sub(r"\s*[\|·]\s*LinkedIn.*$", "", s, flags=re.IGNORECASE).strip()
    parts = [p.strip() for p in s.split(" - ") if p.strip()]
    if not parts:
        return None, None, ""

    name = parts[0]
    # Sometimes the name includes trailing suffixes; keep just first two tokens
    name_tokens = name.split()
    if len(name_tokens) < 2:
        return None, None, ""
    # Reject names with non-alpha tokens
    cleaned = []
    for t in name_tokens[:4]:
        t_stripped = t.strip(",.")
        if not re.match(r"^[A-Z][a-zA-Z'\-]{1,24}$", t_stripped):
            break
        if t_stripped.lower() in NAME_TOKEN_BLOCKLIST:
            break
        cleaned.append(t_stripped)
    if len(cleaned) < 2:
        return None, None, ""
    first = cleaned[0]
    last = cleaned[-1]

    title = ""
    if len(parts) >= 2:
        # Title is the second segment; might be combined with company.
        # Drop trailing " - <Company>" if present.
        title = parts[1]
        # If there are 3+ parts, the last is usually the company name, so title = parts[1]
    return first, last, title[:80]


def _url_slug(url: str) -> str:
    m = re.search(r"linkedin\.com/in/([a-z0-9\-]+)/?", url, re.IGNORECASE)
    return m.group(1).lower().rstrip("/") if m else ""


def _role_allowed(title: str) -> bool:
    if not title:
        return True  # no title → keep (better than nothing)
    t = title.lower()
    return not any(bad in t for bad in EXCLUDE_ROLE_KEYWORDS)


def _email_from_pattern(first: str, last: str, domain: str, pattern: str) -> str:
    f = re.sub(r"[^a-z]", "", first.lower())
    l = re.sub(r"[^a-z]", "", last.lower())
    builders = {
        "first.last": f"{f}.{l}",
        "firstlast": f"{f}{l}",
        "flast": f"{f[:1]}{l}",
        "f.last": f"{f[:1]}.{l}",
        "first_last": f"{f}_{l}",
        "first": f,
    }
    local = builders.get(pattern, f"{f}.{l}")
    return f"{local}@{domain}"


def ingest_profiles(company_name: str, profiles: List[Dict], min_required: int = 15, max_keep: int = 25):
    """Insert up to `max_keep` real profiles for company_name. Returns count inserted."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=30000")

    company = conn.execute("SELECT * FROM companies WHERE name = ?", (company_name,)).fetchone()
    if not company:
        print(f"  [SKIP] {company_name}: not in DB")
        conn.close()
        return 0

    domain = company["domain"]
    pattern = company["email_pattern"] or "first.last"

    seen_slugs = set()
    parsed = []
    for p in profiles:
        url = p.get("url", "")
        slug = _url_slug(url)
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        first, last, title = _parse_title_field(p.get("title", ""))
        if not first or not last:
            continue
        if not _role_allowed(title):
            continue
        parsed.append({
            "first": first, "last": last, "title": title,
            "linkedin_url": url, "slug": slug,
        })

    print(f"  [{company_name}] parsed {len(parsed)} real profiles from {len(profiles)} raw results")

    if len(parsed) < 3:
        print(f"  [WARN] {company_name}: only {len(parsed)} parseable profiles (want >= {min_required})")

    # Dedupe by (first, last) — different slugs can be same person
    unique = {}
    for p in parsed:
        key = (p["first"].lower(), p["last"].lower())
        if key not in unique:
            unique[key] = p
    unique_list = list(unique.values())[:max_keep]

    inserted = 0
    for p in unique_list:
        # Skip if we already have this contact for this company
        existing = conn.execute(
            "SELECT id FROM contacts WHERE company_id=? AND first_name=? AND last_name=?",
            (company["id"], p["first"], p["last"]),
        ).fetchone()
        if existing:
            continue

        email = _email_from_pattern(p["first"], p["last"], domain, pattern)
        cid = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO contacts
               (id, company_id, first_name, last_name, title, linkedin_url, primary_email, email_confidence, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'linkedin_harvest')""",
            (cid, company["id"], p["first"], p["last"], p["title"] or None,
             p["linkedin_url"], email, 60.0),
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"  [OK] {company_name}: inserted {inserted} new real contacts")
    return inserted


if __name__ == "__main__":
    import json
    # read profiles JSON from stdin
    data = json.loads(sys.stdin.read())
    for company_name, profiles in data.items():
        ingest_profiles(company_name, profiles)
