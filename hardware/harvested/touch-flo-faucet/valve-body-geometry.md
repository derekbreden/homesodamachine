# Touch-Flo Valve Body Geometry

**Part:** Westbrass R2031-NL-12 Touch-Flo valve  
**Measured:** 2026-04-27  
**Measurement tool:** Neiko digital caliper (mm mode, shown in all photos)  
**External constraint:** Standard countertop hole = 1-3/8" = 34.93 mm diameter  
**Note:** The threaded shank below the body is irrelevant to shell design and is excluded from all measurements.

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
| Water port: gap from port wall to arch inner face | ~2.125 mm | ~0.084" | Derived; ≈ 2 mm per Photo 7 | Derived |
| Water port diameter | 9.75 mm | 0.384" | Photo 8 | Measured |
| Water port center (X) | 0.0 mm | 0" | Centered in 31.50 mm long axis | Exact |
| Water port center (Y) | 0.0 mm | 0" | Centered in 14.0 mm plateau | Exact |
| Arch width (each) | 1.5 mm | 0.059" | Confirmed | Measured |
| Plateau width (between arch inner faces) | 14.0 mm | 0.551" | Derived (17 − 2 × 1.5) | Exact |
| Arc height (arc base to arc peak) | 5.0 mm | 0.197" | Derived (46 − 41) | Exact |
| Plateau below arc base | 2.0 mm | 0.079" | Derived (41 − 39) | Exact |
| Rectangular upper body height | 26.0 mm | 1.024" | Derived (39 − 13) | Exact |
| Countertop hole (external constraint) | 34.93 mm | 1.375" | Spec | Exact |

---

## 3. Geometric Description

### 3.1 Overall Form — Two Zones

The body has two distinct axial zones:

**Zone 1 — Cylindrical base (0–13 mm from bottom)**  
Circular cross-section, **31.50 mm OD**, **13 mm tall**. This is the section that would
sit above the countertop shoulder/flange and establishes the body's round footprint.

**Zone 2 — Rectangular upper body (13–46 mm from bottom)**  
Above 13 mm, the body transitions to a rectangular cross-section and stays rectangular
all the way to the top arc features. Cross-section: **31.50 mm × 17 mm**.

- The 31.50 mm dimension carries forward from the base cylinder — it is the full diameter.
- The 17 mm dimension is the thinner axis — the body is substantially narrower in this direction.
- When viewed from above, the body looks like a rectangle with one long side equal to the circle diameter.

### 3.2 Top Surface Features (39–46 mm)

The top of the rectangular body has three features across its face:

**Plateau** — at **39 mm** height. A flat area (or shallow saddle) that sits between the two arc features. It is 2 mm below where the arcs begin (41 mm), making it slightly inset.

**Two arc/arch features** — there are two raised arch features, one over the water port and one over the solid brass actuator plunger. They begin curving upward at **41 mm** and peak at **46 mm**, giving each arc a rise of **~5 mm**.

The arrangement viewed from above: two rounded humps side by side across the rectangular top face, separated by the plateau between them.

### 3.3 Water Port

- **Single water port only.** There is no second fluid port.
- Location: top face of the rectangular body, centered in the plateau between the two arches
- Port diameter: **9.75 mm**
- Port center in long axis (X): **0 mm** — centered in the 31.50 mm long dimension
- Port center in short axis (Y): **0 mm** — centered in the 14.0 mm plateau (between arch inner faces)
- Gap from port wall to each arch inner face: **(14.0 − 9.75) / 2 = 2.125 mm** ≈ 2 mm (Photo 7)
- Port fitting: brass
- The port is in the open plateau zone between the two arches; the tube exits straight upward

### 3.4 Actuator Plunger (Not a Port)

The second brass feature visible at the top face is a **solid brass plunger** — a mechanical actuator, not a fluid port. No water flows through it.

Mechanism: lever/cap pressed down → lever arm lifts the solid brass plunger upward → plunger opens the water port internally.

The plunger is covered by the second arc feature at the top. Its OD has not been directly measured (see Open Questions).

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

The body mounts through a standard 1-3/8" (34.93 mm) countertop hole. The 31.50 mm body OD fits through this hole with ~3.4 mm diametric clearance (1.7 mm per side). The exact shoulder/flange geometry is not measured but must exist to stop the body from passing fully through the hole.

**Summary of what goes where relative to the deck:**

| Position | Feature | Key Dimension |
|----------|---------|---------------|
| Above deck | Full body: cylindrical base + rectangular upper + arc features | 46 mm total height |
| At deck | Shoulder/flange (not measured) | OD > 34.93 mm |
| Below deck | Threaded shank + locknut | Not measured; not relevant to shell |

---

## 5. Shell Design Implications

**The shell wraps around the body exterior.** The body's footprint at the base is a 31.50 mm circle; above 13 mm it becomes 31.50 mm × 17 mm. A cylindrical shell with 31.50 mm + clearance inner bore fits the base. Above 13 mm the shell can follow the rectangular profile or maintain a cylinder that clears the rectangle (i.e., inner bore ≥ diagonal of 31.50 × 17 rectangle = ~35.9 mm, or just clear the 31.50 mm long dimension which already drives the minimum).

**The arc features at the top** (up to 46 mm) protrude above the rectangular body. The shell can stop at or below 39 mm (plateau) and let the arc features and actuator cap fully protrude, or it can follow the arc profile if a closer fit is desired.

**Only one tube** exits the top face — the water supply line to the 9.75 mm port. The shell needs a managed exit path for this one tube only.

**The actuator plunger** needs free vertical travel as the lever operates. Any shell feature near the top of the body must not restrict the plunger's upward stroke.

**Installation sequence (single-piece cylindrical shell):**
1. Mount the valve through the countertop and tighten the locknut.
2. Slide the shell down over the body from the top. Shell inner bore must clear the 31.50 mm base cylinder with enough clearance to slide freely.
3. Shell rests on the countertop surface around the valve body.

---

## 6. Open Questions

| # | Unknown | Why It Matters | How to Measure |
|---|---------|----------------|----------------|
| 1 | Shoulder/flange OD | Sets the shell's lower landing reference | Caliper across flange |
| 2 | Shoulder/flange axial thickness | Sets shell base geometry | Caliper from flange bottom to body base |
| 3 | ~~Which body edge the 2 mm port measurement is from~~ | ✅ Resolved: 2 mm from the long side (31.50 mm face); centered on the short axis | — |
| 4 | Actuator plunger OD | Sizes clearance in any shell top face | Caliper directly on the brass plunger |
| 5 | Port-to-plunger center-to-center distance | Locates both features on the top face | Caliper center-to-center |
| 6 | Transition geometry (abrupt step or tapered?) at 13 mm where round becomes rectangular | Affects shell fit at the transition zone | Direct visual + caliper at the transition |
| 7 | Overall assembled height including any cap or lever hardware that rides above the arc peak | Sets total shell height if shell follows the full profile | Ruler from deck to top of lever at rest |
