# Anchor cap

The printed half pipe that closes a 1/4" tube anchor in place of its zip tie. One ships on every
machine, closing the carbonated-water line's crossing under back-top's ceiling (`carb-1`).
Which anchors take a cap is stated in `enclosure_assembly.TUBE_ANCHOR_CLOSURES`; the rib it
closes is described in the [enclosure's tube anchors](../enclosure/README.md#tube-anchors).

## Geometry

The cap is one section extruded [14 mm](CAP_LEN) along the tube, [15.95 mm](CAP_WIDTH) across
and [18.27 mm](CAP_HEIGHT) from its round back to its wing tips. Its bore is the rib's own
[6.65 mm](SEAT_D) seat, so the tube lies in one round pipe once the cap is home, and the bore's
two edges are eased so a slightly offset tube is guided in rather than pinched.

Below the tube's axis plane the cap is solid from the bore out to its round back. Two
[1.5 mm](WING) wings rise up the rib's flanks with [0.15 mm](WING_AIR) of air to each. Each wing
carries a lip that reaches [1.2 mm](ENGAGE) off it, the faucet display cover's engagement: a flat
retention face under it, a short straight tip, and a [30°](LEAD_IN) ramp that spreads the wing as
the lip rides onto the rib's chamfered foot.

A [0.65 mm](CAVITY) gap separates the half pipe from each wing for [36°](CAVITY_DEG) round the
pipe and ends in a full round. The wing bends from that round end, over [12.3 mm](WING_FLEX) to
the middle of its lip. Fixed there and deflected by the lip's engagement, a wing reaches
[1.76%](WING_STRAIN) peak strain on a beam estimate; the same estimate gives
[1.77%](FAUCET_COVER_STRAIN) for the accepted faucet display cover's wings going on, read off
that cover's published STEP (1.35 mm walls, 17.25 mm from the bezel's inner face to the middle
of the lip, 2.6 mm of spread). The estimate compares the two shapes; it predicts neither force
nor life.

Pressed home, the shoulders meet the rib's flat lips and each of the cap's lips has
[0.4 mm](BEARING_PLAY) to go before it bears on its window's bearing face. Under the ceiling the
cap hangs on those faces: its own weight and the tube's take up the play.

One cap is [1.57 cm³](CAP_VOLUME) of solid; [bom.md](/hardware/ledger/bom.md) §7 bills the
filament.

## Printing

PET-GF15 on the 0.4 mm nozzle, standing on its end as exported: the section on the bed and the
tube's axis vertical. Every layer is the whole section, so nothing overhangs and no supports are
needed, and each wing bends along its own extrusion lines. Print it solid — at least six walls
and 100% infill, the recipe the collet press and the pump-dock keepers use — with a 0.20 mm
first layer and 0.24 mm layers. Keep the 0.65 mm gaps open: they are what lets the wings
spring.

## Assembly

The cap goes on while back-top is populated inverted on the bench, ceiling down, so the rib's
half pipe opens upward ([enclosure mechanical](/hardware/assembly/enclosure-mechanical.md),
[internal plumbing](/hardware/assembly/internal-plumbing.md)):

1. Lay the tube in the rib's half pipe. The rib holds the bare tube; the line's insulation
   stops at the rib's two ends.
2. Set the cap over it, shoulders toward the rib and a wing either side.
3. Press it straight down until both lips click into their windows and the shoulders sit on the
   rib's lips.
4. Tug the tube and the cap; neither comes away.

To take a cap off, twist a thin flat blade in the gap between the half pipe and one wing at the
cap's end until that lip clears its window, then do the same on the other side.

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/anchor-cap/anchor_cap.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/anchor-cap/anchor_cap.py selftest
```

The first writes `anchor-cap.step`, `anchor-cap.stl` and the viewer payload, and the figures
above. The self-test checks one valid solid standing on its end, one section along its whole
length, a gap wide enough to print open, and the wings' strain against the faucet cover's.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/anchor-cap/anchor_cap.py`
