# Pump cartridge and cap

The cartridge and raised cap are parts of the complete enclosure trial. The complete
assembly and its physical observations are indexed in
[print readiness](../print-readiness.md). The cap carries the female half of the
[magnetic pogo connection](/hardware/reference/yyfkgcp-pogo-4p/mounting-audit.md);
the male half stays in front-top's bay bulkhead. Its four leads stay on the pump tabs
when the cartridge is withdrawn.

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
0.246 mm air to the collet plate. The retained holder check includes cap insertion,
screw access, front-rim clearance, all four outlet axes and cartridge withdrawal.
The measured tee branch travel is integrated; exact terminal-ring seam and diameter
remain conservative clearance proxies in the native report.

## Native evidence

[`pump-cartridge-generation.json`](pump-cartridge-generation.json) binds a 2026-09-23
holder snapshot to 50 local geometry checks. That report's source and export hashes
are its scope; it does not qualify the current pogo seats. The
[current mounting audit](/hardware/reference/yyfkgcp-pogo-4p/mounting-audit.json)
checks the existing cap and front-top exports, nominal mating and drawing-tolerance
stack without changing CAD:

```sh
tools/cad-venv/bin/python hardware/reference/yyfkgcp-pogo-4p/audit_mounting.py
```

## Print and assembly

Each reviewed two-part archive, with the printer, settings and geometry hashes it binds,
is listed in the [slice reviews](../tee-readiness/full-enclosure-print/native-slice-reviews/README.md).
These archives qualify their identified meshes; a cap carrying the pogo seats needs
its own native slice review. The [contact coupons](contact-pair-coupon/README.md) retain
the production seat orientation for local roof, fit and lead-passage observations.
Both parts use black PET-GF on the left 0.4 mm nozzle. The cartridge stands on its flat
underside; the cap prints crown-down.

The [support audit](pump-support-audit.md) names the actual support bodies and their
removal lanes. Remove them before installing pumps or screws. The complete enclosure
trial checks the raised crown with actual terminal connectors, pump seating, marked
tube insertion depth, capture under a tug, four-collet release and spring return.
Physical support-removal effort and operation remain observations of that trial.
