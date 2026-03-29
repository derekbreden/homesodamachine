# Parts Specification: Sub-E Guide Post Array

## Scope

4 cylindrical guide posts projecting from the rear wall exterior (dock-facing) surface, plus mushroom-cap stop features at each post tip. These posts guide the release plate's 1.5 mm travel along the Y axis to compress the dock-facing collets of the 4 John Guest fittings.

**Parent part:** Tray (printed as one piece with Sub-A box shell)

---

## 1. Mechanism Narrative

### What the user sees and touches

The guide posts are never visible or touched by the user. They are entirely enclosed within the dock cavity when the cartridge is seated. The user interacts only with the front bezel (palm rest and finger channels). The posts exist solely to constrain the release plate's motion behind the rear wall.

### What moves

- **Release plate** (separate printed part, ~55 x 55 x 5 mm): translates along the Y axis on the 4 guide posts. It slides from its rest position (Y = -17.14 mm, wall-facing face resting against the extended collet tips) toward the rear wall (Y = -15.64 mm, wall-facing face) when the user squeezes.
- **4 guide posts**: stationary. Printed integral with the tray rear wall.
- **Rear wall**: stationary. Part of the tray body (Sub-A).

### What converts the motion

The user squeezes the front bezel (palm pushes against bezel outer face, fingers pull the pull-tab paddles inward). Linkage rods running along the tray inner side walls transmit the finger pull force rearward. The linkage rods connect to the release plate. The plate translates in the +Y direction (toward the rear wall), compressing the dock-facing collets of the 4 John Guest fittings. The guide posts do not convert motion -- they constrain it.

### What constrains each moving part

The release plate has exactly one degree of freedom: translation along Y.

- **Rotation about Y (spin):** prevented by 4 guide posts at the corners of a 40 x 40 mm rectangle. The 3.8 mm bores on 3.5 mm posts (0.15 mm clearance per side) at 40 mm spacing limit rotational play to arctan(0.30 / 40) = 0.43 degrees. This is negligible.
- **Translation along X:** prevented by the 4 posts. Maximum lateral play = 0.30 mm (total diametral clearance).
- **Translation along Z:** prevented by the 4 posts. Maximum vertical play = 0.30 mm.
- **Tilt about X (pitch):** prevented by the 40 mm Z-span between upper and lower post pairs. Maximum tilt = arctan(0.30 / 40) = 0.43 degrees, producing 0.003 mm differential at the fitting positions (20 mm span). Negligible.
- **Tilt about Z (yaw):** prevented by the 40 mm X-span between left and right post pairs. Same calculation, same negligible result.
- **Travel limit in +Y direction (toward wall):** the collet internal bottoming limits travel to ~1.3 mm. The rear wall face (Y = 0) provides a hard backstop if the collets were absent, but during normal operation the collets bottom out first.
- **Travel limit in -Y direction (away from wall):** mushroom cap stop features (0.5 mm radial overhang) at each post tip (Y = -25 mm) prevent the release plate from sliding off the posts when the cartridge is removed from the dock.

### What provides the return force

The collet springs inside the 4 John Guest fittings. When the user releases the squeeze, the collet springs push the release plate back to its rest position (Y = -17.14 mm). The guide posts provide no return force -- they are passive guides.

### User's physical interaction with the guide posts

None. The user never touches, sees, or directly interacts with the guide posts. The posts serve the release plate mechanism internally.

---

## 2. Constraint Chain

```
[User fingers]
    -> [Pull-tab paddles: translate in +Y]
    -> [Linkage rods: rigid axial link]
    -> [Release plate: translates +Y on guide posts]
         ^ X constrained by: 4 guide posts (0.15 mm clearance/side)
         ^ Z constrained by: 4 guide posts (0.15 mm clearance/side)
         ^ rotation constrained by: 4-post pattern at 40 x 40 mm spacing
         ^ -Y limit: mushroom caps at post tips (Y = -25 mm)
         ^ +Y limit: collet internal bottoming (~1.3 mm travel)
    -> [Collet faces: compressed 1.3 mm inward]
    -> [Collet teeth disengage tube: tube released]

[User palm]
    -> [Front bezel outer face: stationary reaction surface]
    -> [Bezel snap tabs to tray: transfers reaction force to tray]
    -> [Tray rear wall: holds guide posts and fittings]
         ^ guide posts are integral with rear wall (printed as one piece)

Return path:
[Collet springs] -> [Release plate pushed -Y to rest] -> [Linkage rods relax] -> [Pull tabs return]
```

---

## 3. Part Inventory

### Part E1: Guide Post (qty 4, printed integral with tray)

**Geometry:** Cylindrical extrusion projecting from the rear wall exterior face in the -Y direction.

| Parameter | Value | Source |
|-----------|-------|--------|
| Diameter | 3.5 mm | Concept doc specification |
| Length (base to start of cap) | 24.5 mm | Spatial doc: 25 mm total - 0.5 mm cap height |
| Base plane | Y = 0 mm (rear wall exterior face) | Spatial doc Section 3d |
| Tip plane (before cap) | Y = -24.5 mm | Derived: 0 - 24.5 |
| Cross-section | Circular, constant 3.5 mm diameter | -- |
| Draft angle | 0 degrees (straight cylinder) | -- |
| Surface finish | As-printed (internal, non-cosmetic) | -- |
| Material | PETG, integral with tray | Concept doc Section 7 |

**Post positions (tray frame, X and Z):**

| Post | X (mm) | Z (mm) |
|------|--------|--------|
| P1 (lower-left) | 60 | 17.5 |
| P2 (lower-right) | 100 | 17.5 |
| P3 (upper-left) | 60 | 57.5 |
| P4 (upper-right) | 100 | 57.5 |

Post rectangle: 40 mm x 40 mm, centered at (80, 37.5) = fitting grid center.

### Part E2: Mushroom Cap Stop (qty 4, printed integral with each post tip)

**Geometry:** Short cylindrical disc at each post tip with 0.5 mm radial overhang beyond the post diameter.

| Parameter | Value | Source |
|-----------|-------|--------|
| Cap OD | 4.5 mm (3.5 mm post + 2 x 0.5 mm overhang) | Spatial doc Section 3f |
| Cap height (along Y) | 0.5 mm | Spatial doc Section 3f |
| Cap bottom plane | Y = -24.5 mm | Derived: -25 + 0.5 |
| Cap top plane (post tip) | Y = -25 mm | Spatial doc Section 3d |
| Transition | Sharp step from 3.5 mm post to 4.5 mm cap | -- |
| Overhang per side | 0.5 mm | Spatial doc Section 3f |

**Function:** Prevents the release plate (3.8 mm bore) from sliding off the posts in the -Y direction. The plate bore (3.8 mm) is smaller than the cap OD (4.5 mm), so the cap retains the plate. The plate must be installed onto the posts before the caps are printed (the posts and caps are printed as one piece with the tray, so the release plate must be installed after printing by flexing past the caps or the caps must be designed to allow snap-over assembly -- see Assembly section).

**DESIGN GAP: Snap-over assembly of release plate onto mushroom caps.** The release plate bores are 3.8 mm and the cap OD is 4.5 mm. The plate cannot slide over the caps without elastic deformation. Two resolution paths:

1. **Printed flex caps:** Print the caps as thin fins (0.5 mm radial, 0.5 mm tall) that deflect inward when the plate is pressed over them. PETG at 0.5 mm wall can deflect 0.5 mm. The release plate bore edge (0.15 mm clearance on 3.5 mm post) requires the cap to compress from 4.5 mm to under 3.8 mm, a 0.35 mm deflection per side. This is feasible for PETG at 0.5 mm wall thickness, but only with a chamfered lead-in on the cap. Add a 45-degree chamfer on the cap's -Y face, 0.5 mm tall, to cam the bore open during snap-over.
2. **Separate retaining clips:** Print the caps as separate C-clips that snap onto a groove at the post tip. This adds 4 parts but guarantees easy assembly.

**Recommended resolution:** Option 1 (printed flex caps with 45-degree chamfer). This maintains zero additional part count and the force required is low (4 small PETG fins, each 0.5 mm overhang).

---

## 4. Print Orientation and Manufacturability

The guide posts and mushroom caps print as part of the tray, which prints open-top-up with XY on the build plate.

**Posts:** The 4 posts project in the -Y direction from the rear wall. Since the tray prints with the open top facing up (Z-up in printer frame), the rear wall is vertical (in the XZ plane of the tray frame, which maps to an XZ plane on the build plate). The posts extrude horizontally from this vertical wall.

**Overhang concern:** The posts are 3.5 mm diameter horizontal cylinders projecting 25 mm from a vertical wall. Horizontal cylinders up to ~5 mm diameter print acceptably in PETG with minor drooping on the underside. At 3.5 mm diameter this is well within limits. No support material needed.

**Mushroom caps:** Each cap has a 0.5 mm overhang on all sides. The underside of the cap (the face closest to the rear wall, at Y = -24.5 mm) is a 0.5 mm horizontal overhang. At 0.5 mm projection this prints without support (standard FDM bridges up to 5 mm without support). The 45-degree chamfer on the -Y face (tip face) further aids printability.

**Layer orientation relative to post axis:** The posts print with layers stacked perpendicular to Z (vertically in the printer). The post axis is along Y (horizontal). This means the posts have layer lines running across their diameter. Shear strength along the post axis is limited by layer adhesion, not filament tensile strength. For a 3.5 mm PETG post, the cross-sectional area is 9.62 mm^2. At PETG inter-layer shear strength of ~30 MPa, the post can withstand ~289 N of axial pull before layer delamination. The release plate exerts negligible axial force on the posts (only the snap-over assembly force, which is momentary and under 5 N).

**Bending concern:** A 25 mm long, 3.5 mm diameter PETG cantilever loaded laterally at the tip. The release plate sliding friction is negligible (< 0.5 N per post). The bending stress at the base is sigma = (32 * F * L) / (pi * d^3) = (32 * 0.5 * 25) / (pi * 3.5^3) = 2.97 MPa. PETG flexural strength is ~70 MPa. Safety factor > 20. No concern.

---

## 5. Dimensions and Tolerances

| Feature | Nominal | Tolerance | Rationale |
|---------|---------|-----------|-----------|
| Post diameter | 3.5 mm | +0.0 / -0.1 mm | Posts must fit inside 3.8 mm bores with minimum 0.15 mm clearance per side. If post prints oversize, clearance decreases and plate may bind. Undersizing is acceptable (increases clearance to 0.20 mm/side max). |
| Post length (base to cap start) | 24.5 mm | +/- 0.5 mm | Non-critical. Post must extend past release plate rest position (Y = -17.14 mm) plus plate thickness (5 mm) = 22.14 mm minimum. At 24.5 mm nominal minus 0.5 mm = 24.0 mm, still exceeds 22.14 mm. |
| Post center positions (X, Z) | Per table in Section 3 | +/- 0.2 mm | Must match release plate bore pattern within the 0.15 mm/side clearance budget. 4 posts printed in one piece share the same positional error from the slicer, so relative accuracy is better than absolute. |
| Mushroom cap OD | 4.5 mm | +0.0 / -0.2 mm | Must remain larger than 3.8 mm plate bore to retain plate. At 4.5 - 0.2 = 4.3 mm, still 0.5 mm larger than bore. |
| Mushroom cap height | 0.5 mm | +/- 0.2 mm | Non-critical. Must be thick enough to resist snap-over forces without fracture. At 0.3 mm minimum, still structurally adequate for PETG. |
| Cap chamfer angle | 45 degrees | +/- 5 degrees | Aids snap-over assembly. Exact angle not critical. |
| Cap chamfer height | 0.5 mm | +/- 0.2 mm | -- |
| Post perpendicularity to rear wall | -- | < 0.5 degrees | Controlled by print accuracy. At 0.5 degrees over 25 mm length, the post tip deflects 0.22 mm from true. This is within the 0.30 mm diametral bore clearance budget. |

---

## 6. Interface Definitions

### Interface E-A: Posts to Rear Wall Exterior Face

- **Type:** Integral (printed as one piece, no joint)
- **Post base plane:** Y = 0 mm (rear wall exterior/dock-facing surface)
- **Bond area per post:** Circle, 3.5 mm diameter = 9.62 mm^2
- **Stress at bond:** Negligible (see bending analysis in Section 4)
- **Fillet at base:** None specified. A 0.5 mm fillet at the post-to-wall junction would increase strength, but the safety factor is already > 20. Optional for printability.

### Interface E-Plate: Posts to Release Plate Bores

- **Type:** Sliding clearance fit
- **Post OD:** 3.5 mm
- **Plate bore ID:** 3.8 mm
- **Clearance per side:** 0.15 mm (0.30 mm diametral)
- **Bearing length:** 5 mm (release plate thickness)
- **Bearing length to diameter ratio:** 5 / 3.5 = 1.43. Adequate to prevent significant tilt (combined with 4-post pattern).
- **Lubrication:** None. PETG on PETG sliding at 0.15 mm clearance with < 2 mm travel is inherently low-friction.
- **Plate travel:** 1.5 mm along +Y (from Y = -17.14 to Y = -15.64, wall-facing face)

### Interface E-Dock: Posts to Dock Cavity (clearance)

- **Type:** Clearance (no contact)
- **Required dock cavity envelope:** X: 55..105 mm, Z: 12.5..62.5 mm (post span + 5 mm margin each side), Y depth from dock mating face: minimum 30 mm (25 mm post length + 5 mm plate thickness)
- **No mating feature on dock** -- the dock must simply have an open cavity that accommodates the posts and plate.

### Interface E-Cap-Plate: Mushroom Caps to Release Plate (retention)

- **Type:** Snap-over retention
- **Cap OD:** 4.5 mm
- **Plate bore ID:** 3.8 mm
- **Interference during assembly:** (4.5 - 3.8) / 2 = 0.35 mm per side
- **Chamfer lead-in:** 45-degree chamfer, 0.5 mm tall, on the cap -Y face
- **Retention force in service:** The release plate cannot slide past the caps during normal operation. The collet springs push the plate to Y = -17.14 mm (rest). The caps are at Y = -24.5 to -25 mm. The plate would need to travel an additional 7.36 mm past rest to reach the caps. The linkage mechanism does not produce this travel -- the mechanism only pushes the plate +Y (toward the wall), not -Y (toward the caps). The caps are a safety retention for when the cartridge is out of the dock and handled freely.

---

## 7. Assembly Sequence

1. **Print the tray** (Sub-A through Sub-E in the build sequence). Posts and mushroom caps are printed integral. No assembly step for the posts themselves.
2. **Install release plate onto posts.** Orient the plate so its 4 bores (3.8 mm) align with the 4 posts. Press the plate onto the posts from the -Y direction (from the post tip side). The plate bores cam over the mushroom caps (45-degree chamfer guides engagement). Each cap deflects inward 0.35 mm as the bore edge passes over it, then springs back to retain the plate. Apply firm even pressure across all 4 posts simultaneously. The snap-over force is low (< 5 N total for 4 PETG caps).
3. **Verify plate slides freely.** Push the plate toward the rear wall and release. It should slide smoothly on the posts and return to the rest position under gravity or light finger push (in service, collet springs provide return force). Travel should be at least 1.5 mm without binding.

**Disassembly (service):** Pull the release plate away from the rear wall (in the -Y direction) firmly enough to cam the bores back over the mushroom caps. Same snap-over force as assembly. The caps may wear slightly after repeated assembly/disassembly cycles, but this operation is expected to be extremely rare (see concept doc Section 6, Tier 4: "Extremely rare").

---

## 8. Coordinate System Reference

All dimensions in the tray reference frame:
- **Origin:** rear-left-bottom corner of tray
- **X:** 0..160 mm, left to right when facing the front
- **Y:** 0..155 mm, 0 at rear/dock wall exterior, 155 at front/user side. Posts project in -Y (into dock space).
- **Z:** 0..72 mm, 0 at floor bottom, 72 at top of side walls

---

## Design Gaps

1. **Snap-over cap assembly force verification.** The calculated 0.35 mm deflection per side on 0.5 mm PETG fins at the mushroom cap is theoretically feasible, but has not been empirically verified. A test print of a single post with cap and a test bore should confirm the snap-over works without fracturing the cap. If the cap fractures, increase cap height to 0.8 mm (more material to distribute stress) or switch to resolution path 2 (separate C-clips).

2. **Decomposition document inconsistency.** The tray-decomposition.md states Sub-E posts "rise from the interior face of the rear wall" and describes "8-10 mm" post length. The spatial resolution document (the authoritative dimensional source) places the posts on the exterior (dock-facing) face at Y = 0 projecting -Y, with 25 mm length. The spatial resolution document is followed here as it is the primary dimensional input. The decomposition document should be updated to reflect the correct direction and length.
