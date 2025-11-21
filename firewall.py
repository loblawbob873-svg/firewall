import re
import time
import os
import subprocess
import logging
from collections import defaultdict
import argparse
import psutil
import re
import httpx
import asyncio
import json
from ip_blocks import IP_BLOCKS
from tier_one import TIER_ONE
from html import basicHTML
from html import htmlRELOAD
from html import buildWeb
from ntfy import send_to_ntfy
from api import app
from commands import save_nft_rules
from cli import buildCLI
from config import LOG_FILE
from config import IP_OCCURRENCE_THRESHOLD
from config import TIME_FRAME
from config import SUBNET_BLOCKS
from config import LOCAL_NETWORK
from config import SKIP_ALERTS

ip_counts = {}  # Dictionary to store IP addresses and their occurrence counts
activity = []

# Set up logging
logging.basicConfig(
    filename="firewall.log", level=logging.INFO, format="%(asctime)s - %(message)s"
)


# Set up logging
logging.basicConfig(
    filename="firewall.log", level=logging.INFO, format="%(asctime)s - %(message)s"
)


# Data structures to store IP addresses and their request counts
ip_requests = defaultdict(int)

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


def main():
    parser = argparse.ArgumentParser(description="Firewall Script")
    parser.add_argument("--print", action="store_true", help="Print IP address counts")
    args = parser.parse_args()

    while True:
        # Get the current time and the time one minute ago
        ip_counts = {}  # Dictionary to store IP addresses and their occurrence counts
        activity = []
        now = time.strftime("%d/%b/%Y:%H:%M:%S", time.localtime(time.time()))
        timestamp = time.strftime(
            "%d/%b/%Y:%H:%M", time.localtime(time.time() - TIME_FRAME)
        )

        with open(LOG_FILE, "r") as f:
            for line in f:
                # Increment the occurrence count for the IP address
                # Excludes TIER_ONE Traffic
                if timestamp.lower() in line.lower() and not any(
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
                                    shorten = line.lower().split(" ")[6]
                                    shoroten_again = shorten[:30]
                                    BIG_IP = extract_first_three_parts(ip_address)
                                    message = f"\t🚨 Blocked Subnet: {ip_address} 👉 {shoroten_again}\n"
                                    activity.append(message)
                                    block_ip(f"{BIG_IP}.0/24", message)

                                # Blocks anything in IP_BLOCKS
                                elif any(
                                    word.lower() in line.lower() for word in IP_BLOCKS
                                ):
                                
                                    shorten = line.lower().split(" ")[6]
                                    shoroten_again = shorten[:30]
                                    message = f"\t🚨 Blocked IP: {ip_address} 👉 {shoroten_again}\n"
                                    activity.append(message)
                                    block_ip(ip_address, message)
                                else:
                                    # Prints any Web Traffic that does not fit into any of the filtering arrays above
                                    shorten = line.lower().split(" ")[6]
                                    shoroten_again = shorten[:30]
                                    activity.append(
                                         f"\t🕵️ {ip_address} {shoroten_again}\n"
                                    )
                            except Exception as err:
                                print(f"Something went wrong: {err}")

                activity.append(f"<br><br>IP Address Count:<br>")
                # Block IP's over the IP_OCCURRENCE_THRESHOLD
                # TIER_ONE Traffic does not count
                for ip, count in ip_counts.items():
                    activity.append(f"\t📍 {ip} {count}")
                    if count > IP_OCCURRENCE_THRESHOLD:
                        message = f"🚨 Blocked: {ip} with a count of {count}"
                        activity.append(message)
                        block_ip(ip, message)

            save_nft_rules()
            os.system("clear")

            if args.print:
                buildCLI(activity, timestamp)
            else: 
                buildWeb(activity,timestamp)

        time.sleep(
            TIME_FRAME
        )  # Wait for the specified time frame before processing again


if __name__ == "__main__":
    main()
