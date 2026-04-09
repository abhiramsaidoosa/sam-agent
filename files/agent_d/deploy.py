import os
import json
import base64
import requests
from datetime import datetime

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN_HERE")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "YOUR_GITHUB_USERNAME")
GITHUB_REPO = os.getenv("GITHUB_REPO", "indian-client-websites")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN", "YOUR_VERCEL_TOKEN_HERE")

GITHUB_API = "https://api.github.com"

def ensure_repo_exists():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    # Check if repo exists
    r = requests.get(f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{GITHUB_REPO}", headers=headers)
    if r.status_code == 404:
        # Create it
        body = {
            "name": GITHUB_REPO,
            "description": "Auto-generated websites for Indian clients",
            "private": False,
            "auto_init": True
        }
        r = requests.post(f"{GITHUB_API}/user/repos", headers=headers, json=body)
        if r.status_code == 201:
            print(f"[Agent D] GitHub repo created: {GITHUB_REPO}")
        else:
            print(f"[Agent D] Failed to create repo: {r.text[:200]}")
    else:
        print(f"[Agent D] Repo exists: {GITHUB_REPO}")

def push_to_github(slug: str, html_content: str) -> str:
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    filepath = f"{slug}/index.html"
    encoded = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")

    # Check if file already exists (need SHA to update)
    r = requests.get(
        f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{filepath}",
        headers=headers
    )
    sha = r.json().get("sha") if r.status_code == 200 else None

    body = {
        "message": f"Add website for {slug} — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "content": encoded
    }
    if sha:
        body["sha"] = sha

    r = requests.put(
        f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{filepath}",
        headers=headers,
        json=body
    )

    if r.status_code in [200, 201]:
        file_url = r.json()["content"]["html_url"]
        print(f"[Agent D] Pushed to GitHub: {filepath}")
        return file_url
    else:
        print(f"[Agent D] GitHub push failed: {r.text[:200]}")
        return None

def deploy_to_vercel(slug: str, html_content: str) -> str:
    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "name": slug,
        "files": [
            {
                "file": "index.html",
                "data": html_content
            }
        ],
        "projectSettings": {
            "framework": None
        }
    }
    r = requests.post(
        "https://api.vercel.com/v13/deployments",
        headers=headers,
        json=body,
        timeout=60
    )
    if r.status_code in [200, 201]:
        data = r.json()
        url = f"https://{data.get('url', slug + '.vercel.app')}"
        print(f"[Agent D] Deployed to Vercel: {url}")
        return url
    else:
        print(f"[Agent D] Vercel deploy failed: {r.text[:200]}")
        # Fallback URL format
        return f"https://{slug}.vercel.app"

def run(build_result: dict) -> dict:
    if not build_result.get("success"):
        print("[Agent D] Skipping — no website was built")
        return build_result

    lead = build_result["lead"]
    slug = build_result["slug"]
    filepath = build_result["filepath"]

    print(f"[Agent D] Deploying: {lead['name']}")

    # Read the HTML file
    with open(filepath, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Push to GitHub
    ensure_repo_exists()
    github_url = push_to_github(slug, html_content)

    # Deploy to Vercel
    vercel_url = deploy_to_vercel(slug, html_content)

    return {
        **build_result,
        "github_url": github_url,
        "vercel_url": vercel_url,
        "deployed_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("[Agent D] Run via main pipeline — agent_d/deploy.py")
