# Editing code and documentation

Describe the current state. Git keeps the history. Explain a choice against
alternatives only when asked. Keep numbers in the constant, program or measurement
that owns them. Comments and docs point there. The costs ledger keeps the figures
the site shows.

When writing or editing source code, follow the [source comment guidance](source-comments.md).
Settings files hold values. A setting's commit records its purpose and evidence
according to the [Git conventions](../tools/hsm/git-tools/README.md#commit-messages).

## Purpose

Give each program, build step, check, report, cache and lock a present-tense line
where it is defined saying what it is for. Add that line before building on it.
Remove machinery whose purpose has gone. When a one-off script fills a gap in
the repo's tools, Derek decides whether it joins the repo. The [part positioning
example](principle/Positions.md) shows how such a gap comes to light.

When Derek identifies a class of obsolete work, trace why the example persisted
and investigate the other instances. Retiring a design includes its unused catalog
identities, relationships, publication entries and agent-facing commands.
