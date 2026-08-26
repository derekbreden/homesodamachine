# Model

Derek wants a reminder of the value, in 3D model work, of speaking in terms of the specific **model change** — the construction operation — not just the resulting **geometry change**. Describing only the end shape ("rotate it so the lid is the most-negative-Z thing; move the midpoint screw holes") leaves the operation ambiguous, and the agent fills that gap in its own frame (the CAD coordinates) instead of Derek's (the finished printed part). It took three rounds to land a one-operation change.

## The foam cap

- **Derek asked for:** the foam-cap-bottom to seat mouth-down — lid the most-negative-Z layer — so the whole cap screws to the bottom of the shell, lid and all; "simply move the midpoint screw holes"; the pour hole about twice the diameter; and a foam-assembly STEP to check before printing.
- **Agent built** (`c7350952`): the assembly and a mouth-down bottom cap — but moved *both* midpoint screws to the same +X side, making the shell and both caps symmetric and changing the shell's bosses.
- **Derek clarified:** both mid screws on +X don't line up; restore the bosses and the top cap to original; only the *bottom's* midpoint screws should move.
- **Agent built** (`9b4db4d0`): split the shell's midpoint bosses across *both* diagonals — adding bosses — so the top and bottom each had their own.
- **Derek specified:** that put bosses on both sides of center-X; wrong. Keep the bosses exactly as they were and the top untouched; the bottom is mouth-down with screwholes that simply land on the existing bosses.
- **Agent built** (`1936abc5`): reverted shell, bosses, and top to original; built the bottom cap mouth-down on the original diagonal, screws landing on the existing bosses. Verified, committed, pushed.

The crux, surfaced afterward: from the finished part's frame the screwholes *did* move, but the agent kept arguing from the coordinate list ("the coordinates didn't change") — the wrong frame. The correct fix changed no coordinates at all; it only shelled the opposite face of the cup — and that *is* what "move the screw holes" meant in Derek's frame. Naming the operation up front — "build the bottom cap mouth-down (shell the other face) without changing the hole coordinates" — removes the frame ambiguity that caused the detour.

## Two asks, one night

One manager briefed both out of the same conversation, into the same `enclosure.py`, to
agents of the same tier, within an hour of each other. The room is
[`model/`](model/README.md).

**The MQ6 — operation and outcome. One pass.**

- **Derek asked for:** "the MQ6 sensor needs rotated 90 degrees about Z and 90 degrees about X, such that the MQ6 supports print vertically from the floor instead of horizontally from the wall."
- **Agent built** (`MQ6_TURN = ((X, −90°), (Z, +90°))`, across `c5300876` … `bc2b7052`): thickness across X, the 32 mm side fore-aft, the 20 mm side vertical; can west into the flank, header east into the bay; two posts standing on the slab, grooves taking the card's short edges, bite clamped to `min(mq6_grip, (card − can)/2)` so the can states it.
- **The agent checked its own signs against the clause and said so** — they resolve "the way the outcome clause asks," and the other sign would have pressed the header against a wall with the loom reaching for it. On the way through it corrected an inverted claim in `mq6_gas_sensor.py` (`59ba86ca`): the can leaves 0.5 mm at the *long* edges, so the *short* edges are the ones with material to grip.

**The corbel — end shape only. Four commits and a scope round-trip.**

- **Derek asked for:** two pick blocks and "Need a 45 degree chamfer or corbel or whatever it is called."
- **Derek expanded:** "Yes of course its twin but also, I mean all of them, not just flanks, these too" — the whole y=95.08 family, not the picked segment.
- **Agent built** (swept into `ca35bc07`): a 45° wedge struck along the deck underside's root off the tee wall's aft face, its leg read as `far - wall_aft_y` ≈ 4.06 mm rather than typed.
- **Then** `654875a9`: nothing cleared the valve's boss and top box out of the new band.
- **Then** `af21669d`: the port channel's reach was sized to the deck's original floor, 216.015, and never asked past it.
- **Then** `3d75333c`: the post-shaped cutters added by the first fix had reamed all 32 sockets over their whole 6 mm grip length — 0.000 mm of 6 engagement at every seat.

The crux: the wedge moves the deck's floor down 4.06 mm, and each round finds one more thing that had been living under the old one. The ask names the edge treatment; nothing in it says material is entering occupied space. `pack-closes` reads green after `af21669d` *because* of the over-cut — removing material removes clashes — and the retention loss surfaces from a different session reading an identical 0.9956 across eight valves as the probe cap rather than a displacement.

Naming the operation up front — "fuse a 45° wedge along the deck underside's root, struck off the tee wall's aft face, so the deck prints without support" — states where the material comes from, what fixes its size, and what done means. An agent holding that sentence is being told the floor is moving.
