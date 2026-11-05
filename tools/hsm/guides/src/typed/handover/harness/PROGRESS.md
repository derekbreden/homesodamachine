# typed guides: progress (coordinator notes)

- Typed runtime: tools/hsm/guides/src/typed/{mod.rs, py.rs (copied from cold-core-data typed +
  `with`), table.rs (from compiled/modules.rs)}; placeholders for 22 modules. Private tree
  RUN/tree (workspace with guides only; deps by absolute path), target RUN/target (warm).
- Baseline: results/before (5 steps, all ok, every Python pinned via pinhook/sitecustomize.py).
  install-guide-build 123 s CPU / 412 s wall; kit-art 13.6 s; opening-scene 8.3 s;
  render-modern-tee 3.0 s; plumbing-scenes 1.5 s.
- Names: results/names-before.json (22 modules, 973 names; six manual-tool modules probed
  from the checkout root: common, faucet_book, preflight, hold_scene, fill_scene, ice_scene).
- Modules no build step reaches: scenes, startup, cylinder_actions, hold_scene,
  insertion_actions, fill_scene, ice_scene, faucet_book, common, preflight.
- 2026-11-04 ~20:00: four agents porting groups a/b/c/d (agents/<g>/group.json), each with
  its own tree, target clone and pins (agents/<g>/pins.json → agents/<g>/guides-typed).
