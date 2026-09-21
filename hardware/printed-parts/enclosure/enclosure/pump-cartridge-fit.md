# Pump cartridge and cap

The current cartridge and raised cap are parts of the complete enclosure trial.
[`pump-cartridge-generation.json`](pump-cartridge-generation.json) binds their native
STEP/STL exports, the checked Box and 50 passing local geometry checks. The complete
assembly and its physical trial have their own readings in
[print readiness](../print-readiness.md).

The cap has a broad underside, fitted octagonal boss openings and Ø37 motor bores.
Derek confirms that the assembled holder retains both pumps firmly with no vertical
play. The [physical-fit record](/hardware/reference/kamoer-kphm400/physical-fit.json)
and [fitted-well comparison](/hardware/reference/kamoer-kphm400/fitted-well-audit/README.md)
identify that accepted fit. The surrounding crown reaches the cartridge top at
Z284.174 mm. Two Ø45 terminal wells leave both motor ends open. Two M3×60 screws seat
in counterbores accessible from above.

The cartridge uses the matching relieved enclosure floor. Its fitted lower wells
match the retained printed input within 0.004 mm at the sampled triangles. The cap
and cartridge share an aft face at Y79.269 mm, with a complete 3 mm skirt band and
0.246 mm air to the collet plate. The current local check includes cap insertion,
screw access, front-rim clearance, all four outlet axes and cartridge withdrawal.
The measured tee branch travel is integrated; exact terminal-ring seam and diameter
remain conservative clearance proxies in the native report.

## Reproduce the native check

The command checks the existing exports against the retained current Box:

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/prepare_pump_geometry.py \
  --existing-exports \
  --box-sha256 7407956c5dc8e371113406815ff10518a7fe205e4e81d3162ad75c5c262bf5c7
```

## Print and assembly

The [full enclosure queue](../tee-readiness/full-enclosure-print/queue.json) identifies
the current two-part Mark2 archive. Both parts use black PET-GF on the left 0.4 mm
nozzle, the saved automatic-brim profile and +0.04 mm requested trim. The emitted
textured-plate command is `G29.1 Z0.02`. The cartridge stands on its flat underside;
the cap prints crown-down.

The [support audit](pump-support-audit.md) names the actual support bodies and their
removal lanes. Remove them before installing pumps or screws. The complete enclosure
trial checks the raised crown with actual terminal connectors, pump seating, marked
tube insertion depth, capture under a tug, four-collet release and spring return.
Physical support-removal effort and operation remain observations of that trial.
