"""Multi-provider LLM client with automatic fallback.

Order: Claude -> Perplexity -> Qwen. When a provider returns a credit/auth
error (low balance, invalid key, quota), the next one is tried. Transient
errors (5xx, timeouts, 429) also fall through after one retry.

All providers expose a single `complete(prompt, max_tokens)` returning str.
"""
import os
import time
import json
import requests
from typing import Optional

import config


class ProviderExhausted(Exception):
    """Raised when a provider is out of credits / key invalid — fall through."""


class AllProvidersFailed(Exception):
    pass


# ---- Anthropic ----------------------------------------------------------
class AnthropicProvider:
    name = "anthropic"
    model = "claude-sonnet-4-5-20250929"
    endpoint = "https://api.anthropic.com/v1/messages"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def complete(self, prompt: str, max_tokens: int = 800) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        r = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        if r.status_code == 400 and "credit balance" in r.text.lower():
            raise ProviderExhausted(f"anthropic: credits exhausted")
        if r.status_code in (401, 403):
            raise ProviderExhausted(f"anthropic: auth failed ({r.status_code})")
        if r.status_code == 429:
            raise ProviderExhausted(f"anthropic: rate limited")
        r.raise_for_status()
        data = r.json()
        return data["content"][0]["text"]


# ---- Perplexity ---------------------------------------------------------
class PerplexityProvider:
    """Perplexity Sonar — OpenAI-compatible chat completions.

    Great for research-style prompts because Sonar models are grounded in
    live web results, which matches `research_company` better than Claude's
    static knowledge.
    """
    name = "perplexity"
    model = "sonar-pro"
    endpoint = "https://api.perplexity.ai/chat/completions"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def complete(self, prompt: str, max_tokens: int = 800) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        r = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        if r.status_code in (401, 403):
            raise ProviderExhausted(f"perplexity: auth failed ({r.status_code})")
        if r.status_code == 402:
            raise ProviderExhausted(f"perplexity: payment required")
        if r.status_code == 429:
            raise ProviderExhausted(f"perplexity: rate limited")
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]


# ---- Qwen (DashScope OpenAI-compatible) ---------------------------------
class QwenProvider:
    """Alibaba Qwen via DashScope's OpenAI-compatible endpoint.

    Works with both qwen-plus (general) and qwen-coder-plus. We use
    qwen-plus because these prompts are not code tasks.
    """
    name = "qwen"
    model = "qwen-plus"
    endpoint = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def complete(self, prompt: str, max_tokens: int = 800) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        r = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        if r.status_code in (401, 403):
            raise ProviderExhausted(f"qwen: auth failed ({r.status_code})")
        if r.status_code == 402:
            raise ProviderExhausted(f"qwen: payment required")
        if r.status_code == 429:
            raise ProviderExhausted(f"qwen: rate limited")
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]


# ---- OpenRouter ---------------------------------------------------------
class OpenRouterProvider:
    """OpenRouter — one key, many models. Defaults to a Qwen model so this
    slots in as a Qwen fallback billed against an OpenRouter balance
    instead of an Alibaba Cloud account.

    Override with OPENROUTER_MODEL env var, e.g.
    "anthropic/claude-sonnet-4.5", "qwen/qwen3-coder",
    "qwen/qwen-2.5-72b-instruct".
    """
    name = "openrouter"
    endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model or os.getenv(
            "OPENROUTER_MODEL", "qwen/qwen-2.5-72b-instruct"
        )

    def complete(self, prompt: str, max_tokens: int = 800) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            # Optional but recommended by OpenRouter for analytics/ranking.
            "HTTP-Referer": os.getenv(
                "OPENROUTER_REFERER", "https://github.com/bbs-outreach"
            ),
            "X-Title": os.getenv("OPENROUTER_APP_TITLE", "BBS Outreach"),
        }
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        r = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        if r.status_code in (401, 403):
            raise ProviderExhausted(f"openrouter: auth failed ({r.status_code})")
        if r.status_code == 402:
            raise ProviderExhausted(f"openrouter: insufficient credits")
        if r.status_code == 429:
            raise ProviderExhausted(f"openrouter: rate limited")
        r.raise_for_status()
        data = r.json()
        # OpenRouter occasionally surfaces a provider error inside a 200.
        if "error" in data and "choices" not in data:
            msg = (data.get("error") or {}).get("message", "")
            if "credit" in msg.lower() or "balance" in msg.lower():
                raise ProviderExhausted(f"openrouter: {msg}")
            raise requests.HTTPError(f"openrouter error: {msg}")
        return data["choices"][0]["message"]["content"]


# ---- Router -------------------------------------------------------------
class LLMRouter:
    """Tries providers in order. Remembers which ones are exhausted within
    this process so we stop wasting calls on a known-dead provider."""

    def __init__(self, providers=None):
        if providers is None:
            providers = _default_providers()
        self.providers = providers
        self.dead: set = set()

    def complete(self, prompt: str, max_tokens: int = 800) -> tuple:
        """Returns (text, provider_name_used)."""
        last_err = None
        for p in self.providers:
            if p.name in self.dead:
                continue
            try:
                text = p.complete(prompt, max_tokens=max_tokens)
                return text, p.name
            except ProviderExhausted as e:
                print(f"  [LLM] {p.name} exhausted: {e} — falling through")
                self.dead.add(p.name)
                last_err = e
                continue
            except (requests.Timeout, requests.ConnectionError) as e:
                print(f"  [LLM] {p.name} transient error: {e} — one retry")
                time.sleep(2)
                try:
                    text = p.complete(prompt, max_tokens=max_tokens)
                    return text, p.name
                except Exception as e2:
                    last_err = e2
                    continue
            except requests.HTTPError as e:
                # 5xx or unexpected — fall through to next provider
                print(f"  [LLM] {p.name} HTTP error: {e} — next provider")
                last_err = e
                continue

        raise AllProvidersFailed(
            f"All LLM providers failed/exhausted. Last error: {last_err}"
        )


def _default_providers():
    out = []
    if getattr(config, "ANTHROPIC_API_KEY", "") or os.getenv("ANTHROPIC_API_KEY"):
        out.append(AnthropicProvider(
            config.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")
        ))
    pk = os.getenv("PERPLEXITY_API_KEY", "")
    if pk:
        out.append(PerplexityProvider(pk))
    qk = os.getenv("QWEN_API_KEY", "") or os.getenv("DASHSCOPE_API_KEY", "")
    if qk:
        out.append(QwenProvider(qk))
    ork = os.getenv("OPENROUTER_API_KEY", "")
    if ork:
        out.append(OpenRouterProvider(ork))
    if not out:
        raise RuntimeError(
            "No LLM providers configured. Set ANTHROPIC_API_KEY, "
            "PERPLEXITY_API_KEY, QWEN_API_KEY (DASHSCOPE_API_KEY), "
            "or OPENROUTER_API_KEY."
        )
    return out


_default_router: Optional[LLMRouter] = None


def default_router() -> LLMRouter:
    global _default_router
    if _default_router is None:
        _default_router = LLMRouter()
    return _default_router
