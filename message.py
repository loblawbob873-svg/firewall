import logging
from config import SKIP_ALERTS
from config import NTFY_URL
from ntfy import send_to_ntfy

# Set up logging
logging.basicConfig(
    filename="firewall.log", level=logging.INFO, format="%(asctime)s - %(message)s"
)

def check_message(message):
    Proceed = True
    for word in SKIP_ALERTS:
        if word.lower() in message.lower():
            Proceed = False

    return Proceed

def send_message(message):
    if check_message(message):
        if NTFY_URL:
            send_to_ntfy(message)
        logging.info(message)