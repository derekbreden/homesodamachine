# Installed enclosure wiring

The enclosure's electrical graph and proposed installed geometry live together in
this model. Every insulated conductor has a stable ID, two named attachments, a
stock profile, an assembly owner and a routed centreline. The four separable pump
contacts and each distribution bus are explicit electrical interfaces.

- [Populated enclosure](../manifold-layout/enclosure-assembly.step): hardware,
  printed pieces, wiring, connector housings and pogo-joint insulation together.
- [Wiring assembly](enclosure-wiring.step): the same installed wiring on its own.
- [Resolved model](enclosure-wiring.json): terminal positions and directions,
  sources, nominal dimensions, connections, routes, lengths and service boundaries.
- [Conductor worksheet](enclosure-wiring.csv): one row per physical conductor.
- [Routing review](installed/routing-review.json): manually requested interference,
  native-solid and integration readings, bound to their actual artifact hashes.
- [Integration record](installed/integration-review.json): wiring subassembly and
  retained physical assembly scope.
- [Inspection overview](installed/enclosure-wiring-overview.png): the complete
  wiring and a closer front-assembly view, with unresolved routes dashed red.

The model covers the AC inlet, PSU, compressor/fuse lead, earth bonds, 12 V
distribution, diaphragm pump, all eleven valves, condenser fan, both pump-contact
halves, both pump motors, rear faucet jack, enclosure display, gas sensor, two
temperature probes and all ten reeds. The external line cord and the faucet's
outboard umbilical end at their enclosure interfaces. J2 OUT4, J4 IO23/IO27 and
the I2C expansion header have no installed cable.

## Attachments and fidelity

`modeled` means a location follows the existing native part geometry. It is not a
physical acceptance. `nominal` marks a layout dimension or proposed solder-joint
region. `unlocated` keeps a required electrical connection whose precise device
terminal is absent from the reference model. These states are separate from the
route's status.

Valve attachments use the separate native metal spades. G/J's proposed wire exit
is aft from the tab engagement region; the tabs and disconnects can bend. The
model imposes no rigid Faston boot box. Board pin identities and physical XY
positions come from the fabricated `pcba.circuit.json`, carried through the native
board pose. J10's side wire entries are separate from the screw-head direction.
The tilted display and vertical pump motors retain their own reference frames.

The ten XH housings use nominal dimensions from the
[JST XH drawing](https://www.jst-mfg.com/product/pdf/eng/eXH.pdf): 2.5 mm pitch,
5.7 mm depth, 7.5 mm housing height and 9.8 mm assembled height above the board.
Their outer profiles and wire throats are layout envelopes; latch details and the
on-hand copies' fit are unmeasured. Each pogo solder exit has its own proposed
heat-shrink sleeve.

The compressor's three conductors share one jacket corridor and a separate
annular jacket solid. Its 8 mm outside diameter is a proposed layout allowance,
with an editable common route and distinct core offsets. End fanouts and final
donor terminations remain proposed.

Exact compressor, fan, pump-motor, diaphragm-pump and display terminal details,
and the carbonator's metal bond landing remain unlocated. Power-wire insulation
ODs and recovered heat-shrink dimensions are editable layout allowances. Those
allowances do not establish a reason to change the surrounding hardware.

The two temperature probes' bare leads and the carbonator reeds' leads terminate
at proposed insulated splice regions outside the coil. Their detailed bare-lead
dressing remains part of device integration. The reservoir columns carry four
signals and one continuous common, with insulated local taps. The carbonator's
reed pair also shares one common.

## Routing and assembly

`proposed` is an installed route for review. `unresolved` means the saved routing
needs attention; geometry remains visible for complete electrical coverage. An
unsuccessful bounded route search does not prove that the physical route is
impossible. The manual routing report names actual mesh intersections separately.

The fixed J13 lead belongs to the enclosure. Its cartridge-side counterpart and
four motor leads leave with the pump cartridge. The manifest lists every wire
crossing between the base, cold core, front-top, back-top and cartridge. Electrical
continuity through the magnetic pair is represented by the four mating-contact
records, rather than by permanent wires across the service joint.

A drawn route does not establish that the dressed harness permits every enclosure
closing or removal motion. Terminal access, actual ribbon web/branch dressing,
sleeve fit and service slack remain assembly details. Centreline lengths exclude
hidden termination insertion and a final cut allowance; the CSV is not a cut list.
The mechanical assembly scorecard retains its mechanical scope. Wiring review is
the separate, manually invoked reading linked above.

## Editing and materializing

The editable source is under [`installed/`](installed/):

| Source | Responsibility |
| --- | --- |
| `connections.py` | Conductor IDs, nets, logical endpoints, common buses, separable contacts and owners |
| `terminals.py` | Reference geometry, pin map, attachment location/direction and fidelity |
| `connector-map.json` | Tracked snapshot of fabricated board pins, source hashes and the J10 component envelope |
| `model.py` | Stock profiles, tangent circular bends, native wire construction and lengths |
| `routes.py` | Hardware-relative route families and override interpretation |
| `route-overrides.json` | Individually editable hardware-relative stations and unresolved routing records |
| `bundle-routes.json` / `bundles.py` | Shared jacket corridor, core placement and jacket geometry |
| `terminations.py` | Removable housing and solder-exit insulation envelopes |
| `build.py` | Native wiring assembly, manifest, worksheet and enclosure integration |

Rebuild the wiring against the current populated native enclosure:

```sh
tools/cad-venv/bin/python hardware/wiring/installed/build.py
```

The normal `enclosure_assembly.py` composition includes the same wiring model.
The wiring-only materializer replaces its own marked STEP subassembly and viewer
meshes; existing physical component records and meshes are retained. Native and
viewer outputs use the same `wire-<ID>` and `terminal-<ID>` names. For example,
`wire-J13-AM2` is the fixed AM2 conductor in both assemblies and in the worksheet.

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

The current model has 103 conductor runs. The linked mesh review identifies
169 wire/body interference pairs across 33 conductors, plus 69 wire/wire pairs.
Those 33 conductors carry unresolved routing status; the other 70 remain proposed.
Sixteen device-terminal locations remain unlocated. The review's native readback
finds all 103 wires valid, each a single solid, with identical installed bounds.
The ten connector housings, eight pogo sleeves and common compressor jacket are
also valid native solids. The jacket has no native overlap with its three cores.
