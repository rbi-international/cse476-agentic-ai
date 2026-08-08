"""
Prove the three pillars of observability, offline and deterministically: a timed
trace of one run, metrics aggregated across runs, and a structured log line. The
timing is injected, so the trace is real but the tests never flake.
"""

import sys

sys.path.insert(0, "src")

from cse476.observability import (  # noqa: E402
    OBSERVABILITY_MAP,
    Metrics,
    log_line,
    the_three_pillars,
    trace_run,
)

ok = True


def chk(label, cond):
    global ok
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
    ok = ok and cond


print("\n1. a trace records the ordered, timed steps of one run")
trace = trace_run([("classify", 10.0), ("lookup_policy", 30.0), ("decide", 5.0)])
chk("three steps recorded", len(trace.spans) == 3)
chk("the path is in order", trace.path() == ["classify", "lookup_policy", "decide"])
chk("the total is the sum", trace.total_ms() == 45.0)

print("\n2. the trace finds the slowest step (where to optimise)")
chk("slowest is the policy lookup", trace.slowest().step == "lookup_policy")
chk("and it names the duration", trace.slowest().ms == 30.0)

print("\n3. an empty trace is handled")
empty = trace_run([])
chk("empty total is zero", empty.total_ms() == 0.0)
chk("empty slowest is None", empty.slowest() is None)

print("\n4. metrics aggregate across MANY runs")
m = Metrics()
m.observe(trace_run([("a", 10.0), ("b", 10.0)]))                 # 20ms, ok
m.observe(trace_run([("a", 30.0), ("b", 10.0)]), failed=True)    # 40ms, failed
m.observe(trace_run([("a", 20.0), ("b", 10.0)]))                 # 30ms, ok
chk("three runs counted", m.runs == 3)
chk("one failure counted", m.failures == 1)
chk("average latency is right", m.average_ms() == 30.0)          # (20+40+30)/3
chk("failure rate is right", m.failure_rate() == round(1 / 3, 4))

print("\n5. metrics on no runs do not divide by zero")
empty_m = Metrics()
chk("average is zero, not a crash", empty_m.average_ms() == 0.0)
chk("failure rate is zero", empty_m.failure_rate() == 0.0)

print("\n6. a structured log line is searchable data, not text")
line = log_line("run-123", trace, outcome="ok")
chk("it has a run id", line["run_id"] == "run-123")
chk("it records the outcome", line["outcome"] == "ok")
chk("it records the total time", line["total_ms"] == 45.0)
chk("it records the slowest step", line["slowest_step"] == "lookup_policy")
chk("it records the path", line["path"] == ["classify", "lookup_policy", "decide"])

print("\n7. the trace is deterministic (injected timing, no flakiness)")
a = trace_run([("x", 1.0), ("y", 2.0)]).total_ms()
b = trace_run([("x", 1.0), ("y", 2.0)]).total_ms()
chk("same steps, same trace, every run", a == b)

print("\n8. the mapping and pillars are present and sensible")
chk("before vs after shipping is stated", "watches live" in OBSERVABILITY_MAP["before vs after shipping"])
chk("a trace is one run", "one run" in OBSERVABILITY_MAP["a trace"])
chk("metrics are many runs", "many runs" in OBSERVABILITY_MAP["metrics"])
p = the_three_pillars()
chk("trace is for one run", "one run" in p["trace"])
chk("metrics are for health", "overall health" in p["metrics"])
chk("together: metrics alert, logs locate, trace explains", "alert" in p["together"])
chk("the point: you cannot fix what you cannot see", "cannot see" in p["the_point"])

print("\n" + ("ALL PASS" if ok else "SOMETHING FAILED"))
sys.exit(0 if ok else 1)
