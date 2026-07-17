# Hopper funnel

The removable dishwasher-safe silicone funnel that seats in the Zone C top-wall
opening, right of the display and flush to the front. Pour a full 440 mL
SodaStream flavor bottle into it in one go; lift it out by hand for the
dishwasher and to reach the pumps beneath. Same idiom as the Lite edition's
funnel ([/pie-in-the-sky/lite/printed-parts/funnel/](/pie-in-the-sky/lite/printed-parts/funnel/README.md)).
Zone framing: [`../README.md`](/hardware/printed-parts/zone-c/README.md).

## Shape

A wide funnel, built top to bottom in enclosure world coordinates so it drops
straight into the opening:

- **Brim.** A flat flange overhanging the opening 3 mm all around, resting on the
  enclosure top surface.
- **Chute.** A tall straight rectangular section — vertical walls, no slope —
  [30 mm](HOPPER_CHUTE) from the brim top down to where the ramp starts. Its top
  press-fits the 3 mm top wall; the rest hangs down into the reserve as a straight
  rectangular drop.
- **Ramp + spout.** Below the chute a shallow ramp narrows to a round
  [6.35 mm](HOPPER_SPOUT_ID) spout (1/4", matching the pump tubing), the spout
  offset in −X off the opening center toward the clear column between the two
  pumps. The whole floor is the ramp — every surface of it falls toward the
  spout, no flat anywhere, so the basin drains dry. The ramp necks down to just
  above the tallest content under the mouth (read live), then a short straight
  spout tube carries the exit down to skim it, where the V-B delivery tube
  picks the pour up. Total drop [46 mm](HOPPER_DROP) below the brim.

Capacity to the brim is [499 mL](HOPPER_CAP) — a full 440 mL bottle dumped,
not metered. The enclosure reserves the basin's depth over the pump towers
(`enclosure.py` `hopper_min_depth`).

The chute footprint is taken from the enclosure's opening rectangle
(`enclosure.py` `_hopper_hole`), so the funnel and hole always match.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
→ `hopper-funnel.step`. Seated in the enclosure view by
[`../../enclosure/enclosure-assembly/enclosure_assembly.py`](/hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
