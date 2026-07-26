# Microsoft Foundry, instructor setup

For Rohit. Verified 24 July 2026. Read the first section before you enter a
card number anywhere.

---

## 1. The thing that will cost you money if you skip it

**Pay As You Go subscriptions have no spending limit. None. It does not exist
as a feature.**

The spending limit that automatically disables a subscription when the money
runs out only exists on **credit based** subscriptions: the Azure free account,
Azure for Students, Visual Studio benefits. On Pay As You Go there is no such
control and you cannot enable one.

What Pay As You Go gives you instead is **budgets**, and budgets only send email.
They do not stop anything. Worse, actual cost alerts are evaluated roughly every
24 hours, so an agent stuck in a loop overnight is discovered the next morning,
after the fact.

That combination, an unbounded loop and a notification that arrives a day late,
is exactly the failure you demonstrate live in Lecture 1. It would be a poor
lesson to then fall into it yourself.

### So what actually bounds your spend

Three layers, in order of how hard they are.

| Layer | Stops spending? | How fast |
|---|---|---|
| **TPM quota on the deployment** | Yes, genuinely | Immediately, per minute |
| Spending limit on a credit subscription | Yes, disables the subscription | When credit is exhausted |
| Budget alert on Pay As You Go | **No, email only** | Up to 24 hours late |

The first one is the real control and almost nobody uses it deliberately. Set
it deliberately.

---

## 2. Which subscription to use

**Start with the Azure free account.** It includes trial credit, and critically
the **spending limit is on by default**, which means the subscription disables
itself rather than billing you. Build and rehearse every Lecture 6 demo on this.

When the trial credit or its window runs out, you have a decision:

- **Stay on credit based** if LPU comes through with an institutional
  subscription. Ask for this in writing before the semester starts.
- **Move to Pay As You Go** only after you have set the TPM caps in section 4.
  Without those you are running an unbounded liability against your own card.

There is no shame in the first option and no danger in the second **provided**
the quota work is done first.

---

## 3. Create the resource, in the right portal

There are now two Foundry portals and only one of them is worth learning.

- **Foundry (classic)** is the hub based experience that grew out of Azure AI
  Studio. It still works and it is in maintenance mode.
- **Foundry (new)** is the project first experience built on the consolidated
  resource. Everything Microsoft is investing in, the agent service,
  evaluations, the new model catalogue, observability, is wired up around
  Foundry projects first.

**Create a Foundry project, not a hub project.** Hub projects exist for
backwards compatibility. If a tutorial tells you to "create a new hub", it was
written for the old portal.

### Portal route

1. Sign in to the Foundry portal. **Make sure the New Foundry toggle is on.**
2. Create project. Give it a name, for example `cse476`.
3. Create a **new resource group**, for example `cse476-rg`. Keeping everything
   in one group means you can delete the entire semester in one action later.
4. Pick a location. `eastus` is a safe default. Use `westus3` only if you want
   to try instant models, which skip the deployment step.

The portal creates the parent Foundry resource for you.

### CLI route, if you prefer it reproducible

```bash
az login

az group create --name cse476-rg --location eastus

az cognitiveservices account create \
  --name cse476-foundry \
  --resource-group cse476-rg \
  --kind AIServices \
  --sku S0 \
  --location eastus \
  --custom-domain cse476-foundry \
  --allow-project-management
```

`--allow-project-management` **cannot be changed after creation**. Miss it and
you rebuild the resource. It is the flag that makes this a Foundry resource
rather than a plain AI services one.

---

## 4. Deploy a model with a deliberately small TPM

This is the step that actually protects you, and it is one slider.

Quota is assigned per subscription, per region, per model, in units of tokens
per minute. **Assigning TPM to a deployment sets the enforced rate limit on that
deployment.** Requests beyond it are throttled, not billed.

For a demo account, deploy a small cheap model with a small cap:

```bash
az cognitiveservices account deployment create \
  --name cse476-foundry \
  --resource-group cse476-rg \
  --deployment-name chat-demo \
  --model-name gpt-4o-mini \
  --model-format OpenAI \
  --sku-name Standard \
  --sku-capacity 10
```

`--sku-capacity 10` is **10,000 TPM**. Each unit is 1K TPM, and the minimum is
1. In the portal it is the "Tokens per Minute Rate Limit" slider on the deploy
dialog.

### Work out your own ceiling

The arithmetic is worth doing once, because it converts an unbounded worry into
a number.

```
worst case tokens per month = TPM x 60 x 24 x 30
```

At 10,000 TPM that is 432 million tokens a month **if the deployment ran flat
out, continuously, for thirty days**. Multiply by the current per token price
for your model from the Azure pricing page to get your true ceiling. Your actual
classroom usage will be a rounding error against that, which is the point: you
now know the worst case rather than hoping.

Deploy **one** model. Not four. Every extra deployment is another unbounded
surface, and Lecture 6 only needs one.

### If the TPM slider is stuck at 0

That means your subscription has no quota allocated for that model in that
region. It is common on new and free subscriptions. Check what you have:

```bash
az cognitiveservices usage list -l eastus
```

Then either request a quota increase for that model and region, or pick a
different region where you do have quota. Do this **a week before Lecture 6**,
not the night before, because quota requests are reviewed individually.

---

## 5. Add budget alerts as a second layer

They do not stop anything. They are still worth twenty minutes.

Portal: **Cost Management + Billing**, then **Budgets**, then **Add**. Scope it
to the `cse476-rg` resource group rather than the whole subscription, so the
number means something.

Set four thresholds:

| Type | Threshold | Why |
|---|---|---|
| Actual | 50% | Early awareness |
| Actual | 80% | Time to act |
| Actual | 100% | You are over |
| **Forecast** | 110% | **Fires days earlier than the actual alerts** |

The forecast alert is the useful one. Actual cost alerts are evaluated roughly
every 24 hours; the forecast one fires when Azure's projection crosses the line,
which can be days ahead.

Set the amount to something you would genuinely notice, not something
comfortable. For a demo account, low.

---

## 6. Wire it into the course repo

Get the endpoint and key from the Foundry portal, then in your `.env`:

```
PROVIDER=foundry
AZURE_OPENAI_ENDPOINT=https://cse476-foundry.openai.azure.com/
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_API_VERSION=2024-10-21
MODEL=chat-demo
```

**`MODEL` must be your deployment name, not the model name.** You deployed
`gpt-4o-mini` and named the deployment `chat-demo`, so `MODEL=chat-demo`.
Getting this wrong produces a 404 that reads as though the model does not exist,
and it catches everybody exactly once.

Then:

```bash
python setup_check.py
```

You want the `foundry` lane to show `credential present` and the live call to
pass. Switch `PROVIDER` back to `github` afterwards so your day to day work
stays on the free lane.

---

## 7. Before Lecture 6

A rehearsal checklist, because this is the first lecture where the room watches
rather than types, and a portal that will not load is a lecture that does not
happen.

- [ ] `setup_check.py` passes on `PROVIDER=foundry`
- [ ] You can create a project in the portal **while narrating it**, not just
      click through it silently
- [ ] The model catalogue loads on the projector resolution you actually use
- [ ] The playground responds in under about five seconds on LPU wifi
- [ ] You have the deployment name and the model name **both visible**, because
      slide 6 of Lecture 6 turns that distinction into a teaching point
- [ ] A browser profile with no personal tabs, no bookmarks bar, no email
- [ ] Screenshots of every portal screen you plan to show, saved locally, as a
      fallback for when the wifi dies mid demo

That last one has saved more lectures than any amount of preparation.

---

## 8. Things that changed, which affect the syllabus

Three dates worth having in your head, because students will find contradictory
tutorials and ask.

**The rename.** Azure AI Studio became Azure AI Foundry at Ignite 2024. Azure AI
Foundry became **Microsoft Foundry** at Ignite in November 2025, formalised in
the January 2026 product terms. Same platform, same resource type, same keys.
Azure AI services is now called **Foundry Tools**. When searching for help,
search both names.

**The Assistants API retires on 26 August 2026.** That is inside your semester.
Do not build anything on it. Use **Foundry Agent Service** and the Responses API
instead. If a tutorial says Assistants, it is legacy.

**The SDK split.** `azure-ai-projects` 2.x is incompatible with 1.x. Sample code
written for the classic portal will not run against a new Foundry project. Check
which one a sample targets before you debug it.

---

## 9. Delete it when the semester ends

Everything is in one resource group, which is why section 3 put it there.

```bash
az group delete --name cse476-rg --yes
```

One caution: deleting a resource programmatically bypasses the normal check that
deployments are removed first. When that happens the quota allocation stays
unavailable for 48 hours until the resource is purged. So if you plan to rebuild
immediately, delete the **deployments** first, then the group.
