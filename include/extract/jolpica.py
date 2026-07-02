import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://api.jolpi.ca/ergast/f1"
PAGE_LIMIT = 100        # Jolpica caps a page at 100 rows
POLITE_DELAY = 0.5      # seconds between requests, to be a good citizen


def _session():
    """A requests session that auto-retries on rate-limit (429) and server errors."""
    retries = Retry(
        total=5,
        backoff_factor=2,                         # waits 2s, 4s, 8s... between retries
        status_forcelist=[429, 500, 502, 503, 504],
        respect_retry_after_header=True,
    )
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.headers.update({"User-Agent": "f1-learning-pipeline"})
    return s


def fetch_all_pages(season: int, endpoint: str) -> list:
    """Loop through every page for a season+endpoint. Returns raw JSON pages, untouched."""
    session = _session()
    pages, offset = [], 0
    while True:
        url = f"{BASE_URL}/{season}/{endpoint}.json"
        resp = session.get(url, params={"limit": PAGE_LIMIT, "offset": offset}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        pages.append(data)                        # store the whole page as-is

        total = int(data["MRData"]["total"])
        offset += PAGE_LIMIT
        if offset >= total:
            break
        time.sleep(POLITE_DELAY)
    return pages