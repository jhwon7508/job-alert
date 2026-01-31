import sys
import logging
from .config import load_config
from .fetch import fetch_page
from .parse import parse_listings, extract_job_text
from .store import JobStore
from .score import score_job
from .notify import send_to_discord, send_summary
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

    store = JobStore(config.db_path)
    new_qualified_jobs = []
    
    stats = {
        "total_found": {},
        "new_jobs": 0,
        "excluded": 0,
        "qualified": 0
    }

    for source in config.sources:
        logger.info(f"Processing source: {source.name}")
        stats["total_found"][source.name] = 0
        try:
            html = fetch_page(source.url)
            listings = parse_listings(html, source.url, source.name)
            stats["total_found"][source.name] = len(listings)
            logger.info(f"Found {len(listings)} listings for {source.name}")
            
            for listing in listings:
                if store.is_seen(listing.url):
                    continue
                
                stats["new_jobs"] += 1
                # New job found
                logger.info(f"New job: {listing.title} ({listing.url})")
                
                # Fetch detail page for scoring
                try:
                    detail_html = fetch_page(listing.url)
                    detail_text = extract_job_text(detail_html)
                except Exception as e:
                    logger.warning(f"Failed to fetch detail for {listing.url}: {e}")
                    detail_text = ""
                
                score, reason = score_job(listing.title, detail_text, config.keywords, config.scoring)
                
                # Mark as seen regardless of score to avoid re-processing
                store.mark_seen(listing.url, listing.title, source.name)
                
                if score < config.digest.min_score:
                    if "Excluded" in reason:
                        stats["excluded"] += 1
                    logger.info(f"Filtered out: {listing.title} (Score: {score}, Reason: {reason})")
                    continue

                stats["qualified"] += 1
                new_qualified_jobs.append({
                    "source": source.name,
                    "title": listing.title,
                    "url": listing.url,
                    "score": score,
                    "reason": reason
                })
        except Exception as e:
            logger.error(f"Error processing source {source.name}: {e}")
            continue

    # Sort and take top items
    new_qualified_jobs.sort(key=lambda x: x['score'], reverse=True)
    digest_jobs = new_qualified_jobs[:config.digest.max_items]

    # Prepare summary
    date_str = datetime.now().strftime("%Y-%m-%d")
    summary_lines = [f"**Daily Job Alert: {date_str}**"]
    for src_name, count in stats["total_found"].items():
        summary_lines.append(f"- {src_name}: {count} listings found")
    summary_lines.append(f"- New jobs detected: {stats['new_jobs']}")
    summary_lines.append(f"- Excluded by keywords: {stats['excluded']}")
    summary_lines.append(f"- Qualified jobs: {stats['qualified']}")
    
    if not digest_jobs:
        summary_lines.insert(1, "0 qualified jobs found today.")
    
    summary_text = "\n".join(summary_lines)
    
    # Send summary first
    send_summary(config.discord_webhook_url, summary_text)

    if digest_jobs:
        logger.info(f"Sending {len(digest_jobs)} jobs to Discord")
        send_to_discord(config.discord_webhook_url, digest_jobs)
    else:
        logger.info("No new qualified jobs found.")

if __name__ == "__main__":
    main()
