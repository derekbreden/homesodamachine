# machine agent notes

Modules: _machine, _machine_reporting, _machine_checks, _machine_equipment, _machine_layout, _assembly_questions.

## Status at wind-down (2026-11-04 21:40)

Every module file is written in full and reviewed line by line against the generated code
(scratchpad dec_*.py decompiles and gen/). No comparison or probe ever ran with a typed binary, so each
file has `TYPED = false` and the generated namespace runs. ws/machine is deleted; no steps/ clone was kept.

- _assembly_questions: complete; compiled in its current form (build b3iks0moh, 19:52). Not compared. Runs only in
  enclosure-assembly.
- _machine: complete; compiled in its current form (b3iks0moh). No genrule runs it, so no comparison is possible; needs a
  probe of its namespace functions against the generated build.
- _machine_reporting: complete; compiled in its current form (b3iks0moh). Not compared. Runs only in enclosure-assembly;
  `_bounds`, `_ports`, `_route_rows`, `_run_length`, `_tray_reports` run in no genrule.
- _machine_checks: complete; compiled in its current form (b3iks0moh). Not compared. Runs only in enclosure-assembly;
  `drain` runs in no genrule.
- _machine_equipment: complete; compiled in its current form (b3iks0moh). Not compared. Runs in enclosure-box and
  enclosure-assembly; `frame`, `compose`, `transform`, `_along_y`, `plan`, `_chain_parts`,
  `_chain_inlet`, `local_ports`, `_grid`, `_reducer_insertion`, `route_port_frame`, `_offset`, `_link`,
  `_line`, `_bezier`, `_crowned_beziers`, `_sample_bezier`, `_arc_three`, `_flavor_s_bend`,
  `_flavor_rear`, `local_routes`, `_rear_routes` run in no genrule.
- _machine_layout: complete (written ~20:40, num::cos per the sin/cos rule) but NEVER COMPILED: its
  first build waited in heavy admission 21:00–21:40 and was stopped at wind-down. A build that compiles
  the real typed/ tree (not a ws.sh workspace, which uses the placeholder for a TYPED=false module) may
  stop on it. Runs in enclosure-box (plan stage 'pack') and enclosure-assembly (main); `_point`, `_axis`
  and the namespace `_installed` run in no genrule.

## Left, to resume

1. `$R/ws.sh machine _machine _machine_reporting _machine_checks _machine_equipment _machine_layout _assembly_questions`
   and set `TYPED = true` in the modules under test.
2. `$R/build.sh machine`; fix any compile errors in _machine_layout.rs.
3. enclosure-box (cheaper, first): `cd $R && BINDIR=$R/bin-all $PY compare.py steps enclosure-box
   base0-machine=$R/bin-base0/machine-data machine=$R/ws/machine/target/release/machine-data`
   (the workspace is opt-0, so the base is bin-base0, not bin/; the saved enclosure-box tree predates
   <ENGINE-TMP>).
4. enclosure-assembly once, the same way (about 1.5 GB of hsm parts store per run).
5. A probe for _machine (no genrule).

## Findings
- _assembly_questions: calls _stated_bounds::{state_bound,bound,take} directly (StatedBound.__call__ only forwards to take).
  above_core.specification() read once (generated reads it per fitting; side-effect free); wet_ports snapshot.
- _machine: Machine.measured reads time.strftime, which the native `time` module lacks: errors the same way as generated.
  stamps always read through namespace (native install).
- _machine_reporting: file digests (step blake2b16, artifacts sha256) open the file through Python as generated
  does (open/__enter__/__exit__), but hash the bytes natively (generated streamed 256 KB hex blocks over callbacks:
  ~1.9 GB for enclosure-assembly).
- coverage (cover-logs): enclosure-assembly runs _machine_reporting, _machine_checks, _machine_layout, _machine_equipment,
  _assembly_questions; enclosure-box runs _machine_layout(plan pack) and _machine_equipment. _machine: no genrule.
- _machine_checks: _sha opens via Path.open('rb') (Python) and hashes natively; _plain's unknown-type path errors with
  `_machine_checks: unknown name type` exactly as generated (`type` is no runtime builtin).
- _machine_equipment: generated code drops @cache on _stem/_reducer/_check (reads each call); keep that.
- _machine_layout: arithmetic on provider numbers through Num (same int/float rule as interop::binary);
  the sleeve radius squares go through interop::binary("pow") so they stay the runtime's powf calls;
  cos through num::cos, tan as the runtime's `.tan()`. struct.pack/unpack f32 round trip done as
  `as f32 as f64` (no struct import). run.pts, plumbing.layouts(plate), _reservoir_a_anchors.datums() and
  _joint_numbers are snapshotted once. Path handling mirrors interop's (parent/name/strip_prefix/starts_with).
