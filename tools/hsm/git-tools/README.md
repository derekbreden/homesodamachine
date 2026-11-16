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
```

Each link is an [Agent Trace](https://agent-trace.dev) record, one JSON object per line
of a git note on `refs/notes/agent-trace`, attached to the commit that rewrote the lines.
The record names the file and line range in that commit; its `related` link of type
`derived_from` is a GitHub permalink to the line it was rewritten from, and an optional
note sits under `metadata."com.homesodamachine"`. `git why link` writes one and pushes the
notes, merging any links pushed meanwhile. A trail that ends at a commit carrying links,
none of them for this line, says so and prints the `link` command that records it.
A checkout that has never fetched the notes takes them from origin on its first run.

The enclosure's Rust port, `cd432f36f`, carries links for the settings it moved under the
same name and value from a single hand-written source.

Build and install it like the other tools:

```sh
tools/run -- cargo build --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-git-tools --bin git-why
hsm-run --install-tools "$PWD" tools/hsm/target/release/git-why
```
