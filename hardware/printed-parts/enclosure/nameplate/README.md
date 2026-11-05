# Nameplate

An 88 × 100 mm First Edition plate in the shallow rear receiver of
`enclosure-back-top`. The faucet mark, two-line Georgia Bold company name, fine
divider, matching Helvetica Neue Medium identification lines and QR share one
vertical centreline. A 0.42 mm rounded white frame surrounds the artwork,
inset 4.79 mm from each edge of the black face.

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
The logo, lettering and QR retain their sizes inside the evenly inset frame.

The full-domain address in written instructions is `homesodamachine.com/0001`.
The separate [appliance marking specification](/hardware/markings/README.md) covers
ratings, refrigerant warnings and disposal marking low on the enclosure.

## Four-screw mounting

Four acquired black BNUOK M3 × 6 socket-head screws fasten the plate to four ruthex
RX-M3S × 4 short heat-set inserts in the solid receiver of `enclosure-back-top`.
The screw centres form a 66 × 78 mm rectangle, centred on the plate and 11 mm from
each nearest plate edge. Each head clears the nearest white border by 3.04 mm
both horizontally and vertically. Each Ø3.4 mm
clearance hole has a Ø6.2 × 1 mm counterbore. The Ø5.5 × 3 mm screw heads stand
2 mm above the black face; their 2.5 mm hex sockets face directly outward.

The plate has a flat back, a 2.36 mm bearing floor beneath each counterbore and
3.64 mm of screw engagement. The receiver takes Ø4 × 4.64 mm cold pilots;
insert fronts finish flush with the seat. The upper pair ends against the existing
3 mm support floors; the lower pair opens through the rear wall. The closed
pilots leave 0.64 mm behind each insert and 1 mm behind each screw tip.
The insert lands end on the adjoining cold-core clearance plane.
The broad seat is
3 mm thick, with the four insert lands carried into the existing enclosure wall.
Each land supplies at least 3.7 mm of radial stock around the installed insert.
The 4.6 mm installed
insert envelope represents intentional thermal interference with the Ø4 pilot.

[`snap_dimensions.rs`](snap_dimensions.rs) supplies the shared mount record;
[`snap_geometry.rs`](snap_geometry.rs) cuts the plate, receiver and separate
purchased-hardware models. The production back-top uses the same stock and
cavity construction. Hardware is separate from the printable plate's two-colour
3MF and appears in the installed machine and attachment review.

The plate centre is world X−45.4/Z217 and its face is Y473.3. The complete receiver
is 94.3 mm wide. Its outside edges leave 2.95 mm to the rear-corner tangent at
X−95.5 and 2.90 mm to the adjacent color-chip frame at X4.65. The receiver stands
2 mm proud of the rear wall and has one 45° crown, retaining a 3 mm rim above
the plate opening. The short inserts clear the cold-core envelope by 0.94 mm;
screw tips clear it by 1.30 mm. Wago H and N sit 1 mm inward from their nominal
rear stations, leaving 1.14 mm behind the receiver floor. The screw heads finish
4 mm beyond the rear wall and 7.83 mm inside the rear extent of
the bulkheads. All four screws are reached from outside the assembled machine.
[Production measurements](production-fit.json) record the geometry review.

## Printing and assembly

Print the nameplate flat, face up, with its complete back on the bed and the
counterbores facing up. No supports are needed. Use the shared PET-GF material
settings, a 0.20 mm first layer, Arachne walls and a 75% minimum bead width on
the 0.4 mm nozzle to retain the 0.325 mm identification strokes.

Preserve the accepted Mark2 black/white alignment compensation in the print
package; it is not a CAD translation. The [colour registration print records](horizontal-wing-trial/README.md)
identify that compensation and the external black/white PET-GF spools. Keep the
standard nozzle-offset startup option at Auto.

Back-top prints roof down using the shared PET-GF tree-support settings. Clear
the receiver seat and pilots, then press its four short inserts flush while
back-top is loose. Keep the insert axis normal to the seat; do not press past
flush. Clean the bearing faces. Set the plate into the receiver and start all
four M3 × 6 screws before tightening. Seat them lightly by hand with a 2.5 mm
hex key, alternating diagonal corners. The plate must lie flat without bowing.
Scan the installed QR and compare the unit number with the build record.

The four-screw attachment has Derek's 3D approval. Its physical mounting and
support cleanup are unqualified; printing is held for the enclosure corner review.

## Website review and generation

[`attachment_view.py`](attachment_view.py) exports the complete appliance,
seated detail and separated attachment views from production meshes. Review
models turn 180° about Z to open on the rear with the website’s default camera;
production models keep the machine coordinates. The
separated view exposes the flat plate back, inserts and screw stations.
The [complete enclosure review](https://homesodamachine.com/3d#glb:assembly%2Fscenes%2Fglb%2Fnameplate-shallow-full-context.glb)
opens directly on the rear of the appliance.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/nameplate.py 1
tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/nameplate.py selftest
```

First Edition plates are numbered 0001–0010. Every QR remains version 1. The
manual self-test checks solid validity, disjoint inks, the QR quiet zone,
fastener/artwork clearance, seating, bearing, insert stock and screw engagement.
