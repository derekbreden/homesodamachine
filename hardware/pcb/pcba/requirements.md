# Board requirements

The rules this board must meet, enumerated. Each one is an executable check that runs on every
build. The **gates** and **goals** below are computed from the routed circuit-json by
[`pick-data.ts`](pick-data.ts) and reported by [`scorecard.ts`](scorecard.ts); the **drill
coverage** checks at the end read the emitted Excellon files. The scorecard verdict shows in two
places, from the same geometry, so neither audience can narrate around it:

- **The terminal** — printed at the end of `bun render-board.ts pcba.tsx` (what an agent sees).
- **The modal** — the top of the viewer's Board-checks panel, and the `pcbPath · pcbComb · % score`
  on the board chip (what you see).

Requirements come in two kinds. **Gates** must hold for the board to fab; a failing gate is a
broken board. **Goals** are the manual-routing conversion this effort exists to drive — progress,
not a gate: the board still fabs while it converts.

## Gates — must hold to fab

| # | Requirement | Floor | Why | Audit |
|---|---|---|---|---|
| 1 | Every net fully connected in copper | 0 opens | An open ships a dead pin the clearance floor can't see | [`connectivity.ts`](connectivity.ts) |
| 2 | Copper-to-copper clearance | ≥ 0.14 mm | Below the fab's etch tolerance nets bridge | [`clearance.ts`](clearance.ts) |
| 3 | No overlaps / courtyard faults / slivers / pad shadows | 0 errors | Genuine DRC failures — shorts, part collisions, acid traps, and foreign trace copper inside a pad's through-stack shadow (every pad's column is via-in-pad territory: plane stitches and pad-via-to-pad-via land there) | [`clearance.ts`](clearance.ts) |
| 4 | Part keep-outs clear (IPC-7351 courtyard) | no overlap | Bodies measured as copper + IPC courtyard excess (Nominal 0.25 mm); a real overlap can't be assembled. Sub-Nominal-but-copper-clears pairs are an advisory, not a fab-blocker | [`footprint-audit.ts`](footprint-audit.ts) |
| 5 | Connector bodies clear of edge & neighbours | 0 flagged | Housings must physically seat and mate | [`connector-audit.ts`](connector-audit.ts) |
| 6 | Every footprint imported (`tsci import`), not hand-drawn | 0 hand-drawn | A hand-drawn land is a guess about the part JLCPCB ships; the import is the library's own geometry | [`import-provenance-audit.ts`](import-provenance-audit.ts) |
| 7 | Every placed part carries a JLCPCB # | all sourced | An unsourced placed part can't be assembled | fab stats |
| 8 | Min drill | ≥ 0.2 mm | JLCPCB standard drill floor | fab stats |
| 9 | THT-pad annular ring | ≥ 0.13 mm | JLCPCB component-pad ring floor | fab stats |
| 10 | Via annular ring | ≥ 0.1 mm | JLCPCB's recommended via is 0.5/0.3 = 0.1 mm ring; split from #9 so it doesn't false-flag every via | fab stats |
| 11 | Every top-side SMD pad has solder paste | all covered | A pad with no stencil aperture reflows its IC on bare copper (the gerber fork derives F_Paste from the copper) | fab stats |
| 12 | Current-carrying traces wide enough | 0 narrow | A 0.2 mm logic trace melts under a motor's amps | [`ampacity-audit.ts`](ampacity-audit.ts) |
| 13 | Support caps within budget of their part | 0 flagged | A decoupler far from its pin doesn't decouple | [`cap-audit.ts`](cap-audit.ts) |

Gates 9 and 10 are split because JLCPCB's annular floors differ by hole type: a component (THT) pad
wants ≥ 0.13 mm of ring, but a via is fine at the recommended 0.5 mm pad / 0.3 mm hole = 0.1 mm ring.
Every via on this board sits at exactly 0.1 — intentional, not a defect. A single floor would paint
all 152 of them red.

## Goals — hand-routed, and kept that way

The autorouter cannot deliver traces that meet these requirements, so the board is **100%
hand-routed**. The poured planes carry power and ground (`<copperpour>`: V12, V3V3, V5, GND);
every **signal** connection is hand-authored copper — a `<trace>` with `pcbPath`,
`pcbStraightLine`, or `pcbComb` (the I2C bus rides the inner plane layers as `routeInner`
paths). See [`hand-routing.md`](hand-routing.md) for how to place it.

The headline is a single **score**, counted per rendered signal *connection* (a `source_trace`):

```
score = 100 · (pcbPath + pcbComb) / (pcbPath + pcbComb + deferred + auto)
```

| Bucket | Weight | Meaning |
|---|---|---|
| `pcbPath` | 1.0 | Connections on explicit hand paths (`pcbPath` / `pcbStraightLine`) — done |
| `pcbComb` | 1.0 | Connections on a comb *strategy* (`pcbComb`) — done. A comb is deliberate hand routing, interchangeable with an explicit path: use whichever reads nicer and packs denser |
| `deferred` | 0 | A connection commented out of source — drops the score; none on this board |
| `auto` | 0 | A live signal left to the autorouter — drops the score; none on this board |

`score` is 100 only when every connection is hand-authored — no `auto`, no `deferred` — which is
where this board sits (`130 pcbPath · 0 pcbComb · 100% score`). The counts ride the chip and the
terminal; an `auto` or `deferred` reappearing is a regression to fix, not a backlog to burn down.
The live work is **tightening** — pulling components into denser bundles, toward a smaller board:
the real size floor is the board-edge parts (JSTs, screw terminal, USB-C, buttons, antenna) and
the interior those edges enclose.

**How the split is measured.** There is no "manual" flag in the circuit-json, so authorship is read
from source. Each hand-authored `<trace>` (a `pcbPath`/`pcbStraightLine` is `path`; a `pcbComb` is
`comb`) is matched to its rendered connection through `source_trace.display_name` (`"<from> to <to>"`),
normalising both endpoints to an unordered pin-pair key. A `pcbFan`-style trace has a literal `from`
but a dynamic `to={…}` (a `.map`), so it's matched by its `from` pin. Connections **to a net**
(`"X to net.Y"`) are plane stitches — outside the routing universe. Everything not matched to an
authored trace is `auto`. Giving a connection a hand path *automatically* moves the score — nothing
to mark by hand — and crediting clean-looking autorouter copper (which the router produces by
accident) is impossible, because the credit follows authorship, not shape.

## Drill coverage — asserted where the files are written

Read from the emitted Excellon rather than the circuit-json, and thrown at gerber-write time, so a
board that fails one produces no fab set at all. Both name the features they are missing.

| Requirement | Floor | Audit |
|---|---|---|
| Every via + plated hole claims its own hit in `drill.drl`, on position and drilled diameter | 0 undrilled, 0 mis-sized | [`render-board.ts`](render-board.ts) `assertFullyDrilled` |
| Every non-plated hole likewise in `drill_npth.drl` | 0 undrilled, 0 mis-sized | [`render-board.ts`](render-board.ts) `assertFullyDrilled` |

A `routeInner` via declares its span as the copper transition it makes (`top->inner1`), and the
Excellon converter emits only the spans it is asked for — the default `top->bottom`.
`throughDrilled` restates every via as the through-hole it physically gets, before the drill file
is generated and after the copper layers are.

## The gate is permission; the goal is the work

Green gates mean **fab-ready**, not **done**. `≥ 0.14 mm, zero errors` is permission to proceed —
the goal is a tight, hand-routed board that doesn't read as autorouted. The `score` guards that
every connection stays hand-authored; the tightening toward a smaller board is the work that
remains.
