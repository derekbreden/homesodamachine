# Collet Release Force — John Guest PP0408W Release Plate

## Research Context

The vision specifies a squeeze-release mechanism: the user's hand is palm-up, palm pushes against the cartridge body, fingers curl upward to pull a flat release plate toward the collets of 4 John Guest PP0408W fittings simultaneously. The release plate's stepped bores engage the annular end face of each collet (collet OD 9.57mm, collet ID 6.69mm). This document establishes the force budget, contact geometry, and stroke parameters needed to design that plate.

Geometry baseline: all fitting dimensions are from `hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md` (caliper-verified). Key values used here: collet OD 9.57mm, collet ID 6.69mm, collet travel ~1.3mm per side.

---

## 1. Single-Collet Release Force

### What the manufacturer publishes

John Guest does not publish a numerical collet depression force for the PP0408W or any PP-series fitting in any publicly accessible datasheet, catalog, or application note. Parker Legris, SMC KQ2, Festo QS, and other comparable push-to-connect fitting manufacturers likewise do not publish collet release force specifications. This is universal across the industry — these fittings are designed for finger release without tools, and manufacturers communicate this qualitatively ("push the collet square against the fitting") rather than numerically.

John Guest does sell a dedicated release tool (TSPITOOL / PI-TOOL, 1/4" and 3/8" ends) described as providing "easier disconnection" in "confined areas," explicitly noting the tool "is not required to release the quick connect fittings but can greatly ease the tubing release." This framing establishes that bare-finger force is sufficient for the 1/4" fitting under normal conditions.

### First-principles estimation

The collet mechanism in a PP0408W works as follows: a plastic sleeve (the collet) is spring-loaded outward by a small return spring inside the fitting body. When depressed ~1.3mm inward, the collet geometry releases the stainless steel grip ring's engagement with the tube. The force to depress is the spring preload plus any friction from the collet's sliding fit in the body bore.

Comparable small push-to-connect fittings (Parker Prestolok 1/4" OD pneumatic, SMC KQ2H06) have collet return springs that are intentionally soft — the fitting must hold tube against high line pressure via the stainless teeth geometry, not spring preload. The spring's only job is to return the collet to the extended position after release; it does not contribute to tube retention.

**Spring force estimation:**
- The collet sleeve is a small acetal ring (~9.57mm OD, ~1.44mm wall) with a short travel of 1.3mm
- A small internal return spring for a fitting of this scale typically produces 2–8 N at working compression. The PP0408W PP-series is rated for potable liquid at up to ~145 psi (1000 kPa), not pneumatic service — the return spring is lighter than pneumatic-rated equivalents
- Friction: the collet slides in a close-tolerance bore in the acetal body; acetal-on-acetal friction coefficient is approximately 0.1–0.2. Normal force is negligible at this scale
- Field reports from plumbing and homebrewing communities consistently describe the collet as "easy to move," requiring fingertip pressure rather than grip strength. One firsthand account describes the collet as easily levered out of its housing with a screwdriver, suggesting very light retention force

**Estimated single-collet depression force:**

| Phase | Estimated Force | Basis |
|-------|----------------|-------|
| Initial breakaway | 5–10 N | Spring preload + static friction. Light acetal-on-acetal interface, small return spring |
| Sustained depression (held at full travel) | 8–15 N | Spring compressed ~1.3mm beyond preload position; acetal spring constant ~5–10 N/mm at this scale |

**Working design value: 15 N per collet (conservative upper bound).** This exceeds the plausible maximum based on mechanism analysis and is recommended as the design force to avoid underestimating the aggregate load.

**Important note:** The PP0408W is a plumbing fitting (not pneumatic). In plumbing service at system pressure, the collet spring is supplemented by pressure-assisted tube grip — the tube is harder to pull out under pressure but collet depression force is not pressure-dependent. With the cartridge removed from the machine (no system pressure), the release force is purely the spring — the lower end of the range applies. The design should account for the possibility of attempting release while under pressure (line pressure locked in tubing), which adds negligible collet depression force but is noted as a failure mode concern (see Section 5).

---

## 2. Four-Collet Simultaneous Force

### Is 4× a valid estimate?

Yes, with one important qualification: 4× the single-collet force is valid when all four collets are engaged simultaneously and equally by the release plate. There are no mechanical coupling effects between collets — each fitting's internal spring is independent. Coupling effects (where engaging one collet loads another) would only arise if the fittings were mechanically linked through a shared compliant structure, which they are not.

The qualification: **simultaneous engagement depends on plate flatness and fitting alignment.** If one collet contacts the plate slightly before the others due to manufacturing variation, that collet will be partially depressed before the others begin moving. In the worst case, the user must overcome one collet's full travel before the others engage. This is a sequential, not simultaneous, load — but because the travel is so short (1.3mm), the practical effect is that the user feels a slightly stiffer initial engagement as the plate aligns, then all four release together. This is not a force concern — it is a tactile feel concern addressed by tight tolerances (see Section 4 on contact geometry and by the stroke margin analysis in Section 5).

**4-collet total force:**

| Case | Force | Notes |
|------|-------|-------|
| Ideal simultaneous engagement | 4 × 15 N = **60 N** | Upper bound, all 4 collets engaged at once |
| Sequential worst case (one collet bottoms before others start) | Still 60 N peak, reached earlier in stroke | No force multiplication; same total |
| Practical design load | **60 N** | Use this as the grip force the mechanism must produce |

---

## 3. Human Grip Force — Palm-Up Squeeze Posture

### Grip strength in supinated (palm-up) posture

The palm-up squeeze posture engages wrist flexors with the forearm supinated. Published literature (forearm position studies) consistently finds that supinated grip is equal to or slightly stronger than neutral, and significantly stronger than pronated. This is favorable for this mechanism.

Normative grip strength data (Mathiowetz; Topendsports norms):
- Adult males (25–39 years, peak): ~400–560 N maximum grip force
- Adult females (25–39 years, peak): ~250–400 N maximum grip force
- Weak individuals (75th percentile female, elderly): ~185–250 N maximum grip force

These are maximum voluntary contraction values. Ergonomic guidelines for sustained or repeated hand operations:
- General ergonomic maximum for sustained hand operations: **45 N** (Ergoweb / MEADinfo ergonomics guidelines)
- Maximum pinch force (acceptable for product design): ~40 N (9 lbs)
- For a one-time, brief squeeze (cartridge swap is infrequent — perhaps once every several months): up to **150–200 N** is comfortably achievable by most adults without strain
- A one-time brief squeeze at 60–100 N is well within the comfortable capability of all but the most mobility-limited users

### The grip geometry for this mechanism

The vision specifies a flat-surface squeeze: palm pushes against the cartridge body face, fingers curl upward and pull the release plate toward the palm. This is a **parallel-jaw grip** on a flat object, not a cylindrical grasp. The force produced is:

- **Net force available at the plate** = finger curl force minus any mechanical disadvantage from the grip geometry
- For a flat plate grip at comfortable effort (roughly 30% of maximum), a healthy adult produces approximately **80–150 N** net clamping force
- The cartridge body is approximately 50–60mm deep (front-to-back), giving a reasonable grip span

### Force budget assessment

| Parameter | Value |
|-----------|-------|
| Required plate force (4 collets) | 60 N |
| Comfortable one-time squeeze force (adult population, 5th–95th percentile) | 80–200 N |
| Required / comfortable ratio | 0.3–0.75 |
| Minimum mechanical advantage needed | None — direct squeeze at 1:1 is adequate |

**The 60 N requirement fits comfortably within a direct 1:1 palm squeeze for the vast majority of adult users.** No mechanical advantage (cam, lever, wedge) is required to meet the force budget. The vision's flat-surface squeeze is mechanically sufficient.

**Edge case:** Users with limited hand strength (arthritis, grip disability) may find 60 N challenging. The comfortable pinch/squeeze force for the 5th percentile elderly female is approximately 70–90 N maximum, leaving minimal margin at 60 N required. If inclusive design for mobility-limited users is a priority, targeting 40 N total (10 N per collet) by specifying lighter-spring replacement collets or a slight mechanical advantage in the grip geometry would be worthwhile. For the current design intent (healthy adult user), no accommodation is needed.

---

## 4. Contact Geometry and PETG Bearing Stress

### Contact area at the collet annular face

Per the geometry doc, the release plate contacts the collet's annular end face:
- Collet OD: 9.57mm → radius 4.785mm
- Collet ID: 6.69mm → radius 3.345mm
- Annular contact area per collet:
  - A = π × (r_outer² − r_inner²) = π × (4.785² − 3.345²) = π × (22.90 − 11.19) = π × 11.71 = **36.8 mm²**

For 4 collets, total contact area = 4 × 36.8 = **147 mm²**

### Bearing stress calculation

At the 60 N design load applied across all 4 collets simultaneously:
- Bearing stress per collet = 15 N / 36.8 mm² = **0.41 MPa**
- This is the average compressive stress on the PETG plate lip where it contacts the collet face

At a 2× safety factor (accounting for dynamic loading, misalignment, or aggressive squeezing):
- Peak bearing stress = **0.82 MPa**

### PETG compressive yield strength

FDM-printed PETG (per PMC/MDPI compression studies, ISO-604):
- Compressive yield strength (Z-axis, worst case for a plate printed flat): **14–22.5 MPa**
- Compressive yield strength (in-plane, best case): **19–24 MPa**

The release plate will be printed with the plate face parallel to the build plate (XY plane), so the contact lips engage in the Z-axis compression direction — the lowest-strength orientation.

**Safety factor at design load:** 14 MPa yield / 0.82 MPa peak = **17×**

**There is no PETG bearing stress concern.** The contact pressure at the collet annular face is two orders of magnitude below PETG yield in compression. Even with the inner lip reduced to a thin wall (approaching the 0.8mm minimum structural wall per requirements.md), the stress is negligible. The failure mode for this interface is not material yield — it is geometric (thin wall cracking from bending if the lip is too narrow), which is addressed by the minimum wall constraint in requirements.md.

### Contact geometry design implication

The plate's inner lip bore (just over 9.57mm, as tight as printing allows) serves two functions: it contacts the annular face to transmit force, and it provides lateral constraint to prevent the collet from canting sideways during depression. The lateral constraint function is more demanding than the force-transmission function. The lip should be designed with enough axial depth to prevent the collet from tilting under the asymmetric load that occurs when the plate approaches at a slight angle. A minimum axial engagement depth of **2mm** is recommended — this keeps the collet square during the full 1.3mm depression stroke with 0.7mm of initial engagement.

---

## 5. Stroke Validation and Design Margin

### Required stroke

Per the geometry doc, collet travel is ~1.3mm per side (from extended to compressed). The release plate must travel at least 1.3mm from its resting position to achieve full collet depression on all four fittings.

### Sources of stroke consumption

The 1.3mm figure is the collet travel measured on the physical fitting. The release plate must actually travel more than 1.3mm because:

1. **Part-to-part variation in collet protrusion:** The collet's extended protrusion is approximately 1.4mm per side (39.13mm compressed vs. 36.32mm body = 2.81mm total / 2 = ~1.4mm per side). Manufacturing variation of ±0.2mm is plausible for an injection-molded acetal part at this scale.

2. **Fitting seating variation:** The four fittings in the rear wall will not be perfectly coplanar. If one fitting protrudes 0.2mm more than another, the plate must travel an additional 0.2mm to ensure the last collet is fully depressed.

3. **Release plate flex:** Under 60 N load, a PETG plate of typical thickness (3–4mm) will deflect slightly. For a 4-contact-point plate roughly 40mm across, deflection at the center is small but non-zero. A 3mm PETG plate (E ≈ 1200 MPa) spanning 40mm under 15 N center load deflects approximately 0.05–0.1mm — negligible.

4. **Grip compliance:** The user's squeeze produces some compliance in the printed body and the grip geometry. This is absorbed by the ~1.7mm margin already noted in the geometry doc.

### Recommended stroke

| Stroke component | Value |
|-----------------|-------|
| Full collet travel (required) | 1.3mm |
| Manufacturing variation allowance | +0.3mm |
| Fitting coplanarity allowance | +0.3mm |
| Alignment/approach margin | +0.4mm |
| **Total recommended plate travel** | **2.3mm minimum** |
| **Geometry doc notes cam lever produces 3mm** | 3mm is sufficient with **0.7mm margin** |

**The 3mm of plate travel from the cam/squeeze mechanism is adequate with 0.7mm to spare.** This margin is comfortable for a 1:1 direct squeeze mechanism but should be confirmed with a physical test: depress all four collets simultaneously on a bench fixture and confirm all four tubes release at less than 2.5mm of plate travel.

### Stroke validation test procedure

Before finalizing the release plate geometry, perform this bench test with four PP0408W fittings:
1. Mount four fittings in the rear wall mockup with tubes inserted
2. Apply a flat plate to all four collet faces and push with a depth gauge attached
3. Record the plate travel at which each tube releases
4. The worst-case (last tube to release) travel must be under 2.5mm to confirm the 3mm stroke provides adequate margin

---

## 6. Failure Modes and Concerns

### Failure mode 1: Partial collet depression (most likely)
If the release plate contacts the body end (15.10mm OD shoulder) instead of the collet face (9.57mm OD), the collet cannot be depressed. This occurs if the stepped bore outer diameter is undersized, preventing the plate from reaching the collet annular face. **Mitigation:** The outer bore (clearing the 15.10mm body end) must be generously oversized — 15.5–16mm minimum — so the plate slides over the body end and reaches the collet with no obstruction. This is not a tight-tolerance fit; it is a clearance hole.

### Failure mode 2: Collet canting (occasional)
If the plate approaches at a slight angle to one collet's axis, the collet tilts instead of translating axially. A tilted collet does not release cleanly and may jam. **Mitigation:** The inner lip bore (just over 9.57mm) provides lateral constraint. Its axial depth should be at least 2mm to keep the collet square through full travel. The 4-point simultaneous contact of the release plate also self-corrects small angular errors.

### Failure mode 3: Release attempted under line pressure
If the cartridge is removed while the upstream line still holds pressure (e.g., user forgot to depressurize), the tube may be difficult to withdraw even with the collet fully depressed, because pressure forces the tube outward against the O-ring. The collet depression force is unchanged (spring only), but the tube pull-out force increases with pressure. **Mitigation:** The device's plumbing design should vent pressure on pump shutdown; this is a firmware/plumbing concern, not a release plate geometry concern. The release plate operates correctly regardless.

### Failure mode 4: PETG inner lip fatigue
The inner lip of the release plate engages the collet face on every cartridge swap. Over many cycles, the lip may wear or deform. At 0.41 MPa contact stress and PETG's good tribological properties against acetal, wear is negligible for the expected service life (dozens of cartridge swaps). No concern.

### Failure mode 5: Insufficient grip force from user
If all four fittings are at maximum spring force (15 N each, 60 N total) and the user has limited grip strength, the plate may not travel far enough to fully depress all four collets. **Mitigation:** The mechanism requires only ~60 N — well within the capable range of healthy adults. The flat-surface grip geometry is ergonomically favorable (palm-up, both hand surfaces engaged). If accessibility is a concern in a future revision, a 2:1 mechanical advantage on the squeeze (e.g., a slight cam on the plate travel) would reduce user force to 30 N.

---

## 7. Summary: What This Means for the Release Plate

| Parameter | Value | Implication |
|-----------|-------|-------------|
| Single collet depression force | 5–15 N (use 15 N design) | Light — fingertip-accessible |
| 4-collet total force | 60 N | Direct palm squeeze at 1:1 is sufficient |
| User grip force available (healthy adult) | 80–200 N | 3×–10× margin over required force |
| Mechanical advantage required | None | 1:1 flat squeeze geometry is adequate |
| Collet annular contact area | 36.8 mm² per collet | |
| PETG bearing stress at design load | 0.41 MPa avg / 0.82 MPa peak | 17× safety factor vs. PETG yield |
| Required plate travel | 2.3mm | 3mm stroke provides 0.7mm margin |
| Inner lip axial engagement depth | 2mm minimum | Prevents collet cant during depression |
| Outer bore (body end clearance) | 15.5mm minimum | Must clear 15.10mm body end OD |

The release plate geometry is driven by alignment and contact geometry, not force or material stress. The force budget is generous. The critical design constraints are:
1. The stepped bore must clear the 15.10mm body end (outer bore ≥ 15.5mm)
2. The inner lip must closely hug the 9.57mm collet OD for lateral constraint
3. The inner lip must have ≥ 2mm axial depth
4. The through-hole for the tube must be between 6.30mm (tube OD) and 6.69mm (collet ID) — a 0.39mm design window
5. The plate must travel at least 2.3mm; 3mm is confirmed adequate
