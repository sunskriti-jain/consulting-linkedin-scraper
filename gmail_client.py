"""Gmail OAuth + send + reply detection."""
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import config

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


def authenticate():
    """Run OAuth flow. Requires gmail_credentials.json from Google Cloud Console."""
    if not os.path.exists(config.GMAIL_CREDENTIALS_PATH):
        raise FileNotFoundError(
            f"Missing {config.GMAIL_CREDENTIALS_PATH}. "
            "Download OAuth client credentials from Google Cloud Console "
            "(APIs & Services > Credentials > OAuth 2.0 Client > Download JSON) "
            "and save as gmail_credentials.json"
        )

    creds = None
    if os.path.exists(config.GMAIL_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(config.GMAIL_TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(config.GMAIL_CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(config.GMAIL_TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return creds


def get_service():
    creds = authenticate()
    return build("gmail", "v1", credentials=creds)


class GmailClient:
    def __init__(self):
        self.service = get_service()

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        sender_name: str = None,
        sender_email: str = None,
        thread_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
    ) -> dict:
        """Send an email. Returns {id, threadId}."""
        sender_name = sender_name or config.SENDER_NAME
        sender_email = sender_email or config.SENDER_EMAIL

        msg = MIMEMultipart("alternative")
        msg["to"] = to
        msg["from"] = f"{sender_name} <{sender_email}>" if sender_name else sender_email
        msg["subject"] = subject
        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
            msg["References"] = in_reply_to

        msg.attach(MIMEText(body, "plain"))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        payload = {"raw": raw}
        if thread_id:
            payload["threadId"] = thread_id

        result = self.service.users().messages().send(userId="me", body=payload).execute()
        return {"id": result["id"], "threadId": result["threadId"]}

    def check_thread_replied(self, thread_id: str, our_email: str) -> bool:
        """Return True if thread has any message NOT from our_email."""
        try:
            thread = self.service.users().threads().get(userId="me", id=thread_id).execute()
            for msg in thread.get("messages", []):
                headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
                from_header = headers.get("from", "").lower()
                if our_email.lower() not in from_header:
                    return True
            return False
        except Exception as e:
            print(f"  Error checking thread {thread_id}: {e}")
            return False

    def send_test(self, to: str):
        """Send a simple test email to verify auth works."""
        return self.send_email(
            to=to,
            subject="OutreachEngine test email",
            body="This is a test. If you got this, Gmail auth is working.",
        )
