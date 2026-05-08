import re
import psutil
import subprocess
import os
from message import send_message
from config import NFT_SAVED_RULES
from config import COUNTRY_BLOCKLIST

# Where to save the firewall rules NFT_SAVED_RULES = "/etc/firewall.nft"

def get_cpu_usage():
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent < 50:
        final = f"💻 CPU usage: {cpu_percent}% 😀"
    else:
        final = f"💻 CPU usage: {cpu_percent}% 😡"
    return f"{final}"

def save_nft_rules():
    with open(NFT_SAVED_RULES, "w") as f:
        subprocess.run(["/usr/sbin/nft", "list", "ruleset"], stdout=f, check=True)


def get_block_count():
    """Count elements in the blackhole set."""
    try:
        output = subprocess.check_output(
            ["/usr/sbin/nft", "list", "set", "ip", "filter", "blackhole"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        m = re.search(r"elements\s*=\s*\{\s*([^}]*)\}", output)
        if m:
            elem_str = m.group(1).strip()
            count = len([e.strip() for e in elem_str.split(",") if e.strip()]) if elem_str else 0
            return str(count)
        return "0"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "0"

def block_ip(ip, message, country=None):
    nft_output = subprocess.check_output(["/usr/sbin/nft", "list", "ruleset"], text=True)
    if ip not in nft_output:
        if country is None:
            set_name = "blackhole"
        else:
            set_name = os.path.basename(country).split('-')[0]
        subprocess.run(
            ["/usr/sbin/nft", "add", "element", "ip", "filter", set_name, "{", ip, "}"],
            check=True
        )
        send_message(message)

def block_country():
    for filename in COUNTRY_BLOCKLIST:
        with open(filename, 'r') as file:
            for line in file:
                ip = line.strip()
                if ip:
                    block_ip(ip, f"{ip}", filename)
