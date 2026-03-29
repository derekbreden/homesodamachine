# Pump Cartridge — Conceptual Architecture

This document defines the physical architecture of the pump cartridge mechanism: how the mechanism is split into printed parts, how those parts connect, where the seams fall, and how the whole thing prints and assembles. The interaction design (squeeze-release, rail-guided slide) is settled upstream. This document embodies that interaction in printable parts.

---

## 1. Piece Count and Split Strategy

### Final piece count: 7 printed parts

| # | Part | Material | Function |
|---|------|----------|----------|
| 1 | Bottom shell | PETG | Lower enclosure half: floor, lower side walls with rail grooves, rear wall with JG fitting pockets, spring bosses |
| 2 | Top shell | PETG | Upper enclosure half: ceiling, upper side walls, front wall (palm surface), finger plate slot |
| 3 | Mounting partition | PETG | Internal vertical plate between pump head zone and motor zone; holds both pumps via vibration isolation mounts |
| 4 | Release plate | PETG | Rear-zone plate with 4 stepped bores; rides on collet ODs; depresses all 4 collets simultaneously |
| 5 | Finger plate | PETG | Front-face squeeze surface (finger side); user's fingers pull this to activate release |
| 6 | Linkage arm, left | PETG | Rigid bar connecting finger plate to release plate along the left interior wall |
| 7 | Linkage arm, right | PETG | Rigid bar connecting finger plate to release plate along the right interior wall |

### Evaluation of the synthesis BOM

The synthesis listed 6 printed parts: bottom shell, top shell, release plate, finger plate, 2 linkage arms. This concept adds one part: the mounting partition. The synthesis listed it as part #6 but described it as a separate internal plate — so the count was already 6 custom printed parts in the BOM. The count holds at 7 (counting each linkage arm individually).

**Can any parts be combined?**

- **Finger plate + linkage arms into one piece:** Tempting (reduces count to 5), but the finger plate must translate 2-4mm relative to the shell, while the linkage arms run ~150mm rearward. Printing this as a single U-shaped part would require printing in the Z direction with the long arms cantilevered — prone to warping and weak in bending. Separate arms screw-fastened or press-fit into the finger plate are stiffer and print flat. Keep separate.

- **Release plate + linkage arms:** Same issue. The arms are long bars; the plate is a compact block with precision bores. Combining them creates a part that cannot be printed in any single orientation without compromising one feature. Keep separate.

- **Mounting partition integrated into bottom shell:** Possible — the partition could be a vertical wall rising from the floor. But the partition must span the full interior height (floor to ceiling) to rigidly hold the pumps. If integrated into the bottom half, it would be a 30mm+ tall vertical wall with no top support until the top shell closes. This is printable but fragile during assembly (easy to snap while inserting pumps). A separate partition that drops into slots in both shell halves and is captured at closure is more robust during assembly. Keep separate.

**Should any parts be further split?**

- **Bottom shell rear wall vs. bottom shell body:** The rear wall has the 4 JG fitting pockets (precision press-fit bores). Splitting it off would allow printing the rear wall flat on the build plate for maximum bore accuracy. However, this adds a part, adds a seam on the rear face, and complicates the structural load path (the rear wall takes all the tube-retention force — 350N+ across 4 fittings). The rear wall integral with the bottom shell is stronger and seamless on the back face. The press-fit bores can achieve adequate precision when printed vertically (their axes align with the insertion direction, which is horizontal on the print bed when the bottom shell prints open-face-up). Keep integral.

- **Shell into 3 pieces (bottom, middle band, top):** Would allow the rail grooves to be on a separate mid-height band. Unnecessarily complex. The grooves sit entirely within the bottom shell (see Section 7 for why). No split needed.

### Why each split exists

| Split | Reason |
|-------|--------|
| Bottom shell / Top shell | Print orientation: each half prints open-face-up, exposing all internal features to the build plate or open air. No internal overhangs. Assembly access: internals are loaded into the bottom half before the top closes. |
| Mounting partition (separate) | Assembly access: pumps must be installed onto the partition, then the assembly drops into the bottom shell. Combining with either shell half would require threading pumps into a deep enclosed bay. |
| Release plate (separate) | Relative motion: the plate translates 3mm axially. It must be a free body guided by the collet-hugger bores. |
| Finger plate (separate) | Relative motion: translates 2-4mm relative to the shell front wall. |
| Linkage arms (separate, 2 pcs) | Relative motion: arms connect two moving parts (finger plate and release plate). They must slide through guides in the shell walls. Printing them separately allows flat-on-bed orientation for maximum bending stiffness along the arm length. |

---

## 2. Join Methods

### Shell-to-shell: Bottom shell + Top shell

**Method:** Perimeter snap-fits with optional screw reinforcement.

Cantilever snap-fit hooks printed on the top shell's inner edges engage catch ledges on the bottom shell's outer upper edges. Hooks are spaced every 30-40mm around the perimeter (approximately 12-14 hooks total for the 132mm x 177mm footprint). The hooks engage with 0.3mm interference depth and produce a tactile click during assembly.

For development: 2x M3 screws through the top shell into threaded bosses on the bottom shell (one at each end of the cartridge, on the top face where they are hidden from the user when the cartridge is docked). These screws allow repeated disassembly during development and can be omitted in a final product.

**Joint type:** Semi-permanent. Snap-fits hold permanently under normal use. Screws allow deliberate disassembly with a tool.

### Mounting partition into shell

**Method:** Slot capture.

The bottom shell has two vertical slot channels (one on each side wall interior, at the Y-position of the mounting partition). The partition drops into these slots. The top shell has matching slots. When the shell closes, the partition is captured top and bottom with no freedom of movement. No fasteners. The partition's own stiffness and the slot fit hold it in plane.

Slot width: partition thickness + 0.2mm clearance per side (sliding fit for easy insertion). Slot depth: 2mm into each side wall (provides lateral constraint).

**Joint type:** Captured — no fasteners, fully constrained when shell is closed.

### Pumps to mounting partition

**Method:** M3 rubber vibration isolation mounts (from BOM).

8 total (4 per pump). Each isolation mount has M3 male studs on both ends. One stud threads into the pump bracket hole; the other threads into a matching M3 threaded bore (or passes through a clearance hole into an M3 nut pocket) on the partition. The rubber body decouples vibration.

**Joint type:** Separable with screwdriver. This is the primary service joint — pump replacement requires removing 4 screws per pump from the partition.

### JG fittings into rear wall

**Method:** Press-fit of 9.31mm center body into 9.5mm bore.

The rear wall (integral to bottom shell) has 4 bores at 9.5mm diameter. The JG union's center body (9.31mm OD) press-fits into each bore. The body-end shoulders (step from 9.31mm to 15.10mm) seat against the inboard face of the wall, providing positive axial location. The fittings are retained by friction fit and by the shoulders preventing push-through.

**Joint type:** Press-fit, semi-permanent. Can be pushed out with moderate force for fitting replacement.

### Linkage arms to finger plate

**Method:** Pin-and-socket press-fit.

Each linkage arm has a 3mm cylindrical pin at its front end. The finger plate has two matching 3.1mm sockets (0.1mm clearance for press-fit). The pins press into the sockets. A small dab of CA glue during final assembly prevents pull-out under the cyclic squeeze load.

**Joint type:** Permanent (glued press-fit). During development, friction alone may suffice for testing.

### Linkage arms to release plate

**Method:** Pin-and-socket press-fit (same as finger plate end).

Each linkage arm has a 3mm cylindrical pin at its rear end. The release plate has two matching sockets at its lateral edges, outside the JG fitting pattern. Same press-fit + CA glue approach.

**Joint type:** Permanent (glued press-fit).

### Return springs

**Method:** Compression springs captured between bosses.

Two compression springs (~5mm OD, ~10mm free length) sit on cylindrical bosses — one boss on the inboard face of the rear wall, one on the rearward face of the release plate. The bosses are 3mm diameter, 3mm tall, and center the spring coils. The springs are captured (not bonded) and provide 5-10N of return force at the 3mm working compression.

**Joint type:** Captured, no fasteners. Springs drop onto bosses during assembly and are held by the plate.

---

## 3. Seam Placement

### Primary seam: Shell parting line

The shell splits horizontally (XY plane) at Z = 33.5mm (mid-height of the 67mm cartridge). This seam runs continuously around all four vertical faces of the cartridge: both sides, front, and back.

**Seam treatment:** The top shell is inset 0.3mm from the bottom shell on all four sides. This creates a deliberate step rather than a flush joint. The step reads as an intentional design line — a feature, not a flaw. The 0.3mm recess hides any gap variation (per design patterns research: seam gaps under 0.3mm for finished-product appearance).

**Where the seam falls on each face:**

- **Left and right sides:** The seam runs horizontally at mid-height, well above the rail grooves (which are in the lower portion of the side wall). The seam looks like a subtle belt line running the full depth of the cartridge. It does not cross any functional feature.

- **Rear face:** The seam runs horizontally across the back. The four tube holes are centered vertically (they straddle the mid-height), so the seam passes between the upper and lower pairs of tube holes. The 0.3mm step is visible but reads as intentional alongside the tube holes.

- **Front face:** The seam runs horizontally across the front, between the palm surface (upper zone, part of the top shell) and the finger plate zone (lower zone). The finger plate itself is a separate part and has its own seam against the shell — see below. The horizontal parting line on the front face is hidden by the natural visual break between the palm zone and the finger recess.

### Secondary seam: Finger plate to shell

The finger plate sits in a rectangular recess in the front face of the cartridge. It translates 2-4mm during the squeeze action. The gap between the finger plate edges and the recess walls is 0.5mm per side (enough for free sliding motion without visible daylight). This gap is uniform and reads as an intentional slot — it communicates "this part moves" to the user.

### No other visible seams

The mounting partition, release plate, linkage arms, and return springs are entirely internal. No seams from these parts are visible on any exterior surface.

---

## 4. User-Facing Surface Composition

### What the user sees (front to back)

**Front face — the interaction zone:**

The front face is divided into two visual zones by the finger plate recess:

- **Upper zone (palm surface):** A flat, continuous PETG surface spanning the full width of the cartridge and the upper ~60% of the front face height. This is part of the top shell — a single printed surface with no seams or fasteners. The palm rests here during the squeeze. Subtle crosshatch texture (0.2mm deep, 1mm pitch) provides grip without looking industrial.

- **Lower zone (finger plate):** A flat PETG surface inset ~3mm from the palm surface. The 3mm recess creates a finger-hold. The finger plate spans most of the cartridge width but is narrower than the palm surface by ~6mm per side (3mm shell wall on each side of the recess). The same crosshatch texture as the palm surface. A 0.5mm gap surrounds the finger plate on all sides, communicating that this part moves.

The visual hierarchy is clear: the front face has two flat planes at different depths, separated by a visible gap. Nothing else. No labels, no fasteners, no exposed mechanism.

**Side faces — rail grooves:**

Each side has a single rectangular groove running the full depth. The groove is 4.5mm wide and 4.5mm deep — visually obvious, not a hairline slot. The groove mouth at the front has a 5mm x 30-degree chamfer that tapers to a wider opening, communicating the direction of insertion. The rest of the side wall is flat and featureless except for the horizontal parting line at mid-height.

**Rear face — tube connections:**

Four holes arranged in a 2x2 pattern, each 6.5mm diameter (tube OD + chamfer). Each hole has a 0.5-1.0mm chamfer ring, making the holes look finished and intentional. The four blade terminal slots are positioned in the corners of the rear face, recessed 1mm into the surface and surrounded by a 0.5mm lip so they read as deliberate features, not exposed metal. The horizontal parting line crosses the rear face between the upper and lower hole pairs.

**Top and bottom faces:**

Featureless flat surfaces. The bottom is the build-plate face of the bottom shell (smoothest possible FDM surface). The top is the build-plate face of the top shell (equally smooth). When the cartridge is docked, neither face is visible.

### Visual hierarchy summary

1. **Dominant features:** Finger plate recess on front (the interaction point — the user's eyes go here first)
2. **Secondary features:** Rail grooves on sides (guide the eye along the insertion axis)
3. **Tertiary features:** Tube holes on rear (only visible during insertion/removal)
4. **Hidden features:** Everything else (parting line reads as a design accent, not a feature)

---

## 5. Design Language

### Material

PETG throughout. Chosen for its combination of creep resistance (survives years of static load on rails), toughness (survives drops and repeated squeeze cycles), temperature tolerance (comfortable to 75C in a kitchen environment), and printability on the Bambu H2C without an enclosure. See rail guidance research for the full material comparison.

### Color

Matte black. A single color for the entire cartridge. The finger plate is the same color as the shell — the 3mm recess depth and the surrounding gap slot provide sufficient visual contrast without requiring a second color. If testing shows the squeeze zone needs more visual distinction, a contrasting texture (smooth finger plate against textured shell, or vice versa) achieves this without introducing a second filament.

### Corner treatment

All exterior edges have 1mm fillets (radius). This eliminates the sharp, brittle feel of raw FDM edges and gives the cartridge a finished, handle-able quality. The fillets also reduce stress concentrations at the shell parting line. Interior edges (not user-facing) are left sharp or have 0.5mm fillets where needed for print quality.

### Surface finish

- **Top and bottom faces:** Glass-smooth (printed directly on the build plate with a smooth PEI sheet).
- **Front and rear faces:** Vertical walls during printing — natural FDM layer-line texture (Ra ~15-25 micrometers). Acceptable for a matte black part. The crosshatch grip texture on the squeeze zones masks any layer-line variation.
- **Side faces:** Same vertical-wall finish. The rail grooves are interior channels printed with layers parallel to the groove axis — smooth sliding surface.

### What makes this a product

1. **Single material, single color** — no visual complexity. The cartridge reads as one object, not an assembly.
2. **Recessed parting line** — the 0.3mm step at the shell joint looks intentional.
3. **No visible fasteners** — all assembly is internal (snap-fits, press-fits, captured springs).
4. **Every visible feature has obvious purpose** — tube holes, rail grooves, squeeze recess. Nothing decorative, nothing mysterious.
5. **Consistent edge treatment** — 1mm fillets on every exterior edge.
6. **Deliberate gap at the finger plate** — communicates "this moves" without labels or arrows.

---

## 6. Service Access Strategy

### User service: none

The cartridge is the replaceable unit. When pumps wear out, the user removes the entire cartridge and replaces it. The user never opens the cartridge, never accesses internals, never replaces individual components. The cartridge is a sealed module from the user's perspective.

### Developer service: shell disassembly

During development and prototyping, the developer needs to:

1. **Access pumps** (most frequent): Replace or adjust pumps, re-route tubes, adjust vibration mounts. Requires removing the top shell.
2. **Access release plate and linkage** (moderate frequency): Tune release plate travel, adjust linkage arm fit, replace springs. Requires removing the top shell and possibly lifting out the mounting partition.
3. **Access JG fittings** (rare): Replace a damaged fitting, re-press-fit a loose fitting. Requires removing the top shell, pumps, and partition to reach the rear wall.

**Disassembly sequence:**
1. Remove 2x M3 development screws from top face (if installed).
2. Pry top shell off bottom shell at the snap-fit hooks (a spudger or flat screwdriver inserted at the rear face works — the rear has no functional features that would be damaged by prying).
3. All internals are now exposed in the open-top bottom shell.
4. Pumps lift off the partition after removing 4x M3 isolation mount screws per pump.
5. Partition lifts out of its side-wall slots.
6. Release plate, linkage arms, and springs are now accessible.

**Reassembly** is the reverse. The snap-fit hooks can withstand at least 20-30 assembly/disassembly cycles before significant wear (PETG is tough and the hook geometry includes a shallow entry ramp).

The 2x M3 development screws provide insurance: if a snap-fit hook breaks during prototyping, the screws hold the shell closed. In production, the screws are omitted and the snap-fits alone are sufficient.

---

## 7. Manufacturing Constraints

### Print bed: Bambu H2C, 325mm x 320mm x 320mm (single nozzle)

The cartridge envelope is 132mm x 67mm x 177mm. Every part fits on the bed with large margins.

### Part-by-part print orientation

**Bottom shell (132mm x 33.5mm x 177mm, open-top half-box):**
- **Orientation:** Open face up. Floor on the build plate. Side walls and rear wall rise vertically.
- **Why:** Floor gets the smoothest surface (build plate face). Side walls print as vertical surfaces — rail grooves are rectangular channels cut into vertical walls, requiring no supports. JG fitting bores in the rear wall are horizontal holes (their axes point rearward, parallel to the build plate) — these print as bridged circles, which is acceptable for press-fit bores at 9.5mm diameter (well under the 15mm bridge span limit). The bore accuracy is adequate for a press-fit (tolerance is 0.1mm on a 9.5mm bore).
- **Overhangs:** The rail groove is a rectangular pocket in the side wall. The top surface of the groove is a horizontal ceiling inside a vertical wall — this is a short bridge (~4.5mm span), well within limits. The JG fitting pockets have a 15.1mm counterbore around each 9.5mm press-fit bore; the shoulder of this counterbore is a bridge but only spans ~3mm per side (15.1 - 9.5 = 5.6mm diameter step, so ~2.8mm radial bridge). No supports needed.
- **Snap-fit hook catches:** Printed on the outer upper edge of the side walls. These are horizontal ledges on vertical walls — 45-degree chamfer on the underside eliminates the overhang. The catch face is perpendicular to the wall (horizontal) and only 0.3mm deep — the hook from the top shell does the flexing, not this catch.
- **Build plate footprint:** 132mm x 177mm. Well within 325mm x 320mm.

**Top shell (132mm x 33.5mm x 177mm, open-bottom half-box):**
- **Orientation:** Open face up (ceiling on build plate, walls rising up). The part is printed "upside down" relative to its assembled position.
- **Why:** Ceiling gets the build-plate smooth finish. The front wall (palm surface) is a vertical surface — good layer-line finish. Snap-fit hooks are cantilever beams protruding from the inner edges of the side walls — they flex downward (toward the build plate in printing orientation), meaning the flex direction is in the XY plane. This is the correct orientation for snap-fit arms per the manufacturing constraints: flex direction parallel to the build plate.
- **Finger plate slot:** A rectangular opening in the front wall (lower portion when assembled, which is the upper portion when printing upside-down). The slot is a simple rectangular cutout in a vertical wall — no overhang issues. The slot's upper edge (which becomes the lower edge when assembled, forming the bottom of the finger plate recess) is a horizontal surface inside the front wall. This is supported by the wall below it in print orientation — no overhang.
- **Build plate footprint:** 132mm x 177mm.

**Mounting partition (~128mm wide x ~63mm tall x ~5mm thick):**
- **Orientation:** Flat on the build plate (lying on its face).
- **Why:** The partition is essentially a flat plate with two circular motor bores (~36mm) and 8 M3 through-holes. Printed flat, all holes are vertical (Z-axis) — perfect circles with no bridging issues. The plate thickness (5mm) is only ~25 layers at 0.2mm layer height — fast print.
- **Motor bores:** 36mm diameter vertical holes. Print perfectly as continuous perimeter circles.
- **Build plate footprint:** 128mm x 63mm.

**Release plate (~50mm x 50mm x 5mm):**
- **Orientation:** Flat on the build plate (face down).
- **Why:** The stepped bores (6.5mm, 9.8mm, 15.4mm) are critical-tolerance features. Printed as vertical holes (Z-axis), they produce the best circularity and diameter accuracy. The plate is small and thin — fast print, minimal material.
- **Build plate footprint:** 50mm x 50mm.

**Finger plate (~120mm wide x ~30mm tall x ~4mm thick):**
- **Orientation:** Flat on the build plate (face down).
- **Why:** The face that the user touches is the build-plate face — smoothest possible surface. The two pin sockets for the linkage arms are vertical holes — accurate circles. The crosshatch grip texture is applied to the build-plate face using the slicer's bottom pattern settings or a textured build plate.
- **Build plate footprint:** 120mm x 30mm.

**Linkage arms (2 pcs, each ~150mm long x 6mm wide x 3mm thick):**
- **Orientation:** Flat on the build plate (lying on the 6mm face).
- **Why:** The arms experience bending loads (the user's 40-60N squeeze force creates a bending moment along the arm length). Layers stacking through the 3mm thickness means bending loads are carried by continuous perimeter extrusions along the 150mm length — maximum stiffness and strength. If printed standing up (3mm on the bed, 150mm tall), layers would be perpendicular to the bending plane — catastrophically weak.
- **End pins:** 3mm cylindrical pins at each end are printed horizontally on the bed, which makes them slightly oval. A 0.1mm oversize on the pin diameter compensates — the press-fit into the sockets self-corrects the oval.
- **Build plate footprint:** 150mm x 6mm each.

### Critical manufacturing notes

1. **JG fitting press-fit bores:** The 9.5mm bores in the rear wall print as horizontal holes (bridged circles). Per the requirements, add 0.1mm to the hole diameter for press-fit compensation: design the bore at 9.6mm, expecting it to print at ~9.5mm. Verify with a test print before committing.

2. **Rail grooves:** The 4.5mm wide x 4.5mm deep grooves in the side walls print as rectangular channels in vertical walls. The groove ceiling is a 4.5mm bridge — within limits. Layer lines run parallel to the groove length (the insertion axis), giving the smoothest possible sliding surface. This is the ideal print orientation per the rail guidance research.

3. **Snap-fit hooks on the top shell:** The hooks are cantilever beams ~10mm long, 2mm thick, 8mm wide. They flex in the XY plane (parallel to the build plate). Per the design patterns research, PETG at 5% strain with a 2mm thick, 10mm long beam provides ~1.5mm of deflection — sufficient for the 0.3mm hook engagement. The hook tip has a 30-degree entry ramp and a 1mm fillet at the root.

4. **Elephant's foot:** Both shell halves have their mating edges at the top of the print (farthest from the build plate), so elephant's foot does not affect the parting line fit. The build-plate faces (bottom of bottom shell, ceiling of top shell) are cosmetic surfaces that benefit from the smooth bed finish but should have a 0.3mm x 45-degree chamfer on their perimeter edges to prevent elephant's foot flaring at the seam.

---

## 8. Critical Architecture Decisions

### Shell split: Horizontal at mid-height

The shell splits horizontally at Z = 33.5mm (the XY plane at mid-height). Top half and bottom half.

**Why horizontal, not vertical (left/right):**
- A vertical split would place a seam down the center of the front face, splitting the palm surface in two. The vision requires the palm surface to be a single, continuous, seamless plane.
- A vertical split would split the rear wall and its 2x2 JG fitting pattern across two parts, complicating the press-fit bore alignment.
- A vertical split would place seams on the top and bottom faces — the smoothest surfaces (build-plate faces) would have a joint running through them.

**Why horizontal, not vertical (front/back):**
- A front/back split would place the seam on both side faces running vertically — crossing the rail grooves. The groove would be split between two parts, requiring precise alignment to form a continuous channel.
- The rear wall with JG fittings must be one rigid piece to withstand the 350N+ tube retention force. Splitting front/back would either place this wall in one half (concentrating all structural load in one piece) or split it (weakening it).

**Horizontal split advantages:**
- Each half prints open-face-up with all internal features accessible.
- Rail grooves are entirely in the bottom half (positioned in the lower portion of the side walls), printed as intact channels.
- The palm surface is entirely in the top half — one unbroken surface.
- The rear wall is entirely in the bottom half — one rigid structure with all 4 JG fitting bores.
- The parting line on the sides reads as a horizontal accent line, natural for a rectangular product.

**Rail groove placement:** The grooves are positioned with their centerline at Z = 15mm (15mm above the bottom face). This places them entirely within the bottom shell half (which extends from Z = 0 to Z = 33.5mm). The groove spans from Z = 12.75mm to Z = 17.25mm (4.5mm tall centered at Z = 15mm), with 12.75mm of solid wall below and 16.25mm above — both well above the 1.2mm structural minimum.

### Release plate linkage routing

The two linkage arms connect the finger plate (front face, lower zone) to the release plate (rear zone, 15-20mm from back face). Total routing distance: approximately 150mm.

**Routing path:** The arms run along the bottom outer corners of the pump bays.

The pump heads are 62.6mm square with rounded corners. The cartridge interior at the pump head zone is a rectangular bay ~63mm wide x ~63mm tall per pump. In the corners where the rounded pump head meets the rectangular bay wall, there is a triangular dead space approximately 4mm deep on each side of the corner radius. The linkage arms (3mm x 6mm cross-section) fit in this corner space.

Specifically, each arm routes through the bottom-outer corner of its respective pump bay:

1. **Front zone (Y = 2mm to 27mm):** The arm exits the finger plate at the bottom-left or bottom-right corner and enters the tube routing clearance zone. This zone is 25mm deep and spans the full width — plenty of room. The arm runs rearward along the outer bottom corner of the floor.

2. **Pump head zone (Y = 27mm to 75mm):** The arm continues rearward in the bottom-outer corner of the pump bay. The pump head's rounded corner provides ~4mm of clearance. The arm fits in a printed channel (a shallow rectangular slot in the floor of the bottom shell) that guides it and prevents lateral shift. The channel is 7mm wide x 4mm deep (arm cross-section 6mm x 3mm plus 0.5mm clearance per side).

3. **Motor zone (Y = 75mm to 150mm):** Past the mounting partition, the motor is only ~35mm diameter in a 62.6mm square bay. The arm continues along the bottom-outer wall with 14mm+ of clearance around the motor. No spatial conflict.

4. **Rear zone (Y = 150mm to 177mm):** The arm connects to the release plate at its lateral edge, outside the 2x2 JG fitting pattern. The arm terminates in a 3mm pin that press-fits into a socket on the release plate.

**Arm guidance:** The bottom shell has shallow printed channels (slots in the floor) that the arms slide within. The channels constrain the arms laterally while allowing axial motion (the 2-4mm of squeeze travel translates to 2-4mm of arm travel fore-and-aft). The channel walls are 1.2mm thick (structural minimum), and the channel is open on top (covered by the pump heads and partition when assembled, but accessible during assembly).

**Clearance with mounting partition:** The partition has two notches at its bottom-outer corners where the linkage arms pass through. Each notch is 8mm wide x 5mm tall — the arm (6mm x 3mm) slides freely through with 1mm clearance per side.

### Mounting partition integration

The mounting partition is a vertical plate oriented in the XZ plane at Y = ~75mm (the junction between pump head zone and motor zone). It spans the full interior width (~128mm) and the full interior height (~63mm).

**Features on the partition:**

- **Pump head side (forward face):** Flat surface. No features — the pump heads bear against this face through the vibration isolation mounts.
- **Motor side (rearward face):** Two motor bores (~36mm diameter), centered on each pump's axis. The motor bodies pass through these bores. 8x M3 through-holes in two 48mm-square patterns, one per pump. The vibration isolation mount studs thread into these holes from the motor side; the pump bracket sits on the motor side of the partition.
- **Bottom edge:** 2mm x 2mm registration tabs on each end engage slots in the bottom shell floor.
- **Top edge:** 2mm x 2mm registration tabs on each end engage slots in the top shell ceiling.
- **Bottom corners:** Two 8mm x 5mm notches for the linkage arm pass-through.

**Load path:** Pump weight (200-300g per pump) transfers through the isolation mounts into the partition, through the partition's bottom tabs into the bottom shell floor, and through the floor into the rails and dock. The partition is in compression between the floor and ceiling when the shell is closed — it cannot tilt or shift.

---

## 9. Architecture Summary

The pump cartridge is a 7-piece PETG assembly:

**Shell:** Two halves joined by perimeter snap-fits at a horizontal parting line (Z = 33.5mm). The bottom half contains the floor, lower side walls with rail grooves, and the rear wall with 4 JG press-fit fitting pockets. The top half contains the ceiling, upper side walls, the palm squeeze surface (front wall), and the finger plate recess opening. The parting line is a deliberate 0.3mm step, visible on all four sides. All exterior edges have 1mm fillets. Matte black PETG throughout.

**Internal structure:** A mounting partition drops into slots in both shell halves at the pump head / motor junction plane. Two pumps mount to the partition via M3 rubber vibration isolation mounts (4 per pump). The partition spans the full interior width and height and is captured without fasteners when the shell closes.

**Release mechanism:** A release plate with 4 stepped collet-hugger bores sits in the rear zone, guided by the collet ODs. Two rigid PETG linkage arms (3mm x 6mm x 150mm) run from the finger plate along the bottom-outer corners of the pump bays, through notches in the mounting partition, to the release plate. Two compression springs between the rear wall and the release plate provide 5-10N of return force. The user squeezes the finger plate toward the palm surface (2-4mm travel), the arms pull the release plate rearward (same travel, 1:1 ratio), and the plate depresses all 4 collets simultaneously.

**User-facing surfaces:** Front face has two flat zones (palm surface above, finger plate below) separated by a 3mm recess and a 0.5mm sliding gap. Side faces have 4.5mm x 4.5mm rail grooves with 5mm entry chamfers. Rear face has 4 chamfered tube holes and 4 recessed blade terminal slots. Every visible feature has an obvious purpose.

**Printing:** All 7 parts print on the Bambu H2C in PETG with no supports required. Both shell halves print open-face-up. The partition, release plate, and finger plate print flat. The linkage arms print flat for maximum bending strength. No part exceeds 177mm in any dimension (the bed is 325mm x 320mm).

**Assembly sequence:**
1. Press-fit 4 JG fittings into rear wall bores of bottom shell.
2. Drop return springs onto rear wall bosses.
3. Place release plate over JG fittings (collet-hugger bores engage collets).
4. Install linkage arms into bottom shell floor channels, connecting to release plate.
5. Mount both pumps onto mounting partition via isolation mounts (8x M3).
6. Drop pump-partition assembly into bottom shell slots.
7. Route BPT tubes from pump stubs to JG fitting ports.
8. Connect finger plate to linkage arm front ends.
9. Connect blade terminal wiring from motor terminals to rear-face blade mounts.
10. Close top shell onto bottom shell — snap-fits engage, partition captured, finger plate protrudes through front face slot.
11. Install 2x M3 development screws (optional).
