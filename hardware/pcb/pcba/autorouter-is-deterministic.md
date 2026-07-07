# The capacity autorouter is deterministic

`pcba.tsx` routes with the **capacity autorouter** (`autorouter={{ viaMode: "through-hole", … }}`,
`groupMode: "subcircuit"`). It is a deterministic mesh solver (`patches/capacity-autorouter-fork/`):
**the same input produces byte-identical output.** It does not roll dice. It does not "re-solve
differently" from one render to the next. If two renders differ, the *input* differed — a source
file changed, a dependency bumped — the router did not.

Stop re-discovering this. It is settled, and it is proven below. Treating it as an open question,
or blaming a ripple on nondeterminism, is the recurring mistake this file exists to end.

This doc is the *fact*. What you **do** about it — the complete procedure for moving the board onto
manual traces — is [`routing-procedure.md`](routing-procedure.md). Determinism is not a license to
"run experiments" or "characterize the failure"; it is what makes that procedure followable.

## Proven, not assumed

Two byte-identical board inputs route byte-identically across **all 197 nets** — every waypoint,
via, and layer identical. Reproduce it yourself: render any board twice and diff its copper.

```sh
bun render-board.ts pcba.tsx        # writes out/pcba.circuit.json
cp out/pcba.circuit.json /tmp/a.json
bun render-board.ts pcba.tsx        # same input, again
diff /tmp/a.json out/pcba.circuit.json   # empty — identical
```

## Deterministic is NOT the same as local

The router re-optimizes the **entire board from scratch on every render.** It keeps no memory of
the previous solution and has no bias toward leaving unchanged nets where they were. So any change
anywhere — one pinned trace, one nudged part, one added net — deterministically re-routes nets
*everywhere*. Determinism means the ripple is repeatable; it does not mean the ripple is small.

Measured on this board: pinning just the four tiny **D+/D− USB traces** (a corner cluster ~3 mm
across) re-routed **38 of 197 nets — 19 % of the board** — rippling 61 mm out to the *opposite*
corner, where the RS485 net (`U7.A → J9.A`) gained two vias it did not have before. None of those
nets is near the USB corner. They moved because the whole layout is **one coupled solve**, and
pinning four traces shifted the global optimum.

## This is the "whack-a-mole"

Fix one spot, three others break. That is not the router being random and not the router
"fighting" you — it is the exact, repeatable behavior of a deterministic global optimizer with
**zero solution-locality**. Pin a net → the optimum over every remaining net moves → dozens of
untouched nets move with it. Same input, same moles, every time. Render again and you get the
identical moles, not new ones.

## What this means for how you work

- **Do not re-litigate determinism, and do not attribute a ripple to randomness.** Output is a
  pure function of input. A net that moved, moved *because of the one thing you changed*.
- **Determinism is what makes the routing procedure followable — not a license to run
  experiments.** The goal is never to *characterize* where the autorouter fails; it is to *route
  the board* ([`routing-procedure.md`](routing-procedure.md)). Because output is a pure function of
  input, that procedure's pivotal step — add the autorouter's traces back one at a time and see
  which one fails — gives a definite, repeatable yes/no, and every "comment out the offending
  trace" decision stays stable across renders. Use determinism to route, not to write reports.
- **A ripple is working-as-designed, not a bug.** A pin 3 mm away legitimately moving a net across
  the board is what a global optimizer does. Expect it, don't be surprised by it, and don't declare
  the router broken.
- **To stop the whack-a-mole, take nets out of the solve — don't negotiate with it.** Every net you
  hand-route (`pcbPath` / `pcbComb` — see [`route-hints.md`](route-hints.md)) leaves the
  autorouter's domain. When an autorouter trace interferes with copper you're owning, the move is
  not to reason about it or route around it — it is to **comment that trace out** (evict it) and, if
  it's a net you need, own it too. The only way a net stays put is to own it.

## Own a region completely or not at all

The USB-C corner is fully hand-routed (commit `97589ecf`) for exactly this reason. A region that is
half-pinned and half-autorouted hands the router a fresh coupled sub-problem on every render, so
the autorouted half keeps moving under the manual half — the whack-a-mole, localized. Owning
*all* of a region removes it from the solve; owning *some* of it does not. Pin the whole cluster or
leave the whole cluster to the router.
