import requests
import json
import time
import os
from datetime import datetime

APIFY_TOKEN = os.getenv("APIFY_TOKEN", "YOUR_APIFY_TOKEN_HERE")

# Indian cities with coordinates to force correct location
CITIES = [
    {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777},
    {"name": "Delhi",  "lat": 28.6139, "lng": 77.2090},
    {"name": "Bangalore", "lat": 12.9716, "lng": 77.5946}
]

BUSINESS_TYPE = "real estate agency"
OUTPUT_FILE = "agent_a/leads.json"

def search_google_maps(city: dict):
    print(f"[Agent A] Searching: {BUSINESS_TYPE} in {city['name']} India...")
    url = "https://api.apify.com/v2/acts/compass~crawler-google-places/run-sync-get-dataset-items"
    payload = {
        "searchStringsArray": [f"{BUSINESS_TYPE} in {city['name']} India"],
        "lat": city["lat"],
        "lng": city["lng"],
        "zoom": 12,
        "maxCrawledPlacesPerSearch": 20,
        "language": "en",
        "countryCode": "in",
        "exportPlaceUrls": False,
    }
    params = {"token": APIFY_TOKEN, "timeout": 120}
    try:
        resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, params=params, timeout=180)
        if resp.status_code == 200:
            data = resp.json()
            # Filter to only India results
            india_results = []
            for place in data:
                address = place.get("address", "").lower()
                if any(city_check in address for city_check in ["india", city["name"].lower(), "mumbai", "delhi", "bangalore", "bengaluru"]):
                    india_results.append(place)
                elif not any(foreign in address for foreign in ["new york", "london", "usa", "uk", "united states"]):
                    india_results.append(place)
            print(f"[Agent A] {city['name']}: {len(data)} total, {len(india_results)} in India")
            return india_results
        else:
            print(f"[Agent A] Apify error {resp.status_code}")
            return []
    except Exception as e:
        print(f"[Agent A] Request failed: {e}")
        return []

def has_real_website(place):
    website = place.get("website", "")
    if not website:
        return False
    junk = ["facebook.com", "instagram.com", "justdial.com", "sulekha.com",
            "indiamart.com", "maps.google", "google.com", "magicbricks.com",
            "99acres.com", "housing.com"]
    return not any(j in website.lower() for j in junk)

def extract_lead(place, city_name):
    phone = place.get("phone", "") or place.get("phoneUnformatted", "")
    return {
        "id": place.get("placeId", ""),
        "name": place.get("title", "Unknown"),
        "city": city_name,
        "address": place.get("address", ""),
        "phone": phone,
        "email": place.get("email", ""),
        "rating": place.get("totalScore", 0),
        "reviews": place.get("reviewsCount", 0),
        "category": BUSINESS_TYPE,
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
    print(f"[Agent A] Target: {BUSINESS_TYPE} in India")
    print(f"{'='*50}\n")

    existing = load_existing_leads()
    existing_ids = {l["id"] for l in existing}
    all_new_leads = []

    for city in CITIES:
        results = search_google_maps(city)
        for place in results:
            lead = extract_lead(place, city["name"])
            if lead["id"] in existing_ids:
                continue
            if not lead["has_website"] and lead["phone"]:
                all_new_leads.append(lead)
                print(f"  [LEAD] {lead['name']} — {lead['city']} — {lead['phone']}")
        time.sleep(5)

    if all_new_leads:
        updated = existing + all_new_leads
        save_leads(updated)
        print(f"\n[Agent A] {len(all_new_leads)} new leads found.")
    else:
        print("\n[Agent A] No new leads this scan.")

    os.makedirs("agent_a", exist_ok=True)
    with open("agent_a/latest_scan.json", "w") as f:
        json.dump({"scan_time": datetime.now().isoformat(), "new_leads_count": len(all_new_leads), "new_leads": all_new_leads}, f, indent=2, ensure_ascii=False)

    return all_new_leads

if __name__ == "__main__":
    run()
