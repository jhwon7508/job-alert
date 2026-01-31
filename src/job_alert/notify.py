import requests
from typing import List, Dict

def send_to_discord(webhook_url: str, jobs: List[Dict]):
    if not webhook_url:
        print("Warning: DISCORD_WEBHOOK_URL not set. Skipping notification.")
        return

    if not jobs:
        print("No jobs to notify.")
        return

    # Sort jobs by score desc
    jobs.sort(key=lambda x: x['score'], reverse=True)

    for job in jobs:
        # Format message
        message = (
            f"[{job['source']}] **{job['title']}**\n"
            f"score={job['score']}\n"
            f"reason={job['reason']}\n"
            f"{job['url']}"
        )
        
        # Ensure it fits Discord's 2000 char limit (though individual job alerts are small)
        if len(message) > 2000:
            message = message[:1997] + "..."

        try:
            response = requests.post(webhook_url, json={"content": message})
            response.raise_for_status()
        except Exception as e:
            print(f"Error sending to Discord: {e}")
