# G Ganen diaphragm pump

The [exterior replica](replica-detail.md) separates the observed flat head-cover
land from its clean round and capsule crown features. The detailed source and
the separate conservative integration envelope retain their own scope below.

Derek identifies the received sample as **G Ganen, ASIN B07F35PTFR**, and selects
it for the enclosure. The reference uses three complementary native scans at
**unit millimetre scale**. Derek measures the rubber pads at approximately 7 mm thick; no independent scan
scale calibration is available. The 0.10 mm fusion spacing is not a dimensional tolerance.

The native reference represents the occupied external envelope. Its rigid
housing, two barbs, visible crown features and four removable rubber sliders are
separate named bodies. Vent openings, shallow casing recesses, driver recesses
are filled for clearance. The common foot retains its visible slot, lower
reliefs and exposed clip mouth. The lower casing follows its transverse grooves;
its coarse convex clearance bound is metadata only. These volumes are **not
material, mass or strength inputs**. The foot model does not establish the hidden slot throat, clip retention or
loaded rubber compliance.

The [bare-underside photographs](underside-observation/README.md) identify the
fixed rails, finite molded wire cover and flexible leads. Clear sections between
the sliders supply the rail profile through scan occlusions. The wire cover ends
at approximately reference X = 64.7 mm; the motor and rear cap supply the rigid
surface beyond it. Its lower face projects 1 mm farther down at the front:
native Z3.210583 mm at X0 and Z4.210583 mm at the measured rear-center X64.65.
Derek's physical observation supplies that projection. The
[construction observations](underside-observation/rigid-underside.json) retain
the scan fit separately from that construction datum, the axial ends and cap
interpolation scope.

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

Derek confirms that all four feet are **identical flexible rubber, slide fore/aft
along the casing channels, and can be removed entirely**. One shared native
shape uses the approximately **7 mm pad thickness**, rounded visible scan
profiles and open slot/reliefs; see [common-foot/README.md](common-foot/README.md). Their captured X positions are
independent poses, not a fixed bolt pattern. The visible upper rail faces
continue across approximately X = 0.4–76.9 mm; this is observed face extent, not
a certified hard travel stop or hidden clip engagement limit.

All four openings are obround. Complete first-pass sections where both flanks
and ends are visible measure about **4.07–4.67 mm wide** and **6.38–6.92 mm long**.
Some other sections show only one wall. In particular, the full rear-positive-Y
mouth and the narrowest through-depth section are unqualified. A partial-wall
fit is never used as a smaller established throat.

The local opening axes, depths, widths, lengths, coverage tests and individual
bearing planes remain in the native reference parameters and in
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

[reference-parameters.json](reference-parameters.json) retains the independently
measured ports, rail observations, mounting slots and datum frame. The saved
detailed reference is an input to [replica.rs](replica.rs), which constructs the
exterior model used by the native equipment assembly.

The detailed STEP and matching viewer payload have native solid validity and
bounds recorded in [native-validation.json](native-validation.json). The family
[artifact manifest](artifact-manifest.json) is held for the installed mount review.

[native-validation.json](native-validation.json) checks native solid validity,
port-root continuity, flow mapping, unit-scale inputs and disjoint native scan
observations. Its residuals distinguish observations outside the envelope from
surfaces inside filled openings. The motor, cradle, barbs and crown have separate
readings. The visible foot model does not qualify an unseen minimum slot throat or
compressed rubber stack. The [scan comparison image](native-validation.png)
belongs to the [retained source report](under-head-clearance/prior-native-validation.json).
The current switch passage is assessed by its [rigid underside measurements](under-head-clearance.json).

In the feet-down view, outside-distance p95 is 0.071 mm on the selected motor
surface. The two barb
surface absolute p95 residuals are 0.072 and 0.092 mm in that view. Earlier views
have larger disagreements, retained in the report; these numbers are not a
uniform fit tolerance or proof of a completed physical mount.

The [under-head tube photographs](under-head-tube/physical-observations.json)
show a tube passing through the head-side space on the received sample. They
support the [V-A route study](../../manifold-layout/studies/east-feed/README.md);
they do not establish installed enclosure clearances.

The [flat-elbow observation](under-head-tube/flat-elbow-observation.json)
demonstrates a union elbow resting flat beneath that head on the received pump.
The [rigid underside measurements](under-head-clearance.json) retain that open
space below the switch casing. The native model excludes the flexible lead
loops from rigid occupancy there; the switch's lower front block and the head
shoulder remain. The [scoped update source](https://github.com/derekbreden/homesodamachine/blob/0785c32f89a6e08609e5348aa2beb0096d560326/hardware/reference/g-ganen-pump/under-head-clearance/update_reference.py)
is archived in Git with its bound detailed reference and study inputs.

The two observed lead/casing transition regions are retained separately. These
surface scans do not cleanly separate a protruding rigid strain relief from the
flexible leads there; no rigid lump or fixed loose-wire route is invented. Their
wire path belongs in enclosure integration. Loose leads and scanning putty are
excluded from rigid fitting. Absolute scanner accuracy, spray thickness, loaded
rubber behavior, pump internals and hydraulic performance remain unmeasured.

Production placement uses the [native equipment constructor](/tools/hsm/machine-data/src/equipment.rs).
Cap mounts and tube routes belong to the native layout and retain their own assembly checks.
For under-head routing, use this detailed reference or the
[selected study mesh](../../manifold-layout/studies/east-feed/parts/pump-under-head-source.json).
The frozen production integration envelope includes additional occupied space
in that passage.
The bounded integration sequence and placement traps are in
[integration-handoff.md](integration-handoff.md). Native query cost is recorded
separately in [native-query-cost.json](native-query-cost.json).

## Native replica

The replica reads the saved detailed payload and its parameter records. Regenerate
it through the existing native sandbox example:

```sh
tools/run -- cargo run --release --locked -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-sandbox \
  --example g-ganen-replica -- hardware/reference/g-ganen-pump
```

The [scan, registration and envelope source programs](https://github.com/derekbreden/homesodamachine/tree/0785c32f89a6e08609e5348aa2beb0096d560326/hardware/reference/g-ganen-pump)
are archived in Git. Their saved measurements and hash-bound model inputs remain
with the reference; they are not an ongoing scan pipeline.
