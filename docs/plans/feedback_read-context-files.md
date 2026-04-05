---
name: Always read the relevant context file before starting work
description: Agents repeatedly fail to read context-hardware.md / context-firmware.md / context-ios.md before starting tasks, missing critical info like the CadQuery venv path
type: feedback
---

Before starting any task, read the context file that matches the domain (listed in MEMORY.md under "Context Files"). Do this before writing code, running scripts, or spawning subagents.

**Why:** Multiple agents have wasted time by not reading these files — e.g., trying system python instead of `tools/cad-venv/bin/python` for CadQuery, which is documented in context-hardware.md. The context files contain non-obvious operational details that can't be derived from the code alone.

**How to apply:** At the start of every task, identify which domain applies (firmware, iOS, hardware) and `Read` the corresponding context file. If spawning subagents, include the relevant context in the prompt rather than expecting the subagent to find it.
