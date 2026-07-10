# Hand-routing manual traces (`pcbPath`)

This is the foundation for moving nets off the autorouter onto clean, tight, deterministic
manual copper. Read [`routing-procedure.md`](routing-procedure.md) first for *how* to take
territory (own a region, evict — never negotiate); this doc is about *placing the copper
correctly* once you do.

## Routing principles — the bar this board is held to

Passing DRC is the floor, not the goal. Every trace is an *engineered, intentional* choice; a
board reads as amateur the moment a segment sits somewhere "because that's where it ended up."
The rules below are what "engineered" means here — the helpers encode them so they're the path of
least resistance, but the helpers only matter if the *intent* is right.

1. **Right angles only.** Corners are 90° (or, where a channel is too tight for a square corner,
   45°) — never an arbitrary slope. A 2° slope is a bug, usually a wrong pad reference. `route`
   produces 90°-only paths by construction; verify with the angle check (all segments 0°/90°).

2. **Pads exit along their own face.** A trace leaves a pad *perpendicular to its edge, away from
   the body* — never attached to the pad's side. U1's south-edge pins exit **south** on a clean
   stub before any turn; a stacked resistor's midpoint escapes **sideways** past its own body.
   Side-entry is a defect: it looks sloppy and crowds the pad.

3. **Jog in open space, not at a pad.** The horizontal offset happens out in the clear, away from
   pads and vias — so the pad connection stays clean and the turn isn't cramped. Do the jog low
   (near the source) and run straight into the far pad, as the DOUT→IO36 tap does.

4. **Clearance is a resource — allocate it, never spend it by accident.** A run through a corridor
   between two parts is either **centred** (maximise clearance to both walls) or **deliberately
   biased to one wall to reserve the other side** as an open channel for a future trace. Hugging a
   wall for *no reason* is the worst outcome — it both shrinks clearance and blocks the corridor,
   for nothing. `channel(a, b, bias)` makes the choice explicit: `bias 0` centres, `±1` reserves.
   If you can't say why a segment sits at a given x, centre it.

These are priorities, in order: correctness (connected, DRC-clean, no vias) first, then these
intent rules. Where clearance is free, take it — the floor is a gate you pass, not a number you
sit on.

## Writing a path: `route` (in [`routing.ts`](routing.ts))

A hand trace is a `route(...)`: pad anchors at the ends, one-dimensional constraints between.
Every constraint reads in the **part's own frame**: `F.col(pin, d)` steps `d` along the part's
local-x from a pad, `F.row(pin, d)` along local-y; `F.east/west/above/below(pin, gap)` sit `gap`
clear of the pad's own +x/−x/+y/−y **edge** (real footprint size, so you write the clearance you
mean — never a guessed half-width; the frame reads each pad's true rectangle). The part's placement
rotation drops each onto a board col or row, so at rot 0 they *are* the plain board lines, but when
the part turns the whole trace turns with it — a cluster can be rotated and nothing inside it moves.
A corridor lane is a bare `{ col: x }` — board-absolute, anchored to no part, so it does **not**
ride. Consecutive constraints intersect into
the waypoints, and the closing turn into each pad comes from the pad itself — so every corner is
90° by construction, no point is ever written as a two-coordinate pair, and every coordinate
derives from the pad (or corridor) that shapes it. The path rides any move of its parts, alone or
as a group.

```tsx
<trace from="U14.pin1" to="J14.pin10" pcbPathRelativeTo="board" pcbPath={route(
    "U14.pin1",
    U14f.row("pin1", 0.8),     // U14 sits at rot 270, so a local row lands board-east of pin1
    U14f.col("pin1", 2.45),    // a local col lands board-south, down past the body
    J14f.row("pin10", 1.08),   // up into pin10
    "J14.pin10",
)} />
```

With no constraints, `route("R7.pin1", "C12.pin1")` is the straight pad-to-pad tie. The
`pcbPathRelativeTo="board"` on the trace makes the numeric points board coordinates — exactly
what the viewer and [`plot-region.py`](plot-region.py) read. Vias are full-stack top↔bottom only
(JLCPCB drills through-holes), so a hand path lives on **top or bottom**.

`frame(el)` supplies the pads: centre, rotation, and pad geometry all derive from the placed
element and its imported footprint, so the placement is the single source of truth. `.pin(p)` is
the pad's board `{x, y}`; `.col`/`.row` step along the part's local x / y from that centre, and `.east`/`.west`/`.above`/`.below(p, gap)` clear its local edges — all in the part's frame, so they ride when it turns. Frames register by name —
`route`'s `"U14.pin1"` anchors resolve through the registry.

**`channel(a, b, bias)`** gives a corridor run its x: `bias 0` centres between the column centres
`a` and `b`, `−1`/`+1` hugs one wall to reserve the other side (principle 4). The GAS EN tap runs
`{ col: channel(CX_EN, CX_DOUT) }` — centred in the R7/R3 corridor, not hugging either.

**`routeBottom(from, …, to)`** is `route`'s bottom-layer twin: same orthogonal waypoints, but the run
lives on the **bottom plane** between a via on the `from` pad and a via back up on the `to` pad — the
two pads are the *only* vias ("pad via to pad via"). Each via is a zero-length transition bracketed by a
coincident wire (tscircuit's via-alignment check wants a wire sitting on the via from both sides), which
`routeBottom` emits for you. The bottom GND pour antipads this copper like any signal crossing it, so a
clean render shows **0 errors** (a `pour-short` in `picks.json` means the trace is malformed or the pour
didn't void it). Reach for it only once the **top face is proven blocked** — top is always preferred —
and the bottom corridor is clear; its lanes are board-absolute `{ row }`/`{ col }` because they thread
board-fixed obstacles (plated holes, stitch vias), and any autorouter trace it fouls is deferred.

## Moving a component tighter

Packing the board is a **one-line change**, not a waypoint rewrite:

1. Change the number on the component's element tag (or its shared grid const). The placement and
   its `frame` read the same element, so they can't desync — and the drag editor rewrites the same
   literal.
2. **Every pad-derived point rides its pad** — a lone part or a whole group can move and the
   paths follow. Nothing to retune.
3. Re-render and step the placement outward until the floor breaks; the last clean value is the
   limit. Read *why* it broke: your own pad vs your own trace, or a **courtyard** overlap, is a
   real geometric limit (accept the last-clean position); an autorouter trace in your corridor is
   something to **evict**, per the procedure.

Verified limits at the corner: U14 → ~1.0 mm west (its own D+ pad crowds the D− escape lane);
C22 → 1.25 mm west + 0.5 mm south (west ends at J14's courtyard, south at U14's). Note copper
clearance and courtyard keep-out are different limits: the floor catches the first, `picks.json`
`errors` the second (a courtyard overlap can flag while the floor still reads clean).

## The verify loop

Render is the ground truth; author, render, measure — never eyeball placement.

```
bun render-board.ts pcba.tsx          # writes out/pcba.circuit.json + out/pcba.picks.json
```

- **Floor + errors:** `out/pcba.picks.json` → `clearance.floor` (target **≥ 0.14**) and
  `errors` (must be empty — includes courtyard/placement, not just clearance). This is the
  board's own DRC ([`clearance.ts`](clearance.ts)), and it measures copper leaving vias.
- **Zoom in** — the failure mode is routing from coordinates you can't see. Plot a region:

  ```
  tools/cad-venv/bin/python plot-region.py out/pcba.circuit.json -63 -52 13 23 /tmp/corner.png
  ```

  [`plot-region.py`](plot-region.py) draws pads, traces (by layer), vias, and pin labels for the
  board mm box `X0 X1 Y0 Y1`, so you place copper against what's actually there. For exact
  numbers, read the geometry straight from `out/pcba.circuit.json` (`pcb_smtpad` /
  `pcb_plated_hole` pads, `pcb_trace.route` copper, `pcb_via` vias).

## Rules of thumb

- The floor is a **gate**, not a score. `≥ 0.14` with zero errors is *permission to proceed*,
  not the goal — the goal is a tight, hand-routed board. Handing a net back to the autorouter to
  make a number go green is the failure this whole effort exists to end.
- One `pcbPath` per connection. A pad tie is one small jumper (D+ is `pin10→pin8` on top, one
  "U"); do not draw a second full path over copper that is already connected.
- Keep hand paths on top/bottom and off the inner planes; that discipline is the point (tighter
  packing and a board that doesn't read as autorouted).
