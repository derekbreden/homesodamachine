# calibration

Working calibration between Derek and the agents in this repo.
[`Principle.md`](Principle.md) distills [`principle/You.md`](principle/You.md) and
[`principle/Framing.md`](principle/Framing.md) — the rooms where it happened. Any rule is
better encoded as an example; the desire to write one marks a gap in the repo, and the fix
lives there. [`principle/Provenance.md`](principle/Provenance.md) is the third room: the
geometry read as a record of who decided what, and Derek's word first.
[`principle/Memory.md`](principle/Memory.md) is the fourth room: what memory on this laptop
is for, from the moment an agent wrote a correction into it.

`block-residue.sh` in `~/Developer/claude-code-setup/hooks/` reads `Principle.md` and the two
rooms it distills at these paths. `block-memory-write.sh`, beside it, bounces each session's
first memory write to `principle/Memory.md`.
