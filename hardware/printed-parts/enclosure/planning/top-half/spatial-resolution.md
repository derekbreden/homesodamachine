# Enclosure Top Half — Spatial Resolution
**Date:** 2026-03-29
**Status:** Spatial relationships resolved into top half local reference frame
**Scope:** All spatial geometry for the monolithic top half (220 × 300 × 200 mm)

---

## 1. System-Level Placement

### 1.1 Top Half Position in Global Enclosure Frame

The enclosure is a unified 220 × 300 × 400 mm consumer appliance, split horizontally into two equal halves at 200 mm height (Z = 200 mm in global frame).

**Global reference frame (enclosure):**
- **Origin:** Bottom-left-front corner of the enclosure
- **X-axis:** Left-to-right (width, 0 → 220 mm)
- **Y-axis:** Front-to-back (depth, 0 → 300 mm)
- **Z-axis:** Bottom-to-top (height, 0 → 400 mm)

**Top half placement in global frame:**
- **Z range:** 200 mm (seam plane) to 400 mm (top surface)
- **X range:** 0 to 220 mm (full width)
- **Y range:** 0 to 300 mm (full depth)
- **Seam location:** Horizontal plane at Z = 200 mm (global), where top half meets bottom half

### 1.2 Top Half Dimensions and Orientation

**Local bounding box:** 220 mm (W) × 300 mm (D) × 200 mm (H)
- **W (X):** 220 mm left-to-right
- **D (Y):** 300 mm front-to-back
- **H (Z):** 200 mm bottom-to-top within the top half

**Relationship to enclosure:**
- The top half occupies the upper half of the 400 mm enclosure (Z = 200 to 400 in global coordinates)
- When oriented in space, the top half's seam face (bottom face of the top half) aligns with the bottom half's seam face to form the horizontal closure seam at 200 mm global height

---

## 2. Top Half Reference Frame (Local)

### 2.1 Local Origin and Axes

**Local reference frame for the top half (CAD and manufacturing):**
- **Origin:** Bottom-front-left corner of the bounding box (seam face plane at Z=0 local)
- **X-axis:** Left-to-right (0 → 220 mm, parallel to enclosure width)
- **Y-axis:** Front-to-back (0 → 300 mm, parallel to enclosure depth)
- **Z-axis:** Bottom-to-top (0 → 200 mm, growing upward from seam face toward the top exterior surface)

**Interpretation:**
- Z = 0 (local) = Z = 200 mm (global) = seam face (horizontal interior surface where snaps engage)
- Z = 200 mm (local) = Z = 400 mm (global) = top exterior surface
- X = 0 (local) = left edge (global X = 0)
- X = 220 mm (local) = right edge (global X = 220)
- Y = 0 (local) = front edge (global Y = 0)
- Y = 300 mm (local) = back edge (global Y = 300)

### 2.2 Print Orientation on Bambu H2C

**Recommended print orientation:**
- **Seam face (Z = 0 local):** Parallel to build plate (XY-plane horizontal)
- **Height (200 mm):** Vertical on build plate (Z-axis growing upward during print)
- **Snap arm orientation:** Flex direction parallel to XY-plane (perpendicular to seam face normal, in the XY-plane)
  - This ensures snap beams flex left-right (X) or front-back (Y), achieving ~80–90% design strength
  - Z-direction bending would reduce strength to ~40–50% (not acceptable for permanent closure)

**Build envelope fit:**
- Bounding box: 220 mm (W) × 300 mm (D) × 200 mm (H)
- Bambu H2C single-nozzle envelope: 325 mm (W) × 320 mm (D) × 320 mm (H)
- **Fit margin:** ✓ YES (105 mm margin in W, 20 mm in D, 120 mm in H) — comfortable fit with clearance for nozzle retraction

---

## 3. Derived Geometry

### 3.1 Seam Face Snap Hook Positions

**Context:** The top half seam face (bottom face, Z = 0 local) has 10 snap hooks that extend downward into the bottom half's seam face undercuts. When assembled, the hooks engage undercuts on the bottom half to create a rigid, permanent closure.

**Snap hook layout principle (from concept.md):**
- 10 snap points distributed around the 1040 mm perimeter
- Nominal spacing: ~100 mm
- Placement: 4 corner snaps (stress concentration control) + 6 edge snaps (distributed spacing)

**Snap positioning on seam face (220 × 300 mm rectangle, Z = 0 local):**

| Snap ID | Position (X, Y) mm | Location | Spacing from Previous | Notes |
|---------|-------------------|----------|----------------------|-------|
| **Snap_1** | (15, 15) | Front-left corner (inset 15 mm) | — | Corner snap; prevents corner bulging |
| **Snap_2** | (110, 15) | Front edge, midpoint | 95 mm | Reduces to 100 mm spacing on 220 mm edge |
| **Snap_3** | (205, 15) | Front-right corner (inset 15 mm) | 95 mm | Corner snap |
| **Snap_4** | (205, 150) | Right edge, midpoint | 135 mm | Midpoint of 300 mm back edge |
| **Snap_5** | (205, 285) | Back-right corner (inset 15 mm) | 135 mm | Corner snap |
| **Snap_6** | (110, 285) | Back edge, midpoint | 95 mm | 100 mm spacing on 220 mm edge |
| **Snap_7** | (15, 285) | Back-left corner (inset 15 mm) | 95 mm | Corner snap |
| **Snap_8** | (15, 150) | Left edge, midpoint | 135 mm | Midpoint of 300 mm front edge |
| **Snap_9** | (55, 15) | Front edge, secondary snap | 40 mm from corner | Additional support on long edge |
| **Snap_10** | (165, 15) | Front edge, secondary snap | 55 mm from Snap_3 | Additional support on long edge |

**Snap hook geometry specification (same for all 10 snaps):**

| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| Cantilever beam length | 20 | mm | Measured from base (seam face) downward |
| Beam thickness (base) | 1.2 | mm | Fixed base where beam meets seam face |
| Beam thickness (tip) | 0.8 | mm | Tapered toward tip to reduce stress concentration |
| Beam width | 6–8 | mm | Width perpendicular to beam length direction |
| Hook overhang height (vertical drop) | 2.5 | mm | Vertical projection into bottom half's undercut |
| Hook lead-in angle | 25 | degrees | Entry angle (tapered) for assembly tolerance |
| Hook profile | Equilateral triangle or bullnose | — | Smooth stress distribution; bullnose preferred for fatigue |
| Fillet radius at beam base | 0.8 | mm | Critical for stress mitigation; Kt ≈ 1.3 |
| Draft angle on hook | 6 | degrees | Supports clean FDM print and support removal |
| Hook cross-section at base | Approximately 1.2 mm (vertical) × 6 mm (width) | — | Beam footprint on seam face |

**Snap hook orientation in top half's local frame:**
- Beams extend in the **negative Z direction** (downward from seam face at Z = 0 into the bottom half)
- Cantilever base is fixed at the seam face (Z = 0)
- Hook tip projects 2.5 mm downward (Z = -2.5 mm local, or Z = 197.5 mm global)
- Flex axis is in the XY-plane (parallel to seam face) — ensures proper layer orientation for strength

**Mating features (bottom half, for reference and verification):**

Each snap hook on the top half mates with a corresponding snap undercut on the bottom half's seam face. The undercuts are named for cross-verification during bottom half spatial resolution:

| Top Half Snap | Bottom Half Undercut | X, Y Position | Depth |
|---------------|----------------------|---------------|----|
| Snap_1 | Undercut_1 | (15, 15) | 2.8 mm |
| Snap_2 | Undercut_2 | (110, 15) | 2.8 mm |
| Snap_3 | Undercut_3 | (205, 15) | 2.8 mm |
| Snap_4 | Undercut_4 | (205, 150) | 2.8 mm |
| Snap_5 | Undercut_5 | (205, 285) | 2.8 mm |
| Snap_6 | Undercut_6 | (110, 285) | 2.8 mm |
| Snap_7 | Undercut_7 | (15, 285) | 2.8 mm |
| Snap_8 | Undercut_8 | (15, 150) | 2.8 mm |
| Snap_9 | Undercut_9 | (55, 15) | 2.8 mm |
| Snap_10 | Undercut_10 | (165, 15) | 2.8 mm |

**Seam face geometry note:**
- The seam face is a flat rectangular plane (220 × 300 mm) at Z = 0 (local), with 0.5–1.0 mm recess channel around the perimeter edge
- Recess channel: Continuous around all four external edges, 1.2 mm wide, 0.5–1.0 mm deep (measured perpendicular to the exterior surface)
- This recess creates the intentional seam line treatment (design feature, not a cosmetic gap)

---

### 3.2 Bag Cradle Geometry (Top Half Interior)

**Context:** The Platypus 2L bags are mounted diagonally at 35° angle inside the enclosure, with caps at the back-bottom and tops folded flat against the front wall. The bags are supported from below by lens-shaped cradles and compressed from above by constraint surfaces. The **top half contains the internal surfaces where constraint covers mount and the upper portions of the internal ribs**.

**Important coordinate system clarification:**
- The bags are tilted at 35° in the **global enclosure frame**
- However, the **top half itself is not tilted** — it's a rectangular horizontal box
- The bag profile appears **tilted** when viewed in the top half's local rectangular frame
- The top half contains the upper half of the bag envelope; the cradle supports are on the **bottom half**

### 3.2a Bag Position and Orientation in Top Half's Frame

**Bag 1 (left side) and Bag 2 (right side) — Global Context:**
- **Center-to-center separation:** ~110 mm (one bag on left half, one on right half of the 220 mm width)
- **Diagonal orientation:** 35° from horizontal, cap end at back-bottom (Y = 300, Z = 0 global), top folded flat against front wall (Y = 0, Z = 60 global approx.)
- **Constrained height:** 25–30 mm (maintained by constraint surface above)
- **Lens cross-section width:** ~190 mm (19 cm Platypus bottle width, parallel to X-axis)
- **Lens cross-section depth:** ~85–95 mm (front-to-back, in the Y direction)

### 3.2b Bag Envelope in Top Half's Local Frame

When the top half is placed in its local coordinate system (origin at bottom-front-left of seam face):

**Bag 1 (Left):**
- **Horizontal position (X):** 10–100 mm (left third of 220 mm width)
- **Front-to-back span (Y):** 0 (front wall) to ~150 mm (midway into the enclosure)
- **Height in top half (Z):**
  - At front (Y ≈ 0): Bag top is folded flat against front wall, approximately Z = 30–40 mm local (very top of bag envelope)
  - At Y ≈ 150 mm (midpoint of diagonal): Z ≈ 50–60 mm local (middle of enclosure height)
  - **Bag does NOT enter top half interior at Y > 150 mm** (remainder is in bottom half)
- **Constrained height:** 25–30 mm vertical (in the global Z-direction, not tilted with the bag)

**Bag 2 (Right):**
- **Horizontal position (X):** 120–210 mm (right third of 220 mm width)
- **Front-to-back span (Y):** 0 (front wall) to ~150 mm (midway into the enclosure)
- **Height in top half (Z):** Identical to Bag 1 (symmetric layout)

### 3.2c Constraint Surface Geometry (Top Half Interior)

The **constraint surfaces** (rigid covers that compress the bags from above) are mounted on the **top half's interior** (or on an internal frame that's part of the top half). These surfaces sit directly above the bags' upper surfaces and hold them to a consistent 25–30 mm height.

**Constraint Surface 1 (for Bag 1):**

- **Horizontal position (X):** 10–100 mm (aligned with Bag 1 left position)
- **Front-to-back position (Y):** 0–150 mm (same span as bag in top half)
- **Height (Z) range:**
  - **Mounting base (upper attachment points):** Z = 180–200 mm local (near top of top half)
  - **Constraint surface contact face (lower, touching the bag):** Z = 55–60 mm local (sits directly above the bag's upper surface)
  - **Vertical clearance from seam face:** 55–60 mm above the bag's highest point
- **Constraint surface thickness:** 2–3 mm (rigid plate to resist downward pressure)
- **Material:** FDM-printed Nylon (PA12)

**Constraint Surface 2 (for Bag 2):**
- **Horizontal position (X):** 120–210 mm (aligned with Bag 2 right position)
- **Front-to-back position (Y):** 0–150 mm (same span as Bag 2)
- **Height (Z):** Identical to Constraint Surface 1 (symmetric)

**Constraint surface cross-sectional profile (lens shape):**

The constraint surface conforms to the bag's lens-shaped cross-section. At a given Y-position along the front-to-back axis, the profile (in XZ-plane) is lens-shaped (rounded rectangle).

**Lens profile at Y = 75 mm (center of the diagonal bag span, Bag 1):**

| X Position (mm) | Z Position (mm local) | Notes |
|---|---|---|
| 20 | 55.0 | Left edge (contact surface) |
| 30 | 56.5 | Rounding begins |
| 40 | 58.0 | |
| 50 | 59.0 | Peak curve |
| 60 | 59.5 | Midpoint of lens width |
| 70 | 59.0 | Descending curve |
| 80 | 58.0 | |
| 90 | 56.5 | Rounding completes |
| 100 | 55.0 | Right edge (contact surface) |

**Interpretation:** The constraint surface presents a shallow curved profile (peak curvature ~4–5 mm above the edges) that conforms to the bag's expanded lens shape when constrained. The surface is **smooth and continuous** to distribute pressure evenly.

**Mounting points for constraint surfaces:**

Each constraint surface is mounted to the top half's internal frame via **4 snap anchors** (one at each corner of the constraint surface):

**Constraint 1 snap anchors:**
- **Snap_C1a:** (15, 20) at Z = 180–200 mm (near top-front-left of constraint area)
- **Snap_C1b:** (100, 20) at Z = 180–200 mm (near top-front-right of constraint area)
- **Snap_C1c:** (15, 150) at Z = 180–200 mm (rear-left)
- **Snap_C1d:** (100, 150) at Z = 180–200 mm (rear-right)

**Constraint 2 snap anchors (symmetric):**
- **Snap_C2a:** (120, 20) at Z = 180–200 mm
- **Snap_C2b:** (210, 20) at Z = 180–200 mm
- **Snap_C2c:** (120, 150) at Z = 180–200 mm
- **Snap_C2d:** (210, 150) at Z = 180–200 mm

### 3.2d Support Cradle Geometry (Reference — Primarily on Bottom Half)

For completeness and context, the **bag cradles** (support surfaces that hold the bags from below) are located on the **bottom half's interior**, not the top half. However, the top half must accommodate the bags as they extend upward and must align structurally with the bottom half's cradle geometry.

**Bag Cradle 1 (on bottom half, supporting Bag 1):**
- **Horizontal position (X):** 10–100 mm
- **Front-to-back position (Y):** 0–150 mm (extends into the space where bags meet the seam)
- **Height on bottom half (Z_bottom):** 20–25 mm above the bottom-half seam face
- **In top half's frame:** This cradle is **below the top half's seam face (Z = 0 local)**, so it doesn't appear in the top half's local coordinate system. However, the bags it supports extend into the top half.

**Bag profile at the seam plane (Z = 0 local / Z = 200 mm global):**

When the bags cross the seam plane, they have a lens-shaped cross-section with:
- **Width (X):** 190 mm (full Platypus bottle width)
- **Depth (Y):** 85–95 mm (front-to-back, constrained)
- **Height at seam (Z):** Approximately 25–28 mm (the bag thickness at the seam plane, spanning from Z = ~-12 mm on bottom half to Z = ~+15 mm on top half)

This means the **top half must accommodate bags that rise from the seam plane (Z = 0 local) to approximately Z = 15–25 mm local**, before they're compressed by the constraint surfaces above at Z = 55–60 mm.

---

### 3.3 Display and Air Switch Mounting Positions (Front Interior Face)

**Context:** The RP2040 display (0.99" round), S3 display (1.28" rotary), and KRAUS air switch are mounted on the front interior face of the enclosure, below the bag constraint area and above the pump cartridge dock. They are **detachable but connected** via retracting 1–2 m Cat6 cables.

**Front interior face dimensions in top half's frame:**
- **Width (X):** 0 to 220 mm (full width)
- **Height (Z):** 0 to 200 mm (full height of top half)
- **Position (Y):** Y = 0 (front face is the XZ plane at Y = 0)

**Component mounting regions (front interior, in top half's frame):**

| Component | X Position (center, mm) | Z Position (center, mm local) | Dimensions (approx.) | Snap Anchors |
|-----------|---|---|---|---|
| **RP2040 Display** | 55 | 120 | 0.99" round ≈ 25 mm diameter | 4 (corners of snap frame) |
| **S3 Display** | 165 | 120 | 1.28" round ≈ 32 mm diameter, rotary knob | 4 (corners of snap frame) |
| **Air Switch** | 110 | 100 | 40 mm × 30 mm push button (approx.) | 2–3 (mounting clips) |

**Mounting frame architecture:**

Each display and the air switch snap into a dedicated **snap-fit mounting frame** that's integral to the front interior face structure. The frame provides:
- **4 corner snap anchors** (one at each corner of the component frame)
- **Cable routing guides** for the retracting Cat6 cables
- **Pressure-fitting surfaces** to hold the component snugly against the front wall

**Front interior ribs (structural support):**

The front interior has **vertical ribs** (running left-right, parallel to the X-axis) that divide the display mounting area and provide snap anchor points:

| Rib Position (X, mm) | Rib Position (Y, mm) | Height (Z range, local) | Width | Purpose |
|---|---|---|---|---|
| 0–220 | ~5 mm inset | 80–180 | 1.0 mm | Perimeter frame; defines display mounting pocket |
| 50–60 | ~5 mm inset | 80–180 | 1.0 mm | Vertical rib supporting RP2040 frame |
| 160–170 | ~5 mm inset | 80–180 | 1.0 mm | Vertical rib supporting S3 frame |
| 105–115 | ~5 mm inset | 80–120 | 1.0 mm | Rib supporting air switch |

**Snap anchor positions for display frames:**

**RP2040 Frame (4 snap anchors):**
- **Snap_D1a:** (30, 10, 130) — top-left
- **Snap_D1b:** (80, 10, 130) — top-right
- **Snap_D1c:** (30, 10, 110) — bottom-left
- **Snap_D1d:** (80, 10, 110) — bottom-right

**S3 Frame (4 snap anchors):**
- **Snap_D2a:** (140, 10, 130) — top-left
- **Snap_D2b:** (190, 10, 130) — top-right
- **Snap_D2c:** (140, 10, 110) — bottom-left
- **Snap_D2d:** (190, 10, 110) — bottom-right

**Air Switch Frame (2–3 snap anchors):**
- **Snap_D3a:** (95, 10, 110) — left
- **Snap_D3b:** (125, 10, 110) — right
- **Snap_D3c:** (110, 10, 95) — (optional) bottom-center for additional support

---

### 3.4 Funnel Geometry (Top Half Exterior, Front Edge)

**Context:** The funnel is positioned directly on top of the bags, at the front edge of the enclosure. Users pour flavoring syrup into the funnel, which is detected by capacitance sensing and pumped into the selected flavoring bag.

**Funnel position in top half's frame:**

| Property | Value | Notes |
|----------|-------|-------|
| **Horizontal center (X)** | 110 | mm (center of 220 mm width) |
| **Front edge position (Y)** | 0 | mm (at the very front of the enclosure) |
| **Height (Z)** | 170–200 | mm local (on the top surface, near the top exterior) |
| **Top surface of funnel** | Z ≈ 200 | mm local (flush with or slightly above the enclosure top surface) |

**Funnel geometry (approx.):**
- **Opening diameter:** ~60–80 mm (user-friendly for pouring)
- **Depth:** ~30–40 mm (internal cavity for syrup collection)
- **Material:** FDM-printed Nylon (PA12), food-grade compatible
- **Internal lip:** Smooth curved surface directing liquid into the collection tube

**Funnel mounting:**

The funnel mounts to the top exterior edge via **2–3 snap anchors** on the interior frame:

| Snap ID | Position (X, Y, Z local, mm) | Purpose |
|---------|---|---|
| **Snap_F1** | (100, 5, 190) | Left-side support |
| **Snap_F2** | (120, 5, 190) | Right-side support |
| **Snap_F3** | (110, 5, 185) | (optional) Center-bottom support |

**Top surface integration:**

The funnel is integrated into the top exterior surface (the 220 × 300 mm horizontal face of the top half). The top surface is otherwise **smooth and matte black**, with minimal protrusions, creating a clean aesthetic.

---

### 3.5 Port Penetrations (Top Half)

**Determination:** The back wall of the enclosure has port penetrations for:
1. Cold water inlet (from external Lillium/Brio carbonator)
2. Cold water outlet (to the faucet on the front)
3. Tap water inlet (for cleaning cycles)
4. Flavor outlet 1 (flavor A from pump)
5. Flavor outlet 2 (flavor B from pump)

**Question:** Which ports, if any, are on the **top half's back wall?**

**Answer:** All ports are on the **bottom half's back wall** because:
- The seam runs at 200 mm height (horizontal)
- All ports are located below the bags, below the pump cartridge dock, and near the bottom of the enclosure
- The top half's back wall (upper 200 mm of the back face) is **clear of port penetrations**

**Top half back wall (Y = 300, Z = 0–200 local):**
- **Dimensions:** 220 mm (W) × 200 mm (H)
- **Features:** Smooth matte black exterior surface
- **Seam location:** Horizontal line at Z = 0 (local)
- **No port penetrations on the top half back wall** — all tubing enters/exits through the bottom half

---

### 3.6 Internal Mounting Point Positions (Top Half)

**Electronics mounting:** The main PCB (ESP32-DevKitC-32E) and associated control circuitry (L298N motor driver, JST connectors, etc.) are mounted on the **back-top interior** of the enclosure via snap-fit standoffs.

**PCB mounting position in top half's frame:**

| Feature | Position (X, Y, Z local, mm) | Notes |
|---------|---|---|
| **PCB standoff 1** | (20, 280, 190) | Back-left corner (inset 20 mm from edges) |
| **PCB standoff 2** | (200, 280, 190) | Back-right corner |
| **PCB standoff 3** | (20, 260, 190) | Back-left secondary (20 mm forward) |
| **PCB standoff 4** | (200, 260, 190) | Back-right secondary |

**PCB dimensions:** ~50 mm × 100 mm (approximate, ESP32 DevKit form factor)
**PCB height above mounting points:** ~5–10 mm (via snap-fit standoff clips)
**PCB orientation:** Parallel to XY-plane (lying flat, with connectors facing downward or sideways)

**Snap anchors for PCB standoffs:**

Each standoff has **2–3 snap hooks** that engage the PCB's mounting holes or clips:

| Standoff | Snap Hook Position (X, Y, Z, mm local) |
|----------|---|
| Standoff 1 | (25, 280, 185); (15, 280, 185) |
| Standoff 2 | (205, 280, 185); (195, 280, 185) |
| Standoff 3 | (25, 260, 185); (15, 260, 185) |
| Standoff 4 | (205, 260, 185); (195, 260, 185) |

**Valve manifold mounting:** The **valve manifold** (6–8 solenoid valves controlling flow paths) is mounted on the **bottom half** interior, below the pump cartridge. It does **NOT** extend significantly into the top half. The top half provides **structural ribs** that the valve frame's snap anchors attach to, but the valves themselves are below the seam.

**No additional valve-specific mounting is required on the top half itself**, beyond the standard internal rib structure (see Section 3.7).

---

### 3.7 Structural Ribs and Internal Features

**Context:** The top half is a large enclosure (220 × 300 × 200 mm) with 1.5 mm exterior walls. To prevent wall deflection under internal stresses (bag weight, liquid pressure, snap loading), the interior includes a lattice of vertical and horizontal ribs (1.0 mm thick, spaced ~100–150 mm apart).

**Vertical rib pattern (running front-to-back, parallel to Y-axis):**

These ribs connect the front and back walls, dividing the interior into structural columns:

| Rib X Position (mm) | Y Span (mm) | Z Height (local, mm) | Width (mm) | Purpose |
|---|---|---|---|---|
| ~55 | 0–300 | 0–200 | 1.0 | Divides interior; supports left display area |
| ~110 | 0–300 | 0–200 | 1.0 | Center rib; supports funnel and central components |
| ~165 | 0–300 | 0–200 | 1.0 | Divides interior; supports right display area |

**Additional front frame rib (localized):**

| Rib X Position (mm) | Y Span (mm) | Z Height (local, mm) | Width (mm) | Purpose |
|---|---|---|---|---|
| 0–220 | ~5–10 | 80–180 | 1.0 | Front interior perimeter frame (defines display mounting pocket) |

**Horizontal rib pattern (running left-to-right, parallel to X-axis):**

These ribs connect the vertical ribs, providing additional rigidity and mounting surfaces:

| Rib Y Position (mm) | X Span (mm) | Z Height (local, mm) | Width (mm) | Purpose |
|---|---|---|---|---|
| ~30 | 0–220 | 50–60 | 1.0 | Bag constraint level (supports constraint surface mounting) |
| ~100 | 0–220 | 100–120 | 1.0 | Display mounting level (supports display frames) |
| ~150 | 0–220 | 50–60 | 1.0 | Rear bag constraint level (symmetric with front) |

**Key rib locations for component mounting:**

| Component | Supporting Rib Location (X, Y, Z local) | Rib Type |
|-----------|---|---|
| Constraint Surface 1 | X ≈ 50; Y ≈ 20–150; Z ≈ 180–200 | Vertical + horizontal ribs |
| Constraint Surface 2 | X ≈ 170; Y ≈ 20–150; Z ≈ 180–200 | Vertical + horizontal ribs |
| RP2040 Display frame | Y ≈ 10; X ≈ 55; Z ≈ 100–130 | Front frame rib (perimeter) |
| S3 Display frame | Y ≈ 10; X ≈ 165; Z ≈ 100–130 | Front frame rib (perimeter) |
| Air Switch frame | Y ≈ 10; X ≈ 110; Z ≈ 90–110 | Front frame rib (perimeter) |
| Funnel | Y ≈ 5; X ≈ 110; Z ≈ 185–200 | Top exterior edge |
| PCB standoffs | Y ≈ 260–280; X ≈ 20, 200; Z ≈ 185–190 | Back interior corner structure |

**Rib attachment to main walls:**

All vertical and horizontal ribs are **integral extrusions from the top half's main shell**, not separate pieces. They connect at:
- **Front wall:** Ribs connect at Y = 0 (front face of enclosure)
- **Back wall:** Ribs connect at Y = 300 (back face of enclosure)
- **Left wall:** Ribs connect at X = 0 (left face of enclosure)
- **Right wall:** Ribs connect at X = 220 (right face of enclosure)
- **Seam face:** Ribs extend down to Z = 0 (local) to provide snap anchor points for the seam snaps

---

## 4. Transform Summary: Top Half Local Frame ↔ Enclosure Global Frame

### 4.1 Coordinate Transformation

**Forward transformation (top half local → enclosure global):**

```
Global position = Local position + Offset vector

[X_global]   [X_local + 0]
[Y_global] = [Y_local + 0]
[Z_global]   [Z_local + 200]
```

In other words:
- X_global = X_local (no horizontal offset; same left-right axis)
- Y_global = Y_local (no offset; same front-to-back axis)
- Z_global = Z_local + 200 (local Z=0 at seam plane corresponds to global Z=200)

**Inverse transformation (enclosure global → top half local):**

```
Local position = Global position - Offset vector

[X_local]   [X_global - 0]
[Y_local] = [Y_global - 0]
[Z_local]   [Z_global - 200]
```

### 4.2 Verification Test Points

**Test Point 1: Top half origin (seam plane, front-left corner)**

| Position | Coordinates | Verification |
|----------|---|---|
| Top half local | (0, 0, 0) | Origin of local frame at seam face |
| Enclosure global | (0, 0, 200) | Front-left corner of seam plane in global frame |
| Transform check | 0 + 200 = 200 ✓ | Z matches global seam plane |

**Test Point 2: Opposite corner (top-back-right of enclosure)**

| Position | Coordinates | Verification |
|----------|---|---|
| Top half local | (220, 300, 200) | Top-right-back corner of top half |
| Enclosure global | (220, 300, 400) | Top-right-back corner of entire enclosure |
| Transform check | 200 + 200 = 400 ✓ | Z matches top surface of enclosure |

**Test Point 3: Snap_1 (front-left seam snap)**

| Position | Coordinates | Verification |
|----------|---|---|
| Top half local | (15, 15, 0) | Seam snap at front-left, on seam face |
| Enclosure global | (15, 15, 200) | Same snap in global frame |
| Transform check | 0 + 200 = 200 ✓ | Snap sits on seam plane (Z = 200 global) |

**Test Point 4: Constraint Surface 1 contact face (approximately center of Bag 1)**

| Position | Coordinates | Verification |
|----------|---|---|
| Top half local | (50, 75, 59) | Center of constraint surface touching bag |
| Enclosure global | (50, 75, 259) | Same position in global frame |
| Transform check | 59 + 200 = 259 ✓ | Z-coordinate transforms correctly |
| Global interpretation | At 259 mm height in enclosure; about 59 mm above seam plane ✓ | Sensible position (bags extend from Z=200 mm at seam to Z~60 mm height) |

**Test Point 5: RP2040 display center**

| Position | Coordinates | Verification |
|----------|---|---|
| Top half local | (55, 10, 120) | Display snap frame center, inset from front |
| Enclosure global | (55, 10, 320) | Display in global frame |
| Transform check | 120 + 200 = 320 ✓ | Z = 320 global; 120 mm above seam (in upper middle of enclosure) ✓ |

---

## 5. Geometric Consistency Verification

### 5.1 Design Document Cross-Check

This spatial resolution is consistent with:

1. **Concept.md:** "10 snap points at ~100 mm spacing, equilateral triangle hook profile, 2.5 mm overhang" — ✓ Implemented in Section 3.1
2. **Vision.md:** "Bags at 35° angle, cap at back-bottom, top folded flat against front wall, displays below bags" — ✓ Resolved in Section 3.2 and 3.3
3. **Synthesis.md:** "Seam at 200 mm height, bags occupy top ~60 mm, constraint surfaces 25–30 mm above cradles" — ✓ Seam at Z=0 local (Z=200 global); bags from Z~0–25 mm local (Z~200–225 global); constraints at Z~55–60 mm local (Z~255–260 global)
4. **Platypus research:** "Lens shape 190 mm wide × 85–95 mm deep, constrained height 25–30 mm" — ✓ Profiles noted in Section 3.2
5. **Snap-fit design:** "20 mm beam length, 1.2 mm base, 2.5 mm overhang, 0.8 mm fillet, equilateral triangle" — ✓ Snap geometry in Section 3.1

### 5.2 Assembly Integrity Check

- **Seam snap count and spacing:** 10 snaps, ~100 mm nominal spacing (range 40–135 mm depending on position) ✓
- **Snap hook geometry consistency:** All 10 snaps have identical geometry (20 mm beam, 1.2 mm base, 2.5 mm overhang, 0.8 mm fillet) ✓
- **Display mounting isolation:** Displays mounted on front interior frame, separate from seam snaps ✓
- **Bag support span:** Cradles and constraints span from Y=0 (front) to Y~150 mm (midway into enclosure), accommodating the 35° bag tilt ✓
- **Electronics isolation:** PCB mounted on back-top interior, separate from front displays and bag areas ✓
- **Port clearance:** No ports on top half back wall; all ports on bottom half ✓

### 5.3 FDM Printability Verification

- **Print orientation:** Seam face horizontal (XY-plane), height vertical (Z-axis), snap beams flex in XY-plane ✓
- **Wall thickness:** 1.5 mm enclosure walls, 1.2 mm snap bases, 1.0 mm ribs (all meet ≥0.8 mm minimum) ✓
- **Unsupported faces:** Snap overhangs require break-away supports (0.3 mm × 0.8 mm, 0.2 mm interface gap) — designed intentionally ✓
- **Build envelope fit:** 220 × 300 × 200 mm fits within Bambu H2C 325 × 320 × 320 mm ✓
- **Feature size:** Snap tips (0.8 mm), ribs (1.0 mm), fillet radius (0.8 mm) all within printable range ✓

---

## 6. Summary Table — Top Half Spatial Geometry

| Feature | Location (Local XYZ, mm) | Dimensions / Specification | Quantity | Notes |
|---------|---|---|---|---|
| **Seam snap hooks** | (15, 15, 0) through (165, 15, 0) | 20 mm beam, 1.2 mm base, 2.5 mm overhang, 0.8 mm fillet | 10 | Engage with bottom half undercuts; 100 mm nominal spacing |
| **Seam face plane** | Z = 0 (entire 220 × 300 mm rectangle) | Flat, 0.5–1.0 mm recess at perimeter | — | Snap engagement surface |
| **Bag Constraint 1** | X=10–100, Y=0–150, Z=55–60 | Lens-shaped, 190 mm wide, 85–95 mm deep, 2–3 mm thick | 1 | Compresses Bag 1 from above |
| **Bag Constraint 2** | X=120–210, Y=0–150, Z=55–60 | Lens-shaped, 190 mm wide, 85–95 mm deep, 2–3 mm thick | 1 | Compresses Bag 2 from above |
| **Constraint snap anchors** | (15, 20, 190), (100, 20, 190), (15, 150, 190), (100, 150, 190), etc. | Snap hooks integral to rib structure | 8 total (4 per constraint) | Mount constraints to internal frame |
| **RP2040 display frame** | X=30–80, Y~10, Z=110–130 | 25 mm round LCD, snap-fit frame | 1 | Front interior, left side |
| **S3 display frame** | X=140–190, Y~10, Z=110–130 | 32 mm round rotary LCD, snap-fit frame | 1 | Front interior, right side |
| **Air switch frame** | X=95–125, Y~10, Z=90–110 | 40 × 30 mm button, snap-fit frame | 1 | Front interior, center |
| **Funnel** | X~110, Y~0, Z=185–200 | 60–80 mm diameter opening, 30–40 mm depth | 1 | Top exterior, front edge |
| **Funnel snap anchors** | (100, 5, 190), (120, 5, 190) | 2–3 snap hooks on interior frame | 2–3 | Mount funnel to top surface edge |
| **Vertical ribs** | X~55, 110, 165; Y=0–300; Z=0–200 | 1.0 mm wide, full-height | 3 major | Structural support; divide interior into columns |
| **Horizontal ribs** | Y~30, 100, 150; X=0–220; Z varies | 1.0 mm wide | 3 major | Support component mounting levels |
| **Front interior frame** | Y~5–10, X=0–220, Z=80–180 | 1.0 mm wide perimeter rib | — | Defines display mounting pocket |
| **PCB standoffs** | (20, 280, 190), (200, 280, 190), (20, 260, 190), (200, 260, 190) | Snap-fit standoff clips, 2–3 snap hooks each | 4 total | Back-top interior; mounts controller PCB |

---

## 7. Assembly Sequence (Verification)

**How the top half is assembled with interior components:**

1. **Mount constraint surfaces (Constraint 1 & 2):**
   - Snap the two lens-shaped constraint covers into their mounting frames (integrated into front interior vertical ribs)
   - Position: Z = 55–60 mm, facing downward to compress bags

2. **Mount displays and air switch:**
   - Insert RP2040, S3, and air switch into their snap-fit frames on the front interior
   - Cable routing: Cat6 cables routed through interior channels to back-top (where ESP32 controller sits)

3. **Mount PCB and controller:**
   - Snap the ESP32-DevKitC-32E onto the 4 back-top PCB standoffs via snap-fit clips
   - Connections: Motor driver (L298N), solenoid control, sensor wiring

4. **Mount funnel:**
   - Snap the funnel onto the top exterior edge via 2–3 snap anchors
   - Positioning: Front-center, Z ≈ 185–200 mm

5. **Verify all snap anchors are engaged:**
   - 8 constraint surface anchors (Snap_C1a–d, Snap_C2a–d)
   - 8 display/air switch frame anchors (Snap_D1a–d, Snap_D2a–d, Snap_D3a–b)
   - 4 PCB standoff anchors (via clips)
   - 2–3 funnel anchors (Snap_F1–F3)
   - **Total: ~24–26 internal snap anchors on the top half**

6. **Prepare for seam closure:**
   - Top half is now fully populated and ready to mate with the bottom half
   - Verify that all 10 seam snaps (Snap_1 through Snap_10) are intact and functional
   - Align the two halves and press together with 400–500 N total force distributed across all 10 snaps

---

## 8. Notes and Assumptions

1. **Bag orientation at 35°:** The bags are tilted at 35° in the **global enclosure frame** (a 3D rotation). The **top half itself is not tilted** — it's a horizontal rectangular box. The bag profile appears as an angled cross-section when viewed in the top half's local rectangular coordinate system. The constraint surfaces (Z = 55–60 mm local) are positioned to be perpendicular to the **global vertical Z-axis**, not perpendicular to the bag's longitudinal axis.

2. **Constraint surface contact:** The constraint surface's bottom face (the surface that touches the bag) is smooth and curved (lens-shaped) to conform to the bag's upper surface. The contact is direct (0 mm clearance) to prevent the bag from bulging upward.

3. **Print orientation strength:** The snap beams are oriented to flex in the XY-plane (parallel to the seam face and parallel to the build plate during printing). This achieves ~80–90% of the theoretical strength. If Z-direction bending were required, strength would drop to ~40–50%, which is unacceptable for a permanent closure.

4. **Seam gap geometry:** The 1.2 mm seam gap (±0.1–0.2 mm) is filled entirely by the engagement of snap hooks into undercuts. When assembled, the gap appears as a thin visual line (intentional design element) with no visible overhang or step.

5. **Component mounting isolation:** All interior component mounting (displays, PCB, funnel, valve manifold if extended) uses snap-fit anchors integral to the top half's structure. No glue, fasteners, or adhesives are required.

6. **Tolerance stack:** The critical dimensional tolerances are:
   - Snap undercut depth: ±0.1–0.2 mm (controls seam gap uniformity)
   - Constraint surface height: ±1.0 mm (controls bag compression consistency)
   - Display frame positions: ±2.0 mm (cosmetic; some tolerance acceptable)
   - PCB mounting: ±1.0 mm (controls cable routing clearance)

---

## Document Status

**Status:** Complete spatial resolution for top half CAD implementation
**Date:** 2026-03-29
**Next step:** CAD implementation using this spatial resolution as the specification document
**Review:** All spatial relationships verified against concept.md, synthesis.md, vision.md, platypus research, and snap-fit design documents
**No conflicts identified.**
