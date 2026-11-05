# mount (agent): presentation, artwork, skin, snaps, dimensions, fixed pump mount

Workspace: `$R/aws/mount` (own: `_rust_enclosure_presentation`, `_enclosure_presentation`,
`_disposal_artwork`, `_enclosure_skin`, `_tube_snap_sites`, `_route_snaps`, `_enclosure_dimensions`,
`_fixed_pump_mount`).

## Status
- All eight written with `TYPED = true`; workspace binary builds (20:06).
- `names.py` (with `$ref` renumbering), one module per run: 7 match (presentation 6+3, artwork 7,
  skin 16, tube sites 6, route snaps 10, fixed pump mount 38). `_enclosure_dimensions` cannot be
  probed there: baseline and typed both fail identically (`No module named '_facts'` in the
  enclosure stage); its step `enclosure-dimensions` covers it.
- names.py note: `bad` is not reset per module, so with several modules a module after one that
  errors prints DIFFER though it matches; run modules one at a time.
- Comparing (no `--direct`): quick batch (enclosure-dimensions, bom-masses, 8 presentation steps),
  enclosure.
- enclosure-assembly (binary 20:06): ok, 940 files, **16 differ** (wiring, routes, equipment,
  facts, drain check, assembly meshes). The coordinator sees the same families with a binary
  that changes no recipe and is running a control: left as is until `briefs/common.md` says
  otherwise. Clone deleted (disk); its `cable_passages` and six JSON hashes are in
  `aws/mount/probe/enclosure-assembly.mount.0.kept.json`. Step exercises
  only `datums` + `wiring_passages` of mine, plus 9 other agents' typed modules copied into my
  workspace (`_enclosure_datums` 13 fns, `fixed_returns` 15, `pump_tray` 4, ...). Two of the 16
  (`tmp/.../machine-equipment.json`, `machine-routes.json`) embed `~/Library/Caches/hsm/parts/tmp/
  <pid>-<n>` paths, which the harness does not mask. Attributing with a probe
  (`aws/mount/probe/`): my functions called with the enclosure's own `e` and Box under baseline
  and mine, results diffed.
- `_rust_enclosure_presentation`: `check_print`/`preserve_print_triangles` reach the numbers as the
  caller passed them (generated stores the given value, not `bool(...)`).

- pow/sin/cos rule (GUIDE "Semantics that decide bytes"): no `**`, `math.sin` or `math.cos` in my
  eight modules' generated code and no `powf`/`powi`/`sin`/`cos` in mine. The only transcendental is
  `math.tan` (`_fixed_pump_mount`: `tan_degrees` = `num::radians(x).tan()`, and `tan(pi / 8)` in
  `wing_profile`), which interop also computes with `f64::tan`.

## Names other code replaces (read through the namespace at each call)
- `_fixed_pump_mount`: `inverse_cuts`, `wire_cuts`, `upper_wire_room`, `display_cleanouts`
  (front-top `_leaves`), `_wing` (pump-retainer `_leaves`). `fixed_cuts`, `upper_wire_room`
  (its `wire_cuts`) and `retainer` (its `_wing`) call them via `rt.namespace(MODULE)`.
- `_route_snaps.apply` (back-top `_leaves`, also front-top through `_shared_leaves`): nothing in
  the module calls `apply`, so no internal read needed.
- The enclosure's own leaves (`e._ybox`, `e._xz_prism`, `e._pump_lower_well`, `e._ycyl`,
  `e._tray.boss_room`, ...) are read from `e` at each call.

## Findings
- `_disposal_artwork.numbers` keeps `functools.cache` via `rt::memoize` (the namespace value);
  `flat_bounds` parses the cached document once per `(family, kind)` into a typed reading.
- `_enclosure_skin`: `struct.pack/unpack("<QQ")` done in Rust; flute_skin/reeding field constants
  read once; rails, meshes, arrays stay Python objects.
- `_enclosure_dimensions`: generated behavior has no `ast` (condenser figures are
  `getattr(condenser_block, name)`); `_enclosure_datums` is typed, so `load` is called directly.

## Left
- build, `names.py`, compare: enclosure, enclosure-dimensions, enclosure-assembly, bom-masses,
  and the presentation steps (who.py).
