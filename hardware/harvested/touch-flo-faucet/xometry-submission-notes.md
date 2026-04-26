# Xometry Submission Notes — Tube Bending + Powder Coat

Reference for preparing instant quotes on the dispense spout's stainless tubes. Captures Xometry's current accepted file formats, DFM limits, quote-form fields, and gotchas so we don't re-derive them on every order. Sourced from Xometry's public capabilities and DFM pages, 2026-04-24.

## File format

- **STEP file of the fully-bent 3D solid.** Not a straight stick with a bend table — Xometry's instant-quote engine reads the geometry and derives the bend sequence itself.
- One single-solid STEP per bent tube; do not submit assemblies. Each bent tube is its own line item.
- **Millimeters** as the working unit. Inch-unit STEPs sometimes round-trip badly through their CAM pipeline.
- AP214 is fine — CadQuery's default OCCT export (`exporters.export(obj, "part.step")`) writes AP214. AP242 is richer if you want it; set the OCCT schema override on the exporter.
- No PMI annotations needed. The solid geometry is the spec.

## DFM limits (1/4" SS, applies to 304 and 316)

- **Wall thickness:** 0.035" or 0.049"
- **Min centerline bend radius:** 0.500" (2× OD); below this flags manufacturing risk
- **Min straight between bends:** 0.500" (2× OD) for tubes under 1" OD
- **Max bend angle:** under 180°; no knots, no self-crossing

## Min OD floor

**0.250" OD is the floor.** Xometry's auto-quote range is 0.25"–2.0" OD, round only.

**1/8" (3.18 mm) tubes will not quote.** Workaround: hand-bend the 1/8" flavor tubes at home using the purchased 304 SS stock. 1/8" annealed 304 bends cleanly around a small form without a mandrel — standard instrumentation-tubing practice. Only 1/4" tubes go to Xometry.

## Quote-form inputs (beyond the STEP)

- Material + grade — pick from Xometry's tube list (304 SS, 316 SS, Al 6061, 4130, A513)
- OD (nominal) and wall thickness — snaps to standard size if your STEP lands close
- Quantity
- Finish — dropdown; Powder Coating appears as a value-added line item
- Tolerance — Xometry standard tube tolerances are applied unless a drawing PDF overrides:
  - Bend angle ±1°
  - Rotation ±2°
  - Segment length ±0.030"
  - Overall envelope ±0.125"
  - Tube endpoint ±0.063"
  - CLR ±0.25"
  - Ovality ≤10%

## Powder coat as a same-order line item

- Color: RAL-indexed palette (blacks RAL 9004/9005/9011, etc.). Custom RAL via quote notes.
- Texture: smooth / fine texture / textured / rough textured
- Gloss: matte (default) / semi-gloss / gloss
- Thickness: 0.006"–0.012" typical (ASTM D7803)

**Critical for 304/316 SS:** the quoter UI does not expose a surface-prep selector. Xometry's standard process is degrease + blast, but powder does not adhere reliably to passive stainless without aggressive abrasion. **Attach a one-page drawing PDF requesting mechanical abrasion / grit blast prior to coat.**

## Turnaround

Not published — computed at quote time from the geometry and shown in the live quoter. Powder coat adds days. Plan to read the number off the UI; public docs won't help.

## Single-CLR constraint

Xometry's DFM page recommends one CLR per tube "for ease of
manufacturability." Parts with multiple bend radii need multi-stack
tooling or extra setups; the quoter charges for it or refuses outright.
This bit us on the dispense flavor tube: the real Touch-Flo gooseneck
has asymmetric radii (bend 1 ≈ 12 mm, bend 2 ≈ 48 mm), and we had to
collapse both to a single 1.25" CLR (the legal max for 1/4" OD) to get
a clean quote. See `hardware/cut-parts/dispense-flavor-tube/README.md`
for the silhouette-fidelity tradeoff that creates.

If a future part genuinely needs two CLRs, the path is a niche
tube-bending shop with a custom-quote workflow (Tube-Tec, Triad
Products, Noble Industries, Woolf Aircraft, etc.) — instant-quote
platforms generally don't support it.

## Gaps not confirmed from public docs

- Lead time numbers for low-quantity tube-bent + powder-coated SS
- Whether surface-prep callouts are accepted via a quoter field or only via attached drawing — safe bet is the drawing PDF

## Sources

- [Custom Tube Bending Service | Instant Quotes](https://www.xometry.com/capabilities/tube-bending-services/)
- [Top Tube Bending Design Tips](https://www.xometry.com/resources/tube/tube-bending-design-tips/)
- [Webinar: Tube Bending and Cutting Best Practices](https://www.xometry.com/resources/blog/tube-bending-and-cutting-webinar/)
- [Xometry AI-Driven Auto-Quoting for Tube Fabrication](https://www.xometry.com/resources/tube-instant-quoting/)
- [Manufacturing Standards](https://www.xometry.com/manufacturing-standards/)
- [Powder Coating Service](https://www.xometry.com/capabilities/powder-coating-service/)
- [Powder Coating Finishes Gallery](https://www.xometry.com/finishes/powder-coating/)
