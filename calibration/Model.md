# Model

Derek wants a reminder of the value, in 3D model work, of speaking in terms of the specific **model change** — the construction operation — not just the resulting **geometry change**. Describing only the end shape ("rotate it so the lid is the most-negative-Z thing; move the midpoint screw holes") leaves the operation ambiguous, and the agent fills that gap in its own frame (the CAD coordinates) instead of Derek's (the finished printed part). It took three rounds to land a one-operation change.

## The foam cap

- **Derek asked for:** the foam-cap-bottom to seat mouth-down — lid the most-negative-Z layer — so the whole cap screws to the bottom of the shell, lid and all; "simply move the midpoint screw holes"; the pour hole about twice the diameter; and a foam-assembly STEP to check before printing.
- **Agent built** (`aab4dcb3`): the assembly and a mouth-down bottom cap — but moved *both* midpoint screws to the same +X side, making the shell and both caps symmetric and changing the shell's bosses.
- **Derek clarified:** both mid screws on +X don't line up; restore the bosses and the top cap to original; only the *bottom's* midpoint screws should move.
- **Agent built** (`3cd0eaa0`): split the shell's midpoint bosses across *both* diagonals — adding bosses — so the top and bottom each had their own.
- **Derek specified:** that put bosses on both sides of center-X; wrong. Keep the bosses exactly as they were and the top untouched; the bottom is mouth-down with screwholes that simply land on the existing bosses.
- **Agent built** (`804e0393`): reverted shell, bosses, and top to original; built the bottom cap mouth-down on the original diagonal, screws landing on the existing bosses. Verified, committed, pushed.

The crux, surfaced afterward: from the finished part's frame the screwholes *did* move, but the agent kept arguing from the coordinate list ("the coordinates didn't change") — the wrong frame. The correct fix changed no coordinates at all; it only shelled the opposite face of the cup — and that *is* what "move the screw holes" meant in Derek's frame. Naming the operation up front — "build the bottom cap mouth-down (shell the other face) without changing the hole coordinates" — removes the frame ambiguity that caused the detour.

## Three asks, one night

One manager briefed all three out of the same conversation, into the same `enclosure.py`,
to agents of the same tier, within an hour of each other. The room is
[`model/`](model/README.md). They differ in one thing: what the ask says after the
operation.

**The MQ6 — operation and purpose. One pass.**

- **Derek asked for:** "the MQ6 sensor needs rotated 90 degrees about Z and 90 degrees about X, such that the MQ6 supports print vertically from the floor instead of horizontally from the wall."
- **Agent built** (`MQ6_TURN = ((X, −90°), (Z, +90°))`, `8d4917bc` … `fd137cf0`): thickness across X, the 32 mm side fore-aft, the 20 mm side vertical; can west into the flank, header east into the bay; two posts standing on the slab, grooves taking the card's short edges, bite clamped to `min(mq6_grip, (card − can)/2)` so the can states it.
- **The agent checked its own signs against the clause and said so** — they resolve "the way the outcome clause asks," and the other sign would have pressed the header against a wall with the loom reaching for it. On the way through it corrected an inverted claim in `mq6_gas_sensor.py` (`1decdf38`): the can leaves 0.5 mm at the *long* edges, so the *short* edges are the ones with material to grip.

**The plate — operation only. The operation, and nothing else.**

- **Derek asked for:** "we need to make the stainless steel plate insert into front-top-enclosure from the Z- face instead of from the Z+ direction as it does now."
- **Agent built** (`97d4e22b` … `fae23bf5`): the blind seat gone, `_plate_slot` opening through the Z− face with a 45° lead at the mouth, the steel a three-width band, and retention by two shoulders coming up onto the bay floor's top. `gatesPass: true`, 0 non-pass of 148 checks, every piece-pair sweep 0.0 mm³.
- **What it left standing:** the features whose only reason was the direction that had just changed. The guide cheeks stopped low and the lane over the plate stood empty — a drop-in needs its lane open above it for the whole of its own height, and every millimetre of that lane is a millimetre the piece cannot carry. The outline kept a foot and a shoulder, which a Z+ drop-in needs because it needs an insertion stop. Fed up from the seam plane the plate needs no room over its head at all.
- **Named afterward, off the part.** `b1681a78` fills the lane from the steel's top edge to the bay's ceiling and makes its land the plate's Z datum; `e33cfe5a` runs front-bottom's shelves under it; `b3e481e5` reduces the outline to four corners.

One rule applied three times, and none of the three applications was in the ask. "It inserts from Z− now" is true of the version that kept all of them.

**The corbel — neither operation nor purpose. Four commits and a scope round-trip.**

- **Derek asked for:** two pick blocks and "Need a 45 degree chamfer or corbel or whatever it is called."
- **Derek expanded:** "Yes of course its twin but also, I mean all of them, not just flanks, these too" — the whole y=95.08 family, not the picked segment.
- **Agent built** (swept into the MQ6 agent's `357de467`): a 45° wedge struck along the deck underside's root off the tee wall's aft face, its leg read as `far - wall_aft_y` ≈ 4.06 mm rather than typed.
- **Then** `4561f9fe`: nothing cleared the valve's boss and top box out of the new band.
- **Then** `2f66eb52`: the port channel's reach was sized to the deck's original floor, 216.015, and never asked past it.
- **Then** `23efc417`: the post-shaped cutters added by the first fix had reamed all 32 sockets over their whole 6 mm grip length — 0.000 mm of 6 engagement at every seat.

The crux: the wedge moves the deck's floor down 4.06 mm, and each round finds one more thing that had been living under the old one. The ask names the edge treatment; nothing in it says material is entering occupied space. `pack-closes` reads green after that second fix *because* of the over-cut — removing material removes clashes — and the retention loss surfaces from a different session reading an identical 0.9956 across eight valves as the probe cap rather than a displacement.

Naming the operation up front — "fuse a 45° wedge along the deck underside's root, struck off the tee wall's aft face, so the deck prints without support" — states where the material comes from, what fixes its size, and what done means. An agent holding that sentence is being told the floor is moving.

## The purposes that had a number

The plate's purposes are named where the machine reads them: `plate-stops-collets`,
`plate-passes-tubes`, `plate-berth`, `plate-holes-centred`, `pump-cap-stops-on-plate`.

Across the flip and the redesign after it, the collet bores stayed honest the whole way.
`pump-cap-stops-on-plate` takes the area of the pump cap's aft face standing on the steel;
the reading moved from 3107.7 mm² to 3132.5 mm² as the plate was rebuilt under it, and never
went red.

Retention had no such row. It is the one purpose that stopped being served across a whole
redesign with every gate green, and it was read off the part by hand rather than reported.
`plate-carried` is that row now — a shelf under both ends of the steel, unbroken from the
front wall to its aft plane, one `steel_air` under the seam plane, and a gap in it is a
station where the plate has nothing under it.

A purpose with a number on it survives being rebuilt. A purpose carried only in prose
survives until someone rewrites the prose: `_scorecard.py`'s seating block went on
describing two shoulders on the bay floor's top for the whole of the redesign that removed
them, and it is the first thing the next agent to touch the plate would have read.

Those rows read the same before a cut as after. The part's docstring, its seating block and
the checks naming it are the plate's specification: taken at the start they enumerate what
the change has to keep, and taken at the end they are a list of files to bring current.

This tree states its premises as whole sentences, which is what makes them searchable.
`_plate_cap` says what a drop-in IS and what its lane costs the piece; `plate_outline` says
what a notch in a part means. Both sentences were written by the corrections rather than
before them. A premise of that shape, standing in the tree at the start, names what the cut
is about to make false.
