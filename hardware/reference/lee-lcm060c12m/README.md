# Lee Spring LCM060C12M compression spring

The carrier uses two **Lee Spring LCM060C12M** stock compression springs as the
bench candidate. Each spring pushes between a fixed wall bearing plane and the
moving carrier; the pair acts in parallel.

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
spring. Assembly CAD calls `build()` with its actual bearing-plane distance so a
compressed state does not masquerade as free length.

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

## Bench status

This SKU is a **bench candidate**, not a production commitment. Validate both
springs in the printed seats across the whole travel before freezing the part:

- measure actual pair force at release, connected, squeeze, and park;
- exercise the moving carrier for rubbing, cocking, coil bind, and spring escape;
- guide the small-diameter spring with a rod or sleeve; a shallow locating seat
  alone does not establish buckling margin;
- use the actual bearing-plane separation, including recessed-seat depth, when
  calling `build()` or calculating nominal load;
- keep the zinc-plated music-wire spring dry. Lee describes the plating as light
  corrosion resistance, not a wet-cavity material specification;
- check the 5.99 mm OD tolerance against printed hole shrink and the guide against
  the spring's 4.78 mm nominal ID.

The selection is ready to bench when two physical springs, their printed seats,
and the intended guides are exercised together. CAD clearance and catalog rate
do not replace that test.
