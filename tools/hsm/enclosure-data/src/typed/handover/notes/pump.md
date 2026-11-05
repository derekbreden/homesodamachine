# pump: pump_case, pump_tray

## Done
- Read sources: py/, compiled/, src/pump_case.rs + src/pump_tray.rs recipes, stubs, sigs.
- Workspace: `$R/ws.sh pump pump_case pump_tray`.
- typed/pump_case.rs written (TYPED = true); first build: two `&state(rt)?` borrow errors, fixed.
- typed/pump_tray.rs written (TYPED = true); both build.
- names.py pump_case,pump_tray: 118 and 73 names match.

## Left
- Compare without `--direct`: pump-case, pump-tray (running), then enclosure, enclosure-box, enclosure-assembly, internal-plumbing-sync,
  enclosure-mechanical-sync, enclosure-dimensions, bom-masses.

## Design
- `_read(op, **v)` answered by `rt.enclosure_data(json!({"op":..}))`; an error maps to
  `ValueError: enclosure-data: {e:#}` (the text the Python round trip raises back into Rust).
- pump_case State: typed `Case` (every scalar, arrays, profiles), the defaults reply JSON (sent
  back as `case`), provider handles (cq, WorldWorkplane, planes, Frame, ramps), `_here`.
- Namespace: `_case` = from_json(reply); `globals().update(_case)` = a separate from_json per key,
  in the reply's key order (serde Map order, as Python sees the worker's text).
- pump_tray State: typed `Stock` (the 35 `pump-tray-defaults` names), that reply as JSON (sent
  back as `stock`: nobody rebinds a stock name), `_pump_source()` as JSON (25 `_kp` constants
  read once; the Python-facing `_pump_source()` returns a fresh dict of their snapshots).
- Names others replace: pump_tray `boss_room` (front-top `_replace(shell._tray, ...)`); own code
  never calls it. `installed_boss_room(rt, air)` reads it through the namespace for typed callers.
  Nobody setattrs pump_case names.
- Int literals kept: loft start `0`, `_lower_profile_set(0)`, `offset=0`, `2 *`, snap signs ±1,
  `up_sign` ±1. support_z / z0 / z1 / skirt_y_max held as Num (they reach CadQuery as given).
- main blocks: `_rust_part` imported and started after the module body (as the generated
  entrypoint does), then pump_tray's `selftest` → `sys.exit(code)` check, then `main`.

## Found
- No genrule runs any CadQuery builder of either module (cadquery is deferred in all steps).
- selftest's `except Exception as exc: fails.append(str(exc))` keeps the error's outermost
  message; a provider error's text is not Python's `str(exc)`. No genrule runs selftest.
