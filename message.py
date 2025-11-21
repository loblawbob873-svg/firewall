from ntfy import send_to_ntfy
from ntfy import NTFY_URL

def send_message(message):
    if check_message(message):
        if NTFY_URL:
            send_to_ntfy(message)