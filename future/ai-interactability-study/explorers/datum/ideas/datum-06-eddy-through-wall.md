# datum-06-eddy-through-wall: seat depth from outside, through the wall

Scene: `scenes/datum-06-eddy-through-wall/index.html`. Depth: rough (a toy model that says where a bench test is worth doing). Origin: swarm. **Software commands a scan and observes; nothing sees the corner.**

## Picture it

A small coil slides up the outside of the tube at the weld station, a millimetre or two off the wall. Above the rim the signal is zero. Below the rim, in the pocket, it sees the 1.65 mm wall alone. Over the plate it sees the wall *and the plate seated behind it*, a bump. Below the plate the wall is alone again. The rim step and the top of the bump are a ruler: their spacing is this tube's seat depth, read through the wall, with no line of sight and no contact.

## The proposal

Cameras cannot see the corner; a low-frequency coil can feel the metal behind the wall. The scene plots skin depth in 316L against frequency, the fraction of the field left at the plate after the wall, and the resulting bump, and simulates a scan whose response is a rim step plus a plate bump, blurred by the coil, with noise. Software fits a template of that response to the scan and reports the seat depth. The coil could ride on a small slide, or on the crown's vertical stage (datum-03), or sit fixed at the corner's height as a presence flag for the plate.

## What carries the loads, what establishes position, what is free or restrained

Nothing carries anything new: the coil is light and sits off the outer wall. Position is established by the rim edge and the plate edge, both read through the wall. The coil height is the only driven axis (proposed).

## What software could command, observe, and what stays manual

- **Command:** the coil's height (a proposed scan axis or the crown's stage).
- **Observe:** the response against height; rim and plate edges; the seat depth from their spacing.
- **Blind:** radial position, the dot, the melt. **Manual:** placing the coil on the outside at the station azimuth; a one-time bench calibration of the blur.

## What was tried to break it

Numbers from `calc/eddy_skin.py` (`calc/eddy_skin.out`); resistivity 74 micro-ohm.cm is a handbook value, not measured on this tube; the response is a toy.

1. **The wall is a conductor in the way.** *Assumption:* a metal wall blocks the field. *What the numbers say:* skin depth is 4.3 mm at 10 kHz, 2.5 mm at 30 kHz, 1.37 mm at 100 kHz, 0.43 mm at 1 MHz; it equals the wall at 69 kHz. The plate's bump is 0.47 of full scale at 10 kHz, 0.27 at 30 kHz, 0.09 at 100 kHz, 0.015 at 300 kHz. So the plate is visible at tens of kilohertz and gone by a few hundred. *Uncertain:* the wall and plate are separate parts with a 0.13 mm slip gap, and the thin-conductor formula is crude.
2. **A simple edge search fails.** *Assumption:* the rim and the plate face show up as two edges to find. *What the calc says:* with a 6 mm coil the rim's blurred step swamps the small plate bump; a steepest-edge search is more than 2 mm off in 82% of simulated scans.
3. **A template fit works, if the template is right.** *Change:* fit the whole response (rim step plus bump). *What the calc says:* 0.13 mm RMS when the template's blur is 15% wrong; bias -0.12 mm at 15%, -0.30 at 30%, -0.90 at 50%. Larger coils and higher frequencies degrade it (the toy at 100 kHz, 6 mm coil: 0.41 mm RMS; at 300 kHz it fails).
4. **The fit is limited by calibration, not noise.** *Repair:* calibrate on a tube of known seat depth (a depth gauge); the blur is repeatable for one coil and lift-off. *Uncertain:* whether one calibration holds across tubes, wall thickness and temperature.
5. **The weld heats exactly where the coil looks.** *Repair:* scan once in setup, or look ahead of the pool. *Uncertain:* heat on the coil, and temperature drift of the resistivity, which moves the skin depth.

## Branches and combinations

- **With the crown** (datum-03): the crown's stage scans the coil; the coil gives the seat depth the rim reference lacks, so the plunger is optional.
- **With the datum chain** (datum-01): it removes the seat-depth link without touching the pocket.
- **With the collar** (datum-05): supplies the per-tube seat depth the tags cannot know.

## Unresolved problems and questions for Derek

- A bench test decides everything here: one coil board, a scrap tube-and-plate, a depth gauge. The scene is a set of questions for that test, not a prediction.
- Whether cold-worked 316L near the plate's weld is slightly magnetic and confuses the reading [unknown].
- Does the collar or crown leave a clear strip of outer wall at the station azimuth?

## Assumptions

- Wall 0.065 in = 1.65 mm and plate 0.250 in = 6.35 mm [repo]; nominal recess 6.35 mm [repo]; true seat depth is a slider (default 6.85 mm). Resistivity 74 micro-ohm.cm and relative permeability 1: illustrative. Blur set by coil diameter and lift-off, noise 0.4%: illustrative.

## Sourcing pointers

`sourcing/datum.md`: Seeed Grove LDC1612 module (about $16 at Digi-Key by search snippet, stock unchecked, not Prime on Amazon), and the commodity LJ12A3-4-Z/BX inductive switch (Prime confirmed, $6.99, 386 ratings) as the crudest possible probe. Neither is checked against 316L or against a wall step.

## Scene id

`datum-06-eddy-through-wall`.
