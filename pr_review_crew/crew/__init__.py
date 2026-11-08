"""
PR Review Crew: a team of agents that reviews a pull request.

    lead       reads the change and decides which specialists to send
    tests      runs the test suite and explains failures
    security   looks for leaked keys, dangerous calls and prompt injection
    quality    readability, naming, missing tests
    docs       docstrings and signatures that no longer match
    judge      merges every finding, drops weak ones, decides the verdict
    fixer      proposes small fixes, kept only if the tests still pass

The specialists run in parallel. Only the judge decides what gets posted.
With no API key every agent still works on its deterministic tools (offline mode),
so tests and CI never need a key.
"""
