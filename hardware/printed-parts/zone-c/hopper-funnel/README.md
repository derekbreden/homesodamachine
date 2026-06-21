# Hopper funnel

The removable dishwasher-safe silicone funnel that seats in the Zone C top-wall
opening, right of the display and flush to the front. Pour SodaStream concentrate
into it; lift it out by hand for the dishwasher and to reach the pump cartridge
beneath. Zone framing: [`../README.md`](/hardware/printed-parts/zone-c/README.md).

## Shape

A shallow wide funnel, built top to bottom in enclosure world coordinates so it
drops straight into the opening:

- **Brim.** A flat flange overhanging the opening 3 mm all around, resting on the
  enclosure top surface.
- **Collar.** A straight rectangular section — vertical walls, no slope — that
  press-fits into the opening and fills the 3 mm top wall. The brim + collar give
  6 mm of straight rectangular wall pressing the opening sides.
- **Ramp + spout.** Below the collar the bore ramps from the rectangular mouth
  down to a round [6.35 mm](HOPPER_SPOUT_ID) spout (1/4", matching the pump
  tubing), centered on the opening. The ramp necks one mm above the bib-gate tray
  (read live), then a straight spout tube carries the exit down the clear column.
  Total drop [64 mm](HOPPER_DROP) below the brim.

The collar footprint is taken from the enclosure's opening rectangle
(`enclosure.py` `_hopper_hole`), so the funnel and hole always match.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
→ `hopper-funnel.step`. Seated in the enclosure view by
[`../../enclosure/enclosure-assembly/enclosure_assembly.py`](/hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
