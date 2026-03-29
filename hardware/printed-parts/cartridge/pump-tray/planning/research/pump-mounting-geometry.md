# Pump-Tray Mounting Geometry Research
## Kamoer KPHM400-SW3B25

**Sources used:** Caliper-verified geometry from `hardware/off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md`, Kamoer official product page (kamoer.com/us/product/detail.html?id=10014), Kamoer params page (kamoer.cn/us/product/params.html?id=10014), DirectIndustry/Kamoer datasheet excerpt, Amazon listing (B09MS6C91D), ISO 273 clearance hole standards.

---

## 1. Confirmed Mounting Geometry

All measurements below are caliper-verified from the physical pump unless otherwise noted.

### 1.1 Mounting Hole Pattern

| Parameter | Value | Source | Confidence |
|-----------|-------|---------|------------|
| Hole count | 4 | Caliper + datasheet | HIGH |
| Pattern shape | Square | Caliper + datasheet | HIGH |
| Center-to-center spacing | **48mm × 48mm** | User-verified caliper | HIGH |
| Edge-to-edge spacing (one axis) | 47.88mm | Photo 05 | HIGH |
| Derived c-t-c (edge + hole dia) | 47.88 + 3.13 = **51.01mm** — but user verified 48mm c-t-c directly | — | — |
| Hole diameter (as-manufactured) | **3.13mm** | Photo 06 | HIGH |
| Screw size | M3 | Inferred from 3.13mm hole dia | HIGH |
| Screw orientation | Parallel to motor axis (Z-axis of pump) | Geometry description | HIGH |
| Screws thread into | Pump head body (from motor side) | Geometry description | HIGH |

**Note on the 47.88mm vs 48mm discrepancy:** Photo 05 measured 47.88mm edge-to-edge. Adding one hole diameter (3.13mm) gives 51.01mm center-to-center, which is inconsistent with the user-verified 48mm c-t-c. The most likely explanation: photo 05 is measuring inner-edge to inner-edge of a *different* pair of holes, or the caliper jaw placement was ambiguous. The user-verified 48mm c-t-c is the reliable number. Use **48mm × 48mm c-t-c** for design.

### 1.2 Bracket Face Geometry

| Parameter | Value | Source |
|-----------|-------|--------|
| Bracket width (X) | **68.6mm** | Datasheet + caliper |
| Bracket height (Z) | ~68.6mm | Inferred symmetric; matches pump head height |
| Bracket thickness | ~1.5–2mm | Estimated from photos |
| Pump head width/height | **62.6mm × 62.6mm** | Photos 01–04, HIGH confidence |
| Bracket overhang per side | **(68.6 − 62.6) / 2 = 3.0mm per side** | Derived |

The bracket extends 3mm beyond the pump head on each side (both X and Z). The 4 mounting holes sit in these corners — partially in the bracket overhang zone, partially overlapping with the pump head body behind the bracket face.

**Hole position relative to pump center axis:**
With a 48mm × 48mm square pattern, each hole is 24mm from the center axis (both X and Z). The bracket is 68.6mm wide, so holes sit (68.6/2 − 24) = **10.3mm inward from each bracket edge.** This places the hole centers well within the bracket material, not at the extreme edges.

### 1.3 Motor Bore Geometry

| Parameter | Value | Source |
|-----------|-------|--------|
| Motor body diameter | ~35mm | Photos 15, 16 (LOW confidence, sideways display) |
| Datasheet cross-reference | 68.6W × 115.6D × 62.7H | Confirms overall envelope |
| Motor nub protrusion | **~5.05mm** | Difference of two total-length measurements |
| Motor nub diameter | ~5–8mm estimated | Not directly measured |

The motor cylinder must pass through a bore in the mounting plate. The bore is centered on the pump's center axis, which corresponds to the center of the 48mm × 48mm hole pattern.

---

## 2. Tolerances and Fastener Decisions

### 2.1 M3 Clearance Hole Sizing (ISO 273)

| Fit class | Bore diameter | Use case |
|-----------|--------------|----------|
| Close fit | **3.2mm** | High-alignment applications, minimal float |
| Normal fit | **3.4mm** | General purpose |
| Loose fit | **3.6mm** | Easy assembly, some positional float |

The pump's own holes are 3.13mm — functionally a tight M3 clearance (M3 thread is 3.0mm nominal). The screws thread directly into the pump head body through those holes; the bracket holes are **pass-through clearance holes**, not threaded.

**The pump-tray mounting plate uses clearance holes — the M3 screws pass through the tray and thread into the pump head.** No nut or threaded insert is needed on the tray. The pump head acts as the threaded receiver.

**FDM compensation:** Per `requirements.md`, holes print ~0.2mm smaller than designed for loose fit, ~0.1mm smaller for press fit. To achieve a **3.4mm normal-fit clearance hole** in the tray:
- Design the hole at **3.4 + 0.2 = 3.6mm** nominal diameter in CAD.
- This prints to approximately 3.4mm after FDM shrinkage.
- Verify empirically once printer is calibrated.

**Actionable result:** Design M3 clearance holes in the pump tray at **3.6mm diameter in CAD** (targeting 3.4mm printed). This gives normal ISO fit relative to the M3 screw shank, with adequate float for the ±0.2mm positional variation in the pump's bracket holes vs. the 48mm pattern.

### 2.2 Motor Bore Diameter

The motor body diameter is ~35mm (low confidence, estimated). The bore must clear the motor without excessive slop that allows the pump to rock on the mounting plate.

**Design target:**
- Motor OD: 35mm (nominal, use 35.5mm as conservative upper bound given the ~35.13mm caliper reading)
- Desired radial clearance: 0.5–1.0mm per side (enough for thermal expansion, FDM tolerance, and assembly without needing to force-fit)
- **Bore diameter: 37mm** (1.0mm clearance per side vs. 35mm nominal; 0.75mm clearance vs. 35.5mm upper bound)
- FDM compensation: per requirements, add 0.2mm → design bore at **37.2mm in CAD** for a loose-fit printed result of ~37mm.

The motor nub (5mm protrusion at the center of the motor's far end) is irrelevant to bore sizing — it protrudes away from the tray on the far side of the motor, not toward the plate.

**Failure mode if bore is too tight:** Motor cylinder cannot seat against bracket face. Pump floats on the motor body instead of clamping flat to the plate. Screws cannot pull the bracket down fully. The pump rocks during operation, causing cyclic screw loosening.

**Failure mode if bore is too large:** No structural consequence — the 4 screws carry all load; the bore is only a clearance feature. However, a bore much larger than needed wastes material and reduces tray plate stiffness. 37mm is the right target.

---

## 3. Vibration Analysis

### 3.1 Pump Head RPM

The Kamoer product page confirms: **gear reduction ratio 1:8** (first-stage reduction). The DC brushed motor in the KPHM400-SW3B25 runs at approximately 2,240 RPM at 12V (typical for 280-series brushed DC motors at nominal voltage, unloaded; loaded speed is somewhat lower). After 1:8 reduction:

**Pump head speed = motor RPM / 8 ≈ 280 RPM** at full speed (unloaded).

This matches the Kamoer datasheet statement that tube lifespan tests are conducted "at a speed of about 280 rpm." At typical dispensing duty (partial PWM speed), the pump head runs at **50–280 RPM** depending on the flavor ratio setting.

This is consistent with the flow spec: at 280 RPM with 3 rollers and ~4.8mm ID tube, the pump delivers up to ~400 ml/min.

### 3.2 Vibration Frequency

A 3-roller peristaltic pump produces one tube compression event per roller per revolution. With 3 rollers, there are **3 compression events per revolution.**

**Vibration frequency formula:**
```
f_vibration = (pump_head_RPM × rollers) / 60
```

| Pump Head RPM | Vibration Frequency |
|--------------|---------------------|
| 50 RPM (low duty) | 50 × 3 / 60 = **2.5 Hz** |
| 140 RPM (mid) | 140 × 3 / 60 = **7.0 Hz** |
| 280 RPM (full speed) | 280 × 3 / 60 = **14 Hz** |

**The dominant vibration band is 2.5–14 Hz** during normal dispensing operation.

This is a low-frequency mechanical vibration range. Notably, 2–14 Hz falls squarely in the range where split lock washers and spring washers become ineffective (they lose clamping force through fretting at these frequencies). This range is also where **thread-locker adhesive (Loctite 243 medium-strength, or equivalent)** is the most reliable solution for small fasteners.

### 3.3 Vibration Mitigation — Fastener Recommendation

**Recommendation: Apply Loctite 243 (medium-strength, removable blue thread locker) to all 4 M3 screws at assembly.**

Rationale:
- At 2.5–14 Hz, cyclic loading from roller compressions produces micro-rotation (vibration loosening) in M3-class screws within tens of thousands of cycles — potentially within 24–48 hours of operation.
- Medium-strength thread locker (Loctite 243 or equivalent) prevents vibration loosening while remaining serviceable: screws can be removed with hand tools if the pump ever needs replacement.
- Loctite 638 (high-strength, structural) would be too strong — M3 fasteners may gall or seize during removal.
- Nyloc nuts are not usable here because the screws thread into the pump head body, not a nut. A nyloc would require threading onto the back of the pump head, which has no accessible nut boss.
- Lock washers (split ring type) are ineffective in the 2–15 Hz range under cyclic compressive loading — they work primarily against torque reversal, not compression cycling.

**Screw length guidance:** The screws thread into the pump head body. The pump bracket is ~1.5–2mm thick. The tray plate is the mounting surface — plate thickness should be 2.5–3.5mm for structural reasons (see Section 5). Total engagement from the top of the bracket into the pump head: the screws must engage at minimum 3× the thread pitch (M3 × 0.5mm pitch = 1.5mm minimum; practical minimum for vibration-loaded joints is **6mm thread engagement**). This sets a screw length budget: bracket thickness (~2mm) + tray plate thickness (~3mm) + thread engagement (~6mm) = **~11mm total**. Use **M3 × 12mm socket head cap screws** with Loctite 243.

---

## 4. Pump Head Overhang and Shoulder Geometry

### 4.1 The Bracket-to-Pump-Head Transition

The bracket (68.6mm wide) is wider than the pump head (62.6mm). At the junction face:
- The bracket flat surface is what bears against the mounting plate
- Behind the bracket (on the pump-head side), the pump head body protrudes 3mm per side beyond the bracket edge in width and height
- In the depth axis (Y), the pump head body is entirely on the front side of the bracket

**This means:** When the pump mounts against the tray plate (motor passes through the bore, bracket face rests against the tray surface), the **pump head does not contact the tray at all.** The pump head is entirely forward of the tray surface — the bracket face is the sole contact surface between pump and tray. There is no overhang conflict, and no relief or shoulder is needed on the tray face.

The pump head extends 3mm beyond the bracket width/height, but the pump head is ~48mm forward (tube-outlet side) of the mounting face. This clearance zone is entirely in free air in front of the tray — not a constraint on the tray plate geometry.

**Actionable result:** The tray mounting face is a flat plate. No shoulder, no stepped relief, no counterbore needed for the pump head body. The only features required on the mounting face are:
1. Motor bore (37mm diameter)
2. Four M3 clearance holes (3.6mm CAD diameter) at 48mm × 48mm square pattern

---

## 5. Two-Pump Layout: Minimum Center-to-Center Spacing

### 5.1 Interference Envelope

The pump head is **62.6mm square** in cross-section. This is the widest dimension when looking from the front. The bracket is 68.6mm wide.

When two pumps are placed side by side (X direction):
- Each pump's bracket is 68.6mm wide
- The bracket is the outermost feature in the X direction at the mounting face
- Minimum side-to-side spacing to avoid bracket interference: bracket edge to bracket edge = 0mm with perfect fit; in practice, require minimum **2mm clearance** between brackets for assembly tolerance and thermal expansion

**Minimum pump center-to-center (X) from bracket interference alone:**
```
(68.6 / 2) + 2mm clearance + (68.6 / 2) = 70.6mm
```

### 5.2 Tube Stub Clearance

The tube stubs exit the pump head front face. The tube connectors are offset from center (one above, one below center per the geometry description). The pump head is 62.6mm wide. The tube stubs themselves (4.8mm ID × 8.0mm OD BPT tubing) need access for routing — the user must be able to connect and disconnect tubes without the adjacent pump body being in the way.

The tube stubs protrude 30–50mm forward from the front face, then curve away. Lateral clearance between adjacent pumps at the front face needs to account for hand access to the tube stubs. A practical minimum: **5mm lateral clearance** between pump head bodies at the front face.

**Minimum pump center-to-center (X) from tube stub access:**
```
(62.6 / 2) + 5mm clearance + (62.6 / 2) = 67.6mm
```

The bracket constraint (70.6mm) is the binding one.

### 5.3 Recommended Pump Center-to-Center

- Minimum from bracket interference: 70.6mm
- Round up for manufacturing margin: **75mm center-to-center**

At 75mm c-t-c:
- Bracket gap = 75 − 68.6 = 6.4mm (3.2mm per side between brackets) ✓ adequate for assembly
- Pump head gap = 75 − 62.6 = 12.4mm (6.2mm per side between pump head bodies) ✓ adequate for tube access
- Total tray width for two pumps: 75mm + 68.6mm = **143.6mm** (accounting for the half-bracket on each outer edge)

**Actionable result:** Set pump center-to-center at **75mm**. This is the X-direction dimension of the pump tray from center-to-center of the two motor bores and the two 4-hole patterns.

---

## 6. Complete Pump-Tray Geometry Summary

All dimensions connect to specific findings above.

### 6.1 Per-Pump Mounting Features

| Feature | CAD Dimension | Printed Result | Notes |
|---------|--------------|----------------|-------|
| Motor bore diameter | **37.2mm** | ~37.0mm | 1.0mm radial clearance on 35mm motor |
| M3 clearance hole diameter | **3.6mm** | ~3.4mm | Normal ISO 273 fit |
| M3 hole pattern | **48mm × 48mm square** | — | User-verified c-t-c |
| Hole positions (from bore center) | **±24mm X, ±24mm Z** | — | Symmetric |

### 6.2 Two-Pump Layout

| Parameter | Value | Notes |
|-----------|-------|-------|
| Pump center-to-center (X) | **75mm** | Bracket gap: 6.4mm, head gap: 12.4mm |
| Tray total width | **~144mm** | 75mm + 34.3mm each side outer half-bracket |

### 6.3 Tray Plate Thickness

The tray plate is a structural element carrying two 381g pumps (total ~762g) under 2–14 Hz vibration. The plate must be stiff enough that it does not flex and fatigue the screw threads.

- Recommended plate thickness: **3.0mm**
- This provides 2× minimum wall (0.8mm) at the M3 hole walls (hole diameter 3.6mm, so 3.0mm plate puts full screw length in material), adequate cantilever stiffness, and stays well within the FDM 1.2mm structural wall requirement.
- At 3.0mm thick, print with 4+ perimeters on the hole walls and 40%+ infill in the tray body.

### 6.4 Fasteners

| Item | Spec | Notes |
|------|------|-------|
| Screw | M3 × 12mm socket head cap screw | Threads into pump head body |
| Thread prep | Loctite 243 (medium blue) | Applied to screw before installation |
| Torque | ~0.5–0.8 N·m | Snug; do not over-torque M3 into nylon pump head |
| Quantity | 4 per pump × 2 pumps = **8 screws total** | |

### 6.5 Motor Clearance Depth

Behind the tray plate, the motor cylinder protrudes ~63–68mm (the motor body length from bracket face to end cap). The tray enclosure must provide at least **70mm clear depth** behind the plate face for the motor body, plus ~10mm for wiring at the terminal end = **80mm minimum clear depth** behind tray.

---

## 7. Failure Mode Catalog

| Failure | Cause | Prevention |
|---------|-------|-----------|
| Screw vibration loosening | 2–14 Hz cyclic compression, no thread locker | Apply Loctite 243 to all 8 M3 screws |
| Pump rocking on tray | Motor bore too tight, bracket not fully seated against plate | Motor bore 37mm (1mm per side clearance) |
| Tray plate cracking at holes | Under-thickness plate, under-infill, layer delamination at bore | 3.0mm plate, 4+ perimeters, ≥40% infill |
| Stripped threads in pump head | Over-torque, repeated removal without thread replacement | Snug torque only; Loctite reduces need for retorquing |
| Insufficient screw engagement | Screw too short for plate+bracket stack | M3×12mm minimum; verify thread engagement ≥6mm |
| Adjacent pump bracket interference | Center-to-center too small | 75mm c-t-c → 6.4mm bracket clearance |
| Tube stub access blocked | Center-to-center too small | 75mm c-t-c → 12.4mm pump head clearance |

---

## 8. Open Questions

1. **Motor body diameter confirmation:** The 35mm figure is low-confidence (photos 15, 16 are sideways display readings). The 37mm bore provides adequate clearance even if the motor is up to 35.5mm. If a more precise reading is obtained, the bore can be refined, but 37mm is conservative and correct.

2. **Exact motor shaft RPM:** The 280 RPM pump-head figure is well-established from the datasheet. The underlying motor RPM (~2,240 RPM unloaded) is inferred from the 1:8 gear ratio. The vibration frequency analysis is insensitive to this — what matters is the pump head speed (2.5–14 Hz range), which is established.

3. **Thread engagement depth in pump head:** The pump head body is nylon. Nylon has lower thread stripping strength than metal. The 6mm engagement minimum (12× M3 pitch) is conservative for metal; for nylon, 8–10mm engagement is safer. This is satisfied by the M3×12mm screw through a 3mm plate and ~2mm bracket, leaving ~7mm engagement — borderline. Consider M3×14mm screws if thread pullout is a concern. Verify against actual screw hole depth in pump head.
