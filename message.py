from ntfy import send_to_ntfy

def messaging(message):
    if check_message(message):
        if NTFY_URL:
            send_to_ntfy(message)