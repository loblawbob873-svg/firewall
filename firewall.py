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
OCCURRENCE_THRESHOLD = 50
NTFY_URL = "https://push.poster.place/firewall"
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

SKIPPED_TERMS = [
    "/manifest.json",
    "/socket/websocket",
    "CherryPick",
    "/api/v1",
    "/search",
    "192.168.0",
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

# Set up logging
logging.basicConfig(
    filename="firewall.log", level=logging.INFO, format="%(asctime)s - %(message)s"
)

# Data structures to store IP addresses and their request counts
ip_requests = defaultdict(int)


def messaging(message):
    logging.info(f"{message}")
    print(f"{message}")


def block_ip(ip):
    nft_output = subprocess.check_output("nft list ruleset", shell=True).decode()
    if ip not in nft_output:
        command = (
            f"/usr/sbin/nft insert rule ip filter input position 0 ip saddr {ip} drop"
        )
        os.system(command)
        send_notification(f"IP address {ip} blocked")
        messaging(f"IP address {ip} blocked")
    else:
        messaging(f"IP address {ip} already in the ruleset.")


def send_notification(message):
    requests.post(NTFY_URL, data=message.encode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Firewall Script")
    parser.add_argument("--print", action="store_true", help="Print IP address counts")
    args = parser.parse_args()
    ip_counts = {}  # Dictionary to store IP addresses and their occurrence counts
    log_array = {}
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
                        ip_address = ip_match.group()
                        ip_counts[ip_address] = ip_counts.get(ip_address, 0) + 1

                        # Excludes Fediverse Traffic and SKIPPED_TERMS
                        if any in BLOCK_ARRAY and not any in SKIPPED_TERMS:
                            if ip_counts[ip_address] > OCCURRENCE_THRESHOLD:
                                block_ip(ip_address)
                            if not args.print:
                                messaging(f"Allowed:  {line.strip()}, IP: {ip_address}")
                                # Check if the IP address has exceeded the threshold and block it if necessary

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
