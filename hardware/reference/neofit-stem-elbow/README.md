# NeoFit 1/4-inch stem elbow

The [user-linked white acetal ATEU44W](https://www.freshwatersystems.com/products/neofit-acetal-white-stem-elbow-1-4-tube-x-1-4-stem?variant=48366191542456) connects directly into another 1/4-inch push-fit socket and turns the water path 90°. This editable layout reference uses the ATEU44 row of NeoFit's [Tube Elbow Union drawing](https://assets.freshwatersystems.com/image/upload/s--ua8owcZg--/mlf6gjlehc9xpkjrbfw2.pdf), linked from its [natural-white acetal listing](https://www.freshwatersystems.com/products/neofit-acetal-natural-white-stem-elbow-1-4-tube-x-1-4-stem). Its molded details are estimates, not a scan.

| Supplier dimension | mm |
|---|---:|
| Male stem / female tube OD | 6.35 / 6.35 |
| Maximum collar OD, P | 15.494 |
| Free stem to shoulder, A | 21.0058 |
| Female socket engagement, B | 16.891 |
| Overall along stem axis, E | 34.798 |
| Overall along socket axis, L | 25.0952 |

The axes intersect at the origin. The socket opens **+Y**, with its release face at **(0, 19.05, 0)**. The stem points **−X**, with tip **(−27.051, 0, 0)** and shoulder **(−6.0452, 0, 0)**. The tip and shoulder follow the listed dimensions; the 19.05 mm socket reach assumes equal hub back reach on both axes. Allow approximately ±1 mm on that reach in layout studies. The rounded hub, socket bands, collet lip and 4.3 mm passage are estimated form. The STEP has separate fixed-body/stem and release-collet solids; it supplies no seal, grip or release-stroke model.

Stem seating depends on the **receiving socket**. At this NeoFit row's 16.891 mm engagement, the shoulder remains **4.115 mm** outside the host mouth and the bend axis stands **10.160 mm** out. For unmeasured valve/check sockets, the layout estimate is **12.7 mm insertion**, with a **10–15 mm** study range: the nominal shoulder gap is **8.306 mm** and bend-axis projection **14.351 mm**. The male tip can bottom before its shoulder touches the host. These intervals are uncertainty estimates, not part tolerances. The [measured John Guest tee](../jg-pp0208e-tee/README.md) retains its own receiving depth.

The [polypropylene PTEU44-W](https://www.freshwatersystems.com/products/neofit-polypropylene-natural-white-stem-elbow-1-4-tube-od-x-1-4-stem) has similar photographed form and the same nominal connections. It may share this provisional layout envelope; its tooling dimensions are not independently established. No material-variant geometry equivalence is claimed. Existing NeoFit bulkhead/reducer references are supplier-derived, while the [John Guest elbow](../jg-pp0308e-elbow/README.md) supplies the scanned exterior precedent for separating body and collet.

[`model-dimensions.json`](model-dimensions.json) records the sources, derivations and interface uncertainty. [`neofit_stem_elbow.py`](neofit_stem_elbow.py) exposes `socket()`, `stem_tip()`, `stem_shoulder()` and `seated_host_mouth(insertion)`. The NPZ contains `v` and `f` arrays in this frame, matching the STEP and lightweight STEP mesh.

Rebuild from the repository root:

```sh
PYTHONPATH=. tmp/takeover/cadq "NeoFit stem elbow reference" -- tools/cad-venv/bin/python hardware/reference/neofit-stem-elbow/neofit_stem_elbow.py
```
