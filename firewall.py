# Python Firewall - DDOS Protection
# Copyright (C) 2025  @verita84@poster.place
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import time
import os
import subprocess
import argparse
import threading
from commands import save_nft_rules
from commands import block_country
from cli import buildCLI
from process import process_log
from db import activity
from db import getActivity
from db import clearDB
from config import TIME_FRAME
from config import LISTEN_ADDRESS
from config import LISTEN_PORT
from config import COUNTRY_BLOCKLIST
from html import buildWeb
from api import app
from message import send_message

class CountryBlock(threading.Thread):
    def run(self):
        if COUNTRY_BLOCKLIST:
            block_country()

class BackgroundTasks(threading.Thread):
    def run(self):
        try:
            parser = argparse.ArgumentParser(description="Firewall Script")
            parser.add_argument("--print", action="store_true", help="Print IP address counts")
            args = parser.parse_args()
            if(args.print):
                send_message("[Python Firewall running in Foreground Mode]")
            else:
                send_message("[Python Firewall running in Daemon Mode]")

            while True:
                clearDB()
                now = time.strftime("%d/%b/%Y:%H:%M:%S", time.localtime(time.time()))
                timestamp = time.strftime(
                    "%d/%b/%Y:%H:%M", time.localtime(time.time() - TIME_FRAME)
                )

                process_log(timestamp)
                #save_nft_rules()

                if args.print:
                    os.system("clear")
                    buildCLI(getActivity(), timestamp)
                else: 
                    buildWeb(getActivity(), timestamp)

                time.sleep(
                    TIME_FRAME
                )  # Wait for the specified time frame before processing again
        except Exception as e:
            send_message(f"[BackgroundTasks error: {e}]")
            raise


if __name__ == "__main__":
    import sys
    import uvicorn
    if "--print" in sys.argv:
        # CLI display mode: run loop directly, no web server
        BackgroundTasks().run()
    else:
        t = BackgroundTasks()
        t.daemon = True
        t.start()
        uvicorn.run(app, host=LISTEN_ADDRESS, port=LISTEN_PORT)
    
