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
