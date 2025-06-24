from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class SmtpClientABC(ABC):
    """Abstract base class for SMTP client implementations"""
    
    @abstractmethod
    def __init__(self, api_key: str, domain: str) -> None:
        """Initialize the SMTP client with credentials"""
        pass
    
    @abstractmethod
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
        """Send an email using the configured SMTP service"""
        pass