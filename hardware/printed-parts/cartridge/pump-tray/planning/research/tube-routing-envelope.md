# Tube Routing Requirements and Cartridge Envelope Constraints
## Two Kamoer KPHM400 Pumps, Side-by-Side Pump Tray

**Research date:** 2026-03-29
**Source documents:** geometry-description.md (pump + John Guest union), raw-images (photos 01, 02, 10, 11, 13, 17), requirements.md, vision.md
**Web sources:** FreshWaterSystems (PP201008W length), FixSupply (PE tubing bend radius), JG tech-spec PDF

---

## 1. Tube Stub Exit Geometry

### What the photos show

**Photo 17** ("pump-head-with-connectors-height-82.82mm"): The calipers span vertically across the pump head with both tube stubs in the jaws — top jaw on the outer face of the upper stub, bottom jaw on the outer face of the lower stub. Reading: **82.82mm**. The pump head face is **62.6mm** tall.

**Photo 03** (front face, 62.61mm): Both white BPT tube stubs are clearly visible, one above center, one below center, both exiting near the horizontal centerline of the pump face (i.e., vertically offset from pump center, horizontally near center).

**Photo 10** (side view, 68.74mm): Calipers span from the tip of the forward-pointing tube stub to some rear reference on the pump head. Pump head body is ~48mm deep. The stub tip extends ~20–21mm beyond the pump face.

**Photo 11** (side view, 65.15mm): A second side measurement showing the pump with the tube stub at top in frame and the lower stub below. This appears to measure head height including stub bodies (not stub tips).

**Photo 13** (51.68mm): Measures pump head front face to bracket junction face (~48mm head + ~3.5mm bracket), with upper tube stub visible above — confirms stub exits from near the top edge of the face.

### Derived geometry

The BPT connectors are white plastic barbed fittings for 4.8mm ID / 8.0mm OD BPT tubing. The outer diameter of the connector body/barb assembly is estimated at **~8–10mm**.

**Stub center-to-center (vertical):**
- Photo 17 spans outer face of upper stub to outer face of lower stub = 82.82mm
- Estimated connector OD ≈ 8mm
- C-to-C = 82.82 − 8 = **~74.8mm** (call it **75mm** for working purposes)

**Stub position relative to pump face:**
- Pump face is 62.6mm tall, centered at Z = 0
- Each stub center is at ±37.4mm from pump center
- Pump face edge is at ±31.3mm from center
- Each stub center is therefore **~6mm outside the pump face boundary** (stubs exit near the very top and bottom corners of the front face, not at mid-height)
- Stubs appear horizontally centered on the front face (X ≈ 0 relative to pump centerline)

**Stub protrusion depth (forward, Y-axis):**
- Photo 10: 68.74mm total from stub tip to pump head rear reference
- Pump head depth: ~48mm
- Stub tip extends approximately **20–21mm forward** from the pump face
- The BPT flexible tubing attached to the stub adds further: the geometry description estimates 30–50mm total from pump face to tube end
- **Working assumption: 30mm of forward clearance required for the hard stub + attached flexible tubing before any fitting or bend begins**

### Summary for design

| Parameter | Value | Confidence |
|-----------|-------|------------|
| Stub C-to-C vertical | ~75mm | MEDIUM (derived from photo 17 + stub OD estimate) |
| Stub horizontal position | Near pump face centerline | MEDIUM (photo 03 visual) |
| Stub tip protrusion from face | ~20–21mm (hard stub) | MEDIUM (derived from photo 10) |
| Effective clearance needed | 30mm forward of pump face | LOW-MEDIUM (working assumption) |
| Stubs exit beyond face boundary | ~6mm above/below face edge | MEDIUM (derived) |

**Flag:** The exact stub diameter and exact horizontal (X) offset of each stub from pump centerline are not caliper-verified. The geometry description document lists these as remaining unknowns. The 75mm C-to-C is a derived estimate, not a direct measurement. Verify by direct caliper measurement of one pump before finalizing tray geometry.

---

## 2. Tube Transition: BPT to 1/4" Hard Line

### The problem

The pump uses BPT tubing connectors (4.8mm ID / 8.0mm OD BPT tubing, barbed stub on pump face). The rest of the system uses 1/4" OD (6.35mm) hard polyethylene tubing with John Guest push-fit connections throughout.

These are different tube standards:
- BPT: 8.0mm OD / 4.8mm ID (metric soft flexible)
- John Guest: 1/4" OD = 6.35mm OD / ~4.8mm ID (imperial semi-rigid)

The inner diameters are nearly identical (both ~4.8mm). The outer diameters differ (8.0mm vs 6.35mm). This means a **reducing union** is needed at the transition.

### The fitting: John Guest PP201008W (or PI201008S)

John Guest makes a **5/16" × 1/4" reducing union** in both polypropylene white (PP201008WP) and acetal gray (PI201008S). This fitting accepts:
- 5/16" OD = 7.94mm ≈ 8.0mm (the BPT tube OD) on one end
- 1/4" OD = 6.35mm on the other end

**This is the correct adapter.** The 5/16" end accepts the BPT tubing directly. The 1/4" end accepts the standard 1/4" hard polyethylene system tubing.

### Fitting envelope

The John Guest PP0408W (1/4" × 1/4" straight union, caliper-verified in repo) is **41.80mm long** with collets extended. The reducing union (5/16" × 1/4") has asymmetric ends. FreshWaterSystems lists it as **1.75 inches = 44.5mm** overall length.

As a reducing union the two ends have different collet/body ODs:
- 5/16" end body OD: estimated ~16–17mm (slightly larger than the 1/4" end's 15.10mm, scaling by tube ratio)
- 1/4" end body OD: 15.10mm (caliper-verified on the PP0408W, same mechanism)
- Central body: narrower waist, ~9–10mm

**Working envelope for the PP201008W:**
- Overall length: ~44–45mm (collets extended)
- Max OD: ~16–17mm at 5/16" end

**Installation approach:**

The pump BPT stub carries attached flexible BPT tubing (~30mm stub + tubing). The transition point (where BPT transitions to 1/4" hard line) should happen in the forward clearance zone in front of the pump face — either immediately at the stub exit, or after a short (~50mm) run of flexible BPT tubing. The PP201008W reducing union terminates the BPT stub tubing and begins the 1/4" hard line system.

**Working assumption:** The reducing union sits in the tube routing zone forward of the pump face, and the 1/4" hard line exits the reducing union heading rearward (or laterally) toward the John Guest union fittings in the rear wall.

---

## 3. Minimum Bending Radius for 1/4" OD Semi-Rigid Polyethylene

### Specification

Multiple sources confirm: for 1/8" ID × 1/4" OD polyethylene tubing (the standard John Guest system tube, ASTM D2737), the **minimum bend radius is 3/4 inch = 19mm**.

This is consistent with general PE tubing guidance: thin-wall flexible PE has a minimum bend radius of ~3× OD for short-term bends, which for 6.35mm OD = ~19mm.

**John Guest LLDPE (Linear Low-Density PE) tubing** — the specific type used with John Guest push-fit fittings — is semi-rigid and behaves similarly.

### The u-turn problem

The tube stubs exit **forward** from the pump face. The system tubing and John Guest quick connects are in the **rear wall** of the cartridge. The tube must therefore execute a 180° reversal (u-turn) somewhere in the cartridge.

For a 180° bend with 19mm minimum radius:
- The bend diameter = 2 × 19mm = **38mm**
- The tube centerline at the apex of the u-turn is 19mm ahead of the start of the bend
- Total depth consumed by the u-turn: from where the tube begins to bend to where it exits back rearward = **~38–40mm**

However, the u-turn does not have to happen immediately at the pump face. The flexible BPT section (~30mm), the reducing union (~44mm long), and a short run of 1/4" hard line before the bend all add up. The key question is: **does the u-turn happen inside the cartridge front space, or can the tube run forward far enough to exit the front face of the cartridge and loop back?**

Given the vision (cartridge is a sealed unit, tubes do not exit the front face of the cartridge), the u-turn must occur within the cartridge body. The relevant constraint is:

**Minimum forward depth in front of the pump face to execute a u-turn and return:**
- Tube exits pump stub forward
- BPT flexible section: ~30mm
- Reducing union length: ~44mm (partially overlaps with stub run)
- U-turn radius: 19mm
- Total forward projection from pump face to u-turn apex: conservatively **60–70mm**

**Flag:** The u-turn can be eliminated entirely if the tube routing is redesigned. Instead of a u-turn, the 1/4" hard line can run laterally (sideways) from the reducing union to a 90° elbow fitting, then rearward. This reduces forward clearance requirement to just: stub protrusion + BPT run + reducing union + elbow (~20mm stub + ~20mm BPT + 44mm union + elbow OD). With a right-angle push-fit elbow, lateral routing needs ~50–60mm of forward depth and ~20–25mm lateral clearance per tube — but eliminates the 38mm u-turn depth.

**Design recommendation:** Use 90° push-fit elbows (John Guest PE0408W or equivalent) at the reducing union exit to turn the 1/4" line 90° rearward or laterally before routing to the rear wall. This eliminates the u-turn constraint entirely and reduces forward clearance requirement to approximately **50–55mm** from pump face to cartridge front wall.

---

## 4. Cartridge Envelope Derivation

### Given dimensions (from geometry description, caliper-verified)

| Component | Dimension | Source |
|-----------|-----------|--------|
| Pump head face | 62.6mm × 62.6mm | Caliper HIGH |
| Pump head depth | 48mm | Caliper HIGH |
| Motor + adapter behind bracket | ~68mm | Caliper (116mm total − 48mm head) |
| Bracket width | 68.6mm | Datasheet + caliper |
| Total pump assembly depth | 116mm (to motor nub) | Caliper HIGH |
| JG PP0408W union length (collets extended) | 41.8mm | Caliper HIGH |
| JG PP0408W body end OD | 15.1mm | Caliper HIGH |
| JG reducing union (PP201008W) length | ~44–45mm | FreshWaterSystems (1.75") |
| Tube stub protrusion (hard stub) | ~20mm | Derived (photo 10) |
| BPT flexible tubing + stub total | ~30mm | Working assumption |

### Width calculation (X-axis, side-by-side)

Two pumps mounted side by side on a shared tray plate. Each pump's bracket is 68.6mm wide. The mounting holes are on a 48mm × 48mm square pattern, centered in the bracket.

For each pump, clearance is needed:
- Bracket half-width: 34.3mm from pump centerline to bracket edge
- Pump head half-width: 31.3mm from pump centerline to head edge
- Bracket protrudes 3mm beyond head per side

Between the two pumps, minimum inter-pump clearance needed:
- Wire harness routing along motor body side: ~5–8mm
- FDM wall between pumps: ~2–3mm (structural)
- Minimum inter-pump gap: **10mm** (bracket edge to bracket edge)

Outside the outer pumps, clearance needed:
- FDM outer wall: 2mm minimum
- Rail/groove feature depth (outside): 4–6mm
- Total outside clearance per side: **8–10mm** from bracket edge to outer wall

**Minimum width:**
= (2 × bracket half-width) + inter-pump gap + (2 × outer clearance)
= (2 × 34.3mm) + 10mm + (2 × 9mm)
= 68.6 + 10 + 18
= **~97mm**

Round up with margin: **~105mm minimum width**. A comfortable working width is **110–120mm** to allow real wiring clearance between pumps and rail feature clearance on outer walls.

**Working assumption: 110mm cartridge width.**

### Depth calculation (Y-axis, front to back)

Three depth zones:

**Zone A — Front clearance (forward of pump face):**
- Tube stub + BPT section: ~30mm
- Reducing union (forward-pointing): ~44mm — but with 90° elbow strategy, this runs forward only ~20mm before turning
- With elbow strategy: ~50mm forward of pump face needed
- Add FDM front wall thickness: 2–3mm
- Zone A total: **~52–55mm** forward of pump face

**Zone B — Pump assembly:**
- Pump head + motor: 116mm from front face to motor nub tip
- Tray plate (at bracket face): 3–4mm
- Motor nub clearance behind tray: 5mm minimum
- Zone B total: **~116mm + 5mm nub clearance = 121mm** (but tray plate is at Y=48mm, motor nub needs clearance behind plate)
- Simplified: pump occupies 116mm from its own front face
- Zone B counted from pump face: **116mm + 5mm nub clearance = 121mm**

Wait — Zone A and Zone B overlap at the pump face. The total depth is:

Total cartridge depth = Zone A (forward of pump face) + pump assembly depth + rear zone

**Zone C — Rear zone (behind motor):**
- Motor terminal clearance: 5mm
- Wiring routing: 10mm
- John Guest union fittings (PP0408W) mounted in rear wall, collets extended: 41.8mm
  - These are inline with the tube flow: tube from motor side runs rearward, inserts into the JG union from the inside face of the rear wall
  - The fitting sticks out into Zone C: ~21mm (half the fitting) from the inner wall face
- FDM rear wall thickness: 4–5mm (structural, press-fit for JG fitting)
- Zone C total from motor nub: ~35–40mm

**Total depth = Zone A + pump length + Zone C**
= 55mm + 116mm + 38mm
= **~209mm**

Round to working assumption: **~210mm cartridge depth.**

**Flag — can depth be reduced?** Yes, with these strategies:
1. Routing the 1/4" hard line laterally then rearward in Zone A (90° elbow) reduces Zone A from ~55mm to ~35mm, saving 20mm.
2. The JG fittings in the rear wall can be recessed into the wall (pocket bore), reducing Zone C by ~10mm.
3. Minimum achievable depth (aggressive): ~175–185mm.

**Conservative working assumption: 200mm depth** (allows routing flexibility, wiring, and assembly access).

### Height calculation (Z-axis)

Pump head is 62.6mm tall. The tube stubs extend ~6mm above and below the head face boundary (derived from photo 17: total span 82.82mm), but this is in the forward direction — the stubs exit from the face, not the top/bottom surfaces.

The tray plate sits at the bracket/junction face. The motor cylinder (~35mm diameter) hangs behind the tray. The motor needs no additional Z clearance beyond the pump head height.

The cartridge must also accommodate:
- Wiring from motor terminals running down/sideways: 8–10mm below motor
- FDM floor and ceiling walls: 2–3mm each
- FDM rail groove features in floor/ceiling: 4–5mm per side (if rails are horizontal)

**Minimum height:**
= pump head height + floor wall + ceiling wall + rail feature
= 62.6mm + 3mm + 3mm + 5mm
= **~74mm**

Add 5mm clearance above/below motor body for wiring: ~80mm.

**Working assumption: 80mm cartridge height.**

### Envelope summary

| Dimension | Minimum | Working Assumption | Notes |
|-----------|---------|-------------------|-------|
| Width (X) | ~97mm | **110mm** | Two pumps side-by-side, 10mm inter-pump gap, rail features |
| Depth (Y) | ~175mm | **200mm** | Forward tube routing + pump + rear JG fittings |
| Height (Z) | ~74mm | **80mm** | Pump face + walls + rail groove |

**Working cartridge envelope: 110mm × 200mm × 80mm (W × D × H)**

These are starting assumptions. The depth is the most uncertain dimension — it depends heavily on whether the tube routing in Zone A uses 90° elbows or u-turns, and how much of Zone C the JG fittings can be recessed.

---

## 5. Cartridge-to-Enclosure Interface: Rail Cross-Section

### Requirements

- Module width: ~110mm
- User slides cartridge in by hand, front-to-back
- Must be stable (no wobble) once docked
- Must release cleanly when tubes are disconnected
- Printed in FDM, so rail geometry must be manufacturable without supports

### Cross-section comparison

**T-slot:** Standard in aluminum extrusion (e.g., 20×20 profile). Complex to print accurately. The T-slot requires printing the overhanging T-head, which violates the 45° FDM rule without designed chamfers. Requires careful tolerance management. Better suited to aluminum extrusion than FDM.

**Rectangular tongue-and-groove (simple rail):** A rectangular tongue on the cartridge sides slides into a rectangular groove on the enclosure. Simple to print. No overhang issues if the groove is taller than wide (or chamfered entry). Easy to add tolerance adjustment. Provides 2-axis constraint (vertical + lateral) when engaged. Low manufacturing risk.

**Dovetail:** Angled sides (typically 10–15° draft angle from vertical). Self-centers as it slides in. Provides strong pull-out resistance without a latch (the angled faces resist vertical separation). The overhang is manageable at 10–15° (well within the 45° FDM constraint). Widely used for FDM sliding joints.

### Recommendation: Rectangular tongue-and-groove with chamfered entry

For a 110mm wide cartridge that a user slides in by hand:

**Rail cross-section:** Rectangular tongue, 5mm wide × 4mm tall, on the top and bottom outer edges of the cartridge. Matching groove in the enclosure. Chamfer the leading edge of the tongue at 45° × 1mm for easy insertion.

**Engagement depth for stability:** For a module with a 200mm slide depth, adequate engagement is provided once the cartridge is ~30–40mm inserted. Full engagement (cartridge fully docked) has the full 200mm rail in contact with the enclosure groove. No stability concern at full insertion.

**Lateral clearance:** 0.2mm per side (FDM sliding fit per requirements.md). This gives a snug but free-sliding fit.

**Vertical constraint:** The rail depth (4mm) provides positive vertical constraint — the cartridge cannot tilt or drop once on rails.

**Dovetail is the superior option** if print orientation is managed correctly: a 12° dovetail (12° from vertical on each side, total 24° included angle) has no overhang concern, provides pull-out resistance, and self-aligns during insertion. For this application a dovetail on top and bottom edges is recommended over rectangular tongue-and-groove because:
1. Pull-out resistance means the cartridge cannot accidentally slide out once docked
2. The quick-connect release requires the cartridge to stay in position while the user squeezes the release mechanism — the dovetail provides the reaction force without additional latches
3. Self-centering on insertion improves UX

**Working specification for the rail interface:**
- Profile: Sliding dovetail
- Included angle: 24° (12° per face from vertical)
- Tongue width at widest point: 6mm
- Tongue height: 5mm
- FDM clearance: 0.2mm per face (total 0.4mm wider groove than tongue)
- Chamfered entry: 2mm × 45° lead-in on both tongue and groove
- Engagement depth for stable docking: minimum 20mm engaged (cartridge 20mm+ inserted)
- Full docking: cartridge fully seated, 200mm of rail engaged
- Rails on both top and bottom of cartridge (redundant stability, prevents rotation about slide axis)

---

## 6. Connected Findings for the Pump-Tray Design Agent

### Direct consequences for the tray plate

1. **Tube stub forward clearance:** The tray plate must have its front face set back far enough to give the tube stubs ~30mm of free space. Since the stubs extend 20mm forward of the pump face and flexible BPT tubing adds more, the front wall of the cartridge must be at least **50–55mm forward of the pump face** if routing via 90° elbows, or **75–90mm forward** if u-turns are used.

2. **Stub height span:** The stubs exit ~6mm outside the pump face boundary at top and bottom. The tray floor and ceiling must clear the stub zone. If the pump face is centered in the cartridge height (80mm), the stubs occupy from -37.4mm to +37.4mm of Z — which fits within the 80mm height with ~2.6mm clearance each side (tight). The working height of 80mm may need to be raised to **85mm** to give comfortable stub clearance.

3. **Inter-pump tube routing:** With two pumps side-by-side, the four BPT tube stubs (two per pump, top and bottom) exit in the same forward space. The routing for the inner pump stubs (the stubs closest to the center gap between pumps) must not collide with the other pump's routing. With the pumps 10mm apart bracket-edge-to-bracket-edge, the inner stubs of each pump are ~5mm apart from each other at the pump face, and their tubing diverges forward. A 90° elbow on each inner stub routing laterally outward solves the collision problem.

4. **Rear wall JG fitting positions:** The four JG PP0408W fittings (two per pump, inlet + outlet) mount in the rear wall. Their through-axis is parallel to the cartridge depth axis (Y). Each fitting is 41.8mm long (collets extended), 15.1mm OD at body ends. They can be press-fit into a pocket bore (9.5mm bore for the 9.31mm center body) in a 6–8mm thick rear wall, with collets protruding ~21mm rearward (outside the enclosure dock, where the enclosure tube stubs insert). The collet side facing inward is pressed by the release plate.

5. **Motor bore in tray plate:** The tray plate needs a bore of ~37mm diameter (35mm motor + 1mm clearance per side) and four M3 screw holes at 48mm × 48mm square pattern, per the pump bracket.

6. **Cartridge width note:** At 110mm working width, the printer build plate (325mm × 320mm) can accommodate two cartridge bodies printed side-by-side, or the cartridge printed in a single piece. A 110mm × 200mm footprint fits on the Bambu H2C in any orientation.

### Uncertainty register

| Item | Uncertainty | Impact | How to resolve |
|------|-------------|--------|---------------|
| Tube stub C-to-C (75mm) | Derived, not direct measurement | Affects tray floor/ceiling clearance | Caliper directly: measure stub centerline positions on front face |
| Tube stub horizontal (X) offset | Not measured | Could push stub outside pump width envelope | Caliper or visual confirmation |
| Hard stub protrusion depth (~20mm) | Derived from photo 10 | Affects minimum Zone A depth | Caliper directly: measure stub tip to pump face |
| BPT flexible tubing length (assumed 30mm) | Estimate | Affects Zone A total | Measure or trim to fit |
| Reducing union (PP201008W) length (44mm) | Web-sourced, not caliper-verified | Affects fitting envelope | Caliper the actual fitting before routing |
| Motor diameter (~35mm) | Low-confidence (photos 15/16) | Affects bore hole diameter | Caliper directly |
| Rail dovetail FDM tolerance | Standard 0.2mm per requirements.md | Affects sliding fit quality | Calibrate with test print |
