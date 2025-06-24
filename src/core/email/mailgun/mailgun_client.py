import httpx
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

from ..abc.smtp_client import SmtpClientABC

class MailgunClient(SmtpClientABC):
    """Mailgun implementation of SMTP client"""
    
    def __init__(self, api_key: str, domain: str) -> None:
        self.api_key = api_key
        self.domain = domain
        self.base_url = f"https://api.mailgun.net/v3/{domain}/"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send an email using Mailgun's API"""
        if not from_email:
            from_email = f"<no_reply@{self.domain}>"

        data = {
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "html": html_content
        }

        if cc:
            data["cc"] = ", ".join(cc)
        if bcc:
            data["bcc"] = ", ".join(bcc)
        if reply_to:
            data["h:Reply-To"] = reply_to
        if custom_headers:
            for key, value in custom_headers.items():
                data[f"h:{key}"] = value

        files = []
        if attachments:
            for attachment in attachments:
                if "content" in attachment and "filename" in attachment:
                    files.append(
                        ("attachment", (attachment["filename"], attachment["content"]))
                    )

        auth = (
            "api",
            self.api_key,
        )
        endpoint = urljoin(self.base_url, "messages")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    data=data,
                    files=files,
                    auth=auth,
                    timeout=30.0
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Error sending email via Mailgun: {str(e)}")
            return False