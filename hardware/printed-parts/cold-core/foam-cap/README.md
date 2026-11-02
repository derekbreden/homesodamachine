# Cold-core top lid and bottom cap

The PET-GF casing has three pieces: the taller shell, a top equipment lid and an
open-topped bottom cap. The complete casing is 253.4 mm high in the appliance frame.
The shell's internal vessel and reservoir datums are independent of its upper rim.

`foam_cap.py` derives the current equipment and casing datums for `foam_cap.rs`,
which writes the four pieces' STEP, full-precision model and print mesh. The
generator cuts their viewer payloads from the print meshes. Its `--native` option
retains the construction surfaces used by native assembly and installation readers.

## Top lid

The uniform 7.4 mm plate spans 282.4 × 180.4 mm. Its flat underside is its print face.
In the appliance it occupies Z246.0–253.4 mm; the shell rim is at Z245.85 mm,
leaving the 0.15 mm printed-face fit allowance. The lid installs with its specified
180° half-turn. Ten recessed M5 × 100 screws engage RX-M5×9.5 inserts in the shell.

The PCB, pump bearing, V-B socket, junction wells and tube/cable retainers belong to
the lid. The PCB uses four Ø10 mm posts, 3.6 mm standoffs and M3 × 8 screws.
Its Ø4 × 7.4 mm blind pilots receive RX-M3×5.7 inserts, retain 3.6 mm backing,
and leave 1 mm beyond the seated screw tip. Install these inserts before mounting
the board. Complete the ten M5 clamps before fitting equipment over their driver paths.

Fluid and sensor passages retain their installed axes. Quarter-inch tubes pass through
Ø7.5 mm lid openings. Both independent 4 mm reservoir air tubes use Ø5.2 mm openings.
Install the straight fill, draw and air tubes through their reservoir grips before
the open-body foam pour. Cured foam locates their short dry spans below the lid;
the dip sections inside the closed reservoirs remain free. The shell mouth remains clear for loading the vessels.

The separate Reservoir B fill guide is the accepted R14, 2 mm-wall D-back bend holder,
with no straight outlet leg. Its lower exit clears the reservoir cap. Thread the
continuous tube through it before connecting the reservoir grip. The guide stays
with the tube and cured foam; a plain clearance window in the lid clears its crown.
The fore-facing entry and reservoir endpoint retain their installed positions.
The guide prints flat on its D back, with its teardrop channel roof self-supporting.
Seal the dry lid/window boundary with 3M 425 after potting, leaving all tube lumens open.

The bare G Ganen pump seats in one broad block carved into the lid and uses a
separate upper clip. Its complete rubber feet and legs are removed. Both fixed
rails bear on fitted floors from native X16.75–77.75. The joined stock stops
both rails at each end. One straight 49.62 mm channel is recessed 2.5 mm below
the lid face, leaving a 4.9 mm floor. A single fore plane clears both head lugs. The two rail bearing strips
are 3.419 mm and 3.329 mm wide.
One continuous 54.5 mm filled box half-pipe spans native X20–74.5, with a
6.2 mm crown and one straight east shoulder for ASSE clearance. Independent
1.3 mm spring leaves carry 2.6 mm flat catches. Its continuous side pockets
span X19.75–74.75; the seat leaves
3 mm of solid axial stock at each end. The clip closes after seating the bare
motor and prints on one axial end with a constant outside profile.
The [pump installation](../../../reference/g-ganen-pump/installation/README.md)
owns the bearing datums, axial stops and removable sliders.

V-B uses the shared V69 upright socket. Four DC/sensor WAGO wells occupy the board-facing
back of its wall. Their levers open west. The wall and wells retain ordinary 3 mm stock.
The PCB and plumbing poses belong to the [above-core arrangement](../../../manifold-layout/above-core.md).

The V-A feed seats in the lid's C2 clip at world (16.608, 207.300, 268.970) mm.
The Reservoir A fore fill/draw clips remain at X50.5/64.0, Y209.75, Z258.5 mm,
with Ø6.35 seats, 2.40 mm spring walls and 8 mm spans. The aft paired seat at Y390 mm
uses one four-inch narrow tie. The front-going J1/J2 cable bank has ordinary 3 mm
outer/shared walls and 16 mm span. These features print above the lid's flat bed face.

## Bottom cap

`foam-cap-bottom` is one open-topped part. Its outside face is the flat print face
and the plane the core stands on. Its 2 mm floor, 2.38 mm casing walls and local M5
head pads enclose a 17.85 mm central foam depth beneath the shell's fixed floor.
There is no printed ceiling in the cap. In the appliance its upper rim is Z19.85 mm,
0.15 mm below the shell's Z20 mm base.

Print the cap on its outside floor. Its ten outward-open M5 head pockets use
Normal(auto)/Snug supports with no extra initial support-foot flange. This
part-specific choice keeps the complete native model/support bead envelope
21.02 mm inside the Mark2 bed; automatic tree feet exceed the required 20 mm
border on this wide part. All ten support bodies stay under the head-pocket
ceilings. Remove them outward before fitting hardware or foil. Other casing
pieces retain their own support settings. The native reading establishes
contact locations and removal access; physical release remains article-specific.

Four Ø30 mm pour ports form a 2 × 2 pattern at native X±75/Y±40 mm.
Two Ø6 mm holes vent air. Allocate the measured foam charge across the four local
pour points so each quarter is filled directly. Foam appearing at a vent is not the
fill criterion. Follow the foam's mixing, working-time and cure instructions.

Bolt the cap to the empty shell and mask its dry perimeter and open-sided head
pockets before pouring. Invert the empty casing onto its upper rim, pour through the
underside, let it cure and trim the ports flush. Apply the exterior foil patches and
seam band after cure. Return the casing upright before loading the vessels.
The cap stays fastened to the shell throughout the body assembly.

## M5 closure hardware

Each face has ten screws: three on each short end and two on each aft long flank.
The shell-native axes are X±135.4 at Y−60/0/+60 mm, and X45/110 at Y±84.4 mm.
The top lid carries the inverse pattern in its pre-install half-turn frame.

The selected fully threaded M5 × 100 screws have Ø8.5 × 5 mm heads and 4 mm hex sockets.
The printed passages are Ø5.2 and the outward-open head pockets are Ø9.
RX-M5×9.5 inserts seat in Ø6.4 × 10.5 mm pilots, with 2.6 mm radial host stock.
Continuous Ø11.6 hosts join the casing wall and retain 3.2 mm around the Ø5.2
screw-tail bores. Bottom-facing blind ends and pilot transitions narrow by
0.5 mm per millimetre of build rise, beyond their full cylindrical clearances.

The upper screws project 97.6 mm beyond their insert mouths, the lower screws 85.4 mm.
Each blind tail passage has 2.5 mm nominal tip air. All twenty clamp screws are the
same stock as the enclosure's four seam screws.

At all ten lid axes, a straight Ø4.8 × 80 mm driver envelope clears the printed
lid's integral features above the lid face. The [kernel print and driver review](kernel-print-review.json)
records the Rust meshes, saved recipes, emitted paths and driver envelopes.
The [native M5 driver reading](m5-lid-driver-review.json) retains the native reference.

The [local solid regions](fore-snap-print-regions.json) fill the M5 head bearings,
PCB insert posts and their plate/floor roots at 100%. The same record carries
the fore C2 root and shell M5 hosts. Regenerate it from the current exported
pieces before preparing their native print projects.

Assembly order and foam work: [cold-core assembly](../../../assembly/cold-core.md).
