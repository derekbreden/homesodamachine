# Explainer scene assets

`enclosure-cad.json.gz` and `cold-core-cad.json.gz` contain the genuine named
CAD parts used in the opening reveal. The local `.json` working copies are
ignored. `../prepare-assets.py` extracts them from the existing repository
payloads with conservative display-mesh simplification; it does not rebuild or
change the hardware.

Each bundle has `meshes`, an array of objects containing `name`, `group`,
`color`, `positions`, `normals`, `indices` and `bounds`. All geometry arrays are
flat; positions and normals contain triples, and indices contain triangle
triples. Positions are millimetres. Colors are linear-sRGB triples.

Both bundles use the enclosure's frame: X across its width, +Y toward the
rear and Z up. The standalone cold core is already placed in that frame.
Use `(E.x, E.z, -E.y)` for a right-handed Three.js Y-up scene. The carbonator's
internal floor anchor in that scene is `(0, 64.7, -323.8)`. Its tube spans
Z 52–204.4 mm in the enclosure, with internal faces at Z 64.7 and 191.7 mm.

The four exterior shell mesh names are `enclosure-front-bottom`,
`enclosure-front-top`, `enclosure-back-bottom` and `enclosure-back-top`.
Their `group` values retain those names, so they can move independently.
The other semantic groups are `insulation`, `evaporator`, `carbonator`,
`flavor-reservoirs`, `display`, `funnel` and `mechanical-context`.

`coil-path.json` supplies the actual finished 9.5-turn centerline and sampled
tangent tails. It is already in local Y-up coordinates, with the carbonator's
internal floor at Y 0 and radial center at X/Z 0. Its nominal centerline radius
is 66.675 mm and tube radius is 3.175 mm; the centerline rises from Y 2.3 to
121.7 mm. `flowPoints` follows refrigerant from the inlet station, through the
lower coil end, up the winding, then out through the outlet tail. The source's
local bridge relief is retained. These are refrigerant lines.

`cad-manifest.json` records source paths, hashes, bounds, coordinate mapping,
mesh counts, font origins and licenses. Archivo is the channel's variable
heading/body face; IBM Plex Mono is the regular engineering-label face.
The SVGs and palette are copied from the current brand exports.

`faucet-cad.json.gz` supplies the current Sculpted faucet's exterior parts,
cropped at countertop height, in its native Z-up frame. Every mesh has group
`faucet`. Its origin is the mounting axis at the countertop; forward is −Y.
`faucet-datums.json` records the CAD-based water/flavor outlet stations and
exit tangent, the lever pivot, and illustrative glass/pour staging. Apply
`(F.x, F.z, -F.y)` for the same right-handed Y-up convention. The selected
display texture is decoded directly from the firmware RGB565 artwork.
The Sculpted base and tip use 24,000-triangle display targets with the source
CAD vertex-normal field transferred to the reduced mesh. Crease-aware normal
selection retains designed edges while the curved arch's highlights remain
smooth.

## Animated carbonator

`../prepare-carbonator-assets.py` reads the existing current STEP assemblies
and exports persistent hardware in local Y-up coordinates. Its outputs are
`carbonator-hardware-full.json.gz`, `carbonator-hardware-section.json.gz`,
`magnetic-float-cad.json.gz` and `carbonator-datums.json`. The corresponding
uncompressed CAD JSON files are ignored working copies.

The full and half-section pressure hardware use the same analytic STEP shapes.
The section retains Z ≤ 0 in the local movie frame. Its cut faces are actual
Boolean geometry. `sectionFaceIndices` is a flat vertex-index list of cut
triangles; `sectionTriangleOrdinals` gives their face IDs in the original index
buffer for assigning a separate matte section material. The float and guide
lie behind the section plane. These bundles already have the Y-up coordinate
transform applied: do not rotate them or subtract the enclosure anchor again.

The water jet exits at `(19.05, 124.746, 0)` mm, with its 2 mm axial passage
starting at Y 126.746 mm. The plain CO₂ port opens at `(19.05, 0.254, 0)` and
the soda-water outlet at `(−19.05, 0.254, 0)`. The datums file provides sampled
water, gas and outlet flow centerlines along the source elbow axes. The
6.35 mm modeled elbow bore is the layout placeholder stated in the source;
the connector reference models supply exterior envelopes. Colored flow
within those envelopes is an explanatory overlay.

The movable float comes directly from the current all-ASA Aero assembly STEP:
a 36 mm cylindrical body, 28 mm tall, with a 4.8 mm axial guide bore and an
enclosed coaxial RC62 ring. Its local origin is the magnet midplane, with body
Y −14 to +14 mm. Place it at `(0, level − 8.766, −41.849)` mm using the
provisional dry-foam immersion model. The ring belongs inside the opaque body.
