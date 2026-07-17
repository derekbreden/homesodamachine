# Hopper funnel

The removable dishwasher-safe silicone funnel that drops into the Zone C
top-wall opening right of the display — flush with the enclosure top, nothing
standing above it but its flat brim. Pour a full 440 mL SodaStream flavor
bottle into it in one go; lift it out by hand for the dishwasher and to reach
the pumps beneath. Same idiom as the Lite edition's funnel
([/pie-in-the-sky/lite/printed-parts/funnel/](/pie-in-the-sky/lite/printed-parts/funnel/README.md)).
Zone framing: [`../README.md`](/hardware/printed-parts/zone-c/README.md).

## Shape

One rectangular basin sunk through the opening — from above, a clean flush
rectangle. Built top to bottom in enclosure world coordinates so it drops
straight into the opening:

- **Brim.** A flat [3 mm](HOPPER_BRIM) flange overhanging the opening all
  around, resting on the enclosure top surface.
- **Chute.** A straight [148 × 111 mm](HOPPER_BASIN) rectangular basin —
  vertical walls, no slope — press-fitting the 3 mm top wall and dropping to
  a floor just above the tallest content under the opening (read live).
  Capacity to the brim is [576 mL](HOPPER_CAPACITY) — a full 440 mL bottle
  with margin, dumped, not metered.
- **Floor.** Dishes gently from every side into the drain mouth so the
  basin drains dry.
- **Mouth + spout.** Under the floor a short taper necks the drain mouth to
  a round [6.35 mm](HOPPER_SPOUT_ID) spout (1/4", matching the pump tubing)
  in the clear column between the two pumps — a stub, not a chute — where
  the V-B pickup tube lands. Total drop [74 mm](HOPPER_DROP) below the
  brim.

The chute footprint is taken from the enclosure's opening rectangle
(`enclosure.py` `_hopper_hole`), so the funnel and hole always match.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
→ `hopper-funnel.step`. Seated in the enclosure view by
[`../../enclosure/enclosure-assembly/enclosure_assembly.py`](/hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
