from typing import Dict, Any
from dotenv import load_dotenv
import os

from src.core.message_brokers.rabbitmq import RabbitMQQueue
from src.core.email import MailgunClient, EmailBuilder
from src.core.config import get_settings

settings = get_settings()
load_dotenv()


class EmailQueueService:
    """Service to handle email sending through a message queue"""

    def __init__(self, queue_name: str = "email_queue"):
        self.queue = RabbitMQQueue(queue_name)
        self.mailgun = MailgunClient(
            api_key=settings.mailgun_api_key or os.getenv("MAILGUN_API_KEY"),
            domain=settings.mailgun_domain or os.getenv("MAILGUN_DOMAIN")
        )

    async def start_consuming(self):
        """Start consuming messages from the queue"""
        await self._consume_messages()

    async def _consume_messages(self):
        """Consume and process email messages"""
        async def process_message(message: Dict[str, Any]):
            try:
                await self.mailgun.send_email(**message)
            except Exception as e:
                print(f"Error processing email message: {str(e)}")
                raise

        self.queue.setup_consumer(process_message)
        await self.queue.start_consuming()

    async def queue_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        template_data: Dict[str, Any],
    ) -> bool:
        """Queue an email to be sent"""
        try:
            html_content = self._build_email_content(
                template_name, template_data)

            message = {
                "to_email": to_email,
                "subject": subject,
                "html_content": html_content,
                "from_email": f"{settings.mailgun_sender}@{settings.mailgun_domain}",
            }

            self.queue.publish(message)
            return True

        except Exception as e:
            print(f"Error queueing email: {str(e)}")
            return False

    def _build_email_content(self, template_name: str, template_data: Dict[str, Any]) -> str:
        """Build email content based on template name and data"""
        builder = EmailBuilder()
        company_name = settings.company_name
        support_email = settings.support_email

        match template_name:
            case "welcome":
                return (
                    builder
                    .add_header(f"Welcome to {company_name}!")
                    .add_text(f"Hello {template_data.get('name', 'there')}!")
                    .add_text("Thank you for joining us.")
                    .add_text("To get started, please verify your email address by clicking the button below:")
                    .add_button("Verify Email", template_data.get("verification_url", "#"))
                    .add_text("If you didn't create this account, please ignore this email.")
                    .add_footer(f"© 2025 {company_name}")
                    .build()
                )

            case "verification_code":
                code = template_data.get("code", "")
                return (
                    builder
                    .add_header("Verify Your Email")
                    .add_text(f"Hello {template_data.get('name', 'there')},")
                    .add_text("Please use the following code to verify your email address:")
                    .add_bold(code)
                    .add_text("This code will expire in 30 minutes.")
                    .add_text("If you didn't request this code, please ignore this email.")
                    .add_footer(f"© 2025 {company_name}")
                    .build()
                )

            case "reset_password":
                return (
                    builder
                    .add_header("Password Reset Request")
                    .add_text(f"Hello {template_data.get('name', 'there')},")
                    .add_text("We received a request to reset your password.")
                    .add_text("Click the button below to create a new password:")
                    .add_button("Reset Password", template_data.get("reset_url", "#"))
                    .add_text("This link will expire in 60 minutes.")
                    .add_text("If you didn't request this change, please contact our support team immediately.")
                    .add_divider()
                    .add_text(f"Contact support: {support_email}")
                    .add_footer(f"© 2025 {company_name}")
                    .build()
                )

            case "password_changed":
                return (
                    builder
                    .add_header("Password Changed Successfully")
                    .add_text(f"Hello {template_data.get('name', 'there')},")
                    .add_text("Your password has been changed successfully.")
                    .add_text("If you did not make this change, please contact our support team immediately:")
                    .add_link(support_email, f"mailto:{support_email}")
                    .add_divider()
                    .add_text("For your security, we recommend:")
                    .add_list([
                        "Using a strong, unique password",
                        "Enabling two-factor authentication if available",
                        "Never sharing your password with others"
                    ])
                    .add_footer(f"© 2025 {company_name}")
                    .build()
                )

            case "account_deactivated":
                return (
                    builder
                    .add_header("Account Deactivated")
                    .add_text(f"Hello {template_data.get('name', 'there')},")
                    .add_text("Your account has been deactivated as requested.")
                    .add_text("If you'd like to reactivate your account, you can do so by clicking the button below:")
                    .add_button("Reactivate Account", template_data.get("reactivation_url", "#"))
                    .add_text("If you did not request this change, please contact our support team immediately.")
                    .add_divider()
                    .add_text(f"Contact support: {support_email}")
                    .add_footer(f"© 2025 {company_name}")
                    .build()
                )

            case "account_locked":
                return (
                    builder
                    .add_header("Account Security Alert")
                    .add_text(f"Hello {template_data.get('name', 'there')},")
                    .add_text("We detected unusual activity on your account and have temporarily locked it for your security.")
                    .add_text("To unlock your account, please click the button below:")
                    .add_button("Unlock Account", template_data.get("unlock_url", "#"))
                    .add_divider()
                    .add_text("Recent activity detected:")
                    .add_list([
                        f"Time: {template_data.get('timestamp', 'Unknown')}",
                        f"Location: {template_data.get('location', 'Unknown')}",
                        f"IP Address: {template_data.get('ip_address', 'Unknown')}"
                    ])
                    .add_text("If this was you, you can safely unlock your account. If not, please contact support immediately.")
                    .add_divider()
                    .add_text(f"Contact support: {support_email}")
                    .add_footer(f"© 2025 {company_name}")
                    .build()
                )

            case "login_notification":
                return (
                    builder
                    .add_header("New Login Detected")
                    .add_text(f"Hello {template_data.get('name', 'there')},")
                    .add_text("We detected a new login to your account from an unrecognized device:")
                    .add_list([
                        f"Time: {template_data.get('timestamp', 'Unknown')}",
                        f"Device: {template_data.get('device', 'Unknown')}",
                        f"Location: {template_data.get('location', 'Unknown')}",
                        f"IP Address: {template_data.get('ip_address', 'Unknown')}"
                    ])
                    .add_text("If this wasn't you, please secure your account immediately:")
                    .add_button("Secure Account", template_data.get("secure_url", "#"))
                    .add_footer(f"© 2025 {company_name}")
                    .build()
                )

            case "email_changed":
                return (
                    builder
                    .add_header("Email Address Changed")
                    .add_text(f"Hello {template_data.get('name', 'there')},")
                    .add_text("Your email address has been changed successfully.")
                    .add_text(f"Old email: {template_data.get('old_email', 'Unknown')}")
                    .add_text(f"New email: {template_data.get('new_email', 'Unknown')}")
                    .add_text("If you did not make this change, please contact our support team immediately:")
                    .add_link(support_email, f"mailto:{support_email}")
                    .add_footer(f"© 2025 {company_name}")
                    .build()
                )

            case _:
                raise ValueError(f"Unknown email template: {template_name}")
