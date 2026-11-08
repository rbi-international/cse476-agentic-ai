"""
The crew's web page: pick a pull request, press Run, watch every agent work live.

    GET  /                  the page
    GET  /api/samples       the sample pull requests
    POST /api/run           start a review: {"sample": "02_hardcoded_key"} or {"diff": "..."}
    GET  /api/events/{id}   the run's events as a live stream (server-sent events)
    GET  /health            for the cloud's health check

Run locally:  uvicorn crew.web:app --port 8080   (from the pr_review_crew folder)
"""

from __future__ import annotations

import asyncio
import json
import threading
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field

from crew import crew
from crew.llm import from_env
from crew.trace import Trace

HERE = Path(__file__).resolve().parent.parent
SAMPLES = {
    "01_hostel_route": ("Add a hostel team", "Routes hostel tickets to a new team, but forgets the list of allowed teams."),
    "02_hardcoded_key": ("Quick config change", "Pastes an API key straight into the code \"just for testing\"."),
    "03_prompt_injection": ("Ticket priority score", "Adds a feature, hides a message for AI reviewers, and uses eval()."),
    "04_docs_drift": ("Language option", "Adds a parameter to triage() without updating its docstring."),
    "05_clean_fix": ("Bill keyword fix", "A small fix with a new test. What does a good pull request look like?"),
}
RUNS: dict[str, dict] = {}
MAX_RUNS = 50


class RunRequest(BaseModel):
    sample: str | None = None
    diff: str | None = Field(default=None, max_length=60_000)


app = FastAPI(title="PR Review Crew")


@app.get("/health")
def health() -> dict:
    llm = from_env()
    return {"status": "ok", "model": llm.model if llm else "offline"}


@app.get("/api/samples")
def samples() -> list[dict]:
    return [{"id": k, "title": t, "about": a, "diff": (HERE / "samples" / f"{k}.diff").read_text()}
            for k, (t, a) in SAMPLES.items()]


@app.post("/api/run")
def start(req: RunRequest) -> dict:
    if req.sample:
        if req.sample not in SAMPLES:
            raise HTTPException(404, "no such sample")
        diff = (HERE / "samples" / f"{req.sample}.diff").read_text()
    elif req.diff and req.diff.strip():
        diff = req.diff
    else:
        raise HTTPException(422, "send a sample name or a diff")
    state = {"events": [], "done": False}
    trace = Trace(on_event=lambda e: state["events"].append(asdict(e)))
    if len(RUNS) >= MAX_RUNS:  # keep memory bounded on a small container
        RUNS.pop(next(iter(RUNS)))
    RUNS[trace.run] = state

    def work():
        try:
            result = crew.run(diff, HERE / "demo_repo", from_env(), trace, apply_diff=True)
            state["review"] = crew.markdown(result)
            state["comments"] = crew.inline_comments(result)
        except Exception as exc:
            trace.emit("crew", "error", str(exc)[:300])
        finally:
            state["done"] = True

    threading.Thread(target=work, daemon=True).start()
    return {"run": trace.run}


@app.get("/api/events/{run}")
async def events(run: str):
    if run not in RUNS:
        raise HTTPException(404, "no such run")

    async def stream():
        sent = 0
        state = RUNS[run]
        while True:
            evs = state["events"]
            while sent < len(evs):
                yield f"data: {json.dumps(evs[sent])}\n\n"
                sent += 1
            if state["done"] and sent >= len(state["events"]):
                yield "event: review\ndata: " + json.dumps({"review": state.get("review", ""),
                                                           "comments": state.get("comments", [])}) + "\n\n"
                return
            await asyncio.sleep(0.15)

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/", response_class=HTMLResponse)
def page() -> str:
    return PAGE


PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>PR Review Crew</title>
<style>
:root{--bg:#F6F1E7;--ink:#141414;--sub:#5B5B5B;--line:#D8D1C2;--card:#fff;--blue:#2F5D8C;--green:#2E7D4F;--amber:#B7791F;--rose:#B23A48;--lav:#6B5B95}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:var(--bg);color:var(--ink)}
header{display:flex;align-items:center;gap:16px;padding:14px 22px;border-bottom:1px solid var(--line);background:#fff}
header h1{font-size:20px;margin:0}header .mode{font-size:13px;color:var(--sub)}header .clock{margin-left:auto;font:600 15px ui-monospace,Consolas,monospace}
main{display:grid;grid-template-columns:300px 1fr;gap:18px;padding:18px 22px}
.side h2,.board h2{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--sub);margin:0 0 10px}
.sample{background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin-bottom:8px;cursor:pointer}
.sample:hover,.sample.on{border-color:var(--blue);box-shadow:0 0 0 3px rgba(47,93,140,.12)}
.sample b{display:block;font-size:14px}.sample span{font-size:12.5px;color:var(--sub)}
button{width:100%;padding:11px;border:0;border-radius:10px;background:var(--blue);color:#fff;font-weight:700;font-size:15px;cursor:pointer;margin-top:6px}
button:disabled{opacity:.5;cursor:default}
pre.diff{background:#1E1E1E;color:#DDD;border-radius:10px;padding:10px;font-size:11.5px;max-height:260px;overflow:auto;margin-top:12px}
pre.diff .a{color:#7EE787}pre.diff .r{color:#FF7B72}
.row{display:grid;gap:12px;margin-bottom:12px}.four{grid-template-columns:repeat(4,1fr)}.two{grid-template-columns:1fr 1fr}
.lane{background:#fff;border:1px solid var(--line);border-radius:12px;padding:10px;min-height:96px}
.lane h3{margin:0 0 6px;font-size:14px;display:flex;align-items:center;gap:8px}
.dot{width:10px;height:10px;border-radius:50%;background:#C9C2B3}.lane.work .dot{background:var(--amber);animation:p 1s infinite}.lane.done .dot{background:var(--green)}
@keyframes p{50%{opacity:.3}}
.ev{font-size:12.5px;border-left:3px solid var(--line);padding:4px 8px;margin:5px 0;background:#FBFAF7;border-radius:0 6px 6px 0;animation:in .35s ease}
@keyframes in{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.ev small{color:var(--sub);font-family:ui-monospace,Consolas,monospace}.ev.tool{border-color:var(--blue)}.ev.llm{border-color:var(--lav)}
.ev.finding{border-color:var(--amber)}.ev.high{border-color:var(--rose);background:#FDF0F2}.ev.verdict{border-color:var(--green);font-weight:700}
.ev.fix{border-color:var(--green)}.ev.error{border-color:var(--rose)}
.review{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px;font-size:13.5px;line-height:1.45}.review h3{margin:0 0 8px}.review table{border-collapse:collapse;margin:8px 0}.review td,.review th{border:1px solid var(--line);padding:5px 9px;text-align:left}.review th{background:#F3EEE3}.review pre{background:#1E1E1E;color:#DDD;padding:8px;border-radius:8px;font-size:12px;white-space:pre-wrap}.review code{background:#F3EEE3;padding:1px 4px;border-radius:4px}
.legend{font-size:12px;color:var(--sub);margin:-4px 0 10px}.legend i{display:inline-block;width:10px;height:3px;margin:0 4px 2px 10px}
</style></head><body>
<header><h1>PR Review Crew</h1><span class="mode" id="mode"></span><span class="clock" id="clock">0.0 s</span></header>
<main><section class="side"><h2>1. Pick a pull request</h2><div id="samples"></div>
<button id="run" disabled>2. Run the crew</button><pre class="diff" id="diff"></pre></section>
<section class="board"><h2>3. Watch the crew work</h2>
<div class="legend"><i style="background:#2F5D8C"></i>tool <i style="background:#6B5B95"></i>model call <i style="background:#B7791F"></i>finding <i style="background:#B23A48"></i>high severity <i style="background:#2E7D4F"></i>verdict or fix</div>
<div class="row"><div class="lane" id="lead"><h3><span class="dot"></span>Lead: reads the change, picks the team</h3></div></div>
<div class="row four">
<div class="lane" id="tests"><h3><span class="dot"></span>Tests agent</h3></div>
<div class="lane" id="security"><h3><span class="dot"></span>Security agent</h3></div>
<div class="lane" id="quality"><h3><span class="dot"></span>Quality agent</h3></div>
<div class="lane" id="docs"><h3><span class="dot"></span>Docs agent</h3></div></div>
<div class="row two"><div class="lane" id="judge"><h3><span class="dot"></span>Judge: merges, drops weak findings, decides</h3></div>
<div class="lane" id="fixer"><h3><span class="dot"></span>Fix agent: proposes fixes, keeps only those that pass the tests</h3></div></div>
<h2>4. The review posted on the pull request</h2><div class="review" id="review">The judge's review appears here.</div>
</section></main>
<script>
let pick=null, timer=null, t0=0;
const $=id=>document.getElementById(id);
fetch('/health').then(r=>r.json()).then(h=>{$('mode').textContent='model: '+h.model});
fetch('/api/samples').then(r=>r.json()).then(list=>{
  $('samples').innerHTML=list.map(s=>`<div class="sample" data-id="${s.id}"><b>${s.title}</b><span>${s.about}</span></div>`).join('');
  document.querySelectorAll('.sample').forEach(el=>el.onclick=()=>{
    document.querySelectorAll('.sample').forEach(x=>x.classList.remove('on')); el.classList.add('on'); pick=el.dataset.id; $('run').disabled=false;
    const d=list.find(s=>s.id===pick).diff;
    $('diff').innerHTML=d.split('\n').map(l=>{const e=l.replace(/&/g,'&amp;').replace(/</g,'&lt;');
      return l.startsWith('+')&&!l.startsWith('+++')?`<span class="a">${e}</span>`:l.startsWith('-')&&!l.startsWith('---')?`<span class="r">${e}</span>`:e}).join('\n');
  });
});
function md(t){const esc=x=>x.replace(/&/g,'&amp;').replace(/</g,'&lt;');let h='',inCode=false,rows=[];
  const flush=()=>{if(rows.length){h+='<table>'+rows.filter(r=>!/^\|[-| ]+\|$/.test(r)).map((r,i)=>'<tr>'+r.slice(1,-1).split('|').map(c=>(i?'<td>':'<th>')+inl(c.trim())+(i?'</td>':'</th>')).join('')+'</tr>').join('')+'</table>';rows=[]}};
  const inl=x=>esc(x).replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*\*([^*]+)\*\*/g,'<b>$1</b>').replace(/^_(.*)_$/,'<i>$1</i>');
  for(const l of t.split('\n')){if(l.startsWith('```')){flush();h+=inCode?'</pre>':'<pre>';inCode=!inCode;continue}
    if(inCode){h+=esc(l)+'\n';continue} if(l.startsWith('|')){rows.push(l);continue} flush();
    if(l.startsWith('## '))h+='<h3>'+inl(l.slice(3))+'</h3>';else if(l.trim())h+='<p>'+inl(l)+'</p>';}
  flush();return h}
function reset(){['lead','tests','security','quality','docs','judge','fixer'].forEach(id=>{const l=$(id);l.className='lane';l.querySelectorAll('.ev').forEach(e=>e.remove())});$('review').textContent='The crew is working...'}
$('run').onclick=async()=>{
  reset(); $('run').disabled=true; t0=performance.now(); clearInterval(timer);
  timer=setInterval(()=>$('clock').textContent=((performance.now()-t0)/1000).toFixed(1)+' s',100);
  const r=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sample:pick})});
  const {run}=await r.json(); const es=new EventSource('/api/events/'+run);
  es.onmessage=m=>{const e=JSON.parse(m.data); const lane=$(e.agent==='crew'?'lead':e.agent); if(!lane) return;
    if(e.kind==='start') lane.className='lane work';
    if(['verdict','done'].includes(e.kind)||(e.kind==='finding')||(e.kind==='fix')) {}
    const high=e.kind==='finding'&&e.text.startsWith('[high]');
    const div=document.createElement('div'); div.className='ev '+e.kind+(high?' high':'');
    const meta=[e.t.toFixed(2)+' s', e.ms?Math.round(e.ms)+' ms':'', e.tokens?e.tokens+' tokens':''].filter(Boolean).join(' | ');
    div.innerHTML=`${e.text.replace(/</g,'&lt;')}<br><small>${e.kind} | ${meta}</small>`; lane.appendChild(div);
    if(['finding','verdict','fix'].includes(e.kind) && e.agent!=='fixer' || (e.agent==='fixer'&&e.kind==='fix')) lane.className='lane done';
  };
  es.addEventListener('review',m=>{const d=JSON.parse(m.data); $('review').innerHTML=md(d.review); es.close(); clearInterval(timer);
    document.querySelectorAll('.lane.work').forEach(l=>l.className='lane done'); $('run').disabled=false;});
};
</script></body></html>"""
