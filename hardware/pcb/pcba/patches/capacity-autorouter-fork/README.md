# capacity-autorouter fork — through-hole vias

The stock `@tscircuit/capacity-autorouter` is a blind/buried-capable router: it routes on all
copper layers and places vias that span whatever consecutive z-layers a route happens to
transition between. JLCPCB standard assembly drills **through-holes only** — no blind/buried
vias — so an inner-layer route with a `top→inner1` via is not manufacturable there.

We route signals on the inner copper (it frees the outer layers and the bottom GND plane), so we
need the router to use every layer **and** produce only full-stack (top↔bottom) vias. This is a
constraint the stock router doesn't model, so we maintain a small fork.

## What the fork changes

Three source files, ~53 lines, gated behind the env var `TSCIRCUIT_THROUGH_HOLE_VIAS` (off by
default, so the fork is behavior-identical to upstream unless a consumer opts in). See
[`source.patch`](./source.patch):

1. **`lib/utils/convertHdRouteToSimplifiedRoute.ts`** — emission. Every via a route emits is
   normalized to span the full stack (`top`↔`bottom`) instead of its internal consecutive-z span.
   Sound because the router's route-vs-route via conflict model is already full-column (a via
   reserves its (x,y) against other routes on every layer).

2. **`lib/solvers/HighDensitySolver/SingleHighDensityRouteSolver.ts`** — placement guard. A via
   candidate is allowed only where the node's `availableZ` spans the entire board column
   (`availableZ.length >= boardLayerCount`). The mesh drops the covered layer from a node's
   `availableZ` wherever a pad sits, so requiring the complete stack keeps vias out of pad pockets
   — no through-hole barrel is ever drilled through a pad.

3. **`lib/solvers/HighDensitySolver/IntraNodeSolver.ts`** — plumbing. Passes the true board layer
   count (distinct from the per-node local `layerCount`, which is only the max port-z) down to the
   route solver so the guard has the real stack size.

Together: the router routes on inner copper, places vias only where the full column is clear, and
emits them as through-holes. The board DRC (`../../clearance.ts`) independently asserts no
blind/buried via and no barrel crossing foreign copper on any layer survives.

## How it ships

The **built** fork dist is vendored via the bun patch
[`../@tscircuit%2Fcapacity-autorouter@0.0.583.patch`](../@tscircuit%2Fcapacity-autorouter@0.0.583.patch)
(a whole-file replacement of the minified `dist/index.js` — large because terser re-mangles the
entire bundle). `render-board.ts` sets `TSCIRCUIT_THROUGH_HOLE_VIAS=1` so every `tsci` export it
spawns routes in through-hole mode.

## Rebuilding on an upstream bump

```sh
git clone --branch v0.0.583 https://github.com/tscircuit/capacity-autorouter.git
cd capacity-autorouter
git apply /path/to/patches/capacity-autorouter-fork/source.patch   # re-resolve conflicts if the version moved
bun install && bun run build                                        # -> dist/index.js
```

Then re-vendor the built `dist/index.js` into the bun patch:

```sh
cd hardware/pcb/pcba
bun patch @tscircuit/capacity-autorouter                            # re-extract stock into node_modules
cp /path/to/capacity-autorouter/dist/index.js \
   node_modules/@tscircuit/capacity-autorouter/dist/index.js
bun patch --commit node_modules/@tscircuit/capacity-autorouter      # regenerate the .patch
```

Regenerate `source.patch` from the fork clone with `git diff > source.patch` and update the
version pin here if it changed.
