# The routing procedure — moving this board to manual traces

The question: *can we move the board off the autorouter onto manual traces, and how* — given the
capacity autorouter is [deterministic but has zero solution-locality](autorouter-is-deterministic.md)
and treats any manual copper as one more obstacle to route around, thrashing against it.

This is the answer, and it is a **complete, followable procedure.** Its output is a **routed
board**, not a report about the autorouter. It is not a research experiment and it is not hard to
do. The hard part is only that every tempting shortcut breaks it — see the last section — so the
discipline is in *not* taking them.

## The procedure

Work one **region** at a time. A region is a small area you pick — e.g. U14, J14, the space
between them, and a small margin around them.

1. **Pick the region.**
2. **Comment out every trace you see in that region.** Clear it of the copper you are about to own.
3. **Add those traces back, one at a time, as manual traces,** until you see an error or problem.
4. **Triage the error by its cause:**
   - **your own trace vs. your own trace** → adjust your trace.
   - **the autorouter sent a trace into your region** → comment out the offending (autorouter) trace.
   - **the autorouter did something seemingly unrelated, elsewhere** → **still comment out the
     offending trace.** Do not reason about whether it is "related." If an autorouter trace is the
     problem, evict it. (With zero locality there is no unrelated — a trace on the far side of the
     board is in your region's coupled solve.)
5. **Get your originally-targeted routes error-free before you do anything else** — even if that
   means **commenting out every other trace on the board.** Your region comes first, clean, no
   exceptions.
6. **Then add the autorouter's traces back, one at a time, until the autorouter fails** — until
   re-adding a trace produces an error against your now-fixed manual copper.
7. **When it fails, manually route that trace.** That failing net is now a new region → **go back
   to step 1 for it.**

Iterate. This terminates: everything the autorouter can route without conflicting with owned copper
it keeps; everything it can't, you have manually routed. When re-adding the held traces one at a
time no longer produces a failure, the board is done.

## Why each tempting shortcut breaks it

- **"Make the autorouter coexist with my manual copper here."** It won't. It has no
  solution-locality — it re-solves the whole board every render and treats your manual trace as an
  obstacle, so it keeps shoving copper back into your region. That is the whack-a-mole. The
  procedure does not negotiate with it: **evict.** Comment the offending trace out.
- **"That autorouter trace is way over there / unrelated — I'll leave it."** There is no
  "unrelated." If it is causing your region's error, it is the offending trace; comment it out.
  This is step 4's third rule, and it is the one that gets skipped every time.
- **"I shouldn't comment out the whole rest of the board just to route one corner."** Yes you
  should, if that is what it takes to get the target clean. The rest goes back in one trace at a
  time in step 6. A half-owned, half-autorouted region is the confound; a fully-cleared target is
  the control.
- **"Minimize the total error count."** The global error list is not the objective — a clean
  *target region* is. You will deliberately strip working copper and *raise* the error count to get
  a clean target, then rebuild. Burning the error list down globally is how you end up back in the
  whack-a-mole.
- **"Characterize where and why the autorouter fails."** Not the goal. You *use* each failure — but
  only as the signal for which net to hand-route next (step 7). The deliverable is routed copper,
  not an analysis of the router.

## What "done" looks like

Owning a region means owning every net that **physically transits** it, not just the nets logically
assigned to it — a through-net (e.g. a UART on its way to the WROOM) that crosses an owned region
must itself be owned or it will short into it. The autorouter is left holding only what it can route
without ever conflicting with owned copper; re-adding any held trace produces no new failure; the
board is deterministic and DRC-clean; and there is no manual/autorouter coexistence left anywhere to
thrash. The manual copper accretes reusable emitters as it goes (`pcbFan`, `pcbComb`, `drop`/`rise`
— see [`route-hints.md`](route-hints.md)), so "how we move to manual traces" becomes a small library,
not a one-off grind.
