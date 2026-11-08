# Enclosure

What the pieces have actually been printed in, and at what settings:
[print-log.md](print-log.md).

A PET-GF15 box. is the section a piece starts from and every exterior
wall carries at least, each taken INWARD so the silhouette
and `interior_x` both stand still: a bottom piece's three lipped sides get
 as the lip's own skin carried to the slab, front-top's ±X
flanks are, back-top's are and its
+Y wall 9 mm. The floor is the one section taken OUTWARD:
 of slab under both bottom pieces, with the stated height struck to
its underside, so it stands in the silhouette and the cavity's floor plane — the
one the pack sets its bodies on — does not move. **Split into four printable pieces** — front/back × bottom/top, every piece inside the H2C bed. Each
column's top SLIDES onto its bottom on hooked rails; the two halves telescope and four M5
screws, two at each Y-seam corner, close the whole box.
It measures, and **width, height and both Y walls
are all stated bounds**. `_dims` measures the pack against each one and enters the
reading in `BOUNDS`; the box comes back at its stated size regardless, so a pack
that overruns one gets a wall drawn through it, a red row naming by how much, and a
clash in `pack-closes` at the body that overran.

- **Width** is `appliance_width`, struck symmetric about x = 0. What the pack owes
  it is clearance: a body on the floor slab spans the interior wall to wall, so a
  floor body stands one `side_band_inset` in from the wall **where it meets one of the
  seam's corner stacks in depth and in height** (`seam_bosses`), leaving every knuckle its
  full section. The lower stacks stand from the slab to the Z seam; the
  upper ones from their floor to the ceiling. Outside those footprints the band is air. The cold
  core is the widest of the floor bodies, yawed a quarter turn
  (`enclosure_assembly.FOAM_YAW`) so what crosses the machine is its 181 mm short face
  instead of its 283 mm long one. The yaw is the thin machine.
- **Height** is a stated, floor slab's underside to the
  top wall's outer face. The contents do not lift it; they have to fit under it.

**Depth** is stated at both walls: the front plane `FRONT_PLANE_Y`
([`numbers/shell.rs`](numbers/shell.rs)) and the rear plane `REAR_PLANE_Y`
([`interface/lib.rs`](interface/lib.rs)). The contents do not move either wall.
The compressor bay stands on the floor at the front and the cold core sits
behind it, front face mated flush against the compressor bay's aft plane.

Both columns take their bottom↔top seam on **one stated plane**, `enclosure.z_seam`,
inside the band both of a column's pieces print in (`_bed_band`): the piece under the
seam runs the floor slab to the lip rim, the piece over it the seam to the top wall,
and all four stand on the bed. The seam line runs level round the box, and the four
pieces meet at a four-way corner on each side wall.

Neither column leaves the plane an **open band** — a range with `z_joint_clear` of air
on either side of it, read off the pack, where no body straddles the seam and neither
does whatever holds one. The compressor bay and the flavour deck run the front
column solid; the cold core stands from the floor slab and the whole service bay
stands on its lid in the back. So the seam runs **through** both columns, on the lane
each lip needs — the cavity's own one-`wall` skin (`_lip_band`, the same shape `_z_lip`
fuses onto a piece), held open at every height by the standoffs the pack is packed to,
one wall off the front and +Y walls and one `side_band_inset` off the sides. Being the skin
and not a box, it **wraps every column standing in a vertical**, and that wrap stands a
whole `column_round` inboard of any wall segment — so a body clear of all four walls
can still be in the lip's way there.
`_lip_denied` measures that lane per column, each seam answering for its own half of
the box (`z-seam-front-lane`, `z-seam-back-lane`) — the ring read one rail deeper down
the straight runs, where the groove, arm and head ride. The cold core spans the
seam in both columns.

The plane stands where the seam's own machinery fits the pack: the seam ring's foot
over the condenser's fin crown, and the rim under the forward valve tray's
wall roots (`z-seam-under-deck` — a plate roots on a wall only above the rim).
Each root follows its outermost valve row. The staggered aft tray's lower band and
its foot run below, inset on the lip's own face. The ring's front segment across
the flat span is the pump mount's (`_front_flat_lip_drop`): its underside loading
opening and retainer occupy that run, so the flat front carries no lip there.

The enclosure program, [`enclosure.rs`](enclosure.rs), cuts the four printable pieces
(`enclosure-front-bottom`, `enclosure-front-top`, `enclosure-back-bottom`,
`enclosure-back-top`), the underside pump retainer `enclosure-pump-retainer` and the pump
tube-setting jig, then `enclosure.step`: the pieces as separate solids in assembled position,
seams intact, with the pump dock's tees and elbows (mirrors `faucet/faucet-shell`).

## Seams + corner stacks

Three seams. Front↔back: the front pieces' rear lip telescopes into the back pieces. That
**proud** lip is **3-sided** — both side walls and the ceiling. A proud
tongue is the wall continued one `wall` *into* the cavity, and on those faces the
cavity is free; the floor's is not — the cold core rides on it — so a proud floor
tongue would drive straight into the core. The floor runs on anyway, as a
**full-thickness tongue inside the slab** (`_floor_tongue`): the front floor runs aft
on the print bed and ends square; the back floor starts square one running fit aft of
it. Both ends keep the slab's whole section, the assembled top stays flat under the
core, and both printed bearing faces remain support-free. The handholds remove the slab
at both flanks; the tongue continues across the middle under the cold core. Its square
ends stand on the plane each handhold's inner wall ends on, the wall at its full 3 mm
section, so the floor and both inner walls close on one pair of plumb faces with one
running fit between them. The joint is square because the slab cannot lap: it is 5.65 mm
thick, and a lap inside it with one running fit between its members cannot keep
both members at the nominal 3 mm section. The corner knuckle stacks and their M5 rods align
the halves.

Each ±X corner of that seam is a **stack of knuckles**: blocks of one piece standing in the
other's overlap, alternating up the corner, with two vertical M5 screws through them
(`_y_stacks`). A front knuckle roots fore of the seam in its own
flank and runs aft one running fit inside the back piece's skin; a back knuckle grows out of
that skin and on into the thickened flank. Every knuckle stands in the
overlap and the side band, its screw mid-overlap in Y.

- **The lower stack** is three knuckles inside the bottom pieces: back-bottom's
  knuckle over the handhold, front-bottom's, and back-bottom's under the Z seam. An
  drives up from the handhold ceiling at Z,
  its head seated at Z60.8 in the lower back knuckle, through front-bottom's knuckle into a ruthex RX-M5x9.5
  pressed into the top of the upper back knuckle, flush with the Z seam; its tip stands just
  past the insert's open top. Back-bottom holds the screw at both ends and front-bottom's
  knuckle hangs on it between them, so a pull that opens the seam meets the screw at two
  faces, both bearing on its fully threaded shaft. Nothing of either
  bottom stands above the Z seam.
- **The upper stack**, from the head downward, is front-top's roof head block,
  back-top's middle block and front-top's lower insert block. The
  enters from above and ends in a closed pocket below the insert.
  Front-top's lower block rises from Z to its insert mouth at
  Z; the head block's underside crosses the screw axis at
  Z. Both front-top blocks join its wall and capture
  back-top between them. The middle block retains its running fit; tightening the screw
  seats its head in front-top rather than directly clamping back-top axially.
  Front-top's −X insert block has a 5.1 mm inboard-aft chamfer (`y_stack_upper_chamfer`).
  The head block keeps its square corner, cut only by the funnel's actual clearance.
  Both 4 mm flavor tubes pass inboard of the stack on R25 detours before their rear rises.
  The head block carries the complete rounded outer flank at its station. Its underside
  retains full stock beneath the funnel clearance, and its fore root continues into the lower block.
  The head opening continues aft into the funnel opening without a narrow collar between them.
  Behind that block's running end, back-top's middle-knuckle wall root continues into its roof.

The knuckle faces follow their pieces' print orientations: front-bottom's knuckle rises
aft off its handhold roof, back-bottom's upper knuckle rises inboard off its skin and
front-top's insert block rises inboard off its lip band. Front-top's head block has an
aft-rising underside matched by back-top's middle block; back-top prints roof-down.
Cavity recipes use branching trees with accessible removal lanes.
Front-bottom's fore knuckle root stands directly on its handhold roof.
The slopes run across the slide or close as the front half slides aft, and a top
that rises toward a free face levels off one wall short of it. Every face between knuckles
keeps a running fit, measured square to the face.

The screws pass through printed holes, the selected
[M5 sample fit](https://github.com/derekbreden/homesodamachine/blob/archive-finished-trials/hardware/print-tests/m5-seam-bearing/physical-result.json).
Long passages may require turning the screw before the insert engages. Each insert and
the manufacturer's minimum stock round it, about the axis, fit
inside the side band. The lower axes stand in from the exterior,
where the head passes the handhold's inner wall on its way up; the upper axes
, which leaves 3 mm outboard of the roof opening and 3 mm inboard
of front-top's insert. Each head bears on a printed floor in a Ø9 opening,
 up into the handhold ceiling and down
into the roof. The lower opening ends on the plane of the handhold's inner wall; the upper
one runs on into the funnel opening. Seat the heads with a 4 mm hex key and stop when they
meet their floors; the printed joint has no qualified installation torque.

The [native fit reading](m5-pass-fit-review.json) binds the four current quadrants.
Only the M5 passages and their sloped entries gain material; the knuckle mating
planes retain their stated datums. The [aggregate reading](m5-pass-fit-aggregate-review.json)
identifies the same four native parts in both assemblies and preserves every
other native record and viewer body.

**The lower opening and the handhold's lip:** the lip's R6 roll and its print chamfer take
the first 2.29 mm of the lifting ceiling from the outer face, and the lower opening begins
4.75 mm in, so 2.46 mm of flat ceiling stands between them; 1.2 mm above the ceiling the
stock between the opening and the roll is 3 mm. The opening cannot move inboard: the head
passes the handhold's inner wall with 0.14 mm to spare, and that wall stands 0.25 mm off the
cold core.

Remove the two upper screws to free front-top, which draws fore off its rails. Removing all
four lets the halves part. The upper screws need about 110 mm of clear space above the roof,
the lower screws about 110 mm below the enclosure with the flank supported over the bench
edge. The handhold's inner wall over the seam is front-bottom's, standing on its own floor
tongue to the joint with back-bottom's wall, one fit under the lowest knuckle
(`_handhold_frame`).

A drop that opens the Y seam loads the screws in shear at the faces between knuckles: two
per lower corner and two per upper corner. The floor tongue supplies no tensile interlock. Drop
resistance requires assembled physical qualification.

## Exterior disposal warning

The +Y wall of back-bottom carries the full [household disposal warning](../../../markings/README.md)
as integral raised lettering in the enclosure's own material. Each line is centered on the
rear wall. The bottom of the lettering stands above the enclosure's
base. Its H capitals are high, and the letters are raised
 from the wall.
The generator measures every warning letter's outline against the 6.4 mm minimum.

Back-bottom prints floor-down, so the letters stand on a vertical wall. Every stroke's
underside is raked: it rises out of the wall at 45° to the letter's face, a face the layer
beneath carries. Every top is level and meets the face square, and the face keeps the
letter's whole outline.

The wall stays flat beneath the text and its margin, over a
 by field. The surrounding
flutes fade into this smooth area. It is the wall's own surface, without a border or a
separate carrier. The raised text is fused into the STEP body and retained on the printable
STL and viewer payload after the mesh flute cut.
The production slice adds no support contacts beneath the lettering.

## Exterior form

[`exterior.json`](exterior.json) owns the circular seam band, standing columns,
their concave roots and the continuous upper edge. The band grows out of the
straight walls and meets the columns tangentially. The columns retain the same
circle through the band's height. The upper round and its print-down bevel
continue around the display sides, front lip and rear edge. The display plane
and its blend into the roof retain their construction datums.

The flutes use the same pitch, depth and 5 mm runout on these surfaces. Their
ends taper into the rounded shoulder; the smooth shoulder continues through
the corner and onto the lifting ceiling. The band, standing columns and their
roots remain smooth. The handhold rims retain their lifting rounds and ceilings.
The wall, component, aperture and joint datums stay fixed.
Straight-wall groove coordinates also locate the condenser vents.

The display cover and its matching seat follow the rear nameplate's rounded
outline style. Its optical opening follows the glass. The funnel's mouth, collar and brim
are concentric rounded rectangles with constant-width bands; the supporting
recess follows the brim. The rear First Edition nameplate uses an R5 outline.
Hardware openings follow their mating parts.

## Handholds

One handhold in each ±X flank opens through the standing floor. The recesses are
 long in Y, centered at **Y**, and
 high from the slab's underside to the uncovered lifting ceiling.
The inside corner rounds join the ceiling to the end walls.
The exterior lifting edges retain their rounds.
Each ceiling carries a full section,
joined to the floor by the opening's end walls and to the corner stack above it.
The R6 roll joins the flat lifting ceiling, end walls and fluted exterior
tangentially, including the two corner blends. Its full section and flute
runout follow the top's side shoulder.
One complete handhold profile spans both Y halves and is mirrored onto the two
flanks. It cuts the finished shell and seam blocks together. The central lifting
ceiling remains exactly planar; the exterior transition and both rounded ends
share the same boundary across the seam.

The printed ceiling is the exposed gripping surface. The end walls are complete;
there are no grip covers, cover seats or wing slots. Tree(auto)/Default supports
the flat ceiling during printing. Surface finish and gripping comfort remain
unqualified on the complete production handholds.

The inner wall stands between |X|90.75 and |X|93.75,
0.25 mm outboard of the cold core's |X|90.5 flank. The complete wall, including its
rounded ends, uses that offset. Each opening
is closed toward the interior and open outward and downward. Both bottom pieces form each
handhold; its inner wall closes on square, full-thickness ends with one running
fit between the faces.
The central recess reaches 13.75 mm from the exterior plane to the wall's finger-facing
plane. The exterior transition ends at |X|105.208, leaving 11.458 mm of flat central
lifting-ceiling depth before the screw-pocket openings. The block's 13.75 mm reach
uses a different reference, `interior_x`; it includes the retained blind wall.
The floor tongue continues across the middle of the enclosure. The lower seam screws drive up
through the handhold ceilings. Each head sits in an opening that ends on the inner wall's
finger-facing plane, its face 6.55 mm above the finger surface. The openings remain exposed
during use.

`handholds` reads the upward entry space, full lifting sections, complete end posts and inner walls
on the finished pair, including the inner-wall joint's running clearance. These are geometry
checks; no physical lifting-load test is recorded.
The [wall-end check](handhold-joint/geometry-check.json) measures the complete
3 mm section through the wall's full height and verifies the floor overlap,
lifting roof, screw passages and assembled fit.

## The Z seams slide home

Bottom↔top, per column, at `enclosure.z_seam`: **a full-travel slide on hooked rails, and
no screw anywhere on it.** Down each flank's **straight run** the bottom piece raises an
**4.5 mm arm** on its mouth, standing one inboard of the top's own wall,
and the arm's **head** steps back out over the **groove** between them: a
 overlap on the front column and on the back.
The top piece's wall runs to the mouth at full section — the **foot**, its caught face
 over the mouth — with a **notch** in its inboard face that swallows
the head. Back-top closes that channel back to the full wall on one horizontal roof;
front-top alone uses a 45° roof over the void it prints mouth-down. The storey is
mouth to rim, and **the flavour deck is its ceiling** — the rim stands under the lowest
valve plate (`z-seam-under-deck`), which is the whole height the box has to spend here.
It buys the groove first: of it, the top piece's own sliding tongue,
with of head over the front catch. The rear groove is
 tall with of head over it. That height is the Z seam's own — `lip_len` is the Y
seam's overlap, which its corner stacks stand in, and the two are independent figures. The two columns
enter from opposite ends: **front-top enters fore of home and slides AFT**, over the front
wall's own plane in open air ahead of the box; **back-top enters aft of home and slides FORE**,
over the open Y-seam mouth before the halves telescope. Both broad mouth-to-shoulder
gaps are 0.25 mm. Front-top's mating shoulder face prints on the bed and adds no
supported-overhang allowance.
At the nominal assembled position, each foot's end face has **0.25 mm of running
clearance** to its stop block, a local allowance above the 0.15 mm head-on minimum. The blocks
retain 3.75 mm of length and bound overtravel; the upper seam screws join the two
tops. Reaching the assembled position does not require compressing the rail ends.

On both columns, the foot carries the flank's full 6 mm inward section from `interior_x` to
the nominal 9 mm face on both sides: in front and
 in back. Each bottom hook carries a 5 mm bearing overlap at that
face's inboard edge. Their arms reach in front and
 in back from `interior_x`, inside the 14 mm body-free seam
band. Each catch lies wholly over its six-millimetre foot and keeps a complete exterior wall
outside its channel.

**Lifting a seated top lands each foot's flat top face on its head's flat underside,
along both whole runs** — per flank on the front column,
 and on the back — horizontal printed
face on horizontal printed face after the specified clearance is taken up. The two
back flanks differ by the PRV passage: it crosses the −X run and takes
 of it, which is the figure that flank is already short by.
**The two columns end their runs on different things.** Aft of the front run the top
piece carries nothing but its own seam band and the Y-seam tongue, and both are inboard
surfaces the channel may cut — so that lane runs clear off the piece's aft end, nothing is
left to sweep around, and the run reaches its own structural limit: `wall + z_lip_y_margin`
short of the joint, where the Y telescope's overlap begins and the Z lip must stop. **The
back column is that mirrored**: back-top enters AFT of home and slides FORE, so what sweeps
its run is what it carries fore of it — its own Y-seam band, inboard surface the same
channel may cut. That run needs no horizon either and reaches the rear wall's own corner
round. Neither flank stops short for the PRV chase either, because the chase's two halves
are held to different rules (`_vent_chase`): the RIB keeps out of the band the joint reaches,
since it is solid and would sweep the rail, and it parts on the seam's rim so each piece
stands its own height of it and neither crosses into the other's travel; the PASSAGE is the
hole through that rib, sweeps nothing, and goes straight across — the rail gives up
 where the one opening that has to cross it does, and the duct keeps
its whole section. Both pieces cut that passage, so the groove's discharge leaves through
the flank on either side of the seam rather than half of it standing in the other's wall.
**Each top escapes toward the end of the box it stands at** — front-top fore into the room,
back-top aft toward the wall — so neither has to be lifted over the other. Front-top's
escape is open air, and what holds it there is the Y
seam's **two upper screws** — so with those two out front-top draws straight off the
front of the box, the back column and whatever the box is built under never touched.
Four M5 screws close the box; the same four open it.

**Every catch is square.** The head's broad underside and the foot's broad top face bear
flat against lift along both complete runs. Each bottom piece prints the head with support
under that abrupt ledge. Front-top prints its caught face up from its mouth; back-top prints
its caught face down from its ceiling and support carries it. The arm's base falls back to
the lip's underwall on a 45° under-flare. On either column the notch is an open rebate in the
wall's own inboard face. Back-top closes the channel across that bulk with one **broad,
horizontal roof**, with slicer support underneath it. Front-top's
mouth-down channel alone has a gabled roof of two 45° faces. Every sliding and bearing face
is vertical or horizontal, and the top's outer skin keeps its full `wall` of flute backing
down to the mouth.

**The corners give the slide its lane.** Over the seam band each bottom piece carries its
two pillars **solid to the rim**, flats one `slide_slip` off the walls the top's faces
sweep along; the top piece stands off that whole band and its pillar regrows above on the
45° pair every ceiling over a void here closes at. **The channel is the run's own span
and the sweep aft of it**: what a station of the sliding piece has to clear is the head,
so behind the stop block the lane is carried at **full section right off the front piece's
aft end**, through the Y-seam tongue's own flank segment and past its tip. The flank's
mouth band comes out as one unbroken rebate with no blunt face standing in it. At the
front column's Y/Z crossing, the channel opens from the flank's inboard face to the tongue's
slipped outer face below one broad 45° roof. That roof rises aft from the full wall on the
Y-joint plane, and the symmetric channel gable resumes above it. The tongue returns at full
section **above that ramp** — which is the height the Y telescope bears on.

**And the slide is proved, not asserted.** `_report_slide` sweeps each built top from full
entry to home against its built bottom — a ladder of stations, dense where the joint
closes — and lifts it a millimetre off its catch. The `z-slide-front-clear`,
`z-slide-back-clear`, and two `-catch` build checks fail the generator if any swept station
intersects or either seated catch misses its mate.

**What makes all of that fit is the band the walls keep.** A body standing on the
floor slab spans the interior wall to wall, so a body laid on a wall's face would
leave the seam machinery nowhere to stand. A **floor body is held one
`side_band_inset` in from the ±X walls where it meets the seam's furniture** — the
Y seam's corner stacks, or the rail band over the seam's own storey. Each column's full-section foot,
groove, arm and head reach inward from `interior_x`, inside that same
band.
The **+Y wall keeps one `rear_seam_clear`**, the rear Z-seam lip's own thickness. That is a requirement
on the body where it meets one, not a rule about the wall: beside one — over or under
one — the band is the wall's own air. Of the three bodies on the slab only the cold
core meets the band at the seam's storey; the compressor and condenser stand wholly
under the mouth. The floor is one plane 0.35 mm under the pack's z = 0, the allowance of
the face the core rests and slides on: 0.25 mm running plus 0.10 mm cavity-floor transition.
The slab under it is 5.65 mm. The print-corner relief runs
on the standing verticals and the Y-seam's floor joint stays inside the slab.

The pack's enclosing seam features retain their applicable fit allowances, and both
walls carry their corner stacks at full section.

**A wall that lip stands on is `2 * wall` thick, floor slab to lip rim.** The lip is
the cavity's own one-`wall` skin standing proud of the interior face, and a skin that
began at the seam would land its underside in air: a one-`wall` soffit round three
sides of a piece that prints floor-down, with nothing under it to print on.
`_lip_underwall` carries that same skin from the shoulder down to the slab, so the
two fuse into one wall with no step in it and the bottom pieces come off the bed with
no bridge in them. What it spends is the cavity, one `wall` off three sides of each
bottom piece — which is what the pack already stands off them (`front_seam_clear`,
`rear_seam_clear`, `side_band_inset`), measured rather than assumed by
`wall-under-lip`. `lip_face_x` is the flank a body down there meets: the MQ-6's can
bottoms on it through the well cut back to it, the condenser's aft fin roots on it, and
the compressor's suction lane is struck from it.

The Y seam is a stated plane, `enclosure.y_seam`, checked against those bands
rather than derived from them: which pieces the box comes apart into is a decision
about the pieces — what each has to carry, and what a hand reaches when the front
assembly is off.

`rear_seam_clear` is the single source for the +Y wall: `enclosure_assembly` seats the
rear-wall bodies against it and the declared Box the pieces are cut from is built to it, so the wall
the bulkheads mount through and the wall the box is built to cannot drift apart.

PET-GF bulkhead rings retain their flush front poses, with 0.15 mm behind each ring.
A full-section station keeps 3.85 mm of wall under its pocket, and its nut bears on the wall's
inner face. The relieved CO2 land keeps 3 mm and stands the 0.15 mm gap further in, so that
barrel's clamped stack includes it.
Supported pocket edges receive their directional allowance in back-top's inverted print pose.
The nameplate and DATA plate backs also have 0.15 mm static clearance. The nameplate's
production station is 0.30 mm west of the rear-field midpoint, with 2.14 mm of hidden east
backing for the specified 1 mm PSU margin. The [native fit review](y-seam-fit-review.json)
confirms the actual receiver stock and clearance against the placed PSU.
The label pads keep their full ordinary backing a short lead past the pocket's print-down
edge before their 45° run-outs, so the corner between pocket floor and run-out keeps a 3 mm
wall.
The DATA jack and its complete receptacle are recessed 0.16 mm behind the plate's nominal
back plane, preserving a 3 mm flat lip behind the plate's 0.15 mm allowance. Its required
50° insertion ease remains a separate functional bevel; DATA's wings and retaining roofs
keep their specified sections and poses.

Each printed piece fits the H2C left-nozzle build envelope (325 × 320 × 320 mm)
even though the whole enclosure does not — that is the point of the split.

## Above-core mounts

The [production arrangement](/hardware/manifold-layout/above-core.md) owns the native
component frames. Back-top carries integral upper seats for the ASSE and
Pisco, an east-wall meter seat, and the water regulator's ceiling seat.
Four removable caps close these seats with reinforced 2.6 mm spring leaves.
The ASSE and Pisco load 16 mm fore of their seated positions and slide aft;
the meter slides aft onto its soda outlet stub before its cap enters from
the west. Ordinary supporting stock is at least 3 mm.
Fit and service the meter cap with back-top separated from the cold core.
Fit it before the ASSE cap. For removal, disconnect and dress the tubes and
leads aside, remove the ASSE cap, spread the meter leaves, withdraw 20 mm west,
relax the leaves and move 40 mm fore. This bench sequence leaves room for
the complete lower leaf to open.

The PSU mounts base-up to four ceiling hosts with its AC end aft. The two
relay boards sit on the dry west wall, 20.5 mm apart. Four edge ledges support
each PCB; rigid 3 mm terminal-end rails retain the opposite end from its two
header-end M3×8 screws. Slide each board 6.5 mm aft into the rails before
fitting the screws. The insert faces stand 2.5 mm behind the PCB underside,
leaving 0.5 mm over the nominal pin envelope.

The shared V69 socket sections carry V-A and V-K. Preserve the
[accepted valve-fit scope](/hardware/mechanical-qualification/README.md).
The PCB, bare pump and V-B belong to the cold-core lid. Its broad pump base
has a straight cover channel, fixed rail-end stops, a filled 6.2 mm cap and
one 4 mm chamfer clearing the rear flavor bulkhead. Junction wells follow
their branch points on the rear wall, core lid and front manifold.

The rear fluid field retains its relieved clamping land. The mains inlet uses
an internal flange pocket and inward screw access in a broad wall-rooted tunnel;
only its cord passage opens on the outside. RJ11 uses its keyed
receptacle. Their stations and the two-column fluid grid are defined in the
shared arrangement. The rear ceiling is continuous. No wiring or device
mount attaches to the removable funnel frame.

## Condenser cradle

The condenser's four sheet flanges are the block's whole purchase. Its two fore flanges slide
into rails on the front wall; its two aft holes screw into fingers on a standing fin at the +X
wall. The base rail and lower finger run to the floor slab. The crown rail and upper finger do
not: each carries its entire down-facing plane on a 45° corbel rooted on the wall or fin it grows
from (`_cond_cradle_corbel`, `_cond_mount_corbel`).

The crown wedge is only the rail's reach. The aft wedge is longer, but it
lies wholly in the donor block's open end recess and stops on the fin's west face. The condenser stays fixed and the closer
one keeps `cond_mount_clear` of assembly air.

Each fore-flange groove keeps its exact opening at the seated wall stop,
then its roof rises toward the bay at 45° and leaves through the rail's aft face higher, a full rail wall under the crown.
The groove keeps 0.25 mm on each face of the sheet at its datum. Its sloping roof prints without support.

## Closing and final access

The [mechanical procedure](/hardware/assembly/enclosure-mechanical.md) names the
carrying pieces, preparation and cross-quadrant handoffs. Back-top carries its
PSU, relays, meter, V-A/V-K and fitted plumbing while the core carries the PCB,
pump and V-B. The motion records state the actual tested groups and clearances;
they do not establish flexible tube handling or physical assembly force.

Keep the drop-in funnel frame separate during final cross-quadrant connections.
Lift the silicone and remove the frame's four recessed screws to reopen that
aperture. Its drain cradle snaps into the frame's original 3 mm web. The plug,
stub, elbow and cradle travel with the frame; disconnect the V-B feed before
lifting it. Disconnect and support crossing connections before reversing the
enclosure slides.

## Cold-core grips

The cap crown is the core's Z253.4 nominal reference. The [native fit review](y-seam-fit-review.json)
identifies the five external printed core bodies individually and checks the enclosure's
finite floor, flank, crown and hold-foot faces against their actual native material.

The core is the heaviest body in the machine and the one with no hole in it — a foamed cup
under a screwed cap, plain skin the whole way round. What fastens it is the closed box: **the
seams stand every piece against its neighbours**, so a feature printed on one piece stands
over a body sitting in another, and the front-bottom, the back-bottom and the back-top close
on the core together.

Four features bearing on the core's own faces:

- **Front corner blocks** (`_core_stops`, on `enclosure-front-bottom`). A block in each front
  corner of the slab, across — the ±X wall inboard to one corner round
  past the tangent — and off the slab. **The pocket in it is the core's
  own rounded plan outline offset by 0.25 mm**: a Ø
  bore on the round's own axis outboard of the tangent, and the core's own flat front face
  inboard of it. So the block bears flat where the core is flat and round where it is round —
  the flat bounds forward travel and the round bounds sideways travel and yaw after the
  modeled allowance is taken up. The web ahead of that outline is at every point of it,
  including the tangent, where a bore alone leaves it thinnest. Underside on the slab, outboard
  face on the wall: a corner bracket in one piece with both faces it stands on, the card slot's
  own form.
- **Aft brackets** (`_core_holds`, on `enclosure-back-top`). A right trapezoid in section,
  wide on the west and 9 mm on the east: the bearing face along the cap from
  forward of the core's aft face back to the wall, a leg up that wall in
  the `rear_seam_clear` band, and one straight from the head of the leg down to the foot's tip,
  over the bracket's foot plane. The whole bracket profile stands
  0.25 mm above the core's cap crown, putting the cap-facing foot at Z253.65.
  This face prints upward with back-top inverted and adds no supported-face allowance.
  The straight web carries the flange. The west bracket occupies X−43.6..−37.5;
  the east bracket occupies X6.55..15.55, ending on the wet-field recess boundary.
  Both retain their complete 40 mm wall legs and the Z253.65 bearing plane.
  The populated back column slides over the core before the final flexible
  handoffs are connected. Printed fit and restraint strength remain unqualified.
  The [native hold reading](core-hold-review/native.json) binds the complete east profile,
  wall root and cap gap to the current export, and preserves the west hold exactly.
  The [current slice](core-hold-review/slice.json) binds its print preparation.

The whole core pocket follows that same rounded plan with 0.25 mm around it,
from the floor to Z253.65 above its cap crown. The floor under it is the box's one floor
plane at Z−0.35, which carries the core's 0.25 mm running plus 0.10 mm cavity-floor
transition; the slab is 5.65 mm thick. The floor, front blocks, rear seam band and cap brackets bound
the nominal core envelope in all directions with the modeled allowance at their mating faces.
The [core-stop native review](../pump-dock/core-stop-native-review.json) records the
lower quadrants' bearing faces, supporting webs and pairwise closure against its
bound Box and native pieces. It establishes nominal geometry, with no physical load qualification.

**The core enters from ahead, and only from ahead.** The back column closes empty — its
+Y wall cannot pass over a seated core — so the core rides in through the open Y-seam
mouth, aft over the slab to its seat, the crown sliding under the brackets' eased feet. The front assembly then slides aft onto it and
the corner blocks' pockets close around the front face with the same 0.25 mm allowance.

**The front blocks need no support**: they print floor-down with no overhang in them.
The aft brackets print with back-top ceiling-down. Each cap-facing flat looks print-up;
the gusset face grows from the rear wall at more than 45° to the bed.
The production preparation retains Tree(auto)/Default.

## The reeded skin

The standing walls' flat show faces are **fluted** — half-round grooves
 across and deep, with the profile from
`cadlib/reeding.py`. The four R12 standing corners are smooth through their full
90° turn, at the same outer envelope as the flute tips. The exterior field adds
up to 1.2 mm of material where a corner groove would otherwise cut inward.

**It is in the MESH and not in the solid**, and that is a decision rather than a shortcut. The
fade is what makes the texture look made rather than applied, and the fade is a FIELD OVER THE
SURFACE — how far a station stands from the nearest place the show face ends. A boundary
representation can carry a fade that runs level, because a level fade is a loft; it cannot carry
one that follows an opening's rim, a pocket's edge and the rounded display surround all at
once. So the STEP is a smooth body and [flute_skin.py](/hardware/printed-parts/cadlib/flute_skin.py) cuts the flutes into the
mesh on the way to the bed. Everywhere else on the machine the STEP is the whole of the part;
here it is not, and the `.stl` beside it is.

At every station the field asks the piece whether it has
material AT the nominal plan — by level cut, not by naming features — and takes a distance
transform of the answer. A flank opening, a port chip's seat, the nameplate's pocket, the bay's
own mouth, the seam a piece simply ends on, the bed, the rounded top and display surround are
one fact to it, and every one of them gets the same ramp over.
The rounded plan stations are kept plain; the same distance field fades the
adjacent straight-wall grooves into them. The structural solid defines the
internal seats, joints and complete outer corner envelope.

A rim that runs WITH the flutes is not one of them: a groove ending along its own length has
nothing to stop. The Y seam is one, and so is every jamb.

**The field closes on itself.** nominal stations go round
 of plan, struck by arc length from a datum on the front
wall's centreline. The phase continues across each smooth
corner turn. No station restarts the array and no two arrays meet anywhere. The pitch is what that count lands
on, against the coupon's. The **Y seam** — the
one straight line running the full height of both side walls — lands
off a groove's centre, in the shadow that is already there rather than on a land.
**`flute-closes`** holds the pitch to the coupon's.

The datum is a groove centre on **x = 0**, the plane the whole machine is struck about,
so the field is symmetric in x whatever its pitch. Front-top carries the continuous
front and side skins across the pump-mount height; its exterior field follows that same
closed plan without a cartridge joint.

The pump pockets, lower retainer, skirt lands, tube passages and wire passages are functional
interior surfaces. They stay plain. `flute_rails` supplies the exterior plan only; the
integral upper mount and its broad stock do not create an indoor decorative field.

**Nothing may relieve into the outermost of a fluted face.** The exterior
profile ([print-log.md](print-log.md)) lays two wall loops a side at 0.42 and 0.45, so one
`wall` is 1.74 mm of solid perimeter and a groove floor still has all four of them, with 0.06 mm
to spare. Take more out of the far side and the two pairs of loops meet: the slicer stops laying
four walls, and the change in what it lays under the groove reads THROUGH to the show face as a
mark you can find with a fingertip. What a groove leaves is, and
**`flute-backed`** reads every stated section on a fluted face against the rule — with two of
them computed rather than typed, because the survey that measured this found them and the file
had not stated them: the measured backing below the front curve, and
`east_boss_bore_end` for an insert bore behind a corner round, where the turn carries the
surface inboard of the plane the bore was struck on.

**It is free to print.** Every groove runs down the build axis, so its own side surfaces are
drawn by the nozzle in XY, carry no layer quantisation at all, and hang over nothing. The ramps
are `flute_depth` of relief over `flute_rise` of height — off the wall at the
smoothstep's steepest, against the 45° every relief on this box is struck at.

## The condenser's vents

**The vent is the flutes, pierced.** The condenser's fan draws through one flank of the block
and blows out the other, and both flanks of the box already carry the reeded field — so a slot
 across is struck down the FLOOR of every groove standing over the finstack,
on the field's own centres, clean through the a bottom piece's lipped flank
carries. Both jambs run WITH the flute and the groove carries on past both ends of the slot at
full depth, so nothing crosses a flute anywhere here and no edge it makes is one the skin stops
on. Off-normal the wall reads as unbroken reeding; head-on it is a grille.

**The mullion is the governing number, not the section behind the groove.** A slot takes its
width out of the pitch, and what is left between two of them is at
 centres — against the of loops the exterior
profile lays (2 × 0.42 outer + 2 × 0.45 inner, [print-log.md](print-log.md)), which leaves
 and ceilings a slot down every groove at. The
two figures move OPPOSITE ways: the jamb stands half a slot off the groove's centre, out on the
half-ellipse where the groove is shallower, so the flank behind a jamb is
 rather than the 4.8 under the groove's own floor — a wider slot never
thins the wall and only ever thins the mullion.
The coupon at `c14bb2fff` printed this scheme beside the ceiling slot and a full-groove-width slot
down alternate grooves, on a section of this same flank at this same pitch.

**Every groove, and the stations are the field's own.** `vent_grooves` walks `flute_centres` and
asks `plan_at` where each one landed, so a slot is struck at a groove centre by construction and
the vent follows the field if `flute_count` is ever retuned — there is no Y station typed
anywhere in the feature. A groove is in when its whole slot lies inside the block's AIRWAY: the
 between the block's two recesses, which is finstack. The 20 mm at
either end is the sheet the box holds the block by, and the fan draws through neither.
 grooves stand in that window on each flank.

**In height the band is the FAN, not the airway.** What moves air through this wall is the axial
fan bolted to the block's own flank; the finstack either side of it is served by whatever that fan
pushes, and wall opened opposite it is opening on metal. So the band is the placed block brought
in at its base and at its crown —
, a band, the fan's own footprint and nothing wider.
Both insets are read against the block where it stands, so raising the block raises the vent.

**Less whatever the flank carries behind that particular groove.** Nothing is listed: the piece
is asked, groove by groove, what stands ROOTED on its inner face, probing one
 wall inward and keeping that same margin past both jambs and both ends. The
transoms are the opening vocabulary: if a root's margin enters one course, that whole segment
stays solid and fluted rather than becoming a one-off short slit. A single opening marooned past
such a land stays wall too. The MQ-6's two posts stop below the vent band, and its can stands
off the flank face, so nothing of the sensor reaches the vent. All
 realized intake openings are the full segment;
 have a different height.

** transom bands cross that vent, and they are why it prints.** A mullion is
 across. Pierced clean over the whole band it would stand
 — a picket that tall with nothing tying its top to anything. The brace
is **not** a bar between two mullions, and nothing stands at 45° across a groove: at
 heights — — the wall is simply **not
pierced**, so every mullion and both jambs run into one plate of full section
 tall. Nothing bridges and nothing grows out of a tower. What is left is
 slot segments of apiece, and the four of them plus the
three transoms close exactly on the band — `vent_transoms` divides the band rather than listing
stations, so the layout stays symmetric about its own mid-height whichever of the three figures
moves.

**The groove runs through a transom unbroken.** Only the piercing stops. The field is struck on
the flank's whole plan, so a transom is invisible off-normal and the reeding reads continuous down
the wall — head-on it is a grille in four courses. Both ends of every one of those
 segments are closed by a 45° hip, the angle every relief on this box rises at:
each hip sits down inside the groove's own shadow, the sill only takes material away as the print
climbs, and the ceiling closes at exactly the angle the box supports nothing steeper than.

| | slots | openings | thinnest mullion | tallest opening | free area |
|---|---|---|---|---|---|
| −X intake | | | | | |
| +X exhaust | | | | | |

Both read off the built piece at the flank's mid-section, over the fan's own band. A pierced field
is open where every slot runs; the readings above are what the band came
out at with the transoms, the hips and the intake's rail in it. The tallest opening on either flank is on a
 mullion, which is.

**The air path is the donor's.** The condenser, its fan and shroud, and the compressor beside
them stand in the donor ice maker's own arrangement
([`reference/ice-maker/`](/hardware/reference/ice-maker/README.md)), and these flanks are
pierced more openly than the donor's grilles. The compressor in the pack is a clearance
envelope: [`compressor.py`](/hardware/reference/compressor/compressor.py) runs the shell's
calipered section straight through its full height, so the gap that envelope leaves at the
condenser's intake face is packing room, not the air passage. The heat the loop
rejects, ~240 W at worst, and the 40 mm side gap that keeps the cabinet from being the
restriction are in [`install-envelope.md`](/marketing/install-envelope.md); the cabinet with
its doors shut is in the [enclosure README](/hardware/printed-parts/enclosure/README.md).

## Mating clearances

[`cadlib/fits.py`](/hardware/printed-parts/cadlib/fits.py) supplies the per-face allowances
for PET-GF parts mating with other PET-GF parts in the enclosure:

| Mating surface | CAD clearance |
|---|---:|
| Static | 0.15 mm |
| Sliding | 0.25 mm |
| Static with retained bridge strands | 0.40 mm |
| Static with retained bridge strands on both mating faces | 0.65 mm |
| Sliding with retained bridge strands on one face | 0.50 mm |
| Sliding with retained bridge strands on both opposing faces | 0.75 mm |

The modeled gaps reserve room for rough or oozed printed material, including at
seating and clamping faces. Each supported overhang contributes one bridge allowance
in its print direction, applied to that face or its mate. Both Z-seams' broad
seating shoulders have 0.25 mm running clearance. Front-top's mating face is bedded;
the rear pair's mating faces look print-up. Neither broad shoulder adds an overhang
allowance. The separate front catch has one supported
face and uses 0.50 mm; the rear catch has two and uses 0.75 mm.
Y-normal closure faces approach head-on and use 0.15 mm static clearance. The existing
0.25 mm rail-end gaps remain a local conservative fit.
Sliding covers constrained motion that needs to move easily, including short
spring-driven engagement. The [low-force rule](../clearance-audit.md) adds a working
0.50 mm only to an identified gap requiring low actuation force. The accepted tee-carrier
trial records 1.00 mm above and 0.25 mm below for its identified article; the flat-wing nameplate uses static fits.
A bore receives twice the base per-face allowance in its diameter; only its supported crown
receives the extra 0.25 mm. Where a pocket's enclosing wall is 3 mm thick, its outer stock
moves with the pocket or the mating part retreats. Printed bearing, locating, seating
and clamping faces require the same applicable allowances; a datum does not waive them.
This enclosure pass covers the PET-GF-to-PET-GF interfaces in its stated scope.
Rigid-part fits elsewhere remain subject to the same printed-face allowances and are
unresolved by this pass. Compliant gaskets and seals use their specified installed squeeze
in the compression direction. Screw-head floors retain their nominal source planes and
are outside this pass's fit assessment.
Heat-set pilots follow the manufacturer's installation dimensions.
Finger openings, flexible-tube routing and vibration-isolation spaces have their own envelopes.

`petgf.3mf` carries a 0.45 mm requested support top Z distance, two top interface layers,
0.50 mm top interface spacing and the automatic interface pattern. At the profile's 0.24 mm
layer height, the organic-support slice produces a 0.48 mm interface-to-model gap.

`petgf.3mf` uses `auto_brim`. Enclosure projects retain that automatic setting by default;
individual prepared plates record their brim setting in their
[slice review](../tee-readiness/full-enclosure-print/native-slice-reviews/README.md). Tooling projects may specify a brim.

## Support-removal strategy

Enclosure parts and receiver test coupons use the tree support settings from
`../../petgf.3mf` in each part's production print orientation. The screw-mounted
nameplate prints with its flat back on the bed and its screw seats facing upward.

Use Tree (auto) for accessible exterior features. Supports inside enclosed cavities
must be branching trees; normal rectangular supports are not removable there. The rear
enclosure, front pump cavities and lower pump retainer select Tree Slim. Inspect
the actual branches and removal openings in the emitted native slice. A smaller
footprint or an open-looking lane alone does not establish easy cleanup.

Back-top prints ceiling-down with its rear flutes clear of the bed. Accessible
exterior features and rails use manual Tree Slim selected by native contact
regions. Native exclusions
keep the receiver interiors and covered passages clear of supports.

The rear receiver catches bridge along their pockets between the complete end
shoulders. The Pisco entry relief has a sloping ceiling that preserves its fore
bridge anchor. The sideways meter host uses authored removable trees under its
exposed end shoulders; their trunks stand beside the Pisco pocket and their
forks branch below it. Approved component seats, catch planes and wing travel remain
intact. Local modifiers select the bridge direction and solid catch stock.
Native construction emits the exclusions beside the STL, bound to its digest;
preparation carries them through orientation and placement as blockers and
painted surfaces. The covered bulkhead bores and horizontal valve sockets use
teardrop roofs pointing in the build direction; build-axis valve sockets remain
circular and open. The PRV cap has a rooted chamfer and end-wall backing, and
its short mouth lip bridges between the side walls. The native review reads
support beads inside these named regions, including ordinary support paths
without interface labels.

A production-profile slice reports the connected support bodies which reach the model and their
separate interface islands. One body can reach several distinct contact regions. Two further
readings are recorded per body: its build-up, the vertical distance from its own base to its
first model interface, and its root, the print bed or model material.

**These are measurements of one slice, and none of them ranks a design.** Connected bodies and
interface islands describe the support topology. Neither build-up nor root kind says anything
about what it costs to get the support off. Removal effort, trapped branches and contact finish
are read on the physical print and nowhere else.

**What decides removal is the lane, not the reading.** A body comes away easily when its faces
stand in open air, nothing is installed over it, and it leaves in one piece along a straight run.
It fights when it is walled on several sides, when a branch re-enters a pocket
behind its own interface, or when the hardware goes in first. The Z-seam catches
retain their flat sliding bearings and local solid stock. Their supports must
remain reachable through the open sliding lanes. Localized bridge and foundation
cooling follows the newly supported bearing courses. The
[full rear enclosure result](prints/2026-11-05-back-top-smooth-corners-mark2/physical-result.json)
records removable rail supports with a loose underside and glossy later courses,
and inaccessible receiver supports. Inspect the complete part rather than
applying a coupon's cleanup result where walls block the tool.

The audit records each support's actual root. Its position, contact and removal
lane determine whether it is accessible in the ceiling-down part.

**Expanding print-down show rounds use an additive chamfer/taper at 0.24 mm.**
The shared construction in `../../cadlib/overhang_round.py` fills the lower corner
inside its unrounded envelope, with a 0.5 outward/build-rise slope tangent to the
retained circular taper. R6 has a 3.317 mm straight transition and a 2.292 mm initial
inset; each 0.24 mm layer advances at most 0.12 mm on that section. The enclosure applies it to handhold upper rims
and roof side edges.
Flat lifting ceilings and mating planes keep their required dimensions.

Use a 0.20 mm first bed layer, six walls locally through the expanding band,
and the saved wall-first order, speeds and 15% overlap. Keep support contacts off
those transitions. **Inward/top show rounds retain 0.08 mm**. The
[carrier physical record](../tee-carrier/physical-acceptance.json) includes its
complete top R6 and qualifies the chamfer/taper's surface on that article; sliding fit and the other parts' physical
surfaces remain separate checks. Each fresh slice must verify first/second-layer
bead overlap and absence of support contacts on the show transitions, including
short support bodies without an interface label.

Printed working faces meet the clearance, supported-surface and stock requirements.
A seating or bearing role does not waive them. The face keeps its required working
shape. Accessible trees or anchored bridge paths carry it in the print.
The C14 inlet's flange pocket keeps its floor, because that floor is what the receptacle lands
on; each handhold keeps its flat lifting ceiling, because that ceiling is the surface a hand
pulls up on; the Z-seam catches are broad square planes because they bear against lift along the
complete rails; a corner stack's knuckles keep their square bearing
faces; a pump boss lands on a flat shoulder. A corbel carries the material behind one of
those faces. It does not replace the bearing, locating, sliding, sealing, clamping, insertion or
access face with a slope.

The fixed fluid supports use broad roof/wall roots and separate snap caps.
The four DC/sensor junction wells belong to the core lid. Support removal
access is assessed on each current slice before hardware is installed; accepted
results from a different part or orientation retain their recorded scope.

**A support audit does not authorize a layout or mechanism change.** It does not move a placed
component, shorten a guide, narrow a bearing, reduce retention or alter a working envelope merely
because the other numeric gates still pass. Those are design changes reviewed on their own. If an
independent design change moves a component, the support audit measures the consequence; support
count is never the reason that makes the move valid. Preserve the feature. Where the support
leaves cleanly, take the support: an accessible body is not a debt and is not designed away.
Where the lane is bad — walled, re-entrant, or under hardware that goes in first — add the
smallest printed geometry that carries the face, a corbel or a column, never a slope across a
working face. This policy applies to every printable part in the enclosure assembly, not only
the four shell quadrants.

Each piece's retained slice reading is `<piece>.support-audit.json` beside its STL, and it
identifies its model, profile and G-code by digest. The readings are bench references outside
the normal build and publish path.
The `support-audit` program ([`support_audit.rs`](/hardware/printed-parts/cadlib/support_audit.rs))
reads an exported Bambu G-code or sliced archive directly, or refreshes only the mesh in a
temporary copy of the named production project before slicing it:

```sh
git show 366d54ba040ecc7f1465c200e63e52410ffc0d4c:hardware/printed-parts/enclosure/enclosure/enclosure-back-top-petgf.3mf \
  > /tmp/enclosure-back-top-petgf.3mf
tools/hsm/target/release/support-audit \
  --piece enclosure-back-top --slice-current \
  --model hardware/printed-parts/enclosure/enclosure/enclosure-back-top.stl \
  --profile /tmp/enclosure-back-top-petgf.3mf \
  --profile-label git:366d54ba040ecc7f1465c200e63e52410ffc0d4c:hardware/printed-parts/enclosure/enclosure/enclosure-back-top-petgf.3mf \
  --json-out hardware/printed-parts/enclosure/enclosure/enclosure-back-top.support-audit.json
```

The result carries the model, profile and derived G-code hashes, the slicer's support settings,
all interface islands and both plate and CAD coordinates.

**Retained native slice evidence is bound to its identified geometry.** The following
readings describe the four quadrants and separate pump cradle/cap listed by their archived
STL digests. They do not qualify the integral pump mount, revised front-top or underside
retainer. Current native print preparation and review are recorded beside the
[pump-mount review](pump-mount-review/README.md).
The current integral-mount front-top is STEP `6120cf94…`, paired with retainer
`bd394956…`. The native assembly record binds these exact parts separately from
its original complete-path inputs and identifies the M5-joint review for the
four Y-seam hosts. Pump, valve, glass-seat, wing and cleanout stock keep their
separate native comparisons.

The 3MF snapshots are evidence inputs in Git history: four at
`aef8f43c0eb3eef9c6525ecaa0a1ca52c5b8c71a`, the cap's crown-down project at
`b4e181bee752bebaddc24d5e620fd7f8144129bd`, and back-top's ceiling-down project at
`366d54ba040ecc7f1465c200e63e52410ffc0d4c`. The retained October 25 Mark1 cap,
front-top and front-bottom slices identify STLs `fa10132c600a`, `317721279647` and
`1a1c2762f71e`, recipe `45c16e8c8517`; the Mark2 back-bottom slice identifies
STL `a967b77ebfbc`.

| identified piece | bodies | interface islands | root | shortest build-up |
|---|---|---|---|---|
| `enclosure-pump-cap` | 2 | 2 | bed | 14.16 mm |
| `enclosure-back-bottom` | 4 | 12 | 3 bed, 1 model | 8.16 mm |
| `enclosure-front-bottom` | 4 | 4 | 2 bed, 2 model | 7.92 mm |
| `enclosure-back-top` | 13 | 35 | 2 bed, 11 model | 1.44 mm |
| `enclosure-front-top` | 2 | 6 | bed | 96.95 mm |

These counts establish no cleanup effort. The identified cradle has no supports; the cap's
two bodies leave through its bed-facing screw-counterbore mouths. The identified front-top
slice has one bed-rooted body at its lintel/display region and one at its east WAGO pockets,
with the recorded empty-bay removal routes. Those geometries retain that specific scope.
Four bed-rooted bodies carry the handhold ceilings, one per flank on each bottom piece,
each with 34.08 mm of build-up, and each comes out through the open bottom. On back-bottom
the edge fins split each ceiling's contact into several islands, and the same two bodies also
stand in the M5 head counterbores above the handholds at Z39.8–40.3, 45.6 mm up; each is
walled by its bore and leaves downward through the counterbore's mouth and the handhold. The other bottom-quadrant supports carry one feature
standing on all four flanks: the **Z seam's slide-head catch**, the joint's one down-looking flat and the
whole of its bearing against lift. Back-bottom's west catch reaches the bed from outside its
flank through the 12 mm PRV passage that crosses it — the same opening that splits that catch
into two interface islands. The other three have no lane to the bed and root on the arm's own 45°
under-flare below the catch they carry: 7.92 mm for front-bottom's pair and 8.16 mm
for back-bottom's east catch. These are the material-rooted bodies on the two bottoms, and the
reading says nothing about what they cost: the groove under a catch is open air from the arm's
sliding face out past the exterior plane, so each of the four stands on the outside of its flank
with a face exposed down the whole run. Front-bottom's pair is printed and pulled — the easiest
support on the piece, off cleanly in one piece, reachable without going near the cavity.

Back-top's [support-removal packet](support-removal-review/README.md) binds the native
paths to their source geometry and printer recipe. It reads the receiver interiors,
covered bores, valve sockets and vent passage, together with the support bodies and
their contact islands. Release exposed contacts and remove branches before installing
hardware. Native access establishes geometric lanes; physical cleanup effort and
finish remain observations of the print.
Back-bottom's two slide-head bodies carry the broad flat undersides: the west run from the bed through the PRV passage and the east from the arm's under-flare 8.16 mm below.

## Print orientation + corner relief

The bottom pieces print floor-down and front-top prints mouth-down on its seam rim.
Back-top prints ceiling-down, with its rear flutes clear of the bed. The native
preparation owns this manufacturing pose, and receiver coupons retain its layer direction. Construction retains the piece's own
Z sign for its roof, foot and relief geometry (`enclosure.print_up`).
The mounting forms are described in [Support-removal strategy](#support-removal-strategy).
The anti-warp relief goes on the arrises
that run along the box's Z axis: the box's **standing verticals**, rounded to match the foam
shell's 12 mm outer radius — concentric inner one wall in, so the wall is
preserved.

A quadrant owns only **two** of those four. Its other two "corners" are the
Y-seam — a telescoping mating face, with no exterior arris there to relieve
(the side walls run straight through the seam). So the front pieces round the
front-left and front-right verticals, the back pieces the back-left and
back-right, and **every seam edge stays 90°**. Assembled, all four verticals
read as relieved, each sourced from a different quadrant. Of the horizontal
front-to-back arrises, side-wall↔floor is square and side-wall↔ceiling is the top's
rounded side edge (`SIDE_RADIUS` in [`interface/swept.rs`](interface/swept.rs)).

The display facet raises no fifth standing vertical: running wall to wall, it ends
on the ±X exterior walls and runs out into their own rounds.

Inside those verticals stand the **columns**, and each one is that relief
**mirrored** — congruent, which is what fixes it. The relief outside is a **quarter turn**
of; a mirror is congruent or it is not a mirror, so the column's face is
a quarter turn of the same radius — the **same arc and the same length**. The only place such
a turn fits inside the cavity with its ends on the two inner faces is swung from the corner
they meet at, and that is the whole construction: one radius, one centre.

It lands on each face at 90°, so a standing vertical presents **two sharp corners** opposite
each other, along each inner face, with the arc between them. The
section stands out of the cove at the corner's diagonal.

**The corner behind it is solid.** The face is the column's only free surface — a second arc
back there would leave a through slot the column's whole height — so the column is everything
within the radius and the wall keeps the rest. The cove the wall had turned stops being a
surface at all: what the room meets at a standing vertical is **one arc, congruent with the
one it meets outside**. All four verticals carry one (`enclosure.column_corners`), so each
quadrant prints the two its own two exterior arrises stand behind.

A wall's inner face is **flat only past that landing**, so anything ROOTED on it answers to
`enclosure.wall_flat_from_corner` rather than to the relief's own tangent. The C14 tunnel
follows `c14_station_x`.

**Front-top owns the complete front exterior and the upper pump mount.** The central
opening is underneath, between the continuous front skin and tee wall. The plain lower
retainer fills that opening after the prepared unit enters motor-first. Its outer form is
rectangular, and its fitted lower wells supply the required pump clearance and bearing lands.
Above the fitted upper half the surrounding stock continues to the existing enclosure roof.

A column is the cavity's own shape (`enclosure._cavity`), not a feature bolted into
it, so everything held inside the cavity meets one the way it meets a wall: the
Z-seam lip wraps its face and telescopes on it, a seam block is clipped by it, and
anything standing inside its footprint is **absorbed** — the boss becomes the column's
own material and keeps only its bore.

Where what stands there is a **body** rather than a boss, the column is the one that gives:
`_dims` measures every placed body against every column and hands `build_piece` a pocket per
lump one actually reaches into (`Box.column_reliefs`), cut last of all and clipped to the
pillar so it can never take the wall behind it or the boss beside it. A column is a
print-corner feature — what it buys is a fat vertical on the bed, and it buys that over the
height it does have; a body hung on a wall has already answered to the boss that holds it and
to whatever the pack packed it against. `main()` prints every relief, so a hollowed column is
never silent. The condenser's flanges relieve the front-east column:

- **X+/Y-** — the condenser's two sheet flanges, at z 8.0–10.4 and 144.6–147.0. The pocket
  shares material with the cradle groove. Its ceiling keeps the column's two 45° walks through
  that overlap, while the groove roof rises toward its insertion mouth; the rail's east end and
  the lens print as one body without restoring a flat roof over the pocket.

What a column cannot absorb is a seam station:
the lens runs along the wall to its cusp and would be a leaf-shaped hole through a socket
collar's root, so a station landing there stands one collar radius clear of that cusp
instead and the collar comes out whole — the front column's front-wall station
(`enclosure._z_front_station_y`) and the back column's rear-wall one
(`enclosure._z_back_station_y`), which are the two seam ends that sit in a standing corner.

The rest of the seam furniture follows the orientation rule: the Z seams' rails run
the straight flanks only — a slide neither turns a corner nor stands where a corner's
own skin sweeps — and the deep channel that lets the bay floor and the posts pass the
rails is the one mark the slide leaves inside a standing corner. The Y-seam lip sits
mid-wall where there is no vertical arris, so it stays square.

The Y-seam lip is the one joint the orientation costs something. Front-top's ceiling
tongue juts one overlap past the body into the space the back piece's ceiling
occupies — a cantilever that cannot be buttressed without colliding with the back
piece, and so wants print support. The floor does not share that cost: its tongue
runs aft at the slab's full thickness with its underside on the bed and ends square.
The back half's floor starts square from the bed one running fit aft, so the cold-core
bearing plane carries no supported surface. The side-wall
segments, vertical to the bed, are free. Back-top's upper corner blocks grow directly from
the ceiling slab. Their flat lower ends face print-up, and front-top's passages open around
them through the ceiling tongue.

The −X flank is a continuous 9 mm wall in the rear service bay. The ASSE vent connects through a printed TPU sleeve directly to the white 4 mm LLDPE return, which follows two R25 bends to the middle-row DRAIN bulkhead. [ASSE drain assembly](/hardware/assembly/asse-drain.md) gives the tube and fitting sequence.

The ASSE and regulator saddles join the fixed roof, with their bodies removed
while supports are cleared. Their circular bearing faces retain their functional
geometry. Use the shared Tree(auto)/Default policy and inspect the current slice;
no physical cleanup result for an older anchor transfers to these supports.

The **pump-loading opening** reaches the underside of loose front-top. It removes the
central floor under the prepared unit while keeping the continuous front skin, both flanks
and the tee wall's supporting end regions. The rectangular retainer enters through this
opening and snaps into the two flank receivers before chassis closure.

The **tee wall** grows from the seam region into the continuous upper stock. Each branch
bore and collet opening has a teardropped roof. Flexible pump stubs feed through the
closed bores during loading. The bore-face lands
locate the fixed tee barrels. The shared rear wire passage has a diamond roof forward of
the bulkhead; its motor rooms close with 36° conical roofs. The cross passage has one level
floor and a 45° roof. The display receiver carries the glass seat, PCB opening and blind side-screw pilots. The exact native slice supplies the support/contact reading for those
functional faces; no earlier slice establishes cleanup of this geometry.

The rear fluid bores retain their circular hardware envelopes inside teardrop
roofs. Their covered interiors and the mains inlet's internal flange pocket,
cord passage and blind insert pilots remain free of supports in the ceiling-down
rear-quadrant print. The inlet's broad stock joins the west flank and ceiling;
its rim bears on the pocket floor and its screws enter from inside. Exterior
trees remain on accessible surfaces outside the native exclusions.

The **PRV chase's closed roof leans from the −X wall too**. Where its open exterior groove
becomes the closed fall, the groove's roof is level across the
 show-skin section: it looks print-up on back-top and meets the show
face square. The closed passage's roof is one X plane
from its liner inside the flank through the wall and out to the cold-core lip, and the lip
keeps of solid land below the square mouth. The lip ends
at X−90.75, 0.25 mm outboard of the core's X−90.5 flank. Back-top's share of the rib
stands square on the seam rim, which looks print-up on that piece. Its exterior crown is flat
at the lip's height across the to the grown flank, with the complete
first printed section carried by removable tree support. The inner passage roof keeps its
45° plane. The mouth's floor is a `vent_channel_w` bridge
between the passage's two jambs. The exterior groove edge, the square passage and the back
slide's opening remain on their own datums.

## Fixed fluid supports

The bare ASSE lies above the pump with its vent west. Two 6 mm wide saddles at
Y346 and Y369 join the fixed roof, open toward −X, and retain 3 mm below the
nominal barrel. Each has a separate tie window. The straight TPU cuffs and vent
adapter stay clear of the bearings. Two fixed-roof bearings support the transverse
water regulator's two native diameters; its collets remain free.

The folded gas regulator and separate check use two east-wall saddles with tie
windows. Back-top carries those saddles, the meter's collar bearings and the
continuous ceiling. Main component
placements, actual fitting engagement, insulated routes and support loads retain
the scope stated in the [arrangement](/hardware/manifold-layout/above-core.md).

Thread ties through the empty support windows before fitting bodies. The native
clearance readings establish geometric separation at the recorded datums; they
do not establish tie retention, printed load capacity or lifetime.

## Integral pump mount

`enclosure-front-top` contains the upper inverse of both pumps as part of one broad body.
The surrounding stock continues from the pump-bearing region into the display housing and
existing roof silhouette. Only the fitted pump rooms, display receiver, tube clearances,
wire passages, snap receivers and required fastener holes remove material from that field.

The separate `enclosure-pump-retainer` (`build_pump_retainer`) has a broad rectangular core,
 across, fore–aft and
 high. Its fitted lower wells preserve the head profiles and
flat skirt lands supplied by `pump_tray.py`. Its outside ends on broad planes rather than
following the outlines of the pumps. An integral full-depth wing on each side snaps into
front-top’s flank receiver.

The pump holder stations are X±52.225, Y45.859, Z214.925. The actual seated flange is
, below that holder datum. The
reference boss and motor share an axis 1 mm toward Y− from the head datum; their upper
inverse follows Y44.859. Keeping those two axes distinct preserves the fitted lower wells
and the four existing tube axes.

Each molded skirt is deep. Its fitted lower land remains at
, with continuous bearing on X−, Y− and X+ and between
the two tube passages on Y+. The integral upper bearing plane is
: the flange datum plus the supported-face allowance.
The retainer's nonbearing top ends at, leaving nominal
space between the printed halves. These face allowances describe the CAD and print
process; they are not a measured axial-play or retention result.

The fitted octagonal boss openings use the case-derived profile and its ledges. The Ø37 mm
motor bores open into wider terminal rooms and close above them with 36° conical roofs.
The continuous stock fills the rest of the pump-to-roof volume, around the functional
hardware and cable rooms.

## Integral routing snaps

Back-top carries six direct tube seats and three single-arm cable clips on its
existing roof and wall stock. The quarter-inch fill guide uses the selected C2
section with a **6.35 mm bore** and **2.40 mm wings**. The five 4 mm tube seats
use **4.10 mm bores** and proportionally sized **1.52 mm spring wings**. The cable
seats match the relay ribbon, DC power pair and one V-K lead; no generic oversized
pocket gathers unrelated wires.

Both flavor tubes follow a broad, gentle rise to Z343 and run beneath two
paired roof stations at Y354 and Y390. Each station has one common filled base
with an 8 mm-long seat for each tube. The downward-facing mouths remain
accessible with back-top open. The funnel frame carries no flavor-tube support.

The [routing review](route-snap-review/README.md) identifies every station, its
print direction, cable dressing, installation order and current fit basis. These
features add no separate printed part or fastener. Reservoir A's fore pair seats
in two integral C2 clips on the cold-core lid at 13.5 mm centre spacing;
body-retaining ties keep their existing jobs.

The [combined coupon result](../../../../future/snap-fit-tests/2026-10-26-mark2-combined/physical-result.json)
accepts the C2 6.35 mm bore for present use and the 16 mm-span 4P ribbon clip's
fit and qualitative retention. The 4 mm tube sections, DC-1 pair seat and V-K
single-wire seat remain provisional. The coupon result does not establish the
complete back-top print's cleanup, installed release forces or lifetime.

## Prepared tubes and underside loading

Each pump carries two straight stubs of the machine's black
1/4-inch LLDPE. The pump head's housing clamps its BPT tube around each stub. Four open
passages in the retainer clear the molded casings and let the tubes stand straight toward
the tee wall. Each fitted casing passage is wide around the
 reference casing; each pair has
axis spacing.

Set the four tips with both pumps seated in the loose retainer on the bench. The existing
[tube setting jig](enclosure-pump-tube-setting-jig.stl) seats on its flat rear face at
 and sets the tips to. Tighten the pump-head
housings and remove the jig before approaching front-top; its broad body needs the space
occupied by the tee wall.

Thread the bare pump-end ribbon through the common wire passage, then crimp, ring out and
land its four Fastons on the loose motors. Raise the complete prepared pump/retainer unit
motor-first from underneath. Guide the flexible tubes through their individual
tee-wall bores. Draw wire slack aft without loading the terminals. Press upward until
both wings spring outward and their lower hooks seat on the receiver floors. Inspect both
engagements while front-top is loose and the tees, valve rows, display and funnel frame are
absent. The [assembly procedure](../../../assembly/internal-plumbing.md#3-flavor-manifold-v-a-through-v-j--y-a-y-b-y-c-y-d-y-f-y-g--pumps)
owns the complete order.

## Fixed plumbing behind the mount

Four purchased PP0208E tees receive the pump tubes on X±82.1 and X±22.35 at
. Each branch approaches its fixed tube from aft; the pump mount
stays in place. The extended branch collet grips the tube and the O-ring seals it. The
snap-fit retainer holds the pumps in front-top.

Each tee's upper collet takes one short tube up to its fore valve at
. Its lower return uses two trimmed stem elbows and one
continuous tube with two tangent bends below to reach the rear valve. Install all four prepared
tee, upper-tube and fore-valve groups straight from aft before fitting the rear valve row.
Complete both rows and the returns while front-top is loose, before its aft slide over the populated
lower enclosure. The [pump-mount record](../pump-dock/README.md) supplies the fitting
stations and physical qualification scope.

## The underside opening and tee wall

Front-top retains its continuous front wall and both
 flanks. The underside loading opening spans X−98.5..98.5, from
Y14 to the tee wall at. The retainer has running clearance
around its rectangular core and at the ends of its snap wings. Its bottom is.
The front face and rounded enclosure corners belong to front-top.

The tee wall is one broad slab, deep, reaching aft to
. The fore collet band ends at the bore
face,. Each tee stands in a teardropped
 branch bore, with its extended collet in the smaller
 opening ahead of it. The pump loads with only its flexible tube stubs attached;
the stubs feed through the closed bores. The bore-face land stops the fixed
branch barrel; its lower return stops the tee aft.

Front-bottom's front and flank lips drop over the pump-loading run. Two broad lower feet
support the tee wall's end regions, each ×, with
 section and a underside. The remaining flank
rails keep their complete working runs aft of the tee wall.

## Pump snap retention and release

Each side’s carrier, wing and lower hook share the retainer’s complete Y14.25–82.265 span.
The receiver spans Y14–82.515, leaving 0.25 mm at either end. Each 2.0 mm wing
has a 22.25 mm root-to-bearing length and a tangent 1.5 mm inside root blend.
The roots are at Z197.445; the retaining hooks are at the bottom. Each hook
has one 4.6 mm-high planar insertion face running directly to the pointed
outer corner of the flat retaining face. The matching receiver pocket clears
the complete insertion face and retains its broad backing.

The hook-bearing plane is Z175.195. Each seated hook reaches |X|101.1,
providing 2.6 mm of bearing past the |X|98.5 receiver edge. The relaxed tip
spreads outward 0.35 mm and the assembly represents a 0.10 mm seated spread.
The receiver floor is Z174.795, with 0.4 mm static catch clearance. The
inward spring corridor is 3.35 mm wide; the fitted pump wells and skirt
bearings keep their dimensions.

One centered, 5 mm Y-wide screwdriver opening per side passes through
|X|98.5–104.5 and opens from Z170.195. Its continuous 45° corbel runs from
X101.1/Z180.295 to X104.5/Z176.895 on the right, mirrored on the left.
The opening retains 3 mm of outer wall; the receiver pocket retains 6.4 mm
of backing. The receiver’s lower edge supplies the fulcrum for pushing
the wing inward until its hook clears. Support the pump/retainer unit
while releasing both sides. Complete pump removal with front-top open
and the pump plumbing and motor leads disconnected.

The retainer prints on its Y-minus end, with the spring’s X/Z bending
plane within each layer. Front-top retains its seam-plane print pose.
The [cartridge snap trial](../../../print-tests/pump-cartridge-snaps/README.md)
binds the production parts, receiver sample and outstanding physical checks.

Derek's [accepted holder fit](../../../reference/kamoer-kphm400/physical-fit.json) reports
firm holding with no vertical play in its identified separate cradle and cap. The
[native scan review](../../../reference/kamoer-kphm400/scan-review.md) retains its measured
surface and registration scope. The integrated upper half and underside retainer use direct
two-face skirt capture; no physical assembled fit, vibration, load capacity or lifetime
result is claimed for the snap-fit mount. The [pump-snap review](pump-snap-review/README.md)
records its exact inputs and geometric scope. The [three-screw mount receipts](pump-mount-review/README.md)
retain their separately identified exports and assembly queries.

## The pump lead

DC-5 and SIG-7 use one rear wire passage through the continuous pump/display body. Its
 diamond passage is centred at X0/Z280 and opens through Y99.
Its rear upper half opens straight over the bulkhead lip, leaving no tapered banks.
The pump branches reach their terminal rooms through a cross passage between the two motor
axes. Its level floor at Z274.224 joins the motor rooms and shared outlet beneath a 45° roof.
SIG-7 reaches the open display receiver through one straight-sided corridor containing the
terminal entry, rising link and chimney.

Thread DC-5's bare pump end from aft to the open underside before crimping the Fastons.
Ring out and land the motor pairs while the pumps are loose, with +X serving pump A and
−X serving pump B. Draw slack aft as the prepared pump/retainer unit enters motor-first.
Thread SIG-7 with its display end free and the facet open. Both ribbons stay bare through
the shared passage; the display braid ends aft of the mouth. Complete the central board
connections through the open funnel aperture before the frame goes in. Unplug J13 by its
housing before separating the quadrants.

The [installed wiring model](../../../wiring/installed/) supplies the proposed routes;
its native review records their geometric scope. The
[fixed pump lead review](fixed-pump-lead-review.json) describes only its identified earlier
exports and does not qualify this passage or actual harness dressing.

## Display housing

The machine display sits on its declared inclined plane within the enclosure's
outside dimensions. Its tangent blend into the roof follows the shared swept
profile. The upper edge in [`exterior.json`](exterior.json) follows the display
sides and front lip continuously through the standing columns. Front-top's fine
layers follow the inward upper rounds and the display-to-roof blend.
The print-down roof fill follows the curved display junction at both side edges;
it joins the retained rounds without an exposed horizontal underside.

The flat display bezel uses the enclosure's nominal wall section and the rear
nameplate's rounded-corner and shallow screw-seat style. Side borders carry the
screws with equal insets from the nearest outside edges. Its face seats flush with
the display facet. The [mount dimensions](../display-cover/mount-dimensions.json)
define its glass lap, gasket stack, counterbores, short inserts and engagement.

Blind insert pilots sit in the broad housing stock beside the glass and PCB.
Install the inserts from the open display face. The flat gasket ring spreads the
light clamp load around the glass border. Start all screws before drawing the
bezel onto its seats.

The display sits off the box's middle toward −X, and the
[status plate](../display-cover/README.md#status-plate) takes the rest of the facet's flat
run, with equal margins at both side edges and between the two. Its seat is the cover's in
form: a flush pocket with blind pilots for the same short inserts, its screws level with the
cover's. Under the plate's light a bore sets the LED back behind the aperture. A channel from
the bore's foot to the display's PCB pocket carries the LED's leads; its section stands on one
corner in the print frame, so no face of it overhangs flat.

The 19 mm housing joins the enclosure sides and the continuous pump-mount stock. That
stock runs to the existing outer roof around the actual display pocket; it has no separate
ceiling over an empty pump-to-display storey. The display backing presents one broad aft
face at Y92.75, 0.25 mm ahead of the funnel frame's flat front. Front-top keeps its complete
9 mm flanks to the roof opening. The receiver pockets and the shared pump/display passages
are the functional cuts in this broad field.

The vertical flutes fade over their existing 5 mm end field as the front and sides
turn into the smooth top curves. The rounded display bezel and funnel rim remain
smooth. Print meshes use a 0.005 mm absolute surface tolerance and 0.05 radian
angular tolerance before the flute field is cut.

The display loom shares the pump lead's rear exit at X0/Z280. Its unbraided
ribbon follows the common display corridor from the module's nominal rear terminal plane
to the shared exit; the rear mouth also carries DC-5's pump ribbon. Keep both runs clear of the
frame seats and closing slides. The [wiring procedure](../../../assembly/wiring.md) owns
termination and dressing, and [The pump lead](#the-pump-lead) gives the bench threading order.

## Funnel opening

The silicone funnel sits in a separate solid PET-GF frame, extended 35 mm aft.
The drain and collar share the center at Y179.19575.
Its brim bearing is Z349 and lower body reaches Z299.9. Two full-width end
corbels stand 30° from vertical. The flange is 196.5 mm wide and lower body
176.5 mm wide; its aft shoulders clear the upper M5 seam blocks.

The frame drops vertically through both upper shell openings and seats on four
broad ledges. Four recessed M3 × 12 screws engage full RX-M3×5.7 inserts in the
shell. There are no frame slide rails. The complete silicone brim retains 3 mm
of bearing stock. Its apron covers the screw wells; lift the silicone for access.

The drain cradle snaps into the frame's lower web and supports the elbow and
standing drain stub. Finish the tubing and PCB connections beneath the open
aperture, then fit the frame, engage the cradle's snap seat and complete the
drain connection. The plug, stub, elbow and cradle travel with the frame;
disconnect the V-B feed before lifting it. The
[drop-in review](../../zone-c/funnel/drop-in-review/native-review.json) records
nominal fastener stacks and sampled motion; the
[funnel source](../../zone-c/funnel/README.md) owns its dimensions and physical
qualification limits.

The upper insert mouth is Z265 and the head seat is Z347. The fully threaded
M5 × 100 retains 9.5 mm of insert engagement and ends at Z247 in a blind pilot
with 2.5 mm nominal tip clearance. The source allows ±0.8 mm of screw length,
leaving at least 1.7 mm beyond the longest tip.

## back-top's ceiling

Back-top prints on its exterior roof face at Z355. The 9 mm slab's ordinary
underside is Z346. Broad pockets over the ASSE and gas fittings retain 3 mm roof;
the water-regulator pocket retains 6 mm. The source data names each pocket's
plan and top plane, and `_above_core_shell.py` constructs the fixed supports
from the same part frames. The ASSE’s two east-sector seats stand at Y340 and
Y364. Their broad lower plane is Z315.926, above the populated core’s meter
during the back-column ride; the circular bearing retains at least 3.34 mm of
stock beneath its west edge.

Aft of the funnel opening the slab is continuous, with component recesses and
no access panel. The funnel opening and its four frame ledges span the front/back
roof seam.

The rear nameplate's plain field stands 2.2 mm beyond the rear wall. Its
complete 3.6 mm backing clears the cold core by 1.09 mm. The named receiver
and disposal lettering are the exterior-stock exceptions to the quadrant
silhouette; the wall and component datums stay fixed.

## Regenerate

    python3 tools/run.py -- cargo build --release --locked --manifest-path tools/hsm/Cargo.toml -p hsm-enclosure-back-top --bin enclosure-back-top
    python3 tools/run.py -- tools/hsm/target/release/enclosure-back-top

→ back-top's `.step`, `.step.npz`, `.step.mesh` and `.stl`, from the declared Box. Each printed
piece has its own program, named as its files are: `enclosure-front-bottom`,
`enclosure-front-top`, `enclosure-back-bottom`, `enclosure-back-top`, `enclosure-pump-retainer`
and `enclosure-pump-tube-setting-jig`. `enclosure` reads the shown pieces' fine models and writes
`enclosure.step`, the enclosure model, with the pump dock's tees and stem elbows.

Each program is compiled from its own recipe, the numbers it takes and the construction it
shares, all typed Rust:

- [`numbers/`](numbers/): the Box's types, the wall, seam and boss constants in
  [`numbers/shell.rs`](numbers/shell.rs), the catalog, the structure and the rear wall's lands;
- [`retainer-numbers/`](retainer-numbers/) and [`dock-numbers/`](dock-numbers/): the numbers
  front-top and the model take from the retainer and the dock;
- [`quadrants/`](quadrants/): the construction two or more quadrants share, and
  [`front/`](front/), the front half both front pieces are cut from;
- each piece's own recipe: [`front-bottom/`](front-bottom/), [`front-top/`](front-top/),
  [`back-bottom/`](back-bottom/), [`back-top/`](back-top/) and [`retainer/`](retainer/), the jig's
  in its program;
- [`solid/`](solid/): the plan, its evaluator, and the steps every piece's files share.

[`solid/cache.rs`](solid/cache.rs) retains exact intermediate solids under
`.cache/realized/rust-stages`. An entry names its operation, input identities and
compiled geometry implementation. The evaluator loads reusable stages before
constructing their ancestors. Missing or unreadable entries are rebuilt; storage
is bounded and disposable. `HSM_STAGE_CACHE_OFF` requests fresh construction.

The seam band is an authored addition before the openings and joint limits.
Those operations apply to both it and the mechanical body. Back-top retains the
body's completed print surface independently, so a band-only dimension edit
reuses it. Editing [`exterior.json`](exterior.json) needs no recompilation.

The piece payload shows the printed triangles directly. `publish_now.py` grafts
completed piece payloads into the existing enclosure and appliance viewers;
print preparation and slicing consume the exports separately. Optional
`HSM_STAGE_PROFILE` and `HSM_PHASE_PROFILE` paths record requested timing data.
