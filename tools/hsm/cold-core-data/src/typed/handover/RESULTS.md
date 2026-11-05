# Typed cold-core-data and guides: concise results (stopped unverified, 2026-11-04)

Nothing was committed, and no typed module was switched over or checked for byte identity.

- Baselines: genrule work dirs staged at 289db81b835866a28efd83e58e1b2cd97c1afb3b, running the
  generated modules, with every Python's `_rust_part.program` pinned to the same binaries.
  `baseline-summary.json` holds each step's file count, CPU, wall and peak RSS from one run,
  and the sha256 of every pinned worker.
- The pinned cold-core-data (46906ce57b4e…) and enclosure-data (80998abfee60…) workers are
  opt-level 0 builds. They predate d5d725357, which restored the release optimization. The
  guides worker (ed60f8a3310f…) is a release build.
- Determinism, two runs per step:
  - guides: 5 steps, 0 of 1637 files differ.
  - cold-core-data: 13 steps, 3 of 6258 files differ, all from enclosure-assembly:
    enclosure-assembly.facts.json, enclosure-assembly.scene.npz and
    machine-export-scene.numbers.json.
- `enclosure` (hardware/printed-parts/enclosure/enclosure/enclosure.py) exited 1 at
  289db81b8. `enclosure_back_top.rs` emits a `nameplate-stock` op that `enclosure_checks.rs`
  does not handle.
- A later identity check has to compare release builds with release builds. At opt-level 1
  and up, LLVM merges a sin and a cos of one angle into `__sincos_stret`, which can differ
  from separate calls in the last bit. Generated code never merges them. Typed code with
  hand-written pairs needs non-inlined sin and cos wrappers, as machine-data uses.
- The unverified sources are untracked in the checkout:
  - `tools/hsm/{cold-core-data,guides}/src/typed/`: the modules that type-checked.
  - `typed/drafts/<group>/` inside each: the agents' unchecked drafts.
  - The handover, including the harness scripts and names probes, is in the side-session
    notes folder `local_133364ed-…/typed-rust-handover/`.
