# Tube and cable snap comparison — Mark2

Three separate objects share one centered plate and print **by layer**. Mark2
accepted **task 1379240291** at **11:33 p.m. CDT on October 26**, reporting
RUNNING with print error 0 and no HMS. The [launch receipt](launch.json),
[launch context](launch-context.json) and [preflight](preflight.json) bind the
reviewed archive, cleared-plate authorization and shared-circuit startup spacing.

| Position facing the printer | Test object |
| --- | --- |
| Front | Tube clips labelled **6.55 / 6.45 / 6.35 mm**, left to right |
| Rear left | Cable clip with **16 mm** cavity span on a **9 mm** wall |
| Rear right | Cable clip with **24 mm** cavity span on a **9 mm** wall |

## Physical result

The [physical result](physical-result.json) records Derek's preferred tube
sample, **C2 with the 6.35 mm CAD bore**, as good enough for present use.
Trying a smaller bore remains optional future tuning.

The smaller **16 mm-span** cable clip is accepted with the bare insulated 4P
ribbon: it fits perfectly and stays put. Straight sliding entry is difficult;
angling and pulling the ribbon into the seat succeeds. This result belongs to
these identified coupons. The 4 mm tube sections, DC-1 pair seat and V-K
single-wire seat have no physical fit acceptance from this plate. Numerical
retention forces, fatigue and lifetime remain unmeasured.

The [tube trio](../../tube-snap-exploration/README.md) retains C2's 2.40 mm wings,
125.421° wrap per wing, filled roots and rounded noses on a 60 × 16 × 3 mm floor.
The 0.10 mm diameter increment follows the organizer tuning. A straight long tube
runs along Y through only the chosen clip. The control's native geometry matches C2.

The [cable variants](../../cable-clip-exploration/wall9-span-geometry.json) retain
the accepted 2.20 × 7.75 mm seat, 1.45 mm mouth, 0.75 mm retaining beak, 3 mm
hook stock and 45° corbel. Host walls are **9 mm thick**, 28 or 36 mm long,
and extend 6 mm below the hook. Both print upright, entry-up, 25.7 mm tall.
The cavity spans along the cable are 16 and 24 mm. There are no small local
reliefs, added support fins or brim. The physical acceptance above covers the
selected 16 mm-span coupon's 4P fit and retention.

## Experimental cooling

This plate's project and embedded filament preset request **100% part fan from
layer four onward**, leaving the first three bed layers fan-off. The minimum-layer
target is **20 seconds**, allowing slowdown to 5 mm/s, including exterior walls.
Auxiliary cooling stays off. All three objects print on every applicable layer,
giving the nozzle another object to visit between cable layers.

The [manual cooling reading](cooling-review.json) finds full part-fan commands on
every upper cable path, and zero support or brim in all four seat/entry windows.
Commanded motion/feed timing gives a conservative **19.77–48.85 s** upper-layer
lower-bound range and at least **8.63 s** away from a cable object between visits.
Acceleration, synchronization and optional timelapse add time; this is not a measured
physical 20-second guarantee or fan-airflow measurement.

The [stopped coupon reading](failed-upright-cooling-review.json) finds upper-layer
feed-time lower bounds of **1.14–3.54 s** in the failed standalone archive. Its
[physical result](../../cable-clip-exploration/prints/2026-10-26-mark2-relay-ribbon/physical-result.json)
records Derek's cancellation and visible deformation. The stronger cooling and
time policy apply only to this experimental plate. The shared PET-GF source
profile remains unchanged; all three tube sizes share the same test cooling.

## Native preparation

Mark2 uses its left hardened 0.4 mm Standard-flow nozzle with black PET-GF on
external spool 254, reported as PET-CF. The process retains a 0.20 mm first layer,
0.24 mm normal layers, two walls and 15% gyroid infill. Tree(auto)/Default remains
enabled; the native slice emits **zero support and zero brim**. Mark2's +0.04 mm
user trim emits `G29.1 Z0.02` after reset on Textured PEI.

The native estimate is **50 min 25 s**, **13.45 g** using saved profile density,
with **123.985 mm** minimum full-bead bed margin. All three second-layer bead
footprints contact their first layers. The six upper tube wings have connected,
backed bead footprints with **99.50%** minimum sampled stock coverage. Every
sampled cable wall/corbel/hook component contacts previous-layer model material.

- [Editable project](2026-10-26-tube-and-cable-snaps-wall9-cooled-mark2-2179a771/2026-10-26-tube-and-cable-snaps-wall9-cooled-mark2-2179a771.3mf)
- [Native print archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/snap-fit-tests/2026-10-26-mark2-combined/2026-10-26-tube-and-cable-snaps-wall9-cooled-mark2-2179a771/2026-10-26-tube-and-cable-snaps-wall9-cooled-mark2-2179a771.gcode.3mf)
- [Native preview](2026-10-26-tube-and-cable-snaps-wall9-cooled-mark2-2179a771/plate_1.png)
- [Source bindings and preparation](offline-review.json)
- [Manual bead/contact reading](path-review.json)
- [Manual cooling and cavity reading](cooling-review.json)
- [Preparer](prepare.py) and [local declaration](job.json)
