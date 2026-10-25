# Cold-core cap and equipment mounts

The top cap is a foam-pour cup closed by a 5.4 mm lid. The PCB lies flat on
its west half; the diaphragm pump stands aft. V-B seats in
an integral upright socket wall east of the PCB. The water check rests on
a fore–aft quarter bearing on an aft-rooted bridge. It opens upward and west,
leaving the west approach open. The four DC/sensor junction wells and the earth
boss remain accessible from above. Back-top carries V-A, V-K, their fitted
plumbing, the complete inlet header, PSU, both relays and flow meter.

V-B uses the shared V69 socket profile. Its wall travels with the populated
core. V-A and V-K use back-top's sidewall-rooted seats; their open-bench
preparation belongs to [internal plumbing](../../../assembly/internal-plumbing.md).
Their underside flow arrows point down, with the header at the upper inlets
and the pump/Y-A feeds at the lower outlets.

The edge-on flow meter, both collar bearings, continuous external inlet,
accepted R14 holder and one 63 mm square-ended foam piece belong to back-top.
The collar bearings root into its sidewall. Thread the tube through the
holder and slide the foam over both before connecting the meter. The holder
has a 2 mm wall and 3 mm legs; local foam compression remains an estimate
informed by the recorded physical fit. The core guide is a plain boundary in
one uncut tube. Tighten the pump screws before connecting that inlet, which
crosses one pump-driver approach; disconnect it for that screw's service.

The V-B return has an integral lid restraint. Its broad ledge and flat root
sit aft of the PCB, with one six-inch narrow tie on the fixed body band.
Keep both release collets free. V-A's low turn travels with back-top through
its connected tubing. Support and dress that free feed on the open bench;
its final connection is at front-top's Y-A. No independent V-A printed bearing
or retaining strip is included in this cap.

Thread the V-B holder before seating the fitting and dress its tie before
final upper connections. Complete J10 power termination with the selected
return released; that return occupies its vertical screwdriver corridors.
Release the flexible return for the recorded J11 service path. The native
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
| V-B outlet return | Selected route under access review | One 152.4 mm narrow tie |
| Water-check barrel | 69.81 mm | One 152.4 mm narrow tie |

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
one RX-M3Sx4 short insert. Its M3 × 10 screw crosses five 0.8 mm ring tongues
and one 0.8 mm washer: 5.2 mm projection, 1.8 mm nominal tip air and 4.4 mm
blind backing. Its fastener datums belong to
[above_core_wiring.py](../../../manifold-layout/above_core_wiring.py).

The four core WAGO junctions face west toward the PCB and stagger around
the B-draw passage. Their blank-backed wells retain 3 mm walls and sit
entirely on the lid. The levers open upward.

The [neoFit ACHV44-E water check](../../../reference/neofit-achv44-check/README.md)
uses an 8.8 mm-long east quarter bearing centered within its fixed barrel band.
The bearing retains 3 mm below and east of the body clearance; its 5 mm-deep
root begins 1 mm aft of the fore pump foot. A west-open flat notch clears the
fore-west pump screw's nominal 2.5 mm hex driver and leaves a 7.90 mm-wide
continuous beam. Fasten the pump before seating the check. For pump service,
release or disconnect the removable check group to clear that driver lane.

The water check's complete nominal 2.5 × 0.8 mm retaining-strip path is
69.81 mm. It threads through the 15.19 mm-high open space below the bridge;
one six-inch narrow tie leaves 82.59 mm of stock beyond that path. The
outlet elbow has 0.4 mm exposed stem ahead of the reference's 16.891 mm
receiving depth. The check's exterior scale and receiving depth are
same-family layout inferences. Actual part dimensions, collet release travel,
tie threading, head engagement and installed retention remain unqualified.
The manually invoked [bearing review](check_bridge_review.py) records its
3 mm stock, lid backing and nominal strip against the exported lid in the
[cap receipt](above-core-native-review.json).

The cap's ten M3 × 25 closure stations per face, dry seat allowances and
reservoir cap bores retain their separate interfaces. All three valve walls use the
shared [V69 socket fit](../../valve-seat/README.md); that accepted fit does not
establish retention load or life in these upright hosts.

The upper passages follow the installed equipment:

- B-draw and A-fill each make a 3.5 mm shift with two 14 mm centreline-radius
  turns above their unchanged reservoir bores.
- B-fill uses a trimmed NeoFit stem elbow through its original plain reservoir
  bore, a short exposed tube and a JG PP0308E union elbow. The upper socket is
  at enclosure world (−48, 287.5, 264.56239) mm. The 14.7741 mm exposed span
  excludes socket insertion; the JG insertion depth is unmeasured. The lower
  stem ends 1 mm below the reservoir cap's fill boss in the headspace.
- The pressure-water inlet remains one continuous R14 tube from the fixed
  carbonator fitting through the cup to the aft plain guide at world
  (−32.8018, 410.0533, 253.4) mm, directly below the downward check elbow.
  Its short S passes east of the sensor loom and its traverse clears the PSU
  insert column. The D7.5 passage has 3 mm side and roof stock rooted into
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
- Reed and sensor looms have separate lower entries and upper exits. Their
  7.5 mm passages make 5.5 mm turns within the cup. Reed B crosses at world
  Y205 around the PCB columns; the sensor loom follows its named curved corridor.
  Nominal packed loom diameters are 5.0 mm for each reed bundle and 6.6 mm for
  the sensor/earth bundle.

B-fill's lower fitting pocket has a flat floor at world Z235.6 and ceiling at
Z251.4. Its single rectangular roof ends at Z254.45, leaving 3.05 mm roof
stock and 0.55 mm nominal clearance to the populated-board tail envelope.
These are CAD clearances. The existing 2 mm cup floor remains around the
lower stem entry. The purchased fitting references establish external layout;
they do not qualify printed fits, assembly tolerance, pressure sealing or life.

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
