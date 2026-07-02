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

## What the forks change

Triggered by the board prop **`autorouter={{ viaMode: "through-hole" }}`** (see `pcba.tsx`),
which `@tscircuit/props` now accepts, `@tscircuit/core` lowers to `SimpleRouteJson.viaMode`, and
the router honors. Off by default → identical to upstream. Two forks carry the routing change:

**[`derekbreden/rectdiff`](https://github.com/derekbreden/rectdiff)** — branch
`homesodamachine/through-hole-vias`, off `4af388d` (the commit CAR pins). The mesh:
- `lib/types/srj-types.ts`: add `viaMode` to `SimpleRouteJson`.
- `lib/RectDiffPipeline.ts`: in `getOutput`, when `viaMode === "through-hole"`, split every node
  whose `availableZ` is a strict, multi-layer subset of the stack into one single-layer node per
  free layer. Traces still route on each layer; no via can be born there (a single-z node offers
  no other z to hop to). Full-stack nodes stay via-capable; single-layer nodes pass through.

**[`derekbreden/tscircuit-autorouter`](https://github.com/derekbreden/tscircuit-autorouter)** —
branch `homesodamachine/through-hole-vias`, off `v0.0.583`. Emission:
- `lib/types/srj-types.ts`: add `viaMode` to `SimpleRouteJson`.
- `lib/utils/convertHdRouteToSimplifiedRoute.ts`: in through-hole mode, span every emitted via
  `top↔bottom`. Sound because the mesh only births vias where the full column is clear, so
  widening the span crosses no foreign copper — it's a real drilled hole, not a re-labeled blind
  via.
- `AutoroutingPipeline4_TinyHypergraph`: pass `srj.viaMode` into the emitter.
- Its `@tscircuit/rectdiff` devDependency points at the rectdiff fork by commit SHA (the same
  git-SHA mechanism upstream itself uses to pin rectdiff), so the build bundles the forked mesh
  from source — no build-time patch.

`@tscircuit/core` (still a bun patch, `../@tscircuit%2Fcore@0.0.1351.patch`, pending its own
fork): lowers `autorouter.viaMode` → `srj.viaMode` (beside `traceClearance`), and `EVERY_LAYER`
is derived from the board's real layer stack so a plated-hole barrel blocks routing — and reduces
`availableZ` — on every layer it occupies (this is what makes `availableZ` honest enough for the
via-capable test to be correct). `@tscircuit/props` (still a bun patch,
`../@tscircuit%2Fprops@*.patch`, pending its own fork): adds `viaMode` to the autorouter schema.

The board DRC (`../../clearance.ts`) independently asserts that no blind/buried via and no barrel
crossing foreign copper on any layer survives.

## How it ships

Both routing forks are real GitHub forks. `main` tracks upstream; our change lives on the
`homesodamachine/through-hole-vias` branch of each. The CAR fork commits its built `dist/` on the
branch (upstream gitignores it) so a git-dependency consumer installs it without building; the
rectdiff fork ships source (`main: lib/index.ts`), so CAR's build bundles it directly.

The project consumes the CAR fork with a `bun` override in `hardware/pcb/pcba/package.json`,
pinned to the branch commit; the rectdiff fork rides in as CAR's devDependency SHA:

```json
"overrides": { "@tscircuit/capacity-autorouter": "github:derekbreden/tscircuit-autorouter#<sha>" }
```

No vendored minified blob and no bun patch for either package — the reviewable source is the two
fork branches, PR-able to their upstreams.

## Rebuilding / bumping

To change the mesh, edit the rectdiff fork branch, push, and update the `@tscircuit/rectdiff` SHA
in the CAR fork's `package.json`. To change emission, edit the CAR fork branch. Either way, in the
CAR fork: `bun install` (pulls the rectdiff fork), `bun run build` (bundles the forked mesh into
`dist/`), commit `dist/`, push — then bump the override SHA in `hardware/pcb/pcba/package.json`
and `bun install`. To track upstream: sync each fork's `main` from upstream, rebase the branch,
rebuild, re-pin.
