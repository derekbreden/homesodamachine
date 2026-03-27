# Release Plate — Detailed Design Research

The release plate is the part that makes simultaneous contact with all 4 John Guest collets to release the cartridge tubing. It translates axially under cam or lever actuation, pushing each collet inward to disengage the gripper teeth. This document explores the geometry, spacing, compliance, guide features, material choices, and print strategy in enough detail to produce a first print.

This builds on established values from prior research:

| Parameter | Value | Source |
|---|---|---|
| Tube OD | 6.35mm (1/4") | collet-release.md (verified) |
| Fitting profile | Barbell: 9.31mm center body, 15.10mm body ends | Caliper-verified (geometry-description.md) |
| Center body length | 12.16mm | Caliper-verified |
| Body end OD | 15.10mm | Caliper-verified — the fixed housing section |
| Body end length | 12.08mm each | Caliper-verified |
| Collet (release sleeve) OD | 9.57mm | Caliper-verified — the moving part |
| Collet wall thickness | 1.44mm | Caliper-verified |
| Collet ID | 6.69mm | Derived: 9.57 - 2×1.44 |
| Tube OD (measured) | 6.30mm | Caliper-verified (nominal 6.35mm) |
| Tube clearance bore | 6.5mm | collet-release.md (must be between 6.30mm tube and 6.69mm collet ID) |
| Inner lip bore (collet hugger) | 10.0mm | Design (just over 9.57mm collet OD, provides lateral constraint) |
| Outer bore (body end cradle) | 15.6mm | Design (clears 15.10mm body end with 0.25mm/side) |
| Collet travel (inward, per side) | ~1.3mm | Caliper-verified (2.67mm total both ends) |
| Collet protrusion (per side, compressed) | ~1.4mm | Caliper-verified |
| Plate travel (stroke) | 3.0mm (min 2.5mm) | collet-release.md |
| Force per fitting | ~3-5N | collet-release.md |
| Total force (4 fittings) | ~12-20N | collet-release.md |
| FDM sliding clearance | 0.3-0.5mm per side | guide-alignment.md |
| Cam eccentricity | 1-1.5mm (3mm stroke) | cam-lever.md |

---

## 1. Stepped Bore Geometry in Detail

Each hole in the release plate replicates the geometry of a John Guest release tool. The bore has three concentric diameters, each with a specific function.

### 1.1 Cross-Section Profile

```
    ← fitting side (collet faces this way)     plate body →

    ┌───────────────────────────────────────────────────────┐
    │                                                       │
    │   ┌─ outer bore (cradle) ─────────────────────────┐   │
    │   │                                               │   │
    │   │   ┌─ inner lip ───────────────────────────┐   │   │
    │   │   │                                       │   │   │
    │   │   │   ┌─ tube clearance hole ─────────┐   │   │   │
    │   │   │   │                               │   │   │   │
    │   │   │   │       6.5mm dia               │   │   │   │
    │   │   │   │                               │   │   │   │
    │   │   │   └───────────────────────────────┘   │   │   │
    │   │   │         10.0mm dia                    │   │   │
    │   │   └───────────────────────────────────────┘   │   │
    │   │              15.6mm dia                       │   │
    │   └───────────────────────────────────────────────┘   │
    │                                                       │
    └───────────────────────────────────────────────────────┘
```

### 1.2 Axial Profile (Side View of One Bore)

```
    ← fitting side                    back side →

    plate travel direction: ←───────

         outer     inner lip    tube hole
         bore      (hugger)     (through)
        ┌─────┐   ┌────────┐   ┌──────────────────────────┐
        │     │   │        │   │                          │
        │     │   │        │   │    6.5mm through hole    │
        │     │   │        │   │                          │
    ────┘     └───┘        └───┘                          └────
    plate     2.0mm  2.0mm        remaining plate
    face      deep   deep         thickness
```

### 1.3 Feature-by-Feature Breakdown

**Tube clearance hole: between 6.30mm and 6.69mm, through the full plate thickness**

This is the center bore that the tube passes through. Unlike the previous 8.0mm design, this bore is intentionally tight — its purpose is not just tube clearance, but also to enable the plate face around the bore to contact the collet's annular end face and push it inward.

- **Lower bound (6.30mm):** The tube OD, caliper-verified. The bore must be larger than this for the tube to pass through.
- **Upper bound (6.69mm):** The collet ID (derived: 9.57mm OD - 2×1.44mm wall = 6.69mm). The bore must be smaller than this so the plate face extends past the collet opening and contacts the collet's annular face.
- **Design window: only 0.39mm.** This is at the edge of FDM accuracy. FDM holes typically print undersized by 0.1–0.3mm, so the as-designed value should be slightly above center of the window to compensate. May require post-processing (drilling/reaming) after printing.
- The through-hole extends the full thickness of the plate.
- Printing with the bore axis vertical (Z-axis) gives the best circularity. A 0.1mm chamfer at the entry helps thread the tube through during assembly.

**Inner lip (collet hugger): just over 9.57mm bore, 2.0mm depth**

The inner lip bore closely surrounds the collet (9.57mm OD, caliper-verified) for lateral constraint during release. The plate face between the through-hole and this bore is the surface that contacts the collet's annular end face and pushes it inward.

- **Bore diameter:** Must clear the 9.57mm collet OD, but should be as tight as manufacturing allows. Tighter = better lateral constraint, less wobble during the push. The same precision philosophy applies here as to the through-hole — unnecessary clearance reduces grip without adding benefit.
- **Contact annulus:** The plate face contacts the collet's full annular face, from collet ID (6.69mm) to collet OD (9.57mm). This annulus is exactly 1.44mm wide (the collet wall thickness), providing even force distribution across the entire collet face.
- **Lip annular width:** Determined by (inner lip bore - through-hole bore) / 2. This is the radial width of the lip wall that does the pushing. Must be structurally robust for the 3-5N per fitting force.
- **Depth (2.0mm):** The lip must remain engaged with the collet through the full collet travel (~1.3mm per side, caliper-verified). A 2.0mm lip depth provides ~0.7mm minimum engagement margin.

- **Lip face profile:** The face of the lip (the surface that contacts the collet) should be flat, not chamfered. A chamfer would reduce the contact area and could allow the collet to cam sideways. A very slight break (0.1-0.2mm 45-degree chamfer) on the inner edge is acceptable to prevent catching during insertion, but the contact annulus must remain a flat, perpendicular face.

**Outer bore (body end cradle): just over 15.10mm bore, 2.0mm depth**

The outer bore surrounds the body end (15.10mm OD, caliper-verified) and prevents lateral movement during release. This is the feature that prevents the cocking/tilting failure mode described in collet-release.md Section 4.

- **Bore diameter:** Must clear the 15.10mm body end OD, but should be as tight as manufacturing allows. Tighter = better lateral constraint. FDM undersizing actually helps here — a bore designed at 15.2mm that prints at 15.0mm gives a near-perfect sliding fit.
- **Depth (2.0mm):** The collet protrudes ~2.7mm from the body face when extended (at rest). The outer bore cradle surrounds the body end below the collet protrusion. During release, as the plate pushes the collet inward, the body end engagement depth increases.

  **Key insight from the John Guest PI-TOOL:** The commercial tool's cradle wraps around the collet sides, not just its face. Our design applies this principle at two scales: the inner lip hugs the collet (9.57mm), and the outer bore hugs the body end (15.10mm). Both should be as tight as manufacturing allows — the tightest constraint (0.39mm on the through-hole) already limits overall play, so looseness in the other bores only adds wobble without gaining any additional lateral freedom.

- **Wall angle**: The cradle bore should be straight (cylindrical), not tapered. A tapered cradle would allow the collet to shift laterally as it moves axially. The cylindrical bore maintains constant lateral constraint through the full stroke. A small lead-in chamfer (0.3mm x 45 degrees) at the entry helps the plate slide over the collet without catching on any slight collet protrusion asymmetry.

### 1.4 Transition Between Bores

The transition from outer bore to inner lip is a flat annular step (a shoulder). The shoulder face is perpendicular to the bore axis. This shoulder doesn't contact anything during normal operation -- it exists between the lip face (which pushes the collet) and the cradle wall (which constrains the collet sides). The sharp internal corner where the shoulder meets the cradle wall will naturally have a small radius from FDM printing (~0.2mm for a 0.4mm nozzle), which is fine.

The transition from inner lip to tube hole is also a flat step. This internal shoulder serves no functional purpose during release -- it's simply the geometry left by the two different bore diameters. Again, FDM corner radius is acceptable.

### 1.5 Complete Axial Dimension Stack

From the fitting-facing surface of the plate inward:

| Zone | Depth | Running Total | Feature |
|---|---|---|---|
| Outer bore (cradle) | 2.0mm | 2.0mm | Just over 15.10mm dia, constrains body end sides |
| Inner lip (hugger) | 2.0mm | 4.0mm | Just over 9.57mm dia, hugs collet and pushes collet face |
| Structural back | 2.0mm | 6.0mm | Through-hole only (between 6.30 and 6.69mm) |
| **Total plate thickness** | | **6.0mm** | |

The 2.0mm structural back provides material behind the inner lip for rigidity. Without this, the lip would be a thin cantilevered ring that could flex under load. The through-hole continues through this zone.

**Alternative: 5.0mm total** by reducing the structural back to 1.0mm. This is the minimum before the lip becomes too flexible in PETG. 6.0mm is the conservative starting point; 5.0mm is acceptable if plate thickness is constrained by the overall assembly.

---

## 2. Hole Spacing and Arrangement

### 2.1 Minimum Center-to-Center Spacing

The outer bore is 15.6mm diameter (sized to clear the 15.10mm body end OD, caliper-verified). Two adjacent outer bores need a wall of material between them for structural integrity.

**Minimum wall thickness between bores in PETG (FDM)**:
- Absolute minimum: 1.0mm (approximately 2.5 perimeter widths at 0.4mm nozzle). The wall would be structurally sound in compression (the plate pushes collets inward) but fragile if any lateral or bending load is applied.
- Recommended minimum: 1.5mm (approximately 4 perimeter widths). Provides meaningful cross-section for both compression and bending loads.
- Comfortable: 2.0mm. Allows full infill between bores and provides enough material to resist plate flex between holes.

**Center-to-center spacing = outer bore diameter + wall thickness**:

| Wall Thickness | Center-to-Center | Notes |
|---|---|---|
| 1.0mm | 16.6mm | Absolute minimum, fragile |
| 1.5mm | 17.1mm | Recommended minimum |
| 2.0mm | 17.6mm | Comfortable, resistant to flex |
| 3.0mm | 18.6mm | Very robust, may be larger than needed |

**Note:** The parts.md already specifies 40mm horizontal x 28mm vertical center-to-center spacing for the fitting grid, which provides 40 - 15.6 = 24.4mm wall between horizontal bores and 28 - 15.6 = 12.4mm wall between vertical bores -- both very comfortable. At these spacings, wall thickness between bores is not a constraint.

### 2.2 Arrangement Options

The 4 fittings correspond to 2 pumps x 2 connections each (inlet + outlet). The physical arrangement of these 4 holes on the plate determines the plate footprint and aspect ratio.

**Update:** The fitting spacing has been finalized in parts.md as **40mm horizontal x 28mm vertical center-to-center** in a 2x2 grid. This spacing was chosen to accommodate the caliper-verified barbell profile (15.10mm body ends) with comfortable margins. The original analysis below explored tighter spacings based on the assumed 12.7mm uniform body OD — those options are no longer feasible because the body end OD is 15.10mm, which requires a minimum ~17.1mm C-C (with 1.5mm wall between 15.6mm outer bores). The 40x28mm spacing provides far more than enough room. The analysis below is retained for reference but the dimensions are superseded.

#### Option A: 4-in-a-Line (1x4)

Not selected. At 40mm horizontal spacing, a 4-in-a-line arrangement would produce a plate span of 120mm — impractically wide.

#### Option B: 2x2 Grid (SELECTED — per parts.md)

```
    ┌───────────────────────────────────────────────────────────┐
    │   (1)                                   (2)               │
    │    O                                     O                │
    │                                                           │
    │                                                           │
    │   (3)                                   (4)               │
    │    O                                     O                │
    └───────────────────────────────────────────────────────────┘
         ←──────────── 40 ────────────→
                        ↕
                       28mm
```

| Dimension | Value |
|---|---|
| Span (horizontal) | 40.0mm |
| Span (vertical) | 28.0mm |
| Plate width | 40.0 + 15.6 + 2x1.7 = 59.0mm (per parts.md: 59mm) |
| Plate height | 28.0 + 15.6 + 2x1.7 = 47.0mm (per parts.md: 47mm) |
| Aspect ratio | ~1.26:1 |

**Pros**: Generous spacing between bores. The wall between adjacent outer bores is 28 - 15.6 = 12.4mm (vertical) and 40 - 15.6 = 24.4mm (horizontal) — extremely robust. The maximum moment arm to any bore from plate center is sqrt(20^2 + 14^2) = 24.4mm. The fitting body ends (15.10mm OD) have 28 - 15.10 = 12.9mm clearance vertically and 40 - 15.10 = 24.9mm clearance horizontally — no interference possible.

**Cons**: Larger plate footprint (59x47mm) than the tighter spacings originally analyzed. But the cartridge interior (140x122mm) easily accommodates this, and the wider spacing improves parallelism margin.

**Tilt sensitivity**: A 0.3mm parallelism deviation across 59mm plate width = 0.29 degrees. Across the 47mm height = 0.37 degrees. Both are within acceptable limits with proper guide pin placement.

#### Option C: Diamond (Rotated 2x2)

Not selected. No practical advantage over the rectangular 2x2 grid, and complicates both dock mounting and tube routing.

#### Option D: Offset Pairs (2+2)

Not selected. Asymmetric layout with no advantage at the 40x28mm spacing.

### 2.3 Arrangement Summary

**2x2 grid at 40mm H x 28mm V center-to-center** (per parts.md). This was chosen to match the cartridge rear wall fitting pocket layout. The spacing provides generous material between bores and comfortable clearance around the 15.10mm body ends.

| Property | Value |
|---|---|
| Plate width | 59mm |
| Plate height | 47mm |
| Max moment arm (center to corner bore) | 24.4mm |
| Wall between bores (vertical, minimum) | 12.4mm |
| Wall between bores (horizontal) | 24.4mm |
| Edge-to-bore clearance (minimum) | 1.7mm |

Pairing: In the 2x2 grid, the natural grouping is pump 1 inlet/outlet as one column, pump 2 inlet/outlet as the other column:

```
    Pump 1 IN    Pump 2 IN
        O            O

    Pump 1 OUT   Pump 2 OUT
        O            O
```

This keeps each pump's inlet and outlet in a vertical pair, which simplifies internal tube routing inside the cartridge.

---

## 3. Plate Thickness

### 3.1 Thickness Budget

The plate thickness is driven by the axial depth stack of the stepped bore features plus structural material behind them.

From Section 1.5:

| Zone | Depth |
|---|---|
| Outer bore (cradle) | 2.0mm |
| Inner lip (pusher) | 2.0mm |
| Structural back | 2.0mm |
| **Total** | **6.0mm** |

### 3.2 Can It Be Thinner?

**5.0mm minimum** (reducing structural back to 1.0mm):
- The inner lip radial width depends on final bore sizes but is narrower than the previous design (~1.75mm vs 2.25mm with the tighter bores). With only 1.0mm of material behind it, the lip would have adequate compression strength but reduced rigidity against FDM defects (underextrusion, layer adhesion issues).
- Acceptable for a test coupon. Not recommended for the production plate.

**6.0mm recommended** for prototyping. Provides 2.0mm structural back, which gives confident rigidity and allows the back face to serve as a bearing surface for guide features.

**7.0mm or more** would add no functional benefit and increases the overall assembly depth unnecessarily. The plate travel is only 3.0mm, so the plate moves within a small axial envelope.

### 3.3 Assembly Depth Implications

The plate sits between the cam/lever mechanism and the fitting face. The total axial depth consumed by the release mechanism is:

```
    cam mechanism depth + plate thickness + plate travel + collet protrusion

    = (TBD, ~10-15mm for cam) + 6.0mm + 3.0mm + 2.5mm
    = ~21.5-26.5mm total
```

This is the depth behind the dock mating face dedicated to the release mechanism. For a cartridge dock that might be 150-200mm deep total, this is a manageable 10-15% of the total depth.

---

## 4. Linear Guide Features

### 4.1 Why Guides Are Critical

The plate must translate axially (parallel to the tube/fitting axis) without tilting. Collet-release.md Section 4 identifies plate tilt as a system-level failure mode: if the plate cocks during actuation, some collets release while others grip harder, replicating the single-fitting "one-sided press" failure at the multi-fitting level.

The parallelism spec (from collet-release.md): <0.3mm deviation across the plate. For the 59x47mm plate (2x2 arrangement at 40x28mm C-C), this means the plate must stay parallel to within 0.3mm / 59mm = 0.29 degrees across the width and 0.3mm / 47mm = 0.37 degrees across the height during the full 3.0mm stroke.

### 4.2 Guide Options for the Plate

#### Option 1: Pin-in-Slot (Recommended for Prototype)

Two or more round pins press-fit or bolted into the dock frame. The plate has matching holes or slots that slide along the pins. The pins constrain the plate to axial translation only.

```
    Top view (plate face):

    ┌──────────────────────────────────┐
    │  ○ pin hole      ○ pin hole      │
    │                                  │
    │       O (1)        O (2)         │
    │                                  │
    │       O (3)        O (4)         │
    │                                  │
    │  ○ pin hole      ○ pin hole      │
    └──────────────────────────────────┘
```

**Pin sizing**: 3mm or 4mm diameter steel dowel pins. For 3mm pins, the plate holes would be 3.2-3.3mm (0.1-0.15mm clearance per side for smooth sliding). For 4mm pins, holes at 4.2-4.3mm.

**Pin placement**: Symmetrically placed at corners or midpoints of edges, outside the bore pattern. For the 59x47mm plate (2x2 grid at 40x28mm C-C), pins placed symmetrically outside the bore pattern (per parts.md: at X=(-5.5, 23.5) and X=(64.5, 23.5) relative to plate bottom-left). This constrains tilt about the horizontal axis.

**Number of pins**: 2 pins fully constrain tilt in one plane. For full anti-tilt, either use 2 pins far apart (maximizing the moment arm against tilt) or 4 pins in a rectangular pattern. Two pins is sufficient if the plate is compact (2x2 grid) and the pins are at least 25mm apart.

**Slot vs. round hole**: Round holes provide the tightest constraint but require the pins to be perfectly parallel. If the dock frame has any tolerance error in pin spacing or parallelism, the plate binds. Slots (elongated holes, round-ended) provide forgiveness in one axis at the cost of looseness in that axis. For a 3D-printed dock, slots are more practical -- they tolerate the ~0.2mm dimensional variation in FDM without binding.

**Slot dimensions**: For 3mm pins: slot width 3.3mm, slot length 3.3mm + 3.0mm travel + 1.0mm margin = 7.3mm. The slot is oriented along the plate travel axis.

**Pros**: Simple, cheap (steel dowel pins are pennies each), precise (steel pin surface is much smoother than 3D printed). The pins can also serve as spring seats if return springs are needed.

**Cons**: Requires hardware (pins). Pins must be securely mounted in the dock frame. Two separate components (plate + dock frame) must be printed and assembled.

#### Option 2: Integral Rail Grooves

The plate has grooves or channels on its sides that mate with corresponding rails on the dock frame. The plate slides along the rails.

```
    Side view:

    dock frame wall    plate edge    dock frame wall
    ┌─────┐          ┌──────────┐          ┌─────┐
    │     │          │          │          │     │
    │  ▶──┤          ├──◀  ▶──┤          ├──◀  │
    │     │          │          │          │     │
    │     │          │          │          │     │
    └─────┘          └──────────┘          └─────┘
              rail/groove interface
```

**Pros**: No separate hardware. Can be printed as part of the plate and dock frame.

**Cons**: FDM rail surfaces are rough (layer lines). Binding is likely without post-processing (sanding). The clearance needed for smooth FDM sliding (0.3-0.5mm per side) is loose enough to allow 0.3-1.0mm of tilt -- right at or beyond the parallelism spec. This approach is sensitive to print quality.

#### Option 3: Bore-Guided (Collets Themselves as Guides)

The outer bores of the stepped profile slide over the body end/fitting body, using the fittings themselves as guide surfaces. The plate is guided by the 4 fittings it engages with.

**Pros**: Zero additional hardware. The guide and actuation surfaces are colocated, which inherently prevents the plate from tilting relative to the collets (the most important reference).

**Cons**: The plate must approach the fittings already roughly aligned -- it can't be guided by features it hasn't engaged yet. There's a "last millimeter problem": the plate has no guidance until the outer bore slides over the body end. Works as secondary guidance once engaged but needs primary guidance for the approach. Also, the tighter the clearance between outer bore and body end (15.10mm, caliper-verified), the better the secondary centering but the more critical the approach alignment.

#### Option 4: Hybrid (Recommended)

**Pins for primary guidance, bores for secondary alignment.**

Two steel dowel pins (3mm) through the plate provide the primary linear constraint. The outer bore cradles provide secondary centering as the plate engages the collets. The pins keep the plate from tilting during the approach; the bore cradles self-center on the collets during engagement.

This is the server blade approach: coarse rails (pins) for the travel, fine features (bores) for the final alignment.

### 4.3 Cam/Lever Interface

The plate needs a feature where the cam or lever applies force to drive it axially. Options:

**Central boss**: A raised pad or boss on the back face of the plate, centered. The cam presses against this pad. Transmits force through the plate's center, minimizing tilt.

**Cam slot**: A through-slot in the plate that the cam shaft passes through. As the cam rotates, its eccentric profile pushes against the slot walls. This constrains the cam to act at a known location on the plate.

**Edge push**: The cam or lever pushes on the plate's edge. Simpler mechanically but applies force off-center, which tends to tilt the plate. Only acceptable if the guide pins are robust enough to resist the resulting moment.

**Recommendation for first print**: Design the back face of the plate with a flat surface (the 2.0mm structural back). The cam interface can be a simple flat-on-flat contact at the plate's center. The cam mechanism is a separate design problem; the plate just needs a flat back face and guide pin holes.

### 4.4 Return Mechanism

After the cam retracts (lever opened), the plate must return to its retracted position (away from the collets). Options:

1. **Collet springs**: The body ends themselves are spring-loaded to their resting (gripping) position. When the plate retracts, the collets push the plate back. This provides ~2-5N per fitting of return force (same as the actuation force), totaling 8-20N. This is enough to return the plate without additional springs.

2. **Compression springs on guide pins**: Small compression springs around the guide pins, between the plate and the dock frame. Provides a positive return force independent of the collets. Adds cost (springs) but ensures the plate always returns even if collets are absent (useful during assembly/testing).

3. **Cam profile**: If the cam has a positive displacement profile in both directions (not just a single lobe), it can drive the plate both inward and outward. An eccentric cam does this naturally -- rotating one way pushes the plate in, rotating the other way allows it to retract. The plate follows the cam profile.

**Recommendation**: Rely on collet spring-back (option 1) for the initial prototype. The collets naturally push the plate back. If testing reveals unreliable return, add compression springs later (option 2). The plate design should accommodate either -- meaning the guide pin holes should have enough length for a spring to sit around the pin.

---

## 5. Compliance (Handling Collet Protrusion Variation)

### 5.1 The Problem

The 4 body ends may not all protrude the same distance from the fitting body face. Collet-release.md estimates +/-0.3mm variation between fittings of the same model. Additionally, the dock's fitting mounting may introduce +/-0.5mm variation in fitting face position. Total worst-case variation between the most-protruding and least-protruding collet: up to 0.8mm.

A rigid plate pushing all 4 collets simultaneously will contact the most-protruding collet first. The plate must continue traveling until the least-protruding collet is also fully engaged. During this continued travel, the already-engaged collets are pushed beyond their required travel.

### 5.2 Overtravel (Simplest Approach)

**Concept**: Design the plate travel (3.0mm) to exceed the collet travel (~1.3mm per side, caliper-verified) by enough margin to absorb the variation.

**Math**: Collet travel needed = ~1.3mm per side (caliper-verified). Variation = 0.8mm worst case. Minimum plate travel = 1.3mm + 0.8mm = 2.1mm. The 3.0mm design travel provides 3.0 - 2.1 = 0.9mm margin -- comfortable.

**What happens to the first-engaged collets**: They are pushed 0.8mm beyond their required travel (worst case). The collet has an internal hard stop where it bottoms out against the fitting body. The force required to push a collet past its travel limit is higher than the release force (the spring compresses further and/or the collet contacts a hard stop). This additional force is absorbed by the cam mechanism.

**Risk**: If the collet has a definite hard stop (metal-on-metal inside the fitting), the overtravel force could be substantial. If the collet spring simply compresses further (no hard stop), the overtravel force is modest. This must be tested with actual fittings.

**Verdict**: Overtravel is the simplest approach and should be the first thing tested. The 3.0mm plate travel provides 0.9mm margin beyond worst-case need (1.3mm collet travel + 0.8mm variation = 2.1mm). If testing shows the collet has a hard stop that makes overtravel problematic, add compliance.

### 5.3 Elastomeric Layer

**Concept**: A thin sheet of rubber or silicone between the rigid plate and the collets. Each collet presses into the elastomer independently, and the elastomer deforms to accommodate variation.

**Material**: 1-2mm sheet of 40-60A durometer silicone (soft). Available as silicone gasket sheet from McMaster-Carr or Amazon.

**Compliance**: A 1.5mm sheet of 50A silicone compresses approximately 20-30% under the 3-5N per fitting load. That's 0.3-0.45mm of independent travel per collet -- close to the +/-0.3mm fitting variation spec.

**Implementation**: Cut a gasket-shaped piece (same outline as the plate, with through-holes matching the tube clearance bore) and sandwich it between the plate face and the collets. The gasket sits in the outer bore cradle.

**Pros**: Simple, cheap, no moving parts. Provides distributed compliance. Can be replaced if it degrades.

**Cons**: Adds an axial layer (1-2mm) to the assembly. The elastomer may creep under sustained load (though the cam only applies force during the release action, not continuously). The elastomer fills the outer bore cradle space, which may interfere with collet lateral constraint.

**Verdict**: Good fallback if overtravel alone doesn't work. Easy to retrofit -- just cut a gasket and insert it. The plate design doesn't need to change.

### 5.4 Spring-Loaded Lips

**Concept**: Each of the 4 inner lip features is independently spring-loaded, allowing it to travel axially relative to the plate body.

**Implementation in FDM**: Extremely difficult. Each lip would need to be a separate sliding ring within the plate body, with a small compression spring behind it. The bore diameters are very tight (inner lip just over 9.57mm within the ~15.2mm outer bore), leaving very little room for spring seats and sliding features. The assembly complexity (4 springs, 4 sliding rings, 4 retaining features) is far beyond what's needed for 0.8mm of compliance.

**Verdict**: Over-engineered for this application. The compliance need is <1mm, and overtravel or an elastomeric layer handles it trivially. Spring-loaded lips are appropriate for systems with 5mm+ variation or where different fittings need fundamentally different travel.

### 5.5 Compliance Recommendation

**Start with overtravel alone.** The 3.0mm plate travel provides 0.9mm margin over the 1.3mm collet travel (caliper-verified) plus 0.8mm worst-case variation. This is comfortable. If overtravel causes excessive force (collet hard stops), **add a 1.5mm silicone gasket** between the plate and the collets for additional independent compliance per collet.

---

## 6. Material and Print Orientation

### 6.1 Material: PETG

PETG is the recommended material (consistent with guide-alignment.md for all sliding surfaces):

- **Tensile strength**: ~50 MPa (adequate for the 12-20N total load on the plate)
- **Flexural modulus**: ~2.1 GPa (stiff enough that the plate won't flex meaningfully under load)
- **Layer adhesion**: significantly better than PLA. Important because the inner lip (2.25mm wall) must withstand repeated axial loading without delamination.
- **Chemical resistance**: resistant to water, mild acids/bases. Important for moisture-adjacent environment.
- **Friction coefficient (PETG on PETG)**: ~0.1-0.2. Lower than PLA-on-PLA (~0.2-0.3). Important for smooth sliding on guide pins and in the dock frame.
- **Creep resistance**: better than PLA at room temperature.

**Alternatives**:
- PLA: easier to print, more brittle. Acceptable for test coupons, not for the production plate.
- ABS: better heat resistance, worse layer adhesion than PETG, requires enclosure. No advantage for this application.
- Nylon/PA: excellent wear resistance and toughness. Harder to print (warping, moisture absorption). Overkill.

### 6.2 Print Orientation

The critical question is which axis the bore runs relative to the build plate.

#### Option A: Bore axis vertical (Z-up) -- RECOMMENDED

```
    Build plate (XY)
    ┌───────────────────┐
    │                   │
    │  O  O   ← bores  │   ← looking DOWN at the plate
    │  O  O             │      lying flat on the bed
    │                   │
    └───────────────────┘
```

The plate lies flat on the build plate. The bore axis runs vertically (Z direction). Each layer is a horizontal slice through the plate.

**Pros**:
- The circular bores are printed as circles in the XY plane -- best possible circularity from FDM.
- The inner lip is formed by the XY perimeter paths, which gives the smoothest and strongest surface.
- The lip wall (2.25mm radial) is printed as perimeter walls, which are the strongest part of an FDM print.
- The plate's overall flatness is determined by the build plate, which is the most planar reference surface available.
- No supports needed (all features are either flat bottom or circular holes).

**Cons**:
- The plate thickness (6mm) is in the Z direction. Layer adhesion must be good to resist the axial (Z-direction) forces. PETG's superior layer adhesion makes this acceptable.
- The flat outer face (fitting-facing surface) is the first layer on the build plate. First-layer quality matters for the lip face flatness. Print on a smooth PEI sheet for the best first-layer finish.

#### Option B: Bore axis horizontal

The plate stands upright on the build plate, with the bore axes running in the XY plane.

**Pros**: Layer adhesion direction aligns with the axial load direction (strongest). The lip face is formed by the perimeter paths.

**Cons**: The circular bores are formed by stacked layers (stairstepping). A circle printed in the ZX or ZY plane has visible layer steps that create a rough bore surface. The inner lip bore (just over 9.57mm) would have ~0.2mm step artifacts at 0.2mm layer height — problematic given the tight tolerances needed for collet hugging. The plate needs supports for the overhanging bore features. Overall worse geometric accuracy.

**Verdict**: Option A (bore axis vertical) is clearly superior.

### 6.3 Print Parameters

| Parameter | Value | Rationale |
|---|---|---|
| Layer height | 0.16-0.20mm | Standard quality. 0.16mm for best bore accuracy. |
| Nozzle | 0.4mm | Standard. The 2.25mm lip wall is ~5-6 perimeters at 0.4mm. |
| Perimeters/walls | 4 minimum | Ensures robust lip wall structure. |
| Infill | 40-60% | Body infill between bores. Higher infill = stiffer plate. |
| Infill pattern | Grid or gyroid | Gyroid for best isotropic stiffness. |
| Top/bottom layers | 4 minimum | Solid cap on the fitting-facing surface (lip face). |
| First layer | 0.20mm on smooth PEI | Clean first layer = flat lip face. |
| Print speed | 40-60mm/s | Slower for better dimensional accuracy on small features. |

### 6.4 Minimum Wall Thicknesses

| Feature | Wall Thickness | Perimeters (0.4mm nozzle) | Assessment |
|---|---|---|---|
| Inner lip radial wall | 2.25mm | 5.6 perimeters | Robust. Solid perimeter walls, no infill needed. |
| Wall between outer bores (vertical, at 28mm C-C) | 12.4mm | N/A (solid material) | Very comfortable. Not a constraint. |
| Wall between outer bores (horizontal, at 40mm C-C) | 24.4mm | N/A (solid material) | Very comfortable. Not a constraint. |
| Edge-to-bore clearance (minimum) | 1.7mm | 4.25 perimeters | Adequate. Provides material for guide pin slots outside the bore pattern. |

---

## 7. First Print Specifications

### 7.1 Single-Hole Test Coupon

**Purpose**: Validate the stepped bore geometry against an actual John Guest fitting before committing to a 4-hole plate. Verify that the inner lip correctly engages and releases the collet. Measure actual collet release feel and force.

**Design**:

```
    Top view:
    ┌─────────────────────────┐
    │                         │
    │          O              │    Single stepped bore
    │                         │    centered on a square block
    │                         │
    └─────────────────────────┘

    Dimensions:
    - Block: 22mm x 22mm x 6mm thick
    - Bore: stepped profile per Section 1 (tube clearance / collet hugger / body end cradle)
```

| Dimension | Value |
|---|---|
| Block width | 22.0mm |
| Block height | 22.0mm |
| Block thickness | 6.0mm |
| Tube clearance bore | Between 6.30–6.69mm, through (see Section 1.3) |
| Inner lip bore (collet hugger) | Just over 9.57mm, 2.0mm deep (see Section 1.3) |
| Outer bore (body end cradle) | Just over 15.10mm, 2.0mm deep (see Section 1.3) |
| Material | PETG |
| Print orientation | Bore axis vertical (Z-up) |
| Estimated print time | ~10-15 minutes |
| Estimated material | <2g |

**Test procedure**:
1. Insert 1/4" hard tubing through the test coupon's bore.
2. Insert the tubing into a John Guest fitting.
3. Slide the test coupon along the tubing toward the fitting until the cradle engages the body end and inner lip surrounds the collet.
4. Push the coupon axially toward the fitting (simulating plate actuation).
5. Feel for collet release. Can the tubing be withdrawn while the coupon holds the collet depressed?
6. Test centering: does the collet release cleanly, or does it cock/bind?
7. Intentionally tilt the coupon during release to find the tilt tolerance.

**Print 3 copies with variation**: Vary the through-hole and inner lip bore diameters to bracket the optimal fit. For example, through-holes at 6.4mm, 6.5mm, 6.6mm (spanning the 6.30–6.69mm window), and inner lip bores at 9.7mm, 9.8mm, 9.9mm (varying the collet hug tightness). The outer bore should also be varied in tightness — try 15.2mm, 15.3mm, 15.4mm. The goal is to find the tightest dimensions that still allow smooth plate engagement without binding.

### 7.2 Four-Hole Plates

Print after validating the single-hole bore geometry. Use the bore dimensions confirmed by the test coupon.

#### Spec A: 2x2 Grid Plate (per parts.md)

```
    Top view:
    ┌─────────────────────────────────────────────────────────────┐
    │  ○                                                     ○    │
    │        O (1)                            O (2)               │
    │                                                             │
    │                                                             │
    │        O (3)                            O (4)               │
    │  ○                                                     ○    │
    └─────────────────────────────────────────────────────────────┘

    ○ = guide pin slots (3.3mm wide x 7.3mm long)
    O = stepped bore (per Section 1.3)
```

| Dimension | Value |
|---|---|
| Plate width | 59.0mm |
| Plate height | 47.0mm |
| Plate thickness | 6.0mm |
| Bore center-to-center | 40.0mm horizontal, 28.0mm vertical |
| Bore centers (relative to plate bottom-left) | (9.5, 9.5), (49.5, 9.5), (9.5, 37.5), (49.5, 37.5) |
| Guide pin slots | 2x 3.3mm wide x 7.3mm long, at X=(-5.5, 23.5) and X=(64.5, 23.5) relative to plate bottom-left |
| Push rod contact | 8mm dia x 1mm boss at plate center (29.5, 23.5) |
| Material | PETG |
| Estimated print time | ~45-60 minutes |
| Estimated material | ~12-15g |

Dimensions per parts.md. The 59x47mm envelope provides 1.7mm minimum edge-to-bore clearance (at the vertical bore edges) and generous 12.4mm+ walls between all bore pairs.

#### Spec B: 4-in-a-Line Plate

Not applicable — the 40mm horizontal spacing makes a 4-in-a-line layout impractically wide (120mm+ span). The 2x2 grid (Spec A) is the selected arrangement.

---

## 8. Interdependencies with Other Components

### 8.1 Mating Face (Dock)

The dock's mating face must have:
- 4 John Guest fittings mounted in the same pattern as the plate bores (40mm H x 28mm V C-C, per parts.md).
- Guide pin holes (or pin mounts) matching the plate's guide pin holes, with pins extending toward the incoming plate.
- Clearance behind the plate for the cam mechanism.
- The fitting body end OD (15.10mm, caliper-verified) is the controlling dimension for clearance. At 40x28mm C-C, fitting body ends have 12.9mm minimum clearance (vertical) — no interference risk. The fitting pocket bore grips the 9.31mm center body (caliper-verified), with the 15.10mm body ends protruding on both sides of the wall.

### 8.2 Cam/Lever Mechanism

The cam acts on the back face of the plate. Key interface dimensions:
- Plate back face is flat, at a known distance from the fitting face (6.0mm behind the fitting-facing surface in the retracted position, 3.0mm in the actuated position -- because the plate moves 3.0mm).
- The cam must apply force at or near the plate center to minimize tilt. For the 2x2 grid, the center is at the geometric center of the 4 bores.
- The cam's eccentricity (1.0-1.5mm from cam-lever.md) produces 2.0-3.0mm of displacement. The plate travel spec (3.0mm) matches the upper end of this range.
- The cam pivot axis should be perpendicular to the plate's travel axis (i.e., the cam rotates in a plane parallel to the plate face).

### 8.3 Cartridge Body

The cartridge body houses the pumps and tube stubs. The tube stubs must align with the plate's tube clearance holes. For the 2x2 grid, this means 4 hard 1/4" OD tube stubs in a 40mm H x 28mm V C-C grid on the cartridge face. The stubs pass through the plate's through-holes (between 6.30–6.69mm, very tight fit) and into the John Guest fittings.

**Tube stub length**: Must be long enough to reach through the plate thickness (6.0mm) and into the fitting (~16mm insertion depth). Total stub length from cartridge face: 6.0mm (plate) + 3.0mm (plate travel gap when retracted) + 16.0mm (fitting insertion) = 25.0mm minimum. Add 2-3mm safety margin = **28mm stub length**.

### 8.4 Return Path

If the plate relies on collet spring-back for return (Section 4.4), the plate must have a feature that prevents it from separating from the cam. Either:
- The cam is captive in a slot in the plate (cam pushes and pulls), or
- The guide pins have retaining features (snap rings, shoulders) that limit the plate's outward travel, and the collet springs push the plate against these stops.

---

## 9. Recommendation Ranking

### Arrangement

1. **2x2 grid at 40mm H x 28mm V C-C** (selected, per parts.md) -- 59x47mm plate, generous inter-bore walls (12.4mm minimum), comfortable body end clearance (12.9mm minimum). Max moment arm 24.4mm to corner bore.

### Compliance

1. **Overtravel** -- simplest, no additional parts. 3.0mm plate travel provides 0.9mm margin over ~1.3mm collet travel (caliper-verified) plus 0.8mm worst-case variation. Test first.
2. **Elastomeric gasket** -- retrofit if overtravel causes excessive force at collet hard stops. 1.5mm silicone sheet.
3. **Spring-loaded lips** -- over-engineered. Only if variation exceeds 2mm.

### Guide Features

1. **Steel dowel pins through plate slots** (hybrid with bore self-centering) -- precise, simple hardware, tolerant of FDM variation.
2. **Integral printed rails** -- no hardware, but FDM surface finish and tolerance make smooth sliding difficult.
3. **Bore-guided only** -- works as secondary alignment but can't guide the approach.

### Material and Orientation

1. **PETG, bore axis vertical (Z-up)** -- best bore circularity, strongest lip walls, no supports needed.

---

## 10. Concrete First-Print Plan

### Print 1: Three Single-Hole Test Coupons

**Goal**: Validate bore geometry against actual fittings.

Three 22mm x 22mm x 6mm blocks, each with a single stepped bore:
- **Coupon A**: 8.0 / 12.5 / 15.6mm (nominal from caliper-verified dimensions)
- **Coupon B**: Tighter inner lip and outer bore (closer to reference dimensions, less clearance)
- **Coupon C**: 8.0 / 13.0 / 15.6mm (looser lip, less contact area)

All three print on one bed in under 30 minutes. Test each against a John Guest fitting with tubing inserted. Record which coupon gives the cleanest release.

### Print 2: 2x2 Grid Plate (No Guide Pins)

**Goal**: Validate 4-hole spacing and simultaneous release.

59mm x 47mm x 6.0mm plate with 4 stepped bores at 40mm H x 28mm V C-C in a 2x2 grid. No guide pin holes yet -- just hand-hold the plate against 4 fittings and press. Verify that all 4 collets release. Check for uneven engagement.

Use the bore dimensions validated by Print 1.

### Print 3: 2x2 Grid Plate with Guide Pin Holes

**Goal**: Test guided actuation.

Same as Print 2, but add 4 corner guide pin holes (3.3mm diameter, 7.3mm slot length). Purchase 4x 3mm steel dowel pins (40-50mm long). Build a simple test frame (3D printed) that holds the pins and 4 John Guest fittings. Test plate travel on the pins. Measure parallelism deviation with calipers at each corner.

### Hardware Needed for Testing

| Item | Qty | Source | Approximate Cost |
|---|---|---|---|
| 3mm x 50mm steel dowel pins | 4 | Amazon / McMaster-Carr | $5-8 |
| John Guest 1/4" push-to-connect unions | 4 | Already in hand | $0 |
| 1/4" OD hard tubing (short stubs) | 4x 50mm | Already in hand | $0 |
| 1.5mm silicone gasket sheet (optional) | 1 small piece | Amazon | $5-8 |
| PETG filament | ~20g total | Already in hand | ~$0.50 |

---

## Sources

- Collet-release.md (this project) -- bore dimensions, forces, failure modes, tolerances
- Guide-alignment.md (this project) -- FDM clearances, rail tolerances, sliding fit recommendations
- Cam-lever.md (this project) -- cam eccentricity, force multiplication, over-center behavior
- Electrical-mating.md (this project) -- contact placement relative to water fittings
- [John Guest 1/4" Push-to-Connect Technical Specifications](https://www.johnguest.com/sites/default/files/files/tech-spec-od-fittings-v2.pdf) -- fitting body dimensions
- [3D Printing Tolerances and Fits (Prusa Knowledge Base)](https://help.prusa3d.com/article/tolerance-and-engineering-fits_341710) -- FDM clearance guidelines for sliding fits
- [PETG Material Properties (MatWeb)](https://www.matweb.com/search/DataSheet.aspx?MatGUID=4de1c3bb37f04e7e959e286bf7474ae3) -- tensile strength, flexural modulus
- [Engineering Fit Tolerances for FDM (CNC Kitchen)](https://www.cnckitchen.com/blog/the-ultimate-engineering-fits-guide-for-3d-printing) -- clearance per side recommendations
- [Silicone Rubber Durometer and Compression Properties](https://www.stockwell.com/blog/silicone-rubber-hardness-durometer/) -- compression % vs durometer for elastomeric compliance layer
