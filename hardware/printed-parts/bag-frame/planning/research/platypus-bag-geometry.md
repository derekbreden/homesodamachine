# Platypus 2L Platy Bottle — Physical Geometry Research

**Date:** 2026-03-29
**Purpose:** Characterize the physical geometry of the Platypus 2L Collapsible Bottle (ASIN B000J2KEGY) when filled and oriented at 35° from horizontal (cap end downward), to inform the lens-shaped cradle platform design described in vision.md.

---

## Sources

- Platypus official product page: [cascadedesigns.com/products/platy-2l-bottle](https://cascadedesigns.com/products/platy-2l-bottle)
- Platypus Closure Cap official page: [cascadedesigns.com/products/closure-cap](https://cascadedesigns.com/products/closure-cap)
- CleverHiker review (physical dimensions of packed state): [cleverhiker.com](https://www.cleverhiker.com/more-gear/platypus-platy-water-bottle-review/)
- Amazon product listing: [amazon.com/dp/B000J2KEGY](https://www.amazon.com/dp/B000J2KEGY)

---

## 1. Bag External Dimensions — Empty / Flat

**Official specs (from cascadedesigns.com):**

| Dimension | Value |
|-----------|-------|
| Flat length | 350 mm (13.8 in) |
| Flat width | 190 mm (7.5 in) |
| Weight | 36 g (1.3 oz) |
| Capacity | 2.0 L / 70 fl oz |
| Film material | Nylon / Polyethylene laminate |
| Spout material | Polyethylene |
| Cap material | Polypropylene |
| Made in | USA |

**Packed/rolled state (from review sources):** 7.5 x 2.25 x 0.5 in (190 x 57 x 13 mm). This is the rolled-up form — not directly relevant to the flat orientation used in the enclosure, but it confirms the film is thin enough to collapse to ~1mm per layer.

**Bag geometry description:**

The Platy bag is a flat pouch — two panels of thin nylon/PE laminate film heat-sealed at all four edges. The seals create four zones along the bag's length:

1. **Cap/neck zone (bottom ~30mm):** The bag narrows to a ~28mm PE spout at the lower end. This is a rigid-ish neck with 28-400 threads. The film here is gathered/formed around the spout fitting.
2. **Taper zone (~50mm):** The bag body transitions from the 28mm neck up to the full 190mm body width over approximately 50mm.
3. **Body zone (~220mm):** The main inflating section. Full 190mm width. This is where the lens profile develops.
4. **Fold/seal zone at top (~50mm):** The top of the bag is a heat-sealed band approximately 15–20mm wide. Per the vision, this end is pinned flat against the front wall and does not inflate.

**Total effective inflating length** (taper zone + body zone): approximately 270mm out of 350mm total bag length.

---

## 2. Cross-Sectional Thickness When Filled at 35°

### Geometric model

The bag is constructed from inextensible film. When filled, each cross-section inflates into a **lens shape** (biconvex ellipse approximated by two circular arcs), because the film perimeter at each cross-section is fixed by the flat bag width (190mm). The lens-shape cross-section with chord W and total thickness T has:

- Arc radius: R = (W² + T²) / (4T)
- Cross-section area: the standard lens-area formula (two circular segments)

### Empirical ground truth from vision.md

The vision states, from direct observation of the actual bag:

> "Without this constraint, the bottom portion may rise to 40mm height."

This 40mm figure is the empirical unconstrained peak midsection thickness for the 2L bag when full. All model calculations below are calibrated to this observation.

### Full bag (2.0 L) at 35°, unconstrained

At 40mm midsection thickness, the 190mm-wide lens cross-section has:

| Parameter | Value |
|-----------|-------|
| Width (W) | 190 mm |
| Thickness (T) — unconstrained peak | ~40 mm |
| Arc radius (R) | (190² + 40²) / (4 × 40) = **235 mm** |
| Cross-section area | ~51 cm² |

The midsection is the thickest zone. The cap-end taper and the fold end taper both reduce the cross-section toward zero, so the midsection bulges beyond the average.

**Profile along bag axis (35°, full, unconstrained):**

| Zone | Distance from cap | Approx thickness |
|------|------------------|-----------------|
| Neck (cap end) | 0–30 mm | 0 → ~20 mm (taper) |
| Taper | 30–80 mm | ~20 → ~35 mm (transitioning) |
| Body lower third | 80–160 mm | ~35–40 mm |
| Body middle third | 160–240 mm | **~40 mm (peak)** |
| Body upper third | 240–300 mm | ~30–38 mm (thins toward fold) |
| Fold (top end) | 300–350 mm | 0 mm (pinned flat) |

### Full bag (2.0 L) at 35°, constrained to 25–30 mm

Per vision.md, the top constraint brings the midsection to 25–30 mm. Using 27 mm as the working target:

| Parameter | Value |
|-----------|-------|
| Constrained T | 27 mm |
| Arc radius at 27 mm, 190 mm wide | (190² + 27²) / (4 × 27) = **341 mm** |
| Cross-section area at 27 mm | ~34.3 cm² |
| Cross-section area at 40 mm (unconstrained) | ~51.1 cm² |
| Volume displaced from body by constraint | ~370 mL (redistributed to cap/taper zone) |

The constraint reduces the midsection cross-section area by ~33%. That ~370 mL is redistributed to the cap-end zone (the lower third), which becomes slightly deeper than the constrained midsection. The cap zone is less critical to constrain uniformly because it is buried in the lower pocket of the enclosure, and the tubing connection is at the very bottom of that zone.

---

## 3. Partial Fill Profile at 35°

At 35° with the cap end down, gravity pools liquid toward the cap end. The bag is sealed, so there is no free surface — but it is a flexible pouch, meaning the film follows the liquid column. As the bag empties:

- The **lower (cap) zone** remains filled to near-maximum thickness as long as any significant liquid remains.
- The **liquid/film interface** (the zone of transition from full to empty) migrates upward along the bag axis.
- The **upper (fold) zone** collapses toward 0 mm as liquid drains.

This means the bag presents a consistent deep cross-section at the cap-end zone regardless of fill level, and progressively flattens toward the top as the bag empties.

### Estimated thickness profiles at 35°

The cross-section model below assumes the liquid pools to the cap end. The "filled length" is the portion of the body zone containing liquid; the remainder is flat.

| Fill level | Approx filled length from cap | T at lower (cap) zone | T at upper zone |
|------------|-------------------------------|----------------------|-----------------|
| 2.0 L (full) | Full 270 mm active length | ~27 mm (constrained) | ~27 mm (constrained) |
| 1.5 L | ~200 mm from cap | ~27 mm (constrained) | 0–5 mm (flattening) |
| 1.0 L | ~135 mm from cap | ~27 mm (constrained) | 0 mm |
| 0.5 L | ~70 mm from cap | ~20–25 mm | 0 mm |

**Key insight for cradle design:** The unconstrained cross-section at the lower zone is approximately constant regardless of fill level — the same volume of liquid occupies the same depth of profile as long as the cap zone is full. As the bag empties, the filled column simply shortens. The constraint therefore needs to be active throughout the body zone (not just the midsection), so the profile stays in the 25–30 mm range throughout the dispensing cycle.

---

## 4. Cap / Valve Area Dimensions

### Official Platypus Closure Cap dimensions

From cascadedesigns.com/products/closure-cap (SKU 14318):

| Dimension | Imperial | Metric |
|-----------|---------|--------|
| Cap dimension 1 | 0.69 in | 17.5 mm |
| Cap dimension 2 | 1.17 in | 29.7 mm |
| Cap dimension 3 | 1.0 in | 25.4 mm |
| Weight | 0.1 oz | 2.6 g |
| Material | Polypropylene | — |

The most likely interpretation of these three dimensions:
- **1.17 in (29.7 mm)** — outer body diameter of the cap (viewed from above), the widest point you grip
- **1.0 in (25.4 mm)** — total height of the cap body
- **0.69 in (17.5 mm)** — inner bore or some other secondary dimension

### Thread standard

The Platypus bottle uses the **28-400 thread finish** (confirmed by multiple sources including the Platypus Gravity Works adapter documentation):
- **28 mm** = nominal outer diameter of the bottle neck thread
- **400** = single-turn short finish (common for caps under 32oz)

### Cap and spout assembly depth

The Platy bag has a PE spout heat-fused to the bottom seam of the bag. The spout + cap assembly below the bag body seam:

- **Spout neck above bottom seam:** estimated 15–20 mm (the rigid PE neck that accepts the thread)
- **Cap height:** 25.4 mm (per official spec)
- **Total protrusion from bag bottom seam:** approximately **40–50 mm**

This is the cap end that sits in the back/bottom pocket of the enclosure. The pocket must provide at least **50 mm of axial clearance** from the bottom seam of the bag body to the enclosure wall.

**Cap area cross-section:** The widest point of the cap assembly is the cap body OD of ~30 mm. The bag film at this zone gathers around a ~28 mm spout, so the local cross-section across the bag width tapers from 190 mm down to ~30–35 mm over the taper zone (~50 mm length). The cradle at this end should accommodate a ~35–40 mm wide, ~40–45 mm deep pocket for the cap assembly.

---

## 5. Fold / Top End Geometry

The top (opening) end of the Platy bag is a **heat-sealed band**:

- The seal band is approximately **15–20 mm tall** (the width of the fused seam).
- The bag material at this end is the full 190 mm wide.
- When folded flat and pinned against the front wall per vision.md, the folded thickness is:
  - Film is approximately 0.2–0.3 mm per layer (ultralight nylon/PE at 36g total for 2L bag).
  - A single fold = two layers + fold radius = approximately **2–5 mm** total.
  - With any gathering or wrinkling: up to **8–10 mm**.
- The fold end presents as a **flat strip** ~190 mm wide and ~20 mm tall, pressed against the front wall.
- It contributes negligible depth — the front wall constraint can be a flat surface with a small ledge or clip to hold this end.

**For the front wall interface:** A simple slot or tab ~5 mm deep is sufficient to capture the folded top. The bag presents a clean, predictable flat end here.

---

## 6. Material Properties Affecting Cradle Shape

The Platypus Platy film is a **nylon/polyethylene co-extrusion or laminate**, approximately 0.2–0.3 mm thick:

**Behavior under constraint:**
- The film is **inextensible** when taut — it does not stretch meaningfully under liquid pressure.
- The film is **fully flexible** — it has no bending stiffness and will conform to any surface it contacts.
- When the bag is placed in a lens-shaped cradle and a matching top constraint is applied, the film simply drapes against the surfaces and the liquid fills the available volume.
- The shape inside the constraint is **entirely determined by the constraint geometry**, not by any stiffness of the bag material.
- This means: a smooth-surfaced cradle will produce a precise, repeatable cross-section. The bag does not fight back. It conforms.

**Consistency across fill levels:**
- At full (2L): entire cradle surface is contacted by the bag.
- At partial fill: the lower portion of the cradle is contacted; the upper portion has collapsed film lying flat. The transition is a clean line.
- The bag does not "sag" away from the cradle bottom in an uncontrolled way. Once constrained from above, it occupies the cradle volume fully in the liquid-filled zone.

**Seam durability:**
- The heat-welded seams are the structural weak point. The cradle must not put sharp bending loads on the seams — the contact surfaces should be smoothly radiused at the bag perimeter (no sharp edges that would concentrate stress on the side seams).

---

## 7. Design Implications for the Lens-Shaped Cradle

### Confirmed numbers from research

| Parameter | Value | Source |
|-----------|-------|--------|
| Bag flat length | 350 mm | Official spec |
| Bag flat width | 190 mm | Official spec |
| Cap thread OD | 28 mm | Industry standard for Platypus (28-400) |
| Cap body OD | ~30 mm | Official cap dimension (1.17 in = 29.7 mm) |
| Cap body height | ~25 mm | Official cap dimension (1.0 in = 25.4 mm) |
| Cap + spout protrusion from bag seam | ~40–50 mm | Derived |
| Unconstrained midsection T at 2L | ~40 mm | Vision.md (empirical) |
| Constrained midsection T (target) | 25–30 mm | Vision.md (empirical) |
| Cradle arc radius at 27mm depth, 190mm wide | 341 mm | Calculated |
| Fold end thickness when pinned flat | ~3–8 mm | Derived |

### Cradle geometry that follows from this

**Bottom cradle (lens platform):**
- Cross-section profile: circular arc, R = 341 mm, chord = 190 mm, sagitta = 27 mm at the midsection.
- The depth along the axis: the cradle should be deepest in the body zone (22 cm from taper to fold) and shallower toward the fold end. The cap end needs a deeper pocket (~35–40 mm deep) for the cap protrusion.
- The taper zone (bottom ~50 mm of the active bag) transitions from the pocket depth to the body cradle depth — this should be a smooth longitudinal curve, not a step.

**Top constraint (matching the bottom profile):**
- Must match the bottom arc geometry exactly (R = 341 mm, same chord)
- Total gap between bottom and top = 27 mm at midsection
- The top constraint is the element that enforces the 25–30 mm profile and prevents unconstrained expansion to 40 mm

**Critical fit note:** The cradle arc of R = 341 mm for a constrained 27 mm profile is a very shallow curve — the sagitta is 27 mm across the full 190 mm chord. This is a gentle bowl shape. Confirm that this shallow arc captures the bag correctly; a mismatch of even 3–4 mm in sagitta will be immediately visible as an inconsistency in the bag shape. Empirical calibration with the actual bag is essential.

---

## 8. Dimensions NOT Confirmed — Must Be Resolved Empirically

The following dimensions could not be confirmed from available sources and must be verified by measuring the actual Platypus 2L bag (ASIN B000J2KEGY):

| Unknown | Why it matters | Suggested measurement |
|---------|---------------|----------------------|
| Spout neck height above bag bottom seam | Determines cap-end pocket depth | Measure with calipers from seam to spout shoulder |
| Exact spout OD at thread root | Determines pocket width at cap end | Measure thread OD (expect 28 mm) |
| Length of taper zone (neck to full body width) | Determines where the body cradle starts | Lay bag flat, measure 28mm-width zone to 190mm-width zone |
| Film thickness | Confirms material stiffness assumptions | Measure with micrometer |
| Unconstrained midsection T at 2L lying at 35° | Vision says ~40 mm; confirm with ruler | Fill bag, orient at 35°, measure midsection |
| Constrained T achievable at 25 vs 30 mm | The 25–30 mm range in vision.md: which end is comfortable? | Test cradle at 25, 27, 30 mm depths and observe bag behavior |
| Cap body OD (actual) | The Platypus spec 1.17 in = 29.7 mm may be height, not diameter | Measure cap with calipers |
| Top seal band height | Determines fold-end interface ledge depth | Measure the white/opaque sealed band at top |
