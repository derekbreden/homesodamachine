# DIGITEN flow sensor — measured reference

The purchased DIGITEN inline flow meter is represented by an analytic exterior
for mounting, tube routing, lead routing and enclosure clearance. The MINI 2
capture records the actual sample. The STEP is a reference for integration;
its hidden turbine, seals and electronics are not reconstructed.

The ports are coaxial, but their axis is offset from the round housing centre.
That offset, the fixed mounting collars and the complete cover envelope matter
for placement. Dimensions below are millimetres.

| Feature | Model dimension |
|---|---|
| Collet face to face | [61](PORT_SPAN) |
| Cover flange diameter | [35](FLOW_BODY_DIA) |
| Overall depth, including screw heads | [28.3](BODY_LEN) |
| Housing centre toward the lead, above the port axis | [8.9](BODY_OFFSET) |
| Fixed port neck diameter | [15.9](NECK_DIA) |
| Fixed collar maximum diameter | [18.3](FLOW_PORT_DIA) |
| Fixed collar, measured outward along either port | [19.6](COLLAR_START) to [26.8](COLLAR_END), length [7.2](COLLAR_LEN) |
| Separate collet beyond the fixed collar | [3.7](COLLET_LEN) long |
| Lead-root envelope | [6](WIRE_ROOT_WIDTH) × [3](WIRE_ROOT_DEPTH) × [1.5](WIRE_BOSS_LEN) |

The collar is gently drafted, with radius 8.95 mm at its inner end and 9.15 mm
at its outer end. `mounting_profile(sign)` supplies the fixed neck and collar
sections. Mounts must leave the separate collet free to move.

## Frame and interfaces

The origin is the midpoint of the two collet faces on the port axis. **X** is
along that axis; **+Y** points toward the label; **+Z** points toward the lead
exit. With the label facing the viewer and the lead above it, **+X is left**.
The round housing centre is at `(0, 0, 8.9)` when projected into the XZ plane.

| Function | Position | Outward direction |
|---|---|---|
| `inlet()` | `(−30.5, 0, 0)` | `−X` |
| `outlet()` | `(+30.5, 0, 0)` | `+X` |
| `wire_exit()` | `(0, 14.8, 26.5)` | `+Z` |

The fluid function names currently retain the repository convention: flow from
−X to +X. **The molded flow arrow has not yet been confirmed on the sample.**
The scan establishes the two port stations, not their hydraulic handedness.
The arrow must point left in the label-facing, lead-up view for those names to
match this convention.

The complete rigid exterior bounds are X `−30.5…30.5`, Y `−9.4…18.9`,
Z `−9.15…26.5`. The flexible pigtail needs routed space beyond `wire_exit()`.
The modeled mouth is Ø6.5 mm with a 6 mm visual recess; this recess is not a
measured tube insertion stop or a reconstruction of the flow passage.

## Capture and fidelity

Five passes on 20 September 2026 cover both cover faces, level and 15° tilted
views, and a higher-exposure view of the dark band and collet noses. Revo Scan
6.3.2 used MINI 2 High Accuracy / Feature / Normal, no colour capture, and
0.10 mm fusion spacing. All native projects, raw frames, calibration files and
original fused clouds are preserved with SHA-256 hashes in
`~/Documents/3D Scans/2026-09-20-flow-meter`. The rigid registrations use no scale
change. No hole filling or smoothing is applied to the recorded point clouds.

The model retains the drafted rotor shell, cover flange and bevel, four screw
bosses and head envelopes, six underside ribs/recesses, offset port necks,
fixed collars, collet stems and visible mouths, one locking-clip position per
end, and the lead root. Curved and planar primitives express the stable shape.
Small moulding blends, lettering, screw-drive recesses, surface texture and the
flexible lead are omitted. The underside centre recess is simplified to its
outer envelope. Invisible interiors carry no asserted geometry.

The locking clips can rotate. The modeled positions and the final collet
observations come from underside passes 04/05; upright clip positions are
excluded beyond the fixed collar. The reference does not combine different
clip rotations into extra material.

The retained exterior contains 642,615 observations. At deterministic 0.3 mm
comparison spacing, 98,652 observations have a median distance to the analytic
exterior of 0.089 mm and a 95th-percentile distance of 0.630 mm. The fixed
collars have a 0.046 mm median and 0.155 mm 95th percentile; the cover and
underside reach about 0.71 mm at the 95th percentile because their smaller
surface details are simplified. These are scan/model discrepancies, not
manufacturing tolerances. Absolute scale accuracy has not been independently
calibrated, and 0.10 mm point spacing does not establish accuracy. Surface
preparation for this sample was not recorded.

[scan-evidence.json](scan-evidence.json) records captures, hashes, registration,
measurements and modeling choices. [scan-model-check.json](scan-model-check.json)
records feature residuals against the exact generator SHA.
[model-check.json](model-check.json) is regenerated with the STEP and records
valid native solids, bounds and interfaces. Its `executed_producer_sha256`
hashes the source bytes actually executed, which Bazel normalizes. The scan
comparison's `model_source_sha256` hashes the full repository source bytes;
the two fields intentionally describe different inputs.

Generate from the repository root:

```sh
tools/cad-venv/bin/python hardware/reference/digiten-flow-sensor/digiten_flow_sensor.py
```

Recheck the preserved observations:

```sh
tools/cad-venv/bin/python hardware/reference/digiten-flow-sensor/validate_scan.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/reference/digiten-flow-sensor/digiten_flow_sensor.py`
