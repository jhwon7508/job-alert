from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dataclasses import dataclass
from typing import List

@dataclass
class JobListing:
    title: str
    url: str
    source_name: str

def parse_listings(html: str, base_url: str, source_name: str) -> List[JobListing]:
    """
    Generic parser that looks for common job link patterns.
    Can be extended with site-specific logic.
    """
    soup = BeautifulSoup(html, 'html.parser')
    listings = []
    
    # Heuristic: look for <a> tags that might be job links
    # This is a generic implementation as requested for MVP
    # Specific sites might need more targeted selectors
    
    if "wanted.co.kr" in base_url:
        # Wanted specific (example)
        items = soup.select('a[href^="/wd/"]')
        for item in items:
            title_elem = item.select_one('strong, h4, span.job-card-title')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
            url = urljoin(base_url, item['href'])
            listings.append(JobListing(title=title, url=url, source_name=source_name))
            
    elif "jobkorea.co.kr" in base_url:
        # JobKorea specific (example)
        items = soup.select('div.post-list-info a.title, td.tplTit a')
        for item in items:
            title = item.get_text(strip=True)
            url = urljoin(base_url, item['href'])
            listings.append(JobListing(title=title, url=url, source_name=source_name))
            
    elif "saramin.co.kr" in base_url:
        # Saramin specific: Extract links with 'rec_idx' or typical job view patterns
        items = soup.find_all('a', href=True)
        for item in items:
            href = item['href']
            # Search for typical Saramin job detail patterns
            if any(p in href for p in ["/zf_user/jobs/relay/view", "/zf_user/jobs/view", "rec_idx="]):
                title = item.get_text(strip=True)
                # If title is empty, look for it in parents or children (some cards have links on images/empty tags)
                if not title:
                    # Try to find a title in the parent card
                    parent_card = item.find_parent(['div', 'li', 'tr'])
                    if parent_card:
                        title_elem = parent_card.select_one('.job_tit, .item_title, strong, h2')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                
                if not title:
                    title = "Saramin Job Listing"

                url = urljoin("https://www.saramin.co.kr", href)
                listings.append(JobListing(title=title, url=url, source_name=source_name))
    else:
        # Fallback generic logic
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Very basic heuristic for job links
            if any(path in href.lower() for path in ['/job/', '/recruitment/', '/wd/', '/view/']):
                title = a.get_text(strip=True)
                if len(title) > 5:
                    url = urljoin(base_url, href)
                    listings.append(JobListing(title=title, url=url, source_name=source_name))

    # Deduplicate within the same page
    unique_listings = {}
    for l in listings:
        if l.url not in unique_listings:
            unique_listings[l.url] = l
            
    return list(unique_listings.values())

def extract_job_text(html: str) -> str:
    """
    Extract readable text from job detail page.
    """
    soup = BeautifulSoup(html, 'html.parser')
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()
        
    # Get text
    text = soup.get_text(separator=' ')
    
    # Break into lines and remove leading/trailing whitespace
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text
