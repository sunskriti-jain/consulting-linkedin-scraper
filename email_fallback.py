"""Free email discovery fallback.

Strategy when Hunter.io returns nothing:
1. Scrape DuckDuckGo HTML results for "@{domain}" to harvest any real emails.
2. Reverse-engineer the dominant local-part pattern from those emails.
3. Construct the target contact's email by applying the pattern to their name.

No API key required. Confidence is necessarily lower than Hunter verified
emails, so we tag these at 45-65% and treat them as "best-guess, not verified".
"""

import re
import sys
import time
from collections import Counter
from typing import Optional, Tuple, List

import requests

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

# Role-address blocklist: these reveal nothing about the personal-email pattern.
ROLE_PREFIXES = {
    "info", "contact", "support", "hello", "hi", "sales", "help", "mail",
    "press", "media", "marketing", "careers", "jobs", "recruiting",
    "hr", "legal", "privacy", "security", "abuse", "admin", "webmaster",
    "no-reply", "noreply", "donotreply", "reply", "newsletter",
    "team", "office", "inquiries", "enquiries", "general",
}

# Ordered from most- to least-common enterprise patterns.
PATTERN_BUILDERS = {
    "first.last":  lambda f, l: f"{f}.{l}",
    "firstlast":   lambda f, l: f"{f}{l}",
    "flast":       lambda f, l: f"{f[0]}{l}",
    "f.last":      lambda f, l: f"{f[0]}.{l}",
    "first":       lambda f, l: f"{f}",
    "first_last":  lambda f, l: f"{f}_{l}",
    "firstl":      lambda f, l: f"{f}{l[0]}",
    "last":        lambda f, l: f"{l}",
    "last.first":  lambda f, l: f"{l}.{f}",
    "lastf":       lambda f, l: f"{l}{f[0]}",
}


def _fetch(url: str, params: dict, timeout: int = 15) -> str:
    try:
        r = requests.get(
            url,
            params=params,
            headers={
                "User-Agent": UA,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            timeout=timeout,
        )
        if r.status_code == 200:
            return r.text
        return ""
    except requests.RequestException as e:
        print(f"    [fetch error] {e}", file=sys.stderr)
        return ""


def _search_bing(query: str) -> str:
    return _fetch("https://www.bing.com/search", {"q": query, "count": 30})


def _search_ddg(query: str) -> str:
    # Lite endpoint is more scrape-friendly than html.duckduckgo.com
    return _fetch("https://lite.duckduckgo.com/lite/", {"q": query})


def _search_google(query: str) -> str:
    return _fetch("https://www.google.com/search", {"q": query, "num": 30, "hl": "en"})


def search_emails_for_domain(domain: str, max_queries: int = 3) -> List[str]:
    """Harvest real @domain emails from public search results.
    Tries Bing → DDG lite → Google until we get hits. Returns deduped list of
    non-role email addresses.
    """
    domain = domain.lower().strip()
    queries = [
        f'"@{domain}"',
        f'"@{domain}" contact',
        f'site:linkedin.com "@{domain}"',
    ][:max_queries]

    pattern = re.compile(rf"\b([a-zA-Z0-9._+-]+)@{re.escape(domain)}\b", re.IGNORECASE)
    found = set()

    for q in queries:
        # Try each backend in order; stop for this query once one returns hits.
        for backend in (_search_bing, _search_ddg, _search_google):
            html = backend(q)
            if not html:
                continue
            new_hits = set()
            for local in pattern.findall(html):
                local = local.lower()
                if local in ROLE_PREFIXES:
                    continue
                if local.startswith(("www", "http")):
                    continue
                if len(local) < 2 or len(local) > 64:
                    continue
                new_hits.add(f"{local}@{domain}")
            if new_hits:
                found.update(new_hits)
                break  # got results for this query — don't hammer other engines
        time.sleep(0.8)  # polite delay between queries

    return sorted(found)


def _classify_local(local: str) -> Optional[str]:
    """Given a local-part (before the @), infer its pattern shape.
    We can only classify when there's a separator; single-token locals
    are ambiguous (could be first, last, firstlast, flast).
    """
    local = local.lower()
    if "." in local:
        parts = local.split(".")
        if len(parts) == 2 and parts[0] and parts[1]:
            if len(parts[0]) == 1:
                return "f.last"
            if len(parts[1]) == 1:
                return "first.l"  # rare — we won't build this one
            return "first.last"
    if "_" in local:
        parts = local.split("_")
        if len(parts) == 2:
            return "first_last"
    return None  # ambiguous single token


def detect_pattern(emails: List[str]) -> Tuple[Optional[str], float]:
    """Return (best_pattern_name, confidence 0-100) from a sample of real emails."""
    if not emails:
        return None, 0.0

    votes = Counter()
    for e in emails:
        local = e.split("@")[0]
        p = _classify_local(local)
        if p and p in PATTERN_BUILDERS:
            votes[p] += 1

    if not votes:
        # No strongly-classifiable locals — default to "first.last" with low
        # confidence since it's the statistically most common enterprise pattern.
        return "first.last", 35.0

    top_pattern, top_count = votes.most_common(1)[0]
    # confidence = 45 base + up to +40 for agreement share, +5 per unique corroborating email
    agreement = top_count / sum(votes.values())
    conf = 45 + agreement * 40 + min(10, top_count * 2)
    return top_pattern, round(min(conf, 85.0), 1)


def _normalize(name: str) -> str:
    """Strip accents, hyphens, apostrophes; lowercase."""
    s = name.lower().strip()
    # Fold common accents
    repl = str.maketrans("áàâäãåéèêëíìîïóòôöõúùûüñçýÿ", "aaaaaaeeeeiiiiooooouuuuncyy")
    s = s.translate(repl)
    s = re.sub(r"[^a-z]", "", s)
    return s


def guess_email(first_name: str, last_name: str, domain: str, pattern: str) -> Optional[str]:
    f, l = _normalize(first_name), _normalize(last_name)
    if not f or not l:
        return None
    builder = PATTERN_BUILDERS.get(pattern) or PATTERN_BUILDERS["first.last"]
    return f"{builder(f, l)}@{domain.lower()}"


def discover_pattern(domain: str, verbose: bool = True) -> Tuple[str, float, List[str]]:
    """Full pipeline: search → detect → return (pattern, confidence, sample_emails)."""
    emails = search_emails_for_domain(domain)
    if verbose:
        print(f"    fallback: harvested {len(emails)} emails for @{domain}" + (f" (sample: {emails[:3]})" if emails else ""))
    pattern, conf = detect_pattern(emails)
    return pattern or "first.last", conf, emails
