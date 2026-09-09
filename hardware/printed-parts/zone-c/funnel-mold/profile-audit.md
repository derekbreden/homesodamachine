# Funnel mold configuration audit

The project is built from three explicit inputs: **the current STL geometry,
[print-recipe.json](print-recipe.json), and the installed Bambu system presets**.
[prepare_print.py](prepare_print.py) constructs the 3MF from those inputs.
It reads no other 3MF and no user-profile directory.

[profile-audit.json](profile-audit.json) accounts for **all 579 effective saved
settings**, the five objects, two modifiers, three plate assignments and every
layer-height range. It records the source-file hashes and actual serialized
values. [audit_profile.py](audit_profile.py) checks the recipe against the sliced
project, including local settings that are not visible in the global profile.

## Sources and precedence

1. **Machine:** `Bambu Lab H2C 0.8 nozzle`, including its stock H2C machine-code
   templates. The user's measured plate trim is an explicit edit to the plate
   compensation block. Both +0.04 and +0.18 mm are provided; +0.04 is selected.
2. **Process:** `0.40mm Standard @BBL H2C 0.8 nozzle`. The recipe changes structural
   filling, wall generation, the top-surface speed, brim and seam gap.
3. **Filament:** `Bambu PETG Translucent @BBL H2C 0.8 nozzle`. The recipe changes
   temperature to 255 °C, the High Flow cap to 18 mm³/s and the cost estimate to
   the ledger's acquired-material cost. The vendor's 0.97 flow ratio, cooling,
   bed temperatures and retraction overrides remain in force.
4. **Objects and modifiers:** only the specified 60 mm/s outer-wall speed and
   2,000 mm/s² outer-wall acceleration. The witnesses receive the same settings
   at object level; the two large bodies receive them through the CAD surface zones.
5. **Height ranges:** only 0.16 mm layer height, over the named geometric bands.
   The default and first layer are 0.40 mm.
6. **Slicer engine:** Bambu Studio 02.08.02.61 supplies built-in defaults, resolves
   aliases, limits speeds, plans motion, expands machine templates and exports G-code.
   The final values are recorded rather than inferred from a preset's name.

The physical nozzle assignment is explicit: one filament on **left extruder 1,
0.8 mm High Flow**. Standard and High Flow are separate filament parameter columns;
their flow caps are 16 and 18 mm³/s respectively. Machine and process arrays contain
four columns: left Standard, left High Flow, right Standard, right High Flow.
The unused right slot is represented as Standard; it is not used by this print.
The print file does not set the machine's real nozzle inventory or AMS backup spools.
Each plate explicitly records `bed_type: Textured PEI Plate`; its bed choice does
not depend on the preceding project's global plate selector. The two trim profiles
are saved as Bambu Studio User presets, with start-code templates matching the
respective 3MFs. [Installation and selection](print-profile.md) precede opening the
project on a fresh Bambu Studio installation.

## Controls with practical consequences

| Control | What governs this project |
|---|---|
| Flow | The active High Flow column requests 18 mm³/s; the 0.97 flow ratio affects the commanded extrusion amount. This is a proposed operating point, not a measured material limit. |
| Surface speed | The two CAD modifiers and witness object settings request 60 mm/s. They act in addition to the global process and flow/cooling limits. |
| Layer height | Explicit fine bands retain shallow-slope overlap and forming detail. Straight structural regions use the stock 0.40 mm height. |
| Structural material | Four requested Arachne wall loops and 100% residual fill. The empty backing bays are modeled geometry. |
| Cooling | Vendor 20–60% normal fan range, first three layers off, auxiliary fan off and 90% overhang override. |
| Seam | Stock conventional aligned seam, with an explicit 0% gap. Scarf is disabled in both process and filament settings. |
| Travel | Stock retract/lift and travel limits. Avoid-crossing-wall detours are disabled. |
| Dimensions | No XY contour/hole compensation. Stock 0.15 mm elephant-foot compensation and 0.012 mm slicing resolution remain active. Nominal widths are 0.82 mm and vary with Arachne. |
| Plate contact | Stock 0.40 mm first layer plus the user's explicit plate trim; stock 70 °C textured-PEI temperature and an explicit 6 mm outer brim. |
| Extra processing | No post-processing commands, extra filament config files, custom per-layer G-code, support, raft, ironing or prime tower. |

The slicer's compiled defaults and machine firmware remain software dependencies;
recording their inputs is not a proof of their implementation or of physical print
strength. The manufacturer's preset names alone do not establish a calibrated flow
limit, finished dimensions or extraction capacity.

## Export reconciliation

The audit compares every supplied active setting with the exported value. Numeric
formatting, percentage representation and the legacy wall-order name are accounted
for. Fourteen supplied preset keys are not serialized; the JSON retains their
origins and accounts for `wall_infill_order` at `wall_sequence`. Bambu omits the
remaining obsolete or unrecognized fields from the effective configuration.

Bambu's CLI explicitly sets **`filament_prime_volume` to 45 mm³** when slicing a BBL
3MF without a separately loaded filament file, even though the selected filament
preset supplies 30. That assignment is present in
[the CLI implementation](https://github.com/bambulab/BambuStudio/blob/master/src/BambuStudio.cpp).
It is recorded as a slicer rewrite. The project has no prime tower or material
changes. This field is not the extrusion-flow cap.

Slice results, actual extrusion paths and checksums are recorded in
[print-profile.json](print-profile.json). The full project is also opened and
re-sliced by the CLI to check that the exported settings and layer ranges survive
a reload. Validation uses `--slice 0` for all plates. In this installed CLI,
selective loading with `--slice 1` crashes on the variable-layer project; the
fully exported projects already contain separate G-code for all three plates.
This is not a tested command for regenerating a single plate.

## Reproduce

Run from the repository root with the project CadQuery Python. The installed
Bambu resource hashes and version in the audit identify the exact preset inputs.
A different installation is a new slice to inspect.

```sh
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel-mold/prepare_print.py --output /tmp/funnel-mold-build/input.3mf
/Applications/BambuStudio.app/Contents/MacOS/BambuStudio --arrange 0 --slice 0 --outputdir /tmp/funnel-mold-build --export-3mf funnel-mold-petg-hf08-variable-016-040.3mf /tmp/funnel-mold-build/input.3mf
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel-mold/audit_profile.py /tmp/funnel-mold-build/funnel-mold-petg-hf08-variable-016-040.3mf --provenance /tmp/funnel-mold-build/input.provenance.json --output /tmp/funnel-mold-build/profile-audit.json
```

Use `--z-trim 0.18` on the generator and a separate output directory for the alternate
calibration. The generator writes a bundle containing both printer presets beside
its output. Machine start-code changes must preserve the manufacturer's code outside
the explicit plate-compensation block.
