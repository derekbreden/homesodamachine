# Funnel

The removable dishwasher-safe silicone funnel seats in the top-wall opening,
directly behind the display facet. It holds [606 mL](FUNNEL_CAP), including a
full 440 mL SodaStream flavor bottle. Its brim, collar and ramp are 6 mm thick;
the outlet has a [4.5 mm](FUNNEL_SPOUT_WALL) radial wall.
Zone framing: [`../README.md`](/hardware/printed-parts/zone-c/README.md).

## Shape

A static part in its own frame: origin at the collar-rectangle center, z = 0
at the brim underside. The machine places it at
[`enclosure_assembly.funnel_centre`](/hardware/manifold-layout/enclosure_assembly.py),
with its brim resting on the enclosure top. Top to bottom:

- **Brim.** A 6 mm thick flange overhangs the collar
  [7 mm](FUNNEL_HOLD) all around. The collar sits [10 mm](FUNNEL_MARGIN) inside
  the top-wall frame. The flange rests on that frame and provides the lifting rim.
- **Chute.** A 159 × 159 mm rectangular collar surrounds a 147 × 147 mm bore:
  6 mm vertical walls. The straight section extends [21.31 mm](FUNNEL_CHUTE)
  from the brim top to the inner ramp's start. Its upper portion seats in the
  enclosure's 3 mm top wall.
- **Ramp.** The sloping floor narrows to a round [6.35 mm](FUNNEL_SPOUT_ID)
  bore, offset 1.85 mm in X and centred in Y. Its vertical fall is set by a
  15° slope along the long X half-run. The silicone is 6 mm thick measured
  perpendicular to the inner ramp surface. Round joins connect the ramp faces,
  collar and throat; the throat is locally thicker.
- **Throat.** The inner ramp ends at the outlet bore. A 5.3 mm vertical
  transition below this point accommodates the rounded exterior before the
  straight clamp land begins.
- **Clamp land.** The outlet has [12 mm](FUNNEL_LAND) of straight round tube,
  with a [4.5 mm](FUNNEL_SPOUT_WALL) radial wall and an outside diameter of
  [15.35 mm](FUNNEL_SPOUT_OD). A worm clamp's band sits between two 2 mm
  shoulders. A 1/4" LLDPE stub runs through the land and the clamp closes the
  silicone onto it. The factory joint washes with the funnel
  ([`reference/funnel-drain-stub`](/hardware/reference/funnel-drain-stub/), card
  SA-06). The machine's push-fit collet grips the stub. The distance from brim
  top to outlet is [58 mm](FUNNEL_DROP).

The enclosure cuts its top-wall opening from this collar at the funnel's
placement (`enclosure.py` `_funnel_hole`), asserting the top-wall frame accommodates it.
The enclosure-assembly scorecard measures the surrounding solids and drain route.

## Wall reading

[`wall-review.json`](wall-review.json) records the exact minimum distance from
all five complete inner ramp faces to the filled exterior boundary. This check
includes every point on the faces, their boundaries and the rounded throat
transitions, establishing a 6 mm minimum ramp wall throughout. The source
silicone solid and exported STEP have zero geometric volume difference.

The report also checks 501 locations in both source and STEP: 453 surface-normal
measurements across the ramp, 12 collar measurements, 12 brim measurements and
24 clamp-land measurements. The collar and brim are 6 mm thick; the cylindrical
clamp land has a [4.5 mm](FUNNEL_SPOUT_WALL) radial wall.

```sh
tools/cad-venv/bin/python tools/funnel-mold-print/review_funnel_wall.py --grid 9 --output hardware/printed-parts/zone-c/funnel/wall-review.json
```

## Lifting it out

The funnel's drain stub seats in the JG PP0308E union elbow below it
([`reference/elbow-connector`](/hardware/reference/elbow-connector/README.md)).
The elbow turns `fluid-4` aft toward V-B. The funnel stays captive until this
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

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/zone-c/funnel/funnel.py`
