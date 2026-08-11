# calibration

Working calibration between Derek and the agents in this repo. Top level is what you read.
Each folder holds the conversations its document distills — full transcripts, user and
assistant turns, no tool calls.

Most documents here are a stated rule, which [`Principle.md`](Principle.md) calls the
compromise of last resort: reserved for a lesson the repo has already tried to teach by
example and failed to. Each one says so about itself, and each one points back at the rooms
where the lesson actually happened. The rooms are the teaching.

[`Fences.md`](Fences.md) is the exception and states no rule. It is a record Derek points an
agent at after that agent has reported a limit he does not believe, so the agent can see the
pattern is repeated and documented rather than a one-off. Everything in it is a quotation or a
number from a session in [`fences/`](fences/README.md).

| Read | About | Rooms |
| --- | --- | --- |
| [Principle.md](Principle.md) | Any rule is better encoded as an example. Explanations mislead when a reader takes one for the design space — **residue**, distinct from clutter. | [`principle/`](principle/) — You.md, Framing.md |
| [Fences.md](Fences.md) | The record, not a rule. Agents report limits that are the edge of the box they searched rather than the edge of the world, they do not notice, and when pushed they name their own bound immediately. Sixteen sessions of it. | [`fences/`](fences/README.md) — sixteen sessions |
| [Discretion.md](Discretion.md) | A softened instruction is still an instruction. Ending a turn on an offer spends it on the one output with no value. | [`discretion/`](discretion/README.md) — one session |
| [Hack vs Teach meta lesson.md](<Hack vs Teach meta lesson.md>) | Where a fix stands. The decision point is where the knowledge your fix needs is already native. | [`hack-vs-teach/`](hack-vs-teach/) — one session |
| [Model.md](Model.md) | In 3D model work, name the construction operation, not just the resulting shape. | — |

[`sessions/`](sessions/) holds conversations that nothing distills yet — `Avoidance.md`,
`Comments are a code smell.md`, and `Routes 22`/`23`/`24`.

Hooks in `~/Developer/claude-code-setup/hooks/` read paths under this folder:
`block-residue.sh` at `Principle.md` and its rooms, and `block-unlooked-move.sh` and
`note-inherited-fence.sh` at `Fences.md`. The last one bails
silently when that file is absent, so the path is load-bearing — moving or renaming `Fences.md`
turns the hook off without saying so. `block-underived-measurement.sh` points at this repo's
docgen rather than here.
