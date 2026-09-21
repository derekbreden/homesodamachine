# Tee integration checks

The measured PP0208E envelope and operating faces are integrated into the production
reference, manifold, carrier, release-wall journals and water split. The complete
enclosure is an assembly trial for spring retention, tension, rigidity and release
feel. Native geometry and current slices qualify that print; the physical behavior
is measured with the assembled print.

| Interface | Current dimension |
|---|---:|
| Nominal collar diameter used for the caliper datum | 16.3 mm |
| Rounded scanned collar envelope, including draft | 16.5 mm |
| Rounded fixed root envelope | 14.0 mm |
| Printed journal diameter | 17.0 mm |
| Carrier trough radius | 8.75 mm |
| Run span, extended / both sleeves pressed | 42.5 / 39.2 mm |
| One run sleeve's travel | 1.65 mm |
| Branch outside width, extended / pressed | 30.5 / 29.0 mm |
| Branch face from run axis, extended / pressed | 22.35 / 20.85 mm |
| Branch terminal travel / connected nose gap | 1.50 / 0.50 mm |
| Carrier release / connected / aft-stop offset | 0 / 2.00 / 4.50 mm |
| Tee axes across X | ±22.35 / ±82.10 mm |
| Tee bearing line / axis elevation | Y111.790 / Z186.174 mm |
| Retained backing at / above each tee | 2.5 / 5.504166 mm |
| Deck separation | 60.95 mm |
| Air at complete aft-valve post insertion | 0.25 mm |
| Spring axes | X±97.535, Z211.209 mm |
| Fixed spring floor / moving release floor | Y90.040 / Y109.390 mm |
| Circular release aperture | Ø8.5 mm |

The branch-axis stations subtract the nominal 8.15 mm back-collar radius from
[Derek's outside-width readings](../../../reference/jg-pp0208e-tee/branch-operating-measurements.json).
The conservative 8.25 mm clearance radius is a separate datum. The scanned collar
envelope is a rounded reading of the sample, not a manufacturing tolerance. Root/collar
fit intervals are interior patches; their endpoints are not molded shoulder edges.

## Terminal-ring bearing

Derek identifies the small outermost terminal ring as the moving part. The larger
reduced barrel behind it stays fixed. The [terminal-face review](../../../reference/jg-pp0208e-tee/terminal-bearing-review.json)
reads the existing registered scan at its original scale. Its near-planar front face
has observed bearing outside the Ø8.5 aperture in all 36 ten-degree sectors: 20.07 mm²
of projected face, including 99.73% of the R4.25–4.75 mm band. Sampled 0.35 mm lateral
offsets retain observed face in every sector.

This supports the aperture for the complete enclosure assembly trial. No additional
tee scan or pre-print rear-seam measurement is required for this face-pushing interface.
The approximate side-wall OD is 10.62 mm; neither its exact OD nor its rear seam is
caliper-qualified. Projected scan area is not guaranteed simultaneous contact area,
a strength rating or a manufacturing tolerance. The native R4.26–5.00 mm witness
proves plate stock only: R5.00 is not a measured minimum terminal-face radius.

The physical trial checks that every actual ring bears on the flat shoulder, reaches
release over its measured 1.5 mm travel, and permits tube withdrawal and relocking
without the larger fixed barrel bottoming on the plate. If contact is uneven, the
smallest useful follow-up is the affected ring's flat-face outside diameter and its
contact mark on the plate.

## Carrier and springs

The [integrated two-half carrier](../tee-carrier/simple-carrier-study/README.md) uses
an integral broad-wall latch and broad bearing regions. Its moving spring cups are
closed; the matching fixed cups belong to the enclosure. No joint screws, separate
keeper or retained spring guide pin is used. The measured springs are 27 mm free,
approximately 7 mm compressed and Ø6 mm. This capture design does not require spring ID.

Spring-floor separation is 19.35 / 21.35 / 23.85 mm at release / connected / aft stop.
Both-end retention, actual spring force, unequal-hand motion, assembly effort and
whole-carrier rigidity remain full-enclosure trial observations. The native cup,
stock, neighbor and installation checks are named by the carrier's
[artifact manifest](../tee-carrier/simple-carrier-study/artifact-manifest.json).

## Evidence and complete-enclosure scope

[`tee-integration.json`](tee-integration.json) and the
[measured-branch fixture](branch-propagation/) record their exact source/native input
digests and captured geometry. They are bounded integration evidence, not a release
of every current enclosure component. The [routing corrections](routing-clearance/)
cover the water-split flank, retained anchors and reservoir-A fill lane. Their current
whole-pack checks accompany the coordinated Box/enclosure generation.

The pump-only placement pair is `pump_station_lead = -0.074` and
`PUMP_BARBS_TO_RELEASE_PLANE = 5.526` mm; it preserves the tee/deck/valve stations.
Kamoer's accepted fitted cap geometry, raised open crown and current cartridge fit
checks belong to the separate pump evidence. The complete enclosure still requires
matching generated parts, full native paths/clearances, current support-removal review
and exact slice identity. The [root readiness report](../print-readiness.md) owns that
combined status.

```sh
tools/cad-venv/bin/python hardware/reference/jg-pp0208e-tee/analyze_terminal_bearing.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-readiness/verify_tee_integration.py
```

The first command only reads scan/measurement evidence. The second builds the bounded
native region in memory and refreshes its local report; full enclosure installation
and current slice checks remain separate.
