# datums (agent) — `_enclosure_datums`, `_above_core_shell`

Workspace: `$R/aws/datums` (own: `_above_core_shell`, `_enclosure_datums`).

## Status
- `_enclosure_datums`: typed (`TYPED = true`), builds, names match (44). Native `Vector`/`Plane`/
  `Location` + Python-facing `"Class.method"` entries; `py::Py` impls for the three (to_py = `to_val`,
  from_py = `read`, through `rt::current()`; from_py refuses a non-Ref).
  Compared, all ok / differ 0: enclosure-dimensions (665 files), cold-core-sync (331), asse-drain-sync
  (288), handwork-sync (329), fluid-topology-sync (678), acceptance-and-burn-in-sync (333),
  firmware-and-commissioning-sync (332), faucet-and-umbilical-sync (317), internal-plumbing-sync (671),
  enclosure-mechanical-sync (671). Left for it: enclosure, enclosure-box, enclosure-assembly,
  bom-masses (run with `_above_core_shell`).
- `_above_core_shell`: written (typed records `FastenerPlan`, `WallMount`/`WallStation`,
  `FastenerLane`, `C14Fasteners`, `ValveSeatDatum`; pub fns per Python function). Compiled with
  `TYPED = false`; set `TYPED = true`, then wound down before that build ran: not compiled typed,
  no names/calls/compare. Two later edits uncompiled (lane check keeps Bools and short-circuits;
  seat stock refuses a NaN side). Workspace and probe scripts deleted.
- `rotation()` in `_enclosure_datums` takes `num::cos`/`num::sin` (the opt-level 3 sincos merge).
- Direct-call probe (functions no rule runs): `$R/aws/datums/calls.py <binary>` runs
  `probe_calls.py` (stand-in methods, every `_above_core_shell` datum function, lane checks) with the
  candidate and the baseline binary, floats as hex, and prints the calls whose results differ.

## Findings
- Every stub method arrives with `self` as a `Val::Ref`; Python sends int/float subclasses by value,
  so `isinstance(<Ref>, (int, float))` is always False and `isinstance(<non-Ref>, <Python class>)`
  is always False: both callbacks are skipped.
- `float(v)` in the runtime: text parses, anything else is `v.num().unwrap_or(0.)` (None reads 0.0).
- Reading an instance's fields: one callback through a cached `operator.attrgetter`.
- `Plane` to Python: `object.__new__(Plane)` + setattr origin, zDir, xDir, yDir (re-running
  `__init__` on normalized axes is not bitwise idempotent).
- `Location` to Python: `Location()` then `_Matrix(rows)`, setattr rows, setattr wrapped, as
  `__mul__`/`inverse` do.
- Failure-only difference: an error raised inside what was a nested Python round trip (normalizing a
  zero vector) now has the plain runtime text (`division by zero`) without the `ValueError:
  enclosure-data:` wrapping of the nested call.
- `_rust_objects.reference` handles are permanent and identity-keyed: a cached Ref stays valid.
- serde_json has `float_roundtrip`; Python json uses repr: floats cross the boundary exactly, so
  computing `itertools.product` locally gives the generated code's values.
- `compare("is", Ref, None)` makes a remote `==`; no enclosure shape class defines `__eq__`
  (only `_rust_objects`/`_rust_part`/meshcad proxies do).

## _above_core_shell plan
- Replaceable (read from ns at each use): box, rectangle, ycylinder, zcylinder, rear_well_tower,
  wall_bosses, valve_seats, c14_rear_cutters, keystone_rear_geometry, fluid_supports (back-top
  `_above_leaves`), stacked_well_towers (front-top `_replace`); `above_core_wiring.shell_features` and
  the identification namespace's `apply` read at call time.
- Layout data (poses, mount axes/points, valve-seat corners, provider constants) cached per registry:
  `specification()` is functools.cached, `point`/`vector` are pure worker calls, nobody patches them.
- sys.path insertions kept on every call.

## Left
- build with `_above_core_shell` typed; names; direct-call probe; compare enclosure, enclosure-box,
  enclosure-assembly, bom-masses (both modules).
