# Autorouter coexistence with manual traces

How the capacity autorouter behaves when part of a region is hand-routed and the
rest is left to it — and the rule that follows. Companion to
[`route-hints.md`](route-hints.md) (which covers the `pcbPath` / `pcbComb`
mechanics themselves).

## The rule

To hand-route a region, own **every net that physically transits it**, not just
the nets logically assigned to it. A single through-net left to the autorouter
can be driven straight across the owned copper.

## Why

The capacity autorouter has two properties that together make partial-manual
routing unstable:

- **Deterministic.** The same input produces byte-identical routing (verified:
  197/197 nets unchanged across two identical renders). An autorouted net does
  *not* re-solve differently render-to-render — so "an autorouted net is never
  nailed down" is false. What changes the output is the *input* changing.
- **No solution locality, no corridor concept.** Pinning one net changes the
  obstacle field, and the deterministic solver then re-solves the *rest* with no
  bias toward its previous solution — a 4-net pin re-routed 38 nets (19% of the
  board) out to 61 mm away. Manual copper is just an obstacle that consumes local
  routing capacity; the solver has no notion of "this channel is reserved."

So the two stable regimes for a region are the endpoints — **0 % owned** (the
autorouter finds a clean global solution, if an ugly, via-heavy, inner-plane-
diving one) and **100 % owned** (removed from the solver's problem entirely). The
middle is a moving target: every net you pin re-solves a large fraction of the
rest, and the region's clearance floor is *worse* partway than at either end.

## The worked case — the USB-C corner (J14 / U14 / U13)

Measured from the autorouter-only baseline, owning the J14↔U14 target
(D+, D−, VBUS, CC, host) and reintroducing the autorouter one net at a time:

| state | floor | result |
|---|---|---|
| target owned, autorouter starved of all other point-to-point nets | 0.155 | clean — the target is fully ownable in isolation |
| + UART TXD alone (autorouted) | 0.155 | clean |
| + UART RXD alone (autorouted) | 0.155 | clean |
| + UART pair (TXD **and** RXD) | −0.2 | TXD short through manual D+/VBUS |
| + all other nets | −0.322 | TXD short + tightening |
| UART pair owned too, rest autorouted | 0.155 | clean |

Neither UART net fails alone — each finds a path that dodges the owned copper.
The failure **emerges at the pair**: TXD and RXD both escape the corner to the
WROOM through the one bottom corridor, the manual copper has consumed the corner's
spare capacity, and the solver resolves the over-capacity by overlapping TXD onto
the manual copper. The USBLC6/CH340 block sits bodily over the WROOM's north-
castellation fan-out, so the nets that transit the corner (UART, and under heavier
load the pump-control lines) are what must be owned — owning the *logical* USB nets
is not enough.

## Reproducing it

From an autorouter-only board (no manual corner):

1. Comment out every point-to-point `<trace>` so the autorouter is starved; keep
   the `to="net.*"` plane pickups so no pad floats.
2. Author the target nets as manual `pcbPath` routes; render
   (`bun render-board.ts <board>.tsx`) and confirm the target is clean in
   isolation — the clearance floor and error list land in `out/<board>.picks.json`.
3. Uncomment the autorouted nets one (or one contending group) at a time,
   rendering after each, until the floor breaks. The net that breaks it is the one
   to own.
