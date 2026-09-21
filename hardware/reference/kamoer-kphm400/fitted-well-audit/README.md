# Kamoer fitted well and floor

The production lower well uses 0.4 mm of lateral case-profile air, the case's original
axial ramp stations, and 0.30 mm of extra room at the +Y skirt edge. The skirt lands
remain flat. The outlet passage retains its measured station.

The comparison in [fitted-well-check.json](fitted-well-check.json) reads the actual
September 13 cartridge/cap 3MF and its retained print provenance. It places the current
native well at that print's holder datums, so the reading isolates local fit from
the assembly's pump placement. It samples all 208 selected inward-facing lower-well
triangles on the positive pump, including 144 vertical-wall and 50 lower-ramp triangles.
The native comparison surface has a 0.004 mm tessellation tolerance; this is a sampled
surface reading rather than a bound on the whole assembly.

The actual print has its skirt land at Z205.494 mm, broad cap underside at Z215.745 mm,
and cartridge bottom at Z165.365 mm. In the same holder frame the current fixed floor
is Z164.015 mm. Changing only the floor-relief parameter leaves the native fitted well
and cap unchanged. A matching cartridge extends to that lower floor; placing the older
cartridge on it would lower the complete cartridge and both pumps.

Both raw scan passes are evaluated at unit scale in the recorded underside-strip
seated pose. Their observed rigid front rims project through the actual printed
cradle's open wells. The report records their clearance to the old bottom plane and
the current fixed floor separately. This supports the floor's role as front-rim
clearance, without identifying the physical assembly's clamp-load path.

[Derek's physical observation](../physical-fit.json) establishes firm retention of
both pumps and no vertical play in the assembled cartridge/cap. The exact print date
of that assembly and its individual contact faces are unconfirmed. The retained
September 13 print is the available earlier printable comparison.

Run from the repository root:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/reference/kamoer-kphm400/fitted-well-audit/check_fitted_well.py
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-tray/pump_tray.py selftest
```

The audit hashes its script, imported project sources, print input, provenance, scan
reports and supplied Box, checks both raw-cloud digests, and rejects inputs that
change during the run. It writes no native part or dependency graph. `--box` selects
a serialized placement input and `--output` selects the report path.

The full 3 mm aft skirt band and minimum 0.240 mm plate air are checked against that
explicit Box. This local fit report does not qualify a stale Box as current or replace
fresh assembly/tube checks, the raised cap's separate contact audit, or a physical
assembly test.
