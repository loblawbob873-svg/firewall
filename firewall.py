import time
import os
import subprocess
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
from process import process_log
from db import activity

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

        process_log(timestamp)
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
