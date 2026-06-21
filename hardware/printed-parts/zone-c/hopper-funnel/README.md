# Hopper funnel

The removable dishwasher-safe silicone funnel that seats in the Zone C top-wall
opening, right of the display and flush to the front. Pour SodaStream concentrate
into it; lift it out by hand for the dishwasher and to reach the pump cartridge
beneath. Zone framing: [`../README.md`](/hardware/printed-parts/zone-c/README.md).

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
  offset in −X off the opening center. The ramp necks one mm above the bib-gate
  tray (read live), then a short straight spout tube carries the exit on down.
  Total drop [76 mm](HOPPER_DROP) below the brim.

The chute footprint is taken from the enclosure's opening rectangle
(`enclosure.py` `_hopper_hole`), so the funnel and hole always match.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
→ `hopper-funnel.step`. Seated in the enclosure view by
[`../../enclosure/enclosure-assembly/enclosure_assembly.py`](/hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
