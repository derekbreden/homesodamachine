# iface: interface/display/bulkhead modules

Modules (in order): _enclosure_interface, _anchor_cap_interface, _display_retention, _swept_top,
_display_wing_interface, _enclosure_structure, bulkhead_ring, display_gasket, display_cover,
_grip_interface, _back_top_meter.

Workspace: $R/aws/iface (my module files linked live). Scratch: scratchpad fmt/<module>.rs
(rustfmt of generated), fmt/<module>.pp (pp.py output), tools/pp.py.

## Status
- All 11 written (TYPED = true) and built clean (20:01).
- names.py (with `$ref` renumbering): all 11 match in order and value, exit 0.
- Builds take other agents' finished modules as ws.sh copies them; a broken copy (pump_case,
  _enclosure_datums at 19:5x) stops the build: re-run ws.sh for their latest.

## Findings
- `_read(...)` answered in process with rt.enclosure_data; serde_json sorts object keys, so
  `globals().update(reading)` orders names alphabetically.
- Replaced names: front-top `_leaves` patches `_display_wing_interface` box/rounded_prism/
  support_exits; back-top patches `_swept_top.rounded_prism` (no own function reads it).
- `_swept_top._parameters` reads `globals()[name]` for each key of `_values` at call time.
- Steps: _display_retention, _grip_interface, _back_top_meter run in no step.
- reference.py (soda-studies) sets `_swept_top.FLAT` around `profile` calls: `_parameters` reads
  the six constants through the namespace for that.

## Comparisons
- Quick batch (26 rules, no `--direct`): running; weld-rotation-rig-sync, foam-shell ok, 0 differ.
- Heavy rules: per the coordinator, a difference confined to enclosure-box `tmp/machine-layout/`
  machine-equipment/machine-routes, enclosure `enclosure.step.npz` / `.build-time.samples.json`, or
  enclosure-assembly's assembly/wiring meshes and facts is unresolved harness noise, not ours.
  Kept clones are deleted once read (disk is short).
- `x ** y`, `math.sin`, `math.cos` are `num::pow`/`num::sin`/`num::cos` (GUIDE rule): changed in
  `_anchor_cap_interface` (`_cavity`, `cap`, `wing_strain`) and `_back_top_meter`
  (`meter_tie_routes`'s `point`). No step runs those functions; rebuilt, then names.py for both
  and fluid-topology-sync (the one step that installs `_anchor_cap_interface`) re-checked.
