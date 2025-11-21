import time
import os
import subprocess
import argparse
from commands import save_nft_rules
from cli import buildCLI
from process import process_log
from db import activity
from db import getActivity
from db import clearDB
from config import TIME_FRAME
from html import buildWeb
from api import app
from message import send_message

def main():
    parser = argparse.ArgumentParser(description="Firewall Script")
    parser.add_argument("--print", action="store_true", help="Print IP address counts")
    args = parser.parse_args()

    while True:
        clearDB()
        now = time.strftime("%d/%b/%Y:%H:%M:%S", time.localtime(time.time()))
        timestamp = time.strftime(
            "%d/%b/%Y:%H:%M", time.localtime(time.time() - TIME_FRAME)
        )

        process_log(timestamp)
        save_nft_rules()

        if args.print:
            os.system("clear")
            buildCLI(getActivity(), timestamp)
        else: 
            send_message("Python Firewall running in Daemon Mode")
            buildWeb(getActivity(),timestamp)

        time.sleep(
            TIME_FRAME
        )  # Wait for the specified time frame before processing again


if __name__ == "__main__":
    main()
