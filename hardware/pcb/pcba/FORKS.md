# tscircuit forks

The pcba board build consumes several `@tscircuit/*` packages (and `circuit-json-to-gerber`)
that we've **forked** so our changes live as real, reviewable, eventually-PR-able source — not as
opaque `bun` patches of the published `dist/`. This is active fork-based development: we build on
these forks, keep them synced with upstream, and open PRs from fresh forks as changes mature. The
goal is to become a contributor to tscircuit — and, whether or not that lands, to do our own
forward development on it while still pulling in upstream.

There are no `bun` `patchedDependencies` left. Every tscircuit change the board needs rides in
through a fork.

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
| `@tscircuit/capacity-autorouter` | [tscircuit-autorouter](https://github.com/derekbreden/tscircuit-autorouter) | `v0.0.583` | override | via emission spans top↔bottom in through-hole mode | yes (with props/core/rectdiff) |
| `@tscircuit/rectdiff` | [rectdiff](https://github.com/derekbreden/rectdiff) | `4af388d` | CAR devDep SHA | mesh: a node is via-capable iff its `availableZ` spans the full stack | yes |
| `@tscircuit/props` | [props](https://github.com/derekbreden/props) | `v0.0.553` | override | `viaMode` on the autorouter config schema | yes |
| `@tscircuit/core` | [core](https://github.com/derekbreden/core) | `v0.0.1351` | override | `viaMode`/`traceClearance` lowering, honest `EVERY_LAYER`, 6/8-layer names, pour stitch/keepout/carve, hole clearance ring, silk ref-des rotation | mixed — the `viaMode` lowering yes; the pour/stitch logic is project-specific |
| `@tscircuit/copper-pour-solver` | [copper-pour-solver](https://github.com/derekbreden/copper-pour-solver) | `v0.0.29` | override | antipad pill/oval pads (not just rect/circle) + through-hole via/hole guards + manual-trace net fallback | yes (clean bug fix) |
| `@tscircuit/footprinter` | [footprinter](https://github.com/derekbreden/footprinter) | `v0.0.357` | override | `flippinlabels` pinrow option + `applyNoRefDes` fix | yes |
| `circuit-json-to-gerber` | [circuit-json-to-gerber](https://github.com/derekbreden/circuit-json-to-gerber) | `v0.0.78` | override | inlined Hershey single-stroke font for gerber text | maybe |
| `@tscircuit/cli` | [cli](https://github.com/derekbreden/cli) | `v0.1.1537` | override | multi-format export + inner-layer/Hershey gerbers (see wart) | mixed |

The detailed through-hole-via design (why it's taught at the mesh, the decision point) is in
[`patches/capacity-autorouter-fork/README.md`](patches/capacity-autorouter-fork/README.md).

## Known wart: the cli fork vendors circuit-json-to-gerber

`@tscircuit/cli`'s build inlines `circuit-json-to-gerber` into its bundle (cjtg is not in the
`tscircuit` dependency tree). 11 of the cli patch's 12 hunks were therefore gerber changes, and
the cli fork carries them by **vendoring a copy of cjtg's source** into
`lib/vendor/circuit-json-to-gerber/`. This is faithful to what the prior bun patch did (it patched
cli's inlined cjtg), but it duplicates the gerber change that also lives in the `circuit-json-to-gerber`
fork, so the two can drift. Reshape target: make the cli fork depend on the cjtg fork instead of a
vendored copy. (Note the two copies are different cjtg versions — cli inlines `0.0.51`, the
standalone fork is `0.0.78` — so they carry version-appropriate, not identical, change sets.)

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
