# Fore paired snap print preparation

The cap and top lid have offline Mark2 jobs for black PET-GF on the left hardened
0.4 mm Standard-flow nozzle. The cap uses three Classic loops and 100% zig-zag
infill. Source +Y becomes print +Z; the six-millimetre extrusion stands on its
−Y end, with the 1.44 mm spring sections and their bending profiles in the bed
plane. Every layer repeats the same section, so the cap needs no supports.

The lid keeps its existing pose, three-wall recipe, ordinary infill and
Tree(auto)/Default supports. One 100% zig-zag modifier covers the existing
receiver, its two axial shoulders and a 3 mm-deep lid root. The modifier adds
no geometry. Its appliance bounds are X41.885–66.615, Y203.5–216 and
Z250.4–260.4 mm; the native lid bounds are recorded with their frame transform
in [`fore-snap-print-regions.json`](../../fore-snap-print-regions.json).

[`review.json`](review.json) binds both projects, sliced archives and their
current STEP/STL sources. The cap's full-bead bed margin is 150.04 mm and its
slice contains no supports. The lid's margin is 21.13 mm. Its unchanged native
bytes and identical modifier geometry preserve the identified offline slice;
the original region input is frozen alongside that preparation.

The emitted lid support-interface boxes do not meet the fore receiver/root
region. Its short catch ledges print with the model. The cap retains 0.40 mm
at their undersides, and the top and both flanks remain open for inspection
and cleanup before fitting the tubes and cap. Other lid supports retain their
automatic recipe. This records access and emitted paths, not printed surface
finish or removal effort.

The manual [`review.py`](review.py) additionally samples actual model beads
through the cap roof, both spring leaves and both hooks using the existing
native print reader. Its sampling boxes are analysis only. No build or commit
invokes this reader.

```sh
tools/cad-venv/bin/python hardware/printed-parts/cold-core/foam-cap/prepare_fore_snap_regions.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py reservoir-a-fore-snap-cap --slice --review --output .cache/prints/reservoir-a-fore-snap-2026-10-26
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py foam-cap-lid-top --slice --review --output .cache/prints/reservoir-a-fore-snap-2026-10-26
```

These commands prepare and slice without contacting a printer. Physical fit,
retention, release, load capacity and repeated-use performance remain unmeasured.
