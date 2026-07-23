# Practical 2: Conversational hotel information agent

**Unit 1. Assessed.**

Extend `notebooks/u1/l1_first_agent.ipynb` into something that survives contact
with a real conversation.

## Requirements

1. **A third tool of your own.** Function, `REGISTRY` entry, and `TOOL_SCHEMA`
   entry. Forgetting the third of those is the most common mistake.
2. **Multi turn.** The agent holds a conversation rather than answering once.
   "What about the 15th?" must work without repeating the hotel name.
3. **Honest failure.** When asked something no tool can answer, it says so
   rather than inventing an answer.
4. **A termination guard** with a value you chose, and one sentence in your
   notebook saying why that number.

## The experiment you must include

Write one tool description deliberately vaguely. Ask a question that should route
elsewhere. Record which tool the model picked. Then fix the description and record
it again. Two cells, both with outputs.

This is the practical asking you to prove that a tool description is an
instruction, not documentation.

## Viva questions come from these

- Why is this an agent and not a script?
- What stops your loop?
- What happens if the model requests a tool you did not define?
- Show me the only line in your notebook where code actually executes.
