# neoFit ACHV44-E check valve

One native analytic reference represents the purchased black acetal
[ACHV44-E](https://www.freshwatersystems.com/products/neofit-acetal-black-single-check-valves-1-4-tube-0-3-psi-crack-pressure)
at both the water-pump discharge and CO₂ check positions. The supplier lists
¼-inch OD tube connections, acetal copolymer, food-grade EPDM and 0.3 psi
nominal cracking pressure. The purchase is WEBFWS100715131, bag of ten.

The exact product's [GLB](https://cdn.shopify.com/3d/models/o/939a932bdf15ab37/yihuwtagfre0ay5n1gao.glb)
and [USDZ](https://cdn.shopify.com/3d/models/o/913a0b443c00f8bc/yihuwtagfre0ay5n1gao.usdz)
supply the check-specific exterior proportions. Their file units do not
establish actual dimensions. The neoFit
[ATEU44 sheet](https://assets.freshwatersystems.com/image/upload/s--ua8owcZg--/mlf6gjlehc9xpkjrbfw2.pdf)
and [ATRU444 sheet](https://assets.freshwatersystems.com/image/upload/s--rN_5qBOD--/nvkzj79bbgumy8drpkff.pdf)
both specify **15.494 mm maximum female socket collar diameter** (P, .610 in)
and **16.891 mm female engagement** (B/B2/B3, .665 in). The corresponding
GLB landmark is its short outlet socket's fixed cylindrical collar, radius
1.0 in the model; the larger check barrel is a separate feature. Scaling
that exterior collar to the sibling dimension gives **55.432 mm mouth
spacing** and **16.863 mm maximum fixed-body diameter**. Both ACHV dimensions
are same-family inferences, without an established engineering tolerance.
The linked
[neoFit catalogue](https://assets.freshwatersystems.com/image/upload/s--FacjKp_O--/xa3vlqau7opjabwxmc5o.pdf)
lists the connection and pack count. The source URLs, hashes, normalization
and estimated profile are in [model-dimensions.json](model-dimensions.json).

Native flow is **+Y**, inferred from the supplier cutaway's poppet and spring.
The origin bisects the mouths: inlet `(0, −27.715803, 0)`, outlet
`(0, +27.715803, 0)`, with outward axes −Y and +Y. Physical arrow direction
has not been verified. Both socket insertions use the **16.891 mm sibling
neoFit engagement** as an explicit inference for this unmeasured check.
The two nominal inserted tube ends leave **21.650 mm** between them. This
is an axial packaging check; it does not qualify the valve internals or a
cut length. The 4.24 mm open bore is illustrative;
valve internals, seals, grab teeth and release motion are absent.

The fixed cylindrical support band is **4.436502–20.193125 mm from the inlet
mouth**, radius **8.431479 mm**, with 15.757 mm available along its axis.
Keep both moving collets free. The STEP has a
separate fixed case and two analytic oval release collets. CAD clearance to
this estimated envelope establishes no hardware fit, grip, seal, pressure
capacity, cracking performance or service life.

[neofit_achv44_check.py](neofit_achv44_check.py) exposes `inlet()` and `outlet()`
as `(position, outward_axis)` pairs; `ports()` includes the common insertion
estimate. `socket_depth()`, `bearing_band()` and `sections()` are stdlib-only
interfaces. `sections()` returns `(label, radius, s0, s1)` along flow from the
inlet; tapered spans and oval collets use conservative radial bounds.
`build_parts()` returns the three native solids and `build()` their compound.
Production imports this reference STEP; it does not import the vendor mesh.

Rebuild from the repository root:

```sh
tmp/takeover/cadq "neoFit ACHV44-E reference" -- tools/cad-venv/bin/python tools/bazel/trace_inputs.py hardware/reference/neofit-achv44-check/neofit_achv44_check.py
```
