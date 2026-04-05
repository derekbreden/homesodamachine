---
name: "Starting point" means copy the file, not reinvent
description: When told a file is the starting point for a new part, copy it verbatim — do not design something new
type: feedback
---

When the user says "our starting point will be [existing file]", copy that file's code exactly into the new location. Do not interpret "starting point" as inspiration or structural guidance — it means the literal code is the baseline and will be modified from there.

**Why:** The user plans to iteratively modify the copied code toward the new part. Inventing new geometry throws away the dozen features already in the source file and ignores the user's direction.

**How to apply:** Copy the source script verbatim, change only the output filename/path, commit, then wait for the user to direct changes.
