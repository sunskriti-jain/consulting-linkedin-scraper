"""LinkedIn profile scraper — finds real names + titles for a company.

Scrapes Bing/DuckDuckGo/Google for site:linkedin.com/in results. Extracts
First Last and their role from snippets. Filters out HR/recruiting/frontline
so we target decision-makers.

No API key needed. Designed to feed real contacts into the outreach pipeline
BEFORE personalization so emails don't go to invented people.
"""
import re
import sys
import time
import html
from typing import List, Dict, Set
from urllib.parse import quote_plus

from email_fallback import _fetch, _search_bing, _search_ddg, _search_google

# Roles to reject — user does not want HR/recruiters/frontline.
EXCLUDE_ROLE_KEYWORDS = [
    "recruiter", "recruiting", "talent acquisition", "hr ", "human resources",
    "people operations", "people team", "benefits", "payroll",
    "sales associate", "cashier", "teller", "customer service rep",
    "intern", "student", "assistant store", "store associate",
    "barista", "driver", "technician ",
]

# Roles to prioritize (senior / decision-maker signals).
PRIORITY_ROLE_KEYWORDS = [
    "vp ", "vice president", "director", "head of", "chief", "cto", "cfo",
    "ceo", "cmo", "cio", "coo", "president", "svp", "evp", "partner",
    "principal", "managing director", "general manager", "gm ",
    "senior manager", "senior director", "lead ", "founder",
]

# Words that sometimes appear in LinkedIn result titles but aren't names.
NON_NAME_TOKENS = {
    "linkedin", "profile", "view", "profiles", "sign", "log", "login",
    "jobs", "job", "company", "school", "see", "the", "and", "or", "of",
}


def _search_all(query: str) -> str:
    """Run a query against all three engines, return concatenated HTML."""
    parts = []
    for fn, name in [(_search_bing, "bing"), (_search_ddg, "ddg"), (_search_google, "google")]:
        html_text = fn(query)
        if html_text:
            parts.append(html_text)
        time.sleep(1)  # be gentle
    return "\n".join(parts)


# Matches LinkedIn profile URLs: linkedin.com/in/firstname-lastname-xxxxx
LINKEDIN_URL_RE = re.compile(
    r"linkedin\.com/in/([a-z0-9][a-z0-9\-]{2,80})",
    re.IGNORECASE,
)

# Matches "First Last - Title - Company" patterns in SERP snippets.
SNIPPET_RE = re.compile(
    r"([A-Z][a-z]{1,20}(?:\s+[A-Z][a-z]{1,20}){0,3})"     # Name
    r"\s*[\u2013\u2014\-–—\|·•]\s*"                         # separator
    r"([^\u2013\u2014\-|]{3,80}?)"                          # Title
    r"\s*[\u2013\u2014\-–—\|·•]\s*"                         # separator
    r"([A-Z][A-Za-z0-9 &\.,'\-]{1,60})"                    # Company
)


def _clean(s: str) -> str:
    s = html.unescape(s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _name_from_url(slug: str) -> tuple:
    """linkedin.com/in/jane-doe-8a1b2 -> ('Jane', 'Doe') or (None, None)."""
    slug = slug.lower()
    # Drop the trailing hash segment (alphanumeric id)
    parts = slug.split("-")
    name_parts = []
    for p in parts:
        if re.match(r"^[a-z]{2,}$", p):  # pure alpha word of length 2+
            name_parts.append(p)
        else:
            break
    if len(name_parts) >= 2:
        return name_parts[0].capitalize(), " ".join(x.capitalize() for x in name_parts[1:])
    return None, None


def _looks_like_name(text: str) -> bool:
    words = text.split()
    if not (2 <= len(words) <= 4):
        return False
    for w in words:
        if w.lower() in NON_NAME_TOKENS:
            return False
        if not re.match(r"^[A-Z][a-zA-Z'\-]{1,24}$", w):
            return False
    return True


def _role_allowed(title: str) -> bool:
    t = title.lower()
    if any(bad in t for bad in EXCLUDE_ROLE_KEYWORDS):
        return False
    return True


def _role_priority(title: str) -> int:
    t = title.lower()
    return sum(1 for kw in PRIORITY_ROLE_KEYWORDS if kw in t)


def harvest_profiles(company_name: str, num_searches: int = 5) -> List[Dict]:
    """Run `num_searches` LinkedIn-targeted queries and return a deduped list
    of real profiles: [{first_name, last_name, title, linkedin_slug}]."""
    queries = [
        f'site:linkedin.com/in "{company_name}" director',
        f'site:linkedin.com/in "{company_name}" vice president',
        f'site:linkedin.com/in "{company_name}" manager',
        f'site:linkedin.com/in "{company_name}" head of',
        f'site:linkedin.com/in "{company_name}" chief',
        f'site:linkedin.com/in "{company_name}" senior',
        f'site:linkedin.com/in "{company_name}"',
    ][:num_searches]

    profiles: Dict[str, Dict] = {}  # keyed by linkedin slug

    for q in queries:
        print(f"    [q] {q}")
        page = _search_all(q)
        if not page:
            continue

        # Pass 1: find every linkedin.com/in/<slug> URL in the HTML
        for m in LINKEDIN_URL_RE.finditer(page):
            slug = m.group(1).rstrip("/").lower()
            if slug in profiles:
                continue
            fn, ln = _name_from_url(slug)
            if not fn or not ln:
                continue
            # Try to find the snippet window around this URL to extract a title
            pos = m.start()
            window = _clean(page[max(0, pos - 400): pos + 600])
            title = _extract_title_for_name(window, fn, ln)
            profiles[slug] = {
                "first_name": fn,
                "last_name": ln,
                "title": title,
                "linkedin_slug": slug,
                "source_query": q,
            }

        time.sleep(2)  # rate-limit between query rounds

    # Filter by role
    allowed = []
    for p in profiles.values():
        if p["title"] and not _role_allowed(p["title"]):
            continue
        allowed.append(p)

    # Sort: priority roles first, then whoever has a title at all.
    allowed.sort(key=lambda p: (
        -_role_priority(p["title"] or ""),
        0 if p["title"] else 1,
        p["last_name"],
    ))
    return allowed


def _extract_title_for_name(window: str, first: str, last: str) -> str:
    """Pull a title out of a SERP snippet window around a matching name."""
    m = SNIPPET_RE.search(window)
    if m:
        name_match = m.group(1).strip()
        title = m.group(2).strip()
        if first.lower() in name_match.lower() and last.lower() in name_match.lower():
            return title[:80]
    # Fallback: look for "at <Company>" phrasing
    m2 = re.search(
        rf"{re.escape(first)}\s+{re.escape(last)}[^a-zA-Z]+([A-Za-z][^|.\n\r]{{5,70}}?)\s+at\s",
        window,
    )
    if m2:
        return m2.group(1).strip()[:80]
    return ""


if __name__ == "__main__":
    # quick smoke test
    name = sys.argv[1] if len(sys.argv) > 1 else "Dell Technologies"
    profiles = harvest_profiles(name, num_searches=5)
    print(f"\n=== {name}: {len(profiles)} profiles ===")
    for p in profiles[:25]:
        print(f"  {p['first_name']} {p['last_name']} — {p['title'] or '(no title)'}")
