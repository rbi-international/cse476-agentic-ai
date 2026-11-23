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
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from game import agents
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
START = time.time()


def _empty_counters() -> dict:
    return {x.n: {"attempts": 0, "rejected": 0, "blocked": {}, "cracked": 0, "players": set()} for x in lv.LEVELS}


COUNTERS = _empty_counters()    # per level, for /api/export: counts and player ids only, never names or messages
COUNTING_SINCE = time.time()


def tally(n: int, field: str, pid: str = "", guard: str = ""):
    with LOCK:
        c = COUNTERS[n]
        if guard:
            c["blocked"][guard] = c["blocked"].get(guard, 0) + 1
        else:
            c[field] += 1
        if pid:
            c["players"].add(pid)


def reset_counters():
    global COUNTERS, COUNTING_SINCE
    with LOCK:
        COUNTERS, COUNTING_SINCE = _empty_counters(), time.time()


def _utc(t: float) -> str:
    return datetime.fromtimestamp(t, timezone.utc).isoformat(timespec="seconds")


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
    name: str = Field(default="", max_length=24)


def player(pid: str, name: str = "") -> dict:
    with LOCK:
        p = PLAYERS.setdefault(pid, {"name": name or "player", "cleared": set(), "last": {}, "t": 0.0, "state": {}})
        if name:
            p["name"] = name.strip()[:24]
        return p


def unlocked(p: dict, n: int) -> bool:
    need = lv.required(lv.BY_N[n])
    return need is None or need in p["cleared"]


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL.name}


@app.get("/api/levels")
def levels_info():
    return [{"n": x.n, "name": x.name, "defence": x.defence, "hints": x.hints, "mode": x.mode, "brief": x.brief,
             "needs": lv.required(x), "placeholder": x.placeholder, "extreme": x.n >= 6} for x in lv.LEVELS]


@app.post("/api/chat")
def chat(c: Chat):
    p = player(c.player, c.name)
    log("attempt", f"L{c.level}", player=p["name"], level=c.level)
    tally(c.level, "attempts", pid=c.player)
    if not unlocked(p, c.level):
        tally(c.level, "rejected")
        raise HTTPException(403, "Clear the previous level first.")
    now = time.time()
    if now - p["t"] < GAP:
        tally(c.level, "rejected")
        raise HTTPException(429, f"Slow down: one message every {GAP:.0f} seconds.")
    p["t"] = now
    level = lv.BY_N[c.level]
    p["last"][c.level] = c.message
    stopped = lv.blocked_input(level, c.message)
    if stopped:
        log("blocked", f"L{level.n} input detector", player=p["name"], level=level.n, guard="detector")
        tally(level.n, "blocked", guard="detector")
        return {"reply": "", "blocked": stopped, "by": "detector"}
    if level.mode != "chat":
        return agent_turn(p, level, c.message)
    text = lv.spotlight(c.message) if level.spotlight else c.message
    source = MODEL.name
    if not BUSY.acquire(timeout=20):
        tally(level.n, "rejected")
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
        log("blocked", f"L{level.n} output guard", player=p["name"], level=level.n, guard="output guard")
        tally(level.n, "blocked", guard="output guard")
        return {"reply": "", "blocked": stopped, "by": "output guard"}
    return {"reply": reply, "model": source}


def agent_turn(p: dict, level, message: str) -> dict:
    """Levels 6 to 9: several model calls, tools and agents; the player sees the trace."""
    state = p["state"].setdefault(level.n, {})
    source = MODEL.name
    if not BUSY.acquire(timeout=30):
        tally(level.n, "rejected")
        raise HTTPException(503, "ShopMate is busy with the whole class. Try again in a few seconds.")
    try:
        try:
            turn = agents.play(MODEL, level, message, state)
        except Exception as exc:  # never crash in class: replay the turn on the simulated model
            log("model_error", type(exc).__name__)
            if state.get("reviews"):
                state["reviews"].pop()
            turn, source = agents.play(FALLBACK, level, message, state), FALLBACK.name
    finally:
        BUSY.release()
    if turn.blocked:
        log("blocked", f"L{level.n} {turn.by}", player=p["name"], level=level.n, guard=turn.by)
        tally(level.n, "blocked", guard=turn.by)
    log("agent_turn", f"L{level.n} {len(turn.trace)} steps", player=p["name"])
    return {"reply": turn.reply, "blocked": turn.blocked, "by": turn.by, "trace": turn.trace,
            "server_log": turn.server_log, "model": source}


@app.post("/api/guess")
def guess(g: Guess):
    p = player(g.player, g.name)
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
    tally(g.level, "cracked")
    nxt = next((x.n for x in lv.LEVELS if lv.required(x) == g.level), None)
    return {"ok": True, "lesson": level.lesson, "next": nxt}


@app.get("/api/board")
def board():
    with LOCK:
        per_level = {x.n: sum(1 for p in PLAYERS.values() if x.n in p["cleared"]) for x in lv.LEVELS}
        top = sorted(PLAYERS.values(), key=lambda p: -len(p["cleared"]))[:12]
        return {"players": len(PLAYERS), "per_level": per_level, "model": MODEL.name,
                "top": [{"name": p["name"], "cleared": len(p["cleared"])} for p in top if p["cleared"]],
                "cracks": CRACKS[:8]}


def is_admin(request: Request) -> bool:
    token = os.environ.get("ADMIN_TOKEN")
    return bool(token) and request.headers.get("x-admin-token") == token


@app.get("/api/export")
def export(request: Request):
    """Counts for the course evaluation. No names and no message text: display names stay on /api/board."""
    if not is_admin(request):
        raise HTTPException(403, "Export needs ADMIN_TOKEN.")
    now = time.time()
    with LOCK:
        everyone = set().union(*(c["players"] for c in COUNTERS.values()))
        per = {}
        for n, c in COUNTERS.items():
            blocked = sum(c["blocked"].values())
            per[str(n)] = {"attempts": c["attempts"], "rejected": c["rejected"], "players": len(c["players"]),
                           "blocked_by_guard": dict(c["blocked"]), "blocked_total": blocked, "cracked": c["cracked"],
                           "players_cleared": sum(1 for p in PLAYERS.values() if n in p["cleared"]),
                           "bypass_rate": round((c["attempts"] - blocked) / c["attempts"], 4) if c["attempts"] else None}
        since = COUNTING_SINCE
    return {"exported_at": _utc(now), "model": MODEL.name, "uptime_seconds": int(now - START),
            "counting_since": _utc(since), "players": len(everyone), "levels": per}


@app.post("/api/reset")
def reset(request: Request):
    if not is_admin(request):
        raise HTTPException(403, "Reset needs ADMIN_TOKEN.")
    with LOCK:
        PLAYERS.clear()
        CRACKS.clear()
    reset_counters()
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
.sys{background:#DCEFE3;color:#245C39;font-weight:600}
.tr{font:12.5px/1.4 ui-monospace,Consolas,monospace;background:#F3F1EC;border-left:3px solid #9AA3AE;margin:4px 40px 4px 10px;padding:6px 9px;border-radius:6px}
.tr.call{border-color:#6A55A8}.tr.tool{border-color:#2E8B57}.tr.code{border-color:#C2456A;background:#FBE9EC;font-weight:700}.tr.victim{border-color:#C98A12}
.tr b{font-weight:700}.srv{background:#11151A;color:#7FD1A8;font-family:ui-monospace,Consolas,monospace;font-size:13px;margin-right:40px}
.brief{font-size:14px;margin-top:8px;padding:9px 11px;background:#FBF1D3;border-radius:8px;border:1px solid #E5D3A0}
.tab.x{border-color:#C2456A;color:#C2456A}.tab.x.on{background:#C2456A;color:#fff}.row{display:flex;gap:8px;margin-top:8px}
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
function step(s){const d=document.createElement('div');d.className='tr '+s.kind;const b=document.createElement('b');b.textContent=s.who+': ';
 d.appendChild(b);d.appendChild(document.createTextNode(s.text));$('log').appendChild(d);$('log').scrollTop=1e9}
const open_=l=>l.needs===null||cleared.has(l.needs);
async function boot(){L=await (await fetch('/api/levels')).json();if(name){$('name').value=name;join()}}
function join(){name=$('name').value.trim();if(!name)return;save();$('join').style.display='none';$('game').style.display='block';
 $('who').textContent=name;cur=Math.max(1,...L.filter(open_).map(l=>l.n));tabs();show()}
function tabs(){$('tabs').innerHTML='';L.forEach(l=>{const b=document.createElement('button');b.className='tab'+(l.extreme?' x':'')+(l.n===cur?' on':'')+(cleared.has(l.n)?' done':'');
 b.textContent='L'+l.n;b.disabled=!open_(l);b.onclick=()=>{cur=l.n;tabs();show()};$('tabs').appendChild(b)})}
function show(){const l=L[cur-1];hintI=0;$('def').innerHTML='';const t=document.createElement('b');t.textContent='Level '+l.n+': '+l.name;$('def').appendChild(t);
 $('def').appendChild(document.createTextNode('. Defence: '+l.defence));$('hint').textContent='';$('log').innerHTML='';
 if(l.brief){const d=document.createElement('div');d.className='brief';d.textContent=(l.extreme?'EXTREME. ':'')+l.brief;$('def').appendChild(d)}
 $('msg').placeholder=l.placeholder;
 if(l.mode!=='rag')add('bot',l.mode==='chat'?'Hi! I\\'m ShopMate. How can I help with your order today?':'Hi Asha! I\\'m ShopMate. I can check orders, refunds and billing.');if(l.hints.length){const h=document.createElement('a');h.href='#';h.textContent='Need a hint?';
 h.onclick=e=>{e.preventDefault();$('hint').textContent='Hint: '+l.hints[Math.min(hintI++,l.hints.length-1)]};$('hint').appendChild(h)}}
async function send(){const m=$('msg').value.trim();if(!m)return;add('me',m);$('msg').value='';
 const r=await fetch('/api/chat',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({player:pid,name,level:cur,message:m})});
 const j=await r.json();if(!r.ok){add('blk',j.detail||'Error');return}
 $('who').textContent=name+((j.model||'').includes('simulated')?'  ·  OFFLINE MODE':'');(j.trace||[]).forEach(step);if(j.blocked)add('blk',j.blocked);else if(j.server_log&&j.server_log.length)add('srv',j.reply);else add('bot',j.reply)}
async function check(){const g=$('guess').value.trim();if(!g)return;
 const r=await fetch('/api/guess',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({player:pid,name,level:cur,guess:g})});
 const j=await r.json();if(!r.ok){add('blk',j.detail||'Error');return}
 if(!j.ok){add('blk','Not the code. Keep trying.');return}
 cleared.add(cur);save();add('sys','Level '+cur+' cleared! Lesson: '+j.lesson);$('guess').value='';
 if(j.next===5)add('sys','Level 5 cannot be won by anyone. Try it, then jump to L6: the extreme levels are open.');if(j.next){cur=j.next;setTimeout(()=>{tabs();show()},2600)}else{tabs();add('sys','You cleared every level that can be cleared.')}}
$('msg').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});boot();
</script></body></html>"""

BOARD = """<!doctype html><html><head><meta charset="utf-8"><title>Hack ShopMate: board</title><style>""" + CSS + """
body{background:#1F2328;color:#fff}main{max-width:1400px}.grid{display:grid;grid-template-columns:1.1fr 1fr;gap:20px}
.card{background:#2A3038;border-color:#3A424D}.bar{display:flex;align-items:center;gap:12px;margin:8px 0;font-size:20px}
.bar .l{width:280px}.bar .t{flex:1;height:30px;background:#3A424D;border-radius:8px;overflow:hidden}.bar .f{display:block;height:100%;background:#5FA37A;transition:width .6s}
.bar .c{width:60px;text-align:right;font-weight:700}h2{margin:4px 0 10px;font-size:22px;color:#E8C66A}
.crack{border-left:4px solid #E8C66A;padding:8px 12px;margin:10px 0;background:#232931;border-radius:6px;font-size:17px}
.crack q{display:block;color:#B8C0CC;font-size:15px;margin-top:4px}ol{font-size:22px;line-height:1.7}</style></head><body>
<header><b style="font-size:24px">Hack ShopMate</b><span id="meta" style="font-size:16px"></span></header><main><div class="grid">
<div><div class="card"><h2>Who cracked which level</h2><div id="bars"></div></div><div class="card"><h2>Top players</h2><ol id="top"></ol></div></div>
<div class="card"><h2>Latest cracks, and how</h2><div id="cracks"></div></div></div></main>
<script>
let names={};
async function tick(){try{if(!Object.keys(names).length)(await (await fetch('/api/levels')).json()).forEach(l=>names[l.n]=l.name);const b=await (await fetch('/api/board')).json();
document.getElementById('meta').textContent=b.players+' players | model: '+b.model;
const mx=Math.max(1,b.players);const bars=document.getElementById('bars');bars.innerHTML='';
Object.entries(b.per_level).forEach(([n,c])=>{const d=document.createElement('div');d.className='bar';
d.innerHTML='<span class="l"></span><span class="t"><span class="f"></span></span><span class="c"></span>';
d.querySelector('.l').textContent='L'+n+' '+(names[n]||'');d.querySelector('.f').style.width=(100*c/mx)+'%';d.querySelector('.c').textContent=c;bars.appendChild(d)});
const top=document.getElementById('top');top.innerHTML='';b.top.forEach(p=>{const li=document.createElement('li');li.textContent=p.name+'  ('+p.cleared+' levels)';top.appendChild(li)});
const cr=document.getElementById('cracks');cr.innerHTML='';b.cracks.forEach(c=>{const d=document.createElement('div');d.className='crack';
d.textContent=c.name+' cleared L'+c.level;const q=document.createElement('q');q.textContent=c.how;d.appendChild(q);cr.appendChild(d)})}catch(e){}}
tick();setInterval(tick,3000);
</script></body></html>"""
