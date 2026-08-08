---
description: Open on the scorecard, take one failing check, move whatever chain it takes to fix it, commit. The routing session's opening act.
argument-hint: [check or run to take — omit to take the worst one on the board]
disable-model-invocation: true
---

You are fixing one thing in the enclosure. It is the assignment. Whatever has to move for the
machine to hold it is the work, however far from the check that turns out to be.

Requested: **$ARGUMENTS**

**"The problem is elsewhere" is not an answer here.** A whole bunch of elsewheres is the task.
Something is broken; something moves. If you finish the turn with it no better and no
committed state, you have spent it.

## 1. Open on the board

The board is the committed sidecar beside the assembly — the same figures the build prints and
the viewer's bottom bar reads, at the cost of a file read.

```
jq -r '.checks[] | "\(.status)  \(.id)  \(.value)"' hardware/manifold-layout/front-half.scorecard.json
```

Then the offenders under whichever ones read `fail`:

```
jq -r '.checks[] | select(.status=="fail") | "\(.id)  \(.value)", (.detail[] | "    \(.)")' \
  hardware/manifold-layout/front-half.scorecard.json
```

`source.generated` and `source.commit` in the same file say which build wrote it. If the tree
has moved since, rebuild before you read it:
`tools/cad-venv/bin/python hardware/manifold-layout/front_half.py`.

Then read `calibration/Chain.md` in full. It is short, and the rest of this command assumes
it.

## 2. Take one

If `$ARGUMENTS` names a check or a run, that is the assignment. If it does not, take the worst
failing check — the one furthest from its own value.

Then open it and look. The runs carry their own row, port to port:

```
jq -r '.bends[] | select(.id=="<run>")' hardware/manifold-layout/front-half.scorecard.json
tools/look.sh <run>,<its two end bodies>
```

A check's `detail` names the bodies it fails on. They are candidates. The bodies that have to
move may not be any of them — a fix is often a body the check never names.

## 3. State the target as a condition

The goal is fixed — the scorecard states it and it is not yours to move. What needs stating is
the condition on whatever you are moving to get there.

Not `coil-v-a at y 240`. `coil-v-a far enough aft that fluid-4 passes the pair with a full
floor either side`. A number cannot be iterated on, because a miss says nothing about which
way to go.

Write it down before you edit anything.

## 4. Print the chain

Every derivation that reads the body you are moving, and everything reading those. Grep the
function, grep its callers, and keep going until the list closes. Print it.

Walk it yourself — no subagents, on this step or any other in this command. A subagent
returns a report, and a report is prose about a state that does not exist. The chain is also
the thing you have to be holding whole when you move it, and a summary of it is not it.

If a link has no answer you can derive, **that link is the turn** — send that one line and
stop. It is what Derek needs and it is the only thing in the turn he needs.

## 5. Move all of it, once

One commit. Build once. `pack-closes`, `lines-clear`, `bend-radius`, `port-leads` and the rest
of the gates are exact and they are the oracle — you do not need to approach them by sampling,
and a Stop hook will catch you if you try.

Moving one link and letting the build price the wreckage is the failure this command exists to
prevent.

## 6. Red is committed red

If the whole move is built and the gates go red, commit it and name in the message the link
you could not re-answer and what it did to the gates. `git revert` is Derek's, not yours. A
reverted red is the one artifact he can read, destroyed.

Then look at what you landed and read the render — not the tables.

## 7. End on what is on main

Not on an offer. `calibration/Discretion.md` if that sentence needs explaining.

Lead with the state: what moved, what the gates say now, what the board says now. Re-read the
sidecar and show the row you were given, at whatever it now reads.
