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
orientations, using the complete saved trial PET-GF profile. The standalone
STLs are already in those print poses:

- `display-trial-housing.stl`
- `display-trial-cover.stl`

`trial-geometry.json` records the CAD source hashes, the plane cutting the
short neck, proof that the complete display housing is retained, and the
validated print meshes. `faucet-display-fit-trial.step` shows the nominal
seated cover, display, tubes and ribbon together. The standalone cover STEP,
STL and print project contain the relaxed, inward-preformed cover.

Generate with the project's CadQuery Python:

```sh
tools/cad-venv/bin/python hardware/printed-parts/fixtures/faucet-display-snap/faucet_display_snap_trial.py
tools/cad-venv/bin/python hardware/printed-parts/fixtures/faucet-display-snap/prepare_print_project.py
```

After removing supports, feed the three real tubes and ribbon through the
stub. Seat the display on all four supports and check the underside
components clear the tubes and ribbon. Lower the cover squarely, letting
its side walls spread over the rigid cylinder until both broad lips enter
the side grooves. Check the seam closes, the glass remains clear of the bezel,
and pressing the touchscreen does not rock the module or move the tubes.
Check that the real ribbon lies in the open space below the PCB and reaches
the southwest corner as viewed from the glass, clear of the deeper components.
The 2 mm dispense face has one flat rear plane. The CAD envelope
does not establish how the cable's bonded web bends.
Record any tight spot before trimming it, together with material/color,
drying and print orientation.

The cover itself supplies the flex. Each relaxed wing is preformed inward
0.75 mm at its upper retaining edge and 0.908 mm at its bottom. The two
broad retaining lips are 3 mm high, with 1 mm nominal radial engagement
in 1 mm deep grooves. The seated lips contact the groove roots, keeping the
wings spread. There is 0.15 mm clearance above the lip tops; the groove
floors support the seated lips before the bezel can reach the glass.
All four metal-foot pads keep their 3 mm sections. The seated CAD is a fit
reference, not a prediction of the cover's elastic shape or force.
Print both parts together: the larger lips require the matching housing.
The complete cover's insertion force, retention, repeatability, whitening,
cracking and permanent spread are observations from this physical trial.

Polymaker's [PET-GF15 technical data sheet](https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PET-GF15_V1.0_EN.pdf)
reports 4.0 ± 0.5% elongation at break in X–Y and 2.6 ± 0.1% in Z, with
Young's moduli of 4144.2 and 3428.9 MPa respectively. Its specimens were
annealed at 120°C for 16 hours. Those values are not an allowable strain
for this snap in the saved print profile. The [physical print log](print-log.md)
records fit and handling observations; this preloaded geometry awaits its trial.

## Print and support reading

The separate [trial project](faucet-display-fit-trial.3mf) preserves its
saved project and filament settings byte for byte: Bambu H2C,
0.4 mm nozzle, 0.24 mm layers, two walls and 15% grid infill.
The saved trial uses a 0.40 mm support top gap and 0% part cooling; the
production project has its own saved profile.
[The project report](faucet-display-fit-trial.print.json) records the
settings and embedded-mesh hashes. Both source STLs are already oriented
and seated for printing; the project adds no further rotation.

The offline Bambu Studio 02.08.02.61 slice completed without a warning.
Its estimate is 2 h 24 min 3 s and 30.60 g using the saved 1.29 g/cm³
filament density. These grams are a profile estimate, not a measured PET-GF
part mass. Actual extrusion paths retain 64.89 mm to the shared bed boundary
and 93.86 mm between the two parts.

| Part / support body | Root | Contact reading | Build-up |
|---|---|---|---|
| Housing / tree-1 | Print bed, Z0.20 mm | Housing and neck-stub underside; exact contacts are unlabelled in the G-code. The support spans Z0.20–85.40 mm | Not measured without interface labels |
| Cover / trees 1–2 | Print bed, Z0.20 mm | Two explicitly labelled lip interfaces begin at Z14.84 mm. The supports reach Z15.08 mm | 14.64 mm to first labelled interface on each body |

[The retained support audit](faucet-display-fit-trial.support-audit.json)
records the support bounds and toolpaths. The supports print the actual
fit features in their production orientations. The cover's open underside
provides the intended removal route to its two lip supports before fitting
the display. An unlabelled interface count is unknown, not zero. Check
removal access and the finish of the tube passages, display supports,
broad lips and groove bearing faces on the physical print before testing
the fit.

To repeat the offline slice, add `--slice-output /path/to/local/slice` to
`prepare_print_project.py`. This writes local G-code and its audit; it
does not connect to a printer.
