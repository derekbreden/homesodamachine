# Lee Spring LCM060C12M compression spring

This is a standalone catalog reference. The tee carrier uses the delivered spring's
[measured envelope](/hardware/printed-parts/enclosure/tee-carrier/tee_carrier_spring.py)
for fit checks. The installed uxcell 304 stainless product is sold as 6 mm OD and
30 mm free length, with nominal 0.8 mm wire ([bom.md §8](/hardware/ledger/bom.md));
its measured sample dimensions control the carrier.

Derek's measured stiffer set is **6 mm OD, 27 mm uncompressed and approximately 7 mm
fully compressed**, possibly slightly less. Those sample measurements are recorded in
[spring-measurements.json](/hardware/printed-parts/enclosure/tee-carrier/spring-measurements.json)
and govern its fit. The Lee catalog rate below does not establish the actual pair's force.

Source: [Lee Spring, LCM060C 12 M product page](https://www.leespring.com/product/compression-spring-lcm060c12m-music-wire),
accessed 2026-09-05. The product page is the authority for the values below.

## Official catalog specification

| Property | Published value |
|---|---:|
| published stock code | `LCM060C12M` |
| product | metric stock compression spring |
| outside diameter | 5.99 mm, +0.08 / −0.13 mm |
| inside diameter | 4.78 mm |
| wire diameter | 0.61 mm |
| recommended hole diameter | 6.40 mm |
| recommended guide-rod diameter | 4.39 mm minimum |
| nominal free length | 30.00 ± 0.99 mm |
| solid height | 8.61 mm |
| nominal rate | 0.688 ± 0.07 N/mm |
| published load at solid | 14.68 N |
| active / total coils | 12.36 / 14.36 |
| ends | squared and ground |
| material | ASTM A228 music wire |
| finish | zinc plate and bake per ASTM B633 |

The nominal one-spring catalog arithmetic at bearing-plane separation `L` is
`0.688 × (30 − L)` newtons. Two equal springs in parallel give twice that
nominal value. This arithmetic does not include spring-rate and free-length
tolerances, seat friction, guide friction, off-axis loading, or plastic-part
deflection.

## CAD contract

[`lee_lcm060c12m.py`](lee_lcm060c12m.py) is a constructed reference, not a
vendor STEP. It exposes:

- `build(installed_length=FREE_LENGTH)` — one solid, on local +Z, with ground
  bearing planes at Z=0 and Z=`installed_length`.
- `centerline(installed_length=FREE_LENGTH)` — the visual variable-pitch wire
  path used by `build`.
- `bearing_planes(installed_length=FREE_LENGTH)` — `(0.0, installed_length)`.
- `catalog_load_estimate(installed_length)` — nominal catalog-rate arithmetic
  for one spring, separate from the geometry.
- `export_model(installed_length, step_path=..., stl_path=...)` — write one
  requested state.
- `selftest()` — validate a single solid, outside diameter, bearing planes, and
  catalog arithmetic at the solid, representative installed, and free lengths.

The path carries one nominal inactive turn at each end, as implied by the
published total and active coil counts. The ground faces are planar cuts through
that path. Pitch redistribution only makes the reference occupy a requested
installed length; it is not a winding drawing, finite-element model, buckling
analysis, fatigue analysis, or contact model. Do not derive force from the CAD
pitch or volume.

The committed [`lee-lcm060c12m.step`](lee-lcm060c12m.step) and
[`lee-lcm060c12m.stl`](lee-lcm060c12m.stl) show one nominal **30 mm free-length**
spring. A standalone compressed catalog reference uses `build()` with its requested
bearing-plane distance. The production carrier does not consume this wire geometry
or its catalog load function.

Run the canonical export and its checks with:

```sh
tools/cad-venv/bin/python \
  hardware/reference/lee-lcm060c12m/lee_lcm060c12m.py
tools/cad-venv/bin/python \
  hardware/reference/lee-lcm060c12m/lee_lcm060c12m.py selftest
```

A one-off installed state must use a distinct output stem:

```sh
tools/cad-venv/bin/python \
  hardware/reference/lee-lcm060c12m/lee_lcm060c12m.py \
  --installed-length 18.322 \
  --output-stem /tmp/lcm060c12m-18p322
```

## Installed duty

The pair supplies the short separating movement that locks the collets after insertion,
and returns the empty carrier to park. Derek's
[physical observations](/hardware/reference/tee-connector/README.md#observed-push-connect-action)
establish that a small tug engages a free collet and that insertion pushes it inward against
spring-level force.

The fixed body's round bores and the carrier's recessed seats locate the two springs.
Each bore opens into a loading well that admits a compressed spring before the fore valve row
and flexible links are installed.
The production spring facts use measured sample dimensions and the actual bearing-plane
separations, including seat depth. Pair forces, rate, wire diameter, inside diameter and
material volume remain unknown. The displayed spring cylinder is a clearance envelope.
Geometry checks do not establish spring force, buckling resistance or positive capture.

The springs occupy the dry enclosure cavity. The current guide bore is Ø6.57 mm and
its loading window admits a spring compressed to 9.61 mm. Derek's measured 6 mm OD and
approximately 7 mm compressed length leave 0.285 mm nominal radial air and at least
approximately 2.61 mm axial loading margin. The actual 27 mm free length leaves 2.85 mm
compression at the 24.15 mm aft-limit separation. Capture at both ends remains open in the
[readiness audit](/hardware/printed-parts/enclosure/print-readiness.md).
