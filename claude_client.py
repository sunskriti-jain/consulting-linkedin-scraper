"""LLM client for company research + email personalization.

Uses `llm_client.LLMRouter` under the hood — if the Anthropic key is out of
credits, it automatically falls through to Perplexity, then Qwen. The
public surface (`research_company`, `personalize_email`) is unchanged so
existing callers (personalize.py, etc.) keep working.

The class is still named ClaudeClient for backwards compatibility.

New method:
  personalize_from_template(template, contact, company) → {"subject", "body"}
  Called by template_personalizer.personalize_for_company() to resolve dynamic
  placeholders (e.g. [Personalization for company]) in a user-supplied template.
"""
import json
from llm_client import default_router, AllProvidersFailed

# System prompt used by personalize_from_template — matches the React UI spec.
_TEMPLATE_SYSTEM_PROMPT = """You are an email personalization engine for outreach campaigns. \
You receive an email template that already has contact/company fields filled in, \
but still contains dynamic [Placeholder] tags that need original content. \
Fill every remaining placeholder with warm, specific, human writing.

RULES:
- Dynamic placeholders (e.g. [Personalization for company], [Custom hook], \
[Relevant insight]) → write 1-2 sentences referencing something concrete and \
real about the company: a recent product, known challenge, funding milestone, \
or market position. Connect naturally to the surrounding paragraph.
- [Your Name] → leave exactly as-is.
- Match the exact tone and register of the surrounding text.
- Do NOT fabricate specific statistics or quotes you are uncertain about.
- Do NOT repeat the company name unnecessarily if it already appears nearby.
- Return ONLY valid JSON: {"subject": "...", "body": "..."}
  • subject: under 8 words, specific to the company, no placeholder tags remaining
  • body: the completed email body with every placeholder replaced, \
preserving all original line breaks and paragraph spacing exactly"""


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    # Perplexity sometimes appends citations like [1][2] — strip trailing
    # non-JSON tail after the last closing brace.
    last = text.rfind("}")
    if last != -1:
        text = text[: last + 1]
    return text


class ClaudeClient:
    def __init__(self, api_key: str = None):
        # api_key arg kept for backwards compat but router reads env itself.
        self.router = default_router()

    def _complete(self, prompt: str, max_tokens: int) -> str:
        text, provider = self.router.complete(prompt, max_tokens=max_tokens)
        if provider != "anthropic":
            print(f"  [LLM fallback] used {provider}")
        return text

    def research_company(self, company_name: str, domain: str, industry: str = "") -> dict:
        prompt = f"""Research the company "{company_name}" (domain: {domain}, industry: {industry}).

Return ONLY valid JSON (no markdown, no prose, no citations) with this exact shape:
{{
  "summary": "2-3 sentences on what they do and who they serve",
  "pain_points": ["specific pain point 1", "specific pain point 2", "specific pain point 3"],
  "value_prop": "one sentence describing their core value proposition",
  "hook": "one specific, non-generic fact about this company that would make a good email opener"
}}

If you don't know the company, make reasonable inferences from the domain/industry but keep hook concrete.
"""
        try:
            raw = self._complete(prompt, max_tokens=600)
        except AllProvidersFailed as e:
            print(f"  [LLM] all providers failed: {e}")
            return {
                "summary": f"{company_name} operates in {industry or 'their sector'}.",
                "pain_points": ["scaling operations", "reducing costs", "improving efficiency"],
                "value_prop": "Providing value in their market.",
                "hook": f"your work at {company_name}",
            }
        text = _strip_code_fence(raw)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "summary": f"{company_name} operates in {industry or 'their sector'}.",
                "pain_points": ["scaling operations", "reducing costs", "improving efficiency"],
                "value_prop": "Providing value in their market.",
                "hook": f"your work at {company_name}",
            }

    def personalize_email(
        self,
        first_name: str,
        last_name: str,
        title: str,
        company_name: str,
        research: dict,
        sender_name: str,
        sender_title: str,
        sender_company: str,
        value_prop_from_sender: str,
        step_number: int,
        template: str = "bbs",
    ) -> dict:
        past_clients_by_industry = {
            "tech": ["Google", "Samsung", "Magic Leap", "Instagram"],
            "social_media": ["Instagram", "Pinterest", "Quora", "VSCO"],
            "healthcare": ["CVS Health", "Tempus", "American Cancer Society"],
            "consumer_goods": ["Victorinox", "Adidas"],
            "automotive": ["BMW"],
            "education": ["Grammarly"],
            "nonprofit": ["Mozilla Foundation", "Bill and Melinda Gates Foundation"],
            "finance": ["Indiegogo"],
            "other": ["Salesforce", "Google", "Instagram"],
        }

        deliverables_by_industry = {
            "tech": "product roadmaps and technical builds",
            "social_media": "market entry analyses and product optimization strategies",
            "healthcare": "operational audits and market entry analyses",
            "consumer_goods": "go-to-market strategies and product development roadmaps",
            "automotive": "market research and competitive analysis",
            "finance": "market entry analyses and business strategy",
            "default": "market entry analyses, product roadmaps, technical builds, and operational audits",
        }

        _bbs_step1 = f"""You are writing a step-1 cold outreach email using a specific template.

EMAIL TEMPLATE:
Hi {{first_name}},

I lead Berkeley Business Society at UC Berkeley — a [club_type] club that partners with companies like [client1] and [client2] on semester-long engagements, and specializes in [specialization_phrase].

[2-3 sentences of personalization about {{company_name}} / {{title}} — tie it to their hook or pain point]

We're selecting 2–3 companies for the Fall 2026 and are reaching out to a handful of companies we think would be a strong fit. Past teams of 6-10 people have delivered [deliverables] that clients have found genuinely useful beyond the classroom.

Would you be open to a 10-minute call to explore whether there's a fit? Happy to share past work samples beforehand.

Here is my calendly link: https://calendly.com/d/d2fr-zwb-wxs?month=2026-06&date=2026-06-17

Best,
Eleyn Xiong | 858-371-9042
Berkeley Business Society
UC Berkeley

FILL INSTRUCTIONS:
- [club_type]: choose "consulting", "product", or "tech" based on {company_name}'s industry and {title}
- [client1] and [client2]: pick 2 REAL past clients from this list that are relevant to {company_name}'s industry: {past_clients_by_industry}
- [specialization_phrase]: 1-2 sentences describing what BBS specializes in FOR THIS COMPANY/INDUSTRY. E.g., for healthcare: "helping large healthcare systems operationalize care delivery models at scale"
- [2-3 sentences]: personalization referencing the hook: "{research.get('hook', '')}" or pain point
- [deliverables]: pick from this list what's most relevant to {company_name}'s industry: {deliverables_by_industry}
- NO CHANGES to signature, calendly link, or structure
- Ensure body flows naturally with actual names and details filled in
"""

        _fv_step1 = f"""You are writing a step-1 cold outreach email using a specific template.

EMAIL TEMPLATE:
Hi {{first_name}},

I lead Free Ventures at UC Berkeley — Berkeley's leading pre-seed startup accelerator and the university's only nonprofit, student-run program of its kind. Over the past decade, we've helped 100+ portfolio companies raise $200M+ in follow-on capital from firms like Kleiner Perkins, Accel, and Greylock, with multiple YC exits and acquisitions by companies like Coinbase, Discord, and Opendoor.

I was impressed to learn that [Company] [personalized insight — 1 sentence about what {company_name} has been doing recently, tied to the hook: "{research.get('hook', '')}"].  Given [Company]'s work in [relevant domain — {company_name}'s core market or domain in 2-4 words], I think there could be a genuine fit between your team's strategic challenges and what we can deliver.

We've advised and helped scale the very startups that have gone on to raise from Y Combinator, Greylock, and Kleiner Perkins — working directly on strategy, product, and growth with founders at the earliest and most critical stages. We're currently selecting 2–3 partners for Fall 2026, and given [Company]'s trajectory, we think there's a strong case for what a team of Berkeley's sharpest founders and operators could help you solve.

Would you be open to a 10-minute call to explore whether there's a fit? Happy to share past work and examples of what our teams have delivered.

Here is my Calendly link: https://calendly.com/d/d2fr-zwb-wxs?month=2026-06&date=2026-06-17

Best,
Eleyn Xiong | 858-371-9042
Free Ventures
UC Berkeley

FILL INSTRUCTIONS:
- [Company]: replace both occurrences with the actual company name: {company_name}
- [personalized insight]: 1 sentence about what {company_name} has been doing recently (scaling, expanding, pivoting, etc.) — use the hook: "{research.get('hook', '')}"
- [relevant domain]: {company_name}'s core market or domain in 2–4 words (e.g. "enterprise AI infrastructure", "B2B fintech", "defense tech")
- NO CHANGES to signature, Calendly link, or the Free Ventures bio paragraph
- Ensure the body flows naturally with actual details filled in
"""

        _vo_step1 = f"""You are writing a step-1 cold outreach email using a specific template.

EMAIL TEMPLATE:
Hi {{first_name}},

I lead Venture Out, a collective of consultants, product managers, software engineers, and founders pulled from some of the top startup and consulting programs in the country — including Berkeley Business Society (Berkeley's oldest and most selective consulting club), Free Ventures (Berkeley's leading pre-seed accelerator), Web Development at Berkeley, Girls Who Venture and 180 Degrees Consulting at Duke, and ProductSC at USC, whose members focus on work with F500 companies and high growth startups.

Together, we've advised and helped scale startups that went on to raise from Y Combinator, Greylock, and Kleiner Perkins — working directly with founders on strategy, product, software, and growth at their earliest and most critical stages.

I was looking into [Company] and noticed [specific, researched insight — 1 sentence about {company_name}'s recent move, challenge, or growth area, tied to the hook: "{research.get('hook', '')}"].  Given [Company]'s work in [relevant domain — {company_name}'s core market in 2-4 words], I think there's a real fit between what your team is navigating and what we can deliver.

We're selecting 2–3 partners for Fall 2026, and given [Company]'s trajectory, I'd love to explore whether a team of Berkeley, Duke, and USC's sharpest builders could help.

Would you be open to a quick 10-minute call? Happy to share examples of past work.

Here is my Calendly link: https://calendly.com/d/d2fr-zwb-wxs?month=2026-06&date=2026-06-17

Best,
Eleyn Xiong | 858-371-9042
Venture Out | UC Berkeley

FILL INSTRUCTIONS:
- [Company]: replace all three occurrences with the actual company name: {company_name}
- [specific, researched insight]: 1 sentence about what {company_name} has been doing recently — use the hook: "{research.get('hook', '')}"
- [relevant domain]: {company_name}'s core market in 2–4 words (e.g. "enterprise AI infrastructure", "B2B fintech", "defense tech")
- NO CHANGES to the org intro paragraph, signature, or Calendly link
- Ensure the body flows naturally with actual details filled in
"""

        if template == "fv":
            _step1 = _fv_step1
        elif template == "vo":
            _step1 = _vo_step1
        else:
            _step1 = _bbs_step1

        step_instructions = {
            1: _step1,
            2: "FOLLOW-UP #1 (skip the template, just 'Hi {first_name},').",
            3: "FOLLOW-UP #2 / break-up.",
        }

        if template == "fv":
            org_label = "Free Ventures"
        elif template == "vo":
            org_label = "Venture Out"
        else:
            org_label = "Berkeley Business Society"
        prompt = f"""You are writing a cold outreach email for {org_label}.

RECIPIENT:
- First Name: {first_name}
- Last Name: {last_name}
- Title: {title}
- Company: {company_name}

COMPANY RESEARCH:
- Summary: {research.get('summary', '')}
- Pain points: {', '.join(research.get('pain_points', []))}
- Specific hook: {research.get('hook', '')}

STEP {step_number} INSTRUCTIONS:
{step_instructions[step_number]}

IMPORTANT RULES:
1. Return ONLY valid JSON: {{"subject": "...", "body": "..."}}
2. The body for step 1 MUST use the exact template structure above with all blanks filled in
3. Sign all emails exactly as shown in the template: for Venture Out use "Eleyn Xiong | 858-371-9042\nVenture Out | UC Berkeley"; for others use "Eleyn Xiong | 858-371-9042\n{org_label}\nUC Berkeley"
4. Subject line: under 6 words, specific to {company_name}, professional but personable
"""
        try:
            raw = self._complete(prompt, max_tokens=800)
        except AllProvidersFailed as e:
            print(f"  [LLM] all providers failed: {e}")
            return {
                "subject": f"quick question, {first_name}",
                "body": f"Hi {first_name},\n\nNoticed {company_name}'s work and thought it was worth reaching out.\n\n{value_prop_from_sender}\n\nOpen to a quick chat?\n\n{sender_name}",
            }
        text = _strip_code_fence(raw)
        try:
            data = json.loads(text)
            return {"subject": data["subject"], "body": data["body"]}
        except (json.JSONDecodeError, KeyError):
            return {
                "subject": f"quick question, {first_name}",
                "body": f"Hi {first_name},\n\nNoticed {company_name}'s work and thought it was worth reaching out.\n\n{value_prop_from_sender}\n\nOpen to a quick chat?\n\n{sender_name}",
            }

    def personalize_from_template(
        self,
        template: str,
        contact: dict,
        company: dict,
    ) -> dict:
        """Fill dynamic [Placeholder] tags in a user-supplied template.

        Designed to be called by template_personalizer.personalize_for_company().
        Static placeholders ([First Name] etc.) should already be resolved before
        calling this — only dynamic ones (e.g. [Personalization for company])
        remain for the LLM to generate.

        Args:
            template: Partially-filled email body (static fields already replaced).
            contact:  Dict with first_name/firstName, last_name/lastName, title.
            company:  Dict with name, domain, industry.

        Returns:
            {"subject": str, "body": str}
        """
        first_name   = contact.get("first_name") or contact.get("firstName", "there")
        company_name = company.get("name") or company.get("companyName", "your company")

        user_message = (
            f"TEMPLATE (static fields already filled — resolve remaining [Placeholders]):\n"
            f"{template}\n\n"
            f"CONTACT: {first_name} {contact.get('last_name') or contact.get('lastName', '')}, "
            f"{contact.get('title', '')}\n"
            f"COMPANY: {company_name} | Industry: {company.get('industry', 'N/A')} | "
            f"Domain: {company.get('domain', 'N/A')}\n\n"
            f"Return JSON: {{\"subject\": \"...\", \"body\": \"...\"}}"
        )

        # _TEMPLATE_SYSTEM_PROMPT is module-level; inject it as a system turn
        full_prompt = f"[SYSTEM]\n{_TEMPLATE_SYSTEM_PROMPT}\n\n[USER]\n{user_message}"

        try:
            raw = self._complete(full_prompt, max_tokens=900)
        except AllProvidersFailed as e:
            print(f"  [LLM] all providers failed: {e}")
            return {
                "subject": f"Quick question, {first_name}",
                "body": template,   # return as-is rather than dropping the email
            }

        text = _strip_code_fence(raw)
        try:
            data = json.loads(text)
            return {"subject": data["subject"], "body": data["body"]}
        except (json.JSONDecodeError, KeyError):
            # LLM returned plain text instead of JSON — treat whole response as body
            return {
                "subject": f"Quick question, {first_name}",
                "body": text if text else template,
            }
