# WR1110 fixed inline regulator

The received WR1110 is the secondary regulator inside the appliance's warm CO₂
chain. Its reference is an analytic CadQuery exterior measured from two coated
MINI 2 captures. The inlet face is Y = 0, the male outlet points along +Y, and the
smooth mounting barrel is centred on X/Z.

| Feature | Model, mm | Evidence |
|---|---:|---|
| Smooth barrel diameter | 18.87 | Independent scan fits: 18.883 and 18.852 |
| Straight barrel band | Y 14.65–50.05 | Radial profile at the wrench transitions |
| Usable model barrel length | 35.40 | Difference of those two stations |
| Barrel midpoint | Y 32.35 | Enclosure cradle datum |
| Inlet wrench across flats / turned blank | 19.00 / 20.60 | Flat normals and corner arcs |
| Outlet wrench across flats / turned blank | 19.08 / 21.76 | Flat normals and corner arcs |
| Outlet hex shoulder | Y 54.47 | Observed annular face |
| Overall length | 63.65 | Rounded tip of the outlet stub |
| Exposed outlet stub length | 9.18 | Shoulder to tip; not measured engagement |
| Maximum stub root diameter | 14.20 | External root envelope, not a thread specification |

The two wrench sections have different lengths and clipped corners. Short conical
sections approximate the turned rounds. The external thread uses a smooth crest
envelope. The visible mouths have shallow bores with unobserved display closures;
the scan does not establish the regulator's internal passages, diaphragm, spring,
thread geometry, pressure setting or sealing performance.

## Capture and measurement

The untouched native projects, preview clouds, fusion outputs and capture manifest
are retained in
`~/Documents/3D Scans/2026-09-23-wr1110-regulator/`. Pass 1 contains 858 frames and
443,305 fused points; the rolled pass contains 863 frames and 457,527 fused points.
Revo Scan 6.3.2 used MINI 2 High Accuracy, feature tracking, normal object mode,
colour off, exposure 1, base removal off and a 120–250 mm range. Fusion spacing is
0.10 mm; smoothing, mesh hole filling and rescaling are not applied.

[`analyze_scan.py`](analyze_scan.py) finds the marker-covered table in each native
preview, fits the exposed barrel at unit scale, locates the inlet face, and clocks
the wrench-flat normals. The owner's half turn selects the complementary hex
orientation, which the symmetric flats otherwise determine only modulo 60°.
Only the surface above the local support exclusion plane is retained from each
pass. Putty and table observations remain in the archived inputs. A narrow angular
gap on one side is covered by the fitted analytic form rather than filled scan
triangles. Small surface marks and the vent are not resolved as model features.

[`scan-measurements.json`](scan-measurements.json) records source hashes, rigid
transforms, regional selections, plane statistics and the common observation
strip. [`scan-profiles.png`](scan-profiles.png) shows the two retained surfaces.
Optical scale and spray thickness are not independently calibrated; the fitted
precision is not a statement of absolute accuracy.

[`validate_scan.py`](validate_scan.py) compares observations with the CAD surface
without dropping distant points. At 0.25 mm observation sampling and 0.025 mm CAD
tessellation, 95% of retained observations are within 0.204 mm; the mounting barrel's
95th-percentile distance is 0.019 mm. Thread-envelope differences reach 0.55 mm,
and the maximum over all regions is 0.68 mm at a visible mouth. The full regional
results and diagram are in [`scan-model-check.json`](scan-model-check.json) and
[`scan-model-check.png`](scan-model-check.png).

## Appliance integration

`barrel()` supplies the enclosure-back-top cradle and the neighboring GASHER
placement datum. With the shared 0.15 mm radial slip, the WR1110 seat is Ø19.17 mm.
Its 9.5 mm rib occupies the centre of the 35.4 mm barrel, leaving 12.95 mm of round
band at each end. The inlet location remains the assembly's bulkhead-derived
station; connected parts, gas routes and ceiling reliefs derive from that placement.
The regulator-to-check U-turn also respects the carbonated-water cradle's aft
flank, keeping the gas tube 1.1 mm beyond the rib with R14 bends.

`_gas_chain.py` limits its nominal female-adapter insertion to the 9.18 mm exposed
stub, so the adapter cannot start inside the hex shoulder. Shoulder seating remains
an assumption until the actual PI450822S is installed. The modeled regulator plus
adapters spans 98.97 mm between tube mouths. GASHER dimensions, gray-adapter envelopes
and actual made-up reaches remain nominal, as the assembly scorecard states.

[`integration-check.json`](integration-check.json) records the current placement, gas
route lengths, adapter fit, printed mesh checks and the assembly’s 99 passing gates.

```sh
tools/cad-venv/bin/python hardware/reference/wr1110-regulator/analyze_scan.py
tools/cad-venv/bin/python hardware/reference/wr1110-regulator/wr1110_regulator.py
tools/cad-venv/bin/python hardware/reference/wr1110-regulator/validate_scan.py
```
