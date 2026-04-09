import os
import json
import requests
from datetime import datetime

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"

def build_prompt(lead: dict, template: dict) -> str:
    name = lead.get("name", "Business")
    city = lead.get("city", "India")
    address = lead.get("address", "")
    phone = lead.get("phone", "")
    email = lead.get("email", "")
    rating = lead.get("rating", 0)
    reviews = lead.get("reviews", 0)
    maps_url = lead.get("maps_url", "")
    template_url = template.get("url", "https://vertical.framer.media/")
    template_style = template.get("style", "Bold, editorial")

    prompt = f"""
Build me a complete, single-file HTML website for **{name}** — a real estate agency based in {city}, India.

**Reference design:** {template_url}
Copy this site's exact design language: {template_style}. Use oversized bold uppercase typography, stark black and white contrast, thin 0.5px grid borders, scrolling ticker bars in solid black, numbered service cards, scroll-triggered fade-in animations, and cinematic section transitions. The overall feel should be premium, editorial, and bold — like a high-end property firm.

**Animations to include:**
- Hero headline text reveals line by line on load
- Scrolling horizontal ticker bar in black with white text looping
- Scroll-triggered fade-in for each section
- Service cards lift slightly on hover
- Stat numbers count up when they enter viewport

**Business Information:**
- Business name: {name}
- Location: {city}, India
- Address: {address}
- Phone: {phone}
- Email: {email if email else 'info@' + name.lower().replace(' ', '') + '.in'}
- Google Rating: {rating} stars ({reviews} reviews)
- Google Maps: {maps_url}

**Services to feature (standard Indian real estate):**
1. Residential Properties — apartments, villas, independent houses
2. Commercial Properties — offices, shops, warehouses
3. Plot & Land — residential and agricultural plots
4. Rental Properties — managed rental homes and offices
5. Property Management — end-to-end property management services
6. Legal & Documentation — registration, paperwork, title verification

**Page Sections:**
1. Sticky nav — logo left, links center, "Get Free Consultation" button right
2. Hero — oversized two-line headline in English, short subtext, 3 animated stats ({rating}★ Rating / {reviews}+ Reviews / 10+ Years Experience), two buttons: "View Properties" and "Contact Us"
3. Black scrolling ticker — Residential · Commercial · Plots & Land · Rental · Property Management · {city} · Trusted Since 2010
4. Services — 6 cards numbered 001–006 with title and description
5. About — headline left, business info table right (address, phone, email, rating, maps link)
6. Why Choose Us — 4 points: Local Expertise · Transparent Dealing · Legal Support · Best Prices
7. Black CTA band — "Looking for your dream property?" — phone number large — "Call Now" button
8. Footer — logo, address, nav links, copyright 2025 {name}

**Design Rules:**
- Black and white only — no color
- No gradients, no shadows, no rounded corners
- All section labels in small uppercase with wide letter-spacing
- Mobile responsive
- Output as a single complete HTML file with all CSS and JS inline
- No external dependencies except Google Fonts (Inter)
- Clean, fast, professional

Output ONLY the complete HTML code. No explanation. No markdown. Just the raw HTML starting with <!DOCTYPE html>
"""
    return prompt.strip()

def call_gemini(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192
        }
    }
    try:
        resp = requests.post(GEMINI_URL, headers=headers, params=params, json=body, timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print(f"[Agent C] Gemini error {resp.status_code}: {resp.text[:300]}")
            return None
    except Exception as e:
        print(f"[Agent C] Gemini call failed: {e}")
        return None

def clean_html(raw: str) -> str:
    # Strip markdown code fences if Gemini wraps output
    raw = raw.strip()
    if raw.startswith("```html"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return raw.strip()

def save_website(lead: dict, html: str) -> str:
    slug = lead["name"].lower().replace(" ", "-").replace("&", "and")
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    city = lead["city"].lower()
    filename = f"{slug}-{city}"
    os.makedirs("agent_c/websites", exist_ok=True)
    filepath = f"agent_c/websites/{filename}.html"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[Agent C] Website saved: {filepath}")
    return filepath

def run(lead: dict, template: dict) -> dict:
    print(f"[Agent C] Building website for: {lead['name']}, {lead['city']}")
    prompt = build_prompt(lead, template)

    print(f"[Agent C] Sending to Gemini API...")
    raw_html = call_gemini(prompt)

    if not raw_html:
        return {"success": False, "lead": lead}

    html = clean_html(raw_html)
    filepath = save_website(lead, html)

    return {
        "success": True,
        "lead": lead,
        "template": template,
        "filepath": filepath,
        "slug": filepath.split("/")[-1].replace(".html", ""),
        "built_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Test with dummy lead
    test_lead = {
        "name": "Sharma Real Estate",
        "city": "Mumbai",
        "address": "Andheri West, Mumbai 400058",
        "phone": "+91 98765 43210",
        "email": "",
        "rating": 4.6,
        "reviews": 124,
        "maps_url": "https://maps.google.com/?q=sharma+real+estate+mumbai"
    }
    test_template = {
        "name": "Vertical Editorial",
        "url": "https://vertical.framer.media/",
        "style": "Bold, black & white, editorial, premium"
    }
    result = run(test_lead, test_template)
    print(json.dumps({k: v for k, v in result.items() if k != "html"}, indent=2))
