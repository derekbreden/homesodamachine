# Nameplate

An 88 × 100 mm First Edition plate in the raised rear receiver of
`enclosure-back-top`. The faucet mark, two-line Georgia Bold company name, fine
divider, matching Helvetica Neue Medium identification lines and QR share one
vertical centreline. A 0.42 mm rounded white frame surrounds the artwork.

[`nameplate.py`](nameplate.py) generates the two-colour part. [`wordmark.svg`](wordmark.svg)
holds the outlined title, edition and frame; [`identification-glyphs.json`](identification-glyphs.json)
holds the matching unit-number letterforms. The faucet comes from [`brand/mark.svg`](/brand/mark.svg).
The black face is 3.36 mm thick. White artwork has a 0.72 mm embedded base and rises
0.48 mm above the face. STEP and 3MF preserve both colour volumes; the STL represents
their combined exterior.

## QR and identification

Unit 0001 reads `FIRST EDITION` and `UNIT 01 OF 10`. Both identification lines use
the same 3.5 mm em, weight and tracking. The QR contains `HTTPS://HOSM.US/0001`:
version 1, error correction M, 21 × 21 active modules at 1.2 mm. Its active square
is 25.2 mm; the four-module quiet zone makes a 34.8 mm square. The QR and its quiet
zone clear the frame and text. Diagonal-only white contacts have 0.02 mm corner joins.
The complete artwork retains its size within the narrower black horizontal margins.

The full-domain address in written instructions is `homesodamachine.com/0001`.
The separate [appliance marking specification](/hardware/markings/README.md) covers
ratings, refrigerant warnings and disposal marking low on the enclosure.

## Retention

The attachment is under review and the nameplate is held from printing.
[Full-size attachment options](attachment-options/README.md) show broad walls
joined continuously to the plate or receiver, and a rigid screw-mounted option.
The interface described below is the currently generated geometry; it is not a
released attachment.

The rigid plate presses straight into its receiver. Two hidden leaves flex inward
behind it. Each leaf is 2 mm thick in X and 2 mm deep in Y, with an R1.5 transition
at its root, a 25 mm free length to its head, and a single pointed 1.2 mm lead-in.
The hooks capture 1.05 mm of receiver shoulder. Their insertion stroke is 1.2 mm;
the receiver provides space for that stroke, the complete roots and both heads.
The leaf outline lies within each face-up printed layer.

The clip tips extend 4 mm behind the plate back. Blind receiver pockets have
0.25 mm rear clearance, at least 3 mm of backing stock, 0.15 mm body clearance per
side and 0.25 mm additional allowance at the print-down opening. The retaining
shoulder is 1.6 mm deep. A centered 6 mm-wide front tool opening in each receiver
side exposes its spring head while leaving a 2 mm bearing band at either end of
the hook. Insert a small flat screwdriver beside the plate, push the head inward
and lift that side; release the opposite head to remove the plate. The tool
openings are in the receiver, accessible from outside the assembled enclosure.

[`snap_dimensions.rs`](snap_dimensions.rs) supplies the common dimensions.
[`snap_geometry.rs`](snap_geometry.rs) cuts the complete plate and the receiver
stock and cavities used by the production back-top. The local receiver export and
website cutaway use that same interface.

The plate centre is world X−45.4/Z220 and its face is Y476.3. The complete receiver
is 94.3 mm wide: its outside edges leave 2.95 mm to the rear-corner tangent at
X−95.5 and 2.90 mm to the adjacent color-chip frame at X4.65. These are frame-to-frame
and frame-to-corner spaces. The receiver stands 5 mm proud of the rear wall,
2 mm beyond the color-chip rail.
This depth retains at least 3 mm behind the clip pockets where the cold-core
clearance trims the interior of back-top.
[Production fit measurements](production-fit.json) record the geometry review.

## Printing and assembly

Print the nameplate face up, with the hidden clip backs on the bed and supports
under the plate back. Remove supports through the open sides of the 2 mm space
behind each leaf; keep its root and pointed head intact. Use the shared PET-GF
material settings, a 0.20 mm first layer, Arachne walls and a 75% minimum bead width
on the 0.4 mm nozzle to retain the 0.325 mm identification strokes.

Preserve the accepted Mark2 black/white alignment compensation in the print
package; it is not a CAD translation. The [colour registration print records](horizontal-wing-trial/README.md)
identify that compensation and the external black/white PET-GF spools. Keep the
standard nozzle-offset startup option at Auto.

The receiver prints within back-top in its roof-down orientation using shared
PET-GF tree supports. Clear the pockets through the front opening before
installation. The complete hidden-leaf plate and enclosure attachment await
physical verification; geometry checks do not establish plastic fatigue life.

## Website review and generation

[`attachment_view.py`](attachment_view.py) exports seated, separated and installed
GLB views from the actual production meshes. The separated plate is turned around
to expose its leaves; that inspection pose is not its installation path.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/nameplate.py 1
tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/nameplate.py selftest
```

First Edition plates are numbered 0001–0010. Every QR remains version 1. The manual
self-test checks solid validity, disjoint inks, the QR quiet zone, seated clearance
and an insertion sweep with the spring heads displaced inward.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/nameplate/nameplate.py`
