import smtplib
from email.message import EmailMessage

from backend.config import settings


def send_complaint_email(
    recipient: str,
    complaint_id: int,
    category: str,
    description: str,
    severity: str,
    address: str
):
    message = EmailMessage()

    message["Subject"] = f"GAARD Complaint #{complaint_id} - {category}"
    message["From"] = settings.smtp_sender
    message["To"] = recipient

    message.set_content(f"""
New Civic Issue Reported

Complaint ID: GAARD-{complaint_id:06d}
Issue Category: {category}
Severity: {severity}
Location: {address}

Description:
{description}

Please review and take appropriate action.

Regards,
GAARD - Civic Issue Monitoring System
""")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)

    return True