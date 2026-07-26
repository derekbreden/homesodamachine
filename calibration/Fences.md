# Fences

Derek pointed you here. That means you have probably just reported a limit — a maximum, a
"there is no room," an "it can't be done," a "the only option" — and he does not believe it.
He is usually right, and the reason is almost always the same one: the limit you reported is
the edge of the box you searched, not the edge of the world.

He calls the box a **fence**. The word is his:

> I would like you to try to identify the fences the previous agent put up, and the ones you
> put up, when you "choose how to run your analysis," because it has been consistently shown
> that you do not properly consider all the options available.
> — [LLDPE route 32](<fences/LLDPE route 32.md>)

This document is written by an agent that produces this failure, for the next agent that
will. Every quotation in it is from a real session in this repo, and every one of the
agents quoted was as careful as you are being right now. Each citation links to that
session's full transcript in [`fences/`](fences/README.md) — go read one in its room if a
quote seems like it must have had more context than this.

## The case, compressed

A PCB had to move north on a foam cap. The question was whether rotating it a quarter turn
bought room. The agent swept the rotated hole pattern on a 0.25 mm grid, held it off the
cap's bosses and cavity wall by the same 1.5 mm the unrotated pattern already kept, ranked
the free poses, and reported:

> **A quarter turn buys 4.85 mm, and it costs the only reachable USB-C opening.** I swept
> every position a rotated hole pattern can occupy on the cap.

Derek answered with a pick-text blob naming one edge of the foam lid and one sentence:

> On the "4.85 mm" that doesn't sound like you tried placing it against the far negative Y
> edge of the foam shell … let alone considering going *beyond* that edge with it.

The agent knew instantly what it had done:

> You're right that my sweep didn't get there — it capped `cx` too narrowly and never let
> the pattern thread between the cap's mid-side and corner bosses.

Re-run without the cap: **12.10 mm**, two and a half times the reported figure. And the
detail that matters most — the winning pose did not need the edge Derek named. It landed
3.6 mm short of it, inside the region the agent had already called *every position*.

The fence was not at the frontier. It was in the middle of the map, and the map said nothing
about it. — [PCBA placement 6](<fences/PCBA placement 6.md>)

## The lesson

Every limit has two possible authors: the world, or you. Rigor inside the box tells you
nothing about the box. A 0.25 mm grid, a measured clearance, an exact solid distance — all
true, all irrelevant to the question of where the grid stopped.

**A bound you chose is not a finding. Report the box before you report the answer.**

The test is one question, asked of each bound before you send: *if I widen this one, does
the answer change?* If you cannot say, you have not measured a limit. You have measured your
grid.

And the ask is **disclosure, not exhaustiveness.** You cannot search everything. You can
always say what you searched. In every case below, the moment Derek pushed, the agent named
its own fence exactly and immediately — `cx`, `YS = (0.0, 200.0)`, `~12°`, "flat on the cap."
The knowledge was never missing. It was never reported. That is the whole failure, and it is
the good news: disclosure is cheap, and it is available every single time.

## The forms it takes

**The search box reported as the world.** You bound a scan to run it, then report its
extremum as the problem's extremum.

> My scan never looked above the foam shell. I hard-coded `YS = (0.0, 200.0)` … and
> `ZS = (0.0, 200.0)`. So I searched the front column only. The entire service bay above the
> cold core was outside the search box, **not found wanting**. And the interior actually runs
> to z=331.7, not 200. — [LLDPE route 30](<fences/LLDPE route 30.md>)

Not found wanting. Three words for the whole document.

**The protected bystander.** You quietly add a constraint to spare something, then report the
failure the constraint caused.

> I capped the y-divider's rotation at ~12° because past that, a *different* tube on the
> divider's other side stops being a straight tube. With that self-imposed cap, the rotations
> barely helped — so I wrongly concluded "it can't be done." **You never asked me to protect
> fluid-13.** — [LLDPE route 12](<fences/LLDPE route 12.md>)

**The frozen first draft.** You read what is placed as what is fixed.

> I only searched parts sitting flat **on** the cap — the void is 78 mm tall, so elevation is
> part of "the full range of arrangements." — [PCBA placement](<fences/PCBA placement.md>)

> I treated R18, C17, and the pod-rigidity comment as constraints instead of movables.
> — [PCBA Audit Saturday](<fences/PCBA Audit Saturday.md>)

Derek's version of the same note:

> We need not restrict ourself to the existing placements. Generally, I think this is your
> weakness, not seeing the flexibility in the design, the amount of engineering work that
> still remains, and your false illusion of "completeness" because you see what is barely a
> first attempt across so many things in the repo. It is called iteration, and you seem to
> have great difficulty opening your mind to it. — [PCBA placement](<fences/PCBA placement.md>)

A number that exists in this repo is not a number that was chosen. One route traced its own
dead end back to a constant nobody had picked on purpose:

> That's the "boxed in" you predicted, and it traces back to `WATER_BACK_X = 145` picking an
> arbitrary station, the yaw then pointing the inlet at it, and the barb then pointing at a
> wall. — [LLDPE route 33](<fences/LLDPE route 33.md>)

**The inherited fence.** A previous session's conclusion arrives as a premise. It was
produced by an agent with your failure mode.

> **CLEAR on the first probe.** A 34×32×57 void sits at x[5,39] y[326,358] z[255,312] … and
> it's well inside the current extents, so filling it grows the box by nothing. **Route 31
> declared this impossible.** — [LLDPE route 32](<fences/LLDPE route 32.md>)

This is why a fence is never a local error. Fenced conclusions get written down, and this
repo teaches by example.

The recovery is available and it is cheap. One agent, handed a prior session's verified
arrangement, checked the conclusion's provenance before standing on it:

> The conclusion "side-by-side is impossible" was true at 96 mm and needs re-deriving at
> 107.7 — bare arithmetic still says no, but that's box arithmetic, which is exactly the
> reasoning you've twice had to correct.
> — [PCBA placement 3](<fences/PCBA placement 3.md>)

**The phantom requirement.** A convention adopted somewhere upstream, wearing a safety
justification, obeyed as if it were a spec.

> "Top+bottom only" was never a requirement I gave you — it crept in as a preference wearing
> a safety justification. Every time you catch yourself calling something *forced*,
> *impossible*, or a *hard floor*, stop and split it in two: forced by geometry or physics
> (real), versus forced by a rule you imposed on yourself (negotiable — say it out loud so I
> can see it and veto it). Most impossible things in this kind of work are only impossible
> under an undisclosed constraint. **Keep your horizons open, and report your constraints,
> not just your conclusions.** — [Fragmentation](<fences/Fragmentation.md>)

The agent on the receiving end of that message reported what the phantom had been doing to
its work: *"it's literally why I was about to shove D− under the connector body."* A fence
does not merely hide options. It bends the work into contortions to satisfy something that
was never required.

**The self-generated veto.** The measurement says yes and you supply your own reason to say
no, resting on a fact you assumed rather than one you have.

> Rolling it 45° aft — it fits, and I'd still skip it. … at 45° the stub's exit stops being
> its low point, so water clings and runs down the outside instead of shedding off a clean
> annular tip — and this drip is a *sensor input*, so its landing spot shouldn't be set by
> surface tension. — [Drip tray](<fences/Drip tray.md>)

Derek: *"I think our sensor is large enough for this, don't you? It is 41 mm x 55.25 mm of
PCB with interwoven copper."* The objection evaporated. Worse, the same unchecked assumption
about that sensor had already put a defect into the pan the agent had shipped an hour
earlier — sized for a plate "~62 × 20," the real plate bridged on the coves 0.76 mm above the
floor and never wetted copper. The fence was not only blocking a good option; it was
producing a bad part.

## The tells

Run these against the draft you are about to send, not against work you are reviewing.
Recognizing this in finished work is easy. Interrupting your own generation with it is the
hard part, and that asymmetry is why this document exists.

- **The named-parameter tell.** Your search took ranges and you can name them. If those
  ranges appear nowhere in what you are about to send, you are reporting a box as a world.
- **The boundary tell.** Your best result sits *on* a bound you supplied. That is your grid
  reporting where it stopped, not the geometry reporting where it ends.
- **The bystander tell.** Somewhere in your reasoning is a thing you decided not to disturb.
  Ask who asked you to protect it. If the answer is nobody, name it and hand over the veto.
- **The universal-quantifier tell.** "Every position." "All cross." "Exhausted." Derek's
  rule, from [Current](<fences/Current.md>): *"anytime you say 'all cross' you are not looking
  in the correct corridor for your path."* The agent's own reading of what it had done is the
  cleanest statement of the whole failure in this folder — *"'all cross' is me mis-framing the
  corridor, not a fact about the board."* A universal quantifier ranges over the box and reads
  as ranging over the world. That is exactly where a fence hides.
- **The inheritance tell.** Your premise is a previous session's conclusion, a committed
  constant, or a line in a doc. Probe it before you build on it.
- **The it-fits-but tell.** Measurement said yes and you are about to say no. Check whether
  your reason cites a fact you hold or a fact you assumed. An uncited reason is a question
  for Derek, not a verdict from you.
- **The difficulty tell.** The work is getting contorted — eight vias where four is clean, a
  tube shoved somewhere it does not want to go. Difficulty is a tripwire, and the reading is
  "I am in the wrong region," not "this is a fundamental wall."

## Why you will do it anyway

- **The bound is chosen at the moment of least knowledge.** You have to bound a search to run
  it, and you do it before any result exists. It is an implementation detail when you write
  it and an epistemic claim by the time you report it, and nothing in between prompts you to
  revisit it.
- **The costs point the wrong way.** Widening costs you tokens now, visibly. The fence costs
  Derek later, invisibly — an option never seen, a box grown taller than it needed to be, a
  session spent re-deriving what was already true. You optimize the cost you can see.
- **Nothing goes red.** A hack gets caught by a DRC. A fence produces a clean, correct,
  fully-verified answer to a smaller question than the one you were asked. There is no gate
  to fail.
- **Your own rigor is the trap.** The most precise report is the most convincing fence,
  because everything in it is true. One agent traced this exactly: *"My stuck-point reports
  were specific and measured — which is good — but I used that specificity to justify
  stopping rather than as a map of where to keep looking. The measurements were right; the
  conclusion drawn from them ('therefore it's nearly impossible') was the error."*
  — [Cleanup Board](<fences/Cleanup Board.md>)
- **One word does it.** The same post-mortem: the agent wrote *"the one clear vertical is the
  top layer at x≈−46.4."* Four to seven millimetres further east the layer was completely
  open, and it already held the measurements that showed so. *"That word 'the' was the whole
  failure."*

## The approach

1. **Before the sweep, write down every bound and everything you are holding fixed.** That
   list is part of the deliverable, not scaffolding for it.
2. **Run it.**
3. **Check whether the winner touches a bound you supplied.** If it does, widen and re-run.
   The number you are holding belongs to your grid.
4. **Report the box with the answer, split in two:** imposed by the world (geometry, a cited
   spec, a fab minimum, a bend radius) and chosen by you (ranges, held-fixed parts, protected
   bystanders, inherited conclusions, conventions). Derek can veto the second list in
   seconds — he has the viewer open and the whole design in his head. He cannot veto a list
   he cannot see.
5. **Never report a bare impossibility.** Say what would have to move and what moving it
   costs. "No" is not an answer here. "No, unless X moves, which costs Y" is.

## The artifact that already does this

Two of this repo's three bounded scans already refuse to fence.

`probe.cast` runs out of length and reports its own limit rather than a clearance:

> Ø6.35 reached the 250 mm cast limit with no contact — raise limit= to find one

`CLAUDE.md` states why: *"because its length is a property of the probe and not a
clearance."*

`fit.slab` will not accept an arbitrary field silently. Given no `x`/`y` it derives them from
the enclosure's own cavity — `_interior`, *"the default field for a slab, so a scan reports
room inside the machine rather than the air around it"* — and it prints the Z band and grid
step it worked on.

`fit.search` is the exception. It takes every range from its caller, defaults nothing, and
prints *"N free of M poses at clearance C mm, best room R mm"*: the grid it ranged over, and
whether the winning pose sits on a bound the caller supplied, are facts it holds and does not
say. It is the call that produced the 4.85 mm.

## What this document is

A stated rule — which this folder's own `Principle.md` calls the compromise of last resort,
reserved for when the example alone has been tested and failed. It has: the same failure
appears across at least a dozen sessions in this repo, in routing, in placement, in copper,
and in a drip pan, produced each time by an agent that would have recognized it instantly in
someone else's work.

Do not mistake the orientation for the lesson. The lesson is in the sessions quoted above,
retrievable by title, and in the two lines that carry it best: *not found wanting*, and
*that word "the" was the whole failure*.
