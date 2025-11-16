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
OCCURRENCE_THRESHOLD = 5
IP_OCCURRENCE_THRESHOLD = 30
NTFY_URL = "https://push.poster.place/logs"
TIME_FRAME = 30  # 30 Seconds

FEDIVERSE_TRAFFIC = {
    "husky",
    "mastodon",
    "misskey",
    "akkoma",
    "pleroma",
    "soapbox",
    "ShitPissCum",
    "poa.st",
    "poast",
    "WhatsApp",
    "Friendica",
    "Fedilab",
    "incestoma",
    "sharkey",
    "calkey",
    "rebased",
}

BLOCK_ARRAY = {
    "GET / HTTP",
    '"-" "-"',
    "/commits/commit/",
    "/blame/commit",
    "/src/commit/",
    "/raw/commit/",
    "/rss/commit",
    "/tree-view/commit/",
    "/tree-list/commit/",
    "/find/commit/",
    "Amethyst",
    "47.82.",
    "47.79.",
    "43.74.",
    "nostr",
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
    "SerendeputyBot",
    "Arquivo-web-crawler",
    "Expanse",
    "x22Xpanse-bot",
    "KixxActivityPubCrawler",
    "Gabanzabot",
    "hstspreload-bot",
    "YisouSpider",
    "gotosocial",
    "FAST-WebCrawler",
    "Facebot",
    "MisskeyBot",
    "search-engine-indexer",
    "PixelFedBot",
    "lemmy-stats-crawler",
    "Crawler",
    "SemrushBot",
    "bingbot",
    "CyberFindCrawler",
    "AportCatalogRobot",
    "LivelapBot",
    "duckduckbot",
    "YandexBot",
    "intelx.io_bot",
    "FediIndex",
    "Sogou",
    "YandexImageResizer",
    "Slack-ImgProxy",
    "ISSCyberRiskCrawler",
    "YandexRenderResourcesBot",
    "FriendlyCrawler",
    "MbinBot",
    "YandexImages",
    "Exabot",
    "SemanticScholarBot",
    "Twitterbot",
    "SeznamBot",
    "oii-research",
    "Horrid",
    "Ai2Bot-Dolma",
    "ZoominfoBot",
    "CCBot",
    "serpstatbot",
    "YandexUserproxy",
    "SeoCherryBot",
    "Amazonbot",
    "DotBot",
    "VirusTotalBot",
    "AwarioBot",
    "ws-bot-v1",
    "AhrefsBot",
    "ldspider",
    "Googlebot-Image",
    "ImagesiftBot",
    "Bytespider",
    "BW/1.2",
    "AwarioSmartBot",
    "vmcrawl",
    "GenomeCrawlerd",
    "Chodes",
    "Barkrowler",
    "ev-crawler",
    "CDSCbot",
    "PerplexityBot",
    "BitSightBot",
    "DataForSeoBot",
    "baidu",
    "RedekenBot",
    "coccocbot-web",
    "GNUsocialBot",
    "PagePeeker",
    "bots.retroverse.social",
    "CensysInspect",
    "BLEXBot",
    "Googlebot",
    "archive.org_bot",
    "majestic",
    "applebot",
    "Mail.RU_Bot",
    "KOCMOHABT",
    "openai",
    "Discordbot",
    "lemmy",
    "TurnitinBot",
    "BacklinksExtendedBot",
    "meta-externalagent",
    "ahrefsbot",
    "PetalBot",
    "kbinBot",
    "robots.txt",
    "IonCrawl",
    "SiteCheckerBotCrawler",
    "yacybot",
    "FreshRSS",
    "YandexWebmaster",
    "LinkedInBot",
    "HeadlessChrome",
    "t3versionsBot",
    "ClaudeBot",
    "Qwant",
    "msnbot",
    "Trident",
    "rss-is-dead.lol",
    "SurdotlyBot",
    "MJ12bot",
    "YandexFavicon",
    "AdsBot-Google",
    "GPTBot",
    "CyberFind",
}

LOCAL_NETWORK = [
    "192.168.0",
]

SKIPPED_TERMS = [
    "/manifest.json",
    "/socket/websocket",
    "CherryPick",
    "/api/v1",
    "/search",
    "POST",
    "/inbox",
    "/api/v2",
    "/relay",
    "/objects",
    "/media",
    "emoji",
    "assets",
    "favicon",
    "avatar",
    "inbox",
    "kuma",
    "users",
    "webfinger",
    "static",
    "logo",
    ".web",
    ".html",
    "friends",
    "notice",
    "host-meta",
    "nodeinfo",
    "fetch",
    "css",
    "notifications",
    "fediverse-light",
    "AodeRelay",
    "sw-pleroma.js",
    "wolfgirl.bar",
    "socks.cafe",
    "videojs",
    "ActivityRelay",
    "GuzzleHttp",
    "FoundKey",
    "comments",
    "fonts",
    "storyboards",
    "lists",
    "bookmarks.xbel.lock",
    "node_modules",
    "polls",
    "embed",
    "latest_version",
    "watch?",
    "shitposter",
    "danksquad",
    "illegitimate",
    "majestic12",
    "nicecrew",
    "Mitra",
    "Misskey",
    "Lalilulelo",
    "frontend_settings",
    "announcements",
    "Husky",
    ".js",
    "feed/popular",
    "apple-touch",
    "ANNIHILATION",
    ".png",
    ".jpg",
    "packs",
    "shitposter.world",
    "matrix",
    "_app",
]

# SKIP NTFY Alerts if a word is on this list
SKIP_ALERTS = ["already", "searching", "allowed", "sleeping"]

# Set up logging
logging.basicConfig(
    filename="firewall.log", level=logging.INFO, format="%(asctime)s - %(message)s"
)

# Data structures to store IP addresses and their request counts
ip_requests = defaultdict(int)


def send_to_ntfy(message):
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

    if response.status_code == 200:
        print(f"🌈 Successfully sent message: {message} 🌈")
    else:
        print(
            f"❌ Failed to send message. Status code: {response.status_code}. Error: {response.text} ❌"
        )

    # Print the entire response for debugging purposes
    print(f"Response: {response.text}")


def messaging(message):
    logging.info(f"{message}")
    print(f"{message}")
    for word in SKIP_ALERTS:
        print(f"Looking for {word} in {message}")
        if word.lower() in message.lower():
            logging.info("✨ Oh my gosh! The string has '{word}' in it! ✨")
        else: 
           send_to_ntfy(message)

def block_ip(ip):
    nft_output = subprocess.check_output("nft list ruleset", shell=True).decode()
    if ip not in nft_output:
        command = (
            f"/usr/sbin/nft insert rule ip filter input position 0 ip saddr {ip} drop"
        )
        os.system(command)
        messaging(f"IP address {ip} blocked")
    else:
        messaging(f"IP address {ip} already in the ruleset.")


def main():
    parser = argparse.ArgumentParser(description="Firewall Script")
    parser.add_argument("--print", action="store_true", help="Print IP address counts")
    parser.add_argument("--blocked", action="store_true", help="Shows what is blocked")
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
                # Excludes Fediverse Traffic
                if one_minute_ago.lower() in line.lower() and not any(
                    term.lower() in line.lower() for term in FEDIVERSE_TRAFFIC
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

                            # Excludes SKIPPED_TERMS
                            if not any(
                                item.lower() in line.lower() for item in SKIPPED_TERMS
                            ):
                                # BLOCK BLOCK_ARRAY
                                if any(
                                    word.lower() in line.lower() for word in BLOCK_ARRAY
                                ):
                                    if ip_counts[ip_address] > OCCURRENCE_THRESHOLD:
                                        if args.blocked:
                                            messaging(
                                                f"Blocked: {line.strip()}, IP: {line.lower()}"
                                            )
                                        block_ip(ip_address)
                                else:
                                    if not args.print:
                                        messaging(
                                            f"Allowed:  {line.strip()}, IP: {ip_address}"
                                        )

                    if args.print:
                        messaging("\n\n\n[IP Address Counts]\n")
                        for ip, count in ip_counts.items():
                            messaging(f"{ip}: {count}")

        messaging(f"Firewall sleeping for: {TIME_FRAME}")
        time.sleep(
            TIME_FRAME
        )  # Wait for the specified time frame before processing again


if __name__ == "__main__":
    main()
