# Internal Plumbing

The selected warm-side fluid geometry is the
[production above-core arrangement](/hardware/manifold-layout/above-core.md).
Its native component frames, trimmed fittings and physical tube paths are in
[above-core.json](/hardware/manifold-layout/above-core.json),
[above_core_parts.py](/hardware/manifold-layout/above_core_parts.py) and
[above_core_routes.py](/hardware/manifold-layout/above_core_routes.py).
The [fluid topology](/hardware/topology/fluid-topology.md) defines the valve
functions and logical connections. A logical connection can contain several
short tubes and directly inserted stem fittings.

Assemble the fixed front manifold while front-top is loose. Fit below-lid core
plumbing before the PCB, then the pump, V-B and other core equipment.
Prepare V-A, V-K, their fitted plumbing, the complete inlet header, ASSE and
gas group on back-top. Complete the remaining connections between
quadrants through the two roof apertures after the enclosure ride. Install the
funnel frame and empty electronics panel after final tubing and wiring work.
See [mechanical assembly](enclosure-mechanical.md) for the closing sequence.

## Parts and cut lengths

| Group | Selected parts |
|---|---|
| Water protection | Bare Multiplex 19-0897 ASSE 1022, straight printed TPU inlet/outlet cuffs, printed vent adapter |
| Water split and flavor-water control | Trimmed NeoFit ATBU444-E stem tee, YZMSZ fixed 0.3 MPa native 1/4-inch push-connect regulator, V-A |
| Carbonator fill | V-K, G Ganen pump, two printed TPU pump elbows and four trial clamps, single neoFit ACHV44-E 1/4-inch water check |
| Gas feed | PISCO RVFUP1/4-1/4-0.3 regulator, separate neoFit ACHV44-E 1/4-inch check, five trimmed NeoFit stem elbows |
| Core/reservoir interfaces | Existing carbonator fittings; two below-lid B-fill fittings; selected passive cap guides |
| Soda and flavor outputs | DIGITEN meter, rear soda bulkhead, two 4 mm dispense reducers and rear flavor bulkheads |

Use white 1/4-inch LLDPE for water, blue for carbonated water, black for the
1/4-inch flavor/funnel circuit, red for gas, black 4 mm for flavor dispense and
white 4 mm for the ASSE vent. Four-millimetre paths retain R25; selected
1/4-inch continuations use R14 or larger. Native Bezier paths report their own
curvature. These are layout bend constraints, with each part's evidence scope
retained in its reference.

Square-cut tube blanks and mark the actual seated insertion at each fitting.
A displayed path or known exposed link is not a stock blank until both socket
engagements are established. Stem trim lengths belong to their receiving
socket families; keep the original sealing surface undamaged and verify the
actual seated engagement before use. The JG union-elbow scan does not establish
its hidden insertion stop.

The carbonator's water-in adapter and the check's downward outlet elbow share
one continuous white 1/4-inch tube. Combine the internal `water-in` CAD span
and warm `water-5` span, using the actual receiving-end insertion marks in
place of their nominal allowances. The plain lid guide adds no insertion,
fitting or physical cut. The reported warm span is part of this single tube,
as with the continuous soda riser through its own plain guide.

The V-A turn and feed travel with back-top on their connected tubing. The
V-B return bearing belongs to the core lid. Thread its retaining tie before
seating the fitting. Keep the tie on the fixed body band and leave both
release collets free.

## Procedure

### 1. Folded gas group

The upper-right rear bulkhead feeds the PISCO regulator through a stem elbow
and red tube. The regulator and separate neoFit ACHV44-E check stand on the
east-wall saddles at X78.2. Five trimmed stem elbows retain their full receiving
depths and 0.4 mm nominal exposed shaft at each shoulder. Exact R14 S bends
join the fixed rear bulkhead and the fixed X77.5/Y368.7622 cap guide to this
folded group. The below-lid route continues to the carbonator's existing gas
fitting and support-ring lane. That check-to-carbonator leg is one uncut tube
through the plain gas guide; combine both CAD spans when marking its two
receiving ends.

Thread ties through the two fixed east-wall support windows before seating the
bodies. Retain their fixed barrels without loading a stem elbow or moving
release collet. Follow the actual flow arrows. The PISCO reference permits
reverse free flow, so the separate downstream check belongs to this path.
Its published air specification does not establish exact CO2 service; retain
the component compatibility and reverse-sealing qualification limits.
The ACHV body scale and 16.891 mm receiving depth are explicitly inferred
from vendor media and neoFit sibling drawings. Verify actual arrow direction
and seating before use; the CAD reference establishes no sealing performance.

### 2. Water group

The upper-left rear water fitting feeds the ASSE's straight inlet cuff. The bare
body lies fore–aft above the pump, with its atmospheric vent west. Its outlet
cuff receives the trimmed stem tee. One branch feeds the transverse YZMSZ
regulator and V-A; the other feeds V-K beside the east wall, the pump inlet elbow,
the pump, the discharge elbow and the neoFit ACHV44-E check.

V-A and V-K mount in back-top's integral socket seats. Clock their underside
flow arrows downward: the header feeds their upper inlet ports, and their
lower outlets feed Y-A and the pump respectively. Their terminal blades point
downward. Seat the bare valves on the open back-top bench, then attach their
prepared blade leads before fitting the surrounding plumbing. Dress the free
PCB ends for final connection through the open roof. Physical terminal-housing
fit and seating force remain unqualified.

Thread the two ASSE ties and two regulator ties through their back-top support
windows before seating the bodies. Fit V-A's and V-K's inlet/outlet elbows,
the split tee, regulator and all three short header links on that same
subassembly. The two outer links have no exposed tube between their opposed
collets. Clock V-A's upper inlet release ear clear of the elbow body; the
nominal model uses a 15° turn. Keep release collets free to operate and tighten
ties on the fixed body bands. The complete water header travels with back-top;
the pump inlet is its connection to the core, and the low V-A feed connects
to front-top's Y-A. Keep those handoffs accessible through the uncovered roof.

Fit the pump's [TPU elbows](/hardware/printed-parts/diaphragm-pump-sleeve/README.md)
to the measured barb datums. Inspect both passages for strands first. Each barb
and tube socket takes its own trial clamp, four per pump. Seat the barb to its
shelf and the tube to its actual marked engagement, with the clamp band flush
at the mouth. Preserve the existing fit/pressure-trial scope; a modeled cuff
is not a qualified pressure joint.

The check lies fore–aft west of the pump in its lid saddle, arrow away from the
pump. Its outlet stem elbow faces downward into the passive aft water-in guide.
The same uncut tube continues through that plain guide to the carbonator's
existing water-in adapter. Assemble the internal route before closing the core;
the lid carries no water joint.
Fasten the pump before seating this removable check group. Its printed bearing
clears the driver, but the check body occupies that screw's tool column;
release and disconnect the check group for pump-screw service.

The reported internal water path is 229.656 mm and its warm span is 24.610 mm,
a combined 254.266 mm of CAD centreline. The warm span includes the NeoFit
ATEU44 outlet elbow's published 16.891 mm female receiving dimension
(B = 0.665 inch) and 7.719 mm exposed above the guide; verify actual seating.
The internal reference retains an 18.5 mm adapter standoff; that standoff does
not measure the actual PP010822E socket insertion. Between the modeled release
faces the path is 218.875 mm: 211.156 mm inside plus 7.719 mm above the guide.
The single physical blank follows that exposed path plus actual receiving
depths at both ends, adjusted to the fitted geometry and seated marks.

The west-facing ASSE adapter feeds the dedicated white 4 mm vent line to the
middle-left rear bulkhead and the faucet's separate outlet over the bowl.
Keep that complete atmospheric path open. Vent fitting retention and actual
made-up performance follow the
[adapter record](/hardware/printed-parts/asse-drain-adapter/README.md).

### 3. Flavor manifold: V-A through V-J + Y-A, Y-B, Y-C, Y-D, Y-F, Y-G + pumps

Build to [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) segment-for-segment. The truth table there names every valve, every Y-junction, and every tube segment by number; this step describes the build cadence around that truth table, not its content.

**This step begins on the bench with `enclosure-front-top` open and both valve rows absent.**
Front-top carries the two valve trays and the tee wall: the collet plate and, behind each of
the plate's four holes, a collar-clear bore through the rest of the wall. One purchased PP0208E pump tee stands on each pump port, Y-C and Y-D on
pump A and Y-F and Y-G on pump B, its branch facing the pump on the tube row and its run
upright. Its branch stands in its bore, which holds the tee in X and Z, and the collet
plate holds its branch collet pressed home its whole [1.5 mm](DOCK_TEE_STROKE) stroke, so the
collet never grips. The four cartridge tube tips pass the plate's holes into the tees' branch
collets and seal on their O-rings. The
[pump dock](/hardware/printed-parts/enclosure/pump-dock/README.md) describes the dock; the
[pump service procedure](/hardware/service/pump-replacement.md) describes the separating
joints and the complete prepared pumps supplied for a customer swap.

**V-A and V-K mount on back-top; V-B mounts in the cold-core lid's upright socket wall.** Their forward runs reach Y-A and Y-B beneath the open funnel aperture. Complete these connections before fitting the drop-in frame.

Lay out the ten Beduan valves and the [6](MANIFOLD_TEES) PP0208E tees. Cut stationary links from the [current manifold geometry](/hardware/manifold-layout/README.md), including engagement at both actual fittings. Exposed path length is not a tube-blank cut length. Use black LLDPE except for `fluid-3`, which uses white. Square-cut, deburr without scoring the sealing surface, and tag each segment.

1. **Seat the rear valves.** Press V-C, V-D, V-G and V-J onto their tray posts with the
   topology's coil clocks. Each bottom collet opens down into front-top's port channel,
   which runs from the seam up into its tray and keeps room for the collet and its stem elbow.

2. **Fit each tee with its upper tube and fore valve.** The upper tubes are `fluid-10`
   (Y-C to V-E), `fluid-13` (Y-D to V-F), `fluid-20` (Y-F to V-H) and `fluid-23` (Y-G to
   V-I). Each nominal blank is [38.901 mm](DOCK_UPPER_TAIL): [15.251 mm](DOCK_FORE_LINK)
   exposed, [11.65 mm](DOCK_TEE_INSERTION) bottomed in the tee's extended upper collet and
   an estimated [12 mm](DOCK_VALVE_INSERTION) in the valve. Seat uncut tube fully in the
   actual fore valve's bottom collet, mark the tube at the collet face, and cut it the
   exposed length plus the tee's insertion beyond that mark. Push the tube fully into the
   tee's upper collet and the fore valve's bottom collet. Bring the tee, tube and valve in
   together, the branch into its bore from the tee wall's aft face until the collet bottoms
   against the collet plate, and press the fore valve onto its tray posts. The fore valve's
   axis stands over the tee's run axis, so the upper tube stands straight.

3. **Cut the stem elbows.** Each lower return takes two NeoFit ATEU44W stem elbows. Cut each
   tee elbow's stem square [11.65 mm](DOCK_TEE_ELBOW_STEM) past its shoulder, the run
   collet's seat, and each valve elbow's [15.75 mm](DOCK_VALVE_ELBOW_STEM) past its shoulder:
   an estimated [12 mm](DOCK_VALVE_INSERTION) seat in the valve and the
   [3.75 mm](DOCK_VALVE_ELBOW_SHOWING) of stem that stands below its collet. Take the valve's
   seat from the actual received valve's fully seated mark. Chamfer each cut edge so it
   passes the O-ring without scoring it.

4. **Fit the lower returns.** From front-top's underside, push each tee elbow up into its
   tee's lower collet until its shoulder stands on the collet face, and each valve elbow up
   into its rear valve's bottom collet until its stem bottoms. Turn each pair's sockets to
   face each other. `fluid-9` runs from Y-C to V-C and `fluid-19` from Y-F to V-D; `fluid-17`
   from Y-D to V-G and `fluid-27` from Y-G to V-J lean inboard to their valves. Each is one
   straight tube of black LLDPE, cut to [53.88 mm](DOCK_RETURN_INNER) for the inner two and
   [54.47 mm](DOCK_RETURN_OUTER) for the outer two: the straight between the two sockets and
   [16.89 mm](DOCK_ELBOW_SOCKET) into each. Push it fully into both sockets. Use actual
   insertion marks and tug-check every push-fit joint. Complete this work while front-top is
   loose, before it closes over the condenser/compressor half.

5. **Prepare the pumps.** Pull Kamoer's barbed connectors out of both pumps' tube ends.
   Cut four [33.2 mm](DOCK_PUMP_TUBE_CUT) tubes of black 1/4" LLDPE, square and burr-free
   with eased outer edges, and push one into each BPT end under the loosened pump-head
   housing. Lower both complete pumps into their fitted wells with the tubes facing +Y
   through the cradle's open tube passages. The customer's replacement pumps receive this
   same [factory preparation](/hardware/service/pump-replacement.md#factory-preparation-of-replacement-pumps).

6. **Fit the electrical contact and cap, then set the tube tips.** Install the cap's two M1.4 inserts with
   their tops [5.125 mm](POGO_INSERT_HOST_DEPTH) inside its aft printed face, [2 mm](POGO_INSERT_SETBACK) behind the recessed ear-bearing datum, using
   the recessed-seat procedure in
   [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §1. Solder four
   ~100 mm 22 AWG leads to the female contact half and mount it in the cap with its marked
   end at −X. Seat the two M1.4 × 8 screws with the hand-operated 1.3 mm hex driver,
   stopping with the ears flat. Lower the broad cap over both pump bosses and draw its
   [2](CAP_SCREWS) M3×[60](CAP_SCREW_LEN) screws evenly into the cradle's center inserts.
   Verify firm pump retention without vertical play within the
   [accepted holder scope](/hardware/reference/kamoer-kphm400/physical-fit.json).
   Route the +X groove pair to pump A and the −X pair to pump B; the four leads are
   `AM2`, `AM1`, `BM2`, `BM1` from +X to −X. Crimp their female Faston receptacles and
   connect them to the marked motor tabs. Keep all leads below the crown. With the cap
   closed, set the printed tube setting jig on the cartridge's flat rear face and slide each
   tube until its tip meets its jig stop at the seated datum, where it bottoms in its tee.
   Tighten each housing so it clamps the BPT tube around its LLDPE tube. Keep the exposed
   tubes straight and verify all four tip positions, a firm hand pull on each tube and
   pump-end sealing.

7. **Connect the cartridge after chassis assembly.** Both parts arrive with their
   SB443-IN blocks loaded at their print pauses: two in each of the two slots in front-top's
   tee wall behind the bay face, and two in each of the two slots in the cartridge's flat
   back. Inspect the columns' exposed attracting faces. With power disconnected, slide the
   cartridge on its floor and present all four tube tips squarely to the collet plate's
   holes. Push evenly: the tips pass the tees' pressed branch collets and bottom, and the
   magnets draw the cartridge onto its seat with the front face flush.
   Confirm that every tube enters straight and the pogo pair reaches its designed
   compression. The meeting magnet poles establish closure, with
   [0.25 mm](DOCK_BODY_GAP) of air between the broad aft planes. Withdraw and reinsert
   straight to confirm that the four tubes draw out together and the tees and tubing stay in
   the machine. Magnetic attraction alone does not establish sealing.

Y-A and Y-B remain on the inner limbs with their branches facing one another across the
mirror plane. V-A's inlet takes the water split through the flow regulator. V-B's inlet
takes `fluid-4` from the PP0308E elbow carried by the removable funnel frame. No reservoir has a
tee: V-F/V-E reach reservoir A's fill/draw conduits and V-I/V-H reach reservoir B's.

Route and retain fixed spans while the front-top is accessible. The four reservoir lines
land on the cold core's own cap conduits: `fluid-14` to `reservoir-a-fill`, `fluid-24` to
`reservoir-b-fill`, and `fluid-16`/`fluid-26` from the draw conduits into V-E/V-H. Each draw
line is its reservoir's dip tube: cut it long enough to reach the reservoir's floor, cut that
end at 45°, straighten it by hand, and feed it down its draw conduit and the cap's draw bore
until the tip touches the floor
([floor and dip tube](/hardware/printed-parts/cold-core/reservoir/floor-and-dip-tube.md)).
Reservoir B fill turns through two actual compact fittings below the lid and emerges aft of the PCB. Its lower stem enters the reservoir cap's existing fill bore; the short link between fittings has known exposed length, while the JG socket insertion remains unmeasured. A-fill and B-draw use shallow guide offsets. Dress and tag the front-top ends on the bench, and connect the remaining ends through the open roof before fitting the closures. Keep access to the lower returns' elbows and their collets.

The carbonated-water riser leaves `carb-water-out` directly for the rear middle-right rear
bulkhead through the DIGITEN meter. Flavor A leaves V-G on `fluid-18`; flavor B leaves
V-J on `fluid-28`. Complete these routes in §4.

### 4. Rear beverage connections

The soda outlet is the middle-right rear fitting. One continuous blue tube
runs from the carbonator through the plain core guide at world
(50, 342.4148, 253.4) mm and the accepted R14 printed bend holder directly
into the DIGITEN inlet. The holder has a 2 mm wall, 3 mm legs and a 6.8 mm
channel. The guide adds no joint, insertion or physical cut. The meter sits
in its two cold-core lid collar bearings, with its lead root down and label
east. Its outlet collet meets the rear return fitting's collet; the short
tube occupies both sockets with no exposed span.

The drawn continuous tube is 461.382 mm: 380.715 mm from the metal elbow
mouth to the plain guide, plus 80.667 mm above it. This includes the nominal
18.5 mm PP010822E adapter standoff and the meter's estimated 15.7 mm receiving
depth. Prepare one physical tube using the actual receiving marks at those
two fittings; the guide adds no length allowance or cut.

Tighten all four pump screws before threading this inlet: the installed tube
crosses one vertical pump-driver approach. Disconnect and remove the inlet
for that screw's service. Thread the continuous tube through the holder.
Square-cut one 63 mm piece
of the owned CARGEN ID6.35/OD25.4 mm foam and slide it over the tube and holder
before connecting the meter. Keep the square ends; no axial slit or shaped
trimming is specified. The nominal foam centreline is 62.867 mm. The foam
compresses around the holder and locally beside V-K, the pump, its inlet TPU
elbow and barb band. The occupied CAD display estimates that compression;
it is not a measured strain, physical air-gap or thermal result. The external
umbilical retains its five 1-ft foam segments. Meter-body insulation remains
deferred.

Prepare the rear soda connection with back-top on the open bench:

1. Install the soda and adjacent vent/drain bulkheads with their nuts through
   the rear wall. Keep the white 4 mm drain-vent line disconnected for final
   dressing through the open roof.
2. Connect both nested soda stem elbows on back-top and secure the bulkhead
   nuts while access is open. Prepare the nominal 32.591 mm concealed blue
   tube on the core: seat 15.7 mm in the meter and leave the other 16.891 mm
   for the return elbow. Replace nominal depths with actual receiving marks.
3. Close the back column with its rear fittings. Guide the return elbow onto
   the free tube carried by the meter, over its nominal 16.891 mm engagement.
   Keep the meter, both collars and rear fittings on their common axis.
   The complete inlet header remains on its back-top mounts throughout this
   motion, as described in §2.
4. With the quadrants seated, inspect the engagements through the open roof
   and connect the white drain-vent line, keeping its atmospheric path open.
   Dress the remaining inter-quadrant leads before installing either closure.

The [rear assembly record](/hardware/mechanical-qualification/enclosure-above-core/rear-plumbing-assembly.json)
records each tested rear group's staging and finite socket scope. It retains the explicit 0.22493 mm³ nominal soda fitting
contact. Collet fit, connection force, threading and hand/tool access remain
unqualified. The meter installs on the open core before closure; a straight
late lift meets the fixed ASSE saddle and a fore insertion crosses its
collar bearing.

Flavor A and B use black 4 mm lines from the reducers at V-G and V-J to the
lower-left and lower-right rear fittings respectively. Retain R25 turns and
straight socket entries. Dress valve leads clear of those lines and leave
collets accessible.

### 5. Final connections and roof closures

Make the V-A low feed and V-B high feed/return with the funnel frame absent.
The single Y-A stem points aft and slightly east. The raised B connections
clear that first elbow. The drain cradle snaps into the removable frame’s 3 mm
web and carries the elbow and stub. Complete the drain connection before fitting
the silicone funnel. Disconnect the drain tube or release the cradle snap before
withdrawing the frame.

Confirm every push-fit witness, trim engagement, clamp and tie on the made-up
hardware. Keep wiring clear of wet joints and preserve access to moving
collets. Fit the drop-in frame and empty electronics panel after the final
connections. Physical leak, pressure, venting and cleaning qualifications are
separate from native geometry and precede fluid commissioning.

## Qualification scope

The [mechanical qualification index](/hardware/mechanical-qualification/README.md)
preserves accepted results at their named parts and artifacts. The pump dock's
accepted dry connection cycle does not establish wet sealing, pressure
retention, insertion endurance or food-contact suitability. The pump/ASSE TPU
interfaces, shortened fitting stems and selected gas hardware retain their
part-specific open qualification items. No unit is declared primed-ready or
safe to energize solely because the CAD paths connect.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_internal_plumbing_sync.py`
