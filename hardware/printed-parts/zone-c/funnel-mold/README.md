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

![Open dry backs; the cavity's feet and the core's rod socket](backs.png)

## Forming surfaces and fit

Both forming faces reserve [0.30 mm](FINISH) of net finishing growth, including
primer, sealer and release. Sand and coat a sample with the actual finishing
stack, then measure its net growth. Mask the parting lands, locating pegs and
holes, clamp holes, and steel-rod socket. The finishing allowance belongs to
the silicone-forming surfaces; the bare lands establish closure height.

The [6.35 mm](ROD_D) × [50.8 mm](ROD_LEN) steel dowel forms the spout bore and
seats [28.8 mm](SOCKET) into a local boss. Its socket has
[0.30 mm](ROD_CLEARANCE) diametral clearance and a separate
[2.5 mm](SOCKET_VENT) air vent into the open back. Verify that the actual pin
slides to its seat and withdraws freely. A thin silicone film can enter the
socket clearance and must be peeled out between casts.

![Section through the assembled forming shells, silicone and steel dowel](section.png)

Teal is the cavity, gold the core, grey the nominal silicone and light grey the
steel dowel. The nominal casting, including its sacrificial spout tip, is
[135 mL](CAST_VOLUME). The two halves fit inside a [276.7 mm](ENVELOPE) circle,
leaving [11.5 mm](CHAMBER_GAP) radial clearance in the recorded chamber. Check
the actual opening, clamp/bolt envelope and catch tray before pouring.

## Load and vacuum

The complete mold sits inside the vacuum chamber. Its fill hole, five casting
vents, rod-socket vent and both dry backs communicate with that chamber.
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
[0.772 kPa](HEAD_PRESSURE). This flat-plate model is a screening approximation;
it does not establish the printed shell's stiffness, creep, release force or
transient pressure during degassing.

Bambu reports PETG Translucent bending moduli of 1610 MPa in XY and 1520 MPa in
Z on conditioned test specimens. The sizing assumption is lower; the actual
print still needs its own dry-fit and vacuum trial.
[Material data sheet](https://store.bblcdn.eu/s8/default/71ca815e70e74afc96ff5883f003235f/Bambu_PETG_Translucent_Technical_Data_Sheet.pdf).

## Print

[Recommended project, +0.04 trim](funnel-mold.3mf) ·
[Alternate +0.18 trim](funnel-mold-z018.3mf) ·
[Printer, filament and process presets](funnel-mold-presets.bbscfg)

| Body | Envelope | Estimated print | PETG, including supports |
| --- | --- | --- | --- |
| [Cavity](cavity.step) | [205 × 205 × 73.6 mm](CAVITY_DIMS) | [17 h 19 min](CAVITY_TIME) | [615 g](CAVITY_MASS) |
| [Core](core.step) | [205 × 205 × 45.3 mm](CORE_DIMS) | [10 h 55 min](CORE_TIME) | [441 g](CORE_MASS) |

Together: [28 h 14 min](TOTAL_TIME), [1.06 kg](TOTAL_MASS). These are slicer
estimates. The files use the left [0.8 mm](NOZZLE) [High Flow](NOZZLE_TYPE) nozzle, [0.24 mm](LAYER) layers,
translucent PETG at 255 °C, an [18 mm³/s](FLOW_CAP) volumetric cap, a removable 6 mm brim,
and same-material tree supports with 0.3 mm vertical separation. The cavity
prints upright and the core inverted. Supports are accessible from the dry
backs. Inspect and remove every branch before finishing.

The [0.4 mm project](funnel-mold-04.3mf), at 0.16 mm layers on the left Standard
nozzle, is estimated at [55 h 10 min](FINE_TIME) and [0.93 kg](FINE_MASS) for both halves.
It uses the same geometry, +0.04 mm plate trim and automatic tree supports.

[print-profile.json](print-profile.json) records the actual saved settings,
STL and G-code checksums, support usage and estimates.
[layer-review.json](layer-review.json) records model connectivity at the sliced
layer heights. The cavity spout tip and core socket boss begin above the plate;
the G-code has support-interface paths directly beneath both features.
[print log](print-log.md) records physical observations with their known provenance.
Coated closure, vacuum cycling, support removal and casting are untested for
these shells.

## Cast and open

1. Remove supports and brim. Seat the steel pin and dry-fit the two halves.
   Check the lands with a light behind the seam; use the flange bolts or clamps
   to close slight bow. Confirm that the coated halves still meet on those lands.
2. Prove the PETG, finishing stack, release and [silicone](silicone.md) on a
   sample. Degas the mixed silicone in a separate container with expansion room.
   [Smooth-On's degassing example](https://www.smooth-on.com/tutorials/making-piece-cut-block-mold/vacuum-de-gassing/)
   shows the required headroom above the liquid.
3. Fill the open cavity, including the blind spout pocket. Lower the core slowly
   with its dowel installed. Seat and hold the flanges evenly. Top up through the
   [11 mm](FILL_D) fill hole; the five [4 mm](VENT_D) vents remain open.
4. For a filled-mold vacuum cycle, use a catch tray and keep overflow clear of the
   dry-back openings. Vent slowly, recheck the fill level and top up while fluid.
   Hold the flanges through the silicone's room-temperature cure.
5. Trim overflow at the port mouths. Open in small alternating movements at
   opposite notches. Peel the accessible silicone brim to admit air, lift the
   core straight, peel the casting from the cavity, withdraw the dowel and trim
   the sacrificial spout tip at its shoulder.

## Regenerate

```sh
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel-mold/funnel_mold.py
tools/cad-venv/bin/python tools/funnel-mold-print/prepare_print.py --models hardware/printed-parts/zone-c/funnel-mold --output /tmp/funnel-shell-print-08/default-input.3mf --nozzle 0.8
```

Prepare the alternate input with `--z-trim 0.18`. Slice both inputs in Bambu
Studio, then run [verify_print.py](/tools/funnel-mold-print/verify_print.py) with
this models directory and the slice directory. `--nozzle 0.4` prepares the
comparison project; pass its slice directory as `--comparison-slices` when
verifying to refresh both estimates.

After publication, run [review_geometry.py](/tools/funnel-mold-print/review_geometry.py)
with this models directory. Geometry lint reports overhangs in the print
orientations; the saved slice's tree supports carry the dry faces.

## Sources
[value](NAME) texts are updated by:
- `/tools/funnel-mold-print/verify_print.py`
