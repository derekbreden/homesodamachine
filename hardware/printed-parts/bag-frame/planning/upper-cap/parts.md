# Upper Cap — Parts Specification

**Version:** 1.0
**Date:** 2026-03-29
**Dimensional source:** spatial-resolution.md (sole authoritative source for all coordinates and dimensions)
**FDM constraint source:** hardware/requirements.md
**Assembly authority:** concept.md

---

## 1. Part Identification

| Field | Value |
|-------|-------|
| Part name | Upper Cap |
| Version | 1.0 |
| Material | PETG |
| Instances | 2 (identical; same file, print twice) |
| Print orientation | Bag-contact face down — Y=0 flat on build plate; rib grid builds upward; snap arms extend horizontally outward in X |
| Print envelope (X × Y × Z) | 244mm × 6.5mm × 287mm (including arm extensions) |
| Cap body footprint | 204mm (X) × 287mm (Z) |
| Build plate footprint | 244mm (X including arms) × 287mm (Z) |
| Print height | 6.5mm (Y) |
| Fits single-nozzle volume | Yes — 244mm ≤ 325mm (X); 287mm ≤ 320mm (Z, tightest axis, 33mm margin); 6.5mm ≤ 320mm (Y) |

**Print orientation rationale:** The bag-contact face (Y=0) is printed flat on the build plate. This provides the best surface quality on the face that contacts the bag film, preventing stress concentrations on the film seams (concept.md §4). The rib grid builds upward as vertical walls from Y=1.5mm — no overhang. Snap arms extend horizontally in X from the cap body long edges; they flex in the X direction (parallel to the build plate), satisfying requirements.md layer-strength constraint for snap-fit arms. The hook undercuts at Y=0 on each arm require the designed frangible bridge geometry per requirements.md §FDM.

---

## 2. Coordinate System

**Origin definition:**

| Axis | Zero point | Positive direction |
|------|------------|--------------------|
| X | Left edge of cap body (aligns with left cradle lip outer face when assembled; cap frame X=0 = cradle frame X=−4mm) | Right — toward right cap body edge and right arm root |
| Y | Bag-contact face (smooth; on build plate during printing) | Away from bag — toward rib-grid face, outboard from bag |
| Z | Cap-end face (the end nearest the Platypus bag cap; the back-bottom of the enclosure in installed orientation) | Toward fold end — toward enclosure front wall in installed orientation |

**Origin location:** Intersection of the bag-contact face (Y=0), the left body edge (X=0), and the cap-end face (Z=0). This is the bottom-left corner of the cap body when looking at the bag-contact face.

**Part envelope:**

| Axis | Minimum | Maximum | Span |
|------|---------|---------|------|
| X | −20mm (left arm tip) | 224mm (right arm tip) | 244mm total |
| X (body only) | 0mm | 204mm | 204mm |
| Y | 0mm (bag-contact face) | 6.5mm (rib tip) | 6.5mm |
| Z | 0mm (cap-end face) | 287mm (fold-end face) | 287mm |

**Coordinate frame offset (cap frame → cradle frame):**

```
X_cradle = X_cap − 4mm
Y_cradle = Y_cap + 3.7mm   (assembled; cap Y=0 is at cradle Y=3.7mm when hooks seated)
Z_cradle = Z_cap            (same physical axis; Z=0 at cap end for both)
```

---

## 3. Mechanism Narrative (Rubric A)

The upper cap is the top half of a two-part bag-containment sandwich. It presses against the top face of the Platypus 2L collapsible bag, constraining the bag's cross-sectional profile to the designed 27mm lens depth while the bag is held at 35° from horizontal.

**What the cap does mechanically:** The bag, unconstrained, expands to approximately 40mm midsection thickness under gravity at 35°. The cap holds it to 25–30mm. This is not a clamp — the cap applies no clamping force independent of the bag's internal pressure. The bag's hydraulic pressure (up to 2L liquid at 35°) presses outward against both the cradle bowl and the cap face simultaneously. The cap's structural function is to be rigid enough not to bow outward under that pressure. The rib grid (Feature 2) provides the stiffness. The snap arms (Feature 3) lock the cap to the cradle lips so the cap cannot lift as pressure increases.

**What the cap does not do:** The cap has no user interface. It has no tool access provisions. It is not designed to be removed. There is no opening in the cap face — no tube fittings, no sensors, no access holes. It is a flat rigid panel with stiffening ribs on one side and four snap arms on its perimeter.

**Assembly sequence:** The cap is the last structural element installed during initial assembly. The bag is laid into the cradle first, cap-end pocketed, fold-end slipped into the spine front slot. The cap is then pressed straight down over the bag from above. The 30° lead-in on each of the four hooks contacts the cradle lip top edges and cams the arms outward. At full engagement, all four hooks clear the lips simultaneously and spring inward into the rebates — one tactile snap drop, firm stop as the cap face contacts the bag. Assembly is confirmed by feel, not sight.

**The cap is assembled once.** The 90° retention face on each hook means disengagement requires tool-level force or deliberate destruction. This is intentional. The vision specifies that the enclosure is snap-shut permanently and the bags are a permanent fixture. The cap is the structural enforcement of that decision.

**Constraint flow:** The bag pushes outward (perpendicular to bag face, in +Y cap frame direction). The cap face resists this via plate bending, distributed into the rib grid roots at Y=1.5mm. The ribs carry the bending moment to the rib-cap-body junctions, distributing load to the cap body perimeter. The snap arms carry the reaction force at the perimeter — the hooks bear against the rebate bottom walls on both cradle lip outer faces, transferring force into the cradle lips, into the cradle body, into the spine tabs, into the spine, into the enclosure.

---

## 4. Constraint Chain (Rubric B)

```
Bag hydraulic pressure (outward, perpendicular to bag face, in cap +Y direction)
         |
         ↓
Cap bag-contact face (Y=0, smooth PETG plate, 1.5mm thick)
         |
         | Distributed load → plate bending resisted by rib grid
         ↓
Rib grid (3 longitudinal + 2 transverse, Y=1.5mm to Y=6.5mm, 1.2mm wide)
         |
         | Bending moments carried to rib roots at cap body perimeter
         ↓
Cap body perimeter (X=0, X=204mm, Z=0, Z=287mm edges)
         |
         | Reaction force transferred outward through snap arms
         ↓
4 snap arms (2 per long edge, Y=0–2.0mm, 20mm cantilever in X)
         |
         | Hook retention faces (90°, permanent) bearing against rebate bottom walls
         ↓
Cradle lip rebates (1.2mm × 1.2mm groove at Y=4.9–6.1mm on lip outer faces)
         |
         ↓
Cradle side lips (4mm thick, X=−4mm to X=0 left; X=196mm to X=200mm right)
         |
         ↓
Cradle body (lens-profiled bowl, R=341mm arc, 2.0mm floor wall, 3 longitudinal ribs)
         |
         ↓
4 cradle snap tabs (8mm wide, 2mm thick, 15mm cantilever) → spine horizontal slots
         |
         ↓
Spine body (220mm span, single part)
         |
         ↓
4 spine snap posts (2 per enclosure half, 90° retention) → enclosure inner walls
         |
         ↓
Enclosure structure (220mm × 300mm × 400mm)
```

---

## 5. Feature List

Features are listed in modeling sequence per decomposition.md. Every dimension is taken directly from spatial-resolution.md with no independent re-derivation.

---

### Feature 1: Cap Body (Flat Plate)

**What it does:** The primary structural volume of the cap. The smooth bag-contact face (Y=0) presses directly against the top face of the Platypus bag film. The body is the base solid from which all other features are added. It must be rigid enough across its 204mm × 287mm span that the bag's hydraulic pressure does not cause visible bowing between ribs — the rib grid (Feature 2) provides this stiffness, but the 1.5mm floor is the continuous membrane that the ribs stiffen.

**Geometry:**

| Parameter | Value | Frame |
|-----------|-------|-------|
| X extent | X=0mm to X=204mm | Cap X |
| Y extent | Y=0mm to Y=1.5mm | Cap Y |
| Z extent | Z=0mm to Z=287mm | Cap Z |
| Width (X) | 204mm | — |
| Thickness (Y) | 1.5mm | — |
| Length (Z) | 287mm | — |

- Bag-contact face: Y=0 plane. Smooth — no features, no ribs, no protrusions. This face is on the build plate during printing; it receives build-plate surface quality (smoothest face on the part). No elephant's foot mitigation feature is required on this face itself because it is a non-mating flat face; the perimeter chamfer (Feature 4) handles the bottom-edge elephant's foot concern.
- Body top face: Y=1.5mm plane. All rib features (Feature 2) root here.
- Left body edge: X=0mm. Snap arm roots for left arms (Feature 3) here.
- Right body edge: X=204mm. Snap arm roots for right arms (Feature 3) here.
- Cap-end face: Z=0mm.
- Fold-end face: Z=287mm.

**Material:** PETG. Minimum wall thickness 1.5mm — this is 3.75× the 0.4mm nozzle minimum wall (0.8mm); it is 1.25× the 1.2mm structural minimum. The rib grid reduces the effective unsupported span to 51mm × 95.7mm cells, within which a 1.5mm PETG plate is structurally adequate per synthesis.md §3.3 (structural analysis confirms 1.5mm face thickness adequate for ~447 Pa distributed load with grid ribs).

**Tolerance / fit notes:** The bag-contact face (Y=0) is not a precision mating surface. The bag film conforms to it. No tolerance critical on this face beyond flatness (maintained by print orientation face-down). The body edges at X=0 and X=204mm are the arm root datums — arm geometry is defined relative to these edges.

---

### Feature 2: Rib Grid (Longitudinal + Transverse Ribs)

**What it does:** Three longitudinal ribs running along Z and two transverse ribs running along X create a grid of rectangular cells on the cap body top face. The grid converts a 204mm × 287mm plate bending problem into a set of 51mm × 95.7mm plate cells — reducing the unsupported span by 4× in X and 3× in Z. The rib height (5mm) provides the section modulus. The grid pattern is also the design language of this mechanism: the spine face carries transverse ribs, the cradle underside carries longitudinal ribs, and the cap top face carries both in a grid, reading as a stiffened panel (concept.md §5).

**All ribs: common parameters**

| Parameter | Value |
|-----------|-------|
| Rib thickness | 1.2mm (in the direction perpendicular to the rib's primary run axis) |
| Rib height | 5mm (in Y) |
| Y base (rib root) | Y=1.5mm |
| Y tip | Y=6.5mm |

**Rib intersections:** At each of the 6 intersection points (L1×T1, L1×T2, L2×T1, L2×T2, L3×T1, L3×T2), model as a boolean union of the two rib solids. No special joint geometry. The union produces a 1.2mm × 1.2mm × 5mm solid post at each intersection.

#### Longitudinal Ribs (×3, running along Z)

Each longitudinal rib spans the full Z length of the cap body (Z=0 to Z=287mm). 1.2mm wide in X, 5mm tall in Y.

| Rib ID | X center | X range | Y base | Y tip | Z extent |
|--------|----------|---------|--------|-------|----------|
| L1 | X=51mm | X=50.4mm to X=51.6mm | Y=1.5mm | Y=6.5mm | Z=0 to Z=287mm |
| L2 | X=102mm | X=101.4mm to X=102.6mm | Y=1.5mm | Y=6.5mm | Z=0 to Z=287mm |
| L3 | X=153mm | X=152.4mm to X=153.6mm | Y=1.5mm | Y=6.5mm | Z=0 to Z=287mm |

Spacing verification: body edge (X=0) to L1 center = 51mm; L1 to L2 = 51mm; L2 to L3 = 51mm; L3 to body edge (X=204) = 51mm. Even spacing confirmed.

#### Transverse Ribs (×2, running along X)

Each transverse rib spans the full X width of the cap body (X=0 to X=204mm). 1.2mm wide in Z, 5mm tall in Y.

| Rib ID | Z center | Z range | Y base | Y tip | X extent |
|--------|----------|---------|--------|-------|----------|
| T1 | Z=95.7mm | Z=95.1mm to Z=96.3mm | Y=1.5mm | Y=6.5mm | X=0 to X=204mm |
| T2 | Z=191.3mm | Z=190.7mm to Z=191.9mm | Y=1.5mm | Y=6.5mm | X=0 to X=204mm |

Spacing verification: cap-end face (Z=0) to T1 center = 95.7mm; T1 to T2 = 95.7mm; T2 to fold-end face (Z=287) = 95.7mm. Even spacing confirmed (287 / 3 = 95.667mm, rounded to 95.7mm).

**Printability:** Ribs are vertical walls (1.2mm thick in X or Z, 5mm tall in Y) built upward from the cap body top face at Y=1.5mm. No overhang. Rib thickness of 1.2mm equals the structural wall minimum (requirements.md: 1.2mm = 3 perimeters for structural walls). All rib walls self-support during printing.

**Tolerance / fit notes:** Rib dimensions are structural, not precision fit. ±0.2mm acceptable on rib width and height.

---

### Feature 3: Snap Arms (×4)

**What they do:** The four snap arms are horizontal cantilever beams that extend outward from the cap body long edges (in ±X). Each arm carries a hook at its tip that engages a 1.2mm × 1.2mm rebate cut into the outer face of the corresponding cradle side lip. When the cap is pressed down onto the filled bag, the 30° lead-in on each hook cams the arm outward (in ±X) by 1.5mm deflection as the hook crosses the lip top edge. Once the hook clears the lip, the arm springs back inward and the hook engages the rebate. The 90° retention face prevents the hook from camming back out — the assembly is permanent.

**Arm geometry (all 4 arms, common parameters):**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Arm thickness (Y) | 2.0mm | Y=0mm (bag-contact face) to Y=2.0mm |
| Arm width (Z) | 6mm | ±3mm from arm Z center |
| Arm length (X) | 20mm | Root at cap body edge to arm tip (not including hook protrusion) |
| Root fillet radius | 1.0mm | Applied at arm-to-body junction on Y=0 and Y=2.0mm edges at the root (X=0 for left arms, X=204mm for right arms) |
| Hook height (Y) | 1.2mm | Hook protrusion: Y=0mm to Y=1.2mm (full designed height; frangible bridge occupies Y=0 to Y=0.2mm) |
| Hook lead-in angle | 30° chamfer | On outer face of hook (X=−20mm face for left hooks; X=224mm face for right hooks) |
| Hook retention face | 90° | Perpendicular to Y axis; at Y=1.2mm; faces −Y (toward bag); permanent assembly |
| Hook protrusion depth (X) | 1.2mm | Into arm body from tip |
| Frangible bridge | 0.2mm void at Y=0 to Y=0.2mm | Designed support per requirements.md; breaks on first deflection during assembly |

**Arm Y alignment:** The arm bottom face is coplanar with the cap body bag-contact face (both at Y=0). This ensures the arm is supported at both Y faces (Y=0 and Y=2.0mm) along its full root attachment to the cap body. The arm top face at Y=2.0mm is 0.5mm proud of the cap body top face at Y=1.5mm.

**Hook engagement in assembled position:** When seated, the cap Y=0 face is at cradle Y=3.7mm. The hook retention face (cap Y=1.2mm) is at cradle Y=4.9mm — coinciding with the rebate bottom wall. The hook body (cap Y=0.2mm to Y=1.2mm, after frangible bridge breaks) occupies cradle Y=3.9mm to Y=4.9mm. The rebate runs from cradle Y=4.9mm to Y=6.1mm. Hook retention face bears against rebate bottom wall. Full 1.2mm of rebate height available above the hook retention face for clearance (cradle Y=4.9mm to Y=6.1mm). The resulting seam step: cap body top (cap Y=1.5mm = cradle Y=5.2mm) minus cradle lip top (cradle Y=3.5mm) = 1.7mm proud step. This is within the 1.5–2mm target from concept.md §3.

#### Left Arm 1 (Cap-End, Left Edge)

| Feature | X range | Y range | Z range |
|---------|---------|---------|---------|
| Arm body | X=−20mm to X=0mm | Y=0mm to Y=2.0mm | Z=37mm to Z=43mm |
| Hook body (full designed) | X=−20mm to X=−18.8mm | Y=0mm to Y=1.2mm | Z=37mm to Z=43mm |
| Hook body (above frangible bridge) | X=−20mm to X=−18.8mm | Y=0.2mm to Y=1.2mm | Z=37mm to Z=43mm |
| Frangible bridge | X=−20mm to X=−18.8mm | Y=0mm to Y=0.2mm | Z=37mm to Z=43mm |
| Hook lead-in | On X=−20mm face of hook | Y=0mm to Y=1.2mm | Z=37mm to Z=43mm |
| Hook retention face | At Y=1.2mm surface | — | Z=37mm to Z=43mm |
| Root fillet | 1.0mm at X=0 root | Y=0 and Y=2.0mm edges | Z=37mm to Z=43mm |

Z center: Z=40mm. Z range: Z=37mm to Z=43mm (±3mm from center).
Arm tip (hook outer face): X=−20mm.
Hook protrudes in +X direction (back toward cap center): X=−20mm to X=−18.8mm.
Lead-in chamfer: 30° on the X=−20mm face of the hook (the face that contacts the cradle lip top edge during press-down). The chamfer removes the bottom-outer corner of the hook, creating a sloped surface that cams the arm in the −X direction as the cap is pushed down.

#### Left Arm 2 (Fold-End, Left Edge)

Same geometry as Left Arm 1 in all respects except Z position.

| Feature | X range | Y range | Z range |
|---------|---------|---------|---------|
| Arm body | X=−20mm to X=0mm | Y=0mm to Y=2.0mm | Z=244mm to Z=250mm |
| Hook body (full designed) | X=−20mm to X=−18.8mm | Y=0mm to Y=1.2mm | Z=244mm to Z=250mm |
| Hook body (above frangible bridge) | X=−20mm to X=−18.8mm | Y=0.2mm to Y=1.2mm | Z=244mm to Z=250mm |
| Frangible bridge | X=−20mm to X=−18.8mm | Y=0mm to Y=0.2mm | Z=244mm to Z=250mm |
| Hook lead-in | On X=−20mm face of hook | Y=0mm to Y=1.2mm | Z=244mm to Z=250mm |
| Hook retention face | At Y=1.2mm surface | — | Z=244mm to Z=250mm |
| Root fillet | 1.0mm at X=0 root | Y=0 and Y=2.0mm edges | Z=244mm to Z=250mm |

Z center: Z=247mm. Z range: Z=244mm to Z=250mm.

#### Right Arm 1 (Cap-End, Right Edge)

Mirror of Left Arm 1 in X (reflected about X=102mm, cap center). Hook protrudes in −X direction (back toward cap center).

| Feature | X range | Y range | Z range |
|---------|---------|---------|---------|
| Arm body | X=204mm to X=224mm | Y=0mm to Y=2.0mm | Z=37mm to Z=43mm |
| Hook body (full designed) | X=222.8mm to X=224mm | Y=0mm to Y=1.2mm | Z=37mm to Z=43mm |
| Hook body (above frangible bridge) | X=222.8mm to X=224mm | Y=0.2mm to Y=1.2mm | Z=37mm to Z=43mm |
| Frangible bridge | X=222.8mm to X=224mm | Y=0mm to Y=0.2mm | Z=37mm to Z=43mm |
| Hook lead-in | On X=224mm face of hook | Y=0mm to Y=1.2mm | Z=37mm to Z=43mm |
| Hook retention face | At Y=1.2mm surface | — | Z=37mm to Z=43mm |
| Root fillet | 1.0mm at X=204mm root | Y=0 and Y=2.0mm edges | Z=37mm to Z=43mm |

Arm tip (hook outer face): X=224mm.
Hook protrudes in −X direction: X=222.8mm to X=224mm (1.2mm from tip back toward cap body).
Lead-in chamfer: 30° on the X=224mm face of the hook.

#### Right Arm 2 (Fold-End, Right Edge)

Same geometry as Right Arm 1 in all respects except Z position.

| Feature | X range | Y range | Z range |
|---------|---------|---------|---------|
| Arm body | X=204mm to X=224mm | Y=0mm to Y=2.0mm | Z=244mm to Z=250mm |
| Hook body (full designed) | X=222.8mm to X=224mm | Y=0mm to Y=1.2mm | Z=244mm to Z=250mm |
| Hook body (above frangible bridge) | X=222.8mm to X=224mm | Y=0.2mm to Y=1.2mm | Z=244mm to Z=250mm |
| Frangible bridge | X=222.8mm to X=224mm | Y=0mm to Y=0.2mm | Z=244mm to Z=250mm |
| Hook lead-in | On X=224mm face of hook | Y=0mm to Y=1.2mm | Z=244mm to Z=250mm |
| Hook retention face | At Y=1.2mm surface | — | Z=244mm to Z=250mm |
| Root fillet | 1.0mm at X=204mm root | Y=0 and Y=2.0mm edges | Z=244mm to Z=250mm |

Z center: Z=247mm. Z range: Z=244mm to Z=250mm.

**Structural note:** Arm deflection during assembly: 1.5mm in X (to cam hook past 1.2mm lip top clearance plus 0.3mm lead-in). PETG strain at 1.5mm deflection for a 20mm × 2mm arm = 1.1%, well within the 4% elastic limit (synthesis.md §3.3, structural-analysis.md). Arms return to rest position after hook clears lip.

**Tolerance / fit notes:** Hook protrusion depth: 1.2mm. Cradle rebate depth: 1.2mm (designed at 1.3mm per cradle spatial-resolution.md to provide 0.1mm snug fit clearance for hook entry). Arm-to-lip-face X clearance: 0.1mm (snug fit per requirements.md). Arms print as horizontal walls extending from the build plate face — no overhang, no support required for the arm bodies. Hook undercuts require designed frangible bridges (see frangible bridge specification below).

---

### Feature 3a: Frangible Bridges (×4, one per hook)

**What they do:** Each hook has an undercut at Y=0 (the hook's bottom face, which faces the build plate during printing). Without intervention, the slicer would need to generate support material under each hook — support that would be inaccessible for removal in the finished part. Instead, the hook is modeled with a 0.2mm-thick solid base connecting the hook bottom to the arm body at Y=0. This 0.2mm base is the designed support per requirements.md §FDM ("Include a 0.2mm interface gap... the printer bridges this gap with a thin fragile connection that breaks away cleanly"). On the first snap arm deflection during assembly engagement, the 0.2mm frangible bridge breaks cleanly.

**After bridge breaks:** Hook effective height becomes 1.0mm (Y=0.2mm to Y=1.2mm). This 1.0mm effective hook height is confirmed adequate for permanent assembly per concept.md (hook seats at rebate bottom wall with full 90° retention face bearing).

**Geometry (per hook):**

The hook solid in CadQuery is modeled as two additive volumes:
1. Hook proper: the X-range protrusion, Y=0.2mm to Y=1.2mm (1.0mm tall), with 30° lead-in chamfer on outer face and 90° retention face at Y=1.2mm.
2. Frangible bridge: the same X-range protrusion, Y=0mm to Y=0.2mm (0.2mm tall). This is a thin rectangular plate at the hook base, connecting hook to arm body.

**Left hook frangible bridge (both left arms):**

| Parameter | Value |
|-----------|-------|
| X range | X=−20mm to X=−18.8mm |
| Y range | Y=0mm to Y=0.2mm |
| Z range | (arm Z range: Z=37–43mm or Z=244–250mm) |
| Bridge span | 1.2mm (in X) — within 15mm bridge limit |
| Break behavior | Breaks on first arm deflection during assembly |

**Right hook frangible bridge (both right arms):**

| Parameter | Value |
|-----------|-------|
| X range | X=222.8mm to X=224mm |
| Y range | Y=0mm to Y=0.2mm |
| Z range | (arm Z range: Z=37–43mm or Z=244–250mm) |

**CadQuery implementation note:** Do NOT subtract the full hook undercut. Model the frangible bridge as a thin positive volume (0.2mm in Y) that is a solid union with the arm body and hook. This preserves the thin fragile layer in the print. The bridge is not a gap in the model — it is a deliberately thin solid floor that prints as a bridging layer across the Y=0 face of the hook space.

---

### Feature 4: Perimeter Chamfer

**What it does:** A 1.5mm × 45° chamfer on all four perimeter edges of the cap body top face (the Y=1.5mm surface edges). This chamfer serves two purposes. First, it is the design language feature that signals "press here" — the angled face catches light and gives visual direction during assembly (concept.md §5: "a chamfer provides a consistent visual cue to the engagement direction"). Second, it subsumes the elephant's foot mitigation requirement (requirements.md: "add a 0.3mm × 45° chamfer to the bottom edge" where the bottom face is a mating surface). In print orientation the Y=1.5mm face is 1.5mm above the build plate; the 1.5mm chamfer removes the corner between the Y=1.5mm face and each side face, with the chamfer slope reaching Y=0 — addressing any potential elephant's foot at the cap body side edges.

**Location:** Applied to the four edges of the cap body at Y=1.5mm — the boundary between the body top face (Y=1.5mm) and each of the four side faces (X=0, X=204mm, Z=0, Z=287mm). The chamfer is on the cap BODY only (X=0 to X=204mm, Z=0 to Z=287mm). It does not extend onto snap arm geometry.

**Chamfer specification:**

| Edge | Location | Chamfer runs | Chamfer size |
|------|----------|-------------|-------------|
| Left long edge | (X=0, Y=1.5mm) edge | Z=0 to Z=287mm | 1.5mm × 45° |
| Right long edge | (X=204mm, Y=1.5mm) edge | Z=0 to Z=287mm | 1.5mm × 45° |
| Cap-end short edge | (Z=0, Y=1.5mm) edge | X=0 to X=204mm | 1.5mm × 45° |
| Fold-end short edge | (Z=287mm, Y=1.5mm) edge | X=0 to X=204mm | 1.5mm × 45° |

The chamfer removes material from the cap body top face perimeter: at the left long edge, material from X=0 to X=−1.5mm and Y=1.5mm to Y=0mm. At the right long edge, from X=204mm to X=205.5mm and Y=1.5mm to Y=0mm. At the end edges, analogously in Z.

Note: the chamfer corner vertices at the four body corners (X=0,Z=0; X=204,Z=0; X=0,Z=287; X=204,Z=287) are all at Y=1.5mm. CadQuery applies chamfer to each edge independently; corner treatment at the four intersecting chamfer edges uses the default CadQuery chamfer intersection behavior (mitered or minimal-material corner).

**Printability:** The chamfer face is at 45° from horizontal in print orientation — exactly at the minimum printable angle per requirements.md. Printable without support. The chamfer is at Y=0 to Y=1.5mm near the build plate; it is a sloped face transitioning from the build plate level to the cap body side face. No support required.

---

## 6. Complete Feature Summary Table

| # | Feature | Operation | Key dimensions |
|---|---------|-----------|----------------|
| 1 | Cap body | Extrude rectangle | 204mm(X) × 1.5mm(Y) × 287mm(Z) |
| 2a | Longitudinal rib L1 | Add extrusion to body top | X=50.4–51.6mm, Y=1.5–6.5mm, Z=0–287mm |
| 2b | Longitudinal rib L2 | Add extrusion | X=101.4–102.6mm, Y=1.5–6.5mm, Z=0–287mm |
| 2c | Longitudinal rib L3 | Add extrusion | X=152.4–153.6mm, Y=1.5–6.5mm, Z=0–287mm |
| 2d | Transverse rib T1 | Add extrusion | Z=95.1–96.3mm, Y=1.5–6.5mm, X=0–204mm |
| 2e | Transverse rib T2 | Add extrusion | Z=190.7–191.9mm, Y=1.5–6.5mm, X=0–204mm |
| 3a | Left Arm 1 body | Add extrusion | X=−20–0mm, Y=0–2mm, Z=37–43mm |
| 3b | Left Arm 1 hook | Add extrusion + chamfer | X=−20–−18.8mm, Y=0–1.2mm, Z=37–43mm |
| 3c | Left Arm 2 body | Add extrusion | X=−20–0mm, Y=0–2mm, Z=244–250mm |
| 3d | Left Arm 2 hook | Add extrusion + chamfer | X=−20–−18.8mm, Y=0–1.2mm, Z=244–250mm |
| 3e | Right Arm 1 body | Add extrusion | X=204–224mm, Y=0–2mm, Z=37–43mm |
| 3f | Right Arm 1 hook | Add extrusion + chamfer | X=222.8–224mm, Y=0–1.2mm, Z=37–43mm |
| 3g | Right Arm 2 body | Add extrusion | X=204–224mm, Y=0–2mm, Z=244–250mm |
| 3h | Right Arm 2 hook | Add extrusion + chamfer | X=222.8–224mm, Y=0–1.2mm, Z=244–250mm |
| 3i | Root fillets ×4 | Fillet | 1.0mm at each arm root (Y=0 and Y=2.0mm edges at X=0 or X=204mm) |
| 3j | Frangible bridges ×4 | Thin solid at Y=0–0.2mm | 0.2mm base at each hook; Y=0–0.2mm |
| 4 | Perimeter chamfer | Chamfer 4 edges | 1.5mm × 45° at Y=1.5mm perimeter of cap body |

---

## 7. Rubric G — FDM Printability Analysis

**Print orientation:** Bag-contact face down. Y=0 on build plate. Y increases upward (away from build plate). Z runs along the long axis of the part.

**Feature-by-feature analysis:**

**Cap body (Feature 1):**
Y=0 face is on the build plate — no overhang. The body is a 1.5mm-thick plate lying flat. It prints as a solid horizontal slab. No issues.

**Rib grid (Feature 2):**
All ribs are vertical walls perpendicular to the build plate (X-normal walls for longitudinal ribs, Z-normal walls for transverse ribs). They grow from Y=1.5mm to Y=6.5mm — straight upward. No overhang. Rib width 1.2mm = 3 perimeters, printable. Rib height 5mm = 50 layers at 0.1mm — no bridging required, pure wall extrusion. All rib intersections are solid posts (1.2mm × 1.2mm × 5mm) — stable. No issues.

**Snap arm bodies (Feature 3, arm bodies only):**
Arms extend horizontally in X from the cap body long edges. In print orientation (cap face down), the arms are in the XZ plane (flat). The arm bottom face (Y=0) is coplanar with the cap body bottom face (Y=0) — it is on the build plate side. Arms print as thin horizontal slabs starting from the build plate level, extending outward in X. The arm thickness of 2.0mm is well above the 0.8mm minimum wall (requirements.md). The arm bottom is not an overhang — it is supported by the build plate surface level (the arm body Y=0 is at the same Z level as the cap body Y=0; in print coordinates Y=0 is the first printed layer and the arm body grows upward from there same as the cap body). No issues.

**Hook lead-in faces (30° chamfer on outer face):**
The lead-in chamfer is 30° from vertical = 60° from horizontal. Per requirements.md: "No unsupported face angle below 45° from horizontal." 60° from horizontal is above 45°. The lead-in face is printable without support. No issues.

**Hook retention faces (90° face at Y=1.2mm):**
The retention face is a vertical surface (perpendicular to Y, facing −Y). It is a vertical wall. No overhang. No issues.

**Hook undercuts — frangible bridges (Feature 3j):**
The hook body occupies Y=0 to Y=1.2mm (full designed), with the frangible bridge at Y=0 to Y=0.2mm. In print orientation, the hook is at Z position relative to the build plate: the hook body bottom (Y=0) is at the build plate level. The hook extends outward in X (for left hooks: X=−20mm to X=−18.8mm). The hook's Y=0 face is the build plate face of the arm — it prints as the first layer of that X position, attached to the build plate and to the arm body at Y=0.

Specifically: the arm body at Y=0 is a continuous floor. The hook is part of the arm at the tip. The hook bottom face (Y=0) is coplanar with the arm body bottom face (Y=0) — both are at the build plate level. There is NO undercut void in the print. The frangible bridge IS the 0.2mm bottom of the hook solid. The hook is fully supported by its Y=0 face being on the build plate. No void, no overhang.

What creates the "breakaway" behavior is that the hook occupies the space from Y=0 to Y=1.2mm while the arm body at that X location (X=−20mm) is only the arm body from Y=0 to Y=2.0mm but the arm body in X terminates at X=−20mm — the hook is at the tip. The 0.2mm frangible bridge is modeled as the lowest 0.2mm of the hook (Y=0 to Y=0.2mm): this creates a zone of minimal material in Z cross-section connecting the hook to the arm body. In practice, at Y=0 the hook and arm body are both at the build plate, but the joint between them at the hook-arm boundary is only 0.2mm tall — the frangible layer. When the arm deflects in X, this 0.2mm base at the hook root is the failure point. This is correct per requirements.md design intent.

Bridge span for the 0.2mm frangible bridge: the bridge at Y=0 to Y=0.2mm spans 1.2mm in X (from hook outer face at X=−20mm to hook inner face at X=−18.8mm). 1.2mm is well within the 15mm maximum bridge span. No issues.

**Root fillets (Feature 3i):**
1.0mm fillets at the arm root on Y=0 and Y=2.0mm edges. These are concave fillets on a corner that is parallel to the build plate. They print as normal concave curves. No overhang. No issues.

**Perimeter chamfer (Feature 4):**
The chamfer is on the Y=1.5mm edges of the cap body. In print orientation (Y=0 on build plate), the chamfer face slopes at 45° — from Y=0 at the outer extent to Y=1.5mm at the cap body face. The slope is exactly 45° from horizontal, which is the minimum printable angle per requirements.md. Printable without support. This chamfer also removes any elephant's foot corner at the cap body perimeter edges. No issues.

**Summary: No support material required anywhere on this part.** All features either self-support or use the designed frangible bridge geometry as the sole designed support provision. The frangible bridges are positive material (not voids), consistent with requirements.md §FDM guidance.

---

## 8. Rubric H — Feature Traceability

Every feature on this part traces to either a vision statement, a functional requirement, or a physical necessity.

| Feature | Traces to | Source |
|---------|-----------|--------|
| Cap body, 204mm wide | Cap must span from lip outer face to lip outer face so snap arm roots are at the rebate engagement position. Cap body width = lip outer face span = 204mm (cradle frame: X=−4mm to X=200mm). | spatial-resolution.md §2; concept.md §2 |
| Cap body, 1.5mm thick | Structural analysis establishes 1.5mm face plate as adequate for ~447 Pa distributed load with grid ribs in place. Below 1.5mm the plate spans would be too compliant under hydraulic pressure. | synthesis.md §3.3; structural-analysis.md |
| Cap body, 287mm long | Matches the cradle Z length exactly — the bag runs the full 287mm projected horizontal span at 35°. | concept.md §1; spatial-resolution.md §2 |
| Bag-contact face smooth (Y=0, no features) | Bag film must not be stressed by surface protrusions. Stress concentrations on Platypus bag film seams would cause premature failure of the bag. Smooth face = no stress risers. | concept.md §4; vision.md §2 ("nothing else is replaceable — bags are permanent fixture") |
| Rib grid on top face only | Design language: stiffened panel language on the visible face. Ribs on the bag-contact face would create stress concentrations. | concept.md §4, §5 |
| 3 longitudinal + 2 transverse ribs | Reduces unsupported cap span from 204mm × 287mm to 51mm × 95.7mm cells, enabling 1.5mm floor thickness. Also expresses the design language of the mechanism's interior surfaces (consistent rib pattern across all bag frame parts per concept.md §5). | synthesis.md §3.3; concept.md §5 |
| Rib dimensions: 1.2mm wide, 5mm tall | 1.2mm = minimum structural wall (requirements.md: 3 perimeters). 5mm tall provides section modulus adequate for the distributed bag pressure load (structural-analysis.md). Consistent rib language with cradle underside (6mm ribs) and spine face (1.5mm ribs) — within the same design family. | requirements.md §FDM; synthesis.md §3.3; concept.md §5 |
| 4 snap arms (2 per long edge, not top/bottom) | Arms must flex in the X direction (parallel to the build plate) to satisfy requirements.md layer-strength constraint for snap-fit features. Arms on long edges flex in X/Y plane. Arms extending from the face perimeter downward would flex in Y (perpendicular to layers = weakest direction). | requirements.md §layer-orientation; concept.md §7 (Conflict 2 resolution) |
| Arm length 20mm | Structural analysis: 20mm cantilever at 2.0mm PETG thickness gives 1.5mm deflection at 1.1% strain — within 4% elastic limit. Shorter arms would require higher strain for the same deflection; longer arms would be fragile. | structural-analysis.md; synthesis.md §3.3 |
| Arm thickness 2.0mm | Sets the strain during assembly deflection to 1.1%, within PETG elastic limit. | structural-analysis.md; synthesis.md §3.3 |
| Arm width 6mm | Provides adequate bearing area at the hook face (6mm × 1.2mm = 7.2mm² contact). Concept.md specifies 6mm width. | concept.md §2 |
| Hook 30° lead-in | Assembly UX requirement: the cap must cam over the cradle lip smoothly with one-hand thumb pressure. 30° lead-in tolerates ±3mm lateral placement error during assembly. Angle is above 45° from horizontal (60° from horizontal) — printable without support. | concept.md §2; requirements.md §overhang |
| Hook 90° retention face | Permanent assembly. Vision states bags are a permanent fixture; the enclosure is snap-shut permanently. The 90° face cannot cam out under any functional load. | vision.md §2; requirements.md ("The bag frame has no service access provisions"); concept.md §6 |
| Root fillet 1.0mm | Reduces stress concentration at the arm root — the highest-stress point during snap engagement. 1.0mm is the minimum effective fillet for this application. | concept.md §2; structural-analysis.md |
| Frangible bridge 0.2mm | Requirements.md requires designed support geometry with a 0.2mm interface gap for any hook undercut that cannot be accessed for support removal. The hook undercut at Y=0 faces the build plate — slicer-generated support cannot be removed. The frangible bridge is the required designed support. | requirements.md §FDM ("designed support geometry must not be a solid union... include a 0.2mm interface gap") |
| Perimeter chamfer 1.5mm × 45° | Design language: concept.md §5 specifies "1.5mm chamfer" on the cap perimeter edge, "chamfer rather than fillet on the cap perimeter: the cap is the element the assembler presses down, and a chamfer provides a consistent visual cue to the engagement direction." Also serves as elephant's foot mitigation (requirements.md: 0.3mm × 45° minimum; 1.5mm subsumes it). | concept.md §5; requirements.md §dimensional-accuracy |
| Cap body only (no arm extension) on chamfer | The snap arms are on the side faces of the cap body, not the top face perimeter. The chamfer is on the top face perimeter only — the visual feature that the assembler sees when looking down at the cap before pressing it. Extending the chamfer onto arm geometry would be undefined and serves no purpose. | concept.md §5 |
| PETG material | All bag frame parts are PETG for visual uniformity (same color, same sheen, reads as one mechanism). PETG provides adequate flexibility for snap arm engagement (elongation at break ~250% vs. strain ~1.1% during engagement). Food-adjacent use (no direct food contact — the bag film is between the cap and the syrup; PETG is generally food-safe). | concept.md §5; requirements.md §materials |
| Print orientation face-down | Best surface quality on the bag-contact face (build-plate surface quality). Arms flex in X (parallel to layers). Rib grid builds as vertical walls without support. All overhang constraints satisfied. | concept.md §7; requirements.md §layer-orientation, §overhang |
| 2 instances (same file, print twice) | Each bag position gets one upper cap. Both are identical — the bags are at the same orientation (both cap-end toward back-bottom) so no mirroring is required. | concept.md §1 |
