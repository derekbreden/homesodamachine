# Editing code and documentation

Describe the current state. Git keeps the history. Explain alternatives only when asked.
Keep numbers in their owning constant, program or measurement. Point there from prose.

When writing or editing code, follow the [source comment guidance](source-comments.md).
Settings files hold values. Record a setting’s purpose and evidence [in its commit](../tools/hsm/git-tools/README.md#commit-messages).

## Purpose

Give each program, build step, check, report, cache and lock a present-tense line
at its definition saying what it does for the project. Add it before building on it.
Remove machinery whose purpose has gone. Derek decides whether a [one-off tool](principle/Positions.md) joins the repo.

When Derek identifies a class of obsolete work, trace why the example persisted and
find the other instances. Retire a design’s unused catalog identities, relationships,
publication entries and agent-facing commands with it.
