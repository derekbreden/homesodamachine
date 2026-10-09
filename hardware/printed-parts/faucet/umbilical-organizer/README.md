# Umbilical organizer

One floating PET-GF puck keeps the three quarter-inch tubes and 4 mm drain in
formation below the faucet's plate, washer and nut working area. Each tube can
be deliberately adjusted while holding the puck in the other hand. The signal
ribbon passes through a separate loose passage. The puck threads over free
tube and cable ends during factory assembly and sits inside the upper braid.

The selected fit is the **L / rightmost / loose** article from the
[three-sample Mark2 print](../../../../future/umbilical-organizer-exploration/fit-trial-mark2/README.md).
Derek accepted it as “pretty close to perfect, or at least good enough for now.”
The [physical acceptance record](physical-acceptance.json) binds that report to
the exact printed mesh, native archive and settings. It establishes the reported
fit; installed mounting access, quantified sliding force and endurance are not
separately reported.

| Feature | Dimension |
|---|---|
| Round stock | Ø32 × 10 mm |
| Soda and both flavor bores | Ø6.65 mm |
| Drain bore | Ø4.20 mm |
| Loose signal passage | Ø5 mm |
| Tube entrance chamfers, both ends | 0.4 mm × 45° |
| Smooth tube contact length | 9.2 mm |
| Cable entrance chamfers, both ends | 0.2 mm × 45° |
| Outer rim chamfers | 0.6 mm × 45° |

The body is one cylinder with five straight passages and entrance/rim chamfers.
It has no teeth, fasteners, liner, opening seam or identification embossing.
The canonical print frame has the stock centred at XY=0 and the bottom face at
Z=0. [`umbilical_organizer.py`](umbilical_organizer.py) defines its tube axes in
the faucet frame and supplies the placement transform.

## Installation

One organizer ships per umbilical, on both faucet styles and finishes. The
[`faucet assembly`](../../../faucet-layout/faucet_assembly.py) places its top
at Z=−88 mm and bottom at Z=−98 mm. That puts its top 50.476 mm below the
steel plate for the illustrated 30 mm slab, or 42.476 mm below the plate for a
38 mm slab. These are modeled gaps, not a reported washer/nut access result.
The tubes are straight and parallel through the organizer. The White faucet's
upper flavor union begins 7 mm below the puck; its second union sits end to end
below that. Foam on the blue tube begins below the lower gathering bends.
The [manual integration check](integration-check.json) records the accepted STL
binding, passage alignment and nominal cable/braid clearances in this assembly.

Thread the organizer before joining the White faucet's flavor unions, before
clamping the blue tube into the retained Westbrass, and before crimping the
signal plug. Set the tube positions with two hands, leaving the mounting stack's
working area clear. The organizer floats with the bundle; it is not fixed to
the counter or enclosure. Keep room between gripping stations for the tubes to
settle as the bundle bends.

## Print

PET-GF, flat bottom face on the textured plate with all passages vertical.
The accepted Mark2 article used its fixed left hardened 0.4 mm nozzle,
0.20 mm first layer, 0.24 mm layers above it, two walls and 15% grid infill.
No support or brim was emitted. Nozzle temperatures were 265 °C first / 280 °C
subsequent, bed 80 °C, profile flow ratio 0.9555, XY hole/contour compensation
zero and elephant-foot compensation 0.15 mm. Mark2's requested +0.04 mm trim
is included in its native textured-plate `G29.1 Z0.02` after `G29.1 Z0`.
That trim is specific to Mark2. The physical material is PET-GF; its saved
printer metadata reports PET-CF/GFT01.

The [accepted native job and bead review](../../../../future/umbilical-organizer-exploration/fit-trial-mark2/README.md)
retain all three original samples. Production STEP/STL/viewer payloads are
generated from the selected L dimensions. The production STL is byte-identical
to the accepted trial's loose STL. Regenerate manually with
`tools/cad-venv/bin/python hardware/printed-parts/faucet/umbilical-organizer/umbilical_organizer.py`.
