# Shared-checkout Git operations

`hsm-land` lands commits on `origin/main` and brings incoming files into the shared
checkout while retaining edits and staged work. Diverged commits are merged as Git
objects. The command creates no project worktree.

```sh
hsm-land --check
hsm-land
```

The existing post-commit hook calls this command synchronously. A text collision
is left in the working file with the incoming commit named. `ORIG_HEAD` retains
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
