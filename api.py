from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from html import basicHTML
from html import htmlRELOAD
from ai import generate_reply
from config import LOG_FILE, USE_JOURNALD, JOURNALD_UNIT, REDIRECT
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

        content += '''<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  background: #0f172a; color: #f1f5f9;
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  min-height: 100vh; padding: 2rem;
}
.ip-header {
  background: linear-gradient(135deg, #1e293b, #0f172a);
  border: 1px solid #334155; border-radius: 0.75rem;
  padding: 1.5rem 2rem; margin-bottom: 1.5rem;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.3);
}
.ip-header h2 { font-size: 1.25rem; font-weight: 700; margin-bottom: 0.5rem; }
.ip-header .ip-link { color: #3b82f6; text-decoration: none; font-weight: 600; }
.ip-header .ip-link:hover { color: #60a5fa; text-decoration: underline; }
.ip-header .track-link {
  display: inline-flex; align-items: center; gap: 0.25rem;
  margin-top: 0.5rem; padding: 0.375rem 1rem;
  background: rgba(59,130,246,0.15); color: #3b82f6;
  border-radius: 9999px; font-size: 0.875rem; font-weight: 500;
  text-decoration: none; transition: background 0.2s;
}
.ip-header .track-link:hover { background: rgba(59,130,246,0.25); }
.log-card {
  background: #1e293b; border: 1px solid #334155;
  border-radius: 0.75rem; overflow: hidden;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.3);
}
.log-card-header {
  padding: 0.75rem 1.25rem;
  font-size: 0.8rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; border-bottom: 1px solid #334155;
  color: #eab308; display: flex; align-items: center; gap: 0.5rem;
}
#logs {
  width: 100%; height: 500px; padding: 1rem;
  background: #0f172a; color: #e2e8f0;
  border: none; font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 0.8125rem; line-height: 1.6; resize: vertical;
}
#logs:focus { outline: none; }
.back-link {
  display: inline-flex; align-items: center; gap: 0.5rem;
  margin-bottom: 1rem; padding: 0.5rem 1rem;
  color: #94a3b8; text-decoration: none; font-size: 0.875rem;
  border-radius: 0.5rem; transition: all 0.15s;
}
.back-link:hover { background: #1e293b; color: #f1f5f9; }
</style>'''
        content += f'<a class="back-link" href="{REDIRECT}">← Back to Dashboard</a>'
        content += f'<div class="ip-header"><h2>🔬 Analyzing Logs for IP: <a class="ip-link" target="_blank" href="https://{ip}">{ip}</a></h2><a class="track-link" target="_blank" href="https://www.ip-tracker.org/lookup.php?ip={ip}">🌐 Track IP Location</a></div>'
        content += '<div class="log-card"><div class="log-card-header">📋 Log Entries</div>'
        content += '<textarea id="logs" readonly></textarea></div>'
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


@app.get("/ip/data")
async def ip_data(ip: str, date: str):
    array = []
    try:
        if USE_JOURNALD:
            month_map = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                        "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
            if ":" in date:
                date_part, time_part = date.split(":", 1)
                day, month, year = date_part.split("/")
                month_num = month_map.get(month, month)
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
            for line in result.stdout.splitlines():
                if ip in line:
                    array.append(line)
        else:
            with open(f"{LOG_FILE}", "r") as f:
                for line in f:
                    if date in line and ip in line:
                        array.append(line.rstrip())
        return JSONResponse({"ip": ip, "date": date, "logs": array})
    except Exception as e:
        return JSONResponse({"ip": ip, "date": date, "logs": [], "error": str(e)})


@app.get("/ai")
async def main(ip: str):
    return generate_reply(ip)
