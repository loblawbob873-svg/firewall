import re
import psutil
import subprocess
import os
import time
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

def _country_set(filename):
    return os.path.basename(filename).split('-')[0]


def _set_exists(set_name):
    return subprocess.run(["/usr/sbin/nft", "list", "set", "ip", "filter", set_name],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def load_country(filename, wait_seconds=120):
    """Replace one country set with the contents of its zone file. Returns (loaded, failed).

    ONE nft transaction per file ("flush set" + "add element" with every range), instead of one
    `nft add` per range preceded by a full `nft list ruleset` to see if it is already there. That
    was ~20,000 listings of an ever-growing ruleset, and the first range nft refused (an overlap)
    raised out of the thread and silently skipped every country after it. The transaction is
    atomic: the set is never seen half-empty, and a refused batch changes nothing.
    """
    set_name = _country_set(filename)
    # At boot this can start before firewall.service has created the sets.
    deadline = time.time() + wait_seconds
    while not _set_exists(set_name):
        if time.time() > deadline:
            send_message(f"[country blocklist: set {set_name} does not exist, {filename} not loaded]")
            return 0, 0
        time.sleep(2)
    with open(filename, 'r') as file:
        ranges = [l.strip() for l in file if l.strip() and not l.strip().startswith('#')]
    if not ranges:
        return 0, 0
    script = f"flush set ip filter {set_name}\nadd element ip filter {set_name} {{ {', '.join(ranges)} }}\n"
    batch = subprocess.run(["/usr/sbin/nft", "-f", "-"], input=script, text=True, capture_output=True)
    if batch.returncode == 0:
        return len(ranges), 0
    # The batch was refused as a whole (e.g. two overlapping ranges in the zone file). Fall back to
    # adding one range at a time so one bad line cannot cost the rest of the country.
    failed = 0
    for ip in ranges:
        one = subprocess.run(["/usr/sbin/nft", "add", "element", "ip", "filter", set_name, "{", ip, "}"],
                             capture_output=True, text=True)
        if one.returncode != 0:
            failed += 1
    return len(ranges) - failed, failed


def block_country():
    for filename in COUNTRY_BLOCKLIST:
        try:
            loaded, failed = load_country(filename)
            send_message(f"[country blocklist {_country_set(filename)}: {loaded} ranges loaded"
                         + (f", {failed} refused" if failed else "") + "]")
        except Exception as e:
            # One unreadable file must not stop the other countries loading.
            send_message(f"[country blocklist {filename} failed: {e}]")
