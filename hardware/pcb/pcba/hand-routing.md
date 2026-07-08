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

`frame(name, cx, cy, rot, pins)` captures a component and turns pin geometry into path points. It
knows each pad's footprint-local offset (the `pins` table, read once from a render and
movement-invariant), so it can **divine where a pad actually is** — not just where the center is.
Every method returns a point in the trace's **`from`** frame:

| call | returns | how it moves |
|---|---|---|
| `.ref(pin)` | the string anchor `"U14.pin1"` | — (use for a pcbPath's endpoints) |
| `.pin(pin)` | the pad's **board** `{x,y}` | — |
| `.at(bx, by)` | a fixed **board** point | stays put when this component moves |
| `.off(dx, dy)` | a raw **local** offset | rides this component |
| `.fromPin(pin, bx, by)` | a point `bx,by` mm (board axes) from **this** frame's own pad | **rides** the pad — an exit stub follows its pad |
| `.toPin(f, pin, bx, by)` | a point `bx,by` mm from **another** frame `f`'s pad | board-fixed, but **follows** that pad if `f` moves |

```tsx
const U14_X = -56.25, U14_Y = 17.75          // one source of truth for the placement
const U14f = frame("U14", U14_X, U14_Y, 270, { pin1: [-0.95, -1.149], /* … */ })
const J14f = frame("J14", -62.45, 17.75, 270, { pin10: [0.75, 2.624], /* … */ })

<trace from="U14.pin1" to="J14.pin10" pcbPath={[
  U14f.ref("pin1"),
  U14f.fromPin("pin1", 0.8, 0),        // exit 0.8 mm east of pin1 — rides pin1
  U14f.fromPin("pin1", 0.8, -2.45),    // drop south of U14's body
  U14f.at(-58.75, 16.25),              // thread the gap by the pad column (board-fixed)
  U14f.toPin(J14f, "pin10", 1.08, 0),  // approach pin10 — tracks it if J14 moves
  J14f.ref("pin10"),
]} />
```

All numeric points in one `pcbPath` resolve in the **`from`** frame regardless of which helper
name you call — it's the receiver (`U14f.toPin(...)`) that matters, and it must be the `from`
frame. The `pins` offsets are footprint-baked; regenerate them (and the resolved center) from a
render if a footprint changes (`plot-region.py`, or read `pcb_smtpad`).

## Pattern helpers

Built on the frame primitives — add your own (a comb, a serpentine) the same way:

- **`pcbU(f, a, b, [dx, dy])`** — a no-via "U" tie between two pads of the same connector: out from
  `a` by the board stub `[dx,dy]`, across to `b`, back in. One jumper, not a second full path. The
  D+ tie is `pcbU(J14f, "pin10", "pin8", [-1.4, 0])` (bulges 1.4 mm west of the pad row).
- **`pcbFan(srcF, srcPin, [ex,ey], destF, destPins, laneX)`** — fan one source pad to several dest
  pads sharing an approach lane: each branch exits the source the same way, runs to board
  `x=laneX`, then to its dest pad's row and in. Returns one `{ to, pcbPath }` per dest — `.map`
  them onto `<trace>`. The D− pair is
  `pcbFan(U14f, "pin3", [-0.85, 0], J14f, ["pin9", "pin7"], -58.25)`.

## Moving a component tighter

Packing the board is a **one-line change**, not a waypoint rewrite:

1. Change only the component's placement const (`U14_X`, `C22_X/Y`). The `<Component>` and its
   `frame` read the same const, so they can't desync.
2. **Every point auto-recomputes** — `.fromPin` exits ride their pad, `.toPin` approaches track
   their target, `.at` gap points hold, `.off` rides. Nothing to retune by hand.
3. Re-render and step the placement outward until the floor breaks; the last clean value is the
   limit. Read *why* it broke: your own pad vs your own trace, or a **courtyard** overlap, is a
   real geometric limit (accept the last-clean position); an autorouter trace in your corridor is
   something to **evict**, per the procedure.

Verified limits at the corner: U14 → ~1.0 mm west (its own D+ pad crowds the D− escape lane);
C22 → 1.25 mm west + 0.5 mm south (west ends at J14's courtyard, south at U14's). Both were found
by changing one const and re-rendering — the traces followed on their own. Note copper clearance
and courtyard keep-out are different limits: the floor catches the first, `picks.json` `errors`
the second (a courtyard overlap can flag while the floor still reads clean).

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
