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


def _token_path(account: str) -> str:
    if account == "default":
        return config.GMAIL_TOKEN_PATH
    return f"gmail_token_{account}.json"


def _creds_path(account: str) -> str:
    if account == "default":
        return config.GMAIL_CREDENTIALS_PATH
    # Fall back to shared credentials file if no account-specific one exists
    account_specific = f"gmail_credentials_{account}.json"
    return account_specific if os.path.exists(account_specific) else config.GMAIL_CREDENTIALS_PATH


def authenticate(account: str = "default"):
    """Run OAuth flow for the given account name.

    Token is stored as gmail_token_{account}.json (or gmail_token.json for 'default').
    Credentials file: gmail_credentials_{account}.json if present, else gmail_credentials.json.
    """
    token_path = _token_path(account)
    creds_path = _creds_path(account)

    if not os.path.exists(creds_path):
        raise FileNotFoundError(
            f"Missing {creds_path}. "
            "Download OAuth client credentials from Google Cloud Console "
            "(APIs & Services > Credentials > OAuth 2.0 Client > Download JSON)."
        )

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return creds


def get_service(account: str = "default"):
    creds = authenticate(account)
    return build("gmail", "v1", credentials=creds)


class GmailClient:
    def __init__(self, account: str = "default"):
        """
        account: name of the Gmail account to use.
          "default"  → gmail_token.json / gmail_credentials.json (original behaviour)
          "vo"       → gmail_token_vo.json  (run `python gmail_client.py auth vo` to set up)
          "fv"       → gmail_token_fv.json
          any name   → gmail_token_{name}.json
        """
        self.account = account
        self.service = get_service(account)

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

    def get_message_details(self, message_id: str) -> dict:
        """Fetch full message metadata including headers, labels, and content."""
        try:
            msg = self.service.users().messages().get(userId="me", id=message_id, format='metadata').execute()
            headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
            labels = msg.get("labelIds", [])
            return {
                "id": msg["id"],
                "threadId": msg["threadId"],
                "headers": headers,
                "labels": labels,
                "date": headers.get("date"),
                "from": headers.get("from"),
                "subject": headers.get("subject"),
            }
        except Exception as e:
            print(f"  Error getting message details for {message_id}: {e}")
            return {}

    def check_message_opened(self, message_id: str) -> bool:
        """Return True if message has been opened (UNREAD label absent)."""
        try:
            msg = self.service.users().messages().get(userId="me", id=message_id, format='metadata').execute()
            labels = msg.get("labelIds", [])
            # UNREAD label means message is unopened; absence means opened
            return "UNREAD" not in labels
        except Exception as e:
            print(f"  Error checking if message opened {message_id}: {e}")
            return False

    def detect_bounce(self, thread_id: str) -> dict:
        """Detect if thread contains a bounce. Returns {bounced, bounce_reason, bounce_date, bounce_source}."""
        try:
            thread = self.service.users().threads().get(userId="me", id=thread_id, format='metadata').execute()
            messages = thread.get("messages", [])

            for msg in messages:
                labels = msg.get("labelIds", [])
                headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}

                # Check 1: SPAM folder
                if "SPAM" in labels:
                    return {
                        "bounced": True,
                        "bounce_reason": "Message in SPAM folder",
                        "bounce_date": headers.get("date"),
                        "bounce_source": "SPAM",
                    }

                # Check 2: NDR messages from mail system
                from_header = headers.get("from", "").lower()
                subject = headers.get("subject", "").lower()

                bounce_senders = ["mailer-daemon", "postmaster", "mail delivery subsystem", "noreply", "no-reply"]
                if any(sender in from_header for sender in bounce_senders):
                    bounce_subjects = ["undeliverable", "delivery failed", "failure notice", "delivery status notification", "returned mail"]
                    if any(subj in subject for subj in bounce_subjects):
                        return {
                            "bounced": True,
                            "bounce_reason": f"NDR: {subject}",
                            "bounce_date": headers.get("date"),
                            "bounce_source": "NDR",
                        }

                # Check 3: 5xx status codes in headers
                status_header = headers.get("status", "")
                x_status = headers.get("x-status", "")
                if "5" in status_header or "5" in x_status:
                    return {
                        "bounced": True,
                        "bounce_reason": f"5xx error: {status_header or x_status}",
                        "bounce_date": headers.get("date"),
                        "bounce_source": "Header",
                    }

            return {
                "bounced": False,
                "bounce_reason": None,
                "bounce_date": None,
                "bounce_source": None,
            }
        except Exception as e:
            print(f"  Error detecting bounce for thread {thread_id}: {e}")
            return {
                "bounced": False,
                "bounce_reason": f"Error: {str(e)}",
                "bounce_date": None,
                "bounce_source": None,
            }

    def get_thread_latest_message_date(self, thread_id: str) -> Optional[str]:
        """Get the date of the most recent message in the thread."""
        try:
            thread = self.service.users().threads().get(userId="me", id=thread_id, format='metadata').execute()
            messages = thread.get("messages", [])
            if not messages:
                return None

            # Get the last message
            last_msg = messages[-1]
            headers = {h["name"].lower(): h["value"] for h in last_msg["payload"].get("headers", [])}
            return headers.get("date")
        except Exception as e:
            print(f"  Error getting thread latest date for {thread_id}: {e}")
            return None

    def check_thread_replied_with_timestamp(self, thread_id: str, our_email: str) -> dict:
        """Check if thread has a reply and return timestamp. Returns {replied, reply_date, reply_from}."""
        try:
            thread = self.service.users().threads().get(userId="me", id=thread_id, format='metadata').execute()
            messages = thread.get("messages", [])

            for msg in messages:
                headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
                from_header = headers.get("from", "").lower()

                # Look for a message NOT from our email
                if our_email.lower() not in from_header:
                    return {
                        "replied": True,
                        "reply_date": headers.get("date"),
                        "reply_from": headers.get("from"),
                    }

            return {
                "replied": False,
                "reply_date": None,
                "reply_from": None,
            }
        except Exception as e:
            print(f"  Error checking thread replied with timestamp for {thread_id}: {e}")
            return {
                "replied": False,
                "reply_date": None,
                "reply_from": None,
            }

    def check_thread_engagement(self, thread_id: str, our_email: str) -> dict:
        """Single thread.get call that returns reply + bounce info together.

        NOTE on opens: Gmail API cannot detect whether a *recipient* opened an email.
        The UNREAD label only reflects your own mailbox state, not the recipient's.
        Opens require email tracking pixels (not implemented here).

        Returns: {replied, reply_date, reply_from, bounced, bounce_reason, bounce_date, bounce_source}
        """
        try:
            thread = self.service.users().threads().get(userId="me", id=thread_id, format='metadata').execute()
            messages = thread.get("messages", [])

            replied = False
            reply_date = None
            reply_from = None
            bounced = False
            bounce_reason = None
            bounce_date = None
            bounce_source = None

            # NDR / bounce sender patterns
            bounce_senders = ["mailer-daemon", "postmaster", "mail delivery subsystem", "mailer daemon"]
            bounce_subjects = [
                "undeliverable", "delivery failed", "failure notice",
                "delivery status notification", "returned mail", "mail delivery failed",
                "delivery failure", "nondelivery", "non-delivery",
            ]

            for msg in messages:
                labels = msg.get("labelIds", [])
                headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
                from_header = headers.get("from", "").lower()
                subject = headers.get("subject", "").lower()

                # Skip our own sent messages — only inspect inbound/bounce messages
                is_our_message = our_email.lower() in from_header or "SENT" in labels
                if is_our_message:
                    continue

                # Bounce check 1: SPAM label on a received message
                if "SPAM" in labels:
                    bounced = True
                    bounce_reason = "Message flagged as SPAM"
                    bounce_date = headers.get("date")
                    bounce_source = "SPAM"
                    continue

                # Bounce check 2: NDR message from mailer-daemon / postmaster
                # Requires BOTH a bounce sender AND a bounce subject to avoid false positives
                if any(s in from_header for s in bounce_senders) and any(s in subject for s in bounce_subjects):
                    bounced = True
                    bounce_reason = f"NDR: {headers.get('subject', subject)}"
                    bounce_date = headers.get("date")
                    bounce_source = "NDR"
                    continue

                # Reply: any inbound message in the thread that is NOT a bounce
                if not replied:
                    replied = True
                    reply_date = headers.get("date")
                    reply_from = headers.get("from")

            return {
                "replied": replied,
                "reply_date": reply_date,
                "reply_from": reply_from,
                "bounced": bounced,
                "bounce_reason": bounce_reason,
                "bounce_date": bounce_date,
                "bounce_source": bounce_source,
            }
        except Exception as e:
            print(f"  Error checking thread engagement for {thread_id}: {e}")
            return {
                "replied": False, "reply_date": None, "reply_from": None,
                "bounced": False, "bounce_reason": None, "bounce_date": None, "bounce_source": None,
            }

    def send_test(self, to: str):
        """Send a simple test email to verify auth works."""
        return self.send_email(
            to=to,
            subject="OutreachEngine test email",
            body="This is a test. If you got this, Gmail auth is working.",
        )


if __name__ == "__main__":
    import sys
    # Usage:
    #   python gmail_client.py auth <account_name>
    #       → runs OAuth browser flow and saves gmail_token_<account_name>.json
    #   python gmail_client.py test <account_name> <to_email>
    #       → sends a test email from that account
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python gmail_client.py auth <account_name>")
        print("  python gmail_client.py test <account_name> <to_email>")
        print()
        print("Account names: 'default', 'vo', 'fv', 'bbs', or any custom name.")
        print("Token stored as: gmail_token_<account_name>.json")
        sys.exit(1)

    cmd = sys.argv[1]
    acct = sys.argv[2]

    if cmd == "auth":
        print(f"Authenticating account '{acct}'...")
        print(f"  Credentials file : {_creds_path(acct)}")
        print(f"  Token will save to: {_token_path(acct)}")
        authenticate(acct)
        print(f"[OK] Token saved to {_token_path(acct)}")

    elif cmd == "test":
        if len(sys.argv) < 4:
            print("Usage: python gmail_client.py test <account_name> <to_email>")
            sys.exit(1)
        to_email = sys.argv[3]
        print(f"Sending test email from account '{acct}' to {to_email}...")
        client = GmailClient(account=acct)
        result = client.send_test(to_email)
        print(f"[OK] Sent — message ID: {result['id']}")

    else:
        print(f"Unknown command: {cmd}. Use 'auth' or 'test'.")
        sys.exit(1)
