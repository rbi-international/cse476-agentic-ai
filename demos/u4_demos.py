"""Companion demos for the Unit IV slides. Every number on the slides comes from here."""
import asyncio, sys, time, json
sys.path.insert(0, "src")  # run from the repository root
from agent_framework import WorkflowBuilder, WorkflowContext, executor

# 1. sequential vs concurrent, three "LLM calls" of 1.2 s, 0.8 s, 1.5 s
async def fake_llm(name, secs):
    await asyncio.sleep(secs)
    return name
async def seq():
    t=time.perf_counter()
    for n,s in [("security",1.2),("priority",0.8),("sentiment",1.5)]:
        await fake_llm(n,s)
    return time.perf_counter()-t
async def conc():
    t=time.perf_counter()
    await asyncio.gather(fake_llm("security",1.2),fake_llm("priority",0.8),fake_llm("sentiment",1.5))
    return time.perf_counter()-t
print("DEMO1 sequential %.2f s" % asyncio.run(seq()))
print("DEMO1 concurrent %.2f s" % asyncio.run(conc()))

# 2. fan-in barrier: order of events
order=[]
@executor(id="start")
async def start(x: str, ctx: WorkflowContext[str]) -> None:
    order.append("start"); await ctx.send_message(x)
@executor(id="fast")
async def fast(x: str, ctx: WorkflowContext[str]) -> None:
    order.append("fast done"); await ctx.send_message("fast")
@executor(id="slow")
async def slow(x: str, ctx: WorkflowContext[str]) -> None:
    await asyncio.sleep(0.3); order.append("slow done"); await ctx.send_message("slow")
@executor(id="join")
async def join(r: list[str], ctx: WorkflowContext) -> None:
    order.append("join ran with %d results" % len(r)); await ctx.yield_output(sorted(r))
wf=(WorkflowBuilder(start_executor=start).add_fan_out_edges(start,[fast,slow]).add_fan_in_edges([fast,slow],join).build())
out=asyncio.run(wf.run("go")).get_outputs()
print("DEMO2 order", order, "output", out)

# 3. the overwrite bug: an agent writes without reading first
@executor(id="intake")
async def intake(t: str, ctx: WorkflowContext[str]) -> None:
    ctx.set_state("findings", []); await ctx.send_message(t)
@executor(id="security")
async def security(t: str, ctx: WorkflowContext[str]) -> None:
    ctx.set_state("findings", ctx.get_state("findings") + ["security: RISK"]); await ctx.send_message(t)
@executor(id="careless_priority")
async def careless_priority(t: str, ctx: WorkflowContext[str]) -> None:
    ctx.set_state("findings", ["priority: HIGH"]); await ctx.send_message(t)   # forgot to read
@executor(id="summary")
async def summary(t: str, ctx: WorkflowContext) -> None:
    await ctx.yield_output(ctx.get_state("findings"))
bad=(WorkflowBuilder(start_executor=intake).add_edge(intake,security).add_edge(security,careless_priority).add_edge(careless_priority,summary).build())
print("DEMO3 board after careless agent", asyncio.run(bad.run("hack attempt, urgent")).get_outputs())

# 4. the manager's tools, exactly what the model is shown
from agent_framework.openai import OpenAIChatClient
from cse476.manager import build_specialists, specialist_tools
c=OpenAIChatClient(model="x", api_key="dummy", base_url="http://localhost:1")
tools=specialist_tools(build_specialists(c))
for t in tools:
    print("DEMO4 tool", getattr(t,"name",None), "|", getattr(t,"description",None))

# 5. token cost of fan-out: 1 ticket of 400 tokens, 3 reviewers, each with 300-token instruction, 80-token answer
inp=400; ins=300; ans=80
single = inp+ins+ans
multi = 3*(inp+ins+ans) + (3*ans+200+60)   # + combiner reading three answers
print("DEMO5 single agent tokens", single, "| fan-out of 3 + combiner", multi, "| ratio %.1fx" % (multi/single))
