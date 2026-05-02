"""SQLite database init and connection helpers."""
import sqlite3
import uuid
from datetime import datetime
from contextlib import contextmanager
import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT NOT NULL UNIQUE,
    industry TEXT,
    email_pattern TEXT,
    email_pattern_confidence REAL DEFAULT 0.0,
    status TEXT DEFAULT 'imported',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contacts (
    id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    title TEXT,
    linkedin_url TEXT,
    primary_email TEXT,
    email_confidence REAL DEFAULT 0.0,
    status TEXT DEFAULT 'discovered',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS company_research (
    id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL UNIQUE,
    summary TEXT,
    pain_points TEXT,
    value_prop TEXT,
    researched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS campaigns (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    status TEXT DEFAULT 'draft',
    daily_cap INTEGER DEFAULT 40,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS personalized_messages (
    id TEXT PRIMARY KEY,
    contact_id TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    step_number INTEGER NOT NULL,
    subject TEXT,
    body TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(contact_id) REFERENCES contacts(id),
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
);

CREATE TABLE IF NOT EXISTS send_records (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    contact_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    step_number INTEGER NOT NULL,
    status TEXT DEFAULT 'queued',
    gmail_message_id TEXT,
    gmail_thread_id TEXT,
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    error TEXT,
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id),
    FOREIGN KEY(contact_id) REFERENCES contacts(id),
    FOREIGN KEY(message_id) REFERENCES personalized_messages(id)
);

CREATE INDEX IF NOT EXISTS idx_send_status ON send_records(status);
CREATE INDEX IF NOT EXISTS idx_send_campaign ON send_records(campaign_id);
CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company_id);
"""


def init_db():
    """Initialize database with schema + idempotent migrations."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.executescript(SCHEMA)
    # Idempotent migrations for existing DBs
    cols = {r[1] for r in conn.execute("PRAGMA table_info(companies)").fetchall()}
    if "email_pattern" not in cols:
        conn.execute("ALTER TABLE companies ADD COLUMN email_pattern TEXT")
    if "email_pattern_confidence" not in cols:
        conn.execute("ALTER TABLE companies ADD COLUMN email_pattern_confidence REAL DEFAULT 0.0")
    conn.commit()
    conn.close()


@contextmanager
def get_db():
    """Get database connection context manager."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def new_id() -> str:
    return str(uuid.uuid4())


def now() -> str:
    return datetime.utcnow().isoformat()
