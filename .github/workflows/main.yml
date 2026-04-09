name: Sam Agent
on:
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python main.py
        env:
          APIFY_TOKEN: apify_api_BbfYzHtb8qp0JFfURwY8UQxBtNVYYU3IDDcx
          GEMINI_API_KEY: AIzaSyDpgjsgqWobx6_ODfWtgsi0OaNGIlhUwvE
          GITHUB_USERNAME: abhiramsaidoosa
          GITHUB_REPO: sam-agent
          VERCEL_TOKEN: vcp_41UwXikdJ5wnymCde1bjfq8VqdF1CO6rYFvy9MCz8qTzUE2Syv3ATCov
          TWILIO_ACCOUNT_SID: AC873a6430643fc363f97f8c63e9df3739
          TWILIO_AUTH_TOKEN: 6d4d5c21dd12be328884f3ed7df24bdc
          TWILIO_WHATSAPP_FROM: whatsapp:+14155238886
          YOUR_WHATSAPP: whatsapp:+16825591608
          YOUR_PHONE: "+16825591608"
          GMAIL_ADDRESS: abhiramsai.agency@gmail.com
          GMAIL_PASSWORD: xyopgmuxviuusljx
          BOOKING_LINK: https://calendly.com/abhiramsaidoosa87/30min
          PAYMENT_LINK: https://razorpay.me/abhiramsai
          YOUR_NAME: Abhiram
