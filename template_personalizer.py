"""
template_personalizer.py
Python port of the JS templatePersonalizer.js.

Key exports:
  analyze_placeholders(template)                        → dict
  fill_static_placeholders(template, contact, company)  → str
  clone_for_contact(base, prev_contact, new_contact)    → str   ← word-boundary safe
  personalize_for_company(template, contacts, company,
                          claude_client)                → list[dict]

All functions are pure (no DB I/O) and work independently of the existing
personalize_once.py orchestration layer, which imports from here.
"""
from __future__ import annotations
import re
from typing import Callable

# ---------------------------------------------------------------------------
# Static field map
# Maps placeholder label (lowercase) → getter(contact_dict, company_dict) → str
# ---------------------------------------------------------------------------
STATIC_FIELD_MAP: dict[str, Callable[[dict, dict], str]] = {
    "first name":   lambda c, co: c.get("first_name") or c.get("firstName") or "there",
    "last name":    lambda c, co: c.get("last_name")  or c.get("lastName")  or "",
    "company name": lambda c, co: co.get("name") or co.get("companyName")   or "",
    "title":        lambda c, co: c.get("title") or "",
}

# Placeholder intentionally left for the sender — never touched by the engine
_SENDER_PLACEHOLDER = "your name"


# ---------------------------------------------------------------------------
# analyze_placeholders
# ---------------------------------------------------------------------------
def analyze_placeholders(template: str) -> dict:
    """Scan a template for [Placeholder] tags and classify each one.

    Returns:
        {
          "all":     list[str]  — unique labels, order-preserving,
          "static":  list[str]  — map directly to contact/company data,
          "dynamic": list[str]  — require LLM generation,
        }

    Example:
        >>> info = analyze_placeholders("Hi [First Name], I love [Company Name]. [Custom hook]")
        >>> info["static"]   # ["First Name", "Company Name"]
        >>> info["dynamic"]  # ["Custom hook"]
    """
    found = re.findall(r'\[([^\]]+)\]', template)
    unique = list(dict.fromkeys(found))            # deduplicate, preserve order

    static_keys = set(STATIC_FIELD_MAP.keys())
    static  = [p for p in unique if p.lower() in static_keys]
    dynamic = [
        p for p in unique
        if p.lower() not in static_keys
        and p.lower() != _SENDER_PLACEHOLDER
    ]
    return {"all": unique, "static": static, "dynamic": dynamic}


# ---------------------------------------------------------------------------
# fill_static_placeholders
# ---------------------------------------------------------------------------
def fill_static_placeholders(template: str, contact: dict, company: dict) -> str:
    """Replace data-driven placeholders with real values — no LLM needed.

    Fills: [First Name], [Last Name], [Company Name], [Title]
    Leaves untouched: [Your Name], and any dynamic placeholder
    (e.g. [Personalization for company], [Custom hook]).

    Args:
        template: Raw email body string.
        contact:  Dict with keys first_name / firstName, last_name / lastName, title.
        company:  Dict with keys name / companyName.
    """
    out = template
    for label, getter in STATIC_FIELD_MAP.items():
        value = getter(contact, company) or ""
        # Use a lambda replacement to avoid re interpreting backslashes in `value`
        out = re.sub(
            rf'\[{re.escape(label)}\]',
            lambda _, v=value: v,
            out,
            flags=re.IGNORECASE,
        )
    return out


# ---------------------------------------------------------------------------
# clone_for_contact   ← THE KEY FIX
# ---------------------------------------------------------------------------
def clone_for_contact(
    base_email: str,
    prev_contact: dict,
    new_contact: dict,
) -> str:
    """Adapt a personalised email from prev_contact to work for new_contact.

    The [Personalization for company] block is preserved as-is; only first
    name, last name, and title are substituted.

    FIX vs JS cloneForContact
    ─────────────────────────
    The JS version used:
        out.replace(new RegExp(prevContact.firstName, "g"), newContact.firstName)

    This has two bugs:
      1. No word boundaries  — "Sara" → "Sarah" would turn "Saraswati" → "Sarahswati"
      2. Missing last name   — last name was never substituted at all

    This Python version fixes both:
      • \\b word boundaries via re.sub prevent partial-word matches
      • Last name is swapped (before first name to avoid double-substitution
        when a first name is a substring of a last name)
      • re.IGNORECASE handles openers like "Hi sarah," generated in lowercase
    """
    def _swap(text: str, old: str, new: str) -> str:
        if old and new and old.lower() != new.lower():
            return re.sub(
                rf'\b{re.escape(old)}\b',
                new,
                text,
                flags=re.IGNORECASE,
            )
        return text

    prev_first = (prev_contact.get("first_name") or prev_contact.get("firstName") or "").strip()
    new_first  = (new_contact.get("first_name")  or new_contact.get("firstName")  or "").strip()
    prev_last  = (prev_contact.get("last_name")  or prev_contact.get("lastName")  or "").strip()
    new_last   = (new_contact.get("last_name")   or new_contact.get("lastName")   or "").strip()
    prev_title = (prev_contact.get("title") or "").strip()
    new_title  = (new_contact.get("title")  or "").strip()

    out = base_email
    # Last name first — prevents double-hit when first name appears inside last name
    out = _swap(out, prev_last,  new_last)
    out = _swap(out, prev_first, new_first)
    out = _swap(out, prev_title, new_title)
    return out


# ---------------------------------------------------------------------------
# personalize_for_company  (orchestrator)
# ---------------------------------------------------------------------------
def personalize_for_company(
    template: str,
    contacts: list[dict],
    company: dict,
    claude_client,
) -> list[dict]:
    """Personalise one template for every contact at a single company.

    Strategy (mirrors JS personalizeForCompany):
      1. Pre-fill static placeholders from data — zero LLM calls.
      2. Call the LLM ONCE for the first contact to resolve dynamic placeholders
         (e.g. [Personalization for company], [Custom hook]).
      3. Clone + word-boundary-safe substitution for all remaining contacts.

    Args:
        template:      Raw email body with [Placeholder] tags.
        contacts:      List of contact dicts.  Required keys per contact:
                         first_name / firstName, last_name / lastName, title.
        company:       Dict with at least name, domain, industry.
        claude_client: ClaudeClient instance (handles Anthropic → Perplexity fallback).

    Returns:
        List of {"contact": dict, "subject": str, "body": str},
        same order as `contacts`.
    """
    if not contacts:
        return []

    info    = analyze_placeholders(template)
    primary, *rest = contacts

    # Step 1 — static fill for primary contact
    primary_filled = fill_static_placeholders(template, primary, company)

    # Step 2 — LLM for dynamic placeholders (once per company)
    if info["dynamic"]:
        result          = claude_client.personalize_from_template(primary_filled, primary, company)
        primary_body    = result["body"]
        primary_subject = result["subject"]
    else:
        primary_body    = primary_filled
        primary_subject = f"Quick question, {primary.get('first_name') or primary.get('firstName', 'there')}"

    results = [{"contact": primary, "subject": primary_subject, "body": primary_body}]

    # Step 3 — clone for remaining contacts
    for contact in rest:
        cloned_body    = clone_for_contact(primary_body,    primary, contact)
        cloned_subject = clone_for_contact(primary_subject, primary, contact)
        results.append({"contact": contact, "subject": cloned_subject, "body": cloned_body})

    return results
