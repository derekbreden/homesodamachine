---
description: Open on the ugly board, take one body, move its whole chain, commit. The routing session's opening act.
argument-hint: [body or run to take — omit to take the board's worst]
disable-model-invocation: true
---

You are moving one body in the enclosure. Not diagnosing one, not pricing one — moving it.

Requested: **$ARGUMENTS**

## 1. Open on the board

```
python3 hardware/printed-parts/enclosure/enclosure-assembly/ugly.py
python3 hardware/printed-parts/enclosure/enclosure-assembly/ugly.py --runs
```

`debt` is what a body owes — every run standing on it the stock cannot bend. `=` on a binding
corner means its own leg is the whole of its limit; `<` means a neighbour is taking part of
the share. `leg` against `wants` is the reach that corner is short by.

If the footer says STALE, rebuild before you read it.

Then read `calibration/Chain.md` in full. It is short, and the rest of this command assumes
it.

## 2. Take the body

If `$ARGUMENTS` names one, that is the body. If it does not, take the board's top row and say
in one line what the board says about it — which runs, which corners, how short.

Then look at it before you touch it:

```
tools/look.sh <body>[,<body>...]
```

## 3. State the target as a condition

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
`ugly.py` and show the row that changed.
