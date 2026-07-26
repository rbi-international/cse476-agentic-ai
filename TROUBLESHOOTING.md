# Troubleshooting

Find your error text below. If it is not here, post the **full** output in the
course channel along with which lane you are on.

---

### `ModuleNotFoundError: No module named 'cse476'`

You have not installed the package.

```bash
pip install -e .        # from the repository root
```

If you are in a notebook, restart the kernel after installing.

---

### `LaneError: Lane 'github' ... GITHUB_TOKEN is not set`

Either `.env` does not exist, or the variable is empty, or you edited
`.env.example` by mistake instead of `.env`.

```bash
cp .env.example .env
```

Then edit `.env`, not `.env.example`.

---

### `404` or `The model does not exist`

**On Lane B (github):** model names are namespaced. Use `openai/gpt-4.1-mini`.

**On Lane A (foundry):** `MODEL` must be your **deployment name** from the
Foundry portal, not the model name.

---

### `401 Unauthorized`

The token is wrong, expired, or has stray whitespace. Regenerate it and paste
it with no quotes and no trailing space.

On Lane A this usually means the key belongs to a different resource than the
endpoint you set.

---

### `429 Rate limit exceeded`

You hit the free tier cap. Three options, in order of preference:

1. Wait. Most caps are per minute and clear quickly.
2. Switch lane. Set `PROVIDER=groq` or `PROVIDER=local` in `.env`.
3. If the whole lab hits this at once, that is the instructor's problem, not
   yours. Say so in the channel.

---

### The agent runs forever and will not stop

This is a real failure mode, not a bug in the starter code, and we cover it
properly in Unit 2. The immediate fix is a max iterations guard on your loop.
If you have already burned a lot of quota, switch to `PROVIDER=local` while
you debug, because Ollama costs nothing.

---

### `Connection refused` on `localhost:11434`

Ollama is not running.

```bash
ollama serve
```

---

### The notebook is using the wrong Python

The kernel is pointing at your system Python instead of the virtual
environment.

```bash
source .venv/bin/activate
python -m ipykernel install --user --name cse476 --display-name "Python (cse476)"
```

Then pick **Python (cse476)** in the notebook kernel picker.

---

### I committed a key by accident

Rotate it immediately. Deleting the commit is not enough, because it is
already in the history and, if you pushed, in GitHub's cache.

1. Revoke the old key at the provider.
2. Generate a new one.
3. Put it in `.env`, which is gitignored.

Nobody will be penalised for doing this once. Everybody gets penalised for
not telling anyone.

---

### pip tries to install an ancient version of something and the build crashes

Symptom: `pip install -r requirements.txt` starts downloading a very old
version of a package you have never heard of, for example `Werkzeug-0.4.1`,
and the build fails with a Python 2 syntax error like
`except X, e:  SyntaxError: multiple exception types must be parenthesized`.

What is happening: two of your packages disagree about what version of a shared
transitive dependency is allowed, and the disagreement has no solution. When
pip cannot satisfy a constraint, it walks backward through older releases
trying combinations, until it reaches a version so old it does not run on
Python 3. The ancient version is a symptom. The real cause is an
**unsatisfiable version conflict** higher up the tree.

The specific case you may hit in this course: the full `agent-framework`
meta-package pulls in every integration Microsoft ships, including an
Azure Functions piece that pins one `werkzeug` version, while `semantic-kernel`
pins an incompatible one. There is no `werkzeug` that satisfies both, so the
install fails. This is why `requirements.txt` installs `agent-framework-core`
and `agent-framework-openai` rather than the meta-package: we only ever import
`agent_framework.openai`, and the two focused packages carry none of the
conflicting dependencies.

The fix:

1. **Make sure you are on the current `requirements.txt`.** `git pull`, then
   reinstall. If it lists `agent-framework-core` and `agent-framework-openai`
   rather than a bare `agent-framework`, you have the fixed version.

2. **Install into a clean environment**, so no unrelated package you added for
   another project joins the resolution and adds its own conflicting bound.

   ```bash
   conda deactivate
   conda env remove -n cse476
   conda env create -f environment.yml
   conda activate cse476
   pip install -e .
   python setup_check.py
   ```

The general lesson: a build error for a package you never asked for is almost
always a version conflict, not a problem with that package. Read one line above
the crash to see who pulled it in, and install course work into its own clean
environment so unrelated packages cannot join the fight.
