# Hopper funnel

The removable dishwasher-safe silicone basin that fills the Zone C top-wall
opening right of the display. Pour a full 440 mL SodaStream flavor bottle
into it in one go; lift it out by hand for the dishwasher and to reach the
pumps beneath. Zone framing:
[`../README.md`](/hardware/printed-parts/zone-c/README.md).

## Shape

One rectangular basin — the whole opening is the pour target. Built top to
bottom in enclosure world coordinates so it drops straight into the opening:

- **Stepped tub.** The lower body, [148 × 111 mm](HOPPER_BASIN), drops
  through the opening (press-fitting the 3 mm top wall) and floors just
  above the power deck; at the top surface the walls step outward to a
  [160 × 121 mm](HOPPER_CURB) curb whose underside rests on the wall frame
  around the opening — the step carries the load, and the curb stands
  [18 mm](HOPPER_PROUD) proud as the pour rim. Capacity to the rim is
  [707 mL](HOPPER_CAPACITY) — a full 440 mL bottle with margin, dumped, not
  metered.
- **Floor.** Slopes from every side into the throat mouth so the basin
  drains dry.
- **Throat.** A rectangular slot dropping straight down the clear column
  between the two pumps.
- **Ramp + spout.** Below the throat a short ramp necks to a round
  [6.35 mm](HOPPER_SPOUT_ID) spout (1/4", matching the pump tubing), ending
  just above the tallest content under the throat (read live), where the
  V-B pickup tube meets it. Total drop [151 mm](HOPPER_DROP) below the rim.

The body footprint is taken from the enclosure's opening rectangle
(`enclosure.py` `_hopper_hole`), so the funnel and hole always match.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
→ `hopper-funnel.step`. Seated in the enclosure view by
[`../../enclosure/enclosure-assembly/enclosure_assembly.py`](/hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
