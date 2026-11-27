# Internal Plumbing

The selected warm-side fluid geometry is the
[production above-core arrangement](/hardware/manifold-layout/above-core.md).
Its native component frames, trimmed fittings and physical tube paths are in
[above-core.json](/hardware/manifold-layout/above-core.json),
[machine_equipment.rs](/hardware/manifold-layout/machine_equipment.rs) and
[machine_routes.rs](/hardware/manifold-layout/machine_routes.rs).
The [fluid topology](/hardware/topology/fluid-topology.md) defines the valve
functions and logical connections. A logical connection can contain several
short tubes and directly inserted stem fittings.

Load and screw-retain the pumps from below, then assemble the fixed front manifold while
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
engagement before use.

The carbonator's water-in adapter and the check's upward outlet elbow share
one continuous white 1/4-inch tube. Combine the internal `water-in` CAD span
and warm `water-5` span, using the actual receiving-end insertion marks in
place of their nominal allowances. The plain lid guide adds no insertion,
fitting or physical cut. The reported warm span is part of this single tube,
as with the continuous soda riser through its own plain guide.

The V-A outlet elbows belong to back-top. Keep its feed tube loose during the
column slide. With the column home, the continuous white tube runs from the
nested outlet elbow over the pump, through the lid clip and into Y-A. The
V-B return is one continuous length of black LLDPE between the valve outlet
stem and the Y-B stem. The lid clip guides its bend.

Prepare the funnel drain's outlet elbow and its straight link to V-B as
described in the final connections below.

## Procedure

### 1. Rear gas group

The regulator and outlet check form **HSM-0559**, prepared before entering
back-top together. The retaining cap and continuous core tube are installed
with the carrier open.

Fit the ACVUS-44 stem check directly into the PISCO regulator's outlet, following
both flow arrows. With back-top inverted, lower the pair into its seat 16 mm
forward and slide it aft. The regulator's inlet neck passes the CO2 hole;
its external release face is the rear tube station. Fit the lower snap cap
with its lip ahead of the outlet neck's shoulder. Load the cap 45 mm fore
and 3.6 mm below its final station, slide it aft through the fore flank
exits, then press upward into its catches. For service, remove the ASSE
and meter caps first, spread the Pisco leaves, lower 3.6 mm and withdraw
45 mm fore with the leaves held open.

Insert the continuous red tube into the check. It leaves forward in one bend,
then an S reaches the straight cap guide at X59.101/Y354.664/Z253.4. The same
tube continues to the carbonator's gas fitting through the retained lower
support-ring lane. The guide adds no tube cut or socket. Use the actual fully
seated marks at the check and carbonator fitting when cutting the blank.

### 2. Water group

**HSM-0558** is the threaded TAP/backflow-preventer chain, made up before it
enters the back-top seat. **HSM-0560** is the prepared pump discharge joint:
reinforced cuff, trimmed reducer, stem clamp, outlet fold and check.
**HSM-0570** is the prepared suction joint: cuff, trimmed reducer, stem clamp
and receiving elbow. Both travel with their pump ends open. The pump
enters its equipment-lid seat bare per its
[installation procedure](../reference/g-ganen-pump/installation/README.md);
the prepared joints and barb clamps are fitted afterward while the core is open.

TAP enters the PP010822E and GAGIRA threaded inlet chain. The ASSE lies
fore–aft with its vent downward. Its PI4512F6S and PP061208W outlet fittings
feed the JG PP0208E union tee through one gently curved stub. Clock the tee's
branch slightly downward toward the ASSE outlet while its through-run stays
aligned with the regulator and V-K. The modeled stub follows a tangent curve
with at least 55.9 mm bend radius; actual insertion marks determine its cut.
The tee's east
run feeds V-K's upper elbow; its west run feeds the YZMSZ regulator and V-A.
V-A hangs by its posts in the ceiling plinth. V-K uses the east-wall socket
plate with its inlet above its outlet.

1. Make up the ASSE threaded chain, keeping the two wrench flats aligned.
   Lower it into its swept hex seat 16 mm forward, slide it aft and fit the
   lower hex cap after fitting the meter cap. The cap bears against the inlet
   coupling and passes the vent. Populate these seats with back-top inverted
   on the bench and separated from the cold core. The meter cap loads 20 mm
   west and 40 mm fore of its station, slides aft, then presses east. Removal
   reverses this path after removing the ASSE cap and dressing the disconnected
   tubes and leads aside.
2. Seat the regulator upward and close its lower snap cap. Fit V-A and V-K,
   their stem elbows, the tee and the three short header links. Keep release
   collets accessible. Both opposed regulator links contain their receiving
   depths with no exposed tube.
3. Fit the pump's two [reinforced PVC joints](/hardware/reference/pump-barb-joint/README.md).
   Each has a PP061208W stem trimmed to 10 mm and a butterfly clamp on the barb
   and reducer stem. The suction tube bends in one arc to the concealed
   quarter-inch link and the nested elbow in V-K's lower port. Its stem-clamp
   key points forward; the barb-clamp key points aft. Keep the pump suction
   elbow and quarter-inch link loose while closing the rear column over the
   core. Clock the round joints and seat that link through the open funnel
   aperture after the column is home.
4. The discharge PVC cuff bends 10.289 degrees. Clock its stem clamp to the
   selected clear position, fit the trimmed stem elbow and insert the ACVUS-44
   check directly into that elbow. Follow the check's arrow away from the pump.
5. Seat the bare pump in the lid's rail seats and engage both upper-cap hooks
   before fitting the PCB. Seat the continuous white inlet to its mark in
   the discharge check. Press the crest of its bend down into the lid clip
   between the check and the water-in passage. To release the tube, lift the
   bend out of the clip before pressing the check's collet.
6. Fit the downward vent cup, its two ties and the direct white 4 mm return
   to DRAIN. Its [assembly record](asse-drain.md) defines the open faucet outlet.

Prepare push-fit ends to the actual receiving-stop marks. The native model
retains each purchased fitting's frame and nominal insertion allowance; buried
reference closures do not specify internal hydraulic geometry.

### 3. Flavor manifold: V-A through V-J + Y-A, Y-B, Y-C, Y-D, Y-F, Y-G + pumps

Build to [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) segment-for-segment. The truth table there names every valve, every Y-junction, and every tube segment by number; this step describes the build cadence around that truth table, not its content.

**This step begins on the bench with `enclosure-front-top` loose and both valve rows,
pump tees, display and funnel frame absent.** Its upper fitted pump inverses are integral
with the broad stock continuing into the display housing and roof. The broad
Each `enclosure-pump-retainer` holds one pump's flange from below. Its screws enter
from the open underside into regular heat-set inserts in front-top. Fixed upper stops and
the fitted cylindrical motor guide align the pump. The loading well tapers toward the
guide and stock separates the independent retainer pockets.

Flexible pump stubs pass through the tee wall's closed bores. Each purchased PP0208E tee
approaches from aft; its fixed branch barrel lands on the wall datum while its extended
collet grips the pump tube. Complete the fore groups before fitting the rear valve row.

The tee, upper tube and fore valve move together as **HSM-0561** (Y-C to V-E),
**HSM-0562** (Y-D to V-F), **HSM-0563** (Y-F to V-H) and **HSM-0564**
(Y-G to V-I). Their preparation and insertion follow the sequence below.

1. **Prepare the pump tube blanks.** Remove the supplied barbs from the flexible BPT
   ends. Cut the LLDPE blanks with the tube-length gauge and insert them under the loosened
   pump-head housing. Keep the housing loose enough to adjust the tubes against the actual
   seated tees during the next step. The gauge is a bench tool and stays off the assembly.

2. **Install the inserts and land the motor leads.** With front-top loose and power
   disconnected, install the regular heat-set inserts in the pump-retainer posts. Feed the
   bare pump end of [DC-5](harnesses/j13.md) through the shared rear wire passage and out
   below. Crimp and ring out its Fastons, then land the +X pair on pump A and the −X pair
   on pump B with the tabs accessible. Support the free board-end slack.

3. **Load and secure each pump independently.** Raise the pump motor-first through its
   loading well and into the fitted cylindrical guide. Feed its flexible stubs through the
   closed tee-wall bores while drawing wire slack aft. Keep the flange against its upper
   stops, fit its retainer beneath the flange, and snug the screws from below. Confirm the
   pump is straight, captured and free of wire pinches. The socket heads remain accessible
   while front-top is loose, before the tees, valves, display and chassis closure.

4. **Fit all four tees with their upper tubes and fore valves.** Keep the rear valve row
   absent for this straight approach from aft. The upper tubes are `fluid-10`
   (Y-C to V-E), `fluid-13` (Y-D to V-F), `fluid-20` (Y-F to V-H) and `fluid-23` (Y-G to
   V-I). Each nominal blank is:
   exposed, bottomed in the tee's extended upper collet and
   an estimated in the valve. Seat uncut tube fully in the
   actual fore valve's bottom collet, mark the tube at the collet face, and cut it the
   exposed length plus the tee's insertion beyond that mark. Push the tube fully into the
   tee's upper collet and the fore valve's bottom collet. Bring the tee, tube and valve in
   together from aft, keeping the tee branch coaxial with its fixed pump tube. Push the
   branch onto the tube and into its bore with its collet in the opening ahead of the bore,
   and press the fore valve onto its tray posts. Set the pump stub against the actual tee’s
   internal stop with the tee barrel on its wall datum, then tighten the pump-head housing
   to clamp the BPT around the stub. Verify insertion marks and pump-end retention. Verify the pump tube reaches its seated
   mark at the extended branch collet; the pump mount stays fixed while the tee moves.
   The fore valve's
   axis stands over the tee's run axis, so the upper tube stands straight.

5. **Seat the rear valves.** After all four fore groups are seated, press V-C, V-D, V-G
   and V-J onto their tray posts with the topology's coil clocks. Each bottom collet
   opens down into front-top's port channel, which runs from the seam up into its tray
   and keeps room for the collet and its stem elbow.

6. **Cut the stem elbows.** Each lower return takes two NeoFit ATEU44W stem elbows. Cut each
   tee elbow's stem square past its shoulder, the run
   collet's seat, and each valve elbow's past its shoulder:
   an estimated seat in the valve, with its shoulder on the
   collet face. Take the valve's
   seat from the actual received valve's fully seated mark. Chamfer each cut edge so it
   passes the O-ring without scoring it.

7. **Fit the lower returns.** From front-top's underside, push each tee elbow up into its
   tee's lower collet until its shoulder stands on the collet face, and each valve elbow up
   into its rear valve's bottom collet until its stem bottoms. Turn each pair's sockets to
   face each other. `fluid-9` runs from Y-C to V-C and `fluid-19` from Y-F to V-D; `fluid-17`
   from Y-D to V-G and `fluid-27` from Y-G to V-J lean inboard to their valves. Each is one
   continuous tube of black LLDPE, cut to for the inner two and
   for the outer two. Form two tangent arcs between the parallel
   sockets, R18.084 on the inner pair and R19.36 on the outer pair, with the rear mouths
   3.749 mm lower. Keep the inside each socket straight and
   fully seated. Use actual
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
takes `fluid-4` from the uncut ATEU44W stem elbow carried by the removable funnel frame. No reservoir has a
tee: V-F/V-E reach reservoir A's fill/draw conduits and V-I/V-H reach reservoir B's.

Route and retain fixed spans while the front-top is accessible. The four reservoir lines
land on the cold core's own cap conduits: `fluid-14` to `reservoir-a-fill`, `fluid-24` to
`reservoir-b-fill`, and `fluid-16`/`fluid-26` from the draw conduits into V-E/V-H. Each draw
line is its reservoir's dip tube: cut it long enough to reach the reservoir's floor, cut that
end at 45°, straighten it by hand, and feed it through the reservoir cap's draw grip
until the tip touches the floor. Install both dip tubes before the open-body foam pour;
their dry spans above the closed reservoirs are located by cured foam, while the dip
sections inside remain free
([floor and dip tube](/hardware/printed-parts/cold-core/reservoir/floor-and-dip-tube.md)).

Reservoir A’s two continuous tubes use two pairs of integral C2 clips on the lid: the fore
pair on one broad base, and the aft pair where each line makes its last level turn before
the reservoir. Draw is west of fill at both. The fore clips' centreline X stations are
50.5/64.0 mm, at Y209.75 and Z258.5 mm. The aft clips follow the lines' turns; the draw
line's stands higher than the fill line's and the two are one body. Press each tube down
through its clip's open +Z mouth. For removal, release the exposed jaws and lift the tube upward.
Leave the front valve ends free during the column slide and dress the
flexible spans clear of passing fittings. Once the column is home, finish
dressing the free spans and connect the front ends. For reservoir B, turn the draw
tube west in front of the funnel frame. With the frame out, seat the tube in the
V-H inlet and press its level bend downward into the bulkhead clip, one pair of
wings at a time. Lift the bend through the opening to release it for service.

Keep each tube unbroken through its plain core guide. The valve ports and clips
locate the tubing. Dress the free spans around the installed hardware, then
route the wiring. For the reservoir A blanks, include the receiving depth of
each front-valve stem elbow and the span through the guide to the fill bore
or dip-tube tip. Use the fully seated insertion mark on the actual fitting.
The guide adds no fitting, insertion or cut. Seat the bare pump in its lid saddle
and close its upper snap per the [pump installation](/hardware/reference/g-ganen-pump/installation/README.md).
Keep the continuous reservoir tubes clear of the snap's release access.
The aft pair's hand fit is accepted on its [printed crop](https://github.com/derekbreden/homesodamachine/blob/62ee60e57a37209f04aed1586ca333b5fc9a9c97/hardware/print-tests/reservoir-a-aft-snaps/prints/2026-11-20-mark1/physical-result/physical-result.json). The fore pair's fit, and insertion force and retention at either pair, have no physical acceptance. The [route record](/hardware/mechanical-qualification/enclosure-above-core/reservoir-a-route-review.json)
preserves the selected line/arc definitions and contact scope.

V-F's outlet and V-E's inlet each receive one ATEU44W stem elbow on front-top. Cut each male stem to the valve's marked tube stop (12.7 mm nominal in CAD), seat it fully and point its tube socket aft. Their reservoir tubes rise gently to the Z295.5 free runs beneath the funnel frame, with 1.225 mm nominal tube/frame air. V-I's outlet takes the same trimmed stem elbow with its socket clocked 15° east of aft. Its B-fill tube descends toward the fore-facing cap entry. Flavor A's 4 mm crossover runs at Y156/Z288.5; the J9 display ribbon's free bends pass below it while the printed cable mouth and connector positions retain their datums.

Use one continuous black LLDPE tube for B-fill from V-I to the reservoir
headspace. Protect the inlet and locate the holder during the pour, then feed
the final tube lengthwise from the front through the seated lid, holder and
TPU grip to its marked depth. [Cold-core pour](cold-core.md#6-open-body-foam-pour) · [Lid closure and B-fill feed](cold-core.md#7-close-and-populate-the-top-lid)

The cap-entry boundary divides the CAD spans of the same tube. Measure the
complete route to the reservoir tip and mark the actual receiving length in
V-I's stem elbow. Make that connection after the tube is seated in the
reservoir. Terminate both J10 power leads on the loose
PCB before fastening it to the core, then land their free ends at the core WAGOs.
Dress and tag the front-top ends on the bench and make the flexible handoffs through
the funnel opening before fitting the frame. Stage B-fill clear of the J5/J6/J13
withdrawal approaches when handling those connectors.

The carbonated-water riser leaves `carb-water-out` through the DIGITEN meter for
the middle-left rear bulkhead, viewed from behind the appliance. Flavor A leaves V-G on `fluid-18`; flavor B leaves
V-J on `fluid-28`. Complete these routes in §4.

### 4. Rear beverage connections

The soda outlet is the middle-left fitting, viewed from behind. One continuous blue tube
runs from the carbonator's bottom outlet through the straight guide at
X77.5/Y359.51/Z253.4, around the accepted R14 holder and into the DIGITEN inlet.
The holder stands 7.75 mm from the meter mouth. Slide one square-cut 56 mm piece
of ID6.35/OD25.4 foam over the tube and holder before connecting the meter.
Keep both square ends. The occupied foam model describes local compression.

With back-top inverted, prepare the meter with its inlet and the concealed
outlet stub. Slide it aft into its east-wall seat and onto the soda union,
then fit its cap from the west. Its label faces east and its lead root faces
down. The outlet stub occupies both receiving sockets with no exposed span.
Use the actual seating marks for the meter and union depths.

Flavor A runs from V-G to X28.8/Z294.2, the middle-right rear fitting;
flavor B runs from V-J to X28.8/Z264, the bottom-right rear fitting.
Both use black 4 mm tubing with R25 or larger bends. Their free fore runs
cross below the funnel frame, use the pump's east aisle and enter the rear
sockets beside the meter. Flavor A turns into the X30/Z276.5 lane between
the pump and meter caps, then rises aft of the ASSE vent sleeve to its rear
socket. Flavor B descends to its retained X35/Z264 rear span. Load A's crossover span into the
upward-opening snap at X26.5/Y266/Z296 and flavor B's rear span into the
snap at X35/Y414/Z264 before positioning back-top.
The 4.10 mm bores and 1.52 mm wings are the selected modeled 4 mm section.

The reservoir A pair retains its fore and aft anchors. Follow the free aft
bends in [reservoir-a-routes.json](/hardware/manifold-layout/reservoir-a-routes.json):
they pass the V-K outlet and the east side of the soda foam before returning
to their original reservoir mouths. The fill tube enters the 11 mm straight lid passage at X56/Y426.3
and follows an R14 S bend to the fixed reservoir bore. The passage through
the printed lid is straight and open at both ends. Press the fill and draw
tubes into their curved aft clips while the core is open.

Carry the loose front dispense ends while positioning back-top. Connect V-G
and V-J through the uncovered funnel opening, matching each faucet tail's
collar to its logical rear socket. Align the two V-G bends at X−33 before
lowering the funnel frame. The dispense tubes stay with the machine when
the frame lifts.

### 5. Final connections through the funnel opening

Make the V-A feed and V-B connections with the funnel frame absent.
Lay the white V-A feed in the curved seat beside the PCB. Press the bend
between the board-side wings, then seat the outgoing straight toward Y-A. Dress
`PE-carbonator` and `J4-V5` clear of the clip's mouth.
Release the tube from the lid clip before moving back-top for service.
Seat J11 at the main board before laying in the V-B return tube, which passes
over J11. Seat the marked tube ends in the V-B outlet stem and the Y-B stem.
Lay the bend over the curved seat and press each half down between its pair of
wings. Both straight legs should leave the clip tangent to the seat.
See [wiring](wiring.md) for J11 access. The single Y-A stem points aft and slightly east. The
raised B connections clear that first elbow.

The drain joint is made as the frame goes in, after commissioning. Snap its
cradle into the removable frame’s 3 mm web and seat the uncut ATEU44W elbow
with its male stem upward. Fit `drain-outlet-stem` into the elbow’s aft socket:
its male stem retains 17.303 mm from shoulder to tip and enters the complete
16.891 mm socket depth. Clock its female socket east and down by 12.725°;
clock V-B’s inlet turn west and up to face it.

Cut the straight black `fluid-4` link to 36.469 mm, including the 16.891 mm
insertion at each socket. Mark and fully seat both ends; the exposed span is
2.687 mm. Connect it through the open roof, then lower the frame onto its
ledges. Complete and inspect the joint before fitting the silicone funnel.
The funnel’s straight bore presses over 11.265 mm of the uncut stem, whose
tip finishes at the bowl opening. The elbow and cradle travel with the frame;
disconnect the V-B feed before withdrawing it.

Confirm every push-fit witness, trim engagement, clamp and tie on the made-up
hardware. Keep wiring clear of wet joints and preserve access to moving
collets. Fit the drop-in frame after the final
connections. Physical leak, pressure, venting and cleaning qualifications are
separate from native geometry and precede fluid commissioning.

## Qualification scope

The [mechanical qualification index](/hardware/mechanical-qualification/README.md)
preserves accepted results at their named parts and artifacts. The pump dock
has no physical seal, retention, lifetime or cleaning acceptance, and its
food-contact suitability is not established. The ASSE vent adapter, reinforced PVC pump joints, shortened fitting stems and
selected gas hardware retain their part-specific open qualification items. No unit is declared primed-ready or
safe to energize solely because the CAD paths connect.

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
