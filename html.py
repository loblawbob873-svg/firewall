from commands import get_cpu_usage
from commands import get_block_count
from db import addHTML 
from db import clearHTML
from db import getHTML
from db import html
from config import REDIRECT

def basicHTML(timestamp):
    cpu = get_cpu_usage()
    blocked = get_block_count().strip()
    HTML = f"""<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
:root {{
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-card: #1e293b;
  --bg-card-hover: #334155;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --accent-blue: #3b82f6;
  --accent-green: #22c55e;
  --accent-red: #ef4444;
  --accent-yellow: #eab308;
  --accent-purple: #a855f7;
  --border-color: #334155;
  --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.3);
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }}
body {{
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}}
header {{
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow);
}}
.header-top {{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}}
.header-title {{
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.025em;
}}
.header-title a {{
  color: var(--text-primary);
  text-decoration: none;
  transition: color 0.2s;
}}
.header-title a:hover {{ color: var(--accent-blue); }}
.header-stats {{
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
}}
.stat-badge {{
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}}
.stat-badge.cpu {{ background: rgba(59,130,246,0.15); color: var(--accent-blue); }}
.stat-badge.blocked {{ background: rgba(239,68,68,0.15); color: var(--accent-red); }}
.header-timestamp {{
  text-align: center;
  padding: 0.5rem 0 0.25rem 0;
  font-size: 1rem;
  color: var(--text-secondary);
  border-top: 1px solid var(--border-color);
  margin-top: 0.5rem;
}}
main {{
  display: flex;
  flex: 1;
  gap: 1rem;
  padding: 1rem;
  min-height: 0;
}}
.column {{
  flex: 1;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 0.75rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow);
  transition: border-color 0.2s;
}}
.column:hover {{ border-color: #475569; }}
.column-header {{
  padding: 0.75rem 1rem;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}}
.column-header.blocked {{ color: var(--accent-red); border-bottom-color: rgba(239,68,68,0.3); }}
.column-header.queries {{ color: var(--accent-yellow); border-bottom-color: rgba(234,179,8,0.3); }}
.column-header.counters {{ color: var(--accent-purple); border-bottom-color: rgba(168,85,247,0.3); }}
.column-body {{
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  scrollbar-width: thin;
  scrollbar-color: var(--border-color) transparent;
}}
.column-body::-webkit-scrollbar {{ width: 4px; }}
.column-body::-webkit-scrollbar-track {{ background: transparent; }}
.column-body::-webkit-scrollbar-thumb {{ background: var(--border-color); border-radius: 2px; }}
.entry {{
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.625rem;
  margin-bottom: 0.25rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  transition: background 0.15s;
  word-break: break-all;
}}
.entry:hover {{ background: var(--bg-card-hover); }}
.entry a {{
  color: var(--accent-blue);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.15s;
}}
.entry a:hover {{ color: #60a5fa; text-decoration: underline; }}
.entry .meta {{
  color: var(--text-secondary);
  font-size: 0.75rem;
}}
.entry .badge-icon {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  flex-shrink: 0;
}}
.entry .badge-icon.blocked {{ background: rgba(239,68,68,0.15); }}
.entry .badge-icon.query {{ background: rgba(234,179,8,0.15); }}
.entry .badge-icon.counter {{ background: rgba(168,85,247,0.15); }}
.entry .count {{
  background: rgba(59,130,246,0.15);
  color: var(--accent-blue);
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 600;
  white-space: nowrap;
  margin-left: auto;
}}
.entry .lookup-btn {{
  padding: 0.125rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.15s;
  flex-shrink: 0;
}}
.entry .lookup-btn:hover {{
  background: rgba(59,130,246,0.15);
  color: var(--accent-blue);
}}
@media (max-width: 768px) {{
  main {{ flex-direction: column; }}
  .column {{ max-height: 40vh; }}
  header {{ padding: 0.75rem 1rem; }}
  .header-top {{ flex-direction: column; align-items: flex-start; }}
}}
</style>
</head><body>
<header>
  <div class="header-top">
    <div class="header-title"><a href="{REDIRECT}">🛡️ Firewall Console</a></div>
    <div class="header-stats">
      <span class="stat-badge cpu">⚡ {cpu}</span>
      <span class="stat-badge blocked">🚫 Blocked: {blocked}</span>
    </div>
  </div>
  <div class="header-timestamp">📡 Traffic as of: {timestamp}</div>
</header>
"""
    return HTML

def htmlRELOAD():
    return """<script>
(function() {
  let seconds = 40;
  const el = document.getElementById('countdown');
  const updateCountdown = () => { if (el) el.textContent = seconds + 's'; };
  const tick = () => {
    seconds--;
    if (seconds <= 0) { window.location.reload(); }
    updateCountdown();
  };
  const style = document.createElement('style');
  style.textContent =
    '#reload-bar { position: fixed; bottom: 0; left: 0; height: 3px; background: linear-gradient(90deg, #3b82f6, #a855f7); transition: width 1s linear; z-index: 999; }' +
    '#reload-indicator { position: fixed; bottom: 10px; right: 16px; font-size: 0.75rem; color: #64748b; z-index: 999; font-family: system-ui, sans-serif; }';
  document.head.appendChild(style);
  const bar = document.createElement('div'); bar.id = 'reload-bar'; bar.style.width = '100%';
  const indicator = document.createElement('div'); indicator.id = 'reload-indicator';
  indicator.innerHTML = '🔄 <span id="countdown">40s</span>';
  document.body.appendChild(bar);
  document.body.appendChild(indicator);
  setInterval(tick, 1000);
  let w = 100;
  setInterval(function() { w -= 2.5; if (w < 0) w = 0; bar.style.width = w + '%'; }, 1000);
})();
</script>"""

def buildWeb(activity, timestamp):
    blocked_array = []
    standard_queries = []
    ip_counters = []

    for line in activity:
        if "🚨 Blocked IP:" in line:
            value = line.split(" ")
            line = f'<div class="entry"><span class="badge-icon blocked">🛑</span><a target="_blank" href="https://{value[3]}">{value[3]}</a> <span class="meta">{value[4]} {value[5]}</span><a class="lookup-btn" target="_blank" href="/ip?ip={value[3]}&date={timestamp}">🔍</a></div>'
            blocked_array.append(line)
        if "🚨 Blocked Subnet:" in line:
            value = line.split(" ")
            line = f'<div class="entry"><span class="badge-icon blocked">🛑</span><a target="_blank" href="https://{value[3]}">{value[3]}</a> <span class="meta">{value[4]} {value[5]}</span><a class="lookup-btn" target="_blank" href="/ip?ip={value[3]}&date={timestamp}">🔍</a></div>'
            blocked_array.append(line)
        if "📍" in line:
            URL_FIX = line.split(" ")
            value = line.split(" ")
            line = f'<div class="entry"><span class="badge-icon counter">📍</span><a target="_blank" href="https://{URL_FIX[1]}">{URL_FIX[1]}</a><span class="count">{value[2]} hits</span><a class="lookup-btn" target="_blank" href="/ip?ip={URL_FIX[1]}&date={timestamp}">🔍</a></div>'
            ip_counters.append(line)
        if "🕵️" in line:
            URL_FIX = line.split(" ")
            URL_PARSE = line.split(" ")
            line = f'<div class="entry"><span class="badge-icon query">⁉️</span><a target="_blank" href="https://{URL_FIX[1]}">{URL_FIX[1]}</a> <span class="meta">👉 {URL_PARSE[2]}</span><a class="lookup-btn" target="_blank" href="/ip?ip={URL_PARSE[1]}&date={timestamp}">🔍</a></div>'
            standard_queries.append(line)
    
    clearHTML() 
    addHTML(basicHTML(timestamp))
    
    addHTML('<main>')
    
    addHTML('<div class="column"><div class="column-header blocked">🛑 Blocked Traffic</div><div class="column-body">')
    for line in blocked_array:
        addHTML(line)
    addHTML('</div></div>')
    
    addHTML('<div class="column"><div class="column-header queries">⁉️ Queries</div><div class="column-body">')
    for line in standard_queries:
        addHTML(line)
    addHTML('</div></div>')
    
    addHTML('<div class="column"><div class="column-header counters">📍 IP Counters</div><div class="column-body">')
    for line in ip_counters:
        addHTML(line)
    addHTML('</div></div>')
    
    addHTML('</main>')
    addHTML(htmlRELOAD())
    addHTML('</body></html>')
