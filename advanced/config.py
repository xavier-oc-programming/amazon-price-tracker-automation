# ── Paths ────────────────────────────────────────────────────────────────────
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

# ── Scraping ─────────────────────────────────────────────────────────────────
PRODUCT_URL = (
    "https://www.amazon.com/dp/B075CYMYK6"
    "?ref_=cm_sw_r_cp_ud_ct_FM9M699VKHTT47YD50Q6&th=1"
)

BROWSER_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.5",
    "Prefer": "safe",
    "Priority": "u=0, i",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:143.0) "
        "Gecko/20100101 Firefox/143.0"
    ),
}

PRICE_CSS_CLASS = "aok-offscreen"

# ── Thresholds ────────────────────────────────────────────────────────────────
TARGET_PRICE = 100.00  # USD — send alert if price drops below this

# ── Email / SMTP ──────────────────────────────────────────────────────────────
SMTP_PORT = 587
