# Shared-checkout Git operations

`hsm-land` lands commits on `origin/main` and brings incoming files into the shared
checkout while retaining edits and staged work. Diverged commits are merged as Git
objects. The command creates no project worktree.

```sh
hsm-land --check
hsm-land
```

The existing post-commit hook calls this command synchronously. A generated file,
one a producer in the build graph writes whole, takes main's copy when both sides
changed it, since it regenerates from source. A document a producer rewrites keeps
authored text and merges like any other. A text collision is left in the working
file with the incoming commit named. `ORIG_HEAD` retains
the local commits that need resolution. The native `hsm-merge-pointers` command
merges CAD publications by member.

`hsm-land --commit-snapshot FILE.json` commits selected frozen Git blobs locally:

```json
{"message":"publication message","files":[{"path":"hardware/example.json","blob":"GIT_BLOB_ID","mode":"100644"}]}
```

The operation uses a private index and updates the shared index under Git's
existing index lock. Selected entries that matched the previous HEAD take the
frozen blob; intentional staged changes remain staged. Working files stay in
place, including newer outputs produced during an upload. It returns JSON with
`commit` and `changed`. After it returns and releases its locks, the publisher
runs `git hook run post-commit` and verifies remote ancestry.

Focused Git fixtures run on demand:

```sh
tools/run -- cargo test --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-git-tools
```

## Commit messages

End the message with one trailer block.

```text
Session: <session title>
Model: <app, model, effort>
Derek: "<his words, exactly as typed>"
Derek: "<another passage, with ... marking a cut; a long one wraps onto
 lines that start with a space>"
Co-Authored-By: <the harness's line, when it adds one>
```

`python3 ~/Developer/claude-code-setup/jsonl2md/jsonl2md.py whoami` prints the
session title, then the `Model:` line as the commit carries it. It marks an unnamed
title `(auto-generated)`. In a cloud session
the `Claude-Session:` link names the session. Quote a passage from Derek exactly
for each request the commit answers. Omit `Derek:` for a commit he did not request.
Read the passages with `git log --format='%(trailers:key=Derek)'`.

The commit that sets a value says what it does on the part and where its evidence
is. A commit that moves a setting carries Derek's original words with it. When a
rewrite breaks blame, record the link with [`git why link`](#following-a-line-past-a-rewrite).

An instruction is a setting on the agents who read it. The commit that adds, rewrites
or removes one says what an agent did that led to it, in which app and on which model,
and what a session does differently once it reads the new text. A removal says what
was seen while the line was in. A rewrite or move records its `git why link`.

## Following a line past a rewrite

`git why` follows a line back past the commits where git loses track of it. It runs
`git blame`; where the commit it lands on rewrote lines git can't follow, such as a port
to another language, it reads that commit's link records and blames again from the line
each was rewritten from. It stops at the commit that set the line and prints each hop
with that commit's message and its `Derek:` lines.

```sh
git why hardware/printed-parts/enclosure/enclosure/back-top/supports.rs '/^const METER_HOUSING_FIT/'
git why PATH:LINE
git why PATH LINE --rev REV --json
git why link COMMIT:PATH:LINE[-END] FROM-COMMIT:FROM-PATH:LINE[-END] --note TEXT
git why origin COMMIT:PATH:LINE[-END] --note TEXT
```

Each link is an [Agent Trace](https://agent-trace.dev) record, one JSON object per line
of a git note on `refs/notes/agent-trace`, attached to the commit that rewrote the lines.
The record names the file and line range in that commit; its `related` link of type
`derived_from` is a GitHub permalink to the line it was rewritten from, and an optional
note sits under `metadata."com.homesodamachine"`. `git why link` writes one and pushes the
notes, merging any links pushed meanwhile. `git why origin` records why a line begins in a
commit, such as a setting the port introduced or a unit conversion. `git why` ends the
trail at that line and prints the note. For a line still missing a record in a documented
rewrite, it prints the `link` command.

A checkout fetches the notes on its first `git why` run. Refresh an existing checkout
with `git fetch origin refs/notes/agent-trace:refs/notes/agent-trace`.

The Rust ports' records point to the earlier hand-written lines that set or computed
their values. When an earlier rewrite also has a record for the line, `git why` follows
both. The instruction guides' records tie each line that `6a685efd1a` and `9685395782`
reworded or put back to the root instruction it came from.

Build and install it like the other tools:

```sh
tools/run -- cargo build --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-git-tools --bin git-why
hsm-run --install-tools "$PWD" tools/hsm/target/release/git-why
```
