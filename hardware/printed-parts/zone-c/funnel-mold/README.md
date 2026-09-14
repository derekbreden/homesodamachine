# Funnel mold

Two PETG shells follow the [funnel](../funnel/README.md), with
[5 mm](SKIN) forming walls and [5 mm](FLANGE) clamping flanges. The cavity
stands on three small feet. The core has a [136.4 mm](DRY_MOUTH) square opening
in its dry back. Both halves print with automatic breakaway tree supports;
the modeled shells print at 100% fill.

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

Both forming faces reserve [0.30 mm](FINISH) of net finishing growth, including
primer, sealer and release. Sand and coat a sample with the actual finishing
stack, then measure its net growth. Mask the parting lands, locating pegs and
holes, clamp holes, rod passage, V cradle and rod stop. The finishing allowance belongs to
the silicone-forming surfaces; the bare lands establish closure height.

The [6.35 mm](ROD_D) × [50.8 mm](ROD_LEN) steel dowel passes freely through an
[8.35 mm](ROD_GUIDE_D) opening, with [2 mm](ROD_CLEARANCE) diametral clearance.
An open V cradle on the dry back centres it. Its upper end meets a visible
stop; two zip ties in [4.4 mm](ROD_TIE_WIDTH) grooves hold it in the cradle.
Engagement is [32.8 mm](ROD_ENGAGEMENT), leaving [18 mm](ROD_EXPOSED) below the
core's neck. The rod stays clear of the cavity during closure.

Pack a small removable seal around the rod at the forming-face entry, flush
with the adjacent surface. The illustrated seal is [2 mm](ROD_SEAL_DEPTH) deep.
Prove the mold-sealing clay's compatibility with the actual
[platinum-cure silicone](silicone.md) on a sample before using it in the mold.
The cradle holds the rod; the seal
closes the annular passage into the dry back. Smooth-On's
[sealer reference](https://www.smooth-on.com/page/sealers-releases/) distinguishes
sulfur-free modeling clay from sulfur-bearing clay for platinum silicone.

The finished outlet has a [4.5 mm](SPOUT_WALL) nominal wall and
[15.35 mm](SPOUT_OD) outside diameter around the [6.35 mm](ROD_D) bore. Its
[12 mm](SPOUT_LAND) clamp land takes the 1/4-inch LLDPE stub and the recorded
10–16 mm worm clamp. A full-diameter [18 mm](TIP_LENGTH) sacrificial extension
leaves [12 mm](TIP_CAP) beneath the rod end. Mark the trim plane
[18 mm](TIP_LENGTH) from the casting's closed end and cut square after demolding.

[design.json](design.json) checks simultaneous [1.5 mm](ROD_OFFSET) lateral
offset, [2°](ROD_TILT) tilt and axial error in eight directions. The rod may
project [6 mm](ROD_EXTRA) farther when not fully seated, or [3 mm](ROD_AXIAL)
less than nominal. The minimum depth beneath its tip in these cases is
[5.90 mm](ROD_MIN_END).
The minimum silicone clearance in that envelope is [2.37 mm](ROD_MIN_WALL),
including the sacrificial end. These checks describe geometry; the first
physical trial establishes retention, sealing and casting quality.

![Rod held from the open core cradle, with a full-thickness outlet and closed sacrificial end](rod-detail.png)

![Section through the assembled forming shells, silicone and steel dowel](section.png)

Teal is the cavity, gold the core, grey the nominal silicone, light grey the
steel dowel and blue the removable entry seal. The nominal casting, including its sacrificial spout tip, is
[145 mL](CAST_VOLUME). The two halves fit inside a [276.7 mm](ENVELOPE) circle,
leaving [11.5 mm](CHAMBER_GAP) radial clearance in the recorded chamber. Check
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
[159 mm](LOAD_SPAN) flat square, [5 mm](SKIN) thick, under a uniform
[1.00 kPa](LOAD_PRESSURE), using an assumed PETG modulus of
[1000 MPa](LOAD_MODULUS) and Poisson ratio 0.4. Its calculated deflection is
[0.209 mm](LOAD_DEFLECTION); the maximum static silicone head is
[0.839 kPa](HEAD_PRESSURE). This flat-plate model is a screening approximation;
it does not establish the printed shell's stiffness, creep, release force or
transient pressure during degassing.

Bambu reports PETG Translucent bending moduli of 1610 MPa in XY and 1520 MPa in
Z on conditioned test specimens. The sizing assumption is lower; the actual
print still needs its own dry-fit and vacuum trial.
[Material data sheet](https://store.bblcdn.eu/s8/default/71ca815e70e74afc96ff5883f003235f/Bambu_PETG_Translucent_Technical_Data_Sheet.pdf).

## Print

[Checked cavity print file, Textured PEI and +0.18 trim](funnel-mold-h2c-support-feet.gcode.3mf) ·
[Editable project](funnel-mold.3mf) ·
[Saved printer, filament and process presets](funnel-mold-presets.bbscfg)

The editable project selects these saved Bambu Studio User Presets:

- Process: **Funnel mold shell - 0.8 nozzle - 8mm support feet**
- Filament: **Funnel mold PETG Translucent - 0.8 nozzle - Bambu defaults**
- Printer: **Bambu Lab H2C 0.8 High Flow +0.18 Z trim**

The preset bundle also includes the +0.04 printer variant. Import the bundle
on another Bambu Studio installation to add these presets to its selectors.
The selected names appear without an asterisk when their settings match the
saved presets. Check the plate and nozzle assignments, then slice the editable
project; it contains no saved G-code.

The target printer is named **H2C**. Its physical plate is Textured PEI.
The +0.18 trim adds to Bambu's −0.02 mm Textured PEI correction, giving
`G29.1 Z0.16` in the checked G-code. The trim is calibrated for PET-GF;
its use with PETG is a physical trial recorded in the [print log](print-log.md).
The checked retry file contains the cavity, with a slicer estimate of **18 h 31 min**
and **653 g** including supports. The core is plate 2 of the editable project;
slice it with the selected profile before printing. Its envelope is
[205 × 205 × 45.2 mm](CORE_DIMS); the cavity is [205 × 205 × 79.6 mm](CAVITY_DIMS).

The files use the left [0.8 mm](NOZZLE) [High Flow](NOZZLE_TYPE) nozzle, [0.24 mm](LAYER) layers,
translucent PETG at 250 °C on the first layer and 245 °C afterward, a
[16 mm³/s](FLOW_CAP) volumetric cap, a 0.40 mm first layer, a removable 6 mm
model brim, and same-material tree supports with 0.3 mm vertical separation.
**Support → Initial layer expansion is 8 mm**, with 90% initial layer density
and zero raft layers. The cavity
prints upright and the core inverted. Supports are accessible from the dry
backs. Inspect and remove every branch before finishing.

The named filament preset inherits Bambu's H2C 0.8 PETG Translucent operating
settings; its only numerical override is the ledger cost. The process uses
three walls, solid modeled shells, 40 mm/s outer walls, 60 mm/s top surfaces,
and automatic trees at a 35° threshold. Bed temperature is 70 °C. Cooling,
support speed and tree branch geometry use the stock presets.

[support-foot-review.json](support-foot-review.json) checks the retry's emitted
first-layer support paths, bed bounds, settings and G-code checksums against the
reference slice in [print-profile.json](print-profile.json). The support footprint
is about 2.8 times the reference area. Startup commands retain the same Z trim,
temperatures and nozzle behavior; progress estimates and the bed-leveling
rectangle reflect this slice.
[layer-review.json](layer-review.json) records model connectivity at the sliced
layer heights. The cavity spout tip and core rod cradle begin above the plate;
the G-code has support-interface paths directly beneath both features.
[print log](print-log.md) records physical observations with their known provenance.
[print-jobs.json](print-jobs.json) records submitted files, settings and printer responses.
Coated closure, vacuum cycling, support removal and casting are untested for
these shells.

## Cast and open

1. Remove supports and brim, including branches inside the open rod cradle.
   Slide the rod through the loose passage, bring its end to the visible stop
   and secure it in the V with two zip ties. Dry-fit the two halves.
   Check the lands with a light behind the seam; use the flange bolts or clamps
   to close slight bow. Confirm that the coated halves still meet on those lands.
2. Prove the PETG, finishing stack, release, entry-seal clay and
   [silicone](silicone.md) on a sample. Pack the rod-entry seal flush with the
   forming face. Degas the mixed silicone in a separate container with expansion room.
   [Smooth-On's degassing example](https://www.smooth-on.com/tutorials/making-piece-cut-block-mold/vacuum-de-gassing/)
   shows the required headroom above the liquid.
3. Fill the open cavity, including the blind spout pocket. Lower the core slowly
   with its dowel installed. Seat and hold the flanges evenly. Top up through the
   [11 mm](FILL_D) fill hole; the five [4 mm](VENT_D) vents remain open.
4. For a filled-mold vacuum cycle, use a catch tray and keep overflow clear of the
   dry-back openings. Vent slowly, recheck the fill level and top up while fluid.
   Hold the flanges through the silicone's room-temperature cure.
5. Trim overflow at the port mouths and cut the rod's zip ties. Open in small alternating movements at
   opposite notches. Peel the accessible silicone brim to admit air, lift the
   core straight off the rod, peel the casting from the cavity, withdraw the
   dowel and cut off the marked sacrificial extension. Remove the entry seal
   and clean the passage before the next cast.

## Regenerate

```sh
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel-mold/funnel_mold.py
tools/cad-venv/bin/python tools/funnel-mold-print/prepare_print.py --models hardware/printed-parts/zone-c/funnel-mold --output /tmp/funnel-shell-print-08/default-input.3mf --nozzle 0.8 --z-trim 0.18
```

Slice both plates into `default/funnel-mold-h2c.gcode.3mf` below the slice
directory. Run [verify_print.py](/tools/funnel-mold-print/verify_print.py) with
this models directory, the slice directory, `--project-stem funnel-mold-h2c.gcode`
and `--single`. The editable `funnel-mold.3mf` is separate from the checked slice.

After publication, run [review_geometry.py](/tools/funnel-mold-print/review_geometry.py)
with this models directory. Geometry lint reports overhangs in the print
orientations; the saved slice's tree supports carry the dry faces.

## Sources
[value](NAME) texts are updated by:
- `/tools/funnel-mold-print/verify_print.py`
