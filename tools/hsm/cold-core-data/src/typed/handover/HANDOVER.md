# Typed Rust for cold-core-data and guides: handover (2026-11-04, stopped unfinished)

Session "Typed Rust for cold-core-data and guides" (local_4eb08324), started by
local_133364ed. It was wound down at the parent's request before anything was verified.
Nothing is committed. Both run directories under `.cache/runs/` are removed. This folder
holds everything worth keeping.

## Where the work is

- `cold-core-data/typed/` and `guides/typed/`: copies of the untracked
  `tools/hsm/<crate>/src/typed/` dirs in the main checkout. Those dirs are still in the
  checkout. No `lib.rs` refers to them, so nothing compiles them.
- `*/in-progress/<group>/`: drafts that were in sub-agent build trees when the agents were
  stopped. They have not been type-checked. The same drafts are also untracked in the
  checkout, under `tools/hsm/<crate>/src/typed/drafts/<group>/`.
- `.cache/runs/typed-rust-results-202611042201/` (RESULTS.md, baseline-summary.json): the
  concise results. The six-hour cleanup removes it after three days without a write.
- `*/harness/`: run.py, compare.py, measure.py, wrap.c, pinhook/, probe_names.py,
  compare_names.py, stage.py, inner.py, CONVENTIONS.md (the porting rules the agents
  followed), PROGRESS.md, the group splits (agents/*.json), and for cold-core
  graph_swap.py.
- `*/names-before.json`: every public name and value of the generated modules, probed at
  289db81b8. cold-core-data has 51 modules and 2207 names. guides has 22 modules and 973 names.

## cold-core-data state

- Typed and installed in the checkout's `typed/`: 49 modules, plus the helpers mod.rs (the
  runtime), py.rs, table.rs, cad.rs and above_core.rs.
- Still placeholders: `cold_core_assembly.rs` and `core_numbers.rs`. Drafts are in
  `in-progress/d/`: cold_core_assembly.rs (45 KB) looked complete, and core_numbers.rs
  (28 KB) was being written when the agent stopped.
- 103 calls between modules still go through the dynamic namespace (`// via namespace:`).
  They are in 14 installed files. `in-progress/ns/` has a partial conversion of those files
  (and a reservoir.rs that makes `float_guide_diameter` pub). It is unchecked.
- Never done: a whole typed binary build, a typed names probe against names-before.json,
  the 33-step after-run and identity comparison, measurements, or integration.
- Integration plan: move typed/ to src/recipes/ and delete src/compiled/ and compiled.rs.
  In lib.rs: `pub mod recipes;`, with `compiled::` → `recipes::` for request, invoke and
  register_io. The wire op names "compiled" and "compiled-invoke" stay. Then
  `graph_swap.py tools/hsm/cold-core-data tools/hsm/target/release/cold-core-data.d` and
  re-render BUILD.bazel with `tools/bazel/gen_build.py`. graph_swap reproduced today's
  graph.json byte for byte as a no-op for both crates. 35 graph entries read cold-core-data
  (60 crate files each) and 5 read guides.

## guides state

- Typed runtime (mod.rs, py.rs, table.rs) plus 3 installed modules: cad_art, cad_art_mesh
  and install_art_mesh. The other 19 are placeholders in the checkout. Unchecked drafts of
  16 are in `in-progress/{a,b,c,d}/`. Some are near-empty stubs: preflight, hold_scene and
  fill_scene.

## Baselines at 289db81b8 (generated modules; every Python pinned to the same binaries)

The pinned cold-core-data and enclosure-data workers are opt-level 0 builds. They predate
d5d725357, which restored the release optimization, so restage the baselines with release
builds. At opt-level 1 and up, LLVM merges a sin and a cos of one angle into
`__sincos_stret`, which can differ from separate calls in the last bit. Generated code goes
through the Val runtime and never merges them. Typed code with hand-written pairs needs
non-inlined sin and cos wrappers, as the machine-data session uses, to match it on release
builds.

Pinned "before" workers, sha256:
- cold-core-data `46906ce57b4e260716dd8b2cc238d71c6f0c99e5e8cebf0276744ea5bd986b29`
- guides `ed60f8a3310fa4ea657b706734bcdb2460164b119840dd32639e940fbb3fc688`

These are one-run step CPU seconds (client + workers) and output file counts, not medians.

- cold-core-data steps: bom-masses 4.28 s (831 files), foam-cap 3.28 (386),
  cold-core-assembly 0.50 (405), reed-bridge 0.46 (374), cold-core-sync 0.24 (331),
  enclosure-box 27.8 (664), enclosure-assembly 52.1 (939). The other 25 steps are at or
  under 1.2 s.
- guides steps: install-guide-build 57.1 s (411 files, 1.23 GB peak RSS),
  kit-art 5.67 (356), opening-scene 4.05 (361), render-modern-tee 1.47 (258),
  plumbing-scenes 0.69 (251).

Determinism of the baselines:
- guides: two runs, 0 of 1637 files differ.
- cold-core-data: two runs over 13 steps, 3 of 6258 files differ, all in
  enclosure-assembly: enclosure-assembly.facts.json, enclosure-assembly.scene.npz and
  machine-export-scene.numbers.json. These differ between identical runs, so they need
  excluding from the identity comparison.

## Found along the way (not fixed: outside the task)

- The `enclosure` step (hardware/printed-parts/enclosure/enclosure/enclosure.py) exited 1
  at 289db81b8. `enclosure_back_top.rs` emits a `nameplate-stock` op that
  `enclosure_checks.rs` does not handle.
- Manual-tool modules that no build step runs. They can only be checked by the names probe
  or by a sandbox run:
  - cold-core-data: carbonator_vessel_drawing, evaporator_coil_drawing,
    float_rod_drawing, reservoir_float_rod_drawing.
  - guides: scenes, startup, cylinder_actions, hold_scene, insertion_actions, fill_scene,
    ice_scene, faucet_book, common, preflight.

## Resuming

1. Restage the baselines at the new HEAD. The generated files may have changed. Check
   `git log a78cf15ba.. -- tools/hsm/<crate>/src/compiled` and carry any edits into the
   typed modules.
2. Copy the in-progress drafts over the placeholders, then type-check:
   `cargo check --release -j2 -p hsm-cold-core-data --features typed` in a private tree
   whose lib.rs swaps `compiled` for `#[path = "typed/mod.rs"] pub mod recipes`, as in
   harness/CONVENTIONS.md.
3. Then: the names probe, the after-run and comparison against the baseline, measurement
   (median of 3 warm runs), integration, a record in tools/hsm/conversion-results/, the
   conversion.md text, and a path-scoped commit.
