# Tee integration checks

The measured PP0208E envelope and operating faces are integrated into the production
reference, manifold, release-wall journals and water split. The complete enclosure is an
assembly trial for release feel. Native geometry and current slices qualify that print;
the physical behavior is measured with the assembled print.

| Interface | Current dimension |
|---|---:|
| Nominal collar diameter used for the caliper datum | 16.3 mm |
| Rounded scanned collar envelope, including draft | 16.5 mm |
| Rounded fixed root envelope | 14.0 mm |
| Printed journal diameter | 17.0 mm |
| Run span, extended / both sleeves pressed | 42.5 / 39.2 mm |
| One run sleeve's travel | 1.65 mm |
| Branch outside width, extended / pressed | 30.5 / 29.0 mm |
| Branch face from run axis, extended / pressed | 22.35 / 20.85 mm |
| Branch terminal travel / connected nose gap | 1.50 / 0.50 mm |
| Tee release / connected offset | 0 / 2.00 mm |
| Tee axes across X | ±22.35 / ±82.10 mm |
| Tee axis elevation | Z186.174 mm |
| Deck separation | 60.95 mm |
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

## Evidence and complete-enclosure scope

The [routing corrections](routing-clearance/) cover the water-split flank, retained
anchors and reservoir-A fill lane. Their current whole-pack checks accompany the
coordinated Box/enclosure generation.

The pump-only placement pair is `pump_station_lead = -0.074` and
`PUMP_BARBS_TO_RELEASE_PLANE = 5.526` mm; it preserves the tee/deck/valve stations.
Kamoer's accepted fitted cap geometry, raised open crown and current cartridge fit
checks belong to the separate pump evidence. The complete enclosure still requires
matching generated parts, full native paths/clearances, current support-removal review
and exact slice identity. The [root readiness report](../print-readiness.md) owns that
combined status.

```sh
tools/cad-venv/bin/python hardware/reference/jg-pp0208e-tee/analyze_terminal_bearing.py
```

The command only reads scan/measurement evidence; full enclosure installation and
current slice checks remain separate.
