# Kamoer cartridge and cap bench fit

The cartridge and cap can be qualified for a local bench-fit print independently of
the complete enclosure and the diaphragm-pump replacement. The retained
[`pump-cartridge-generation.json`](pump-cartridge-generation.json) identifies the
exact Box, scan evidence, runtime source closure and emitted STEP/STL/payload bytes.
It keeps `assembly_current: false` and `production_enclosure_released: false`.

The local check reads the emitted native parts. It verifies the two fitted skirt
lands, four 3 × 32 mm cap bearing rails, cap insertion and closure, screw adjustment,
continuous bay floor, current outlet-row alignment and tube clearance through the
local collet plate. The scan observations put the front rim at least 0.340 mm above
the floor; the conservative declared envelope retains 0.329 mm. The four rail
footprints bracket both scan passes within the available ±0.25 mm contact adjustment.
These are geometric checks. Printed fit and clamp load remain unmeasured.

The two pieces share the flat aft face at Y79.269. It preserves the complete 3 mm
skirt band and leaves 0.246 mm to the current collet plate. The preferred 0.25 mm
plate air has an explicit maximum 0.01 mm station allowance, matching the
hundredth-millimetre precision of the measured skirt datum. A native comparison
requires the corresponding 0.004 mm extension to add material only at the terminal
face, leaving wells, bearing lands and pull pockets unchanged.

The remaining tee branch/nose datums are explicitly carried as unqualified in the
manifest. Their final measurement can change the production cartridge/plate
relationship. This print establishes pump seating and cap contact; complete
four-tube operation requires the final collet plate and carrier, then a physical dry
cycle. The current full enclosure is not qualified by this bench fit.

## Reproduce

After the Box producer has finished successfully, pass its exact digest to the
dedicated local builder. The digest below names the retained checked Box; a changed
Box requires its own completed producer check.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/prepare_pump_geometry.py \
  --box-sha256 a1468381b233f54a07cd491fefe3dabdc56da89bb46fa3bffb6d2181802427c9
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/prepare_pump_print.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/review_pump_print.py
```

The print script uses the retained PET-GF profile, black material on Mark2's left
external spool, and the requested +0.04 mm trim. The native textured-plate command
is `G29.1 Z0.02` after the profile's compensation. The cartridge prints upright on
its flat bearing bottom; the cap prints on its crown with the four terminal rails
facing print-up. The scripts never connect to a printer.

[`pump-print-readiness.json`](pump-print-readiness.json) binds the actual native
archive, profile, source meshes and G-code. The
[`toolpath review`](pump-toolpath-review.json) reads the emitted bearing-rail roads,
temperatures, support topology and removal mouths. Its support ledger applies to
that exact slice; physical cleanup effort is a separate reading.

Remove all support before installing pumps or screws. Cartridge pull supports leave
through the open outer pockets. Any cap screw-seat support leaves through the
crown-facing counterbore mouths. The new cap rails have exposed sides and finish
print-up; no hardware covers them during cleanup.

For physical acceptance, both pump skirts must seat on their lands without the
rigid front rims lifting them. The cap must take up play through its four rails
before a screw or bridge reaches a hard stop, while the pumps and cap remain
removable. The final assembled collet/carrier mechanism needs its own insertion,
release, return and tube-capture check before powered or wet operation.
