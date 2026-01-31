import requests
from typing import List, Dict

def send_to_discord(webhook_url: str, jobs: List[Dict]):
    if not webhook_url:
        print("Warning: DISCORD_WEBHOOK_URL not set. Skipping notification.")
        return

    # Sort jobs by score desc
    jobs.sort(key=lambda x: x['score'], reverse=True)

    for job in jobs:
        # Format message
        message = (
            f"[{job['source']}] **{job['title']}**\n"
            f"Score: {job['score']}\n"
            f"Reason: {job['reason']}\n"
            f"URL: {job['url']}"
        )
        
        # Ensure it fits Discord's 2000 char limit
        if len(message) > 2000:
            message = message[:1997] + "..."

        try:
            response = requests.post(webhook_url, json={"content": message})
            response.raise_for_status()
        except Exception as e:
            print(f"Error sending to Discord: {e}")

def send_summary(webhook_url: str, summary: str):
    if not webhook_url:
        return
    try:
        response = requests.post(webhook_url, json={"content": summary})
        response.raise_for_status()
    except Exception as e:
        print(f"Error sending summary to Discord: {e}")
