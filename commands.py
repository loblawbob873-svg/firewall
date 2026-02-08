import psutil
import subprocess
import os
from message import send_message
from config import NFT_SAVED_RULES

# Where to save the firewall rules
NFT_SAVED_RULES = "/etc/firewall.nft"

def get_cpu_usage():
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent < 50:
        final = f"💻 CPU usage: {cpu_percent}% 😀"
    else:
        final = f"💻 CPU usage: {cpu_percent}% 😡"
    return f"{final}"

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
        # Add to blackhole set only (single IPs and CIDR; blackhole set needs "flags interval" for CIDR)
        command = f"/usr/sbin/nft add element ip filter blackhole {{ {ip} }}"
        os.system(command)
        send_message(f"{message}")
