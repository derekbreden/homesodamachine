# Cold-core top lid and bottom cap

The PET-GF casing has three pieces: the taller shell, a top equipment lid and an
open-topped bottom cap. The complete casing is 253.4 mm high in the appliance frame.
The shell's internal vessel and reservoir datums are independent of its upper rim.

[`numbers/`](numbers/lib.rs) holds the cap's numbers, and [`foam_cap.rs`](foam_cap.rs),
the build step, writes the top lid and bottom cap STEP, full-precision model, print mesh and
viewer payload from them, and `foam-cap.numbers.json` for the whole machine. Assembly
and installation readers use the saved full-precision models.

## Top lid

The uniform 7.4 mm plate spans 282.4 × 180.4 mm. Its flat underside is its print face.
In the appliance it occupies Z246.0–253.4 mm; the shell rim is at Z245.85 mm,
leaving the 0.15 mm printed-face fit allowance. The lid installs with its specified
180° half-turn. Ten recessed M5 × 100 screws engage RX-M5×9.5 inserts in the shell.

The PCB, pump bearing, V-B socket, junction wells and tube/cable retainers belong to
the lid. The PCB uses integral posts with regular M3 inserts and the short screws
seated directly on its mounting pads. Its placement and the lid's flat underside
follow the shared deck dimensions.
Its Ø4 × 7.4 mm blind pilots receive RX-M3×5.7 inserts, retain 3.6 mm backing,
and leave 1 mm beyond the seated screw tip. Install these inserts before mounting
the board. Complete the ten M5 clamps before fitting equipment over their driver paths.

Fluid and sensor passages retain their installed axes. Quarter-inch tubes pass through
Ø7.5 mm lid openings. Both independent 4 mm reservoir air tubes use Ø5.2 mm openings.
Install the straight fill, draw and air tubes through their reservoir grips before
the open-body foam pour. Cured foam locates their short dry spans below the lid;
the dip sections inside the closed reservoirs remain free. The shell mouth remains clear for loading the vessels.

The separate Reservoir B fill guide has a flush rectangular top and a lower
exit over the reservoir's TPU grip. Locate the guide with a removable tube
offcut and keep its approach clear during the pour. Once the lid seats around
the guide, feed the final tube lengthwise through the fore entry and into the
TPU grip. Seal the seating seam with 3M 425, leaving the tube lumen open.
[Cold-core assembly](../../../assembly/cold-core.md#6-open-body-foam-pour)

The guide and its rectangular top grow from the flat print face, with a
self-supporting teardrop channel roof.

The bare G Ganen pump seats in one broad block carved into the lid and uses a
separate upper clip. Its complete rubber feet and legs are removed. Both fixed
rails bear on fitted floors from native X16.75–77.75. The joined stock stops
both rails at each end. One straight 49.62 mm channel is recessed 2.5 mm below
the lid face, leaving a 4.9 mm floor. A single fore plane clears both head lugs. The two rail bearing strips
are 3.419 mm and 3.329 mm wide.
One continuous 54.5 mm filled box half-pipe spans native X20–74.5, with a
6.2 mm crown and one straight east shoulder for ASSE clearance. Independent
2.0 mm spring leaves have 1.5 mm inside root blends. Each full-length hook bears on
a matching 45° ledge. Its lead-in ends in a 0.90 mm flat crest raised 0.40 mm
toward the lid. The straight pockets extend outboard for release. The east pocket
opens into Reservoir A's air passage beside the aft corner.

From the nominal installed position, the arch reaches the rigid motor at
0.454 mm of downward travel. The crest stops at 0.590 mm. With the bare motor
already resting on its rail floors, the rigid arch still has 0.168 mm of
vertical travel to the barrel when the crests meet the pocket floors. The
benchtop pair preserves both rail seats, end stops and the lid's print face.
[Loaded fit and release measurements](../../../print-tests/pump-seated-snaps/parts/fit-check.json)
The [pump installation](../../../reference/g-ganen-pump/installation/README.md)
owns the bearing datums, axial stops and removable sliders.

V-B uses the shared V69 upright socket. Four DC/sensor WAGO wells occupy the board-facing
back of its wall. Their levers open west. The wall and wells retain ordinary 3 mm stock.
The PCB and plumbing poses belong to the [above-core arrangement](../../../manifold-layout/above-core.md).

The [top-lid print recipe](../../enclosure/trial-preparation/pieces.json) uses the PET-GF
tree support process. Remove the
supports through the open receiver mouths and the underside inlet groove before assembly.

The V-B return presses into a curved C2 seat that follows the tube from its
valve-side tangent to its fore-going tangent. A round-bottomed radial slot
splits both lips into independently opening wings. The floor under the tube is
continuous. Derek seated the black return tube in the crop of the complete
bend and its lid footing. “Fit is good.” [Mark 1 fit record and photos](https://github.com/derekbreden/homesodamachine/blob/6f1ace30ded2ef1eec928d2c04f39be1b1b485dd/hardware/print-tests/vb-return-clip/prints/2026-11-21-mark1/physical-result/physical-result.json).

The V-A feed presses into an upward-opening C2 seat beside the PCB. The seat
follows the end of the feed's bend and continues along the straight tube toward
Y-A. A radial slot separates the wings on each side. The floor supports the
tube across the slot, and the board-side end leaves clearance to the PCB.

The white pump-discharge tube snaps down into a short seat between the check
valve and the water-in passage. Its two free jaws follow the crest of the bend.
The foot and jaws print upright on the lid.

The Reservoir A fore fill/draw clips remain at X50.5/64.0, Y209.75, Z258.5 mm,
with Ø6.35 seats, 2.40 mm spring walls and 8 mm spans. The aft fill/draw clips are the
same seats, each turned along its line's last level turn before the reservoir. The draw
line's stands on the taller root, and the fill line's is filled square against that root
up to its jaw's top, so the pair is one body. That jaw of the fill clip is square along its
whole length and joined to the root over the aft part of it, so it bends little. The clip's
free jaw takes the fit of back-top's east-wall fill seat, which has one fixed jaw: a thinner
jaw, standing further out from the stiff one
([`reservoir_a::aft`](numbers/reservoir_a.rs)). The pair's [hand fit](https://github.com/derekbreden/homesodamachine/blob/5a5c589208a470c654f443981a4b9bc1802563cb/hardware/print-tests/reservoir-a-aft-snaps/prints/2026-11-20-mark1/physical-result/physical-result.json)
is accepted on a printed crop of the lid. The front-going J1/J2 cable bank has ordinary 3 mm
outer/shared walls and 16 mm span. These features print above the lid's flat bed face.
The tube clips' jaws stand side by side at the same print height, with both roots
on the lid. Their openings face away from the lid, so they do not use the
back-top's lower-jaw corbel or upper-jaw support strips.

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

The rear nameplate's two upper insert hosts dip into the lid's rear edge, and each takes
a plain recess there ([`nameplate_clearance.rs`](../nameplate_clearance.rs)). The recess
beside the rear middle screw opens into that screw's head pocket: one pocket on the
head's floor, in as far as the screw's axis.

At all ten lid axes, a straight Ø4.8 × 80 mm driver envelope clears the printed
lid's integral features above the lid face. The [kernel print and driver review](kernel-print-review.json)
records the Rust meshes, saved recipes, emitted paths and driver envelopes.
The [native M5 driver reading](m5-lid-driver-review.json) retains the native reference.

The [local solid regions](fore-snap-print-regions.json) give the V-A feed, V-B return and pump-discharge clips,
the reservoir A clip pairs, the casing screw hosts and head bearings, and the PCB
insert posts solid infill through their roots. Before preparing a print project,
regenerate the regions from the cap dimensions and the exported pieces with
[`foam-cap-print-regions`](print_regions.rs).

Assembly order and foam work: [cold-core assembly](../../../assembly/cold-core.md).

## Receiver service

With the lid on the bench, dress the pump plumbing and leads aside, spread the
exposed leaves until both hooks clear their ledges and lift the cap straight up.
The pocket floors give both raised crests room to swing out with the leaves.

The [complete snap set](https://github.com/derekbreden/homesodamachine/blob/ed4ebc3cf65805689fe1421af6710770936107ec/hardware/print-tests/receiver-tool-access/README.md)
records the earlier receiver trials. The [independent pump pair](../../../print-tests/pump-seated-snaps/README.md)
fits the complete bare pump for checking cover movement and release.
