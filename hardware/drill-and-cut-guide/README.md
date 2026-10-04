# Drill & cut bench guide

28 illustrated pages on 8.5 × 11 inch Letter: end plates, vessel tube, float rods,
water-inlet jet, rotator contact shoe, metal and plastic tubing, coverings, and
harness stock. The large setup pictures and the short action/check blocks follow
the weld-rotator guide's bench-reading pattern.

The guide is a hand-authored document. It has no Bazel target, no geometry-build
dependency, no card sync and no CAD imports. The PDF, cover and shelf sidecar are
committed. Source hashes and the selected small numeric inputs are recorded in
[`output/pdf/drill-and-cut-guide.sources.json`](/output/pdf/drill-and-cut-guide.sources.json).

## Operation inventory

| Pages | Operation | Procedure |
|---|---|---|
| 1-2 | Picture key, operation map and powered-cut setup | WEN manuals linked below |
| 3 | Chamfer both faces of all four endcap pilots | [`pressure-vessel.md` step 1](/hardware/assembly/pressure-vessel.md) |
| 4 | Spring-guided hand 1/4-18 NPT tapping from outside | Same |
| 5-6 | Locate and drill both blind rod registers; prove tip depth | Same; [`endcap_circular_dxf.py`](/hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py) |
| 7 | Inside lead-in / outside burr-only perimeter treatment | `pressure-vessel.md` steps 1, 3 |
| 8 | Deburr both vessel tube ends, ID and OD; check seating | `pressure-vessel.md` step 3 |
| 9-10 | Cut three float rods, deburr, hand-fit the carbonator rod | [`handwork.md`](/hardware/assembly/handwork.md), `pressure-vessel.md` steps 2, 5 |
| 11 | Measure candidate jet stock, elbow land and tapped-plate fit | [`water-inlet-jet.md`](/hardware/assembly/water-inlet-jet.md) |
| 12 | Saw a 50-60 mm handling blank | Same, step 1 |
| 13 | Split-jaw clamping and stopped-spindle grip/clearance trial | [`jet fixture`](/hardware/printed-parts/fixtures/water-inlet-jet/README.md) |
| 14 | Short axial 1/16-inch drill trial | `water-inlet-jet.md` step 1 |
| 15 | Saw and inspect the nominal 2 mm cap slice | Same |
| 16 | Hand-deburr the jet, wash, rinse and dry | Same |
| 17 | Section the welded trial through the axis and a second azimuth | `water-inlet-jet.md` step 3 |
| 18 | Crosscut the C110 rotator contact shoe | [`rotator fixture`](/hardware/printed-parts/fixtures/weld-rotator/README.md) |
| 19 | Clean square metal-tube cuts and bench-fit argon purge links | `water-inlet-jet.md` step 2; [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) |
| 20 | Square-cut LLDPE; inspect round ends and full insertion | [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) |
| 21 | Black/White faucet factory tube cut schedules | [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md) step 1 |
| 22 | Trim the three outlets flush at the printed faucet tip | [`faucet shell assembly`](/hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md) |
| 23 | Internal fluid color/ID cut plan, engagement and fit limits; PRV mouth | `internal-plumbing.md`; [`cold-core.md`](/hardware/assembly/cold-core.md) |
| 24 | Reinforced PVC pump-hose blanks, atmospheric vent stub, funnel drain stub | `internal-plumbing.md` step 2; [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) |
| 25 | Cut fitted insulation/braid; flush-cut ties | `faucet-and-umbilical.md` step 3; `internal-plumbing.md`; [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md) |
| 26 | Ribbon/bulk-wire blanks, branch trimming, terminal-length stripping | `cable-assemblies.md`; [`wiring run schedule`](/hardware/wiring/ac-wiring-schedule.md) |
| 27 | Snip attached filler wire; dress its stub without grinding the crater | `pressure-vessel.md` step 3 |
| 28 | Source links, companion guides and print setting | Sources named above |

The [refrigeration guide](/hardware/refrigeration-guide/README.md) owns coil stock
and tails, opening a charged donor, refrigerant cut placement, capillary tubing and
contamination controls. The [mold guide](/hardware/mold-guide/README.md) owns cured
foam/silicone trimming. Customer countertop work stays with the
[installation guide](/hardware/install-guide/README.md). Purchased laser-cut plate
outlines and printed CAD cavities are supplied geometry, not in-shop drill/cut steps.

## Reading the pictures

Coral marks a cutting action, fresh edge or part being fitted. Blue marks a gauge,
clamp, measurement or check. Existing stock is neutral; copper retains its material
color. Every picture is a schematic. Printed size and depicted proportion are not
a drill template or a dimension.

The Letter body is centered at 98% with a separate full-scale bleed layer, drawn
1/4 inch beyond all edges. Cobalt top and coral right bands extend 1/3 inch inward.
Print Letter one-up at 100% / no additional scaling; the calibrated Epson photo
paper source is the rear feeder.

## Evidence limits

- The jet cap, jaw grip, drill/cut repeatability, cap fit and sectioned weld root are
  fabrication trials. Candidate dimensions and 1100 rpm are labeled at their steps.
- The production NPT fixture and elbow clock/engagement trial remain open. A turns
  count alone does not establish port fit.
- Generated internal routes do not establish received-fitting insertion lengths,
  warm CO2 placement, moving bowed-link blank lengths or the stated fluid-2 clearance.
  Those steps call for the actual fit, without asserting acceptance.
- The vessel blank must be fitted to actual conical registers. The reservoir rods
  retain the written procedure's end clearance and cap-seat check.
- The printed razor miter box is CAD-checked and physically untested. The Mudder
  remains the illustrated baseline cutter.
- Ribbon web peeling, sleeve sizing and the current donor compressor connector
  retain the limits in the current cable/wiring procedures.

The [mechanical qualification index](/hardware/mechanical-qualification/README.md)
is a source for physical scope. This document records no invented test results.

## Manufacturer references

Verified 2026-10-04 from WEN's own product-page manual links:

- [WEN 4208 / 4208T manual](https://cdn.shopify.com/s/files/1/0012/0350/3168/files/4208T.manual.20220914.pdf?v=1664398265),
  particularly pages 6-7 (work holding, gloves, stopped setup, chips) and 14 (speed adjustment).
- [WEN BA4555 manual](https://cdn.shopify.com/s/files/1/0012/0350/3168/files/BA4555.manual.20211206.pdf?v=1649272733),
  particularly pages 6-7 (vise, cutoff support, gloves and stopped adjustment) and 11-13 (setup/operation).

## Build by hand

```sh
python3 tools/drill-and-cut-guide/build.py
```

Any Python with ReportLab, Pillow and `pdftoppm` available can run the same builder.
It reads selected arithmetic constants and bracketed procedure figures without
evaluating appliance geometry. Content and pictures require deliberate document
review when a source changes. It writes:

- `hardware/drill-and-cut-guide/drill-and-cut-guide.pdf`
- `hardware/drill-and-cut-guide/drill-and-cut-guide.cover.png`
- `hardware/drill-and-cut-guide/drill-and-cut-guide.pdf.json`
- `output/pdf/drill-and-cut-guide.pdf` (identical delivery copy)
- `output/pdf/drill-and-cut-guide.sources.json`

Render all pages with `pdftoppm` and inspect them after an edit. The builder checks
text boxes/action-band heights; it does not substitute for visual proofing.
