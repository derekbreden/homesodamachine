# Pump Tray Structural Requirements Research

## Purpose

This document derives the structural requirements for the pump-tray plate — the flat FDM-printed plate inside the pump cartridge to which both Kamoer KPHM400 pumps mount via 4x M3 screws each. It addresses plate thickness, print orientation, material selection, boss design, screw fastening strategy, and vibration isolation.

---

## Pump Mass — Verified

The pump in use is the **KPHM400-SW3B25** (12V brushed DC motor, BPT tube variant). Kamoer's published technical parameters for the SW/SV (brushed) variant give the weight as **~306g**. Two pumps total: **~612g (~6.0 N combined static load)**.

Source: kamoer.cn technical parameters page, id=10014.

---

## Geometry Inputs

From the caliper-verified geometry document:

| Parameter | Value |
|-----------|-------|
| Mounting hole pattern (c-c) | 48mm x 48mm square |
| Motor cylinder diameter | ~35mm (low-confidence; use 36mm bore for clearance) |
| Mounting hole diameter (pump bracket) | 3.13mm (M3 clearance) |
| Bracket width | ~68.6mm |

### Web Width Calculation — Thinnest Point

The critical structural concern is the web of material between the motor bore edge and the nearest screw hole edge.

```
Bore radius (with clearance) = 36 / 2 = 18.0 mm
Screw hole center from plate center = 48 / 2 = 24.0 mm
Distance: bore edge to screw hole center = 24.0 - 18.0 = 6.0 mm
M3 screw hole radius (clearance) = 3.2 / 2 = 1.6 mm
                                         (3.0mm + 0.2mm per requirements.md)
Web width (bore edge to hole edge) = 6.0 - 1.6 = 4.4 mm
```

**Minimum web width: 4.4 mm.** This is the thinnest cross-section of material in the plate, at the inboard edge of each screw hole, closest to the bore.

Minimum wall requirement from requirements.md: structural walls bearing load must be at least **1.2mm** (3 perimeters). The 4.4mm web exceeds this requirement by 3.7x. The web is not the limiting constraint on plate geometry.

---

## 1. Plate Thickness

### Load Analysis

Each pump weighs ~306g. The pump is cantilevered from the tray: the mounting bracket bears a moment arm equal to half the pump body depth. The pump head extends ~48mm in front of the bracket face; the motor extends ~68mm behind. The center of gravity is approximately at the pump head midpoint (~24mm in front of the bracket). The dominant load on the plate is:

- **Static bending moment per pump**: 306g × 9.81 m/s² × 0.024m ≈ 0.072 N·m
- **Vibration amplification**: A 3-roller peristaltic at ~100–400 RPM (brushed DC) produces cyclic force at ~5–20 Hz per roller pass (3 rollers × RPM/60). At typical dosing speeds for this application (slow — syrup injection is a few seconds per pour), RPM will be low. Even at max speed (~400 RPM brushed), vibration frequency is ~20 Hz. This is well below structural resonance for a plate of reasonable thickness. Assume a dynamic amplification factor of **1.5x** (conservative).

Effective load per pump: 306g × 1.5 = **459g effective, or 4.5 N per pump, at 24mm moment arm** = 0.108 N·m per pump.

### Plate Bending Stiffness

For a simply-supported flat plate, flexural rigidity:

```
D = (E × t³) / (12 × (1 - ν²))
```

FDM-printed PETG properties (XY plane, in-plane loading):
- E (flexural modulus, XY) ≈ **1,174 MPa** (literature: 1,174 ± 64 MPa)
- ν ≈ 0.38 (typical for PETG)

The plate is more realistically modeled as a stiff plate with localized point loads at four screw holes per pump, rather than a uniformly loaded simply-supported plate. The relevant failure mode is **local bending in the web between the bore and the screw hole** and **global sag of the plate midspan** between the two mounting regions.

**Global sag check (beam approximation):**
Two pumps, each ~150mm apart (pump center to pump center on tray), loaded at midspan. Treat the tray as a simply-supported beam of width B and thickness t:

At midspan with two point loads, maximum bending stress:
```
σ = M × (t/2) / I
where I = B × t³ / 12
M per pump = 0.108 N·m
```

For σ < 25 MPa (half of FDM PETG flexural strength 53.7 MPa, safety factor 2):
```
σ ≤ 25 MPa
M × (t/2) / (B × t³ / 12) ≤ 25 × 10⁶
M × 6 / (B × t²) ≤ 25 × 10⁶
```

With B = 80mm (tray width, conservative narrow estimate), M = 0.108 N·m:
```
0.108 × 6 / (0.080 × t²) ≤ 25 × 10⁶
0.648 / (0.080 × t²) ≤ 25 × 10⁶
t² ≥ 0.648 / (0.080 × 25 × 10⁶)
t² ≥ 3.24 × 10⁻⁷ m²
t ≥ 0.00057 m = 0.57 mm
```

This gives a structurally trivial minimum from static bending. The far more constraining requirements are:

1. **Screw pullout resistance** — covered in section 4/5.
2. **Boss wall integrity** — boss wall must be >2mm surrounding the insert.
3. **Practical stiffness** — a plate thin enough to flex visibly under hand pressure is unacceptable for a consumer product.

**Practical minimum plate thickness (non-boss region): 4 mm.**

Rationale:
- 4mm provides a plate that is stiff to the touch with no perceptible flex under pump weight.
- At 4mm with 4 perimeters (1.6mm walls) and 40% infill or more, the plate has adequate compressive resistance at the boss bases.
- Less than 4mm in a plate this size (~120–180mm span) would feel hollow and compliant when tapped, inconsistent with a consumer product feel.
- Boss region below the insert adds additional thickness — see section 4.

**Recommendation: 5 mm plate thickness (non-boss region).** This provides margin, a solid feel, and adequate clearance for boss height to be minimized.

**Failure mode if violated:** If the plate is printed at 2–3mm, the plate will flex under pump weight creating cyclic stress at the screw hole bosses. Over weeks of use, this will fatigue the boss-to-plate fillet, eventually cracking the base of the boss. The motor bore web (4.4mm minimum) sets a geometric floor — any plate thinner than the web width itself would feel structurally dubious. 5mm is well above all minima.

---

## 2. Print Orientation

### Option A: Print Flat (plate face on build plate, Z = thickness)

- Layer lines are parallel to the plate face.
- Screw holes are drilled through the Z axis — **screw pullout force acts along Z, perpendicular to layer lines.** This is the weakest FDM direction. Pullout loads delaminate layers.
- Motor bore circles print as horizontal features — excellent roundness and surface finish.
- Boss cylinders print vertically — boss walls are all perimeter material (strongest for a cylinder in this orientation).

### Option B: Print on Edge (plate face vertical, Z = plate width or height)

- Layer lines are perpendicular to the plate face — they stack along the plate width.
- Screw holes print as features in the XY plane — screw pullout acts in the XY plane, perpendicular to layer lines... this does NOT improve things: with face vertical, pullout is still across layers.
- Wait — re-analysis: if the plate face is vertical, the screw holes in the bracket face are also horizontal (bore axis is horizontal in this orientation). Screw pullout direction is horizontal = parallel to layer lines. This IS the stronger direction.
- **But:** bore circles now print as vertical circles. Their roundness degrades. More critically, the ~36mm bore is a **bridge** — the top half of the bore arc is a 36mm unsupported span. Requirements.md limits bridges to 15mm. A 36mm bridge will sag and distort the bore. A distorted bore cannot mate with the motor cylinder.
- Additionally, surface quality on the bore's downward-facing arc will be rough from unsupported bridging, creating point contact with the motor cylinder rather than a clean clearance fit.

### Verdict: **Print flat (Option A) with heat-set inserts.**

Printing flat is the correct choice. The bore distortion problem with on-edge printing is a hard failure (36mm span vastly exceeds the 15mm bridge limit). With flat printing, the correct response to the Z-axis screw pullout weakness is not to change print orientation — it is to eliminate the weakness by using heat-set inserts, which distribute the pullout load through a brass cylinder embedded in the plastic rather than relying on FDM layer adhesion.

**Print orientation note for parts.md:** Print flat. Plate face on build plate. Z direction = plate thickness. Apply elephant's foot chamfer (0.3mm × 45°) to the bottom edge per requirements.md.

---

## 3. Material Recommendation

### Available options from requirements.md: PLA, PETG, TPU, ABS, ASA, PC, PA, and CF variants.

### PLA

- Higher in-plane stiffness (~3,500 MPa bulk vs PETG 2,200 MPa bulk; similar when printed)
- Brittle failure mode: will shatter rather than deform under shock/vibration
- **Creep under sustained load is worse than PETG.** Testing shows PLA deforms substantially over 24 hours under static stress and does not return to shape.
- Glass transition temperature ~55–60°C. The brushed DC motor at sustained load gets warm. Under-sink installations may be thermally benign, but a motor mounted directly to a PLA plate introduces creep risk at the screw bosses over hundreds of hours of operation.
- Screw boss integrity will degrade due to creep: the clamping force on the pump bracket screws will relax over time, eventually allowing the pump to work loose.

### PETG

- Impact tough: deforms rather than shatters under vibration-induced shock loads.
- **Lower creep than PLA** at typical operating temperatures.
- Glass transition ~80°C: fully adequate for this application (motor surface temperature under normal load is well below 80°C for a 10W brushed motor).
- Heat-set inserts install well in PETG (245°C iron temperature). The melt zone re-fuses cleanly around the knurled insert, creating good mechanical interlock.
- CNC Kitchen measured pullout forces for M3 threads in PETG (heat-set insert): ~119 kg (~1,167 N). This is 194x the actual axial load per screw (6.0 N / 8 screws = 0.75 N per screw in static loading). An enormous safety margin.
- PETG flexural strength (FDM XY): ~53.7 MPa. Adequate for the loads in this application.

### Recommendation: **PETG**

PETG is the correct choice. The creep resistance and impact toughness are directly relevant: the pump mount is a sustained-load application with cyclic vibration, and PLA's brittle failure mode and higher creep rate create long-term reliability risks. PETG is listed as supported (standard and CF reinforced) in requirements.md.

**Failure mode if PLA is used:** Over 100–500 hours of operation, PLA bosses will creep under the sustained screw clamping load, screw engagement will loosen, and the pump will develop micro-movement at the mounting face. Micro-movement accelerates fretting wear of the plastic boss. Eventually one or more screws strips out, and the pump is loose on the tray. This is silent and progressive — the user may not notice until the cartridge rattles audibly.

---

## 4. Boss Design

Bosses are raised cylinders around each screw hole. Their purpose is to increase the thread engagement length for the fastener — the screw engages more material, which dramatically increases pullout resistance.

### Why Bosses Are Necessary in This Application

With a flat plate printed flat (Z = thickness), the screw engages only a length equal to the plate thickness minus any countersink. At 5mm plate + 5mm boss height, the screw engages ~10mm of material, which for heat-set inserts equals the full insert length. Without a boss on a 5mm plate, the insert must fit entirely within 5mm, leaving almost no plate material below the insert. The boss provides the engagement length.

### Boss Geometry Recommendation

**Insert specification (Ruthex M3 standard for Voron/Prusa, RX-M3x5x4):**
- Outer diameter: 5.0mm (knurled OD)
- Length: 4.0mm
- Cavity diameter: 4.7mm (Voron/Prusa community-verified spec)
- Cavity depth: 4.5mm (insert length + 0.5mm clearance at bottom)

**Boss outer diameter:** Per the 2–3× rule (outer diameter = 2–3× insert OD), use **10mm OD** (2× 5.0mm). This provides a 2.5mm wall thickness around the insert on each side. The 2mm minimum wall is met with margin.

Rationale: 12mm OD would be better in theory but may be tight on the 4.4mm web between bore and screw hole. At 10mm OD boss, the boss outer radius is 5mm. The screw hole center is at 24mm from plate center; bore edge at 18mm. Boss outer edge inboard = 24mm - 5mm = 19mm — just barely clears the 18mm bore edge by 1mm. This is acceptable since the bore is a clearance hole, not a mating surface. If the boss slightly overhangs the bore edge, it does not affect function.

Alternatively: use **9mm OD boss** to give 1.5mm wall and 3mm total clearance to bore edge. 9mm OD with 4.7mm hole = 2.15mm wall — still above the 2mm minimum.

**Recommended: 9mm OD boss outer diameter.**

**Boss height:** The heat-set insert is 4mm long. The insert must be fully embedded with at least 0.5mm of plastic below it. Boss height = insert length + 0.5mm floor + 0.5mm above = **5mm boss height above the plate face.**

Total fastener engagement = boss height = 5mm, matching insert length exactly. This is the correct design: the insert sits flush with the top of the boss, and the M3 screw passes through the pump bracket and engages the full insert length.

**Boss geometry summary:**
- Outer diameter: 9mm
- Height above plate face: 5mm
- Cavity diameter: 4.7mm
- Cavity depth: 4.5mm (4.0mm insert + 0.5mm floor)
- Boss base fillet: 1.5mm radius minimum (reduces stress concentration at boss-to-plate junction)

**Failure mode if bosses are omitted:** With a flat 5mm plate and no bosses, the insert is only 4mm long and the plate is only 5mm thick — leaving 1mm of plastic below the insert. This 1mm floor is the first failure point. Under pullout load, the insert pushes through the floor. With bosses, the floor is 0.5mm (just above the minimum) and the insert is supported by 5mm of engaged plastic on all sides plus the boss OD walls.

**Failure mode if boss OD is too small:** If the wall around the insert is less than 1.5mm, the boss splits longitudinally during heat-set insertion (the plastic cannot accommodate the displaced volume and cracks axially). The 9mm OD provides 2.15mm wall — sufficient to absorb insert installation without cracking.

---

## 5. FDM Screw Hole Design Strategy

Three options:
1. **Self-tapping screws** into printed plastic (undersized pilot hole)
2. **Heat-set inserts** (brass threaded insert pressed in with soldering iron)
3. **Through-clearance with nut** (M3 through-bolt, nut on back)

### Self-Tapping Analysis

A self-tapping screw into PETG can achieve surprisingly high pullout resistance for a single installation. Community testing shows a 6mm engagement length in PETG will cause plastic to fracture before thread stripping (~plastic breakout failure mode). However:
- Self-tapping screws damage threads each insertion/removal cycle.
- The pump tray is designed to be user-replaceable (requirements.md Section 4: "the user can remove and replace the pump cartridge which contains both pumps"). Even though pumps are inside the cartridge and the user doesn't disassemble the tray themselves, manufacturing assembly requires seating screws once. Self-tapping is acceptable for single-assembly if the tray is never disassembled.
- BUT: if a pump fails and needs replacement before the entire cartridge is replaced, self-tapping makes the tray single-use. Design intent is "replace the cartridge" — the tray goes with it. Self-tapping could work.
- Self-tapping in PETG with a 3mm (nominal) hole: use pilot hole at **2.5mm diameter** (undersized by 0.5mm from M3 nominal), allowing the screw to cut its own thread. Engagement depth: 8mm minimum.

### Through-Bolt with Nut Analysis

- Highest pullout resistance (limited only by screw tensile strength, ~800 MPa for M3 8.8 stainless = ~5.5 kN ultimate).
- Requires access to the back face to hold the nut.
- The pump bracket face is the mounting face; the back of the plate is inside the cartridge. Access for a wrench or socket during assembly is possible but awkward in a tight cartridge.
- Adds assembly complexity (four loose nuts per pump = eight total).
- Most reliable for high-stress applications.

### Heat-Set Insert Analysis

- Brass insert thermally embedded in plastic boss with a soldering iron.
- Standard M3 heat-set insert (RX-M3x5x4): 5mm OD, 4mm length, M3 internal thread.
- Pullout force: ~1,167 N per insert (CNC Kitchen test, PETG).
- Required pullout per screw: static 0.75 N, dynamic ~1.1 N (1.5x factor). Safety margin: **>1,000x**.
- Survives repeated assembly/disassembly — threads are metal (brass), not plastic.
- Correct for a product that might require inspection or factory rework before shipment.
- The boss geometry exactly accommodates this approach.

### Recommendation: **Heat-set inserts (M3, 5mm OD, 4mm length)**

Heat-set inserts are the correct approach. They transform the M3 screw engagement from a plastic-threading problem (creep, single-use threads) to a metal-threading problem (repeatable, durable, permanent). The pullout margin is essentially infinite for this application's loads. The brass insert also acts as a local thermal sink, reducing the tendency of pump vibration to slowly degrade the threaded engagement. Installation requires a standard soldering iron — a one-time factory assembly step.

**Failure mode if self-tapping is used instead:** The tray may be assembled and work fine for years. But if a factory rework is needed (wrong pump orientation, mis-screwed hole), removing and re-inserting the screw in the same self-tapped hole degrades the thread engagement each time. After 2–3 insertion cycles, the hole strips. Heat-set inserts eliminate this failure mode entirely.

---

## 6. Vibration Isolation

### Vibration Characterization

The Kamoer KPHM400 uses a 3-roller peristaltic mechanism. Each roller passes and squeezes the tube, generating a force impulse. At 400 RPM (max), the roller pass frequency is:

```
3 rollers × 400 RPM / 60 = 20 Hz (roller pass frequency at max speed)
```

For typical syrup injection in this application (a 2–5 second dispense of ~1–4ml), the pump runs at moderate speed, likely 50–150 RPM during use:

```
3 rollers × 100 RPM / 60 = 5 Hz at 100 RPM
```

This is in the low-frequency range (5–20 Hz) — the same frequency band as HVAC equipment and dishwashers. At these frequencies, isolation requires compliant mounts with a natural frequency well below 5 Hz, which would require very soft elastomers and is generally not practical in a rigid plastic plate assembly.

### Does This Pump Need Vibration Isolation?

Consider what the vibration actually causes:
1. **Acoustic radiation:** Pump noise transmitted to the cartridge body, then to the enclosure, then to the under-sink cavity or countertop. The enclosure acts as a sounding board.
2. **Fatigue:** Cyclic stress at screw bosses. At the loads involved (roller force is very small for a pump this size pumping low-viscosity syrup at low pressure), fatigue stress amplitude at the bosses is negligible. Fatigue failure would require millions of cycles at significant stress — the pump runs for seconds per pour, not hours per day.
3. **Tube noise:** The tube squeezing itself generates most of the acoustic output; this is not transmitted through the mounting plate.

### Conclusion on Vibration Isolation

**Direct hard mounting is acceptable for this application.** The structural fatigue case is negligible. The acoustic case (noise transmission through the plate) is a secondary concern — the pump produces audible noise from the tube squeezing mechanism regardless of mount compliance.

If noise reduction is a goal: a **30A Shore TPU gasket** between the pump bracket face and the tray boss faces would provide meaningful acoustic decoupling. At 30A Shore, the gasket is compliant enough to not transmit high-frequency vibration but stiff enough to maintain pump alignment under the low loads involved. The TPU would be printed as a flat washer (OD: 9mm, ID: 3.5mm, thickness: 1–2mm) to sit under each boss, interposed between the pump bracket and the tray boss face.

However: the TPU gaskets add BOM complexity and assembly steps. A consumer product optimizes for simplicity. For a pump operating at 5–20 Hz, mounting compliance matters most at 1–5 Hz for isolation, which 30A Shore TPU does not provide at 1–2mm thickness.

**Recommendation: Hard mount without TPU gaskets.** Accept the pump noise as a characteristic of the product. The noise level of a peristaltic pump squeezing BPT tubing is minimal in a kitchen environment dominated by refrigerator compressor, dishwasher, and water sounds.

**If acoustic requirements tighten:** Add 30A Shore TPU printed flat washers under each boss at 1mm thickness. Boss height should increase by 1mm (to 6mm) to maintain screw engagement depth through the gasket. The gasket does not need to be permanently bonded — compression under screw clamping force holds it in place.

---

## Consolidated Design Specifications

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Pump weight (per pump) | ~306g (verified, brushed DC variant) | Kamoer technical params |
| Minimum web width (bore-to-screw) | 4.4mm | Geometric calculation: 24mm - 18mm bore radius - 1.6mm hole radius |
| Plate thickness (non-boss) | **5mm** | Practical stiffness, safety margin, boss base clearance |
| Print orientation | **Flat (face on build plate)** | Bore roundness requirement; bridge limit exceeded on-edge |
| Material | **PETG** | Impact toughness, creep resistance, heat-set insert compatibility |
| Boss OD | **9mm** | 2.15mm wall around 5mm OD insert; clears 4.4mm web |
| Boss height | **5mm** | Accommodates 4mm insert + 0.5mm floor clearance |
| Cavity diameter | **4.7mm** | Standard Voron/Prusa spec for M3 RX-M3x5x4 insert |
| Cavity depth | **4.5mm** | 4mm insert + 0.5mm floor |
| Boss fillet | **1.5mm radius** | Reduces stress concentration at boss base |
| Fastener type | **Heat-set insert, M3, OD5mm, L4mm** | Metal threads, 1,000x+ safety margin on pullout |
| Screw | M3 × 8mm minimum | Engages full 4mm insert with adequate clamping |
| Vibration isolation | **None (hard mount)** | Loads trivial; noise acceptable; assembly simplicity |
| Infill | **40% minimum, grid or gyroid** | Adequate boss compressive support |
| Perimeters | **4 minimum** | Structural per requirements.md, boss wall integrity |
| Elephant's foot chamfer | **0.3mm × 45°** on bottom face | Per requirements.md dimensional accuracy |

---

## Critical Failure Mode Summary

| Violation | First Failure Mode |
|-----------|-------------------|
| Plate thickness < 3mm | Plate flexes visibly under pump weight; cyclic stress at boss fillets → crack at boss base over weeks |
| PLA instead of PETG | Boss creep under sustained screw clamping → screw loosening over 100–500 hours; brittle fracture if pump is dropped or cartridge impacts enclosure during removal |
| Boss OD < 7mm (wall < 1mm) | Boss splits axially during heat-set insert installation before assembly is complete |
| No boss (flat plate only) | Only 1mm of plastic below insert floor; insert punches through floor under first tightening torque |
| Boss height < 4mm | Insert not fully captured; only partial thread engagement; pullout force reduced; screw strips insert on first over-tighten |
| Self-tapping without boss | Thread engagement ≤ plate thickness; single-use threads; factory rework destroys hole |
| On-edge print orientation | 36mm bore prints as 36mm bridge span; exceeds 15mm bridge limit (requirements.md); bore distorts; motor cylinder cannot seat cleanly |

---

## References

- Kamoer technical parameters (kamoer.cn): brushed DC variant weight ~306g
- CNC Kitchen: M3 heat-set insert pullout in PETG ~119 kg (~1,167 N)
- Ruthex RX-M3x5x4: M3 insert, OD 5.0mm, length 4mm; cavity 4.7mm diameter
- FDM PETG flexural modulus (XY, literature): 1,174 ± 64 MPa; flexural strength 53.7 ± 2.4 MPa
- Thrinter.com creep testing: PLA exhibits substantially higher creep than PETG under sustained load
- hardware/requirements.md Section 6: FDM manufacturing constraints (bridge limit, wall thickness, orientation rules)
- hardware/off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md: mounting hole pattern, bore dimensions
