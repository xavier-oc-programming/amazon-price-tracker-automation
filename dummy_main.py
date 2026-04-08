import requests
from bs4 import BeautifulSoup
import smtplib
from dotenv import load_dotenv
import os

# Step 1: Load environment variables
load_dotenv()
SMTP = os.getenv("SMTP_ADDRESS")
MY_EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")
TARGET_EMAIL = os.getenv("TARGET_EMAIL")

# Step 2: Scrape the test Amazon page
URL = "https://appbrewery.github.io/instant_pot/"
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

# Step 3: Locate and extract the price
price_tag = soup.find("span", class_="aok-offscreen")
price_text = price_tag.get_text().strip()
price = float(price_text.replace("$", ""))
print(f"Current product price: ${price}")

# Step 4: Set target price
TARGET_PRICE = 100.00

# Step 5: Function to send an email alert
def send_email_alert(current_price):
    subject = "Amazon Price Alert!"
    body = (
        f"The Instant Pot is now ${current_price} — below your target price of ${TARGET_PRICE}!\n"
        f"Check it here: {URL}"
    )
    message = f"Subject:{subject}\n\n{body}"

    with smtplib.SMTP(SMTP, port=587) as connection:
        connection.starttls()  # Secure the connection
        connection.login(user=MY_EMAIL, password=PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=MY_EMAIL,
            msg=message.encode('utf-8')   # ✅ FIX: Encode message to UTF-8
        )

    print("✅ Email sent successfully!")

# Step 6: Check condition and trigger email
if price < TARGET_PRICE:
    send_email_alert(price)
else:
    print("No alert — price is above target.")
