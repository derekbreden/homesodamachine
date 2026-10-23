# Threadless TPU gas-joint layout models

Two compact joints connect 6.35 mm tube to the existing metal gas components.
The regulator's inlet joint wraps its external wrench boss and leaves straight
along −Y. The check's outlet joint wraps its male stub and turns directly down
−Z. The regulator male outlet remains threaded directly into the check's
female inlet; there is no extra part at that connection.

The regulator joint uses the first 9 mm of the scanned 19 mm AF / 20.6 mm
clipped inlet boss. Its tube mouth is `(0,−18.5,0)` in the regulator frame.
The check joint covers the 11 mm male stub from its tip at Y20 back to its
shoulder at Y9. Its tube mouth is `(0,24.9161326,−18.5)` in the check frame.

Both use the diaphragm pump sleeve's 2.8 mm relaxed radial walls, 6.10 mm
relaxed / 6.35 mm installed tube socket, 15 mm tube engagement, 4.4 mm passage,
3.5 mm tube stop and 9 mm band seats. The elbow copies its smooth reducer,
rounded heel and flat-foot construction. Its tube-axis offset follows the same
band clearance rule: `−(11−9)+1+11.8322652/2 = 4.9161326` mm past the tip.
The new metal cuff bores have an explicit 0.25 mm diametral interference
estimate. The installed OD follows the existing annular-area approximation.

Installed metal-cuff diameters are 26.1465 mm on the regulator and 19.2273 mm
on the check. Those seats require larger clamp ranges than the owned
10–16 mm tube clamps. Tube seats are 11.8323 mm installed OD. The model includes
four closed 9 mm bands with 0.6 mm radial skin, without screw housings or keys.

These are layout and fit estimates. The accepted pump articles' manual fit,
print quality and qualitative seal observations remain scoped to those
identified articles and recipes. They do not establish gas performance of
these new external-boss and threaded-stub cuffs. `interfaces.json` records
their source hashes, dimensions and limits; `audit.json` records the local
geometry query. This work supplies no sliced or pressure-qualified print.

## Use

`model.py` reads only local JSON and NumPy meshes:

- `library()` gives two installed joint meshes and four bands.
- `instances(poses)` places them with independent `regulator` and `check`
  poses, each containing `rotation` and `translation_mm`.
- `direct_instances(rotation=None, translation=None, include_metals=False)`
  places both around the direct metal connection, with check center at
  `(0,74.47,0)` in the regulator frame.
- `direct_ports(...)` returns the two tube-mouth datums and 15 mm insertion.
- `metal_library()` supplies the two frozen canonical metal references when
  `include_metals=True` is used.
- `mates()` identifies intended cuff, band and threaded contacts.
- `interfaces()` returns the complete frozen source/dimension record.

`geometry/` contains native STEP and NPZ for installed joints, relaxed joints
and closed bands. `reference/` holds frozen metal meshes. The canonical frames
are the regulator's inlet face Y0, flow +Y, and the check's center Y0, flow +Y.

Rebuild manually through the repository CAD queue:

```sh
PYTHONPATH=. tmp/takeover/cadq "CO2 threadless TPU joints" -- tools/cad-venv/bin/python hardware/manifold-layout/studies/co2-tpu/tpu-joints/build.py
```

No production placement, print profile or recurring check depends on this directory.
