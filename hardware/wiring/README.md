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
their own reference frames.

The ten XH housings use nominal dimensions from the
[JST XH drawing](https://www.jst-mfg.com/product/pdf/eng/eXH.pdf): 2.5 mm pitch,
5.7 mm depth, 7.5 mm housing height and 9.8 mm assembled height above the board.
Their outer profiles and wire throats are layout envelopes; latch details and the
on-hand copies' fit are unmeasured.

The four J13 conductors leave the board stacked 1.9 mm apart, over the J6 leads
and west of the Y-B stem elbow. They cross the bulkhead side by side through
front-top's lead bore, `AM2`, `AM1`, `BM2` and `BM1` from +X to −X, climb the
clamp's lead-slot floor and follow one crown groove per pump into its terminal
well. Each motor's outboard tab takes its groove's aft lane, and each lead ends
in a Faston receptacle on its motor tab.

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

Exact compressor, fan, pump-motor, diaphragm-pump and display terminal details,
and the carbonator's metal bond landing remain unlocated. Power-wire insulation
ODs and recovered heat-shrink dimensions are editable layout allowances. Those
allowances do not establish a reason to change the surrounding hardware.

The two temperature probes' bare leads and the carbonator reeds' leads terminate
at proposed insulated splice regions outside the coil. Their detailed bare-lead
dressing remains part of device integration. The reservoir columns carry four
signals and one continuous common, with insulated local taps. The carbonator's
reed pair also shares one common. Each reservoir column's common is a straight
spine beside the reeds, with short local soldered taps.

Each reservoir column's five conductors share a transported section through
the cap bore and its upper turn. Below the cap, four signals descend around
the reed envelopes and the common runs beside them. The temperature bus also
has a shared three-conductor path between probes. Its tangential splice rows
are proposed harness joints; they do not specify the TO-92 package pin order.
The incoming feeds approach the first row from above, with the bus continuing
below the taps toward the second probe.

The two reservoir reed columns each use their own top-cap conduit. The three
temperature-bus conductors, three carbonator-reed conductors and carbonator
earth lead share the separate Ø7.5 mm `sensor-cable` conduit, west of the pump.
Its axis comes from the cap reference and is recorded in `cable_passages` in
the resolved model. These internal leads are laid in the foam annulus before
the body pour, with their free ends threaded through the cap and lid.

## Routing and assembly

`proposed` is an installed route for review. `unresolved` means the saved routing
needs attention; geometry remains visible for complete electrical coverage. An
unsuccessful bounded route search does not prove that the physical route is
impossible. The manual routing report names actual mesh intersections separately.

The manifest lists every wire crossing between the base, cold core, front-top,
back-top and the pump cradle (`pump-cartridge`). The four J13 conductors run
from the board on the cold core to the motor tabs on the cradle.

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
the current physical meshes and earlier wires; `--retry` preserves saved routes
and searches unresolved ones. Its output needs the same route and assembly review
as hand-authored stations.

The current model has 98 proposed conductor routes and no unresolved routes.
Sixteen device-terminal locations remain unlocated. Native readback places every
wire with identical installed bounds. 88 of the 98 wires are valid single solids;
the other ten are cores of the reed-column and sensor-cable bundles. All 14
connector and insulation bodies are valid single solids. The compressor jacket
is a valid single solid with zero native overlap with its cores. Cores overlap
one another within the compressor cord, both reed columns and the sensor cable.

The full mesh review records 16 wire/body pairs and 339 wire/wire pairs. Eight
wire/body pairs are the four J13 conductors against `pump-contact-male` and
`pump-contact-female`, meshes in the reviewed assembly payload that the current
enclosure source does not build; the J13 conductors meet no other body and no
other wire. No jacket or fuse insulation interference appears in the mesh
reading. These are installed-geometry readings; closing motions and physical
harness dressing retain the scope described above.

The [compressor-cable review](installed/compressor-review.json) records no
hardware or neighboring-wire intersections for its jacket, three cores and
fuse-to-donor link. Its cores have zero native overlap with each other and with
the jacket. The fuse leads fit within the reference's available lead lengths.

The [WAGO arrangement review](installed/wago-arrangement-review.json) records nine
connectors: seven 221-413, one 221-415 and one 221-420. Reservoir A has a continuous
common from J6. The two west-wall commons each use all three ports of a 221-413.
The five power blocks run front to rear as +12 V, DC GND, PE, L and N.
Their 14 connections total 1718 mm with 64 modeled bends. The reservoir-A
common totals 293 mm. These figures describe installed conductor geometry;
bench cutting includes the termination and service allowances above.
