import json
import time
import re
from config import LOG_FILE
from config import IP_OCCURRENCE_THRESHOLD
from db import activity
from db import addActivity
from db import ip_counts
from commands import block_ip
from tier_one import TIER_ONE
from ip_blocks import IP_BLOCKS
from config import SUBNET_BLOCKS
from config import LOCAL_NETWORK


def extract_first_three_parts(ip):
    return ".".join(ip.split(".")[:3])

def process_log(timestamp):
    
    with open(LOG_FILE, "r") as f:
        for line in f:
            # Increment the occurrence count for the IP address
            # Excludes TIER_ONE Traffic
            if  timestamp.lower() in line.lower() and not any(
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
                                addActivity(message)
                                block_ip(f"{BIG_IP}.0/24", message)
                                
                                # BLocks anything in IP_BLOCKS
                            elif any(
                                word.lower() in line.lower() for word in IP_BLOCKS
                            ):
                               
                                shorten = line.lower().split(" ")[6]
                                shoroten_again = shorten[:30]
                                message = f"\t🚨 Blocked IP: {ip_address} 👉 {shoroten_again}\n"
                                addActivity(message)
                                block_ip(ip_address, message)
                            else:
                                # Prints any Web Traffic that does not fit into any of the filtering arrays above
                                shorten = line.lower().split(" ")[6]
                                shoroten_again = shorten[:30]
                                addActivity(
                                f"\t🕵️ {ip_address} {shoroten_again}\n")
                        except Exception as err:
                            print(f"Something went wrong: {err}")

        a4ddActivity(f"\nIP Address Count:\n")
        # Block IP's over the IP_OCCURRENCE_THRESHOLD
        # TIER_ONE Traffic does not count
        for ip, count in ip_counts.items():
            addActivity(f"\t📍 {ip} {count}")
            if count > IP_OCCURRENCE_THRESHOLD:
                message = f"🚨 Blocked: {ip} with a count of {count}"
                #addActivity(message)
                block_ip(ip, message)