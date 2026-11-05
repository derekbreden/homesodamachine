//! Module docstrings, as each module's `__doc__` reports them.

pub const FACTS: Option<&str> = Some(r#"What one build knows, written down so the readers do not each build it again.

    tools/cad-venv/bin/python hardware/scripts/_facts.py            # exit 2 if it moved
    tools/cad-venv/bin/python hardware/scripts/_facts.py selftest

    import _facts
    f = _facts.read()
    f.box.outer                      # the Box, field for field
    f.runs                           # the drawn runs, measured
    f.check("clearance-floor").status

THE DOC DRIVERS WANT NUMBERS, NOT SOLIDS. Of the figures they substitute, the overwhelming
majority is arithmetic over module constants and needs no geometry at all; the rest is what
this file adds — the `Box` the walls are cut from, the wall bores, the printed pieces' own
boxes, a named face, a carried point, the drawn runs, and a few exact distances between
declared pairs. `enclosure-assembly.scorecard.json` is beside it for a driver that wants a
check's own verdict.

So a driver reads two files and stands no machine. `enclosure-assembly.scorecard.json` is
written by the assembly's own run; this artifact is written beside it.

THE CARD RIDES WITH THE VALUES. `card` names what `enclosure-assembly.scorecard.json` measured
at the moment this was written beside it, so a reader holding both can tell whether they came
off the same machine without importing the CAD.

AND THE TREE RIDES WITH THE RUN. `card` and `step` hold the three artifacts to one run; nothing
in them holds that run to this tree, and a stale triple agrees with itself perfectly. `sources`
is the third digest — every file `tools/bazel/graph.json` traced the generator opening that no
generator writes — so a reading taken off a machine that has since moved says so instead of
reading green.
"#);
pub const GAS_CHAIN: Option<&str> = Some(r#"External adapter envelopes and tube mouths on the warm CO2 chain.

WR1110 and the downstream GASHER check each run female 1/4-inch NPT in and male 1/4-inch NPT
out, and gray acetal John Guest fittings take every end onto 1/4-inch tube: a PI010822S male
connector threads into each female socket, and a PI450822S female adapter onto each male stub.
The PI010822S uses the existing nominal 1/4-inch PTC reference dimensions. The PI450822S is the
PP450822E's form in gray acetal and takes the nominal sections the SeaFlo discharge chain draws
for that adapter. Measure the made-up fittings before accepting this layout for assembly.
"#);
pub const LINES: Option<&str> = Some(r#"The enclosure assembly's tube runs — every line between two placed bodies, authored port to port.

The manifold's own 21 segments are drawn by `manifold_layout.py`, which knows its butt joints
and its lower returns. This module is for the runs BETWEEN sub-assemblies: a mouth on one placed body
to a mouth on another, through whatever the pack leaves between them.

Each run is one `R.bent(...)` — the source port, hand-placed interior waypoints, the destination
port — swept at the port's own bore. `_routing` seats the largest arc each corner's two legs
allow and records the shortfall of any that cannot: a run drawn past its stock's floor is still
drawn, and `BLOCKED` says by how much.

A RUN ARRIVES WITH THE BODIES IT JOINS. Both of its mouths have to be placed before it can be
authored, so the set here grows as `enclosure_assembly.build_pack` grows, and a run with one end in
the pack and the other nowhere is not written down as a guess. `build_seated_runs` is the same rule
one step later: the box is sized on the pack, so a body seated in one of its WALLS is placed after
it, and the lines reaching those bodies are drawn once the box exists.

Frames come off the placed pack, so a run rides a move of its parts: change a pose in
`enclosure_assembly.py` and every waypoint measured off that body's ports moves with it.

Where a piece of a run can stand is read by sweeping it —
[`probe.World.reroute`](/hardware/scripts/probe.py) slides named waypoints across a range of
offsets, redraws the run at each one, and reports what it collides with there, the bands that
are clear, and the radius each corner has left:

    tools/cad-venv/bin/python hardware/scripts/probe.py route fluid-14
    tools/cad-venv/bin/python hardware/scripts/probe.py reroute fluid-14 3-4 y- 0:80:2.5

A bend, a fall, a crossing, a leg — whatever the piece is called it is some waypoints of the
route, and those indices are the handle (`route` numbers them, `--near x,y,z` says which index
a pick off the STEP is). The centreline is what moves; the ribs struck on the run, the cap's
seat for it and the stretch it is graded on stand where they stand, and each sweep prints them.

Run it through the assembly:
    tools/cad-venv/bin/python hardware/manifold-layout/enclosure_assembly.py
"#);
pub const MACHINE: Option<&str> = Some(r#"The machine scene, scalar document and Rust fine-model export interface.

The scene holds world-placed bodies, runs, frames, Box data and check readings.
`machine()` reads a current scene or runs the Rust assembly driver before reading it.
"#);
pub const MACHINE_CHECKS: Option<&str> = Some(r#"Plain-data adapter to the machine's Rust fit, clearance and drain reader.

The physical model is immutable. Placement provides scalar construction ledgers
and explicit installed frames; Rust owns geometry import, tools and decisions.
"#);
pub const MACHINE_EQUIPMENT: Option<&str> = Some(r#"Compatibility interfaces for Rust's equipment dimensions, placements and tube recipes.

Python resolves the existing scalar providers and model files for callers that still
import this module. Rust computes the construction recipe and installed port frames.
"#);
pub const MACHINE_EXPORT: Option<&str> = Some(r#"File-reference model and presentation export through the Rust machine program.

The inputs are ordered fine-model selections and explicit installed frames. Python
passes metadata; the program streams physical arrays, prepares presentations and
writes STEP, viewer payloads and GLBs without constructing Python geometry objects.
"#);
pub const MACHINE_LAYOUT: Option<&str> = Some(r#"Numeric installation inputs for the machine's Rust placement program.

The inputs are current part models and authored scalar datums. A plan carries ordered
references and installed frames, with no CadQuery, OCP or meshcad geometry in Python.
"#);
pub const MACHINE_REPORTING: Option<&str> = Some(r#"Scalar wiring context and reports from the machine's Rust reference plan."#);
pub const MACHINE_ROUTES: Option<&str> = Some(r#"Scalar requests for Rust's installed warm-tube and insulation geometry."#);
pub const SCORECARD: Option<&str> = Some(r#"The enclosure assembly's requirements as a single pass/fail scorecard — the one place the
arrangement's rules are enumerated as executable checks, computed from the placed geometry
the pack already builds. Printed at the tail of every `enclosure_assembly.py` run and written
beside the STEP as `enclosure-assembly.scorecard.json`, which the 3D viewer's bottom bar reads
([`web/contracts/scorecard-sidecar.js`](/web/contracts/scorecard-sidecar.js)).

Two kinds of check:

  - GATE — a requirement that must hold for the machine as it stands to be built.
  - GOAL — a reading the card takes and does not gate on, carried as a `score` (0..100).

Two readings are exact queries against the solids, rather than their boxes, and that
is most of what the run costs. `pack-closes` asks what two bodies share, and `clearance-floor`
how far apart they stand. A box appears in each only as a prefilter: two boxes that miss are two
solids that miss, and two boxes that overlap say nothing at all.

Every check's detail is printed to `DETAIL_MAX` rows and carried whole in the sidecar, so a
list ending in "… n more" is a terminal cap and never the end of the finding.

Run it through the assembly:
    tools/cad-venv/bin/python hardware/manifold-layout/enclosure_assembly.py

The need figure's own controls, against known-answer geometry:
    tools/cad-venv/bin/python hardware/manifold-layout/_scorecard.py selftest
"#);
pub const STATED_BOUNDS: Option<&str> = Some(r#"_stated_bounds — the bounds a module states about its own constants, read at import.

A generator's constants carry claims about each other: a screw is long enough for its insert, a
band is wide enough for the bore it carries. Those
claims are settled the moment the module is read, before any solid exists — so they have no
assembly to hang a reading on and no build to be measured during. This is the ledger they record
into instead. `enclosure_assembly.carry_stated_bounds` drains it onto the assembly beside the
bounds the machine measures at every build, and `_scorecard._bounds` renders one gate row apiece.

A VIOLATED BOUND IS A THING TO LOOK AT, and what a reader looks at is the STEP, the three
elevations and the scorecard a run writes. A guard that raises at import destroys all four
before the build starts, leaving the only account of the fault in a terminal nobody commits.
So a bound here never stops the module: the constants stand as written, the geometry comes out
as those constants describe it, and the fault is a red row on the committed card carrying the
message the bound wrote — beside the clashes and the open leads the same geometry produces in
`pack-closes` and the rest. Two bodies packed nearer than they are wide come out overlapping,
which the card can show a volume and a location for; a raise can only say so.

An `assert` is the same fault twice over, because `python -O` strips it: build-killing under
one interpreter and absent under another, which is the pair of failure modes a check must not
have. A bound recorded here reads the same either way.

Two entry points, both thin:

    _bounds.state("id", "label", "target", ok, "what went wrong")

for a bound with one reading, and

    room = _bounds.bound("id", "label", "target")
    for name in stations:
        room(clear(name) >= gap, f"{name} stands {clear(name):.2f} mm off its neighbour")

for a bound stated once over a population — one card row, its value the tally, its detail the
notes the failing readings wrote. Both hand back the reading, so a caller whose next line
cannot run on a violated bound can branch on it rather than proceeding into a lookup that
is not there.
"#);
pub const TUBE_EXPORT: Option<&str> = Some(r#"Scalar route stations, ports, anchors and materials for the assembly handoff."#);
pub const ABOVE_CORE_BOM: Option<&str> = Some(r#"Selected above-core fitting names without native CAD imports."#);
pub const ABOVE_CORE_PARTS: Option<&str> = Some(r#"Reference frames, port stations and tube routes in the above-core arrangement.

Purchased references remain exterior layout geometry. The ASSE's straight TPU
cuffs are fit candidates; their displayed installed sections do not establish
sealing, retention or pressure capacity. Tube insertions retain the named
estimates in ``above-core.json``.
"#);
pub const ABOVE_CORE_WIRING: Option<&str> = Some(r#"Electrical junctions placed at their actual branches in the above-core layout.

All component and feature shapes use enclosure-world millimetres. Junctions
follow their named back-top, front-top or cold-core mounting parent.
``cap_features`` supplies stock and cutters for the core lid;
``shell_features`` supplies the features for a named enclosure quadrant.
"#);
pub const CHECK_ASSE_DRAIN: Option<&str> = Some(r#"Read the dedicated ASSE drain against the actual installed appliance bodies.

Read the explicitly bound physical fine model and the exact casing model in its
installed frame. The normal caller excludes wiring; the standalone installed
reader includes it under the existing tube exclusions. Connections share material
by design. This is nominal geometry evidence, not vent-flow qualification.
"#);
pub const ENCLOSURE_ASSEMBLY: Option<&str> = Some(r#"Rust machine assembly entry point and scalar construction questions."#);
pub const MANIFOLD_LAYOUT: Option<&str> = Some(r#"Two-channel flavor manifold with a purchased PP0208E tee on each pump port.

Each pump tee stands behind front-top's collet plate, its branch on the pump tube and its
run upright (`fixed_returns`). The fore valve stands over the run on one short tube; a lower
return, a stem elbow in each collet and one straight tube, joins the run's lower port to the rear
valve's bottom port. Each tee's branch collet stands extended in its recess and grips its pump
tube.

Authoring frame: X spans the two channels; +Y becomes enclosure +Z; +Z becomes
enclosure +Y. The pump station retains its fitted physical datum. The fore
valves keep their height and stand over their tees' run axes; the rear row stands 8 mm over
its deck reference. The two source turns
retain their own construction independently of the pump-port connections.
"#);
pub const REAR_PLUMBING: Option<&str> = Some(r#"Rear inlet header, pump joints and integral snap seats in appliance coordinates.

Purchased profiles retain their own reference frames. The shared production
specification places every fitting and defines the short flexible pump joints;
no exploratory assembly or exported study is a build input.
"#);
pub const REAR_SNAPS: Option<&str> = Some(r#"The seats on back-top that the ASSE chain, the Pisco and the flow meter slide into, and the snap
caps that hold each in its seat.

Back-top is inverted on the bench. Each part drops into its seat SLIDE ahead of its station and
slides aft until its nose is through the rear wall; the meter slides aft onto the soda union's
stub. A seat is one block, the part's upper side cut into it, swept forward by SLIDE so the part
passes every station on its way. A snap cap then holds the part's other side at its station: one
half pipe under the part, its two side walls rising past the part's axis as the springs, each
hooking over a ledge in a pocket in the seat's flank. Each pocket's ends are the cap's end
shoulders. The ASSE's seat stands down to the body's axis, through its wrenches' side corners, and
its cap is the lower half of a hex pipe about them, so the two hold the wrenches' flats. The ASSE's
and the Pisco's caps go on from below. The meter's is the same snap turned a quarter about Y and
goes on from the west.

World frame: -Y fore, +Z up, +X east.
"#);
