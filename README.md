# job-alert

MVP for a personal job alert system that scrapes job sites and sends a daily digest to Discord.

## Overview

This project is a batch script designed to:
- Scrape public job listings from configured sources.
- Deduplicate jobs using a local SQLite database.
- Score new jobs based on keywords in title and description.
- Send the top-scoring jobs to a Discord channel via a webhook.
- Run automatically once a day using GitHub Actions.

## Local Setup

### Prerequisites
- Python 3.12+

### Installation
1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### `sources.yaml`
Modify `sources.yaml` to customize:
- `sources`: List of site names and search URLs.
- `keywords`: `include` (positive points) and `exclude` (immediate discard).
- `scoring`: Points for keyword matches in title or body.
- `digest`: `min_score` for notification and `max_items` per run.

### Environment Variables
- `DISCORD_WEBHOOK_URL`: (Required) Your Discord channel webhook URL.
- `DB_PATH`: (Optional) Path to the SQLite database file (default: `jobs.db`).

## Running Locally

```bash
export DISCORD_WEBHOOK_URL="your_webhook_url_here"
export PYTHONPATH=src
python -m job_alert.main
```

## GitHub Actions

The system is configured to run daily via GitHub Actions (`.github/workflows/daily.yml`).

### Setup in GitHub:
1. Go to your repository settings.
2. Navigate to **Secrets and variables** > **Actions**.
3. Add a **New repository secret**:
   - Name: `DISCORD_WEBHOOK_URL`
   - Value: Your Discord webhook URL.

### How it works:
- Runs every day at 00:00 UTC.
- Caches pip dependencies for faster runs.
- Downloads the previous run's `jobs.db` from artifacts to maintain deduplication.
- Runs the script.
- Uploads the updated `jobs.db` as an artifact (kept for 14 days).

## Safety & Robustness
- Fetches each page at most once per run.
- Includes random delays between requests.
- Uses common browser User-Agents.
- Continues processing other sites if one fails.
- Retries on transient network errors using `tenacity`.
