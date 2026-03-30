# Pump-Tray Synthesis
## Cartridge Pump-Tray — Execution Plan

**Sources synthesized:**
- `hardware/printed-parts/cartridge/pump-tray/planning/research/design-patterns.md`
- `hardware/printed-parts/cartridge/pump-tray/planning/research/pump-mounting-geometry.md`
- `hardware/printed-parts/cartridge/pump-tray/planning/research/structural-requirements.md`
- `hardware/printed-parts/cartridge/pump-tray/planning/research/tube-routing-envelope.md`
- `hardware/off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md`
- `hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`
- `hardware/requirements.md`, `hardware/vision.md`

---

## Working Assumptions (Cartridge Not Yet Fully Designed)

The following are stated explicitly as working assumptions because the cartridge shell, dock, and release plate are not yet specified. The pump-tray synthesis is internally consistent under these assumptions; conflicts with later cartridge design decisions should be resolved by adjusting the shell, not the tray.

1. The pump-tray is the rear structural wall/backbone of the cartridge interior. The two pump heads project forward of it; the two motor cylinders extend behind it.
2. The four John Guest PP0408W fittings mount in the rear wall of the cartridge. This rear wall may be integral with the pump-tray (as a flange or ledger face) or it may be a separate shell panel that attaches to the tray. This synthesis treats the tray as carrying the fitting mounting bosses directly; if a separate rear wall is adopted, the tray must at minimum transfer load to that wall rigidly.
3. The cartridge slides on rails (dovetail profile, per tube-routing-envelope.md recommendation) at its top and bottom faces into a dock in the enclosure front-bottom bay.
4. Tube routing in the cartridge uses 90° push-fit elbows (e.g., John Guest PE0408W or equivalent) at the BPT-to-1/4" reducing union exits to turn the 1/4" line rearward. This eliminates the u-turn routing constraint and is the basis for all depth calculations below.
5. Working cartridge envelope: 110mm W × 200mm D × 80–85mm H. These are the tube-routing-envelope.md conservative figures; the height may increase to 85mm for tube stub clearance (see Section 7, Open Questions).
6. The cartridge pump-tray is replaced as a unit with the entire cartridge. Individual pump replacement inside the tray is not a user-facing operation — the user replaces the cartridge, not the pumps within it. Factory assembly requires inserting screws once; factory rework capability is required.

---

## 1. Mechanism Description

The pump-tray is a flat PETG plate, approximately 5mm thick, that serves as the structural backbone of the pump cartridge interior. It stands perpendicular to the cartridge's depth axis (the slide-in direction), dividing the cartridge into a forward pump-head zone and a rearward motor zone.

Both Kamoer KPHM400 peristaltic pumps mount face-first to this plate. Each pump's black stamped metal bracket rests flat against the tray's front face, with the motor cylinder passing through a bore in the plate and extending rearward. Eight M3 socket head cap screws — four per pump — pass through clearance holes in the plate and thread into the pump head body, clamping the bracket face firmly against the tray.

The tray's rear face presents the motor ends of both pumps and is flanked by two channels for motor wiring. At or near the tray's rear edge (exact integration with the cartridge rear wall is a cartridge shell decision), four John Guest PP0408W fittings mount in through-wall pocket bores, oriented with their long axis parallel to the cartridge depth axis. These fittings are the four quick-connect interfaces through which the cartridge receives and delivers fluid — two per pump, one inlet and one outlet for each flavor circuit.

When the cartridge is fully docked and a tube stub from the enclosure dock is inserted into a John Guest fitting, the connection is secure. When the user squeezes the release mechanism (defined by the release plate, which is a separate part), the collets of all four fittings are depressed simultaneously, releasing the tube stubs and allowing the cartridge to slide free of the dock.

The pump-tray does not move during operation or removal. It is fixed inside the cartridge shell. Its width, height, and position determine the cartridge's external dimensions on all axes. It is the part that everything else in the cartridge keys off of.

---

## 2. Critical Dimensions

### Dimensional Source Key
- **[C]** = caliper-verified from physical parts (highest confidence)
- **[D]** = derived from caliper-verified data by arithmetic (high confidence)
- **[A]** = working assumption, not yet directly measured (must be confirmed before final CAD)

### 2.1 Tray Plate Envelope

| Dimension | Value | Derivation | Confidence |
|-----------|-------|------------|------------|
| Tray width | **~144mm** | 75mm pump c-t-c + 34.3mm half-bracket on each outer side (68.6mm bracket / 2 = 34.3mm) [C]+[D] | HIGH |
| Tray thickness (plate, non-boss) | **5.0mm** | Structural-requirements.md: minimum for stiffness-to-touch; 0.57mm structurally minimum, 5mm for consumer feel [D] | CONFIRMED |
| Tray height | **~80–85mm** | Pump head 62.6mm [C] + floor/ceiling walls 3mm each + rail feature 5mm + stub clearance margin; see Open Questions | MEDIUM |

### 2.2 Motor Bore Positions and Diameters

| Feature | Value | Derivation | Confidence |
|---------|-------|------------|------------|
| Motor bore diameter (CAD design value) | **37.2mm** | Motor OD ~35mm [A, low confidence] + 1.0mm radial clearance per side = 37mm; +0.2mm FDM compensation per requirements.md = 37.2mm | LOW-MEDIUM |
| Motor bore diameter (printed target) | **~37.0mm** | After FDM shrinkage | LOW-MEDIUM |
| Pump center-to-center (X) | **75mm** | Minimum from bracket interference: 70.6mm [D]; rounded to 75mm for 6.4mm bracket gap [D] | HIGH |
| Bore 1 center (X) | **0mm** (tray centerline) | Symmetric layout; each bore at ±37.5mm from tray center | HIGH |
| Bore 2 center (X) | **75mm** from bore 1 | 75mm c-t-c [D] | HIGH |
| Bore Z position | **Vertical center of tray** | Pump head fills most of tray height; centered within height envelope | [A] |

Note: The 37mm bore figure is the most consequential low-confidence dimension. Motor diameter photos 15 and 16 read 34.54mm and 35.13mm respectively; 37mm bore gives 0.94–1.23mm radial clearance depending on actual motor OD. This is adequate even at the pessimistic end. Verify motor OD by direct caliper before finalizing bore diameter.

### 2.3 Mounting Hole Positions — Per Pump

All positions are relative to the center of that pump's motor bore.

| Feature | Value | Derivation | Confidence |
|---------|-------|------------|------------|
| Hole pattern | 48mm × 48mm square, c-t-c | User-verified caliper [C] | HIGH |
| Hole center offset from bore center | ±24mm in X, ±24mm in Z | 48mm / 2 = 24mm [C]+[D] | HIGH |
| M3 clearance hole diameter (CAD design value) | **3.6mm** | Target 3.4mm printed (normal ISO 273 fit) + 0.2mm FDM compensation per requirements.md | HIGH |
| M3 clearance hole diameter (printed target) | **~3.4mm** | After FDM shrinkage | HIGH |
| Boss OD | **9mm** | 2× insert OD (5mm); 2.15mm wall around 5mm OD insert; verified clear of 18mm bore radius [D] | HIGH |
| Boss height above plate face | **5mm** | Accommodates 4mm M3 insert (RX-M3x5x4) + 0.5mm floor + flush with boss top | HIGH |
| Boss cavity diameter | **4.7mm** | Ruthex/Voron/Prusa community-verified spec for RX-M3x5x4 insert | HIGH |
| Boss cavity depth | **4.5mm** | 4.0mm insert + 0.5mm floor clearance | HIGH |
| Boss base fillet | **1.5mm radius** | Stress concentration reduction; confirmed in structural-requirements.md and design-patterns.md | HIGH |
| All 8 bosses identical | **Yes** | Design language requirement from design-patterns.md UX Quality 3 | SPECIFIED |

### 2.4 Quick-Connect Fitting Pocket Positions (4× John Guest PP0408W)

The fittings mount in the rear wall with their long axis parallel to the cartridge depth axis (Y). The pocket bore grips the 9.31mm center body; the 15.10mm body ends protrude fore and aft of the wall.

| Feature | Value | Derivation | Confidence |
|---------|-------|------------|------------|
| Fitting pocket bore diameter | **9.5mm** | JG center body 9.31mm [C] + 0.2mm clearance per requirements.md = light press-fit | HIGH |
| Fitting shoulder OD (body ends) | **15.10mm** | Caliper-verified [C] | HIGH |
| Rear wall pocket depth | **6–8mm** | DeLonghi brew unit study (design-patterns.md): buries flange/body shoulder, leaves collet accessible; consistent with JG fitting axial geometry | SPECIFIED |
| Fitting X positions | **Matched to tube routing from pumps** | Each pump has two fittings (inlet + outlet); exact X/Z positions TBD by tube routing [A] | LOW |
| Fitting Z positions | **Vertically within motor wiring clearance band** | Must not conflict with motor terminals at rear; specific Z TBD [A] | LOW |

The exact fitting X and Z positions in the rear wall depend on the tube routing path from the BPT stubs through the reducing unions and elbows to the rear wall. This is a tube-routing layout decision that the cartridge shell step must resolve. The tray provides the structural backbone; the fitting pocket positions key to the tube routing.

---

## 3. Structural Approach

### Material: PETG

PETG is the specified material. Rationale from structural-requirements.md, confirmed here: PETG has lower creep than PLA under the sustained screw clamping load required to hold the pump brackets, adequate glass transition temperature (~80°C vs. motor operating temperature well below this), and impact-tough failure mode (deforms, does not shatter) appropriate for a user-handled replaceable module. Heat-set inserts install well in PETG at 245°C iron temperature. PLA is explicitly rejected due to creep at boss threads over 100–500 operating hours.

### Print Orientation: Flat

Print with the tray face (the face the pump brackets bear against) on the build plate. Z-axis equals plate thickness. This is the only acceptable orientation: printing on-edge would make the 37mm motor bore a 37mm unsupported bridge span, which vastly exceeds the 15mm bridge limit in requirements.md, distorting the bore and preventing the motor cylinder from seating cleanly.

Apply 0.3mm × 45° elephant's foot chamfer to the bottom edge per requirements.md. The designed 1.5mm × 45° perimeter chamfer (see Section 4) is on the top face (pump-head side) and lateral edges.

### Print Settings

- Minimum 4 perimeters throughout (structural wall requirement; boss wall integrity)
- 40% infill minimum, gyroid or grid pattern (boss compressive support, plate stiffness)
- These are minimum values; 50% infill and 5 perimeters at the boss zones is preferred

### Boss Geometry

Eight bosses total (4 per pump), all identical. Each boss is a cylinder: 9mm OD, 5mm tall above the plate face, 1.5mm base fillet. A 4.7mm diameter × 4.5mm deep cavity (blind hole from boss top) receives one M3 heat-set insert (RX-M3x5x4: OD 5.0mm, length 4.0mm). The 0.5mm floor below the insert prevents insert punch-through. The 2.15mm wall around the insert is above the 2mm minimum for clean heat-set installation without axial splitting.

Boss geometry is consistent across all 8 locations. Variation in boss OD, height, or fillet is explicitly not allowed — design-patterns.md UX Quality 3 finding: consistent boss geometry reads as a designed system; variation reads as improvised.

The mounting pad zone — the flat boss region including the bore circle and the 4-boss pattern — sits at the primary surface height. The field zone (remainder of plate face) drops 0.5mm. This 0.5mm step, recommended by design-patterns.md from the toner cartridge contact-surface study, ensures the pump bracket seats on a clean flat reference surface with no interference from field-zone features or surface debris.

### Heat-Set Insert Strategy

M3 heat-set inserts (RX-M3x5x4) are installed from the pump-bracket side of the plate (front face) using a soldering iron at 245°C. Pullout force per insert in PETG: ~1,167 N (CNC Kitchen data, cited in structural-requirements.md). Required pullout per screw in operation: less than 1.5 N. Safety margin exceeds 700×. The metal brass thread survives repeated assembly/disassembly for factory rework without thread degradation.

Self-tapping screws are rejected: they provide single-use threads, insufficient for factory rework scenarios where a screw might be removed and reinserted.

Through-bolts with nuts are rejected: require back-face wrench access during assembly that is awkward in a cartridge environment, and add 8 loose nuts to the BOM with no benefit over inserts given the enormous insert safety margin.

### Web Geometry

The minimum web of PETG between the motor bore edge and the nearest M3 screw hole edge:
- Bore radius (37mm bore): 18.5mm from plate center
- Screw hole center: 24mm from plate center
- Screw hole radius (3.6mm CAD): 1.8mm
- Minimum web: 24.0 − 18.5 − 1.8 = **3.7mm**

This exceeds the 1.2mm structural wall minimum from requirements.md by 3×. Not the limiting constraint.

Note: structural-requirements.md computed this as 4.4mm using a 36mm bore. The difference is that this synthesis uses the pump-mounting-geometry.md recommendation of 37.2mm CAD bore (37mm printed) rather than the 36mm figure used in structural requirements. At 37mm printed bore, the web becomes 3.7mm — still well above 1.2mm minimum.

---

## 4. Surface and Aesthetic Treatment

This section synthesizes design-patterns.md UX Quality 3 findings into a specific, non-optional surface treatment plan. These are not embellishments — they are the difference between a prototype and a product component.

### Mounting Pad Zone vs. Field Zone

The front face (pump-bracket side) has two surface levels:
- **Mounting pad zone:** Full thickness surface, extending to encompass each pump's bore circle plus its 4-boss pattern (approximately a 74mm × 74mm region centered on each bore). This is the seating plane for the pump bracket.
- **Field zone:** 0.5mm lower than the mounting pad zone. Covers the plate face outside the mounting pad regions. This makes the structural purpose of the mounting pad visually obvious and prevents field-zone surface variation from affecting bracket seating.

The 0.5mm step transition between zones should be a 45° chamfer, not a 90° step, to avoid a stress riser and to print cleanly without supports.

### Rib Pattern

Three rib types, all on the front face of the plate, all 5mm tall (flush with boss height — the rib height matches the boss height so the front face reads as a unified elevated surface):

1. **Bore-to-bore cross rib:** A single rib running along the X axis between the two motor bore circles, centered at the plate's Z midline. Width: 6mm. Height: 5mm. This rib visually and structurally connects the two pump mount zones and adds cross-plate stiffness against differential pump vibration loading. It also closes the gap between the two mounting pad zones into a single visual band.

2. **Boss-to-bore radiating ribs:** From each of the 8 bosses, one rib radiates toward the nearest bore circle edge. Width: 4mm. Height: 5mm. Length: from boss OD edge to bore circle edge (approximately 18.5mm bore radius − 24mm boss center + 4.5mm boss radius = variable, approximately 2–6mm depending on which boss). These short ribs make the rib pattern read as converging on the bore — the structural story is explicit: "the boss load routes to the bore and into the motor cylinder axis."

3. **Lateral perimeter ribs (conditional):** If the tray width exceeds the mounting zone by more than 20mm on either lateral side (likely given 144mm tray width vs. ~110mm outer-hole span), add lateral perimeter ribs at the outer edges: 3–4mm wide, 5mm tall, running the full tray height. These close the visual frame and prevent the outer plate edges from reading as unoccupied flat stock.

### Perimeter Chamfer

1.5mm × 45° chamfer on all four perimeter edges of the tray plate:
- Top face (pump-head side) outer edge: 1.5mm × 45°
- Both lateral edges (full plate height): 1.5mm × 45°
- Bottom face (build plate) edge: 0.3mm × 45° elephant's foot chamfer per requirements.md (this is the manufacturing requirement, not the design chamfer — scale difference is intentional)

This single treatment is identified in design-patterns.md as the highest-ratio design move for internal structural components: minimal material removed, maximum quality signal. A tray without edge chamfers reads as raw stock off the build plate.

### Wiring Channel

A 6mm wide × 4mm deep channel on the rear face of the tray plate (the motor-side face), running from the motor terminal region (near each bore, at the rear face) to the side edge of the tray where the motor harness exits. Channel walls: 1.5mm thick. Three strain-relief bumps per channel: 1.5mm tall × 2mm wide, rounded, spaced 20mm apart along the channel floor. The channel prevents motor wires from lying freely across the tray rear face.

The exact routing path (whether channels run laterally outward to the tray side edges, or converge at a single central exit point) is a decision for the cartridge shell step, which will define the harness connector location.

### Corner Radii

All internal corners where walls or features meet the plate face: 2mm radius minimum. All outer plate corners: 3mm radius. This brings the part into the visual register of molded components rather than CNC-cut stock, per the Dell XPS battery carrier finding in design-patterns.md.

### Boss Consistency

Stated again for emphasis: all 8 bosses are identical. 9mm OD, 5mm height, 1.5mm base fillet. No exceptions. A boss that differs from this spec for any reason is a design regression.

---

## 5. Interface with Cartridge Shell

The pump-tray does not stand alone — it connects to the cartridge shell (top wall, bottom wall, side walls, front wall, rear wall). The following defines what the tray provides and what the shell must provide, so the shell design agent has a clear interface contract.

### What the Pump-Tray Provides

- Structural backbone; sets cartridge internal width at ~144mm and constrains height at 80–85mm
- Flat mounting face for both pump brackets (with heat-set inserts, bosses, bore)
- Motor cylinder clearance bores (37mm diameter × plate thickness)
- Rear-face integration point for the John Guest fitting pockets (either as tray-integral bosses or as a mating flange that the rear wall attaches to)
- Wiring channels on rear face

### What the Cartridge Shell Must Provide

- Top and bottom walls with dovetail rail tongues (per tube-routing-envelope.md: 6mm wide, 5mm tall, 24° included angle, 0.2mm FDM clearance per face, 2mm × 45° lead-in chamfer)
- Front wall with ~50–55mm forward clearance from pump face for tube stub + BPT run + reducing union + elbow routing
- Rear wall with John Guest fitting pocket bores (9.5mm bore diameter, 6–8mm pocket depth, pockets recessed from exterior per design-patterns.md: rear face reads as flat panel with four small recesses, not four protruding fittings)
- Snap latch groove on top or bottom rail face: 1.0–1.5mm deep, 3–4mm wide in insertion direction, 0.5mm × 45° entry chamfer on leading edge, 90° retention face on trailing edge
- Hard mechanical end-stop at rear of dock that arrests cartridge travel at full insertion simultaneously with snap latch engagement
- Step-and-shoulder seam geometry at all shell parting lines: 1.5mm step height, shadow gap 0.3–0.5mm, per HP LaserJet cartridge finding in design-patterns.md
- Seam placement: rear face and top/bottom faces only — never on front face or lateral faces carrying the rail tongues

### Tray-to-Shell Attachment

Working assumption: the tray attaches to the shell by pressing into a channel or ledger molded into the side walls of the cartridge shell, then is secured by a small number of additional fasteners or snap features that the shell carries. The exact attachment method is a cartridge shell decision. The tray must be removable from the shell in a factory rework scenario without destroying either part. Snap-in with fastener backup is the expected approach; the shell step will specify.

---

## 6. Bill of Materials (Pump-Tray Specifically)

| Item | Specification | Qty | Notes |
|------|--------------|-----|-------|
| Printed pump-tray | PETG, printed flat (face on build plate), 4+ perimeters, 40%+ infill, gyroid or grid | 1 | ~144mm W × 5mm thick × 80–85mm H |
| Heat-set inserts | M3, OD 5.0mm, length 4.0mm (Ruthex RX-M3x5x4 or equivalent) | 8 | Installed from front face with soldering iron at 245°C |
| M3 socket head cap screws | M3 × 12mm, stainless steel | 8 | 4 per pump; threads into pump head body through tray clearance holes; Loctite 243 applied at assembly |
| Loctite 243 (medium blue thread locker) | Standard | — | Applied to all 8 M3 screw threads before installation; prevents vibration loosening at 2.5–14 Hz operating band |

Notes on screw length: M3 × 12mm provides bracket thickness (~2mm) + tray plate thickness (5mm) + ~5mm thread engagement into pump head nylon body. This is 5mm engagement — borderline for nylon (8–10mm preferred per pump-mounting-geometry.md open question). M3 × 14mm would give 7mm engagement, which is better for nylon thread stripping resistance. See Open Question #1.

The pump-tray BOM does not include the John Guest PP0408W fittings (4×) — those are technically mounted in the rear wall interface zone. Whether they belong to the tray BOM or the cartridge shell BOM depends on how the rear wall integration is resolved. If the tray carries the rear wall integrally, the JG fittings are tray BOM items. If the rear wall is a separate shell panel, they belong to the shell BOM.

---

## 7. Open Questions

The following are technical details the research did not fully resolve and must be addressed in the concept and specification steps.

**OQ-1: M3 screw length — thread engagement in nylon pump head**
The pump head body is nylon. Pump-mounting-geometry.md flags that for nylon, 8–10mm thread engagement is safer than the 6mm metal minimum. With a 5mm tray plate and ~2mm bracket, M3 × 12mm leaves only ~5mm engagement. M3 × 14mm would give ~7mm. The actual screw hole depth in the pump head must be measured before specifying screw length. If it accepts 8mm of engagement depth, specify M3 × 15mm (5mm plate + 2mm bracket + 8mm = 15mm total). **Action: caliper the screw hole depth in the pump head body.**

**OQ-2: Motor body diameter verification**
The 37mm bore is derived from a ~35mm motor OD that is low-confidence (photos 15 and 16 in geometry-description.md are sideways display readings: 34.54mm and 35.13mm). The 37mm bore is conservative and correct either way, but if the motor is meaningfully larger (say, 36mm+), the bore would need to increase to 38–39mm and the web width would decrease correspondingly. **Action: caliper the motor body diameter directly.**

**OQ-3: Tube stub vertical position (Z) on pump face**
Tube-routing-envelope.md derives the stub center-to-center as ~75mm from photo 17, with the stubs at approximately ±37.4mm from pump center — 6mm outside the pump face 62.6mm boundary. This sets the minimum tray height to 80mm (62.6mm + walls + clearance). However, if the stubs are closer to center, the tray height could decrease. If they are farther out, 85mm may be needed. **Action: caliper the tube stub centerline Z positions directly on the pump front face.**

**OQ-4: Tube stub horizontal (X) position on pump face**
The stub X offset from pump centerline is not caliper-verified. If the stubs are offset significantly in X, the tube routing in front of the tray may become asymmetric, affecting reducing union placement and elbow routing. **Action: caliper or visually confirm stub X positions on pump face.**

**OQ-5: John Guest fitting mounting — tray-integral vs. separate rear wall**
This synthesis assumes the JG fittings may be carried integrally in the pump-tray if the tray is thickened at its rear edge to form a rear-wall ledger. Alternatively, the rear wall is a separate cartridge shell panel. This decision affects tray geometry significantly: if the tray carries the fittings, it needs to be 6–8mm thicker at its rear face to accommodate the pocket bore depth. If the rear wall is separate, the tray terminates at the rear edge and the shell handles the fitting pockets. **This is the highest-priority cartridge architecture decision; the concept step must resolve it before any CAD begins.**

**OQ-6: Wiring channel routing and harness exit point**
The motor wire routing channels on the tray rear face need a defined exit point — a location where the wires leave the tray and pass to the main harness connector in the enclosure. This exit point defines the channel routing path. The cartridge shell step must define the harness connector location (inside the dock, accessible when the cartridge is docked) so the tray channel can route to it. **Action: cartridge shell concept step defines harness connector location; tray channel routing finalizes after.**

**OQ-7: Fitting X/Z pocket positions in rear wall**
The four John Guest fitting pockets (two per pump, inlet and outlet) must be positioned to match the tube routing from the pump BPT stubs through the reducing unions and elbows to the rear wall. Tube-routing-envelope.md identifies this as an uncertainty: the exact X and Z positions of the fittings in the rear wall depend on the tube routing layout. **Action: tube routing layout step resolves this after pump stub positions are confirmed (OQ-3, OQ-4).**

---

## 8. Conflict Flags

### Flag 1 — Vision specifies 4 quick-connects inside the cartridge; research reveals barbell geometry not assumed in vision

The vision (vision.md section 3) specifies four quick connects inside the cartridge with a release plate that presses the collets. The caliper-verified JG PP0408W geometry (geometry-description.md for the union) reveals the fitting is a barbell profile (15.10mm body ends, 9.31mm center body), not a uniform cylinder as likely assumed when the vision was written. The release plate stepped bore design must account for this: the plate must pass through the 15.10mm body end zone with a bore just over 15.10mm to reach the 9.57mm collet. This is more geometrically constrained than a simple collet-press operation.

**This is not a conflict with the vision's specified interaction — the interaction (squeeze to release) is preserved exactly.** It is a constraint on the release plate geometry that the release-plate design agent must execute correctly. The vision is unchanged. The release plate bore design must use the caliper-verified dimensions.

**No modification to the vision required. The release plate design agent must read geometry-description.md for the JG union before designing the release plate.**

### Flag 2 — Tray thickness (5mm) vs. structural requirements document thickness recommendation

Pump-mounting-geometry.md specifies 3.0mm plate thickness. Structural-requirements.md specifies 5.0mm. These two research documents disagree. The synthesis adopts 5.0mm from structural-requirements.md, which provides the more complete analysis: the 5mm figure is justified on the grounds of stiffness-to-touch (consumer product feel) and boss height support, not structural minimum (which is 0.57mm). The 3.0mm figure in pump-mounting-geometry.md is a structural minimum estimate without the consumer-feel consideration.

**No vision conflict. Resolution: 5mm plate thickness. The structural-requirements.md figure is the one that addresses consumer product standards explicitly.**

### Flag 3 — Motor bore diameter: two research documents use different values

Structural-requirements.md uses a 36mm bore for web width calculations. Pump-mounting-geometry.md recommends 37.2mm CAD / 37mm printed. The synthesis adopts 37.2mm CAD (pump-mounting-geometry.md), which is the more thoroughly analyzed figure. This reduces the minimum web from 4.4mm (structural-requirements.md calculation) to 3.7mm — still 3× the 1.2mm structural wall minimum. No structural consequence.

**No vision conflict. Resolution: 37.2mm CAD bore diameter.**

### Flag 4 — Cartridge depth vs. enclosure dimension constraints

Tube-routing-envelope.md derives a working cartridge depth of 200mm. The vision specifies a total enclosure of 220mm × 300mm × 400mm with the cartridge at the front-bottom. The cartridge must fit within the 300mm depth of the enclosure. A 200mm cartridge within a 300mm enclosure leaves 100mm for the valve zone (behind the cartridge) and the enclosure rear wall — this appears geometrically feasible based on the vision architecture.

**No conflict flagged** — the numbers appear compatible — but this has not been formally verified against the enclosure layout. **The enclosure layout step should confirm that the 200mm cartridge depth plus valve zone plus rear fittings fits within 300mm enclosure depth before cartridge CAD begins.**

---

## Summary of Actionable Decisions

The following decisions are made by this synthesis and are ready to execute in CAD:

| Decision | Value |
|----------|-------|
| Material | PETG |
| Print orientation | Flat (front face on build plate) |
| Plate thickness | 5.0mm |
| Pump center-to-center | 75mm |
| Tray width | ~144mm |
| Motor bore diameter (CAD) | 37.2mm |
| M3 clearance hole diameter (CAD) | 3.6mm |
| Mounting hole pattern | 48mm × 48mm square per pump |
| Boss OD | 9mm |
| Boss height | 5mm |
| Boss base fillet | 1.5mm radius |
| Boss cavity diameter | 4.7mm |
| Boss cavity depth | 4.5mm |
| Heat-set insert | M3, OD 5.0mm, length 4.0mm (RX-M3x5x4) |
| Screw | M3 × 12mm SHCS minimum; M3 × 14–15mm preferred pending OQ-1 |
| Thread locker | Loctite 243, all 8 M3 screws |
| Bore-to-bore cross rib | 6mm wide, 5mm tall |
| Radiating boss ribs | 4mm wide, 5mm tall |
| Perimeter chamfer | 1.5mm × 45° on top face and lateral edges |
| Wiring channel | 6mm wide × 4mm deep, rear face |
| Wire strain-relief bumps | 1.5mm tall, 20mm spacing |
| Internal corner radii | 2mm minimum |
| Outer plate corner radii | 3mm |
| Mounting pad step depth | 0.5mm below field zone |
| Infill | 40% minimum (50% preferred at boss zones) |
| Perimeters | 4 minimum |
| Elephant's foot chamfer | 0.3mm × 45° on build plate face edge |
| JG fitting pocket bore | 9.5mm diameter, 6–8mm depth |
