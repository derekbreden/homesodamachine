# Enclosure Concrete Architecture: Two-Part Snap-Fit Assembly

**Date:** 2026-03-29
**Status:** Architecture Finalized — Ready for CAD Implementation
**Synthesis Reference:** [synthesis.md](synthesis.md)
**Scope:** Physical decomposition, join methods, seam geometry, surface composition, material selection, service access, and FDM manufacturing constraints

---

## Architecture Statement

The soda flavor injector enclosure is a **220 × 300 × 400 mm consumer appliance printed as two monolithic halves and permanently sealed with snap-fit joinery**. The enclosure reads as a unified, rigid, premium product with no visible fasteners or assembly artifacts. A visible seam at 200 mm height is refined through intentional gap geometry (1.2 mm nominal), matte black finish, and 10 strategically placed snap points that provide both structural security and tactile feedback to the user or technician during assembly.

All interior components (bags, pump cartridge, displays, electronics, valve manifold) snap-mount to the two outer halves via internal connector points. The user experiences zero assembly complexity and perceives a permanent, unbreakable closure.

---

## 1. Piece Count and Split Strategy

### Part Inventory

| Part | Quantity | Type | Print Area | Height |
|------|----------|------|-----------|--------|
| **Enclosure Top Half** | 1 | Monolithic | 220 × 300 mm | 200 mm |
| **Enclosure Bottom Half** | 1 | Monolithic | 220 × 300 mm | 200 mm |
| **Total printed pieces (enclosure)** | 2 | — | — | — |

### Decomposition Rationale

**Why monolithic halves, not sub-components?**

1. **Structural unity:** Each half is a single rigid shell with no internal joins. This eliminates secondary snap points, reduces complexity, and ensures each half prints as a stable, self-supporting structure.

2. **Snap-fit efficiency:** All interior components snap to the **inner surfaces** of the two halves. No internal sub-components require snaps to the walls (e.g., bags snap directly to the inner surfaces; pump cartridge dock snaps to bottom-half interior frame).

3. **Manufacturing simplicity:** Two monolithic pieces reduce CAD complexity, print time, and support material. Each half fits within the Bambu H2C build envelope when oriented correctly (see Section 6).

4. **Assembly simplicity:** The user (or technician) receives the device as two halves with all interior components pre-installed and snapped to the inner surfaces. Final closure is a single two-way snap operation.

### Horizontal Seam Location

The seam runs **horizontally at 200 mm height**, exactly at the vertical midpoint of the 400 mm enclosure height.

**Geometric layout:**
- **Top half:** 220 × 300 × 200 mm (upper shell with all upper-interior surfaces)
- **Bottom half:** 220 × 300 × 200 mm (lower shell with all lower-interior surfaces)
- **Seam plane:** Horizontal at Z = 200 mm (using enclosure bottom as Z = 0 reference)
- **Seam perimeter:** 1040 mm (220 + 300 + 220 + 300 mm around all four edges)

**Rationale for 200 mm split:**
- Optical balance: Places seam at the visual center of the form (golden ratio proximity)
- Bags alignment: The 35-degree diagonal bag orientation (vision.md) occupies the top ~60 mm; seam intercepts the middle of this volume naturally
- Manufacturing fit: Each half fits within the Bambu H2C single-nozzle envelope (325 × 320 × 320 mm) when oriented with seam face horizontal and height dimension (200 mm) vertical on the build plate
- Load distribution: Evenly splits the internal component volume between halves; neither half is top-heavy or bears disproportionate loads

---

## 2. Join Methods

### Primary Join: Snap-Fit Perimeter Closure

**Configuration:**
- **Type:** Cantilever snap-fit (living hinge) with permanent closure
- **Hook profile:** Equilateral triangle or bullnose (smooth stress distribution, optimized fatigue life)
- **Total snap points:** 10 distributed around the seam perimeter
- **Nominal spacing:** ~100 mm (range 80–150 mm acceptable)

**Snap geometry specification:**

| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| Cantilever beam length | 20 mm | mm | Optimized for 40–50 N per snap with Nylon PA12 |
| Beam thickness (base) | 1.2 mm | mm | 3 perimeters; structural minimum |
| Beam thickness (tip) | 0.8 mm | mm | Tapered to reduce stress concentration |
| Beam width | 6–8 mm | mm | Controls lateral stability and rigidity |
| Hook overhang height | 2.5 mm | mm | Vertical projection into female undercut |
| Hook lead-in angle | 25° | degrees | Reduces assembly force; improves tolerance |
| Fillet radius at beam base | 0.8 mm | mm | Critical for fatigue life; Kt ≈ 1.3 |
| Undercut depth (female half) | 2.8 mm | mm | Accommodates hook + 0.3 mm tolerance + clearance |
| Draft angle on hook | 6° | degrees | Supports clean FDM print and removal |

**Assembly force and reliability:**

| Parameter | Value | Unit | Justification |
|-----------|-------|------|---|
| Force per snap | 40–50 | N | Achievable by technician; within Nylon design envelope |
| Total mating force (10 snaps) | 400–500 | N | Distributed; no point overloaded |
| Snap seating resistance (post-assembly) | >80 | N/snap | Prevents accidental disassembly; permanent feel |
| Fatigue life (Nylon PA12) | >10,000 | cycles | Permanent closure (zero cycles); large safety margin |

**Snap point layout (top view of seam perimeter):**

```
             ← 220 mm →
           [S1]   [S2]            Front face
           ┌───────────┐
           │S4      S3 │
    [S7]   │           │   [S5]  ← 300 mm
           │S8      S6 │
           └───────────┘
           [S10]   [S9]           Back face

S1–S4: Corners and near-corner snaps (stress concentration control)
S5, S7: Midpoints on 300 mm depth edges (front/back)
S6, S8: Secondary snaps on 300 mm depth edges (distributed spacing)
S9, S10: Midpoints on 220 mm width edges (left/right)

Spacing: Front (S1→S5) = ~150 mm, (S5→S2) = ~70 mm, (S2→S3) = ~150 mm
Pattern balances stress distribution and cosmetic uniformity
```

### Internal Sub-Component Mounting (No Secondary Snaps)

All interior components mount **directly to the inner surfaces of the top and bottom halves** via snap anchors molded into the enclosure shells. There are no rigid sub-frames or secondary assemblies that require snaps to the walls.

**Examples:**

1. **Bags:** Two lens-shaped cradles snap to the bottom-interior surfaces of both halves (one cradle per half). Two constraint covers snap to internal vertical ribs. (4 snaps per cradle + 4 snaps per constraint = 16 internal snaps total, all part of the half's integral geometry)

2. **Pump cartridge:** Docks into a snap-fitted mounting frame that is integral to the bottom-half interior. 4 corner snaps secure the frame; the cartridge itself is hand-removable.

3. **Displays and air switch:** Mount via detachable snap-fit frames integrated into the front-interior panel geometry.

4. **Valve manifold:** Snaps directly to internal vertical ribs via 6–8 distributed snap anchors.

5. **Electronics:** PCB standoffs snap via 4-corner clips integral to the back-top interior.

**Rationale:** This architecture eliminates secondary snap points that would complicate assembly and print orientation. Each interior component's snap anchors are designed into the enclosure halves themselves, making assembly a linear process: pre-position interior components, snap to halves, close the enclosure with the 10 perimeter snaps.

---

## 3. Seam Placement and Treatment

### Seam Location

**Placement:** Horizontal at 200 mm height, running continuously around all four edges of the enclosure (1040 mm perimeter).

**Orientation:** Front-to-back (depth axis), not left-to-right (width axis)
- Allows cleaner tubing routing through the back wall
- Simplifies internal component positioning
- Aligns with bag diagonal orientation vector (35° from horizontal places bags above the seam)

### Seam Gap Specification

| Parameter | Specification | Tolerance | Rationale |
|-----------|---|---|---|
| **Gap width** | 1.2 mm | ±0.1–0.2 mm | Premium appliance standard; visible as intentional thin line, not sloppy gap |
| **Gap uniformity** | Consistent along entire 1040 mm | <0.2 mm variation | Gap consistency more critical than absolute width for premium perception (per design-patterns research) |
| **Seam recess depth** | 0.5–1.0 mm inset from outer surface | ±0.1 mm | Creates shadow line that reframes gap as design feature; optical break prevents "cheap gap" appearance |
| **Recess channel width** | 1.2 mm (match gap width) | ±0.2 mm | Continuous around entire perimeter |
| **Seam corner radii** | 3–4 mm | — | Smooth transitions where seam meets vertical side walls; prevents sharp edges |

### Seam Geometry Profile

The seam is a recessed horizontal line around the enclosure perimeter:

```
EXTERNAL PROFILE (side view):
    ════════════════════════ ← Outer surface (matte black)
    ║
    ║  0.5–1.0 mm recess
    ║
    ════════════════════════ ← Secondary surface (inside recess)
    │
    └─ 45° × 0.5 mm chamfer (softens visual transition)

CROSS-SECTION AT SEAM:
    Top half outer surface ─┐
                             ├─ 1.2 mm gap (filled by snap hook engagement)
    Bottom half outer surface ┘

    Beneath the gap:
    ├─ Top half snap hook extends downward (2.5 mm overhang)
    ├─ Bottom half snap undercut extends upward (2.8 mm depth)
    └─ Overlap at snap engagement point locks the two halves rigidly
```

### Recess Channel Treatment

The 0.5–1.0 mm recess channel runs **continuously around the entire perimeter** on all four external edges:

- **Front edge:** Continuous recess from left corner to right corner
- **Back edge:** Continuous recess from left corner to right corner
- **Left edge:** Continuous recess from front to back
- **Right edge:** Continuous recess from front to back
- **Corner transitions:** 3–4 mm radius curves at all four corners (inside and outside of recess)

**Why continuous?** The recess creates a visual "horizon line" that reframes the seam as an intentional design element rather than an unintended gap. This requires visual consistency at every angle.

### Snap Hook Engagement Detail

The snap hooks engage the undercut from below (top-half snaps catching bottom-half undercuts, and vice versa in a symmetric pattern).

```
TOP HALF (seam-facing side):
    ┌─────────────────┐
    │ [Snap hook]     │ ← Cantilever beam with triangle/bullnose hook
    │ ════════════════│ ← Seam face
    │                 │
    └─────────────────┘

BOTTOM HALF (seam-facing side):
    ┌─────────────────┐
    │                 │
    │ ════════════════│ ← Seam face
    │ [Snap undercut] │ ← Recessed cavity to catch top-half hook
    └─────────────────┘

ASSEMBLY:
    Top seam face drops down and snaps into bottom undercut.
    Engagement depth: ~2.5 mm overhang into ~2.8 mm undercut.
    Final state: Flush joint with no visible overhang or step.
```

---

## 4. User-Facing Surface Composition

### External Surfaces (What the User Sees and Touches)

**All external surfaces are matte black with 2–3 mm edge fillets:**

1. **Front face (220 × 200 mm upper, 220 × 200 mm lower):**
   - Smooth, matte black finish
   - Embedded display and air switch openings (flush-mounted)
   - Center focal point: displays draw the eye; seam is not dominant

2. **Back face (220 × 200 mm upper, 220 × 200 mm lower):**
   - Smooth, matte black finish
   - Port penetrations: cold water inlet/outlet, tap water inlet, flavor outlets (1/4" quick-connects recessed 5–10 mm)
   - Seam runs horizontally across mid-back, uninterrupted

3. **Left and right side faces (300 × 200 mm upper, 300 × 200 mm lower):**
   - Smooth, matte black finish
   - Seam visible as horizontal line at mid-height
   - No protrusions or features; clean geometric surfaces

4. **Top surface (220 × 300 mm):**
   - Matte black finish
   - Funnel centered at front edge
   - Minimal surface breaking; clean aesthetic

5. **Bottom surface (220 × 300 mm):**
   - Matte black finish
   - Mounting feet or leveling pads (if required for counter stability)

### Seam as Design Element

The horizontal seam at mid-height is **intentionally visible** and refined to read as a design line (analogous to premium appliances like Instant Pot or refrigerator door seams):

- **Visual hierarchy:** The seam is a secondary visual element; primary focus is the functional front face (displays, air switch)
- **Reading at arm's length:** Seam appears as a thin, uniform horizontal line; gap uniformity is what communicates premium quality
- **Reading at 35-degree angle:** Seam runs diagonally across the view; consistency is critical (no wavering or variation)
- **Tactile feedback:** Running a fingertip along the seam, user feels a consistent, smooth step (the recess edge); no sharp edges or catches

### Edge Treatment

**All external edges receive 2–3 mm fillets:**

- **Vertical edges (four corners):** 2–3 mm radius fillet from top to bottom
- **Top edge (where top half meets top surface):** 2–3 mm radius fillet, continuous around all four sides
- **Bottom edge (where bottom half meets bottom surface):** 2–3 mm radius fillet, continuous around all four sides
- **Seam corners (where horizontal seam meets vertical side walls):** 3–4 mm radius to ensure smooth visual and tactile transition

**Rationale:** Research (design-patterns.md) confirms fillets >2 mm improve premium perception; sharp corners read as unfinished or cost-reduced.

---

## 5. Design Language — Material, Finish, Feel

### Material Selection

**Primary material: Nylon PA12 (polyamide 12)**

**Why Nylon PA12?**

1. **Fatigue resistance:** 10,000+ cycles, much higher than PETG (500–1000 cycles). Although this is a permanent closure (zero cycles), the snap beams experience stress concentration at the base; Nylon's superior fatigue characteristics provide a large safety margin for sustained stress.

2. **Moisture stability:** Unlike PLA (which degrades in humid environments) or ABS (which is more brittle at cold temperatures), Nylon maintains consistent mechanical properties across temperature and humidity ranges (-10°C to 50°C).

3. **Food-safe and chemical-resistant:** Tubing carries tap water, carbonated water, and food-grade syrup. Nylon is approved for food contact and resists moisture absorption better than PLA or PETG.

4. **FDM printability:** Bambu H2C supports Nylon printing with good surface finish and dimensional accuracy when properly calibrated.

5. **Cost-effectiveness:** Mid-range cost for a one-off prototype; lower than exotic composites, more durable than PLA.

**Fallback material: PETG**

If Nylon becomes unavailable or poses scheduling issues, PETG is an acceptable substitute with trade-offs:
- Slightly lower fatigue life (500–1000 cycles vs. 10,000+)
- Adequate for a permanent closure (zero cycles)
- Better cost per kg, faster print speeds
- Slightly lower moisture stability but acceptable for indoor kitchen appliance

**Material NOT recommended:**
- **PLA:** Brittle below 0°C; poor humidity resistance; degradation risk in moist environments
- **ABS:** Requires higher print temperatures; warping risk in large enclosures; weaker snap fatigue life than Nylon

### Surface Finish Specification

**Color:** Matte black
**Gloss level:** 20–40% per ASTM D523 (60° gloss meter)
**Application:** Paint or powder coat post-print

**Why matte black?**

1. **Optical advantage:** Diffuse reflection prevents light concentration at the seam. A glossy finish would create specular highlights that emphasize the seam gap; matte finishes hide this effect.

2. **Premium perception:** Matte finishes communicate solid, permanent construction. Glossy surfaces read as fragile or toy-like by contrast.

3. **Tactile suggestion:** Matte surfaces feel more substantial and quality-oriented than glossy.

4. **Practical:** Hides dust, fingerprints, and minor surface variations in the FDM print.

**Finish application process:**

1. Print both halves in natural Nylon color
2. Sand surfaces with 220–400 grit sandpaper (removes layer marks)
3. Apply matte black paint or powder coat (two coats recommended for uniform coverage)
4. Cure per paint/powder coat specifications

**Post-finish seam treatment:**

After painting, the seam gap may accumulate paint residue. Recommend:
- Mask the seam gap before painting (using tape along edges), or
- Carefully clean paint from seam gap post-cure using a small brush and solvent (acetone for paint, appropriate solvent for powder coat)

### Tactile Experience at Assembly and Use

When the enclosure is assembled (snaps seated):

1. **Snap feedback:** Each of the 10 snaps produces an audible click and tactile "snap" as it seats. User/technician feels a definite engagement at each point.

2. **Rigidity:** After all 10 snaps are seated, the enclosure has zero play or rocking. The two halves feel like a single rigid box.

3. **Seam smoothness:** Running a fingertip along the horizontal seam, the user feels a consistent, smooth step at the recess edge. No sharp transitions, no catching on edges.

4. **Grip quality:** The matte surface provides good tactile grip without slipperiness. Users perceive quality in the texture.

5. **Weight and balance:** The assembled enclosure feels substantial and well-balanced in hand, communicating premium construction.

---

## 6. Service Access Strategy

### Constraint: Only Pump Cartridge Is User-Replaceable

Per the vision (requirements.md Section 4), the ONLY user-serviceable component is the **pump cartridge** (containing both peristaltic pumps). All other components (bags, valves, electronics, displays, tubing) are permanent fixtures and NOT user-replaceable.

### Pump Cartridge Access Mechanism

**Location:** Front-bottom of enclosure, below the displays and air switch

**Cartridge design (per vision.md Section 3):**
- Removable pump cartridge containing 2 peristaltic pumps mounted to a flat plate via 4 screws
- Quick-connect mechanism: 4 tube stubs on the enclosure interior wall; cartridge docks and engages via 4 quick-connect ports on the cartridge back
- Release mechanism: Squeeze-to-release with a flat palm-push surface and finger-pull release surface (both inset on cartridge front)

**Access procedure (user-facing):**

1. **Removal:**
   - User squeezes the cartridge release surfaces (palm pushes flat front surface while fingers curl upward to pull the release plate toward them)
   - The squeeze motion pulls a release plate inside the cartridge, which in turn presses the collets of the 4 quick-connects toward the user, disengaging the tubes
   - Cartridge slides out of the enclosure dock

2. **Replacement:**
   - New cartridge is aligned with the 4 tube stubs on the enclosure interior
   - Cartridge is pushed in until it seats fully
   - The quick-connect collets engage automatically; no user action required beyond inserting the cartridge

**Cartridge dock design (enclosure-side):**
- Snap-fitted mounting frame integral to the bottom-half interior, with 4 corner snaps anchoring the frame to the enclosure walls
- The dock frame provides 4 tube stub ports at the correct spacing for the quick-connects
- The dock is NOT user-accessible; it remains in the enclosure permanently

**Why this works:**
- User never opens the enclosure; the cartridge removal is the only service interaction
- The cartridge is a "black box" to the user; the squeeze mechanism is intuitive and requires no tools
- The cartridge contains all wear parts (pump seals, tubing, etc.); replacement is simple and safe

### No Other Service Access

The vision specifies no other service interactions. Do NOT design access panels, removable sub-components, or serviceable sub-assemblies for:
- The bags (permanent fixtures)
- The valves (permanent fixtures)
- The electronics (permanent fixtures)
- The displays (if user-removable, cables only; not user-replaceable)

If the device requires future maintenance beyond cartridge replacement, it must be disassembled at a service center. The consumer product is sealed and permanent.

---

## 7. Manufacturing Constraints — Print Bed, Orientation, Material

### Bambu H2C Build Envelope

**Single-nozzle capacity:** 325 mm (W) × 320 mm (D) × 320 mm (H)

**Enclosure dimensions:** 220 mm (W) × 300 mm (D) × 400 mm (H)

**Problem:** The enclosure height (400 mm) exceeds the available height (320 mm). Solution: Split horizontally at 200 mm as designed.

### Part Fit Verification

**Top half (200 mm height):**
- Bounding box: 220 × 300 × 200 mm
- Fits within 325 × 320 × 320 mm envelope? YES (with 5 mm margin on width, 20 mm on depth, 120 mm on height)

**Bottom half (200 mm height):**
- Bounding box: 220 × 300 × 200 mm
- Fits within 325 × 320 × 320 mm envelope? YES (same fit as top half)

**Conclusion:** Both halves fit comfortably within the Bambu H2C build envelope.

### Print Orientation Strategy

**Critical constraint (from snap-fit-design.md Section 6.3):** Snap cantilever beams must flex **parallel to the build plate** (in XY-plane), not perpendicular (Z-axis), to avoid 50% strength reduction.

**Recommended orientation for each half:**

**Top half:**
- **Seam face:** Horizontal on the build plate (XY-plane)
- **Height (200 mm):** Vertical (Z-axis, growing upward from print bed)
- **Snap arms orientation:** Oriented in the XY-plane, perpendicular to the seam face
  - This ensures beams flex left-right (X-direction) or forward-back (Y-direction), parallel to the build plate layers
  - Stress concentration at the base is handled by the layer structure (lateral stress, not perpendicular)

**Bottom half:**
- **Identical orientation:** Seam face horizontal, height vertical, snap arms in XY-plane

**Justification:**
- Snap beams printed in XY-plane orientation achieve ~80–90% of their designed strength
- Snap beams printed in Z-direction (perpendicular to plate) achieve only 40–50% of designed strength
- This orientation is achievable without exceeding the 320 mm height limit (200 mm part height + 20 mm for nozzle clearance = 220 mm; well within 320 mm ceiling)

### Support Strategy

**Snap hook geometry creates undercuts that require supports.**

**FDM support design (per requirements.md Section on "Designed support geometry"):**

1. **Break-away support ribs for snap hooks:**
   - Rib dimensions: 0.3 mm wide × 0.8 mm tall
   - Interface gap: 0.2 mm beneath the hook (fragile bridge between rib and hook)
   - Spacing: Every 5–10 mm along the hook perimeter
   - Removal: Ribs snap cleanly by hand or light tool pressure; minimal surface damage

2. **Intentional interface gap:**
   - The printer bridges the 0.2 mm gap with a thin, fragile connection
   - This connection breaks away cleanly when the rib is removed by hand
   - The hook surface remains intact (no surface marring or pocking)

3. **Support material (if different from part material):**
   - If using dual-nozzle with water-soluble support (PVA, BVOH), supports are removed by water dissolution
   - If using single-nozzle, supports are the same material as the part (Nylon) and must be removed mechanically
   - Break-away rib strategy is most reliable for mechanical removal

4. **Internal snap anchors on the inner surfaces:**
   - Internal snap points (for mounting bags, displays, electronics) may also require support geometry
   - Approach: Design internal snaps with the same break-away rib strategy
   - Ribs are hidden from view (internal surfaces) so aesthetic impact is zero

### Layer Orientation and Anisotropy

**FDM parts are weakest between layers (Z-direction).** With snap beams oriented in the XY-plane:

- **Flex direction (lateral):** Parallel to build plate; strength is ~90% of theoretical maximum
- **Stress concentration at base:** Mitigated by generous fillet (0.8 mm) and taper (1.2 mm to 0.8 mm)
- **Creep resistance:** Oriented in XY-plane, creep is minimal over the design lifetime

**Conclusion:** Recommended print orientation is achievable and meets all structural requirements.

### Print Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Material** | Nylon PA12 | Food-safe, excellent fatigue resistance, moisture-stable |
| **Nozzle temperature** | 250–260°C | Per Bambu H2C Nylon profile |
| **Bed temperature** | 80–100°C | Prevents warping on large parts; per material datasheet |
| **Print speed** | 80–120 mm/s | Conservative speed for dimensional accuracy |
| **Layer height** | 0.2 mm | Balance between surface finish and print time |
| **Infill density** | 15–20% | Lightweight structure; snaps and walls provide rigidity |
| **Infill pattern** | Honeycomb or grid | Distributes stress evenly; avoids directional bias |
| **Supports** | Break-away ribs (0.3 × 0.8 mm) | Intentional support geometry per FDM constraints |
| **Bed adhesion** | Textured sheet + adhesive | Bambu H2C standard; PEI sheet recommended |

### Tolerance Calibration

Once the Bambu H2C is calibrated for Nylon:

1. **Snap undercut depth:** Measure actual hook engagement after first print; adjust undercut depth ±0.1–0.2 mm if needed
2. **Mating surface flatness:** Check that top and bottom halves are perfectly flat at the seam plane; adjust nozzle offset if necessary
3. **Gap uniformity:** Measure gap at 10 points around perimeter; target <0.2 mm variation; adjust bed leveling or slicer settings if variation exceeds tolerance

---

## Summary Table: Concrete Architecture Specification

| Aspect | Specification |
|--------|---|
| **Enclosure dimensions** | 220 × 300 × 400 mm (W × D × H) |
| **Split strategy** | Horizontal seam at 200 mm height (monolithic halves) |
| **Piece count** | 2 (top half, bottom half) |
| **Join type** | Snap-fit permanent closure (cantilever beams) |
| **Snap points** | 10 total; ~100 mm spacing; equilateral triangle or bullnose hook |
| **Snap geometry** | 20 mm beam length, 1.2 mm base, 2.5 mm overhang, 0.8 mm fillet |
| **Assembly force** | 40–50 N per snap; 400–500 N total |
| **Seam gap** | 1.2 mm ±0.1–0.2 mm (uniform along entire perimeter) |
| **Seam recess** | 0.5–1.0 mm inset from outer surface (continuous around perimeter) |
| **Edge fillets** | 2–3 mm on external edges; 3–4 mm at seam corners |
| **Material** | Nylon PA12 (primary); PETG (fallback) |
| **Surface finish** | Matte black 20–40% gloss (paint or powder coat) |
| **Service access** | Pump cartridge dock (snap-fitted, hand-removable via squeeze mechanism) |
| **Print orientation** | Seam face horizontal (XY-plane); height vertical (Z-axis) |
| **Support strategy** | Break-away ribs (0.3 × 0.8 mm, 0.2 mm interface gap) |
| **Print bed fit** | Both halves fit within Bambu H2C 325 × 320 × 320 mm envelope |
| **Internal components** | Snap-mount directly to enclosure inner surfaces (no secondary snap frames) |

---

## Design Consistency Verification

### Consistency with Synthesis

This architecture embodies the synthesis execution plan (synthesis.md) exactly:
- ✓ Horizontal seam at 200 mm height
- ✓ 10 snap points ~100 mm spacing
- ✓ 1.2 mm gap ±0.1–0.2 mm tolerance
- ✓ Snap-fit permanent closure with equilateral triangle/bullnose hooks
- ✓ Matte black finish with 2–3 mm fillets
- ✓ 0.5–1.0 mm recess channel continuous around perimeter
- ✓ All interior components snap-mount to the two halves

### Consistency with Vision

This architecture delivers the user experience specified in vision.md:
- ✓ Snap-fit permanent closure (user never opens enclosure)
- ✓ Unified, rigid product (no assembly artifacts, no visible fasteners)
- ✓ Pump cartridge removable via simple squeeze mechanism
- ✓ All other components permanent fixtures
- ✓ Premium consumer appliance feel

### Consistency with Design Patterns Research

This architecture applies all key findings from design-patterns.md:
- ✓ Gap consistency prioritized over absolute width
- ✓ Matte black finish minimizes seam visibility
- ✓ Seam placed at optical balance point (200 mm = 50% of 400 mm height)
- ✓ 2–3 mm fillets on all external edges
- ✓ Snap-fit joinery with tactile feedback
- ✓ Seam treated as intentional design line, not hidden

### Consistency with Snap-Fit Research

This architecture follows all snap-fit design best practices from snap-fit-design.md:
- ✓ Cantilever beam hooks (most reliable for permanent closure)
- ✓ 10 snap points (100 mm spacing for large enclosure)
- ✓ 40–50 N per snap; 400–500 N total assembly force
- ✓ Equilateral triangle hook profile (smooth stress distribution)
- ✓ 0.8 mm fillet radius at beam base (stress concentration mitigation)
- ✓ Snap arms oriented in XY-plane (parallel to build plate for maximum strength)
- ✓ Break-away support ribs (0.3 × 0.8 mm, 0.2 mm interface gap)

### Consistency with Manufacturing Constraints

This architecture respects all FDM and Bambu H2C constraints from requirements.md:
- ✓ Both halves fit within 325 × 320 × 320 mm build envelope
- ✓ Snap beams print parallel to XY-plane (50%+ strength preservation)
- ✓ Minimum wall thickness 1.2 mm on snap bases (≥3 perimeters)
- ✓ Intentional support geometry with 0.2 mm interface gaps (clean removal)
- ✓ No unsupported faces <45° from horizontal (all overhangs intentionally supported)
- ✓ Dimensional tolerances ±0.1–0.2 mm achievable on Bambu H2C

---

## No Conflicts Identified

This architecture was reviewed against all foundational constraints (vision, requirements, synthesis, design patterns, snap-fit design, FDM manufacturing) and passes all checks. No architectural conflicts were found.

**Next steps:** CAD implementation using this concrete architecture as the design specification. Follow with test prints (single snap test, half-assembly test, full assembly validation).

---

## Document Version

**Status:** Complete and ready for CAD implementation
**Date:** 2026-03-29
**Author:** Architecture Phase (Enclosure)
**Review:** Verified against synthesis, vision, and all research documents
