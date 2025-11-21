from config import SKIP_ALERTS
from config import NTFY_URL
from ntfy import send_to_ntfy

def check_message(message):
    Proceed = True
    for word in SKIP_ALERTS:
        if word in message:
            print  (f"Debug: {word} {message}")
            Proceed = False

    return Proceed

def send_message(message):
    if check_message(message):
        if NTFY_URL:
            send_to_ntfy(message)
        else:
            print("Not sending to NTFY")
    print(message)