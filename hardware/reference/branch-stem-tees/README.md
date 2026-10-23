# Perpendicular-stem tees, 1/4 inch

Purchased-part layout references with two female run sockets on **±X** and a
smooth **Ø6.35 mm male branch stem on +Y**. The origin is the common axis
intersection. The models retain open sockets and a through passage. Neither
part is a scan of the received fitting.

| Native datum, mm | NeoFit ATBU444-E | John Guest CI580808W |
|---|---:|---:|
| Female run mouth span | 40.208 | 38.900 |
| Widest collar diameter | 15.494 | 15.200 |
| Male stem tip from junction | 27.051 | 26.000 |
| Stem shoulder from junction | 6.045 | 6.000 |
| Shoulder-to-tip stem length | 21.006 | 20.000 |
| Female socket insertion depth | 16.891 | 15.700 |
| Junction to a host mouth, with 15 mm insertion | 12.051 | 11.000 |
| Stem remaining outside that host mouth | 6.006 | 5.000 |

The host socket determines stem engagement. With 15 mm engagement in the ASSE
TPU socket, the NeoFit stem has 6.01 mm between its shoulder and the host mouth.

The [NeoFit product](https://www.freshwatersystems.com/products/neofit-acetal-black-branch-stem-tee-1-4-tube-x-stem-1-4)
links the manufacturer's [Branch Tee Union drawing](source/neofit-atbu444-drawing.pdf)
([original](https://assets.freshwatersystems.com/image/upload/s--KgZtyNy0--/w05r40lzxq5efdcb3d9e.pdf)).
Its ATBU444 row publishes Ø6.35 mm stem, Ø0.610 inch collar, 0.827 inch stem
length and 0.665 inch tube depth. The table's H/L dimensions differ from the diagram's E/L
arrows. This reference interprets H1.370 as total branch height and L1.583 as
overall run span, consistent with the photograph and separate NeoFit run-stem
family. This axis mapping is estimated. About 1 mm of envelope sensitivity is
appropriate for layout comparisons; it is not a product tolerance.

The intended [John Guest product](https://www.freshwatersystems.com/products/john-guest-branch-stem-tee-1-4-x-1-4-x-1-4-od-stem-branch)
is CI580808W. Its dimensions are on page 2 of the manufacturer's
[White Acetal Stem Tee sheet](source/jg-ci580808w-datasheet.pdf)
([original](https://www.johnguest.com/sites/jg/files/2023-04/JG%20Drinks%20White%20Acetal%20Stem%20Tee%20Data%20Sheet.pdf)).
The model uses its published pressed-collet state; locked collets may stand
farther out. The manufacturer also publishes a differently named "Branch Stem
Tee" sheet containing the CI530808W run-stem drawing; its URL is retained only
as a topology cross-check in the source metadata.

Molded steps, root diameters, collet profiles and the small tip chamfer are
photo-based approximations. NeoFit's internal Ø4.3 passage is a same-size family
estimate; John Guest publishes its Ø4.3 bore. O-rings, teeth, markings and
internal mechanisms are omitted. The
[scanned PP0208E tee](../jg-pp0208e-tee/README.md) supplies context for collet
motion. These models use their own acetal-part dimensions.

`dimensions.json` records source URLs, retained PDF paths and SHA-256 hashes,
evidence status, ports and the host insertion formula. `branch_stem_tees.py` exposes `build(variant)`,
`specification(variant)` and `stations(variant)`, where the variant is `neofit`
or `john-guest`. Each `.npz` contains `v` vertices and `f` triangle indices in
the native frame. STEP files carry material colors. `model-check.json` records
the generated solids' bounds and validity.

```sh
PYTHONPATH=. tmp/takeover/cadq "branch stem tee estimates" -- \
  tools/cad-venv/bin/python hardware/reference/branch-stem-tees/branch_stem_tees.py
```
