"""
Called by setup_cron.sh and remove_cron.sh to send a one-off status email.
Usage: python send_notification.py <setup|remove>
"""
import sys
import os
import smtplib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from config import PRODUCT_NAME, PRODUCT_URL, TARGET_PRICE, SMTP_PORT
from scraper import AmazonScraper

SMTP_ADDRESS = os.getenv("SMTP_ADDRESS")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TARGET_EMAIL = os.getenv("TARGET_EMAIL")

action = sys.argv[1] if len(sys.argv) > 1 else "setup"

# Fetch current price
try:
    current_price = AmazonScraper().get_price()
    price_status = "BELOW target — alert would fire today!" if current_price < TARGET_PRICE else "above target — no alert today."
    price_line = f"Current price: {current_price:.2f} EUR ({price_status})\n"
except Exception as exc:
    price_line = f"Current price: could not fetch ({exc})\n"

if action == "setup":
    subject = "Amazon Price Tracker — Daily Check Activated"
    body = (
        "Your Amazon price tracker is now running automatically.\n\n"
        f"Product : {PRODUCT_NAME}\n"
        f"Link    : {PRODUCT_URL}\n"
        f"Target  : {TARGET_PRICE:.2f} EUR\n"
        f"{price_line}"
        f"Schedule: every day at 08:00\n\n"
        "You will receive an alert if the price drops below your target.\n"
        "To manage the schedule, open menu.py and use options 4 or 5."
    )
elif action == "remove":
    subject = "Amazon Price Tracker — Daily Check Deactivated"
    body = (
        "Your Amazon price tracker cron job has been removed.\n\n"
        f"Product : {PRODUCT_NAME}\n"
        f"Link    : {PRODUCT_URL}\n"
        f"Target  : {TARGET_PRICE:.2f} EUR\n"
        f"{price_line}\n"
        "The script will no longer run automatically.\n"
        "To re-enable it, open menu.py and select option 3."
    )
else:
    print(f"Unknown action: {action}")
    sys.exit(1)

message = f"Subject:{subject}\n\n{body}"

try:
    with smtplib.SMTP(SMTP_ADDRESS, port=SMTP_PORT) as connection:
        connection.starttls()
        connection.login(user=EMAIL_ADDRESS, password=EMAIL_PASSWORD)
        connection.sendmail(
            from_addr=EMAIL_ADDRESS,
            to_addrs=TARGET_EMAIL,
            msg=message.encode("utf-8"),
        )
    print(f"Confirmation email sent to {TARGET_EMAIL}.")
except Exception as exc:
    print(f"Could not send confirmation email: {exc}")
