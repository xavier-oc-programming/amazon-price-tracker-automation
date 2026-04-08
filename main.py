import os
import re
import requests
import smtplib
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# -------------------------------------------------------
# 1. Load environment variables (.env file)
# -------------------------------------------------------
load_dotenv()

SMTP_ADDRESS = os.getenv("SMTP_ADDRESS")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TARGET_EMAIL = os.getenv("TARGET_EMAIL")

# -------------------------------------------------------
# 2. Define target URL and browser headers
# -------------------------------------------------------
URL = "https://www.amazon.com/dp/B075CYMYK6?ref_=cm_sw_r_cp_ud_ct_FM9M699VKHTT47YD50Q6&th=1"

browser_headers = {
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

# -------------------------------------------------------
# 3. Fetch the webpage with browser headers
# -------------------------------------------------------
response = requests.get(URL, headers=browser_headers)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

# -------------------------------------------------------
# 4. Hel»per function to extract and normalize price
# -------------------------------------------------------
def extract_price(text: str) -> float:
    """
    Extracts a price string from text and normalizes it into a float.
    Handles both EU (€, comma-decimal) and US ($, dot-decimal) formats.

    Examples:
        "$1,299.99"  → 1299.99
        "€59,99"     → 59.99
        "€1.299,99"  → 1299.99
    """
    pattern = r"[€£$]\s?\d{1,3}(?:[.,]\d{3})*[.,]\d{2}"  # Works for both US/EU formats
    match = re.search(pattern, text)

    if not match:
        raise ValueError(f"❌ No valid price found in: {text}")

    raw_price = match.group()
    print(f"Matched raw price text: {raw_price}")

    normalized = (
        raw_price.replace("€", "")
        .replace("$", "")
        .replace("£", "")
        .replace(" ", "")
    )

    # Handle both comma (EU) and dot (US) formats
    if "," in normalized and "." in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")
    else:
        normalized = normalized.replace(",", "")

    return float(normalized)

# -------------------------------------------------------
# 5. Extract price from the Amazon page
# -------------------------------------------------------
price_tag = soup.find("span", class_="aok-offscreen")
if price_tag is None:
    raise ValueError("❌ Could not find price on the page.")

price_text = price_tag.get_text().strip()
print(f"Raw price text from page: {price_text}")

price = extract_price(price_text)
print(f"✅ Extracted numeric price: {price:.2f}")

# -------------------------------------------------------
# 6. Define target price and send alert if needed
# -------------------------------------------------------
TARGET_PRICE = 100.00


def send_email_alert(current_price: float):
    """Send an email alert if product price is below target."""
    subject = "Amazon Price Alert!"
    body = (
        f"The Instant Pot is now ${current_price:.2f} — below your target of ${TARGET_PRICE:.2f}!\n"
        f"Check it here: {URL}"
    )
    message = f"Subject:{subject}\n\n{body}"

    try:
        with smtplib.SMTP(SMTP_ADDRESS, port=587) as connection:
            connection.starttls()  # Secure the connection
            connection.login(user=EMAIL_ADDRESS, password=EMAIL_PASSWORD)
            connection.sendmail(
                from_addr=EMAIL_ADDRESS,
                to_addrs=TARGET_EMAIL,
                msg=message.encode("utf-8")  # Prevent Unicode encoding errors
            )
        print("✅ Email sent successfully!")
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed: Check your app password in .env")
    except Exception as e:
        print(f"⚠️ Error sending email: {e}")

# -------------------------------------------------------
# 7. Compare and trigger email if price is below target
# -------------------------------------------------------
if price < TARGET_PRICE:
    send_email_alert(price)
else:
    print("No alert — price is above target.")
