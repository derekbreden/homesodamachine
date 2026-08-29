# First-layer z-trim

Format: facts only. Direct quotes from Derek where applicable. Settings observed in
committed `.3mf` snapshots.

The H2C sets its first-layer height with `G29.1 Z<mm>`, a firmware z-trim the machine start
G-code writes once per print, cleared to zero at the top of the block and set again by plate
type and nozzle. Bambu's stock values lower the nozzle on textured PEI, because homing lands
the tip on the tops of the texture:

| plate / nozzle | stock | this tree |
| --- | --- | --- |
| Textured PEI, 0.2 mm | −0.01 | **+0.01** |
| Textured PEI, 0.4 mm | −0.02 | **0.0** |
| other plate, 0.2 mm | +0.01 | **+0.03** |
| other plate, 0.4 mm | — | **+0.02** |

Negative lowers. Every branch stands **+0.02 mm** over stock, so the figure holds whichever
plate the project is set to. On textured PEI with the 0.4 mm nozzle it comes to a trim of
0.00 — Bambu's texture compensation off, the nozzle where homing and the bed mesh put it.

The figure is for the stack the exterior ships on: Bambu Lab H2C, 0.4 mm tungsten carbide
hotend on the left extruder, Polymaker Fiberon PET-GF15, textured PEI plate, 0.2 mm initial
layer ([enclosure/enclosure/print-log.md](/hardware/printed-parts/enclosure/enclosure/print-log.md)).

Derek: *"I think .02 might really be our setting, for this material and this nozzle size on
these beds in these H2Cs."*

## The carriers

[`z-trim-0.02.3mf`](z-trim-0.02.3mf) and [`z-trim-0.03.3mf`](z-trim-0.03.3mf) are empty
plates that carry nothing but the printer profile — `Bambu Lab H2C 0.4 nozzle` with
`machine_start_gcode` as its one setting modified from system, on the `Polymaker PET-GF @BBL
H2C` slot over a textured PEI plate. Open one in Bambu Studio and save the printer preset it
loads modified.

| | textured 0.2 | textured 0.4 | other 0.2 | other 0.4 |
| --- | --- | --- | --- | --- |
| [`z-trim-0.02.3mf`](z-trim-0.02.3mf) | 0.01 | 0.0 | 0.03 | 0.02 |
| [`z-trim-0.03.3mf`](z-trim-0.03.3mf) | 0.02 | 0.01 | 0.04 | 0.03 |

[`enclosure/enclosure/enclosure-back-top-petgf.3mf`](/hardware/printed-parts/enclosure/enclosure/enclosure-back-top-petgf.3mf)
carries the 0.02 values, byte-identical in its start G-code to `z-trim-0.02.3mf`.

## Reading it back

The trim is firmware-side. The slicer does not model `G29.1`, so a plate sliced with one
reads the same layer heights as a plate sliced without: 0.20 mm for the first layer, 0.44 for
the second at `layer_height` 0.24. A preview whose layer Z has moved is not carrying a trim,
it is carrying a shifted coordinate origin — which is what `G92 Z` in the start G-code does.
That command re-bases Z at whatever height the toolhead holds when it runs, and at the end of
the H2C start block the slicer tracks that height at 6.2 mm above the plate.
