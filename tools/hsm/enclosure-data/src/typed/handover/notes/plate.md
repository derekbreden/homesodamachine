# plate: nameplate family conversion notes

Modules (in order): _nameplate_interface, _nameplate_wing_interface, _data_wing_interface,
_nameplate_dimensions, nameplate, _y_wall_dimensions, data_ring, rear_identification.

Workspace: $R/aws/plate (ws.sh run with all eight modules).
Readable generated copies: scratchpad gen/*.s.rs (rustfmt, source sites stripped), gen/decode.py
prints a function as pseudo-Python (`python3 decode.py <m>.s.rs '// start' '// end'`).
Call probe: `python3 aws/plate/probe/run_calls.py aws/plate/probe/spec5.json <binary>` (from $R,
background; SHOW=1 prints values); it removes its work dirs.

## Status (wound down 2026-11-04 21:50 at the coordinator's request)
- Verified (call probe spec5 against the baseline, all same except the in-process `_read`
  error text, since fixed but unbuilt; names.py run before the $ref fix: names identical, only
  PosixPath $ref numbers differ): _nameplate_interface, _nameplate_wing_interface,
  _data_wing_interface, _nameplate_dimensions, _y_wall_dimensions.
- Written, TYPED = true, never compiled (build stopped at wind-down): nameplate, data_ring,
  rear_identification. No genrule comparison was run for any module.
- Deleted: aws/plate/names, aws/plate/probe, scratch gen/. No work/*.plate.* existed.

## Findings
- _enclosure_data.dimensions() -> JSON from main.rs `defaults`; serde_json has no preserve_order,
  so the face/nameplate/data/plan dict keys come in sorted order; every number there is a float.
- No memoize in any of the eight generated modules: nameplate's lru_cache decorators and
  rear_identification's functools.cache are dropped by the transpile, so typed code does not cache.
- rear_identification: `_enclosure_back_top._above_leaves` setattr's `apply` and `receiver_field`
  on it; field_land reads `receiver_field` from the namespace. Its `_read`s are in-process, with
  `above_core.specification()` (cached in Python) held as JSON from install.
- rear_identification namespace: the uppercase `labels` keys come in sorted order (STATIONS,
  THICK, WIDTH, WORD_*); STATIONS and WIDTH are rebound in place; WORD_LIFT stays the `_values`
  dict itself (a Ref).
- nameplate.numbers -> crate::nameplate_snap::numbers(dict, &compiled::Env) reads `wing` from the
  Env: typed code builds `compiled::Env::module("nameplate")` with `wing` set.
- Pens: state kept in Rust keyed by the Python instance's $ref (stable: _rust_objects never frees);
  the "Class.method" entries take Python self; super().__init__(None) still runs on the instance.
- `_data_wing_interface::Data` gained `ink_depth` (data_ring reads it); `_y_wall_dimensions`
  State exposes `chip_filaments` (rear_identification.numbers iterates it).
