import time
import os
import subprocess
import argparse
import threading
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

class BackgroundTasks(threading.Thread):
    def run (self,*args,**kwargs):
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
            save_nft_rules()

            if args.print:
                os.system("clear")
                buildCLI(getActivity(), timestamp)
            else: 
                buildWeb(getActivity(),timestamp)

            time.sleep(
                TIME_FRAME
            )  # Wait for the specified time frame before processing again


if __name__ == "__main__":
    import uvicorn
    t = BackgroundTasks()
    t.start()
    uvicorn.run(app, host="0.0.0.0", port=6767)
    
