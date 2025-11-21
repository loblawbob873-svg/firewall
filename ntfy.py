
import requests
import time
from config import NTFY_URL
from config import SKIP_ALERTS

def send_to_ntfy(message):
    time.sleep(10)
    try:
        response = requests.post(
            NTFY_URL,
            data=message.encode("utf-8"),
            timeout=5,  # Add a timeout to prevent the function from hanging indefinitely
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx, 5xx)
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Something went wrong: {err}")
