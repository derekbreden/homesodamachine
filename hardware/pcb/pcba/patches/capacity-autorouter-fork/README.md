# capacity-autorouter fork — through-hole vias

The stock `@tscircuit/capacity-autorouter` is a blind/buried-capable router: it routes on all
copper layers and places vias that span whatever consecutive z-layers a route happens to
transition between. JLCPCB standard assembly (and most low-cost fabs) drills **through-holes
only** — no blind/buried vias — so an inner-layer route with a `top→inner1` via is not
manufacturable there.

We route signals on the inner copper (it frees the outer layers and keeps the bottom GND plane
nearly trace-free), so we need the router to use every layer **and** produce only full-stack
(top↔bottom) vias. That's a constraint the stock router doesn't model, so we maintain a small
fork — taught at the mesh (the decision point), not patched on the output.

## The idea

A through-hole via is conductive on *every* layer, so it may only exist where the **whole board
column is clear**. The routing mesh already answers "which layers are free at this XY" per node
(`availableZ`, carved from the obstacles). So the rule is exactly:

> a node is **via-capable** iff its `availableZ` spans the full board stack.

A node with only *some* layers free sits under a pad or barrel on the missing layer(s); a via
born there would be blind/buried or would drill that obstacle. There's no new geometry and no
layer-count plumbing — `availableZ` already encodes it, and every downstream solver variant reads
`availableZ`, so teaching the mesh teaches all of them at once.

## What the fork changes

Triggered by the board prop **`autorouter={{ viaMode: "through-hole" }}`** (see `pcba.tsx`),
which `@tscircuit/props` now accepts, `@tscircuit/core` lowers to `SimpleRouteJson.viaMode`, and
the router honors. Off by default → identical to upstream.

**`@tscircuit/rectdiff`** (`rectdiff.source.patch`, ~2 files) — the mesh:
- `lib/types/srj-types.ts`: add `viaMode` to `SimpleRouteJson`.
- `lib/RectDiffPipeline.ts`: in `getOutput`, when `viaMode === "through-hole"`, split every node
  whose `availableZ` is a strict, multi-layer subset of the stack into one single-layer node per
  free layer. Traces still route on each layer; no via can be born there (a single-z node offers
  no other z to hop to). Full-stack nodes stay via-capable; single-layer nodes pass through.

**`@tscircuit/capacity-autorouter`** (`capacity-autorouter.source.patch`, ~3 files) — emission:
- `lib/types/srj-types.ts`: add `viaMode` to `SimpleRouteJson`.
- `lib/utils/convertHdRouteToSimplifiedRoute.ts`: in through-hole mode, span every emitted via
  `top↔bottom`. Sound because the mesh only births vias where the full column is clear, so
  widening the span crosses no foreign copper — it's a real drilled hole, not a re-labeled blind
  via.
- `AutoroutingPipeline4_TinyHypergraph`: pass `srj.viaMode` into the emitter.

`@tscircuit/core` (in `../@tscircuit%2Fcore@0.0.1351.patch`): lowers `autorouter.viaMode` →
`srj.viaMode` (beside `traceClearance`), and `EVERY_LAYER` is derived from the board's real layer
stack so a plated-hole barrel blocks routing — and reduces `availableZ` — on every layer it
occupies (this is what makes `availableZ` honest enough for the via-capable test to be correct).
`@tscircuit/props` (in `../@tscircuit%2Fprops@*.patch`): adds `viaMode` to the autorouter schema.

The board DRC (`../../clearance.ts`) independently asserts no blind/buried via and no barrel
crossing foreign copper on any layer survives.

## How it ships

The **built** fork dist is vendored via the bun patch
`../@tscircuit%2Fcapacity-autorouter@0.0.583.patch` — capacity-autorouter's build bundles rectdiff
from source (`main: lib/index.ts`), so the built dist already contains the rectdiff change. The
patch is a whole-file replacement of the minified `dist/index.js` (large because terser re-mangles
the whole bundle); the two `*.source.patch` files here are the human-readable intent.

## Rebuilding on an upstream bump

```sh
# capacity-autorouter (bundles rectdiff from source)
git clone --branch v0.0.583 https://github.com/tscircuit/capacity-autorouter.git
cd capacity-autorouter && bun install
git apply /path/to/patches/capacity-autorouter-fork/capacity-autorouter.source.patch
( cd node_modules/@tscircuit/rectdiff && git apply /path/to/rectdiff.source.patch )  # or patch -p0
bun run build   # -> dist/index.js (rectdiff bundled in)
```

Then re-vendor `dist/index.js` into the bun patch:

```sh
cd hardware/pcb/pcba
bun patch @tscircuit/capacity-autorouter
cp /path/to/capacity-autorouter/dist/index.js node_modules/@tscircuit/capacity-autorouter/dist/index.js
bun patch --commit node_modules/@tscircuit/capacity-autorouter
```

Regenerate the two `*.source.patch` files and update the version pins here if the version moved.
