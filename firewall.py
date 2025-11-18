import re
import time
import requests
import os
import subprocess
import logging
from collections import defaultdict
import argparse
import psutil

# Configuration variables
LOG_FILE = "/tmp/access.log"
IP_OCCURRENCE_THRESHOLD = 50
# NTFY_URL=""
NTFY_URL = "https://push.poster.place/logs"
TIME_FRAME = 30  # 30 Seconds

# Basically Unlimited
TIER_ONE = {
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
    "/ocs/v2.php/cloud/capabilities",
    "/web-oidc-callback",
    "/dav/spaces",
    "/api/v0/settings/assignments-list",
}

IP_BLOCKS = [
    "/issues?assignee" "/.git/config",
    "wp-content",
    "deno",
    "Deno/",
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

# Set up logging
logging.basicConfig(
    filename="firewall.log", level=logging.INFO, format="%(asctime)s - %(message)s"
)

# Data structures to store IP addresses and their request counts
ip_requests = defaultdict(int)

def get_cpu_usage():
    cpu_percent = psutil.cpu_percent(interval=1)
    return f"💻 The current CPU usage is {cpu_percent}%! 🌡️"

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
        logging.info(f"{message}")
        print(f"{message}")
        if NTFY_URL:
            send_to_ntfy(message)


def extract_first_three_parts(ip):
    return ".".join(ip.split(".")[:3])


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

        messaging(f"Searching logs for Time Stamp: {one_minute_ago}")
        activity.append("---------------------------------------------")
        activity.append("🔥 Python Firewall 🔥")
        activity.append(f"{get_cpu_usage()} 📋 Blocked IP's: {get_block_count()}")
        activity.append("----------------------------------------------")
        activity.append(f"⚠️ Unfiltered Traffic as of: {one_minute_ago}\n")
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

                            # Blocks anything in SUBNET_BLOCKS
                            if any(
                                word.lower() in line.lower() for word in SUBNET_BLOCKS
                            ):
                                BIG_IP = extract_first_three_parts(ip_address)
                                message = f"🚨 Blocked Subnet: 👉 {line.lower()}🔪🩸💀"
                                activity.append(message)
                                block_ip(f"{BIG_IP}.0/24", message)

                            # Blocks anything in IP_BLOCKS
                            elif any(
                                word.lower() in line.lower() for word in IP_BLOCKS
                            ):
                                message = f"🚨 Blocked: 👉 {line.lower()}🔪🩸💀"
                                activity.append(message)
                                block_ip(ip_address, message)
                            else:
                                # Prints any Web Traffic that does not fit into any of the filtering arrays above
                                activity.append(f"🔎 {line.lower()}")

        # Block IP's over the IP_OCCURRENCE_THRESHOLD
        # TIER_ONE Traffic does not count
        activity.append(f"IP Address Count:\n")

        for ip, count in ip_counts.items():
            if count > 1:
                activity.append(f"📍 {ip}: {count}")
            if count > IP_OCCURRENCE_THRESHOLD:
                message = f"🚨 Blocked: {ip} with a count of {count}"
                activity.append(message)
                block_ip(ip, message)
        
        os.system('clear')  
        for line in activity:
            print(f"\n{line}")
            
        messaging(f"Firewall sleeping for: {TIME_FRAME}")

        time.sleep(
            TIME_FRAME
        )  # Wait for the specified time frame before processing again


if __name__ == "__main__":
    main()
