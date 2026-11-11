# Display gasket

A TPU ring under the display cover plate's lap, between the plate and the display's
cover glass.

Material: Bambu TPU 90A (black).

The screw-mounted cover bears on the glass through the soft ring. It spreads
light clamp pressure along the glass border and accommodates printed surface
variation. The ring stays beneath the cover.

The outer outline follows the glass and the opening follows the cover window.
Its thickness and seating follow the shared
[display mount dimensions](../display-cover/mount-dimensions.json).

## Print

Print the ring flat without supports. The [display-gasket plate](../trial-preparation/pieces.json)
uses the TPU 90A flat seal profile on the glued Engineering Plate.

## Regenerate

```
tools/run -- cargo build --release --locked --manifest-path tools/hsm/Cargo.toml -p hsm-enclosure-components --bin display-gasket
tools/run -- tools/hsm/target/release/display-gasket
```
