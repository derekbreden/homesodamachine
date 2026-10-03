# Funnel mold

Two PETG shells follow the [funnel](../funnel/README.md), with
[5 mm](SKIN) minimum ramp backing and [5 mm](FLANGE) clamping flanges. The cavity
stands on three small feet. The core has a [142.4 × 95.1 mm](DRY_MOUTH) rounded rectangular opening
in its dry back. Both halves print with automatic normal supports in Snug style.
The shells and a separate contoured PETG mandrel form the complete
[funnel](../funnel/README.md): its rectangular block, flat bearing face,
8.4 mm entry, 6.7 mm relief and 6.0 mm sealing land. The mandrel's
[raw print](forming-mandrel.step) reserves 0.05 mm of normal finishing growth;
the [finished reference](forming-mandrel-finished.step) defines its measured
wet profile. Casting with that profile is geometrically complete. Finishing,
release and casting remain physical checks.

![Cavity and core in their print orientations](overview.png)

Eight [5 mm](BOLT_D) through-holes take M4 × 20 bolts, 9 mm OD washers and nuts.
Small clamps can also reach the flat flange backs. Tighten opposite stations
incrementally until the bare parting lands meet. The two short locating pegs
are [3 mm](LOCATOR_HEIGHT) tall, with [0.60 mm](LOCATOR_CLEARANCE) radial
clearance; one mating hole is slotted in X to accommodate spacing error.
Their asymmetric positions set the drain's orientation. Four edge notches
admit a blunt opening tool.

![Open dry backs; the cavity's feet and the core's rod cradle](backs.png)

## Forming surfaces and fit

The nominal silicone ramp, brim and collar are 6 mm thick. Ramp thickness is
measured perpendicular to its surface, with a locally thicker rounded throat.
[Wall measurements](../funnel/wall-review.json) record the geometry.

Both forming faces reserve [0.30 mm](FINISH) of net finishing growth, including
primer, sealer and release. Sand and coat a sample with the actual finishing
stack, then measure its net growth. Mask the parting lands, locating pegs and
holes, clamp holes, mandrel passage, V cradle and axial stop. The finishing allowance belongs to
the silicone-forming surfaces; the bare lands establish closure height.

The [50.8 mm](ROD_LEN) mandrel's [6.35 mm](ROD_D) dry shank passes through an
[8.35 mm](ROD_GUIDE_D) opening, with [2 mm](ROD_CLEARANCE) diametral clearance.
An open V cradle on the dry back centres the shank. Its upper end meets a visible
stop; two zip ties in [4.4 mm](ROD_TIE_WIDTH) grooves hold it in the cradle.
Engagement is [38.0 mm](ROD_ENGAGEMENT), leaving [12.7648 mm](ROD_EXPOSED) below the
core's neck. Its lower end drops into an [11 mm](SOCKET_D) socket in the cavity floor,
[3 mm](SOCKET_DEPTH) deep below the block's bottom face, and stands
[1.5 mm](ROD_END_DEPTH) into it, so the bore opens through that face. The pilot touches
neither shell as the mold closes; the dry shank seats against the V and stop.

Pack a small removable seal around the mandrel at the forming-face entry, flush
with the adjacent surface. The illustrated seal is [2 mm](ROD_SEAL_DEPTH) deep.
Prove the mold-sealing clay's compatibility with the actual
[platinum-cure silicone](silicone.md) on a sample before using it in the mold.
The cradle holds the mandrel; the seal
closes the annular passage into the dry back. Smooth-On's
[sealer reference](https://www.smooth-on.com/page/sealers-releases/) distinguishes
sulfur-free modeling clay from sulfur-bearing clay for platinum silicone.

The block is [36 × 41 mm](PLUG_BLANK), its walls running into the bowl's
underside. Its complete staged bore is formed by the mandrel. Silicone that
runs into the socket around the pilot leaves a sacrificial collar. Peel the
casting and mandrel from the cavity, then trim that collar flush with the block
bottom **before** withdrawing the 8.4 mm entry through it.

| Wet feature | Raw tool | Finished tool |
| --- | --- | --- |
| Entry | 0.05 mm normal reserve on the lead and shoulder | 8.4 mm entry; 1.8 mm lead to 6.7 mm |
| Relief | 6.6 mm diameter × 0.164821 mm axial length | 6.7 mm diameter × 0.214821 mm axial length |
| Sealing land | 5.9 mm diameter × 3.0 mm axial length | 6.0 mm diameter × 3.0 mm axial length |
| Upper throat | 6.25 mm diameter on its reserved cylindrical zone | 6.35 mm diameter |

The [tool dimensions](forming-mandrel-design.json) identify the actual native
axial trims and the two bare zones: the pilot's first millimetre and the dry
shank from print Z15.764821 to Z50.8. Mask those zones. The shell's 0.30 mm
finishing reserve applies to its own forming faces. The mandrel uses the
separate 0.05 mm reserve, measured over its complete wet boundary in the
[native tool check](forming-mandrel-check.json).

Finish a witness using the actual PETG, abrasion, sealer and release stack,
and measure its net growth with the recorded caliper. Finish the mandrel to
the reference profile, checking the entry, relief, land and both transition
edges. Keep the relief open and the 3 mm land cylindrical. A coating thickness
assumption does not establish those dimensions; inspect the thin relief under
magnification and check its axial extent against the reference. The acquired
acrylic sealer, release spray and silicone are listed in the
[purchases ledger](../../../ledger/purchases.md). Their compatibility and
adhesion on this small tool need a same-stack cure and release sample.
Smooth-On's [sealer guidance](https://www.smooth-on.com/support/faq/101/)
describes acrylic sealing and compatibility checks for printed mould surfaces.

![Finished mandrel's entry, relief and sealing land, in its print datum](forming-mandrel-detail.png)

[design.json](design.json) checks the finished tool at simultaneous
[0.5 mm](ROD_OFFSET) lateral offset, [1°](ROD_TILT) tilt and axial error in eight
directions, for 72 poses. Its end may stand [0.1 mm](ROD_EXTRA) deeper or
[0.1 mm](ROD_AXIAL) shallower than nominal. Every pose clears the complete cavity
by at least [0.66 mm](ROD_MIN_SOCKET), and the whole pilot end remains at least
[1.34 mm](ROD_MIN_END) below the block's bottom. These are tool-specific clearance
limits. Seat the bare shank in the V and against its stop, then confirm nominal
alignment before closing; the screen does not qualify a displaced wet profile,
tie retention or sealing.

![Contoured mandrel held by the open core cradle, with its pilot in the cavity's socket](rod-detail.png)

![Section through the assembled forming shells, finished funnel and contoured mandrel](section.png)

Teal is the cavity, gold the core, grey the nominal silicone, light grey the
finished mandrel and blue the removable entry seal. The nominal casting is
[219 mL](CAST_VOLUME). The two halves fit inside a [278.5 mm](ENVELOPE) circle,
leaving [10.6 mm](CHAMBER_GAP) radial clearance in the recorded chamber. Check
the actual opening, clamp/bolt envelope and catch tray before pouring.

## Load and vacuum

The complete mold sits inside the vacuum chamber. Its fill hole, five casting
vents and both dry backs communicate with that chamber.
Pressure equalizes through these openings; the silicone's weight remains a
load on the forming skins. Keep the passages open, evacuate and vent slowly,
and perform any filled-mold cycle while the silicone is fluid. Cure at ambient
pressure with the flanges held together. The tooling is not rated for a sealed
one-atmosphere differential or pressure injection.

[design.json](design.json) records a sizing calculation: a simply supported
[165 mm](LOAD_SPAN) flat square, [5 mm](SKIN) thick, under a uniform
[1.00 kPa](LOAD_PRESSURE), using an assumed PETG modulus of
[1000 MPa](LOAD_MODULUS) and Poisson ratio 0.4. Its calculated deflection is
[0.243 mm](LOAD_DEFLECTION); the maximum static silicone head is
[0.598 kPa](HEAD_PRESSURE). This flat-plate model is a screening approximation;
it does not establish the printed shell's stiffness, creep, release force or
transient pressure during degassing.

The solid mandrel has at least 5.9 mm stock across the sealing land. A separate
equalized-head cantilever screen in
[forming-mandrel-check.json](forming-mandrel-check.json) gives 0.00284 mm tip
deflection and 0.0646 MPa maximum bending stress at the 0.598 kPa static head,
using an assumed 1000 MPa room-temperature PETG modulus. It does not qualify
release force, coating adhesion, creep or lifetime.

Bambu reports PETG Translucent bending moduli of 1610 MPa in XY and 1520 MPa in
Z on conditioned test specimens. The sizing assumption is lower; the actual
print still needs its own dry-fit and vacuum trial.
[Material data sheet](https://store.bblcdn.eu/s8/default/71ca815e70e74afc96ff5883f003235f/Bambu_PETG_Translucent_Technical_Data_Sheet.pdf).

## Geometry verification

The cavity is a continuous cup from the brim to the block's floor and its blind
pilot socket. Each offset
face, rounded edge and corner is contained in the finished shell envelope.
Before the flange and mouth trim, the minimum distance between the complete
forming and backing boundaries is checked against the 5 mm shell thickness;
[design.json](design.json) records that measurement.
The dry backing includes the forming ramp's 0.01 mm rounded-join allowance.
The core's 0.30 mm brim-finishing recess leaves 4.70 mm behind that pocket;
the surrounding bare flange remains 5 mm thick.
The generator checks that the capped cavity and the assembled mold each retain
the complete casting in one enclosed liquid region, separate from outside air.
The assembled check uses the modeled rod-entry seal and caps the fill and vent
mouths.

[containment-review.json](containment-review.json) records independent checks of
the STEP and STL identified by its file hashes. These checks use the
complete surfaces and the whole casting, including openings smaller than a print
layer. The assembled STEP uses the exact entry seal; the assembled STL gives
that soft seal 0.02 mm contact overlap along each axis at the independently
tessellated surfaces. Coating
porosity, flange sealing and the first casting remain physical checks.

[forming-mandrel-check.json](forming-mandrel-check.json) independently derives
the complete casting from the whole forming envelope, bowl core and contoured
tool. Its complete native solid differences against the current funnel are
0/0 mm³, including all block, ramp, brim and collar stock. Both shell STEP/STL
files and their print payloads remain byte-exact and bound to that record.
The [physical evidence](print-log.md) retains its measured stock-dowel and
shell scope; it does not qualify this printed, finished mandrel. The accepted
[v4 elbow-cradle trial](../funnel/cradle-trial/physical-acceptance.json) retains
its 0.65 mm catch gap and its own frozen print scope.

## Print

[Saved Bambu Studio project](funnel-mold.3mf)

The saved project contains geometry `953dbfa68` on two plates: the cavity
upright and the core inverted. Its meshes are bound to the
[saved slice review](current-slice-review.json); they do not include the
rectangular plug blank or the rod socket in the current CAD exports.
It selects these presets:

- Process: **0.24mm Standard @BBL H2C funnel mold**
- Filament: **Funnel mold PETG Translucent - 0.4 Standard - flow 0.88**
- Printer: **Bambu Lab H2C 0.4 Standard +0.18 Z trim**

The project selects 0.4 mm Standard nozzles. It uses 0.24 mm layers, a 0.20 mm
first layer, Textured PEI,
two wall loops, 100% zig-zag infill and automatic normal supports in Snug style.
Support top and bottom Z distances are 0.20 mm; first-layer gap and object XY
distance are 0.48 mm. Top surfaces use monotonic lines and bottom surfaces
use monotonic fill. The active Standard filament flow ratio is 0.88. Maximum volumetric speed
is 5.61702 mm³/s and infill/wall overlap is 15%. Nozzle temperature is 250 °C on the
first layer and 245 °C afterward.

The startup code applies a +0.18 mm Z trim in addition to the plate correction.
With the 0.4 mm nozzle and Textured PEI, the emitted command is `G29.1 Z0.16`.

The saved project contains no G-code. The
[current native slice review](native-slice-reviews/2026-10-03-centred-short-block/README.md)
binds a separate mesh-refreshed copy to the current cavity and core STLs,
retaining this PETG recipe. Both plates slice successfully with bed-rooted
Snug support and at least 42 mm of deposited-path clearance from the bed edge.
This review covers those exact shell prints. The separate
[mandrel native slice](native-slice-reviews/2026-10-03-forming-mandrel-petg088-v1/README.md)
reviews its current raw tool with the same saved PETG strategy and a local
0.08 mm band across the entry, relief and sealing land. One 0.14 mm local layer
in the dry pilot's Z0.72–0.85 alignment range sets the wet-layer phase; the
0.20 mm bed layer and global recipe stay as recorded. The first expanded entry
layer occupies Z1.540–1.620, starting at the native shoulder's underside.
The relief receives two 0.08 mm layers, Z3.300–3.380 and Z3.380–3.460.

[current-slice-review.json](current-slice-review.json) records successful
slices of the saved geometry with the settings above. Its mesh and source
hashes identify the scope of its casting-match check, layer counts, time and
material estimates.

The core's envelope is [211 × 211 × 42.2 mm](CORE_DIMS); the cavity is
[211 × 211 × 58 mm](CAVITY_DIMS). Supports are accessible from the dry backs.
Inspect and remove every branch before finishing. Sand and finish the layer
steps on the forming slopes before casting.

The [print log](print-log.md) records physical observations with their known
provenance. [print-jobs.json](print-jobs.json) records submitted files, settings
and printer responses. Coated closure, vacuum cycling, support removal and
casting are untested for these shells.

## Cast and open

1. Remove shell and mandrel supports and brim, including branches inside the
   open V cradle and under the tool's exposed entry shoulder. Finish and measure
   the tool to its reference profile, keeping both locating zones bare. Measure
   50.8 mm from the pilot end to the axial-stop end; the native slice deposits
   its final dry top at 50.820 mm, leaving 0.020 mm to finish at that stop.
   Slide its dry shank through the loose passage, bring its end to the visible stop
   and secure it in the V with two zip ties. Dry-fit the two halves and check
   that the pilot drops into the cavity's socket without touching its walls or floor.
   Check the lands with a light behind the seam; use the flange bolts or clamps
   to close slight bow. Confirm that the coated halves still meet on those lands.
2. Prove the shell and mandrel PETG, finishing stacks, release, entry-seal clay and
   [silicone](silicone.md) on a sample. Pack the mandrel-entry seal flush with the
   forming face. Degas the mixed silicone in a separate container with expansion room.
   [Smooth-On's degassing example](https://www.smooth-on.com/tutorials/making-piece-cut-block-mold/vacuum-de-gassing/)
   shows the required headroom above the liquid.
3. Fill the open cavity, including the rod socket. Lower the core slowly
   with its finished mandrel installed. Seat and hold the flanges evenly. Top up through the
   [11 mm](FILL_D) fill hole; the five [4 mm](VENT_D) vents remain open.
4. For a filled-mold vacuum cycle, use a catch tray and keep overflow clear of the
   dry-back openings. Vent slowly, recheck the fill level and top up while fluid.
   Hold the flanges through the silicone's room-temperature cure.
5. Trim overflow at the port mouths, cut the mandrel's zip ties and remove the entry seal.
   Open in small alternating movements at
   opposite notches. Peel the accessible silicone brim to admit air, lift the
   core straight off the mandrel and peel the casting and tool together from
   the cavity. Trim the socket's collar flush with the block bottom. Withdraw
   the tool toward −Z: its 6.35 mm upper shank passes through the 6.0 mm land by
   5.83% diametric silicone expansion. This is an elastic release, and its force,
   surface damage and coating retention remain unqualified. Clean the passage
   and inspect the tool before the next cast.

## Regenerate

```sh
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel-mold/forming_mandrel.py
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel-mold/funnel_mold.py
```

To compose the complete tooling from the current exact shell files without
regenerating their prints, use `funnel_mold.py --preserve-native-shells`.
Run `tools/funnel-mold-print/review_forming_mandrel.py` and
`review_containment.py` afterward. The mandrel prints socket-pilot-down at Z0;
its native receipt records the local fine-band layers and support-removal route.
Reload changed print meshes in a separate Bambu Studio project, retain their
documented orientations and review the native slice before saving.

After publication, run [review_geometry.py](/tools/funnel-mold-print/review_geometry.py)
with this models directory. Geometry lint reports overhangs in the print
orientations. Review support coverage and removal access in Bambu Studio.

## Sources
[value](NAME) texts are updated by:
- `/tools/funnel-mold-print/verify_print.py`
