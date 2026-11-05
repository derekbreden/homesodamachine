# manifold — manifold_layout typed conversion notes

Module: `tools/hsm/machine-data/src/typed/manifold_layout.rs`, **TYPED = false**. Wound down
2026-11-04 21:50 before any typed run: the file is complete but unverified.

## Status
- [x] written in full (about 2770 lines): every line of the Python (`git show a78cf15ba^:hardware/manifold-layout/manifold_layout.py`,
      1314 lines): constants and install in the generated namespace order, the geometry functions,
      plumbing/ports, numbers, report, readme, main_block.
- [x] last compile clean: 20:15, opt 0 in ws/manifold, with TYPED = false.
- [ ] **edits after 20:15 have not been compiled.** Each one type-checks by inspection:
  - `.sin()`/`.cos()` → `num::sin(..)`/`num::cos(..)` at 10 sites. Every receiver is an `f64`,
    and `N` has no float methods or `Deref`.
  - `fpow` (`x.powf(black_box(y))`) is used in `pow` and in `two_arc_floor`, in place of `.powf`.
  - `report` reads `py::at(&r, "inside")` before `"outside"`, as the Python does.
  - removed the dead `fn unused(_: &Path)` and the `Path` import (no other `Path` use).
  The first release build compiles them.
- [ ] build with TYPED = true (`$R/build.sh manifold`). It was queued 20:20–21:45 behind the
      compiler lock and cancelled at wind-down, never compiled.
- [ ] probes, base vs typed: namespace dump (207 names) and function dump (310 calls).
  - The opt-3 base (`bin/`) and opt-0 base (`bin-base0/`) give identical probe output: 0 names differ,
    0 calls differ, and the stdout matches. Any probe diff therefore comes from the typed code.
- [ ] genrules, with base0 in the same call (`BINDIR=$R/bin-all compare.py steps <g> base0-manifold=$R/bin-base0/machine-data manifold=<bin>`):
  - quick: manifold-layout, fluid-topology-sync, internal-plumbing-sync, firmware-and-commissioning-sync,
    bom-masses, acceptance-and-burn-in-sync.
  - slow: enclosure-box, then enclosure-assembly. Use base0 for enclosure-assembly: the opt-3 base differs
    from any opt-0 build by 1 ulp in arc samples.
- Functions no genrule exercised:
  - hairpin_flat, fixed_tee_centers, elbow_pose, factory_tail_runs, factory_tail_length and skew_deg.
  - The Extents properties: the coverage log doesn't list them.
  - The function probe calls all of them.

## Probe tools
Copies are in the session scratchpad,
`/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/d7001403-7740-4475-8098-abce61ab6b5f/scratchpad/manifold/probe/`:
- `ns_dump.py`, `fn_dump.py`.
- `run_probes.sh <binary> <tag>`, which diffs against `*_base2.*`.
- `quick_compares.sh`.

To run them:
- Make a work dir with `cp -cR $R/steps/manifold-layout <probe>/work-base` and fix `P=` in run_probes.sh.
- Run with `PYTHONHASHSEED=0`: frozenset repr order follows the hash seed.
- Use the `$R/bin-all` workers.

The scratchpad is cleared on reboot. To rebuild the base outputs, run `run_probes.sh $R/bin-base0/machine-data base2`.

## Design
- `N(Num)` is int-or-float with the runtime's combine rule:
  - `div` checks for zero and returns a float.
  - `pow` goes through `fpow`.
  - `nmax`/`nmin`: the first wins a tie.
  - `sqrt`/`acos` check their domains.
  - `V3 = [N; 3]`.
- Python-facing wrappers:
  - They keep raw the components a function doesn't touch: fold_pt p0, bend_pt p0, fold_dir d0, bend_dir d0/d1, and the `*_axis` z/y.
  - They negate through `interop::unary("neg")`, so Bool → Float.
- `State` (`rt.keep` after SHIFT) holds:
  - provider handles, the `K` constants, the bodies (`lay_out`) and SHIFT.
  - Caches for: fore_deck (fore_valve_axis_y), tee_axis_y, TUBE_ID, the numbers kit, tee_ports per junction, s_bend per pair of enclosure endpoints, runs, fore stubs, FORE_STUB_EXPOSED and mouths.
  - The plumbing cache, keyed on the identity of ns `_plumbing_cache`.
  - Every cached provider is a pure fixed_returns function or constant.
- The `_tee_ports` wrapper calls the provider fresh. The `pump_plumbing` wrapper returns ns `_plumbing_cache`.
- Stated bound `source-step-room` goes through `_stated_bounds::state_bound`, after SBENDS.
- Opt-level safety: sin/cos only through `num::sin`/`num::cos`, and every `**` through `fpow`. The `** 0.5` in dist/skew_deg goes through `pow(.., 0.5)`, not sqrt. `math.sqrt` is `f64::sqrt`.

## Findings
- All vlv/tee/kp provider constants are floats. They are still held as Num where they flow out.
- `elbow_pose` reads `ELBOW_BEND`, which the module never defines. Calling it fails with
  "manifold_layout: unknown name ELBOW_BEND". JOINS is empty, so nothing calls it.
- Comprehension loop variables do not leak into the generated namespace. The module-level for-loop variables
  `_p`, `_name`, `_dx`, `_dy` and `_dz` do.
- Entry point: `_rust_part` is imported into the module namespace, then `start()`, the argv check and `sys.exit(main())`.
- README.md has no `[value](NAME)` placeholders. The variables don't change its bytes, but they must not raise an error.
