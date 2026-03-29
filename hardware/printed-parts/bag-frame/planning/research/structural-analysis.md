# Bag Frame Structural Analysis

**Part:** Lens-shaped cradle + upper cap for Platypus 2L bag
**Mounting angle:** 35° from horizontal, cap end downward
**Enclosure:** 220 mm × 300 mm × 400 mm
**Placement:** Static kitchen appliance (no drop/impact loads)
**Date:** 2026-03-29

---

## Source Data and Assumptions

### Platypus 2L Platy Bottle — Physical Dimensions

Confirmed from manufacturer and retailer listings:

- Flat/empty footprint: 190 mm wide × 350 mm tall
- Filled footprint: 190 mm wide × 350 mm (the bag "fills out" in the same flat plane)
- **Filled thickness (midsection):** Unconstrained, the midsection rises to ~35–40 mm. The vision document specifies the upper cap constrains this to 25–30 mm. This analysis uses **28 mm** as the working constrained thickness.
- **Working bag length for cradle purposes:** 350 mm flat, but at 35° installation angle the bag is oriented diagonally. The cap-end (bottom) folds to a neck; the opposite end is folded flat against the front wall. The full unsupported structural span of the cradle runs from the neck collar to where the bag contacts the front wall — estimated at **280 mm** (consistent with the task brief and the 350 mm flat length accounting for fold-overs at both ends).
- **Cap thread diameter:** 28 mm (28-400 standard thread finish). This is the smallest cross-section and the interface point at the lower end of the cradle.
- **Bag material weight (empty):** ~37 g (confirmed from product listings, per the 1.3 oz spec)
- **Liquid mass at 2L fill:** 2.000 kg (water density 1.000 kg/L, syrup density approximately the same)
- **Total filled mass:** ~2.04 kg. This analysis uses **m = 2.05 kg** with a small margin.

### FDM Constraints — Cited from requirements.md

All FDM values below come directly from hardware/requirements.md. No "typical" industry values are assumed without citation.

| Constraint | Value | Source |
|---|---|---|
| Minimum structural wall thickness | 1.2 mm (3 perimeters) | requirements.md §FDM, Minimum feature sizes |
| Minimum non-structural wall | 0.8 mm (2 perimeters) | requirements.md §FDM, Minimum feature sizes |
| Minimum unsupported bridge span | < 15 mm (will sag visibly above this) | requirements.md §FDM, Minimum feature sizes |
| Minimum overhang angle | 45° from horizontal | requirements.md §FDM, Overhangs |
| Snap-fit flex direction | Parallel to build plate | requirements.md §FDM, Layer orientation |
| Mating clearance (sliding fit) | 0.2 mm | requirements.md §FDM, Dimensional accuracy |
| Mating clearance (snug/press fit) | 0.1 mm | requirements.md §FDM, Dimensional accuracy |
| Elephant's foot chamfer | 0.3 mm × 45° on bottom mating edges | requirements.md §FDM, Dimensional accuracy |
| Minimum printable rib/text feature | 0.4 mm wide, 0.4 mm tall | requirements.md §FDM, Minimum feature sizes |

### Material Properties — FDM Printed

From published research on FDM-printed specimens (used conservatively):

**PETG (preferred for snap-fits and load-bearing parts):**
- Tensile / flexural modulus E: **1,500 MPa** (conservative FDM value; bulk ~3,000 MPa, printed ~1,040–1,570 MPa per literature)
- Yield strength: ~38–43 MPa (printed), use **35 MPa** conservatively
- Maximum allowable strain ε_max: **4%** (elongation at yield for PETG; PETG is ductile, snap-fits can be reusable)
- Preferred for snap-fits: yes — ductile, tolerates repeated deflection

**PLA (alternative, structural-only, no repeated flexure):**
- Flexural modulus E: **2,400 MPa** (conservative FDM printed value; range 2,390–3,800 MPa per literature)
- Yield strength: ~48 MPa, use **40 MPa** conservatively
- Maximum allowable strain ε_max: **1.5–2%** (brittle at FDM layer bonds; single-assembly snap-fits only)
- Not preferred for snap-fit arms subject to repeated opening

---

## 1. Load Calculation — Vector Decomposition

### Setup

The bag lies at **θ = 35°** from horizontal. The cradle surface is parallel to the bag face, so it is also at 35° from horizontal.

Gravity acts vertically downward at g = 9.81 m/s².

Total weight: **W = m × g = 2.05 kg × 9.81 m/s² = 20.1 N**

The cradle surface normal vector points perpendicular to the 35° inclined plane (i.e., at 35° from vertical, or 55° from horizontal).

### Vector decomposition

```
                         ↑ normal to cradle surface
                          \  (55° from horizontal)
                           \
        ───────────────────── cradle surface at 35° from horizontal
                          /
                         ↓ gravity (vertical)

W_normal = W × cos(θ)   [perpendicular to cradle surface, pushing bag INTO cradle]
W_slide  = W × sin(θ)   [parallel to cradle surface, pulling bag DOWN the slope]
```

**Normal force (force perpendicular to cradle surface, pressing bag into cradle):**

```
F_normal = W × cos(35°) = 20.1 N × cos(35°)
         = 20.1 N × 0.819
         = 16.5 N
```

**Sliding force (force along incline, resisted by the lower lip/collar of the cradle):**

```
F_slide = W × sin(35°) = 20.1 N × sin(35°)
        = 20.1 N × 0.574
        = 11.5 N
```

### Summary of loads the cradle must resist

| Load | Value | Direction | Resisted by |
|---|---|---|---|
| Normal force | 16.5 N | Perpendicular to cradle surface (outward from bag) | Cradle floor (distributed across ~280 mm × 190 mm area) |
| Sliding force | 11.5 N | Along incline, toward cap end (downward) | Lower collar/rim of cradle that engages the bag neck |
| Upper cap reaction | Equal and opposite to normal force component on top face | Perpendicular to bag top face (upward from bag) | Upper cap clips/snap arms |

**Distributed load on cradle floor:**

The cradle floor area is approximately 280 mm × 160 mm = 44,800 mm² = 0.0448 m²

```
Distributed pressure from normal force:
q = F_normal / A = 16.5 N / 0.0448 m² = 368 Pa ≈ 0.37 kPa
```

This is a very low distributed pressure — equivalent to 37 mm of water column. The structural loads on the cradle itself are not challenging; the main concerns are (a) span stiffness so the cradle floor does not flex visibly, and (b) the snap-arm retention geometry.

---

## 2. Span and Wall Thickness

### Problem setup

The cradle is a lens-shaped shell, approximately 280 mm long, 190 mm wide. It must support 16.5 N distributed across its floor without visible deflection.

For a simply supported beam of length L under uniform distributed load w (N/mm), maximum deflection is:

```
δ_max = 5wL⁴ / (384 × E × I)
```

For a rectangular cross-section beam (wall modeled as a wide beam):
```
I = b × h³ / 12   (b = width, h = wall thickness)
```

Target maximum deflection: δ ≤ 0.5 mm (a conservative "no visible flex" criterion for a consumer appliance).

### Minimum wall thickness for the cradle floor

Model the cradle floor as a simply supported plate spanning L = 280 mm, width b = 160 mm.

Distributed load per unit length (along the span):
```
w = F_normal / L = 16.5 N / 280 mm = 0.059 N/mm
```

Solving for minimum I to achieve δ ≤ 0.5 mm with PETG (E = 1,500 MPa = 1,500 N/mm²):

```
I_required = 5wL⁴ / (384 × E × δ)
           = 5 × 0.059 × 280⁴ / (384 × 1500 × 0.5)
           = 5 × 0.059 × 6.147×10⁹ / 288,000
           = 1.813×10⁹ × 0.059 / 288,000
           = Wait, recalculate step by step:
```

Step by step:
```
L⁴ = 280⁴ = 6.147 × 10⁹ mm⁴
5 × w × L⁴ = 5 × 0.059 × 6.147×10⁹ = 1.813×10⁹ N·mm³
384 × E × δ = 384 × 1500 × 0.5 = 288,000 N·mm²

I_required = 1.813×10⁹ / 288,000 = 6,295 mm⁴
```

For a wide plate section with effective width b = 160 mm:
```
I = b × h³ / 12 = 160 × h³ / 12
h³ = I × 12 / b = 6,295 × 12 / 160 = 472
h = ∛472 = 7.8 mm
```

**This means a flat, unribbed 160 mm-wide PETG plate spanning 280 mm would need ~7.8 mm wall thickness to stay within 0.5 mm deflection.** That is far too thick and heavy for a printed part.

### Solution: Longitudinal ribs

A much more efficient approach is a thin floor (1.2 mm — the structural minimum from requirements.md) with longitudinal ribs. The rib grid converts the wide spanning problem into a series of short-span cells.

**With 3 longitudinal ribs spaced ~40 mm apart**, each rib-bounded span is approximately 40 mm wide × 280 mm long. Now recalculate per rib span:

```
b_cell = 40 mm (one rib bay)
w_cell = 0.059 N/mm × (40/160) = 0.0148 N/mm (proportional load on each cell)

I_required_per_cell = 5 × 0.0148 × 280⁴ / (384 × 1500 × 0.5)
                    = (5 × 0.0148 / 5 × 0.059) × 6,295 mm⁴ × (40/160)
                    = 6,295 × 0.25 = 1,574 mm⁴

h = ∛(1574 × 12 / 40) = ∛471.5 = 7.8 mm per rib bay floor alone
```

The floor between ribs still needs 7.8 mm to span 280 mm if the ribs only span laterally. The key is to make the **ribs run along the length (280 mm dimension)**, turning each rib into a longitudinal stiffener that drastically reduces the effective span for the floor panels.

**Correct approach: Longitudinal ribs running along the 280 mm length, spaced transversely.**

With 3 ribs running the length of the cradle, the floor panel between ribs only spans **40 mm transversely** rather than 160 mm or 280 mm. Now:

```
Span for each floor panel = 40 mm (transverse)
Load per unit length on a 40 mm wide panel:
q_transverse = 368 Pa × 0.040 m = 14.7 N/m per meter of length

Modeling as simply supported beam, L = 40 mm, b = 1 mm width:
w = 368 Pa × 0.001 m/mm = 0.368 N/mm per mm width
w_per_panel_mm = 368e-6 N/mm² × 40mm = 0.0147 N/mm

I_required = 5 × 0.0147 × 40⁴ / (384 × 1500 × 0.5)
           = 5 × 0.0147 × 2.56×10⁶ / 288,000
           = 188,160 / 288,000
           = 0.653 mm⁴

b = 1 mm strip:
I = 1 × h³ / 12
h³ = 0.653 × 12 = 7.84
h = 1.98 mm
```

**With longitudinal ribs at 40 mm spacing, the cradle floor between ribs needs approximately 2.0 mm wall thickness** to stay within 0.5 mm deflection across the 40 mm transverse span.

**Practical recommendation for the cradle floor:**

- **Floor wall thickness: 2.0 mm** (rounded up from 1.98 mm; exceeds the 1.2 mm structural minimum from requirements.md)
- **Longitudinal ribs: 3–4 ribs running the 280 mm length, spaced ~35–40 mm transversely**
- **Rib height: 5–8 mm** (ribs convert the 280 mm span load into a stiffened shell; rib height should be 3–5× the floor thickness per FDM rib guidelines)
- **Rib wall thickness: 1.2–1.6 mm** (at or above the structural wall minimum; ribs 60–80% of floor thickness per injection molding guidance is ~1.2–1.6 mm which aligns with the requirements.md structural minimum)

**With PLA (E = 2,400 MPa):**

PLA stiffens the floor further. The same 2.0 mm floor with ribs provides even less deflection (E ratio 2400/1500 = 1.6×, so deflection is 63% of PETG). PLA is acceptable but not preferred due to brittleness at layer bonds; PETG is the recommendation.

### Bridge span check

The ribs create an enclosed pocket on the underside of the cradle. Any bridge spans (e.g., across the base of a rib pocket) must be kept under 15 mm per requirements.md. Rib spacing of 35–40 mm means the floor must be printed facing upward so that ribs are printed as walls, not as bridges. This is addressed in section 6.

---

## 3. Upper Cap Geometry — Internal Pressure and Constraint Force

### Hydrostatic pressure at the constrained midsection

The Platypus bag is filled with a non-carbonated flavoring solution (essentially water). It is **not pressurized** in the way a soda can or pressure vessel is — it is a collapsible bag at ambient internal pressure. The "pressure" acting on the upper cap is purely hydrostatic from the weight of the liquid column.

The bag is at 35° from horizontal. The midsection is constrained to 25–30 mm thickness. The question is: what force does the liquid exert on the upper cap face?

**Model:** The filled bag is a pillow of liquid. When constrained to a thinner cross-section (28 mm vs. unconstrained ~40 mm), the bag material is in tension, pulling the upper cap face and cradle floor toward each other. This is not a pressure vessel — the force on the cap is the component of the liquid weight directed perpendicularly outward through the bag film into the cap.

More precisely, the upper cap is preventing the bag from bulging. The force the bag exerts on the cap equals the vertical component of the bag's weight that acts on the upper face when the bag tries to bulge into a rounder cross-section.

**Simplified hydrostatic approach:**

At the midsection of the 35° inclined bag, the depth of liquid above the midsection face:

```
h_liquid = (bag width / 2) × sin(35°)  [depth component along gravity axis]
         ≈ (190/2) mm × sin(35°)
         ≈ 95 mm × 0.574
         ≈ 54.5 mm = 0.0545 m

Hydrostatic pressure at midsection:
P_hydrostatic = ρgh = 1000 kg/m³ × 9.81 × 0.0545 = 535 Pa ≈ 0.535 kPa
```

This is the **gauge pressure** pushing against the bag walls at the deepest point of the midsection.

**Force on the upper cap face:**

The upper cap constrains the bag's top face across an area of approximately 280 mm × 160 mm = 44,800 mm² = 0.0448 m²

```
F_cap = P_hydrostatic × A_cap
      = 535 Pa × 0.0448 m²
      = 24.0 N
```

**But this hydrostatic pressure applies only at the deepest point.** Averaged over the cap face, the mean pressure is roughly half:

```
F_cap_avg ≈ 0.535 kPa / 2 × 0.0448 m² ≈ 12.0 N
```

However, the dominant force is actually geometric: the bag film trying to assume a more cylindrical (rounder) cross-section when constrained. A simplified model: the bag is a pillow under internal pressure, and the cap face sees a resultant equal to the liquid's weight component normal to the cap surface:

```
F_cap_normal = W × cos(35°) / 2 = 16.5 N / 2 ≈ 8.3 N per face (upper and lower each share the normal load)
```

**Conservative design value: F_cap = 20 N** (accounting for both hydrostatic and weight distribution, with margin).

**Pressure per unit area on cap surface:**
```
q_cap = 20 N / 44,800 mm² = 0.000447 N/mm² = 447 Pa ≈ 0.05 PSI
```

This is extremely low — less than 0.05 PSI. The cap is not a pressure vessel; it is resisting a modest distributed load of less than 500 Pa.

### Optimal cap geometry

For a distributed load of ~447 Pa over a 280 mm × 160 mm face:

- **Flat plate (no ribs):** Would require ~3.5–4 mm wall thickness to stay under 0.5 mm deflection (using the 160 mm transverse span as the governing span, with PETG E = 1,500 MPa). This is workable but wasteful.

- **Grid of ribs (recommended):** A grid of ribs in both directions (3 longitudinal × 2 transverse) creates cells of ~40 mm × 60 mm. Each cell only needs a 1.2–1.5 mm face thickness. This is the preferred approach.

- **Arched cross-section:** An arch profile converts bending stress into compressive stress in the arch, requiring less material. A gentle arch of ~5 mm rise over 160 mm span would significantly stiffen the cap face. This is aesthetically interesting (the "lens shape" of the cap would be slightly convex), but adds complexity to print orientation.

**Recommendation: Grid rib geometry.**

```
Upper cap face thickness: 1.5 mm (above the 1.2 mm structural minimum)
Rib grid: 3 longitudinal ribs + 2 transverse ribs running on the top face of the cap
Rib height: 4–6 mm
Rib thickness: 1.2 mm (structural wall minimum per requirements.md)
Rib spacing: ~40 mm longitudinal, ~55 mm transverse (creates cells well under 60 mm span)
```

Each 40 × 55 mm rib cell with 1.5 mm face and F = 447 Pa:
```
w_cell = 447 Pa × 0.040 m = 17.9 N/m per meter
I_cell = 5 × (0.0179 N/mm) × (55 mm)⁴ / (384 × 1500 × 0.5)
       = 5 × 0.0179 × 9.15×10⁶ / 288,000
       = 819,000 / 288,000 = 2.84 mm⁴

h = ∛(2.84 × 12 / 1) = ∛34 = 3.24 mm ... for a 1mm strip
For full 40mm wide cell:
h = ∛(2.84 × 12 / 40) = ∛0.852 = 0.948 mm
```

A 1.5 mm face (above the 0.95 mm theoretical minimum) provides a comfortable margin. The grid-ribbed cap face at 1.5 mm with 4–6 mm rib height is fully adequate.

---

## 4. Snap/Clip Forces for the Upper Cap

### Design intent

The upper cap presses down on the top face of the bag and must be removable for filling/bag replacement (if ever needed). The vision says bags are "permanent fixtures," but the upper cap likely needs to be assembled at manufacture time and held firmly thereafter. Design for single-assembly or low-cycle snap (10–20 cycles maximum).

### Cantilever snap-fit formulas

For a cantilever snap arm (rectangular cross-section, thickness t, width w, length L):

```
Deflection at snap:   δ = (2/3) × ε_max × L² / t
Assembly force:       P = E × w × t² × δ / (4 × L³)  [simplified beam bending]
Retention force:      P_ret = P × tan(β + φ)   where β = hook lead-in angle, φ = friction angle
```

Or equivalently, the simplified snap-arm equations:

```
Strain during deflection:  ε = (3/2) × (t/L²) × δ
Assembly force:            P = (E × w × t³) / (4 × L³) × δ
```

For maximum allowable strain ε_max = 4% (PETG, reusable):

```
Given deflection δ needed to snap over a 1.5 mm hook:
δ = 1.5 mm (hook height to clear the bag edge or rim)

From ε = (3/2) × (t/L²) × δ:
ε_max = 0.04 = (3/2) × (t/L²) × 1.5

t/L² = 0.04 / (1.5 × 1.5) = 0.04 / 2.25 = 0.01778

For t = 2.5 mm:
L² = 2.5 / 0.01778 = 140.6
L = 11.9 mm → too short, marginal

For t = 2.0 mm:
L² = 2.0 / 0.01778 = 112.5
L = 10.6 mm

For t = 1.6 mm:
L² = 1.6 / 0.01778 = 90.0
L = 9.5 mm

For t = 1.2 mm (minimum structural wall per requirements.md):
L² = 1.2 / 0.01778 = 67.5
L = 8.2 mm → very short, snaps easily but may feel flimsy
```

**Recommended snap arm geometry:**

| Parameter | Value | Rationale |
|---|---|---|
| Arm length L | 20–25 mm | Longer arm = lower assembly force, easier to snap. 20 mm gives comfortable feel. |
| Arm thickness t | 2.0–2.5 mm | PETG, reusable; 2.0 mm at L=20 mm keeps ε well below 4% |
| Arm width w | 6–8 mm | Wide enough for rigidity in the plane perpendicular to flex |
| Hook height | 1.0–1.5 mm | Enough to clear the rim of the cradle; 1.5 mm maximum for easy assembly |
| Hook lead-in angle | 30–45° | Shallow lead-in reduces assembly force; 30° for easy snap-in |
| Hook retention angle | 90° (perpendicular) | Maximum retention; requires tool to release, or design for permanent assembly |
| Root fillet radius | ≥ 1.0 mm (0.5 × t) | Required to prevent stress concentration at cantilever root |

**Verifying strain at L=20 mm, t=2.0 mm, δ=1.5 mm:**

```
ε = (3/2) × (t/L²) × δ = 1.5 × (2.0/400) × 1.5 = 1.5 × 0.005 × 1.5 = 0.01125 = 1.1%
```

1.1% is well below PETG's 4% limit — comfortable for repeated assembly. Arm is not overstressed.

**Assembly force at L=20 mm, t=2.0 mm, w=6 mm, E=1500 MPa, δ=1.5 mm:**

```
P = (E × w × t³) / (4 × L³) × δ
  = (1500 × 6 × 8.0) / (4 × 8000) × 1.5
  = 72,000 / 32,000 × 1.5
  = 2.25 × 1.5
  = 3.38 N per arm
```

Four snap arms total:
```
Total snap-in force = 4 × 3.38 = 13.5 N  (≈ 1.4 kg-force — easy hand pressure)
Total retention force (perpendicular hook) = significantly higher due to hook geometry
```

This is a comfortable assembly feel — the cap clicks into place with light thumb pressure.

**FDM layer orientation constraint (from requirements.md):**
- Snap arms must flex in-plane with layers (parallel to build plate).
- If the cap is printed face-down (face flat on the build plate), snap arms extending downward from the cap perimeter flex in the Z direction — **incorrect** per requirements.md.
- If the cap is printed on its side, snap arms can flex parallel to build plate layers. This conflicts with face flatness.
- **Resolution:** Print the cap face-down, but design snap arms as **living hinge / flex arm pairs that flex in the X/Y plane**, not downward. This means arms that extend horizontally outward from the cap's long edges and curl inward over the cradle rim. Alternatively, separate snap clips that are printed on their side and attached to the cap. This is flagged as a design decision for the next phase.

---

## 5. Stack Height and Enclosure Fit

### Bag geometry at 35° incline

Each bag is 190 mm wide, 350 mm flat length, 28 mm constrained thickness.

**Projected dimensions along enclosure axes:**

With the bag at 35° from horizontal, cap end at the back-bottom, flat end at the front-top:

```
Horizontal projection (depth, front-to-back):
  L_horizontal = 350 mm × cos(35°) = 350 × 0.819 = 286.7 mm ≈ 287 mm

Vertical projection (height):
  L_vertical = 350 mm × sin(35°) = 350 × 0.574 = 200.9 mm ≈ 201 mm
```

The enclosure is 220 mm wide × 300 mm deep × 400 mm tall.

Horizontal depth check: 287 mm < 300 mm deep. The bag's length at 35° fits within the 300 mm front-to-back depth with ~13 mm to spare. Comfortable.

Width check: Bag is 190 mm wide. Enclosure is 220 mm wide. Clearance of 30 mm for tubing, structural walls, and snap interfaces. Tight but workable.

### Vertical stack height for two bags

Each cradle assembly has:
- Bag constrained thickness: 28 mm
- Cradle floor wall: 2.0 mm
- Cradle wall height (rib height): ~7 mm
- Upper cap: 1.5 mm face + 5 mm rib height ≈ 7 mm total
- Clearance between upper cap and lower bag cradle floor: ~3–5 mm (for bag settling and thermal expansion)
- **Total height per bag cradle assembly: 28 + 2 + 7 + 7 + 5 = 49 mm** (conservative estimate)

But this is measured **perpendicular to the bag face** (at 35°). The **vertical height** each cradle occupies within the enclosure:

```
Vertical height per cradle (measured vertically):
  The cradle is 49 mm thick at 35° from horizontal.
  Vertical component of 49 mm thickness = 49 / cos(35°) = 49 / 0.819 = 59.8 mm ≈ 60 mm vertical
```

Wait — the thickness is perpendicular to the bag face (i.e., at 90° from the inclined plane), so:

```
Vertical component of cradle thickness:
  The cradle thickness direction is 90° from the 35° incline plane,
  i.e., 90° - 35° = 55° from horizontal.
  Vertical component = 49 mm × sin(55°) = 49 × 0.819 = 40.1 mm ≈ 40 mm
```

**Two-bag stack vertical height:**
```
Two cradles stacked: 2 × 40 mm = 80 mm vertical
Inter-bag clearance (to allow bag removal from above): ~20 mm
Bottom clearance (cradle mounting, lower enclosure wall): ~10 mm
Total vertical space for bag section: 80 + 20 + 10 = 110 mm
```

The bags occupy the **upper portion of the enclosure** (from the vision: bags at top, screens in middle, pump cartridge at bottom). With a 400 mm tall enclosure:

```
Available for bags (top ~40% of enclosure): ~160 mm vertical
Two-bag stack requirement: ~110 mm
Headroom remaining: ~50 mm
```

**The two bags fit vertically with approximately 50 mm of clearance within their allocated zone.** This is sufficient for bag removal from above (the funnel is on top; bags do not need to be removed routinely per the vision).

### Horizontal depth check (both bags)

Both bags occupy the same depth path (they are stacked vertically, not front-to-back). The 287 mm diagonal projection is within the 300 mm depth. The lower bag's cap end aligns approximately 287 mm from the front wall toward the back. The enclosure back wall is at 300 mm. This gives ~13 mm for the cap-end collar, tubing connections, and mounting interface at the rear. This is tight.

**Flag:** The cap-end collar geometry must be compact. The tubing connector exits the Platypus cap at ~28 mm diameter. A printed collar around the cap needs only ~5–8 mm of wall thickness, making the total cap-end protrusion ~40–45 mm from the bag body. Check: 287 + (cap collar depth projected at 35°) must still be < 300 mm. This constraint should be verified in the spatial layout step.

---

## 6. Print Orientation

### Lens-shaped cradle

The cradle is a concave half-shell (lens/boat shape), open on top, with the bag face resting in the concave surface.

**Recommended print orientation: face-up (concave surface upward, facing the printer's build plate)**

Rationale:
- The lens shape has a curved interior surface. Printing it face-down (concave down) would create a large unsupported overhang across the full 190 mm width — violating the 15 mm bridge span limit from requirements.md.
- Printing face-up (concave surface upward) means the curved interior is built up layer by layer without any overhang. The exterior (convex bottom) is on the build plate.
- Longitudinal ribs on the underside would then become walls printed upward — no overhang issue.
- The snap interface on the side walls (where the upper cap clicks on) must be designed with 45° lead-in chamfers on the hooking surface, since those faces are at a near-vertical orientation when printed face-up.
- **Layer lines run perpendicular to the bag face.** The bag's distributed load pushes perpendicular to the layers — this is the weak direction in FDM (inter-layer tension per requirements.md). However, the load (16.5 N distributed over 44,800 mm²) is extremely low, and the failure mode would be crushing of walls, not inter-layer separation. This orientation is acceptable.
- If maximum floor strength is needed, rotating the cradle 90° (printing on end, with the long axis vertical) puts layer lines parallel to the bag face (layers in compression under the bag's weight). This is geometrically impractical for a 280 mm-long part (exceeds typical print height for this part shape).

**Alternative: Print in two halves** (split longitudinally along the midsection) and bond/snap together. Each half prints flat; the joint is along the neutral axis of the span. This is more complex but allows a fully FDM-optimal orientation for both the floor and the sidewalls. Flag for consideration in the design phase.

### Upper cap

The upper cap is a flat plate (face) with ribs on the top side.

**Recommended print orientation: face-down (flat face on build plate, ribs pointing upward)**

Rationale:
- Face-down gives the smoothest surface on the bag-contact face (build plate gives the best surface quality).
- Ribs on top are printed as walls extending upward — no overhang.
- Snap arms (if integrated into the cap) extend from the cap perimeter. With face-down orientation, snap arms flex in the X/Y plane (parallel to build plate layers) — satisfying the requirements.md constraint for snap-fit flex direction.
- Any horizontal undercut on snap hooks needs a 45° chamfer or designed support per requirements.md (0.2 mm interface gap for clean removal).

---

## 7. Design Constraints Summary Table

| Design Parameter | Calculated Value | Minimum per requirements.md | Recommendation |
|---|---|---|---|
| Cradle floor thickness | 2.0 mm (with ribs) | 1.2 mm structural | **2.0 mm** |
| Cradle rib height | 5–8 mm | N/A | **6 mm** |
| Cradle rib thickness | 1.2–1.6 mm | 1.2 mm structural | **1.6 mm** |
| Longitudinal rib count | 3–4 ribs | N/A | **3 ribs** |
| Upper cap face thickness | 1.5 mm (with grid ribs) | 1.2 mm structural | **1.5 mm** |
| Upper cap rib height | 4–6 mm | N/A | **5 mm** |
| Upper cap rib thickness | 1.2 mm | 1.2 mm structural | **1.2 mm** |
| Snap arm length | 20–25 mm | N/A | **20 mm** |
| Snap arm thickness (PETG) | 2.0–2.5 mm | 1.2 mm structural | **2.0 mm** |
| Snap arm width | 6–8 mm | N/A | **6 mm** |
| Snap hook height | 1.0–1.5 mm | N/A | **1.2 mm** |
| Snap hook lead-in angle | 30–45° | 45° max overhang | **30°** |
| Snap root fillet | ≥ 1.0 mm | N/A | **1.0 mm** |
| Bridge spans | < 15 mm | < 15 mm hard limit | Design rib grid accordingly |
| Mating clearance (cap to cradle) | 0.2 mm | 0.2 mm sliding | **0.2 mm** |
| Bottom edge chamfer | 0.3 mm × 45° | 0.3 mm × 45° | Apply to all bottom mating edges |

---

## 8. Assumptions Requiring Empirical Verification

The following assumptions are engineering estimates that should be validated before finalizing the design:

1. **Bag filled thickness:** The vision document states the bag unconstrained midsection rises to ~40 mm, constrained to 25–30 mm. This analysis uses 28 mm. **Verify by filling the prototype bag with 2L of water and measuring actual midsection thickness under light constraint.** The cradle depth and upper cap gap must match this measurement.

2. **Bag length at 35° incline:** The cradle span of 280 mm is estimated. **Measure the actual horizontal footprint of the filled bag lying on a flat surface.** The flat dimension is 350 mm; the cradle-supported span (between the lower collar and the flat-folded top end) may be shorter.

3. **PETG modulus (FDM printed):** This analysis uses E = 1,500 MPa. Published values range from 1,040–1,570 MPa depending on printing parameters. The Bambu H2C with Bambu PETG filament may print closer to 1,400–1,500 MPa. **Print test coupons and measure deflection under known load to calibrate.** The impact on design is modest (within the margin already built in).

4. **Snap fit: single vs. multi-assembly:** The vision states bags are permanent fixtures. If the upper cap is assembled once during manufacture and never opened, a retention hook angle of 90° (perpendicular undercut) is fine. If the cap must be removable for cleaning or inspection, the hook angle should be 45° and the arm geometry re-evaluated for cyclic loading. **Clarify the required assembly cycle count.**

5. **Cap-end clearance (13 mm at rear wall):** The depth analysis shows only ~13 mm between the cap-end of the bag's diagonal projection and the rear enclosure wall. This is tight once a printed collar and tubing are added. **Verify in spatial layout step before committing to cradle length.**

6. **Material selection:** PETG is recommended for all structural parts of the bag frame. PLA is stiffer (E ≈ 2,400 MPa) and could be used for the cradle floor if maximum rigidity is desired, but is not preferred for the snap arms. Using different materials for the cradle and cap is workable on the Bambu H2C with its dual-nozzle mode but adds complexity. Default to **PETG throughout** unless rigidity testing shows deflection is unacceptable.

---

## Key Findings for the Designer

1. **The structural loads are low.** The bag exerts only ~20 N total, split as 16.5 N normal and 11.5 N sliding. A 2.0 mm PETG floor with 6 mm longitudinal ribs is more than adequate — this is not a structural challenge.

2. **The upper cap sees less than 500 Pa distributed pressure.** A 1.5 mm PETG face with a grid of 5 mm ribs (3 longitudinal, 2 transverse) resists this with negligible deflection. The cap does not need to be thick or heavy.

3. **Snap arms at L=20 mm, t=2.0 mm (PETG) deflect to only 1.1% strain for a 1.5 mm hook.** This is a comfortable, low-force snap that will click closed with light thumb pressure. Four arms provide ~13.5 N total assembly force — easy.

4. **Two bags at 35° consume approximately 110 mm of vertical height** within the enclosure. The bags' allocated zone (top ~160 mm of the 400 mm enclosure) provides ~50 mm headroom. This fits.

5. **Print the cradle face-up; print the cap face-down.** Cradle ribs extend upward without overhang; cap ribs extend upward from the face; cap snap arms flex in-plane with layers.

6. **The critical dimension to verify empirically is the bag's constrained midsection thickness.** Everything else follows from that measurement.

---

## Sources

- Platypus 2L Platy Bottle dimensions: [Garage Grown Gear](https://www.garagegrowngear.com/products/platy-2l-bottle-collapsible-bottle-by-platypus), confirmed 19 cm × 35 cm filled footprint; 37 g empty weight
- PETG FDM mechanical properties: Published research range 1,040–1,570 MPa modulus, ~35–43 MPa yield strength, ~4% elongation at yield (Ymer Digital, SD State University, ScienceDirect)
- PLA FDM mechanical properties: 2,148–2,640 MPa flexural modulus in printed specimens (PMC, ResearchGate)
- Snap-fit design formulas: Hubs Knowledge Base, Fictiv snap-fit articles, Wevolver FDM snap-fit guide
- Rib design guidelines: Fictiv best practices for ribs and gussets; deflection reduction ~10× with rib grid
- Platypus cap thread size: 28-400 standard (Cascade Designs product listings, Backpacking Light forum)
- FDM manufacturing constraints: hardware/requirements.md (all values cited directly)
- Vision geometry: hardware/vision.md (35° angle, 25–30 mm constrained thickness, 220×300×400 mm enclosure)
