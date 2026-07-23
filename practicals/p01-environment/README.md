# Practical 1: Development environment

**Unit 1. Assessed. Do this before Lecture 2.**

## What you are proving

That you can run code on at least one lane, that your keys are not in git, and
that you know which lane you are on.

## Steps

1. Create the environment. `conda env create -f environment.yml` then
   `conda activate cse476` then `pip install -e .` from the repository root.
2. `cp .env.example .env` and put a GitHub token in `GITHUB_TOKEN`.
   github.com/settings/tokens, classic token, no scopes ticked.
3. Register the kernel:
   `python -m ipykernel install --user --name cse476 --display-name "Python (cse476)"`
4. Run `python setup_check.py` until it prints `You are ready.`
5. Open `notebooks/u1/l1_first_agent.ipynb`, pick the **Python (cse476)** kernel,
   and run every cell.

## Submit

A screenshot of `setup_check.py` passing, and your notebook with outputs, committed
to your fork.

## Marks are lost for

Committing `.env`. Running on the system Python instead of the environment.
Submitting a notebook with no outputs, since that means it was never run.

## If it will not work

`docs/TROUBLESHOOTING.md` first. Then post the **entire** output of
`setup_check.py` in the course channel, not a screenshot of one line.
