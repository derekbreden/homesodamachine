# Beduan solenoid valve

Measured exterior of the Beduan 12 V normally closed, 1/4-inch quick-connect
valve (Amazon B07NWCQJK9). The model supplies the mounting, tubing and electrical
interfaces used by the manifold and its printed supports.

[Open the STEP](beduan-solenoid.step) · [Generator](beduan_solenoid.py) ·
[Capture evidence](scan-evidence.json) · [Model checks](model-check.json)

The MINI 2 capture covers four full turntable passes: feet down and feet up,
each level and tilted 15°. The raw frames, calibration, four untouched fused
clouds and processing scripts live in
`~/Documents/3D Scans/2026-09-19-beduan-valve/`. The evidence manifest records
hashes and rigid transforms. The scan uses millimetres without scale adjustment.
Putty is removed by combining the independently visible upper and lower regions.

## Coordinate frame

X is across the flow axis. +Y points to the outlet, toward the terminals and in
the direction of the underside arrow. Z rises through the coil. The origin is
at the mean center of the four posts, on their end-face mounting plane.

| Interface | Model dimension |
|---|---|
| Post center spacing, X × Y | [24.4](POST_PITCH_X) × [24.85](POST_PITCH_Y) mm |
| Lower posts | Ø[6.9](POST_DIA) mm; shoulder at Z[11](POST_SHOULDER_Z) mm |
| Underside boss | Ø[24.3](BEARING_DIA) mm; bearing face at Z[5.2](BOSS_Z0) mm |
| Main body | Ø[31](SOLENOID_BODY_DIA) mm with four upper corner bosses |
| Cap envelope, X × Y | [33.5](CAP_X) × [33.8](CAP_Y) mm, with central edge notches |
| Port barrels | Ø[15.2](SOLENOID_PORT_DIA) mm; axis at Z[11.05](PORT_CENTER_Z) mm |
| Port face spacing | [59.5](PORT_LEN) mm |
| Collet ring and ear sweep | Ø[10.2](COLLET_DIA) mm ring; Ø[13.8](COLLET_SWEEP_DIA) mm swept envelope |
| Terminal blades | [6.3](SPADE_W) × [0.8](SPADE_T) mm; centers [14.9](SPADE_SPACING) mm apart |
| Terminal position | center Z[52.2](SPADE_Z) mm, tips at Y[27.1](SPADE_Y_END) mm |
| Overall envelope | [33.5](CAP_X) × [59.5](PORT_LEN) × [57.3](COIL_TOP) mm |

`body_width_x` is the existing [34.25](STATION_PITCH) mm assembly station pitch,
including air. The physical cap dimensions are `cap_width_x` and `cap_depth_y`.
The rectangular socket pattern comes from `mounting_centers()`; callers must
retain both axes when turning a valve into a support's coordinate frame.

The [valve seat](../../printed-parts/valve-seat/README.md),
[manifold trays](../../printed-parts/enclosure/valve-tray/README.md), and three
cold-core lid cradles use this pattern and bearing height. Their checks measure
native solid interference, port clearance, placement and socket engagement.

## Chosen fidelity

The STEP contains analytic solids with separate white body/collets, black coil,
steel yoke and fasteners, and metal terminals. It remains practical to edit,
section and use in interference checks.

| Feature | Representation and reason |
|---|---|
| Mounting | Four post cylinders, end faces, shoulders, bore mouths, the smaller rounded underside boss, annular recess and shallow underside pocket; these determine seating and grip. |
| Fluid connections | Stepped barrels, tube-entry mouths, separate collets, C-shaped locking collars and release ears; these determine tube access and release clearance. |
| Coil and yoke | Cylindrical coil, terminal block, bent steel sides/top, base plate, and open gaps; these determine the actual occupied space. |
| Electrical connection | Blade width, thickness, reach, spacing, rounded tips and latch holes; these determine connector access. |
| Fasteners and markings | Screw-head envelopes. Drive recesses, lettering, coating texture and shallow cosmetic seams are omitted. Flow direction is recorded by the port datums. |
| Hidden interiors | Bore mouths extend only through the observed entrance region. Their interior closure faces are modeling boundaries; hidden threads and fluid passages are unspecified. |

The release collets turn about the port axes. Their ears are shown in the
feet-up capture configuration. The feet-down captures contain different ear
angles and are excluded from the combined nose region, so the model has one
ear on each collet. A clearance for arbitrary rotation uses the ear's swept
radius, not only the pictured orientation.

The two underside passes have a 0.175 mm 95th-percentile nearest-point
separation on normal-matched overlaps. This is repeatability on the coated
sample, not calibrated absolute accuracy. Mounting dimensions use 0.05–0.1 mm
increments; broad exterior forms use simple nominal surfaces. Local scan-to-CAD
checks record the remaining differences by feature in
[scan-model-check.json](scan-model-check.json). Across all 95,278 sampled
observations the median distance to a CAD component surface is 0.098 mm and the
95th percentile is 0.504 mm. The post walls and port barrels have 95th percentiles
of 0.113 and 0.165 mm respectively; omitted recess details remain in the totals.

## Regeneration

From the repository root:

```sh
tools/cad-venv/bin/python hardware/reference/beduan-solenoid/beduan_solenoid.py
```

The generator writes the colored STEP, viewer payload and validity/bounds report.
`build_beduan_solenoid()` supplies the complete exterior compound to assemblies;
`build_assembly()` retains the material components for direct inspection.

## Sources
[value](NAME) texts are updated by:
- `/hardware/reference/beduan-solenoid/beduan_solenoid.py`
