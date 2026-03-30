# Pump-Tray Concept
## Physical Architecture

**Status:** Architecture settled. Feeds directly into detailed specification (step 4b).

**Sources:** synthesis.md (primary), design-patterns.md, pump-mounting-geometry.md, structural-requirements.md, tube-routing-envelope.md, kamoer geometry-description.md, john-guest geometry-description.md, requirements.md, vision.md.

---

## 1. Piece Count and Split Strategy

**Decision: One part.**

The pump-tray is a single printed piece. No split is needed.

The governing question is whether any feature creates a build-plate constraint or an overhang that requires splitting. It does not:

- **Width: ~144mm.** The Bambu H2C build plate is 325mm × 320mm. The tray fits in any orientation with over 180mm to spare.
- **Height (Z on part, Y on plate): ~80mm.** Fits trivially.
- **Feature geometry is 2.5D.** Motor bores, clearance holes, bosses, ribs, and wiring channels are all vertical extrusions from a flat plate. Every feature is printable in the flat orientation without supports. Nothing requires a second body.

The only architectural scenario that would force a split is if the tray carried the JG fitting pockets integrally — thickening the rear edge to ~12mm pocket depth would create an L-shaped profile. That scenario is addressed in Section 2 below and rejected on different grounds; it is not a print constraint.

**The tray prints as a single flat part, front face down, in one session.**

---

## 2. Join Method

**Decision: The tray slides into a channel molded into the cartridge shell side walls, and is captured by a snap latch on the rear edge of the channel. No user-visible fasteners. No screws in the tray-to-shell interface.**

### The three options considered

**Option A — Snap-fit tabs on tray edges engage shell walls.**
The tray carries cantilevered snap arms on its lateral or top/bottom edges; the shell walls have catch pockets. The tray snaps in from the front during factory assembly. Problems: snap arm flex direction is Z (perpendicular to build plate), which is the weakest FDM direction per requirements.md — snap arms oriented this way are at higher risk of fatigue failure. Also, snap arms on a 5mm plate edge are short and stiff; achieving adequate flex without over-stressing the arm requires a geometry that is better placed on the shell than on the tray.

**Option B — The tray IS the cartridge rear wall; shell halves snap onto it.**
The tray thickens at its rear edge to 12mm+ to form a rear wall panel, carrying the JG fitting pockets integrally. The shell front wall, top, and bottom snap to the tray's lateral edges. Problems: the tray is no longer a flat plate — it becomes an L-profile. This complicates print orientation (the L-flange adds a significant overhang perpendicular to the plate) and makes the tray the most complex printed part in the assembly. The synthesis explicitly flags the JG fitting pocket location as OQ-5 (highest-priority open question) with the preferred answer being that the fittings belong to a separate rear wall, not the tray. This option merges two resolved design responsibilities into one part unnecessarily.

**Option C (chosen) — The tray is a discrete inner plate that sits in a shell-provided channel.**
The cartridge shell side walls each carry an inward-facing channel (a groove running front-to-back along the interior wall face). During factory assembly, the pump-tray slides into these channels from the rear of the partially assembled cartridge, then is captured. A small snap latch on the interior rear face of the channel engages a notch in the tray's rear edge to prevent forward withdrawal.

### Why Option C

This division of responsibility matches the vision's principles precisely:

- **Tray is structurally pure.** It does the one thing it does well: provide a stiff flat mounting face with bores, bosses, and ribs. Nothing else.
- **Shell carries the assembly interface.** The channel is a shell feature. This means all snap geometry is in the shell, where the tray's flat edges are the engaging surface. The flat edge of a 5mm plate sliding in a channel is the most manufacturing-tolerant interface possible.
- **No user-accessible fasteners inside the cartridge.** The latch is interior, engaged only when the tray is in the shell and the shell is closed. The user sees the assembled cartridge as a black box; the tray attachment is invisible.
- **Factory rework is possible.** If the snap latch is not permanent (i.e., the shell rear face has an access gap for a thin tool to depress the latch), a technician can remove the tray from the shell without destroying either part. The specification step for the shell must preserve this access.
- **Snap geometry is parallel to build plate.** The snap latch is on the shell interior, not on the tray. Tray geometry remains simple; the shell carries the flex.

### Channel geometry (tray interface requirements for the shell)

The shell must provide:
- Interior side-wall channel: 5.2mm wide (5.0mm tray thickness + 0.2mm sliding clearance per requirements.md) × 6mm deep, running the full interior depth of the cartridge.
- A hard front stop at the channel's forward end: prevents the tray from over-traveling forward during assembly.
- A rear snap latch: 1.5mm tall × 3mm wide hook that engages a corresponding 1.5mm × 3mm notch in the top or bottom edge of the tray's rear face. The snap geometry is on the shell. The tray notch is a passive rectangular relief.
- The tray notch on the tray: 1.5mm deep × 3mm wide relief cut into the rear edge of each lateral face (top or bottom edge of the tray body, not the pump-face surface). This is the only tray geometry driven by the shell attachment.

**The tray does not carry the JG fitting pockets.** The rear wall of the cartridge is a separate shell panel. The JG fitting pockets are a shell design decision (as flagged in OQ-5 of the synthesis). This concept does not change that answer — it reinforces it.

---

## 3. Seam Placement

The seam between the pump-tray and the cartridge shell is entirely interior. It is occluded in every assembled state.

- **When the cartridge is fully docked in the enclosure:** The cartridge rear face faces the enclosure interior. The tray-to-shell interface (the channel and snap latch) is behind the cartridge rear wall — invisible from any user viewpoint.
- **When the cartridge is removed from the enclosure:** The user sees the cartridge exterior. The tray-to-shell interface is inside the cartridge body. The tray itself is not visible; only the cartridge shell surfaces are visible.
- **When the cartridge is placed on a surface and the user peers inside (service scenario):** The tray becomes visible through the cartridge open rear face (if the rear wall is removable) or through the front opening if the front wall is open. In this view, the visible feature is the tray's rear face (the motor-side service face). The channel that carries the tray is on the shell interior walls — these are interior surfaces, not the cartridge exterior.

**The tray-to-shell seam is never on any user-facing exterior surface of the assembled cartridge.** It is inside the channel groove on the cartridge interior side wall. The channel opening faces inward (toward the tray), not outward.

The only surface that approaches a "visible seam" is the rear edge of the tray visible through the cartridge rear opening — this is not a seam but the tray's own chamfered edge, which reads as a designed edge, not a parting line.

**Seam location summary:** Shell channel (interior side wall) meets tray lateral edge. Seam is on the interior of the assembled cartridge. Not visible from any exterior viewpoint in normal use.

---

## 4. User-Facing Surface Composition (Service Face)

The service face is the tray's rear face — the motor side. This is the face a technician or curious user sees when looking into the cartridge from the rear.

### What is visible on the service face

**Motor cylinders:** Two 37mm bores appear as large through-holes from which the motor cylinders protrude. The bores have a 0.3mm × 45° chamfer on the rear-face edge (the build-plate elephant's foot chamfer is on the front face; the rear face bore edge can be given a light 0.5mm × 45° chamfer for a finished appearance). The motor nubs (5mm protrusion, ~5–8mm diameter at motor end center) are visible within each bore.

**Boss arrangement:** Eight bosses are visible as raised cylinders on the front face — they are not on the rear face. The rear face is flat in the boss zones because the bosses project from the front face only. From the rear, what is visible at each screw location is the back of the clearance hole: a 3.6mm CAD diameter through-hole flush with the rear plate surface.

**Rib pattern:** The ribs are on the front face, not the rear face. From the rear, the tray presents a largely flat surface. The only rear-face features are:
- Wiring channels (see below)
- The motor bore openings
- The M3 clearance hole openings (8×, flush)
- The rear-edge snap notches (2×, one per side, 1.5mm deep relief cuts)

**Wiring channels:** Two channels, one per motor, on the rear face. Each channel is 6mm wide × 4mm deep. Routing path: from the motor bore edge (near the motor terminal zone) laterally outward toward the tray side edge, then longitudinally forward toward the cartridge harness connector access zone. Each channel includes three strain-relief bumps: 1.5mm tall × 2mm wide, rounded, spaced 20mm apart along the channel floor. The exact routing path (lateral-then-longitudinal vs. diagonal) is resolved when the shell step defines the harness connector location (OQ-6 from synthesis).

**Overall rear face character:** The rear face reads as a flat utility surface with two large bores, two wiring channels running laterally, and a clean perimeter edge. It is not decorative. The structural story is readable: the bores are the motor clearances, the channels route the wires, nothing is hidden. This is the correct internal-component aesthetic for a consumer product.

---

## 5. Design Language

All measurements below are concrete geometric decisions that feed directly to the specification step without further deliberation.

### Corner radii

| Location | Radius |
|----------|--------|
| Outer tray plate corners (4 corners, plan view) | 3.0mm |
| Internal corners where ribs meet plate face | 2.0mm minimum |
| Internal corners where wiring channel walls meet channel floor | 1.5mm |
| Boss base fillet (boss cylinder meets plate face) | 1.5mm radius |

Rationale: 3mm outer corners place the tray in the visual register of molded components. 2mm internal corners prevent stress concentration and print cleanly at 0.4mm nozzle. 1.5mm fillet at boss base is the structural minimum from structural-requirements.md and is confirmed consistent with the 9mm boss OD (fillet does not extend into the 3.7mm web between bore and hole).

### Chamfers

| Location | Chamfer |
|----------|---------|
| Top face (pump-head side) perimeter edge | 1.5mm × 45° |
| Lateral edges (full plate height, both sides) | 1.5mm × 45° |
| Rear face bore edges (both bores) | 0.5mm × 45° |
| Bottom edge (build plate face) | 0.3mm × 45° (elephant's foot, per requirements.md) |

The 1.5mm perimeter chamfer on the pump-face side and lateral edges is the primary quality signal for this part: maximum design intent with minimum material removal.

### Rib geometry

Three rib types, all on the front face (pump-bracket side):

**Bore-to-bore cross rib:**
- Orientation: X-axis, connecting the two motor bore circles at the plate Z midline
- Width: 6mm
- Height: 5mm (flush with boss height — the rib crown and boss tops are coplanar)
- Transitions: 2mm radius where rib base meets plate face; 1mm chamfer on rib crown
- Visual effect: creates a visual band joining the two pump mount zones into a unified structural unit

**Boss-to-bore radiating ribs (8 total, one per boss):**
- Each rib runs from the OD of a boss outward toward the nearest point on the motor bore circle edge
- Width: 4mm
- Height: 5mm (coplanar crown with bosses and cross rib)
- Length: variable (~2–6mm depending on which boss, since the bore-to-hole geometry sets the available span); these are short by nature — the structural story is the load path, not the span
- Transitions: 2mm radius at rib base; no chamfer needed given short length
- Visual effect: the rib pattern reads as converging on the bore from all eight bosses; the structural intent is immediately legible

**Lateral perimeter ribs (conditional):**
- Applied if tray lateral extent beyond the outermost boss pattern exceeds 20mm on either side
- At 144mm tray width with outermost hole at (34.3mm + 24mm) = 58.3mm from tray center → 72mm from center to outer edge; outermost hole at 58.3mm from center → 72 − 58.3 = 13.7mm of plate beyond the outer boss. This is under the 20mm threshold. Lateral perimeter ribs are **not needed** at 144mm tray width.
- If tray width is later revised upward above 164mm (unlikely), add: 3mm wide, 5mm tall, full tray height.

### Mounting pad step

- Mounting pad zone: the flat region around each bore and its 4-boss pattern, covering approximately a 74mm × 74mm area centered on each bore
- This zone sits at full plate thickness surface height
- Field zone: 0.5mm lower than mounting pad zone, covering all plate face area outside the two mounting pad regions and the cross-rib
- Step transition: 45° chamfer (not 90° step) to avoid stress riser and print cleanly
- The 6mm cross rib connecting the two mounting pad zones is at mounting pad height (not field zone height) — it is structurally and visually part of the mounting pad band

### Boss geometry

All 8 bosses are identical. No exceptions:
- OD: 9mm
- Height above plate face: 5mm
- Base fillet: 1.5mm radius
- Cavity diameter: 4.7mm
- Cavity depth: 4.5mm

### Wiring channel

- Width: 6mm
- Depth: 4mm
- Wall thickness: 1.5mm
- Strain-relief bumps: 1.5mm tall × 2mm wide, rounded crowns, 20mm spacing, 3 per channel
- Channel is on the rear face only
- Exact routing path: deferred to shell step (OQ-6)

---

## 6. Service Access Strategy

**Factory assembly sequence for the pump-tray:**

1. Print tray flat. Install 8 heat-set inserts from the front face using soldering iron at 245°C.
2. Place tray on assembly fixture, front face up.
3. Lower pump 1 onto tray: motor cylinder through bore 1, bracket face flat against tray mounting pad zone. Align 4 boss holes with pump bracket holes. Start 4 × M3 × 12–15mm SHCS with Loctite 243. Torque to 0.5–0.8 N·m.
4. Repeat for pump 2 onto bore 2.
5. Route motor wires into wiring channels. Press into strain-relief bumps.
6. Insert tray into shell: slide tray lateral edges into shell side-wall channels from the rear. Advance until forward stop is reached and rear snap latch engages.

**All 8 M3 screws are accessible from the front face in step 3 and 4.** The pump bracket face bears against the tray front face; the screw heads are on the motor side (rear face). This means the screws are inserted from the rear face, through the clearance holes in the tray, into the bosses (inserts) from behind. Wait — this requires re-examination.

**Clarification on screw direction:** The M3 screw passes through the pump bracket hole, through the tray clearance hole, and threads into the heat-set insert in the tray boss. The screw head is on the pump bracket side (front face — the motor/bracket face of the pump assembly). The insert receives the screw from the front. The assembly technician holds the screw from the pump front and drives it toward the tray rear.

Correction to synthesis language: the inserts are installed from the front face (insert cavity opens toward the front face), and the screws are driven from the pump front, through the bracket and tray clearance hole, into the insert. The screw head ends up on the pump-head/bracket side — forward of the tray. This means once both pumps are on the tray, the screw heads are forward-facing and inaccessible once the tray is inside the closed cartridge shell. This is correct and intentional: the screws are not user-serviceable and should not be accessible from any exterior surface.

**Screw accessibility summary:** Accessible during factory assembly (tray is on a flat surface, pumps are lowered onto it, screws are driven from above/front). Not accessible once tray is in shell. Not user-serviceable. This is the correct architecture per requirements.md Section 4: "the user can remove and replace the pump cartridge" — the cartridge is replaced as a unit; no user opens it.

**Factory rework:** A technician can extract the tray from the shell (depress snap latch, slide tray out from rear). With tray out of shell, both pumps are accessible from the front. Remove Loctite 243 screws (medium-strength, removable with standard driver). Pump can be replaced. Reinstall pumps, re-loctite, slide tray back into shell. This is a ~15-minute operation for a skilled technician. Acceptable for field rework or factory QC.

---

## 7. Manufacturing Constraints

### Print orientation

Print flat: pump-face (front face) on build plate. Z-axis equals plate thickness (5mm). This is confirmed mandatory — printing on-edge creates a 37mm bore as a 37mm bridge span, which exceeds the 15mm bridge limit in requirements.md and will distort the bore.

### Build plate fit

Tray envelope: **~144mm W × 5mm thick × 80mm H** (80mm is the working assumption; may increase to 85mm pending OQ-3 resolution).

On the Bambu H2C build plate (325mm × 320mm, single nozzle):
- 144mm × 80mm footprint in plan view
- Leaves 181mm × 240mm of remaining build plate in the two principal directions
- The part fits with enormous margin in any orientation on the plate
- Two trays can be printed simultaneously side by side (144mm × 2 + clearance ≈ 295mm — fits on 325mm axis)

### Overhang audit (flat print orientation, Z = plate thickness)

Every non-horizontal feature, assessed for overhang:

| Feature | Overhang assessment | Result |
|---------|--------------------|----|
| Motor bores (37mm diameter, through-hole, vertical axis) | Circular hole printed horizontally — no overhang; concentric perimeters, fully supported | Pass |
| M3 clearance holes (3.6mm diameter, through-hole, vertical axis) | Same as above — small vertical bores, fully supported | Pass |
| Bosses (9mm OD cylinder, 5mm tall, growing upward from plate face) | Vertical extrusion from plate surface — 100% supported, all perimeter material | Pass |
| Boss cavity (4.7mm diameter, 4.5mm deep blind hole from top of boss) | Blind hole opening upward — no overhang; prints as concentric bridges at top, but top of boss is open, so this is a straight vertical bore | Pass |
| Ribs (5mm tall, 4–6mm wide, growing upward from plate face) | Vertical extrusions — fully supported | Pass |
| Cross rib top surface (horizontal) | Top face of rib is horizontal — fully supported by rib walls | Pass |
| Wiring channels (6mm W × 4mm D, on rear face, grows downward from rear face toward build plate) | Channels are on the rear face, which is the top surface when printing. Channel walls grow upward; channel floor is bridged across. Bridge span: 6mm — well within the 15mm bridge limit. | Pass |
| Wiring channel strain-relief bumps (1.5mm tall, grow up from channel floor) | Floor is a 6mm bridge already cleared; bumps are vertical extrusions from that floor — no additional overhang | Pass |
| 0.5mm mounting pad step (step down to field zone) | The 45° chamfer at the step transition is exactly at the 45° FDM limit — acceptable per requirements.md | Pass |
| Snap notch in lateral edge (1.5mm × 3mm relief cut) | This is a notch cut into the side of the tray. In flat print orientation, the notch is on a vertical wall face. The notch ceiling is a 3mm horizontal span — well within 15mm bridge limit | Pass |
| Perimeter chamfers (1.5mm × 45°) | 45° is exactly at the design limit — acceptable. No support needed. | Pass |
| Elephant's foot chamfer (0.3mm × 45°, build plate face edge) | On the first layer; standard FDM practice | Pass |

**No features require supports. No overhangs exceed 45° from horizontal. No bridges exceed 15mm.**

One note: the bore edges on the rear face (top surface when printing) may have a small cosmetic sagging artifact at the very top of the bore arc where the last unsupported perimeter closes. For a clearance hole this is inconsequential — the motor cylinder does not contact the bore surface. A 0.5mm × 45° chamfer on the rear-face bore edge further reduces this by creating a brief angled approach rather than a horizontal lip.

### Material

PETG. This is specified in the synthesis and confirmed in structural-requirements.md for the reasons stated there (creep resistance, impact toughness, heat-set insert compatibility, Tg 80°C vs. motor operating temperature well below 80°C). Not revisited here.

### Print settings (minimum)

- 4 perimeters throughout
- 40% infill, gyroid or grid
- 50% infill and 5 perimeters at boss zones preferred
- Standard 0.2mm layer height acceptable; 0.15mm preferred for bore roundness and boss surface quality

---

## Summary Architecture

The pump-tray is **one single PETG printed part**. It is a flat plate, ~144mm W × 5mm thick × ~80mm H, printed face-down on the build plate. All features are vertical extrusions from the flat plate — no supports required, no bridges exceeding 6mm.

**Front face (pump-bracket side):** Two mounting pad zones at full plate height, separated by a 0.5mm field zone. Each mounting pad zone has a 37.2mm motor bore, eight M3 boss cylinders (9mm OD, 5mm tall), and radiating ribs converging on the bore. A 6mm cross rib connects the two mounting pad zones along the plate centerline at mounting pad height. 1.5mm × 45° perimeter chamfer on all visible edges.

**Rear face (motor side / service face):** Flat, with two 37mm bore openings, eight 3.6mm clearance hole openings, and two wiring channels (6mm W × 4mm D) with strain-relief bumps. Clean functional surface — no cosmetic features.

**Tray-to-shell interface:** The tray slides into channels in the cartridge shell side walls. The shell carries all snap geometry. The tray contributes only two 1.5mm × 3mm notches in its rear lateral edges for snap engagement. No fasteners in the tray-to-shell interface.

**Seams:** All tray-to-shell seams are inside the cartridge, on interior surfaces. Never on any exterior face of the assembled cartridge.

**Service:** Factory assembly is performed with the tray on a flat fixture, both pumps installed from the front in sequence, screws driven into heat-set inserts, wires routed into channels, then tray slid into shell. Technician rework is possible by extracting tray from shell (snap release) and removing pumps with standard driver. No user-serviceable access.

**Build plate fit:** 144mm × 80mm footprint on a 325mm × 320mm plate — fits with margin, two can print simultaneously.

---

## Open Questions Carried Forward

The following open questions from the synthesis are not resolved by this concept step and must be addressed before final CAD:

- **OQ-1:** Measure screw hole depth in pump head body to confirm M3 × 12mm vs. M3 × 14–15mm screw length.
- **OQ-2:** Caliper motor body diameter directly to confirm 37mm bore adequacy.
- **OQ-3 / OQ-4:** Caliper tube stub Z and X positions on pump face to confirm 80mm vs. 85mm tray height.
- **OQ-6:** Shell concept step defines harness connector location before wiring channel routing is finalized.
- **OQ-7:** Tube routing layout step resolves JG fitting pocket X/Z positions after stub positions are confirmed.

These do not block CAD start for the fixed-dimension features (plate, bores, bosses, ribs, chamfers, cross rib). They affect the snap notch depth and wiring channel routing, which can be finalized in the specification step once the shell concept is in progress.
