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

Load and snap-retain the pumps from below, then assemble the fixed front manifold while
front-top is loose. Fit below-lid core
plumbing before the PCB, then the pump, V-B and other core equipment.
Prepare V-A, V-K, their fitted plumbing, the complete inlet header, ASSE and
gas group on back-top, together with the sidewall PSU, relays, meter and its
external inlet/insulation. Complete rear connections on the open subassembly.
The electronics ceiling is continuous. Complete the accessible central
inter-quadrant connections before installing the funnel frame.
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
engagements are established. Trim each stem to its host's marked tube stop:
mark the stop on the actual received fitting, then cut the stem to that depth
plus any specified showing length. Y-A and Y-B take their stems to the
PP0208E's measured 10.0 mm stop ([tee connector](/hardware/reference/tee-connector/README.md)).
Keep the original sealing surface undamaged and verify the actual seated
engagement before use. The JG union-elbow scan does not establish
its hidden insertion stop.

The carbonator's water-in adapter and the check's upward outlet elbow share
one continuous white 1/4-inch tube. Combine the internal `water-in` CAD span
and warm `water-5` span, using the actual receiving-end insertion marks in
place of their nominal allowances. The plain lid guide adds no insertion,
fitting or physical cut. The reported warm span is part of this single tube,
as with the continuous soda riser through its own plain guide.

The V-A turn and feed belong to back-top, with their final connection at
front-top's Y-A. Fit their bare low tube under the pump after the column is
home, then add the east-turn union and forward feed
([assembly staging](/hardware/mechanical-qualification/enclosure-above-core/sliding-assembly-staging.json)). The
V-B return bearing belongs to the core lid. Thread its retaining tie before
seating the fitting. Keep the tie on the fixed body band and leave both
release collets free.

The funnel drain's NeoFit outlet stem is 16.7 mm long past its shoulder:
15.7 mm nominal seated depth plus 1 mm showing above the union's collet.
Use the received union's actual insertion mark when cutting it. Its collar
has 1 mm air to the cradle's lower aft face. Connect its R14.07 S-offset to
V-B's inlet with both receiving ends fully seated. The V-B return elbow's
forward leg sits in the lid's filled pedestal; thread its tie through the
peaked passage before seating the elbow, then close the tie on the fixed
body band.

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

For the enclosure slide, fit the last elbow (`gas-upper-b`) to that core
tube and leave its male stem separate from `gas-upper-a` on back-top.
Keep the tube and loose elbow clear while V-K passes. Present the elbow
for the final approximately 20 mm, guiding its aft-pointing stem into the
fore-facing socket as the column seats. The existing stem joint follows Y;
its nominal engagement is 16.891 mm. Use the actual receiving mark and keep
the joint aligned by hand, without using the enclosure screws to seat it.

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
prepared blade leads before fitting the surrounding plumbing. Dress their free
ends forward to the funnel opening for the final connection
([wiring](wiring.md#4-cabinet-side-12-v-runs-dc-3-dc-5-through-dc-9)). Physical terminal-housing
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
at the mouth. Turn each clamp's screw housing away from the water check and
the lid; the model does not draw the housings. Preserve the existing fit/pressure-trial scope; a modeled cuff
is not a qualified pressure joint.

The check lies fore–aft west of the pump in its lid saddle, arrow away from the
pump. Its outlet stem elbow faces upward. One continuous white tube arches
above the lid at R18, enters the straight guide at world (−53, 288.7265) mm,
and continues to the carbonator's existing water-in adapter. Its lower turn
is laid in the open main body before potting; the cap contains only a straight
passage and the lid carries no water joint.

Make up the check group on the open core, with the check's six-inch narrow tie
already threaded through its east-quarter pedestal ([cold core](cold-core.md) §3):

1. Fasten the pump while all four driver approaches are open.
2. Seat the discharge TPU elbow on the pump's outlet barb (11 mm), and seat
   the 31.9 mm link in its tube socket (15 mm).
3. Seat the check's inlet on the link (16.9 mm). Seat the outlet stem elbow
   to its 0.4 mm showing mark with its tube socket facing upward.
4. Lower the fixed check barrel into its open quarter bearing. Feed the
   continuous inlet through its plain guide and form the exposed R18 arch
   into the upward-facing outlet socket, using the actual insertion mark.
5. Close both TPU clamp bands and the check tie, verify the insertion marks,
   then dress the flexible leads clear of the arch.

The metal-adapter mouth to guide path is 87.551 mm. The warm path is
208.817 mm including the NeoFit ATEU44 elbow's published 16.891 mm receiving
allowance (B = 0.665 inch); 191.926 mm is exposed above the guide. The modeled
exposed path between the two release faces is therefore 279.477 mm. Prepare
one blank with the actual receiving depths at both ends, adjusted to the
fitted geometry and seated marks. The plain guide adds no cut or insertion.

The west-facing ASSE adapter feeds the dedicated white 4 mm vent line to the
middle-left rear bulkhead and the faucet's separate outlet over the bowl.
Keep that complete atmospheric path open. Vent fitting retention and actual
made-up performance follow the
[adapter record](/hardware/printed-parts/asse-drain-adapter/README.md).

### 3. Flavor manifold: V-A through V-J + Y-A, Y-B, Y-C, Y-D, Y-F, Y-G + pumps

Build to [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) segment-for-segment. The truth table there names every valve, every Y-junction, and every tube segment by number; this step describes the build cadence around that truth table, not its content.

**This step begins on the bench with `enclosure-front-top` loose and both valve rows,
pump tees, display and funnel frame absent.** Its upper fitted pump inverses are integral
with the broad stock continuing into the display housing and roof. The broad
`enclosure-pump-retainer` holds the fitted lower wells. Its two integral, full-depth snap
wings engage front-top’s flank receivers and retain the molded-skirt capture between
the two fitted halves.

Front-top also carries the valve trays and tee wall. Four bottom-open tube-loading gates
lead into its collet openings and branch bores. The prepared pump tubes rise through these
gates while the tees are absent. After the retainer is secured, each purchased PP0208E
tee approaches from aft and pushes onto its fixed pump tube, with its branch in the wall
bore and its run upright. Y-C and Y-D serve pump A; Y-F and Y-G serve pump B. The extended
branch collet grips the tube and its O-ring seals it. The [pump mount and tee wall](/hardware/printed-parts/enclosure/pump-dock/README.md)
describe the fitted mounting surfaces and assembly clearances.

**V-A and V-K mount on back-top; V-B mounts in the cold-core lid's upright socket wall.** Their forward runs reach Y-A and Y-B beneath the open funnel aperture. Complete these connections before fitting the drop-in frame.

While front-top is open, land the J1 and J2 trunks on the front coils V-C through V-J and their `COM` feeds in the 221-420 and 221-415 ([wiring](wiring.md#4-cabinet-side-12-v-runs-dc-3-dc-5-through-dc-9)).

Lay out the ten Beduan valves and the [6](MANIFOLD_TEES) PP0208E tees. Cut stationary links from the [current manifold geometry](/hardware/manifold-layout/README.md), including engagement at both actual fittings. Exposed path length is not a tube-blank cut length. Use black LLDPE except for `fluid-3`, which uses white. Square-cut, deburr without scoring the sealing surface, and tag each segment.

1. **Prepare the pumps and set the tubes in the loose retainer.** Pull Kamoer's barbed
   connectors out of both pumps' tube ends. Cut four [33.2 mm](DOCK_PUMP_TUBE_CUT) tubes of
   black 1/4" LLDPE, square and burr-free with eased outer edges, and push one into each
   BPT end under the loosened pump-head housing. Seat both pumps in the loose retainer's
   fitted wells with the tubes facing +Y. Set the tube setting jig on its flat rear face
   and slide each tube until its tip meets the jig's stop at the seated tee datum. Tighten
   each pump-head housing to clamp the BPT tube around its LLDPE stub. Keep the stubs
   straight; check their four tip positions, firm hand retention and pump-end sealing.
   Take the jig off before approaching front-top: its broad body occupies the tee wall's
   space and cannot be fitted after the pumps are installed.

2. **Land the pump leads with the motors accessible.** With power disconnected, feed
   the bare pump end of [DC-5](harnesses/j13.md) forward through the shared rear wire mouth
   and out of front-top's open underside. Crimp its four Faston receptacles, ring out the
   [J13 map](harnesses/j13.md#end-to-end-conductor-map), then land the +X pair on pump A
   and the −X pair on pump B. Keep the board end free and support its slack.

3. **Load and secure the pumps from underneath.** Raise the prepared pumps and retainer
   motor-first into front-top's fitted upper half. Guide each straight stub up its own
   bottom-open tee-wall gate while drawing the lead slack aft through the common wire
   passage. The lower fitted lands support the molded skirts and the integral upper
   faces capture them from above. Press the retainer upward so both upper-rooted wings
   flex inward, then spring outward with their lower hooks seated on the receiver floors.
   Inspect both engagements and confirm the pumps are seated against their fitted lands. The [accepted holder record](/hardware/reference/kamoer-kphm400/physical-fit.json)
   applies to its identified cradle and cap; physical fit and retention of this two-face
   skirt capture remain unqualified. Complete both snap engagements while front-top is loose.

4. **Fit all four tees with their upper tubes and fore valves.** Keep the rear valve row
   absent for this straight approach from aft. The upper tubes are `fluid-10`
   (Y-C to V-E), `fluid-13` (Y-D to V-F), `fluid-20` (Y-F to V-H) and `fluid-23` (Y-G to
   V-I). Each nominal blank is [38.901 mm](DOCK_UPPER_TAIL): [15.251 mm](DOCK_FORE_LINK)
   exposed, [11.65 mm](DOCK_TEE_INSERTION) bottomed in the tee's extended upper collet and
   an estimated [12 mm](DOCK_VALVE_INSERTION) in the valve. Seat uncut tube fully in the
   actual fore valve's bottom collet, mark the tube at the collet face, and cut it the
   exposed length plus the tee's insertion beyond that mark. Push the tube fully into the
   tee's upper collet and the fore valve's bottom collet. Bring the tee, tube and valve in
   together from aft, keeping the tee branch coaxial with its fixed pump tube. Push the
   branch onto the tube and into its bore with its collet in the opening ahead of the bore,
   and press the fore valve onto its tray posts. Verify the pump tube reaches its seated
   mark at the extended branch collet; the pump mount stays fixed while the tee moves.
   The fore valve's
   axis stands over the tee's run axis, so the upper tube stands straight.

5. **Seat the rear valves.** After all four fore groups are seated, press V-C, V-D, V-G
   and V-J onto their tray posts with the topology's coil clocks. Each bottom collet
   opens down into front-top's port channel, which runs from the seam up into its tray
   and keeps room for the collet and its stem elbow.

6. **Cut the stem elbows.** Each lower return takes two NeoFit ATEU44W stem elbows. Cut each
   tee elbow's stem square [11.65 mm](DOCK_TEE_ELBOW_STEM) past its shoulder, the run
   collet's seat, and each valve elbow's [15.75 mm](DOCK_VALVE_ELBOW_STEM) past its shoulder:
   an estimated [12 mm](DOCK_VALVE_INSERTION) seat in the valve and the
   [3.75 mm](DOCK_VALVE_ELBOW_SHOWING) of stem that stands below its collet. Take the valve's
   seat from the actual received valve's fully seated mark. Chamfer each cut edge so it
   passes the O-ring without scoring it.

7. **Fit the lower returns.** From front-top's underside, push each tee elbow up into its
   tee's lower collet until its shoulder stands on the collet face, and each valve elbow up
   into its rear valve's bottom collet until its stem bottoms. Turn each pair's sockets to
   face each other. `fluid-9` runs from Y-C to V-C and `fluid-19` from Y-F to V-D; `fluid-17`
   from Y-D to V-G and `fluid-27` from Y-G to V-J lean inboard to their valves. Each is one
   straight tube of black LLDPE, cut to [53.88 mm](DOCK_RETURN_INNER) for the inner two and
   [54.47 mm](DOCK_RETURN_OUTER) for the outer two: the straight between the two sockets and
   [16.89 mm](DOCK_ELBOW_SOCKET) into each. Push it fully into both sockets. Use actual
   insertion marks and tug-check every push-fit joint. Complete this work while front-top is
   loose, before it closes over the condenser/compressor half.

8. **Complete the front-top subassembly.** Finish the remaining front manifold links
   and valve wiring while the interior and underside are accessible. Thread SIG-7's
   free display end through the same rear wire passage and leave it accessible at the
   open facet. Join the populated front-top to the lower enclosure. Pumps, retainer and
   plumbing travel with front-top during its aft slide. Fit and wire the display, gasket
   and cover per [mechanical assembly §8](enclosure-mechanical.md#8-let-the-display-into-the-facet-and-clear-the-funnel-opening).
   Dress DC-5 and SIG-7 clear of the rails, tubing and funnel-frame seats; complete the
   central connections and plug the XHP-4 into J13 through the open funnel aperture before
   fitting the frame. Disconnect J13 by its housing before separating enclosure pieces.

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

Reservoir A’s two continuous tubes use two integral fore C2 clips on one broad base
and one aft tied seat. Draw is west of fill: their centreline X stations are
50.5/64.0 mm at the fore clips, Y209.75 and Z258.5 mm, and 86.5/94 mm at the aft
seat, Y304 and Z259.5 mm. Press each tube down through its clip's open +Z mouth.
For removal, release the exposed jaws and lift the tube upward.
At the aft seat, Y304 mm, thread one four-inch narrow tie through the empty transverse
slot before laying in the pair; retain both tubes there with that shared tie on the
open core.
Leave the front valve ends free during the column slide and dress the
flexible spans clear of passing fittings. Once the column is home, finish
dressing the free spans and connect the front ends. Keep each tube
unbroken through its plain core guide. Only the connection points and
paired-anchor centres/axes are fixed; the bends and displayed lengths between
them illustrate routing and may change to clear installed hardware and
wires. The current drawn warm spans are
[452.830 mm](RESERVOIR_A_FILL_WARM) for `fluid-14` fill and
[394.059 mm](RESERVOIR_A_DRAW_WARM) for `fluid-16` draw. Each includes the
16.891 mm receiving length in its front-valve ATEU44W stem elbow. For the physical blank,
continue through the guide to the reservoir fill bore or dip-tube tip and
replace the socket allowance with its actual fully seated insertion mark.
The guide adds no fitting, insertion or cut. Tighten the pump screws before
threading the draw tube; remove that tube for the affected screw's service.
The aft nominal closed tie path is
47.182 mm before head engagement and tail; threading and retention remain
unqualified. Fore snap insertion force, fit and retention have no physical acceptance. The [route record](/hardware/mechanical-qualification/enclosure-above-core/reservoir-a-route-review.json)
preserves the selected line/arc definitions and contact scope.

V-F's outlet, V-E's inlet and V-I's outlet each receive one ATEU44W stem
elbow on front-top. Cut each male stem to its valve's marked tube stop
(12.7 mm nominal in CAD), seat it fully and point the tube socket aft. The
reservoir tubes leave these sockets below the funnel frame, then rise gently
to the Z295.5 free runs. The nominal tube/frame gap is 1.225 mm. Flavor A's
4 mm crossover runs at Y156/Z288.5; the J9 display ribbon's free bends pass
below it while the printed cable mouth and connector positions remain fixed.

Reservoir B fill turns through two actual compact fittings below the lid and emerges aft of the PCB at X−33/Y287.5. Its lower stem enters the reservoir cap's existing fill bore; the approximately 15.6 mm exposed link excludes the unmeasured JG socket insertion. Assemble the pair and link in the open cup before the top cap's pour ([cold core](cold-core.md) §3); the lid then closes over the lower 3.05 mm and upper 2.4 mm retaining covers. The upper cover has 0.25 mm nominal CAD air to the PCB tails; physical fit and retention load remain unqualified. A-fill and B-draw use shallow guide offsets. Dress and tag the front-top ends on the bench, and connect the remaining ends through the funnel opening before the frame goes in. Keep access to the lower returns' elbows and their collets.

The drawn `fluid-24` span is [225.698 mm](RESERVOIR_B_FILL_WARM), including
the 16.891 mm receiving length in V-I's stem elbow and ending at the upper JG socket
face. Add the actual JG receiving mark when preparing that physical tube;
the cap's separate short link is another piece. Terminate both J10 power
leads on the loose PCB before fastening the board to the core, then connect
their free ends to the core WAGOs. The captured B-fill fitting clears the
installed lead and vertical screw tools but overlaps the optional straight
wire-entry witness. Installed retermination and flexible service handling
remain unqualified. Disconnect/stage the flexible B-fill tube for the
recorded vertical J5/J6/J13 withdrawal approaches.

The carbonated-water riser leaves `carb-water-out` directly for the rear middle-right rear
bulkhead through the DIGITEN meter. Flavor A leaves V-G on `fluid-18`; flavor B leaves
V-J on `fluid-28`. Complete these routes in §4.

### 4. Rear beverage connections

The soda outlet is the middle-right rear fitting. One continuous blue tube
runs from the carbonator through the plain core guide at world
(50, 342.4148, 253.4) mm and the accepted R14 printed bend holder directly
into the DIGITEN inlet. The holder has a 2 mm wall, 3 mm legs and a 6.8 mm
channel. The guide adds no joint, insertion or physical cut. The meter sits
in its two back-top sidewall-rooted collar bearings, with its lead root down
and label east. Its outlet collet meets the rear return fitting's collet; the short
tube occupies both sockets with no exposed span.

The drawn continuous tube is 434.567 mm: 353.900 mm from the metal adapter
mouth to the plain guide, plus 80.667 mm above it. The upper span includes
the meter's estimated 15.7 mm receiving depth. Prepare one physical tube using the actual receiving marks at those
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
   tube between the meter and return elbow: 15.7 mm in the meter and
   16.891 mm in the return elbow. Replace nominal depths with actual receiving
   marks. Keep both collars and the rear fittings on their common axis.
3. Fit the continuous inlet, holder and foam to the meter on the open back-top
   subassembly. Its plain core guide introduces no physical cut or joint.
   The actual closing and flexible handoffs remain scoped by the manual
   assembly record; a drawn mounting parent does not establish rigid closing
   clearance.
4. Connect and dress the white drain-vent line with its atmospheric path open.
   Complete accessible central inter-quadrant leads before fitting the frame.

The [rear assembly record](/hardware/mechanical-qualification/enclosure-above-core/rear-plumbing-assembly.json)
retains the explicit 0.22493 mm³ nominal soda fitting contact and its finite
socket scope. Collet fit, connection force, threading and hand/tool access remain
unqualified. The meter and rear outlet are prepared together on back-top.
Closing and flexible handoffs are established only to the scope of that record.

Flavor A and B use black 4 mm lines from the reducers at V-G and V-J to the
lower-left and lower-right rear fittings respectively. Seat `fluid-18` and
`fluid-28` in their rear bulkheads on the open back-top and carry their free
ends ahead of back-top's open front through the ride. Once the box is closed,
connect them at the V-G and V-J reducers through the funnel opening. Retain
R25 turns and straight socket entries. Dress valve leads clear of those lines
and leave collets accessible.

### 5. Final connections through the funnel opening

Make the V-A low feed and V-B high feed/return with the funnel frame absent.
Seat J11 at the main board before the V-B return union and its flexible
return tube go in; the return lies over J11
([wiring](wiring.md)). The single Y-A stem points aft and slightly east. The
raised B connections clear that first elbow.

The drain joint is made as the frame goes in, after commissioning. The drain
cradle snaps into the removable frame’s 3 mm web and carries the PP0308E elbow
and stub. Push `fluid-4`, the straight 10.95 mm exposed tube, fully into V-B's
inlet turn, push the cradle's elbow onto its free end, then lower the
frame so its web snaps over the cradle's wings. Complete the drain connection
before fitting the silicone funnel. The plug, stub, elbow and cradle travel
with the frame; disconnect the V-B feed before withdrawing it.

Confirm every push-fit witness, trim engagement, clamp and tie on the made-up
hardware. Keep wiring clear of wet joints and preserve access to moving
collets. Fit the drop-in frame after the final
connections. Physical leak, pressure, venting and cleaning qualifications are
separate from native geometry and precede fluid commissioning.

## Qualification scope

The [mechanical qualification index](/hardware/mechanical-qualification/README.md)
preserves accepted results at their named parts and artifacts. The pump dock
has no physical seal, retention, lifetime or cleaning acceptance, and its
food-contact suitability is not established. The pump/ASSE TPU
interfaces, shortened fitting stems and selected gas hardware retain their
part-specific open qualification items. No unit is declared primed-ready or
safe to energize solely because the CAD paths connect.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_internal_plumbing_sync.py`

## Reservoir tube grips and passive air paths

Each reservoir lid has two flush TPU 90A liquid-tube spools and one smaller
air-tube spool in matching 45° countersinks. The dip tubes remain continuous
from the draw fittings to the floors. B-fill retains its captured trimmed
stem elbow; A-fill extends 1 mm through the flat lid into the headspace.

Cut two nominal 31.25 mm pieces of white 4 mm OD / 2.5 mm ID LLDPE. Feed each
through its dedicated foam-cap passage and air grip, leaving 6 mm above the
outer cap face. Its lower end stands 1 mm below the reservoir plate. Each air
path is open in both directions and independent of the other reservoir.
[Installation and dimensions](/hardware/printed-parts/cold-core/reservoir/vent.md).
