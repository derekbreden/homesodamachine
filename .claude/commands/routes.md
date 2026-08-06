---
description: Open on the ugly board, take one RUN, move whatever chain it takes to fix it, commit. The routing session's opening act.
argument-hint: [run to take — omit to take the board's worst]
disable-model-invocation: true
---

You are fixing one run in the enclosure. The run is the assignment. Whatever has to move for
it to reach its stock's radius is the work, however far from the run that turns out to be.

Requested: **$ARGUMENTS**

**"The problem is elsewhere" is not an answer here.** A whole bunch of elsewheres is the task.
The run is broken; something moves. If you finish the turn with the run no better and no
committed state, you have spent it.

## 1. Open on the board

```
python3 hardware/printed-parts/enclosure/enclosure-assembly/ugly.py
```

Runs, worst first. `binding` is the corner holding each one down and what that corner needs —
`reach` is short of leg, `share` is a neighbour taking part of the leg, `REVERSAL` turns back
on itself and no leg length fixes it. `[n]` beside an end body is what else that body carries.

If the footer says STALE, rebuild before you read it.

Then read `calibration/Chain.md` in full. It is short, and the rest of this command assumes
it.

## 2. Take the run

If `$ARGUMENTS` names one, that is the run. If it does not, take the board's top row.

Then open it and look:

```
python3 hardware/printed-parts/enclosure/enclosure-assembly/ugly.py <run>
tools/look.sh <run>,<its two end bodies>
```

The second table is the leverage: the bodies that run stands on, and how many other runs the
same move would pay off. They are candidates. The bodies that have to move may not be either
of them — a run's fix is often a body it never touches.

## 3. State the target as a condition

The run's own goal is fixed: every corner at its stock's minimum. What needs stating is the
condition on whatever you are moving to get there.

Not `Y-F at x 108.6`. `Y-F far enough west that fluid-21 leaves on carb-1's riser's west
side`. A number cannot be iterated on, because a miss says nothing about which way to go.

Write it down before you edit anything.

## 4. Print the chain

Every derivation that reads the body you are moving, and everything reading those. Grep the
function, grep its callers, and keep going until the list closes. Print it.

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

Lead with the state: what moved, what the gates say now, what the board says now. Re-run
`ugly.py` and show the run's row — the one you were given, at whatever it now reads.
