# assembly — enclosure_assembly

Module file: tools/hsm/machine-data/src/typed/enclosure_assembly.rs
Workspace: $R/ws/assembly (scratch/gen.rs = rustfmt'd copy of compiled/enclosure_assembly.rs,
scratch/genc.rs = compacted (view with scratch/c3.sh FROM TO), scratch/aq.rs = _assembly_questions).
Python source: scratchpad/py/enclosure_assembly.py (session scratchpad).
Parts: ws/assembly/parts/p2..p6.rs, inserted with `python3 parts/add.py pN.rs install_N`
(adds the part before `pub fn install` and chains install_N).

## Findings
- Generated initialize does NOT bind `annotations` (stub's _rust_exports lists it); follow generated.
- `if __name__ == '__main__'` skipped at top level; entrypoint = call `main` (imports
  `_machine_layout` locally, calls its `main()`), SystemExit(0) is a no-op.
- The Python stub runs its own Python `main()` for the enclosure-assembly genrule, so main_block
  is only reached through Module.main() (nobody calls it).
- Callers of this module (generated): _lines (cap_conduit), _tube_export (TUBE_ANCHOR_SITES, _cci,
  cap_anchor, cap_side_anchor, unsupported_spans), _scorecard (MADE_BY_MATE, MADE_BY_TUBE,
  REFRIGERANT_IDS, TUBE_ANCHOR_CLOSURES, TUBE_ANCHOR_SITES, TUBE_ANCHOR_SPAN, _cci, _on_leg,
  reservoir_a_anchor_sites, unsupported_spans, _with_manifold_rows). Python: above_core_routes
  (cap_conduit), _wiring_data (TUBE_ANCHOR_SITES).
- No caller assigns into the namespace (only a reproduce.py text patch of FOAM_STEP, unused here).
- Python bridge: provider getattr/call/getitem return dict/list/set as live $ref; tuples by value.
- collections.namedtuple/defaultdict are Python objects (Ref) via the native collections shim.
- raise X(msg) -> bail!("X: msg").
- math.radians in the runtime is x*PI/180 (num::radians matches it); math.dist folds hypot.
- Coverage (28 of 42 genrules swept at 19:25): no cover log shows an `enclosure_assembly|`
  function, and no EXT line imports it; enclosure-assembly's log only runs `_assembly_questions`.

- No genrule initializes the module: the importers (_scorecard, _tube_export, _lines) import it inside
  functions no swept genrule runs; constants read without a function call leave no cover line, but
  their importers' function lines would show and don't.
- Differential probe: ws/assembly/probe/ea_probe.py (namespace dump + ~300 synthetic calls), run by
  `python3 tools/run.py -- zsh probe/run_probe.sh <label> <binary>` -> probe/out-<label>.jsonl;
  `_boxes.boxed` is patched to identity and FakeBox objects stand in for solids. Providers are
  Rust-backed shims (no OCP loaded; the probe records sys.modules cadquery/OCP at the end).

## Status (final, wind-down 2026-11-04 21:45)
COMPLETE: all of Python 1-2458 converted, `pub const TYPED: bool = true;`, build clean (last build 20:32,
with every sin/cos through num::sin/num::cos as the coordinator required).

What verified it (no genrule runs it, so probes stand in for comparisons):
- Coverage sweep, all 42 genrules: `who.sh enclosure_assembly` prints nothing, no REQ line names it, and
  the functions that import it (_scorecard, _tube_export, _lines._ea_cap) never run. The
  enclosure-assembly genrule's stub runs Python `main()` -> `_machine_layout.main()`; the module is
  never initialized there.
- Probe 1 (namespace names and values before and after the calls, all 109 namespace functions, 961
  entries incl. 156 error paths) against bin/machine-data (generated): identical except 3 entries whose
  text comes from shared py::bind (see below). Last run on the 20:01 build; the only later source change
  is sin/cos -> num::sin/num::cos (the same libm call at opt 0). A rerun on the final binary queued
  behind the engine and was stopped at the wind-down.
- Probe 2 (synthetic cold-core cradle/anchor tables and foam readers installed before initialization;
  cradle_rows, cradles_land, cap_tube_anchors, lid_cap_stations, anchor_rows, STANDALONE caps; 58
  entries) on the final binary: identical.
- Not run: the enclosure-assembly base0-vs-typed comparison (queued 35 min on the engine, stopped at
  the wind-down; the coordinator's release-build check covers it). `main` was not probed (it is the
  whole `_machine_layout.main()`).

Shared-file notes for the report:
- typed/py.rs `bind`: says `unexpected keyword arguments ["x"]` where the generated bind says
  `unexpected keyword arguments`, and reports unexpected kwargs before a missing required argument
  (generated: `missing argument t` first).
- $R/instrument.py marks only function entries, so a genrule that only reads a module's constants
  never shows in who.sh.

Probe scripts (ea_probe.py, ea_probe2.py, run_probe.sh, both*.sh, diff.py) are kept in the session
scratchpad: /private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/d7001403-7740-4475-8098-abce61ab6b5f/scratchpad/ea-probe
(ws/assembly deleted at the wind-down).
