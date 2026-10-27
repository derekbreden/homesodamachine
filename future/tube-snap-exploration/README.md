# Direct tube-snap bore trial

The current comparison has **three clips on one 60 × 16 × 3 mm floor**.
Every clip keeps C2's **2.40 mm wings**, **125.421° circular wrap per wing**,
rounded noses, filled lower root and 8 mm span along the tube. The tube centre
is 4.5 mm above the floor. Only the bore diameter changes; the outer radius
follows it to retain the same wing thickness.

| Position | Raised diameter label | Bore radius | Role |
| --- | ---: | ---: | --- |
| Left | 6.55 mm | 3.275 mm | C2 control |
| Centre | 6.45 mm | 3.225 mm | One diameter step down |
| Right | 6.35 mm | 3.175 mm | Two diameter steps down |

The step is the organizer's established **0.10 mm in diameter**. All three
mouths face up and their tube axes run along Y. A long straight tube meets
only its selected clip; the other two clips sit beside it along X. Raised
labels leave the full 3 mm floor intact.

The [matrix physical result](prints/2026-10-26-mark2-retention-matrix/physical-result.json)
identifies the thickest row, C, as best, and its middle sample, C2, as preferred.
It calls for smaller bores to improve grip. The 6.55 mm control matches C2's
native clip geometry with zero missing or added volume. The [geometry report](c2-bore-geometry.json)
binds that comparison, all three native bore sections, the source and the exports.

The [Mark2 C2 bore job](prints/2026-10-26-mark2-c2-three-bores/README.md) has a
**14 min 12 s** native estimate and emits no support or brim. It is ready for
the bed after the upright cable-clip coupon is removed.

Compare insertion, seated grip, axial movement, removal and wing/root survival
on the same actual quarter-inch tube, identifying each result by its diameter
label. The two smaller bores have no physical result yet.

```sh
tools/cad-venv/bin/python future/tube-snap-exploration/c2_bore_trial.py
tools/cad-venv/bin/python future/tube-snap-exploration/prints/2026-10-26-mark2-c2-three-bores/prepare.py
tools/cad-venv/bin/python future/tube-snap-exploration/prints/2026-10-26-mark2-c2-three-bores/path_review.py
```

The [retention-matrix job](prints/2026-10-26-mark2-retention-matrix/README.md)
contains the A1–C3 layout and source. The [organizer-sized bore trial](prints/2026-10-26-mark2-organizer-fit/README.md)
records the diameter increment and its qualitative physical comparison.
