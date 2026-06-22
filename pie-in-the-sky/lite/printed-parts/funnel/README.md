# Funnel (hopper)

The removable hopper you pour SodaStream concentrate into. It drains to **V-B**
on the [source-select tray](/hardware/printed-parts/valve-manifold/source-select-tray/)
— fluid topology [segment 4](/hardware/topology/fluid-topology.md),
"Hopper funnel bottom → V-B-I". A **pour-through guide**, not a batch reservoir:
what you pour gets pumped straight on to a bag.

The same idiom as the Kitchen edition's
[hopper funnel](/hardware/printed-parts/zone-c/hopper-funnel/): it seats in the
top-wall opening to the **right of the display**, cut by the enclosure via
`_hopper_hole`, so the collar always matches the hole.

## Shape

Built top to bottom in enclosure world coordinates so it drops straight into the
opening:

- **Brim.** A flat flange overhanging the opening 3 mm all around, resting on the
  enclosure top surface.
- **Chute.** A tall straight rectangular section — vertical walls, no slope —
  [30 mm](HOPPER_CHUTE) from the brim top down to where the ramp starts. Its top
  press-fits the [3 mm](WALL) top wall; the rest hangs down into the reserve as a
  straight rectangular drop.
- **Ramp + spout.** Below the chute a shallow ramp narrows to a round
  [6.35 mm](SPOUT_ID) spout (1/4", matching the pump tubing), offset toward the
  source-select side. The spout exits into the open air above the tallest
  content below the mouth (read live — the front bag-circuit tray), with room
  left below for a tube/barb fitting; a short flexible tube then carries the pour
  on to V-B (the spout does not land on V-B directly, same as the Kitchen
  hopper). Total drop [78 mm](HOPPER_DROP) below the brim; capacity to the brim
  rim ≈ [280 mL](HOPPER_CAP).

The chute footprint is taken from the enclosure's opening rectangle
(`enclosure.py` `_hopper_hole`), so the funnel and hole always match.

## Regenerate

`tools/cad-venv/bin/python pie-in-the-sky/lite/printed-parts/funnel/funnel.py`
→ `funnel.step`. Seated in the enclosure view by
[`../../enclosure-assembly/enclosure_assembly.py`](/pie-in-the-sky/lite/enclosure-assembly/enclosure_assembly.py).

## Sources
[value](NAME) texts are updated by:
- `/pie-in-the-sky/lite/printed-parts/funnel/funnel.py`
