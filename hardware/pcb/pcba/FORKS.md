# tscircuit forks

The pcba board build consumes several `@tscircuit/*` packages (and `circuit-json-to-gerber`)
that we've **forked** so our changes live as real, reviewable, eventually-PR-able source — not as
opaque `bun` patches of the published `dist/`. This is active fork-based development: we build on
these forks, keep them synced with upstream, and open PRs from fresh forks as changes mature. The
goal is to become a contributor to tscircuit — and, whether or not that lands, to do our own
forward development on it while still pulling in upstream.

There are no `bun` `patchedDependencies` left. Every tscircuit change the board needs rides in
through a fork — except `copper-pour-solver`, which we no longer fork (upstream superseded our fix),
now pinned to a stock upstream version (see below).

## The model

- **One fork per upstream package we change.** Each fork's `main` tracks upstream untouched; our
  work lives on the branch `homesodamachine/through-hole-vias`.
- **Consumed by a SHA-pinned `bun` `overrides` git dependency** in [`package.json`](package.json).
  That override is the single source of truth for which fork commit ships — this doc does not
  repeat SHAs (they would drift).
- **dist-shipping packages commit their built `dist/` on the branch** (upstream gitignores it), so
  a git-dependency consumer installs without building. Source-shipping packages need no committed
  dist — the consumer's build bundles their `lib/` directly.
- **`rectdiff` is not a top-level override.** It rides in as `capacity-autorouter`'s
  `@tscircuit/rectdiff` devDependency SHA — the *same git-SHA mechanism upstream itself uses to
  pin rectdiff* — and the CAR build bundles it from source.

## Syncing upstream

A weekly Claude Code routine (run from the laptop, not CI) pulls each upstream into the fork's
`main`, rebases our branch on top, rebuilds `dist/`, and re-pins the override SHA here. It is not a
GitHub Actions cron: scheduled workflows are disabled on forks by default.

## Opening PRs

As a change matures, open the PR from a **fresh fork off upstream `main`** carrying just that one
coherent change — never from the active dev branch, which bundles several changes and a committed
`dist/`. The active forks are our workbench; PRs are extracted clean.

## The forks

| Package | Fork | Base | Consumed via | What it changes | Upstream-PR-able |
|---|---|---|---|---|---|
| `@tscircuit/capacity-autorouter` | [tscircuit-autorouter](https://github.com/derekbreden/tscircuit-autorouter) | `v0.0.620` | override | via emission spans top↔bottom in through-hole mode | yes (with props/core/rectdiff) |
| `@tscircuit/rectdiff` | [rectdiff](https://github.com/derekbreden/rectdiff) | `v0.0.47` | CAR devDep SHA | mesh: a node is via-capable iff its `availableZ` spans the full stack | yes |
| `@tscircuit/props` | [props](https://github.com/derekbreden/props) | `v0.0.565` | override | `viaMode` on the autorouter config schema | yes |
| `@tscircuit/core` | [core](https://github.com/derekbreden/core) | `v0.0.1351` (held — see note) | override | `viaMode`/`traceClearance` lowering, honest `EVERY_LAYER`, 6/8-layer names, pour stitch/keepout/carve, hole clearance ring, silk ref-des rotation | mixed — the `viaMode` lowering yes; the pour/stitch logic is project-specific |
| `@tscircuit/footprinter` | [footprinter](https://github.com/derekbreden/footprinter) | `v0.0.363` | override | `flippinlabels` pinrow option + `applyNoRefDes` fix | yes (`flippinlabels` PR'd: [footprinter#672](https://github.com/tscircuit/footprinter/pull/672)) |
| `circuit-json-to-gerber` | [circuit-json-to-gerber](https://github.com/derekbreden/circuit-json-to-gerber) | `v0.0.78` | override | inlined Hershey single-stroke font for gerber text | maybe |
| `@tscircuit/cli` | [cli](https://github.com/derekbreden/cli) | `v0.1.1586` | override | multi-format export (its gerber output comes from the cjtg fork it depends on) | maybe |

**`@tscircuit/copper-pour-solver` is no longer forked.** Upstream added native pill/rotated_pill
geometry (PR #50) and a global connectivity map (#53/#56), superseding our fork's bounding-box fix.
tscircuit pins the old `0.0.29` (which reintroduces pour-shorts on this board), so `package.json`
pins stock upstream `0.0.36` via a plain version override instead.

**`@tscircuit/core` is held at `v0.0.1351`.** Its sync onto upstream `v0.0.1380` rebased cleanly but
regressed the board (pour-shorts): upstream refactored CopperPour connectivity
(`pour_connectivity_key` → `subcircuit_id` + `source_net_id`), so our project-specific pour logic
(auto-stitch, stitch-keepout, EVERY_LAYER) must be adapted to that new architecture before core can
advance. The synced attempt is preserved on the core fork's `homesodamachine/sync-v0.0.1380-wip`
branch as the starting point for that work. (The other six forks are synced to current upstream.)

The detailed through-hole-via design (why it's taught at the mesh, the decision point) is in
[`patches/capacity-autorouter-fork/README.md`](patches/capacity-autorouter-fork/README.md).

The gerber change (Hershey silkscreen font) has a single home in the `circuit-json-to-gerber` fork.
It reaches the board two ways, both pointing at that one fork: render-board.ts imports
`circuit-json-to-gerber` directly (top-level override), and `@tscircuit/cli` depends on it as a
devDependency that cli's build inlines into its bundle. The cli fork therefore carries only its own
change — the multi-format export — and inner-layer gerbers come for free from the fork's `0.0.78`
base (native there; they were only ever backported because cli's old `^0.0.51` pin predated them).

## Local working trees

The forks are checked out at **`~/Developer/tscircuit-forks/<pkg>`**, each on the
`homesodamachine/through-hole-vias` branch, with `origin` = our fork and `upstream` =
`tscircuit/<pkg>` (so the sync can `git fetch upstream` and rebase). Each tree's `HEAD` matches the
commit this project pins in [`package.json`](package.json) (for rectdiff, the commit the CAR fork
pins). The board build does **not** use these trees — it installs the forks from GitHub via the
overrides — they exist for developing the forks and running the weekly sync.

To develop a fork: edit its `lib/`/`src/`, then `bun install && bun run build` (commit the rebuilt
`dist/` for the dist-shipping packages — it's gitignored, so `git add -f dist`), push the branch,
and bump its SHA in [`package.json`](package.json) `overrides` (or the CAR fork's `package.json`
for rectdiff) followed by `bun install` here.

## Working on a fork (git-guard notes)

The homesodamachine worktree's `block-branch`/`block-commit-curation` hooks fire on any Bash in
this environment, including inside a fork clone. So, in a fork clone:

- Create the branch by **refspec push**, not a local branch command:
  `git push origin HEAD:refs/heads/homesodamachine/through-hole-vias`.
- `git checkout <tag>` / `<sha>` (whole-tree, detaches) is allowed; `checkout -b` / `switch -c` /
  `branch <name>` / `worktree add` / `gh pr create` / `push -u` are not.
- Stage with `git add -A lib` (or `src`) plus `git add -f dist` (dist is gitignored in the
  dist-shipping packages). Avoid `reset --hard` / `restore` / `checkout <path>` / `clean` /
  `stash push` (they discard tree state).
- Bump a fork: push the fork branch, then update its SHA in [`package.json`](package.json)
  `overrides` (or, for rectdiff, in the CAR fork's `package.json`) and `bun install`.
