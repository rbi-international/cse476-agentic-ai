# The lanes

You only need one. The default, **Groq**, is free and takes about two minutes.
Read that section, ignore the rest until you need it.

The whole idea: your code never names a provider. You pick a lane in `.env`, and
every notebook runs the same way regardless. I built it like this on purpose, so
that nobody in the class is ever blocked from a practical for lack of money, and
so the code you write works unchanged whether you are on my paid demo account or
your own free key.

> **GitHub Models has been retired.** GitHub shut GitHub Models down on 30 July
> 2026, so that lane now returns a 410 error for everyone and has been removed as
> an option. If an old `.env` still says `PROVIDER=github`, switch it to `groq`
> or `local` below. The rest of the course is unchanged: the lane abstraction was
> built for exactly this kind of provider change, so it is a one-line edit, not a
> rewrite.

---

## Lane 1, Groq  (start here)

This is the one I want you on. It gives you fast, free API access to a set of
strong open models through an OpenAI-compatible endpoint, with no card and about
two minutes of setup.

**Endpoint:** `https://api.groq.com/openai/v1`

**Get a credential**
1. Go to console.groq.com/keys
2. Sign in (GitHub or Google works)
3. Create an API key
4. Paste it into `GROQ_API_KEY` in your `.env`, and set `PROVIDER=groq`

**Model names.** The lane defaults to `llama-3.3-70b-versatile`, which is plenty
for class. You do not need to set `MODEL` at all. The catalogue is at
console.groq.com/docs/models.

**The limit, told honestly.** Groq cut its free tier during 2026, down to roughly
1,000 requests per day on most models, with a modest per-minute rate limit. That
is comfortable for one person working through a practical and genuinely too small
for production. Knowing exactly where a free tier stops being enough is a real
skill, so in Unit 5 we measure it rather than guess. If a full lab hits it at
once and you see rate-limit errors, switch to Lane 2 (Ollama), which never runs
out.

---

## Lane 2, Ollama, on your own machine  (free, no key, no limit)

Nothing to sign up for and nothing to run out of. It is slower and weaker than
every other lane, and it will never fail you the night before a submission,
which is exactly why I keep it in the course. It is also the safe fallback when
Groq's daily cap is exhausted.

```bash
# install from ollama.com, then
ollama pull llama3.2
ollama serve            # usually already running after install
```

Then set `PROVIDER=local` in your `.env`. No key, no `MODEL` line; the lane
defaults to `llama3.2`.

**What to expect.** A 3B model will follow simple tool schemas and will struggle
with the multi-step reasoning in Unit 4. That is not a bug in your code, it is a
real and useful lesson about what model size buys you, and we lean into it rather
than hiding it.

---

## Lane 3, Microsoft Foundry

This is the real enterprise platform, and it is the one I demonstrate on in
class, on my account. You do not need it to pass a single practical. If you want
to run the Foundry parts yourself, here is how.

Foundry was called Azure AI Foundry until Ignite in November 2025, and Azure AI
Studio before that. Same platform, renamed twice. When you search for help you
will hit all three names.

The current Foundry surface is OpenAI-compatible, which means this lane uses the
plain `OpenAI` client, exactly like the Groq lane. There is no special Azure
client and no API version to track. That is a deliberate simplification on
Microsoft's side and it makes the whole thing easier to teach.

```
AZURE_OPENAI_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project/openai/v1/
AZURE_OPENAI_API_KEY=...
MODEL=your-deployment-name
```

**Two things catch everybody, so I am flagging them up front.**

- The endpoint has to be the **v1 base**, ending in `/openai/v1/`. Get it from
  the portal: open your project home, copy the Endpoint. I wrote the lane to tidy
  up a trailing slash or a pasted `/responses` path for you, so a slightly messy
  copy still works, but the host itself must be right.
- Foundry routes by **deployment name**, not model name. When I set up the course
  account I deployed `gpt-5-mini` and named the deployment `chat-demo`, so
  `MODEL=chat-demo`. Get this wrong and you get a 404 that reads as though the
  model does not exist, which sends people debugging in the wrong place for an
  hour. It is almost always this.
- Keep the `MODEL` line **only** in the Foundry block of your `.env`. If it is
  left set after you switch back to a free lane, that free lane tries to use
  `chat-demo` and fails. The lane catches this and tells you, but it is easier to
  never let it happen.

---

## Retired, GitHub Models

GitHub Models used to be the free default for this course. GitHub retired it on
30 July 2026, after two warning brownouts earlier that month, and the inference
API now returns a 410 error for every account, including ones with prior usage.
There is no token or setting that brings it back. If your `.env` still selects
it, the course code will stop and tell you to switch to Groq or Ollama. This is
the second provider shake-up in a year, which is exactly why the course routes
everything through one lane abstraction: when a provider disappears, you change
one line, not forty notebooks.

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
