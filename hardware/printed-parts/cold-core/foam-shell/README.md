# Cold-core insulation shell

3D-printed PET-GF enclosure for the soda machine's "cold core" — the
back-of-enclosure subsystem that holds the carbonator, the
copper evaporator coil wrapped around it, and two flavor reservoirs in
pockets on opposite sides. Pour-in-place polyurethane foam fills the
cavities around the wetted/cold parts for thermal insulation.

## Coordinate convention

The CadQuery script uses an explicit XY plane with +Z normal
(`xy_plane_z_up`), so geometry grows upward in +Z.

- **Z** is vertical. The floor sits at z=0; everything stacks upward from
  there.
- **X** is the reservoir axis. Two reservoir pockets sit on opposite sides along X.
- **Y** is perpendicular to the reservoir axis.

## Physical inputs

- **Carbonator** — 5.000" OD × 0.065" wall × 6.000" cut length 316 SS
  welded tube (OnlineMetals #12498). Two 1/4"-thick 316 SS endcap plates
  laser-welded internally, recessed flush with the tube ends. Hand-tapped
  1/4" NPT, four ports total — two top plate (water inlet, PRV), two
  bottom plate (CO2 inlet, water outlet). Both plates are clocked so the
  port pairs stand on the shell's **±Y** axis
  (`_cold_core_interface.carbonator_port_offset`); the float rod's register, at
  right angles to each plate's own pair, is what holds the two together. Carbonator assembled height = tube
  length = **[152.4 mm](TANK_H)**. Outer radius = **[63.5 mm](TANK_R)**.
- **Reservoir** — printed rigid PETG flavor reservoir, one per flavor,
  two per cold core, standing on its pocket's floor. **Two mouths, both in its
  cap, and they never share one.** The FILL is a ⌀[7.5 mm](TUBE_HOLE_D) bore
  opening into the headspace above the liquid; the DRAW is a second bore the
  line goes on down through to the flat floor as its own dip tube. Everything
  that enters has to cross the cavity to leave. The floor carries a printed boss
  for the internal SS float rod. Body envelope: **[140.5 mm](RESERVOIR_W) wide (along Y)
  × [48.5 mm](RESERVOIR_D) deep (along X, radially outward) × [199.9 mm](RESERVOIR_H)
  tall**, sized to hold ≥ 1 L usable per reservoir. Reservoir geometry
  and internal features live at [`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/).
- **Evaporator coil** — 1/4" OD × 0.187" ID × 0.031" wall ACR copper,
  hand-wound helically around the carbonator exterior, bonded with 3M 425
  aluminum foil tape. ~6.35 mm radial occupancy plus tolerance — budgeted
  at [7 mm](COIL_GAP). The coil is embedded in the inner slice of the
  cylinder's foam blanket; pour foam fills the helical gaps between wraps
  and out to the reservoir wall.
- **Carbonator-port fittings** — 1/4" NPT 90° elbows on every port, turning the
  line laterally. ~[30 mm](ELBOW_ENV) vertical envelope per elbow above
  and below the carbonator. Each is clocked to the line it feeds, which is what lets
  a run leave straight. The bottom-plate CO2 port's elbow carries a
  **PP010822E 1/4" PTC × 1/4" NPT M adapter** on its outlet; that pair is made
  up on the carbonator at the bench and hangs inboard of the support ring's bore,
  so it descends in open space as the carbonator seats. Its collet faces the CO2
  bore at y = [-19.05](CO2_BORE_Y), and the 1/4" OD line arrives on that axis
  from the port lane — laid down the lane from the top cap before the cap goes
  on, not pushed in from outside.

## Shells

The geometry is built up from open-topped sub-shells that union into
one foam-shell solid. **Ordinary standing walls use [2.38 mm](FSHELL_WALL_T);
the floor remains [2 mm](FSHELL_FLOOR_T).** Reservoir-facing cavity profiles,
reed slots, screw axes and component heights have independent fit datums.
The [integration receipt](../casing-integration-review.json) binds their geometric checks.

### reservoir_pocket_walls

Two reservoir pockets, one on each ±X side of the cold-core, mirrored
across the YZ plane. Each pocket is a four-walled enclosure (open at
+Z; the outer_shell's floor closes the bottom; the shell's open +Z
top receives the foam pour):

- **Far ±X wall** — outboard face at x = ±[131.9 mm](POCKET_X_OUTER), cavity face at
  x = ±[129.5 mm](POCKET_X_INNER).
- **+Y wall** — outboard face at y = +[72.88 mm](POCKET_Y_OUTER), cavity face at y = +[70.5 mm](POCKET_Y_INNER).
- **−Y wall** — outboard face at y = −[72.88 mm](POCKET_Y_OUTER), cavity face at y = −[70.5 mm](POCKET_Y_INNER).
  The ±Y half-width is the reservoir's own standalone flavor-charge
  dimension (the window that holds 2 × SodaStream 0.44 L bottles); it
  is not derived from the centerward-arc radius, so growing the
  cylinder's foam blanket slides the pocket outward without resizing
  or splaying the reservoir.
- **Centerward wall** — the only curved wall. Its cavity-side face
  rides on a cylinder of radius **[80.5 mm](POCKET_ARC_R)** (centered on the
  cold-core Z axis); its carbonator-side face is concentric one wall-thickness
  inboard. That carbonator-side face is the reservoir's carbonator-facing wall, and
  because it is a concentric arc the span from the cylinder OD
  (R = [63.5 mm](TANK_R)) out to it is a uniform 14.62 mm of foam around the
  wrapped arc — the cylinder's designed foam blanket, with the 1/4" ACR
  copper coil ([7 mm](COIL_GAP) radial) embedded in its inner slice and
  pour foam filling everywhere the copper isn't.

The centerward wall is one continuous curved wall built from three
arc segments along its length:

1. A **middle segment** — the cylindrical arc that wraps the carbonator+coil
   envelope, running from y = −[60 mm](POCKET_ARC_TRANSITION_Y) to y = +[60 mm](POCKET_ARC_TRANSITION_Y).
2. Two **transition segments**, one at each ±Y end — short
   [8.42 mm](TRANSITION_ARC_R)-radius arcs that swing the wall out from
   the middle arc to the pocket's ±Y wall. Each transition arc is
   tangent to the middle arc and to the ±Y outboard face; its
   carbonator-side face has radius [8.42 mm](TRANSITION_ARC_R) and its
   cavity-side face is concentric with the same center but a slightly
   smaller radius derived from geometry.

The two **far-side corners** (where the far +X wall meets the ±Y
walls) are filleted: **[6.25 mm](POCKET_CORNER_R) inner radius**,
outer radius one wall-thickness larger (so the wall thickness stays
uniform through the bend). The inner radius matches the rigid PETG
reservoir's outer fillet plus the [0.25 mm](RESERVOIR_GAP) clearance, so
the reservoir slides into a snugly-mated pocket with uniform clearance
around the corner.

The pocket is **open along its centerward face into the foam zone
inside the centerward arc envelope** — there's no wall at radius
R < [78.12 mm](POCKET_ARC_INNER_R). During operation, that interior region
holds the carbonator + copper coil, and the foam pour fills the full 14.62 mm
blanket from the cylinder OD out to the wall's carbonator-side face —
around and between the embedded helical wraps.

The four walls of each pocket are traced as a single connected
outer-perimeter polyline (with the matching cavity-perimeter polyline
cut out of it), so the four walls union into one solid by
construction. The +X pocket is traced explicitly; the −X pocket is
its mirror across YZ. Total assembly height = [213.4 mm](OUTER_H).

### carbonator_support_ring

Annular ring sitting inside the lower portion of the assembly,
holding the carbonator up by its outer rim. The ring's outer face sits on
the carbonator+coil envelope (R = 70.5, the carbonator OD plus the coil radial
clearance) — inboard of the pocket's centerward wall, which has moved
outward with the foam blanket. Its inner face sits [9 mm](SUPPORT_RING_W)
inboard. The top face is a flat annular plateau where the carbonator's outer
rim rests, [30 mm](SUPPORT_RING_H) tall above the floor.

Inboard of the ring's inner face (R < [61.5 mm](SUPPORT_RING_INNER_R))
is open volume — so the carbonator's bottom-plate fittings have unobstructed
downward space, and pour foam fills around them.

Four 30°-wide angular slots are cut through the ring, centred at
37°/127°/217°/307° — the diagonals clocked −8° (`_support_ring.slot_clock`) — leaving
four 60° support segments. The slots let pour foam reach the under-carbonator
floor regardless of which cavity it enters from, and they are where the two
bottom-plate lines cross the ring, one slot each, so the ring is bored nowhere.

The **CO2 inlet** takes a ⌀[7.5 mm](TUBE_HOLE_D) reach in to the bottom plate's
lane-side port at y = [-19.05](CO2_BORE_Y), z = [17](CO2_BORE_Z), **leaning** across the
shell's floor from the port lane through the 307° slot. The line falls the shell's whole
height down that lane, runs along its floor and turns in where the lean both lands in
the slot and stays outboard of reservoir A's pocket corner — the reservoir stands on that
pocket's floor. The **carbonated-water outlet** crosses the 217° slot on the column it
climbs, straight out from its own port.

Neither notches a bearing segment and all four stay whole.
`_port_cuts` measures both crossings against `ring_slot_spans` every build, so moving a
column or the ring fails rather than drifts.

### outer_shell

Outer rectangular cup framing the whole foam-shell: floor + four
perimeter walls + [10](BOSS_COUNT) ⌀[8 mm](BOSS_D) cylindrical bosses. Total height
matches the foam-shell outer height of [213.4 mm](OUTER_H).
Outer footprint [282.4 mm](SHELL_OUTER_X) × [180.4](FSHELL_OUTER_Y). The **short** axis is
the one that matters to the appliance: the foam assembly is yawed a quarter turn
in the enclosure, so 181 is what sets the machine's width and the ±X faces are
its front and back. The outboard foam-pour gap is split by direction: the ±Y
faces leave [14.94 mm](FSHELL_POUR_BAND) of foam-pour zone between the outer_shell's inner
face and the pocket's ±Y walls, while on the ±X side there is no outboard foam —
the reservoir's reed channel butts the outer shell wall. The 283 mm is held that
way: the reservoir, shifted outward by the cylinder's foam blanket, lands with
its reed channel against the shell wall, and the foam that would otherwise sit
outboard of the reed has moved to the cylinder side. Those two ±Y bands are what
every penetration travels along — see §Port lane.

The four vertical corners are rounded — the exterior wall is a true
[11.7 mm](CORNER_ROUND_R)-radius quarter-arc on the outer face, the inner
face concentric one wall inboard — so the warp-prone sharp
corner is gone. STEP and STL describe the same smooth surface.

#### Smooth casing

The shell, cups and lid edges share a plain 282.4 × 180.4 mm casing footprint,
with R11.7 outside corners. The 2.38 mm exterior walls and pocket walls take
stock from their foam-facing sides; the reservoir cavities keep 0.25 mm
running clearance to the printed reservoirs. The floor is 2 mm.

Foil tape sits directly on the smooth perimeter. Its 0.30 mm per-face envelope
allowance contains at most two 0.12 mm tape layers without a groove. The
component mounts, clamp axes and nominal 253.4 mm stack height retain their
independent datums. Copper-cover jambs retain their own seating planes.

**Every boss stands hard against the wall it leans on, and the station names which
wall that is** — never the sign of its own coordinates, which for a boss centred on a
±X wall is neither. Four sit over the reservoir pockets' own far walls, near the ±X
ends. Four more are mid-long-side, two to each ±Y wall, offset in X by
±[40 mm](MID_BOSS_OFFSET). The last two stand centred on each ±X wall. The whole pattern is symmetric under a
180° turn about Z, which is what leaves the top cap free to install either way round.

That is a placement rule the PORT LANE sets, not a preference. A boss seated
diagonally IN a corner — its cylinder tangent to the exterior arc, which is the
deepest seat available — reaches diagonally into the ±Y pour band, and closed the
one corner every front penetration has to travel through. Held against the wall
instead, every ±Y boss reaches exactly [8 mm](BOSS_D) in from its outer face and
leaves the same clear lane. The two ±X bosses are in neither band — they stand on the
face those lines arrive at, clear of both lanes in y. See §Port lane.

Each boss is tied into the wall with the cylinder + corner-fill teardrop idiom of
the reservoir pocket-corner supports, so it fuses into the outer skin (one
wall-thickness of PET-GF over the insert) instead of meeting the wall on a
knife-edge seam. The four corner bosses also get a web toward the ±X wall they stand
near, which stiffens that corner; a ±Y boss gets one toward its own ±Y wall and a ±X
boss one toward its own ±X wall.
Each carries a heat-set insert pocket at each end (drilled in from each face) —
[20](STACK_INSERTS) inserts total, [10](FACE_SCREWS) per face, for fastening the
foam-cap stacks.

The outer **−X** wall carries one Z-elongated slot on each of its two lanes and
**no round bore at all**. **Nothing else crosses it** — this face is mated against the
refrigeration base, so a bore struck here opens into that base rather than into the
machine. All seven fluid lines leave by the top cap's conduits, along with the
two reservoir reed cables and sensor/earth loom in their own passages. See Penetrations.

### foam_cap and foam_cap_lid

The `foam_cap` is a cup matching the outer shell's footprint,
printed twice — [15.7 mm](CAP_H) of pour at the bottom end and
[12.3 mm](CAP_H_TOP) at the top, whose lid takes the band its wall
would have stood in. The top cap opens +Z (mouth up); the bottom cap
is the same cup built mouth-down so its open ceiling faces −Z. Each seats with its floor against the shell's end face and
its open mouth + lid pointing outward — the lid is the outermost
(extreme-Z) layer at that end, most +Z on top and most −Z on the
bottom. Both share the one screw pattern (below), so the mouth-down
bottom cap lands its screws on the shell's existing bottom-face
inserts with no rotation. The cap interior receives the foam pour
through the pour and vent holes in the lid.

The `foam_cap_lid` is a [2.38 mm](FSHELL_WALL_T) plate matching the same outer
footprint, closing a cap's open mouth. It has the pour hole (Ø [20 mm](POUR_D))
and two vent holes (Ø [6 mm](LID_VENT_D)), and it carries a pad at each of the
[10](FACE_SCREWS) screw stations on its mouth-facing side — "The head sits in the lid" below.
It is the clamp for the pour and it stays: the lid ships bolted to its cap, and
its outer face is the plane the core stands on at the bottom and the water deck
and the electronics stand on at the top.

The shell, cups and lids share the same **[10](BOSS_COUNT) clamp axes** —
four corners, four long-wall stations at X ±[40 mm](MID_BOSS_OFFSET), and
one centred on each ±X wall. The shell and cup hosts use the common
⌀[8 mm](BOSS_D) cylinder and teardrop-web builder. The lower lid's head
pads add 1.28 mm radially, giving a 10.56 mm diameter and 2.38 mm inward wall
around each ⌀5.8 mm head pocket. The bottom cup receives those pads in
10.86 mm pockets with 0.15 mm radial static clearance. Every position
passes an M3 screw through the lid and cup into its shell insert.
See "Cap-to-outer-shell joinery" below.

### Dry casing seams

The shell and foam-filled caps enclose insulation. Their seams carry no
liquid or operating pressure; the reservoirs and carbonator have their own
wet closures. Both foam pours cure before the caps are assembled onto the
body. The dry casing has no TPU cap gasket.

Each cap-to-shell seat and cap-to-lid seat has 0.15 mm static clearance.
The cup's mating faces retreat into the cup while its floor grows inward
by the same amount, retaining a complete 2 mm floor. The shell, lid faces,
deck hardware and complete 253.4 mm stack retain their construction datums.
The 253.4 mm figure is the nominal CAD envelope; screw clamping may take up
the four 0.15 mm seating allowances, making the physical core shorter.
The bottom lid's pad ends and top cap's flush deck columns have the same
axial allowance; their radial fits retain their own dimensions.

The shell, cups and lids have plain vertical outer faces. Foil sits on these
faces within a 0.30 mm per-side allowance around the casing. Each corner pilot
retains at least 1.69 mm radial wall through its depth; the shared clamp axes
stand independently of the ordinary wall thickness.

Seal each assembled end with one continuous band of the already-owned
**3M 425 aluminum foil tape**, covering both its cap/shell and cap/lid
joints, reaching at least 13 mm onto the shell. Trim the 50.8 mm stock to the
assembled end, ending at the lid's outside
edge without folding onto its flat bearing face. Apply to clean, dry parts
at room temperature. Press around the rounded corners and burnish the
edges; overlap the band's ends by 25 mm. Use at most two foil layers, with
no patches stacked over that overlap. The head pockets open to the casing
edge, with radial corner openings and 2.38 mm inward stock on the lower
lid's inward pad walls. The complete 2 mm bearing floors remain under
the screw heads. The band
spans those small dry side openings. Keep the axial driver openings on
the lid's flat outer face, mounting seats and fluid passages clear. Burnish
the foil onto the smooth lands around the openings without wrinkles or
air channels. This local seam seal is not a complete cold-core vapor-barrier or lifetime qualification.

[3M's technical data](https://multimedia.3m.com/mws/media/2366321O/3m-aluminum-foil-tape-425.pdf)
identifies low moisture-vapor transmission and moisture-barrier use in
appliances. This supports the local static-seam application. The
[casing integration receipt](../casing-integration-review.json) records the
rigid seats, floor stock, screw reach and fixed stack planes.
Reservoir gaskets retain their separate wetted-seal function and accepted
physical evidence.

#### Why the operating core's seams are sealed

The upper cap/shell joint opens into the body's component and insulation
space. At its nominal 0.15 mm seat allowance, a path crosses above the
flush-trimmed body foam and enters the unfilled clearance around the chilled
water outlet tube. That conduit is 7.5 mm across around the measured 6.5 mm
tube. The reservoir pockets and reed channels also remain air cavities.
The [one-off seam review](../foam-cap/seam-moisture-review.json) records a
continuous native route clear of the shell, cup, lid and tube envelope from
the cabinet into this conduit. Clamping may close the nominal allowance;
dry printed contact provides no specified continuous air seal.

The carbonator wall control is 2–4 °C. For an illustrative room condition
of 25 °C and 50% RH, the calculated dew point is 13.9 °C; at 60% RH it is
16.7 °C. Cabinet air admitted beside a tube carrying chilled water can
therefore condense inside the core. The outside seam itself need not be
below the dew point, and no bulk air flow is needed for vapor diffusion
along a connected gap. These examples establish the design reason to close
the route; they are not measurements of this core's leak rate or wetting time.

[ASHRAE's refrigeration insulation guidance](https://handbook.ashrae.org/Handbooks/R26/IP/R26_Ch10/R26_Ch10_ip.aspx)
calls for sealing seams and penetrations on the warm side of below-ambient
insulation. Even insulation that itself supplies sufficient vapor resistance
needs sealed joints. The
[foam supplier](https://fiberglasssupplydepot.com/Expandable-Polyurethane-Pour-Foam-2lb.html)
describes a 95–98% closed-cell, water-resistant material; that does not close
the casing's gaps or establish its vapor permeance at our thickness.

The cap/lid joints border the separate cap insulation cavities. The bottom
cap/shell joint lies between two printed floors and has no equivalent open
route into the body foam; the common lower band covers it while sealing
the lower cap/lid joint. These joints do not all have the same exposure.

The foil bands close the perimeter joints only. Tube/cable annuli, copper
exits, screw access and exposed foam at the cap pour/vent holes belong to
the rest of the warm-side moisture boundary. Their presence prevents a
complete vapor-retarder claim from these bands alone. Functional reservoir
vents, fluid lumens and the PRV discharge route must stay open. Specify the
complete boundary's closure materials, application and any required printed
sealing lands for refrigerated operation before releasing affected prints.
The perimeter-seam decision alone does not close the
[complete appliance readiness assessment](../../enclosure/print-readiness.md#remaining-work-for-the-complete-working-appliance).

## Cap-to-outer-shell joinery

Each cap (top and bottom) is fastened to the outer_shell with **[10](FACE_SCREWS)
M3 × 25 mm DIN 912 socket head cap screws, 12.9 alloy steel, black
oxide finish** ([BNUOK B0DJQGF665](https://www.amazon.com/dp/B0DJQGF665))
threading into **[10](FACE_SCREWS) ruthex RX-M3x5.7 full-length heat-set inserts**
([B08BCRZZS3](https://www.amazon.com/dp/B08BCRZZS3); per-build insert counts in
[`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §13) pressed into the
corresponding face of the outer_shell. **[20](STACK_INSERTS) inserts and
[20](STACK_INSERTS) screws total per outer_shell:** [10](FACE_SCREWS) on the top face
accepting the top-cap screws threading down from above, [10](FACE_SCREWS) on the
bottom face accepting the bottom-cap screws threading up from below.

Each screw engages a heat-set insert in the outer_shell with a small relief
below the insert for tip clearance. See `_foam_cap.py` and
`_cold_core_interface.py` for the values that set the screw length.

Insert pocket: Ø 4.0 mm × [10.5 mm](INSERT_DEPTH) deep (insert
engagement + tip-relief), drilled in from each face.

### The head sits in the lid

At each station the cap's boss column stops [3.4 mm](HEAD_PAD_H) short of the
cup's mouth, and the lid carries a pad of that same boss cross-section into the
relief — both trimmed to the one footprint, the relief a slip larger. The pad is
counterbored Ø[5.8 mm](HEAD_CBORE_D) from the lid's outer face and the
[3 mm](SCREW_HEAD_H) head drops into it, leaving one wall of PET-GF between the
head and the boss section it bears on. The outer face is a plane: the bottom
cap's is what the whole core stands on.

From under the head an M3 × [25](CAP_SCREW_LEN) crosses the land, the continuous
pad-and-column section and dry-seat allowances, reaching [8.4 mm](CAP_SCREW_REACH) past the
shell's face — the whole [5.7 mm](INSERT_LEN) of the insert, with
[2.1 mm](TIP_CLEAR) of nominal pocket under the tip. `_cold_core_interface.py` asserts
both ends of that.

## Penetrations

Thirteen pass-throughs total — ten tube lines, two reservoir reed cables and the sensor/earth loom. Every tube is **1/4" OD
(6.35 mm nominal, about 6.5 mm measured)**. Passive passages through printed
material are ⌀[7.5 mm](TUBE_HOLE_D), with 0.5 mm radial air around the measured
tube for insertion below the reservoirs and through the cap. These passages
do not retain the tube. Faucet and organizer fits use their own dimensions.

**THE CORE IS REACHED THROUGH ITS LID.** All seven fluid lines leave by the TOP, each up a
conduit through the foam cap and its lid (`_cold_core_interface.cap_conduits`), and the
service bay stands on the face they open on. What is left on the −X face — the one the
enclosure's quarter turn puts at the front of the machine, mated flat against the
refrigeration base — is the two copper evaporator lines in their lane slots. The PRV vent crosses
the +Y flank into the enclosure’s exterior relief chase.

| # | Pass-through | Opening | Carries |
|---|---|---|---|
| 1 | Reed cable (+X) | top-cap reed conduit | the reservoir-A level reeds' cable |
| 2 | Reed cable (−X) | top-cap reed conduit | the reservoir-B level reeds' cable |
| 3 | Copper evaporator inlet | port-lane slot | 1/4" OD ACR copper, made up on the condenser's own outlet pick across the plane the two bodies share |
| 4 | Copper evaporator outlet | west-lane slot | 1/4" OD ACR copper, made up on the compressor's own suction pick across that same plane |
| 5 | PRV vent | **+Y flank** | short 1/4" OD LLDPE from the prv-shroud’s barrel into the enclosure’s west-wall relief chase, which opens outside the cabinet (see [`prv-shroud`](/hardware/printed-parts/cold-core/prv-shroud/)) |
| 6 | Water inlet | **plain aft top-cap guide** `water-in` | one continuous tube from the pump's check and downward outlet elbow, through the curved cap corridor to the fixed top-plate −Y adapter **above the water line**, where the water-inlet jet discharges into headspace against the CO2 back-pressure; the guide adds no joint or cut |
| 7 | Carbonated-water outlet | **top-cap conduit** `carb-water-out` | to the dispense faucet — off the bottom-plate Port 3 elbow **under the liquid**, across under the carbonator, out through the ring's 217° slot and up beside the coil |
| 8 | CO2 inlet | **top-cap conduit** `co2-in` | from the neoFit ACHV44-E check downstream of the PISCO regulator — down the port lane, along its floor, then through the ring's 307° slot onto Port 1, which opens **directly below the liquid** |
| 9 | Reservoir A draw | **top-cap conduit** `reservoir-a` | A's dip tube: straight down through the draw bore in A's own cap to **its floor** |
| 10 | Reservoir B draw | **top-cap conduit** `reservoir-b` | one continuous dip tube through the cap's 3.5 mm passive shift and B's draw bore to its floor |
| 11 | Reservoir A fill | **top-cap conduit** `reservoir-a-fill` | through the cap's 3.5 mm passive shift to A's fill bore, **above its liquid** |
| 12 | Reservoir B fill | **two fitted cap pockets** `reservoir-b-fill` | an upper JG elbow, short tube and lower trimmed NeoFit stem through B's fill bore, ending in the headspace |
| 13 | Sensor and earth loom | top-cap `sensor-cable` passage | temperature-bus conductors, carbonator reed conductors and carbonator earth lead |

**The carbonator and both reservoirs are filled high and drawn low** — the carbonator at
its two plates, each reservoir through its cap, from above the liquid and from its floor. Nothing that enters one can leave
without crossing it, which is what the air-purge and clean-flush service modes run on.

The selected warm-side water and CO2 groups use 1/4-inch push-connect
interfaces, as defined by the [above-core arrangement](/hardware/manifold-layout/above-core.md).
Their tubes continue through the plain guides to the carbonator fittings.
Every fluid line inside this core is 1/4-inch OD.

### The runs themselves

[`_internal_routes.py`](/hardware/printed-parts/cold-core/_internal_routes.py) draws every
line as a swept solid on the tube's own centreline, and `foam_assembly.py` measures each
against the shell, the carbonator with its wrapped coil, and both reservoirs with their caps —
then lands them as `foam-assembly/internal-routes.step`. A line in here is a void's
occupant: it appears in no bounding box and collides with nothing, so drawing it is the
only way to know it fits.

Each run also reports the **arc it turns at**, found by drawing it at the stock's own bend
floor — `_routing.STOCKS`, the same bench-tested figure every run outside the core is
graded against — and stepping down until it stops meeting anything. That reading is the
corridor's answer, not a choice, and the last line of the report is the pack's short list.

Every one turns at the stock arc. Where a line has to reach and rise at once it **leans** —
one diagonal in place of two square corners on a step's own width — which is what the
carbonated water does on its way up beside the coil, and again at the top to put itself on
its conduit's column. No line crosses a bag pocket: each reservoir's two lines are straight
drops through its own cap, and the carbonated water's climb stands in the middle of the
annulus between the coil and reservoir B's pocket wall.

### Port lane

**Nothing reaches the −X face head-on.** The reservoir pockets fill both ±X ends
of the shell, so a line from the carbonator or from either pocket gets there along the
−Y pour band — the [14.94 mm](OUTER_GAP) strip that runs the shell's whole length
outboard of both pockets.

What a line may use of that band is the **lane**: the strip inboard of every
attachment boss, y [-82.5 to -72.5](LANE_Y) — [10 mm](LANE_W) wide, on
y = [-77.5](LANE_MID_Y). Every ±Y boss stands hard against its wall and reaches
[8 mm](BOSS_D) in from its outer face, so the lane is exactly what they leave, and
it runs clear from one corner round to the other at every height above the floor
slab. `foam_shell.py` fails the build on a station whose bore does not go through.

Approaching a ±X wall the corner rounds' inner arcs — concentric one wall inboard
of the exterior ones — bulge into the lane's outboard edge and pinch it to about a
bore's width at the very corner. That is not an obstruction: it is the material
each station's bore is cut through.

The lane is **one bore wide**, which is what makes each lane a column rather than a
grid.

### What holds the slot up

A lane's floor is the pocket floor's own band — [6.9 mm](SLOT_FLOOR_Z), one wall of PET-GF
over the floor, one bore of lane, one wall again. The slot does not sit there: it stands
one lane pitch above it, on `_cold_core_interface.front_slot_standoff`.

That standoff is **stated, not derived**. Nothing inside this shell sets it — what does is
the appliance's own floor slab outside this face, which both of the evaporator's coppers
would cross into if the slot dropped to the bottom of its lane. `enclosure_assembly` reads
that against the loop itself, on `clearance-floor` and `pack-closes`, so a
slot that drops reads red over there rather than quietly walking the refrigerant loop into
a wall. `copper_plugs.evap_cross_z` takes the slot's own reach up from this top.

**Two fluid lines use this lane and neither crosses this wall:** the CO2 falls the
lane's whole height and runs along its floor at the plate band before it turns in; the
carbonated water joins only once the carbonator's top plate is under it. The lane is one bore
wide, so what keeps them apart is the storey each takes, and
`_internal_routes.report_routes` is what proves it. Above the shell,
`cap_conduit_pair_neck` holds the two columns in this lane apart.

### The two lane slots and their copper plug stacks

The −X outer_shell wall carries a **Z-elongated slot** on each of its two lanes, and
between them they take the two copper evaporator lines, one lane pitch up off each lane’s floor. Each slot is
⌀[6.65 mm](PLUG_ARCH_D) wide (rounded ends along Z) and both are cut by
`cut_lane_slots` in `_port_cuts.py`. A slot's
top extends past the wall top so no sliver of wall material remains
above it — the plugs slide down into the slot from
above during assembly. With the centerward wall extending only to
y = ±[72.88 mm](POCKET_Y_OUTER) (where it meets the ±Y walls via the
transition arcs), each slot pierces only this one outer wall.

**There are two because the refrigeration base is two bodies.** This wall is mated face
to face with that base: the condenser stands against the port lane's face and the
compressor just short of the west lane's. So the evaporator's two coppers leave by
opposite lanes, each on the pick the body behind it already carries — the condenser's
joint made up across the plane the two bodies share, the compressor's cut and brazed
across the standoff its pressed shell leaves. A slot rather than a bore is the coil's
doing either way — a tail formed
off a coil that is lowered into the cavity travels *down* the wall to its station rather
than being threaded through it.

Both the slots and the plug stacks that fill them are authored in the **port frame** —
the frame where the wall a port crosses is a −Y wall and the slot runs lateral in
x — and `_cold_core_interface.port_to_shell` is the one transform that carries that
frame onto a lane. A pose turned by hand alongside a slot cut by hand is two
implementations of one transform; this way the plug and the hole it plugs cannot
land in two places. One frame serves both lanes, so a plug drawn there fits either.

Pass-through Z heights (centers, absolute in the model — the floor occupies
z = 0 to z = [2.38 mm](FSHELL_WALL_T), so subtract that for a height above the
cavity floor):

[port-lane evap-inlet 28.43; west-lane evap-outlet 28.43](SLOT_Z)

The two coppers cross at the same height, each after dropping down its own lane.
The slots sit in the bottom [28.43 mm](COLUMN_TOP) band of a wall
[213.4 mm](OUTER_H) tall. `copper_plugs.py` derives their stations.
The PRV vent has a separate +Y-flank opening; it does not enter either copper slot.

Two printed PETG **copper plugs**, one per lane, slide down into their own lane's slot
from above:

| Plug | Lane | Z span (mm) | Z end arches |
|---|---|---|---|
| `copper-plug-west` | west | [28.43 → 213.4](PLUG_SPAN_WEST) | bottom end only (top flat) |
| `copper-plug-port` | port | [28.43 → 213.4](PLUG_SPAN_PORT) | bottom end only (top flat) |

Each plug runs from its own tube's center to the wall top, and the arch cutout at
its bottom end holds exactly half of that tube — the tube is the gap. **The two come
out the same solid**, because the two lanes carry one copper each and both cross at
the same height; they stay two parts because a plug is what fills one column, and a
station added to either lane divides that lane's plug alone.

Each plug has a **continuous interior flange** that overlaps both slot edges
by 1 mm and seats against the shell's local jamb planes. This 8.65 mm wide,
1 mm thick lip keeps foam inside along the slot; outward foam pressure bears
it against the seat. The 6.15 mm wide web spans the copper-cover port frame.
The local casing jamb is 2.90 mm thick; the cover retains its independent
3.20 mm grip datum and printed-face clearances.

The **exterior flange is limited to two 8 mm long retaining tabs**, one at
each end of the web. Each tab is 8.65 mm wide and 1 mm thick. The wall slides
between a tab and the interior flange with its running and supported-face allowances, keeping the plug
aligned before the foam pour. The web and lower tab start 2.35 mm above the
copper's centre to leave printable stock beside the arch. Print with the
continuous interior flange flat on the bed. See `copper-plugs/copper_plugs.py`
for the middle and end-tab cross-sections.

Each plug end that abuts a tube has a **⌀[6.65 mm](PLUG_ARCH_D) half-circle
arch cutout** centered at x = 0, so the plug seats around the tube
without crushing it. Both plugs arch at the bottom only and end flat at the shell
rim beneath the cap. Small gaps around the copper and the rounded slot
bottom fill during the foam pour.

A column's last plug reaches the wall top with that flat face, so nothing is left
open above either stack. Once the two plugs are installed, what is left unfilled
in either slot along Z — the strip below that lane's lowest line, plus the narrow
clearance band around each tube — gets filled by the body foam pour.

## Assembly and foam pour

Production-procedure framing at [`/hardware/assembly/cold-core.md`](/hardware/assembly/cold-core.md). The geometry detail below is the source-of-truth for the shells and the pour paths; the assembly doc is the production-cadence wrapper that places this pour in the appliance build sequence.

The cold core is foam-filled in **three pour operations** — one per cap
(each a self-contained cup + lid pour, done in parallel on the bench) and
the body pour into the shell's open +Z top.

### Body pour (after all body-side assembly)

Every internal component is installed first:

- Carbonator lowered into the centerward arc envelope, seated
  on the `carbonator_support_ring`. Its four port elbows are already made up and clocked
  to the lines they feed — the bottom-plate CO2 elbow onto the leaning reach, the
  bottom-plate outlet elbow toward −X, the top-plate inlet elbow toward +Y — with
  the water-side PP010822E and gas-side gray PI010822S collets hanging inboard
  of the ring. The top water-inlet elbow carries its qualified jet cap; the bottom
  gas opening is plain.
- Copper evaporator coil hand-wound around the carbonator exterior and
  bonded with 3M 425 aluminum foil tape.
- Reservoirs installed into the two reservoir pockets.
- Copper evaporator inlet routed along the port lane and out through its slot; copper
  evaporator outlet routed along the west lane and out through that lane’s own slot. Each leaves its fitting and turns onto its
  lane, and each of the two coppers lands on the pick of the body standing against its
  own lane's face — the condenser's outlet east, the compressor's suction west.
- Water inlet: a 1/4" PTC × 1/4" NPT M adapter (JG PP010822E) made up on the
  lateral FNPT of the carbonator's top-plate −Y elbow, collet clocked onto the diagonal
  the line leaves on. One continuous 1/4-inch OD LLDPE tube follows the nominal R14
  cap corridor, east of the sensor passage, then rises through the aft `water-in` guide beneath the downward check outlet.
  The guide is plain: it adds no fitting, insertion or tube cut. Lay the complete
  route before pouring; use both CAD spans and actual receiving-end marks for
  its single blank per [Internal plumbing](/hardware/assembly/internal-plumbing.md#parts-and-cut-lengths).
- Two copper plugs slid down from above, one per lane, with the continuous
  interior flange facing the cavity and the shell wall held between it and
  the exterior end tabs. Each bottom arch seats over its copper and the top
  finishes flush with the shell rim.
- PRV shroud subassembly (`../prv-shroud/`) — already built and
  cured ahead of time, threaded into Port 4 at carbonator install — is
  here as part of the carbonator by the time the body pour happens.
  Press-fit a length of 1/4" OD LLDPE into the bore in the shroud's barrel and
  route it down the west lane, turn once and cross the +Y flank. Cut its free mouth
  flush with the flank to open into the enclosure’s exterior relief chase. The
  native route is [`_internal_routes.py`](/hardware/printed-parts/cold-core/_internal_routes.py)
  `prv-vent`; installed relief backpressure and capacity remain unqualified.
- Carbonated-water outlet off the bottom-plate Port 3 elbow, out to its own column
  on the +Y side of the plate's axis, then straight −Y under the carbonator and out
  through the ring's 217° slot into the annulus between the coil and reservoir B's
  pocket wall. From there it climbs beside the coil clear of the lane, and leans at
  the top to put itself on its conduit's own column for the last stock arc.
- CO2 inlet on the plate's lane-side port at y = [-19.05](CO2_BORE_Y),
  z = [17](CO2_BORE_Z) — its leaning reach crosses the ring's 307° slot and opens on
  the lane's floor. The line comes DOWN the lane from the top cap's `co2-in` conduit,
  runs along that floor to the lean and goes straight in onto the collet already made
  up under the plate.

These four potted runs are laid **before the top cap goes on**, because every one of
them leaves by the lid and every one is potted where it turns. The two reservoirs' lines
are not: each reservoir is filled and drawn through its own cap, and those lines go in
from above once the top cap is on (`reservoir/floor-and-dip-tube.md`).
[`_internal_routes.py`](/hardware/printed-parts/cold-core/_internal_routes.py) is
each run's drawn shape and the arc it turns at.

With everything in place, liquid foam is poured **directly into the
body's open +Z top** all at once — no lid on, no down-channels.
Foam falls into the body and fills one connected volume: the
**surrounding foam zone** between the outer_shell and the pockets'
±Y walls (the front/back foam-pour gap; the ±X reservoir side has no
outboard foam, its reed channel butting the shell wall). This zone
reaches the centerward space around the carbonator+coil through the gap at
the pockets' ±Y ends (y = ±[72.88 mm](POCKET_Y_OUTER)), where the ±Y
walls stop and the centerward walls' transition arcs swing in to join
them.

The **two reservoir pockets take no foam.** Each is occupied by its
reservoir, which fills the pocket to [0.25 mm](RESERVOIR_GAP) on all
four sides and leaves the same clearance at the top under the pocket
wall top — the pour has no way in. The reed channels are open
cavities and stay empty: their columns drop in after cure
([`../reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)).

The longest required traverse for the foam is around the back of the
coil at the ±X azimuths — the foam has to work through the embedded
helical wraps and fill the 14.62 mm blanket out to the centerward wall's
carbonator-side face, ~110 mm of arc to reach around from the ±Y entry.

Before the pour, mask the clearance gaps around installed tubes at the
outer exits with removable tape on the dry side. Keep tube mouths, collets and reed channels open. After cure, remove
the masks and trim any external foam flush.

### Final assembly (after the body foam pour has cured)

Drop the pre-soldered reed columns into the still-open reed channels,
then seat the foam-filled top cap onto the body's top edge with
[10](FACE_SCREWS) M3 × 25 SHCS into the top-face inserts, and the bottom cap
(mouth-down) under the body with [10](FACE_SCREWS) more into the bottom-face
inserts. Apply the exterior seam tape as specified under "Dry casing seams".

## Nominal walls and functional stock

Ordinary casing and pocket walls use 2.38 mm. Pocket cavities, reed slots,
copper-cover seats and hardware axes have separate fit datums; their local
junctions retain the stock their function requires. Floors are 2 mm, the
carbonator support ring retains its 9 mm radial section, and the top lid
retains its 5.4 mm equipment plate. The printed reservoirs and their caps
keep their own geometry and watertight PETG recipe.

## Print settings

The shell uses a 0.4 mm Standard-flow left nozzle, Classic with three wall
loops, and 15% gyroid in thicker regions. Three loops from each boundary
pack six perimeter beads across the ordinary 2.38 mm walls. PET-GF15 takes its filament settings from the
current shared [`petgf.3mf`](../../petgf.3mf), including the
[localized cooling policy](../../cooling/README.md).

Plate contents (when slicing): `foam-shell` alone; the two `foam-cap`s + their
two lids on a second plate. **The two
copper plugs are not on the shell's plate** — they are PETG
([bom.md §7](/hardware/ledger/bom.md)) and go on the small-PETG plate with the
drip pan, the PRV shroud, the reed bridge and the fuse clamp
([machine-time.md](/hardware/ledger/machine-time.md) §1).

### Printer / profile

- **Printer:** Bambu Lab H2C, **0.4 mm hardened nozzle, left hotend** —
  every abrasive stock runs left ([tools.md](/hardware/ledger/tools.md))
- **Hotend flow:** Standard; current inputs are declared in
  [`pieces.json`](../../enclosure/trial-preparation/pieces.json).
- **Print profile:** `petgf.3mf` 0.4 mm process
- **Layer height:** 0.24 mm (initial layer 0.20 mm)
- **Line width:** 0.42 mm outer, 0.45 mm inner
- **Wall loops:** 3, Classic
- **Top / bottom shells:** 4 / 3
- **Sparse infill:** 15 % gyroid
- **Speeds:** shared 0.4 mm process, capped at 18 mm³/s maximum volumetric flow.
  The native preparation records the emitted speeds.
- **Supports:** off (threshold 30°)
- **Brim:** auto, 5 mm width, 0.1 mm object gap, 0.15 mm elephant-foot
  compensation
- **Wrapping detection:** off

### Filament

- **Material:** Polymaker Fiberon PET-GF15, black — slot `Polymaker PET-GF @BBL H2C`
- **Nozzle temp:** 280 °C (initial layer 265 °C)
- **Bed:** Textured PEI Plate at 80 °C
- **Chamber:** unheated (`chamber_temperatures: 0`)
- **Flow ratio:** 0.9555
- **Max volumetric speed:** 18 mm³/s
- **Part-cooling fan:** ordinary min/max 0%; bridges and overhangs 70% at the
  50% unsupported-width threshold. Fan off for the first three bed layers;
  auxiliary cooling off, fan-always-on off and fan pre-start 0 s.
- **Retraction:** nil
- **Drying:** 100 °C × 10 h in the SUNLU E2, only if the spool has taken on
  moisture; a 3 kg spool feeds the print from a PolyDryer Box XL
  ([tools.md](/hardware/ledger/tools.md) "What dries where")

The casing is smooth. Physical surface finish is assessed on the printed shell.

## Geometry receipt

The [casing integration receipt](../casing-integration-review.json) records
native solid validity, reservoir cavity preservation, fixed fit datums,
floor sections, cap seats and the foil allowance for these inputs. It is a
one-off record, not a recurring build or commit check.

## Reference

- [`/hardware/printed-parts/faucet/faucet-shell/faucet_shell.py`](/hardware/printed-parts/faucet/faucet-shell/faucet_shell.py)
  — gold standard for the printed-enclosure pattern in this repo.

The cadquery venv lives at `tools/cad-venv/bin/python` (cadquery is not
on system Python).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/foam-shell/foam_shell.py`
- `/hardware/printed-parts/cold-core/reservoir/reservoir.py`

Printed mating gaps and support allowances are listed in [Cold-core printed fits](../fit-clearances.md).
