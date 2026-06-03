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
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
:root {{
  --bg-primary: #05060f;
  --bg-card: #080a18;
  --bg-card-hover: #0e1028;
  --text-primary: #cbd5e1;
  --text-secondary: #4a5568;
  --neon-cyan: #00f0ff;
  --neon-pink: #ff2d78;
  --neon-purple: #c500ff;
  --neon-yellow: #f0c000;
  --neon-green: #00ff9f;
  --border-dim: #111827;
  --shadow: 0 4px 24px rgba(0,0,0,0.7);
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ -webkit-font-smoothing: antialiased; }}
body {{
  background-color: var(--bg-primary);
  background-image:
    linear-gradient(rgba(0,240,255,0.022) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,240,255,0.022) 1px, transparent 1px);
  background-size: 44px 44px;
  color: var(--text-primary);
  font-family: 'Share Tech Mono', 'Courier New', monospace;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}}
body::after {{
  content: '';
  position: fixed; inset: 0; pointer-events: none; z-index: 9999;
  background: repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,0,0,0.04) 3px, rgba(0,0,0,0.04) 4px);
}}
header {{
  background: linear-gradient(180deg, #0a0c20 0%, #05060f 100%);
  border-bottom: 1px solid rgba(0,240,255,0.2);
  padding: 1rem 2rem;
  position: sticky; top: 0; z-index: 100;
  box-shadow: 0 0 40px rgba(0,240,255,0.07), 0 4px 20px rgba(0,0,0,0.6);
}}
.header-top {{
  display: flex; flex-direction: column; align-items: center; gap: 0.5rem;
}}
.header-title {{
  font-size: 1.5rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.15em;
}}
.header-title a {{
  color: var(--neon-cyan);
  text-decoration: none;
  text-shadow: 0 0 8px var(--neon-cyan), 0 0 24px rgba(0,240,255,0.45), 0 0 48px rgba(0,240,255,0.18);
  transition: text-shadow 0.3s;
}}
.header-title a:hover {{
  text-shadow: 0 0 12px var(--neon-cyan), 0 0 36px rgba(0,240,255,0.65), 0 0 72px rgba(0,240,255,0.3);
}}
.header-stats {{ display: flex; gap: 1rem; }}
.stat-badge {{
  display: inline-flex; align-items: center; gap: 0.3rem;
  padding: 0.2rem 0.8rem; border-radius: 2px;
  font-size: 0.72rem; font-weight: 700;
  white-space: nowrap; text-transform: uppercase; letter-spacing: 0.07em;
  border: 1px solid;
}}
.stat-badge.cpu {{
  background: rgba(0,180,220,0.07); color: #00c8ef;
  border-color: rgba(0,200,240,0.25);
  box-shadow: 0 0 10px rgba(0,200,240,0.1), inset 0 0 8px rgba(0,200,240,0.04);
}}
.stat-badge.blocked {{
  background: rgba(255,45,120,0.07); color: var(--neon-pink);
  border-color: rgba(255,45,120,0.28);
  box-shadow: 0 0 10px rgba(255,45,120,0.12), inset 0 0 8px rgba(255,45,120,0.04);
}}
.header-timestamp {{
  text-align: center; padding: 0.4rem 0 0.1rem 0;
  font-size: 0.72rem; color: var(--text-secondary);
  border-top: 1px solid rgba(0,240,255,0.08);
  margin-top: 0.5rem; letter-spacing: 0.1em; text-transform: uppercase;
}}
main {{
  display: flex; flex-direction: column; flex: 1; gap: 1rem; padding: 1rem; min-height: 0;
}}
.top-row {{
  display: flex; gap: 1rem; flex: 2; min-height: 0;
}}
.column {{
  flex: 1; background: var(--bg-card);
  border: 1px solid var(--border-dim);
  border-radius: 3px; overflow: hidden;
  display: flex; flex-direction: column;
  box-shadow: var(--shadow);
  transition: border-color 0.3s, box-shadow 0.3s;
  position: relative;
}}
.column::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
}}
.column:has(.column-header.blocked)::before {{
  background: linear-gradient(90deg, transparent 0%, var(--neon-pink) 50%, transparent 100%);
  box-shadow: 0 0 12px var(--neon-pink);
}}
.column:has(.column-header.queries)::before {{
  background: linear-gradient(90deg, transparent 0%, var(--neon-yellow) 50%, transparent 100%);
  box-shadow: 0 0 12px var(--neon-yellow);
}}
.column:has(.column-header.counters)::before {{
  background: linear-gradient(90deg, transparent 0%, var(--neon-purple) 50%, transparent 100%);
  box-shadow: 0 0 12px var(--neon-purple);
}}
.column:has(.column-header.blocked):hover {{
  border-color: rgba(255,45,120,0.25);
  box-shadow: var(--shadow), 0 0 20px rgba(255,45,120,0.06);
}}
.column:has(.column-header.queries):hover {{
  border-color: rgba(240,192,0,0.25);
  box-shadow: var(--shadow), 0 0 20px rgba(240,192,0,0.06);
}}
.column:has(.column-header.counters):hover {{
  border-color: rgba(197,0,255,0.25);
  box-shadow: var(--shadow), 0 0 20px rgba(197,0,255,0.06);
}}
.column:has(.column-header.allowed)::before {{
  background: linear-gradient(90deg, transparent 0%, var(--neon-green) 50%, transparent 100%);
  box-shadow: 0 0 12px var(--neon-green);
}}
.column:has(.column-header.allowed):hover {{
  border-color: rgba(0,255,159,0.25);
  box-shadow: var(--shadow), 0 0 20px rgba(0,255,159,0.06);
}}
.column-header {{
  padding: 0.7rem 1rem; font-size: 0.72rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.12em;
  border-bottom: 1px solid var(--border-dim);
  display: flex; align-items: center; gap: 0.5rem;
}}
.column-header.blocked {{
  color: var(--neon-pink); border-bottom-color: rgba(255,45,120,0.18);
  text-shadow: 0 0 8px rgba(255,45,120,0.55);
}}
.column-header.queries {{
  color: var(--neon-yellow); border-bottom-color: rgba(240,192,0,0.18);
  text-shadow: 0 0 8px rgba(240,192,0,0.55);
}}
.column-header.counters {{
  color: var(--neon-purple); border-bottom-color: rgba(197,0,255,0.18);
  text-shadow: 0 0 8px rgba(197,0,255,0.55);
}}
.column-header.allowed {{
  color: var(--neon-green); border-bottom-color: rgba(0,255,159,0.18);
  text-shadow: 0 0 8px rgba(0,255,159,0.55);
}}
.column-body {{
  flex: 1; overflow-y: auto; padding: 0.4rem;
  scrollbar-width: thin; scrollbar-color: rgba(0,240,255,0.25) transparent;
}}
.column-body::-webkit-scrollbar {{ width: 3px; }}
.column-body::-webkit-scrollbar-track {{ background: transparent; }}
.column-body::-webkit-scrollbar-thumb {{ background: rgba(0,240,255,0.25); border-radius: 2px; }}
.entry {{
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.4rem 0.5rem; margin-bottom: 0.15rem;
  border-radius: 2px; font-size: 0.78rem;
  transition: background 0.12s, border-color 0.12s;
  word-break: break-all;
  border-left: 2px solid transparent;
}}
.entry:hover {{ background: var(--bg-card-hover); border-left-color: var(--neon-cyan); }}
.entry a {{
  color: var(--neon-cyan); text-decoration: none; font-weight: 500;
  transition: text-shadow 0.15s;
}}
.entry a:hover {{ text-shadow: 0 0 8px var(--neon-cyan); }}
.entry .meta {{ color: var(--text-secondary); font-size: 0.7rem; letter-spacing: 0.02em; }}
.entry .badge-icon {{
  display: inline-flex; align-items: center; justify-content: center;
  width: 1.4rem; height: 1.4rem; border-radius: 2px;
  font-size: 0.72rem; flex-shrink: 0;
}}
.entry .badge-icon.blocked {{ background: rgba(255,45,120,0.12); }}
.entry .badge-icon.query  {{ background: rgba(240,192,0,0.12); }}
.entry .badge-icon.counter {{ background: rgba(197,0,255,0.12); }}
.entry .badge-icon.allowed {{ background: rgba(0,255,159,0.12); }}
.entry .count {{
  background: rgba(0,180,220,0.08); color: #00c8ef;
  border: 1px solid rgba(0,180,220,0.2);
  padding: 0.1rem 0.45rem; border-radius: 2px;
  font-size: 0.65rem; font-weight: 700;
  white-space: nowrap; margin-left: auto; letter-spacing: 0.05em;
}}
.entry .lookup-btn {{
  padding: 0.15rem 0.45rem; border-radius: 2px; font-size: 0.72rem;
  color: var(--text-secondary); background: none;
  border: 1px solid transparent; cursor: pointer;
  transition: all 0.15s; flex-shrink: 0;
}}
.entry .lookup-btn:hover {{
  background: rgba(0,240,255,0.07); color: var(--neon-cyan);
  border-color: rgba(0,240,255,0.28);
  box-shadow: 0 0 8px rgba(0,240,255,0.1);
}}
.modal-overlay {{
  position: fixed; inset: 0; background: rgba(0,0,0,0.88);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 0.5rem;
  backdrop-filter: blur(6px);
}}
.modal-box {{
  background: #070918; border: 1px solid rgba(0,240,255,0.28);
  border-radius: 3px; width: 95vw; max-width: 1100px;
  height: 90vh; display: flex; flex-direction: column;
  box-shadow: 0 0 50px rgba(0,240,255,0.08), 0 0 100px rgba(0,0,0,0.9), inset 0 0 30px rgba(0,240,255,0.015);
}}
.modal-header {{
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.875rem 1.25rem; border-bottom: 1px solid rgba(0,240,255,0.12);
  background: linear-gradient(90deg, rgba(0,240,255,0.04), transparent 60%);
}}
.modal-header-title {{
  font-size: 0.82rem; font-weight: 700; color: var(--neon-cyan);
  text-transform: uppercase; letter-spacing: 0.12em;
  text-shadow: 0 0 8px rgba(0,240,255,0.5);
}}
.modal-close {{
  background: none; border: 1px solid rgba(0,240,255,0.2); color: var(--text-secondary);
  cursor: pointer; font-size: 0.9rem; padding: 0.2rem 0.55rem;
  border-radius: 2px; transition: all 0.15s; line-height: 1.4;
  font-family: inherit;
}}
.modal-close:hover {{
  background: rgba(255,45,120,0.1); border-color: var(--neon-pink);
  color: var(--neon-pink); box-shadow: 0 0 8px rgba(255,45,120,0.2);
}}
.modal-body {{
  flex: 1; overflow: hidden; display: flex; flex-direction: column;
  padding: 0.875rem; gap: 0.65rem; min-height: 0;
}}
.modal-ip-info {{
  display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;
  font-size: 0.76rem; letter-spacing: 0.04em;
  padding: 0.45rem 0.75rem;
  background: rgba(0,240,255,0.025);
  border: 1px solid rgba(0,240,255,0.1); border-radius: 2px;
}}
.modal-ip-info a {{
  color: var(--neon-cyan); text-decoration: none; font-weight: 500;
  transition: text-shadow 0.15s;
}}
.modal-ip-info a:hover {{ text-shadow: 0 0 8px var(--neon-cyan); }}
#modal-logs {{
  flex: 1; min-height: 0; background: #020308; color: #39ff9a;
  border: 1px solid rgba(0,240,255,0.12); border-radius: 2px;
  padding: 0.75rem; font-family: 'Courier New', 'Consolas', monospace;
  font-size: 0.76rem; line-height: 1.7; resize: none; overflow: auto;
  white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere;
  scrollbar-width: thin; scrollbar-color: rgba(0,240,255,0.25) transparent;
  text-shadow: 0 0 4px rgba(57,255,154,0.3);
}}
@media (max-width: 768px) {{
  .top-row {{ flex-direction: column; }}
  .column {{ max-height: 40vh; }}
  header {{ padding: 0.75rem 1rem; }}
  .header-top {{ flex-direction: column; align-items: flex-start; }}
  .modal-overlay {{ padding: 0; backdrop-filter: none; }}
  .modal-box {{ width: 100vw; height: 100vh; border-radius: 0; }}
}}
</style>
</head><body>
<header>
  <div class="header-top">
    <div class="header-title"><a href="{REDIRECT}">🛡️ Firewall Console</a></div>
    <div class="header-stats">
      <span class="stat-badge cpu">⚡ {cpu}</span>
      <span class="stat-badge blocked">🚫 {blocked} blocked</span>
    </div>
  </div>
  <div class="header-timestamp">📡 traffic as of: {timestamp}</div>
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

def htmlModal():
    return """<div id="ip-modal" class="modal-overlay" style="display:none" onclick="if(event.target===this)closeModal()">
  <div class="modal-box">
    <div class="modal-header">
      <span class="modal-header-title">🔬 <span id="modal-ip-title">IP Analysis</span></span>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body">
      <div class="modal-ip-info" id="modal-ip-info"></div>
      <textarea id="modal-logs" readonly>Loading...</textarea>
    </div>
  </div>
</div>
<script>
function openIPModal(ip, date) {
  document.getElementById('modal-ip-title').textContent = ip;
  var info = document.getElementById('modal-ip-info');
  info.innerHTML = '<a href="https://' + ip + '" target="_blank">🔗 ' + ip + '</a>' +
    '<a href="https://www.ip-tracker.org/lookup.php?ip=' + encodeURIComponent(ip) + '" target="_blank">🌐 Track Location</a>';
  var logs = document.getElementById('modal-logs');
  logs.value = 'Loading...';
  document.getElementById('ip-modal').style.display = 'flex';
  fetch('/ip/data?ip=' + encodeURIComponent(ip) + '&date=' + encodeURIComponent(date))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      logs.value = data.logs.length ? data.logs.join('\\n') : 'No log entries found.';
    })
    .catch(function() { logs.value = 'Error fetching data.'; });
}
function closeModal() {
  document.getElementById('ip-modal').style.display = 'none';
}
document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeModal(); });
</script>"""

def buildWeb(activity, timestamp):
    blocked_array = []
    standard_queries = []
    ip_counters = []
    allowed_array = []

    for line in activity:
        if "🚨 Blocked IP:" in line:
            value = line.split(" ")
            ip_val = value[3]
            line = f'<div class="entry"><span class="badge-icon blocked">🛑</span><a target="_blank" href="https://{ip_val}">{ip_val}</a> <span class="meta">{value[4]} {value[5]}</span><button class="lookup-btn" onclick="openIPModal(\'{ip_val}\', \'{timestamp}\')">🔍</button></div>'
            if line not in blocked_array:
                blocked_array.append(line)
        if "🚨 Blocked Subnet:" in line:
            value = line.split(" ")
            ip_val = value[3]
            line = f'<div class="entry"><span class="badge-icon blocked">🛑</span><a target="_blank" href="https://{ip_val}">{ip_val}</a> <span class="meta">{value[4]} {value[5]}</span><button class="lookup-btn" onclick="openIPModal(\'{ip_val}\', \'{timestamp}\')">🔍</button></div>'
            if line not in blocked_array:
                blocked_array.append(line)
        if "📍" in line:
            URL_FIX = line.split(" ")
            value = line.split(" ")
            ip_val = URL_FIX[1]
            line = f'<div class="entry"><span class="badge-icon counter">📍</span><a target="_blank" href="https://{ip_val}">{ip_val}</a><span class="count">{value[2]} hits</span><button class="lookup-btn" onclick="openIPModal(\'{ip_val}\', \'{timestamp}\')">🔍</button></div>'
            if line not in ip_counters:
                ip_counters.append(line)
        if "🕵️" in line:
            URL_FIX = line.split(" ")
            URL_PARSE = line.split(" ")
            ip_val = URL_PARSE[1]
            line = f'<div class="entry"><span class="badge-icon query">⁉️</span><a target="_blank" href="https://{URL_FIX[1]}">{URL_FIX[1]}</a> <span class="meta">👉 {URL_PARSE[2]}</span><button class="lookup-btn" onclick="openIPModal(\'{ip_val}\', \'{timestamp}\')">🔍</button></div>'
            if line not in standard_queries:
                standard_queries.append(line)
        if "✅" in line:
            URL_FIX = line.split(" ")
            ip_val = URL_FIX[1]
            count_val = URL_FIX[2].strip() if len(URL_FIX) > 2 else ""
            entry = f'<div class="entry"><span class="badge-icon allowed">✅</span><a target="_blank" href="https://{ip_val}">{ip_val}</a><span class="count">{count_val} hits</span><button class="lookup-btn" onclick="openIPModal(\'{ip_val}\', \'{timestamp}\')">🔍</button></div>'
            if entry not in allowed_array:
                allowed_array.append(entry)

    clearHTML()
    addHTML(basicHTML(timestamp))
    
    addHTML('<main>')
    addHTML('<div class="top-row">')

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

    addHTML('</div>')

    addHTML('<div class="column"><div class="column-header allowed">✅ Allowed Traffic</div><div class="column-body">')
    for line in allowed_array:
        addHTML(line)
    addHTML('</div></div>')

    addHTML('</main>')
    addHTML(htmlModal())
    addHTML(htmlRELOAD())
    addHTML('</body></html>')
