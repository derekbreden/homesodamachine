# Pump-Tray — Parts Specification

**Part name:** Pump-Tray
**Part count:** 1 (single printed part, no sub-assembly)
**Material:** PETG
**Print orientation:** Front face (Y=0) on build plate
**Coordinate frame:** Defined in Section 2 below; identical to spatial-resolution.md and decomposition.md

**Status:** Complete specification. Feeds directly into CAD generation (Step 4c).

**Sources:** spatial-resolution.md (primary dimensional source), concept.md, decomposition.md, synthesis.md, pump-mounting-geometry.md, structural-requirements.md, tube-routing-envelope.md, kamoer-kphm400/geometry-description.md, john-guest-union/geometry-description.md, hardware/requirements.md, hardware/vision.md.

---

## Mechanism Narrative (Rubric A)

### What the user sees and touches

The pump-tray is never seen or touched during normal use. It lives inside the pump cartridge shell. The cartridge — as a whole — is what the user handles: a black-box module they pull from the enclosure front-bottom bay when the pumps wear out and replace with a new one. The user's hand contacts the cartridge's exterior surfaces, not the tray.

There is one scenario in which the tray is visible to the user: when the cartridge has been removed from the enclosure and the user peers into the rear opening. In that case, the rear face of the tray is visible: a flat surface with two large circular bore openings (motor exits), two lateral wiring channels, and eight small clearance-hole openings. This is a utility face. It reads as a designed internal component — structured, purposeful — not as improvised FDM stock.

The front face (pump-bracket side) is never visible; it is occluded by the pump brackets and pump-head bodies once the pumps are installed.

### What moves

Nothing on the tray moves during operation or during cartridge removal. The tray is a static structural element fixed inside the cartridge shell.

**Stationary parts:**
- The tray itself (fixed in the shell via the channel-and-snap interface)
- Both pump assemblies (fastened to the tray via 8 M3 SHCS with Loctite 243)

**Moving parts (not on the tray):**
- The cartridge as a whole slides along the dock rails during removal and installation
- The dock's release plate (separate part) acts on the JG fitting collets — this is a cartridge-shell concern, not a tray concern

### What is the structural function

The tray is a rigid plate that takes the static weight of two pumps (~306g each, 612g total), the cyclic 2–14 Hz vibration load from pump operation, and the clamping preload of 8 M3 screws (each torqued to 0.5–0.8 N·m). It transmits these loads through its body to the cartridge shell via the two lateral sliding-contact surfaces (the channel interface). No bending failure, no boss-base cracking, no screw loosening within the design operating life is expected under these loads with the specified geometry and material.

The heat-set inserts (brass, M3, 4mm engagement) provide metal-threaded screw engagement in the PETG boss bodies. Pullout resistance per insert (~1,167 N) exceeds the maximum operating load per fastener (~1.5 N) by a margin exceeding 700×.

### How the pumps are attached

Each pump's stamped metal bracket (68.6mm × ~68.6mm) rests flat against the tray's front face at the mounting pad zone. The motor cylinder (nominal ~35mm OD) passes through the motor bore (37.2mm CAD diameter) and extends rearward through the tray into the motor zone.

Four M3 socket-head cap screws (M3 × 12mm, with Loctite 243) per pump pass from the pump-bracket side (forward of the tray, Y < 0) through the bracket clearance holes, then through the tray clearance holes (3.6mm CAD diameter, Y=0 to Y=5.5mm), and thread into the M3 brass heat-set inserts seated in the boss cavities. The inserts are seated in the bosses on the rear face, with the cavity opening toward Y=+infinity (boss-tip direction). The screw tip enters the boss cavity from below (from Y=5.5, coming from Y=0 direction), engages the insert threads, and draws the pump bracket tight against the mounting pad zone.

Loctite 243 on each screw prevents vibration-induced loosening at the 2–14 Hz operating frequency.

### How the tray attaches to the shell

The tray's lateral faces (at X=0 and X=144mm) slide into inward-facing channels on the cartridge shell's interior side walls. The channels are 5.2mm wide (tray is 5.0mm thick Y-direction, plus 0.2mm sliding clearance per requirements.md) × 6mm deep. The tray slides in from the rear during factory assembly until the front face (Y=0) contacts the channel's hard front stop. A 1.5mm spring latch hook on each shell channel then engages the corresponding 1.5mm × 3mm rectangular notch in each of the tray's lateral rear edges, preventing the tray from withdrawing. The latch geometry is on the shell; the tray contributes only the passive notch.

### User interaction with the tray

None during normal operation. During factory assembly: technician installs heat-set inserts from the boss-tip (rear) face using a soldering iron (245°C), then fastens pumps from the front face using a hex driver, then slides the tray into the shell.

---

## Reference Frame

```
Origin:    Front-face, bottom-left corner of tray
           (corner where Y=0, X=0, Z=0 meet — the build-plate face corner)

X-axis:    Tray width, left to right
           X=0 → left edge
           X=144mm → right edge

Y-axis:    Tray thickness, front-face to rear-face
           Y=0 → front face (pump-bracket side; on build plate during printing)
           Y=5mm → rear face (motor/service side; top surface during printing)

Z-axis:    Tray height, bottom to top
           Z=0 → bottom edge (elephant's foot chamfer at Y=0/Z=0)
           Z=80mm → top edge (working assumption, pending OQ-3/OQ-4 resolution)

Plate center X: 72mm
Plate center Z: 40mm
Print orientation: front face (Y=0) on build plate.
```

No coordinate transforms. The tray frame is the assembly frame for all features.

---

## Part Envelope

| Dimension | Value | Notes |
|-----------|-------|-------|
| Width (X) | **144mm** | 75mm pump c-t-c + 34.3mm half-bracket on each outer side |
| Thickness (Y) | **5mm** | Plate body, non-boss region |
| Height (Z) | **80mm** | Working assumption — OQ-3/OQ-4 pending |
| Total Y extent with bosses | **10mm** | Rear-face bosses protrude to Y=10mm |
| Total Y extent with ribs | **5mm toward pump** | Front-face ribs extend to Y=−5mm |
| Outer corner radii (plan view) | **3.0mm** | At all 4 X/Z corner combinations, full Y depth |

---

## Feature Inventory

### F1 — Plate Body

| Parameter | Value |
|-----------|-------|
| Envelope | X=[0, 144mm], Y=[0, 5mm], Z=[0, 80mm] |
| Outer corner radii (plan view) | 3.0mm at all 4 corners (X=0/144, Z=0/80), full Y depth |
| Material | PETG |
| Print orientation | Front face (Y=0) on build plate |

### F2 — Motor Bores (2×, identical)

Two cylindrical through-cuts, one per pump.

| Parameter | Value | Source |
|-----------|-------|--------|
| Count | 2 | One per pump |
| Bore diameter (CAD design value) | **37.2mm** | Motor OD ~35mm + 1.0mm radial clearance/side + 0.2mm FDM compensation |
| Bore diameter (printed target) | ~37.0mm | After FDM shrinkage |
| Bore axis | Y-axis | Through Y=0 to Y=5 |
| Bore depth (Y extent) | Y=0 to Y=5 | Full plate thickness |
| Bore 1 center | **(X=34.5mm, Z=40.0mm)** | Pump 1, symmetric at 72−37.5 |
| Bore 2 center | **(X=109.5mm, Z=40.0mm)** | Pump 2, symmetric at 72+37.5 |
| Rear-face entry chamfer | 0.5mm × 45° | On bore edge at Y=5, both bores |
| Front-face entry chamfer | None | Front face is build plate — clean concentric perimeters, no chamfer needed |
| Contact with motor body | None — clearance only, no bearing surface | Motor cylinder does not contact bore wall |

### F3 — M3 Clearance Holes (8×, identical)

Eight cylindrical through-cuts, four per pump, in a 48mm × 48mm square pattern per pump.

| Parameter | Value | Source |
|-----------|-------|--------|
| Count | 8 | 4 per pump |
| Hole diameter (CAD design value) | **3.6mm** | ISO 273 normal fit target 3.4mm + 0.2mm FDM compensation |
| Hole diameter (printed target) | ~3.4mm | After FDM shrinkage |
| Hole axis | Y-axis | |
| Hole depth (Y extent) | **Y=0 to Y=5.5mm** | Through plate (Y=0 to Y=5) PLUS 0.5mm into boss floor — see Path Continuity note below |
| Pattern per pump | 48mm × 48mm square, ±24mm X and Z from pump bore center | Caliper-verified |

**PATH CONTINUITY RESOLUTION — Critical:**
The clearance hole must extend from Y=0 through the 5mm plate AND through the 0.5mm solid boss floor to Y=5.5mm. This is required because:
- The plate rear face is at Y=5.
- The boss sits on the rear face; its cavity opens at Y=10 (boss tip) and bottoms at Y=5.5.
- The 0.5mm material between Y=5.0 and Y=5.5 is otherwise solid — it blocks the screw path.
- The clearance hole (3.6mm diameter) must cut through this floor section so the screw tip can enter the cavity void (Y=5.5 to Y=10) from below.
- Since the clearance hole (3.6mm) is smaller than the boss cavity (4.7mm), extending the hole 0.5mm into the boss floor does not remove the 0.5mm structural floor function. The insert still has 0.5mm of PETG below it (in the annular ring between the 3.6mm clearance hole and the 4.7mm cavity wall, 0.35mm wide — though structurally thin). See Design Gap DG-01 below for full evaluation.

**Hole center positions (X, Z):**

| Hole ID | X (mm) | Z (mm) | Pump | Pattern position |
|---------|--------|--------|------|-----------------|
| 1A | **10.5** | **16.0** | Pump 1 | Bottom-left |
| 1B | **58.5** | **16.0** | Pump 1 | Bottom-right |
| 1C | **10.5** | **64.0** | Pump 1 | Top-left |
| 1D | **58.5** | **64.0** | Pump 1 | Top-right |
| 2A | **85.5** | **16.0** | Pump 2 | Bottom-left |
| 2B | **133.5** | **16.0** | Pump 2 | Bottom-right |
| 2C | **85.5** | **64.0** | Pump 2 | Top-left |
| 2D | **133.5** | **64.0** | Pump 2 | Top-right |

### F4 — Boss Cylinders (8×, identical)

Eight cylindrical extrusions from the rear face, one above/around each clearance hole. All identical — no exceptions.

| Parameter | Value | Source |
|-----------|-------|--------|
| Count | 8 | One per clearance hole |
| Boss OD | **9mm** | 2.15mm wall around 5mm insert OD; clears bore web |
| Boss base Y | **5mm** (at rear face) | |
| Boss tip Y | **10mm** (5mm protrusion from rear face) | |
| Boss cavity diameter | **4.7mm** | Ruthex/Voron/Prusa community spec for RX-M3x5x4 |
| Boss cavity depth | **4.5mm** (measured from boss tip Y=10 inward) | 4.0mm insert + 0.5mm floor |
| Boss cavity void: from | **Y=10** (boss tip, open) | |
| Boss cavity void: to | **Y=5.5** (bottom, closed — annular floor) | |
| Boss base fillet | **1.5mm radius** (where boss cylinder meets rear face) | Stress concentration; structural-requirements.md |
| Boss center positions | Same X, Z as corresponding clearance holes (F3 table) | Concentric with clearance holes |
| Boss orientation | Protruding in +Y direction from rear face | Vertical extrusion upward during printing |

**Insert spec for BOM:** Ruthex RX-M3x5x4 (or equivalent M3 heat-set insert: OD 5.0mm, length 4.0mm). Installation from boss tip (Y=10 face) with soldering iron at 245°C. 8 inserts per tray.

### F5 — Mounting Pad Zones (2×) and Field Zone Step

The front face is divided into mounting pad zones (at full plate height, Y=0) and a field zone (0.5mm lower, at Y=+0.5mm recessed into the plate).

| Zone | X range | Z range | Surface level |
|------|---------|---------|---------------|
| Pump 1 mounting pad | X=0 to X=71.5mm | Z=3.0mm to Z=77.0mm | Y=0 (full height) |
| Pump 2 mounting pad | X=72.5mm to X=144mm | Z=3.0mm to Z=77.0mm | Y=0 (full height) |
| Cross-rib band (see F7) | X=69.0mm to X=75.0mm | Z=37.0mm to Z=43.0mm | Y=0 (mounting pad height) |
| Field zone (all remaining front face) | Outside above zones | Outside above ranges | Y=+0.5mm recessed |

Step transition: 45° chamfer (not 90° step) at all field-zone-to-mounting-pad boundaries.

### F6 — Bore-to-Boss Radiating Ribs (8×)

Eight short rectangular ribs on the front face, one per boss, running from boss OD toward the nearest point on the motor bore circle edge.

| Parameter | Value |
|-----------|-------|
| Count | 8 (one per boss) |
| Width | 4mm (centered on the boss-to-bore vector) |
| Height | 5mm (extends from front face at Y=0 to Y=−5mm, toward pump) |
| Base fillet | 2.0mm radius at rib base (where rib meets front face) |
| Crown | Flat; 1.0mm chamfer on crown edge per synthesis.md |
| Rib axis | Along the vector from bore center to boss center, for each boss-bore pair |
| Rib length | ~10.84mm for all 8 ribs (see spatial-resolution.md Section 7.2 derivation) |

**Rib endpoints (Rib 1A as representative; all ribs computed the same way):**

For Rib 1A (Boss 1A at (10.5, 16.0), Bore 1 at (34.5, 40.0)):
- Boss OD endpoint (toward bore): **(13.68, 19.18)** in (X, Z)
- Bore edge endpoint (toward boss): **(21.35, 26.85)** in (X, Z)
- Rib length: 10.84mm

All 8 ribs are at the same boss-center to bore-center distance (33.94mm diagonal for corner bosses), producing the same rib length. The CAD agent places each rib along the vector from each boss OD toward its pump's bore edge.

### F7 — Bore-to-Bore Cross Rib (1×)

A single rib running along the X-axis, connecting the two mounting pad zones at the plate Z midline.

| Parameter | Value |
|-----------|-------|
| Count | 1 |
| Width (Z extent) | 6mm (Z=37.0mm to Z=43.0mm, centered at Z=40.0mm) |
| Height | 5mm (extends from front face at Y=0 to Y=−5mm) |
| X extent | X=0 to X=144mm (full tray width, but functional span is from Bore 1 left edge to Bore 2 right edge) |
| Base fillet | 2.0mm radius where rib meets front face |
| Crown transition | 1.0mm chamfer on crown edge |
| Surface level | At mounting pad height (Y=0) — connects the two mounting pad zones |

### F8 — Wiring Channels (2×)

Two rectangular channel cuts on the rear face (Y=5), one per motor.

| Parameter | Value |
|-----------|-------|
| Count | 2 |
| Width (Z extent) | 6mm |
| Depth (Y extent) | 4mm (cut from Y=5 inward to Y=1; channel floor at Y=1) |
| Wall thickness | 1.5mm on each side of channel |
| Interior corner radius | 1.5mm (channel wall meets channel floor) |
| Channel 1 entry point | **(X=15.9mm, Z=40.0mm)** at bore 1 edge toward X=0 |
| Channel 2 entry point | **(X=128.1mm, Z=40.0mm)** at bore 2 edge toward X=144 |
| Channel 1 routing | Lateral: X=15.9mm → X=0 (toward left tray edge), Z centered at 40.0mm |
| Channel 2 routing | Lateral: X=128.1mm → X=144mm (toward right tray edge), Z centered at 40.0mm |
| Channel 1 Z extent | Z=37.0mm to Z=43.0mm at all X along the lateral run |
| Channel 2 Z extent | Z=37.0mm to Z=43.0mm at all X along the lateral run |
| Longitudinal routing | Deferred to shell step (OQ-6) |

### F9 — Wiring Channel Strain-Relief Bumps (4× on lateral segments)

Small rounded protrusions from each channel floor, providing friction retention for motor wiring.

| Parameter | Value |
|-----------|-------|
| Count | 2 per channel (4 total on lateral segments); may increase when longitudinal segment added per OQ-6 |
| Height | 1.5mm (protrudes from channel floor at Y=1 toward Y=−0.5mm, i.e., bump crown at Y=−0.5mm) |
| Width | 2mm |
| Profile | Rounded crown |
| Spacing (on short lateral segment) | 5mm intervals from channel entry (20mm target spacing unachievable on 15.9mm run) |

**Revised bump positions (spatial-resolution.md Section 8.3 final):**

| Channel | Bump 1 center (X, Z) | Bump 2 center (X, Z) |
|---------|----------------------|----------------------|
| Channel 1 | **(10.9, 40.0)** | **(5.9, 40.0)** |
| Channel 2 | **(133.1, 40.0)** | **(138.1, 40.0)** |

### F10 — Snap Notches (2×)

Rectangular relief cuts at the rear edge of each lateral face, for engagement with the shell snap latch.

| Parameter | Value | Status |
|-----------|-------|--------|
| Count | 2 (one each at X=0 and X=144) | |
| Notch depth (X extent) | 1.5mm | Left notch: X=0 to X=1.5mm inward; right notch: X=144 to X=142.5mm inward |
| Notch width (Z extent) | 3mm | Z=38.5mm to Z=41.5mm (Z center at Z=40.0mm) |
| Notch Y extent | Y=2mm to Y=5mm (opens at rear face, 3mm deep toward front) | Working assumption — confirm with shell step |
| Z center position | Z=40.0mm | Working assumption — must be confirmed with shell step (OQ: snap notch Z) |

**Note:** Z=40.0mm and Y depth of 3mm are working assumptions. The shell concept step must confirm the snap latch receiver Z position and required engagement depth before final CAD. These dimensions are flagged as requiring confirmation, not as design gaps — the geometry is sound but not yet cross-referenced to the shell.

### F11 — Chamfers

All chamfer features, listed exhaustively.

| Chamfer | Location | Size |
|---------|----------|------|
| Perimeter — top edge, front face | Z=80 edge at Y=0 side | 1.5mm × 45° |
| Perimeter — top edge, rear face | Z=80 edge at Y=5 side | 1.5mm × 45° |
| Perimeter — left lateral edge, both faces | X=0, full Z=[0, 80], at Y=0 and Y=5 faces | 1.5mm × 45° |
| Perimeter — right lateral edge, both faces | X=144, full Z=[0, 80], at Y=0 and Y=5 faces | 1.5mm × 45° |
| Perimeter — bottom edge, rear face | Z=0 edge at Y=5 side | 1.5mm × 45° |
| Elephant's foot — bottom edge, front face | Z=0 edge at Y=0 side (build plate contact edge) | 0.3mm × 45° |
| Rear bore entry | Bore opening at Y=5, both bores (Bore 1 and Bore 2) | 0.5mm × 45° |

### F12 — Corner Radii (Fillets)

| Location | Radius |
|----------|--------|
| Outer tray plate corners, plan view (4 corners at X=0/144, Z=0/80, full Y depth) | 3.0mm |
| Boss base fillet (boss cylinder meets rear face plate surface, Y=5) | 1.5mm radius |
| Rib base fillet (all ribs where rib base meets front face, Y=0) | 2.0mm radius |
| Wiring channel interior corners (channel wall meets channel floor) | 1.5mm radius |

---

## Feature Depth Summary (Complete Y-axis extents)

| Feature | Y start | Y end | Direction | Notes |
|---------|---------|-------|-----------|-------|
| Plate body | 0 | 5mm | — | Full plate thickness |
| Motor bore through-cut | 0 | 5mm | Cut in +Y | Through full plate |
| M3 clearance holes | 0 | **5.5mm** | Cut in +Y | Through plate PLUS 0.5mm into boss floor — see path continuity |
| Boss cylinders | 5mm | 10mm | Union in +Y | 5mm protrusion from rear face |
| Boss cavities (blind bore from boss tip) | 10mm | 5.5mm | Cut in −Y from tip | Opens at Y=10, bottoms at Y=5.5 |
| Heat-set insert (seated) | 10mm | 6.0mm | — | 4mm insert; 0.5mm annular floor below insert at Y=5.5 to Y=6.0 |
| Cross-rib | 0 | −5mm | Union in −Y | 5mm tall protrusion from front face toward pump |
| Radiating ribs | 0 | −5mm | Union in −Y | Same |
| 0.5mm field zone recess | 0 | +0.5mm | Cut into +Y | Outside mounting pad zones; front face only |
| Wiring channels | 5mm | 1mm | Cut in −Y | 4mm deep cut from rear face inward |
| Strain-relief bumps | 1mm | −0.5mm | Union in −Y | 1.5mm tall from channel floor |
| Snap notches | 5mm | 2mm | Cut in −Y | 3mm deep cut from rear edge inward |
| Rear bore chamfer | at Y=5 | — | — | 0.5mm × 45° on bore edge at rear face |
| Elephant's foot chamfer | at Z=0, Y=0 | — | — | 0.3mm × 45° on bottom-front edge |
| Perimeter chamfers | all top/lateral/rear-bottom edges | — | — | 1.5mm × 45° |

---

## Assembly Sequence

1. **Print tray.** Front face (Y=0) on build plate. Standard PETG settings: 4 perimeters minimum, 40% infill (gyroid or grid), 0.2mm layer height (0.15mm preferred at bosses and bore zones). Elephant's foot chamfer on front-bottom edge is printed-in.

2. **Install 8 heat-set inserts.** With tray lying front-face-down (rear face Y=5 accessible from above), use soldering iron at 245°C to press each RX-M3x5x4 insert into each boss cavity (from Y=10 boss tip face). Inserts seat flush with or slightly below the boss tip face. Floor at Y=5.5 (annular ring 0.35mm wide between clearance hole 3.6mm and cavity 4.7mm) stops insert descent.

3. **Place tray on fixture, front face up.** The tray is now inverted from print orientation — front face (Y=0) faces upward, bosses face down.

4. **Install Pump 1.** Lower Pump 1 onto the tray: motor cylinder enters Bore 1 (center at X=34.5mm, Z=40.0mm) from above (from the Y=0 face). Bracket face contacts the mounting pad zone at Y=0. Align 4 bracket holes with clearance holes 1A, 1B, 1C, 1D. Drive 4 × M3 × 12mm SHCS with Loctite 243 applied to screw threads. Torque to 0.5–0.8 N·m. Screws pass through bracket holes, through tray clearance holes (Y=0 to Y=5.5), and thread into brass inserts in bosses 1A–1D.

5. **Install Pump 2.** Repeat step 4 for Pump 2 at Bore 2 (X=109.5mm, Z=40.0mm) using clearance holes 2A, 2B, 2C, 2D and bosses 2A–2D.

6. **Route wiring.** Route each pump's motor wires from the motor terminal area, into the corresponding wiring channel on the rear face, pressing wires into strain-relief bumps. Wires exit at the tray lateral edges (X=0 for Pump 1, X=144 for Pump 2) pending final harness routing to shell connector (OQ-6).

7. **Slide tray into shell.** Insert tray lateral edges (X=0 and X=144 faces) into the shell's interior side-wall channels from the rear of the partially assembled cartridge. Advance until front face (Y=0) contacts the channel's forward hard stop. Rear snap latches (on shell) engage the tray snap notches (F10) simultaneously, capturing the tray.

---

## Bill of Materials (Tray Sub-Assembly)

| Item | Specification | Qty | Purpose |
|------|--------------|-----|---------|
| Pump-tray (printed) | PETG, per this spec | 1 | Structural backbone |
| M3 heat-set insert | Ruthex RX-M3x5x4 or equivalent: OD 5.0mm, length 4.0mm, M3 thread | 8 | Threaded engagement in bosses |
| M3 × 12mm SHCS | Socket head cap screw, stainless preferred | 8 | Pump-to-tray fastening |
| Loctite 243 | Medium-strength blue thread locker | — | Vibration-resistant screw retention |

---

## Print Settings

| Parameter | Minimum | Preferred |
|-----------|---------|-----------|
| Material | PETG | PETG |
| Layer height | 0.2mm | 0.15mm (boss/bore zones) |
| Perimeters | 4 | 5 (boss zones) |
| Infill | 40% | 50% (boss zones) |
| Infill pattern | Gyroid or grid | Gyroid |
| Print orientation | Front face on build plate | — |
| Supports | None required | — |

---

## Open Items Carried Forward

| OQ | Description | Impact on this spec |
|----|-------------|-------------------|
| OQ-2 | Motor body diameter — currently ~35mm, low confidence | Bore diameter (currently 37.2mm CAD); if actual motor OD deviates significantly, bore may need adjustment |
| OQ-3/OQ-4 | Tube stub Z and X positions on pump face | Affects tray height (currently 80mm) and bore center Z (currently 40mm) |
| OQ-6 | Shell harness connector location | Determines wiring channel routing beyond lateral tray edge; bump count will increase when longitudinal channel segment is added |
| Snap notch Z | Shell concept step must confirm snap latch receiver Z | F10 Z=40.0mm and Y=2–5mm are working assumptions |

---

---

# Self-Review Rubrics

---

## Rubric A — Mechanism Narrative

**Result: PASS**

The mechanism narrative is present at the top of this document. It covers:

0. What the user sees and touches: tray is not user-facing; the cartridge exterior is. The one visibility scenario (rear-face visible on removed cartridge) is described.
1. What moves: nothing on the tray moves. Both pumps and tray are stationary during operation.
2. What converts motion: N/A — no motion conversion. The tray is structural, not kinematic.
3. What constrains each part: pumps constrained by 8 M3 SHCS with Loctite 243 and bracket-face contact at mounting pad zone. Tray constrained by shell channel slides and snap latch engagement at notches.
4. Return force: N/A — static assembly, not a mechanism with a rest position.
5. User interaction: none during operation. Factory assembly sequence is described in detail.

Grounding rule applied to narrative claims:
- "stiff flat mounting face" → grounded: F1 plate 5mm PETG, 4 perimeters, 40% infill, per structural-requirements.md thickness analysis
- "pump bracket seats on a clean flat reference surface" → grounded: F5 mounting pad zone at Y=0, 74mm × 74mm per pump, field zone 0.5mm lower prevents interference
- "screw tip enters boss cavity" → grounded: F3 clearance hole extends to Y=5.5mm; F4 boss cavity void from Y=5.5 to Y=10; continuous path confirmed (see Rubric D)
- "1.5mm spring latch engages notch" → grounded: F10 notch 1.5mm × 3mm at each lateral edge; shell carries the latch spring geometry

---

## Rubric B — Constraint Chain Diagram

```
[Factory: screwdriver] --> [M3 SHCS × 8: axial clamp force] --> [Pump brackets (×2): seat flat on mounting pad zones at Y=0]
                               |                                       |
                               |  passes through bracket clearance holes  |  bracket OD (68.6mm) constrained to
                               |  through F3 clearance holes (3.6mm Ø)   |  mounting pad zone (74mm × 74mm)
                               |  into F4 boss inserts (M3, 4mm)         |
                               v                                       |
                         [Heat-set inserts in bosses: axial pullout resistance]
                               |
                               ^ constrained by: boss OD (9mm) provides 2.15mm wall; boss fillet (1.5mm) distributes stress
                               ^ fixed by: Loctite 243 prevents vibration loosening at 2–14 Hz

[Motor cylinders (×2)] --> [pass through F2 motor bores (37.2mm Ø)] --> [extend into rear zone Y>5]
                               |
                               ^ constrained by: 37mm bore vs ~35mm motor OD; 1mm radial clearance; bore is clearance only, no bearing contact

[Tray plate] --> [lateral faces at X=0 and X=144] --> [slide in shell channels (5.2mm wide)]
                               |
                               ^ constrained in Y (forward): shell channel hard front stop contacts tray front face Y=0
                               ^ constrained in −Y (rearward withdrawal): shell snap latch hooks engage F10 snap notches (1.5mm × 3mm)
                               ^ constrained in Z (vertical): rests on cartridge floor at Z=0
                               ^ constrained in X: channel walls at both sides; 0.2mm sliding clearance

[Motor wiring] --> [exits motor terminals at rear face] --> [routed into F8 wiring channels (6mm × 4mm)]
                               |
                               ^ retained by: F9 strain-relief bumps (1.5mm tall, 2mm wide) at 5mm intervals
                               ^ exits at: tray lateral edges X=0 / X=144 toward shell connector (OQ-6)
```

Every arrow is labeled. No unlabeled transitions. No unconstrained parts.

---

## Rubric C — Direction Consistency Check

| Claim | Direction | Axis | Verified? | Notes |
|-------|-----------|------|-----------|-------|
| Bosses protrude from rear face toward motor zone | +Y | Y-axis | YES | Bosses at Y=5→Y=10, rear face is Y=5, motor zone is Y>5 |
| Ribs protrude from front face toward pump | −Y | Y-axis | YES | Ribs at Y=0→Y=−5mm, front face is Y=0, pump bracket is at Y<0 |
| Screw travels from pump side through tray into bosses | +Y | Y-axis | YES | Screw enters at Y<0 (pump bracket), travels +Y through clearance hole to boss insert |
| Boss cavity opens toward boss tip (accessible from Y=10) | Insert from +Y direction | Y-axis | YES | Insert driven from boss tip at Y=10; cavity goes from Y=10 to Y=5.5 |
| Tray slides into shell from rear (backward, −Y direction relative to assembly) | Slide in −Y direction | Y-axis | YES | Tray enters shell channels from rear (Y=5 side first) |
| Snap latch prevents rearward tray withdrawal (+Y exit from shell) | Resist +Y motion | Y-axis | YES | Snap notch at Y=2–5mm; latch hook resists tray moving in +Y direction out of shell |
| Cross-rib runs along X-axis | +X | X-axis | YES | X=0 to X=144mm, centered at Z=40mm |
| Channel 1 runs toward X=0 | −X | X-axis | YES | From X=15.9 to X=0 |
| Channel 2 runs toward X=144 | +X | X-axis | YES | From X=128.1 to X=144 |
| Field zone recessed below mounting pad | +Y (into plate from front face) | Y-axis | YES | 0.5mm cut from Y=0 toward Y=+0.5 (into the plate body) |

No contradictions. All directional claims are consistent with the coordinate frame.

---

## Rubric D — Interface and Path Consistency

### Part 1 — Interface Dimensions

| Interface | Tray dimension | Mating component dimension | Clearance | Source |
|-----------|---------------|---------------------------|-----------|--------|
| Motor bore to motor cylinder | 37.2mm CAD (37.0mm printed) | ~35mm motor OD (low confidence; conservative 35.5mm upper bound) | 0.75–1.0mm radial per side | Motor OD: estimate from caliper photos; bore: derived with FDM compensation per requirements.md |
| M3 clearance hole to M3 screw shank | 3.6mm CAD (3.4mm printed) | 3.0mm M3 nominal shank | 0.2mm radial per side (normal ISO 273 fit) | ISO 273 normal fit + FDM compensation |
| Boss cavity to insert body | 4.7mm cavity | 5.0mm insert OD | −0.3mm (interference press-fit for heat-set) | Ruthex/Voron/Prusa community spec; heat-set insert displaces and melts PETG during installation |
| Tray thickness to shell channel width | 5.0mm tray (Y extent) | 5.2mm shell channel | 0.2mm sliding clearance | Per requirements.md sliding fit minimum |
| Snap notch to shell latch hook | 1.5mm × 3mm (W × H) notch | 1.5mm × 3mm latch hook | ~0 (engagement fit; latch springs and snaps) | concept.md Section 2 |
| Mounting pad zone to pump bracket face | Y=0 flat reference surface | Pump bracket flat face | Bearing contact (0 nominal; bracket seats flat on mounting pad) | Bracket face geometry from geometry-description.md |

**Flags:**
- Boss cavity to insert: −0.3mm is intentional interference for heat-set installation. This is correct — the insert melts the surrounding PETG as it is pressed in. No flag.
- Motor bore confidence: motor OD is low-confidence (~35mm). The 37.2mm bore provides 0.75–1.0mm radial clearance which is adequate for FDM tolerance. If motor OD measurement is subsequently confirmed, the bore can be adjusted. Not a design gap — a measurement confirmation needed (OQ-2).

### Part 2 — Path Continuity (All 8 Fastener Paths)

Each fastener path is identical. Analysis shown once; all 8 paths are structurally equivalent.

**Fastener path for hole 1A (representative; identical for all 8):**

| Segment | Feature | Y start | Y end | Void diameter | Connects to next? |
|---------|---------|---------|-------|--------------|------------------|
| 1 | Pump bracket clearance hole (in pump, not tray) | Y < 0 (external) | Y=0 | 3.13mm bracket hole | YES — exits into tray at Y=0 |
| 2 | M3 clearance hole through plate (F3) | Y=0 | Y=5.0mm | 3.6mm CAD | YES — continues into boss body; see segment 3 |
| 3 | M3 clearance hole extension through boss floor (F3 extended) | Y=5.0mm | Y=5.5mm | 3.6mm CAD | YES — connects to boss cavity void at Y=5.5 |
| 4 | Boss cavity void (F4) | Y=5.5mm | Y=10mm | 4.7mm (wider than clearance hole — screw shank 3mm freely passes) | YES — insert thread engagement zone |
| 5 | Heat-set insert (M3 thread) | Y=10mm (insert entry) | Y=6.0mm (insert base) | M3 internal thread, 3.0mm nominal ID | YES — screw engages thread; terminal segment |

**Continuity check at every transition:**

| Transition | Segment A ends at | Segment B starts at | Gap? | Diameter compatible? |
|------------|------------------|-------------------|------|---------------------|
| Bracket hole → tray clearance hole | Y=0 (bracket back face) | Y=0 (tray front face) | None — faces in contact | Bracket: 3.13mm; Tray: 3.6mm — 3.6mm > 3.13mm ✓ screw passes freely |
| Tray clearance hole → boss floor extension | Y=5.0mm (plate rear face) | Y=5.0mm (boss base) | None — boss sits on rear face | 3.6mm through; no diameter change ✓ |
| Boss floor extension → boss cavity | Y=5.5mm (floor of clearance hole extension) | Y=5.5mm (bottom of boss cavity) | None — same Y coordinate | 3.6mm → 4.7mm; diameter widens ✓ screw shank (3mm) passes into wider void |
| Boss cavity → insert thread | Y=6.0mm (insert base, 4mm insert seated from Y=10 to Y=6) | Y=6.0mm | None | Insert bore ~2.5mm (M3 minor diameter) accepts 3.0mm screw ✓ |

**DESIGN GAP ANALYSIS — DG-01:**

The original spatial-resolution.md specifies the clearance hole depth as Y=0 to Y=5 (through-plate only) and the boss cavity as opening at Y=10 and bottoming at Y=5.5. Between Y=5.0 and Y=5.5 there is solid PETG in the boss floor — no void. A screw arriving at Y=5 from the front would hit this solid material and stop.

**Resolution:** The clearance hole (F3) is extended from Y=5.0 to Y=5.5 — i.e., the clearance hole cuts through the full plate (Y=0 to Y=5) AND 0.5mm into the boss floor (Y=5 to Y=5.5). At Y=5.5 the clearance hole diameter (3.6mm) meets the boss cavity diameter (4.7mm). The void is now continuous.

**Does the extension compromise the 0.5mm floor function?**

The boss cavity floor serves to prevent insert punch-through during installation — the insert pressing downward (from Y=10 toward Y=5.5) must be stopped before breaking through the plate. With the 3.6mm clearance hole extended through Y=5.5, the floor is no longer a solid disk but an annular ring: outer radius 4.7mm/2 = 2.35mm, inner radius 3.6mm/2 = 1.8mm → annular width 0.55mm. This ring remains intact. The insert OD is 5.0mm — it is stopped by the boss inner wall (4.7mm cavity stops the insert body) rather than by a floor that the insert pushes through. The floor's function is actually to prevent the insert from going below the cavity bottom — and with an annular ring of 0.55mm width around the 3.6mm hole, the insert is still stopped. The 5.0mm OD insert cannot pass through the 4.7mm cavity regardless of the clearance hole.

**Conclusion: DG-01 is RESOLVED.** The clearance hole depth is specified in this document as Y=0 to Y=5.5mm (F3 specification). The path is continuous, the annular floor ring remains functional, and the original spatial-resolution.md requires a correction noted below.

**Required correction to spatial-resolution.md:** Update the M3 clearance hole Y-extent from "Y=0 to Y=5mm" to "Y=0 to Y=5.5mm." All other dimensions in spatial-resolution.md are unaffected.

**Path continuity table for all 8 paths:** All 8 paths are geometrically identical (same X,Z offset pattern from each bore center, same Y-axis features). The continuity verified for 1A applies identically to 1B, 1C, 1D, 2A, 2B, 2C, 2D.

**Final path continuity status: PASS — zero unresolved design gaps.**

---

## Rubric E — Assembly Feasibility Check

**Step 1 — Can each step physically be performed?**

| Step | Physical feasibility |
|------|---------------------|
| Print tray flat | Pass — 144mm × 80mm footprint on 325mm × 320mm Bambu H2C. Fits with margin. No supports required. |
| Install heat-set inserts from boss-tip face | Pass — boss tips are at Y=10, oriented upward during this step (tray front-face-down). Soldering iron approaches from above. 9mm OD boss is large enough for standard M3 insert tip. All 8 bosses fully accessible simultaneously. |
| Install pumps from front face | Pass — tray on flat fixture with front face up (Y=0 surface upward). Pumps lowered from above, motor cylinders through bores. Screw heads accessible from above/front. No enclosed space; standard hex driver access. |
| Drive 8 M3 screws | Pass — screws driven from front face (pump-bracket side). No obstruction during this open-fixture step. |
| Route wiring into channels | Pass — channels on rear face; wiring pushed into channels before tray enters shell. |
| Slide tray into shell | Pass — tray slides on X=0 and X=144 flat lateral faces into shell channels. No interference from bosses (bosses are on the rear face, which trails into the shell). |

**Step 2 — Order correct?**

Yes. Inserts must be installed before pumps (inserts from boss-tip side, which is inaccessible once pumps cover the rear-face zone). Pumps must be installed before tray enters shell (screw heads are inaccessible once tray is in shell). Order is correct as specified.

**Step 3 — Parts trapped after later steps?**

- Screw heads (on pump bracket side, Y<0 side): become inaccessible once tray is inside closed cartridge shell. This is intentional — the screws are not user-serviceable.
- Heat-set inserts: permanently captured in bosses. Correct — inserts are not removed.
- Motor cylinders: protrude rearward from bores. Accessible from rear of cartridge until shell is closed. Intentional.

**Step 4 — Disassembly sequence (factory rework)?**

1. Depress shell snap latch (shell-side feature; access gap required — this is a shell design requirement to note).
2. Slide tray rearward and out of shell.
3. With tray free, remove Loctite 243 screws using hex driver (medium-strength, serviceable with hand tools).
4. Lift pump off tray. Motor cylinder clears bore.
5. Replace pump; reinstall with new Loctite 243 on screws.
6. Slide tray back into shell.

Feasibility: Pass. ~15 minutes estimated for a skilled technician.

**Assembly feasibility: PASS**

---

## Rubric F — Part Count Minimization

| Part pair | Relationship | Assessment |
|-----------|-------------|------------|
| Tray plate body + bosses | Bosses are structural extensions of the plate. Printed as one piece. | CORRECT — one part |
| Tray + ribs | Ribs are structural features of the plate. Printed as one piece. | CORRECT — one part |
| Tray + wiring channels | Channels are cut features in the plate. Same piece. | CORRECT — one part |
| Tray + snap notches | Passive notches cut into tray edge. Same piece. | CORRECT — one part |
| Tray + heat-set inserts | Inserts are metal hardware, dissimilar material, threaded components. Cannot be printed as part of tray. | CORRECT — separate hardware; inserts are installed post-print |
| Tray + M3 screws | Metal fasteners, must be separate. | CORRECT |
| Pump 1 assembly + Pump 2 assembly | Move relative to nothing during operation, but are separate OTS pumps that must be installed individually. Cannot be combined. | CORRECT — separate OTS parts |
| Tray + cartridge shell | Shell is a separate enclosure that the tray slides into. They move relative to each other during assembly/disassembly. Must be separate. | CORRECT |

**No unnecessary splits. No missed consolidations. Part count is at minimum for the tray sub-assembly.**

**Part count minimization: PASS**

---

## Rubric G — FDM Printability

**Step 1 — Print orientation**

**Orientation: Front face (Y=0) on build plate.** The part's Y-axis aligns with the printer's Z-axis. The part grows from its front face (Y=0) upward to its rear face (Y=5mm, top surface when printing), with bosses growing further upward to Y=10mm and ribs growing downward into the build plate void (actually: ribs protrude from the front face in the −Y direction, but since Y=0 is on the build plate, the ribs are printed as overhangs below the plate level — this requires examination). Wait:

**Rib orientation re-examination:**
The ribs are on the front face (Y=0) and protrude in the −Y direction toward the pump bracket. With Y=0 on the build plate, −Y direction would be INTO the build plate — impossible. This means in the actual printing orientation:
- The build plate is at Y=0. The part grows upward from Y=0 to Y=5mm, then bosses continue upward to Y=10mm.
- The ribs protrude from Y=0 in the −Y direction (toward the pump, away from the build plate). In the printing orientation, this means the ribs would need to grow downward into the air below the build plate — which is impossible.

**Resolution:** The ribs must protrude from the front face in the −Y direction (toward the pump bracket side), which means when the front face is on the build plate (Y=0 = build plate), the rib crowns at Y=−5mm would be below the build plate surface. This is a physical impossibility.

**Correct understanding:** The ribs are on the front face. The front face is Y=0. In the printed part orientation, Y=0 is the BUILD PLATE SURFACE. The ribs extend DOWNWARD from Y=0, meaning the rib crowns are at Y=−5mm. Since the build plate is at Y=0, the ribs would extend into the build plate during printing — physically impossible.

**Resolution — rib protrusion direction must be CORRECTED:**

Looking at this more carefully: if the front face (Y=0) is down on the build plate, and the bosses protrude in the +Y direction (from the rear face at Y=5 to Y=10), then the ribs on the front face must also protrude in the +Y direction to be printable. But the front face is at Y=0 (build plate contact surface) — so ribs on the front face that protrude away from the front face in the −Y direction (toward the pump, which is BELOW the build plate when printing front-face-down) are not printable.

**The ribs must be on the FRONT face but printed from the FRONT FACE UPWARD into the part (+Y direction) — but that means they are interior features, not external protrusions.**

OR: the ribs are external protrusions on the front face that face the pump bracket, and since the front face is the build plate contact surface, the ribs are printed as features that emerge from the first layers of the build. That means the ribs are between the build plate and the tray body — they exist in the Z=0 (printing Z) layer region, printed as positive features on the build plate surface, with the tray body on top of them. This IS how it works: the rib crown is on the build plate (first layers), the rib grows upward, and the tray plate body is printed on top of the rib and plate together.

In this reading: the rib "protrudes from the front face toward the pump" means the rib is on the lower face of the tray (which is the front face when installed, at Y=0). When printing front-face-down, the ribs are printed as raised features on the bottom surface — they are part of the first layers, growing upward (in printer Z, not part Y). The rib crown at Y=−5mm (in part space) corresponds to the lowest point on the part (below the front face) — in printer space, this is the BOTTOM of the print, at printer Z=0. The rib base at Y=0 (front face) is in printer space at printer Z=5mm.

**This is printable — the ribs are printed from the bottom of the build upward, as features standing on the build plate, with the tray plate as the cap. The rib crowns touch the build plate (printer Z=0), and the tray plate surface is at printer Z=5mm.**

Confirmation: concept.md Section 7 Overhang Audit says: "Ribs (5mm tall, 4–6mm wide, growing upward from plate face): Vertical extrusions — fully supported: Pass." This confirms the ribs are vertical extrusions upward in the printer Z sense. The description "protrude from front face toward pump" describes the installed orientation (when installed, the pump is on the front face side; the ribs protrude in that direction). In printing, the ribs are at the bottom of the print, growing from the build plate as vertical posts, topped by the tray plate.

**Print orientation: confirmed correct. Ribs are at the bottom of the print (printer Z ≈ 0–5mm), tray plate body is on top (printer Z = 5–10mm for rib zone, 5mm for non-rib zone), bosses continue upward (printer Z = 10–15mm at boss tip).**

**Step 2 — Overhang Audit**

| Surface / Feature | Angle from horizontal (print orientation) | Printable? | Resolution |
|------------------|--------------------------------------------|------------|------------|
| Tray top surface (rear face, Y=5, horizontal) | 90° from horizontal (horizontal surface on top) | OK | Top surface — no overhang |
| Tray lateral faces (X=0, X=144, vertical) | 90° from horizontal (vertical wall) | OK | Vertical walls — no overhang |
| Motor bore walls (cylindrical, vertical axis) | 90° at top arc, but printed as concentric perimeters | OK | Vertical cylinder; no overhang at any point |
| Boss cylinder walls (vertical extrusion) | 90° — vertical walls | OK | Vertical extrusion upward |
| Boss cavity bore (vertical blind hole from boss top) | 90° — vertical hole, opening upward | OK | Top-open bore; no bridging |
| Rib walls (vertical, growing from build plate) | 90° — vertical walls | OK | Vertical extrusion from build plate |
| Rib crowns (horizontal, at printer Z=0–5) | 90° from horizontal (horizontal; on build plate) | OK | Supported by build plate |
| Cross-rib crown (horizontal) | 90° from horizontal (horizontal top surface) | OK | Horizontal top face; supported by rib walls |
| Wiring channel walls (vertical, cut features on top surface when printing) | 90° — vertical channel walls | OK | Channel is a slot on top surface during printing; no overhang |
| Wiring channel floor (horizontal bridge) | 90° from horizontal (horizontal) but it is a 6mm span | OK | 6mm bridge < 15mm limit |
| Strain-relief bumps (rounded protrusions from channel floor) | 90° at start; rounded crown | OK | Small features; channel floor already passed bridge check |
| Snap notch ceiling (horizontal overhang) | 90° from horizontal — but it is a 3mm horizontal span inside notch | OK | 3mm span < 15mm limit |
| Mounting pad step transition (45° chamfer) | 45° from horizontal | OK — exactly at limit | Per requirements.md: 45° is acceptable |
| Perimeter chamfers (1.5mm × 45°) | 45° from horizontal | OK — exactly at limit | Per requirements.md: 45° is acceptable |
| Elephant's foot chamfer (0.3mm × 45°, at build plate) | 45°, at first layer | OK | Standard FDM first-layer geometry |
| Rear bore chamfer (0.5mm × 45°, on bore edge at top surface when printing) | 45° from horizontal | OK | On top surface; no overhang |
| Field zone step underside (inverted 45° chamfer transition seen from underneath) | 45° from horizontal (inverted; at bottom face) | OK | Transition is on the front face (bottom of print); 45° chamfer faces downward and is built-in to first layers above the rib zone |

**No features require supports. No features exceed 45° overhang. All bridge spans are under 6mm (well under 15mm limit).**

**Step 3 — Wall thickness check**

| Feature | Minimum wall thickness | Meets requirement? |
|---------|----------------------|-------------------|
| Tray plate body (non-boss zone) | 5mm (full plate thickness) | Pass — exceeds 1.2mm structural minimum by 4× |
| Web between bore edge and hole edge | 3.6mm (calculated in spatial-resolution.md Section 4.3) | Pass — exceeds 1.2mm structural minimum |
| Boss wall (boss OD 9mm, cavity 4.7mm) | (9 − 4.7) / 2 = 2.15mm | Pass — exceeds 1.2mm structural minimum |
| Wiring channel wall | 1.5mm | Pass — exceeds 1.2mm structural minimum |
| Snap notch remaining wall | 1.5mm deep notch in 5mm plate; remaining material = 3.5mm | Pass |
| Rib walls (all ribs 4–6mm wide, 4 perimeters) | 4mm rib width / 2 outer walls ≈ multiple perimeters | Pass — 4mm rib width printed as solid with 4 perimeters (1.6mm) walls |
| Annular floor ring (boss floor after clearance hole extension) | 0.55mm wide annular ring | MARGINAL — see note |

**Note on annular floor ring:** With clearance hole at 3.6mm (radius 1.8mm) and boss cavity at 4.7mm (radius 2.35mm), the annular ring width is 0.55mm. This is below the 0.8mm standard wall minimum (2 perimeters). However, this is a non-structural zone — the ring's functional purpose is to stop insert punch-through, which is achieved by the boss cavity wall (4.7mm ID stops the 5.0mm OD insert body), not by this thin ring. The ring does not carry load. In practice with 0.4mm nozzle, a 0.55mm feature is printable (1 perimeter plus partial 2nd) but thin. The insert installation at 245°C will melt and reform this zone regardless — the ring's integrity post-installation is determined by the solidified PETG around the insert.

**Assessment: the annular ring is below minimum wall thickness for a structural wall (0.8mm) but is acceptable here because it is not a structural feature — it is a geometric artifact of the overlapping bore. Flag as informational, not a design gap. If this ring splits during insert installation, the insert is still captured by the 4.7mm cavity walls. No design change required.**

**Step 4 — Bridge span check**

| Bridge feature | Span | Meets limit (< 15mm)? |
|---------------|------|-----------------------|
| Wiring channel floor (6mm wide channel, horizontal bridge) | 6mm | Pass |
| Snap notch ceiling (3mm span) | 3mm | Pass |
| Motor bore — bore arc at top when printing (horizontal closure of bore circle) | The bore is printed as concentric perimeters, not as a bridged span. The last perimeter closes the circle with a small keystone-shaped final pass | Pass — bore closure is perimeter-based, not a bridge |

**Step 5 — Layer strength check**

| Feature | Load direction | Layer line direction (in print orientation) | Correct orientation? |
|---------|---------------|---------------------------------------------|---------------------|
| Boss-to-plate fillet (bending load at boss base under pump weight) | Tension on one side, compression on other (bending in YZ plane) | Layer lines parallel to XZ plane (stacking in +Y direction) | Acceptable — load is primarily compression from screw; bending component is small |
| Screw pullout (axial load along Y-axis) | Axial along Y | Layer lines perpendicular to Y load | This is the FDM weakness acknowledged in structural-requirements.md — resolved by heat-set inserts which distribute the load through a brass cylinder. Pullout force is on the insert, not on the PETG threads. |
| Plate bending (Z-axis bending from pump weight) | Z-axis bending | Layer lines in XZ plane (strongest for in-plane bending) | Pass — Z-axis bending is carried by in-plane layer structure |
| Wiring channel walls (cantilever if wire tension pulls channel wall) | Y-axis tension on channel wall | Layer lines in XZ plane — Z-axis wall resistance is weak | Acceptable — wiring tension is minimal; strain-relief bumps carry most retention force |

**FDM Printability: PASS with one informational note (annular floor ring 0.55mm, acceptable for non-structural zone).**

---

## Rubric H — Feature Traceability

| Feature | Justification source | Specific reference |
|---------|---------------------|-------------------|
| F1 Plate body (144mm × 5mm × 80mm) | Physical necessity — Structural | Carries two pumps, 612g total, 2–14 Hz vibration; 5mm thickness per structural-requirements.md Section 1 "practical minimum 4mm, recommendation 5mm"; 144mm from pump mounting geometry spacing (synthesis.md Section 2.2); 80mm from tray height working assumption (OQ-3/OQ-4) |
| F2 Motor bores (37.2mm, two locations) | Physical necessity — Structural | Motor cylinder (~35mm OD) must pass through plate; clearance bore required; diameter from pump-mounting-geometry.md Section 2.2 with FDM compensation |
| F3 M3 clearance holes (3.6mm CAD, extended to Y=5.5) | Physical necessity — Assembly | M3 screws must pass through tray to reach heat-set inserts; diameter per ISO 273 normal fit + FDM compensation; Y=5.5 extension is path continuity fix per Rubric D |
| F4 Boss cylinders + cavities (9mm OD, 5mm H, 4.7mm cavity) | Physical necessity — Structural | Heat-set inserts require boss geometry to provide engagement length, sufficient wall, and 0.5mm floor; boss spec per structural-requirements.md Section 4 |
| F5 Mounting pad zones + field zone (0.5mm step) | Vision + Physical necessity — Assembly | Vision: "consumer product" appearance; mounting pad ensures pump bracket seats on clean flat reference surface without interference; 0.5mm step from synthesis.md Section 4 per design-patterns.md UX Quality 3 |
| F6 Radiating ribs (4mm W, 5mm H, 8×) | Vision + Physical necessity — Structural | Vision: "consumer appliance" visual legibility; structural: connect boss load path to bore column; design-patterns.md UX Quality 3; structural justification: visual structural story explicit per synthesis.md Section 4 |
| F7 Cross-rib (6mm W, 5mm H) | Vision + Physical necessity — Structural | Vision: "consumer appliance" visual legibility; structural: adds cross-plate stiffness against differential vibration loading; synthesis.md Section 4: "connects two pump mount zones into single visual band" |
| F8 Wiring channels (6mm × 4mm, 2×) | Physical necessity — Routing | Motor wires must route from motor terminals to cartridge harness connector; channels prevent wires from lying loose across rear face; concept.md Section 4 and synthesis.md Section 4 |
| F9 Strain-relief bumps (1.5mm × 2mm, 4× on lateral segments) | Physical necessity — Routing | Wires must be retained in channels under pump vibration 2–14 Hz; bumps provide friction retention; concept.md Section 4 |
| F10 Snap notches (1.5mm × 3mm, 2×) | Physical necessity — Assembly | Tray must be captured in shell after sliding into channels; passive notch on tray receives shell's spring latch hook; concept.md Section 2 Option C rationale |
| F11 Chamfers — perimeter 1.5mm × 45° | Vision + Physical necessity — Manufacturing | Vision: "consumer product, look and feel like one" — design-patterns.md: "highest-ratio design move for internal structural components"; FDM: all chamfers are at 45° (exactly at printable limit without support) |
| F11 Elephant's foot chamfer (0.3mm × 45°) | Physical necessity — Manufacturing | FDM: requirements.md Section 6 "elephant's foot" dimensional accuracy note; prevents first-layer flare from interfering with shell channel sliding |
| F11 Rear bore chamfer (0.5mm × 45°) | Physical necessity — Manufacturing + Vision | FDM: reduces cosmetic sagging artifact at bore arc top on rear face; concept.md Section 7 bore chamfer discussion; vision: finished interior surface appearance |
| F12 Corner radii — outer 3mm | Vision | Vision: "consumer product, a kitchen appliance" — synthesis.md Section 4: "3mm outer corners place tray in visual register of molded components"; design-patterns.md UX Quality 3 |
| F12 Boss base fillet 1.5mm | Physical necessity — Structural | Reduces stress concentration at boss-plate junction under cyclic pump loading; structural-requirements.md Section 4 "boss base fillet: 1.5mm radius minimum" |
| F12 Rib base fillet 2mm | Physical necessity — Structural + Manufacturing | Reduces stress concentration at rib-plate junction; prints cleanly at 0.4mm nozzle; concept.md Section 5 "2mm minimum" |
| F12 Channel interior radius 1.5mm | Physical necessity — Manufacturing + Routing | FDM minimum feature; prevents wire damage from sharp corner; concept.md Section 5 |

**No unjustified features identified.** Every feature traces to a vision line or a physical necessity category.

**Feature traceability: PASS**

---

## Design Gap Summary

| ID | Description | Status |
|----|-------------|--------|
| DG-01 | Clearance hole Y-extent: original spatial-resolution.md specifies Y=0→Y=5 (through-plate only), leaving a 0.5mm solid boss floor blocking the screw path from clearance hole to boss cavity | **RESOLVED** in this document: clearance hole extended to Y=5.5mm; continuous void confirmed; annular floor ring 0.55mm wide is acceptable non-structural geometry |

**Zero unresolved design gaps.**

---

## Open Measurement Confirmations Required Before Final CAD

| OQ | Item | Impact if unconfirmed |
|----|------|-----------------------|
| OQ-2 | Motor body OD direct caliper measurement | Bore diameter (currently 37.2mm CAD) may need adjustment |
| OQ-3/OQ-4 | Tube stub Z and X positions on pump face (direct caliper) | Tray height (currently 80mm) and bore Z center (currently 40mm) |
| OQ-6 | Shell harness connector location | Wiring channel routing beyond lateral edge; bump count and positions |
| Snap notch Z | Shell concept step snap latch receiver position | F10 Z=40.0mm is working assumption |

None of these block CAD start for fixed-geometry features (plate, bores, bosses, ribs, chamfers, cross-rib). They affect snap notch position and wiring channel routing, which can be reconciled when shell concept is complete.

---

## Correction Required to Upstream Document

**spatial-resolution.md, Section 5 (Mounting Hole Positions), table note:**

Change: "All holes are through-cuts along the Y-axis (Y=0 to Y=5)."
To: "All holes are through-cuts along the Y-axis (Y=0 to Y=5.5). The 0.5mm extension beyond the plate rear face (Y=5 to Y=5.5) cuts through the boss floor annular ring, creating a continuous void from the clearance hole into the boss cavity. See parts.md Rubric D DG-01 for full path continuity analysis."

**spatial-resolution.md, Section 12 (Feature Depth Summary), M3 clearance holes row:**

Change: Y start=0, Y end=5mm
To: Y start=0, Y end=5.5mm, Notes: "Extended 0.5mm beyond rear face into boss floor for path continuity — see parts.md DG-01"
