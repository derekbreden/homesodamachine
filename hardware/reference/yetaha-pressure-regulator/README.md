# Yetaha compact water-pressure regulator

Estimated exterior of the [Yetaha 1/4-inch quick-connect regulator, B07GDGYHZV](https://www.amazon.com/dp/B07GDGYHZV), model SZ070030063979RK-1. This reference supports layout work; no received specimen has been measured, and this part is not installed in the enclosure assembly.

[Open the STEP](yetaha-pressure-regulator.step) · [Generator](yetaha_pressure_regulator.py) · [Dimensions and photo datums](estimated-dimensions.json)

Millimetres. Flow follows **+X**, the cap points **+Z**, and the origin is midway between the two tube mouths. `inlet()` and `outlet()` return `(position, outward_axis)` at X=−29.75 and +29.75, respectively. The photographed flow arrow establishes the end assignment.

| Feature | Nominal, mm | Plausible interval, mm |
|---|---:|---:|
| Port-face span | 59.5 | 55–64 |
| Fixed socket diameter | 14.0 | 13–15 |
| Bonnet square | 34.5 | 32–37 |
| Four-bolt pitch, both axes | 24.5 | 23–26.5 |
| Cap hex across flats / corners | 24.0 / 27.7 | 22–26 / 25.4–30.0 |
| Port axis above mounting plane | 15.5 | 14–18 |
| Mounting-plane to cap-face height | 53.0 | 50–58 |
| Transverse fork-tip span | 63.0 | 58–68 |

The mounting plane is Z=−15.5; the cross-adjuster face is Z=+37.5. The forks are 12 mm wide and 3.5 mm thick, with estimated 4.2 mm slots opening at Y=±31.5. Their closed ends are nominally Y=±23.5; these slots do not establish one exact screw pitch. Decimal places are modeling choices, not measurement precision. The intervals are engineering estimates rather than manufacturing tolerances.

The six product photographs show the opposed sockets, rounded square bonnet, four fasteners, hex-sided cap, central cross adjuster and near fork. Image IDs and manually selected pixel datums are recorded in the dimension file. The photographs remain linked at their primary source; package dimensions are excluded.

The [scanned Beduan valve](../beduan-solenoid/README.md) provides a nearby family comparison: 24.4×24.85 mm corner spacing, a 33.5×33.8 mm cap and Ø10.2 mm collets. The regulator photograph's approximately 480 px bolt pitch and 665 px bonnet width support the nominal scale. This is a similarity inference, not evidence of an identical mould. The [JG tee's measured Ø10.43 mm median collet](../jg-pp0208e-tee/README.md) provides another scale check. A 1/4-inch tube does not standardize the outside of its collet.

The visible mouth's entrance-to-rim ratio is approximately 0.65. With the nominal Ø10.6 mm collet, that gives a Ø6.9 mm lead-in, consistent with a Ø6.35 mm tube and a small chamfer. The visible chamfer is not treated as an exact tube-diameter datum.

The near fork reaches approximately 21 mm beyond the base edge after correcting for the photograph's approximately 27° elevation. Adding the base's half-depth gives about 32 mm from center to tip. The obscured opposite fork uses conservative symmetry completion; its presence is not independently established by the gallery views.

Adjustment access follows the central cross-disc along **+Z**, from the face at Z=+37.5. Its estimated diameter is 21.5 mm. A Ø23×20 mm approach corridor is a practical layout allowance for a flat blade or coin, rather than a manufacturer-specified operating space.

The native reference separates the white body, adjuster and collets, blue retaining clips, and metal fastener envelopes. Appearance uses the existing material palette. Clip clocking, small recesses and fastener sizes are estimated visible forms. Shallow mouth closures represent unobserved geometry; they do not establish insertion depth, release stroke, internal pressure-control geometry or adjuster travel.

[The one-off artifact review](model-check.json) records ten valid native and reloaded STEP solids, zero component overlap volume, the nominal bounds, open mouths and slots, and the matching STEP/payload digest. This validates the representation rather than a received part or installed fit.

`build()` returns the exterior compound; `build_assembly()` returns its named material components. Regenerate manually with:

```sh
tools/cad-venv/bin/python hardware/reference/yetaha-pressure-regulator/yetaha_pressure_regulator.py
```
