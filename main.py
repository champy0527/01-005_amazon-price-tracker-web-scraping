from bs4 import BeautifulSoup
import requests
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

# ---------------- SETUP VARIABLES --------------#
URL = "https://appbrewery.github.io/instant_pot/"
PRICE_THRESHOLD = 100

SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
SMTP_ADDRESS = os.getenv('SMTP_ADDRESS')

recipient_email = os.getenv('RECIPIENT_EMAIL')


# --------------------- WEB SCRAPE ---------------------#
response = requests.get(URL)
response.raise_for_status()
webpage = response.text

soup = BeautifulSoup(webpage, 'html.parser')

amazon_product_name = soup.select_one(selector='#productTitle')
product_name = " ".join(amazon_product_name.text.strip().split())
print(product_name)

amazon_price = soup.select_one(selector='.a-offscreen')
price = float(amazon_price.text.split("$")[-1])
print(price)


# --------------------- EMAIL SENDER ---------------------#
def send_email(sender, recipient, product):
    subject = f"Amazon price alert for {product_name[:20]}..."
    email_body = (f"{product_name}"
                  f"\n\nNow at: ${price}."
                  f"\n\nBuy now: {URL}")

    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = recipient_email
    message["Subject"] = subject

    message.attach(MIMEText(email_body, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_ADDRESS) as connection:
        connection.starttls()
        connection.login(user=SENDER_EMAIL, password=SENDER_PASSWORD)
        connection.sendmail(
            from_addr=SENDER_EMAIL,
            to_addrs=recipient_email,
            msg=message.as_string()
        )


# ------------------------ PRICE CHECK ------------------------#
if price < PRICE_THRESHOLD:
    send_email(SENDER_EMAIL, recipient_email, product_name)
