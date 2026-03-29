# Parts Specification: Sub-D Fitting Bore Array

## Scope

This document specifies Sub-D of the tray: the 4 fitting through-bores, their entry funnels on the dock face, and the bore plate structure that houses the fittings. The bore plate is not a separate printed part -- it is integral to the tray (Sub-A), formed by cylindrical bosses extending inward from the rear wall interior face.

**Coordinate frame:** Tray frame. Origin at rear-left-bottom corner of tray outer envelope. X = width (0..160), Y = depth (0 = dock face, 155 = user side), Z = height (0 = floor bottom, 72 = top of walls). Print orientation: open top facing up, XY plane on build plate.

---

## 1. Mechanism Narrative (Rubric A)

**What the user sees and touches:** Nothing. Sub-D is entirely internal to the cartridge. The user never contacts the bore plate, the fittings, or the entry funnels directly. The dock-face funnels face the enclosure dock wall; the user-side fitting ports face the cartridge interior where tubes connect during factory assembly.

**What is stationary:** Everything in Sub-D is stationary during operation. The bore plate is integral to the tray. The 4 John Guest PP0408W fittings are press-fit into the bore plate and do not move in any degree of freedom once installed.

**What moves nearby:** The release plate (Sub-E, separate part) slides along Y on guide posts between the rear wall interior face and the dock-side body ends of the fittings. The release plate engages the fitting collets -- but the collets are part of the fitting, not part of Sub-D's printed geometry. Sub-D provides the rigid mounting that the release plate pushes against.

**How the fittings are captured:** Each fitting's barbell profile has a 9.31 mm OD center body flanked by two 15.10 mm OD body end sections. The bore plate has a 9.5 mm press-fit bore (12.2 mm deep) that grips the center body with 0.19 mm diametral interference. On both faces of the bore plate, 15.5 mm diameter x 2.0 mm deep counterbores recess the body-end-to-center-body shoulder transitions. The dock-side shoulder (15.10 mm to 9.31 mm step) bears against the dock-face counterbore rim. The user-side shoulder bears against the user-face counterbore rim. Together, these two shoulders plus the press-fit lock the fitting in all 6 DOF: the press-fit prevents radial translation and rotation; the shoulders prevent axial translation in both directions.

**How dock tubes reach the fittings:** Tubes from the enclosure dock pass through the rear wall (Y = 0 to Y = 8.5) via 8.0 mm clearance bores centered on the same axes as the fitting bores. On the dock face (Y = 0), conical entry funnels taper from 12.0 mm to 8.0 mm over 2.0 mm depth, guiding the tube stubs into alignment during cartridge insertion. The tubes then traverse the open gap between the rear wall interior (Y = 8.5) and the dock-side fitting port (Y = 15.9), passing through the release plate's 6.5 mm through-holes along the way, and push into the fitting's dock-side collet port.

**Assembly sequence for Sub-D fittings:** Before the release plate is placed on the guide posts, each fitting is pressed into its bore from the user side (higher Y). The user-side body end enters the 15.5 mm counterbore first, then the 9.31 mm center body engages the 9.5 mm press-fit bore. The fitting is pushed until the dock-side shoulder seats against the dock-face counterbore rim. A firm hand push is sufficient -- no tools required. The PETG bore wall deflects slightly (0.19 mm interference on a 9.5 mm bore = 2.0% strain, within PETG elastic range).

---

## 2. Constraint Chain Diagram (Rubric B)

```
[Fitting center body, 9.31 mm OD] --press-fit--> [Bore plate bore, 9.5 mm ID, 12.2 mm deep]
    ^ radial constraint: 0.19 mm interference fit prevents X/Z translation and rotation about Y
    ^ axial constraint (dock direction): dock-side shoulder (15.10 to 9.31 step) bears on
      dock-face counterbore rim (15.5 mm dia, 2.0 mm deep, at Y = 28.0)
    ^ axial constraint (user direction): user-side shoulder (9.31 to 15.10 step) bears on
      user-face counterbore rim (15.5 mm dia, 2.0 mm deep, at Y = 40.2)

[Bore plate bosses] --integral--> [Rear wall interior face at Y = 8.5]
    ^ bosses are solid PETG cylinders from Y = 8.5 to Y = 42.2 (33.7 mm total length)
    ^ boss OD = 20.0 mm, providing 2.25 mm wall around the 15.5 mm counterbore

[Dock tube stubs] --clearance--> [Rear wall tube bores, 8.0 mm ID, Y = 0 to 8.5]
    ^ 0.825 mm radial clearance on 6.35 mm OD tube
    ^ entry funnel (12.0 to 8.0 mm taper, 2.0 mm deep at Y = 0) guides tube alignment

[Release plate] --pushes against--> [Fitting dock-side collets at Y = 14.5 to 15.9]
    ^ bore plate provides the rigid reaction: collet force transmits through
      fitting body into bore plate shoulders, into tray rear wall
```

No unlabeled arrows. No unconstrained parts. The bore plate is the rigid backbone that transmits all collet release forces into the tray structure.

---

## 3. Parts and Features

### 3a. Bore Plate Bosses (4x, identical)

The bore plate is formed by 4 cylindrical bosses extending from the rear wall interior face into the cartridge interior. Each boss is a solid cylinder with a stepped bore cut through it.

| Parameter | Value | Source |
|-----------|-------|--------|
| Boss outer diameter | 20.0 mm | 4s doc: 2.25 mm wall around 15.5 mm counterbore |
| Boss base (Y-start) | Y = 8.5 | Rear wall interior face (Sub-A) |
| Boss tip (Y-end) | Y = 42.2 | User-side counterbore outer face (40.2 + 2.0) |
| Boss total length | 33.7 mm | 42.2 - 8.5 |
| Material | PETG | requirements.md printer spec; concept doc material selection |

Each boss center is coaxial with its corresponding fitting bore center (see section 3d).

**Wall between adjacent bosses:** At 20 mm center-to-center spacing, adjacent 20.0 mm OD bosses touch tangentially (20 - 20/2 - 20/2 = 0 mm gap). The bosses will merge into a continuous structure where they meet. This is acceptable -- it creates a stronger, stiffer bore plate. The merged region between any two adjacent bosses forms a bridge of solid material spanning the full Y depth (33.7 mm). In practice, modeling as 4 overlapping cylinders produces a single connected solid.

### 3b. Press-Fit Bore (4x, identical)

Each bore is a stepped profile cut along the Y axis through one boss.

| Feature | Diameter (mm) | Y-start | Y-end | Depth (mm) | Purpose |
|---------|---------------|---------|-------|------------|---------|
| Dock-side counterbore | 15.5 | 26.0 | 28.0 | 2.0 | Recess for dock-side body end shoulder; 15.10 mm to 9.31 mm transition seats here |
| Press-fit bore | 9.5 | 28.0 | 40.2 | 12.2 | Captures 9.31 mm OD center body; 0.19 mm diametral interference |
| User-side counterbore | 15.5 | 40.2 | 42.2 | 2.0 | Recess for user-side body end shoulder |

**Press-fit bore diameter rationale:** 9.5 mm bore for 9.31 mm center body = 0.19 mm interference. The 4s document specifies this. PETG at 2.0% circumferential strain is within elastic range for short-duration installation loads. The fitting is inserted once and stays permanently.

**Counterbore diameter rationale:** 15.5 mm for 15.10 mm body end OD = 0.40 mm diametral clearance. This is not a press fit -- the counterbore merely recesses the shoulder transition so the shoulder face bears flat against the bore plate face. The 0.20 mm radial clearance accommodates FDM dimensional variation.

### 3c. Rear Wall Tube Pass-Throughs (4x, identical)

These are clearance holes through the existing 8.5 mm rear wall (Sub-A geometry), coaxial with the fitting bores.

| Feature | Diameter (mm) | Y-start | Y-end | Depth (mm) | Purpose |
|---------|---------------|---------|-------|------------|---------|
| Entry funnel (dock face) | 12.0 at Y=0, tapering to 8.0 at Y=2.0 | 0 | 2.0 | 2.0 | Conical countersink guiding dock tube stubs |
| Tube clearance bore | 8.0 | 2.0 | 8.5 | 6.5 | Straight bore for 6.35 mm OD tube passage |

**Funnel taper angle:** From 12.0 mm to 8.0 mm over 2.0 mm depth = 2.0 mm radial reduction per side over 2.0 mm = 45-degree half-angle. This is a standard chamfer angle, printable without supports when the tray prints open-top-up (the funnel opens on the dock face, which is a vertical wall in print orientation -- the conical surface is a circular chamfer on a horizontal bore, fully self-supporting).

**Tube clearance rationale:** 8.0 mm bore for 6.35 mm tube = 1.65 mm diametral clearance (0.825 mm per side). This generous clearance accommodates angular misalignment of the dock tube stubs during cartridge insertion. The fitting collet, not the wall bore, provides the final tube centering.

### 3d. Bore Center Positions (X, Z)

2x2 grid centered on the rear wall. Wall center: X = 80.0, Z = 36.0.

| Bore | X (mm) | Z (mm) | Label |
|------|--------|--------|-------|
| 1 (lower-left) | 70.0 | 26.0 | Pump 1 inlet |
| 2 (lower-right) | 90.0 | 26.0 | Pump 1 outlet |
| 3 (upper-left) | 70.0 | 46.0 | Pump 2 inlet |
| 4 (upper-right) | 90.0 | 46.0 | Pump 2 outlet |

Center-to-center spacing: 20.0 mm in both X and Z.

**Clearance to tray interior walls (from 4s doc):**
- Bore 1 to left interior wall (X = 5): 70.0 - 7.55 = 62.45 mm. OK.
- Bore 1 to floor interior (Z = 3): 26.0 - 7.55 = 18.45 mm. OK.
- Bore 4 to right interior wall (X = 155): 155 - 90.0 - 7.55 = 57.45 mm. OK.
- Bore 4 to top edge (Z = 72): 72 - 46.0 - 7.55 = 18.45 mm. OK.
- Between adjacent counterbores (20 mm c-c, 15.5 mm counterbore dia): 20.0 - 15.5 = 4.5 mm wall. Adequate for FDM.
- Between adjacent bosses (20 mm c-c, 20.0 mm boss OD): 0 mm -- bosses merge (see 3a discussion).

### 3e. Bore Plate Merged Envelope

Because the 4 bosses at 20 mm spacing with 20 mm OD merge into a single connected solid, the bore plate's outer envelope in the XZ plane is approximately:

- X: 60.0 to 100.0 (bore centers at 70 and 90, minus/plus 10 mm radius)
- Z: 16.0 to 56.0 (bore centers at 26 and 46, minus/plus 10 mm radius)
- Y: 8.5 to 42.2

The merged shape in the XZ plane is a rounded cross/clover of 4 overlapping circles. Total XZ footprint is approximately 40 mm wide x 40 mm tall, well within the tray interior (150 mm x 69 mm interior cross-section).

---

## 4. Direction Consistency Check (Rubric C)

| Claim | Direction | Axis | Verified? | Notes |
|-------|-----------|------|-----------|-------|
| Fitting inserted from user side | Toward dock (decreasing Y) | -Y | Yes | User-side body end enters counterbore at Y=40.2, center body enters bore, dock-side shoulder seats at Y=28.0 |
| Dock-side shoulder bears against bore plate dock face | Toward dock (-Y) | -Y | Yes | Shoulder at Y=28.0 presses against counterbore rim at Y=28.0; reaction to collet release force pushing fitting toward dock |
| User-side shoulder bears against bore plate user face | Toward user (+Y) | +Y | Yes | Shoulder at Y=40.2 presses against counterbore rim at Y=40.2; reaction to tube insertion force |
| Dock tubes pass through rear wall toward user | Toward user (+Y) | +Y | Yes | Tubes enter funnel at Y=0, exit rear wall interior at Y=8.5, continue to fitting port at Y=15.9 |
| Entry funnel tapers inward (dock to user) | Taper narrows in +Y direction | +Y | Yes | 12.0 mm at Y=0, 8.0 mm at Y=2.0 |
| Bosses extend from rear wall interior toward user | Toward user (+Y) | +Y | Yes | Base at Y=8.5, tip at Y=42.2 |
| Release plate pushes collets toward dock | Toward dock (-Y) | -Y | Yes | Plate at Y=9.5..14.5 pushes collets from Y=14.5 toward Y=15.9 body face; collet compresses inward (-Y relative to fitting dock end face) -- wait, this needs clarification. The release plate moves toward higher Y (toward user) during squeeze, and the plate's user face pushes the collet inward (toward fitting center, which is +Y). Correcting: plate moves +Y, pushes collet +Y (inward). |

**Correction on release plate direction:** The decision document states the release plate moves "toward the fittings" during squeeze. The fittings are at higher Y than the plate. The plate moves from Y=9.5 toward Y=11.0 (1.5 mm in +Y direction). The plate's user-facing face (at Y=14.5 at rest, Y=16.0 at full travel) pushes the collet sleeve inward (+Y, into the fitting body). This is consistent: squeeze pulls the plate toward user (+Y), plate pushes collets inward (+Y). The constraint chain's reaction force goes through the fitting body into the bore plate dock-face counterbore rim at Y=28.0. All directions are consistent.

---

## 5. Interface Dimensional Consistency (Rubric D)

| Interface | Part A dimension | Part B dimension | Clearance | Source |
|-----------|-----------------|-----------------|-----------|--------|
| Center body to press-fit bore | 9.31 mm OD (caliper-verified) | 9.5 mm ID | -0.19 mm (interference) | Caliper photo 06; 4s doc |
| Body end to counterbore | 15.10 mm OD (caliper-verified) | 15.5 mm ID | +0.40 mm (clearance) | Caliper photo 01; 4s doc |
| Tube to rear wall bore | 6.35 mm OD (nominal) | 8.0 mm ID | +1.65 mm (clearance) | Nominal tube spec; 4s doc |
| Funnel mouth to funnel bore | 12.0 mm (funnel entry) | 8.0 mm (funnel exit) | N/A (taper) | 4s doc |
| Boss OD to adjacent boss OD | 20.0 mm each | 20.0 mm c-c spacing | 0 mm (merging) | 4s doc; intentional |
| Counterbore depth to shoulder height | 2.0 mm depth | 2.90 mm shoulder width (annular) | N/A (shoulder seats flush; counterbore recesses the OD transition zone, not the full shoulder width) | 4s doc; caliper-derived |
| Boss base to rear wall interior | Boss starts at Y=8.5 | Rear wall interior at Y=8.5 | 0 mm (integral) | 4s doc; bosses are part of tray |

No zero-clearance fit interfaces (the press-fit is intentional interference). No mismatched dimensions. The 0.19 mm interference is achievable with PETG's compliance on a Bambu H2C at 0.2 mm layer height (concept doc notes this should be verified with a test print).

---

## 6. Assembly Feasibility Check (Rubric E)

### Assembly Sequence (Sub-D features during tray assembly)

The bore plate bosses, tube pass-throughs, and entry funnels are all integral to the tray -- they exist after the tray is printed. The only assembly action for Sub-D is pressing the 4 fittings into the bores.

1. **Tray is printed** with bore plate bosses, tube clearance bores, and entry funnels already formed.
2. **Insert fitting 1** from the user side: orient fitting with long axis along Y, push user-side body end into the user-side counterbore (15.5 mm, plenty of clearance for the 15.10 mm body end). Continue pushing until the center body (9.31 mm) engages the 9.5 mm bore. Press firmly until the dock-side shoulder seats against the dock-face counterbore rim at Y=28.0.
3. **Repeat for fittings 2, 3, 4.** Order does not matter -- bosses are spaced far enough apart (4.5 mm between counterbore edges) that fingers can reach each bore.
4. **Verify:** Each fitting's dock-side body end protrudes from the bore plate dock face (body end extends from Y=15.9 to Y=28.0), and the dock-side collets are accessible at Y=14.5 to Y=15.9 for release plate engagement.

**Can a hand reach the bores?** Yes. The bore plate is at Y=28.0 to Y=42.2, which is 28 mm from the dock face. The tray is open-top and open-front. A hand can easily reach in from the top or front to press fittings into the bores. The bores are centered at X=70/90, Z=26/46 -- roughly in the middle of the tray cross-section, not in a corner.

**Can fittings be removed for service?** Yes. After removing the lid and front bezel (snap-fit, tool-free), and sliding the release plate off the guide posts, each fitting can be pushed back out through its bore from the dock side using a 9 mm diameter rod inserted through the rear wall tube clearance bore (8.0 mm bore is too small -- a rod cannot fit). Alternative: push from the dock side by inserting a tube or rod through the entry funnel and applying force to the fitting's dock-side port face. The 8.0 mm bore is smaller than the 9.31 mm center body, so a push-rod cannot pass through the rear wall bore to reach the fitting.

**DESIGN GAP: Fitting removal path.** The 8.0 mm rear wall clearance bore is smaller than the 9.31 mm center body. A fitting cannot be pushed out from the dock side through the rear wall. Removal must be done from the user side: grip the user-side body end (15.10 mm OD, protruding from Y=40.2 to Y=52.3) with fingers or pliers and pull toward the user (+Y). The press-fit force is modest (0.19 mm interference on PETG), so hand extraction should be feasible. If not, a tube inserted into the user-side port could serve as a handle. This is acceptable for a "rare" service event (Tier 2 in the concept doc service hierarchy).

### No Trapped Parts

The bore plate bosses are integral to the tray. The fittings are pressed in before the release plate, guide posts, lid, or bezel are installed. No subsequent assembly step blocks access to the fittings. The release plate slides onto the guide posts after the fittings are installed and can be removed first during disassembly.

---

## 7. Part Count Minimization (Rubric F)

| Part pair | Permanently joined? | Move relative? | Same material? | Verdict |
|-----------|-------------------|----------------|----------------|---------|
| Bore plate bosses + tray rear wall | Yes (integral, printed as one) | No | Yes (PETG) | Already one part. Correct. |
| Fitting + bore plate | Press-fit (permanent in use, removable for service) | No (stationary once installed) | No (acetal fitting in PETG tray) | Must be separate: different materials, off-the-shelf part. Correct. |
| Boss 1 + Boss 2 (adjacent) | Yes (merged solid) | No | Yes | Already one part (merged bosses). Correct. |
| Entry funnel + rear wall | Yes (integral) | No | Yes | Already one part. Correct. |

Sub-D adds zero separate printed parts. Everything is integral to the tray. The only separate items are the 4 off-the-shelf John Guest fittings, which must be separate (different material, purchased part). Part count is minimized.

---

## 8. Complete Dimension Table

All values in tray frame (mm). All bore features are coaxial per bore position (section 3d).

| Parameter | Value | Source |
|-----------|-------|--------|
| Bore grid center (X, Z) | (80.0, 36.0) | 4s doc: centered on rear wall |
| Bore center-to-center spacing | 20.0 x 20.0 (X, Z) | 4s doc |
| Bore 1 center (X, Z) | (70.0, 26.0) | 4s doc |
| Bore 2 center (X, Z) | (90.0, 26.0) | 4s doc |
| Bore 3 center (X, Z) | (70.0, 46.0) | 4s doc |
| Bore 4 center (X, Z) | (90.0, 46.0) | 4s doc |
| Boss outer diameter | 20.0 | 4s doc |
| Boss Y range | 8.5 to 42.2 | 4s doc (8.5 base + 33.7 length) |
| Boss total length | 33.7 | 42.2 - 8.5 |
| Dock-side counterbore diameter | 15.5 | 4s doc; 0.40 mm clearance on 15.10 mm body end |
| Dock-side counterbore Y range | 26.0 to 28.0 | 4s doc |
| Dock-side counterbore depth | 2.0 | 4s doc |
| Press-fit bore diameter | 9.5 | 4s doc; 0.19 mm interference on 9.31 mm center body |
| Press-fit bore Y range | 28.0 to 40.2 | 4s doc |
| Press-fit bore depth | 12.2 | 4s doc; matches center body length |
| User-side counterbore diameter | 15.5 | 4s doc |
| User-side counterbore Y range | 40.2 to 42.2 | 4s doc |
| User-side counterbore depth | 2.0 | 4s doc |
| Rear wall tube bore diameter | 8.0 | 4s doc; 0.825 mm radial clearance on 6.35 mm tube |
| Rear wall tube bore Y range | 2.0 to 8.5 | 4s doc (straight portion after funnel) |
| Entry funnel large diameter | 12.0 | 4s doc |
| Entry funnel small diameter | 8.0 | 4s doc |
| Entry funnel Y range | 0 to 2.0 | 4s doc; 2.0 mm depth on dock face |
| Entry funnel half-angle | 45 degrees | Derived: (12.0 - 8.0) / 2 / 2.0 = 1.0, arctan(1.0) = 45 deg |
| Merged boss envelope (XZ) | X: 60..100, Z: 16..56 | Derived: bore centers +/- 10 mm radius |

---

## 9. Design Gaps

1. **Fitting removal method:** The 8.0 mm rear wall clearance bore does not allow a push rod to reach the fitting from the dock side (center body is 9.31 mm). Removal must be by pulling the user-side body end. This is acceptable for rare service but should be verified during prototyping. If extraction force is too high for bare hands, a simple tube-as-handle technique (insert a short tube into the user-side port for grip) resolves it. No geometry change needed -- this is a procedure note.

2. **Boss merge geometry:** The 4 bosses merge where they touch (0 mm gap at 20 mm spacing with 20 mm OD). The CAD model should union these into a single solid. If the merged cross-shape creates stress concentrations at the narrow necks (where two circles barely overlap), adding a small rectangular bridge plate (e.g., X = 60..100, Z = 16..56, Y = 8.5..42.2, 2-3 mm thick backing plate behind the bosses) would stiffen the assembly. This is a CAD/FEA decision, not a design gap requiring specification changes. The 4s document noted this as a deferred choice and the merged-cylinder approach is the baseline.
