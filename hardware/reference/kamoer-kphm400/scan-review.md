# Kamoer pump scan and contact review

The two native fused scans support the pump's two rigid bearing faces, front-cover rim and
molded outlet-casing stations. The cap uses four exposed pressing rails over the skirt lands;
the fixed bay floor clears the front rim along the complete cartridge insertion path. The
fitted side walls, skirt lands and locating profiles retain their local geometry.

The corrected parts still require a dry assembly with both physical pumps. Scan agreement and
CAD clearance do not establish clamp force, operating rigidity or endurance.

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
complementary observations are sufficient for the contact corrections below. No specific third
view is required for them. Hidden pump internals and sealed cavities are outside this review.
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

The physical pump rests 0.251 mm below the holder station datum on its skirt lands.
`_enclosure_interface.pump_seated_drop` is shared by the pump placement, holder-datum recovery
and cap contact calculation. The manifold's four outlet paths and carried tee axes consume
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
The conflicting floor contact would hold the pump above the intended skirt seat, partly
consuming the cap gap. It does not provide the intended clamp load path.

The production construction follows these measured interfaces:

- The continuous fixed floor is relieved by 2.6 mm from its pump-neutral datum. The cradle's
  bearing block follows that same flat plane, with no local pocket lip to obstruct withdrawal.
  At the frozen station fixture, it retains 4.015 mm of stock and gives the minimum observed
  front rim 0.340 mm air. The conservative declared rigid envelope has 0.329 mm air. Fresh
  assembly placement determines the absolute floor height and stock.
- Two 3 × 32 mm flat rails per pump extend from the cap bridge to the nominal flange plane,
  8 mm above the existing skirt lands. Their X bands are −32…−29 and 29…32 mm, and Y is
  −16…16 mm about the rear motor axis. These are inspected outer-rim regions clear of the
  flexible outlets and mounting-hole centers. The actual contact area is the pump rim,
  not the full nominal printed rail face.
- The cap has 0.25 mm downward screw adjustment over the measured rim-height range. At maximum
  closure the bridge still has 1.75 mm clearance to the holder datum, and the screw tips have
  0.25 mm remaining pilot depth. The cap crown, screw-head seats, fitted octagonal openings
  and skirt lands keep their local datum relationship.

The floor grows from front-top's print bed. The cap prints crown-down, so the terminal rail
bearing faces face print-up. Rail sides are exposed; the correction adds no supported bearing
face or enclosed support-removal pocket. Production support assessment still belongs to the
fresh slice and physical print.

## Checks and remaining acceptance

[check_pump_contacts.py](check_pump_contacts.py) builds the current cap and floor at an explicit
archived station fixture. [contact-check.json](contact-check.json) records one valid cap solid,
zero native-cradle interference at sampled lifts −0.25, 0, 0.25, 5, 35 and 70 mm, real planar
rail faces over the selected observations, screw/bridge travel, minimum floor stock, and
continuous flat head insertion corridors. This bounded check is separate from the complete
current assembly build and its tube/collet alignment checks.

Before production acceptance, the physical assembly needs:

1. Both pumps seated on the skirt lands with the front rims clear of the floor. Tightening
   the cap must remove vertical play before the bridge or screw tips bottom.
2. Straight cartridge insertion and withdrawal, followed by cap removal and separate upward
   pump removal on the bench.
3. Four marked tube insertion depths, secure collet capture and carrier release, followed by
   a primed pumping/leak check. Silicone outlet flexibility is not a substitute for this test.

The reference's coarse holder-derived surfaces remain useful for layout. These selected
independent observations qualify the named interfaces; they do not certify every reference
surface as a scan fit.

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
