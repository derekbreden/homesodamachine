# Kamoer pump scan and contact review

Derek confirms that the existing assembled cartridge and cap hold both pumps firmly with
no vertical play. [physical-fit.json](physical-fit.json) records his report and photograph.
The production cap has a broad underside, fitted octagonal bosses and Ø37 motor openings.
Its surrounding crown reaches the cartridge top, with two Ø45 openings around the motor ends
and spade terminals. The cap has no projecting underside rails.

The two native scans independently describe selected rigid surfaces and outlet-casing
stations. Their transform assumes that the underside strips seat on the modeled cradle lands;
it does not independently identify the assembled cap's complete contact path.

## Evidence and registration

The capture archive is `/Users/derekbredensteiner/Documents/3D Scans/2026-09-20-kamoer-pump`.
Its `capture-manifest.json` owns acquisition details. Full clouds, native projects and frozen CAD
exports remain there; [scan-evidence.json](scan-evidence.json) records their paths, digests and
ownership of observations.

| Native scan | Points | SHA-256 |
|---|---:|---|
| `pass-01-upright/Fused 0920_1 (0.10mm).ply` | 2,076,077 | `8df2a6f04f30afec5655df8c1d051a6c9f280283d83fc2f7c197598a54a14c97` |
| `pass-02-remounted/Fused 0920_1 (0.10mm).ply` | 3,053,059 | `0247db27a6d9a219d0bb00c6c033c97e8e142e15ae20116a2d9edccd21c24fc1` |

Both are unsmoothed native 0.10 mm fusion exports with fixture/putty observations retained.
Analysis selects inspected rigid regions; it does not rewrite either cloud. Registration is
six-degree rigid motion at scale **1.0**, using shared motor, flange side and front-face patches.
The head envelope copied from the fitted holder is not a registration target.

[scan-registration.json](scan-registration.json) preserves the independently observed initial
frames, named fitting and validation regions, final transforms and bidirectional residuals.
Final fitting point-to-plane absolute p95 is 0.158 mm. Withheld molded casings have approximately
0.21–0.23 mm bidirectional point-to-plane p95; withheld skirt surfaces approximately
0.15–0.17 mm. These residuals describe overlap agreement, not absolute scanner accuracy or a
manufacturing tolerance. The scan spray thickness is unmeasured.

Pass 2 supplies the opposite head side and underside bearing strips obscured in pass 1. Those
complementary observations support the surface readings below. No specific third
view is indicated by the current review. Hidden pump internals and sealed cavities are outside this review.
The independent head Y datum is not fully established: the existing fitted head/rear-axis
relationship is retained, with the observed motor axis aligned to the native rear opening.

## Outlet identity and station

**Derek identifies the short terminal pieces as inserted 1/4-inch LLDPE stubs in the pump's
silicone.** They are external tubing, not integral rigid pump barbs. Neither the silicone nor
the inserted stubs define rigid registration, scale, pump envelope or integral part dimensions.
The complete outlet stack is withheld from alignment. Only the rigid molded casing roots are
used for the independent station comparison.

The twelve casing-section fits across both passes place the centers at Z −28.43 to −28.53 mm
relative to the observed motor-facing flange datum. The reference outlet station is therefore
`arch_plane_z = pump_case.skirt_bottom_z`, or −28.5 mm, with
`outlet_above_skirt_bottom = 0`. The oval exterior sections do not independently justify
changing the fitted circular-bottom/straight-shaft openings. A native-cradle point containment
check of rigid casing roots finds at most 0.235/0.183 mm penetration in pass 1 and
0/0.040 mm in pass 2. That discrepancy is not consistent across the passes and is comparable
to registration/spray uncertainty; it is not a large repeatable clash or a zero-clearance
certification. Physical insertion remains the acceptance check.

The assembly model places the pump 0.251 mm below the holder station datum on its skirt lands.
`_enclosure_interface.pump_seated_drop` is shared by the pump placement, holder-datum recovery
and outlet calculation. The manifold's four outlet paths and carried tee axes consume
that seated pose. The tee reference's own measured length can change the whole manifold's
placement; that global placement change is distinct from the local pump seating correction.

## Contact geometry

[scan-measurements.json](scan-measurements.json) contains the exact selections and native
comparison. The five baseline CAD digests are frozen separately from regenerated production
outputs. The baseline placement comes from the actual scanned underside strips seated on the
actual native cradle lands; no extra plate thickness is used to place the pump.

| Independent observation at the recorded station | Result |
|---|---:|
| Native cap underside above scanned motor-facing flange strips | median 2.200 mm; p05–p95 2.070–2.388 mm |
| Rigid observed topography reaching that cap footprint | none; nearest observation remains 1.954 mm below |
| Rigid head-front rim versus the native fixed floor, with skirt seated | down to −1.260 mm clearance |
| Rim heights under the selected pressing rails, above underside bearing plane | 7.813–8.130 mm |
| Cross-pass fitted underside-plane absolute p95 residual | 0.079 mm |

The repeated front-face structure is the native rigid molded cover and rim in both scans.
These readings are conditional on the stated seating transform. The flange-only gap does
not establish loose pump retention; Derek's assembled part has no observed vertical play.

The cap's broad underside stands 2 mm above the holder datum. The boss opening, Ø37 motor
bore and screw seats retain their fitted geometry. The crown reaches the cartridge top and
has two Ø45 open terminal wells above the fitted motor bores.

The continuous fixed floor is relieved by 2.6 mm from its pump-neutral datum. At the retained
native station it has 4.015 mm of stock and gives the scanned front rim 0.340 mm air under the
stated transform. The floor is one flat insertion lane. Its effect on the physically accepted
cradle is recorded in the [fitted-well audit](fitted-well-audit/README.md). The lower well
matches 208 sampled triangles of the retained printed input within 0.004 mm. Changing
only the floor relief leaves the native well and cap geometry unchanged; the matching
new cartridge extends to the lower floor. Both scanned front rims project through the
printed cradle's open wells. An older cartridge placed on the new floor would lower
the complete cartridge and pumps, so the trial uses the matching new cartridge.

## Checks and assembly test

[check_pump_contacts.py](check_pump_contacts.py) and [contact-check.json](contact-check.json)
record the current cap at the archived station: one valid solid, a clear sampled vertical
path through the native cradle, open motor-terminal wells and a flat floor corridor.
The fitted boss/can band is compared to vertices and triangle centers from the retained
September 13 print input in a common pump-local frame. The maximum surface discrepancy is
0.012 mm, within the mesh chord approximation. The input archive and original STL hashes
identify that comparison; Derek has not identified his physical part by print date.

The cap prints crown-down. Its two upper-well transition faces are flat supported annuli.
Their support is open to the bed and exits axially through the Ø45 wells before pump assembly.
The fresh production slice supplies the final support reading.

The complete enclosure print tests terminal-connector space, cartridge insertion and
withdrawal, all four marked tube insertion depths, collet capture, carrier release and spring
feel. Primed operation supplies the leak check. These are physical acceptance results of the
assembled trial, not prerequisites for printing it.

## Reproduce

From the repository root, with the external capture archive present:

```sh
tools/cad-venv/bin/python hardware/reference/kamoer-kphm400/register_scan.py selftest
tools/cad-venv/bin/python hardware/reference/kamoer-kphm400/register_scan.py hardware/reference/kamoer-kphm400/scan-registration.json --out /tmp/kamoer-registration-check.json
tools/cad-venv/bin/python hardware/reference/kamoer-kphm400/analyze_scan.py --out /tmp/kamoer-measurements-check.json
tools/cad-venv/bin/python hardware/reference/kamoer-kphm400/check_pump_contacts.py selftest --out /tmp/kamoer-contact-check.json
```

`analyze_scan.py` accepts `--archive` and `--native-dir` for a relocated archive. Every raw cloud
and frozen CAD input is verified by SHA-256 before measurement. The registration selftest uses
synthetic surfaces and requires neither scans nor CAD exports. The contact audit requires the
archived native cradle and remains separate from hermetic build tests.
