import re
import time
import requests
import os
import subprocess
import logging
from collections import defaultdict
import argparse
import psutil
import re
import httpx
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json

# Configuration variables
LOG_FILE = "/tmp/access.log"
IP_OCCURRENCE_THRESHOLD = 50

# NTFY_URL=""
NTFY_URL = "https://push.poster.place/logs"
TIME_FRAME = 30  # 30 Seconds

# Web Inferface HTML File
WEB_HTML = "/tmp/python-firewall.html"

# Where to save the firewall rules
NFT_SAVED_RULES = "/etc/firewall.nft"

# Get the current time and the time one minute ago
ip_counts = {}  # Dictionary to store IP addresses and their occurrence counts
activity = []

# Open AI Integration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
MODEL = "mistral-nemo:latest"

# Basically Unlimited/ Comment out a line if you want to
# block if it's accessed greater than IP_OCCURRENCE_THRESHOLD
TIER_ONE = {
    "mumble",
    "/status",
    "/extension.php",
    "/logs",
    "/drc/",
    "lalilulelo",
    "cherrypick",
    "husky",
    "tusky",
    "whatsapp",
    "fedilab",
    ".js",
    ".png",
    ".jpg",
    ".css",
    ".json",
    ".html",
    ".web",
    "/activities",
    "/emoji",
    "/images",
    "/friends",
    "/notice",
    "/nodeinfo",
    "/outbox",
    "/following",
    "/followers",
    "/api/v1/notifications",
    "/api/v1/timelines",
    "/api/v1/statuses",
    "/api/v1/polls/",
    "/api/v1/tools",
    "/api/v1/directory",
    "/api/v1/streaming",
    "/api/v1/profile",
    "/api/v1/auths",
    "/api/v1/configs",
    "/api/v1/pleroma/admin",
    "/api/v1/functions",
    "/api/v1/announcements",
    "/api/v1/timelines/public",
    "/api/v1/timelines/home",
    "/api/v1/timelines/tag",
    "/api/v1/pleroma/statuses",
    "/api/v1/pleroma/chats",
    "/api/v1/pleroma/emoji",
    "/api/v1/instance",
    "/api/v1/users/user/settings",
    "/api/v1/accounts",
    "/api/v1/lists",
    "/api/v1/mutes",
    "/api/v1/akkoma/frontend_settings",
    "/api/pleroma/frontend_configurations",
    "/api/v1/akkoma/translation",
    "/api/v1/media",
    "/tag/",
    "/internal/fetch",
    "/contexts/",
    "/search",
    "/inbox",
    "/api/v2",
    "/relay",
    "/objects",
    "/media",
    "/users",
    "/static",
    "/assets",
    "/favicon",
    "/avatar",
    "uptime-kuma",
    "/logo",
    "/main",
    "/.well-known",
    "/manifest.json",
    "/apple-touch",
    "/fonts",
    "/_matrix",
    "/socket",
    "/signin",
    "/files",
    "/graph",
    "/api/v0",
    "/ocs",
    "/app",
    "/app/list",
    "/remote.php",
    "/remote.php/webdav",
    "/status.php",
    "/themes",
    "/web",
    "/Branding",
    "/ws",
    "/web-oidc",
    "/oidc",
    "/status.php",
    "/konnect",
    "/icons",
    "/api/v0/settings",
    "/ocs/v2.php/cloud/user",
    "/ocs/v2.php/apps/notifications/",
    "/api/v1/notifications",
    "/api/v1/pleroma/notifications/read",
    "/ocs/v2.php/cloud/capabilities",
    "/web-oidc-callback",
    "/dav/spaces",
    "/api/v0/settings/assignments-list",
}

IP_BLOCKS = [
    "/source.zip",
    "/backup.zip",
    "/config/db.sql",
    "/sql/db.sq",
    "\\x00\\x00",
    "/issues?assignee",
    "/.git/config",
    "wp-content",
    "wp-includes",
    "deno",
    "Deno/",
    "/commits/",
    "/commits/commit/",
    "/blame/commit",
    "/src/commit/",
    "/raw/commit/",
    "/rss/commit",
    "/tree-view/commit/",
    "/tree-list/commit/",
    "/find/commit/",
    "amethyst",
    "nostr",
    "nostter.app",
    "170.33.24",
    "98.11.128.",
    "203.107.",
    "205.205.",
    "223.5.5.",
    "223.6.6.",
    "156.245.",
    "170.33.80.",
    "187.198.252",
    "habla.news",
    ".php",
    ".env",
    "impendoom-bot",
    "msnbot-media",
    "serendeputybot",
    "arquivo-web-crawler",
    "expanse",
    "x22xpanse-bot",
    "kixxactivitypubcrawler",
    "gabanzabot",
    "hstspreload-bot",
    "yisouspider",
    "gotosocial",
    "fast-webcrawler",
    "facebot",
    "misskeybot",
    "search-engine-indexer",
    "pixelfedbot",
    "lemmystats-crawler",
    "crawler",
    "semrushbot",
    "bingbot",
    "cyberfindcrawler",
    "aportcatalogrobot",
    "livelapbot",
    "duckduckbot",
    "yandexbot",
    "intelx.io_bot",
    "fediiindex",
    "sogou",
    "yandeximageresizer",
    "slack-imgproxy",
    "isscyberriskcrawler",
    "yandexrenderresourcesbot",
    "friendlycrawler",
    "mbinbot",
    "yandeximages",
    "exabot",
    "semanticscholarbot",
    "twitterbot",
    "seznambot",
    "oii-research",
    "horrid",
    "ai2bot-dolma",
    "zoominfobot",
    "ccbot",
    "serpstatbot",
    "yandexuserproxy",
    "seocherrybot",
    "amazonbot",
    "dotbot",
    "virustotalbot",
    "awariobot",
    "ws-bot-v1",
    "ahrefsbot",
    "ldspider",
    "googlebot-image",
    "imagesiftbot",
    "bytespider",
    "bw/1.2",
    "awariosmartbot",
    "vmcrawl",
    "genomecrawlerd",
    "chodes",
    "barkrowler",
    "ev-crawler",
    "cdscbot",
    "perplexitybot",
    "bitsightbot",
    "dataforseobot",
    "baidu",
    "redekenbot",
    "coccocbot-web",
    "gnusocialbot",
    "pagepeeker",
    "bots.retroverse.social",
    "censysinspect",
    "blexbot",
    "googlebot",
    "archive.org_bot",
    "majestic",
    "applebot",
    "mail.ru_bot",
    "kocmohabt",
    "openai",
    "discordbot",
    "lemmy",
    "turnitinbot",
    "backlinksextendedbot",
    "meta-externalagent",
    "ahrefsbot",
    "petalbot",
    "kbinbot",
    "robots.txt",
    "ioncrawl",
    "sitecheckerbottcrawler",
    "yacybot",
    "yandexwebmaster",
    "linkedinbot",
    "headlesschrome",
    "t3versionsbot",
    "claudeBot",
    "qwant",
    "msnbot",
    "trident",
    "primal-android",
    "rss-is-dead.lol",
    "surdotlybot",
    "mj12bot",
    "yandexfavicon",
    "adsbot-google",
    "gptbot",
    "damus",
]

SUBNET_BLOCKS = [
    "rottenwheel",
    "47.82.",
    "47.79.",
    "43.74.",
]
LOCAL_NETWORK = ["192.168.0", "47.5.68.214", "192.168.5", "107.175.34.92"]

# SKIP NTFY Alerts if a word is on this list
SKIP_ALERTS = [
    "already",
    "searching",
    "sleeping",
    "IP Address Counts",
    "Amethyst",
    "rottenwheel",
    "/commit",
    "bot",
]

# ------------------------------------------------------------------
# FastAPI app
# ------------------------------------------------------------------
app = FastAPI(
    title="Python Firewall",
    description="DDOS Protection",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def main():
    DATA = ""
    with open(f"{WEB_HTML}", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)


async def get_html():
    with open(f"{WEB_HTML}", "r") as f:
        return f.read()


# Set up logging
logging.basicConfig(
    filename="firewall.log", level=logging.INFO, format="%(asctime)s - %(message)s"
)


# Set up logging
logging.basicConfig(
    filename="firewall.log", level=logging.INFO, format="%(asctime)s - %(message)s"
)

@app.get("/ai")
async def main(ip: str):
    openai_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }

    messages = []
    messages.append(
        {"role": "user", "web_search": True, "content": f"Tell me information about this IP address such as the owner, abuse details, and location: {ip}. Find as much information as y ou can."}
    )

    payload = {"model": MODEL, "messages": messages}
    if(OPENAI_API_KEY):
        try:
            r = requests.post(
                OPENAI_ENDPOINT,
                headers=openai_headers,
                data=json.dumps(payload),
                timeout=500,
            )
            result = r.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e: return(e)

# Data structures to store IP addresses and their request counts
ip_requests = defaultdict(int)


def get_cpu_usage():
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent < 50:
        final = f"💻 CPU usage: {cpu_percent}% 😀"
    else:
        final = f"💻 CPU usage: {cpu_percent}% 😡"
    return f"{final}"


def send_to_ntfy(message):
    time.sleep(10)
    try:

        if message in SKIP_ALERTS:
            logging.info(f"Skipping NTFY Message")
        else:
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


def check_message(message):
    Proceed = True
    for word in SKIP_ALERTS:
        if word.lower() in message.lower():
            Proceed = False

    return Proceed


def messaging(message):
    if check_message(message):
        if NTFY_URL:
            send_to_ntfy(message)


def extract_first_three_parts(ip):
    return ".".join(ip.split(".")[:3])


def save_nft_rules():
    command = f"/usr/sbin/nft list ruleset > {NFT_SAVED_RULES}"
    subprocess.check_output(command, shell=True, text=True)


def get_block_count():
    command = f"/usr/sbin/nft list ruleset | grep -i drop | wc -l"
    data = subprocess.check_output(command, shell=True, text=True)
    return data


def block_ip(ip, message):
    nft_output = subprocess.check_output("nft list ruleset", shell=True).decode()
    if ip not in nft_output:
        command = (
            f"/usr/sbin/nft insert rule ip filter input position 0 ip saddr {ip} drop"
        )
        os.system(command)
        messaging(f"{message}")


def main():
    parser = argparse.ArgumentParser(description="Firewall Script")
    parser.add_argument("--print", action="store_true", help="Print IP address counts")
    args = parser.parse_args()

    while True:
        # Get the current time and the time one minute ago
        ip_counts = {}  # Dictionary to store IP addresses and their occurrence counts
        activity = []
        now = time.strftime("%d/%b/%Y:%H:%M:%S", time.localtime(time.time()))
        one_minute_ago = time.strftime(
            "%d/%b/%Y:%H:%M", time.localtime(time.time() - TIME_FRAME)
        )

        if args.print:
            activity.append(
            "-------------------------------------------------------------------------------------------------")
            activity.append("\t\t🔥 Python Firewall 🔥")  
            
        activity.append(
            f"{get_cpu_usage()}\tBlocked IP's: {get_block_count().strip()} ✅"
        )
        activity.append("-------------------------------------------------------------------------------------------------")
        activity.append(
            f"\t\t\t⚠️ Unfiltered and Blocked Traffic as of: {one_minute_ago}\n"
        )
        with open(LOG_FILE, "r") as f:
            for line in f:
                # Increment the occurrence count for the IP address
                # Excludes TIER_ONE Traffic
                if one_minute_ago.lower() in line.lower() and not any(
                    term.lower() in line.lower() for term in TIER_ONE
                ):
                    ip_match = re.search(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", line)
                    if ip_match:

                        # Don't Count the Local Network Against you
                        if not any(
                            lan.lower() in line.lower() for lan in LOCAL_NETWORK
                        ):
                            ip_address = ip_match.group()
                            ip_counts[ip_address] = ip_counts.get(ip_address, 0) + 1

                            try:
                                # Blocks anything in SUBNET_BLOCKS
                                if any(
                                    word.lower() in line.lower()
                                    for word in SUBNET_BLOCKS
                                ):

                                    BIG_IP = extract_first_three_parts(ip_address)
                                    message = f"\t🚨 Blocked Subnet: 👉 {ip_address} {line.lower().split(" ")[6]}\n"
                                    activity.append(message)
                                    block_ip(f"{BIG_IP}.0/24", message)

                                # Blocks anything in IP_BLOCKS
                                elif any(
                                    word.lower() in line.lower() for word in IP_BLOCKS
                                ):
                                    message = f"\t🚨 Blocked: {ip_address} 👉 {line.lower().split(" ")[6]}\n"
                                    activity.append(message)
                                    block_ip(ip_address, message)
                                else:
                                    # Prints any Web Traffic that does not fit into any of the filtering arrays above
                                    activity.append(
                                        f"\t🕵️ {ip_address} {line.lower().split(" ")[6]}\n"
                                    )
                            except requests.exceptions.RequestException as err:
                                print(f"Something went wrong: {err}")

        if args.print:
            activity.append(f"\nIP Address Count:\n")
        else:
            activity.append(f"<br><br>IP Address Count:<br>")
        
        # Block IP's over the IP_OCCURRENCE_THRESHOLD
        # TIER_ONE Traffic does not count    
        for ip, count in ip_counts.items():
            if count > 1:
                activity.append(f"\t📍 {ip}: {count}")
            if count > IP_OCCURRENCE_THRESHOLD:
                message = f"🚨 Blocked: {ip} with a count of {count}"
                activity.append(message)
                block_ip(ip, message)

        save_nft_rules()
        os.system("clear")

        with open(WEB_HTML, "w") as f:
            f.write("<html><head><style> body {  background-color: black; font-family: Arial, sans-serif; text-align: left; } #stats { font-size: 1em; margin-top: 50px; }</style></head>")
            f.write(
                "<script>\nwindow.setTimeout( function() {window.location.reload();}, 32000);</script>"
            )
            f.write("<body><h1><span style=\"color: red;\">🔥</span> Python Firewall Web Console 🔥</h1> <br> <br>")
            f.write("<div id=\"stats\">")
            
            for line in activity:
                GET_AI_IP = ""
                print(f"\n{line}")
                f.write("\n")
                if not args.print and "🚨" in line:
                    value = line.split(":")
                    URL_FIX = line.split(" ")
                    line = f"🚨 Blocked: <a style=\"text-decoration:none\" target=\"_blank\" href=\"https://{URL_FIX[3]}\">{URL_FIX[3]}</a>  {value[1]}"
                if not args.print and "📍" in line:
                    value = line.split(":")
                    URL_FIX = line.split(" ")
                    line = f"📍 <a style=\"text-decoration:none\" target=\"_blank\" href=\"https://{URL_FIX[1]}\">{URL_FIX[1]}</a>  {value[1]}"
                if not args.print and "🕵️" in line:
                    URL = line.split("🕵️")
                    URL_PARSE = line.split(" ")
                    URL_FIX = line.split(" ")
                    line = f"<a style=\"text-decoration:none\" target=\"_blank\" href=\"https://{URL_FIX[1]}\">🕵️ {URL_FIX[1]}</a> {URL_PARSE[2]} <a href=\"https://www.ip-tracker.org/lookup.php?ip={URL_PARSE[1]}\" style=\"text-decoration:none\" target=\"_blank\">  🔍 <a style=\"text-decoration:none\" href=\"https://who.is/whois-ip/ip-address/{URL_PARSE[1]}\" target=\"_blank\">🌐</a>"
                if "\t" in line:
                    line.replace("\t", "")
                if "\n" in line:
                    line.replace("\n", "<br>")          
                f.write(f"<br>{line}</br>")

        time.sleep(
            TIME_FRAME
        )  # Wait for the specified time frame before processing again


if __name__ == "__main__":
    main()
