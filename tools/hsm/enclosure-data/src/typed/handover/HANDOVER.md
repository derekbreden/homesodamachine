# Typed enclosure-data: hand-over at the 2026-11-04 wind-down

Nothing landed on main. The typed sources are untracked in `tools/hsm/enclosure-data/src/typed/`
(52 `.rs` files). `typed/hybrid.patch` holds the hybrid build's changes to three tracked files:
`main.rs` routes requests to `typed::rt`, `compiled.rs` gains the hooks that let typed and generated
modules import each other, and `Cargo.toml` gains a `hybrid` feature. Once `git apply`'d, the crate
builds every `TYPED = true` module typed and the rest generated.

Every check below ran on unoptimized (opt-level 0) harness builds, against an opt-0 build of the
generated crate at 21d4adf8c. None ran on release builds, which main uses again (d5d725357), so
nothing below counts as verified.

## Modules

| module(s) | state | names.py | rules compared (files, differing) |
|---|---|---|---|
| `_enclosure_datums` | compiled | 44 match | enclosure-dimensions, cold-core-sync, asse-drain-sync, handwork-sync, fluid-topology-sync, acceptance-and-burn-in-sync, firmware-and-commissioning-sync, faucet-and-umbilical-sync, internal-plumbing-sync, enclosure-mechanical-sync: all 0 |
| `_above_core_shell` | written, never compiled typed | — | — |
| `_enclosure_interface`, `_anchor_cap_interface`, `_display_retention`, `_swept_top`, `_display_wing_interface`, `_enclosure_structure`, `bulkhead_ring`, `display_gasket`, `display_cover`, `_grip_interface`, `_back_top_meter` | compiled (20:01) | all match | weld-rotation-rig-sync (311, 0), foam-shell (333, 0) |
| `_nameplate_interface`, `_nameplate_wing_interface`, `_data_wing_interface`, `_nameplate_dimensions`, `_y_wall_dimensions` | compiled | identical | a call probe against the baseline: same |
| `nameplate`, `data_ring`, `rear_identification` | written, never compiled | — | — |
| `pump_case`, `pump_tray` | compiled | 118, 73 match | pump-case (156, 0), pump-tray (248, 0) |
| `fixed_returns`, `dock_structure`, `valve_tray`, `rear_equipment_caps` | compiled | 34, 44, 40, 15 match | fixed_returns: manifold-layout, fluid-topology-sync, internal-plumbing-sync, firmware-and-commissioning-sync, acceptance-and-burn-in-sync, bom-masses all 0; enclosure-assembly 16 differ, all in the harness-suspect set below |
| `_rust_enclosure_presentation`, `_enclosure_presentation`, `_disposal_artwork`, `_enclosure_skin`, `_tube_snap_sites`, `_route_snaps`, `_enclosure_dimensions`, `_fixed_pump_mount` | compiled (20:06) | 7 match; `_enclosure_dimensions` can't load in the enclosure stage (`No module named '_facts'`) for either binary | enclosure-assembly 16 differ, all in the harness-suspect set |
| `_enclosure_panel`, `_rust_enclosure_checks`, `_enclosure_pump_retainer` | written in full, never compiled | — | — |
| `_enclosure_rust_driver`, `_enclosure_back_top`, `_enclosure_front_top`, `_enclosure_front_bottom` | placeholders | — | — |
| `enclosure` root (`enclosure.rs`) | `TYPED = true`: it adopts the generated namespace and reads every constant into `State` | 592 match | enclosure-dimensions (665, 0); record structs added since, uncompiled; `State::compute` and the final install not written |
| `enclosure/p1.rs` | 52 typed signatures, bodies call the generated function; uncompiled | | |
| `enclosure/p2.rs` | 36 of 63 functions typed, compiled; 27 not in the file | | |
| `enclosure/p3.rs`, `p4.rs` | placeholders | | |
| `enclosure/p5.rs` | 25 of 43 typed, 18 call the generated function; uncompiled | | |

The `num::pow`/`num::sin`/`num::cos` edits in `_anchor_cap_interface`, `_back_top_meter`,
`_enclosure_datums`, `_enclosure_panel`, the dock four and `pump_tray` came after their last builds.

## What the next comparison needs

1. The "before" is a release build of HEAD's generated crate (opt-level 3, `debug = 1`), and the
   "after" the typed crate at the same profile. `core_profiles.rs` and `pump_case.rs` take the sin
   and cos of one angle, which the optimizer merges into one `__sincos_stret` call. The pinned
   cold-core-data worker is also an opt-0 build.
2. Typed code computes `**`, `math.sin` and `math.cos` through `num::pow`, `num::sin` and `num::cos`
   (`#[inline(never)]`, `black_box`), so its bytes don't depend on the opt level.
3. Masks beyond the work path and this crate's source sites (`harness/batch.py`,
   `tree(work, extended=True)`, not yet exercised on a run):
   - `hardware/ledger/.build-time.samples.json` is wall time;
   - `machine-equipment.json` / `machine-routes.json` hold `~/Library/Caches/hsm/parts/tmp/<pid>-<n>`
     paths;
   - `enclosure.step.npz` (`document.npy`) and the assembly and wiring JSON (`drain-clearance-check`,
     `integration-review`, `machine-export-scene.numbers`, facts) embed raw sha256s of meshes whose
     bytes hold the work path and source sites.
   The npz members other than `document.npy` were not yet accounted for: the substitution test on
   `enclosure.step.npz` did not reproduce the baseline hash.
4. Each staged enclosure-assembly run adds about 1.5 GB to the parts store.

## Findings for the next converter

- `py::snapshot` keeps provider objects as `$ref` handles that are never freed, so a handle works
  as an identity key; names.py renumbers `$ref` ids before comparing.
- interop's `is` is false for two functions, so `cutter is shell._port_cuts` (the panel's and
  back-top's `numbers`) never holds; the west-port branch runs for both pairs.
- `Pack` has 30 fields, with 29 defaults set on `__new__.__defaults__`; the record classes are made
  with `module="enclosure"`.
- The generated top level takes the core constants from one `_core_namespace(...)` update (keys
  sorted, lists as tuples). serde_json keeps no insertion order, so every in-process `_read` reply
  arrives with sorted keys.
- Read through the namespace at every use: the 29 slots, `_teardrop_y`, `record_bound`, `cq`,
  `_flank_vents` (front-bottom replaces it), `_valve_tray.build_body_clearance`/`build_port_channel`,
  `_dock.box`/`ycyl`/`teardrop_y`/`return_clearances`, `_fixed_pump_mount.inverse_cuts`/`wire_cuts`/
  `upper_wire_room`/`display_cleanouts`/`_wing`, `_display_wing_interface.box`/`rounded_prism`/
  `support_exits`, `_swept_top`'s six profile constants and `rounded_prism`, `_route_snaps.apply`,
  `rear_identification.apply`/`receiver_field`, `pump_tray.boss_room`.
- Back-top `_replace` reads every original in dict order, sets them in order, restores in the
  originals' order, and always runs its exit. `_rust_enclosure_checks` enters back-top `_leaves`
  through the namespace with a questions graph, so `_leaves` stays a Python-callable context manager.
- `nameplate_snap::numbers` takes a `compiled::Env` only to read `wing`: the swap gives it the wing
  value.
- The p1–p5 signature conventions settled late: `inner`/`outer` are `[f64; 6]` by value and number
  pairs are `[f64; 2]` (p2 still uses `&[f64; 6]` and `(f64, f64)`); `box` is `box_`.
- The traced steps never reach the east-boss, tube-anchor, keystone-receptacle, C14-tunnel or
  side-well bodies (their stations are empty) and never call `can_cut` or `_wing_receiver`; no
  comparison can check those.
- `plan_at` runs once per rail sample through `flute_skin.Rail` lambdas and sends nine segments to
  `reeding.walk` each time: the largest saving in the module once typed.

## Harness

`typed-enclosure-data-harness.tar.gz` beside this note holds the scripts and the analysis:
`ws.sh`, `build.sh`, `compare.py`, `names.py`, `who.py`, `harness/` (batch, run_step, probe_names,
treecmp, fnmeta, sig_drafts, gen_enclosure_root, analyze_types), `GUIDE.md`, `CONVENTIONS.md`,
`briefs/`, `swap.md`, the agents' `notes/`, `placeholders/`, `sigs/`, `enclosure-functions.json`,
`enclosure-sigs-draft.md` and `trace-summary.json`. `drafts/` holds earlier drafts of the runtime
files (`graph.rs`, `datums.rs`, `py.rs`, `python.rs`, `py_trait.rs`); `src/typed/` holds the current
ones. Paths inside assume `R=.cache/runs/typed-enclosure-202611041700`: extract the tarball there
to rerun them. `fnmeta`, `sig_drafts` and `analyze_types` also read `$R/py/<module>.py`, the Python
recipes before they became shims: `git show 392a60abc:<path>` of each path in `modules.txt`. None
of it is in the repo; whether any joins it is Derek's call.

Baseline CPU, opt-0 generated crate at 21d4adf8c (one run each, loaded machine): enclosure-assembly
154.8 s, install-guide-build 114.4 s, enclosure 101.5 s, enclosure-box 74.0 s,
enclosure-dimensions 3.2 s.
