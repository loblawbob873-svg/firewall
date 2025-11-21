# Configuration variables
LOG_FILE = "/tmp/access.log"

# Block IP's after this many connections
IP_OCCURRENCE_THRESHOLD = 50

# Scan NGINX log file LOG_FILE this ofter
TIME_FRAME = 30  # 30 Seconds

# Automatically blocks these
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
    "php",
]

#OPTIONAL NTFY URL for Push Notificiations
#NTFY_URL = ""
NTFY_URL = "https://push.poster.place/logs"

# Web Inferface HTML File
WEB_HTML = "/tmp/python-firewall.html"

# Save the NFT rules
NFT_SAVED_RULES = "/etc/firewall.nft"
