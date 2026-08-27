# model

The session [`Model.md`](../Model.md) quotes, as a clean transcript — user and assistant
turns, no tool calls. The filename is the session's own title, so it is also retrievable
live:

```
python3 ~/Developer/claude-code-setup/jsonl2md/jsonl2md.py export-session "Manager"
```

Read `Model.md` first. Come here for the three asks in their room — what Derek typed, what
the manager passed to each agent, and what each agent reported back.

| Session | What it holds | Find |
| --- | --- | --- |
| [Manager](Manager.md) | One manager, one night, one file. Three geometry asks briefed out within an hour of each other, differing in what they say after the operation. | `whatever it is called` |

| Ask | What it says | Find |
| --- | --- | --- |
| MQ6 | Operation and purpose | `such that the MQ6 supports print vertically` |
| Plate | Operation only | `from the Z- face instead of from the Z+ direction` |
| Corbel | Neither | `whatever it is called` |

All three are Derek's own words, forwarded to the agents nearly verbatim. The MQ6's purpose
clause is what its agent checked its own signs against, and it says so: `the way the outcome
clause asks`. The corbel agent reaches the same kind of statement on its own — `far -
wall_aft_y`, the leg read off the tee wall rather than typed — one round after it began, in
the identification message at `GENERATING FEATURE`.

The plate ask is the one that isolates the variable. It names its operation exactly and
stops there, and the agent's report at `FRONT_RIDER` is a clean account of that operation
carried out.

The corbel's last defect is worth reading in place. Search `0.9956`: the lane that made it
could not see it, because the over-cut that broke retention is what turned its own clash
check green.

The shas the agents quote in this transcript are the ones they wrote under, and a history
rewrite has moved all of them since — `git cat-file -e` fails on every one. `Model.md` cites
this tree's own. To follow a sha from the transcript into the current history, look it up in
[`tools/git-history/commit-map`](../../tools/git-history/commit-map), which holds an
`old new` pair per line:

```
grep -E '^27a7c995' tools/git-history/commit-map
```
