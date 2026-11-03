"""
The live service: the triage agent, served to a whole classroom at once.

Unit 5 finale. Every lecture of the unit, inside one running app that students
reach from their own phones:

    testing        tests/test_live.py drives every route offline with TestClient
    validation     the team is checked against the menu before it is counted
    observability  every ticket is traced and timed, and writes one log line
    serving        the same make_app() API (/health, /triage), plus a phone form
    deployment     the Dockerfile starts this app, and CI ships it on a green push

    make_live_app   build the app
    LiveStats       what the dashboard shows: counts per team, escalations, latency

Nothing here changes the agent. triage() in serving.py is still the whole brain;
this module only wraps it, exactly like make_app() does.
"""

from __future__ import annotations

import json
import time
import uuid
from collections import Counter
from dataclasses import dataclass, field

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from cse476.observability import Metrics, Trace, log_line
from cse476.quiz import add_quiz
from cse476.serving import TEAMS, make_app, triage
from cse476.validation import validate_choice

# ---------------------------------------------------------------- the contract

# WHY limits on the text: the service is public. A 3-character minimum rejects
# empty taps, and a 300-character maximum stops anyone pasting an essay at it.
# FastAPI turns a violation into a 422 before the agent runs.


class LiveTicket(BaseModel):
    """What the phone form sends: one short ticket."""

    text: str = Field(min_length=3, max_length=300)


# ---------------------------------------------------------------- the dashboard numbers

@dataclass
class LiveStats:
    """
    The numbers the projector shows, kept in memory.

    In memory on purpose, to keep the demo to one file. The cost is real and worth
    saying out loud: a restart wipes the counts, and two copies of the service
    would each count only their own tickets. A production service keeps this in a
    shared store (a database or Redis), as the scaling slides explain.
    """

    teams: Counter = field(default_factory=Counter)
    escalations: int = 0
    off_menu: int = 0
    metrics: Metrics = field(default_factory=Metrics)

    def snapshot(self) -> dict:
        return {
            "total": self.metrics.runs,
            "teams": dict(self.teams),
            "escalations": self.escalations,
            "off_menu": self.off_menu,
            "average_ms": self.metrics.average_ms(),
        }


# ---------------------------------------------------------------- the app

def make_live_app() -> FastAPI:
    """
    Build the classroom service: the L4 API plus a phone form and a dashboard.

      GET  /           the phone form students open from the QR code
      POST /ticket     runs the agent on one ticket, validates, traces, logs, counts
      GET  /dashboard  the projector view, refreshing every two seconds
      GET  /stats      the dashboard's numbers as JSON
      GET  /health and POST /triage come unchanged from make_app()
      GET  /q/{n} and /q/{n}/results  the class questions (quiz.py)
    """
    app = make_app()
    stats = LiveStats()

    @app.post("/ticket")
    def ticket(request: LiveTicket) -> dict:
        trace = Trace()

        start = time.perf_counter()
        result = triage(request.text)  # the agent, unchanged
        trace.record("triage", round((time.perf_counter() - start) * 1000, 3))

        start = time.perf_counter()
        team = validate_choice(result["team"], set(TEAMS))  # validation: on the menu?
        trace.record("validate", round((time.perf_counter() - start) * 1000, 3))

        outcome = "ok" if team else "off_menu"
        if team is None:
            stats.off_menu += 1
            team = "general"  # the safe default, as in decide_route
        stats.teams[team] += 1
        stats.escalations += result["escalate"]
        stats.metrics.observe(trace, failed=outcome != "ok")

        # observability: one structured line per ticket. The ticket text is never
        # logged, because students type real complaints into a public service.
        record = log_line(uuid.uuid4().hex[:8], trace, outcome)
        record["team"] = team
        print(json.dumps(record), flush=True)

        return {"team": team, "escalate": result["escalate"], "ms": trace.total_ms()}

    @app.get("/stats")
    def get_stats() -> dict:
        return stats.snapshot()

    @app.get("/", response_class=HTMLResponse)
    def form() -> str:
        return FORM_HTML

    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard() -> str:
        return DASHBOARD_HTML

    add_quiz(app)  # the class questions: GET /q/{n} on phones, /q/{n}/results on the projector
    return app


# ---------------------------------------------------------------- the two pages

FORM_HTML = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Helpdesk triage</title>
<style>
body{font-family:system-ui,sans-serif;background:#F6F1E7;color:#141414;margin:0;padding:20px}
h1{font-size:24px;margin:8px 0 4px}p{color:#555;margin:0 0 16px}
textarea{width:100%;box-sizing:border-box;height:120px;font-size:17px;padding:12px;
border:1px solid #8A8A8A;border-radius:12px}
button{margin-top:12px;width:100%;padding:14px;font-size:18px;font-weight:700;border:0;
border-radius:12px;background:#2F5D8C;color:#fff}
#out{margin-top:18px;padding:16px;border-radius:12px;font-size:20px;font-weight:700;display:none}
</style></head><body>
<h1>Helpdesk triage</h1>
<p>Type a hostel, fee or UMS problem. The agent picks the team.</p>
<textarea id="t" maxlength="300" placeholder="I paid the hostel fee twice, please refund"></textarea>
<button onclick="send()">Send ticket</button>
<div id="out"></div>
<script>
async function send(){
  const out=document.getElementById('out');
  const r=await fetch('/ticket',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({text:document.getElementById('t').value})});
  out.style.display='block';
  if(!r.ok){out.style.background='#F9E0E3';out.textContent='Rejected ('+r.status+'): 3 to 300 characters please';return;}
  const d=await r.json();
  out.style.background=d.escalate?'#F9E0E3':'#DDF2E6';
  out.textContent='Team: '+d.team.toUpperCase()+(d.escalate?'  |  ESCALATED':'')+'  ('+d.ms+' ms)';
}
</script></body></html>"""

DASHBOARD_HTML = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Live triage dashboard</title>
<style>
body{font-family:system-ui,sans-serif;background:#F6F1E7;color:#141414;margin:0;padding:28px}
h1{margin:0 0 18px;font-size:30px}.row{display:flex;gap:16px;margin-bottom:22px}
.card{flex:1;background:#fff;border:1px solid #8A8A8A;border-radius:14px;padding:16px}
.card b{display:block;font-size:44px}.card span{color:#555}
.bar{display:flex;align-items:center;margin:10px 0;font-size:20px}
.bar div.l{width:140px;font-weight:700}.bar div.b{height:34px;border-radius:8px;background:#2F5D8C;
transition:width .4s}.bar div.n{margin-left:12px;font-weight:700}
</style></head><body>
<h1>Live triage dashboard</h1>
<div class="row">
<div class="card"><b id="total">0</b><span>tickets</span></div>
<div class="card"><b id="esc">0</b><span>escalated</span></div>
<div class="card"><b id="off">0</b><span>off-menu teams caught</span></div>
<div class="card"><b id="ms">0</b><span>average ms</span></div>
</div>
<div id="bars"></div>
<script>
async function tick(){
  const d=await (await fetch('/stats')).json();
  total.textContent=d.total;esc.textContent=d.escalations;off.textContent=d.off_menu;ms.textContent=d.average_ms;
  const max=Math.max(1,...Object.values(d.teams));
  bars.innerHTML=Object.entries(d.teams).sort((a,b)=>b[1]-a[1]).map(([k,v])=>
    '<div class="bar"><div class="l">'+k+'</div><div class="b" style="width:'+(v/max*60)+'%"></div><div class="n">'+v+'</div></div>').join('');
}
tick();setInterval(tick,2000);
</script></body></html>"""
