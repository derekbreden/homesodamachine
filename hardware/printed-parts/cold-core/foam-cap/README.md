# Cold-core cap and equipment mounts

The top cap is a foam-pour cup closed by a 5.4 mm lid. The PCB and Mean Well
PSU lie flat on its west half; the diaphragm pump stands aft. V-A, V-B and V-K
seat in integral upright socket walls. V-B stands east of the PCB; V-A and
V-K flank the fore plumbing. The water check rests on a fore–aft quarter
bearing on an aft-rooted bridge. It opens upward and west, leaving the PSU face clear.
The four DC/sensor junction wells and the earth boss remain accessible from
above. The fixed enclosure wall carries both relays.

V-A and V-K retain their complete socket plates above each plate's lower
bearing edge. Their broad lower roots stay inside the core's X±90.5 mm
footprint, while the socket plates project about 4.7 mm beyond it above the
root. A single flat aft relief below each complete socket plate clears the
lower valve barrel and its attached NeoFit collar with 0.15 mm nominal air;
the full-width lower root retains 7.153 mm of depth. The three socket walls
move with the populated core during enclosure assembly.

Clock V-A and V-K with their underside flow arrows downward, inlet above
and outlet below. Their terminal blades point downward.
Seat bare V-A first and V-K second on the open bench, before the PCB, PSU,
pump, meter, fitted elbows and leads. Lower each body 6.2 mm aft of its final
position, then seat it 6.2 mm fore. The native approach keeps the post tips
1 mm off the lip before its 5.2 mm engagement. Clock V-A's upper inlet release
ear clear of the elbow body; the model uses a 15° turn. Keep the collet free
to operate. Fit the upper inlet elbows
before the back column closes; the fixed roof obstructs their complete axial
insertion stroke. These are geometric sequencing constraints, not insertion
force or fit qualification.

Attach the prepared blade leads after both bare valves are seated, before
installing the PCB, PSU, pump and meter. Dress the free PCB ends for final
connection through the open roof. The native valve proof includes the blades;
separate female terminal housings and their seating force remain unqualified.

The edge-on flow meter sits fore–aft on two fixed-collar bearings rooted in
the lid. Each six-millimetre-wide east-lower quarter bearing opens upward
and west, retains 3 mm of outer stock and has a 2.8 × 2 mm closed tie window
below its seat. One
six-inch tie retains each collar without crossing a release collet or the
downward lead root. Tighten the pump screws before dropping the meter into
its bearings. The meter, continuous inlet tube, accepted R14 holder and
single 63 mm square-ended foam piece belong to the standalone core assembly.
Thread the tube through the holder and slide the foam over both before
connecting the meter. The holder has a 2 mm wall and 3 mm legs; local foam
compression remains an estimate informed by the recorded physical fit.
The fore bearing has one flat step above the pump foot,
leaving a 4.6 mm-thick east root below Z280. The aft bearing occupies the fore 6 mm of its fixed
collar band, leaving 0.1 mm at the band's fore edge.

Two JG union elbows have integral lid restraints. V-A's east turn sits on
an upward-open west quarter bearing below the pump head. V-B's return uses a
short broad ledge and a flat root aft of the PCB; its
closed tie window retains more than 3 mm above it. Each uses one six-inch
narrow tie around a fixed
body band. Bearings and nominal strap routes stay off the collet reference
envelopes; release travel is unmeasured.

Thread the empty holders and seat V-A's elbow on the bench before installing
the pump. Dress the V-B tie before its final upper connections. The native
review includes the pump, PCB and PSU mounting tools, PSU terminal approaches,
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
`meter_tie_routes()` and `check_tie_route()` in the mount helper; `nominal_tie_strips()` builds their
complete native witness solids. Purchased tie dimensions, bend/twist transitions, threading,
head engagement and retention remain unqualified.

| Restraint | Nominal strip route | Allocated tie |
| --- | ---: | --- |
| V-A east turn | 81.99 mm | One 152.4 mm narrow tie |
| V-B outlet return | 112.05 mm | One 152.4 mm narrow tie |
| Fore meter collar | 88.65 mm | One 152.4 mm narrow tie |
| Aft meter collar | 137.40 mm | One 152.4 mm narrow tie |
| Water-check barrel | 69.81 mm | One 152.4 mm narrow tie |

The [production arrangement](../../../manifold-layout/above-core.md) owns the
installed component frames. [_above_core_mounts.py](../_above_core_mounts.py)
carries the native PCB, PSU and four identical pump-foot mounting patterns into
the cap. No equipment or wiring attaches to the removable electronics panel.

| Equipment | Stations | Screw | Insert | Bearing stack and reach |
| --- | ---: | --- | --- | --- |
| G Ganen diaphragm pump | 4 | M3 × 20 | RX-M3x5.7 | Nominal 7 mm rubber pad + 0.8 mm washer, 5.4 mm lid and 0.15 mm dry joint; 6.65 mm nominal reach into the column |
| Main PCB | 4 | M3 × 8 | RX-M3x5.7 | 1.6 mm PCB on 3.6 mm standoffs; 6.4 mm reach |
| Flat IRM-90-12ST | 4 | M3 × 20 | RX-M3x5.7 | 6.7 ± 1 mm mounting ear, 5.4 mm lid and 0.15 mm dry joint; 6.75–8.75 mm reach |

These twelve cup-rooted columns are Ø8 mm with Ø4 mm blind pilots 9.75 mm
deep. The PSU's minimum ear thickness leaves 1 mm screw-tip reserve; its
maximum still engages the full 5.7 mm insert. Flush pilot bottoms retain
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
  Its R14 upper bends occupy a 2 mm-wall sleeve within the cup. The horizontal
  span retains 2.10 mm of floor beneath the passage; the curved entry crosses
  the cup floor beside the lower riser. The plain upper guide is a boundary
  in one uncut tube that follows the accepted R14 holder directly into the
  meter inlet. No extra fitting or tube cut occurs at the guide.
- Reed and sensor looms have separate lower entries and upper exits. Their
  7.5 mm passages make 5.5 mm turns within the cup. Reed B crosses at world
  Y205 around the PCB columns; the sensor loom passes around the PSU columns.
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
queries. The twelve pilots retain their complete 9.75 mm depth with the
supplier's 1.6 mm minimum surrounding wall and at least 1 mm blind backing.

The lid lifts after the equipment connections and its fasteners are released;
the core-mounted junctions lift with it. Final inter-quadrant connections are
accessible with the funnel frame and electronics panel removed. Both enclosure
closures install last. The cap's dry seams require a continuous exterior foil seal. Physical fit and foil
adhesion records retain their identified article scopes; they do not qualify
this complete cap assembly or the appliance vapor barrier.
