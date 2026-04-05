---
name: No shotgun debugging
description: Don't make multiple speculative changes at once — test one thing at a time, methodically
type: feedback
---

Don't make multiple speculative changes at once. Test one hypothesis at a time.

**Why:** A prior agent made ~8 changes simultaneously (buffer sizing, connection gating, boot timing, retry logic, send timeouts, re-sync code) without testing any individually. When the build still didn't work, there was no way to know which changes mattered and which introduced new bugs. The user and a reviewing agent both flagged this as "shotgun debugging."

**How to apply:** When debugging hardware/firmware issues: (1) identify the simplest possible test that isolates one variable, (2) make that one change, (3) flash and test, (4) observe results before making the next change. If you're about to modify more than 2 things at once, stop and reconsider. The cost of an extra flash cycle is much lower than the cost of an untraceable regression.
