# Bay harness study

The control topology contains 71 canonical conductor jobs for J1–J7, J9,
J11 and J13 plus device-end fanouts. J10's two power conductors belong to the
power module. J8 retains its native expansion wafer without an installed loom.
Every control job maps to an occupied grouped run or a named fixed continuation
in `controls-loom-interfaces.json`. J5 has four conductors until its device-end
fork tees the shared 5V and ground into the two relay modules.

`controls-candidate.json` carries 26 grouped control runs, 13 fixed counted
sections and 36 explicit connector/fanout working regions when its complete-count
check passes. `power-candidate.json` carries the 19 AC/DC/earth runs and three
explicit lower-bay lead exteriors. `compose.py` emits `candidate.json` only after
both complete modules and their occupied native pair check pass. Per-module
partial results retain `pass:false` and their missing routes or collisions.

## Occupied exteriors

Each signal conductor uses the inherited 1.7 mm exterior of the bought 22 AWG
silicone stock. A shared circular run reserves capacity for its actual count,
with 1.8 mm nominal packing pitch where applicable. Four wires reserve Ø4.3 mm;
seven reserve Ø5.5 mm; eight service wires reserve Ø6.4 mm in the accepted Ø6.8 mm
bores. Searched grouped-run centreline radii include the packing offset so the
innermost nominal wire centre has at least R3.4. Fixed grounding fanouts reserve
R3.4 at the shared exterior's centre; their individual constituent turns remain
unlocated. Every analytic circular sweep preserves its full section volume
along the path.

The reed-B service trunk includes a complete bare 14.3×1.7 mm eight-wire ribbon.
Its horizontal section at Z325.2 passes between the supply and controller.
Its retained 35 mm normal stem feeds the bare ribbon at X−32,Y205,Z298.05;
the long crossing column is X30.5, with 1.35 mm air to the ASSE carrier edge.
The reed-A lead leaves its unchanged bore through an explicit bare flattening
region, then follows a counted R6 round trunk. The nominal 35 mm normal clearance
reserve in the mount check screens the host; it is not an actual rigid lead or
a manufacturer minimum straight exit. Individual wire dressing at the bare
transition remains unlocated.

The inherited forward manifold corridor remains three bare 1.7 mm layers in a
5.1×8.5 mm section. Its 11 retained branches continue beneath the east bay floor,
with a complete-section R8 inward S starting at Y326. The aft run's axis is
X93.25 and its upward bend is at Y456.5, before the 7+4 counted exits. The
first 4 mm shares the named continuous dressing joint with the unchanged
forward corridor. Nominal lower-back and cold-core air are 0.204 and 0.200 mm;
printed fit and individual wire dressing remain unqualified. Changed source-valve
branches have their own complete routes to the actual native blade faces.
The seven-wire aft dressing face is at (100.3,460.2,284); the four-wire face
is at (94.7,460.2,276.5). Both face forward. Their independent native round
approaches retain the full bare forward ribbon.

Eight reservoir ground tails occupy one counted descent at
(−25.5,394.05), Z326.4..347.8. Distinct four-wire approaches from the A and B
junctions meet only in the named upper merger. The A crossover stands at
Z347.8/Y390.1 above the sensor working exits. Its lower fork separates the two
reservoir branches. The meter has three explicit bare wire approaches at its
measured pigtail root and a counted 2+1 dressing fork.

J1's seven-wire manifold branch leaves its native header through a bare
12.5×1.7 mm ribbon. Seven parallel X rows turn upward with R3.4 centre bends
before the aft gas crossing; its round loom dock is
(25.3,424.616,340.3). The actual header pins retain their locations. The
flattening and round-packing transitions remain nominal dressing regions.

J9's four-wire display branch uses a WEST-facing below-header dressing dock
at (−13,382.866,317.15). Its R4.7 WEST/FORE departure reaches the clear space
above the pump. The retained display passage remains at
(32,95.208,305.505); its counted approach continues aft and east before joining
the full loom. J13's four-wire cartridge branch uses a WEST-facing dressing
dock at (48.3,388.366,320). Its retained front passage remains at
(0,93.836,276.426). The exact ridge/frame chase reaches (90,122,301), then
turns down to Z286 and aft before joining the bay run. These fanouts preserve
all true header and fixed-passage pin locations.

J11's four-wire MQ6 branch uses a DOWN-facing nominal dressing dock at
(6.55,338.616,333.25). Its complete R4.7 departure reaches Z324.85, turns
fore to Y328.2 and descends to Z295.95. Its west return runs at
X−81.65,Z305.5 to Y384.31 before dropping outside the pump. The actual four
header pins retain their canonical locations;
their counted bare-wire fanout and constituent dressing remain nominal. The
MQ6 upper-bay approach at (−92.5,374,253.4) retains its separate lower-interface
scope.

The source-B positive branch leaves the retained common upward, then reaches
the native blade through a 2 mm normal straight and an R3.4 eastward turn before
the needle valve's fore face. The unlocated probe-ground service boundary is
reserved at (0,395,253.4); it represents an upper-bay cable approach and does
not specify a new cold-core hole.
Its single-conductor ground branch crosses at Z323.85, then follows an explicit
diagonal to the Z322.6 downward column at X−30,Y406. The actual junction mouth
and lower dressing face remain fixed. `controls-selected-routes.json` supplies
this complete R3.4 centreline.

The unlocated carbonator, probe and MQ6 lead continuations reserve only their
upper-bay approaches. Carbonator switch leads approach at
(−94.7,408.55,253.4), their paired grounds at (−80.7,408.55,253.4), probe
signal/supply at (−88,396,253.4), and the four MQ6 conductors at
(−92.5,374,253.4). All approach upward and then turn forward in the clear
west bay. These locations do not locate a donor cable, create a cold-core
hole, or establish the actual retained lower cable exit.

These are bare conductor and nominal packing exteriors. Braided sleeve fit,
individual fanout bends and finished harness retention remain separate from
the occupied CAD proof. The native purchased wafers, valve blade faces and
relay representative working faces remain visible beside the nominal dressing
regions. The inherited 11.65 mm board contact allowance locates the free-wire
plane; it does not establish a newly measured mating-housing or crimp fit.

## Geometric proof

The search raster ranks possible travel. A route is admitted only after its
complete native occupied exterior clears hardware, existing power/control runs,
other endpoint leads and junction lever working regions. Native commons use
0.0001 mm fuzzy tolerance and 1e−9 volume integration tolerance. The 49 static
control regions have a separate pair check; only named physically continuous
joins are exempted.
Each grouped pipe is emitted as its exact native cylinder and arc members.
The admission check tests those physical members against every hard body,
occupied wire and full fluid exterior before saving the scene packet. Every
shared section face has the same centre, diameter and tangent;
the members have zero internal overlap and preserve the complete authored
path length and circular-section volume. Their enlarged clearance members
form one valid native union, with zero missing physical-member volume in
every containment cut. Per-solid native checks cover the complete occupied
wire, including each shared section seam.
`control-terminal-owner-check.json` independently checks each main run against
its own nominal dressing regions and actual purchased endpoint bodies. Only
the unique first or last straight member aligned with the terminal normal may
engage the purchased owner. Named bare fanout joins can also meet the immediate
arc sharing that straight member's section, or the arc tangent at the dressing
mouth. The receipt records their exact overlap bounds and section adjacency;
every later return remains occupied against both owner types.
Full tube, braided-hose and insulation exteriors require at least 1 mm unrelated
air. Native enlarged fluid obstacles guide the searches; the final complete
occupied controls are independently measured against the received physical
fluid solids in `control-fluid-air-check.json`.

Forward shell stock through Y325.7 is a hard obstacle. Display and cartridge
looms land at their actual retained native passages. The protected nameplate
receiver and backing remain hard obstacles even where the aft shell admits
local wiring recesses. Each emitted aft clearance cutter grows the occupied
exterior by 1 mm. Width/roof centre limits preserve at least 3 mm exterior stock;
the parent integrated audit checks the finished shells and complete factory
motions separately.
The controller reed-A departure preserves its +X terminal normal, then turns
upward to Z340.3, aft and east around the adjacent cartridge-header approach.
`controls-selected-departures.json` supplies its explicit R4.7 docking paths.
All dock choices face the complete native obstacles; a completed route occupies
its selected full exterior and releases unused search alternatives.
The rear roof hatch follows the same admitted recess rule. Its hardware and
mounting bridges remain hard obstacles; completed loom cutters are applied
to the actual hatch stock with the same retained outer stock requirement.

`bench_cut_review` compares the inherited bench cuts with each authored shared
run and the board's contact allowance. Its remaining value precedes fanout
dressing, fixed continuations, hidden termination insertion and service
allowance. It is not a finished-harness cut length or a claim that an existing
donor cable reaches. The stock-spool make-up and continuity procedure remains
in [cable assemblies](../../../hardware/assembly/cable-assemblies.md).

## Factory front handling

The display, gasket, cover and J9 wiring are installed after the front-top and
frame complete their 102.2 mm closing stroke. The J13 contact solder joints are
prepared on the loose, unpowered front-top at the retained EN-10 bench stage.
Its contact-side fanout stays on that article; its board dressing end remains
free during closure. The board-side J13 fanout and both J9 fanouts are absent
from this factory state.

`front_loom_handling.py` emits the temporary J13 arrangement and its independent
`front-loom-handling.json` receipt. It preserves all 537.199 mm of the modeled
four-conductor grouped run, Ø4.3 mm with R4.7 centre bends. The free board end
passes through the existing Ø14.7 mm display passage and the empty display
pocket. The complete parked article follows one rigid translation with
front-top. A containing prism or a native-distance interval bound proves
clearance over the whole stroke against every fixed body; the retained contact
normal and complete physical section remain unchanged. This arrangement does
not replace either installed J9/J13 route.

The ground hook feed is already dressed and the rear roof hatch stays seated.
The silicone funnel and display remain out for subsequent J13 make-up and J9
installation through those open apertures. Final manual dressing, XH insertion
and retention have no tool-access or manipulation qualification in this
receipt. The temporary run's native minimum front-shell air is 0.043 mm inside
the retained chase, with 0.802 mm to the frame; printed tolerance and workholding
remain unqualified. The grouped-run length excludes individual termination and
service dressing, so it does not establish a finished stock cut or reach from
the inherited 350 mm DC-5 bench blank.

## Interface scope

Actual valve blade local-X identity does not establish diode polarity.
Keystone IDC clamp pitch, WAGO metal-clamp centres, relay clamp make-up,
carbonator/probe exits, the dry moisture comparator and lower refrigeration
terminations retain their named nominal reservations. The measured meter root
does not locate its flexible lead order or length. Sleeve fit, terminal
retention, mains insulation, earth continuity, thermal output, vibration and
lifetime are not established by these native checks.

## Rebuild

Use `controls.py --inventory-only`, `controls_j13_passage.py`,
`funnel/underframe_reliefs.py`, `controls_core_boundaries.py` and
`controls_escape_leads.py`, then `controls_looms.py --reserves-only`, `--fanouts-only` and
`check_static_controls.py`. `probe_loom_docks.py` checks complete endpoint lead
options before searching. After the physical fluid package and 19 power runs
are frozen, run `controls_looms.py`; `--resume-failed` reuses only routes whose
native files, endpoints and current clearances still pass. Run `compose.py`
after both complete modules pass, then the parent integrated native audit,
shell-stock reconstruction and factory motion proof.
Run `check_static_controls.py`, `check_control_terminal_owners.py` and
`check_control_fluid_air.py` against the
frozen published exteriors. The complete controls report and these checks bind
actual native file hashes, source code and consumed manifests at execution,
and reject changes made during the checks.
Run `front_loom_handling.py` after the parent stock is frozen, then the parent
front-closing checker and factory viewer against its named occupancy classes.

For a final evidence refresh, use `--received-statics` with both static modes
and `--resume-failed --received-cutters` for the full packet. This checks the
received fixed regions against the current native analytic recipe and preserves
all 75 occupied bodies and 75 clearance cutters byte for byte. Each frozen
cutter must match the complete native supports, real trimmed boundary curves,
wire loops and solid ownership of its 1 mm enlargement recipe. The receipt
checks the same actual physical members against the current parent hardware
and refuses to replace a route or cutter that fails. It records the 150 native
hashes before and after validation; no native file is written in this mode.
