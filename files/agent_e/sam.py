import os
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- YOUR CREDENTIALS ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "YOUR_TWILIO_SID")
TWILIO_AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN",  "YOUR_TWILIO_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")  # Twilio sandbox
YOUR_WHATSAPP      = os.getenv("YOUR_WHATSAPP", "whatsapp:+91XXXXXXXXXX")  # YOUR number

GMAIL_ADDRESS  = os.getenv("GMAIL_ADDRESS",  "YOUR_EMAIL@gmail.com")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "YOUR_APP_PASSWORD")  # Gmail App Password

# Calendar booking link (your Calendly or Google Meet)
BOOKING_LINK = os.getenv("BOOKING_LINK", "https://calendly.com/YOUR_LINK")

def send_whatsapp_to_you(message: str):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    data = {
        "From": TWILIO_WHATSAPP_FROM,
        "To": YOUR_WHATSAPP,
        "Body": message
    }
    try:
        r = requests.post(url, data=data, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        if r.status_code == 201:
            print(f"[Sam] WhatsApp sent to you")
        else:
            print(f"[Sam] WhatsApp failed: {r.text[:200]}")
    except Exception as e:
        print(f"[Sam] WhatsApp error: {e}")

def send_gmail_to_you(subject: str, body: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = GMAIL_ADDRESS
        msg["To"]      = GMAIL_ADDRESS
        msg.attach(MIMEText(body, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, GMAIL_ADDRESS, msg.as_string())
        print(f"[Sam] Gmail sent to you")
    except Exception as e:
        print(f"[Sam] Gmail error: {e}")

def send_cold_whatsapp_to_client(lead: dict, vercel_url: str):
    name = lead.get("name", "")
    phone = lead.get("phone", "").replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        phone = "+91" + phone.lstrip("0")

    message = f"""Hi, I came across *{name}* on Google Maps.

I noticed you don't have a website yet — so I went ahead and built one for you.

Have a look: {vercel_url}

Takes just 5 minutes to see. If you like it, it's yours. If not, no problem at all.

— Sam"""

    to = f"whatsapp:{phone}"
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    data = {"From": TWILIO_WHATSAPP_FROM, "To": to, "Body": message}
    try:
        r = requests.post(url, data=data, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        if r.status_code == 201:
            print(f"[Sam] Cold WhatsApp sent to client: {name}")
            return True
        else:
            print(f"[Sam] Client WhatsApp failed: {r.status_code}")
            return False
    except Exception as e:
        print(f"[Sam] Client WhatsApp error: {e}")
        return False

def build_notification(lead: dict, vercel_url: str, github_url: str) -> tuple:
    name    = lead.get("name", "Unknown")
    city    = lead.get("city", "")
    phone   = lead.get("phone", "N/A")
    address = lead.get("address", "")
    rating  = lead.get("rating", 0)
    reviews = lead.get("reviews", 0)

    whatsapp_msg = f"""🔔 *New Lead Found — Sam*

*{name}*
📍 {city} | {address}
📞 {phone}
⭐ {rating} ({reviews} reviews)

🌐 Website live: {vercel_url}
📂 GitHub: {github_url}

✅ Cold message sent to client on WhatsApp.

Reply *YES* to book a Google Meet with them.
Book link: {BOOKING_LINK}"""

    email_subject = f"[Sam] New Lead: {name}, {city}"
    email_body = f"""
<html><body style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px">
<h2 style="border-bottom:2px solid #000;padding-bottom:10px">New Lead — {name}</h2>
<table style="width:100%;border-collapse:collapse">
  <tr><td style="padding:8px;color:#666;width:120px">Business</td><td style="padding:8px"><strong>{name}</strong></td></tr>
  <tr style="background:#f5f5f5"><td style="padding:8px;color:#666">City</td><td style="padding:8px">{city}</td></tr>
  <tr><td style="padding:8px;color:#666">Address</td><td style="padding:8px">{address}</td></tr>
  <tr style="background:#f5f5f5"><td style="padding:8px;color:#666">Phone</td><td style="padding:8px">{phone}</td></tr>
  <tr><td style="padding:8px;color:#666">Rating</td><td style="padding:8px">⭐ {rating} ({reviews} reviews)</td></tr>
  <tr style="background:#f5f5f5"><td style="padding:8px;color:#666">Website</td><td style="padding:8px"><a href="{vercel_url}">{vercel_url}</a></td></tr>
  <tr><td style="padding:8px;color:#666">GitHub</td><td style="padding:8px"><a href="{github_url}">{github_url}</a></td></tr>
</table>
<br>
<p style="background:#000;color:#fff;padding:15px;text-align:center">
  <strong>Cold message already sent to client on WhatsApp.</strong>
</p>
<p><a href="{BOOKING_LINK}" style="background:#000;color:#fff;padding:10px 20px;text-decoration:none;display:inline-block">Book Google Meet</a></p>
<p style="color:#999;font-size:12px">Sent by Sam — Your Automated Sales Agent</p>
</body></html>"""

    return whatsapp_msg, email_subject, email_body

def log_lead(lead: dict, result: dict):
    os.makedirs("agent_e", exist_ok=True)
    log_file = "agent_e/sales_log.json"
    logs = []
    if os.path.exists(log_file):
        with open(log_file) as f:
            logs = json.load(f)
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "lead_name": lead.get("name"),
        "city": lead.get("city"),
        "vercel_url": result.get("vercel_url"),
        "whatsapp_sent": result.get("whatsapp_sent"),
        "notification_sent": result.get("notification_sent")
    })
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)

def run(deploy_result: dict) -> dict:
    if not deploy_result.get("success"):
        return deploy_result

    lead        = deploy_result["lead"]
    vercel_url  = deploy_result.get("vercel_url", "")
    github_url  = deploy_result.get("github_url", "")

    print(f"[Sam] Processing lead: {lead['name']}, {lead['city']}")

    # 1. Send cold WhatsApp to the CLIENT
    whatsapp_sent = send_cold_whatsapp_to_client(lead, vercel_url)

    # 2. Notify YOU via WhatsApp + Gmail
    whatsapp_msg, email_subject, email_body = build_notification(lead, vercel_url, github_url)
    send_whatsapp_to_you(whatsapp_msg)
    send_gmail_to_you(email_subject, email_body)

    result = {
        **deploy_result,
        "whatsapp_sent": whatsapp_sent,
        "notification_sent": True,
        "completed_at": datetime.now().isoformat()
    }

    log_lead(lead, result)
    print(f"[Sam] Done — {lead['name']}")
    return result

if __name__ == "__main__":
    print("[Sam] Run via main pipeline")
