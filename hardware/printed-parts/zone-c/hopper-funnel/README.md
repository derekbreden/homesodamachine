# Hopper funnel

The removable dishwasher-safe silicone funnel that seats in the top-wall
opening, centred on the machine directly behind the display facet. Pour a full 440 mL
SodaStream flavor bottle into it in one go; lift it out by hand for the
dishwasher and to reach the valve trays beneath.
Zone framing: [`../README.md`](/hardware/printed-parts/zone-c/README.md).

## Shape

A static part in its own frame — origin at the collar-rectangle center, z = 0
the brim underside — placed by the machine
([`enclosure_assembly.funnel_centre`](/hardware/manifold-layout/enclosure_assembly.py), brim on
the box top). The drain is defined in this frame and rides the part. Top to
bottom:

- **Brim.** A flat flange overhanging the collar [7 mm](HOPPER_HOLD) all around,
  resting on the enclosure top surface — this reach is the whole of what holds
  the funnel out of the box, so it is sized to be caught and lifted by hand at
  the rim, not merely to cover the cut edge. The collar sits
  [10 mm](HOPPER_MARGIN) inside the top-wall frame on every side, so the flange
  lands mid-margin with a full overhang's width of wall still outboard of it,
  and the part reads square in its opening from above.
- **Chute.** A tall straight rectangular section — vertical walls, no slope —
  [21.31 mm](HOPPER_CHUTE) from the brim top down to where the ramp starts. Its top
  press-fits the 3 mm top wall; the rest hangs down into the box as a straight
  rectangular drop.
- **Ramp + spout.** Below the chute a shallow ramp narrows to a round
  [6.35 mm](HOPPER_SPOUT_ID) spout (1/4", matching the manifold tubing), the
  spout offset off the collar center in X (`neck_dx` — the spout stands over the
  slot it drains into) and on the collar's own centre in Y, so the basin is
  symmetric about its drain front to back; the placement's
  `enclosure_assembly.FUNNEL_ROT` picks which side of the box it descends (the
  rectangular collar seats either way). The whole floor is the ramp — every
  surface of it falls toward the spout, no flat anywhere, so the basin drains
  dry. One rise serves every run, so the grade is struck on the long X half-run
  and every other line on the floor lands steeper. A straight spout tube carries the exit down to the drain, and the
  elbow under it turns the fall aft one leg lower — which still stands
  **above** V-B's inlet collet, since `fluid-4` is the gravity drain and the
  air-purge path and the run from that mouth to V-B must only fall. The pack is
  measured on the real solids by the enclosure-assembly scorecard. Total drop
  [53 mm](HOPPER_DROP) below the brim.
- **The clamp land.** That spout tube is [12 mm](HOPPER_LAND) of straight round,
  which is a worm clamp's band and a shoulder of silicone either side of it. A
  1/4" LLDPE stub runs up the whole of it and the band closes the silicone onto
  the stub — the joint is made at the factory and washes with the basin
  ([`reference/hopper-drain-stub`](/hardware/reference/hopper-drain-stub/), card
  SA-06). The stub is what the machine's push-fit collet grips, since a collet
  grips tube and this spout is silicone. Every millimetre of this land lowers the
  drain exactly as a millimetre of chute does, so the two come out of one budget.

Capacity to the brim is [662 mL](HOPPER_CAP) — a full 440 mL bottle dumped,
not metered.

The enclosure cuts its top-wall opening from this collar at the funnel's
placement (`enclosure.py` `_hopper_hole`), asserting the top-wall frame
accommodates it — funnel and hole cannot drift apart.

## Lifting it out

The basin is captive until its collet lets go. `fluid-4` starts at a JG PP0308E
union ELBOW under the spout
([`reference/elbow-connector`](/hardware/reference/elbow-connector/README.md)):
its +Z leg stands coaxial with the spout and holds the drain stub, its +Y leg
hands the run aft. Turning the fall inside the fitting is what keeps the joint
out of the folded deck's own storey, where the anchor tees' barrels crown one
storey under the top wall. Releasing it is a push on the sleeve's own annular
face, and the push has to land **square**: a collet
grips by wedging its teeth against the tube, so a sleeve pressed on one side
bites harder rather than letting go. That face stands below the top wall at the
foot of the [53 mm](HOPPER_DROP) drop, and it carries concentrate.

**The user releases it with the 1/4" jaw of a JG collet quick-connect tool.**
The jaw drops over the stub and bears on the whole annulus at once, so the push
is square by construction — which a thumb on a millimetre and a half of land,
reached blind and sticky, is not. The basin then lifts away with its stub and clamp still on it,
and `fluid-4` stays on the machine.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
→ `hopper-funnel.step`. Seated in the machine by
[`../../../manifold-layout/enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py`
