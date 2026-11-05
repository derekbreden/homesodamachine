# typed cold-core-data: progress (coordinator notes)

- Task: replace src/compiled (generated Val modules) with typed modules in src/typed, verify
  byte-identical outputs on the 33 steps, measure, record, commit; then the same for guides.
- Typed by coordinator: _cold_core_interface, _above_core_mounts, _reservoir_b_fill,
  _core_points, _show_skin, _water_inlet_jet (+ helpers above_core.rs, cad.rs, py.rs, mod.rs).
- 2026-11-04 ~18:35: four subagents porting groups a/b/c/d (see agents/<g>/group.json),
  each in agents/<g>/tree with its own target dir; CONVENTIONS.md is their brief.
- mod.rs entrypoint now dispatches every module with a __main__ block (23).
- Probes: results/names-before.json (generated, 50 modules; _reservoir_a_c2 added to
  modules.txt later). probe_names.py takes PROBE_MODULES=a,b,c. compare_names.py compares.
- Baseline step runs: results/before (25 of 33 ok; acceptance-and-burn-in-sync,
  cold-core-interface, enclosure FAILED; 8 steps after internal-plumbing-sync not run).
  Need: rerun failed/missing before, a second before for determinism, then after.
