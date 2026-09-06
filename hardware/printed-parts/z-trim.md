# First-layer z-trim

Format: facts only. Direct quotes from Derek where applicable. Settings observed in
committed `.3mf` snapshots.

The H2C sets its first-layer height with `G29.1 Z<mm>`, a firmware z-trim the machine start
G-code writes once per print, cleared to zero at the top of the block and set again by plate
type and nozzle. Bambu's stock values lower the nozzle on textured PEI, because homing lands
the tip on the tops of the texture:

| plate / nozzle | stock |
| --- | --- |
| Textured PEI, 0.2 mm | −0.01 |
| Textured PEI, 0.4 mm | −0.02 |
| other plate, 0.2 mm | +0.01 |
| other plate, 0.4 mm | — |

Negative lowers. This tree stands a flat **+0.01 to +0.20 mm** over those values on every
branch, so the figure holds whichever plate the project is set to. At +0.02, textured PEI
with the 0.4 mm nozzle comes to a trim of 0.00 — Bambu's texture compensation off, the nozzle
where homing and the bed mesh put it.

The figures are for the stack the exterior ships on: Bambu Lab H2C, 0.4 mm tungsten carbide
hotend on the left extruder, Polymaker Fiberon PET-GF15, textured PEI plate, 0.2 mm initial
layer ([enclosure/enclosure/print-log.md](/hardware/printed-parts/enclosure/enclosure/print-log.md)).

Derek, on 0.02: *"I think .02 might really be our setting, for this material and this nozzle
size on these beds in these H2Cs."* Then, off the prints it came back on: *"the more I look
at the prints here, the more I think I might be wrong and we might need a .01."*

## The carriers

[`z-trim-0.01.3mf`](z-trim-0.01.3mf) through [`z-trim-0.20.3mf`](z-trim-0.20.3mf) are empty
plates, one per value, carrying nothing but the printer profile — `Bambu Lab H2C 0.4 nozzle`
with `machine_start_gcode` as its one setting modified from system, on the `Polymaker PET-GF
@BBL H2C` slot over a textured PEI plate. Open one in Bambu Studio and save the printer preset
it loads modified.

Each carrier adds the value in its name to all four stock branches, so
`z-trim-0.07.3mf` on a textured plate with the 0.4 mm nozzle emits `G29.1 Z{0.05}` — stock
−0.02 plus 0.07. The files run 0.01 to 0.20 in 0.01 steps.

What the retained working file and the back-top's history snapshots stand on —
[`petgf.3mf`](petgf.3mf) is the PET-GF 0.4 mm working profile, whichever models are loaded into
it at the time:

| file | trim | printer preset |
| --- | --- | --- |
| [`petgf.3mf`](petgf.3mf) | +0.04 | `Bambu Lab H2C 0.4 nozzle 04 first layer by agent`, first layer 265 °C |
| history-only `git:657c7978c:hardware/printed-parts/petgf.3mf` | +0.17 | `Bambu Lab H2C 0.4 nozzle 17 first layer by agent`, first layer 280 °C |
| history-only `git:aef8f43c0eb3eef9c6525ecaa0a1ca52c5b8c71a:hardware/printed-parts/enclosure/enclosure/enclosure-back-top-petgf.3mf` | +0.02 | `Bambu Lab H2C 0.4 nozzle`, the start G-code its one project override |
| history-only `git:366d54ba040ecc7f1465c200e63e52410ffc0d4c:hardware/printed-parts/enclosure/enclosure/enclosure-back-top-petgf.3mf` | +0.02 | the same snapshot turned onto its ceiling, unprinted |

The `657c7978c` profile runs its **first layer at 280 °C**, the same nozzle temperature as the
rest of the print rather than a cooler one; the retained `petgf.3mf` carries a 265 °C first layer
on the `04` preset, and which of the two a long first-layer loop is sliced with is decided at the
printer. What asked for 280 °C and +0.17 is the welding rotary table: two plates of it failed in the first layer or two off a 265 °C first
layer, where the front-top, the pump cartridge and the display covers all came off the same
profile clean. The parts that failed carry the rig's large circles — the 165 mm ball race in
the base, the 90T pulley round the turntable — so their first layer is a long unbroken
perimeter loop with a full lap of cooling between one pass over a point and the next
([`fixtures/weld-rotator/README.md`](/hardware/printed-parts/fixtures/weld-rotator/README.md)
"Print").

## What else touches Z

The start block, in order: the bed mesh over the first layer's bounding box (`G29.20 A3`,
`G29 A1` and `G29 A2 … R`), then `G28 R`, then `G28.140 S0` to calibrate the pre-extrude z
pos, then the plate-type block that sets the trim, then `M983.4 S1` deformation compensation
and `G29.2 S1` position compensation on, then the nozzle-load line with `G28.14 R0` restoring
the pre-extrude position, and `G29.99` last before the print.

Nothing after the plate-type block sets `G29.1` again, and everything that re-derives Z — the
mesh, the homing, the pre-extrude calibration — runs before it. `layer_change_gcode`,
`change_filament_gcode`, `time_lapse_gcode` and `wrapping_detection_gcode` hold no `G28`,
`G29` or `G92` at all, and the end block's only `G92` is `G92 E0`. Bambu's own textured-plate
compensation is this same command in this same block, so a machine that discarded the trim
would discard the stock −0.02 with it.

The mesh is measured fresh each print, over the bounding box of that plate's own first layer.

[`z-trim-0.30-probe.3mf`](z-trim-0.30-probe.3mf) is the isolation print: +0.30 mm over stock,
ten times the sweep's step, more than a 0.2 mm first layer can reach the plate through.

## The plate is a variable

Two H2Cs, two 0.4 mm tungsten nozzles, two textured PEI plates. Derek: *"it seems one of the
confounding variables is which textured PEI plate is used. One of the plates is consistently
getting more melty pressed in material from first layer into plate, and is taking more lift
to get away from."*

Homing touches the peaks of the texture — Bambu's own comment on the block says the trim is
there because *"the nozzle was touching topmost of the texture when homing"*. Plate thickness
therefore cancels at the touch-off and texture geometry does not: at the same gap above the
peaks, a plate whose valleys are shallower or whose peaks are more worn takes more of the
first layer into itself. A trim value belongs to a plate, not to the machine and not to the
material, and the plates need marking for a value to be carried against one.

## What the machine receives

`BambuStudio --slice 0 --outputdir <dir> petgf.3mf` renders a plate headlessly, conditionals
already resolved. The emitted G-code holds one `G29.1 Z0 ; clear z-trim value first` near the
top and exactly one value line — `G29.1 Z0.02 ; for Textured PEI Plate` for a profile
carrying 0.04, the taken branch and no other. After it, only `G29.2 S1`, `G28.14 R0`,
`G29.2 S0`, `G29.2 S1` and `G29.99`; no second trim.

Slicing the same plate at 0.02 and at 0.20 and diffing the two G-codes leaves that one line
changed, plus seam-order noise. No layer Z moves, no flow, no speed, no temperature. Whatever
the trim does or does not do on the plate, the slicer is not the part that varies.

## Reading it back

The trim is firmware-side. The slicer does not model `G29.1`, so a plate sliced with one
reads the same layer heights as a plate sliced without: 0.20 mm for the first layer, 0.44 for
the second at `layer_height` 0.24. A preview whose layer Z has moved is not carrying a trim,
it is carrying a shifted coordinate origin — which is what `G92 Z` in the start G-code does.
That command re-bases Z at whatever height the toolhead holds when it runs, and at the end of
the H2C start block the slicer tracks that height at 6.2 mm above the plate.
