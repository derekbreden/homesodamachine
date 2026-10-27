# Direct tube-snap fit trial

Three filled-root snaps share one **54 × 14 × 3 mm floor**. The floor lies flat
on the print bed, the tube axes run along Y, and the openings face up. The
quarter-inch tube centre is 4.5 mm above the floor's top face. This is a
physical comparison of grip, insertion and wing/root survival in that print
orientation.

The organizer's [accepted quarter-inch bore](../../hardware/printed-parts/faucet/umbilical-organizer/physical-acceptance.json)
is **Ø6.65 mm**. Its [last A/B/C tuning round](../umbilical-organizer-exploration/diameter-increments-mark2/README.md)
used **0.10 mm diameter steps**, as implemented by
[`prepare_increment_trial.py`](../umbilical-organizer-exploration/prepare_increment_trial.py).
The comparison here centres those steps on the accepted size.

Facing the printer, the snaps are ordered **smallest to largest, left to
right**. Mark the small-bore end before lifting the common floor off the bed.

| Position | Bore diameter | Relative to organizer | Nominal radial allowance around Ø6.35 tube |
| --- | ---: | ---: | ---: |
| A — left | 6.55 mm | −0.10 mm diameter | 0.10 mm |
| B — centre | 6.65 mm | Organizer size | 0.15 mm |
| C — right | 6.75 mm | +0.10 mm diameter | 0.20 mm |

Each snap has the same 8 mm span along the tube, 1.44 mm functional spring
wall, 0.72 mm rounded nose, and 5.45 mm mouth. The nominal tube extends
0.45 mm beyond each side of that mouth. The lower root is filled out to
straight exterior sides across the full span. The outer radius follows the
bore radius to retain the same spring thickness. There are no identification
cuts or lettering on the comparison floor.

The organizer's accepted bores printed upright; these seats print horizontally.
Its accepted fit therefore supplies the trial's diameter baseline, not an
acceptance of this snap's grip. The organizer has 9.2 mm of straight tube
contact between entrance chamfers; this snap has an 8 mm open seat. The short
upper wings and bending across printed layers are part of the physical test.

Try the actual quarter-inch tube in each position and compare insertion,
seated grip, axial movement and release. Record any root separation, broken
wing, permanent opening or tube damage with its A/B/C position. The desired
result is the close fit Derek identified on the organizer. A printed result
has not yet been reported for this trial.

## Preparation

The [Mark2 print job](prints/2026-10-26-mark2-organizer-fit/README.md) contains
the editable project, sliced archive and native review.

```sh
tools/cad-venv/bin/python future/tube-snap-exploration/tube_snap_trial.py
tools/cad-venv/bin/python future/tube-snap-exploration/prints/2026-10-26-mark2-organizer-fit/prepare.py
```

The [generator](tube_snap_trial.py) writes the
[STEP](parts/tube-snap-three-bores.step),
[STL](parts/tube-snap-three-bores.stl) and
[native geometry report](geometry-report.json). The report measures each
native bore section and binds the organizer baseline and tuning evidence to
their source hashes. The coupon is one connected solid with its bed face
at Z=0.
