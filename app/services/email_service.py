
import smtplib
from email.message import EmailMessage
from app.core.config import settings


def send_email_otp(receiver_email: str, otp: str):
    message = EmailMessage()
    message["Subject"] = "Your Resume Parser OTP Verification"
    message["From"] = settings.SMTP_EMAIL
    message["To"] = receiver_email

    message.set_content(
        f"Your OTP for account verification is {otp}.\n\n"
        "This OTP is valid for 5 minutes.\n"
        "Please do not share this OTP with anyone."
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(
            settings.SMTP_EMAIL,
            settings.SMTP_APP_PASSWORD
        )
        server.send_message(message)

    return True
