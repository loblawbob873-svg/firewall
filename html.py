from commands import get_cpu_usage
from commands import get_block_count
from db import addHTML 
from db import clearHTML
from db import getHTML
from db import html

def basicHTML(timestamp):
    HTML = ("<html><head><style> p { text-indent: 50px; } #stats { font-size: 2em; margin-top: 50px; }"
        "body {  background-color: black; color: white;font-family: Arial, sans-serif; text-align: left; display: flex; flex-direction: column; height: 100vh; margin: 0; } header { background-color: black; padding: 20px; text-align: center; } main { display: flex; flex: 1; } aside, article, nav { flex: 1; border: 1px solid #ddd; box-sizing: border-box; } #logs { white-space: pre-wrap; width: 1000px; height: 1000px; }"
        '@import "compass/css3"; * { -moz-box-sizing: border-box; -webkit-box-sizing: border-box; box-sizing: border-box; } html { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; } textarea { background-image: linear-gradient(#F1F1F1 50%, #F9F9F9 50%); background-size: 100% 4rem; border: 1px solid #CCC; width: 100%; height: 400px; line-height: 2rem; margin: 0 auto; padding: 4px 8px; }'
        "</style></head>" 
        "<body><header><h2>🔥 Python Firewall Web Console 🔥</h2><br> <br>"
        f"<p align=center><h2>{get_cpu_usage()}\tBlocked IP's: {get_block_count().strip()} ✅</h2></header"
        f"<br><p align=center><h2> ↕️Traffic as of: {timestamp}</p></h2></div>"
    )
    return HTML

def htmlRELOAD():
    addHTML("<script>\nwindow.setTimeout( function() {window.location.reload();}, 60000);</script>")

def buildWeb(activity,timestamp):
    blocked_array = []
    standard_queries = []
    ip_counters = []

    for line in activity:
        if "🚨 Blocked IP:" in line:
            value = line.split(" ")
            line = f'<p>🚨<a style="text-decoration:none" target="_blank" href="https://{value[3]}">{value[3]}</a>  {value[4]} {value[5]} <a target="_blank" href="/ip?ip={value[3]}&date={timestamp}" style="text-decoration:none"> 🔍</a></p>'
            blocked_array.append(line)
        if "🚨 Blocked Subnet:" in line:
            value = line.split(" ")
            line = f'<p>🚨<a style="text-decoration:none" target="_blank" href="https://{value[3]}">{value[3]}</a>  {value[4]} {value[5]} <a target="_blank" href="/ip?ip={value[3]}&date={timestamp}" style="text-decoration:none">🔍 </a> </a> </p>'
            blocked_array.append(line)
        if "📍" in line:
            value = line.split(" ")
            URL_FIX = line.split(" ")
            line = f'<p>📍 <a style="text-decoration:none" target="_blank" href="https://{URL_FIX[1]}">{URL_FIX[1]}</a>&nbsp;&nbsp;{value[2]} time(s) <a target="_blank" href="/ip?ip={URL_FIX[1]}&date={timestamp}" style="text-decoration:none"> 🔍</a></p>'
            ip_counters.append(line)
        if "🕵️" in line:
            URL = line.split("🕵️")
            URL_PARSE = line.split(" ")
            URL_FIX = line.split(" ")
            line = f'<p>🕵️<a style="text-decoration:none" target="_blank" href="https://{URL_FIX[1]}">{URL_FIX[1]}</a> &nbsp;👉 &nbsp;{URL_PARSE[2]} &nbsp; <a href="/ip?ip={URL_PARSE[1]}&date={timestamp}" target="_blank" style="text-decoration:none">🔍  </p></a></p>'
            standard_queries.append(line)
        if "\t" in line:
            line.replace("\t", "")
        if "\n" in line:
            line.replace("\n", "<br>")
    
    clearHTML() 
    addHTML(basicHTML(timestamp))
    htmlRELOAD()
    addHTML("<main><aside><h2><b>🚨 &nbsp; Blocked Traffic</b></h1><br></h2>")
    for line in blocked_array:
          if "🚨" in line:
            addHTML(f"<br>{line.replace("🚨","🛑")}</br>")
    addHTML("</aside>")
    addHTML("<article><h2><b>🕵️ &nbsp; Queries</b></h2><br>")
    for line in standard_queries:
        if "🕵️" in line:
            addHTML(f"<br>{line.replace("🕵️","⁉️")}</br>")
    addHTML("</article>")
    addHTML("<nav><h2><b>🧮 IP Counter</b></h2><br>")
    for line in ip_counters:
        if "📍" in line:
            addHTML(f"<br>{line}</br>")
    addHTML("</nav></main></body></html>")
    print(html)  