# calibration

Working calibration between Derek and the agents in this repo. Top level is what you read.
Each folder holds the conversations its document distills — full transcripts, user and
assistant turns, no tool calls.

Every document here is a stated rule, which [`Principle.md`](Principle.md) calls the
compromise of last resort: reserved for a lesson the repo has already tried to teach by
example and failed to. Each one says so about itself, and each one points back at the rooms
where the lesson actually happened. The rooms are the teaching.

| Read | About | Rooms |
| --- | --- | --- |
| [Principle.md](Principle.md) | Any rule is better encoded as an example. Explanations mislead when a reader takes one for the design space — **residue**, distinct from clutter. | [`principle/`](principle/) — You.md, Framing.md |
| [Fences.md](Fences.md) | A limit you report has two possible authors: the world, or the bound you chose. Report the box before the answer. | [`fences/`](fences/README.md) — fifteen sessions |
| [Discretion.md](Discretion.md) | A softened instruction is still an instruction. Ending a turn on an offer spends it on the one output with no value. | [`discretion/`](discretion/README.md) — one session |
| [Chain.md](Chain.md) | A move is the whole chain or it is nothing. A sweep surveys half-moves and reports their defeat as the world's; a red half-move reverted is evidence destroyed. | [`chain/`](chain/README.md) — three sessions |
| [Hack vs Teach meta lesson.md](<Hack vs Teach meta lesson.md>) | Where a fix stands. The decision point is where the knowledge your fix needs is already native. | [`hack-vs-teach/`](hack-vs-teach/) — one session |
| [Model.md](Model.md) | In 3D model work, name the construction operation, not just the resulting shape. | — |

[`sessions/`](sessions/) holds conversations that nothing distills yet — `Avoidance.md` and
`Comments are a code smell.md`.

Two hooks in `~/Developer/claude-code-setup/hooks/` point here: `block-residue.sh` at
`Principle.md` and its rooms, and `block-underived-measurement.sh` at this repo's docgen.
