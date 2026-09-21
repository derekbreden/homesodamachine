# G Ganen diaphragm pump

Derek identifies the received sample as **G Ganen, ASIN B07F35PTFR**, and selects
it for the enclosure. The reference uses three complementary native scans at
**unit millimetre scale**. No caliper or independent scale calibration is
available. The 0.10 mm fusion spacing is not a dimensional tolerance.

The native reference represents the occupied external envelope. Its rigid
housing, two barbs, visible crown features and four removable rubber sliders are
separate named bodies. Vent openings, shallow casing recesses, driver recesses
and hidden foot cavities are filled for clearance. The lower-cradle envelope
also fills its reentrant underside channels. These volumes are **not
material, mass or strength inputs**. The foot solids cannot establish screw
passage or clamp engagement.

## Evidence and frame

[scan-evidence.json](scan-evidence.json) records direct sample/material/flow
authority and the archived source hashes. The feet-up, on-back and feet-down
captures contain 9,702,869 observations in total. They retain native fusion only;
no isolation, smoothing, hole filling, scale fit or rewritten source cloud is
used. The per-pass rigid registrations retain disjoint fitting and held-out
regions, including the actual overlap fractions.

The frame has **X = 0 at the observed motor/head junction**, positive X toward
the motor rear, and **Z = 0 at the average first-pass unloaded foot bearing
plane**. Y completes the right-handed frame. Each foot's own bearing plane is
retained. Z = 0 does not assert that four free rubber feet are exactly coplanar.
The motor's measured direction and its small inclination to that datum remain
separate from the projected X direction.

The selected exposed motor arc fits **49.110 mm diameter**. Every fifth selected
observation is withheld from the fit; its absolute p95 residual is **0.073 mm**.
This is agreement with one scanned arc, not independent dimensional accuracy.
The native straight-can envelope fills real ventilation openings; the molded
lower housing and rear cap follow the separate casing observations.

Derek identifies flow as right while reading the `4002` label upright, and
resolves the intended mounted direction as **enclosure −X**. The intended
positive 90° Z rotation maps reference +Y to enclosure −X, so **+Y is discharge
and −Y is suction**. This establishes identity and intended rotation; production
translation is a separate integration decision.

## Ports

The third pass observes both terminal faces. Ports are measured independently;
neither is a reflected copy of the other. Tip coordinates and axes refer to the
external barb, with the axis pointing outward.

| Interface | Tip X, Y, Z (mm) | Outward axis |
| --- | --- | --- |
| Suction / −Y | −33.288, −37.261, 26.724 | 0.00465, −0.99999, 0.00221 |
| Discharge / +Y | −33.259, 37.017, 26.769 | 0.00253, 0.99994, 0.01045 |

The exterior profiles cover about 13.2 mm from their measured root band to the
tip. Crest/root diameters and the full profile are stored per port. That length
is not a completed hose insertion or retention test. Earlier-view residuals
remain explicit: the second-pass positive-Y tip is about 0.74 mm higher than the
third-pass tip after rigid casing registration. That disagreement is not removed
by averaging, symmetry or a fitted scale.

## Mounting

Derek confirms that all four feet are **flexible rubber, slide fore/aft along the
casing channels, and can be removed entirely**. Their captured X positions are
independent poses, not a fixed bolt pattern. The visible upper rail faces
continue across approximately X = 0.4–76.9 mm; this is observed face extent, not
a certified hard travel stop or hidden clip engagement limit.

All four openings are obround. Complete first-pass sections where both flanks
and ends are visible measure about **4.07–4.67 mm wide** and **6.38–6.92 mm long**.
Some other sections show only one wall. In particular, the full rear-positive-Y
mouth and the narrowest through-depth section are unqualified. A partial-wall
fit is never used as a smaller established throat.

The local opening axes, depths, widths, lengths, coverage tests and individual
bearing planes remain accessible in `mount_slots()` and in
[registered-measurements.json](registered-measurements.json). Per-view unloaded
pad-top planes are in [interface-measurements.json](interface-measurements.json).
The third-view median top heights range from about 6.44 to 7.15 mm above the
retained datum. These are not compressed clamp-stack dimensions.

For a simple mount using the purchased feet, the remaining physical observation
is a freely passing actual M3 screw through **all four complete slots**, plus
flat seating and upstand clearance of the selected washer. This does not need a
removed-foot scan. A replacement foot or new rail-gripping interface would need
its hidden clip geometry and retention qualified separately. Mount positions,
washer coverage, screw length and rubber compression are integration checks.

## Native model and checks

[g_ganen_pump.py](g_ganen_pump.py) builds the native reference from
[reference-parameters.json](reference-parameters.json). It exposes `suction()`,
`discharge()`, `port_profile(name)`, `mount_slots()`, `sliding_rails()` and
`mount_seat_z()`. There is no invented common `HOLE_D`, fixed rectangle or single
port diameter/length.

The detailed STEP contains **26 valid solids and 29,636 faces**. Its source,
reports, STEP and matching viewer payload are bound by
[artifact-manifest.json](artifact-manifest.json).

[native-validation.json](native-validation.json) checks native solid validity,
port-root continuity, flow mapping, unit-scale inputs and disjoint native scan
observations. Its residuals distinguish observations outside the envelope from
surfaces inside filled openings. The casing, barbs and crown have separate
readings. A mesh comparison does not qualify a screw passing through a filled
foot envelope. [native-validation.png](native-validation.png) shows the retained
comparison regions.

In the feet-down view, outside-distance p95 is 0.071 mm on the selected motor
surface, 0.191 mm on the lower cradle and 0.432 mm on the rear cap. The two barb
surface absolute p95 residuals are 0.072 and 0.092 mm in that view. Earlier views
have larger disagreements, retained in the report; these numbers are not a
uniform fit tolerance or proof of a completed physical mount.

The two observed lead/casing transition regions are retained separately. These
surface scans do not cleanly separate a protruding rigid strain relief from the
flexible leads there; no rigid lump or fixed loose-wire route is invented. Their
wire path belongs in enclosure integration. Loose leads and scanning putty are
excluded from rigid fitting. Absolute scanner accuracy, spray thickness, loaded
rubber behavior, pump internals and hydraulic performance remain unmeasured.

The production mount and tube routes remain separate from this reference. The
existing SeaFlo consumer is not silently replaced by importing this module.
The bounded integration sequence and placement traps are in
[integration-handoff.md](integration-handoff.md). Native query cost is recorded
separately in [native-query-cost.json](native-query-cost.json).

## Reproduce

Run from the repository root with the archived sources available at the recorded
paths. Every native cloud is checked against its SHA-256 before measurement.

```sh
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/scan_tools.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/register_scan.py --selftest
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/selftest_analysis.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/analyze_scan.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/register_scan.py hardware/reference/g-ganen-pump/pass-02-registration-config.json --out hardware/reference/g-ganen-pump/pass-02-registration.json
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/register_scan.py hardware/reference/g-ganen-pump/pass-03-registration-config.json --out hardware/reference/g-ganen-pump/pass-03-registration.json
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/analyze_registered.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/derive_casing.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/measure_interfaces.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/build_reference.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/validate_reference.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/g_ganen_pump.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/benchmark_native.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/freeze_reference.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/freeze_reference.py --check
```

The native exporter produces the STEP assembly and its viewer payload. Native
preview artifacts belong outside `hardware`, for example under
`.cache/g-ganen-reference-preview/`; publication scans STEP files even in ignored
directories. The independent source clouds are never written by these tools.
