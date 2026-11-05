# dock: fixed_returns, dock_structure, valve_tray, rear_equipment_caps

Workspace: `$R/aws/dock` (ws.sh dock fixed_returns dock_structure valve_tray rear_equipment_caps).
Scratch copies of the generated code (long lines broken): scratchpad `dock/gen/<module>.b.rs`.
Binaries compared: `$R/aws/dock/bin/enclosure-data.v<N>` (clones of the build, so a rebuild
never moves a running comparison).

## Status
- All four TYPED. v3 names (refs renumbered): fixed_returns 34, dock_structure 44, valve_tray 40,
  rear_equipment_caps 15 names match.
- v4 (building): `num::pow`/`num::sin`/`num::cos` in place of powf/sin/cos (dock_structure 1,
  fixed_returns 3, valve_tray 1, rear_equipment_caps 2). Unoptimized harness builds compute the
  same libm calls either way, so v1-v3 comparisons stand for v4.
- v1 (fixed_returns): manifold-layout, fluid-topology-sync, internal-plumbing-sync,
  firmware-and-commissioning-sync, acceptance-and-burn-in-sync, bom-masses all ok, 0 differ.
- v2 (fixed_returns, dock_structure, valve_tray): enclosure-assembly ok, 16 differ, all in the
  harness-suspect set (assembly/wiring meshes and facts, machine-equipment/machine-routes, and
  drain-clearance-check.json / machine-export-scene.numbers.json / integration-review.json, which
  embed the assembly and wiring mesh hashes and counts): unresolved per coordinator. Clone deleted;
  its hash manifest and the differing JSONs are in `aws/dock/kept/enclosure-assembly.v2/`.
  Running: valve-tray, tee-valve-bow-trial, enclosure-dimensions, enclosure-mechanical-sync,
  internal-plumbing-sync; enclosure-box, enclosure, bom-masses.
- v3 (all four): rear-equipment-caps running.

## Findings
- Replaced names (read through the namespace at every use):
  - dock_structure: `box`, `ycyl` (`_enclosure_rust_driver._dock_recipe`, front-top `_leaves`),
    `teardrop_y`, `return_clearances` (front-top `_leaves`). Internal callers: teardrop_y -> ycyl;
    plate_holes/tee_bores -> teardrop_y; tube_setting_jig -> box, ycyl.
  - valve_tray: `build_body_clearance`, `build_port_channel` (front-top `_leaves`). Internal callers:
    web -> build_port_channel; build_valve_tray -> build_port_channel.
- machine-data reaches fixed_returns (manifold_layout `_returns`: ELBOW_DROP, TIP_FROM_FORE, TUBE_ID,
  fore_valve_axis_y, s_bend, station, tee_axis_y, tee_ports; _machine_layout `plumbing`) and
  dock_structure (_scorecard: elbow_host, stem_overlap, stem_mate_region; enclosure_assembly:
  HOLE_R, plumbing, stations, tee, wall_aft_y) through Python.
- valve_tray `_data` answers in process (`rt.enclosure_data`); generated went Python `_read` ->
  nested worker request. Errors there read `ValueError: enclosure-data: {e:#}` in generated.
  `_source()` (11 provider reads) is read once; nobody rebinds `valve_seat`/`beduan_solenoid`
  constants or valve_tray's stock names, so `stock` sent = the defaults reply.
- Provider refs (`$ref`) are kept forever by `_rust_objects`, so caching provider handles is safe.
- names.py renumbers `$ref` ids by first appearance (coordinator, 2026-11-04): the earlier
  "only `$ref` ids differ" Path names are rechecked with v3.
- `Val::Path` reaches Python as a plain `str` (interop `encode`); `_rust_part.cut` takes
  `Path(part_dir)`, so HERE as `Val::Path` is fine there.
