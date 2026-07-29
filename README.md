# CSE476 Agentic AI and Intelligent Automation

Lovely Professional University, School of Computer Science and Engineering.

This repository is the course. Every practical, every notebook I build in
class, the slide handouts, the setup script, the tests, all of it lives here.
Clone it once, and pull before every session.

I have written this README to be the thing you actually follow, not a thing you
skim. If you do exactly what is below, in order, you will have a working setup
in about fifteen minutes and you will not hit the problems that usually eat the
first lab. Read it properly once. It saves you time, not the other way round.

**New here? Two files to open first.** `RUN_THIS_PROJECT.md` is the fastest path
to a working setup, plus a full map of every file and how we run models in this
course (the Foundry way). Then, for following along file by file, each unit has a
guide: `docs/unit1/GUIDE.md`, `docs/unit2/GUIDE.md`, `docs/unit3/GUIDE.md`,
`docs/unit4/GUIDE.md`. They
list every module, notebook, and test, what each does, and the exact command to
run it.

---

## What you need before you start

Three tools, installed once. If you already have them, skip ahead.

**Git.** This is how you get the code and how you submit work. On Windows,
install **Git for Windows**, which also gives you **Git Bash**, the terminal I
use in every walkthrough. Download it from git-scm.com. When it asks a lot of
questions during install, the defaults are fine.

**Python 3.12.** From python.org. On Windows, tick **"Add Python to PATH"** on
the first screen of the installer. People miss this and then nothing works from
the terminal. If you miss it, reinstall and tick it.

**VS Code.** From code.visualstudio.com. After installing, open it once, go to
the Extensions panel on the left, and install the **Python** and **Jupyter**
extensions. Those two let VS Code run our notebooks.

You also need a **GitHub account**. You need it for the code and for the free
model access in Lane B, so make one now at github.com if you do not have one.

---

## Step 1: Get the code

Open **Git Bash** (Windows) or your terminal (Mac, Linux) and run:

```bash
git clone https://github.com/rbi-international/cse476-agentic-ai.git
cd cse476-agentic-ai
```

You are now inside the project folder. Everything from here happens in this
folder, so stay in this terminal.

---

## Step 2: Create your environment

An environment is a clean, isolated box for this project's packages, so they
never fight with anything else on your machine. I use conda. If you do not have
conda, or you just prefer plain Python, the venv path right below does the same
job.

Pick **one** of these two. Not both.

### Option A: conda  (this is what I use in class)

If you have Anaconda or Miniconda installed:

```bash
conda env create -f environment.yml
conda activate cse476
pip install -e .
```

### Option B: plain venv  (if you do not use conda)

Nothing wrong with this. It is simpler and it is built into Python.

```bash
python -m venv .venv

# then activate it:
source .venv/bin/activate          # Mac, Linux, or Git Bash on Windows
# .venv\Scripts\activate           # Windows PowerShell or cmd

pip install -r requirements.txt
pip install -e .
```

You will know either one worked because your terminal prompt now shows
`(cse476)` or `(.venv)` at the start of the line. That tells you the box is
active. If you close the terminal and come back later, you have to activate
again. That is normal, not a bug.

### Two things about these commands, because you should know what you ran

`environment.yml` only pins Python and pip. Everything else installs through
`requirements.txt`. I did that on purpose: the agent libraries we use change
almost weekly, and conda's own package channel lags the real world by weeks. If
I pinned them in conda, you would get stale versions of exactly the packages
that matter most. So conda gives us a clean Python, and pip gives us current
libraries.

`pip install -e .` installs this repository itself as a package, in "editable"
mode. That is the line that lets you write `from cse476.lanes import ...` in any
notebook and have it just work. If you ever see `ModuleNotFoundError: No module
named 'cse476'`, it is almost always because you skipped this line or you are in
the wrong environment. Run it again.

---

## Step 3: Register the notebook kernel

This tells Jupyter and VS Code to run our notebooks inside the environment you
just made, instead of your system Python where none of the packages exist.

```bash
python -m ipykernel install --user --name cse476 --display-name "Python (cse476)"
```

Later, when you open a notebook in VS Code, click the kernel picker in the top
right and choose **Python (cse476)**. If your imports fail in a notebook, this
is the first thing to check. Nine times out of ten the notebook is running on
the wrong Python.

---

## Step 4: Pick a lane and add your key

Here is the idea that runs through the whole course. The model is like
electricity, and your code is an appliance. Your mixer does not care whether the
power came from a coal plant, a solar panel, or your neighbour's inverter. It
cares about one thing: does the plug fit the socket. Almost every model provider
now offers the same socket shape, so we write every practical against that one
socket and change nothing but which plug is in the wall.

That plug is one line in a file called `.env`. Change it, and the entire course
runs somewhere else. No other line of any notebook changes.

First, make your own `.env` from the template:

```bash
cp .env.example .env          # Mac, Linux, Git Bash
# copy .env.example .env      # Windows PowerShell or cmd
```

Now open `.env` in VS Code and fill in **one** lane. You do not need all four. I
strongly recommend starting with Lane B, because it is free and takes two
minutes.

### Lane B: GitHub Models  (free, start here)

This is your default. It is free model access through Microsoft's own
infrastructure, tied to the GitHub account you already have.

1. Go to github.com/settings/tokens
2. Generate a new **classic** token
3. Tick **no scopes at all**. Genuinely none. It still works.
4. Copy it into `GITHUB_TOKEN=` in your `.env`
5. Make sure the top of `.env` says `PROVIDER=github`

That is it. You are done. Skip to Step 5.

The other three lanes are there when you want them. Full detail on all of them,
including where each key comes from and what the real limits are, is in
[`docs/LANES.md`](docs/LANES.md). Here is the short version.

### Lane C: Groq  (free, fast)

A key from console.groq.com into `GROQ_API_KEY`, and `PROVIDER=groq`. Fast, but
its free tier is small since 2026, roughly a thousand requests a day.

### Lane D: Ollama  (free forever, runs on your laptop)

Install from ollama.com, run `ollama pull llama3.2`, set `PROVIDER=local`. No
key. Slow and weak, and it never goes down and never runs out. Your safety net.

### Lane A: Microsoft Foundry  (the real enterprise platform)

This is what I demonstrate on in class, on my own account. **You do not need it
for any practical.** But some of you will want to follow exactly what I do, so
here is the full walkthrough. It costs real money, so read the whole thing
before you start, especially the part about the spending cap.

**1. Make an Azure account.** Go to portal.azure.com, sign in with a Microsoft
account, and start the **Azure free trial**. It gives you 200 USD of credit for
30 days. The important part: on the free trial the spending limit is **on by
default**, which means the account disables itself rather than billing you when
the credit runs out. It asks for a card only to verify you are real. Keep that
spending limit on and ignore any banner asking you to remove it.

**2. Create a Foundry project.** Go to ai.azure.com. Make sure the **New
Foundry** toggle, top right, is on. Click **Create project**. Under Advanced
options, name the project `cse476`, the resource `cse476-foundry`, create a new
resource group `cse476-rg`, and leave the region on its default. **Turn off "Set
up recommended resources."** That toggle provisions an extra logging resource
that costs money continuously, and we do not need it until much later.

**3. Deploy a model, with a cost cap.** Inside the project, go to Models, then
Deploy a base model. Pick a model that is **not** marked deprecated, `gpt-5-mini`
is a good cheap one. Choose **Custom settings**, not Default. Name the
deployment `chat-demo`. Set the deployment type to **Global Standard**. Now the
line that actually protects your card: drag **Tokens per Minute** down to
**10000**, the minimum. That caps how fast the deployment can ever spend, which
turns your worst case from a scary unknown into simple arithmetic. You can raise
it later in two clicks. You cannot un-spend money.

**4. Get your endpoint and key.** Open the deployment, click the **key icon**.
Copy the Endpoint. The key is a secret, so never screenshot it or paste it where
others can see it. If it ever does get exposed, regenerate it immediately, which
is a thing you will learn to do reflexively in this course.

**5. Wire it into `.env`:**

```
PROVIDER=foundry
AZURE_OPENAI_ENDPOINT=https://cse476-foundry.openai.azure.com/openai/v1/
AZURE_OPENAI_API_KEY=your-key-here
MODEL=chat-demo
```

Two things that catch everyone. The endpoint must end in `/openai/v1/`. And
`MODEL` is your **deployment name**, `chat-demo`, not the model name
`gpt-5-mini`. Get that second one wrong and you get a 404 that reads like the
model does not exist, and you will debug in the wrong place for an hour. It is
almost always this.

---

## Step 5: Prove it works

```bash
python setup_check.py
```

This checks your Python, your packages, your `.env`, every lane you configured,
and then it makes one real call to the model. It ends in either
`You are ready.` or a list of the exact things to fix, in plain language.

If it fails, read what it says first, then check
[`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md). If you are still stuck,
post the **entire** output in the course channel. Not a screenshot of one line,
not "it's not working". The whole output. Half the class will hit the same
thing and one good thread solves it for everyone.

When it says `You are ready.`, you are. Open
`notebooks/u1/l1_first_agent.ipynb`, pick the **Python (cse476)** kernel, and
run the first cell. If it prints your lane, you are set for the whole course.

---

## Why the folders look the way they do

You will see this shape when you open the repo. It is not random, and knowing
why each piece exists will make the whole thing easier to navigate.

```
src/cse476/          the shared library every notebook imports
notebooks/u1/         the code I build live in each Unit 1 lecture
notebooks/u2/         and Unit 2, one notebook per lecture
notebooks/u3/         and Unit 3, built on the real frameworks
notebooks/u4/         and Unit 4, the multi agent collaboration system
docs/                 setup, lanes, troubleshooting, syllabus map, unit guides
tests/                tests that prove the code works, offline
environment.yml       the conda environment definition
requirements.txt      the exact package versions
.env.example          the template you copy to make your own .env
.env                  YOUR keys. Never shared, never committed.
setup_check.py        run this first, and whenever something breaks
```

Here is the thinking behind the important ones.

**`src/cse476/` holds the shared library.** Instead of copy-pasting the same
agent loop into twenty notebooks, I wrote it once here, and every notebook
imports it. So when I improve the loop, every notebook gets the improvement.
This is also why `pip install -e .` matters: it makes this folder importable
from anywhere.

**`.env` and `.env.example` are two different files on purpose, and this is the
single most important thing in the whole repo to understand.** `.env.example` is
the empty template. It is safe to share, it has no secrets, and it is committed
to git so everyone can copy it. `.env` is **yours**, with your actual keys in it,
and it must **never** be committed or shared. That is why the repo is configured
to ignore it automatically, and why the setup script refuses to pass if it is
not being ignored. A leaked key is real money and a real security hole. Treat
your `.env` like your password, because it effectively is one.

**`tests/` is not just for me.** Yes, they run automatically to catch mistakes
before they reach you. But they are also the clearest possible statement of what
the code is supposed to do, written as runnable proof rather than prose. When
you are unsure how something behaves, reading its test is often faster than
reading its code. Several of them are the arguments from my lectures, written so
you can run them and watch them be true.

**`slides/pdf/` exists so you can read the decks without PowerPoint.** Each
lecture ships a slide deck and a PDF of it. The PDF is for reading on a phone,
on a train, anywhere.

---

## The rules that will save you marks

**Never commit your key.** `.env` is ignored automatically, and the setup script
checks this before it lets you pass. If you ever paste a key into a notebook
cell, the output gets saved into the notebook, and committing that notebook
leaks the key. If it happens, regenerate the key immediately and tell someone.
Nobody is penalised for doing that once. People are penalised for hiding it.

**Delete your cloud resources after every lab.** If you use Lane A, an idle
deployment costs money while you sleep. Get in the habit of removing what you
deployed once the lab is done.

**Pull before every session.** I fix and improve things between classes,
including fixing whatever broke in the last one. Run `git pull` before you sit
down.

**Submit notebooks with their outputs.** A notebook with empty output cells
tells me it was never actually run. Run it, then submit it.

---

## A few things that recently changed

This field renames and retires things fast, faster than its own documentation
keeps up. The ones that will confuse you if you go searching for help:

- **Azure AI Foundry is now Microsoft Foundry.** Renamed at the end of 2025.
  Same platform, same keys. Search both names.
- **The Bot Framework SDK is retired.** Its support ended in December 2025 and
  its code is archived. We use the Microsoft 365 Agents SDK instead. If a
  tutorial tells you to use Bot Framework, it is out of date.
- **The Assistants API retires on 26 August 2026,** which is during our
  semester. Do not build anything on it. We use the Foundry Agent Service.
- **Semantic Kernel and AutoGen merged into Microsoft Agent Framework.** This is
  the big one for Unit 3. On 3 April 2026 Microsoft shipped Agent Framework 1.0,
  which absorbs both into one production SDK. Both older frameworks are now in
  maintenance mode: bug fixes only, no new features. So when the syllabus says
  Semantic Kernel and AutoGen, we learn what they were and why they merged, and
  then we build on the framework that actually replaced them, because that is
  what you would use in a job today and what an interviewer expects you to know.
  One trap to know now: if your imports fail, run `pip show autogen` first. There
  are several packages with similar names and it is easy to install the wrong one.

I keep the materials current and I will tell you in class when something shifts.
When you find a tutorial online that contradicts what we do, check its date
first. It is usually just old.

---

## Getting help

Course channel first. Post the full error text and say which lane you are on.
[`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) covers the errors that come
up most: missing installs, wrong model names, 401s, 429s, runaway loops, and
what to do if you leak a key.

And if you want to know *why* we are doing any of this, before the mechanics,
read [`docs/WHY_THIS_COURSE.md`](docs/WHY_THIS_COURSE.md) first. That one is the
story. Start there if the setup feels dry.
