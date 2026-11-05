# machine-data typed modules: hand-over (2026-11-04)

Nothing is committed. `tools/hsm/machine-data` still runs its generated `Val` modules. The typed
sources sit untracked in `tools/hsm/machine-data/src/typed/`: 27 files, about 17,900 lines. The
crate's `main.rs` never references them. No tracked file was changed. Nothing ran on a release
build. Every typed check below came from an opt-level 0 build.

## Modules

Complete, `TYPED = true`:

| Module | Lines | Checked by |
| --- | --- | --- |
| `_stated_bounds`, `_gas_chain`, `above_core_bom`, `_machine_routes`, `_machine_export` | 184, 266, 61, 93, 116 | A hybrid build with these five gives 405/0 differing files on cold-core-assembly and 832/0 on bom-masses. fluid-topology-sync gives 678/0 alongside `_lines`. enclosure-assembly shows 23 differing files, all downstream of two 1-ulp arc samples that layout-data computes at opt 0 (pitfall 3). No run against `bin-base0` or a release build yet. |
| `_lines` | 1560 | fluid-topology-sync 678/0, all workers pinned. A probe of every function is identical, except that `_gate_lead` with a string `lead` fails one step earlier, which is outside its domain. |
| `_scorecard` | 4821 | On the 20:12 build: fluid-topology-sync 678/0, internal-plumbing-sync 671/0, enclosure-mechanical-sync 671/0, enclosure-dimensions 665/0. A 110-call probe matched except at `selftest` and `selected_clearance_joints`. The 21:16 build fixes those two and compiles clean, but has never run. |
| `_facts`, `above_core_parts`, `_tube_export` | 874, 435, 206 | Final build: fluid-topology-sync 678/0, enclosure-mechanical-sync 671/0, enclosure-dimensions 665/0. Earlier build: foam-cap 386/0. Probe 139/0. The other 11 genrules that touch them were not run. |
| `enclosure_assembly` | 4215 | No genrule initializes it: `enclosure_assembly.py` runs `_machine_layout.main()`. A probe of all 109 functions gives 961 entries, all matching except 3 error texts that come from `py::bind`. A probe with synthetic cradle and anchor tables gives 58/58. The final `num::sin`/`num::cos` build has not been re-probed. |

Written, `TYPED = false`:

| Module | Lines | State |
| --- | --- | --- |
| `_machine`, `_machine_reporting`, `_machine_checks`, `_machine_equipment`, `_assembly_questions` | 431, 682, 547, 628, 164 | Compiled clean at 19:52; never compared. |
| `_machine_layout` | 1629 | Never compiled. |
| `manifold_layout` | 2778 | Compiled clean at 20:15 with `TYPED = false`. Five later edits are uncompiled: `num::sin`/`num::cos`, an unfoldable `fpow`, the report's `"inside"` key, a dead function removed, and the flag. Never ran typed. `bin-base0` and `bin` give identical probe output (207 names, 310 calls). |
| `check_asse_drain`, `above_core_wiring` | 375, 424 | Complete, but parts were never compared. In `check_asse_drain`: `write`, and `main` past its input checks. In `above_core_wiring`: `_box`, `_union`, `_well`, `_features`, `cap_features`, `shell_features`, `driver_columns`, `components`. |
| `rear_snaps`, `rear_plumbing` | 1749, 369 | On the last compiled binary: rear-equipment-caps 278/0, and an 85-call probe matched. Since then, `rear_plumbing`'s `ValueError: layout-data: ` prefix wrap has been added, uncompiled. Its `continuations` 1-ulp difference comes from opt-0 layout-data. enclosure and foam-cap were not compared. |

Runtime: `rt.rs`, `py.rs`, `num.rs`, `docs.rs`, `mod.rs`. `mod.rs` and `rt.rs` carry the
development fallback to the generated namespace under `cfg(feature = "hybrid")`.

Per-module details are in `notes/`, the agents' own notes. They cover the functions no genrule
runs, the probe methods and exactly what is left.

## Pitfalls that change bytes

1. A worker missing from the pinned directory is rebuilt from the live checkout during the run,
   so sibling sessions' edits leak in. Pin every worker: `cp -c` every executable in
   `tools/hsm/target/release` into one directory. `tools/compare.py` takes it as `BINDIR`;
   `UNPINNED_LOG` lists any worker still taken from the checkout.
2. `tmp/machine-layout/installed/{equipment,routes}/machine-*.json` name the engine's scratch
   directory `Library/Caches/hsm/parts/tmp/<pid>-<n>`, so any two runs differ there.
   `compare.py` writes it as `<ENGINE-TMP>`, and the clone's own path as `<WORK>`.
3. Float results depend on the opt-level.
   - At opt ≥1, LLVM merges a `sin` and a `cos` of one angle in one block into
     `__sincos_stret`, which differs in the last bit for 89,265 of 20,000,000 angles.
     layout-data's arc sampling has such a pair, so any opt-0 build differs from the opt-3
     base at a few route samples on enclosure-assembly.
   - At opt 3, a constant-exponent `powf(2.)` folds to `x * x`, which differs from libm
     `pow` for about 0.13% of values.
   - The interop runtime calls libm `sin`, `cos` and `pow` separately, with runtime
     arguments, and typed code must do the same. `num::sin` and `num::cos` exist
     (`#[inline(never)]`). There is no shared unfoldable `pow` yet: `manifold_layout` has a
     local `fpow`, and `rear_snaps.rs` still calls `powf(2.)`.
   - Compare opt-0 builds against an opt-0 generated build. Verify the final binary at the
     workspace release profile.
4. `tools/instrument.py` logs only function calls, so a genrule that only reads a module's
   constants is missing from `coverage.txt`. The release check has to run all 42 genrules.
5. Error text from shared files:
   - `py::bind` names the unexpected keywords, and reports them before a missing argument. The
     generated bind says `unexpected keyword arguments` and reports the missing argument first.
   - `rt.layout_data` lacks the generated `ValueError: layout-data: ` prefix, so
     `above_core_parts` wraps it locally.
   - `py::dict_of` does not take `dict(pairs)`.

## Left

1. Compile and verify the eleven `TYPED = false` modules: probe them against an opt-0
   generated build, then compare genrules with all workers pinned.
2. Add an unfoldable `num::pow` and send every `**` through it. Match `py::bind`'s error text
   and order to the generated bind.
3. Switch the crate.
   - `main.rs`: `mod compiled;` becomes `mod typed;`, and `compiled::{request, invoke,
     register_io}` become `typed::rt::…`.
   - `native_profiles.rs`: import `typed::rt::{Ns as Env, Rt as Runtime}` and
     `hsm_documents::interop::Val`, and update its doc line.
   - Delete `src/compiled.rs` and `src/compiled/`, the hybrid `cfg` code and the `TYPED`
     constants.
   - Switch the 45 `graph.json` entries and 42 `BUILD.bazel` srcs lists with `tools/switch.py`.
     `write` mode changes the tree; `blobs` mode makes HEAD-plus-own-lines blobs for staging.
     Both files are shared.
4. Release check: build at the workspace profile (release, `debug = 1`), then run all 42 genrules
   against the generated base, with every worker pinned.
5. Measure CPU, the median of three warm runs, before and after, on enclosure-assembly,
   fluid-topology-sync, enclosure-mechanical-sync and enclosure-box. Then measure the
   recompile CPU after a one-line edit in `_scorecard.rs`. For the profile, the opt-level must
   match the base's so the bytes match; `debug` and `incremental` are the free settings.
6. Write a record in `tools/hsm/conversion-results/`, update `conversion.md`, then commit and push.

## Results

- Staged genrule directories came from `78404375d`. The crate is unchanged since `a78cf15ba`.
- `bin/machine-data` `9fe15e7d5d39516ae4abb8b272a40fe3a37608d8fb8ec6fea8f86751c7dbc2a7` is the
  HEAD generated crate at opt 3, `debug = 1`.
- `bin-base0` `d985a9c49622b8dcd5d435fb0b2819f87aab8ef4726f35731ee4557ec13c54e7` is the same
  crate with every crate at opt 0.
- The hybrid with five typed modules, `840d2b052a14e02902d2df79e012dcc626510e64ed1245604e2ddc5b1fb63b23`,
  was built at opt 0.
- The pinned set is 90 workers as of 19:58, list digest
  `7a92dc570d5a51ef2c81f7df9fb542cac5978bfe00c6ef5072bd839cd9f7b1fb`. Its enclosure-data and
  cold-core-data pins are the opt-0 builds from 16:44 and 16:33.
- `base-summary.json` gives each genrule's file count, the CPU and wall of the instrumented
  opt-1 generated run, and its tree digest. The 42 runs total 442.8 CPU s. `enclosure` stops in
  enclosure-checks at `nameplate-stock` (unsupported operation) with the generated build too.
- `coverage.txt` lists which modules each genrule touches.
- No CPU before/after or recompile measurement was taken, and no profile was changed.

`tools/` holds the run's scripts: `stage.py`, `harness.py`, `compare.py`, `sweep.sh`,
`measure.py`, `instrument.py`, `who.sh`, `ws.sh`, `build.sh` and `switch.py`. `GUIDE.md` is the
conversion guide: runtime API, namespace contract and byte semantics. The repo lacks these
tools, and Derek decides which join it. `probes/` holds the agents' probe scripts.
