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
gas group on back-top, together with the ceiling PSU, west-wall relays, meter and its
external inlet/insulation. Complete rear connections on the open subassembly.
The electronics ceiling is continuous. Complete the accessible central
inter-quadrant connections before installing the funnel frame.
See [mechanical assembly](enclosure-mechanical.md) for the closing sequence.

## Parts and cut lengths

| Group | Selected parts |
|---|---|
| Water protection | Multiplex 19-0897 ASSE 1022, PP010822E inlet adapter, GAGIRA coupling, PI4512F6S outlet adapter, PP061208W reducer, printed vent cup |
| Water split and flavor-water control | John Guest PP0208E union tee, YZMSZ fixed 0.3 MPa native 1/4-inch push-connect regulator, V-A |
| Carbonator fill | V-K, G Ganen pump, two reinforced 3/8-inch PVC joints, trimmed PP061208W reducers, four YDS butterfly clamps and an ACVUS-44 stem check |
| Gas feed | PISCO RVFUP1/4-1/4-0.3 regulator, neoFit ACVUS-44 stem check directly in the outlet |
| Core/reservoir interfaces | Existing carbonator fittings; continuous B-fill tube through its fore-entry guide; selected passive cap guides |
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

### 1. Rear gas group

Fit the ACVUS-44 stem check directly into the PISCO regulator's outlet, following
both flow arrows. With back-top inverted, lower the pair into its seat 16 mm
forward and slide it aft. The regulator's inlet neck passes the CO2 hole;
its external release face is the rear tube station. Fit the lower snap cap
with its lip ahead of the outlet neck's shoulder.

Insert the continuous red tube into the check. It leaves forward in one bend,
then an S reaches the straight cap guide at X59.101/Y354.664/Z253.4. The same
tube continues to the carbonator's gas fitting through the retained lower
support-ring lane. The guide adds no tube cut or socket. Use the actual fully
seated marks at the check and carbonator fitting when cutting the blank.

### 2. Water group

TAP enters the PP010822E and GAGIRA threaded inlet chain. The ASSE lies
fore–aft with its vent downward. Its PI4512F6S and PP061208W outlet fittings
feed the JG PP0208E union tee through one gently raised stub. The tee's east
run feeds V-K's upper elbow; its west run feeds the YZMSZ regulator and V-A.
V-A hangs by its posts in the ceiling plinth. V-K uses the east-wall socket
plate with its inlet above its outlet.

1. Make up the ASSE threaded chain, keeping the two wrench flats aligned.
   Lower it into its swept hex seat 16 mm forward, slide it aft and fit the
   lower hex cap. The cap bears against the inlet coupling and passes the vent.
2. Seat the regulator upward and close its lower snap cap. Fit V-A and V-K,
   their stem elbows, the tee and the three short header links. Keep release
   collets accessible. Both opposed regulator links contain their receiving
   depths with no exposed tube.
3. Fit the pump's two [reinforced PVC joints](/hardware/reference/pump-barb-joint/README.md).
   Each has a PP061208W stem trimmed to 10 mm and a butterfly clamp on the barb
   and reducer stem. The suction tube bends in one arc to the concealed
   quarter-inch link and the nested elbow in V-K's lower port. Its stem-clamp
   key points forward; the barb-clamp key points aft.
4. The discharge joint bends down 15 degrees. Clock its stem clamp to the
   selected clear position, fit the trimmed stem elbow and insert the ACVUS-44
   check directly into that elbow. Follow the check's arrow away from the pump.
5. Fasten the pump while all four driver approaches are open. The continuous
   white inlet turns R14 from the check into the straight core guide at
   X−80.417/Y402.999/Z253.4, then reaches the carbonator's existing water
   fitting. The cap guide adds no joint or tube cut.
6. Fit the downward vent cup, its two ties and the direct white 4 mm return
   to OVER. Its [assembly record](asse-drain.md) defines the open faucet outlet.

Prepare push-fit ends to the actual receiving-stop marks. The native model
retains each purchased fitting's frame and nominal insertion allowance; buried
reference closures do not specify internal hydraulic geometry.

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
[450.797 mm](RESERVOIR_A_FILL_WARM) for `fluid-14` fill and
[392.027 mm](RESERVOIR_A_DRAW_WARM) for `fluid-16` draw. Each includes the
16.891 mm receiving length in its front-valve ATEU44W stem elbow. For the physical blank,
continue through the guide to the reservoir fill bore or dip-tube tip and
replace the socket allowance with its actual fully seated insertion mark.
The guide adds no fitting, insertion or cut. Tighten the pump screws before
threading the draw tube; remove that tube for the affected screw's service.
The aft nominal closed tie path is
47.182 mm before head engagement and tail; threading and retention remain
unqualified. Fore snap insertion force, fit and retention have no physical acceptance. The [route record](/hardware/mechanical-qualification/enclosure-above-core/reservoir-a-route-review.json)
preserves the selected line/arc definitions and contact scope.

V-F's outlet and V-E's inlet each receive one ATEU44W stem elbow on front-top. Cut each male stem to the valve's marked tube stop (12.7 mm nominal in CAD), seat it fully and point its tube socket aft. Their reservoir tubes rise gently to the Z295.5 free runs beneath the funnel frame, with 1.225 mm nominal tube/frame air. V-I's outlet takes the same trimmed stem elbow with its socket clocked 15° east of aft. Its B-fill tube descends toward the fore-facing cap entry. Flavor A's 4 mm crossover runs at Y156/Z288.5; the J9 display ribbon's free bends pass below it while the printed cable mouth and connector positions retain their datums.

Prepare B-fill as one continuous black 1/4-inch LLDPE tube from V-I to reservoir B's headspace. Seat three full-length RX-M3x5.7 inserts in the cup's clamp pilots, fit the lid and tighten its three recessed M3 × 10 clamps. Thread the tube through the fore-facing entry, around the guide and out the cup floor with the V-I end free, then install the PCB. Mask the dry passage joint and both mouths during the cap pour. The lower tube passes through the TPU fill grip at world X−43.5/Y233.3 and ends nominally at Z228.15, 1 mm below the reservoir plate; the short tip may remain slightly angled. A-fill and B-draw pass through their aligned straight guides. Dress and tag the front-top ends on the bench, then make the flexible handoffs through the funnel opening before fitting the frame.

The drawn external `fluid-24` span includes the nominal 16.891 mm receiving length in V-I's stem elbow. The cap-entry boundary divides the CAD spans of one physical blank; measure the complete route through the passage to the reservoir tip and use the actual V-I receiving mark when preparing it. Keep the source end free while seating the cap and completing its three clamps, then insert it into V-I's clocked elbow. Terminate both J10 power leads on the loose PCB before fastening it to the core, then land their free ends at the core WAGOs. Stage the flexible B-fill tube clear of the J5/J6/J13 withdrawal approaches when handling those connectors.

The carbonated-water riser leaves `carb-water-out` directly for the rear middle-right rear
bulkhead through the DIGITEN meter. Flavor A leaves V-G on `fluid-18`; flavor B leaves
V-J on `fluid-28`. Complete these routes in §4.

### 4. Rear beverage connections

The soda outlet is the middle-right rear fitting. One continuous blue tube
runs from the carbonator's bottom outlet through the straight guide at
X77.5/Y359.51/Z253.4, around the accepted R14 holder and into the DIGITEN inlet.
The holder stands 9 mm from the meter mouth. Slide one square-cut 61 mm piece
of ID6.35/OD25.4 foam over the tube and holder before connecting the meter.
Keep both square ends. The occupied foam model describes local compression.

With back-top inverted, prepare the meter with its inlet and the concealed
outlet stub. Slide it aft into its east-wall seat and onto the soda union,
then fit its cap from the west. Its label faces east and its lead root faces
down. The outlet stub occupies both receiving sockets with no exposed span.
Use the actual seating marks for the meter and union depths.

Flavor A runs from V-G to X77.5/Z264; flavor B runs from V-J to X37.25/Z264.
Both use black 4 mm tubing with R25 or larger bends. Their free fore runs
cross below the funnel frame, use the pump's east aisle and enter the rear
sockets below the meter. Flavor A passes through the relief in the meter
cap's lower wing. Load their straight rear spans into the upward-opening lid
snaps at X70/Y412/Z257 and X35/Y414/Z264 before positioning back-top.
The 4.10 mm bores and 1.52 mm wings are the selected modeled 4 mm section.

The reservoir A pair retains its fore and aft anchors. Follow the free aft
bends in [reservoir-a-routes.json](/hardware/manifold-layout/reservoir-a-routes.json):
they pass the V-K outlet and the east side of the soda foam before returning
to their original reservoir mouths. Keep the paired tie and both collets
accessible while the core is open.

Carry the loose front dispense ends while positioning back-top. Connect V-G
and V-J through the uncovered funnel opening, matching each faucet tail's
collar to its logical rear socket. The removable funnel frame carries no
flavor-tube seat.

### 5. Final connections through the funnel opening

Make the V-A low feed and V-B high feed/return with the funnel frame absent.
Press the straight white V-A feed, `fluid-3` / `above-core-va-fore-feed`,
downward into the core lid's upward-opening C2 clip at world
(11, 254.5, 261.6) mm. Seat that tube before final dressing of
`PE-carbonator` and `J4-V5`; keep both leads out of its loading approach.
Release the tube from the lid clip before moving back-top for service.
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
from the draw fittings to the floors. Both continuous fill tubes end 1 mm
below their reservoir plates, open to the headspace.

Cut two nominal 31.25 mm pieces of white 4 mm OD / 2.5 mm ID LLDPE. Feed each
through its dedicated foam-cap passage and air grip, leaving 6 mm above the
outer cap face. Its lower end stands 1 mm below the reservoir plate. Each air
path is open in both directions and independent of the other reservoir.
[Installation and dimensions](/hardware/printed-parts/cold-core/reservoir/vent.md).
