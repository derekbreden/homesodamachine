# Model

Derek wants a reminder of the value, in 3D model work, of speaking in terms of the specific **model change** — the construction operation — not just the resulting **geometry change**. Describing only the end shape ("rotate it so the lid is the most-negative-Z thing; move the midpoint screw holes") leaves the operation ambiguous, and the agent fills that gap in its own frame (the CAD coordinates) instead of Derek's (the finished printed part). It took three rounds to land a one-operation change.

- **Derek asked for:** the foam-cap-bottom to seat mouth-down — lid the most-negative-Z layer — so the whole cap screws to the bottom of the shell, lid and all; "simply move the midpoint screw holes"; the pour hole about twice the diameter; and a foam-assembly STEP to check before printing.
- **Agent built:** the assembly and a mouth-down bottom cap — but moved *both* midpoint screws to the same +X side, making the shell and both caps symmetric and changing the shell's bosses.
- **Derek clarified:** both mid screws on +X don't line up; restore the bosses and the top cap to original; only the *bottom's* midpoint screws should move.
- **Agent built:** split the shell's midpoint bosses across *both* diagonals — adding bosses — so the top and bottom each had their own.
- **Derek specified:** that put bosses on both sides of center-X; wrong. Keep the bosses exactly as they were and the top untouched; the bottom is mouth-down with screwholes that simply land on the existing bosses.
- **Agent built:** reverted shell, bosses, and top to original; built the bottom cap mouth-down on the original diagonal, screws landing on the existing bosses. Verified, committed, pushed.

The crux, surfaced afterward: from the finished part's frame the screwholes *did* move, but the agent kept arguing from the coordinate list ("the coordinates didn't change") — the wrong frame. The correct fix changed no coordinates at all; it only shelled the opposite face of the cup — and that *is* what "move the screw holes" meant in Derek's frame. Naming the operation up front — "build the bottom cap mouth-down (shell the other face) without changing the hole coordinates" — removes the frame ambiguity that caused the detour.
