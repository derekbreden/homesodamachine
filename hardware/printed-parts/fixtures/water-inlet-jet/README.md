# Water-inlet jet drilling fixture

Two printed jaws hold the candidate 9.5 mm stainless rod vertically while the
WEN 4208T drills the jet passage. The fixed jaw has a broad base and a solid
floor under the rod; the loose jaw slides toward it. Four owned C-clamps
close the jaws and hold the base to the drill table. The spindle supplies
alignment; there is no printed drill guide.

**Status: CAD checked, physical trial untested.** The printed grip, real clamp
clearance and the press's setup must be demonstrated on a scrap handling
blank before making caps. This is shop tooling, separate from the machine
assembly. The fabrication procedure is
[`water-inlet-jet.md`](/hardware/assembly/water-inlet-jet.md).

| File | Use |
|---|---|
| [`water_inlet_jet_fixture.py`](water_inlet_jet_fixture.py) | Generator, dimensions and geometric checks |
| [`water-inlet-jet-fixture-fixed.stl`](water-inlet-jet-fixture-fixed.stl) | Fixed jaw and base, print orientation |
| [`water-inlet-jet-fixture-loose.stl`](water-inlet-jet-fixture-loose.stl) | Loose jaw, print orientation |
| [`water-inlet-jet-fixture-fixed.step`](water-inlet-jet-fixture-fixed.step), [`water-inlet-jet-fixture-loose.step`](water-inlet-jet-fixture-loose.step) | Exact, material-coloured solids |

## Print and inspect

Print both parts in the owned PET-GF15, flat on their exported Z=0 faces.
The intended starting profile is 0.2 mm layers, six walls, six top/bottom
layers and 50% infill. The jaws have vertical, open grooves and need no
support. This profile and the grip have not had a physical trial.

The base is [120 × 90 × 8 mm](JET_FIXTURE_BASE); the jaws support
[30 mm](JET_FIXTURE_GRIP) of rod. Their nominal grooves are
[9.8 mm](JET_FIXTURE_GROOVE) in diameter, with a
[1 mm](JET_FIXTURE_GAP) open split. That extra diameter permits the loose
jaw to close before the two flat faces touch. Nominal 9.5 mm stock takes up
0.3 mm of travel; the remaining split is a visible check that the faces have
not bottomed out. Real stock and print dimensions decide the actual grip.

Remove loose print whiskers. Check that both bottoms lie flat, the loose
jaw slides squarely and the rod reaches the solid base floor. Do not assume
a print that looks round grips the rod. A tight, crooked or bottomed-out
pair requires a recorded groove adjustment and a new print; do not force
the stock or drill with inadequate grip.

## Set up on the drill table

1. With the saw, cut a handling blank approximately
   [50 mm](JET_FIXTURE_BLANK) long from the 400 mm rod; 50–60 mm gives a
   manageable first setup. Deburr its ends. Do not stand the complete
   400 mm rod under the drill press.
2. Put the fixed base flat on the owned plywood/MDF backer on the drill
   table. The fixed jaw sits behind the rod; the loose jaw sits in front,
   on the same base. Seat the rod on the solid floor between the grooves.
3. Close the two jaws using **two C-clamps with horizontal screw axes**,
   one on each side of the rod. Their pads bear on the flat outer jaw
   faces, approximately [±20 mm](JET_FIXTURE_JAW_CLAMP_X) from the rod
   axis. Point the C-frames outward, away from the spindle. Tighten
   evenly until the rod cannot turn, rock or lift by a firm hand check;
   the split must remain visible. Do not crush the printed jaws.
4. Use the **other two C-clamps vertically** on the base's left and right
   flanges, approximately [±46 mm](JET_FIXTURE_BASE_CLAMP_X) from the rod
   axis, clamping the base and backer to the drill table. They must reach
   a solid table edge; neither a table slot nor a loose backer is the
   lower bearing surface. The actual clamp pads and frames are unmeasured:
   adjust their positions on the flat lands and verify that all four can
   be tightened without colliding.
5. Fit the drill with power off. Align its tip to the rod axis **after
   tightening the jaws**; their closure shifts the rod slightly. Move the
   whole fixture for alignment, then secure both table clamps. Lower the
   stopped quill through the intended stroke and turn the chuck by hand
   to check clearance and runout. Check the drill approaches the rod
   squarely from front and side. The chuck, quill and drill must clear all
   four clamps throughout the stroke.
6. Make the short trial hole using the procedure's 1100 rpm starting
   setting. Stop at any rod movement, jaw opening, fixture movement,
   rubbing or drill wander. Recheck grip with the spindle stopped. A
   successful grip trial is recorded before caps are made.

The C-clamps close the jaws mechanically and resist fixture rotation; the
solid floor takes downward drilling thrust. Printed material still has to
demonstrate adequate grip in this exact setup. Keep the fixture cool and
wipe away cutting fluid; replace it if softened, cracked or distorted.
It is a drilling fixture and does not enter the laser welding setup.

Remove the rod from the fixture for each bandsaw cutoff. Before the next
hole, clear chips from the floor, reseat the stock and realign the drill.
Stop using a handling blank when less than
[40 mm](JET_FIXTURE_MIN_BLANK) remains; the rod must project at least
10 mm above the jaws, and the actual chuck clearance can require more.
Keep the short remainder for other coupons.

## Generate and check

From the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/fixtures/water-inlet-jet/water_inlet_jet_fixture.py selftest
tools/cad-venv/bin/python hardware/printed-parts/fixtures/water-inlet-jet/water_inlet_jet_fixture.py
```

The checks establish valid individual solids, print orientation, open-jaw
clearance, candidate rod contact before the faces bottom out, clamp-pad
layout allowances and a drill path clear of the plastic. They do not model
the real C-clamp frames, friction, clamp force, print tolerance or the WEN
chuck. The nominal rod diameter is shared with the candidate jet CAD; the
fixture is not an input to enclosure or cold-core geometry.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/fixtures/water-inlet-jet/water_inlet_jet_fixture.py`
