# Direct tube-snap retention trial

The current comparison has **nine clips on three separate 60 × 16 × 3 mm
strips**. Every clip has the same **R3.275 mm / Ø6.55 mm bore**, 8 mm span
along the tube, filled lower root and tube centre 4.5 mm above the floor.
The two experimental axes are wing thickness and circular wrap.

| Strip | Wing thickness | Column 1 | Column 2 | Column 3 |
| --- | ---: | --- | --- | --- |
| A | 1.44 mm | A1 — reference wrap | A2 — +5° per wing | A3 — +10° per wing |
| B | 1.92 mm | B1 — reference wrap | B2 — +5° per wing | B3 — +10° per wing |
| C | 2.40 mm | C1 — reference wrap | C2 — +5° per wing | C3 — +10° per wing |

The reference circular end angle is 120.421° on each wing: 240.842° total
circular coverage. Columns 2 and 3 have 250.842° and 260.842° total coverage.
The rounded noses add their own surfaces beyond the circular seat. The
outer radius and nose radius follow wing thickness; the bore remains fixed.
Consequently the mouth width is an outcome of both axes, from 5.45 mm at A1
to 4.414 mm at C3. It is not a third independently tuned parameter.

**A1 repeats the tested smallest-bore clip geometry**, verified by native
Boolean comparison. The trial's [physical feedback](prints/2026-10-26-mark2-organizer-fit/physical-result.json)
identifies that size as the best of the first three while reporting all
three fairly loose and easy to remove. Quantified retention force remains
unmeasured.

Each sample has its identity raised 0.48 mm above the full 3 mm structural
floor. Facing the printer, A is the front strip, B the middle strip and C
the rear strip; columns 1–3 run left to right. **Separate the strips before
testing with a long tube.** The tube runs along Y and then meets only its
chosen clip, with the other two on that strip beside it along X.

Compare push-in and pull-out effort on the actual quarter-inch tube, seated
grip, axial movement, release and wing/root survival. Report the A1–C3 label
with any permanent opening, fracture or tube damage. These are experimental
fixtures, with no production assembly or accepted-retention claim.

## Preparation

The [Mark2 retention-matrix job](prints/2026-10-26-mark2-retention-matrix/README.md)
contains the three-part editable project, sliced archive and native reviews.
The three floors lie flat on the bed with the same layer direction as the
first trial.

```sh
tools/cad-venv/bin/python future/tube-snap-exploration/retention_matrix.py
tools/cad-venv/bin/python future/tube-snap-exploration/prints/2026-10-26-mark2-retention-matrix/prepare.py
```

The [generator](retention_matrix.py) and
[native geometry report](retention-matrix-geometry.json) bind all nine bore
sections, the three individual solids, their STLs/STEPs and the A1 control.
The earlier [organizer-sized bore trial](prints/2026-10-26-mark2-organizer-fit/README.md)
retains its print archive and physical result. Its [generator](tube_snap_trial.py)
also supplies the control shape for the current trial.
