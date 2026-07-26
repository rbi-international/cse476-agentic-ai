# Why we are doing all of this

Read this first. Before the setup, before the code, before any of it. It is
short, it has no commands in it, and it is the only document in the whole
repository where I get to just talk to you.

---

## A small story

The year is 2027. You have just started at a company, and on your first morning
your manager, a tired woman named Captain Rao who has clearly not had enough
coffee, drops a problem on your desk.

"Three suppliers," she says. "One of them keeps delivering late and it is
costing us. Find out which one, and draft the email that lights a fire under
them. I have a meeting. Go."

Then she leaves.

Notice what she did not do. She did not tell you which spreadsheet to open. She
did not say "first check the delivery records, then sort by date, then compare."
She gave you an **outcome** and walked away, trusting you to work out the steps.

That, right there, is the entire course.

For seventy years, computers have been the opposite of that. You did not give a
computer a goal. You gave it exact, dead-literal instructions, and if you got one
semicolon wrong it fell over and blamed you. Computers were the world's most
powerful, most obedient, most profoundly unimaginative interns.

What changed, and why you are in this room, is that we can now build software
that behaves a little more like you did with Captain Rao. Software you can hand a
goal to. Software that decides its own next step, uses tools, checks whether it
worked, and tries again. We call it an **agent**, and by December you will have
built several, broken them on purpose, and fixed them.

---

## Meet the cast

You are going to spend fifty hours with a handful of recurring characters. I
introduce them properly in the lectures, but here they are, so you know who is
who.

**The Model.** Think of it as a brilliant, well-read intern who has memorised
half the internet, answers instantly, and has two enormous flaws. One: it cannot
actually *do* anything. It can only talk. It cannot open a file, check a price,
or send an email, no matter how confidently it describes doing so. Two: it has
the memory of a goldfish. Every single time you talk to it, it has completely
forgotten the last thing you said, and you have to hand it the entire
conversation again, like introducing yourself to a colleague who has amnesia,
every morning, forever.

Sounds useless? It is not. It is the most useful goldfish in history. But you
have to build everything *around* it, and that everything is what we are here to
learn.

**The Tools.** These are the intern's hands. A tool is just a normal function
you wrote, that you decided to let the Model ask for. Give it a tool to check
the database, and suddenly the talker can act. Take away its tools and it is back
to being a very articulate paperweight.

**The Loop.** This is the engine. Think, act, observe, repeat. It is what turns
"answer one question" into "keep working until the job is done." It is also, and
I cannot stress this enough, the thing that will happily spend all your money if
you forget to tell it when to stop. You will watch this happen. Live. In class.
It is very funny right up until it is your credit card.

**The Guardrails.** Every good story needs someone sensible. The Guardrails are
the boring, essential character who says "you have tried the same thing four
times, it is not working, please stop" and "no, you may not send an email, you do
not have an email tool" and "we are twelve rupees from the spending limit,
perhaps calm down." Nobody thinks about the Guardrails until the day they save
everything. Unit 6 is basically a love letter to them.

---

## The honest part, because you will figure it out anyway

Here is the thing the flashy demos on the internet will not tell you.

Making an agent that works *once*, on the demo machine, with the demo question,
is easy. I could teach you that in an afternoon and you would leave feeling like
a wizard.

Making an agent that works *reliably*, for a thousand different users, without
leaking data, inventing facts, looping forever, or getting talked into things it
should not do, is the actual job. That gap between the flashy demo and the
reliable system is where the entire second half of this course lives, and it is
also where the entire salary lives. The people who can only do the afternoon
version are a dime a dozen. The people who can do the reliable version get hired.

So when we spend a whole unit on testing, and another on security, and I keep
making you write down what your agent should say when it *fails*, that is not me
padding the syllabus. That is me handing you the part that pays.

---

## How I am going to teach this

Three promises.

**Layman first, then the real thing.** Every single concept, you get the simple
human version first, the intern and the goldfish and the shop, and only then do I
put the proper technical name on it. If I ever give you jargon before the idea, I
have failed, and you are allowed to say so.

**We break things on purpose.** I am not going to hand you working code and
explain why it works. That produces students who can run my code and cannot write
their own. Instead we write the naive version together, we run it, it breaks in a
specific and educational way, and *then* we fix the actual cause. You will
remember the fix because you watched it hurt.

**I use AI to build this, and I check every line.** This is a course about
building things with AI. It would be strange, and honestly a bit dishonest, if I
pretended I built all of this by hand in a cave. I use AI assistance heavily to
produce these materials, and then I verify every claim against code that actually
runs before it reaches you. That is not cheating. That is exactly the workflow I
am trying to teach you: use the powerful tool, then check its work, because it is
a brilliant goldfish and brilliant goldfish are confidently wrong all the time.
If you learn nothing else this semester, learn that.

---

## What you will be able to say in December

Not "I did a course on AI agents." Anyone can say that.

You will be able to say: "I built a multi-agent system. Here is the live link.
It is instrumented, so here is a trace of a real request going through it. It
runs with least privilege, so here is exactly what it is *not* allowed to touch.
It caught a prompt-injection attack during testing, and here is the fix I wrote."

That sentence is the whole point of the next fifty hours. Everything in the
syllabus, every deck, every broken-on-purpose notebook, exists to make that
sentence true for you.

Captain Rao would hire that person on the spot.

Now go do the setup. It is dry, I know. But it is the boring bit that makes all
the fun bits possible, and the fun starts in Lecture 1.

See you in class.
