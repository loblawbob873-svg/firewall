from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from html import basicHTML
from ai import generate_reply
from config import LOG_FILE
from db import getHTML
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
        content = (f" {basicHTML()} Web Interface not ready yet.")
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(content=DATA)

@app.get("/ip")
async def main(ip: str, date: str):
    array = []
    content += basicHTML()
    try:
        with open(f"{LOG_FILE}", "r") as f:
            for line in f:
                if date in line:
                    if ip in line:
                        array.append(line)

        content += f'<br><br><p allign=center><h2>🔬 Analyzing Logs for IP: <a style="text-decoration:none" target="_blank" href="https://{ip}"> {ip} </a> </a></p><a href="https://www.ip-tracker.org/lookup.php?ip={ip}" style="text-decoration:none" target="_blank"> &nbsp🌐 Track IP</a></h2></p>'
        content += '<textarea id="logs" readonly></textarea>'
        content += "<script>"
        content += f"const myArray = [{array}]"
        content += "\nconst logs = document.getElementById('logs');\n"
        content += "for (line of myArray) {   logs.innerHTML += `${line}`; }"
        content += "</script>"
        return HTMLResponse(content=content)
        #return array
    except Exception as e:
        content += "<h2><p> Error finding data</p></h2>"
        return HTMLResponse(content=content)


@app.get("/ai")
async def main(ip: str):
    return generate_reply(ip)