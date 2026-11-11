# Nameplate

A First Edition plate in the shallow rear receiver of
`enclosure-back-top`. The faucet mark, two-line Georgia Bold company name, fine
divider, matching Helvetica Neue Medium identification lines and QR share one
vertical centreline. A rounded white frame surrounds the artwork with an even
inset from the black face's edges. The plate and its artwork share the scale in
[`rear_wall.rs`](../enclosure/numbers/rear_wall.rs).

[`nameplate.rs`](nameplate.rs) cuts the two-colour part: [`artwork.rs`](artwork.rs) reads the
outlines and [`qr.rs`](qr.rs) encodes each unit's code. [`wordmark.svg`](wordmark.svg)
holds the outlined title, edition and frame; [`identification-glyphs.json`](identification-glyphs.json)
holds the matching unit-number letterforms. The faucet comes from [`brand/mark.svg`](/brand/mark.svg).
The black face is 3.36 mm thick. White artwork has a 0.72 mm embedded base and rises
0.48 mm above the face. STEP and 3MF preserve both colour volumes; the STL represents
their combined exterior.

## QR and identification

The identification lines share their typeface, weight and tracking. Each unit's
QR addresses its own portal and uses medium error correction. The artwork master,
including the QR's quiet zone and diagonal contact joins, scales uniformly across
the face. Its relief and embedded depth keep their authored dimensions. The QR
and its quiet zone clear the frame and text.

The full-domain address in written instructions is `homesodamachine.com/0001`.
The separate [appliance marking specification](/hardware/markings/README.md) covers
ratings, refrigerant warnings and disposal marking low on the enclosure.

## Four-screw mounting

Four acquired black BNUOK M3 × 6 socket-head screws fasten the plate to four ruthex
RX-M3S × 4 short heat-set inserts in the solid receiver of `enclosure-back-top`.
The screw centres form a rectangle centred on the plate, with their edge offsets
defined in the shared mount record. Each head clears the white border.
Each Ø3.4 mm
clearance hole has a Ø6.2 × 1 mm counterbore. The Ø5.5 × 3 mm screw heads stand
2 mm above the black face; their 2.5 mm hex sockets face directly outward.

The plate has a flat back, a 2.36 mm bearing floor beneath each counterbore and
3.64 mm of screw engagement. The receiver uses the cold pilots in the shared mount coordinates;
insert fronts finish flush with the seat. The upper pair ends against the existing
support floors; the lower pair opens through the rear wall. The closed pilots
clear the inserts and screw tips.
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

The plate's position comes from the rear identification plan in
[`above-core.json`](/hardware/manifold-layout/above-core.json). Its receiver has
matching clear space beside the rounded corner root and above the seam band,
and clears the adjacent port-label rail. The raised field has a sloped crown.
The short inserts and screw tips clear the cold-core envelope. All screws are
reached from outside the assembled machine.
[Production measurements](production-fit.json) record the current geometry review.

## Printing and assembly

Print the nameplate flat, face up, with its complete back on the bed and the
counterbores facing up. The [Mark1 identification plate](../trial-preparation/README.md)
prints the black and white PETG with fine nozzles on the glued Engineering Plate
without supports. It carries the filament assignments and side-specific trim from
the [approved colour registration print](../display-cover/prints/2026-11-08-identification-set-mark1-right-z005/physical-result.json).

Back-top prints roof down using the shared PET-GF tree-support settings. Clear
the receiver seat and pilots, then press its four short inserts flush while
back-top is loose. Keep the insert axis normal to the seat; do not press past
flush. Clean the bearing faces. Set the plate into the receiver and start all
four M3 × 6 screws before tightening. Seat them lightly by hand with a 2.5 mm
hex key, alternating diagonal corners. The plate must lie flat without bowing.
Scan the installed QR and compare the unit number with the build record.

The plate and receiver's physical fit and support cleanup are unqualified.

## Generation

```sh
tools/run -- cargo build --release --locked --manifest-path tools/hsm/Cargo.toml -p hsm-enclosure-components --bin nameplate
tools/run -- tools/hsm/target/release/nameplate --unit 1
```

The first unit also writes the receiver, its fasteners and the receiver's dimensions that the
enclosure's print regions read. A unit outside the First Edition, or a code too long for
version 1, stops the program.
