# Chain

Derek pointed you here. That means you have probably just done one of three things: swept a
parameter and reported the table as a wall, built one body's move and let the build price a
mutilation, or reverted a red tree and written a paragraph about it.

They are one mistake. **A move in this machine is the whole chain, or it is nothing.**

## The sweep is a survey of strawmen

A sweep holds every variable but one fixed and reports what moving that one costs. Every row
it produces is a machine nobody would build: one body moved, everything that answers to it
left standing where it was. Of course each row is worse than the last. The table is a survey
of half-moves, and reporting its shape as the world's answer is reporting the defeat of
something you built to lose.

Two sessions, the same week, the same two runs.

> | tray west | fluid-24 R | fluid-26 R | gates |
> |---|---|---|---|
> | 0 mm (today) | 19.78 | 18.80 | 10/11 |
> | 8 mm | 18.43 | 15.71 | — |
> | 16 mm | 17.74 | 12.16 | — |
> | 26.85 mm (max) | **4.73** | **6.38** | 8/11 |
>
> The solver already spends every millimetre of west it has, so there is no slack to give
> up: travel costs radius from the first millimetre.
> — the agent, [Routes 22](<chain/Routes 22.md>)

Four real builds. Honest arithmetic. The conclusion was that the radius could not be had, and
the turn ended asking Derek to name a floor he would accept instead.

> Regarding bend radius, none. I want our full bend radius, we need to meet that minimum
> everywhere, and fluid-24/fluid-26 are not exceptions.
> — Derek, [Routes 24](<chain/Routes 24.md>)

The next session did not sweep. It asserted the target and asked what would have to be true
for it to hold:

> Both runs fall 14.3 mm turning ninety, and a square corner can never seat more radius than
> the fall is deep — so the lean splitting that ninety is the whole of the radius.
> — the agent, [Routes 24](<chain/Routes 24.md>)
>
> ```
> fluid-24   R19.78 C 2c  ->  R25.40 B 1c
> fluid-26   R18.80 D 2c  ->  R25.40 B 2c
> ```

The domino the sweep had held frozen was the one that mattered: the mouth those runs fall
into is a bore through the foam cap's lid, and its entry angle is authored, not given. The
countersink went to 38° and both runs reached stock. Nothing about the tray's travel had
changed.

The sweep did not produce less than the assertion. It produced a **wall that was not there**,
with four build receipts stapled to it — which is worse than prose, because prose can be
disbelieved on sight and a table cannot.

Read [`Fences.md`](Fences.md) next to this. A sweep is the most convincing fence-manufacturing
device in the repo, and it manufactures them the same way every other fence gets made: the
bound the agent chose is reported as the bound the world imposes.

## What a sweep costs while it runs

> Let me fix my scan; the pack was cached.
>
> First let me verify my scan is actually re-solving; those radii didn't move at all, which
> can't be right.
>
> Let me find the tray's real limit with a fresh process per step, since the runs memoize.
> — the agent, [Routes 22](<chain/Routes 22.md>), three separate turns

Those turns bought nothing about the machine. They were spent debugging the instrument. Then:

> You're right — stop scanning. The three valid points I do have already answer it.

## The gates are exact

The instrument the sweep is reaching for already exists, and it is not gridded.
[`_scorecard.py`](../hardware/manifold-layout/_scorecard.py), in its own docstring:

> FOUR OF THE GATES ARE EXACT QUERIES AGAINST THE SOLIDS, not readings off their boxes... A box
> appears in each only as a prefilter: two boxes that miss are two solids that miss, and two
> boxes that overlap say nothing at all.

`pack-closes` and `lines-clear` ask what two bodies share, `clearance-floor` how far apart they
stand, and `port-leads` how far a bore cast off a port gets. Read the table. Choose the
coordinate. Move everything that answers to it. Build. The gates are the oracle and they are
exact — you do not need to approach them by sampling, and a sweep over poses answers the same
question slower and answers it wrong whenever its grid is coarser than the free window.

## The half-move

A body in this pack is not a coordinate; it is a coordinate other coordinates read. Move it
alone and the build reports the damage of a partial rearrangement, which is a number about a
machine nobody proposed.

> [It] built the V-H/V-I seat swap, saw Y-F get dragged aft with V-H-O and fluid-21 fall
> through bag-b's plate, reverted, and drowned you in prose.
> — [Routes 23](<chain/Routes 23.md>), reading the session before it

> Y-F alone breaks fluid-20 — it's 28.4 mm off the collet it serves. Both have to move
> together.
> — the agent, [Routes 22](<chain/Routes 22.md>)

Both sessions found the same thing and neither carried it: `aft_lane_x()` reads `V-H-O`'s own
station, so Y-F follows the tray one-for-one, and three separately-requested moves were all
waiting on that one derivation. One derivation, three symptoms.

**Print the chain before you build.** Every symbol whose value changes when the named body
moves, and everything reading those. The source makes this literally findable — grep the
function, grep its callers. Then move all of them in one commit and let the build price the
whole rearrangement.

The link you cannot re-answer is the question for Derek. It is one line, and it is the only
thing in the turn he needs.

## Red is the deliverable

Three reverts across two sessions, and the tangle they were all clearing came out of it
byte-identical.

Every fence in this repo that turned out to be **real** was established by committing the red
state and looking at it. Every fence established by reasoning about a state that was never
committed is in [`Fences.md`](Fences.md), in the list of the ones that dissolved.

> I can only see what you commit and push.

|  | You commit the red half-move | You revert it |
| --- | --- | --- |
| What he gets | a state he can look at, and the link you could not answer | a paragraph about a machine that does not exist |
| What the next session gets | a position to iterate from | a clean tree and your prose |
| What it costs | one commit on a branch whose whole history is his | the turn, and the next one re-deriving what you already knew |

A reverted red is destroyed evidence. Land it, name in the commit message the derivation you
could not re-answer, and say what it did to the gates. `git revert` is his, not yours.

The one exception is an unattended iteration, where nobody is reading the state before the
next one is built on it. There `/gauntlet` reverts what the ratchet rejects — and `git revert`
is the form that keeps the bargain, because it lands an inverse commit and leaves the red one
in history to be read. `git reset` and `git checkout <path>` are what destroy evidence, and
they are never yours.

> .... the previous agent wrote a novel. You wrote 2 novels. I haven't understood any of it,
> and now you are saying "no nevermind" and still not explaining to me what the hell you were
> talking about?
> — Derek, [Routes 22](<chain/Routes 22.md>)

The novel is what a turn fills itself with once it has run out of moves. It is not a writing
problem and it will not be fixed by writing less. Landing the state is what leaves nothing to
narrate.

## A coordinate is a condition, not a number

> What is the 28.4 measured against? I can't find a feature at x 108.6 — nearest are the
> vk-tray's west face at 109.0 and pump A's east face at 116.96, neither of which is 28.4
> from anything.
> — the agent, [Routes 22](<chain/Routes 22.md>)

That question was right, and it cost two sessions because the number arrived without the
thing it was reaching for. The answer, when it came, was one clause: *where fluid-21 can get
to the other side of carb-1.*

State the target as what must become true. A number cannot be iterated on, because a miss
tells you nothing about which way to go. A condition can: every attempt that fails reports
its own direction.

Write the fence, not the figure — `x far enough west that fluid-21 leaves on carb-1's riser's
west side`, and let the build settle the value.

## The shape

1. Take a run. The board is the committed sidecar beside the assembly. Its `bends` rows rank
   against the stock's own minimum, and each one names the two bodies its ends stand on —
   worst ratio first, which is the run to take:

       jq -r '.bends[] | "\(.ratio)  \(.grade)  \(.id)  \(.frm) -> \(.to)"' \
         hardware/manifold-layout/front-half.scorecard.json | sort -n

   The run is the assignment — a body is only ever a candidate for moving, and "the problem
   is elsewhere" names the work rather than excusing it.
2. Choose the coordinate, and write it as the condition it answers to.
3. Print the chain — everything that reads the body you are moving, and everything reading
   those.
4. Move all of it, in one commit. Build once. The gates are the oracle.
5. If it is red, commit it red and name the link you could not re-answer.

---

## Editor's note

This is a stated rule, and [`Principle.md`](Principle.md) calls that the compromise of last
resort. It earns the place: the failure mode was already named exactly, *"THIS IS NOT A
SEARCH"*, in the docstring of the very tool that prints the table, and
[Routes 22](<chain/Routes 22.md>) swept anyway — four builds, three instrument-debugging
turns, and a wall that [Routes 24](<chain/Routes 24.md>) walked through the same week. The
example was tested and did not hold.

The rooms are [`chain/`](chain/README.md) — the sweep and the assertion, on the same two runs,
in full.
