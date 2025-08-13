import os
import random
import string
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# -----------------------------
# Password Encryption & Verification
# -----------------------------
def hash_password(password):
    return generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)

def verify_password(hashed_password, password):
    return check_password_hash(hashed_password, password)


# -----------------------------
# OTP Cache (in-memory with expiry)
# -----------------------------
OTP_CACHE = {}  # { "email_or_phone": {"otp": "123456", "expires_at": datetime_obj} }
OTP_EXPIRY_MINUTES = 5


def generate_otp(length=6):
    return "".join(random.choice(string.digits) for _ in range(length))


# -----------------------------
# Send Email OTP using Brevo/Sendinblue
# -----------------------------
def send_email_otp(email, otp):
    """
    Send OTP via Brevo/Sendinblue Transactional Email API.
    Requires: BREVO_API_KEY in .env
    """
    api_key = os.getenv("BREVO_API_KEY")
    if not api_key:
        raise ValueError("BREVO_API_KEY is missing in .env file")

    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {"name": "YourApp", "email": "no-reply@yourapp.com"},
        "to": [{"email": email}],
        "subject": "Your OTP Code",
        "htmlContent": f"<p>Your OTP is <b>{otp}</b>. It will expire in {OTP_EXPIRY_MINUTES} minutes.</p>"
    }
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 201:
        raise Exception(f"Email sending failed: {response.text}")
    return True


# -----------------------------
# OTP Store & Verify
# -----------------------------
def store_otp(identifier, otp):
    """
    Store OTP with expiry time in memory
    identifier = email or phone
    """
    expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=OTP_EXPIRY_MINUTES)
    OTP_CACHE[identifier] = {"otp": otp, "expires_at": expiry_time}


def verify_otp(identifier, otp):
    """
    Verify OTP and auto-remove if valid
    """
    if identifier not in OTP_CACHE:
        return False, "OTP not found. Please request a new one."

    record = OTP_CACHE[identifier]
    if datetime.datetime.now() > record["expires_at"]:
        del OTP_CACHE[identifier]
        return False, "OTP expired. Please request a new one."

    if record["otp"] != otp:
        return False, "Invalid OTP."

    # OTP valid — remove from cache to prevent reuse
    del OTP_CACHE[identifier]
    return True, "OTP verified successfully."


# -----------------------------
# Generate & Send OTP (Full Flow)
# -----------------------------
def initiate_email_otp_flow(email):
    otp = generate_otp()
    store_otp(email, otp)
    send_email_otp(email, otp)
    return f"OTP sent to {email}"
