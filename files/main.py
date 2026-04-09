import time
import json
import schedule
from datetime import datetime

from agent_a.scraper import run as agent_a
from agent_b.template_picker import run as agent_b
from agent_c.prompt_builder import run as agent_c
from agent_d.deploy import run as agent_d
from agent_e.sam import run as agent_e

def run_pipeline():
    print(f"\n{'='*60}")
    print(f"PIPELINE START — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # AGENT A — Find leads
    new_leads = agent_a()

    if not new_leads:
        print("\n[Pipeline] No new leads. Sleeping until next run.\n")
        return

    print(f"\n[Pipeline] Processing {len(new_leads)} new leads...\n")

    for lead in new_leads:
        try:
            print(f"\n--- Processing: {lead['name']}, {lead['city']} ---")

            # AGENT B — Pick template
            b_result = agent_b(lead)
            template = b_result["template"]

            # AGENT C — Build website
            c_result = agent_c(lead, template)
            if not c_result["success"]:
                print(f"[Pipeline] Website build failed for {lead['name']}, skipping")
                continue

            # AGENT D — Deploy
            d_result = agent_d(c_result)

            # AGENT E — Sam notifies + sends cold message
            e_result = agent_e(d_result)

            print(f"\n[Pipeline] COMPLETE: {lead['name']}")
            print(f"  Website: {e_result.get('vercel_url', 'N/A')}")
            print(f"  Client WhatsApp: {'Sent' if e_result.get('whatsapp_sent') else 'Failed'}")
            print(f"  Your notifications: Sent")

            # Wait between leads to avoid API rate limits
            time.sleep(10)

        except Exception as ex:
            print(f"[Pipeline] ERROR for {lead.get('name')}: {ex}")
            continue

    print(f"\n{'='*60}")
    print(f"PIPELINE DONE — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

def main():
    print("="*60)
    print("  SAM AGENT SYSTEM — INDIA REAL ESTATE")
    print("  Running 24/7 — Mumbai, Delhi, Bangalore")
    print("="*60)

    # Run immediately on startup
    run_pipeline()

    # Then run every 6 hours automatically
    schedule.every(6).hours.do(run_pipeline)

    print("\n[System] Scheduler active. Running every 6 hours.")
    print("[System] Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
