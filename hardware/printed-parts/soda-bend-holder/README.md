# Continuous soda inlet bend holder

This PET-GF holder carries one continuous 6.35 mm OD LLDPE tube around an R14
quarter turn into the core-mounted flow meter. Its 6.8 mm teardrop channel has
a 2 mm minimum wall and 3 mm straight legs at both ends. The flat back is the
print-bed face; the channel closes with 45° flanks.

The 2 mm wall is a named functional exception supported by the
[selected holder's physical result](../../../future/tube-bend-holder-exploration/prints/2026-10-23-legs-123-w2-petgf-left04-z018-mark1/physical-result.json).
The report covers this wall/leg combination qualitatively. Threading force,
tube roundness, flow, pressure and retention over time are unmeasured.

The [production inlet plan](../../manifold-layout/soda_inlet.py) supplies the
single native builder and installed frame. The holder is outside the wet
path, supported by the tube it encloses, and has no separate bracket.

One approximately 63 mm square-cut piece of the owned 6.35 mm ID/25.4 mm OD foam
slides over the tube and holder before the meter connection is made. The
[physical foam observation](../../reference/cargen-pipe-insulation/elbow-fit-2026-10-24/physical-observation.json)
supports qualitative compression around the pictured holder. The installed
occupied-space model estimates local compression against the named neighboring
bodies. Its Boolean subtraction is not a shaped cutting pattern, measured
strain or thermal-performance result; the physical foam remains one piece.

The plain cap guide is a boundary in the continuous tube. It adds no cut,
joint or receiving allowance. The 15.7 mm meter receiving depth remains a
layout estimate. The manual
[inlet receipt](../../mechanical-qualification/enclosure-above-core/soda-inlet-review.json)
records the current native passage and installed-envelope scope.

The cap's curved D7.5 passage carries the internal tube from its retained lower
riser to the plain guide at world `[50, 342.4148, 253.4]`. New side and roof stock
is 3 mm. Its horizontal run retains the established cup floor with 2.10 mm
backing; that floor has a separate 2 mm specification. The actual carbonator
metal outlet and its receiving allowance remain part of the continuous tube.

Regenerate from the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/soda-bend-holder/soda_bend_holder.py
```
