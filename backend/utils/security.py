import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

# -----------------------------
# Password Encryption & Verification
# -----------------------------
def hash_password(password):
    # Use werkzeug for hashing passwords securely
    return generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)

def verify_password(hashed_password, password):
    return check_password_hash(hashed_password, password)

# -----------------------------
# OTP Generation
# -----------------------------
def generate_otp(length=6):
    digits = string.digits
    return "".join(random.choice(digits) for _ in range(length))

# -----------------------------
# Placeholder OTP Senders
# -----------------------------
def send_email_otp(email, otp):
    # Implement email sending via SMTP or external service
    print(f"[DEBUG] OTP {otp} sent to email {email}")

def send_sms_otp(phone, otp):
    # Implement SMS sending via Twilio or other API
    print(f"[DEBUG] OTP {otp} sent to phone {phone}")
