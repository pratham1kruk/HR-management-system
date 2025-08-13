import os
import secrets
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

load_dotenv()

# OTP in-memory store: {email: {"otp": str, "expires_at": datetime}}
otp_cache = {}

def generate_otp(length=6):
    """Generate a secure numeric OTP."""
    return ''.join(secrets.choice("0123456789") for _ in range(length))

def store_otp(email, otp):
    """Store OTP with expiry."""
    expiry_time = datetime.utcnow() + timedelta(minutes=int(os.getenv("OTP_EXPIRY_MINUTES", 5)))
    otp_cache[email] = {"otp": otp, "expires_at": expiry_time}

def verify_stored_otp(email, otp_input):
    """Verify OTP and remove it if valid."""
    if email not in otp_cache:
        return False, "No OTP found or expired."

    record = otp_cache[email]
    if datetime.utcnow() > record["expires_at"]:
        del otp_cache[email]
        return False, "OTP expired."

    if record["otp"] != otp_input:
        return False, "Invalid OTP."

    del otp_cache[email]
    return True, "OTP verified."

def initiate_email_otp_flow(email):
    """Generate OTP, store it, and send via Brevo email."""
    otp = generate_otp()
    store_otp(email, otp)

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

    sender_email = os.getenv("BREVO_SENDER_EMAIL")
    subject = "Your Password Reset OTP"
    content = f"Your OTP is: {otp}\nIt expires in {os.getenv('OTP_EXPIRY_MINUTES', 5)} minutes."

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email}],
        sender={"email": sender_email},
        subject=subject,
        text_content=content
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        raise Exception(f"Failed to send OTP email: {e}")
