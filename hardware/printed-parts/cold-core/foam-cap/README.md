# Cold-core cap and equipment mounts

The top cap is a foam-pour cup closed by a 5.4 mm lid. Its plain vertical
casing wall is 2.38 mm and its floor is 2 mm. The 282.4 × 180.4 mm casing
leaves 0.30 mm per face for the exterior foil bands. The
[casing integration receipt](../casing-integration-review.json) records its
independent mounting, passage and stack-height datums. The PCB lies flat on
its west half; the diaphragm pump stands aft. V-B seats in
an integral upright socket wall east of the PCB. The water check rests on
a fore–aft quarter bearing on a filled lid-rooted pedestal. It opens upward and west,
leaving the west approach open. The four DC/sensor wells sit on the board-facing back of V-B’s wall,
with levers opening west. The earth boss is accessible from above. Back-top carries V-A, V-K, their fitted
plumbing, the complete inlet header, PSU, both relays and flow meter.

Two independent reservoir air tubes have floor-rooted 5.2 mm passages through
the cup's foam cavity, with 2 mm printed walls and matching openings through
the lid. Each straight 4 mm tube passes through a flush TPU grip in its
reservoir lid and ends 6 mm above this casing face. Native shell-frame axes
are A (120, -26) and B (-102, -32.5) mm; the top cup/lid install after their
shared 180° half-turn. [Tube and grip details](../reservoir/vent.md).

V-B uses the shared V69 socket profile. Its wall travels with the populated
core. V-A and V-K use back-top's sidewall-rooted seats; their open-bench
preparation belongs to [internal plumbing](../../../assembly/internal-plumbing.md).
Their underside flow arrows point down, with the header at the upper inlets
and the pump/Y-A feeds at the lower outlets.

The edge-on flow meter, both collar bearings, continuous external inlet,
accepted R14 holder and one 63 mm square-ended foam piece belong to back-top.
The collar bearings root into its roof. Thread the tube through the
holder and slide the foam over both before connecting the meter. The holder
has a 2 mm wall and 3 mm legs; local foam compression remains an estimate
informed by the recorded physical fit. The core guide is a plain boundary in
one uncut tube. Tighten the pump screws before connecting that inlet, which
crosses one pump-driver approach; disconnect it for that screw's service.

The V-B return has a filled 11.24 × 11.5 mm lid pedestal beneath its forward
leg, with a peaked tie passage and one six-inch narrow tie on the fixed body band.
Keep both release collets free. V-A's low turn travels with back-top through
its connected tubing. Support and dress that free feed on the open bench;
its final connection is at front-top's Y-A. No independent V-A printed bearing
or retaining strip is included in this cap.

Thread the V-B holder before seating the fitting and dress its tie before
final upper connections. Complete J10 power termination and seat J11 before
fitting the selected return; that return occupies J10's vertical screwdriver
corridors in the recorded access study. The recorded J11 housing path belongs to the X−50 return variant. The native
review includes the source-scoped pump and PCB mounting tools,
seven JST housing withdrawal columns, both KF301 screw axes and 8 mm straight
wire-entry lands. J1, J2 and J11 use the complete housing paths in the
[connector service record](../../../mechanical-qualification/enclosure-above-core/flavor-and-connector-review.json):
J1 and J2 lift 17 mm, then move 8 mm fore to a disengaged staging position.
With the funnel, frame and attached drain removed, J11 lifts 6 mm, moves 6 mm
east, then lifts another 20 mm. Its first lift clears the selected header by
1.30 mm. These are CAD access
envelopes; hand access, flexible lead dressing, clone fit and installed
tightening force remain unqualified. Nominal 2.5 × 0.8 mm
strip paths and their line/arc lengths belong to `union_tie_routes()`,
`check_tie_route()` in the mount helper; `meter_tie_routes()` delegates to
the back-top bearings. `nominal_tie_strips()` builds their
complete native witness solids. Purchased tie dimensions, bend/twist transitions, threading,
head engagement and retention remain unqualified.

| Restraint | Nominal strip route | Allocated tie |
| --- | ---: | --- |
| V-B outlet return | 76.96 mm | One 152.4 mm narrow tie |
| Water-check barrel | 72.34 mm | One 152.4 mm narrow tie |

The [production arrangement](../../../manifold-layout/above-core.md) owns the
installed component frames. [_above_core_mounts.py](../_above_core_mounts.py)
carries the native PCB and four identical pump-foot mounting patterns into
the cap. The PSU mounts on back-top's dry sidewall; its ceiling is continuous.

| Equipment | Stations | Screw | Insert | Bearing stack and reach |
| --- | ---: | --- | --- | --- |
| G Ganen diaphragm pump | 4 | M3 × 20 | RX-M3x5.7 | Nominal 7 mm rubber pad + 0.8 mm washer, 5.4 mm lid and 0.15 mm dry joint; 6.65 mm nominal reach into the column |
| Main PCB | 4 | M3 × 8 | RX-M3x5.7 | 1.6 mm PCB on 3.6 mm standoffs; 6.4 mm reach |

These eight cup-rooted columns are Ø10 mm with Ø4 mm blind pilots 9.75 mm
deep, retaining the ordinary 3 mm radial insert wall. Flush pilot bottoms retain
4.55 mm of stock to the cup's outer floor. The PCB posts pass through clearance
holes in the lid. The pump retains its purchased rubber sliders and Ø9 × 0.8 mm
washers; installed rubber compression and isolation remain unqualified.

The separate lid-mounted earth boss is Ø10 mm with a Ø4 × 7 mm pilot for
one RX-M3Sx4 short insert. Its M3 × 8 screw crosses three 0.8 mm ring tongues
and one 0.8 mm washer: 4.8 mm projection, 2.2 mm nominal tip air and 4.4 mm
blind backing. Its fastener datums belong to
[above_core_wiring.py](../../../manifold-layout/above_core_wiring.py).

The four core WAGO junctions form two rows on the board-facing back of V-B’s
wall. V12 and sensor ports face fore; GND and reed ports face aft. Their
levers open west. The blank-backed wells retain 3 mm walls and join the
V-B wall and lid. Their top and V-B’s wall share the flat Z298.65 mm plane, with 1.25 mm to the funnel frame.
V-B’s native origin is Z279.41 mm.

The four junction origins share world X29.0 mm. Reservoir B's 4 mm vent tube
remains at X32.5/Y221.8, ending at Z259.4. Its Ø5.2 mm straight passage continues
through the full adjacent V-B wall height. The west backing plane is X32.0;
the vent has 1.5 mm nominal air to the lower V12 connector and 0.6 mm radial
allowance in its printed passage. The socket backing and broad wall root remain
at least 3 mm. These are native CAD clearances. The
[vent and junction review](vent-review/README.md) binds this arrangement and
the Mark1 archive for its recorded STL hash.

Reservoir A’s draw and fill tubes use two direct fore C2 clips and one aft tied
seat. Draw occupies the west position at each station. The fore tube axes are
X50.5/64.0 at Y209.75, Z258.5 mm: **13.5 mm centre spacing**. Each clip has the
selected **6.35 mm bore**, **2.40 mm spring wall** and **125.421° wrap per wing**.
Both span the full Y205.75–213.75 mm run.

One broad base spans X44.925–69.575 mm. It fills the space below the tube equators
at Z258.5, with the two round bores cut through that common stock. Its bottom at
Z250.4 joins 3 mm into the existing lid beneath the Z253.4 face. The curved arms
above the equators remain free to spread. Press each tube down through its open
+Z mouth; lift it upward with the exposed jaws released for removal. The clips
are integral to the lid, which prints on its flat underside.

The [C2 coupon result](../../../../future/snap-fit-tests/2026-10-26-mark2-combined/physical-result.json)
selects this quarter-inch bore and spring section for present use. It does not
qualify the complete paired station's printed finish, installed access, numerical
forces or lifetime. Both tubes pass below V-B at Z258.5 and rise to Z259.5 before
the aft restraint. The
[wall-routing review](wago-wall-review/README.md) records the native fit and lid slice.

The aft seat occupies Y299–309 at Z259.5 mm. Its R3.325 mm grooves follow the
actual tube curves, with one narrow tie passage beneath the pair. The top plane
at Z256.95 retains a central ridge above the ordinary 3 mm stock. The outer tube uses an open outboard quarter-seat
with a 3 mm bottom bearing. The base ends at X97.7, clear of the enclosure flank.
The slot ceiling at Z253.175 retains a complete 3 mm wall below the lowest seat;
its floor at Z251.6 leaves 3.6 mm beneath it. The anchor base shares the lid’s underside
at Z248. Side mouths provide threading access. One nominal 2.5 × 0.8 mm tie witness
describes the aft path; purchased tie dimensions, threading, installed retention and
load capacity remain unqualified. The aft seat extends beyond the core’s east edge.

[_reservoir_a_c2.py](../_reservoir_a_c2.py) supplies the fore C2 geometry;
[_reservoir_a_anchors.py](../_reservoir_a_anchors.py) defines the shared tube stations
and aft seat, passage and tie witness. The tubes remain continuous. The
[anchor reader receipt](reservoir-a-anchor-review.json) binds its identified two-tie
article and finite native stock witnesses; those fore tie-passage results do not qualify
the direct C2 interface. The lid and cup use the same smooth print-mesh export. Nearby
electrical and nominal-tie contacts retain their explicit fixture status.

The [neoFit ACHV44-E water check](../../../reference/neofit-achv44-check/README.md)
uses an 8.8 mm-long east quarter bearing beginning 0.5 mm inside its fixed barrel
band. Its full 11.58 × 8.8 mm pedestal reaches the lid directly, ahead of the
fore pump foot. A transverse tie passage has 2.8 mm width, 1.8 mm straight sides and a
45° peaked roof at 3.2 mm overall height. It retains 3 mm
of stock beneath the bearing and at both axial ends. The printed pedestal clears
all four pump-driver columns. Fasten the pump before seating the check. For pump service,
release or disconnect the removable check group to clear that driver lane.

The water check's complete nominal 2.5 × 0.8 mm retaining-strip path is
72.34 mm, read from `check_tie_route()`. Thread it through the pedestal's straight passage
before seating the check. One six-inch narrow tie is allocated. The
outlet elbow has 0.4 mm exposed stem ahead of the reference's 16.891 mm
receiving depth. The check's exterior scale and receiving depth are
same-family layout inferences. Actual part dimensions, collet release travel,
tie threading, head engagement and installed retention remain unqualified.
The manually invoked [bearing review](check_bridge_review.py) records its
3 mm stock, lid backing and nominal strip against the exported lid in the
[cap receipt](above-core-native-review.json).

The cap's ten M3 × 25 closure stations per face, dry seat allowances and
reservoir cap bores retain their separate interfaces. The V-B wall, the lid's only
valve wall, uses the shared [V69 socket fit](../../valve-seat/README.md); that accepted
fit does not establish retention load or life in this upright host.

The upper passages follow the installed equipment:

- B-draw and A-fill each make a 3.5 mm shift with two 14 mm centreline-radius
  turns above their unchanged reservoir bores.
- B-fill uses a trimmed NeoFit stem elbow through its original plain reservoir
  bore, a short exposed tube and a JG PP0308E union elbow. The upper socket is
  at enclosure world (−33, 287.5, 264.56239) mm. The approximately 15.6 mm exposed link
  excludes socket insertion; the JG insertion depth is unmeasured. The lower
  stem ends 1 mm below the reservoir cap's fill boss in the headspace.
- The pressure-water inlet remains one continuous R14 tube from the fixed
  carbonator fitting through the cup to the aft plain guide at world
  (−32.8018, 410.0533, 253.4) mm, directly below the downward check elbow.
  Its short S passes east of the sensor loom. The D7.5 passage has 3 mm side and roof stock rooted into
  the cup floor. The existing [cap-floor specification](../_cold_core_interface.py) retains
  the complete 2 mm cup floor, with 2.10 mm backing under the horizontal
  passage; only its actual curved entry cuts the floor. No new stock projects
  below the cup. The upper guide is a boundary in one uncut tube.
- The gas guide feeds the retained lower gas lane through a shallow shift;
  the carbonator fitting and support-ring approach retain their own stations.
- The soda outlet retains its lower riser beside the coil, then turns through
  a curved 7.5 mm passage above the tank to world (50, 342.4148, 253.4) mm.
  Its R14 upper bends have 3 mm side and roof stock within the cup. The horizontal
  span retains 2.10 mm of floor beneath the passage; the curved entry crosses
  the cup floor beside the lower riser. The plain upper guide is a boundary
  in one uncut tube that follows the accepted R14 holder directly into the
  meter inlet. No extra fitting or tube cut occurs at the guide.
- The carbonator's three reed conductors use a straight Ø7.5 mm passage through
  the upper cup and top lid at shell (0, −74) mm / enclosure
  (74, 323.8, 253.4) mm. A floor-rooted Ø12.26 mm column keeps pour foam out.
  Its nominal packed loom is 4.0 mm across. Seal its warm-side exit with its
  own foil collar. The three conductors turn west beneath the pump housing,
  then rise along the clear west PCB approach to J7 and the common WAGO.
  The shared upper dressing uses nominal 3 mm bends; individual pin and reed
  fanouts have their measured model radii in the wiring worksheet.
- The two reservoir reed looms and temperature/earth loom have separate lower entries and upper exits. Their
  7.5 mm passages make 5.5 mm turns within the cup. Reed B crosses at world
  Y205 around the PCB columns; the sensor loom follows its named curved corridor.
  Nominal packed loom diameters are 5.0 mm for each reed bundle and 6.6 mm retained envelope for
  the temperature/earth bundle.

B-fill's lower fitting pocket has a flat floor at world Z235.6 and ceiling at
Z251.4. Its flat cover ends at Z254.45, retaining 3.05 mm stock. The upper
fitting has a separate broad 2.4 mm retaining cover ending at Z254.75, with
0.25 mm nominal air to the PCB solder tails. One plain transition joins each
cover to the lid; the pocket walls retain at least 3 mm stock. The short
link opens into the dry pocket beneath the plain lid. Assemble both fittings
and their prepared link in the open cup before the lid goes on for the cap pour. The upper
horizontal barrel bears upward against its cover; the PCB is not a restraint.
The original 2 mm cup floor remains around the lower stem entry. Mask the
fitting pockets and link during the foam pour, including their dry lid joints.
The [local fitting review](b-fill-pair-review.json) and
[manual reader](b_fill_pair_review.py) scope these CAD readings. The 2.4 mm
section is specific to this internal cover; it does not qualify pull strength,
printed tolerance, support removal, pressure sealing, condensation or life.
Terminate both J10 power leads on the loose PCB before fastening the board
to the core, then land their free ends at the core WAGOs. The captured upper
fitting overlaps the optional 8 mm straight J10-V12 wire-entry witness;
the current installed lead and vertical screw tools clear it. Installed
wire insertion/withdrawal service is unqualified and may require unbolting
and staging the PCB and flexible leads.

The [aft water-passage receipt](../../../mechanical-qualification/enclosure-above-core/water-in-passage-review.json)
binds the exported cup, lid and continuous internal tube, including the existing
2 mm floor scope, 3 mm new side/roof stock and receiving-allowance limits.

The [native geometry review](above-core-native-review.json) records the scoped
passage, insert-stock, fitting-pocket, pump/check-bridge and valve-wall interface
queries. The eight pilots retain their complete 9.75 mm depth with the
supplier's 1.6 mm minimum surrounding wall and at least 1 mm blind backing.

The lid lifts after the equipment connections and its fasteners are released;
the core-mounted junctions lift with it. Final inter-quadrant connections are
completed on the open subassemblies and through the available funnel opening
before its frame is fitted. The electronics ceiling is continuous. The cap's dry seams require a continuous exterior foil seal. Physical fit and foil
adhesion records retain their identified article scopes; they do not qualify
this complete cap assembly or the appliance vapor barrier.
