import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from config import TARGET_PRICE
from scraper import AmazonScraper
from notifier import EmailNotifier

SMTP_ADDRESS = os.getenv("SMTP_ADDRESS")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TARGET_EMAIL = os.getenv("TARGET_EMAIL")

scraper = AmazonScraper()
notifier = EmailNotifier(
    smtp_address=SMTP_ADDRESS,
    sender=EMAIL_ADDRESS,
    password=EMAIL_PASSWORD,
    recipient=TARGET_EMAIL,
)

try:
    price = scraper.get_price()
    print(f"Current price: ${price:.2f}")

    if price < TARGET_PRICE:
        print(f"Price is below target (${TARGET_PRICE:.2f}). Sending alert...")
        notifier.send_alert(price)
        print("Alert sent successfully.")
    else:
        print(f"No alert — price (${price:.2f}) is above target (${TARGET_PRICE:.2f}).")

except ValueError as exc:
    print(f"Price extraction error: {exc}")
except RuntimeError as exc:
    print(f"Notification error: {exc}")
except Exception as exc:
    print(f"Unexpected error: {exc}")
