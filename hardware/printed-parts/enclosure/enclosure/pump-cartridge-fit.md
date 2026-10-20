# Pump cartridge and cap

The cartridge and raised cap are parts of the complete enclosure trial. The complete
assembly and its physical observations are indexed in
[print readiness](../print-readiness.md). The cap carries the female half of the
[magnetic pogo connection](/hardware/reference/yyfkgcp-pogo-4p/mounting-audit.md);
the male half stays in front-top's bay bulkhead. Its four leads stay on the pump tabs
when the cartridge is withdrawn.

The lower cradle and fixed receiver wall carry eight attracting SB443-IN pairs,
one four-high column on each pump's own load line at the fluid-port row. The
blocks are bedded in DP420 and pushed home to the floor of one 45°-roofed pocket
per column in each part, and the bare poles meet at the cartridge's seat
([magnet record](../pump-dock/magnet-retention.md)).
Installed retention and contact compression remain physical qualifications.

The cap has a broad underside, fitted octagonal boss openings and Ø37 motor bores.
Derek confirms that the assembled holder retains both pumps firmly with no vertical
play. The [physical-fit record](/hardware/reference/kamoer-kphm400/physical-fit.json)
and [fitted-well comparison](/hardware/reference/kamoer-kphm400/fitted-well-audit/README.md)
identify that accepted fit. The surrounding crown reaches the cartridge top at
Z284.174 mm. Above each motor bore a 45° cone opens through the crown and leaves the
motor end open. Two M3×60 screws seat in counterbores accessible from above.

The cartridge uses the relieved enclosure floor. The cap and cartridge share an
aft face at Y82.265 mm, with a complete 3 mm skirt band and 0.250 mm body clearance
to the receiver wall. The contact faces are each recessed 0.125 mm, giving a
0.500 mm nominal mating gap. The four prepared LLDPE stubs are clamped in the pump
heads and pass the lower cradle's open tube passages. Their tips enter permanent TPU
receivers and finish 0.50 mm before the internal shoulders.
The meeting magnet poles establish that position; the broad aft planes retain
their stated clearance.

The [fitted-well audit](/hardware/reference/kamoer-kphm400/fitted-well-audit/README.md)
records its sampled 0.004 mm match to the retained printed input and its cap,
screw-access, front-rim and outlet-axis scope. It does not extend the accepted
holder fit to the complete fluid dock.

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

The RC62 trial's [paused source](magnet-retention/pump-cartridge-pause.3mf) and
[emitted-path check](magnet-retention/native-check.json) retain their identified
ring-pocket scope. The current SB443-IN columns follow the bonding process
linked above. The cap's purchased pogo magnets arrive inside the connector.

The [support audit](pump-support-audit.md) names the actual support bodies and their
removal lanes. Remove them before installing pumps or screws. The complete enclosure
trial checks the raised crown with actual terminal connectors, pump seating, marked
stub tip positions, stub clamping, simultaneous four-receiver insertion, fixed
receiver/tee retention and straight cartridge withdrawal.
Physical support-removal effort and operation remain observations of that trial.
