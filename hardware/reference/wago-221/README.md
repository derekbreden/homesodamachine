# WAGO 221 COMPACT lever nuts — reference solids

Every splice in the machine where one conductor becomes many, mains and DC alike
(`hardware/ledger/bom.md` §11). Rated 32 A, 450 V; all three accept 24–12 AWG at an
11 mm strip.

| SKU | poles | where | count |
|---|---|---|---|
| 221-413 | 3 | the mains H / N / G and the 12 V + / GND rails, in a row on the +X wall | 5 |
| 221-415 | 5 | J2 MANIFOLD B `COM`, J6 REEDS A `GND`, J4 SENSORS `GND` | 3 |
| 221-420 | 10 | J1 MANIFOLD A `COM`, J7 REEDS B `GND` | 2 |

None has a mounting hole — each is a free splice, so a **printed press-fit well**
grown into an enclosure wall's own inner face is the whole mount
(`enclosure._side_wells`), butt-first, ports facing the room. There is no carrier
part and no screw.

## Geometry

| | 221-413 | 221-415 | 221-420 |
|---|---|---|---|
| Width — lever-hinge axis (mm) | 18.8 | 30.0 | **29.8** |
| Height — closed body (mm) | 8.4 | 8.4 | **15.8** |
| Depth — wire-entry axis (mm) | 18.6 | 18.6 | **18.3** |
| Lever rows | 1, on +Z | 1, on +Z | **2, on +Z and −Z** |
| Ports per row | 3 | 5 | 5 |

The 221-420 is one busbar in a two-storey body: all ten ports on the same wire-entry
face, five levers hinging off each of the two large faces — so it wants
`lever_swing` clear on **both** sides, where the single-row parts want it on one.

Levers stay inside the closed envelope; fully up, one reaches **15.25 mm** off the
seating plane (measured on a 413) — `lever_swing` 6.85 mm past the face it hinges on.
Both live in the front half of the depth, which leaves the rear half blank on every
face and is what a well grips.

In the file's frame: X = width, Y = depth, Z up; origin at the footprint center,
Z = 0 the seating plane. Datasheet figures run slightly generous vs. calipered
(413 H ≈ 8.25 measured) — treat the envelope as loose by ~0.15 mm. Regenerate all
three with `tools/cad-venv/bin/python wago_221.py`.
