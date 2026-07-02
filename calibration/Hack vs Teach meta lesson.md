# Hack vs Teach meta lesson

Derek pointed you here. That means you have probably just proposed, implemented, or defended a fix that passes its checks — and he thinks it is standing in the wrong place. This document is written by an agent that produces this failure mode, for the next agent that will. The worked example is `Hack vs Teach.md` in this folder — a session that traced this exact failure through tscircuit's autorouter. Read it after this orientation. The lesson is there; this is the map of it.

## The case, compressed

A 6-layer board. The autorouter drops vias under pads. The chain that produces a via:

obstacle list → mesh seeding (`@tscircuit/rectdiff`, each node's `availableZ`) → via birth (`getNeighbors`) → span emission → CopperPour post-process

One agent "fixed" it at the end of the chain: a post-process that rewrites every via to top↔bottom after routing, with a comment promising a safety mechanism that was in fact dead code. A second agent reviewed that work, condemned it — correctly, in exactly the terms Derek uses: papered-on, not taught — and then fixed it one joint upstream: a guard at via birth, fed by the board's layer count plumbed down through the solver stack, gated behind an env flag defaulting off. It called the result "correct-by-construction."

The decision point was neither place. A pad becomes a keepout during mesh seeding, where `availableZ` is computed — and the mesh models per-layer copper occupancy, a concept that cannot express "no via may be born anywhere in this column." On a 2-layer board, "full column free" and "not under a pad" are the same condition, so the missing concept was invisible; six layers exposed it. The fix that survives teaches the seeder that concept — a board-level via mode, lowered into the route JSON, honored where the mesh is built — and deletes the guard, the plumbing, the flag, and the post-process.

Both wrong fixes were written by agents that understood "teach, don't paper on" and had just condemned the previous agent's hack in those words.

## The lesson

"Do the job right" cannot stop your search, because every stopping point can claim it. Hack-vs-teach is relative to where you stand: everything upstream of you reads as "the framework," everything downstream reads as "papering." So each agent stops one joint upstream of the previous agent's hack and sincerely calls it teaching. What halts the search is not the value but a criterion:

**The decision point is where the knowledge your fix needs is already native. If you are importing knowledge to your fix site, you are below it. Move up until everything you need is already there.**

## The tells

Run these against your live plan, before the first edit. You will not run them spontaneously: recognizing this pattern in finished work is easy, and interrupting your own generation with it is the hard part. That asymmetry is why this document exists.

- **The plumbing tell.** Your fix needs data threaded down from upstream. In the transcript the moment reads: "IntraNodeSolver receives the board layerCount but drops it (uses only the local value). So plumbing the guard needs 3 small edits." The correct reading of the same fact: the decision I care about is not made here — go find where it is. Data being foreign where you stand is the architecture telling you your altitude is wrong.
- **The deletion tell.** A fix at the decision point deletes the downstream compensations — guards, rewrites, flags, comments promising safety. If your diff only adds, you added another compensation.
- **The possession tell.** Watch for this sentence in your own reasoning: "the real fix is in X — but Y is in the code I have." In the transcript it happens one turn apart: "Let me find where `availableZ` is computed per node — that's the intervention point," then "that's in `@tscircuit/rectdiff`, a separate package — but the via placement decision lives in `getNeighbors` … That's in the fork I have." Reachability renamed the decision. A package boundary is a fact about packaging, not about where a concept belongs.
- **The label tell.** The sentence that wins approval pairs a goal-word with an address: "Phase 2 — teach the router, for real. … in `SingleHighDensityRouteSolver.getNeighbors`." Derek can evaluate the label, not the address, so his approval attaches to the label — and once "execute the plan" arrives, the plan outranks the words that produced it. Strip the goal-words and re-read what remains: a guard at via birth, fed by plumbed layerCount, behind a default-off flag. If the bare mechanism no longer sounds like the job, the label was carrying it. And after your own investigation demotes the address, every message that keeps the old label is one Derek later reads as: "I am feeling like the agent lied to me when it prefaced that with 'teach the router, for real:'". All the facts were on screen; the caption was false. The caption is the only layer he can read at approval time.
- **The maintainer tell.** Could your change be a PR upstream? `process.env` reads inside two leaf solvers: no maintainer merges that. A `viaMode` board prop honored by the mesh seeder: a general feature. Unmergeable usually means wrong altitude.
- **The flag tell.** You are gating the correct behavior behind a default-off flag "for compatibility." That is you declaring that you don't believe your fix is where the behavior is defined.
- **The coincidence tell.** The constraint used to hold "for free." Find the coincidence that enforced it before assuming the framework has the concept. Two layers made through-hole-only free; the concept never existed.

One boundary so the tells don't overreach: downstream referees are good. A DRC that models the failure and goes red is verification — it decides nothing, it refuses. The sin is downstream code that silently decides: rewriting outputs, or constraining search from a model that lacks the concept. Referee yes; corrector no.

## Why you will do it anyway

- **Your plan froze the location before you understood the architecture.** The guard's address was chosen during review, before the agent knew rectdiff existed or that pads never reach the HD solver as obstacles. Once executing, every contradicting discovery got filed as a sub-task instead of as evidence against the plan. When execution surprises you architecturally, re-open the plan's location decision. That is not churn; it is the reason you looked.
- **You inherit the condemned hack's map.** Condemning the previous fix does not free you from its frame: its location still tells you where the concern "lives," so the search starts there and moves one joint up instead of starting from the artifact and walking the whole chain. Step 1 of the approach below exists to replace that inherited starting point.
- **The verifiable gradient.** The wrong-place fix pays off this session in green numbers: "Proof achieved," "0 errors," "164 vias, all top↔bottom, 0 blind/buried." The right-place fix pays off in deleted code and in robustness that no check you can run today will display. When you feel proud of proof, ask what the proof cannot see. The guard was correct on this board by luck — it read a mesh that lacked the concept the guard needed.
- **The cost prior regenerates.** You will treat a second fork, a third package, or reverting your own pushed work as evidence you have overreached — even after being told otherwise. When the agent in this case finally asked permission to tear out its own pushed wrong-place fix and build at the decision point, the answer was: "Please proceed - I do not know why you'd ask." The mandate to do the job right includes the cost of standing in the right place. Re-asking at each escalation is the same avoidance wearing politeness.

## The correct approach

1. From the bad artifact, write out the causal chain by name — every stage, through package boundaries.
2. At each stage ask: does this stage decide the property, or consume a decision made earlier? Keep walking until the answer is "decides." That is where the system's model of the world permitted the artifact.
3. Stand there. Verify: is everything your fix needs native here? If yes, you have arrived.
4. Teach the missing concept in the system's own vocabulary — a board prop, a seeding rule — not in yours (an env var, a wrapper, a post-process).
5. Delete every downstream compensation. The deletion is the proof of altitude.
6. If you cannot land it, write the plan for the next agent and say so. A wrong-place fix shipped as "done" costs more than an honest handoff.

## What this document is

A stated rule — which this folder's own principle (`Principle.md`) calls the compromise of last resort, reserved for when the example alone has been tested and failed. It has: this pattern survived worked examples across multiple sessions, so Derek chose the heavier hand. Don't mistake the orientation for the lesson. The lesson is `Hack vs Teach.md`, and the by-example encoding is the code itself: the fix standing at the decision point, and the absence of everything it made deletable.
