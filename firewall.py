import re
import time
import requests
import os
import subprocess
import logging
from collections import defaultdict
import argparse

# Configuration variables
LOG_FILE = "/tmp/access.log"
OCCURRENCE_THRESHOLD = 4
IP_OCCURRENCE_THRESHOLD = 50
#NTFY_URL=""
NTFY_URL = "https://push.poster.place/logs"
TIME_FRAME = 30 # 30 Seconds

#Basically Unlimited 
TIER_ONE = {
    "lalilulelo",
    "cherrypick",
    "husky",
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
    "/api/v1/akkoma/translation",
    "/api/v1/media",
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
}

#Additional Items to Exclude after TIER_ONE. BLOCKS IP's count that is larger than OCCURRENCE_THRESHOLD
TIER_TWO = [
    "fediverse-light",
    "videojs",
    "storyboards",
    "lists",
    "bookmarks.xbel.lock",
    "illegitimate",
    "_app",
]

BLOCK_ARRAY = [
    "/commits/commit/",
    "/blame/commit",
    "/src/commit/",
    "/raw/commit/",
    "/rss/commit",
    "/tree-view/commit/",
    "/tree-list/commit/",
    "/find/commit/",
    "amethyst",
    "47.82.",
    "47.79.",
    "43.74.",
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
    "freshrss",
    "yandexwebmaster",
    "linkedinbot",
    "headlesschrome",
    "t3versionsbot",
    "claudeBot",
    "qwant",
    "msnbot",
    "trident",
    "rss-is-dead.lol",
    "surdotlybot",
    "mj12bot",
    "yandexfavicon",
    "adsbot-google",
    "gptbot"
]


LOCAL_NETWORK = [
    "192.168.0",
]

# SKIP NTFY Alerts if a word is on this list
SKIP_ALERTS = ["already", "searching", "allowed", "sleeping", "IP Address Counts"]

# Set up logging
logging.basicConfig(
    filename="firewall.log", level=logging.INFO, format="%(asctime)s - %(message)s"
)

# Data structures to store IP addresses and their request counts
ip_requests = defaultdict(int)


def send_to_ntfy(message):
    time.sleep(10)
    try:

        if message in BLOCK_ARRAY:
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

    # Print the entire response for debugging purposes
    print(f"Response: {response.text}")


def check_message(message):
    Proceed = True
    for word in SKIP_ALERTS:
        if word.lower() in message.lower():
            Proceed = False

    return Proceed


def messaging(message):
    if check_message(message):
        logging.info(f"{message}")
        print(f"{message}")
        if NTFY_URL:
            send_to_ntfy(message)


def block_ip(ip):
    nft_output = subprocess.check_output("nft list ruleset", shell=True).decode()
    if ip not in nft_output:
        command = (
            f"/usr/sbin/nft insert rule ip filter input position 0 ip saddr {ip} drop"
        )
        os.system(command)

def main():
    parser = argparse.ArgumentParser(description="Firewall Script")
    parser.add_argument("--print", action="store_true", help="Print IP address counts")
    args = parser.parse_args()
    ip_counts = {}  # Dictionary to store IP addresses and their occurrence counts

    while True:
        # Get the current time and the time one minute ago
        now = time.strftime("%d/%b/%Y:%H:%M:%S", time.localtime(time.time()))
        one_minute_ago = time.strftime(
            "%d/%b/%Y:%H:%M", time.localtime(time.time() - TIME_FRAME)
        )

        messaging(f"Searching logs for Time Stamp: {one_minute_ago}")
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

                            # Block IP's over the IP_OCCURRENCE_THRESHOLD
                            if ip_counts[ip_address] > IP_OCCURRENCE_THRESHOLD:
                                block_ip(ip_address)

                            # Excludes TIER_TWO
                            if not any(
                                item.lower() in line.lower() for item in TIER_TWO
                            ):
                                # BLOCK_ARRAY
                                if any(
                                    word.lower() in line.lower() for word in BLOCK_ARRAY
                                ):
                                    if ip_counts[ip_address] > OCCURRENCE_THRESHOLD:
                                        messaging(f"Blocked: {line.strip()}, IP: {line.lower()}")
                                        block_ip(ip_address)
                                else:
                                    messaging(f"Allowed:  {line.strip()}, IP: {ip_address}")

                    if args.print:
                        messaging("\n\n\n[IP Address Counts]\n")
                        for ip, count in ip_counts.items():
                            print(f"{ip}: {count}")

        messaging(f"Firewall sleeping for: {TIME_FRAME}")
        time.sleep(
            TIME_FRAME
        )  # Wait for the specified time frame before processing again


if __name__ == "__main__":
    main()
