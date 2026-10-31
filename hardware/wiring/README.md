# Installed enclosure wiring

The enclosure's electrical graph and proposed installed geometry live together in
this model. Every insulated conductor has a stable ID, two named attachments, a
stock profile, an assembly owner and a routed centreline. Each distribution bus
is an explicit electrical interface.

- [Populated enclosure](../manifold-layout/enclosure-assembly.step): hardware,
  printed pieces, wiring, connector housings and fuse-splice insulation together.
- [Wiring assembly](enclosure-wiring.step): the same installed wiring on its own.
- [Resolved model](enclosure-wiring.json): terminal positions and directions,
  sources, nominal dimensions, connections, routes, lengths and service boundaries.
- [Conductor worksheet](enclosure-wiring.csv): one row per physical conductor.
- [Routing review](installed/routing-review.json): manually requested interference,
  native-solid and integration readings, bound to their actual artifact hashes.
- [Exact contact follow-up](installed/contact-review.json): native-solid readings
  of the remaining mesh contact witnesses and their local electrical endpoints.
- [Cap passage review](installed/cap-passage-review.json): native cup/lid validity
  and the shared bore through all three assembly hosts.
- [Integration record](installed/integration-review.json): wiring subassembly and
  retained physical assembly scope.
- [Integral pump-mount wiring review](installed/integral-pump-mount-review.json):
  the eight pump/display conductors, shared passage and current printed stock.
- [Manifold junction wiring review](installed/manifold-wago-shift-review.json):
  the 14 conductors at the aligned front-top WAGO holders and retained hardware.
- [Inspection overview](installed/enclosure-wiring-overview.png): the complete
  wiring and a closer front-assembly view, with unresolved routes dashed red.
- [Compressor cable views](https://homesodamachine.com/changes/2026-10-20-2338-compressor-cable):
  shared cable corridor and fuse fanout.

The model covers the AC inlet, PSU, compressor/fuse lead, earth bonds, 12 V
distribution, diaphragm pump, all eleven valves, condenser fan, both pump motors,
rear faucet jack, enclosure display, gas sensor, two temperature probes and all
ten reeds. The external line cord and the faucet's outboard umbilical end at
their enclosure interfaces. J2 OUT4, J4 IO23/IO27 and the I2C expansion header
have no installed cable.

## Attachments and fidelity

`modeled` means a location follows the existing native part geometry. It is not a
physical acceptance. `nominal` marks a layout dimension or proposed solder-joint
region. `unlocated` keeps a required electrical connection whose precise device
terminal is absent from the reference model. These states are separate from the
route's status.

Valve attachments use the separate native metal spades. G/J's proposed wire exit
is aft from the tab engagement region; the tabs and disconnects can bend. The
model imposes no rigid Faston boot box on a valve or pump-motor tab. Board pin
identities and physical XY positions come from the fabricated `pcba.circuit.json`,
carried through the native board pose. J10's side wire entries are separate from
the screw-head direction. The tilted display and vertical pump motors retain
their own reference frames. Their terminal locations remain explicitly
unlocated; the shared passage describes proposed installed wire dressing.

The ten XH housings use nominal dimensions from the
[JST XH drawing](https://www.jst-mfg.com/product/pdf/eng/eXH.pdf): 2.5 mm pitch,
5.7 mm depth, 7.5 mm housing height and 9.8 mm assembled height above the board.
Their outer profiles and wire throats are layout envelopes; latch details and the
on-hand copies' fit are unmeasured.

The four J13 conductors leave the board stacked 1.9 mm apart, over the J6 leads
and west of the Y-B stem elbow. They cross front-top's common rear electrical
mouth side by side, `AM2`, `AM1`, `BM2` and `BM1` from +X to −X, below the J9
display ribbon. The pairs turn through the integral transverse channel into
the two motor terminal rooms. Each lead ends in a Faston receptacle on its
motor tab. J9 shares that rear mouth and rises through the display chimney;
both ribbons are bare inside the print and SIG-7's braid ends aft of the mouth.
The passage centres come from the same native geometry that cuts front-top.

J9's free fore descent stations lie at Z281.5 beneath the 4 mm flavor-A
crossover. The selected J1-positive-C/D free bends have a 0.6 mm west,
0.8 mm aft offset. Electrical endpoints and the integral passage stations
retain their selected coordinates. The
[scoped native routing reading](../mechanical-qualification/enclosure-above-core/stem-elbow-routing-review.json)
records these six free-bend changes with the front reservoir stem elbows.

The compressor's three conductors share one jacket corridor below the funnel
frame, through the gap between the valve banks and into the compressor bay.
The annular jacket uses an 8 mm outside-diameter layout allowance. The three
core positions rotate together through its bends, preserving their section
spacing. Each end fanout has independently editable stations.

The thermal fuse's dressed 1 mm leads continue beyond the reference's fixed
3 mm straight stubs to proposed insulated splice regions beside the retained
power box. The front lead uses the reference's 35 mm side and the aft lead its
20 mm side. The compressor earth uses the existing downward-facing ring lug.
Final donor contacts remain unlocated beside the native power-cover envelope.

Exact compressor, fan, pump-motor, diaphragm-pump and display terminal details
remain unlocated. The carbonator's earth ring clamps directly to the existing
upper vessel rim. Its wire mouth and upward barrel share the rim attachment's
datums. The lead joins the shared west-side sensor riser above the vessel
plate and terminates at the lid earth star at world (−53, 339, 259.4) mm.
Power-wire insulation
ODs and recovered heat-shrink dimensions are editable layout allowances. Those
allowances do not establish a reason to change the surrounding hardware.

The two temperature probes' bare leads and the carbonator reeds' leads terminate
at proposed insulated splice regions outside the coil. Their detailed bare-lead
dressing remains part of device integration. The reservoir columns carry four
signals and one continuous common, with insulated local taps. The carbonator's
reed pair also shares one common. Each reservoir column's common is a straight
spine beside the reeds, with short local soldered taps.

Reservoir A's five conductors rise vertically through an aligned cap bore over
the dry reed channel, with their turns above the lid. Reservoir B's five
conductors leave the dry reed channel through
the shell-rim notch and rise outside the cap beside the B-fill block. Its four
signals terminate at J7, and its common terminates at `wago-reeds-b`. Below the
cap, four signals descend around the reed envelopes and the common runs beside
them. The temperature bus has one shared three-conductor path between probes.
The incoming V/DATA/GND leads feed the coil probe first, then continue to the
carbonator-wall probe. The coil-side route turns aft below the PRV vent at
world Z184, then rises at Y347 to the shared riser. Its tangential splice rows
are proposed harness joints; they do not specify the TO-92 package pin order.

Reservoir A uses its top-cap reed conduit. Reservoir B uses an 8 mm-wide outlet
cut 6 mm below the shell's top edge, with its conductors laid through the open rim
before the cap is seated. The shared west-side Ø7.5 mm `sensor-cable` passage
at world X−48/Y347 carries seven conductors: the three temperature-bus leads,
CLO, CHI, their continuous common and the green 16 AWG carbonator PE lead.
Its printed guide bends at R5.5 inside the cup to the lid exit at world X−78/Y320/Z253.4. The
nominal packed loom envelope is 6.6 mm. The fixed east-side reeds retain
their positions; their three leads transfer over the open vessel head at
world Z225/Y352 to the west riser. Lay these free lead transitions while the
body is open, before the foam pour. Thread the free ends through the cup and
lid before fitting the outside terminations. Above the lid the signal looms
follow the west PCB approach; PE runs aft to the rear-wall earth star. The
temperature and reed commons keep their separate existing WAGO connections.

## Routing and assembly

Insulated wires may lie against a surface or another wire. They need room
to occupy their routed space: avoid trapping them on all sides in a narrow
channel or sending them through solid stock. A uniform 1 mm gap around each
wire is not a design requirement. Local room readings remain manual design
reviews; they add no build or commit check.

`selected_layout` identifies the installed course. The manual routing report
checks its wires and jackets against larger bodies; wire-to-wire and
wire-to-tube contacts are excluded. Endpoint contact is local to the named
attachment. Terminal fidelity and physical harness handling retain their
separate recorded scopes.

The manifest lists every wire crossing between the base, cold core, front-top
and back-top. The four J13 conductors run from the board on the cold core to
the pumps carried by front-top. The lower pump retainer is a mechanical piece;
it carries no separate electrical connection.

A drawn route does not establish that the dressed harness permits every enclosure
assembly and closing motion. Terminal access, actual ribbon web/branch dressing,
sleeve fit and service slack remain assembly details. Centreline lengths exclude
hidden termination insertion and a final cut allowance; the CSV is not a cut list.
The mechanical assembly scorecard retains its mechanical scope. Wiring review is
the separate, manually invoked reading linked above.

## Editing and materializing

The editable source is under [`installed/`](installed/):

| Source | Responsibility |
| --- | --- |
| `connections.py` | Conductor IDs, nets, logical endpoints, common buses and owners |
| `terminals.py` | Reference geometry, pin map, attachment location/direction and fidelity |
| `connector-map.json` | Tracked snapshot of fabricated board pins, source hashes and the J10 component envelope |
| `model.py` | Stock profiles, tangent circular bends, native wire construction and lengths |
| `routes.py` | Hardware-relative route families and override interpretation |
| `route-overrides.json` | Individually editable hardware-relative stations and unresolved routing records |
| `bundle-routes.json` / `bundles.py` | Shared cable corridors, conductor sections, end fanouts and optional jackets |
| `terminations.py` | Removable housings, dressed fuse leads and joint insulation |
| `build.py` | Native wiring assembly, manifest, worksheet and enclosure integration |

Rebuild the wiring against the current populated native enclosure:

```sh
tools/cad-venv/bin/python hardware/wiring/installed/build.py
```

The normal `enclosure_assembly.py` composition includes the same wiring model.
The wiring-only materializer replaces its own marked STEP subassembly and viewer
meshes; existing physical component records and meshes are retained. Native and
viewer outputs use the same `wire-<ID>` and `terminal-<ID>` names. For example,
`wire-J13-AM2` is the AM2 conductor in both assemblies and in the worksheet.

After a PCB export, refresh `connector-map.json` explicitly with
`tools/cad-venv/bin/python hardware/wiring/installed/export_connector_map.py`.
The snapshot records the circuit export, PCB GLB and board-source hashes. Normal
enclosure CAD reads this tracked map and does not need the ignored circuit JSON.

Checks run explicitly when their question is being reviewed:

```sh
tools/cad-venv/bin/python hardware/wiring/installed/review.py
tools/cad-venv/bin/python hardware/wiring/installed/review.py --native
```

`build.py --verify-retained` additionally records the retained viewer arrays for a
specific integration review. No route search or wiring check joins the build,
commit or print path. The optional `route_search.py` authoring tool searches against
the current larger-body meshes; `--retry` preserves saved routes
and searches unresolved ones. Its output needs the same route and assembly review
as hand-authored stations.

The installed graph contains 101 conductor routes. Its twelve WAGOs comprise
ten 221-413 connectors and the two manifold commons, one 221-415 and one
221-420. Three 221-413 joins finish the compressor hot, compressor neutral and
pump-positive branches beneath the removable funnel frame. Each has two
populated ports and one unused port. Their separate pigtails preserve the
open-bench preparation and final through-opening connections.
The compressor hot and neutral joins sit side by side beneath the opening,
with neutral west of hot. The pump-positive join sits lower and east of them.

For board service, remove the funnel and frame, release the three free joins
and lift them with their leads out of the housing paths. Disconnect the
V-B-to-Y-B return and cradled drain before withdrawing J11. The
[current housing sweeps](../mechanical-qualification/enclosure-above-core/connector-service-review.json)
retain J1/J2's 17 mm lift and 8 mm fore movement; J11 lifts 6 mm, moves
10 mm east and lifts another 20 mm, clearing the installed Reservoir B draw.

The [current routing report](installed/routing-review.json) records all
conductors, cable jackets and larger connector housings against the actual
installed bodies. It excludes wire-to-wire and wire-to-tube contacts and
keeps intended contact local to its named attachment. Its preparation budget
covers individual pieces and continuous commons across local taps.

The [installed native binding](installed/above-core-review/installed-wiring-binding.json)
compares the current source curves and bodies with both standalone and
installed STEP readback. Source validity, geometric agreement and the reader's
exchange-validity result remain separate fields. Terminal fidelity, physical
harness handling and closing motion retain their documented scopes.
