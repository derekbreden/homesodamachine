# Umbilical organizer

One floating PET-GF puck keeps the three quarter-inch tubes and 4 mm drain in
formation below the faucet's plate, washer and nut working area. Each tube can
be deliberately adjusted while holding the puck in the other hand. The signal
ribbon passes flat through a separate loose slot. The puck threads over free
tube and cable ends during factory assembly and sits inside the upper braid.

The [three-increment Mark2 fit comparison](../../../../future/umbilical-organizer-exploration/diameter-increments-mark2/physical-result.json)
selects A's Ø6.65 mm bores for the three quarter-inch tubes and B's Ø4.40 mm
bore for the received 4 mm drain tube. The [physical acceptance record](physical-acceptance.json) binds
these feature-level selections to the exact printed samples, job and settings.
The combined production puck is unprinted; the selected bore fits have physical
evidence. Quantified sliding force, endurance and complete installed mounting
access are unmeasured.

| Feature | Dimension |
|---|---|
| Round stock | Ø[32 mm](ORGANIZER_OD) × [10 mm](ORGANIZER_LENGTH) |
| Soda and both flavor bores | Ø[6.65 mm](ORGANIZER_TUBE_BORE) |
| Drain bore | Ø[4.40 mm](ORGANIZER_DRAIN_BORE) |
| Loose flat signal slot | [5.4 × 1.8 mm](ORGANIZER_CABLE_SLOT) |
| Tube entrance chamfers, both ends | [0.4 mm](ORGANIZER_ENTRY) × 45° |
| Smooth tube contact length | [9.2 mm](ORGANIZER_CONTACT) |
| Cable entrance chamfers, both ends | [0.2 mm](ORGANIZER_CABLE_ENTRY) × 45° |
| Outer rim chamfers | [0.6 mm](ORGANIZER_RIM_EASE) × 45° |

The body is one cylinder with four straight round bores, one straight capsule
slot and entrance/rim chamfers. The slot is wide along faucet X and holds the
[measured 4.6 × 1.18 mm ribbon](../../../reference/bntechgo-signal-ribbon/physical-observations.json)
flat, with 0.8 mm width and 0.62 mm thickness clearance. Its rounded ends leave
about 0.13 mm minimum clearance to the measured rectangular envelope. These
are modeled clearances; the slot's printed threading fit is unmeasured.
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
The rear passages follow the plate's F1–D–F2 row, with the flat ribbon behind D.
The soda bore stays on the shank axis. Relative to the mounting row, each flavor
bore is 1.2 mm farther outward and D is 1.2 mm forward; the signal slot is directly
under its mounting axis. These small offsets leave separate bore walls and
entrance chamfers. All lines are straight and parallel through the puck.

The flavor R30 and drain R25 returns to the union layout begin 3 mm below the
organizer's bottom. The White faucet's upper union begins 7 mm below the
completed flavor returns; its second union sits end to end below that. Foam on
the blue tube begins below the lower gathering bends.
The [manual integration check](integration-check.json) records the accepted bore
profiles, passage alignment and nominal cable/braid clearances in this assembly.

Thread the organizer before joining the White faucet's flavor unions, before
clamping the blue tube into the retained Westbrass, and before crimping the
signal plug. Set the tube positions with two hands, leaving the mounting stack's
working area clear. Face the soda bore toward the shank and the signal slot
behind the F1–D–F2 row, matching the plate. Keep the ribbon flat through the slot
and retain the straight tube section through the puck before bending toward
the unions. The organizer floats with the bundle; it is not fixed to
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

The [A/B/C native job and bead review](../../../../future/umbilical-organizer-exploration/diameter-increments-mark2/README.md)
retain the three printed samples: A has Ø6.65/4.30/5.00 mm quarter-inch/drain/signal
bores, B Ø6.75/4.40/5.10 mm and C Ø6.85/4.50/5.20 mm. Production combines
A's beverage bore dimensions with B's drain bore dimensions. Its round stock,
tube contact length, tube chamfers and upright orientation match the trials.
The production axes follow the mounting row and its ribbon passage is a flat
slot. The fit evidence applies to the selected round-bore profiles, not to the
unprinted organizer layout or signal slot.
The separate frozen [Ø4.30 mm drain-fit archive](../../../../future/umbilical-organizer-exploration/drain-fit-mark2/README.md)
is an unsubmitted trial, outside the current production selection.
Regenerate the production geometry manually with
`tools/cad-venv/bin/python hardware/printed-parts/faucet/umbilical-organizer/umbilical_organizer.py`.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/umbilical-organizer/umbilical_organizer.py`
