# lines — converting `_lines` to typed Rust

Module file: tools/hsm/machine-data/src/typed/_lines.rs (TYPED = true). Workspace: ws/lines.

## Status
- [x] read generated code (all of initialize + 41 functions)
- [x] base probe through the Python surface: ws/lines/probe-base.txt (names, stations, calls),
      probe-base-runs.{txt,stdout} (frames, runs, tubes). Probe: ws/lines/probe.py, run_probe.sh.
- [x] module written; 22 run notes checked against the generated literals
- [x] built (19:52 binary); typed code confirmed live: the one edge call that differs (`_gate_lead` with a
      string `lead`, below) differs in this binary, so it runs the typed module, not the generated one
- [x] probes identical to base: names/stations/calls (354 lines), frames/runs/tubes (38 lines + report stdout),
      edge probe ws/lines/probe-edges.py (76 calls: binding errors, malformed arguments, report formatting)
      identical except one case (below)
- [x] fluid-topology-sync: 678 files, differ 0, three ways: AGAINST base-trees; directly against
      bin/machine-data; and pinned (BINDIR=bin-all, base-lines=bin/machine-data first in the same call),
      with no UNPINNED_LOG lines (20:00)
- [x] coverage sweep done (42 genrules): only fluid-topology-sync runs `_lines` (install, with its 10
      valve_ends evaluations, and VALVES reads). The sweep's enclosure run stopped in enclosure-checks
      ("unsupported enclosure question operation nameplate-stock"); nothing on that genrule's import chain
      (rear_snaps, rear_plumbing, above_core_parts/_wiring/_bom, _machine_layout) imports `_lines`,
      above_core_routes or `_scorecard`. No genrule runs a `_scorecard` function, so its `rt.import("_lines")`
      calls (run_ends, run_world, fine_run_clearance_pairs) never run either.
- Functions no genrule exercises (all checked by the probes against base): the STATIONS lambdas, station,
  frames, _frame, build_runs, build_seated_runs, every run function, gate_cruise, the gate/fill helpers,
  _on_cap, _gate_lead, tubes, report, authored, flavor_outlet, _ea_cap.

## Callers found
- Python: above_core_routes._station reads `_lines.STATIONS[name][port]` and calls `station()` (only for a
  body above_core_parts.port_stations does not know; enclosure-assembly never reaches it).
- Python: hardware/topology/_fluid_topology_sync.py reads `list(_lines.VALVES)` (module import at top).
- generated/typed _scorecard: run_world / _fine_run_clearance_pairs import `_lines` inside the function and read
  `_lines.PORT_ADAPTERS.get(anchor)`; no swept genrule runs them.
- verify scripts (not genrules): verify_pump_routes.py, verify_fluid2_guard_equivalence.py.
- No caller of build_runs / build_seated_runs / frames in tree. Nobody assigns into `_lines`.

## Findings (generated code wins)
- `dict.fromkeys` keeps duplicates (Val::dict doesn't dedupe): frames walks STATIONS keys ++ placed ++ bounds
  with repeats, re-framing a body each time it is listed.
- `{a, b} <= set(F)` in build_runs / build_seated_runs: interop compare("le") on two sets falls to numbers
  and raises "expected number, got {'compressor', 'foam-assembly'}" (resp. {'funnel-drain-union', 'valve-v-b'})
  right after frames(). Typed mirrors this by calling interop::compare on the same sets. A shared-file issue:
  interop has no set inclusion for `<=`, so build_runs can never return a list.
- `_routing._call` resends and refills BLOCKED on every Frame.at/normal/diam, stock_min, bent, length,
  tightest, tube: typed keeps every such call in the generated order (including _fluid_14's repeated
  at("reservoir-a") and its second _fill_a_lane_y).
- generated `bind` differs from py::bind in error text/precedence ("unexpected keyword arguments" with no
  list; missing/multiple checked per parameter before "too many positional"): typed uses a private copy.
- `_on_cap` / `_gate_lead` read their arguments where the source reads them (after the `at()` call), so a
  malformed argument fails at the same step with the same text.
- docs::LINES == generated __doc__ (checked).

## Not matched
- `_gate_lead(gate, toward, lead)` with a sequence `lead` (e.g. 'x'): the generated code multiplies the string
  by the lean's tangent (interop truncates the float count to 0, giving '') and fails one step later with
  "expected number, got ''"; typed fails at once with "expected number, got 'x'". Out of the function's domain.
- Numbers that arrive as provider references (numpy scalars) are converted to float at the boundary; the
  generated code would keep them as references through remote arithmetic. Values are equal.

## Shared files
- None needed for this module. One gap in the shared runtime that the module mirrors: interop compare("le")
  has no set inclusion, so `{a, b} <= set(F)` raises in build_runs / build_seated_runs, in the generated
  and the typed code alike (CPython returns a bool there). Nothing in the tree calls either function; the
  verify scripts that import `_lines` call the run functions and _fill_a_cap_z directly.
