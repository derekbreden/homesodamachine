# Funnel

The removable dishwasher-safe silicone funnel seats in the top-wall opening,
directly behind the display facet. It holds [600 mL](FUNNEL_CAP), including a
full 440 mL SodaStream flavor bottle. Its brim, collar and ramp are 6 mm thick;
the outlet has a [4.5 mm](FUNNEL_SPOUT_WALL) radial wall.
Zone framing: [`../README.md`](/hardware/printed-parts/zone-c/README.md).

## Shape

The origin is the collar center at the brim underside. The enclosure seats this
plane at Z349, with the brim flush with its Z355 roof. The rounded outlines share
concentric corner arcs: the 153 × 139 mm mouth has R14 corners, the 165 × 151 mm
collar has R20 corners, and the 179 × 165 mm brim has R27 corners.

The brim is 6 mm thick and overhangs the collar by 7 mm. It bears on 6 mm of
printed enclosure stock, filled outward to the walls. The collar and sloping
floor have 6 mm silicone walls; floor thickness is measured normal to its surface.
The straight chute is [23.4859 mm](FUNNEL_CHUTE) deep from the brim's upper face.
The floor falls continuously toward the outlet, centered fore–aft and offset
1.85 mm in X. The brim underside is [49.9352 mm](FUNNEL_DROP_UNDER) above
the drain's mating face.

A 6.25 mm transition below the inner floor joins the straight outlet. The outlet
has a [6.35 mm](FUNNEL_SPOUT_ID) bore, [4.5 mm](FUNNEL_SPOUT_WALL) radial wall and
[12 mm](FUNNEL_LAND) clamp land. The worm clamp closes the silicone onto the 1/4-inch
LLDPE drain stub between two 2 mm shoulders. The stub and clamp remain attached
when the funnel is removed for washing.

## Wall reading

[`wall-review.json`](wall-review.json) measures the complete inner ramp against
the exterior boundary and samples surface-normal thickness in both the source
and exported STEP. The ramp's minimum normal wall is 6 mm; the collar and brim
are 6 mm thick, and the clamp land has a 4.5 mm radial wall.

```sh
tools/cad-venv/bin/python tools/funnel-mold-print/review_funnel_wall.py --grid 9 --output hardware/printed-parts/zone-c/funnel/wall-review.json
```

## Lifting it out

The funnel's drain stub seats in the JG PP0308E union elbow below it
([`reference/elbow-connector`](/hardware/reference/elbow-connector/README.md)).
The elbow turns `fluid-4` forward; the tube then passes west of the source valves
and returns to V-B. The funnel stays captive until this
elbow's collet releases the stub.

The 1/4" jaw of the printed [`collet press`](../../collet-press/) drops over
the stub and presses the collet sleeve evenly. The funnel lifts away with its
stub and clamp attached; `fluid-4` stays on the machine.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/funnel.py`
→ `funnel.step`. Seated in the machine by
[`../../../manifold-layout/enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/zone-c/funnel/funnel.py`
