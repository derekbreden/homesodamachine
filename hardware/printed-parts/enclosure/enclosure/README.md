# Enclosure

What the pieces have actually been printed in, and at what settings:
[print-log.md](print-log.md).

A PET-GF15 box. [3 mm](WALL_T) is the section a piece starts from and every exterior
wall carries at least [6 mm](LIP_UNDERWALL), each taken INWARD so the silhouette
and `interior_x` both stand still: a bottom piece's three lipped sides get
[6 mm](LIP_UNDERWALL) as the lip's own skin carried to the slab, front-top's ±X
flanks are [9 mm](FRONT_TOP_FLANK), back-top's are [9 mm](BACK_TOP_FLANK) and its
+Y wall [6 mm](BACK_TOP_WALL). The floor is the one section taken OUTWARD:
[6 mm](FLOOR_T) of slab under both bottom pieces, with the stated height struck to
its underside, so it stands in the silhouette and the cavity's floor plane — the
one the pack sets its bodies on — does not move. **Split into four printable pieces** — front/back × bottom/top, every piece inside the H2C bed. Each
column's top SLIDES onto its bottom on hooked rails; the two halves telescope and four M5
screws, two at each Y-seam corner, close the whole box.
It measures [215 × 466.3 × 361 mm](BOX_SIZE), and **width, height and the +Y wall
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
- **Height** is a stated [361 mm](APPLIANCE_HEIGHT), floor slab's underside to the
  top wall's outer face. The contents do not lift it; they have to fit under it.

**Depth** is stated at the back — `rear_plane_y` — and follows the pack at the
front, where the wall stands one `front_seam_clear` ahead of the frontmost body
placed by
[`../../../manifold-layout/enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py).
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
can still be in the lip's way there, as the PSU's aft corner is at the X+/Y+ column.
`_lip_denied` measures that lane per column, each seam answering for its own half of
the box (`z-seam-front-lane`, `z-seam-back-lane`) — the ring read one rail deeper down
the straight runs, where the groove, arm and head ride. The cold core spans the
seam in both columns.

The plane stands where the seam's own machinery fits the pack: the seam ring's foot
over the condenser's fin crown, and the rim under the forward valve tray's
wall roots (`z-seam-under-deck` — a plate roots on a wall only above the rim).
Each root follows its outermost valve row. The staggered aft tray's lower band and
its foot run below, inset on the lip's own face. The ring's front segment across
the flat span is the bay's (`_front_flat_lip_drop`): the bay floor stands in that band
and the pump heads run down through it on their way out, so the
flat front carries no lip there at any height.
`main()` prints each seam, how it landed, and the band the bed allowed it.

`enclosure.py` exports the four printable pieces (`enclosure-front-bottom`,
`enclosure-front-top`, `enclosure-back-bottom`, `enclosure-back-top`), the
`enclosure-pump-cartridge` that slides out of the front pair, and
`enclosure.step` — all of them as separate solids in assembled position, seams
intact (mirrors `faucet/faucet-shell`).

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
under the core, and a lap inside it with one running fit between its members cannot keep
both members at the nominal 3 mm section. The corner knuckle stacks and their M5 rods align
the halves.

Each ±X corner of that seam is a **stack of knuckles**: blocks of one piece standing in the
other's overlap, alternating up the corner, with two vertical M5 screws through them
(`_y_stacks`). A front knuckle roots [3 mm](Y_STACK_FRONT_ROOT) fore of the seam in its own
flank and runs aft one running fit inside the back piece's skin; a back knuckle grows out of
that skin and on into the thickened flank. Every knuckle stands in the [17.8 mm](LIP_LEN)
overlap and the [14 mm](SIDE_BAND) side band, its screw mid-overlap in Y.

- **The lower stack** is a three-knuckle hinge inside the bottom pieces: back-bottom's
  knuckle over the handhold, front-bottom's, and back-bottom's under the Z seam. An
  [M5 × 120](LOWER_ROD) drives up from the handhold ceiling at Z[29.25](Y_STACK_CEILING),
  its head in the lower back knuckle, through front-bottom's knuckle into a ruthex RX-M5x9.5
  pressed into the top of the upper back knuckle, flush with the Z seam; its tip stands just
  past the insert's open top. Back-bottom holds the screw at both ends and front-bottom's
  knuckle hangs on it between them, so a pull that opens the seam meets the screw at two
  faces, both on its plain shank, one wall below its 22 mm of thread. Nothing of either
  bottom stands above the Z seam.
- **The upper stack** stands under the roof, over the tap-water line on the −X flank:
  front-top's knuckle, rooted on its lip band at Z[272.5](Y_STACK_UPPER_FLOOR), up to its
  insert's mouth, and back-top's from Z[299.9](Y_STACK_DATUM) to the roof. An
  [M5 × 60](UPPER_ROD) drives down from back-top's roof into the insert, so tightening it
  holds front-top up against back-top, which also locks front-top's slide. Front-top's −X
  knuckle gives its inboard-aft edge a 5.1 mm, 45° chamfer to the flavour line that turns
  past that corner under the frame (`y_stack_upper_chamfer`).

No knuckle needs support. Each face that prints facing down rises 45° off its own piece's
stock: front-bottom's knuckle rises aft off its handhold roof, back-bottom's upper knuckle
rises inboard off its skin and front-top's rises inboard off its lip band; back-top prints on
its roof. The slopes run across the slide or close as the front half slides aft, and a top
that rises toward a free face levels off one wall short of it. Every face between knuckles
keeps a [0.25 mm](Y_STACK_GAP) running fit, measured square to the face, including the two
the upper screw pulls together.

The screws pass through printed [Ø5.6](Y_STACK_CLEARANCE) clearance holes. Each insert and
the manufacturer's minimum stock round it, [Ø11.6](Y_STACK_INSERT_BOSS) about the axis, fit
inside the side band. The lower axes stand [9.25 mm](Y_STACK_LOWER_AXIS_OUT) in from the exterior,
where the head passes the handhold's inner wall on its way up; the upper axes
[9.8 mm](Y_STACK_AXIS_OUT), which leaves 3 mm outboard of the roof opening and 3 mm inboard
of front-top's insert. Each head bears on a printed floor in a Ø9 opening,
[11.55 mm](Y_STACK_LOWER_CBORE) up into the handhold ceiling and [8 mm](Y_STACK_CBORE) down
into the roof. The lower opening ends on the plane of the handhold's inner wall; the upper
one runs on into the funnel opening. Seat the heads with a 4 mm hex key and stop when they
meet their floors; the printed joint has no qualified installation torque.

**The lower opening and the handhold's lip:** the lip's R6 roll and its print chamfer take
the first 2.29 mm of the lifting ceiling from the outer face, and the lower opening begins
4.75 mm in, so 2.46 mm of flat ceiling stands between them; 1.2 mm above the ceiling the
stock between the opening and the roll is 3 mm. The opening cannot move inboard: the head
passes the handhold's inner wall with 0.14 mm to spare, and that wall stands 0.25 mm off the
cold core.

Remove the two upper screws to free front-top, which draws fore off its rails. Removing all
four lets the halves part. The upper screws need about 60 mm of clear space above the roof,
the lower screws about 125 mm below the enclosure with the flank supported over the bench
edge. The handhold's inner wall over the seam is front-bottom's, standing on its own floor
tongue to the joint with back-bottom's wall, one fit under the lowest knuckle
(`_handhold_frame`).

A drop that opens the Y seam loads the screws in shear at the faces between knuckles: two
per lower corner, one per upper corner. The floor tongue supplies no tensile interlock. Drop
resistance requires assembled physical qualification.

## Exterior disposal warning

The +Y wall of back-bottom carries the full [household disposal warning](../../../markings/README.md)
as integral raised lettering in the enclosure's own material. Each line is centered on the
rear wall. The bottom of the lettering stands [14 mm](DISPOSAL_BOTTOM) above the enclosure's
base. Its H capitals are [6.5 mm](DISPOSAL_CAP_HEIGHT) high, and the letters are raised
[0.6 mm](DISPOSAL_RELIEF) from the wall.
The generator measures every warning letter's outline against the 6.4 mm minimum.

Back-bottom prints floor-down, so the letters stand on a vertical wall. Each letter's outline
is raked: it is carried out of the wall and up at 45° at once, so every stroke's underside is
a 45° face the layer beneath carries, and the letter's face keeps its whole outline.

The wall stays flat beneath the text and its [5 mm](DISPOSAL_MARGIN) margin, over a
[181.0 mm](DISPOSAL_FIELD_WIDTH) by [64.5 mm](DISPOSAL_FIELD_HEIGHT) field. The surrounding
flutes fade into this smooth area. It is the wall's own surface, without a border or a
separate carrier. The raised text is fused into the STEP body and retained on the printable
STL and viewer payload after the mesh flute cut.
The production slice adds no support contacts beneath the lettering.

## Exterior form

The top shoulders, lower handhold rims and cartridge hand-pocket rims use the
same R6 roll from a fluted wall into a smooth surface. The roll continues around
each opening's complete perimeter. R6 inside corners make R12 outside corners
at the hand openings, matching the enclosure's R12 standing corners. The top's
front roll is R12 and its longer turn onto the roof is R18.

The flutes use the same pitch, depth and 5 mm runout on these surfaces. Their
ends taper into the rounded shoulder; the smooth shoulder continues through
the corner and onto the lifting ceiling or pocket wall. The broad standing
corners carry the flutes around them at constant arc-length spacing.

The display's flush cover has R6 outline corners, with an offset R6.3 seat.
Its optical opening follows the glass. The funnel's mouth, collar and brim
are concentric rounded rectangles with constant-width bands; the supporting
recess follows the brim. The thin rear nameplate uses a smaller R3 outline.
Hardware openings follow their mating parts. The rear top edge remains square.

## Handholds

One handhold in each ±X flank opens through the standing floor. The recesses are
[80 mm](HANDHOLD_LENGTH) long in Y, centered at **Y[214 mm](HANDHOLD_Y)**, and
[35.25 mm](HANDHOLD_HEIGHT) high from the slab's underside to the uncovered lifting ceiling.
The [6 mm](HANDHOLD_CORNER_R) inside corner rounds join the ceiling to the end walls.
The exterior lifting edges retain their [6 mm](HANDHOLD_EDGE_R) rounds.
Each ceiling carries a full [12 mm](HANDHOLD_ROOF) section,
joined to the floor by the opening's end walls and to the corner stack above it.
The R6 roll joins the flat lifting ceiling, end walls and fluted exterior
tangentially, including the two corner blends. Its full section and flute
runout follow the top's side shoulder and both cartridge hand pockets.
One complete handhold profile spans both Y halves and is mirrored onto the two
flanks. It cuts the finished shell and seam blocks together. The central lifting
ceiling remains exactly planar; the exterior transition and both rounded ends
share the same boundary across the seam.

The printed ceiling is the exposed gripping surface. The end walls are complete;
there are no grip covers, cover seats or wing slots. Tree(auto)/Default supports
the flat ceiling during printing. Surface finish and gripping comfort remain
unqualified on the complete production handholds.

The [3 mm](HANDHOLD_WALL) inner wall stands between |X|90.75 and |X|93.75,
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
**4.5 mm arm** on its mouth, standing one [0.25 mm](SLIDE_SLIP) inboard of the top's own wall,
and the arm's **head** steps back out over the **groove** between them: a
[5 mm](FRONT_HOOK_LAP) overlap on the front column and [5 mm](BACK_HOOK_LAP) on the back.
The top piece's wall runs to the mouth at full section — the **foot**, its caught face
[8.7 mm](HOOK_FOOT) over the mouth — with a **notch** in its inboard face that swallows
the head. Back-top closes that channel back to the full wall on one horizontal roof;
front-top alone uses a 45° roof over the void it prints mouth-down. The storey is [14.8 mm](Z_RISE)
mouth to rim, and **the flavour deck is its ceiling** — the rim stands under the lowest
valve plate (`z-seam-under-deck`), which is the whole height the box has to spend here.
It buys the groove first: [9.2 mm](HOOK_NECK) of it, the top piece's own sliding tongue,
with [5.6 mm](HOOK_HEAD) of head over the front catch. The rear groove is
[9.45 mm](BACK_HOOK_NECK) tall with [5.35 mm](BACK_HOOK_HEAD) of head over it. That height is the Z seam's own — `lip_len` is the Y
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
the nominal 9 mm face on both sides: [6 mm](FRONT_RAIL_FOOT) in front and
[6 mm](BACK_RAIL_FOOT) in back. Each bottom hook carries a 5 mm bearing overlap at that
face's inboard edge. Their arms reach [10.75 mm](FRONT_RAIL_INBOARD) in front and
[10.75 mm](BACK_RAIL_INBOARD) in back from `interior_x`, inside the 14 mm body-free seam
band. Each catch lies wholly over its six-millimetre foot and keeps a complete exterior wall
outside its channel.

**Lifting a seated top lands each foot's flat top face on its head's flat underside,
along both whole runs** — [94 mm](RAIL_RUN_FRONT) per flank on the front column,
[232 mm](RAIL_RUN_BACK) and [220 mm](RAIL_RUN_BACK_W) on the back — horizontal printed
face on horizontal printed face after the specified clearance is taken up. The two
back flanks differ by the PRV passage: it crosses the −X run and takes
[12 mm](VENT_CHANNEL_W) of it, which is the figure that flank is already short by.
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
[12 mm](VENT_CHANNEL_W) where the one opening that has to cross it does, and the duct keeps
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
groove, arm and head reach [10.8 mm](RAIL_REACH) inward from `interior_x`, inside that same
band.
The **+Y wall keeps one `rear_seam_clear`**, the rear Z-seam lip's own thickness. That is a requirement
on the body where it meets one, not a rule about the wall: beside one — over or under
one — the band is the wall's own air. Of the three bodies on the slab only the cold
core meets the band at the seam's storey; the compressor and condenser stand wholly
under the mouth. The core's rounded fit pocket extends 0.35 mm below its nominal
floor plane: 0.25 mm running plus 0.10 mm cavity-floor transition allowance. The slab
retains 5.65 mm under that pocket. The print-corner relief runs
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
rear-wall bodies against it and `enclosure.py` builds the box to it, so the wall
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

## Electronics-bay boss corbels

The +X wall of back-top carries one horizontal boss for every mounting hole in the PSU, main
board, two relays and ground stack: 17 in all. back-top beds on its ceiling's outer face, so its
print-up is machine −Z (`enclosure.print_up`) and on this piece print-down is machine-up: a face
that looks up in the machine is the face the slicer has to carry. Each stem is a D in its
mounting plane — the round crown keeps the M3 insert annulus compact, and its 7 mm flat chord on
the machine-top side of the hole gives a full-width 45° corbel one continuous print-down plane
to carry. The D section runs all the way to the body's own mounting face, so no round pipe is
left bridging between a generic support block and the part.

`enclosure_assembly.wall_mounts` offers that corbel, struck for back-top's print-up, all the way
to every mounting face and intersects the offered material with the installed pack. Where a body
crosses the offered wedge, the wedge is held back to one millimetre past that body's exact
envelope; where the body crosses it to within that clearance of the wall, no wedge stands over
the blocker itself, and what is clear beside it is a wing only where `enclosure.east_boss_wings`
lets one stand — a wing at each end of the span roots a bridge between them, and a stub carrying
the minority of the span stands down so the chord is offered whole. The two relays' holes come
in pairs 13 mm apart at either end of each board, and each pair stands in one flat-topped bar
with two bores, carried on its upper hole's corbel where the pair stands one over the other and
on one wedge across the bar's span where it stands side by side; the other nine stems stay
D-shaped and whole across their holes.

Four exact-pack rectangles complete this field (`east_mount_fills`), and their names and bounds
are part of the pack rather than a proximity rule. The ground-stack stem stands under one
full-width column from its D chord into the ceiling slab; that column replaces its candidate
corbel. The aft upper main-board stem and relay #2's upper two-hole bar share one rectangular
pad, with all three bores cut through the fused block. Their separate candidate wedges are
omitted, leaving one flat box rather than three partial triangles. Relay #1's two vertical
hole-pair bars each continue on their existing 2.25 × 7 mm footprint as one rectangular column
into the ceiling, with both corbels in each pair omitted atomically. The upper pad's crown meets
the lower face of relay #1's aft column. `east-boss-fills`
intersects all four rectangles with every installed body and admits only the four clear results.

The joined main-board/relay-2 pad's first printed face projects only 2.25 mm from the east wall,
with its crown meeting relay #1's aft column. The production slice prints that wall-rooted
projection with no support body or interface at the pad.

The five Wago wells on the same wall are carried the same way (`enclosure._side_wells`). The
row's tower stands on the ceiling slab's interior face (`enclosure.back_top_ceiling_face`) as a
column: the air over its machine-top face is free of every placed body
(`enclosure_assembly.stand_wells`), so the tower's own section goes straight up to the slab,
and the three-well row on the −X wall stands the same way. Each pocket keeps its two `wago_roof_tab` tabs on its floor, with the 45° ramp folded
on the wall between them, and the complete `wago_well_wall` section on its roof; the lug rests
on the two tabs and the wall's press fit locates it.

The manifold junctions share the +X front-top flank at Y169: the J1 221-420
is centred at Z280 and the J2 221-415 at Z246. Their pockets retain the
3 mm wall section. The lower pocket has a full lid; the upper pocket keeps its two tabs
and ramp, and between the tabs the funnel frame's foot clearance comes down to its lid, so the
ramp ends on that clearance's outboard face. Both connectors face inboard, with room for their
wire entries and lever travel below the funnel frame. J1 branches feed V-A through V-H; J2
branches feed V-I, V-J, the condenser fan and V-K. Their routes and remaining harness
qualification are described in the
[wiring schedule](/hardware/wiring/ac-wiring-schedule.md#loom-terminations).

## Condenser cradle

The condenser's four sheet flanges are the block's whole purchase. Its two fore flanges slide
into rails on the front wall; its two aft holes screw into fingers on a standing fin at the +X
wall. The base rail and lower finger run to the floor slab. The crown rail and upper finger do
not: each carries its entire down-facing plane on a 45° corbel rooted on the wall or fin it grows
from (`_cond_cradle_corbel`, `_cond_mount_corbel`).

The crown wedge is only the rail's [3 mm](COND_SLOT_GRIP) reach. The aft wedge is longer, but it
lies wholly in the donor block's open end recess and stops on the fin's west face. The condenser stays fixed and the closer
one keeps `cond_mount_clear` of assembly air.

Each fore-flange groove keeps its exact [0.9 mm](COND_SLOT_OPEN) opening at the seated wall stop,
then its roof rises toward the bay at 45° and leaves through the rail's aft face [3 mm](COND_SLOT_GRIP) higher, a full rail wall under the crown.
The groove keeps 0.25 mm on each face of the sheet at its datum. Its sloping roof prints without support.

## The box closes in four motions

The slides fix the order, and the order is the service story backwards. **Front column**,
on the bench: the compressor bay seats in front-bottom, and front-top — carrying the
flavour pack made up into its trays and tee wall — slides AFT onto it, in from the front. **Back column**,
on the bench, empty: back-top — carrying the chain, the meter, the ceiling's anchors and the
wall electronics — slides FORE onto a bare back-bottom, over nothing. **The core rides in
through the mouth**: the closed back column stands upright and the cold core enters over
the open Y-seam mouth and slides aft to its seat on the rear lip, under the hold-down
feet (each fore arris eased 45° for exactly this), past the chain and the bulkhead unions,
into the pockets their stems land in; the lid's tenants — the water pump and the rest —
go on through the same mouth after it. **Then the halves telescope**: the front assembly
slides aft into the back, its corner blocks closing on the core's front face, and the four
seam screws go in: the lower two up through the handhold ceilings, the upper two down
through back-top's roof. Service is the same door swinging the other
way: with about 60 mm of access above the roof, **the two upper screws alone free front-top**,
which draws fore off its rails into open air with the box still standing where it is —
the flavour pack, the trays and the tee wall coming with it. All four screws out takes
the front assembly fore and off, opens the bay through the mouth, brings the core out
fore, and back-top slides aft off its rails if the tub itself is the work.

## Cold-core grips

The cap crown is the core's Z253.4 nominal reference. The [native fit review](y-seam-fit-review.json)
identifies the five external printed core bodies individually and checks the enclosure's
finite floor, flank, crown and hold-foot faces against their actual native material.

The core is the heaviest body in the machine and the one with no hole in it — a foamed cup
under a screwed cap, plain skin the whole way round. What fastens it is the closed box: **the
seams stand every piece against its neighbours**, so a feature printed on one piece stands
over a body sitting in another, and the front-bottom, the back-bottom and the back-top close
on the core together.

Four features, two mirror pairs, and nothing on either that is not a face of the core:

- **Front corner blocks** (`_core_stops`, on `enclosure-front-bottom`). A block in each front
  corner of the slab, [38 mm](CORE_STOP_WIDE) across — the ±X wall inboard to one corner round
  past the tangent — and [40 mm](CORE_STOP_RISE) off the slab. **The pocket in it is the core's
  own rounded plan outline offset by 0.25 mm**: a Ø[24.5 mm](CORE_STOP_BORE)
  bore on the round's own axis outboard of the tangent, and the core's own flat front face
  inboard of it. So the block bears flat where the core is flat and round where it is round —
  the flat bounds forward travel and the round bounds sideways travel and yaw after the
  modeled allowance is taken up. The web ahead of that outline is [6 mm](CORE_STOP_WEB) at every point of it,
  including the tangent, where a bore alone leaves it thinnest. Underside on the slab, outboard
  face on the wall: a corner bracket in one piece with both faces it stands on, the card slot's
  own form.
- **Aft brackets** (`_core_holds`, on `enclosure-back-top`). A right trapezoid in section,
  [9 mm](CORE_HOLD_WIDE) wide: the bearing face along the cap from [12 mm](CORE_HOLD_REACH)
  forward of the core's aft face back to the wall, a leg [40 mm](CORE_HOLD_RISE) up that wall in
  the `rear_seam_clear` band, and one straight from the head of the leg down to the foot's tip,
  [8 mm](CORE_HOLD_LAND) over the bracket's foot plane. The whole bracket profile stands
  0.25 mm above the core's cap crown, putting the cap-facing foot at Z253.65.
  This face prints upward with back-top inverted and adds no supported-face allowance.
  The straight web carries
  the flange. The lane is the one strip of the aft crown clear of
  the water pump inboard, the electronics bay outboard and the +Y wall's two flavour unions in the
  band, taken on both flanks so the pair is a mirror.

The whole core pocket follows that same rounded plan with 0.25 mm around it,
from Z−0.35 under the core to Z253.65 above its cap crown. Its floor allowance is
0.25 mm running plus 0.10 mm at the cavity-floor transition. The remaining floor is
5.65 mm thick. The floor, front blocks, rear seam band and cap brackets bound
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
the opposite gusset face is 25° from vertical and lays on the preceding layers.
The brackets take no print support.

## The reeded skin

Every standing wall is **fluted** — half-round grooves [4 mm](FLUTE_WIDTH) across and
[1.2 mm](FLUTE_DEPTH) deep, the profile `cadlib/reeding.py` carries and
the corner coupon at `c14bb2fff` was printed on. That coupon is this box's own corner
at this box's own `wall` and `corner_round`, so what printed there is what prints here, and
neither can drift from the other while they read one function.

**It is in the MESH and not in the solid**, and that is a decision rather than a shortcut. The
fade is what makes the texture look made rather than applied, and the fade is a FIELD OVER THE
SURFACE — how far a station stands from the nearest place the show face ends. A boundary
representation can carry a fade that runs level, because a level fade is a loft; it cannot carry
one that follows an opening's rim, a pocket's edge and the rounded display surround all at
once. So the STEP is a smooth body and [flute_skin.py](/hardware/printed-parts/cadlib/flute_skin.py) cuts the flutes into the
mesh on the way to the bed. Everywhere else on the machine the STEP is the whole of the part;
here it is not, and the `.stl` beside it is.

**Nothing tells it where an edge is.** At every station it asks the piece whether it has
material AT the nominal plan — by level cut, not by naming features — and takes a distance
transform of the answer. A flank opening, a port chip's seat, the nameplate's pocket, the bay's
own mouth, the seam a piece simply ends on, the bed, the rounded top and display surround are
one fact to it, and every one of them gets the same ramp over [5 mm](FLUTE_RISE), on the same
smoothstep the coupon fades on. There is no list of edges anywhere, because there is nothing to
list.

A rim that runs WITH the flutes is not one of them: a groove ending along its own length has
nothing to stop. The Y seam is one, and so is every jamb.

**The field closes on itself.** [272](FLUTE_COUNT) grooves go round [1342 mm](FLUTE_PERIM) of
plan, struck by ARC LENGTH from a datum on the front wall's centreline — which is what carries a
flute across a [12 mm](COLUMN_ARC) corner turn at exactly the spacing it keeps on the flat. No
station restarts the array and no two arrays meet anywhere. The pitch is what that count lands
on, [4.9338 mm](FLUTE_PITCH) against the coupon's [5 mm](COUPON_PITCH). The **Y seam** — the
one straight line running the full height of both side walls — lands [1.3 mm](FLUTE_SEAM_MISS)
off a groove's centre, in the shadow that is already there rather than on a land.
**`flute-closes`** holds the pitch to the coupon's.

The bay's mouths are the opposite case: the field ramps out at each run's two ends
(`flute_rails`), so every mouth arris and the pump cartridge edge inside it stand on unfluted
wall. A rim landing in a groove is an arris tapering to nothing on the groove's floor, and a
wedge that fine at a 0.42 mm bead prints ragged — on the one line the user looks straight at.

The datum is a groove centre on **x = 0**, the plane the whole machine is struck about, so the
field is symmetric in x whatever its pitch.

**The box has a second field indoors.** What the field is struck along is a RAIL, and the outer
plan is one of them. With the pump cartridge in, the bay storey shows the two narrow mouth
returns outboard of the cavity planes; those two actual surfaces are two open rails.
`_bay_storey_segments` carries their one global arc coordinate from one mouth edge to the other:
[364.38 mm](STOREY_RUN) over the storey at z [177.8..284.4 mm](STOREY_BAND). The two open flanks
and the lower tee face advance the phase but carry no cutter: the former are air, the latter is
berthed or hidden, and the upper closure face stands on another Y plane. The datum remains
**x = 0** and the pitch remains [4.9338 mm](FLUTE_PITCH), so both ledges retain the machine's
inside phase. Each real surface is open; its two ends are edges like any other and the field
ramps to zero on them, as it does at both Z ends of the band, which keeps cutter caps off every
mouth and window arris.

**And a body berthed in the room is an edge too.** Inside a storey the piece has material at
the rail in places the pump cartridge stands in front of, and a face another body beds
against is not one anybody finishes. `flute_skin._shadow_mask` asks, at every station, whether
a berthed body stands between that face and the storey's mouth — the same question the show
mask asks, asked of the other bodies — so the bay wall carries flutes only where the pump cartridge
leaves it visible, and its functional receiver/seating band is left plain. Nothing is listed: the
lower cradle and top clamp are what the assembly stands there; the receiver wall is part of front-top.

**Nothing may relieve into the outermost [3 mm](FLUTE_BACKING) of a fluted face.** The exterior
profile ([print-log.md](print-log.md)) lays two wall loops a side at 0.42 and 0.45, so one
`wall` is 1.74 mm of solid perimeter and a groove floor still has all four of them, with 0.06 mm
to spare. Take more out of the far side and the two pairs of loops meet: the slicer stops laying
four walls, and the change in what it lays under the groove reads THROUGH to the show face as a
mark you can find with a fingertip. What a groove leaves is [1.8 mm](FLUTE_LEFT), and
**`flute-backed`** reads every stated section on a fluted face against the rule — with two of
them computed rather than typed, because the survey that measured this found them and the file
had not stated them: the measured backing below the front curve, and
`east_boss_bore_end` for an insert bore behind a corner round, where the turn carries the
surface inboard of the plane the bore was struck on.

**It is free to print.** Every groove runs down the build axis, so its own side surfaces are
drawn by the nozzle in XY, carry no layer quantisation at all, and hang over nothing. The ramps
are `flute_depth` of relief over `flute_rise` of height — [19.8°](FLUTE_RAMP) off the wall at the
smoothstep's steepest, against the 45° every relief on this box is struck at.

## The condenser's vents

**The vent is the flutes, pierced.** The condenser's fan draws through one flank of the block
and blows out the other, and both flanks of the box already carry the reeded field — so a slot
[3.1 mm](VENT_SLOT) across is struck down the FLOOR of every groove standing over the finstack,
on the field's own centres, clean through the [6 mm](VENT_FLANK_T) a bottom piece's lipped flank
carries. Both jambs run WITH the flute and the groove carries on past both ends of the slot at
full depth, so nothing crosses a flute anywhere here and no edge it makes is one the skin stops
on. Off-normal the wall reads as unbroken reeding; head-on it is a grille.

**The mullion is the governing number, not the section behind the groove.** A slot takes its
width out of the pitch, and what is left between two of them is [1.8338 mm](VENT_MULLION) at
[4.9338 mm](FLUTE_PITCH) centres — against the [1.74 mm](VENT_SHELL) of loops the exterior
profile lays (2 × 0.42 outer + 2 × 0.45 inner, [print-log.md](print-log.md)), which leaves
[0.0938 mm](VENT_SPARE) and ceilings a slot down every groove at [3.1938 mm](VENT_CEILING). The
two figures move OPPOSITE ways: the jamb stands half a slot off the groove's centre, out on the
half-ellipse where the groove is shallower, so the flank behind a jamb is
[5.2416 mm](VENT_JAMB) rather than the 4.8 under the groove's own floor — a wider slot never
thins the wall and only ever thins the mullion.
The coupon at `c14bb2fff` printed this scheme beside the ceiling slot and a full-groove-width slot
down alternate grooves, on a section of this same flank at this same pitch.

**Every groove, and the stations are the field's own.** `vent_grooves` walks `flute_centres` and
asks `plan_at` where each one landed, so a slot is struck at a groove centre by construction and
the vent follows the field if `flute_count` is ever retuned — there is no Y station typed
anywhere in the feature. A groove is in when its whole slot lies inside the block's AIRWAY: the
[34..148 mm](VENT_WINDOW) between the block's two recesses, which is finstack. The 20 mm at
either end is the sheet the box holds the block by, and the fan draws through neither.
[23](VENT_GROOVES) grooves stand in that window on each flank.

**In height the band is the FAN, not the airway.** What moves air through this wall is the axial
fan bolted to the block's own flank; the finstack either side of it is served by whatever that fan
pushes, and wall opened opposite it is opening on metal. So the band is the placed block brought
in [22 mm](VENT_FAN_RISE) at its base and [5 mm](VENT_FAN_DROP) at its crown —
[31..141 mm](VENT_BAND), a [110 mm](VENT_BAND_H) band, the fan's own footprint and nothing wider.
Both insets are read against the block where it stands, so raising the block raises the vent.

**Less whatever the flank carries behind that particular groove.** Nothing is listed: the piece
is asked, groove by groove, what stands ROOTED on its inner face, probing one
[3 mm](VENT_CLEAR) wall inward and keeping that same margin past both jambs and both ends. The
transoms are the opening vocabulary: if a root's margin enters one course, that whole segment
stays solid and fluted rather than becoming a one-off short slit. A single opening marooned past
such a land stays wall too. The MQ-6's two posts stop below the vent band, but its can chute is
cut through the added inner flank skin beside it. The two intake grooves whose jambs would leave
less than one 3 mm wall to that chute stay solid through the courses the chute reaches, and vent
like any other above it, there being no chute up there to leave a strip against; the chute is not
widened into a vent, and no strip thinner than a wall survives between the two openings. Over
the chute, the skin between two crossing slots on one flank of its arched roof ends level at
the crown of the can's sweep, square to both jambs. All
[89](VENT_RUNS_IN) realized intake openings are the full [24.5 mm](VENT_SHORTEST) segment;
[0](VENT_SHORT) have a different height.

**[3](VENT_TRANSOMS) transom bands cross that vent, and they are why it prints.** A mullion is
[1.8338 mm](VENT_MULLION) across. Pierced clean over the whole band it would stand
[60:1](VENT_ASPECT_BARE) — a picket that tall with nothing tying its top to anything. The brace
is **not** a bar between two mullions, and nothing stands at 45° across a groove: at
[3](VENT_TRANSOMS) heights — [57.5, 86, 114.5 mm](VENT_TRANSOM_Z) — the wall is simply **not
pierced**, so every mullion and both jambs run into one plate of full section
[4 mm](VENT_TRANSOM_H) tall. Nothing bridges and nothing grows out of a tower. What is left is
[4](VENT_SEGMENTS) slot segments of [24.5 mm](VENT_SEGMENT) apiece, and the four of them plus the
three transoms close exactly on the band — `vent_transoms` divides the band rather than listing
stations, so the layout stays symmetric about its own mid-height whichever of the three figures
moves.

**The groove runs through a transom unbroken.** Only the piercing stops. The field is struck on
the flank's whole plan, so a transom is invisible off-normal and the reeding reads continuous down
the wall — head-on it is a grille in four courses. Both ends of every one of those
[4](VENT_SEGMENTS) segments are closed by a 45° hip, the angle every relief on this box rises at:
each hip sits down inside the groove's own shadow, the sill only takes material away as the print
climbs, and the ceiling closes at exactly the angle the box supports nothing steeper than.

| | slots | openings | thinnest mullion | tallest opening | free area |
|---|---|---|---|---|---|
| −X intake | [23](VENT_SLOTS_IN) | [89](VENT_RUNS_IN) | [1.8338 mm](VENT_MEAS_MULLION) | [24.5 mm](VENT_TOWER_IN) | [63.3 cm²](VENT_OPEN_IN) |
| +X exhaust | [23](VENT_SLOTS_OUT) | [92](VENT_RUNS_OUT) | [1.8338 mm](VENT_MEAS_MULLION) | [24.5 mm](VENT_TOWER_OUT) | [65.5 cm²](VENT_OPEN_OUT) |

Both read off the built piece at the flank's mid-section, over the fan's own band. A pierced field
is [62.8 %](VENT_OPEN_PCT) open where every slot runs; the readings above are what the band came
out at with the transoms, the hips and the intake's rail in it. The tallest opening on either flank is [24.5 mm](VENT_TOWER) on a
[1.8338 mm](VENT_MEAS_MULLION) mullion, which is [13.4:1](VENT_ASPECT).

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
`../../petgf.3mf` in each part's production print orientation. The flat-wing
nameplate itself has no supports: its back and both horizontal wings print
directly on the bed.

Use Tree (auto) with the saved default style and retain Bambu's automatic
support choices, including normal sections it generates. Explicit normal-support
overrides have caused difficult removal: the
[Normal Snug receiver coupon](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-29-nameplate-flat-wing-receiver-h2c-v1/physical-result.json)
is rejected for impossible support removal. An explicit normal choice needs a
named feature that specifically requires it, or evidence of easier removal;
record and explain the exception's reason and scope before printing. An open
removal lane or smaller footprint alone does not establish easy cleanup.
Retain the required bed margin when reviewing automatic tree-support placement;
if that cannot fit, explain the concrete constraint before choosing an override.
Do not replace the automatic recipe with a trees-only rule or blanket blockers
for automatically generated normal sections.

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
It fights when it is walled on several sides, when a branch re-enters a pocket behind its own
interface, or when the hardware goes in first. The Z-seam catches need a short support ribbon contained in the open sliding
groove and rooted on nearby model stock. Derek reports easy release of
that arrangement on the other enclosure quadrants. The
[back-top article](../../drain-readiness/prints/2026-10-10-current-back-top-bridge50-mark1/physical-result.json)
has long fragile stems trapped in walls and failed sliding-groove cleanup. Their
physical starting points are unknown. A back-top preparation must trace the
groove contacts below their own model floor and keep the support removal lane
clear; diameter growth alone does not establish that routing. Short native
roots still require physical cleanup assessment. A
stub of the same build-up inside a 3 mm tie channel is a different job entirely.

What a root means depends on the face the piece prints on. On a piece whose cavity opens toward
the bed — the bottoms on their floors, front-top on its mouth — the bed and the model are two
different places to start. On back-top the cavity opens away from the bed: the ceiling slab's
interior face is the root every interior support has, a hidden flat the piece lays down in its
own first layers. The audit records that root as model material.

**Expanding print-down show rounds use an additive chamfer/taper at 0.24 mm.**
The shared construction in `../../cadlib/overhang_round.py` fills the lower corner
inside its unrounded envelope, with a 0.5 outward/build-rise slope tangent to the
retained circular taper. R6 has a 3.317 mm straight transition and a 2.292 mm initial
inset; each 0.24 mm layer advances at most 0.12 mm on that section. The enclosure applies it to hand-pocket upper rims, pump-cartridge hand-pocket
upper rims and roof side edges.
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
shape, and support carries it.
The C14 inlet's flange pocket keeps its floor, because that floor is what the receptacle lands
on; each handhold keeps its flat lifting ceiling, because that ceiling is the surface a hand
pulls up on; the Z-seam catches are broad square planes because they bear against lift along the
complete rails; a corner stack's knuckles keep their square bearing
faces; a pump boss lands on a flat shoulder. A corbel carries the material behind one of
those faces. It does not replace the bearing, locating, sliding, sealing, clamping, insertion or
access face with a slope.

The ground boss's full-width column joins the ceiling. The ASSE anchor's end sections continue
from the V's arris to the slab pocket's roof as rectangular blocks. The `fluid-28` anchor has
an ordinary corbel at each end. The flow-regulator anchor has two end corbels beneath the ASSE
outlet. Each tube-anchor and
body-anchor end names its form in `TUBE_ANCHOR_END_FORMS` or `BODY_ANCHOR_END_FORMS`, and each
Wago tower names its column in `WELL_COLUMNS`.

`wedge-fills` reads every print-down slope on back-top against the pack: each is under a body
or within a millimetre of one, in a room `enclosure_assembly.KEPT_WEDGES` names — a zip tie's
loop over a crown, a screw head's pass — or a wedge a column
could replace, which the bound names with the viewer's pick text. It is a goal row on the
scorecard. The anchor and tower forms come from their site declarations.

Relay #2's upper bar has a 2.5 mm wing at each end and bridges the 15 mm between them.
The main board's boss at y 241 has no wing (`enclosure.east_boss_wings`). The corresponding
solid, passage, clearance and motion checks read the assembled geometry.

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
[`enclosure_support_audit.py`](/hardware/scripts/enclosure_support_audit.py) reads an exported
Bambu G-code directly, or refreshes only the mesh in a temporary copy of the named production
project before slicing it:

```sh
git show 366d54ba040ecc7f1465c200e63e52410ffc0d4c:hardware/printed-parts/enclosure/enclosure/enclosure-back-top-petgf.3mf \
  > /tmp/enclosure-back-top-petgf.3mf
python3 hardware/scripts/enclosure_support_audit.py \
  --piece enclosure-back-top --slice-current \
  --model hardware/printed-parts/enclosure/enclosure/enclosure-back-top.stl \
  --profile /tmp/enclosure-back-top-petgf.3mf \
  --profile-label git:366d54ba040ecc7f1465c200e63e52410ffc0d4c:hardware/printed-parts/enclosure/enclosure/enclosure-back-top-petgf.3mf \
  --json-out hardware/printed-parts/enclosure/enclosure/enclosure-back-top.support-audit.json
```

The result carries the model, profile and derived G-code hashes, the slicer's support settings,
all interface islands and both plate and CAD coordinates.

**The six enclosure pieces are audited.** Their 3MF
snapshots are retained only in Git history — four at `aef8f43c0eb3eef9c6525ecaa0a1ca52c5b8c71a`,
the pump cap's crown-down project at `b4e181bee752bebaddc24d5e620fd7f8144129bd` and
back-top's ceiling-down project at `366d54ba040ecc7f1465c200e63e52410ffc0d4c`; they
are evidence inputs rather than current files in this directory. No piece is re-oriented to be
read: each enclosure piece beds on the face its own relief scheme is struck on — the Z− face on five of them,
the ceiling's show face on back-top (`enclosure.print_up`), whose project carries that half
turn in its build item. `enclosure-front-bottom-petgf.3mf` and `enclosure-back-bottom-petgf.3mf` carry the PET-GF15
exterior settings of `enclosure-front-top-petgf.3mf` around their own mesh — the same clones
`enclosure-pump-cap-petgf.3mf` and `enclosure-pump-cartridge-petgf.3mf` are; the pump cap's
build item carries a half turn about X, the crown on the bed.
`enclosure-back-top-petgf.3mf` is the one piece on its own 0.24 mm process, and the other whose build item carries a half turn about X. Each retained slice records its model and profile digests. The recorded support counts are:

| piece | bodies | interface islands | root | shortest build-up |
|---|---|---|---|---|
| `enclosure-pump-cartridge` | 2 | 2 | bed | 105.40 mm |
| `enclosure-pump-cap` | 2 | 2 | bed | 8.80 mm |
| `enclosure-back-bottom` | 4 | 5 | 3 bed, 1 model | 8.60 mm |
| `enclosure-front-bottom` | 4 | 4 | 2 bed, 2 model | 8.00 mm |
| `enclosure-back-top` | 13 | 35 | 2 bed, 11 model | 1.44 mm |
| `enclosure-front-top` | 3 | 19 | bed | 29.00 mm |

None of these columns orders the pieces by what their supports cost to remove.

`enclosure-pump-cartridge` has two bed-rooted bodies, one under each flat pull roof. Each
reaches one interface after 105.40 mm and leaves directly through its open side pocket.
`enclosure-pump-cap` prints on its crown and has two bed-rooted bodies, one standing in each
clamp-screw counterbore under its head seat after 8.80 mm; each leaves through the
counterbore's mouth on the bed face. On front-top all three bodies root on the print bed. One reaches the pump-bay lintel and
cartridge-facing recesses after 123 mm. The other two branch to the west and east flanks and
the funnel seat. Their shortest build-up is
29 mm. Remove these branches through the empty cartridge bay and funnel opening before
installing the hardware.
Four bed-rooted bodies carry the handhold ceilings, one per flank on each bottom piece.
Each has 34.20 mm of build-up and comes out through the open bottom. The other bottom-quadrant supports carry one feature
standing on all four flanks: the **Z seam's slide-head catch**, the joint's one down-looking flat and the
whole of its bearing against lift. Back-bottom's west catch reaches the bed from outside its
flank through the 12 mm PRV passage that crosses it — the same opening that splits that catch
into two interface islands. The other three have no lane to the bed and root on the arm's own 45°
under-flare below the catch they carry: 8.00 mm for front-bottom's pair and 8.60 mm
for back-bottom's east catch. These are the material-rooted bodies on the two bottoms, and the
reading says nothing about what they cost: the groove under a catch is open air from the arm's
sliding face out past the exterior plane, so each of the four stands on the outside of its flank
with a face exposed down the whole run. Front-bottom's pair is printed and pulled — the easiest
support on the piece, off cleanly in one piece, reachable without going near the cavity.

Back-top prints on its ceiling, so its supports reach separate functional faces:
nameplate receiver rims and catch pockets,
C14 and keystone pockets, tie-band and anchor ceilings, Z-seam feet, rear port
lips, and the PRV chase crown and mouth. The
[current native review](../tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-back-top-current-mark2-v9/README.md)
records 13 support bodies and 34 labelled contact regions: three bed-rooted and
ten model-rooted. Six short local bodies have 1.68 mm build-up. The slot-floor
interface runs through the 9 mm wall and stays exposed at both ends before the
pan is inserted. Each actual body and contact has a removal route through the
empty shell; release contacts and break sacrificial branches before installing
hardware. Native access and protected-face sweeps establish geometric lanes;
physical cleanup effort and finish remain observations of the print.
Back-bottom's two slide-head bodies carry the broad flat undersides: the west run from the bed through the PRV passage and the east from the arm's under-flare 8.60 mm below.

## Print orientation + corner relief

Three pieces print on their **Z− face** — the bottom pieces floor-down on the
floor slab, front-top mouth-down on its seam rim — and back-top prints on its
**Z+ face**, its ceiling on the bed. The build axis is the box's own Z on every
piece and the sign is the piece's (`enclosure.print_up`): where it is +Z the face
that hangs is the one looking **down**, where it is −Z the one looking **up**.
The mounting forms are described in [Support-removal strategy](#support-removal-strategy).
The anti-warp relief goes on the arrises
that run along the build axis: the box's four **standing verticals**, rounded to match the foam
shell's 12 mm outer radius — concentric inner one wall in, so the wall is
preserved.

A quadrant owns only **two** of those four. Its other two "corners" are the
Y-seam — a telescoping mating face, with no exterior arris there to relieve
(the side walls run straight through the seam). So the front pieces round the
front-left and front-right verticals, the back pieces the back-left and
back-right, and **every seam edge stays 90°**. Assembled, all four verticals
read as relieved, each sourced from a different quadrant. Of the horizontal
front-to-back arrises, side-wall↔floor is square and side-wall↔ceiling is the top's
rounded side edge (`_swept_top.SIDE_RADIUS`).

The display facet raises no fifth standing vertical: running wall to wall, it ends
on the ±X exterior walls and runs out into their own rounds.

Inside those verticals stand the **columns**, and each one is that relief
**mirrored** — congruent, which is what fixes it. The relief outside is a **quarter turn**
of [12 mm](COLUMN_ARC); a mirror is congruent or it is not a mirror, so the column's face is
a quarter turn of the same radius — the **same arc and the same length**. The only place such
a turn fits inside the cavity with its ends on the two inner faces is swung from the corner
they meet at, and that is the whole construction: one radius, one centre.

It lands on each face at 90°, so a standing vertical presents **two sharp corners** opposite
each other, [12 mm](COLUMN_ALONG) along each inner face, with the arc between them. The
section stands [8.27 mm](COLUMN_DEPTH) out of the cove at the corner's diagonal.

**The corner behind it is solid.** The face is the column's only free surface — a second arc
back there would leave a through slot the column's whole height — so the column is everything
within the radius and the wall keeps the rest. The cove the wall had turned stops being a
surface at all: what the room meets at a standing vertical is **one arc, congruent with the
one it meets outside**. All four verticals carry one (`enclosure.column_corners`), so each
quadrant prints the two its own two exterior arrises stand behind.

A wall's inner face is **flat only past that landing**, so anything ROOTED on it answers to
`enclosure.wall_flat_from_corner` rather than to the relief's own tangent. The C14 tunnel
follows `c14_station_x`.

**The pump-cartridge storey has no fixed front-top frame in its withdrawal span.** `_bay_cut`
removes the complete exterior front-wall band, both rounded corners and both side skins from
the bay floor through the lintel, then continues aft to the permanent receiver wall. The installed cradle
owns that same [215 mm](CRADLE_WIDE) exterior width. Its outline is vertical in Z: there is
no 45° narrowing toward the sill. Only the two hand pockets interrupt that width. The cartridge has [0.25 mm](PUMP_CARTRIDGE_Z_CLEARANCE) of functional Z clearance
above the sill and [0.5 mm](PUMP_CARTRIDGE_TOP_AIR) below the lintel; it has no cosmetic reveal or corresponding X/Y inset.

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
to whatever the pack packed it against. Two corners are relieved today, and `main()` prints
every one so a hollowed column is never silent:

- **X+/Y-** — the condenser's two sheet flanges, at z 8.0–10.4 and 144.6–147.0. The pocket
  shares material with the cradle groove. Its ceiling keeps the column's two 45° walks through
  that overlap, while the groove roof rises toward its insertion mouth; the rail's east end and
  the lens print as one body without restoring a flat roof over the pocket.
- **X+/Y+** — the PSU's aft-east corner, over z 252.4–306.4, about a millimetre deep at its
  widest. The brick cannot give ground instead: its rear mount hole is on the aftmost boss
  station, the relay and the main board are packed one `WIRED_CLEAR` at a time ahead of
  it, and the front of that stack stands ~1.3 mm off `carb-1`. What a column cannot absorb is a seam station:
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

The −X flank is a continuous 9 mm wall in the rear service bay. The ASSE vent connects through a printed TPU sleeve directly to the white 4 mm LLDPE return, which follows two R25 bends to the middle-row OVER bulkhead. [ASSE drain assembly](/hardware/assembly/asse-drain.md) gives the tube and fitting sequence.

The **ASSE anchor** looks print-down on its top. Outside the zip ties'
span the block goes on up as a column, from the V's upper arris, or the bore's crossing of it,
back to the wall and straight to the ceiling lane — the piece's own first layers — so nothing
over it looks print-down; over the span the column is absent so the loop has
its room, and the web between the tie cavity and the V ends square to the V, one wall across,
a supported face whose support stands on the slab in the tie channel. Nothing stands under the
block on this print either, so the V's foot ends square to its flank the same way the whole
anchor long. Its two 60° seat flanks stand 30° off vertical and lay on themselves either way;
the two round seats' lower arcs look print-down inside their bores and are supported faces.
Behind the anchor, one channel spans both zip-tie bands: its fore and aft end faces remain
`tie_cav_wide_w` wide about their tie centres, the volume between them is open, and its top
mouth opens into the lane the slab leaves over the same span (`_ceiling_tie_channel_relief`).

The **bay floor** begins at front-top's Z160.25 print bed, one running fit above the
nominal Z seam, so there is
no face under it to hang and no support in it to pick out. It is a solid slab across the whole front storey. The pump cartridge slides across it,
and the rear bulkhead grows from its full section.

The **tee wall** behind that plate costs nothing standing up, and its four bores are the
only thing in it that could have hung. The piece beds parallel to the Z seam, so a bore on Y
lies horizontal and its crown is the only face in the wall that could be laid on air.
Each is **teardropped** (`_tee_bore`): the roof stands on the bore's own tangent points.
Its two planes rise at [36°](TEARDROP_ROOF), one whole degree above the history-only back-top
PET-GF profile's automatic-support threshold and verified support-free with that exact profile;
tangency makes that the narrowest and shortest peak at this angle. The lower circle the collar
bears on is untouched, and the wall needs no support.

The **five round tube crossings in the +Y wall** use the same `_teardrop_y` section through
the wall's whole section at each station, struck toward back-top's print-up. This piece beds
on its ceiling's outer face (`BACK_TOP_UP`), so the crown a print cannot close is each bore's
machine-bottom, and that is the side the tangent [36°](TEARDROP_ROOF) roof stands on; their
stated Ø18/Ø17.86 figures remain the complete circular pass envelopes for the threaded barrels
everywhere else round the circle. The separately printed identification chip keeps its
circular bore, and the fitting's flange and nut clamp the chip and the remaining wall annulus
on their two faces. No face in any of the five passages lies flatter than that roof.

The **AC inlet's mount** stands off the +Y wall's inner face in back-top and needs no added
printed corbel. It is one rectangular block from the flange pocket's mouth to the wall
(`enclosure._c14_tunnel`): its two flanks are vertical to the bed, its crown runs out into the
ceiling slab the piece prints on, and its underside looks print-up — a free flat, with the wall
and the slab carrying the block between them. What is left over air is the bore's own
print-roof, the aperture's machine-bottom face — a bridge the aperture's full width, carried
between the block's two flanks. Nothing on the piece stands outside the print silhouette: the
receptacle's two heat-sets go into the seating face at the floor of the block's flange pocket,
from inside the box, and the back of the machine is flat.

The inlet stands on one column, `enclosure.c14_station_x`: the aperture, tunnel, pocket and
both screw stations all follow that one X datum, and its Z is aligned with the other top-row
ports. The ceiling passage and shallow flange seat are the canonical slipped flange profile —
the same straight-sided dog-bone with its two round ears. Only the 28.3 × 19.3 mm, R1.5
cord-access opening continues through the rear wall and tunnel. Its 3 mm total extra X width
is independent of the female inlet's mounting pocket and keeps the X datum fixed.
Over the inlet the ceiling is the slab's own
underside, which looks print-up, so nothing between the receptacle's moulded rim and the ceiling
asks for a separate rectangular relief band or a support stack.

The **PRV chase's closed roof leans from the −X wall too**. Where its open exterior groove
becomes the closed fall, the groove's roof is level across the
[3 mm](VENT_GROOVE_ROOF) show-skin section: it looks print-up on back-top and meets the show
face square. The closed passage's roof is one X plane
from its liner inside the flank through the wall and out to the cold-core lip, and the lip
keeps [3.05 mm](VENT_RIB_LAND) of solid land below the square mouth. The lip ends
at X−90.75, 0.25 mm outboard of the core's X−90.5 flank. Back-top's share of the rib
stands square on the seam rim, which looks print-up on that piece. Its exterior crown is flat
at the lip's height across the [8 mm](VENT_RIB_BASE) to the grown flank, with the complete
first printed section carried by removable tree support. The inner passage roof keeps its
45° plane. The mouth's floor is a `vent_channel_w` bridge
between the passage's two jambs. The exterior groove edge, the square passage and the back
slide's opening remain on their own datums.

## ASSE anchor

A stepped anchor on the −X wall that the ASSE 1022 chain lies in
(`_asse_cradle`). The chain is five fittings made up by hand on one axis, so
neither the run's length nor the clock any one fitting lands at is a number this
wall can know — but the **section** each one presents about that axis is the
fitting's own. The anchor is cut to each in turn, and the steps between sections
fall out as faces square to the axis.

| section | across | seated on |
|---|---|---|
| PI4512F6S swivel nut | 22.0 | its circumscribed circle — the nut spins on the body |
| Multiplex hex barrel | 33.0 | its own two flats |
| GAGIRA coupling | 25.67 | its circumscribed circle — its clock is wherever the thread stopped |

The two end sections are there to make the barrel's steps and for nothing else, so
each runs the **shorter of the two fittings' lengths** rather than its own: the
coupling is more than twice the nut, and anchor past a section already seated is filament
paid for in the deck's own headroom. The flanks reach under the axis exactly as far as
the chain's own lowest arris — the barrel's apothem, `asse_reach_down` — and no
further, for the same reason.

Every section is the **same 120° V** and only its apex moves. A V of that angle is
the two flanks of a hex read off its corner, and it is equally the tangent seat of
any circle — so the section that sits deepest in the wall is the section that is
widest, and the barrel steps down out of both its neighbours rather than out of a
number chosen here.

**Only the barrel's V is read off flats, and only the barrel's may.** The other two
spin: a V cut to their flats would demand an angle the assembly does not control and
bind on the build that landed 30° off. The Multiplex's hex does not spin — its
atmospheric vent is machined into it — so keying that one section is what holds the
drip over the pan, and it is the whole reason this is an anchor and not a zip tie.

`asse_seat_slip` is the fit across the V and `ASSE_STEP_SLIP` the play along it, the
deeper section taking the latter past both its ends so the barrel drops in and the
steps stop it travelling rather than hold it still. Aft it needs neither: the chain's
inlet collet butts the tap-water union's, and that joint takes the length up.

Two **zip ties** shut the anchor's mouth, one in each band the vent leaves clear on
the barrel — the brass, which is the only section a tie may close on.

Both run through **one shared channel in the anchor's back** (`_asse_tie_cavity`), closed on
every side but its two mouths. Its fore and aft ends are `tie_cav_wide_w` bands centred on
their respective ties. The same XZ profile cuts continuously across the volume between them.
It is **straight on the west and the anchor's own V on the east**, so
it is narrowest at the axis and flares to both mouths: each mouth opens
`asse_tie_back / sin 60°` off its lip's own arris, on the block's face where a hand reaches
it, and at the axis the flare leaves a zip tie pushed through the room to turn the vertex by
cutting its corner. It stands one `wall` west of the apex at every station, struck on the
deepest section's apex so the web is no thinner than that anywhere, and one `wall` off the
side wall behind it — so its width is a remainder between the two rather than a number. The
continuous horizontal passage gives the slicer one support body with a full-width removal path.
Its lower XZ mouth terminates on the anchor's underside, where it opens directly into cabinet
air; its upper mouth runs into the ceiling lane over the same tie span. Only the upper cutter
passes its opening plane, so the flank beside the lower mouth remains one unnotched wall.

A tie is a closed loop, so its zip tie also has to cross the chain's top flat, come west
in that lane and drop into its channel. **The 3 mm top-wall cap stays whole.** The storey leaves
`DECK_CEILING_CLEAR` beneath that cap, while the ceiling slab and flank are relieved over the tie
span to join the channel. The deck pays the millimetre out of its own headroom. That leg is
**laid, not pulled**: this piece
is populated inverted on the bench — ceiling down — so the zip tie lies on the
ceiling's inner face and the chain comes down onto it.

Nothing about the chain's weight is theirs: cut both and it still lies where it lies. `enclosure_assembly.check_asse_seated` is the row that reads the anchor
closed on the barrel, measured off the two placed solids, because every other
reading on the card is satisfied by a chain floating in air. `_ceiling_tie_channel_relief`
reads the **route** fail-fast: an ASSE-named ceiling pocket must overlap the complete tie span
and extend inboard of the flank mouth before the slab opens that span to the lane.

## Flow-meter anchors

Two anchors off the **top wall**, one over each of the DIGITEN meter's fixed port
collars, with its offset housing between them (`_flow_meter_anchors`). The measured
cover stands 1 mm below the nominal ceiling. The pigtail points toward the main
board, and the meter's own axis sits below the rear union; `carb-2` rises to it
through two shallow R14 bends.

The housing's physical flow arrow must agree with the route from `carb-1` to
`carb-2` before the installation pose is accepted; the reference's port names alone
do not establish that direction.

Each fixed collar is 7.2 mm long and drafts from ⌀17.9 to ⌀18.3. Its anchor takes a
**concentric half-round bore at R9.3**, opening down. The seat leaves at least the
0.15 mm radial slip over the collar, and the barrel comes straight up into it.

**The arc stops on the barrel's own axis plane, and the rib carries one
`flow_meter_anchor_wall` past that.** The axis plane is where the arc is widest, so
each lip comes out a **flat 3.000 mm strip**. Carried any further round, the arc
runs out to nothing against the flank and leaves a feather.

Each anchor is 6.9 mm long, centred on the fixed collar with 0.15 mm at either end.
The 3.5 mm tie passage has a 1.7 mm axial end web on each side. Those webs span four
0.42 mm extrusion widths; the radial wall stays 3 mm. The narrower neck and the
full 3.7 mm movable collet remain outside the bearing band.

**The zip ties are the load path here.** A seat that opens downward carries nothing, so
unlike the ASSE anchor's two zip ties these hold the meter up — a purchased part of a few tens
of grams on two nylon zip ties. Each requires a **6-inch, 18 lb tie**: the collar
and anchor make an [81.2 mm](LOOP_DIGITEN) loop. Thread both empty passages before
seating the meter, cinch on the fixed collars and tug-test both ties.

Each anchor's zip tie runs through a window over its bore. No cavity is subtracted from the rib
itself: its centre band is never fused, so the channel is the length the two solid ends do not
span. The ceiling slab's own relief opens the tie route over that same band
(`_ceiling_tie_reliefs`). The rib is one box up to one `wall` over the bore's crown, its two ends
carried on up to the top wall, and one bore through all of it.
**The rib is unified before it joins the wall**, leaving each bore and lip as one
continuous bearing feature.

Back-top prints on its ceiling, so the rib **stands up off the bed**: its two end webs rise
from the slab, the seat is an upward-opening cradle in the print, its lips look print-up, and
the channel's floor over the crown is a `tie_cav_w` bridge between the two webs. The slab
stands off the rib's room over its tie band, the channel's own height and no more
(`_ceiling_tie_reliefs`), so the loop comes down both flanks.

## Tube anchors

One pattern wherever a wall comes near enough to reach something round
(`_tube_anchors`): a **bore concentric with the body**, half a cylinder at
`seat_r`, and the zip tie's channel behind it. The stations in
`enclosure_assembly.TUBE_ANCHOR_SITES` hold lengths of tube and those in
`enclosure_assembly.BODY_ANCHOR_SITES` hold fittings — the same rib either way, since what the
builder is handed is an axis, a direction along it and a radius. What closes each tube site is
stated in `enclosure_assembly.TUBE_ANCHOR_CLOSURES`: a zip tie, as described here, or an
anchor cap (below).

**The arc stops on the body's own axis plane and the rib carries one `wall` past
it**, so each lip is a flat strip rather than a feather — the anchors' bargain,
on the one body this machine has twenty of. The rib's length is its cavity's:
`tie_cav_w` of zip tie and buffer with `tie_cav_wall` of itself at each end. It states
no height of its own — it is handed the body, and the wall it stands on is where it
stops.

Flavor B's wall anchor carries both end webs on the ordinary full-width 45° corbel, rooted on
the −X wall and reaching `tube_anchor_corbel_reach` under each complete 3 mm web.

**The zip tie's channel is what is never fused.** The rib is one box its whole length
up to one `wall` over the bore's crown, its two ends carried on up to the face it
roots on, and one bore through all of it. Where a small tube stands far enough from
its root face to put at least one routing buffer back into the load path, its central
band is solid-backed from the wall until one `wall` of useful cavity remains. Compact
fitting anchors keep their available clearance instead of acquiring a skin-thin roof.
The two side mouths stay open and no cutter grazes them. A zip tie therefore goes in
**before** the body does.

**And the face is the piece's own** (`piece_root_faces`), not the box's interior. A
station is struck in the box's frame because that is the frame the body is in; the
plane a rib STOPS on is whatever the piece carrying it presents, and on the two
pieces with a grown flank those two stand [6 mm](BACK_TOP_FLANK_GROWN) and
[6 mm](FRONT_TOP_FLANK_GROWN) apart. Measured to the wrong one, the channel is
drawn inside the wall's own stock and the rib arrives buried to its crown.

**Where the piece's face leaves no channel, the wall gives the rib its lane back.**
The box's interior is one `wall` inside the exterior, and a piece carrying stock
inboard of it carries stock the rib was drawn to use — so it gives that up over
the rib's footprint and the rib roots on the box's plane. The
relief is **wider than the rib, and by the zip tie**: what the loop runs down is the
rib's two flanks, from the channel's floor to the body's axis plane, so it is
carried `tie_t + tie_cav_buffer` past each flank and those two lobes are
what the loop comes down. The tap-water pair's two ribs are the pair that take it —
back-top's 9 mm flank occupies the room their zip-tie cavities use, so those two generated
reliefs return only the ribs' footprints to `interior_x` while the nominal flank stays whole
around them.

**The regulator's rib** closes on its round barrel. The WR1110 lies fore and aft
on the panel deck one column east of the carb union, and the section under the rib is
the **scanned ⌀18.87 barrel between its two wrench hexes**. The circular seat is
independent of wrench clock. The 9.5 mm rib sits in the centre of the 35.4 mm round
band, leaving 12.95 mm to each wrench transition. The
[WR1110 measurement record](/hardware/reference/wr1110-regulator/README.md) identifies
the retained scans, dimensions and model comparison.

The cylindrical seat keeps 0.15 mm radial clearance around the WR1110 barrel. Its
three-millimetre web separates the bore from the tie channel, which has at least 3.25 mm
of room under the full three-millimetre exterior ceiling cap. The CO₂ inlet and WR1110
share one axis 0.25 mm below the other rear ports. The CO₂ chip reaches the common top edge.

**The zip tie is the load path here**, the same bargain the flow-meter anchors make: a
seat that opens downward carries nothing. Barrel and rib make an [83.2 mm](LOOP_WR1110)
loop, past what a 4" tie closes, so this one takes the 6".

**The downstream gas check has a separate ceiling cradle**, east and forward of the
regulator, with its flow arrow pointing aft. The seat closes on the check's round metal
inlet boss; its adapters remain clear of the tie. Thread one **6-inch
18 lb zip tie** through the empty cradle before seating the made-up check, then close and
flush-cut the tie. The [calculated loop and tie allocation](/hardware/ledger/bom.md)
come from the named body seat, and
[`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §1
owns the assembly sequence. The fitting envelopes and received-part cradle fit remain
physical qualification items. The nominal routes run from the inlet to WR1110, turn
forward from its outlet into the check inlet, then return from the check through the
east lane to the cold core.

**Anchor caps close back-top's three ribs that hold a tube, and those ribs take no zip tie**
(`_capped_anchor`, `_anchor_cap_interface`): `carb-1`'s and `co2-2`'s under the ceiling and
`fluid-28`'s on the −X wall. Each is the same half pipe at `seat_r` with flat lips one `wall`
past the axis plane, built as one solid post [16.3 mm](CAP_RIB_LEN) long with nothing cut for a
tie. Each flank carries a catch window: a pocket [10.3 mm](CAP_WINDOW_LEN) long between the
rib's two end webs, [1.6 mm](CAP_WINDOW_DEPTH) deep, from [6.92 mm](CAP_WINDOW_B0) over the axis
plane to where the flank meets the ceiling, past the [10.19 mm](CAP_WINDOW_B1) the lip reaches.
Back-top prints ceiling-down, so under the ceiling each window's bearing face, the side nearest
the tube, prints as a bridge web to web. On the −X wall the rib reaches level out of the wall:
the flank that looks print-down and its window's roof bridge web to web, and the two end webs
stand on the tied rib's own 45° corbels, beyond the cap's ends. The rib's two outer
bottom edges carry a [0.8 mm](CAP_RIB_CHAMFER) chamfer the cap's lips ride onto. The
[anchor cap](../anchor-cap/README.md) presses on over the tube, and its lips drop into the
windows.

The cap's wings reach [10.3 mm](CAP_WING_TOP) over the axis plane. Where the ceiling's face
stands inside [0.6 mm](CAP_HEADROOM) of that, the ceiling gives each wing a slot as wide as the
wing and the spread its lip makes (`_ceiling_cap_reliefs`), and the rib's flank runs on up the
slot's inner wall. Over `carb-1` the slab's face stands that far off, and the ceiling gives up
nothing; over `co2-2` it stands 7.04 mm off and gives both slots. `fluid-28`'s wall stands
12.43 mm off its axis and gives up nothing.

The rib stands at the head of `carb-1`'s climb, its near end one `wall` past the corner the run
climbs into (`enclosure_assembly.tube_anchor_midpoint`): `co2-1`'s U runs beside the middle of
the crossing inside the cap's wings, and at the head of the climb the cap stands clear of it.

The cap is cut for the 1/4" seat. It closes a rib rooted on the face its piece prints on or
reaching level out of a wall, and its rib has to stand on its leg's straight: `co2-2`'s,
16.85 mm between its two R14 bends, is the shortest it closes.

## The pump cartridge and its bay

**The pumps leave through one large lower cradle.** `enclosure-pump-cartridge`
(`build_pump_cartridge`) owns the complete removable front wall, the filled body behind it,
and both hand pulls. Its filled bearing block has 0.35 mm of modeled room above the receiving
floor: 0.25 mm running clearance plus 0.10 mm for the cavity-floor transition. Its exterior
face begins on the cartridge bed plane and ends
[0.5 mm](PUMP_CARTRIDGE_TOP_AIR) below the lintel. The bed plane is z [165.195 mm](PUMP_CARTRIDGE_BOTTOM_Z), the crown is z
[284.174 mm](PUMP_CARTRIDGE_TOP_Z), and the complete removable face is
[118.979 mm](PUMP_CARTRIDGE_RISE) high. Its outer shell
keeps the complete 215 mm enclosure width, including both rounded front corners and side skins,
and its show plane shares the fixed front face at [0 mm](PUMP_FACE_OFFSET) offset. The flavour pack stands behind that plane. The show plane stands one complete
[1.2 mm](PUMP_SHOW_GROWTH) flute depth ahead of the pump-pocket datum. Its filled body reaches both cavity
planes, and the front display-support columns have no section anywhere in this withdrawal span.

The pump stations use a [3 mm](PUMP_STATION_DROP) downward world-Z datum. The stationary
manifold, tees and tube passages stand 2 mm above the manifold's nominal datum. The pump
reference's rear boss and motor axis stands 1 mm toward Y− from its head datum, and the
clamp's fitted octagon and motor-can openings follow that rear-stack axis. Four straight LLDPE stubs, clamped in the pump heads, connect the complete pumps to the
permanent TPU receivers.

**Each pump drops into that cradle from Z+.** Two straight wells pass the motor, boss, molded
flange, head and tube fittings. The fitted head well leaves flat skirt lands on −Y and both X
sides, with tube passages on +Y. The physical skirt rests on those lands; the molded flange
transfers the pump weight and clamp load into the cradle and the continuous bay floor.

The head's [8 mm](PUMP_SKIRT_DEPTH) skirt stands over one flat horizontal land at z
[206.674 mm](PUMP_SKIRT_SUPPORT_Z). The physical pump sits [0.251 mm](PUMP_SEATED_DROP)
below the holder station datum when the skirt is seated. The land keeps the skirt's fitted X/Y plan;
there is no slanted substitute for it. It is continuous across the X−, Y− and X+ flanks, with
[4.9 mm](PUMP_SKIRT_Y_MINUS_LAND) under Y−. The
measured [54 mm](PUMP_SKIRT_BODY_Y) body has [0.25 mm](PUMP_SKIRT_XY_AIR) per-face clearance
in a [54.5 mm](PUMP_SKIRT_OPEN_Y) Y opening, from y
[18.387 mm](PUMP_SKIRT_BODY_Y_MINUS_EDGE) to y
[72.887 mm](PUMP_SKIRT_BODY_Y_PLUS_EDGE). On Y+ the same land continues only between the two
tube-casing passages. The skirt itself spans [62.5 mm](PUMP_SKIRT_Y), from y
[13.469 mm](PUMP_SKIRT_Y_MINUS_EDGE) to y [75.969 mm](PUMP_SKIRT_Y_PLUS_EDGE); its opening ends
at y [76.269 mm](PUMP_SKIRT_Y_PLUS_OPEN_EDGE), leaving
[0.3 mm](PUMP_SKIRT_Y_PLUS_AIR) around the skirt and
[3.382 mm](PUMP_SKIRT_Y_PLUS_LAND) of supporting land back to the body opening. Behind
that opening the cradle keeps [5.996 mm](PUMP_SKIRT_AFT_STOCK) of stock, at least the
[3 mm](PUMP_SKIRT_UPPER_BAND) upper band that ends at y [79.269 mm](PUMP_SKIRT_UPPER_BAND_AFT),
and ends on the cartridge's flat back at y [82.265 mm](PUMP_CARTRIDGE_AFT_Y): the bay bulkhead
less its [0.25 mm](CARTRIDGE_BULKHEAD_KISS) clearance, the plane the clamp ends on too.

**The second printed piece is the top clamp.** `enclosure-pump-cap`
(`build_pump_cap`) is [174.4 mm](CLAMP_SPAN) across and [67.249 mm](CLAMP_RISE) high. Its bridge underside
stands at z [216.93 mm](CLAMP_BASE_Z), [2 mm](CLAMP_BRIDGE_RISE) above the holder datum.
The fitted cylindrical motor bores are Ø37 mm. Above its upper end, each opens through the
crown as a 45° cone, [47.5 mm](CLAMP_TERMINAL_OPENING) across at the crown, leaving the motor
end and its terminal pair exposed.
One filled field spans both pump heads from their clean
fore envelope to the cartridge's flat back and reaches one common crown at z
[284.17 mm](CLAMP_CROWN_Z), with [0.5 mm](CLAMP_LINTEL_AIR) of Z air below the fixed bay lintel.
Two fitted openings wrap
both bosses with [0.25 mm](CLAMP_BOSS_AIR) clearance from each octagonal face and leave one shoulder around each motor
can. Both fitted openings follow the pump reference's rear-stack axis,
[1 mm](CLAMP_PUMP_Y_SHIFT) toward Y− from the head and lower-cradle datum. Above those fitted openings, the motor-terminal wells open through the crown. The [50.95 mm](CLAMP_SCREW_LANE) lane between the two octagons stays full from
base to crown, and the two screw stations cross it in their own bores,
[36 mm](CLAMP_SCREW_PITCH) apart on the centreline. Each [60 mm](CLAMP_SCREW_LEN) M3 drops
through a counterbore in the crown whose seat is struck from the screw,
[15.2 mm](CLAMP_HEAD_SEAT_DEPTH) under the crown at z [268.975 mm](CLAMP_HEAD_SEAT_Z), runs the
whole field and the bridge clearance under it, and takes the complete
[5.7 mm](CLAMP_INSERT_LEN) long insert opened from the cradle's station plane. The clamp
carries no show face, plate stop or hand pull. Its insertion wells leave
[0.25 mm](CLAMP_DROP_AIR) per-face clearance around the clamp.

The service sequence follows those two load paths. Withdraw the assembled cartridge by its
cradle pulls before any Z service; back out the two clamp screws on the withdrawn cartridge;
lift off the clamp; then lift either complete pump straight up. Assembly is the reverse on the
bench, followed by straight Y insertion.

**Each of the four tube-casing openings is [13.25 mm](CAP_TUBE_OPEN) wide** around a
[12.75 mm](CAP_TUBE_PART) casing, leaving [0.25 mm](CAP_TUBE_RADIAL_AIR) per side. The two casing axes on each pump
stand [59.75 mm](CAP_TUBE_PITCH) apart. The physical pair spans
[72.5 mm](CAP_TUBE_PART_SPAN), while its holder openings span
[73 mm](CAP_TUBE_OPEN_SPAN). Each passage begins at the case-room seam,
y [49.936 mm](CAP_TUBE_START_Y). Its circular lower half is
centered on the casing axis and a straight [13.25 mm](CAP_TUBE_OPEN) shaft continues through the complete vertical
insertion path. The shafts, tube-side case room and upper well share the same outer X planes;
printed wall remains between and outside the passages. The full-width upper wells end together
at the bulkhead face, y [82.515 mm](PUMP_UPPER_WELL_AFT). The cradle and clamp have flat
aft faces beside these openings.

The pump outlet planes stand [5.351 mm](PUMP_OUTLET_BULKHEAD_AIR) fore of the
bulkhead. The show face shares the fixed front plane at [0 mm](PUMP_FACE_OFFSET) offset and
stands one flute depth ahead of the pump-pocket datum. The pump wells and their Y+ edge occupy
the complete flavour pack's common station.

**Four permanent TPU receivers form the pump dock.** Each complete replacement pump
carries two straight stubs of 1/4" LLDPE in its tube ends, clamped by the pump head's
own housing, which carries their axial loads into the rigid head. The stubs pass the
cradle's open tube passages. The customer's pump change does not cut, trim or
transfer a stub.

The stubs enter [4](RECEIVER_COUNT) custom TPU funnels followed by
Ø[6.1 mm](DOCK_SEAL_BORE), [6 mm](DOCK_LAND) straight sealing lands. The rigid wall
locates the receivers in X/Z. Their recessed collars fit in the wall, and
[3](KEEPER_COUNT) flat PET-GF keepers capture Y: one for each outer receiver and one for
the inner pair, the magnet column between each pump's ports dividing the wall into three
bays. Each keeper is [3 mm](DOCK_KEEPER_T) thick and slides up its slot behind the wall's
interior face from the seam, [0.25 mm](DOCK_KEEPER_SLIDE_AIR) from each slot face, until
each [11.7 mm](DOCK_NECK) receiver neck snaps through its keyhole's
[10.4 mm](DOCK_NECK_MOUTH) mouth into the [11.9 mm](DOCK_NECK_GRIP) grip. The slot's faces
back the keeper both ways in Y and the TPU neck holds it in X and Z; no screw, insert or
washer. Each receiver is a complete asymmetric Y with
90° between its pump inlet and upper branch, with a nominal 135° lower branch.
Its upper link is straight. A one-piece compound TPU return supplies the lower
45° and 90° turns, with straight LLDPE between the junction and return and a
short straight tail into the original aft valve station.

All four returns snap into one PET-GF return block under the seam: a straight slot
per return, narrower than the TPU body, with a round seat along the return's path. Three M3×12 screws
hold the block's top face to the aft tray foot. All permanent plumbing is
assembled on loose front-top before that piece joins the compressor half.

The meeting magnet poles set full insertion, with the stub tips
[7.75 mm](DOCK_TIP_FROM_BACK) aft of the cartridge back, at enclosure
Y[90.015 mm](DOCK_TIP_Y). The tips remain 0.5 mm short of their internal shoulders.
A straight pull withdraws the four stubs while every junction, keeper, return,
the return block and every fixed tube remain in place. No commercial collet moves during a pump
change. The [pump-dock specification](../pump-dock/README.md) supplies the manufacturing
parts, native geometry review, tube setting jig and material selections.

**Printed-in SB443-IN pairs seat and retain the cartridge.**
[16](DOCK_MAGNET_COUNT) magnets stand in one [4](DOCK_MAGNET_ROWS)-high column on each
pump's own load line in each half. Each column is one slot open at the mating face, with a
printed rail standing in each of the blocks' side grooves; the blocks drop down the rails at
the part's one print pause and the next layer closes over them. Pulled onto its rails, each
pole stands 0.125 mm proud of its face, so the poles meet in the middle of the 0.25 mm gap
and seat the cartridge. The [magnet record](../pump-dock/magnet-retention.md) gives the slot,
the pause and the loading. Installed holding force and the printed rails' fit remain physical
qualifications rather than advertised-array calculations.

The cradle's flat aft edge is at y [82.265 mm](PUMP_CARTRIDGE_AFT_Y),
[0.25 mm](CARTRIDGE_BULKHEAD_KISS) fore of the bay bulkhead. Its accepted pump-seat
fit keeps its recorded scope; the stub clamp, TPU sealing and the complete magnetic
dock require their own assembled physical results.

**Both pulls are tall rounded pockets centred on the cradle's Y run.** Each is [15.75 mm](PULL_DEPTH)
deep and [28 mm](PULL_RUN) long in Y, from z [177.43 mm](PULL_FLOOR_Z)
to z [272.194 mm](PULL_TOP_Z), a [94.77 mm](PULL_RISE) height. The cartridge keeps
[12.23 mm](PULL_FLOOR_LIGAMENT) below each pocket and [11.98 mm](PULL_ROOF_LIGAMENT)
above it. The four corners have [6 mm](PULL_CORNER_R) radii, and the complete exposed
perimeter has [6 mm](PULL_EDGE_R) rounds, leaving [6.23 mm](PULL_RIM_FLOOR_LIGAMENT)
at the lower rim and [5.98 mm](PULL_RIM_ROOF_LIGAMENT) at the upper rim.
The rim's roll and corner blends follow the top shoulder and lower handholds;
the flutes taper into the same broad smooth edge.
The fore face at y [29.63 mm](PULL_LEDGE)
carries cartridge extraction; the aft face at y [57.63 mm](PULL_AFT_LEDGE) takes the thumb's
push during insertion. The cradle keeps [24.63 mm](PULL_FORE_STOCK) of stock fore
of the pocket and [24.63 mm](PULL_AFT_STOCK) aft of it. The inboard walls join both grip
faces to the cartridge body. The top clamp has no separate grip.

## Fixed plumbing behind the receiver wall

Four permanent TPU junctions combine the pump-facing funnel, tight inlet land
and two branches in one printed wet body. The inlet and upper outlet are at
90 degrees; the lower outlet points 45 degrees aft from downward. The upper
LLDPE link runs straight to its original valve port. Each lower outlet joins
one permanent printed return containing a 45-degree turn, a straight passage
and a 90-degree turn. Two straight LLDPE links connect that body to the junction
and the original aft valve port.

Both front flanks retain their full [9 mm](FRONT_TOP_FLANK) section across this room.
The flat receiver keepers install from the open interior before the valve rows close
access. Each junction's solid TPU between its branches backs its upper socket; the
return block's channels seat the returns, so the fixed socket stops locate the short
diagonal links against axial motion. The aft valves and coils enter from the loose
piece's underside and move onto their mounting posts. The Beduan socket fit retains
its identified physical acceptance; ties supply retention. Factory assembly and the
complete dock's physical qualification are specified in
[`internal-plumbing.md`](../../../assembly/internal-plumbing.md) §3 and the
[pump-dock record](../pump-dock/README.md).

## The full-width opening

One opening spans the full cartridge width between the bay floor and lintel. Both
rounded front corners and the exterior flanks belong to the removable cradle. Its
straight aft face follows the bay bulkhead across the complete width with
[0.25 mm](CARTRIDGE_BULKHEAD_KISS) broad-face clearance. The meeting magnet poles
establish the closing datum.

The cradle's exterior stands plumb from its common bed plane to
[0.5 mm](PUMP_CARTRIDGE_TOP_AIR) below the lintel. The fixed shell perimeter is recessed
[0.25 mm](PUMP_CARTRIDGE_Z_CLEARANCE) below its lower edge; the receiving
floor is 0.35 mm below its flat underside. Both rounded hand pockets belong to this cradle.

## The bay floor

Front-top carries one continuous floor from the front wall through the rear bulkhead.
Its flat receiving sill is z [164.845 mm](PUMP_BAY_FLOOR_Z), 0.35 mm below the cartridge's
unchanged Z165.195 bed datum. The independent [2.6 mm](PUMP_BAY_FLOOR_RELIEF) neutral-floor
relief also remains. The scanned rigid front-rim envelope keeps
[0.679 mm](PUMP_HEAD_FLOOR_AIR) above the receiver. The full floor retains
[4.595 mm](PUMP_BAY_FLOOR_STOCK) of stock above front-top's Z160.25 print bed and keeps one
flat insertion/withdrawal lane. It runs into the full thickness of the bulkhead.

Front-bottom's lip drops around the front and both flanks as far as the receiver-wall backing datum.
The floor crosses that run wall to wall.
The remaining side lips and rails telescope along their complete working runs.

Two feet on front-bottom's flanks bear beneath the bulkhead ends. Each offers a
[10 mm](PLATE_FOOT_X) × [20 mm](PLATE_FOOT_Y) land on the seam plane, with
[3 mm](PLATE_FOOT_T) of section at its inboard edge and a
[45°](PLATE_FOOT_ANGLE) underside. Their common underside clearance over the condenser
is [2 mm](PLATE_FOOT_COND_AIR).

## The bay bulkhead

One rectangular bulkhead joins the floor, lintel and both enclosure flanks. Its flat
cartridge-facing plane is Y [82.515 mm](BAY_BACK_Y); its full backing depth is
[14.321 mm](BAY_BULKHEAD_T), with the receiver-row interior recessed as described below. The cradle and clamp share one flat back at y
[82.265 mm](PUMP_CARTRIDGE_AFT_Y), one [0.25 mm](CARTRIDGE_BULKHEAD_KISS) kiss fore of that
plane.

The receiver row has a 7 mm wall section with four closed Ø12 mm bores and recessed
front lips and rear collar seats. The interior access recess leaves flat keeper guides,
their lock hosts and the fixed socket mounting fixtures. The full
backing depth continues into the ridge/contact wall above. The Z-seam rail channels
begin at the bulkhead's retained aft datum.

The clamp lifts through the cradle's straight upper wells, which open through its aft
face. Its broad underside, fitted boss openings and motor bores close over both pumps.

The **bay** is the opening all that leaves through (`_bay_cut`): exterior side face to exterior
side face, from the receiver floor at z [164.845 mm](PUMP_BAY_FLOOR_Z) to the fixed lintel at z
[284.674 mm](PUMP_BAY_LINTEL_Z), and aft to the flat bay bulkhead. The lintel is relieved
[2.5 mm](PUMP_BAY_ROOF_RELIEF) upward from its pump-neutral roof datum and keeps
[7.45 mm](PUMP_MOTOR_LINTEL_AIR) over the installed motor crowns. The flat sill runs wall to
wall; the lintel carries the facet and the display on a stated ligament.
The removable shell follows the enclosure's rounded plan with its front plane flush at
[0 mm](PUMP_FACE_OFFSET) offset. The filled block behind the face reaches both cavity planes;
its fitted head wells and upper clamp wells follow the installed pump stations.
Front-bottom's front lip drops across the whole flat span
(`_front_flat_lip_drop`) — the floor stands in that band and the heads run down through
it — and the front wall below keeps its single `front_wall` section from slab to seam.
The face keeps [0.25 mm](PUMP_CARTRIDGE_Z_CLEARANCE) of Z clearance over the recessed stationary
sill and [0.5 mm](PUMP_CARTRIDGE_TOP_AIR) below the lintel. Its complete front, rounded corners and exterior flanks stand plumb
between those two flat gaps with no taper.

**The fixed front wall is [9 mm](FRONT_WALL) thick and grows inward.** The removable pump
face shares its exterior plane. The fitted lower head wells leave at least
[8.459 mm](PUMP_FACE_SKIN) of smooth stock ahead of them. The upper insertion wells end
on one flat plane, [0.25 mm](CLAMP_DROP_AIR) ahead of the clamp, leaving
[5.609 mm](PUMP_UPPER_SMOOTH_SKIN) of smooth section and
[4.409 mm](PUMP_UPPER_FLUTED_SKIN) behind the deepest flutes.
Both lower wells follow the pump stations, including their skirt lands and fitting passages.
The fixed wall's two 45°-chamfered compressor reliefs (`_front_relief_cuts`) follow the
mounting plate's front strip and power box. The compressor is the only body in the compressor bay
standing fore of the wall's interior plane — the condenser bears on that plane through
its rails and the fuse clamp stands clear behind it — so the wall keeps its full section
across the rest of the front. `box-front` reads every placed body against the relieved
surface, region by region.

## Pump clamp field

The geometry in `printed-parts/enclosure/pump-tray/` supplies the fitted boss and motor
openings. The cap has one broad underside and two screw counterbores. Its surrounding crown
is level with the cartridge top; two conical wells leave the motor ends and terminal pairs exposed.
The screw seats and lower fitted surfaces remain on their holder datums.

Derek confirms the existing assembled cartridge and cap hold both pumps firmly with no vertical
play. [Physical-fit evidence](/hardware/reference/kamoer-kphm400/physical-fit.json) records that
observation and the requested open crown. The [scan review](/hardware/reference/kamoer-kphm400/scan-review.md)
records the independent surfaces and their assumed seating transform. A flange-only gap does
not identify the cap's complete contact path.

The octagonal openings locate the rear bosses in plan and clock. Their vertical path keeps
[5.609 mm](CLAMP_FRONT_SKIN) of smooth cradle skin ahead of the cap and
[10.91 mm](CLAMP_AFT_WALL) behind each octagon.

**Two M3 close one clamp onto one cradle.** Both screw heads sit in counterbores in the crown,
reached from above with the same 2.5 mm key as every other M3 in the box. Their full-length
heat-set inserts open upward in the cradle spine. Once the complete cartridge is withdrawn in Y,
back both screws out and the entire clamp lifts in Z; either pump then follows through the same
straight well. The cradle's centre clearance spans the clamp's complete fore/aft depth, so the
filled field has one unobstructed bench-service path. No zip tie or hidden underside fastener
closes a pump.

The fitted opening's exact source dimensions and section readings are in
[`pump-tray/README.md`](/hardware/printed-parts/enclosure/pump-tray/README.md). The enclosure
uses those fitted profiles for the boss openings and Ø37 mm motor bores.

**The lower cradle prints on its Z− floor.** Its filled bearing block, flush front, rounded
corners and both flank skins begin together on that bed and rise plumb. Each hand pocket's
flat roof takes support removable through the open side. The pump wells remain open above.
The print pauses once, before the layer over the two magnet slots.
**The top clamp prints on its crown** (`print_up` is −1 for `pump-cap`). Its boss
octagons open upward through the underside. Each motor bore opens through the crown in a
45° cone that the print builds without support; each screw-head seat is accessible through
its counterbore mouth on the crown. Each native preparation must record its support contacts
and removal paths at those regions.

## Cartridge contacts

**The cartridge connects as it seats.** A
[YYFKGCP 4-pin magnetic pogo pair](/hardware/reference/yyfkgcp-pogo-4p/yyfkgcp_pogo_4p.py)
mates across a [0.5 mm](POGO_FACE_GAP) contact-face gap. The cartridge's flat back
and bay bulkhead retain their [0.25 mm](CARTRIDGE_BULKHEAD_KISS) body clearance;
each connector face is recessed [0.125 mm](POGO_FACE_RECESS) into its printed host.
The female half, four flush pads between two magnets, is let into the clamp's aft
face. The male half, four sprung pins, stands opposite it in the bulkhead's fore
face. Both rows share one axis, on the centreline at z
[275.524 mm](POGO_AXIS_Z). Straight Y insertion is the pair's mating axis, so each pin meets its
pad head-on and nothing sweeps across either face. Seated, each pin is pressed
[0.5 mm](POGO_PIN_PRESS) of its 1.10 mm stroke, leaving [0.6 mm](POGO_PIN_SPARE). Each
contact is rated 12 V and 2 A.

The [mounting audit](/hardware/reference/yyfkgcp-pogo-4p/mounting-audit.md) covers
the current exported seats, drawing tolerances and physical evidence. The purchased
connector halves contain their own magnets. The separate eight-pair
[SB443-IN dock array](../pump-dock/magnet-retention.md) acts at the four fluid-port
row, its bare poles meeting at the cartridge's seat. Its retention does
not establish pin compression or electrical continuity. The
[RC62 ring-magnet print records](magnet-retention/README.md) retain their identified
pocket, covering-layer and rattle scopes; they do not qualify the SB443-IN mounts.
The nominal press is not a complete tolerance check: the seller's dimensions permit
0.80–1.20 mm pin protrusion. Applying ±0.05 mm face error per half about the
recessed positions gives 0.200–0.800 mm compression and 0.300 mm additional
closing allowance before full stroke. The accepted coupon's connector fit and
mating/compression retain their identified geometry scope; they do not qualify
the complete recessed seats or frame. Installed gap,
magnetic retention and operating contact resistance have no reported physical result.

Contacts pair by X: the two −X contacts serve the −X pump and the two +X contacts the +X pump.
The pair attracts only in its matching orientation. Keep its plastic faces 0.50 mm
apart with equal measured nonconductive shims during local mating checks, mark the end of
each half that will stand at −X, and seat both halves with that mark at −X.

**Each half bears on its ear plate.** The seat's mouth is the plate's outline,
[23.7 × 4.3 mm](POGO_MOUTH), cut from the face to the plate's back. That plane,
[3 mm](POGO_DATUM_DEPTH) behind the recessed connector face, is the datum the plate
lands on, 3.125 mm behind the printed host face. The
body's stadium continues behind it, and the tails and their solder joints stand in the lead
passage behind that. Two M1.4 × 8 socket-head screws pass the
ears' Ø1.5 mm holes into M1.4 × 4 × Ø2.3 brass heat-set inserts, each in a
[Ø2 × 5.5 mm](POGO_INSERT_HOLE) pilot starting 2 mm behind the ear datum, or 5.125 mm
inside the printed host face. A 2.6 mm wide loading stadium admits the entire knurl through that
setback. The full insert occupies depths 5.125–9.125 mm, the pilot ends at 10.625 mm,
and the M1.4×8 tip ends at 10.125 mm, engaging the whole 4 mm insert with 0.5 mm of
blind-tip room. Each head stands
[0.6 mm](POGO_HEAD_RECESS) behind the recessed connector face. Install the inserts before the half goes in, using the recessed-seat
procedure in [enclosure assembly](../../../assembly/enclosure-mechanical.md).
The supplier specifies the insert body, without a host-wall or hole-depth rule;
Ø2.0 is the starting fit and requires physical coupon qualification.

**Both seats are horizontal pockets.** Front-top builds in +Z and the clamp prints on its
crown, so each seat roof spans the mouth's 23.7 mm length along X between its round ends, with the
supported-surface allowance on the face that looks print-up. The insert pilots are plain
round Ø2 holes, so each knurl has stock all round it.

**The leads leave by the routes each print allows.** Behind the male, one
[Ø11 mm](POGO_LEAD_BORE) teardrop bore starts at the body's back and runs through the bulkhead to
its aft face, apex up, wide enough at the contact row for both outer tails and their solder
joints. Its apex keeps [3 mm](POGO_LEAD_BORE_ROOF) of bulkhead under the crown, so its axis
stands [0.8984 mm](POGO_LEAD_DROP) below the pair's. It opens through the aft face above the fore
valve tray's crown at z [274.45 mm](POGO_LEAD_EXIT_FLOOR) and ends on that face below it. Behind the female, a lead slot
opens through the clamp's crown, which is the clamp's bed face, and one
[4 × 3.5 mm](POGO_GROOVE) groove per pump carries that pump's pair along the crown into its
terminal well. The crown keeps [6.5 mm](POGO_CROWN_SKIN) of clamp over the seat's mouth.

## Display housing

The machine display sits on a 30° plane within the enclosure's [215 × 466.3 × 361 mm](BOX_SIZE)
outside dimensions. An R12 tangent curve joins that plane to the front wall, and
an R18 tangent curve joins it to the roof. The long side edges are R6. The rear
top edge remains square. The flat display plane is 87 mm long along its slope;
the front curve begins about 15.5 mm above the pump cartridge. Front-top prints its
top 2.6 mm in 0.08 mm layers, a third of its 0.24, where the R18 and the R6 roof edges
roll level into the roof.
The side rounds blend through the junction with the R12 standing front corners,
forming one continuous surface around each top-front corner.
The print-down roof fill follows the curved display junction at both side edges;
it joins the retained rounds without an exposed horizontal underside.

The face-up PET-GF display cover measures 125.5 × 83 × 3.84 mm with R6 corners.
It seats flush, with 0.30 mm clearance per side in X and 0.15 mm along the slope.
Its 107.5 × 71 mm window laps the glass through the 1 mm TPU gasket. The glass
face is 4.84 mm below the display plane and its back is 5.84 mm below it. The
106 × 69 × 17 mm module is offset 0.5 mm laterally and 1 mm down the slope.
The PCB opening is 23.84 mm deep, retaining 1 mm behind the module's rear face.
The flat display backing keeps at least 3.02 mm of stock behind the deepest
PCB-pocket corner.

Each horizontal wing is 1.44 mm thick, projects 3.60 mm and spans 70 mm. It has
0.60 mm clearance below the retaining roof and at least 3.00 mm of capture at
full sideways float. The 1.80 mm lips carry the cover; its back seats directly
against the receiver. The pockets open print-down through the display storey
to the existing lintel level, leaving the tee mechanism and bay below unchanged.
Shared-profile trees leave through the empty bay before the screen is installed.

The [accepted cover](../display-cover/face-up-trial/physical-acceptance.json)
passes shaking and has acceptable appearance with a small residual bow. Its
physical geometry and clearances are retained in the
[integrated checks](accepted-fit-integration/geometry-check.json).

The 19 mm housing and its internal ridge join the side walls and the pump-bay
bulkhead. Either side of the display's opening the storey beneath the housing is one
wall and one cavity. The wall stands on the pump bay's lintel and runs up into the
housing, between the display opening and the side cavity. The cavity runs from
its inboard plane out to 6 mm inside the side wall's flute valleys, and from the front wall
back to the plane of the pump bay's aft wall, straight up to the ceiling. It opens into
the bay across its whole floor, and its ceiling is 10.02 mm behind the display plane. Between the two walls the opening continues down to
the bay as one room, which holds the display's back and SIG-7's run to the ridge bore.
The display backing presents one broad vertical cavity face at Y92.75 up
to Z355, 3 mm behind the display's PCB pocket and 0.25 mm ahead of the funnel frame's
flat front. A 4.09 mm rise at its foot joins it to the bay bulkhead at 45°. The facet's
roof round ends on this face 0.19 mm under the roof plane. The front-top flanks carry
their complete 9 mm section to the roof opening.
Supports carry the lintel's flat underside, the room's short housing strips and the two
cavity ceilings from the bay; their geometry preserves the display seats and the catches.

The vertical flutes fade over their existing 5 mm end field as the front and sides
turn into the smooth top curves. The rounded display bezel and funnel rim remain
smooth. Print meshes use a 0.005 mm absolute surface tolerance and 0.05 radian
angular tolerance before the flute field is cut.

**Running it to the flanks closes the storey, and two electrical runs meet it.** SIG-7 crosses
the rib halfway up its straight section, [+32 mm](DISPLAY_LOOM_X) in X from the centreline —
**east**, the side it arrives on, since the run comes forward from the electronics bay along the +X
wall. Its four conductors are one flat ribbon, and an expandable braid opens over what is inside
it: over a single 4P ribbon the 1/2" sleeve lies at or under the
[12.7 mm](CABLE_SLEEVE_NOM) nominal it is bought by and never reaches the ceiling that figure
opens to, so the teardrop bore is that nominal with air all round — Ø[14.7 mm](CABLE_BORE). It
locates nothing and carries nothing; the display loom is dressed after it is through.

The **fixed J13-to-contact lead** leaves the contact pair's lead bore
([Cartridge contacts](#cartridge-contacts)), rises behind the bay bulkhead and lies along
its crown below the funnel frame. It returns toward the electronics bay through the +X half of the cavity, clear of
the manifold Wago and tube approaches. The display backing and the fore end of the 9 mm flank present
continuous inner walls. Keep the bare ribbon below the frame and clear of the
closing slides, with a relaxed exit at the insulated solder joints. Support its free
J13 end during assembly; unplug J13 by its housing before separating enclosure pieces.
Both ends stay fixed during a cartridge change. The contact body's screws take the
contact-separation load.

SIG-7 follows the same +X wall toward its separate display-loom bore. The
[fixed pump lead review](fixed-pump-lead-review.json) binds the continuous wall to the
current export and records the limits of the installed routing assessment. The loom bore is teardropped because
the piece beds on Z.

## Funnel opening

The 531 mL silicone funnel sits in a separate solid PET-GF frame centered at
Y161.70, with its outlet at the same Y centre. The frame's flat front and the brim's
square-cornered front edge stand together one running fit behind the display wall.
Its front rail pair slides into
front-top's receivers. The rear frame is 182.5 mm wide beside back-top's screw
blocks and has no rear rails. Its actual aft corners retain R6 plan rounds;
the clearance shoulders at Y199.75 remain square. `funnel_frame.py` uses the
production Z-seam head/channel section and fit allowances for the front pair.

The frame's brim bearing is Z349, its flat underside is Z299.9, and its two full-width
end corbels are 30° from vertical. Its socket has a 3 mm floor, pierced by an 11.25 mm
elbow-collet hole and the cradle's two wing slots. The silicone block rests on the cradle's
hook tops 3.15 mm above that socket floor. The 2.75 mm hooks leave 0.40 mm above
the web for static assembly and its supported finish; the receiving web retains 3 mm.
The front rail feet remain at Z306.9; front-top's receiver underside is Z307.4,
providing 0.50 mm for the running fit and its supported receiver face.
The roof surround's two side strips reach the flush Z355 roof plane and end at Y199.75,
one running clearance before the seam. The rear frame retains its Z349
envelope beneath the existing back-top roof. Front-top's opening clears the
removable side strips and roof tongue, leaving no fixed inward brim-bearing
ledge above the frame. The complete brim footprint retains 3 mm of frame
bearing beneath Z349. The rail channels retain their separate functional profile.
The funnel's integral silicone apron covers the exposed frame joints and
upper seam screw wells, reaching both exterior sides. Its mouth and cover
seat are Z358; the fitted cover reaches Z361. Its underside roof-contact rib
and spill-path geometry are recorded in the
[overflow review](../../zone-c/funnel/overflow-review/README.md).
See [`../../zone-c/funnel/`](../../zone-c/funnel/) for dimensions and the drain joint.

## back-top's ceiling

back-top's ceiling is **one slab, and it is the face the piece prints on.** The exterior
top is at z 355 and the rear storey's established pack lane at z [352](CEILING_LANE):
every body, port and anchor station under the ceiling is struck on that lane. The slab
carries [12 mm](BACK_TOP_CEILING_T) of section from the show face inward, to z
[343](BACK_TOP_CEILING_FACE), between the grown flanks and from the Y telescope's end to
the +Y wall — [9 mm](BACK_TOP_CEILING_GROWTH) more than the top wall's own `wall` — and
gives that section back over whatever stands in it. Every pocket opens from the slab's
interior face up to the lane and no further, so the top wall's own `wall` stands over each
one (`ceiling-show-cap`).

**Three kinds of pocket.** Each connected piece of a named purchased body that enters the slab,
or comes within the stated 1 mm crown clearance, earns its own rectangular plan pocket with
2 mm of assembly slip and a roof 1 mm beyond its crown
(`enclosure_assembly.ceiling_reliefs`; the named population is what keeps an unrelated
encroachment visible to `pack-closes`). Duplicate readings from the direct and lifted probes
collapse to one cutter. The ASSE chain's five overlapping section plans share one flat floor
without changing any plan edge, and the flow meter's body and two arms do the same. Relay #1 and
the ground stack share one named roof plane and one local connector across their 1.181 mm plan
gap; the ground stack's two overlapping source rectangles alone take their small rectangular
envelope. No other pair is merged by proximity. Where a pocket runs on out of another body's
overlapping pocket under the same roof, both its sides less than a wall inside that pocket's,
the slab takes it with that pocket's sides (`enclosure._back_top_ceiling`): the gas chain's two
check adapters and the gasher's crown open as one channel. Gasher's singleton crown pocket
keeps its plan and is exactly one 3 mm wall deep; every other local pocket between zero and
3 mm deep is a producer error. The C14's ceiling pocket is its canonical slipped flange profile
continued along the insertion run, so the pocket and the flange seat are one outline.
The flow meter's two anchors and every rib a zip tie closes on
the ceiling — the regulator's — get the room their zip tie's
loop comes down: over the tie band alone, the rib's reach plus the tie's thickness and its
routing air either side, from the axis plane up to the channel's roof and no deeper
(`_ceiling_tie_reliefs`); the rib is fused back afterwards and stands up off the bed with
its seat an upward-opening cradle in the print. And the tap-water chain's shared tie channel is open to the lane from the −X
flank to the far edge of the chain's own pocket over the span its two zip ties take
(`_ceiling_tie_channel_relief`), so each loop comes west over the chain's crown in the
`DECK_CEILING_CLEAR` lane and drops into the anchor's cavity through the mouth the flank
leaves it.

**Everything rooted on the ceiling is this piece's**: the flow meter's two anchors and the
three ribs bored for `carb-1`, `co2-2` and the WR1110's barrel, each drawn to the lane
through `piece_root_faces` and fused into its own pocket. Back-top is populated inverted
on the bench, ceiling down, and every one of those seats is a cradle a body drops into.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/enclosure.py`
→ the four `enclosure-*.step` pieces + `enclosure.step`. Wall, seam, boss, and
facet constants are at the top of `enclosure.py`. Prints the facet size, the
Y seam's corner stacks and screws, each piece's envelope vs. the H2C
bed, every piece-pair's slip fit, and the cold-core clearance.

## Sources
[value](NAME) texts are updated by:
- `/<stdin>`
- `/hardware/printed-parts/enclosure/enclosure/enclosure.py`
