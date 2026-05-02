# Configuration variables
LISTEN_ADDRESS = "0.0.0.0"
#LISTEN_ADDRESS =  "192.168.7.1"

LISTEN_PORT = "6767"

LOG_FILE = "/tmp/access.log"

# Block IP's after this many connections
IP_OCCURRENCE_THRESHOLD = 50

# Scan NGINX log file LOG_FILE this ofter
TIME_FRAME = 30 # 30 Seconds

# Automatically blocks these
SUBNET_BLOCKS = [
]

# Front Page Title Redirect Path 
REDIRECT='/'
#REDIRECT='/status'

LOCAL_NETWORK = ["192.168.0", "47.5.68.214", "192.168.5", "107.175.34.92", "69.145.1.133"]

# SKIP NTFY Alerts if a word is on this list
SKIP_ALERTS = [
    "Daemon Mode",
    "already",
    "searching",
    "sleeping",
    "IP Address Counts",
    "Amethyst",
    "rottenwheel",
    "/commit",
    "bot",
    "php",
]

#OPTIONALNTFY URL for Push Notificiations
NTFY_URL = ""
#NTFY_URL = "https://push.poster.place/logs"

# Save the NFT rules
NFT_SAVED_RULES = "/etc/firewall.nft"

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COUNTRY_BLOCKLIST = [
        os.path.join(BASE_DIR, "il-aggregated.zone"),
        os.path.join(BASE_DIR, "in-aggregated.zone"),
        os.path.join(BASE_DIR, "cn-aggregated.zone")
]
