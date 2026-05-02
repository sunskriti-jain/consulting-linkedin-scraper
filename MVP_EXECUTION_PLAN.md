# OutreachEngine MVP — Execution Plan
## Lean, Focused, Ship-First Approach

---

## PHILOSOPHY: Why This MVP Will Work

**Hypothesis:** Response rates are driven by:
1. **Right person at right company** (60% of impact) → Simple targeting
2. **Genuine personalization** (25% of impact) → Claude API research
3. **Reliable delivery** (10% of impact) → Gmail + basic warmup
4. **Timing** (5% of impact) → Business hours scheduling

**NOT driven by:**
- Having 5 email sources vs. 1 (diminishing returns after 2nd source)
- Complex sequences (3 steps > 4 steps for MVP)
- LinkedIn automation (high risk, account bans, cookie fragility)
- A/B testing variants (premature optimization)

**Result:** We'll get 80% of the responses with 20% of the effort by cutting:
- ❌ Snov.io, Apollo.io APIs (duplicate of Hunter/RocketReach)
- ❌ LinkedIn automation entirely (too risky for MVP)
- ❌ Website scraping for research (use API enrichment instead)
- ❌ SMTP verification (rely on API confidence scores)
- ❌ Complex warmup scheduling (simple daily cap instead)
- ❌ Thread management/reply detection (manual pause option only)

---

## PHASE 0: FOUNDATION (Week 1) — 40 hours

### 0.1 Project Setup
**Time: 4 hours**

```bash
# Repository structure
outreach-engine/
├── pyproject.toml              # Poetry dependencies
├── .env.example
├── .env                        # Encrypted with python-dotenv
├── main.py                     # Entry point
├── cli.py                      # Click-based CLI
├── config.py                   # Load & validate config
├── db.py                       # SQLite init & connection
├── models.py                   # Pydantic data classes (single file)
├── src/
│   ├── discovery/              # Email finding
│   │   ├── hunter_client.py
│   │   ├── rocketreach_client.py
│   │   └── email_deduper.py
│   ├── research/               # Company research
│   │   ├── enrichment_client.py (Clearbit)
│   │   └── research_aggregator.py
│   ├── personalization/        # AI copy generation
│   │   ├── claude_client.py
│   │   └── quality_scorer.py
│   ├── gmail/                  # Email sending
│   │   ├── oauth.py
│   │   ├── sender.py
│   │   └── tracker.py
│   └── campaign/               # Campaign orchestration
│       ├── campaign_manager.py
│       ├── batch_processor.py
│       └── scheduler.py
├── tests/
│   ├── test_discovery.py
│   ├── test_personalization.py
│   └── test_gmail.py
└── outreach_engine.db          # SQLite (git-ignored)
```

**Dependencies (Poetry):**
```toml
[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.0"
click = "^8.1"
anthropic = "^0.7"
google-auth-oauthlib = "^1.1"
google-auth-httplib2 = "^0.2"
google-api-python-client = "^1.13"
requests = "^2.31"
python-dotenv = "^1.0"
cryptography = "^41.0"
sqlite3-python = ""
pytz = "^2024.1"
```

### 0.2 Database Schema (Simplified)
**Time: 2 hours**

```sql
-- Core tables only (no email_records, api_usage_logs)
CREATE TABLE companies (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT NOT NULL UNIQUE,
    industry TEXT,
    status TEXT DEFAULT 'imported',
    created_at TIMESTAMP
);

CREATE TABLE contacts (
    id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    title TEXT,
    primary_email TEXT,
    email_confidence REAL,  -- 0-100
    linkedin_url TEXT,
    status TEXT DEFAULT 'discovered',
    created_at TIMESTAMP,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

CREATE TABLE company_research (
    id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL UNIQUE,
    summary TEXT,           -- 200 words
    pain_points TEXT,       -- JSON list
    value_prop TEXT,
    researched_at TIMESTAMP,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

CREATE TABLE templates (
    id TEXT PRIMARY KEY,
    name TEXT,
    subject TEXT,
    body TEXT,
    channel TEXT,           -- 'email'
    created_at TIMESTAMP
);

CREATE TABLE campaigns (
    id TEXT PRIMARY KEY,
    name TEXT,
    status TEXT DEFAULT 'draft',
    batch_size INTEGER DEFAULT 10,
    daily_cap INTEGER DEFAULT 50,
    created_at TIMESTAMP
);

CREATE TABLE send_records (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    contact_id TEXT NOT NULL,
    template_id TEXT NOT NULL,
    step_number INTEGER,    -- 1, 2, 3
    gmail_message_id TEXT,
    status TEXT,            -- queued, sent, bounced, replied
    scheduled_send_at TIMESTAMP,
    sent_at TIMESTAMP,
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id),
    FOREIGN KEY(contact_id) REFERENCES contacts(id),
    FOREIGN KEY(template_id) REFERENCES templates(id)
);

CREATE TABLE gmail_threads (
    id TEXT PRIMARY KEY,
    campaign_id TEXT,
    contact_id TEXT,
    gmail_thread_id TEXT,
    has_reply BOOLEAN DEFAULT 0,
    replied_at TIMESTAMP,
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id),
    FOREIGN KEY(contact_id) REFERENCES contacts(id)
);
```

### 0.3 Config & Encryption
**Time: 2 hours**

```python
# config.py
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        
        # API keys (will be encrypted in .env)
        self.hunter_api_key = self._decrypt(os.getenv("HUNTER_API_KEY"))
        self.rocketreach_api_key = self._decrypt(os.getenv("ROCKETREACH_API_KEY"))
        self.claude_api_key = self._decrypt(os.getenv("CLAUDE_API_KEY"))
        
        # Gmail OAuth
        self.gmail_client_id = os.getenv("GMAIL_CLIENT_ID")
        self.gmail_client_secret = self._decrypt(os.getenv("GMAIL_CLIENT_SECRET"))
        
        # Sender info
        self.sender_name = os.getenv("SENDER_NAME")
        self.sender_email = os.getenv("SENDER_EMAIL")
        
    def _decrypt(self, encrypted_value):
        if not encrypted_value:
            return ""
        cipher = Fernet(self.encryption_key)
        return cipher.decrypt(encrypted_value.encode()).decode()
```

### 0.4 CLI Skeleton
**Time: 2 hours**

```python
# cli.py
import click

@click.group()
def cli():
    pass

@cli.command()
def init():
    """Initialize config, API keys, Gmail OAuth"""
    pass

@cli.command()
@click.argument('csv_file')
def import_companies(csv_file):
    """Import companies from CSV (name, domain)"""
    pass

@cli.command()
@click.option('--campaign', required=True)
def discover(campaign):
    """Find contacts and emails"""
    pass

@cli.command()
@click.option('--campaign', required=True)
def research(campaign):
    """Research companies"""
    pass

@cli.command()
@click.option('--campaign', required=True)
def personalize(campaign):
    """Generate personalized messages"""
    pass

@cli.command()
@click.option('--campaign', required=True)
def preview(campaign):
    """Preview emails before sending"""
    pass

@cli.command()
@click.option('--campaign', required=True)
def launch(campaign):
    """Launch campaign"""
    pass

@cli.command()
@click.option('--campaign', required=True)
def status(campaign):
    """Show campaign status"""
    pass

if __name__ == '__main__':
    cli()
```

### 0.5 Models (Simplified)
**Time: 2 hours**

```python
# models.py - Single file with Pydantic models
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Company(BaseModel):
    id: str
    name: str
    domain: str
    industry: Optional[str] = None
    status: str = "imported"
    
class Contact(BaseModel):
    id: str
    company_id: str
    first_name: str
    last_name: str
    title: Optional[str] = None
    primary_email: str
    email_confidence: float
    status: str = "discovered"

class CompanyResearch(BaseModel):
    id: str
    company_id: str
    summary: str
    pain_points: List[str]
    value_prop: str

class Campaign(BaseModel):
    id: str
    name: str
    status: str = "draft"
    batch_size: int = 10
    daily_cap: int = 50

class SendRecord(BaseModel):
    id: str
    campaign_id: str
    contact_id: str
    status: str = "queued"
    scheduled_send_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
```

### 0.6 Gmail OAuth Flow
**Time: 10 hours** (most time-consuming setup piece)

```python
# src/gmail/oauth.py
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    """Run OAuth2 flow and save tokens"""
    flow = InstalledAppFlow.from_client_secrets_file(
        'gmail_client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Save tokens to config
    with open('gmail_token.json', 'w') as f:
        f.write(creds.to_json())
    
    return creds

def get_gmail_service():
    """Get authenticated Gmail service"""
    from google.auth.transport.requests import Request
    
    creds = None
    if os.path.exists('gmail_token.json'):
        creds = Credentials.from_authorized_user_file('gmail_token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    
    service = build('gmail', 'v1', credentials=creds)
    return service
```

---

## PHASE 1: EMAIL DISCOVERY (Week 2) — 30 hours

### 1.1 Hunter.io Integration
**Time: 8 hours**

```python
# src/discovery/hunter_client.py
import requests
from typing import List, Dict, Optional

class HunterClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hunter.io/v2"
    
    def find_domain_pattern(self, domain: str) -> Dict:
        """Find company email pattern"""
        # GET /email-finder → returns emails with pattern
        # Returns: {"pattern": "first.last", confidence: 0.95}
        pass
    
    def find_email(self, first_name: str, last_name: str, 
                   domain: str) -> Optional[str]:
        """Find individual email"""
        # GET /email-finder with name + domain
        # Returns: email, confidence score
        pass
    
    def verify_email(self, email: str) -> bool:
        """Verify email validity"""
        # GET /email-verifier
        # Returns: valid/invalid/unknown
        pass
```

### 1.2 RocketReach Integration (Optional for MVP)
**Time: 8 hours**

```python
# src/discovery/rocketreach_client.py
class RocketReachClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def lookup_person(self, first_name: str, last_name: str, 
                      company: str) -> Dict:
        """Look up person's email"""
        # Returns: email, confidence, phone
        pass
    
    def lookup_employees(self, company: str, title: str) -> List[Dict]:
        """Find employees by company + title"""
        # Returns: list of people matching criteria
        pass
```

### 1.3 Email Deduplication & Scoring
**Time: 6 hours**

```python
# src/discovery/email_deduper.py
from typing import List, Dict

class EmailDeduper:
    """
    Simple rule: if 2+ sources agree on email → 80+ confidence
    If 1 source + pattern match → 60+ confidence
    """
    
    def score_email(self, email: str, sources: List[str], 
                    pattern_match: bool) -> float:
        score = 0.0
        score += len(sources) * 40  # 40 pts per source
        if pattern_match:
            score += 20
        return min(score, 100.0)
    
    def deduplicate_contacts(self, contacts: List[Dict]) -> List[Dict]:
        """Remove duplicates, keep best email per person"""
        by_name = {}
        for contact in contacts:
            key = f"{contact['first_name']}_{contact['last_name']}"
            if key not in by_name or contact['email_confidence'] > by_name[key]['email_confidence']:
                by_name[key] = contact
        return list(by_name.values())
```

### 1.4 LinkedIn Scraper (Lightweight)
**Time: 8 hours**

```python
# src/discovery/linkedin_scraper.py
from selenium import webdriver
from typing import List, Dict
import time

class LinkedInScraper:
    """
    WARNING: LinkedIn ToS violation. Use with caution.
    For MVP: manual export from Sales Navigator, then parse CSV.
    Or: use free LinkedIn public API with proper auth.
    """
    
    def __init__(self):
        # Skip browser automation for MVP
        # Instead: manually export from Sales Navigator
        pass
    
    def parse_sales_navigator_export(self, csv_file: str) -> List[Dict]:
        """
        Parse CSV export from LinkedIn Sales Navigator
        Columns: first_name, last_name, title, company, linkedin_url
        """
        import csv
        contacts = []
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                contacts.append({
                    'first_name': row['First Name'],
                    'last_name': row['Last Name'],
                    'title': row['Title'],
                    'company': row['Company'],
                    'linkedin_url': row['URL']
                })
        return contacts
```

**For MVP: Manual LinkedIn Workflow**
- Export from Sales Navigator → CSV
- Script parses CSV
- Gets names + titles + company names
- Hands off to Hunter/RocketReach for email lookup

### 1.5 Discovery CLI Command
**Time: 4 hours**

```
Usage:
  outreach discover --campaign my_campaign --input contacts.csv
  
Flow:
  1. Import contacts from CSV (first_name, last_name, title, company, linkedin_url)
  2. For each contact:
     a. Extract company domain
     b. Query Hunter.io for email
     c. Query RocketReach if budget allows
     d. Score and deduplicate
  3. Store contacts in DB with primary_email + confidence
  4. Report: "Found 147 contacts, avg confidence 82%"
```

---

## PHASE 2: COMPANY RESEARCH (Week 2-3) — 20 hours

### 2.1 Clearbit Company Enrichment
**Time: 10 hours**

```python
# src/research/enrichment_client.py
import requests
from typing import Dict

class ClearbitClient:
    """Free tier: 100 lookups/month. Sufficient for 50 companies."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://company-stream.clearbit.com/v2/companies"
    
    def lookup(self, domain: str) -> Dict:
        """Get company info: description, industry, size, tech stack"""
        # Returns: {
        #   "name": "Acme Corp",
        #   "description": "...",
        #   "industry": "SaaS",
        #   "employees": {"range": "50-100"},
        #   "tech": ["AWS", "React"],
        #   "founded_year": 2018,
        #   "funding": {...}
        # }
        pass
```

### 2.2 Website Summary (Claude API)
**Time: 10 hours**

```python
# src/research/research_aggregator.py
from anthropic import Anthropic

class ResearchAggregator:
    def __init__(self, claude_api_key: str):
        self.client = Anthropic(api_key=claude_api_key)
    
    def build_research_brief(self, company_domain: str, 
                            enrichment_data: Dict) -> Dict:
        """
        Scrape website → Claude summarizes
        Takes Clearbit data + website content
        Returns: summary, pain_points, value_prop
        """
        
        prompt = f"""
Analyze this company for an outreach campaign.
Company: {enrichment_data['name']}
Website: {enrichment_data.get('website_url')}
Clearbit data: {enrichment_data}

Provide:
1. 2-3 sentence summary of what they do
2. List 3-4 specific pain points they likely have
3. 1-2 sentence value proposition for a B2B sales tool

Format as JSON:
{{
  "summary": "...",
  "pain_points": ["...", "..."],
  "value_prop": "..."
}}
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.content[0].text)
```

**Note:** For MVP, skip website scraping. Use Clearbit + Claude summary only.

---

## PHASE 3: AI PERSONALIZATION (Week 3) — 25 hours

### 3.1 Email Templates (3 simple ones)
**Time: 3 hours**

```python
# Initial outreach templates
TEMPLATE_1 = """
Subject: Quick question about {{company_name}}

Hi {{first_name}},

I came across {{company_name}} and was impressed by {{personalized_opener}}.

We help {{industry}} teams {{personalized_value_prop}}.

Would you be open to a 15-min call to explore this?

Best,
{{sender_name}}
"""

TEMPLATE_2 = """
Subject: {{company_name}} + {{personalized_angle}}

{{first_name}},

Saw your recent {{personalized_news_reference}}.

One thing that caught my attention: {{personalized_observation}}

Think you'd find this useful: {{personalized_cta}}

{{sender_name}}
"""

TEMPLATE_3 = """
Subject: Followup - {{company_name}}

{{first_name}},

Following up on my last message about {{personalized_topic}}.

Found this case study that's relevant: {{case_study_url}}

Let me know if it resonates.

{{sender_name}}
"""
```

### 3.2 Claude Personalization Engine
**Time: 15 hours**

```python
# src/personalization/claude_client.py
from anthropic import Anthropic
import json

class PersonalizationEngine:
    def __init__(self, claude_api_key: str):
        self.client = Anthropic(api_key=claude_api_key)
    
    def generate_opener(self, contact: Dict, research: Dict) -> str:
        """
        Generate ONE personalized opening line
        Example: "noticed you just landed Series C"
        """
        
        prompt = f"""
Generate a personalized 1-line opener for a cold email.

Context:
- Recipient: {contact['first_name']} {contact['last_name']}, {contact['title']} at {contact['company']}
- Company: {research['summary']}
- Recent news: {research.get('news')}
- Pain points: {', '.join(research.get('pain_points', []))}

Requirements:
1. Reference something SPECIFIC about their company (not generic)
2. Show you've done homework
3. One sentence max (15 words)
4. Natural, conversational tone

Return ONLY the opener text, no quotes or explanation.
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    def generate_value_prop(self, contact: Dict, research: Dict) -> str:
        """Generate personalized value prop for their company"""
        
        prompt = f"""
Write a 1-line value prop for {research['summary']}.

They likely care about: {', '.join(research.get('pain_points', []))}

Format: "help [role] [action] [outcome]"
Example: "help sales teams close deals 3x faster"

Return ONLY the value prop, no explanation.
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=30,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
```

### 3.3 Quality Scorer
**Time: 7 hours**

```python
# src/personalization/quality_scorer.py
from anthropic import Anthropic

class PersonalizationQualityScorer:
    def __init__(self, claude_api_key: str):
        self.client = Anthropic(api_key=claude_api_key)
    
    def score_email(self, email_body: str, research: Dict) -> float:
        """
        Score personalization quality 0-100
        
        Criteria:
        - Mentions specific company fact (not "we work with SaaS teams")
        - Doesn't use generic templates
        - Shows research done
        """
        
        prompt = f"""
Rate this email's personalization quality (0-100):

EMAIL:
{email_body}

RESEARCH CONTEXT:
{json.dumps(research, indent=2)}

Score it:
- 0-30: Generic, could be sent to anyone
- 31-60: Mentions company but lacks depth
- 61-80: Good personalization, shows research
- 81-100: Specific facts, custom offer, clearly targeted

Return ONLY a number 0-100.
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            return float(response.content[0].text.strip())
        except:
            return 65.0  # Default if parsing fails
```

---

## PHASE 4: GMAIL INTEGRATION (Week 4) — 15 hours

### 4.1 Email Sender
**Time: 10 hours**

```python
# src/gmail/sender.py
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class GmailSender:
    def __init__(self, gmail_service):
        self.service = gmail_service
    
    def send_email(self, to: str, subject: str, body: str, 
                   sender_name: str, sender_email: str) -> str:
        """
        Send email via Gmail API
        Returns: gmail_message_id
        """
        
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['from'] = f"{sender_name} <{sender_email}>"
        message['subject'] = subject
        
        # Add body
        msg_text = MIMEText(body, 'plain')
        message.attach(msg_text)
        
        # Send via Gmail API
        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()
        
        send_message = {
            'raw': raw_message
        }
        
        result = self.service.users().messages().send(
            userId='me',
            body=send_message
        ).execute()
        
        return result['id']
    
    def check_daily_quota(self) -> Dict:
        """Check Gmail API quota usage"""
        # Returns: {sent_today: 42, limit: 500}
        pass
```

### 4.2 Bounce & Reply Detection
**Time: 5 hours**

```python
# src/gmail/tracker.py
class GmailTracker:
    def __init__(self, gmail_service):
        self.service = gmail_service
    
    def check_for_replies(self, campaign_id: str) -> List[str]:
        """
        Poll Gmail for replies
        Mark contacts as "REPLIED" and pause their sequence
        
        Simple approach: search for threads containing contact emails
        """
        # Query: "from:{contact_email}"
        # If thread has > 1 message → reply detected
        pass
    
    def check_for_bounces(self, contact_email: str) -> bool:
        """
        Check for bounce messages
        Look for: Undeliverable, Mailer-Daemon, etc.
        """
        # Query: "from:mailer-daemon to:{our_email} subject:undeliverable"
        pass
```

---

## PHASE 5: CAMPAIGN ORCHESTRATION (Week 4) — 20 hours

### 5.1 Campaign Manager
**Time: 8 hours**

```python
# src/campaign/campaign_manager.py
import uuid
from datetime import datetime, timedelta

class CampaignManager:
    def __init__(self, db):
        self.db = db
    
    def create_campaign(self, name: str, companies: List[str], 
                       daily_cap: int = 50) -> str:
        """Create new campaign"""
        campaign_id = str(uuid.uuid4())
        self.db.execute("""
            INSERT INTO campaigns 
            (id, name, status, daily_cap, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (campaign_id, name, "draft", daily_cap, datetime.utcnow()))
        return campaign_id
    
    def enroll_contacts(self, campaign_id: str, company_ids: List[str]):
        """Add contacts from companies to campaign"""
        # Gets top 3 contacts per company
        # Creates send_records for steps 1-3
        pass
```

### 5.2 Batch Processor
**Time: 7 hours**

```python
# src/campaign/batch_processor.py
import time
from typing import List
from datetime import datetime, timedelta
import pytz

class BatchProcessor:
    def __init__(self, db, gmail_sender):
        self.db = db
        self.gmail_sender = gmail_sender
    
    def process_batch(self, campaign_id: str, step_number: int,
                      batch_size: int = 10):
        """
        Send a batch of emails
        
        1. Get unsent records for this step + campaign
        2. Check daily cap (50/day)
        3. For each contact in batch:
           a. Respect 60-120 second delays between sends
           b. Check business hours (9am-5pm recipient timezone)
           c. Send email via Gmail
           d. Log send_record
           e. Sleep 60-120 seconds
        4. Sleep 10-20 minutes between batches
        """
        
        # Get records ready to send
        ready = self.db.execute("""
            SELECT sr.id, sr.contact_id, c.primary_email,
                   t.subject, t.body
            FROM send_records sr
            JOIN contacts c ON sr.contact_id = c.id
            JOIN templates t ON sr.template_id = t.id
            WHERE sr.campaign_id = ?
              AND sr.step_number = ?
              AND sr.status = 'queued'
            LIMIT ?
        """, (campaign_id, step_number, batch_size)).fetchall()
        
        # Check daily cap
        sent_today = self.db.execute("""
            SELECT COUNT(*) FROM send_records
            WHERE campaign_id = ?
              AND sent_at > datetime('now', '-1 day')
        """, (campaign_id,)).fetchone()[0]
        
        campaign = self.db.execute("""
            SELECT daily_cap FROM campaigns WHERE id = ?
        """, (campaign_id,)).fetchone()
        
        if sent_today >= campaign['daily_cap']:
            print(f"Daily cap reached ({campaign['daily_cap']})")
            return
        
        # Send batch
        for record in ready:
            # Check business hours
            contact = self.db.execute(
                "SELECT timezone FROM contacts WHERE id = ?",
                (record['contact_id'],)
            ).fetchone()
            
            if not self._is_business_hours(contact['timezone']):
                print(f"Outside business hours for {contact['timezone']}")
                continue
            
            # Send email
            try:
                gmail_id = self.gmail_sender.send_email(
                    to=record['primary_email'],
                    subject=record['subject'],
                    body=record['body'],
                    sender_name=config.sender_name,
                    sender_email=config.sender_email
                )
                
                # Log send
                self.db.execute("""
                    UPDATE send_records
                    SET status = 'sent', gmail_message_id = ?, sent_at = ?
                    WHERE id = ?
                """, (gmail_id, datetime.utcnow(), record['id']))
                
                print(f"Sent to {record['primary_email']}")
                
                # Random delay 60-120 seconds
                time.sleep(random.randint(60, 120))
                
            except Exception as e:
                print(f"Failed to send: {e}")
                self.db.execute(
                    "UPDATE send_records SET status = 'failed' WHERE id = ?",
                    (record['id'],)
                )
    
    def _is_business_hours(self, timezone: str) -> bool:
        """Check if current time is business hours in timezone"""
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return 9 <= now.hour < 17 and now.weekday() < 5  # Mon-Fri 9-5
```

### 5.3 Scheduler (Simple Approach)
**Time: 5 hours**

```python
# src/campaign/scheduler.py
from datetime import datetime, timedelta

class CampaignScheduler:
    """
    Simple: Use cron or task scheduler to call process_batch()
    
    For MVP: no complex scheduling needed
    Just run: python main.py process-batch --campaign X --step 1
    """
    
    def schedule_campaign(self, campaign_id: str):
        """
        Sequence:
        - Day 0, 9am: Process step 1 (initial email)
        - Day 3, 9am: Process step 2 (first followup)
        - Day 7, 9am: Process step 3 (second followup)
        """
        
        campaign = self.db.execute(
            "SELECT * FROM campaigns WHERE id = ?", (campaign_id,)
        ).fetchone()
        
        # Create scheduled tasks
        # Use: Windows Task Scheduler / cron / APScheduler
        # Call: batch_processor.process_batch(campaign_id, step)
        pass
```

---

## PHASE 6: CLI & FINAL INTEGRATION (Week 4-5) — 15 hours

### 6.1 Complete CLI with Progress Bars
**Time: 10 hours**

```bash
# Usage examples:

# 1. Initialize (one-time)
outreach init
  → Prompts for API keys
  → Gmail OAuth flow
  → Creates DB

# 2. Import companies
outreach companies import companies.csv
  → CSV: company_name, domain, [industry]
  → Output: "Imported 50 companies"

# 3. Discovery
outreach discover my_campaign
  → Finds contacts in DB
  → Queries Hunter.io + RocketReach
  → Scores emails
  → Output: "Found 147 contacts"

# 4. Research
outreach research my_campaign
  → For each company, calls Clearbit
  → Generates research brief via Claude
  → Output: "Researched 50 companies"

# 5. Personalize
outreach personalize my_campaign
  → For each contact × template:
    - Generate opener
    - Generate value prop
    - Score quality
  → Output: "Generated 441 messages, 92% quality"

# 6. Preview
outreach preview my_campaign
  → Show 5 random emails
  → Show campaign summary

# 7. Launch
outreach launch my_campaign
  → Sends step 1 in batches
  → Schedules steps 2, 3 for future days
  → Output: "Campaign active, next send in 10 minutes"

# 8. Status
outreach status my_campaign
  → Shows:
    Step 1: 50/147 sent, 2 replies, 1 bounce
    Step 2: scheduled for 2025-03-25 at 9am
    Next action: in 10 minutes

# 9. Pause/Resume
outreach pause my_campaign
outreach resume my_campaign

# 10. Export
outreach export my_campaign csv
  → Exports all contacts + email addresses + send status
```

### 6.2 Configuration UI
**Time: 5 hours**

```python
# cli.py init command
def init():
    """Interactive setup"""
    
    print("=== OutreachEngine Setup ===\n")
    
    # Step 1: API Keys
    hunter_key = click.prompt("Hunter.io API Key", hide_input=True)
    claude_key = click.prompt("Claude API Key", hide_input=True)
    rocketreach_key = click.prompt(
        "RocketReach API Key (optional)",
        default="",
        hide_input=True
    )
    
    # Step 2: Sender Info
    sender_name = click.prompt("Your name")
    sender_email = click.prompt("Your email")
    
    # Step 3: Gmail OAuth
    click.echo("\nGmail OAuth Flow:")
    authenticate_gmail()
    
    # Step 4: Save config (encrypted)
    config = {
        'hunter_api_key': encrypt(hunter_key),
        'claude_api_key': encrypt(claude_key),
        'rocketreach_api_key': encrypt(rocketreach_key),
        'sender_name': sender_name,
        'sender_email': sender_email,
    }
    
    save_config(config)
    
    click.echo("\n✓ Setup complete!")
```

---

## PHASE 7: TESTING & FINAL POLISH (Week 5) — 10 hours

### 7.1 Core Test Suite
**Time: 6 hours**

```python
# tests/test_discovery.py
def test_hunter_email_finding():
    client = HunterClient(api_key="test_key")
    email = client.find_email("John", "Doe", "acme.com")
    assert email is not None
    assert "@acme.com" in email

def test_email_deduplication():
    deduper = EmailDeduper()
    contacts = [
        {"name": "John Doe", "email": "john@acme.com", "sources": 2},
        {"name": "John Doe", "email": "jdoe@acme.com", "sources": 1},
    ]
    result = deduper.deduplicate_contacts(contacts)
    assert len(result) == 1
    assert result[0]['email'] == "john@acme.com"

# tests/test_personalization.py
def test_personalization_quality():
    scorer = PersonalizationQualityScorer(api_key="test_key")
    email = "Hi John, noticed you just raised Series B..."
    score = scorer.score_email(email, {})
    assert score > 60  # Should have good score
```

### 7.2 Manual Testing Checklist
**Time: 4 hours**

```
[ ] Test Gmail OAuth flow
[ ] Send 1 test email
[ ] Verify email arrives in inbox
[ ] Check reply detection
[ ] Test batch sending 10 emails
[ ] Verify 60-120 second delays work
[ ] Check business hours filter
[ ] Test daily cap enforcement
[ ] Export CSV of contacts
[ ] Preview emails before sending
```

---

## DELIVERABLES

**At end of Week 5, you have:**

1. ✅ CLI tool that handles entire workflow
2. ✅ Hunter.io + RocketReach email discovery
3. ✅ Company research via Clearbit + Claude
4. ✅ Personalized emails via Claude (3 templates)
5. ✅ Gmail integration with OAuth
6. ✅ Batch sending (10 at a time, 60-120 sec delays)
7. ✅ Daily caps and business hours scheduling
8. ✅ Reply detection (pause sequences)
9. ✅ Campaign status tracking
10. ✅ CSV import/export

---

## WHAT'S INTENTIONALLY EXCLUDED (for Phase 2)

- ❌ LinkedIn automation (too risky)
- ❌ Website scraping (Clearbit enough)
- ❌ SMTP verification (rely on API scores)
- ❌ Complex warmup scheduling
- ❌ Thread management/full reply detection
- ❌ A/B test statistics
- ❌ Web dashboard (CLI sufficient)
- ❌ Webhook reply detection (polling sufficient)

---

## SUCCESS METRICS (What "Shipped" Means)

✅ **You can:**
1. Import 50 companies in < 2 minutes
2. Find emails for 80%+ of contacts in < 20 minutes
3. Research all companies in < 30 minutes
4. Generate personalized emails in < 60 minutes
5. Launch campaign and send 147 emails over 14 days
6. See replies come in and pause those sequences automatically
7. Export final results as CSV

✅ **Response rate target:**
- 5-10% reply rate (industry standard for personalized cold email)
- You'll hit this BECAUSE of personalization depth, not API source count

✅ **Time investment:**
- Setup: 30 minutes
- Per campaign: 2-3 hours of active work (import → launch)
- Then: system runs on autopilot for 14 days

---

## ESTIMATED EFFORT

| Phase | Hours | Days |
|-------|-------|------|
| Foundation | 40 | 5 |
| Discovery | 30 | 4 |
| Research | 20 | 2 |
| Personalization | 25 | 3 |
| Gmail | 15 | 2 |
| Orchestration | 20 | 2 |
| CLI | 15 | 2 |
| Testing | 10 | 1 |
| **TOTAL** | **175** | **~25 days** |

**Timeline: 5 weeks working solo, ~4-5 hours/day**

With focus: **3 weeks, 6 hours/day**
