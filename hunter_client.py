"""Hunter.io API client for email discovery."""
import requests
import time
from typing import Optional, Dict, List
import config


class HunterClient:
    BASE_URL = "https://api.hunter.io/v2"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.HUNTER_API_KEY
        if not self.api_key:
            raise ValueError("HUNTER_API_KEY not set")

    def _get(self, endpoint: str, params: Dict) -> Dict:
        params["api_key"] = self.api_key
        for attempt in range(3):
            try:
                r = requests.get(f"{self.BASE_URL}/{endpoint}", params=params, timeout=30)
                if r.status_code == 429:
                    time.sleep(2 ** attempt)
                    continue
                r.raise_for_status()
                return r.json()
            except requests.RequestException as e:
                if attempt == 2:
                    print(f"  Hunter API error: {e}")
                    return {}
                time.sleep(2 ** attempt)
        return {}

    def find_email(self, first_name: str, last_name: str, domain: str) -> Optional[Dict]:
        """Find email for a specific person. Returns {email, confidence}."""
        data = self._get("email-finder", {
            "domain": domain,
            "first_name": first_name,
            "last_name": last_name,
        })
        result = data.get("data", {})
        email = result.get("email")
        score = result.get("score", 0)
        if email:
            return {"email": email, "confidence": float(score)}
        return None

    def domain_search(self, domain: str, limit: int = 10) -> List[Dict]:
        """Get all emails for a domain. Useful for discovering contacts."""
        data = self._get("domain-search", {"domain": domain, "limit": limit})
        result = data.get("data", {})
        emails = result.get("emails", [])
        pattern = result.get("pattern", "")
        return [
            {
                "email": e.get("value"),
                "first_name": e.get("first_name"),
                "last_name": e.get("last_name"),
                "title": e.get("position"),
                "linkedin_url": e.get("linkedin"),
                "confidence": float(e.get("confidence", 0)),
                "pattern": pattern,
            }
            for e in emails
            if e.get("value")
        ]

    def verify_email(self, email: str) -> Dict:
        """Verify email deliverability."""
        data = self._get("email-verifier", {"email": email})
        result = data.get("data", {})
        return {
            "status": result.get("status", "unknown"),
            "score": float(result.get("score", 0)),
        }
