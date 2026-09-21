# Carrier spring pusher

One reusable flat pusher loads both springs during the complete enclosure
assembly. It bears on the end of the spring; it does not enter its unknown ID.
The Ø6.3 mm tip and 10 × 3 mm tongue have a constant 2 mm thickness. The
complete print envelope is 13.15 × 6.3 × 2 mm.

The [STL](carrier-spring-pusher.stl) and [STEP](carrier-spring-pusher.step)
lie flat on XY, with the broad face on the bed at Z0 and +Z up. No rotation
or support is required. Every layer has the same footprint. At a uniform
0.20 mm layer height, the body occupies ten layers; the actual slice records
its layer heights and confirms the entire tongue and head remain connected.

Work with the front-top loose, four bare tees seated at release, and both
valve rows absent. Load and seat the left carrier half first.

1. Put the spring in the moving cup. Hold its length at 12.15 mm with the
   flat tip; point the tongue inboard.
2. Carry the half and held spring through the rear opening, lower it,
   shift outward to the staging position, slide fore and seat it outward.
   The carrier's [assembly sequence](../../enclosure/tee-carrier/README.md#assembly)
   specifies those distances.
3. With the half at its aft stop, withdraw the pusher 15.435 mm inboard and
   lift it through the outer tee well. The spring expands into both cups.
4. Turn the same pusher 180° about the spring axis and repeat for the right
   half. Remove it before installing the valves and tubes.

The [native route record](native-sequence-check.json) covers nineteen
installation, removal and reuse sweeps against the frozen full wall, bare
tees and complete carrier. The right-half path clears the released left
spring. There is 1.70 mm between the tool's fore face and the fixed cup at
withdrawal, and 0.30 mm to the upper tray along the lift lane. A current
generated-wall check accompanies the complete enclosure release.

Tool durability, spring compression force, finger/plier handling and actual
assembly effort are observations for the assembled physical trial.

Generate the part with:

```sh
tools/cad-venv/bin/python hardware/printed-parts/fixtures/carrier-spring-pusher/carrier_spring_pusher.py
```
