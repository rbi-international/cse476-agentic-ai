# The four lanes

You only need one. The course default is Lane B.

---

## Lane B, GitHub Models  (start here)

Free API access to a catalogue of frontier and open models through an
Azure hosted, OpenAI compatible endpoint. Every student in this course
already needs a GitHub account for this repository, so you already have
most of the setup done.

**Endpoint:** `https://models.github.ai/inference`

**Get a credential**
1. github.com/settings/tokens
2. Generate new token, classic
3. Tick **no scopes at all**
4. Copy it into `GITHUB_TOKEN` in your `.env`

**Model names are namespaced.** Use `openai/gpt-4.1-mini`, not `gpt-4.1-mini`.
Browse the catalogue at github.com/marketplace/models.

**Limits, honestly.** Roughly 8K tokens in and 4K tokens out per request, with
a modest requests per minute cap that depends on your GitHub plan. This is
comfortable for learning and genuinely inadequate for production. We will
measure exactly where it stops being enough in Unit 5 rather than guess.

---

## Lane A, Microsoft Foundry

The real enterprise platform. Demonstrated in class on the instructor account.
You do not need this to pass any practical.

Formerly called Azure AI Foundry. Renamed at Ignite November 2025 and
formalised in the January 2026 product terms.

```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_API_VERSION=2024-10-21
MODEL=your-deployment-name
```

**The one thing that catches everybody:** Azure routes by **deployment name**,
not model name. If you deployed `gpt-4o-mini` and named the deployment
`chat-dev`, then `MODEL=chat-dev`. Getting this wrong produces a 404 that
looks like the model does not exist.

---

## Lane C, Groq

Fast inference on open models. Free tier, no card.

Get a key at console.groq.com. Set `GROQ_API_KEY`.

**Note:** Groq reduced its free tier limits during 2026. Most models now sit
around 1,000 requests per day rather than the much higher figure you will see
quoted in older tutorials. Fine for one person, tight for a full lab running
simultaneously.

---

## Lane D, Ollama, on your own machine

Nothing to sign up for and nothing to run out of. Slower and weaker than every
other lane, and it will never fail you the night before a submission.

```bash
# install from ollama.com, then
ollama pull llama3.2
ollama serve            # usually already running after install
```

Set `PROVIDER=local`. No key needed.

**What to expect.** A 3B model will follow simple tool schemas and will
struggle with the multi step reasoning in Unit 4. That is a real and useful
lesson about model capability, not a bug in your code.

---

## Azure for Students

Optional, and worth doing early rather than late.

100 USD of Azure credit, valid twelve months, renewable each year you remain
enrolled. No credit card. You verify with your institutional email address.
You must be eighteen or over and a full time student at an accredited,
degree granting institution.

Two things to know before you activate:

- When the credit is exhausted the subscription is **disabled rather than
  billed to you**. Protective, but it also means one forgotten resource can
  quietly consume your whole year.
- The credit does **not** top up early. You get the next 100 USD when the
  twelve months are up, not when you run out.

The twelve month clock starts on activation, and your project work is in the
back half of the semester, so activate in week one.
