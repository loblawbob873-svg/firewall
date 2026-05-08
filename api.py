from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from html import basicHTML
from html import htmlRELOAD
from ai import generate_reply
from config import LOG_FILE, USE_JOURNALD, JOURNALD_UNIT
from db import getHTML
import subprocess
import time
import json
# ------------------------------------------------------------------
# FastAPI app
# ------------------------------------------------------------------
app = FastAPI(
    title="Python Firewall",
    description="DDOS Protection",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def main():
    DATA = ""
    for line in getHTML():
        DATA+= line
    if not DATA:
        content = (f" {basicHTML("")} {htmlRELOAD()} <br><br><h2>Please wait...........</h2>")
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(content=DATA)

@app.get("/ip")
async def main(ip: str, date: str):
    array = []
    content = basicHTML(date)
    try:
        if USE_JOURNALD:
            # Parse date like "08/May/2026:08:39" to journalctl format
            month_map = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                        "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
            if ":" in date:
                date_part, time_part = date.split(":", 1)
                day, month, year = date_part.split("/")
                month_num = month_map.get(month, month)
                # time_part could be "08" or "08:39"
                if ":" in time_part:
                    since = f"{year}-{month_num}-{day} {time_part}:00"
                    until = f"{year}-{month_num}-{day} {time_part}:59"
                else:
                    since = f"{year}-{month_num}-{day} {time_part}:00:00"
                    until = f"{year}-{month_num}-{day} {time_part}:59:59"
            else:
                day, month, year = date.split("/")
                month_num = month_map.get(month, month)
                since = f"{year}-{month_num}-{day} 00:00:00"
                until = f"{year}-{month_num}-{day} 23:59:59"
            result = subprocess.run(
                ["journalctl", "-u", JOURNALD_UNIT, f"--since={since}", f"--until={until}", "--no-pager", "-o", "cat"],
                capture_output=True, text=True
            )
            lines = result.stdout.splitlines()
            for line in lines:
                if ip in line:
                    array.append(line)
        else:
            with open(f"{LOG_FILE}", "r") as f:
                for line in f:
                    if date in line:
                        if ip in line:
                            array.append(line)

        content += f'<br><br><p allign=center><h2>🔬 Analyzing Logs for IP: <a style="text-decoration:none" target="_blank" href="https://{ip}"> {ip} </a> </a></p><a href="https://www.ip-tracker.org/lookup.php?ip={ip}" style="text-decoration:none" target="_blank"> &nbsp🌐 Track IP</a></h2></p>'
        content += '<textarea id="logs" readonly></textarea>'
        content += "<script>"
        content += f"const myArray = {json.dumps(array)}"
        content += "\nconst logs = document.getElementById('logs');\n"
        content += "for (line of myArray) {   logs.innerHTML += line + '\\n'; }"
        content += "</script>"
        return HTMLResponse(content=content)
        #return array
    except Exception as e:
        content += "<h2><p> Error finding data</p></h2>"
        return HTMLResponse(content=content)


@app.get("/ai")
async def main(ip: str):
    return generate_reply(ip)
