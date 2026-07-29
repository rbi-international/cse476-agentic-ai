# Unit 4 run-along guide: multi-agent systems and collaboration

Every file in Unit 4, what it does, and how to run it. Everything here runs
offline on the real `agent-framework` package, because the nodes are plain
functions writing to real workflow state. No lane needed except where noted.

Run all commands from the repository root, on the `cse476` environment.

## Lecture 1, fan-out and fan-in

- **Module:** `src/cse476/orchestration.py`
- **Notebook:** `notebooks/u4/l1_fan_out_fan_in.ipynb`
- **Test:** `tests/mock_run_u4l1.py`

One ticket goes to three reviewers (security, priority, sentiment) at once, and a
fan-in gathers their findings into one verdict. The deep idea: fan-in
synchronises, the combine step waits for every reviewer before it runs.

```bash
python tests/mock_run_u4l1.py
```

## Lecture 2, routing

- **Module:** `src/cse476/routing.py`
- **Notebook:** `notebooks/u4/l2_routing.ipynb`
- **Test:** `tests/mock_run_u4l2.py`

A switch-case router: classify the ticket once, then send it to exactly one
handler, with a default for the rest. The framework requires a default; a
hand-rolled conditional edge does not, and silently drops unmatched work.

```bash
python tests/mock_run_u4l2.py
```

## Lecture 3, the manager pattern

- **Module:** `src/cse476/manager.py`
- **Notebook:** `notebooks/u4/l3_manager.ipynb`
- **Test:** `tests/mock_run_u4l3.py`

Specialist agents wrapped as tools, and a manager that delegates by judgement
instead of fixed rules. The specialists and tool wiring build offline; the
manager's actual decision needs a lane, because deciding is what the model does.

```bash
python tests/mock_run_u4l3.py
```

## Lecture 4, the blackboard

- **Module:** `src/cse476/blackboard.py`
- **Notebook:** `notebooks/u4/l4_blackboard.ipynb`
- **Test:** `tests/mock_run_u4l4.py`

Agents read and append findings to a shared board via `set_state` and
`get_state`. Read, modify, write, and the overwrite bug when an agent forgets to
read before writing.

```bash
python tests/mock_run_u4l4.py
```

## Lecture 5, the full system

- **Module:** `src/cse476/triage_system.py`
- **Notebook:** `notebooks/u4/l5_full_system.ipynb`
- **Test:** `tests/mock_run_u4l5.py`

The finale. All four primitives composed into one system: route a ticket to a
team, fan out the checks onto a shared board, fan in, and decide. The blackboard
is the connective tissue that makes the composition work.

```bash
python tests/mock_run_u4l5.py
```

## Run every Unit 4 test at once

```bash
for f in tests/mock_run_u4l*.py; do echo "== $f =="; python "$f" | tail -1; done
```

## What you can do after this unit

You can take a real problem, decompose it into narrow specialists, and wire them
together with routing, parallelism, and shared state into one coordinated system.
Decompose, route, parallelise, share, decide. That is a multi-agent system, and
Unit 5 takes it into production: serving, monitoring, testing, and deploying it.
