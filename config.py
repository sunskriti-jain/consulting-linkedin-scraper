"""Central config loader."""
import os
from dotenv import load_dotenv

load_dotenv(override=True)

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "") or os.getenv("DASHSCOPE_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "qwen/qwen-2.5-72b-instruct")

SENDER_NAME = os.getenv("SENDER_NAME", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_TITLE = os.getenv("SENDER_TITLE", "")
SENDER_COMPANY = os.getenv("SENDER_COMPANY", "")

DAILY_EMAIL_CAP = int(os.getenv("DAILY_EMAIL_CAP", "40"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
MIN_DELAY_SECONDS = int(os.getenv("MIN_DELAY_SECONDS", "60"))
MAX_DELAY_SECONDS = int(os.getenv("MAX_DELAY_SECONDS", "120"))
BUSINESS_HOURS_START = int(os.getenv("BUSINESS_HOURS_START", "9"))
BUSINESS_HOURS_END = int(os.getenv("BUSINESS_HOURS_END", "17"))

DB_PATH = "outreach.db"
GMAIL_TOKEN_PATH = "gmail_token.json"
GMAIL_CREDENTIALS_PATH = "gmail_credentials.json"
