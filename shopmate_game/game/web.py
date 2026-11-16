"""
Hack ShopMate: the class game.

  /        the player page (phones)
  /board   the leaderboard for the projector

Run:  uvicorn game.web:app --port 8090
"""

from __future__ import annotations

import json
import os
import threading
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from game import levels as lv
from game.model import Simulated, make

app = FastAPI(title="Hack ShopMate")
MODEL = make()
FALLBACK = Simulated()
LOCK = threading.Lock()
BUSY = threading.BoundedSemaphore(int(os.environ.get("GAME_PARALLEL", "4")))  # model calls at once
GAP = float(os.environ.get("GAME_GAP_SECONDS", "3"))                              # per player
PLAYERS: dict[str, dict] = {}   # id -> {"name", "cleared": set, "last": {level: message}, "t": last request}
CRACKS: list[dict] = []         # newest first, for the board


def log(kind: str, text: str, **data):
    """One JSON line per event: readable in Cloud Logging, same as the crew."""
    print(json.dumps({"agent": "shopmate", "kind": kind, "message": f"shopmate {kind}: {text}"[:300],
                      "severity": "WARNING" if kind == "cracked" else "INFO", **data}), flush=True)


class Chat(BaseModel):
    player: str = Field(min_length=4, max_length=40)
    name: str = Field(min_length=1, max_length=24)
    level: int = Field(ge=1, le=len(lv.LEVELS))
    message: str = Field(min_length=1, max_length=500)


class Guess(BaseModel):
    player: str = Field(min_length=4, max_length=40)
    level: int = Field(ge=1, le=len(lv.LEVELS))
    guess: str = Field(min_length=1, max_length=60)


def player(pid: str, name: str = "") -> dict:
    with LOCK:
        p = PLAYERS.setdefault(pid, {"name": name or "player", "cleared": set(), "last": {}, "t": 0.0})
        if name:
            p["name"] = name.strip()[:24]
        return p


def unlocked(p: dict, n: int) -> bool:
    return n == 1 or (n - 1) in p["cleared"]


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL.name}


@app.get("/api/levels")
def levels_info():
    return [{"n": x.n, "name": x.name, "defence": x.defence, "hints": x.hints} for x in lv.LEVELS]


@app.post("/api/chat")
def chat(c: Chat):
    p = player(c.player, c.name)
    if not unlocked(p, c.level):
        raise HTTPException(403, "Clear the previous level first.")
    now = time.time()
    if now - p["t"] < GAP:
        raise HTTPException(429, f"Slow down: one message every {GAP:.0f} seconds.")
    p["t"] = now
    level = lv.BY_N[c.level]
    p["last"][c.level] = c.message
    stopped = lv.blocked_input(level, c.message)
    if stopped:
        log("blocked", f"L{level.n} input detector", player=p["name"])
        return {"reply": "", "blocked": stopped, "by": "detector"}
    text = lv.spotlight(c.message) if level.spotlight else c.message
    source = MODEL.name
    if not BUSY.acquire(timeout=20):
        raise HTTPException(503, "ShopMate is busy with the whole class. Try again in a few seconds.")
    try:
        reply = MODEL.reply(level, text)
    except Exception as exc:  # the class must never see a crash: fall back to the simulated model
        log("model_error", type(exc).__name__)
        reply, source = FALLBACK.reply(level, c.message), FALLBACK.name
    finally:
        BUSY.release()
    stopped = lv.blocked_output(level, reply)
    if stopped:
        log("blocked", f"L{level.n} output guard", player=p["name"])
        return {"reply": "", "blocked": stopped, "by": "output guard"}
    return {"reply": reply, "model": source}


@app.post("/api/guess")
def guess(g: Guess):
    p = player(g.player)
    level = lv.BY_N[g.level]
    if not unlocked(p, g.level):
        raise HTTPException(403, "Clear the previous level first.")
    if not lv.is_secret(level, g.guess):
        return {"ok": False}
    with LOCK:
        first = g.level not in p["cleared"]
        p["cleared"].add(g.level)
        if first:
            CRACKS.insert(0, {"name": p["name"], "level": g.level, "how": p["last"].get(g.level, "")[:160], "t": time.time()})
            del CRACKS[40:]
    log("cracked", f"{p['name']} cleared level {g.level}", level=g.level)
    return {"ok": True, "lesson": level.lesson, "next": g.level + 1 if g.level < len(lv.LEVELS) else None}


@app.get("/api/board")
def board():
    with LOCK:
        per_level = {x.n: sum(1 for p in PLAYERS.values() if x.n in p["cleared"]) for x in lv.LEVELS}
        top = sorted(PLAYERS.values(), key=lambda p: -len(p["cleared"]))[:12]
        return {"players": len(PLAYERS), "per_level": per_level, "model": MODEL.name,
                "top": [{"name": p["name"], "cleared": len(p["cleared"])} for p in top if p["cleared"]],
                "cracks": CRACKS[:8]}


@app.post("/api/reset")
def reset(request: Request):
    token = os.environ.get("ADMIN_TOKEN")
    if not token or request.headers.get("x-admin-token") != token:
        raise HTTPException(403, "Reset needs ADMIN_TOKEN.")
    with LOCK:
        PLAYERS.clear()
        CRACKS.clear()
    log("reset", "board cleared")
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
def play_page():
    return PLAY


@app.get("/board", response_class=HTMLResponse)
def board_page():
    return BOARD


CSS = r"""
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,'Segoe UI',sans-serif;background:#F5F0E6;color:#1F2328}
header{background:#1F2328;color:#fff;padding:14px 18px;display:flex;justify-content:space-between;align-items:center}
header b{font-size:18px}header span{font-size:12px;color:#B8C0CC}
main{max-width:720px;margin:0 auto;padding:14px}
.card{background:#fff;border:1px solid #D9D2C3;border-radius:12px;padding:14px;margin-bottom:12px}
.tabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}.tab{flex:1;min-width:52px;padding:9px 0;border-radius:9px;border:1px solid #CFC7B6;background:#fff;font-weight:700;font-size:15px}
.tab.on{background:#2C5D8F;color:#fff;border-color:#2C5D8F}.tab.done{background:#DCEFE3;border-color:#3E8E5E;color:#245C39}.tab:disabled{opacity:.4}
.def{font-size:14px;color:#5B6470}.def b{color:#1F2328}
#log{height:46vh;overflow-y:auto;padding:4px}.m{margin:8px 0;padding:10px 12px;border-radius:12px;font-size:15px;line-height:1.45;white-space:pre-wrap;word-wrap:break-word}
.me{background:#2C5D8F;color:#fff;margin-left:40px}.bot{background:#EFEAE0;margin-right:40px}.blk{background:#FCE4E4;color:#8A1F1F;margin-right:40px;font-weight:600}
.sys{background:#DCEFE3;color:#245C39;font-weight:600}.row{display:flex;gap:8px;margin-top:8px}
input,textarea{font:inherit;font-size:16px;padding:10px;border:1px solid #CFC7B6;border-radius:9px;width:100%}
button.go{padding:10px 16px;border-radius:9px;border:0;background:#2C5D8F;color:#fff;font-weight:700;font-size:16px}
button.win{background:#3E8E5E}.small{font-size:12px;color:#7A828C}.hint{font-size:13px;color:#7A5A00;margin-top:6px}
"""

PLAY = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hack ShopMate</title><style>""" + CSS + """</style></head><body>
<header><b>Hack ShopMate</b><span id="who"></span></header><main>
<div class="card" id="join"><b>Your goal:</b> trick ShopMate, an online shop's AI agent, into revealing its secret staff discount code.
Each level adds one real defence.<div class="row"><input id="name" placeholder="Your first name" maxlength="24">
<button class="go" onclick="join()">Play</button></div><div class="small" style="margin-top:8px">Class exercise. The codes are fake;
do not type anything personal.</div></div>
<div id="game" style="display:none">
<div class="tabs" id="tabs"></div>
<div class="card"><div class="def" id="def"></div><div class="hint" id="hint"></div></div>
<div class="card"><div id="log"></div>
<div class="row"><textarea id="msg" rows="2" placeholder="Message ShopMate..." maxlength="500"></textarea>
<button class="go" onclick="send()">Send</button></div>
<div class="row"><input id="guess" placeholder="I found the code: type it here"><button class="go win" onclick="check()">Check</button></div></div>
</div></main>
<script>
let L=[],cur=1,cleared=new Set(),pid=null,name="",hintI=0;
try{pid=localStorage.getItem('sm_pid');name=localStorage.getItem('sm_name')||'';cleared=new Set(JSON.parse(localStorage.getItem('sm_done')||'[]'))}catch(e){}
if(!pid){pid=Math.random().toString(36).slice(2,12);try{localStorage.setItem('sm_pid',pid)}catch(e){}}
const $=id=>document.getElementById(id);
function save(){try{localStorage.setItem('sm_name',name);localStorage.setItem('sm_done',JSON.stringify([...cleared]))}catch(e){}}
function add(cls,t){const d=document.createElement('div');d.className='m '+cls;d.textContent=t;$('log').appendChild(d);$('log').scrollTop=1e9}
async function boot(){L=await (await fetch('/api/levels')).json();if(name){$('name').value=name;join()}}
function join(){name=$('name').value.trim();if(!name)return;save();$('join').style.display='none';$('game').style.display='block';
 $('who').textContent=name;cur=Math.min(1+Math.max(0,...cleared),L.length);tabs();show()}
function tabs(){$('tabs').innerHTML='';L.forEach(l=>{const b=document.createElement('button');b.className='tab'+(l.n===cur?' on':'')+(cleared.has(l.n)?' done':'');
 b.textContent='L'+l.n;b.disabled=!(l.n===1||cleared.has(l.n-1));b.onclick=()=>{cur=l.n;tabs();show()};$('tabs').appendChild(b)})}
function show(){const l=L[cur-1];hintI=0;$('def').innerHTML='';const t=document.createElement('b');t.textContent='Level '+l.n+': '+l.name;$('def').appendChild(t);
 $('def').appendChild(document.createTextNode('. Defence: '+l.defence));$('hint').textContent='';$('log').innerHTML='';
 add('bot','Hi! I\\'m ShopMate. How can I help with your order today?');if(l.hints.length){const h=document.createElement('a');h.href='#';h.textContent='Need a hint?';
 h.onclick=e=>{e.preventDefault();$('hint').textContent='Hint: '+l.hints[Math.min(hintI++,l.hints.length-1)]};$('hint').appendChild(h)}}
async function send(){const m=$('msg').value.trim();if(!m)return;add('me',m);$('msg').value='';
 const r=await fetch('/api/chat',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({player:pid,name,level:cur,message:m})});
 const j=await r.json();if(!r.ok){add('blk',j.detail||'Error');return}
 if(j.blocked)add('blk',j.blocked);else add('bot',j.reply)}
async function check(){const g=$('guess').value.trim();if(!g)return;
 const r=await fetch('/api/guess',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({player:pid,level:cur,guess:g})});
 const j=await r.json();if(!r.ok){add('blk',j.detail||'Error');return}
 if(!j.ok){add('blk','Not the code. Keep trying.');return}
 cleared.add(cur);save();add('sys','Level '+cur+' cleared! Lesson: '+j.lesson);$('guess').value='';
 if(j.next){cur=j.next;setTimeout(()=>{tabs();show()},2600)}else{tabs();add('sys','You cleared every level that can be cleared.')}}
$('msg').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});boot();
</script></body></html>"""

BOARD = """<!doctype html><html><head><meta charset="utf-8"><title>Hack ShopMate: board</title><style>""" + CSS + """
body{background:#1F2328;color:#fff}main{max-width:1400px}.grid{display:grid;grid-template-columns:1.1fr 1fr;gap:20px}
.card{background:#2A3038;border-color:#3A424D}.bar{display:flex;align-items:center;gap:12px;margin:12px 0;font-size:22px}
.bar .l{width:260px}.bar .t{flex:1;height:30px;background:#3A424D;border-radius:8px;overflow:hidden}.bar .f{display:block;height:100%;background:#5FA37A;transition:width .6s}
.bar .c{width:60px;text-align:right;font-weight:700}h2{margin:4px 0 10px;font-size:22px;color:#E8C66A}
.crack{border-left:4px solid #E8C66A;padding:8px 12px;margin:10px 0;background:#232931;border-radius:6px;font-size:17px}
.crack q{display:block;color:#B8C0CC;font-size:15px;margin-top:4px}ol{font-size:22px;line-height:1.7}</style></head><body>
<header><b style="font-size:24px">Hack ShopMate</b><span id="meta" style="font-size:16px"></span></header><main><div class="grid">
<div><div class="card"><h2>Who cracked which level</h2><div id="bars"></div></div><div class="card"><h2>Top players</h2><ol id="top"></ol></div></div>
<div class="card"><h2>Latest cracks, and how</h2><div id="cracks"></div></div></div></main>
<script>
const names=['Just ask','Please don\\'t tell','The phrase detector','Output guard','The lock is in the code'];
async function tick(){try{const b=await (await fetch('/api/board')).json();
document.getElementById('meta').textContent=b.players+' players | model: '+b.model;
const mx=Math.max(1,b.players);const bars=document.getElementById('bars');bars.innerHTML='';
Object.entries(b.per_level).forEach(([n,c])=>{const d=document.createElement('div');d.className='bar';
d.innerHTML='<span class="l"></span><span class="t"><span class="f"></span></span><span class="c"></span>';
d.querySelector('.l').textContent='L'+n+' '+names[n-1];d.querySelector('.f').style.width=(100*c/mx)+'%';d.querySelector('.c').textContent=c;bars.appendChild(d)});
const top=document.getElementById('top');top.innerHTML='';b.top.forEach(p=>{const li=document.createElement('li');li.textContent=p.name+'  ('+p.cleared+' levels)';top.appendChild(li)});
const cr=document.getElementById('cracks');cr.innerHTML='';b.cracks.forEach(c=>{const d=document.createElement('div');d.className='crack';
d.textContent=c.name+' cleared L'+c.level;const q=document.createElement('q');q.textContent=c.how;d.appendChild(q);cr.appendChild(d)})}catch(e){}}
tick();setInterval(tick,3000);
</script></body></html>"""
