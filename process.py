import time
import re
import subprocess
from config import LOG_FILE, USE_JOURNALD, JOURNALD_UNIT
from config import IP_OCCURRENCE_THRESHOLD
from config import TIME_FRAME
from db import addActivity
from commands import block_ip
from tier_one import TIER_ONE
from ip_blocks import IP_BLOCKS
from config import SUBNET_BLOCKS
from config import LOCAL_NETWORK

def extract_first_three_parts(ip):
    return ".".join(ip.split(".")[:3])

def extract_url(line):
    m = re.search(r'"[A-Z]+\s+(\S+)', line)
    return m.group(1)[:30] if m else "?"

def get_log_lines(timestamp):
    if USE_JOURNALD:
        since = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - TIME_FRAME))
        result = subprocess.run(
            ["journalctl", "-u", JOURNALD_UNIT, f"--since={since}", "--no-pager", "-o", "cat"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"journalctl error: {result.stderr.strip()}")
        return result.stdout.splitlines()
    else:
        with open(LOG_FILE, "r") as f:
            return [line for line in f if timestamp.lower() in line.lower()]

def process_log(timestamp):
    lines = get_log_lines(timestamp)

    ip_counts = {}
    allowed_counts = {}

    for line in lines:
        ip_match = re.search(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", line)
        if not ip_match:
            continue
        ip_address = ip_match.group()
        if any(lan.lower() in line.lower() for lan in LOCAL_NETWORK):
            continue

        if not any(term.lower() in line.lower() for term in TIER_ONE):
            ip_counts[ip_address] = ip_counts.get(ip_address, 0) + 1
            try:
                url = extract_url(line)
                if any(word.lower() in line.lower() for word in SUBNET_BLOCKS):
                    BIG_IP = extract_first_three_parts(ip_address)
                    message = f"\t🚨 Blocked Subnet: {ip_address} 👉 {url}\n"
                    addActivity(message)
                    block_ip(f"{BIG_IP}.0/24", message)
                elif any(word.lower() in line.lower() for word in IP_BLOCKS):
                    message = f"\t🚨 Blocked IP: {ip_address} 👉 {url}\n"
                    addActivity(message)
                    block_ip(ip_address, message)
                else:
                    addActivity(f"\t🕵️ {ip_address} {url}\n")
            except Exception as err:
                print(f"Something went wrong: {err}")
        else:
            allowed_counts[ip_address] = allowed_counts.get(ip_address, 0) + 1

    addActivity(f"\nIP Address Count:\n")
    for ip, count in ip_counts.items():
        addActivity(f"\t📍 {ip} {count}")

    for ip, count in allowed_counts.items():
        addActivity(f"\t✅ {ip} {count}")
        if count > IP_OCCURRENCE_THRESHOLD:
            message = f"🚨 Blocked: {ip} with a count of {count}"
            addActivity(message)
            block_ip(ip, message)
