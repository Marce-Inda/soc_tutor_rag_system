# Universal Agent Harness (UAH) Library

This library provides a standardized control layer for autonomous AI agents. It implements "Harness Engineering" principles to ensure that agents remain deterministic, safe, and efficient.

## Key Pillars

1. **Loop Detection**: Prevents agents from executing the same tool with the same arguments repeatedly, saving tokens and preventing hangs.
2. **Artifact Indexing**: Maintains a session-long "Source of Truth" for technical findings, preventing "instruction fade-out" and hallucinations.
3. **Strategic Deliberation**: Forces the agent to output a plan before interacting with tools, improving reasoning quality.
4. **Context Monitoring**: Tracks session health and turn counts to trigger maintenance or summaries.

## How to use

1. Import the `UniversalAgentHarness` class into your orchestrator or agent.
2. Initialize it with a `session_id`.
3. Wrap your agent's tool execution loop with `check_loop()`.
4. After each agent response, call `extract_and_index()` to save findings.
5. In your system prompt, inject the results of `get_ground_truth_prompt()`.

## Example

```python
from UAH_BOILERPLATE import UniversalAgentHarness

harness = UniversalAgentHarness("session_001")

# Before action
if not harness.check_loop("read_file", {"path": "config.json"}):
    # run tool...
    harness.extract_and_index("Found config key EV_KEY_123")
```

---
*Created for the SOC Tutor Project - 2026*
