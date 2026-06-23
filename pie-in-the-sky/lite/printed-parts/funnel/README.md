# Funnel (hopper)

The removable hopper you pour SodaStream concentrate into. It drains to **V-B**
on the [source-select tray](/hardware/printed-parts/valve-manifold/source-select-tray/)
— fluid topology [segment 4](/hardware/topology/fluid-topology.md),
"Hopper funnel bottom → V-B-I". A **pour buffer** holding ≈ [527 mL](HOPPER_CAP)
to the brim — generous enough to take a full pour at once while the pump draws it
on to a bag.

The Kitchen edition's [hopper funnel](/hardware/printed-parts/zone-c/hopper-funnel/)
turned a quarter-turn: a **narrow-X, deep-Y slot** to the **right of the display**,
cut by the enclosure via `_hopper_hole`, so the collar always matches the hole.

## Shape

Built top to bottom in enclosure world coordinates so it drops straight into the
opening:

- **Brim.** A flat flange overhanging the opening 3 mm all around, resting on the
  enclosure top surface.
- **Chute.** A tall straight rectangular section — vertical walls, no slope —
  [48 mm](HOPPER_CHUTE) from the brim top down to where the ramp starts. Its top
  press-fits the [3 mm](WALL) top wall; the rest hangs down as a straight
  rectangular drop holding the bulk of the buffer.
- **Ramp + spout.** Below the chute a **short** ramp necks to a centered round
  [6.35 mm](SPOUT_ID) spout (1/4", matching the pump tubing). The spout exits
  **high** — its height set by the chute + ramp, well above the short trays
  beneath the mouth — so the funnel sits in the top of the box rather than
  plunging a deep cone toward the floor; a flexible tube then carries the pour
  the rest of the way down to V-B (the spout does not land on V-B directly, same
  as the Kitchen hopper). Total drop [89 mm](HOPPER_DROP) below the brim.

The chute footprint is taken from the enclosure's opening rectangle
(`enclosure.py` `_hopper_hole`), so the funnel and hole always match.

## Regenerate

`tools/cad-venv/bin/python pie-in-the-sky/lite/printed-parts/funnel/funnel.py`
→ `funnel.step`. Seated in the enclosure view by
[`../../enclosure-assembly/enclosure_assembly.py`](/pie-in-the-sky/lite/enclosure-assembly/enclosure_assembly.py).

## Sources
[value](NAME) texts are updated by:
- `/pie-in-the-sky/lite/printed-parts/funnel/funnel.py`
