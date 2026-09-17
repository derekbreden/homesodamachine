# Faucet display fit trial

Two PET-GF prints make the complete faucet-display enclosure: its shell
with a short gooseneck stub, and the complete cover. They come directly from
the faucet's current CAD builders. The display supports, snaps, tube
passages, ribbon route, cosmetic surfaces and cover seam keep their actual
dimensions. Only the neck beyond the complete housing is shortened.

Use the same Waveshare ESP32-S3-Touch-LCD-1.47, one 3/8-inch LLDPE soda tube,
two 1/4-inch LLDPE flavor tubes and the SIG-6 ribbon. The trial includes the
open space between the tubes and the display; there is no printed floor in
that space. The four metal feet sit on their actual printed supports.

`faucet-display-fit-trial.3mf` holds both parts in their production print
orientations, using the complete saved faucet PET-GF profile. The standalone
STLs are already in those print poses:

- `display-trial-housing.stl`
- `display-trial-cover.stl`

`trial-geometry.json` records the CAD source hashes, the plane cutting the
short neck, proof that the complete display housing is retained, and the
validated print meshes. `faucet-display-fit-trial.step` shows the assembled
prints, display, tubes and ribbon together.

Generate with the project's CadQuery Python:

```sh
tools/cad-venv/bin/python hardware/printed-parts/fixtures/faucet-display-snap/faucet_display_snap_trial.py
tools/cad-venv/bin/python hardware/printed-parts/fixtures/faucet-display-snap/prepare_print_project.py
```

After removing supports, feed the three real tubes and ribbon through the
stub. Seat the display on all four supports and check the underside
components clear the tubes and ribbon. Lower the cover squarely until both
snaps engage. Check the seam closes, the glass remains clear of the bezel,
and pressing the touchscreen does not rock the module or move the tubes.
Check that the real bonded ribbon takes the sideways S turn and stays
seated in its passage without lifting toward the PCB. The CAD envelope
does not establish how the cable's bonded web bends.
Record any tight spot before trimming it, together with material/color,
drying and print orientation.

The two long snap arms have 3 × 3 mm sections, 0.30 mm engagement and a
0.50 mm travel stop. The seated arms are unloaded. Their ideal rectangular
beam strain is about 0.239%; that estimate does not include local stress,
print anisotropy or the stiffness of the full housing. Insertion, retention,
repeatability and permanent set are observations from this physical trial.

Polymaker's [PET-GF15 technical data sheet](https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PET-GF15_V1.0_EN.pdf)
reports 4.0 ± 0.5% elongation at break in X–Y and 2.6 ± 0.1% in Z, with
Young's moduli of 4144.2 and 3428.9 MPa respectively. Its specimens were
annealed at 120°C for 16 hours. Those values are not an allowable strain
for this snap in the saved print profile. No physical trial result is recorded.

## Print and support reading

The separate [trial project](faucet-display-fit-trial.3mf) preserves the
production project and filament settings byte for byte: Bambu H2C,
0.4 mm nozzle, 0.24 mm layers, two walls and 15% grid infill.
[The project report](faucet-display-fit-trial.print.json) records the
settings and embedded-mesh hashes. Both source STLs are already oriented
and seated for printing; the project adds no further rotation.

The offline Bambu Studio 02.08.02.61 slice completed without a warning.
Its estimate is 2 h 16 min and 25.63 g using the saved 1.29 g/cm³ filament
density. Actual extrusion paths retain 66.87 mm to the shared bed boundary
and 94.79 mm between the two parts.

| Part / support body | Root | Contact reading | Build-up |
|---|---|---|---|
| Housing / tree-1 | Print bed, Z0.20 mm | Housing and neck-stub underside; exact contacts are unlabelled in the G-code. The support spans Z0.20–84.92 mm | Not measured without interface labels |
| Cover | No supports | None | — |

[The retained support audit](faucet-display-fit-trial.support-audit.json)
records the support bounds and toolpaths. The housing support remains to
print the actual fit features in the production orientation. An unlabelled
interface count is unknown, not zero. Check removal access and the finish
of the tube passages, display supports, snap arms and retaining faces on
the physical print before testing the fit.

To repeat the offline slice, add `--slice-output /path/to/local/slice` to
`prepare_print_project.py`. This writes local G-code and its audit; it
does not connect to a printer.
