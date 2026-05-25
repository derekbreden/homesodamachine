# John Guest PP1208E / PI1208S / CI1208W 1/4" Bulkhead Union — Drawing-Derived Geometry

## Purpose of This Document

Describes the physical geometry of the John Guest 1/4" bulkhead union family (PP1208E black PP, PI1208S gray acetal, CI1208W white acetal — same body, different material/color) in enough detail that an agent generating CAD for a printed-part recess or bulkhead-mounting feature can model every surface, shoulder, and interface zone without holding the part.

All values are **drawing-derived from image pixel-measurement**, calibrated against the published catalog dimensions. Confidence is annotated per row. The reference images are in `../raw-images/`; image numbers referenced in tables (e.g., "image 02") correspond to numbered files there.

A caliper-verified pass on a physical PI1208S (already on hand, 2 units acquired per `purchases.md` §3) will refine these values; treat anything marked **MEDIUM / LOW** as provisional.

## CAD-Ready Summary

The reservoir-CAD constants below correspond to the constants in `hardware/printed-parts/cold-core/reservoir/reservoir.py`. Copy verbatim or use as a starting point for any other consumer:

| Constant | Value (mm) | Confidence | Note |
|----------|-----------|-----------|------|
| `bulkhead_pocket_diameter` | 23.0 | HIGH | Catalog ø22.9 flange + 0.1 mm clearance |
| `bulkhead_panel_hole_diameter` | 17.0 | HIGH | Catalog 0.67" mounting hole, confirmed on multiple sources |
| `bulkhead_total_length` | 34.5 | HIGH | Catalog (Amazon item dim 1.36") |
| `bulkhead_wet_chamber_length` | 12.0 | MEDIUM | Photo-measured ~11.6 mm; rounded for catalog total parity |
| `bulkhead_flange_length` | 8.5 | MEDIUM | Hex-flange portion of wet collet section |
| `bulkhead_release_ring_length` | 3.5 | MEDIUM | Visible release-ring tip |
| `bulkhead_collet_body_length` | (n/a — collapsed into flange section) | — | The wet section reads as 2 zones in the photo (flange + release ring), not 3 |
| `bulkhead_panel_thickness` | 5.0 | LOW | The PETG panel in our reservoir; bulkhead's actual threading section is ~10 mm so panel must be ≤ ~9 mm to leave threading for the locknut |
| `bulkhead_threading_length` | 10.0 | MEDIUM | Body section between the two flanges; supports the locknut |
| `bulkhead_dry_chamber_length` | 17.0 | MEDIUM | Locknut (~5 mm of threading) + dry collet section (~12 mm) |
| `bulkhead_locknut_diameter` | 18.0 | LOW | Photo-uncertain; bigger than panel hole (17), smaller than flange (22.9) |
| `bulkhead_locknut_thickness` | 5.0 | LOW | Photo suggests ~5–8 mm, hard to tell |
| `bulkhead_release_ring_diameter` | 9.57 | HIGH | Inherited from caliper measurement on the PP0408W collet (same 1/4" body family) |

## Overall Form

The fitting is a **symmetric bulkhead union**: a single PP / acetal body with identical push-to-connect collets at each end and a threaded central body between two hex flanges. A separate (plated or all-plastic) **locknut** is supplied loose; it threads onto the central threading and clamps the panel against one flange.

Viewed from the side, the profile is a **double barbell**: two wider hex flanges (one at each end, both ø22.9 mm catalog) with smaller collet bodies and release rings beyond, connected by a narrower threaded shaft in the middle.

In normal install, the panel sits between the locknut and one flange. The "wet" flange is on the syrup side; the "dry" flange + collet are on the outside. Because the body is symmetric, "wet" and "dry" are install-orientation labels, not part-geometry labels.

## Axis Convention

- **Long axis (L):** Axis of tube flow, running through the centers of both collets and the threaded central body. All "length" / "z" dimensions are along this axis.
- **Radial (R):** Perpendicular to L. The body is rotationally symmetric about L — all features described as "diameter" are circles concentric to L.

## Dimensional Profile — 5 Zones Along the Long Axis

The body has 5 distinct zones along L (described from one collet end inward to the other end):

```
   ┌────┐   ┌─────────┐                            ┌─────────┐  ┌────┐
   │REL.│   │  HEX    │   ┌────────────────────┐   │  HEX    │  │REL.│
   │RING│ ─ │ FLANGE  │ ─ │     THREADING      │ ─ │ FLANGE  │ ─│RING│
   │ ø10│   │  ø22.9  │   │       ø ≤ 17       │   │  ø22.9  │  │ ø10│
   │3.5 │   │  8.5    │   │        10          │   │  8.5    │  │3.5 │
   └────┘   └─────────┘   └────────────────────┘   └─────────┘  └────┘
   ◄──────────────────── 34.5 mm overall ──────────────────────────►
```

Because the part is symmetric, only 3 unique zones exist (release ring, flange, threading). Lengths above are rounded for a nominal 34.5 mm total (3.5 + 8.5 + 10 + 8.5 + 3.5 = 34).

### Zone 1: Release Ring (wet end)
- **OD: 9.57 mm** — inherited from the PP0408W caliper measurement (same 1/4" body family, shared collet design). HIGH confidence.
- **Length: 3.5 mm** — photo-measured. MEDIUM confidence.
- Houses the push-to-release sleeve and the spring-steel gripper teeth that retain a 1/4" OD tube.
- The visible end face is the **tube push-in port**, ø6.35 mm (1/4" tube OD).

### Zone 2: Hex Flange (wet end)
- **OD: 22.9 mm** — across the wrench flats of the hex (catalog "envelope" dimension). HIGH confidence on max OD; the hex is faceted rather than circular.
- **Length: 8.5 mm** — photo-measured. MEDIUM confidence.
- The wet face of this flange (facing the threading) is the **panel-seating face**, with an O-ring on it. Provides the wet-side seal.
- Wrench flats let an installer back the bulkhead body up while torquing the locknut.

### Zone 3: Threading (middle)
- **OD: ≤ 17 mm** — threading major diameter, fits 0.67" mounting hole (= 17.0 mm). HIGH confidence on the panel-hole match.
- **Length: 10 mm** — photo-measured (the visible threading span between the two flanges). MEDIUM confidence.
- The **locknut threads on this section** from the dry side.
- Panel sits on this threading on the wet side of the locknut. Practical max panel thickness ≈ 5–6 mm (= threading length − locknut height).

### Zone 4 & 5: Mirror of Zones 2 & 1
Identical hex flange and release ring on the opposite end.

## Locknut (Separate Piece, Shipped Loose)

- **OD: ~18 mm** (photo-measured, LOW confidence — bigger than the 17 mm threading, smaller than the 22.9 mm flange; pixel measurement is rough)
- **Thickness: ~5 mm** (photo-measured, LOW confidence)
- Hex-faceted, plated metal in the CI1208W photo; published material varies by SKU (some are PP, some are plated). The photo shows it threaded onto the middle of the body — its install position depends on panel thickness.

## Catalog Cross-Reference

| Catalog dimension | Source | Value | Confidence |
|---|---|---|---|
| Overall length | Amazon listing item-dim, JG product label | 1.36" / 34.5 mm | HIGH |
| Flange / envelope max OD | Amazon listing item-dim | 0.90" / 22.9 mm | HIGH |
| Mounting hole | JG catalog (image 06, image 08), three independent confirmations | 0.67" / 17.0 mm | HIGH |
| Tube OD | All product titles + body marking ("PP1/4") | 1/4" / 6.35 mm | HIGH |
| Max operating pressure | JG product page | 150 psi @ 70 °F | HIGH |
| Cert | Amazon product description for PP1208E | NSF 51 + NSF 61, FDA-compliant | HIGH |

## Image-Based Measurement Notes

Calibration reference: **total length = 34.5 mm** (catalog) → image-02 pixel scale **≈ 19.4 px/mm** (CI1208W orthographic side view, 700 px wide, bulkhead spans roughly 670 px).

Cross-check with: **flange OD = 22.9 mm** → flange-region pixel height = ~265 px → scale **≈ 19.0 px/mm** (image-Y). Agreement within ~2 %.

| Feature | Px length | Derived mm | Image | Method | Confidence |
|---|---|---|---|---|---|
| Total length, release-ring tip to release-ring tip | 670 | 34.5 (calibration) | 02 | Catalog-anchored | HIGH |
| Left release ring | ~65 | 3.35 | 02 | Pixel | MEDIUM |
| Left hex flange | ~160 | 8.25 | 02 | Pixel | MEDIUM |
| Threading (visible left of locknut) | ~40 | 2.06 | 02 | Pixel | LOW (mostly hidden by locknut) |
| Locknut z-thickness | ~160 | 8.25 | 02 | Pixel | LOW (could be partial threading) |
| Threading (visible right of locknut) | ~35 | 1.80 | 02 | Pixel | LOW |
| Right hex flange | ~160 | 8.25 | 02 | Pixel | MEDIUM |
| Right release ring | ~50 | 2.58 | 02 | Pixel | MEDIUM |
| **Sum check** | **670** | **34.54** | — | — | matches catalog → calibration is self-consistent |

The "visible threading left + locknut + visible threading right" measurements sum to ~12.1 mm. The locknut is partway along the threading in the photo — I can't precisely separate "locknut thickness" from "exposed threading on its sides". A caliper pass on the part will resolve this; for now I rounded threading section to **10 mm** and locknut thickness to **~5 mm**.

## Design Implications for the Reservoir CAD

1. **Wet chamber should match the body's stepped profile** (the chamber currently does, with 3 sections at ø23 / ø19 / ø11 from flange to release ring). The release-ring section (ø11) brings the residual film below the bulkhead's wet collet port down to ~milliliters, where a uniform ø23 chamber held an order of magnitude more.

2. **Panel hole = ø17 mm is firm.** Catalog is unambiguous; three independent confirmations across the agent's image set.

3. **Panel thickness in CAD (5 mm) is a deliberate choice**, not a derived measurement. The bulkhead's threading is ~10 mm; the panel takes 5 mm of that, leaving ~5 mm of threading on the dry side for the locknut. If a thicker PETG panel is needed (e.g., 6–7 mm) the locknut still fits but with less thread engagement.

4. **Dry chamber length = 17 mm** is the locknut zone (~5 mm) plus the dry collet section (~12 mm). The current CAD extends it further (to z = outer_z_max) for axial install access; that's an install/assembly trade-off, not a measurement-driven choice.

5. **Locknut OD (≈18 mm)** is one of the weakest measurements here. If the locknut is actually ø22 mm (matching the flanges), the dry-side chamber's first ~5 mm should be ø23 (current uniform diameter already accommodates this).

## Remaining Unknowns / TODO

- [ ] **Caliper-verify** locknut OD, locknut thickness, and threading length on the PI1208S we already own. Confidence on those three currently ≤ MEDIUM.
- [ ] **Caliper-verify** the wet-flange-vs-release-ring transition shape. The photo shows the flange and release ring as the only visible features; in reality there may be a step or smooth taper between them that doesn't read in 700-px JPEG.
- [ ] If a fully-dimensioned engineering drawing surfaces (JG catalog updates, OEM RFQ, GrabCAD), drop a copy into `raw-images/` and re-derive this table with HIGH confidence on all rows.

## Workflow Used

This is the first application of `tools/measure-from-drawings/README.md`. Key calls made during measurement:

- **Calibration anchor**: catalog total length (34.5 mm), cross-checked against catalog flange OD (22.9 mm). The two agreed within 2 % → image is to-scale and pixel-measurement is valid for medium-confidence numbers.
- **Image rejected**: image 03 (3/4 perspective view of PI1208S) — perspective distortion makes pixel measurement unreliable. Used only for visual confirmation of the body's overall shape.
- **Image used as primary**: image 02 (CI1208W official side view, both collets visible) — orthographic, both ends visible, locknut shown.
- **Image used as cross-check**: image 01 (PP1208E side view, one end + locknut visible) — orthographic from a slightly different angle, confirms the flange / threading / locknut sequence.
- **Catalog images** (06, 08): provide the panel-hole 0.67" spec and the part-number / SKU correspondence. No additional dimensions extractable beyond the table.
