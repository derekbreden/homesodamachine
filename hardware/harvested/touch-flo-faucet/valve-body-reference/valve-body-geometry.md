# Touch-Flo Valve Body Geometry

**Part:** Westbrass R2031-NL-12 Touch-Flo valve  
**Measured:** 2026-04-27  
**Measurement tool:** Neiko digital caliper (mm mode, shown in all photos)  
**External constraint:** Standard countertop hole = 1-3/8" = 34.93 mm diameter  
**Note:** The threaded shank below the body IS modeled in the reference solid (Ø 11 mm × 50 mm long, centered on the body axis) — it's the through-deck portion that the under-deck shell must accommodate.

**Reference solid:** `valve-body-reference/generate_step_cadquery.py`  
Regenerate: `tools/cad-venv/bin/python hardware/harvested/touch-flo-faucet/valve-body-reference/generate_step_cadquery.py`

---

## 1. Per-Photo Inventory

| Photo | What is measured | Caliper reading |
|-------|-----------------|-----------------|
| 1 | Overall body height — base to peak of the rounded arc at the very top | **46 mm** |
| 2 | Body height — base to **bottom** of the arc feature (where the arc begins curving upward) | **41 mm** |
| 3 | Body height — base to the **plateau** that sits between the two arc features (the plateau is inset slightly below the arc bases) | **39 mm** |
| 4 | Height at which the body cross-section transitions from **round** (cylindrical base) to **rectangular** (upper body) | **13 mm** |
| 5 | Diameter of the round base section — also equals the **long dimension** of the rectangle in the upper body | **31.50 mm** |
| 6 | **Short dimension** of the rectangular upper body cross-section (the thinner axis, as seen from above or from the side) | **17 mm** |
| 7 | Distance from the **body edge to the near wall** of the water port | **2 mm** |
| 8 | **Water port diameter** | **9.75 mm** |

---

## 2. Measured Dimensions

| Feature | Value (mm) | Value (in) | Source | Confidence |
|---------|-----------|-----------|--------|------------|
| Overall body height (base to arc peak) | 46.0 mm | 1.811" | Photo 1 | Measured |
| Height to arc base (where arcs begin) | 41.0 mm | 1.614" | Photo 2 | Measured |
| Height to plateau (between arc features) | 39.0 mm | 1.535" | Photo 3 | Measured |
| Height of cylindrical base section | 13.0 mm | 0.512" | Photo 4 | Measured |
| Base cylinder OD = rectangle long dimension | 31.50 mm | 1.240" | Photo 5 | Measured |
| Rectangle short dimension | 17.0 mm | 0.669" | Photo 6 | Measured |
| Water port: gap from port wall to arch inner face (Y) | ~2.125 mm | ~0.084" | Derived: (14.0 − 9.75) / 2 | Derived |
| Water port: gap from port wall to short face (X) | 2.0 mm | 0.079" | Photo 7 | Measured |
| Water port diameter | 9.75 mm | 0.384" | Photo 8 | Measured |
| Water port center (X) | 8.875 mm | 0.349" | 2 mm from short face (X = ±15.75 mm); derived: 15.75 − 2 − 4.875 | Derived |
| Water port center (Y) | 0.0 mm | 0" | Centered in 14.0 mm plateau (between arch inner faces) | Exact |
| Arch width (each) | 1.5 mm | 0.059" | Confirmed | Measured |
| Plateau width (between arch inner faces) | 14.0 mm | 0.551" | Derived (17 − 2 × 1.5) | Exact |
| Arc height (arc base to arc peak) | 5.0 mm | 0.197" | Derived (46 − 41) | Exact |
| Plateau below arc base | 2.0 mm | 0.079" | Derived (41 − 39) | Exact |
| Rectangular upper body height | 26.0 mm | 1.024" | Derived (39 − 13) | Exact |
| Countertop hole (external constraint) | 34.93 mm | 1.375" | Spec | Exact |
| Shank diameter (below deck) | 11.0 mm | 0.433" | User | Stated |
| Shank length (below deck) | 50.0 mm | 1.969" | User | Stated |
| Shank center | (X=0, Y=0) | — | User | Stated |

---

## 3. Geometric Description

### 3.1 Overall Form — Three Zones

The reference solid has three distinct axial zones:

**Zone 0 — Threaded shank (Z = -50 → 0, below deck)**  
Plain cylinder, **11 mm OD**, **50 mm long**, centered on the body axis at (X=0, Y=0). This is the through-deck portion that passes through the 1-3/8" countertop hole; a locknut clamps it from below. Thread profile is not modeled in the reference solid (irrelevant for envelope work).

**Zone 1 — Cylindrical base (Z = 0 → 13 mm, above deck)**  
Circular cross-section, **31.50 mm OD**, **13 mm tall**. The bottom face (Z=0) is the deck-resting surface — the body sits on top of the countertop with the shank passing through.

**Zone 2 — Rectangular upper body (Z = 13 → 39 mm)**  
Above 13 mm, the body transitions to a rectangular cross-section and stays rectangular
all the way to the top arc features. Cross-section: **31.50 mm × 17 mm**.

- The 31.50 mm dimension carries forward from the base cylinder — it is the full diameter.
- The 17 mm dimension is the thinner axis — the body is substantially narrower in this direction.
- When viewed from above, the body looks like a rectangle with one long side equal to the circle diameter.

### 3.2 Top Surface Features (39–46 mm)

The top of the rectangular body has three features across its face:

**Plateau** — at **39 mm** height. A flat area (or shallow saddle) that sits between the two arc features. It is 2 mm below where the arcs begin (41 mm), making it slightly inset.

**Two side arches — identical** — two raised arch ridges run along the long-axis edges of the top face, one at +Y and one at -Y. They are flanking ridges, NOT roof features over any specific top-face component. Each arch is 1.5 mm wide in Y and spans the full X length of the body. They begin curving upward at **41 mm** and peak at **46 mm** at X = 0, giving each arch a rise of **~5 mm**.

The arrangement viewed from above: two rounded humps along the long edges of the rectangular top face, separated by the plateau between them. The brass plunger and the water port both sit IN the plateau (see §3.3 and §3.4), not under the arches.

### 3.3 Water Port

- **Single water port only.** There is no second fluid port.
- Location: top face of the rectangular body, centered in the plateau between the two arches
- Port diameter: **9.75 mm**
- Port center in long axis (X): **8.875 mm** from body center — 2 mm gap from the short face at X = ±15.75 mm; derived as 15.75 − 2 − 4.875 = 8.875 mm
- Port center in short axis (Y): **0 mm** — centered in the 14.0 mm plateau (between arch inner faces)
- Gap from port wall to each arch inner face: **(14.0 − 9.75) / 2 = 2.125 mm** ≈ 2 mm (Photo 7)
- Port fitting: brass
- The port is in the open plateau zone between the two arches; the tube exits straight upward

### 3.4 Actuator Plunger (Not a Port)

The second brass feature visible at the top face is a **solid brass plunger** — a mechanical actuator, not a fluid port. No water flows through it.

- Location: **body center, X = 0, Y = 0**, in the plateau (NOT under either arch)
- Approximately **1 mm** gap between the plunger wall and the water port wall (port wall sits at X ≈ +4.0 mm; plunger wall therefore at X ≈ +3.0 mm)
- Plunger OD therefore ≈ **6 mm** (derived from the 1 mm gap; not yet caliper-confirmed)

Mechanism: lever pressed down → lever arm lifts the solid brass plunger upward → plunger opens the water port internally. The lever attaches to the plunger and swings in the **-X half** of the body.

### 3.5 Surface Treatments

| Zone | Finish | Material (likely) |
|------|--------|------------------|
| Main body (both zones) | Matte black anodized or painted | Aluminum or zinc |
| Water port fitting | Bare brass | Brass |
| Actuator plunger | Bare brass | Brass (solid) |
| Threaded shank (below deck — not measured) | Chrome plated | Steel or brass |
| Locknut | Silver/chrome | Steel |

---

## 4. Countertop Mounting Interface

The body sits on top of the countertop. The **11 mm threaded shank** (Zone 0) passes through the standard 1-3/8" (34.93 mm) hole with substantial radial clearance, and a locknut clamps the body from below. The **31.50 mm body OD** is wider than the 11 mm hole footprint, so the body's bottom face (Z=0) lands on the deck and acts as the retention shoulder — no separate flange or trim ring is required to stop pass-through.

**Summary of what goes where relative to the deck:**

| Position | Feature | Key Dimension |
|----------|---------|---------------|
| Above deck | Full body: cylindrical base + rectangular upper + arc features | 46 mm total height |
| At deck (Z = 0) | Body bottom face — sits on the countertop | 31.50 mm OD landing |
| Below deck | Ø 11 mm shank, 50 mm long; locknut clamps from below | Z = -50 → 0 |

---

## 5. Shell Design Implications

**The shell wraps around the body exterior.** The body's footprint at the base is a 31.50 mm circle; above 13 mm it becomes 31.50 mm × 17 mm. A cylindrical shell with 31.50 mm + clearance inner bore fits the base. Above 13 mm the shell can follow the rectangular profile or maintain a cylinder that clears the rectangle (i.e., inner bore ≥ diagonal of 31.50 × 17 rectangle = ~35.9 mm, or just clear the 31.50 mm long dimension which already drives the minimum).

**The arc features at the top** (up to 46 mm) protrude above the rectangular body. The shell can stop at or below 39 mm (plateau) and let the arc features and actuator cap fully protrude, or it can follow the arc profile if a closer fit is desired.

**Lever clearance — hard constraint.** The lever attaches to the plunger at body center and swings in the -X half of the body. The shell **must leave the entire -X half of the top face open**, including the plateau strip between the two arches forward (toward -X) of the water port. Concretely, the shell's top closure can extend over (a) the +X end behind the water port and (b) the two side arches at ±Y, but it cannot bridge the plateau anywhere from the water port forward to the -X edge.

**Only one tube** exits the top face — the water supply line to the 9.75 mm port at X = +8.875 mm. The shell needs a managed exit path for this one tube only.

**The actuator plunger** needs free vertical travel as the lever operates. Any shell feature near the body center (X = 0, Y = 0) must not restrict the plunger's upward stroke.

**Installation sequence (single-piece cylindrical shell):**
1. Mount the valve through the countertop and tighten the locknut.
2. Slide the shell down over the body from the top. Shell inner bore must clear the 31.50 mm base cylinder with enough clearance to slide freely.
3. Shell rests on the countertop surface around the valve body.

---

## 6. Open Questions

| # | Unknown | Why It Matters | How to Measure |
|---|---------|----------------|----------------|
| 1 | ~~Shoulder/flange OD~~ | Resolved: there's no separate flange — the 31.50 mm body bottom face is the deck-landing shoulder. | — |
| 2 | ~~Shoulder/flange axial thickness~~ | Resolved: the body itself sits on the deck; no flange exists. | — |
| 3 | ~~Which body edge the 2 mm port measurement is from~~ | ✅ Resolved: 2 mm from the long side (31.50 mm face); centered on the short axis | — |
| 4 | ~~Actuator plunger OD~~ | Partially answered: ~6 mm derived from the ~1 mm gap to the 9.75 mm water port. Caliper-confirm when convenient. | Caliper directly on the brass plunger |
| 5 | ~~Port-to-plunger center-to-center distance~~ | Resolved: port at X = +8.875 mm, plunger at X = 0 → center-to-center = 8.875 mm. | — |
| 6 | Transition geometry (abrupt step or tapered?) at 13 mm where round becomes rectangular | Affects shell fit at the transition zone | Direct visual + caliper at the transition |
| 7 | Overall assembled height including any cap or lever hardware that rides above the arc peak | Sets total shell height if shell follows the full profile | Ruler from deck to top of lever at rest |
