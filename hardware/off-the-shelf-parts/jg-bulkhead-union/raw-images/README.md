# JG PP1208E 1/4" Bulkhead Union — Raw Reference Images

## Purpose

Source images for downstream dimensional extraction. The reservoir CAD needs
the stepped cavity profile of the JG PP1208E recessed bulkhead — flange OD,
collet body OD, release ring OD, and each section's axial length. Catalog
specs we already trust: panel hole 0.67" (17.0 mm), envelope OD ~22.9 mm,
overall length ~34.5 mm. Intermediate diameters along the axis are NOT
documented in any datasheet we could find; they must be extracted by
pixel-measurement against the calibrated 0.67" / 17.0 mm brass nut OD or
panel-hole reference.

## Equivalent Parts

All four share the same body geometry — drawings of any one apply to all:

| SKU      | Material            | Color | Amazon ASIN |
|----------|---------------------|-------|-------------|
| PP1208E  | Polypropylene black | Black | B00JYFU8MM  |
| PP1208W  | Polypropylene white | White | B003YKF1SY  |
| PI1208S  | Acetal gray         | Gray  | B0C1F3QR7N  |
| CI1208W  | Acetal white        | White | B0C1HK8LZ8  |

## Acquisition Date

2026-05-11

## Sources Tried (and outcomes)

- John Guest official product pages (johnguest.com) — Cloudflare-blocks
  WebFetch but accessible via browser. The product pages show high-res photos
  but NO dimensional drawing. The Resources & Downloads tab lists only:
  How-to-Connect guide, the full JG Catalog, RWC warranty, and a 1-page
  Tech Spec (pressure/temperature only — no dimensions).
- John Guest technical-downloads SKU search — searching "PP1208E" returns
  the same 3 generic docs (catalog, install instructions, tech spec).
  **John Guest does not publish per-SKU dimensional drawings for this family.**
- Distributor catalogs (Specialty Sales, Big Brand Water, Ryan Herco,
  Fresh Water Systems, H2O Distributors, ESP Water Products, automation-dfw,
  unilogcorp) — all list panel hole = 0.67" and tube OD = 1/4" but show
  only a small product photo, no dimensional drawing.
- GrabCAD (community CAD models) — 45 user-uploaded SLDPRT files for
  John Guest fittings but none named to match the 1208 series; the
  user-supplied models carry a "not affiliated with John Guest" disclaimer
  so they aren't an authoritative geometry source anyway.
- TraceParts / 3DContentCentral — no JG PP1208E results.
- Amazon listing image galleries (PP1208E, PP1208W, PI1208S, CI1208W) —
  all show only product photos, no manufacturer spec drawings inserted in
  the gallery.
- specialty-sales SSI2200 catalog page D49 — single product photo only.

## Conclusion

**No fully-dimensioned engineering drawing exists in the public domain for
this part family.** The best available references are the manufacturer's
high-res product photos (sufficient for pixel-measurement against the
known 0.67"/17.0 mm panel-hole / brass-nut reference) plus the
distributor-catalog product images.

The downstream measurement pass should:
1. Calibrate against the brass locking-nut OD = 0.67" (17.0 mm) — the
   nut is the most reliably-known dimension on the part.
2. Pixel-measure each axial step (flange OD, threaded shaft OD, body OD,
   collet OD) and each axial length from the orthographic side views.
3. Cross-check across multiple SKU photos (PP1208E, PP1212W, CI1208W) for
   consistency, since they share geometry up to nominal scale.

## Images

| # | Filename | Source URL | View | What's Visible | Quality | Use For |
|---|----------|-----------|------|----------------|---------|---------|
| 01 | `01-jg-official-pp1208e-side-view.jpeg` | johnguest.com/sites/default/files/styles/700x525_fallback/public/images/PP1208E.png.jpeg | Near-orthographic side view, 700x525px | Full barbell: collet end at left, threaded shaft, brass nut, second collet end at right | HIGH (clean white-background manufacturer photo, slight 3/4 rotation) | Pixel-measure axial steps; brass nut as calibration |
| 02 | `02-jg-official-ci1208w-orthographic-side.jpeg` | johnguest.com/sites/default/files/styles/700x525_fallback/public/images/CI1208W_3.png.jpeg | Orthographic side view, 700x525px | Full barbell of the white acetal variant, very clean profile, brass nut clearly perpendicular to axis | HIGHEST (cleanest orthographic in the set; brass nut is a perfect calibration ring) | Primary source for pixel-measuring axial dimensions |
| 03 | `03-jg-official-pi1208s-3q-view.jpeg` | johnguest.com/sites/default/files/styles/700x525_fallback/public/images/PI1208S-product-photo.png.jpeg | 3/4-view, 700x525px | Gray acetal variant, foreshortened — collet face visible | MEDIUM (foreshortened; useful for confirming collet end-on geometry but not axial measurement) | Cross-reference for collet ID and gripper-tooth visibility |
| 04 | `04-jg-official-pp1212w-reference-3-8.jpeg` | johnguest.com/sites/default/files/styles/700x525_fallback/public/images/PP1212W-product-photo.png.jpeg | 3/4 angle, 700x525px | 3/8" white PP variant (PP1212W, NOT our part) — included as same-family reference. Panel hole = 0.83". | MEDIUM (different size; geometry scales but not 1:1) | Sanity-check that the 1/4" body proportions match the 3/8" body proportions |
| 05 | `05-freshwatersystems-bulkhead-illustration.jpeg` | assets.freshwatersystems.com/image/upload/s--tEzyZpu2--/iwx2qugdgeqnxblr6jsl.jpg | Schematic cross-section illustration, 490x148px | Two bulkhead unions installed through a wall, labeled "Bulkhead Nut", "Maximum Diameter", "Minimum Diameter" | LOW-MEDIUM (small, no numerical dimensions, but explains the wall-mounting concept — "Max opening = OD of bulkhead nut minus 1/8", rounded down to 1/64"") | Reference for how the bulkhead nut and panel hole relate |
| 06 | `06-jg-2025-catalog-p17-pp1208e.png` | johnguest.com/sites/default/files/files/John-Guest-Fluid-System-Catalog-2025.pdf (page 17) | Catalog page render, 200 DPI | Section "Fluid Systems Fittings — Inch Polypropylene Black" with PP1208E-US listed: 1/4" tube OD, 0.67" mounting hole | MEDIUM (small product photo; authoritative for tube OD + panel hole) | Cite-able catalog reference for the known specs |
| 07 | `07-jg-2025-catalog-p21-pi1208s.png` | johnguest.com/sites/default/files/files/John-Guest-Fluid-System-Catalog-2025.pdf (page 21) | Catalog page render, 200 DPI | Section "Inch Acetal Gray" with PI1208S-US: 1/4", 0.67" mounting hole | MEDIUM | Cite-able catalog reference, gray acetal variant |
| 08 | `08-specialty-sales-d49-pp1208e.png` | specialty-sales.com/content/SSI2200-Full-Catalog-080922.pdf (page 123 = D49) | Distributor catalog page, 200 DPI | "Polypropylene Push Connect Fittings – Black": PP1208E listed with 1/4" tube OD and 0.67" mounting hole | MEDIUM | Distributor confirmation of panel hole |
| 09 | `09-bigbrand-catalog-p10-pi1208s-family.png` | bigbrandwater.com/assets/library/johnguest/johnguest-fluid-catalog.pdf (page 10) | Distributor catalog page, 200 DPI | Acetal Gray Fittings page showing PI1208S, PI1212S, PI1216S with mounting hole diameters and pressure/temperature ratings | MEDIUM-HIGH (largest product photos of the catalog set) | Best small-format side profile in any catalog |

## Licensing / Usage Notes

- All images are publicly hosted manufacturer or distributor catalog material,
  retrieved from public URLs without authentication.
- Product photos from johnguest.com are John Guest / RWC marketing assets;
  used here under fair use for engineering reference in a non-commercial
  hobbyist project.
- The Fresh Water Systems illustration is explicitly marked "sole property of
  Fresh Water Systems, Inc." in its annotation — also used here under fair
  use for reference only.
- All page renders from PDFs are derived from publicly downloadable catalog
  PDFs from each respective distributor.

## NOT Saved (and why)

- John Guest Speedfit Plumbing & Heating Tech Specs Guide PDF — covers a
  different product family (CTS plumbing fittings, not OD tube fittings).
- John Guest White Acetal Fittings Spec Sheet PDF (espwaterproducts) —
  contains the CI1208W part number in a tabular listing but no dimensioned
  drawing.
- 1-page JG OD-fitting tech spec PDF — pressure and temperature only.
- DEMA John Guest Fittings Chart PDF — covers different SKUs (58.x and 95.x
  GHT-thread adapters).
- General JG fluid system marketing PDFs (e.g., Fresh Water Systems' two
  generic JG manuals, the JG quick-connect installation poster) — no
  dimensional content.
- GrabCAD community CAD models — non-authoritative for ground-truth
  geometry; also no exact-name match to the 1208 series.
