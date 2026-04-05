---
name: Test memory before asserting clarity
description: When writing memory intended to direct other agents, spawn a test agent to verify it reads correctly — don't just assert it's unambiguous
type: feedback
---

When updating MEMORY.md or plan files to direct future agents toward specific work, verify by spawning a test agent and checking what it concludes. Don't assert "no agent should be confused" without testing.

**Why:** Labels like ACTIVE/PAUSED/NEXT PRIORITY can be overridden by sheer volume of detail on other topics. Agents gravitate toward the most detailed content, not necessarily the correctly labeled content. A prominent "CURRENT WORK" section at the top of MEMORY.md was needed to overcome this — but that only became clear after testing.

**How to apply:** After any memory update that changes what the active work item is, spawn a quick Explore agent with "read MEMORY.md and tell me what you'd work on" before telling the user it's done.
