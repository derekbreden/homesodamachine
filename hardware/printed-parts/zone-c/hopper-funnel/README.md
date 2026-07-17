# Hopper funnel

The removable dishwasher-safe silicone catch bowl + funnel that stands on the
Zone C top surface, right of the display, draining through the top-wall throat.
Pour SodaStream concentrate into it; lift it out by hand for the dishwasher and
to reach the pumps beneath. Zone framing:
[`../README.md`](/hardware/printed-parts/zone-c/README.md).

## Shape

The through-hole in the top wall is boxed in on every side — the display
housing left, the electronics stack right, the Y-seam lip band behind — so the
pour target lives above the surface: a wide bowl spanning the whole top zone
right of the display, riding the solid wall over the electronics stack and
back across the Y seam (it lifts off before the pieces do). Built top to
bottom in enclosure world coordinates so it drops straight into the opening:

- **Catch bowl.** A [150 × 159 mm](HOPPER_BOWL) shallow rectangular basin
  standing [22 mm](HOPPER_BOWL_H) proud of the enclosure top, flat underside
  resting on the top wall, vertical rim walls, its floor sloping from every
  side into the throat so it drains dry.
- **Throat.** A straight rectangular section — vertical walls, no slope —
  [27 mm](HOPPER_CHUTE) from the enclosure top surface down to where the ramp
  starts. Its top press-fits the 3 mm top wall; the rest hangs down into the
  reserve as a straight rectangular drop.
- **Ramp + spout.** Below the throat a shallow ramp narrows to a round
  [6.35 mm](HOPPER_SPOUT_ID) spout (1/4", matching the pump tubing), the spout
  offset in +X off the throat center toward the clear column beside the pumps.
  The ramp necks down to just above the tallest content under the mouth (read
  live), then a short straight spout tube carries the exit down to skim it,
  where the delivery tube picks it up. Total drop [65 mm](HOPPER_DROP) below
  the bowl rim.

The throat footprint is taken from the enclosure's opening rectangle
(`enclosure.py` `_hopper_hole`), so the funnel and hole always match.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
→ `hopper-funnel.step`. Seated in the enclosure view by
[`../../enclosure/enclosure-assembly/enclosure_assembly.py`](/hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
