---
name: No comments — names must be self-documenting
description: User strongly prefers self-documenting names over comments in code
type: feedback
---

Do not add explanatory comments to code. Names of variables, functions, and constants should explain what is happening and what the intent is. Section headers (e.g. `# ── Tower ──`) are acceptable for visual structure, but no inline explanations.

**Why:** "Comments are a refuge for those who failed to name things properly, and always go stale, and always make things worse."

**How to apply:** When writing or cleaning up code, invest in clear naming instead of adding comments. If a name doesn't explain itself, rename it — don't annotate it. Docstrings on helper functions are acceptable if they describe *what* the function returns, not *how* it works internally.
