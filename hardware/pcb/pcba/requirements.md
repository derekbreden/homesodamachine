# Board requirements

The rules this board must meet, enumerated. Each one is an executable check in
[`scorecard.ts`](scorecard.ts), computed from the routed circuit-json by
[`pick-data.ts`](pick-data.ts) on every build. The verdict shows in two places, from the same
geometry, so neither audience can narrate around it:

- **The terminal** — printed at the end of `bun render-board.ts pcba.tsx` (what an agent sees).
- **The modal** — the top of the viewer's Board-checks panel, and the `% hand-routed` on the
  board chip (what you see).

Requirements come in two kinds. **Gates** must hold for the board to fab; a failing gate is a
broken board. **Goals** are the manual-routing conversion this effort exists to drive — progress,
not a gate: the board still fabs while it converts.

## Gates — must hold to fab

| # | Requirement | Floor | Why | Audit |
|---|---|---|---|---|
| 1 | Every net fully connected in copper | 0 opens | An open ships a dead pin the clearance floor can't see | [`connectivity.ts`](connectivity.ts) |
| 2 | Copper-to-copper clearance | ≥ 0.14 mm | Below the fab's etch tolerance nets bridge | [`clearance.ts`](clearance.ts) |
| 3 | No overlaps / courtyard faults / slivers | 0 errors | Genuine DRC failures — shorts, part collisions, acid traps | [`clearance.ts`](clearance.ts) |
| 4 | No part-body overlaps | gap ≥ 0 mm | Two packages can't occupy the same air | [`footprint-audit.ts`](footprint-audit.ts) |
| 5 | Connector bodies clear of edge & neighbours | 0 flagged | Housings must physically seat and mate | [`connector-audit.ts`](connector-audit.ts) |
| 6 | Every placed part carries a JLCPCB # | all sourced | An unsourced placed part can't be assembled | fab stats |
| 7 | Min drill | ≥ 0.2 mm | JLCPCB standard drill floor | fab stats |
| 8 | THT-pad annular ring | ≥ 0.13 mm | JLCPCB component-pad ring floor | fab stats |
| 9 | Via annular ring | ≥ 0.1 mm | JLCPCB's recommended via is 0.5/0.3 = 0.1 mm ring; split from #8 so it doesn't false-flag every via | fab stats |
| 10 | Current-carrying traces wide enough | 0 narrow | A 0.2 mm logic trace melts under a motor's amps | [`ampacity-audit.ts`](ampacity-audit.ts) |
| 11 | Support caps within budget of their part | 0 flagged | A decoupler far from its pin doesn't decouple | [`cap-audit.ts`](cap-audit.ts) |

Gates 8 and 9 are split because JLCPCB's annular floors differ by hole type: a component (THT) pad
wants ≥ 0.13 mm of ring, but a via is fine at the recommended 0.5 mm pad / 0.3 mm hole = 0.1 mm ring.
Every via on this board sits at exactly 0.1 — intentional, not a defect. A single floor would paint
all 123 of them red.

## Goals — the manual-routing conversion

The autorouter cannot deliver traces that meet these requirements, so the board is going **100%
manual**. The poured planes carry power and ground (`<copperpour>`: V12, V3V3, V5, SDA, SCL, GND);
every **signal** net becomes hand-routed outer copper with **no vias**. See
[`hand-routing.md`](hand-routing.md) for how to place that copper.

| Goal | Target | Meaning |
|---|---|---|
| Signal nets hand-routed on outer copper | 100% | The headline — `% hand-routed`. A signal net is "hand-clean" when all its copper is on one outer layer (top/bottom) with no via |
| No vias on signal nets | 0 | Planes stitch to their pads; signals don't hop layers. A signal via means the trace dodged a plane instead of routing around it |
| No signal copper on inner layers | 0 | Inner layers are planes only. Inner-layer signal copper is autorouter copper by definition |

**How the split is measured.** There is no "manual" flag in the circuit-json, so the split is by
**authorship**, read from source. A net counts as hand-routed only when *every* trace carrying its
copper was authored by hand — a `<trace>` with `pcbPath`, `pcbComb`, or `pcbStraightLine` — **and**
its copper is clean (one outer layer, zero vias, zero inner-layer points). Geometry alone is not
enough: the autorouter routes most short nets clean-shaped by accident, and crediting that as
"hand-routed" would count the autorouter's own copper as progress toward removing it. Authored traces
are matched to nets through `source_trace.display_name` (`"<from> to <to>"`); poured plane nets are
exempt (their vias are plane stitches), identified from the `<copperpour connectsTo="net.X">` tags so
the exemption tracks the pours. Converting a net off the autorouter — i.e. giving it a hand path —
*automatically* moves the number; nothing to mark by hand.

## The gate is permission; the goal is the work

Green gates mean **fab-ready**, not **done**. `≥ 0.14 mm, zero errors` is permission to proceed —
the goal is a tight, hand-routed board that doesn't read as autorouted. Handing a net back to the
autorouter to make a number go green is the exact failure this whole effort exists to end. The
`% hand-routed` is the only number that measures the real work; watch that one.
