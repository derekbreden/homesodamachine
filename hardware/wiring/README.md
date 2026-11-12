# Installed enclosure wiring

The enclosure's electrical graph and selected installed geometry live together in
this model. Every insulated conductor has a stable ID, two named attachments, a
stock profile, an assembly owner and a routed centreline. Each distribution bus
is an explicit electrical interface.

- [Populated enclosure](../manifold-layout/enclosure-assembly.step): hardware,
  printed pieces, wiring, connector housings and fuse-splice insulation together.
- The wiring assembly on its own, `enclosure-wiring.step`, written with the resolved
  model when the wiring is materialized by hand.
- The resolved model, `enclosure-wiring.json`: terminal positions and directions,
  sources, nominal dimensions, connections, routes, lengths and service boundaries.
  The conductor worksheet, `enclosure-wiring.csv`: one row per physical conductor.
  Both are written when the wiring is materialized by hand
  ([Editing and materializing](#editing-and-materializing)), not by the assembly build.
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
20 mm side. The compressor earth runs in its jacket's PE core to port 3 of the
rear PE WAGO.
Final donor contacts remain unlocated beside the native power-cover envelope.

Exact compressor, fan, pump-motor, diaphragm-pump and display terminal details
remain unlocated. The carbonator's earth ring clamps directly to the existing
upper vessel rim. Its wire mouth and upward barrel share the rim attachment's
datums. The lead joins the shared west-side sensor riser above the vessel
plate and terminates in port 2 of the rear PE WAGO below C14.
Power-wire insulation
ODs and recovered heat-shrink dimensions are editable layout allowances. Those
allowances do not establish a reason to change the surrounding hardware.

The two temperature probes' bare leads and the carbonator reeds' leads terminate
at proposed insulated splice regions outside the coil. Their detailed bare-lead
dressing remains part of device integration. The reservoir columns carry four
signals and one continuous common, with insulated local taps. The carbonator's
reed pair also shares one common. Each reservoir column's common is a straight
spine beside the reeds, with short local soldered taps.

Reservoir A's five conductors rise vertically through the equipment lid's
aligned bore over the dry reed channel, with their turns above the lid.
Reservoir B's five conductors leave its dry channel through the fore side
window below the raised shell rim and rise outside the shell. Its four
signals terminate at J7, and its common terminates at `wago-reeds-b`. Below the
lid, four signals descend around the reed envelopes and the common runs beside
them. The temperature bus has one shared three-conductor path between probes.
The incoming V/DATA/GND leads feed the coil probe first, then continue to the
carbonator-wall probe. The coil-side route turns aft below the PRV vent at
world Z184, then rises at Y347 to the shared riser. Its tangential splice rows
are proposed harness joints; they do not specify the TO-92 package pin order.

Reservoir B's fore side window has a nominal 8 × 6 mm clear cable opening at
appliance Z227.4–233.4. Its self-supporting roof peaks at Z241.65, below the
Z245.85 shell rim. Mask the complete opening for the pour. Feed its individual
free wire ends
through the window before fitting their lid-side terminations. For column
service, free those conductors from their lid-side terminations and feed the
ends back through the window before lifting the column from its dry channel.
The column does not pass through the side window.

The shared west-side `sensor-cable` loom at world X−48/Y347 carries seven
conductors: the three temperature-bus leads, CLO, CHI, their continuous common
and the green 16 AWG carbonator PE lead. It follows an R5.5 transition below
the equipment lid to the Ø7.5 mm opening at world X−78/Y320/Z253.4. The
nominal packed loom envelope is 6.6 mm. The fixed east-side reeds retain
their positions; their three leads transfer over the open vessel head at
world Z225/Y352 to the west riser. Lay these free lead transitions while the
body is open, before the foam pour. Foam locates the loom below the lid.
Thread its free ends through the equipment lid before fitting the outside
terminations. Above the lid the signal looms follow the west PCB approach; PE runs aft and drops into the rear PE WAGO. The
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

The current wiring source is typed Rust and authored route data:

| Source | Responsibility |
| --- | --- |
| `tools/hsm/assembly-docs/src/wiring/graph.rs` | Conductor identities, nets, endpoints, shared buses and owners |
| `tools/hsm/assembly-docs/src/wiring/terminals.rs` | Pin maps, attachment positions, directions and fidelity |
| `installed/connector-map.json` | Fabricated board pin snapshot and its source bindings |
| `tools/hsm/assembly-docs/src/wiring/model.rs` | Stock profiles, rounded paths and modeled lengths |
| `tools/hsm/assembly-docs/src/wiring/routes.rs` / `installed/route-overrides.json` | Hardware-relative route families and authored stations |
| `installed/bundle-routes.json` / `tools/hsm/assembly-docs/src/wiring/bundles.rs` | Shared corridors, fanouts and jackets |
| `tools/hsm/assembly-docs/src/wiring/terminations.rs` | Housings, fuse leads and joint insulation |
| `../manifold-layout/installed-machine/wiring/sources.rs` | Current typed dimensions, placed hardware and fine-model measurements |

The [installed machine](../manifold-layout/installed_machine.rs) resolves the wiring
against its physical hardware and publishes the conductors, terminations and jackets
with the current machine. The print build publishes completed producers progressively.

The optional [native bench export](../../tools/hsm/wiring/README.md) writes the resolved
manifest, conductor worksheet, numeric recipe and standalone wiring geometry on request:

```sh
tools/run -- tools/hsm/target/release/hsm-wiring
```

It reads the normal build's retained placement and physical model and uses the same
native route calculations. The manifest names the physical model, numeric recipe,
producer binaries and written wiring by digest. `--output DIR` selects another bench
destination; `--numbers-only` exports the recipe and worksheet for inspection.

The tracked `connector-map.json` carries the fabricated board's pin positions and source
hashes. Refresh that snapshot alongside its PCB export. The normal machine reads the
tracked map and does not need an ignored circuit export.

Use the current published geometry for a focused design question:

```sh
node tools/find-part.mjs "wire"
hsm where wire-
```

The returned identities locate conductor bodies for `hsm gap`, `hsm overlap` or a saved
`tools/inspect-part.mjs` inspection. These run when the current question needs them.

The installed graph contains 100 conductor routes. Its twelve WAGOs comprise
ten 221-413 connectors and the two manifold commons, one 221-415 and one
221-420. Three 221-413 joins finish the compressor hot, compressor neutral and
pump-positive branches beneath the removable funnel frame. Each has two
populated ports and one unused port. Their separate pigtails preserve the
open-bench preparation and final through-opening connections.
The compressor hot and neutral joins sit side by side beneath the opening,
with neutral west of hot. The pump-positive join sits lower and east of them.

The front-going J1 leads pass below those free joins before rising into the
Z297.6 crossing above the drain stem and V-B inlet fitting. J2 and J9 use the
same crossing height below the funnel frame. The manifold leads descend into
their two fixed lid channels; the display ribbon retains the shared rear
electrical mouth and chimney. The faucet leads pass west of the pump head
and butterfly keys. The rear neutral WAGO stands upright west of the
continuous pump seat, with its wire mouths facing fore and levers facing east.
Load the rear junctions with back-top separated from the cold core. The diaphragm-pump leads follow the saddle's outside
aisles before turning toward the motor's aft lead exits.

Open the core junction levers with the V-B return disconnected.

For board service, remove the funnel and frame, release the three free joins
and lift them with their leads out of the housing paths. Disconnect the
V-B-to-Y-B return and cradled drain before withdrawing J11. The
[current housing sweeps](../mechanical-qualification/enclosure-above-core/connector-service-review.json)
retain J1/J2's 17 mm lift and 8 mm fore movement; J11 lifts 6 mm, moves
10 mm east and lifts another 20 mm, clearing the installed Reservoir B draw.
