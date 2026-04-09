# SAM AGENT SYSTEM — SETUP GUIDE
## India Real Estate | Mumbai · Delhi · Bangalore

---

## STEP 1 — Get Your Free API Keys (15 mins)

### 1a. Apify (Agent A — Google Maps)
1. Go to https://apify.com → Sign up free
2. Dashboard → Settings → Integrations → API token
3. Copy token → paste in .env as APIFY_TOKEN

### 1b. Gemini API (Agent C — Website Builder)
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key" → free tier included
3. Copy key → paste in .env as GEMINI_API_KEY

### 1c. GitHub (Agent D — Code Storage)
1. Go to https://github.com/settings/tokens
2. "Generate new token (classic)"
3. Tick: repo, workflow
4. Copy token → paste in .env as GITHUB_TOKEN

### 1d. Vercel (Agent D — Hosting)
1. Go to https://vercel.com → Sign up with GitHub
2. Settings → Tokens → Create token
3. Copy → paste in .env as VERCEL_TOKEN

### 1e. Twilio (Agent E — WhatsApp)
1. Go to https://twilio.com → Sign up free
2. Dashboard → Account SID + Auth Token → copy both
3. Messaging → Try it out → Send a WhatsApp message
4. Follow sandbox setup (send "join [word]" to their number)
5. Your WhatsApp number format: whatsapp:+91XXXXXXXXXX

### 1f. Gmail App Password (Agent E — Email)
1. Go to myaccount.google.com/apppasswords
2. App: Mail, Device: Other → name it "Sam Agent"
3. Copy 16-character password → paste as GMAIL_PASSWORD

---

## STEP 2 — Set Up Project (5 mins)

```bash
# Clone or create folder
mkdir sam-agent && cd sam-agent

# Copy all the agent files into this folder

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your real values
nano .env
```

---

## STEP 3 — Test Locally First (5 mins)

```bash
python main.py
```

Watch the terminal. You should see:
- Agent A searching Mumbai, Delhi, Bangalore
- Leads being found with no websites
- Websites being built via Gemini
- GitHub push happening
- Vercel deploy happening
- Sam sending YOU a WhatsApp + Gmail

---

## STEP 4 — Deploy to Railway (runs 24/7 free)

1. Go to https://railway.app → Sign up with GitHub
2. "New Project" → "Deploy from GitHub repo"
3. Push your agent folder to a GitHub repo first:
   ```bash
   git init
   git add .
   git commit -m "Initial Sam agent system"
   git remote add origin https://github.com/YOUR_USERNAME/sam-agent
   git push -u origin main
   ```
4. In Railway → select your repo → it auto-detects railway.toml
5. Go to Variables → add all your .env values one by one
6. Deploy → your agents run 24/7 even with laptop closed

---

## STEP 5 — What Happens Automatically

Every 6 hours Railway runs the full pipeline:

1. Agent A scans Google Maps in Mumbai, Delhi, Bangalore
2. Finds real estate agencies with no website
3. Agent B picks the right Framer-style template
4. Agent C builds the website via Gemini AI
5. Agent D pushes to GitHub + deploys to Vercel
6. Sam sends cold WhatsApp to the business
7. Sam sends YOU a WhatsApp + Gmail with the lead details + live URL

---

## FREE TIER LIMITS

| Service     | Free Limit                  |
|-------------|----------------------------|
| Apify       | 5 actor runs/month         |
| Gemini API  | 60 requests/minute free    |
| GitHub      | Unlimited public repos     |
| Vercel      | 100 deployments/day        |
| Twilio      | $15 free credit (~1000 msgs)|
| Railway     | $5 free credit/month       |
| Gmail       | 500 emails/day             |

---

## TROUBLESHOOTING

**WhatsApp not sending?**
→ Make sure you joined the Twilio sandbox first
→ Send "join [sandbox-word]" to +1 415 523 8886 on WhatsApp

**Gemini returning empty?**
→ Check your API key in .env
→ Gemini free tier has quota limits — add 10 second sleep between calls

**Vercel deploy failing?**
→ Make sure your VERCEL_TOKEN has correct permissions
→ Check slug has no special characters

**Railway not running?**
→ Check all env variables are set in Railway dashboard
→ Check build logs for missing dependencies
