# Hopper funnel

The removable dishwasher-safe silicone funnel that seats in the Zone C top-wall
opening, right of the display and flush to the front. Pour a full 440 mL
SodaStream flavor bottle into it in one go; lift it out by hand for the
dishwasher and to reach the valve trays beneath.
Zone framing: [`../README.md`](/hardware/printed-parts/zone-c/README.md).

## Shape

A static part in its own frame — origin at the collar-rectangle center, z = 0
the brim underside — placed by the enclosure assembly
(`_contents.FUNNEL_CX/CY`, brim on the box top). The drain is defined in this
frame and rides the part. Top to bottom:

- **Brim.** A flat flange overhanging the collar [7 mm](HOPPER_HOLD) all around,
  resting on the enclosure top surface — this reach is the whole of what holds
  the funnel out of the box, so it is sized to be caught and lifted by hand at
  the rim, not merely to cover the cut edge. The collar sits
  [10 mm](HOPPER_MARGIN) inside the top-wall frame on every side, so the flange
  lands mid-margin with a full overhang's width of wall still outboard of it,
  and the part reads square in its opening from above.
- **Chute.** A tall straight rectangular section — vertical walls, no slope —
  [27.65 mm](HOPPER_CHUTE) from the brim top down to where the ramp starts. Its top
  press-fits the 3 mm top wall; the rest hangs down into the box as a straight
  rectangular drop.
- **Ramp + spout.** Below the chute a shallow ramp narrows to a round
  [6.35 mm](HOPPER_SPOUT_ID) spout (1/4", matching the manifold tubing), the
  spout offset off the collar center (`neck_dx`); the enclosure placement's
  `FUNNEL_ROT` picks which side of the box it descends (the rectangular collar
  seats either way). The whole floor is the ramp — every surface of it falls
  toward the spout, no flat anywhere, so the basin drains dry. A straight
  spout tube carries the exit down to the drain, which sits **above** V-B's
  up-facing inlet collet — segment 4 is the gravity drain and the air-purge
  path, so the tube from drain to V-B must only fall. The pack is measured on
  the real solids by the enclosure scorecard. Total drop
  [53 mm](HOPPER_DROP) below the brim.

Capacity to the brim is [807 mL](HOPPER_CAP) — a full 440 mL bottle dumped,
not metered.

The enclosure cuts its top-wall opening from this collar at the funnel's
placement (`enclosure.py` `_hopper_hole`), asserting the top-wall frame
accommodates it — funnel and hole cannot drift apart.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
→ `hopper-funnel.step`. Seated in the enclosure view by
[`../../enclosure/enclosure-assembly/enclosure_assembly.py`](/hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
