# rear (rear_snaps, rear_plumbing)

## Status (wind-down)
Both modules are fully converted. Both are TYPED = false because the current source of each
was edited after the last compiled binary (ws/rear, 20:16), and that edit has not been compiled.
The parent stopped the rebuild during the wind-down. The 20:16 binary is the one that was
compared and probed. ws/rear is deleted.

- rear_snaps
  - Verified on the 20:16 binary:
    - rear-equipment-caps: 278 files, 0 differ (base = bin/machine-data, BINDIR = bin-all, no
      unpinned workers).
    - The probe matched the generated build on every rear_snaps call: 85 calls in all, every
      function of both modules, shapes digested by BREP sha256 and volume. It covers pockets,
      pisco_cap_service_cuts, asse_service_corner, pisco_bearing_profile, the cap_section and
      section_solid variants, cap, build and the helpers no genrule runs. Script:
      /private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/d7001403-7740-4475-8098-abce61ab6b5f/scratchpad/probe_rear.py,
      run by probe-run.sh beside it.
  - Not compiled yet (edited 20:24): `pow2` calls libm `pow` with a `black_box` exponent, and
    every sine and cosine goes through `num::sin`/`num::cos`. At opt 0 this is the same code;
    it keeps opt 3 equal to the runtime.
  - Left:
    - Compile.
    - Compare enclosure and foam-cap. The wind-down stopped both runs before their typed side
      ran. Only enclosure exercises back-top's swapped `box`/`prism_x`/`section_solid`. The
      typed code looks those names up in the namespace at each call: 12 `box`, 2 `prism_x` and
      6 `section_solid` lookups, one for one with the generated code.
    - Then set TYPED = true.
- rear_plumbing
  - Verified on the 20:16 binary: rear-equipment-caps (plan, reference, chain, snap_datums,
    meter_spans), 0 differ. The probe matched every call except these:
    - `_flavor_rear`, `_flavor_s_bend` and `flavor_routes` raised without the transport's
      `ValueError: layout-data: ` prefix. Fixed at 21:19 in `data()`, not compiled. The fix is
      the same wrap misc verified by run in above_core_parts: the worker answers a refused
      recipe with `{"error": "{error:#}"}`, and the Python transport raises
      `ValueError("layout-data: …")`.
    - `continuations` differs in the last bit of one coordinate: above-core-va-fore-feed
      centerline_mm/points_mm [37][0], generated 11.03695186801432, typed 11.036951868014318.
      This is the opt level, not the typed request. continuations_direct.py (beside
      probe_rear.py) rebuilds the request and sends it straight to bin-all/layout-data
      (opt 3). Its answer equals probe-base exactly and differs from probe-rear at that one
      coordinate. The typed code answers in process with the layout-data crate compiled at the
      workspace's opt 0; layout-data lib.rs:99/235 sample arcs with sin and cos, which opt 3
      merges into `__sincos_stret`. Not yet run against an opt-0 worker.
  - No genrule runs continuations, flavor_routes, `_flavor_*`, route_specs or
    `_route_stations`.
  - Left:
    - Compile and re-probe. Expect 0 differ at release, and only the continuations bit at
      opt 0.
    - Then set TYPED = true.

## Coverage (who.sh, sweep complete)
- rear-equipment-caps: rear_snaps asse_cap_profile, meter_cap_corner_room, half_width, station,
  receiver_tool_ports, pisco_grip_stock, pisco_station, pisco_cap_span, cap_section (+ its `run`);
  rear_plumbing plan, reference, chain, snap_datums, meter_spans.
- enclosure: rear_snaps half_width, station, receiver_tool_ports, pisco_bearing_profile, pockets,
  pisco_cap_service_cuts, asse_service_corner, pisco_station, pisco_cap_span; rear_plumbing as above.
- foam-cap: rear_snaps station, receiver_tool_ports.
- No genrule runs: rear_snaps surface_points, envelope, swept, steps, turned, hex_prism,
  box/prism_x/section_solid (back-top swaps them in), stadium_x, radial_profile,
  stadium_profile_x, radial_room, cap, at_world, build; rear_plumbing union_tee, check, joint,
  _arc_three, ports, _route_stations, route_specs, continuations, _flavor_s_bend, _flavor_rear,
  flavor_routes.

## Findings
- For every agent: at opt >= 1 LLVM rewrites `x.powf(2.)` (constant exponent) to `x * x`, and
  macOS libm `pow(x, 2.0)` differs from `x * x` in the last bit for 2597 of 2,000,000 random
  doubles (e.g. 23.03655421175654: pow 530.6828299511978, x*x 530.682829951198). Interop's
  `binary("pow")` always calls libm `pow` (runtime exponent), so typed `x.powf(2.)` matches the
  generated code at opt 0 and not at opt 3. `x.powf(std::hint::black_box(2.))` keeps the libm
  call (checked with rustc -O on this Mac). Same class as the sincos merge; a shared
  `num::pow` would hold it in one place.
- Any typed module that answers layout-data in process (`rt.layout_data`) is compared at the
  workspace's opt level against the opt-3 worker the generated build asks, so an arc sample can
  differ in the last bit at opt 0 although the request is identical.
- Generated `envelope` wraps elementwise numpy comparisons in `Val::Bool(compare(..).truthy())`:
  `bool(ndarray)` raises for >1 element, so `envelope` (and `build`, which calls it after
  `surface_points`) always errors on real point clouds. `build`'s masks (`vent`, `keep`, `m`,
  `np.where` conditions, profile row masks) use the same pattern. The typed code keeps it.
- `build`, `surface_points`, `envelope`, `swept`, `steps`, `turned`, `hex_prism`, `at_world`,
  `stadium_x`, `stadium_profile_x`, `radial_profile`, `radial_room`, `cap` have no caller outside
  the module (git grep); only `build` reaches them.
- Callers: enclosure-data back-top (`station`, `half_width`, `pockets` with box/prism_x/
  section_solid swapped, `pisco_cap_service_cuts` with box swapped, `asse_service_corner` with
  section_solid swapped, `pisco_cap_span`, `pisco_station`, `pisco_bearing_profile`, native
  `clearance_profile`; `pockets` also gets the meter station and the regulator station from
  native `regulator_datums`, which carries `tool_inner_slope` 2.0); enclosure-data
  rear_equipment_caps (`station`, `half_width`, `asse_cap_profile`, `cap_section`,
  `pisco_cap_span`, `pisco_station`, `pisco_grip_stock`, `meter_cap_corner_room`, natives);
  cold-core above_core_mounts (`station`, `receiver_tool_ports`, `cap_section`, `section_solid`,
  `pockets`, `WALL`); foam_cap getattr WING..CATCH; print-tests/rear-snap-retention/build.py
  (`WALL`, `pisco_cap_span`).
- Only back-top assigns into rear_snaps (box, prism_x, section_solid). Nothing assigns into
  rear_plumbing. Typed code reads those three, and the natives installed after the top level,
  from the namespace at each use.
- `receiver_tool_ports` returns `[]`, so `pockets`' tool-port prisms and flare loop never run.
- `above_core_parts._module` re-executes the reference module on every call: chain()/check()/...
  calls are kept one for one.
