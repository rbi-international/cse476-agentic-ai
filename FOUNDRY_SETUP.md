# Microsoft Foundry, set it up the way I did

This is the exact Foundry setup for this course, written so you can follow it
yourself and end up with the same working thing I use in every live demo. I set
this up myself, hit the real traps, and wrote them down here so you do not have
to hit them too. I will also walk through it in class; this file is so you can do
it again on your own machine afterwards, at your own pace.

**Read section 1 before you enter a card number anywhere.** It is the one part
that can cost you real money if you skip it. Everything after that is safe once
section 1 is done.

If your Foundry account is not ready yet, that is fine. Do the coursework on the
free GitHub Models lane in the meantime (see `docs/LANES.md`), and switch to
Foundry the moment you are set up. Switching is one line in your `.env`, and none
of your code changes. But do get onto Foundry, because running agents on Foundry
the professional way is the whole point of this course.

---

## 1. The thing that will cost you money if you skip it

**A Pay As You Go subscription has no spending limit. None. It does not exist as
a setting you can turn on.**

The automatic spending limit that disables a subscription when the money runs
out only exists on **credit based** subscriptions: the Azure free account, Azure
for Students, Visual Studio benefits. On Pay As You Go there is no such control,
and you cannot add one.

What Pay As You Go gives you instead is **budgets**, and budgets only send email.
They do not stop anything. Worse, cost alerts are evaluated only about once every
24 hours, so an agent stuck in a loop overnight is discovered the next morning,
after the money is already spent.

That combination, an unbounded loop and a warning that arrives a day late, is
exactly the failure we study in this course. It would be a poor lesson to fall
into it ourselves.

### So what actually bounds your spend

Three layers, in order of how well they work.

| Layer | Stops spending? | How fast |
|---|---|---|
| **TPM quota on the deployment** | Yes, genuinely | Immediately, per minute |
| Spending limit on a credit subscription | Yes, disables the subscription | When credit runs out |
| Budget alert on Pay As You Go | **No, email only** | Up to 24 hours late |

The first one is the real control, and almost nobody sets it deliberately. We
will. It is one slider, in section 4.

---

## 2. Which subscription to use

**Start with the Azure free account.** It comes with trial credit, and the
important part is that its **spending limit is on by default**. That means if you
somehow burn through the credit, the subscription disables itself rather than
charging you. For a student learning this for the first time, this is the safest
possible place to start, and it is where I built and rehearsed everything.

When the trial credit or its time window runs out, you have a choice:

- **Stay on a credit based subscription** if you have access to one, for example
  an institutional subscription. There is nothing wrong with this.
- **Move to Pay As You Go** only after you have set the TPM cap in section 4.
  Without that cap, you are running an unbounded liability against your own card.

There is no shame in the first option and no danger in the second, as long as the
TPM work in section 4 is done first.

---

## 3. Create the resource, in the right portal

There are now two Foundry portals, and only one of them is worth learning.

- **Foundry (classic)** is the older hub based experience that grew out of Azure
  AI Studio. It still works, but it is in maintenance mode.
- **Foundry (new)** is the project first experience. Everything Microsoft is
  actively building, the agent service, evaluations, the new model catalogue,
  observability, is wired up around Foundry projects first.

**Create a Foundry project, not a hub project.** Hub projects exist only for
backwards compatibility. If a tutorial tells you to "create a new hub", it was
written for the old portal, and you should find a newer one.

### Portal route (what I recommend you do)

This is the click through path, and it is the one I use in class.

1. Sign in to the Foundry portal. **Make sure the New Foundry toggle is on.**
2. Choose **Create project**. Give it a name. Use `cse476` so yours matches mine
   and the examples in this file.
3. When it asks, create a **new resource group** named `cse476-rg`. Keeping
   everything in one group means you can delete the entire thing in one action at
   the end, which section 9 relies on.
4. Pick a location. `eastus` is a safe default. Only use `westus3` if you
   specifically want to try instant models, which skip the deployment step.

The portal creates the parent Foundry resource for you. You do not need the CLI
for any of this, but if you prefer a reproducible script, the CLI route is below.

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

`--allow-project-management` **cannot be changed after creation.** Miss it and
you have to rebuild the resource. It is the flag that makes this a Foundry
resource rather than a plain AI services one.

---

## 4. Deploy a model with a deliberately small TPM

This is the step that actually protects you, and it is one slider.

Quota is assigned per subscription, per region, per model, in units of tokens per
minute (TPM). **The TPM you assign to a deployment is the enforced rate limit on
that deployment.** Requests past it are throttled, not billed. That is why it is
a real spending control and a budget alert is not.

Deploy one small, cheap model with a small cap:

```bash
az cognitiveservices account deployment create \
  --name cse476-foundry \
  --resource-group cse476-rg \
  --deployment-name chat-demo \
  --model-name gpt-5-mini \
  --model-format OpenAI \
  --sku-name GlobalStandard \
  --sku-capacity 10
```

**Note the model choice, this is a real trap I hit.** The obvious cheap pick used
to be `gpt-4o-mini`, and many tutorials still tell you to deploy it. In the
current catalogue it is marked **Deprecated**, which means it still runs today
but has a retirement date, after which the deployment simply stops answering,
possibly in the middle of the semester, with nothing in your code to explain why.
Before you deploy anything, check the **Lifecycle** column in the model
catalogue and pick a model marked **Generally Available**. `gpt-5-mini` is, which
is why we use it. In the portal, this is the model list on the deploy dialog; the
Lifecycle label is right there next to each model.

`--sku-capacity 10` is **10,000 TPM.** Each unit is 1,000 TPM, and the minimum is
1. In the portal, this is the "Tokens per Minute Rate Limit" slider on the deploy
dialog. Set it low on purpose.

### Work out your own worst case

Do this arithmetic once, because it turns an unbounded worry into a number you
can actually look at.

```
worst case tokens per month = TPM x 60 x 24 x 30
```

At 10,000 TPM that is about 432 million tokens a month, and only if the
deployment ran flat out, every second, for thirty days straight, which it never
will. Multiply that by the per token price for your model from the Azure pricing
page to get your absolute ceiling. Your real classroom usage will be a tiny
fraction of it. The point is not the exact number, it is that you now know the
worst case instead of hoping.

Deploy **one** model, not four. Every extra deployment is another unbounded
surface, and everything in this course needs only one.

### If the TPM slider is stuck at 0

That means your subscription has no quota for that model in that region. It is
common on brand new and free subscriptions. Check what you have:

```bash
az cognitiveservices usage list -l eastus
```

Then either request a quota increase for that model and region, or pick a
different region where you already have quota. Do this **a few days ahead**, not
the night before you need it, because quota requests are reviewed one at a time
and can take time.

---

## 5. Add budget alerts as a second layer

Budget alerts do not stop anything, but they are still worth twenty minutes as a
backstop behind the TPM cap.

In the portal: **Cost Management + Billing**, then **Budgets**, then **Add.**
Scope the budget to the `cse476-rg` resource group, not the whole subscription,
so the number actually means something.

Set four thresholds:

| Type | Threshold | Why |
|---|---|---|
| Actual | 50% | Early awareness |
| Actual | 80% | Time to act |
| Actual | 100% | You are over |
| **Forecast** | 110% | **Fires days before the actual alerts** |

The forecast alert is the useful one. Actual alerts are evaluated only about once
a day; the forecast alert fires as soon as Azure projects you will cross the
line, which can be several days earlier.

Set the amount to something you would genuinely notice. For a demo or student
account, keep it low.

---

## 6. Wire it into the course repo

Get the endpoint and key from the Foundry portal, then put them in your `.env`:

```
PROVIDER=foundry
AZURE_OPENAI_ENDPOINT=https://cse476-foundry.openai.azure.com/openai/v1/
AZURE_OPENAI_API_KEY=your-key-here
MODEL=chat-demo
```

**Note the endpoint form.** This course uses Foundry's OpenAI compatible **v1**
surface, so the endpoint ends in `/openai/v1/` and there is **no** `api_version`
line. The code uses a plain OpenAI client with a `base_url`, the same client that
talks to the free lanes, not the older `AzureOpenAI` class. That is why there is
nothing here about API versions.

You do not have to get the endpoint exactly right by hand. The lane code
normalises it: if you paste what the portal shows you, even if it ends in
`/responses` or is just the bare host, the code trims it and adds `/openai/v1/`
for you. So paste the portal value, and it will work.

**`MODEL` must be your deployment name, not the model name.** You deployed
`gpt-5-mini` and named the deployment `chat-demo`, so `MODEL=chat-demo`. Getting
this wrong produces a 404 that reads as though the model does not exist, and it
catches everyone exactly once. If you see that 404, this line is why.

Then verify:

```bash
python setup_check.py
```

You want the `foundry` lane to show `credential present` and the live call to
pass. Once it does, your Foundry setup is real and working.

For day to day coursework you can switch `PROVIDER` back to `github` (the free
lane) so you are not spending Foundry quota on every small experiment, and switch
to `foundry` when you specifically want to run on Foundry. Because the lane is one
setting, flipping between them costs you nothing and changes no code.

---

## 7. A quick pre run checklist

Before you rely on the Foundry lane for anything that matters, confirm:

- [ ] `python setup_check.py` passes with `PROVIDER=foundry`, and the live call
      returns a real reply
- [ ] You can see both the **deployment name** (`chat-demo`) and the **model
      name** (`gpt-5-mini`) in the portal, so the distinction in section 6 is
      concrete for you
- [ ] The model catalogue and playground load quickly on your connection
- [ ] Your TPM cap from section 4 is set, and you have done the worst case
      arithmetic once so the number is not a mystery

If all four are true, you have a working, bounded, professional Foundry setup,
the same one used throughout this course.

---

## 8. Things that changed, so tutorials will contradict each other

Three facts worth having in your head, because you will find older tutorials that
disagree, and you should know which one is current.

**The rename.** Azure AI Studio became Azure AI Foundry at Ignite 2024. Azure AI
Foundry then became **Microsoft Foundry** at Ignite in November 2025, formalised
in the January 2026 product terms. It is the same platform, the same resource
type, and the same keys throughout. Azure AI services is now called **Foundry
Tools**. When searching for help, search both the old and new names.

**The Assistants API retires on 26 August 2026,** which is inside our semester.
Do not build anything on it. Use **Foundry Agent Service** and the Responses API
instead. If a tutorial is built on Assistants, it is legacy.

**The SDK split.** `azure-ai-projects` 2.x is incompatible with 1.x. Sample code
written for the classic portal will not run against a new Foundry project. Check
which one a sample targets before you spend time debugging it.

---

## 9. Delete it when you are done

Everything is in one resource group, which is exactly why section 3 put it there.
When the course is over, or whenever you want to stop any chance of charges:

```bash
az group delete --name cse476-rg --yes
```

One caution: deleting a resource this way skips the normal check that deployments
are removed first. When that happens, the quota allocation stays unavailable for
about 48 hours until the resource is fully purged. So if you intend to rebuild
right away, delete the **deployments** first, then the group.

Cleaning up is not optional housekeeping. An account you have stopped using but
never deleted is the most common way people get a surprise bill months later. If
you are done, delete it.
