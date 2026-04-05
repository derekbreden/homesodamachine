---
name: CAD scripts — no validation, no documentation bloat
description: CadQuery scripts should be lean code only — no Validator, no FEATURE_TABLE, no rubric headers, no stale docstrings
type: feedback
---

Do not add Validator/step_validate sections, FEATURE_TABLE blocks, or Rubric headers to CadQuery scripts. The user verifies STEP output in a CAD viewer — self-validation was a failed experiment that wasted tokens without catching real spatial errors.

**Why:** The AI cannot verify its own spatial reasoning. Validation checks only confirm the geometry matches the code — not that the code describes something physically correct. The user still has to check every STEP file in CAD anyway.

**How to apply:** CadQuery scripts should contain: imports, parameters, modeling code, STEP export. Comments are fine when they add information not already in variable/constant/function names. Do not duplicate information across docstrings, feature tables, and code. Remove the `revisions/` archive folders — git history is sufficient.
