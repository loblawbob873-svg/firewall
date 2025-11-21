import requests
import json
import os

# Open AI Integration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
MODEL = "mistral-nemo:latest"

openai_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
}

def generate_reply(ip):
    messages = [
        {
            "role": "user",
            "web_search": True,
            "content": f"Tell me information about this IP address such as the owner, abuse details, and location: {ip}. Find as much information as y ou can.",
        }
     ]

    payload = {"model": MODEL, "messages": messages}
    if OPENAI_API_KEY:
        try:
            r = requests.post(
                OPENAI_ENDPOINT,
                headers=openai_headers,
                data=json.dumps(payload),
                timeout=500,
            )
            result = r.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return e
    