import requests
import json
import time
import os
import re
from datetime import datetime

APIFY_TOKEN = os.getenv("APIFY_TOKEN", "YOUR_APIFY_TOKEN_HERE")
CITIES = ["Mumbai", "Delhi", "Bangalore"]
BUSINESS_TYPE = "real estate agency"
OUTPUT_FILE = "agent_a/leads.json"

def search_google_maps(city, business_type):
    print(f"[Agent A] Searching: {business_type} in {city}...")
    url = "https://api.apify.com/v2/acts/compass~crawler-google-places/run-sync-get-dataset-items"
    payload = {
        "searchStringsArray": [f"{business_type} in {city} India"],
        "maxCrawledPlacesPerSearch": 40,
        "language": "en",
        "exportPlaceUrls": False,
    }
    headers = {"Content-Type": "application/json"}
    params = {"token": APIFY_TOKEN, "timeout": 120}

    try:
        resp = requests.post(url, json=payload, headers=headers, params=params, timeout=180)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"[Agent A] Apify error {resp.status_code}: {resp.text[:200]}")
            return []
    except Exception as e:
        print(f"[Agent A] Request failed: {e}")
        return []

def has_real_website(place):
    website = place.get("website", "")
    if not website:
        return False
    # Filter out social media, maps links, empty sites
    junk = ["facebook.com", "instagram.com", "justdial.com",
            "sulekha.com", "indiamart.com", "maps.google", "google.com"]
    return not any(j in website.lower() for j in junk)

def extract_lead(place, city):
    phone = place.get("phone", "") or place.get("phoneUnformatted", "")
    return {
        "id": place.get("placeId", ""),
        "name": place.get("title", "Unknown"),
        "city": city,
        "address": place.get("address", ""),
        "phone": phone,
        "email": place.get("email", ""),
        "rating": place.get("totalScore", 0),
        "reviews": place.get("reviewsCount", 0),
        "category": place.get("categoryName", BUSINESS_TYPE),
        "maps_url": place.get("url", ""),
        "website": place.get("website", "NONE"),
        "has_website": has_real_website(place),
        "found_at": datetime.now().isoformat(),
        "status": "new"
    }

def load_existing_leads():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            return json.load(f)
    return []

def save_leads(leads):
    os.makedirs("agent_a", exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)

def run():
    print(f"\n{'='*50}")
    print(f"[Agent A] Starting scan — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"[Agent A] Cities: {', '.join(CITIES)}")
    print(f"[Agent A] Target: {BUSINESS_TYPE}")
    print(f"{'='*50}\n")

    existing = load_existing_leads()
    existing_ids = {l["id"] for l in existing}

    all_new_leads = []

    for city in CITIES:
        results = search_google_maps(city, BUSINESS_TYPE)
        print(f"[Agent A] {city}: Found {len(results)} places")

        for place in results:
            lead = extract_lead(place, city)

            # Skip if already found before
            if lead["id"] in existing_ids:
                continue

            # Only keep businesses with NO real website
            if not lead["has_website"]:
                all_new_leads.append(lead)
                print(f"  [LEAD] {lead['name']} — {lead['city']} — No website")

        time.sleep(3)  # be polite between requests

    if all_new_leads:
        updated = existing + all_new_leads
        save_leads(updated)
        print(f"\n[Agent A] {len(all_new_leads)} new leads found and saved.")
    else:
        print("\n[Agent A] No new leads this scan.")

    # Write summary for Agent C to pick up
    summary = {
        "scan_time": datetime.now().isoformat(),
        "new_leads_count": len(all_new_leads),
        "new_leads": all_new_leads
    }
    with open("agent_a/latest_scan.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return all_new_leads

if __name__ == "__main__":
    run()
