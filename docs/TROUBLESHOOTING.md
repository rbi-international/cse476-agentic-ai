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
