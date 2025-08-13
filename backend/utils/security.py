import os
import random
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from cachetools import TTLCache

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Cache to store OTPs for a short time
otp_cache = TTLCache(maxsize=1000, ttl=int(os.getenv("OTP_EXPIRY", 300)))

# Brevo API key from .env
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_URL = "https://api.brevo.com/v3/smtp/email"

# Generate random OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP Email via Brevo
def send_email_otp(email, otp):
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    payload = {
        "sender": {"name": "YourAppName", "email": "your_verified_email@example.com"},
        "to": [{"email": email}],
        "subject": "Your OTP Code",
        "htmlContent": f"<h3>Your OTP is <b>{otp}</b></h3><p>This code will expire in 5 minutes.</p>"
    }
    response = requests.post(BREVO_URL, headers=headers, json=payload)
    return response.status_code, response.text

# Request OTP route
@app.route("/send-otp", methods=["POST"])
def send_otp():
    email = request.json.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    otp = generate_otp()
    otp_cache[email] = otp  # Store OTP in cache

    status, msg = send_email_otp(email, otp)
    if status == 201:
        return jsonify({"message": "OTP sent successfully"}), 200
    else:
        return jsonify({"error": "Failed to send OTP", "details": msg}), 500

# Verify OTP route
@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    email = request.json.get("email")
    otp = request.json.get("otp")

    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    stored_otp = otp_cache.get(email)
    if stored_otp and stored_otp == otp:
        del otp_cache[email]  # Remove OTP after successful verification
        return jsonify({"message": "OTP verified successfully"}), 200
    else:
        return jsonify({"error": "Invalid or expired OTP"}), 400

if __name__ == "__main__":
    app.run(debug=True)
