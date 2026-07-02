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

The fork is a real GitHub fork: **https://github.com/derekbreden/tscircuit-autorouter**, branch
`homesodamachine/through-hole-vias` (pinned off upstream tag `v0.0.583`). It carries the CAR
source changes, the built `dist/` committed on the branch (CAR's build bundles rectdiff from
source, so the committed dist already contains the rectdiff change), and `homesodamachine-fork/`
(the rectdiff change + rebuild notes). `main` tracks upstream; our changes live on the branch.

The project consumes it with a `bun` override in `hardware/pcb/pcba/package.json`, pinned to the
branch commit:

```json
"overrides": { "@tscircuit/capacity-autorouter": "github:derekbreden/tscircuit-autorouter#<sha>" }
```

No vendored minified blob, no bun patch for this package — the two `*.source.patch` files here are
mirrors of what's on the fork branch, kept for review next to the other packages' patches.

## Rebuilding / bumping upstream

Work in the fork repo (`derekbreden/tscircuit-autorouter`): sync `main` from upstream, rebase or
re-apply the branch, `bun install`, apply `homesodamachine-fork/rectdiff.source.patch` to
`node_modules/@tscircuit/rectdiff`, `bun run build`, commit `dist/`, push. Then bump the override
SHA in `package.json` and `bun install`. (rectdiff is carried as a build-time patch for now; the
endpoint is a matching `derekbreden/rectdiff` fork so the CAR fork depends on it directly — see the
repo-level fork plan.)
