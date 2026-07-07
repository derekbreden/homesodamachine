# Hand-routing manual traces (`pcbPath`)

This is the foundation for moving nets off the autorouter onto clean, tight, deterministic
manual copper. Read [`routing-procedure.md`](routing-procedure.md) first for *how* to take
territory (own a region, evict — never negotiate); this doc is about *placing the copper
correctly* once you do, which is where hand routing on this board actually goes wrong.

## The one thing that trips everyone up: the coordinate frame

A `pcbPath`'s numeric `{x, y}` points are **not board coordinates**. They are in the **`from`
component's own frame**:

```
board = center + R(rotation) · local
```

- **`center`** is the component's *resolved pcb center* — its placement `x`/`y` **plus the
  footprint's own offset**. It is **not** always the JSX `x`/`y`. J14 is placed at `x={-62}`
  but its resolved center is **−62.45** (a −0.45 mm footprint offset). Use the wrong center
  and every point on the path lands off by that offset.
- **`rotation`** is the component's `rot`. The corner parts J14/U14 are `rot 270`; C22 is
  `rot 0`. Rotation is applied, so on a rot-270 part a local `{x, y}` maps to board
  `(cx + y, cy − x)` — the axes swap. Forget the rotation and the whole path is rotated 90°.

Both facts together are the single reason hand paths "look right in the source and land in the
wrong place." Read the resolved center off a render (see `frame` below), never off the JSX.

Inverse (board → local), which is what the helper's `.at()` does:

```
local = R(−rotation) · (board − center)
   rot 0:   { x: bx−cx,           y: by−cy }
   rot 270: { x: cy−by,           y: bx−cx }   (i.e. R(-270) of the delta)
```

Vias are **full-stack top↔bottom only** (JLCPCB drills through-holes; the inner layers are the
autorouter's). So a hand path lives on **top or bottom** — you cannot hop to an inner layer.

## The `frame` helper (in `pcba.tsx`)

`frame(cx, cy, rot)` captures one component's resolved center + rotation and gives two ways to
author a point, so intent is explicit **and survives moving the component**:

- **`.at(bx, by)`** — a fixed **board** point. Stays put when *this* component moves. Use it for
  the far end of a run, the part shaped against **another** (stationary) component's pads.
- **`.off(dx, dy)`** — a raw **local offset**. Travels **with** this component. Use it for the
  near end, the part shaped against **this** component's own body/pads.

```tsx
const U14_X = -56.25, U14_Y = 17.75      // one source of truth for the placement
const U14f = frame(U14_X, U14_Y, 270)
const J14f = frame(-62.45, 17.75, 270)   // resolved center: placement -62 + footprint -0.45

<trace from="U14.pin1" to="J14.pin10" pcbPath={[
  "U14.pin1",
  U14f.off(-0.95, -0.35),   // exit, shaped against U14 — rides U14 when it moves
  U14f.off(1.5, -0.35),
  U14f.at(-58.75, 16.25),   // approach, shaped against J14's pads — stays board-fixed
  U14f.at(-58.75, 17.0),
  "J14.pin10",
]} />
```

Pad references are plain strings (`"U14.pin1"`); numeric points are frame calls. All numeric
points in one `pcbPath` are in the **`from`** component's frame regardless of which helper you
name — `J14f.off(...)` inside a `from="U14…"` trace still resolves in U14's frame, so keep the
helper you call matching the trace's `from`.

## Moving a component tighter

This is the workflow that makes packing the board a one-line change instead of a waypoint
rewrite:

1. Change only the component's placement const (`U14_X`, `C22_X/Y`). The `<Component>` and its
   `frame` both read it, so they can't desync.
2. **`.at()` points hold their board position; `.off()` points ride along.** No retuning of the
   waypoints that shape a run against fixed pads.
3. Retune only the **cross-component approach** — a point on one component's trace that targets
   *another moving* component. Express it in terms of that component's const so it follows, e.g.
   `U14f.at(C22_X - 1.0, 19.5)` puts a point under `C22.pin1` wherever C22 goes.
4. Re-render and check the floor. If it went negative, read *which* pair — your own pad vs your
   own trace is a real geometric limit (fix the trace or accept the position); an autorouter
   trace in your corridor is something to **evict**, per the procedure.

Real limits found doing exactly this at the USB-C corner: U14 pulls ~1.0 mm west before its own
D+ pad crowds the interleaved D− escape lane; C22 pulls ~0.5 mm south before its **courtyard**
(not its copper) overlaps U14's. Copper clearance and courtyard keep-out are different limits —
the floor catches the first, `picks.json` `errors` catches the second.

## The verify loop

Render is the ground truth; author, render, measure — never eyeball placement.

```
bun render-board.ts pcba.tsx          # writes out/pcba.circuit.json + out/pcba.picks.json
```

- **Floor + errors:** `out/pcba.picks.json` → `clearance.floor` (target **≥ 0.14**) and
  `errors` (must be empty — includes courtyard/placement, not just clearance). This is the
  board's own DRC ([`clearance.ts`](clearance.ts)), which now measures copper leaving vias.
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
