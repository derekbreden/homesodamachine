# Faucet cooling and seam comparison — Mark2

Six specimens use sections of the [accepted Industrial faucet](../../industrial/physical-acceptance.json).
The product geometry and shipping recipe remain separate from this experiment.
The plate uses black Polymaker PET-GF, the fixed left hardened standard-flow
0.4 mm nozzle, Textured PEI, and Mark2's +0.04 mm trim (+0.02 emitted).
Nozzle temperatures are 265/280°C; bed temperature is 80°C.
Timelapse and bed leveling are enabled; nozzle probing clump detection is disabled.

Facing the printer, the front row is **A, B, C** from left to right.
The back row is **D, E, F** from left to right. Foot centers are 68 mm apart;
their 59 mm bodies have 9 mm between them. Neck centers are 36 mm apart.
The native model, support and brim footprint has at least **61.2 mm** of edge
clearance, exceeding the requested 40 mm inset. See [plate placement](plate-layout.png).
The native estimate is **7 h 28 min 03 s**, about 170 g at the saved filament density.

| ID | Actual faucet section | One comparison |
| --- | --- | --- |
| A | Full-size tilted foot, underside and first shoulder | Reference model cooling commanded on the accepted faucet |
| B | Identical to A | Half A's part-fan command in the shoulder band |
| C | Identical to A | At least 70% part fan in the shoulder band |
| D | Full-size tilted straight neck and actual internal passages | Regular back seam |
| E | Identical to D | Bambu contour scarf, 10 mm length |
| F | Identical to D | Same scarf, 20 mm length |

The foot specimens retain the original −15° pose, actual first-bed contact,
tilted underside, supported faces and continuous six-wall solid foot modifier.
The model is cropped above print Z33.799 mm. Its first layer is 0.20 mm;
normal layers are 0.24 mm, with the accepted 0.12 mm band at Z13.40–29.00 mm.
All three keep Tree(auto), Default style, 0.45 mm requested top gap,
two interface layers and 0.50 mm interface spacing.

A's model fan is read from actual outer/overhang wall commands in the accepted
faucet archive at the same print height. B halves that command; C raises it to
at least 70%. The treatment is confined to model deposition at Z13.40–29.00 mm.
Support deposition, brims and the other heights retain native cooling.
Native motion, extrusion, feedrates, heater commands and other fans are unchanged.
`finish.py` applies these explicit fan commands and updates the archive checksum.
Re-slicing the editable project alone does not reproduce this comparison.

The neck specimens are cut at parent print Z82–120 mm, with a print-horizontal
bottom. They retain the tilted curved outside and real passages, but have a
stable seated start. Their normal layer height is 0.24 mm, with 0.08 mm at local
Z16.04–35.24 mm. All three place the seam on the rear curved wall. E and F use
Bambu's other saved scarf defaults: 10% start height, zero slope gap, 10 steps,
smart application at 155°, inner-wall scarf enabled, entire-loop scarf disabled.

The cooling hypotheses point in opposite directions. Lower cooling might improve
bonding between fine strands; higher cooling might freeze a soft edge before it
curls into the nozzle path. A, B and C hold the geometry, supported contact, layer
height and temperature constant to distinguish those responses. D, E and F ask
whether a gradual seam helps this material and curvature, and whether doubling
the overlap length helps or spreads the blemish.

The [PET-GF support evidence](../../../../print-tests/petgf-interface-edges/README.md)
supports the larger gap for clean release. The
[interface-pattern evidence](../../../../print-tests/petgf-interface-patterns/README.md)
identifies loose retained strands as the model's first bridge layer. Accordingly,
this plate retains the accepted support separation and tests cooling first.

[Polymaker's PET-GF15 guidance](https://shop.polymaker.com/products/fiberon-pet-gf15)
lists 280–310°C, a 70–80°C bed and fan off. The faucet's existing cooling is a
part-specific response to reported short-layer sagging. That evidence makes a
local comparison more useful than applying the supplier's fan choice everywhere.
[Bambu's versioned scarf definitions](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintConfig.cpp)
provide the contour choice and the retained default controls.

This is a replication and screening plate. It preserves actual surfaces, tilt,
material and support settings, but cropping and six objects change layer return
times, support topology and heat exposure. Fan response and cooling of neighboring
objects are unmeasured. A coupon improvement selects a candidate for a complete
faucet trial; it does not by itself replace the accepted shipping process.
Temperature, support gap, retraction, speeds and flow are not varied here.

Compare the supported shoulder edges before and after cooling and cleanup, retaining
the specimen letters. Distinguish an upward-curled model edge from sagging bridge
strands, detached model layers and retained support. A useful replication has A's
lifting in the same type of supported region. If A stays clean, this plate cannot
establish a cure for the full faucet. For D–F compare the rear seam and nearby
surface above the fine-layer transition, including any broader scarf depression.
Timelapse can show when a visible change appears, but cannot establish contact
forces or bond strength.

Generate with `tools/cad-venv/bin/python prepare.py`; use the saved slice command,
then `python3 finish.py`. Preparation, native review, exact archive hashes and
the one foreground launch receipt are recorded beside this file. No automatic
resume or scheduled monitoring is authorized.

Mark2 accepted this exact plate as task **1327799013** at **6:45:52 pm CDT
October 10, 2026**. The native duration projects completion at **2:13:55 am CDT
October 11**. [Launch receipt](launch.json) records the archive, options and
fresh readings of both printers. These are start and forecast records; no
physical coupon result is recorded yet.
