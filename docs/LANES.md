# The four lanes

You only need one. I have set the course up so the default, Lane B, is free and
takes about two minutes. Read that section, ignore the rest until you need it.

The whole idea: your code never names a provider. You pick a lane in `.env`,
and every notebook runs the same way regardless. I built it like this on
purpose, so that nobody in the class is ever blocked from a practical for lack
of money, and so the code you write works unchanged whether you are on my paid
demo account or your own free key.

---

## Lane B, GitHub Models  (start here)

This is the one I want you on. It gives you free API access to a catalogue of
frontier and open models through an Azure-hosted, OpenAI-compatible endpoint,
and you already need a GitHub account for the course repository, so you are
most of the way there already.

**Endpoint:** `https://models.github.ai/inference`

**Get a credential**
1. Go to github.com/settings/tokens
2. Generate new token, classic
3. Tick **no scopes at all**. You do not need any.
4. Paste it into `GITHUB_TOKEN` in your `.env`

**Model names are namespaced here.** Use `openai/gpt-4.1-mini`, not
`gpt-4.1-mini`. The catalogue is at github.com/marketplace/models.

**The limit, told honestly.** Requests are capped at roughly 8K tokens in and
4K out, with a modest rate limit that depends on your GitHub plan. That is
comfortable for everything we do in class and genuinely too small for
production. Knowing exactly where a free tier stops being enough is a real
skill, so in Unit 5 we measure it rather than guess.

---

## Lane A, Microsoft Foundry

This is the real enterprise platform, and it is the one I demonstrate on in
class, on my account. You do not need it to pass a single practical. If you
want to run the Foundry parts yourself, here is how.

Foundry was called Azure AI Foundry until Ignite in November 2025, and Azure AI
Studio before that. Same platform, renamed twice. When you search for help you
will hit all three names.

The current Foundry surface is OpenAI-compatible, which means this lane uses the
plain `OpenAI` client, exactly like the GitHub and Groq lanes. There is no
special Azure client and no API version to track. That is a deliberate
simplification on Microsoft's side and it makes the whole thing easier to teach.

```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/openai/v1/
AZURE_OPENAI_API_KEY=...
MODEL=your-deployment-name
```

**Two things catch everybody, so I am flagging them up front.**

- The endpoint has to be the **v1 base**, ending in `/openai/v1/`. Get it from
  the portal: open your deployment, click the key icon, copy the Endpoint. I
  wrote the lane to tidy up a trailing slash or a pasted `/responses` path for
  you, so a slightly messy copy still works, but the host itself must be right.
- Foundry routes by **deployment name**, not model name. When I set up the
  course account I deployed `gpt-5-mini` and named the deployment `chat-demo`,
  so `MODEL=chat-demo`. Get this wrong and you get a 404 that reads as though
  the model does not exist, which sends people debugging in the wrong place for
  an hour. It is almost always this.

---

## Lane C, Groq

Fast inference on open models, free tier, no card. A good option if you want
speed and Lane B is being slow.

Get a key at console.groq.com and set `GROQ_API_KEY`.

**One warning.** Groq cut its free tier limits during 2026, down to roughly
1,000 requests per day on most models. Older tutorials quote a far higher
figure, so do not be surprised when you hit the wall sooner than they suggest.
Fine for one person working alone, tight for a full lab hitting it at once.

---

## Lane D, Ollama, on your own machine

Nothing to sign up for and nothing to run out of. It is slower and weaker than
every other lane, and it will never fail you the night before a submission,
which is exactly why I keep it in the course.

```bash
# install from ollama.com, then
ollama pull llama3.2
ollama serve            # usually already running after install
```

Set `PROVIDER=local`. No key needed.

**What to expect.** A 3B model will follow simple tool schemas and will
struggle with the multi-step reasoning in Unit 4. That is not a bug in your
code, it is a real and useful lesson about what model size buys you, and we
lean into it rather than hiding it.

---

## Azure for Students, if you want your own Foundry credit

Optional, and worth doing early rather than late.

It gives you 100 USD of Azure credit, valid twelve months, renewable each year
you stay enrolled. No credit card. You verify with your university email. You
have to be eighteen or over and a full-time student at an accredited,
degree-granting institution.

Two things I want you to know before you activate it, because both have caught
students out:

- When the credit runs out the subscription is **disabled, not billed to you**.
  That is protective. It also means one resource you forgot to delete can
  quietly eat your whole year.
- The credit does **not** top up early. You get the next 100 USD when the twelve
  months are up, not when you run dry.

The twelve-month clock starts the day you activate, and your project work lands
in the back half of the semester, so activate in week one, not week ten.
