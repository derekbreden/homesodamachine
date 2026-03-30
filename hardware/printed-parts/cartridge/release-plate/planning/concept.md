# Release Plate — Conceptual Architecture

**Step:** 4a — Conceptual Architecture
**Input:** synthesis.md (execution plan), design-patterns.md, collet-release-force.md, guide-geometry.md, John Guest PP0408W geometry, Kamoer KPHM400 geometry
**Output:** Physical form, piece count, splits, joins, seams, surfaces, manufacturing approach

---

## 1. Piece Count and Split Strategy

The release plate is **one printed PETG part**. No splits, no assemblies, no bonded sub-components.

This choice is correct and not a simplification — it is the correct answer to every constraint simultaneously:

**Why integral guide pins (not separate metal pins or a separate pin plate):**

The synthesis settled this question. Integral PETG pins work structurally — the 5mm diameter pin with 28mm bore engagement carries the bending load from the collet pattern offset with a factor-of-safety of approximately 3 at the governing realistic load case (150 N·mm per pin). Separate metal pins would require either a press-fit into the plate (adding assembly steps, tolerance stack, and a potential failure interface during squeeze cycling) or a separate pin plate (adding a piece, a joint, and a seam that serves no UX function). Neither adds reliability. Both add assembly complexity and potential for misalignment that the integral approach eliminates.

Metal pins would be stronger in bending, but the loading does not demand it. The synthesis confirmed PETG is adequate. Metal pins also create a dissimilar-material sliding interface (metal pin in PETG bore) that is actually worse for long-term sliding than PETG-on-PETG: the harder metal abrades the softer bore, eventually loosening the fit. PETG-on-PETG wears symmetrically and maintains close clearance over the service life.

**Why not split the plate into a structural body and a cosmetic user-facing face:**

The user-facing face of the plate is the pull surface — it is a functional surface, not a cosmetic cap. Any joint between a cosmetic face and a structural body would run directly through the primary load path (finger pull force → plate body → collet lips). A joint there is a crack initiation site and a delamination risk under repeated squeeze cycling. The pull surface must be the plate body itself.

**Why not a two-plate sandwich (a thin face plate captured in the body, allowing surface material substitution):**

The inset geometry accomplishes the design goal without this complexity. The pull surface is the plate user-facing face at rest position, naturally inset 10mm below the cartridge body front face. The surface quality of PETG printed flat (XY plane) is excellent on the top face — the layer lines run parallel to the face, producing a smooth surface that is appropriate as a finger contact surface with minimal post-processing. A cosmetic sandwich would be a solution to a problem that does not exist in this configuration.

**Conclusion:** 1 printed part. Integral pins. No joints within the release plate itself.

---

## 2. Join Methods

The release plate connects to its context through three interfaces: the guide pin bores in the cartridge body, the return springs, and the user's hand. The plate itself has no fasteners and no permanent bonds — it is a sliding captive part assembled by insertion.

### 2a. Guide pins into cartridge body bores

The pins slide in bores in the cartridge body — a PETG-on-PETG running fit with 0.15mm radial clearance per side (5.0mm designed pin OD, 5.5mm designed bore ID). This is a sliding captive joint: the plate is retained in the assembled cartridge by the fact that the pins cannot exit the bores without disassembling the cartridge body. The pins have no end-stop feature of their own — they are retained by the cartridge body front wall (which caps the bores) and by the collet fittings behind (which the plate rests against at the inner bore lips at rest). The plate cannot escape the assembled cartridge in any direction without destroying structure.

**What the cartridge body must provide:**
- Two cylindrical bores, 5.5mm designed diameter, ≥30mm deep, at diagonal corner positions matching the pin positions on the plate.
- Bore walls must have ≥1.2mm of PETG surrounding the bore diameter (structural wall requirement per requirements.md).
- Bore entry chamfer: 0.5mm × 45° at the rear-facing entry face to guide pin insertion during assembly and prevent bore edge chipping.
- Bore axes must be parallel to the cartridge's front-to-back translation axis to within the tolerance achievable by printing both the plate and the cartridge body in the same orientation (XY-plane plate face, XY-plane cartridge body base). Since both parts print with their flat faces on the build plate, pin-to-bore alignment is set by the printer's XY accuracy (±0.2mm positional), which is adequate.

### 2b. Return springs

The springs are not attached to the plate. Each spring sits in a pocket in the cartridge body rear wall (8mm diameter, 10mm deep, concentric with or immediately adjacent to each guide pin bore). The plate's fitting-facing face closes each pocket when the plate is in its resting position. On squeeze, the plate face compresses the spring; on release, the spring pushes the plate forward to rest. No clip, no retention, no adhesive. The spring is captured by the pocket depth and the plate face.

**What the cartridge body must provide:**
- Two spring pockets, 8mm diameter, 10mm deep, positioned so the spring bears against the plate user-facing face in the zone outside the guide pin boss base circle. The pocket center may be concentric with the bore or offset by a few mm — either works as long as the spring bears flat against the plate face.
- The pocket diameter (8mm) must not overlap the guide pin bore (5.5mm). If concentric, the spring runs around the outside of the pin (spring OD 7–8mm wraps the 5.5mm bore). This is the cleanest arrangement: the spring is automatically centered on the pin and the pin prevents the spring from collapsing sideways.

**Spring-to-plate interface:** Contact only — flat plate user-facing face against the spring's end coil. No pocket or boss on the plate itself. Keeping the plate user-facing face flat simplifies printing and assembly. The spring sits in the cartridge body pocket; the plate does not need to capture or guide the spring.

### 2c. Pull surface load transfer

The user-facing face of the plate (Y=5) is the pull surface. The user's finger pads contact this face directly and pull it forward. The force path is: finger contact → plate user-facing face surface layer → plate body in tension along the Z-axis (print direction) → stepped bore inner lips → collet annular faces. This is a through-thickness tensile load on the plate.

The plate user-facing face does not need any reinforcement feature to transfer this load because the load is distributed across the full face area (the user's palm-up fingers contact a broad band, not a point). The face is the plate's front perimeter wall plus the material between the bores. At the minimum section — the material between adjacent stepped bore outer diameters (14.4mm edge-to-edge clearance between the horizontal bore pair, as derived in synthesis Section 5) — there is ample cross-sectional area.

The 3mm radius on the rearward pull edge (the edge the finger pads bear against during the pull stroke) is a surface geometry feature on the plate itself. It is not a separate component — it is simply the rearward perimeter edge of the plate user-facing face, radiused. This radius is printed as part of the plate and requires no special treatment in the print orientation (the edge faces upward on the build plate and prints as a series of stepped layers that closely approximate the radius at 0.1–0.2mm layer heights).

---

## 3. Seam Placement

There is one seam on the release plate: the gap between the plate's perimeter and the surrounding pocket wall of the cartridge body. This is the only visible evidence that the plate is a separate moving part.

**Gap geometry:** 0.6–1.0mm uniform all around the plate perimeter. This is the designed value from the synthesis, derived from the design-patterns research (DeWalt 20V and Makita 18V references). Below 0.5mm is not reliably achievable with a 0.4mm nozzle at this scale. Above 1.0mm begins to read as a manufacturing gap rather than a designed parting line.

**Why this seam reads as intentional:**

The gap's appearance is determined by two things — its uniformity and its edge geometry. Uniformity comes from designing the plate outer perimeter to be smaller than the pocket by exactly the gap width on all sides, and printing both parts flat to achieve the best XY dimensional accuracy. Edge geometry is the key design decision.

**Edge treatment — sharp on both sides:**

Both the plate perimeter edge and the pocket wall inner edge are sharp (no fillet, no chamfer). This is the correct choice for a designed parting line. A sharp edge on a gap reads as intentional precision — the same visual language as the gap between a laptop lid and its body, or the gap between a phone's glass face and its aluminum frame. A chamfered or filleted edge on a gap reads as "the designer tried to hide something" or "this was sanded to fit."

Sharp edges are achievable at this scale in FDM if the plate is printed flat: the perimeter walls print vertically, and the top layer (the plate's user-facing face plane) creates a crisp edge at the perimeter. The pocket walls in the cartridge body print the same way.

**Seam position relative to depth:** The gap runs around the perimeter of the plate in the plane of the cartridge body front face. Because the plate user-facing face is inset 10mm below the cartridge body face, the user sees the seam only when looking at the cartridge from below or at an angle — from the natural viewing angle (looking at the front face of the cartridge), the seam is in the shadow of the 10mm deep pocket. This means the seam is effectively invisible during normal use. The user sees the pocket opening (a clean rectangular recess) and the plate face at the bottom of it.

**What makes the pocket opening read as a product feature, not a gap:**

The pocket opening is a rectangular inset that fills most of the cartridge front face width. Its proportions and depth (10mm) make it read as a designed grip zone — the same language as the Makita 18V panel that fills the battery face. The pocket is not a hole with a visible plate rattling inside it; at 0.6–1.0mm gap, the plate and pocket wall look monolithic when the cartridge is not being actively squeezed. The gap is only perceptible on close inspection.

**Cartridge body pocket geometry required for this seam:**
- Pocket inner dimensions: plate outer dimensions + 0.6–1.0mm on each side (uniform)
- Pocket wall faces: flat and parallel to the plate perimeter faces
- Pocket depth: 10mm, measured from the cartridge body front face to the plate user-facing face at rest
- Pocket corners: matching the plate perimeter corner treatment (see Section 5)

---

## 4. User-Facing Surface Composition

The user sees two surfaces on the cartridge front face: the surrounding cartridge body face (the palm surface) and the inset plate face (the pull surface). The plate is responsible for the pull surface and the seam between them.

**What is on the plate's user-facing face:**

The pull surface is the entire user-facing face of the plate (Y=5). It is a flat PETG surface approximately 75mm wide × 65mm tall (nominal, final dimensions from fitting layout), inset 10mm below the surrounding cartridge body face. The surface is smooth or very lightly textured — the synthesis specifies smooth or very light texture because the finger pads must slide slightly as they flex during the pull stroke, and a heavily textured surface creates friction that fights the natural curl of the fingers.

In practice, "smooth or very lightly textured" means: print top surface with default FDM finish (layer lines visible at close inspection but not tactilely prominent). No embossed pattern. No sanding required. The FDM top-face finish at 0.1–0.2mm layer height is appropriate as-printed.

**Four through-holes visible on the user-facing face:**

The four tube clearance holes (6.5mm diameter) are visible on the user-facing face. Their arrangement (62mm horizontal × 30mm vertical center spacing, per synthesis Section 5) is symmetrical and geometrically confident. These holes should not be treated as features to hide — they are small, clean, and read as functional precision. Their presence communicates that something goes through this surface (the tubes), which is accurate and appropriate. They should not be chamfered on the user-facing face: a sharp entry edge reads as precision. A chamfer reads as decorative and draws attention.

**The rearward pull edge:**

This is the edge at the perimeter of the plate user-facing face that the finger pads bear against when pulling. It is the most important tactile feature on the plate. The 3mm radius runs continuously around the plate perimeter at this edge. This radius is not visible from the front (it faces rearward, toward the inside of the pocket) but is deeply felt — the difference between a sharp edge pressing into the finger pad during the squeeze and a smooth curved surface distributing that load. It must be correctly oriented to the print: this edge is a convex radius on the perimeter of the plate, which in the flat print orientation lies at the bottom of the plate (the build plate side). See Section 7 for the printability analysis of this edge.

**What the plate does NOT have on its user-facing face:**

- No label, text, or embossed graphic (the cartridge body may carry labels, but the pull surface does not)
- No ridge, rib, or guide feature (the pocket geometry and finger ergonomics do this without help)
- No indicator line or witness mark for the seam (the seam is designed to be invisible, not marked)

**Visual hierarchy of the cartridge front face (for context, though the palm surface is the cartridge body's responsibility):**

1. The surrounding cartridge body face — the dominant element, flat matte textured surface, receives the palm
2. The pocket opening — the designed recess, clean rectangular inset
3. The plate pull surface — the floor of the pocket, smooth, with the four clean tube holes
4. The seam — recedes into shadow, barely visible

The visual hierarchy moves from dominant (body face) to recessive (plate face) as depth increases. The mechanism disappears into the product.

---

## 5. Design Language

**Material and surface language:**

The plate is PETG, printed flat. PETG produces a surface with a slight natural sheen — neither matte nor glossy, closer to a satin finish on the top (Z) face. This is appropriate for the pull surface: not slippery-looking, not rough-looking, just neutral. The cartridge body palm surface carries the matte embossed texture (the visual contrast that identifies the grip zone), so the pull surface's satin neutrality is the correct complement.

**Corner treatment:**

The plate perimeter corners are rounded, with a radius of 2–3mm at the XY plane corners of the plate (the corners visible from the front). This radius matches the pocket corner radius in the cartridge body, keeping the seam gap consistent at the corners and preventing stress concentration at the corner edges. It also prevents the plate from looking like a plain rectangle dropped into a hole — rounded corners read as a designed part, not a cut blank.

**The 3mm pull edge radius:**

This is the primary tactile design feature of the plate. At 3mm radius, it is large enough to distribute finger pad load comfortably (the cassette tape window reference from design-patterns.md: minimum 2mm, ideally 3–4mm) and large enough to be perceptible as a designed surface rather than a manufacturing break-edge. It is not visible from the front — it faces rearward into the pocket interior — but it is felt on every cartridge removal. This is the difference between a mechanism and a product.

**The seam as design language:**

The 0.6–1.0mm gap with sharp edges on both sides is the same visual language as high-quality injection-molded consumer electronics: laptop lids, phone bodies, premium remote controls. It says "these two surfaces were designed to meet here" rather than "this thing moves." This language is achievable in FDM because both parts are printed flat and the critical dimensions are in the XY plane where FDM is most accurate.

**What unifies the plate with the cartridge body:**

Both parts are PETG. Both are printed flat. Both use the same corner treatment language (2–3mm radii on all exterior perimeter corners). Both have sharp edges at the seam. The plate's pull surface has a slightly different tactile quality (smooth/satin vs. matte embossed) — this is intentional and is the primary affordance: the user's fingers feel the transition from rough (body) to smooth (plate) and know they are on the moving surface.

**No branding or graphics on the release plate.** The plate is a mechanism component that happens to have a user-facing surface. Any branding or identifying text lives on the cartridge body, not the plate.

---

## 6. Service Access Strategy

The release plate requires no service-access features.

The user's only service interaction with the cartridge is removal and replacement of the whole cartridge unit. There is no user-accessible sub-service of the release plate mechanism:

- The plate itself does not wear out in any normal service scenario. The collet contact stress at the inner lip faces is 0.41 MPa against PETG compressive yield of 14 MPa — a 34× safety factor. The sliding surfaces (pins in bores) have generous clearance and low load; surface wear over dozens of cartridge swaps is negligible.
- The return springs are commodity compression springs (302 SS music wire). They are not expected to fail within the service life of the cartridge. If they did fail, the cartridge would be replaced as a unit — the springs are captive inside the assembled cartridge and are not user-replaceable without disassembling the cartridge body.
- The fittings are pressed into the cartridge body rear wall and are also not user-replaceable.
- The plate is captive inside the assembled cartridge. The user never sees it, touches it, or needs to service it.

**There is no scenario in the vision where the user opens the cartridge to access internal components.** The cartridge is replaced as a unit. Service-access features on the release plate would add complexity and create visible evidence of internals — both counter to the product's design values.

The plate therefore has no access holes, no retention tabs the user can release, no service markings, and no deliberately-weakened disassembly features.

---

## 7. Manufacturing Constraints

### Print orientation

**The release plate prints flat — fitting-facing face down on the build plate (Z face down).**

This is the orientation with the plate's fitting-facing face (Y=0, tube exit side) flat on the build plate. The guide pins extend upward from the plate user-facing face — since the fitting-facing face is down, the user-facing face is up, and the pins point straight up (positive Z from build plate).

This orientation places the most critical dimensional features in the XY plane:
- The stepped bore diameters (15.6mm outer, 10.07mm inner, 6.5mm through) are all circular features in the XY plane — they print with the full XY accuracy of the printer, not as extruded circles in the Z direction.
- The 62mm × 30mm center-to-center spacing of the bores is an XY dimension — accurate.
- The guide pin diameters (5.0mm) are in the XY plane at the base but extrude in Z — pins printed as vertical cylinders are the standard approach for maximum pin strength (layers perpendicular to bending load = bending loads in-plane, which is the strong direction).

**Fitting-facing face down (preferred) vs. user-facing face down:**

Fitting-facing face down places the tube-exit surface on the build plate. The build plate contact surface will have the best dimensional accuracy (no elephant's foot on interior features, though a 0.3mm × 45° chamfer on the plate perimeter bottom edge is required per requirements.md to prevent elephant's foot flare on the seam-facing edge). The FDM first-layer compression gives this face an extremely smooth surface finish.

User-facing face down is the alternative. It places the stepped bore features on the build plate side, which is also the side with the most accurate Z-depth control. However, this orientation has one significant problem: the guide pins would be on the bottom (build plate side) rather than on the top, and the pins would need to print with the bore entry faces (the ends of 30mm cylinders) suspended above the build plate — these would have clean surfaces since they're on the top, but the pin bodies print fine either way. The actual problem with user-facing-face-down is that the three-step bore geometry has unsupported overhangs on the fitting-facing side (the bore inner lips and outer counterbore floors face upward away from the build plate, which means they print as bridged features). Fitting-facing-face-down avoids this: the bores open upward from the user-facing side, and the bore floors print on supported surfaces.

**Fitting-facing face down is the confirmed orientation.**

### Overhang analysis — integral guide pins (the critical case)

The synthesis flags this as the key constraint to analyze: the pins extend from the plate user-facing face (now the top of the printed part in build orientation), meaning the pins point straight up from the build plate. This is exactly the correct orientation for printed cylinders — vertical cylinders print without any overhang concern. The pin tip (top surface) is a flat circle that prints as a standard top-layer feature. The pin body is a continuous vertical cylinder. No overhangs anywhere on the pin geometry.

**This concern from the synthesis resolves cleanly: pins pointing up in the print orientation have no overhang issues.**

The synthesis noted concern about "pins on the bottom (build plate side)" — this would apply if the user-facing face were on the build plate. In fitting-face-down orientation, the pins are on the top, and the concern disappears entirely. No resolution needed.

### Overhang analysis — stepped bores

The four stepped bores are concentric circular features. The counterbore (Zone 1) opens at the user-facing face (Y=5, top of print) and the through-hole (Zone 3) exits at the fitting-facing face (Y=0, build plate). In fitting-face-down orientation:

- **Zone 3 (tube clearance through-hole, 6.5mm):** Exits at the fitting-facing face (build plate side). A simple through-hole in the XY plane — prints without overhang issues as holes in layers as they stack.

- **Zone 2 (inner lip bore, 10.07mm, 2.0mm deep):** A bore section above Zone 3, continuing upward. The floor of Zone 2 (the step between Zone 3 and Zone 2) is a flat horizontal surface supported from below. No overhang.

- **Zone 1 (outer bore, 15.6mm, 1.3–1.5mm deep):** The widest counterbore, opening at the user-facing face (top of print). The floor of Zone 1 (the step between Zone 2 and Zone 1) is a flat horizontal surface supported from below. No overhang.

All three bore zones print without overhang concern in fitting-face-down orientation. The step transitions between zones are flat horizontal surfaces facing downward (toward the build plate) — fully supported.

### Overhang analysis — pull edge radius

The 3mm radius on the pull edge runs around the plate's perimeter at the fitting-facing face edge (Y=0). In fitting-face-down orientation, this radius is at the very bottom of the part (the fitting-facing face is down), running along the perimeter of the first layers. This edge radius, being on the bottom perimeter, is essentially in the first 3mm of print height and is supported by the build plate contact. No overhang.

### Wall thickness check

Minimum structural wall requirements per requirements.md: 1.2mm for load-bearing walls (3 perimeters).

Critical sections:
- **Between outer bore (15.6mm) and plate perimeter:** With a 75mm wide × 65mm tall plate and bores centered on the fitting pattern (±31mm horizontal, ±15mm vertical from plate center), the outer bore edge at extreme position is at ~31mm + 7.8mm = 38.8mm from plate center, giving ~37.5mm − 38.8mm = ... checking differently: plate half-width is ~37.5mm, bore edge (15.6mm/2 = 7.8mm radius) at 31mm from center = 31 + 7.8 = 38.8mm from center. Plate perimeter at 37.5mm from center. This shows the outer bore edge at a horizontal extreme position would be 38.8mm from center vs. a 37.5mm half-width — the bore would break through the plate edge. The plate width must be increased to at least 2×(31 + 7.8 + 1.2) = 2×40mm = 80mm to maintain 1.2mm wall outside the outermost bore. The synthesis states 75mm wide as nominal; this check shows **80mm wide is the correct minimum plate width** to maintain structural wall outside the 31mm-offset outer bores. This is a dimensional correction to carry forward into the specification step.
- **Between adjacent bores (horizontal pair, 62mm c-c):** 62mm − 15.6mm = 46.4mm edge-to-edge. 46.4mm/2 = 23.2mm of material between bore edges. No concern.
- **Between adjacent bores (vertical pair, 30mm c-c):** 30mm − 15.6mm = 14.4mm edge-to-edge. 7.2mm of material per side between bore edges. No concern.
- **Between guide pin boss (5.0mm OD) and nearest outer bore edge:** The synthesis specifies ≥1.2mm of plate material between pin base circle and nearest bore feature. This must be verified in the final layout when pin positions are finalized relative to bore positions. The diagonal pin placement (outside the 62mm × 30mm bore rectangle) is designed to maintain this clearance; final layout must confirm.
- **Inner lip wall (10.07mm bore to 15.6mm bore transition):** Wall width = (15.6 − 10.07)/2 = 2.77mm per side. This is the inner lip that contacts the collet annular face. 2.77mm is well above the 1.2mm minimum. No concern.

### Layer orientation vs. load direction

In fitting-face-down orientation:
- **Squeeze load (Z-axis, through-thickness):** The user pulls the plate forward (in the direction the plate travels — let's call this the X direction, front-to-back of the cartridge). The plate translates in X. The collet contact forces act in X. The pins resist bending in X. Layer lines are horizontal (XY planes stacking in Z). The plate's resistance to translation in X is in-plane (XY), which is the strong direction. The pin bending load is also resisted by in-plane material (layers stack along the pin length in the Z-print-direction, which is in-plane with the print layers). This is the correct orientation.
- **Through-thickness tensile (Z print direction, pull):** The finger pull force is transmitted from the user-facing face surface through the plate thickness in the Z print direction to the inner lip faces on the fitting side. This is Z-axis tension — the weakest direction for FDM. However, at the 5mm plate thickness, the shear area between layers is enormous: the full plate width × height cross-section area minus the bore areas (approximately 75mm × 65mm − 4×bore areas ≈ 4,000 mm² cross-section). At 60N pull force, the through-thickness shear stress is 0.015 MPa — negligibly small. The inter-layer weakness in Z is not a concern at this plate thickness and load level.

### Material selection

PETG is confirmed per the synthesis. PETG is appropriate for:
- Food-adjacent application (PETG has better chemical resistance than PLA, acceptable for non-contact proximity to food/beverage)
- Collet sliding interface (PETG-on-acetal sliding is acceptable tribologically)
- PETG-on-PETG pin/bore sliding fit (confirmed in guide-geometry.md)
- FDM printability at this geometry (no warping concerns at this scale, good bridging characteristics)

### Print settings notes for specification step

- Layer height: 0.1–0.2mm recommended for bore accuracy and pull edge radius resolution
- Perimeters: 3 minimum on all walls (1.2mm structural minimum = 3 perimeters at 0.4mm nozzle)
- Infill: 40%+ rectilinear or gyroid for uniform compressive strength across the plate body
- Support: none required in front-face-down orientation (all features print without overhang)
- First layer: standard; the 0.3mm × 45° chamfer on the perimeter bottom edge prevents elephant's foot from affecting the seam-facing edge

---

## Summary

**Piece count:** 1 printed PETG part.

**Print orientation:** Fitting-facing face down (XY plane on build plate). Guide pins point upward (Z direction). Stepped bore counterbores open upward at the user-facing face, with step transitions fully supported.

**Key design decisions:**

1. Integral guide pins are correct — the structural margin is adequate, PETG-on-PETG sliding is appropriate for this service life, and integral construction eliminates assembly tolerance stack between the pin position and the plate.

2. Fitting-facing face down resolves the synthesis's overhang concern entirely — pins pointing up have no overhang issues. This is the orientation.

3. The pull surface (plate user-facing face) and the plate body are one part — no joint in the load path.

4. The seam gap (0.6–1.0mm, sharp edges both sides) is the only evidence of the plate being a separate moving part, and it reads as a designed parting line when the pocket proportions are correct.

5. The plate requires no service-access features.

6. **Dimensional correction:** The plate minimum width is 80mm (not 75mm as in the synthesis nominal). At 75mm, the outer bore edges at the extreme horizontal positions break through the plate perimeter. 80mm maintains the required 1.2mm structural wall outside the outermost bores.

**What the cartridge body must provide (interface requirements):**

| Feature | Dimension | Notes |
|---|---|---|
| Guide pin bores | 5.5mm diameter, ≥30mm deep | 0.5mm over pin for FDM sliding clearance |
| Bore entry chamfers | 0.5mm × 45° | Assembly guidance, edge protection |
| Spring pockets | 8mm diameter, 10mm deep | Concentric with pin bores; spring wraps pin |
| Pocket (grip inset) inner dimensions | Plate outer + 0.6–1.0mm on each side | Uniform gap all around |
| Pocket depth | 10mm | From body front face to plate user-facing face at rest |
| Structural wall around pin bores | ≥1.2mm | Per requirements.md |

---

## Diagram — Plate Surfaces and Features

```
FRONT VIEW (user-facing surface, as printed — fitting-facing face down)

┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  ←—————————— ~80mm wide ————————————————————————————→         │   │
│   │                                                                 │   │
│   │          ○                               ○                     │   │
│   │       (Ø15.6 outer)              (Ø15.6 outer)                 │   │
│   │       (Ø10.1 inner lip)          (Ø10.1 inner lip)             │   │
│   │       (Ø6.5 through)             (Ø6.5 through)                │   │
│   │          ← 62mm c-c →                                          │   │
│   │                                                                 │   │
│   │          ○                               ○                     │   │
│   │       (Ø15.6 outer)              (Ø15.6 outer)                 │   │
│   │       (Ø10.1 inner lip)          (Ø10.1 inner lip)             │   │
│   │       (Ø6.5 through)             (Ø6.5 through)                │   │
│   │              ←— 30mm c-c (vertical) ——→                        │   │
│   │                                                                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│   ↑ seam gap 0.6–1.0mm, sharp edges both sides                         │
│                                                                          │
│   Surrounding = cartridge body face (palm surface, not part of plate)   │
└──────────────────────────────────────────────────────────────────────────┘

SIDE / CROSS-SECTION VIEW (looking from the side, plate only)

  Fitting-facing face (Y=0,          User-facing face (Y=5,
  tube exit, build plate side)        pull surface, stepped bores here)
       ↓                                      ↓
  ─────┬──────────────────────────────────────┬──────────
       │                                      │  ──────── Zone 1 outer bore depth: 1.3–1.5mm
       │◄──── 5mm plate thickness ───────────►│  ──────── Zone 2 inner lip depth: 2.0mm (cumulative 3.3–3.5mm)
       │                                      │  ──────── Zone 3 through-hole to fitting-facing face
  ─────┴──────────────────────────────────────┴──────────
                                              │
                                              │  ←── Guide pin (5mm Ø, 30mm long)
                                              │      extends rearward into cartridge body bore
                                              ●
                                         (one of 2 pins,
                                          diagonal corners)

  ←— 3mm radius here (pull edge, perimeter of fitting-facing face Y=0) ——


PRINT ORIENTATION (build plate view)

  BUILD PLATE
  ───────────────────────────────────────────
  [  FITTING-FACING FACE of plate — down on build plate  ]
  [  Tube through-holes (Zone 3) exit here               ]
  [  Perimeter chamfer 0.3mm × 45° on this edge ]
  ───────────────────────────────────────────
       ↑ Z direction (build direction)
       │
  [  Plate body 5mm thick                       ]
       │
  [  USER-FACING FACE — top of print             ]
  [  2 guide pins extend upward (Z direction)   ]
  [  Pin 1: top-left corner                     ]
  [  Pin 2: bottom-right corner                 ]
  [  30mm tall cylinders, 5mm Ø                 ]
```
