# IEC C14 mains inlet

Measured exterior of the MXR AC-04 panel-mount C14 inlet (Amazon B07DCXKNXQ),
the receptacle the customer's C13 cord plugs into on the +Y wall of back-top.
The model supplies the flange the wall pockets, the screw stations, the rim
the wall bores for, and the housing the electronics bay leaves room for.

[Open the STEP](iec-c14-inlet.step) · [Generator](iec_c14_inlet.py) ·
[Scan reproduction](analyze_scan.py) · [Capture evidence](scan-evidence.json) ·
[Scan-to-model check](scan-model-check.json)

The MINI 2 capture is three turntable passes: the part standing on one flange
ear, flipped onto the other, and that pose again with the table tilted −20° to
see further into the cavity. The raw frames, calibration, three untouched fused
clouds and the registered putty-free cloud live in
`~/Documents/3D Scans/2026-09-21-iec-c14-inlet/`; `capture-manifest.json` there
records hashes and settings. The scan uses millimetres without scale adjustment.

## Coordinate frame

Y is the mating axis and +Y points out of the enclosure toward the cord. X runs
along the flange, centred between the two screw holes. Z is up, with the earth
blade below the line and neutral pair. Y = 0 is the outboard face of the flange's
ears, the plane the wall's seating face carries.

| Interface | Model dimension |
|---|---|
| Flange, nose to nose × across the long flats | [49.97](FLANGE_W) × [21.88](FLANGE_H) mm, [3.25](FLANGE_T) thick |
| Ears and tapers | R[4.885](EAR_R) arcs centred [20](EAR_CX) from the axis, [17.98](FLANGE_END_CHORD) mm from shoulder to nose |
| Screw holes | Ø[3.24](SCREW_D), [40.21](SCREW_PITCH) mm apart on the mating axis, 90° countersunk to Ø[6.1](CSK_D) outboard |
| Rim round the cavity mouth | [31.03](RIM_W) × [22.13](RIM_H) mm R[6](RIM_R), [1.84](RIM_PROUD) proud of the ears |
| Cavity mouth | [24.82](MOUTH_W) × [16.26](MOUTH_H) mm, R[2.3](MOUTH_TOP_R) above, [4.8](MOUTH_CHAMFER) mm chamfers below |
| Cavity floor | [14.3](CAVITY_FLOOR_Y) mm below the seating plane |
| Housing | [26.1](BODY_W) × [18](BODY_H) mm, [13.65](BODY_DEPTH) deep behind the flange, lower edges chamfered [4.85](BODY_CHAMFER_LEG) |
| Tab bosses | three [4](BOSS_W) × [10](BOSS_H) mm, [1.17](BOSS_PROUD) proud of the housing's end |
| Solder tabs | [0.8](TAB_T) × [6.3](TAB_W) mm, tips [25](TAB_TIP_Y) mm behind the seating plane |

`flange_profile()` draws the flange's outline; `bore_outline()` is the rim;
`panel_cutout()` is the manufacturer's stated opening. `panel_screws()`,
`panel_footprint()` and `panel_stack()` carry the stations, the face and the
reach either side of the seating plane.

## In the enclosure

Back-top's inlet tunnel pockets the part with the rim bearing on the pocket
floor around a 24.3 × 18.3 mm bore, the ears 1.84 mm off that floor and the two
screws through them. The pocket outline, bore and screw pitch are the print's
own figures in `enclosure.py`; this model is what stands in them, and the C13
cord mates through that bore.

## Chosen fidelity

The STEP is one solid. The flange's plan outline is the calipered one, which the
scan's broad faces end on and the printed pocket holds; the scan's thin edge band
reads 0.1–0.3 mm outside it and is not used ([scan-evidence.json](scan-evidence.json)
carries the three readings side by side). The flange thickness, rim, cavity,
housing and tab bosses are the measured forms. Blade and tab sections are IEC
nominal at the measured stations.
The knuckle round between flat and taper, the housing's upper edge rounds and
the tab holes are estimates; two small windows in the rim's side walls are
omitted; the ear front faces, which crown about 0.2 mm toward the tips, are flat.

Across 71,424 sampled observations the median distance to the model surface is
0.11 mm and the 95th percentile 0.79 mm. The surfaces the enclosure fits to —
flange faces, screw-hole walls, rim face and walls, housing faces and chamfers,
tabs — sit at 0.04–0.14 mm median; the tails are the rim windows, the cavity's
internal structure and the nominal blades. [scan-model-check.json](scan-model-check.json)
carries every feature's figures and [scan-model-check.png](scan-model-check.png)
the residuals on the cloud.

## Regeneration

From the repository root:

```sh
tools/cad-venv/bin/python hardware/reference/iec-c14-inlet/iec_c14_inlet.py
tools/cad-venv/bin/python hardware/reference/iec-c14-inlet/iec_c14_inlet.py selftest
tools/cad-venv/bin/python hardware/reference/iec-c14-inlet/analyze_scan.py
tools/cad-venv/bin/python hardware/reference/iec-c14-inlet/validate_scan.py
```

The generator writes the STEP and viewer payload. `analyze_scan.py` rebuilds the
part frames, registers the three archived clouds and writes
`scan-measurements.json`; `validate_scan.py` compares the registered cloud with
the model.

## Sources
[value](NAME) texts are updated by:
- `/hardware/reference/iec-c14-inlet/iec_c14_inlet.py`
