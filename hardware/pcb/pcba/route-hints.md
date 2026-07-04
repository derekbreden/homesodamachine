# Influencing PCB routing on this board

`pcba.tsx` renders with the **capacity autorouter** — the `<board autorouter={{ viaMode:
"through-hole", … }}>` default (`groupMode: "subcircuit"`). That choice decides which
routing controls actually do anything: a few tscircuit knobs are wired only to the *other*,
opt-in `sequential-trace` router and are silently inert here.

## The trap: `pcbRouteHints` does nothing here

The `<trace pcbRouteHints={[…]}>` prop is **silently ignored by the capacity autorouter**.
It is read only by the `sequential-trace` router, which this board does not use — the prop
never reaches the capacity solver's input, so it produces no error and no effect. It will
look like it did nothing, because it did nothing. Don't reach for it. (Verified by render
test: under capacity the trace ignores the hint; only `groupMode: "sequential-trace"` honors
it.)

## Soft nudge: `<tracehint>`

To push a specific trace through a point and let the router do the rest, anchor a hint to the
port the trace lands on:

```tsx
// nudge the trace on U11.pin3 up through (12, 4)
<tracehint for=".U11 > .pin3" offsets={[{ x: 12, y: 4 }]} />
```

The capacity path splices the waypoint into that connection and routes through it. Caveats:

- **Positional only.** `via` / `to_layer` on the offset are dropped when the capacity input
  is built — a `<tracehint>` cannot force a via or a layer here, only a location.
- **Put the waypoint between the two pads.** The connection is joined as a tree: a waypoint
  between the endpoints becomes a pass-through detour; one off to the side becomes a dead-end
  stub.
- **Offsets are absolute board coordinates** when the `<tracehint>` is a direct child of
  `<board>` (they are taken through the hint's own transform, which is identity there).

## Deterministic: `pcbPath` / `pcbComb` / `pcbStraightLine`

When you need a *guaranteed* result — a specific path, a via at a point, a chosen layer — use
the manual-trace props. They lay fixed copper in the manual-trace phase *before* the
autorouter and are excluded from it, so the router cannot override them (this is what the
board's pump-bus fan-out already uses):

- **`pcbStraightLine`** — force a straight trace between two pads.
- **`pcbPath={[{ x, y }, { x, y, via: true, toLayer: "inner2" }, …]}`** — a full manual path:
  waypoints, real vias with `fromLayer` / `toLayer`, per-segment layer. The only hint-like
  tool that can force a via and a landing layer.
- **`pcbComb`** — computed straight→45°→straight comb for pin-line bundles (our core fork;
  open upstream PR [tscircuit/core#2567](https://github.com/tscircuit/core/pull/2567)). See
  [`FORKS.md`](FORKS.md).

## Which to reach for

- Router made a mess in one spot, just needs a nudge → `<tracehint>`.
- Need an exact path, a via, or a specific layer → `pcbPath` (or `pcbComb` for a bundle).
- `pcbRouteHints` prop → never, on this board.

Why the two hint spellings differ, and why only one reaches the capacity router, is written up
upstream-style in the core fork at `core/docs/PCB_ROUTE_HINTS.md`.
