from bs4 import BeautifulSoup
import requests
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

# ---------------- SETUP VARIABLES --------------#
# URL = "https://appbrewery.github.io/instant_pot/"  # static practice site
URL = "https://www.amazon.co.uk/gp/product/B0CYH6J19F/ref=ox_sc_saved_title_2?smid=A2L8MSOJVME1M6&psc=1"  # live site

PRICE_THRESHOLD = 80

SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
SMTP_ADDRESS = os.getenv('SMTP_ADDRESS')

recipient_email = os.getenv('RECIPIENT_EMAIL')

# --------------------- GET HEADERS ---------------------#
header = {
    "Accept": os.getenv('ACCEPT'),
    "Accept-Encoding": os.getenv('ACCEPT_ENCODING'),
    "Accept-Language": os.getenv('ACCEPT_LANGUAGE'),
    "Priority": os.getenv('PRIORITY'),
    "Sec-Ch-Ua": os.getenv('SEC_CH_UA'),
    "Sec-Ch-Ua-Mobile": os.getenv('SEC_CH_UA_MOBILE'),
    "Sec-Ch-Ua-Platform": os.getenv('SEC_CH_UA_PLATFORM'),
    "Sec-Fetch-Dest": os.getenv('SEC_FETCH_DEST'),
    "Sec-Fetch-Mode": os.getenv('SEC_FETCH_MODE'),
    "Sec-Fetch-Site": os.getenv('SEC_FETCH_SITE'),
    "Sec-Fetch-User": os.getenv('SEC_FETCH_USER'),
    "Upgrade-Insecure-Requests": os.getenv('UPGRADE_INSECURE_REQUESTS'),
    "User-Agent": os.getenv('USER_AGENT')
}

# --------------------- WEB SCRAPE ---------------------#
response = requests.get(url=URL, headers=header)
response.raise_for_status()
webpage = response.content

soup = BeautifulSoup(webpage, 'html.parser')

amazon_product_name = soup.select_one(selector='#productTitle')
product_name = " ".join(amazon_product_name.text.strip().split())
print(product_name)

amazon_price = soup.select_one(selector='.a-offscreen')
price = float(amazon_price.text.split("£")[-1])
print(price)


# --------------------- EMAIL SENDER ---------------------#
def send_email(sender, recipient, product):
    subject = f"Amazon price alert for {product_name[:20]}..."
    email_body = (f"{product_name}"
                  f"\n\nNow at: £{price}."
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
