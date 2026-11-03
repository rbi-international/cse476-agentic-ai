"""
Class questions on the live service: students scan a QR code, tap an answer, and the
projector shows the votes as they arrive.

    GET  /q/{n}           the question on a phone, four big buttons
    POST /q/{n}/vote      one vote: {"choice": 0..3}
    GET  /q/{n}/counts    the votes as JSON
    GET  /q/{n}/results   the projector view, refreshing every second

The questions live in quiz_questions.json, the same file the slides are built from, so
the slide and the phone always show the same words. Votes are kept in memory, like the
dashboard counts: a restart clears them.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

QUESTIONS = {q["id"]: q for q in json.loads((Path(__file__).parent / "quiz_questions.json").read_text())}


class Vote(BaseModel):
    """One tap on a phone."""

    choice: int = Field(ge=0, le=3)


def _question(n: int) -> dict:
    if n not in QUESTIONS:
        raise HTTPException(status_code=404, detail="no such question")
    return QUESTIONS[n]


def add_quiz(app: FastAPI) -> None:
    """Add the four question routes to an existing app."""
    votes = {n: [0, 0, 0, 0] for n in QUESTIONS}

    @app.post("/q/{n}/vote")
    def vote(n: int, body: Vote) -> dict:
        _question(n)
        votes[n][body.choice] += 1
        return {"ok": True}

    @app.get("/q/{n}/counts")
    def counts(n: int) -> dict:
        q = _question(n)
        return {"question": q["question"], "options": q["options"], "counts": votes[n], "total": sum(votes[n])}

    @app.get("/q/{n}", response_class=HTMLResponse)
    def phone(n: int) -> str:
        _question(n)
        return PHONE_HTML.replace("__N__", str(n))

    @app.get("/q/{n}/results", response_class=HTMLResponse)
    def results(n: int) -> str:
        _question(n)
        return RESULTS_HTML.replace("__N__", str(n))


PHONE_HTML = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Question __N__</title>
<style>
body{font-family:system-ui,sans-serif;background:#F6F1E7;color:#141414;margin:0;padding:20px}
h1{font-size:15px;color:#2F5D8C;margin:4px 0}p#q{font-size:20px;font-weight:700;margin:6px 0 18px}
button{display:block;width:100%;text-align:left;margin:10px 0;padding:16px;font-size:17px;border:1px solid #8A8A8A;
border-radius:12px;background:#fff}button b{color:#2F5D8C;margin-right:10px}
#done{display:none;margin-top:18px;padding:16px;border-radius:12px;background:#DDF2E6;font-size:18px;font-weight:700}
</style></head><body><h1 id="t"></h1><p id="q"></p><div id="opts"></div>
<div id="done">Vote counted. Look at the projector.</div>
<script>
const n=__N__,key='voted_'+n;
async function load(){
  const d=await (await fetch('/q/'+n+'/counts')).json();
  document.getElementById('q').textContent=d.question;
  document.getElementById('t').textContent='Question '+n;
  let seen=false;try{seen=localStorage.getItem(key)}catch(e){}
  if(seen){document.getElementById('done').style.display='block';return;}
  document.getElementById('opts').innerHTML=d.options.map((o,i)=>
    '<button onclick="vote('+i+')"><b>'+'ABCD'[i]+'</b>'+o.replace(/</g,'&lt;')+'</button>').join('');
}
async function vote(i){
  document.getElementById('opts').innerHTML='';
  await fetch('/q/'+n+'/vote',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({choice:i})});
  try{localStorage.setItem(key,'1')}catch(e){}
  document.getElementById('done').style.display='block';
}
load();
</script></body></html>"""

RESULTS_HTML = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Results __N__</title>
<style>
body{font-family:system-ui,sans-serif;background:#F6F1E7;color:#141414;margin:0;padding:32px}
p#q{font-size:30px;font-weight:700;margin:0 0 26px}
.r{display:flex;align-items:center;margin:16px 0;font-size:24px}.l{width:46%;padding-right:16px}
.b{height:46px;border-radius:8px;background:#2F5D8C;transition:width .5s}.c{margin-left:14px;font-weight:700}
#tot{color:#555;font-size:22px;margin-top:22px}
</style></head><body><p id="q"></p><div id="rows"></div><div id="tot"></div>
<script>
const n=__N__;
async function tick(){
  const d=await (await fetch('/q/'+n+'/counts')).json();
  document.getElementById('q').textContent=d.question;
  const max=Math.max(1,...d.counts);
  document.getElementById('rows').innerHTML=d.options.map((o,i)=>'<div class="r"><div class="l"><b>'+'ABCD'[i]+'.</b> '+
    o.replace(/</g,'&lt;')+'</div><div class="b" style="width:'+(d.counts[i]/max*40)+'%"></div><div class="c">'+d.counts[i]+'</div></div>').join('');
  document.getElementById('tot').textContent=d.total+' votes';
}
tick();setInterval(tick,1000);
</script></body></html>"""
