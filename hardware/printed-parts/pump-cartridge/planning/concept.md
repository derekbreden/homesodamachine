# Pump Cartridge -- Conceptual Architecture

This document defines the physical architecture of the pump cartridge mechanism: how the interaction described in the synthesis is embodied in printed parts that fit the printer, assemble cleanly, and look like a consumer product.

---

## Architecture Summary

The cartridge is 5 printed parts and 1 dock part:

1. **Top shell** -- the palm surface, pump mounting plate, rear bulkhead, and upper rail grooves, printed as one piece
2. **Bottom shell** -- the finger-side surface, lower rail grooves, and the lower enclosure of the cartridge, printed as one piece
3. **Release plate** -- rigid plate with 4 through-holes, rides on guide slots in the shell walls
4. **Lever pair** -- two symmetric lever arms that pivot inside the cartridge and convert finger pull into plate push
5. **Finger bar** -- the flat finger-contact surface, connected to the long arms of both levers, exposed through a slot in the bottom shell
6. **Dock cradle** -- the enclosure-side part that holds the rails, tube stubs, retention latch, and electrical connector (not part of the cartridge itself, but designed here because the interface is defined here)

---

## 1. Piece Count and Split Strategy

### Why 5 cartridge parts (not 2, not 8)

The cartridge cannot be printed as one piece because the pumps, fittings, springs, levers, and release plate must be assembled inside. It splits into the minimum number of parts that allows assembly and satisfies print constraints.

**Top shell.** This is the structurally dominant part. It contains:
- The flat palm-contact surface on its underside (which is the build-plate face during printing -- smoothest finish)
- The pump mounting plate as an internal horizontal shelf, spanning the full width, with two 36.4 mm motor bores and eight 3.4 mm screw holes at 48 mm square patterns
- The rear bulkhead with four 17.0 mm holes for the PP1208W bulkhead fittings
- The upper half of the T-slot rail grooves on both side walls
- Spring pockets (two cylindrical pockets on the forward internal wall that seat the return springs)
- Lever pivot bosses (two internal bosses with 3.1 mm holes for the 3 mm steel pivot pins)
- The over-center detent cantilever arm (printed integral with an internal wall, 1.5 mm bump engaging a groove on the release plate edge)

The pump mounting plate is not a separate part. It is a horizontal shelf printed as part of the top shell, with ribs connecting it to the side walls and rear bulkhead. This eliminates one part and one join, and makes the plate-to-bulkhead alignment inherent rather than assembled.

**Bottom shell.** This is the closure piece. It contains:
- The lower half of the T-slot rail grooves on both side walls
- The slot through which the finger bar protrudes (a rectangular opening on the front face, approximately 65 mm wide x 15 mm tall, with 1 mm radiused edges)
- The lower enclosure walls
- Alignment pins (two cylindrical bosses, 4 mm diameter, 5 mm tall) that register into matching holes in the top shell to set the seam position precisely

The bottom shell has no structural role beyond closing the enclosure and carrying the lower rail groove halves. Its walls are 1.5 mm (cosmetic, not load-bearing).

**Release plate.** A flat rectangular plate, 3 mm thick, with four 7.2 mm through-holes at the fitting pattern. Two guide slots (channels cut into the plate edges) ride on matching ribs molded into the top shell side walls. The plate translates 3-4 mm axially. The guide ribs are on the top shell (not the bottom) so the plate is installed before the bottom shell closes.

**Lever pair.** Two identical lever arms, mirror-image of each other, one on each side of the cartridge interior. Each lever is a rigid bar approximately 8 mm wide x 4 mm thick, with:
- A pivot hole (3.2 mm, for the 3 mm steel pin) near the midpoint of the cartridge depth
- A short arm (4-5 mm from pivot to tip) that contacts the release plate's front face
- A long arm (20-25 mm from pivot to tip) that connects to the finger bar

The levers pivot on the steel dowel pins seated in the top shell's pivot bosses. The lever ratio is 4:1 to 6.25:1 depending on the final pivot-to-tip dimensions, which are set by the pivot pin position (adjustable via 2-3 alternate pivot holes spaced 3 mm apart in the bosses).

**Finger bar.** A separate rigid bar that spans between the two lever long-arm tips. It is the user-facing surface the fingers contact. It is a flat rectangular bar, approximately 65 mm wide x 13 mm deep x 4 mm thick, with a fine horizontal rib texture (0.8 mm pitch) on its outward face. The bar connects to the lever tips via snap-fit sockets (the bar has two rectangular pockets at its ends; the lever tips have matching rectangular tabs that snap in during assembly). Once the bottom shell is closed, the finger bar cannot be removed -- the slot constrains it.

### Why this split

- The top shell is the "chassis." All structural loads (pump weight, collet release force, lever reaction forces) flow through it. Printing it as one piece means no joints in the load path.
- The bottom shell is a cosmetic closure. Separating it from the top shell means the entire mechanism can be assembled on the top shell before the bottom shell snaps on.
- The release plate must translate, so it cannot be integral with either shell.
- The levers must pivot, so they cannot be integral with any shell.
- The finger bar is separate from the levers so it can be a single spanning bar (better feel, even force distribution) rather than two separate finger pads. It also allows the finger bar to be printed face-down for smooth texture.

---

## 2. Join Methods

**Top shell to bottom shell: snap fits (permanent).** Four internal snap-fit hooks on the bottom shell engage four matching ledges on the top shell interior. The hooks are 2 mm deep (exceeding the 1.5 mm minimum for clear tactile engagement per design pattern research). Once snapped, the hooks are inaccessible from outside. The user never opens the cartridge -- when the pumps wear out, the entire cartridge is replaced. This is a permanent, non-serviceable join.

Two 4 mm alignment pins on the bottom shell register into 4.2 mm holes in the top shell (0.1 mm clearance per side for snug press fit). These set the seam gap before the snaps engage.

**Lever arms to pivot pins: steel pin through printed bore.** Each 3 mm steel dowel pin press-fits into the top shell pivot boss (3.0 mm hole in boss -- the pin is permanent once pressed in). The lever arm has a 3.2 mm bore (0.1 mm clearance per side) and rotates freely on the pin. The pin extends through the lever and seats in a blind pocket on the opposite boss wall, captured once the bottom shell closes.

**Lever tips to finger bar: snap-fit tab and socket.** Rectangular tabs on the lever tips (2 mm x 4 mm cross section, 3 mm long) snap into matching rectangular pockets on the finger bar ends. This joint transmits the user's pull force. The snap depth is 1.5 mm. Once the bottom shell is closed, the finger bar is axially constrained by the shell slot, so the snap only needs to hold during assembly -- the shell provides the retention during use.

**Release plate: unjoined, captured.** The plate is not fastened to anything. It slides on guide ribs in the top shell, with the return springs on one side and the collet faces on the other. It is captured axially by the springs (pushing it forward) and the collets/fittings (blocking rearward travel beyond the depression distance). The lever short arms contact the plate face but are not attached -- they simply push.

**Quick connect fittings: bulkhead press-fit into rear bulkhead.** The PP1208W bulkhead unions thread into the 17.0 mm holes in the rear bulkhead using their integral nut. The bulkhead wall is 3 mm thick (sufficient for the clamping shoulder).

**Pumps to mounting plate: M3 x 8 screws with nylon lock nuts.** Eight M3 screws (4 per pump) pass through the mounting plate from the pump-head side, with lock nuts on the motor side. This is the only screw joint in the cartridge. The screws are entirely internal -- inaccessible and invisible once the shell is closed.

---

## 3. Seam Placement

There is one external seam: the **horizontal split line** between the top and bottom shells. This seam runs around the full perimeter of the cartridge at approximately the mid-height of the side walls.

**Seam position on each face:**

- **Front face:** The seam runs horizontally across the front, but it is interrupted by the finger bar slot. The seam falls at the upper edge of the finger bar slot opening. The slot itself is in the bottom shell; the top shell's front wall extends down to meet the slot's upper edge. The visible seam on the front face is therefore only the two short segments to the left and right of the finger bar slot, each approximately 40-45 mm long. These run along a horizontal edge where the top shell wall meets the bottom shell wall.

- **Side faces:** The seam runs the full depth of each side, horizontally, at mid-height. It crosses the T-slot rail groove. The rail groove is split: the upper half of the T-profile is in the top shell, the lower half in the bottom shell. The seam gap target is 0.3 mm maximum, achieved by the alignment pin registration. When the cartridge is inserted in the dock, the side seams are partially hidden by the dock rails covering them.

- **Rear face:** The seam runs horizontally across the rear face, below the four tube holes. The tube holes are in the upper portion (rear bulkhead is part of the top shell). The seam is a simple horizontal line on an otherwise featureless face.

- **Top and bottom faces:** No seams. The top face is the uninterrupted inner surface of the top shell. The bottom face is the uninterrupted inner surface of the bottom shell. Both are build-plate surfaces (smooth).

**Seam treatment:** The seam edges on both shells have a 0.15 mm x 45-degree chamfer on the external corners. This means the seam presents as a fine V-groove rather than a sharp step if the two halves are not perfectly flush. At 0.3 mm gap with chamfered edges, the seam reads as a subtle line, consistent with the design pattern guidance that seam gaps under 0.3 mm read as "product."

---

## 4. User-Facing Surface Composition

What the user sees, working around the cartridge:

**Front face (toward user when inserted):**
- Upper region: smooth flat surface (the palm-contact area). This is the top shell's front wall, inset 1.5 mm from the surrounding shell edge to create a shallow palm-shaped recess approximately 65 mm wide x 45 mm tall. The inset tells the user "push here" without a label.
- Lower region: the finger bar, protruding through a slot in the bottom shell. The finger bar face is textured with fine horizontal ribs (0.8 mm pitch, 0.4 mm tall -- minimum printable feature per requirements.md). The bar is inset 1.5 mm from the surrounding bottom shell edge, matching the palm surface inset depth. The gap between the palm surface and the finger bar (the slot opening) is approximately 3-4 mm wide at rest.
- The two inset surfaces and the narrow gap between them are the only non-flat features on the front face.

**Side faces (left and right):**
- T-slot rail grooves running the full depth of the cartridge. The groove is 5 mm deep, with the T-profile providing the mechanical interlock with the dock rails. The groove interior is smooth (printed against support or oriented to avoid support -- see Section 7). The rest of each side face is flat and featureless.

**Rear face (toward dock interior when inserted):**
- Four holes, approximately 7.5 mm diameter each, arranged in a rectangular 2x2 pattern. These are the tube entry points -- the PP1208W fitting faces are recessed 2-3 mm behind the shell surface, so the user sees four dark circles and nothing else. The electrical connector is on the bottom face (see below), not visible from the rear.

**Top face:**
- Flat, featureless, smooth.

**Bottom face:**
- Flat, smooth, with one feature: the blind-mate electrical connector recess. This is a rectangular pocket (approximately 15 mm x 10 mm x 5 mm deep) near the rear of the bottom face, containing the cartridge-side electrical contact pads. When inserted, this mates with a spring-loaded pogo-pin connector on the dock floor. The pocket is not visible during normal handling because the bottom face faces down.

**No visible screws, no visible mechanism components, no visible seams wider than 0.3 mm.** The finger bar texture is the only non-smooth external surface.

---

## 5. Design Language

**Material:** ASA. Chosen for:
- UV stability (the device may sit on a countertop near a window)
- Higher stiffness than PETG (crisper snap-fit engagement, sharper detent click -- per design pattern research, ABS/ASA produce crisper tactile feedback than PETG)
- Good layer adhesion (better than ABS for functional parts)
- Supported by the Bambu H2C (listed in requirements.md)
- Food contact: the cartridge exterior does not contact food or water. Internal tubing and fittings are the food-contact surfaces, and those are silicone and polypropylene respectively.

**Color:** Matte black, matching the matte black faucet described in the vision. Single color throughout -- no dual-extrusion color contrast (simpler printing, more monolithic appearance).

**Surface finish:**
- All user-facing flat surfaces are build-plate surfaces (printed face-down). This is the smoothest achievable FDM finish.
- The finger bar has printed-in horizontal ribs for tactile distinction. These ribs are printed into the face-down surface (the texture is the build-plate face of the finger bar part).
- No post-processing (no sanding, no vapor smoothing, no painting). The build-plate finish of ASA on a textured PEI sheet is consistent, matte, and appropriate for a kitchen appliance.

**Corner treatment:**
- All external edges have 1 mm fillets (C1 radius). This eliminates sharp edges that feel cheap or catch on hands, and is well above the 0.4 mm minimum printable feature size.
- The palm and finger surface insets have 1 mm radius transitions from the surrounding shell surface.
- Internal edges (not user-facing) are left sharp or have 0.5 mm chamfers for printability.

**Proportions:** The cartridge is a low, wide rectangle -- approximately 155 mm wide x 170 mm deep x 75 mm tall. The horizontal proportion (wider than tall) reads as stable and grounded. The flat surfaces, minimal features, and consistent matte black finish give it a monolithic, appliance-grade appearance.

---

## 6. Service Access Strategy

There is exactly one service interaction: **cartridge removal and replacement.**

**Removal:**
1. User reaches to the front-bottom of the enclosure, wraps one hand palm-up around the cartridge front face.
2. User squeezes (palm pushes upper surface, fingers pull lower finger bar). The lever mechanism amplifies the finger pull 4-6x, driving the release plate into the four collets. At 60-80% of the 12-15 mm finger travel, the over-center detent clicks.
3. User pulls the cartridge forward along the dock rails. The four tube stubs slide out of the released quick connects. The cartridge slides free.

**Insertion:**
1. User aligns the cartridge rail grooves with the dock rails. Chamfered rail entries (2 mm x 30 degrees on the dock) and chamfered tube stub ends self-center the cartridge.
2. User pushes the cartridge rearward along the rails. Tube stubs enter the quick connects automatically (collet position is irrelevant for insertion). In the last 3-5 mm of travel, the retention latch deflects and snaps into a notch on the cartridge body with a click. The click is synchronized with full tube seating by geometry.
3. The cartridge front face sits flush with the dock opening.

**No other service access exists.** The user cannot open the cartridge. The user cannot replace individual pumps, fittings, springs, or levers. The cartridge is a sealed replaceable unit. When pumps wear out (estimated 800+ hours of motor life, far exceeding any reasonable home use interval), the user discards the cartridge and inserts a new one.

---

## 7. Manufacturing Constraints

### Print orientation

**Top shell:** Printed upside-down (the palm-contact surface on the build plate, facing down). This puts the smoothest finish on the palm surface. The pump mounting plate prints as a horizontal shelf. The rear bulkhead prints as a vertical wall. The internal ribs, snap-fit ledges, lever pivot bosses, spring pockets, and over-center detent arm all grow upward from the palm surface.

- Overhang concern: The pump mounting plate is a horizontal shelf connecting the side walls. It is not unsupported -- it connects to both side walls and the rear bulkhead. The motor bore holes (36.4 mm) in this shelf are circular openings that the printer bridges across. At 36.4 mm diameter, the topmost span of the circle exceeds the 15 mm unsupported bridge limit. Resolution: the bore holes are printed with designed break-away supports (0.2 mm interface gap per requirements.md) on the top side of the shelf. These supports are inside the motor bore, which is not a cosmetic surface, and are removed after printing. The snap-fit ledges on the interior walls have undercuts; these are small (2 mm deep) and receive designed supports with break-away tabs.

**Bottom shell:** Printed upside-down (the bottom outer face on the build plate). The finger bar slot opening has a horizontal ceiling (the top edge of the slot). This ceiling is an approximately 4 mm overhang into the slot. This is a short bridge (the slot is 65 mm wide but the ceiling is only 4 mm deep in the overhang direction), well within the 15 mm bridge limit. No supports needed.

**Release plate:** Printed flat on the build plate. No overhangs, no supports. Simple rectangular plate with four holes.

**Lever arms:** Printed flat on the build plate, with the pivot hole axis vertical (Z). The lever is 4 mm thick, so it is 10 layers at 0.4 mm layer height or 20 layers at 0.2 mm. The flex direction during use (pivoting) is parallel to the build plate, which means layers stack along the flex axis -- this is the strong orientation per requirements.md.

**Finger bar:** Printed with the textured face on the build plate (face-down). The ribs are printed into the first layer against the build plate surface. The bar is 4 mm thick, no overhangs, no supports.

### Bed fit

All parts fit within the single-nozzle print volume: 325 x 320 x 320 mm.

| Part | Approximate dimensions | Fits? |
|------|----------------------|-------|
| Top shell | 155 x 170 x ~50 mm | Yes (all dimensions well within 325 x 320 x 320) |
| Bottom shell | 155 x 170 x ~30 mm | Yes |
| Release plate | ~80 x 50 x 3 mm | Yes |
| Lever arm (x2) | ~30 x 8 x 4 mm | Yes |
| Finger bar | 65 x 13 x 4 mm | Yes |

All five cartridge parts can be printed on the bed simultaneously in a single print job if desired.

### Support strategy

- **Top shell motor bores:** Designed break-away supports with 0.2 mm interface gap, internal to the bore. Removed after printing with pliers. Not a cosmetic surface.
- **Top shell snap-fit ledge undercuts:** Designed supports with 0.3 mm break-away tabs spaced every 8 mm. Interior surfaces, not cosmetic.
- **Top shell T-slot rail groove (upper half):** The T-profile undercut is printed with the T facing up (since the shell is inverted). The horizontal ceiling of the T-slot is an overhang. This ceiling is 2-3 mm deep (the width of the T-bar engagement) and approximately 3 mm wide. This is a very short span. A 45-degree chamfer on the inside leading edge of the T-ceiling eliminates the need for support entirely.
- **All other parts:** No supports needed.

### Material

ASA, as specified in Section 5. Print settings: 0.2 mm layer height for the shells (balance of surface quality and print time), 0.2 mm for all other parts. 0.4 mm nozzle (standard). 3 perimeters for external walls (1.2 mm), 4 perimeters for structural walls (pump mounting plate, rear bulkhead: 1.6 mm minimum).

### Dimensional accuracy notes from requirements.md applied

- All holes oversized per FDM compensation: M3 through-holes at 3.4 mm, pivot pin bores at 3.2 mm (lever) and 3.0 mm (boss, press fit), motor bores at 36.4 mm, bulkhead fitting holes at 17.2 mm (17.0 mm + 0.2 mm).
- Elephant's foot chamfer (0.3 mm x 45 degrees) on the bottom edges of both shells (the build-plate faces are mating surfaces for the seam).
- Sliding fits (rail grooves, release plate guides): 0.2 mm clearance per face.
- Press fits (alignment pins, pivot pin in boss): 0.1 mm clearance per side.

---

## Dock Cradle (Enclosure-Side)

The dock cradle is a single printed part that mounts inside the enclosure at the front-bottom position. It provides:

- Two T-profile rails (left and right) that the cartridge slides onto. The rails are horizontal, running front-to-back (insertion axis). Chamfered entries (2 mm x 30 degrees) at the front of each rail.
- A rear wall with four tube stubs protruding forward (these are the 1/4" OD tubes permanently inserted into the device-side quick connect fittings behind the wall).
- A spring-loaded retention latch (printed cantilever on the dock floor or one rail) that engages a notch on the cartridge body at full insertion. The latch notch position on the cartridge is set so that the latch clicks at the exact insertion depth where tubes reach the tube stops in the cartridge fittings (15-16 mm past the collet face).
- A pogo-pin connector mount on the dock floor, positioned to align with the cartridge bottom-face connector recess.
- Asymmetric rail positioning (left rail 2 mm higher than right rail) to prevent wrong-orientation insertion.

The dock cradle prints with the rail faces on the build plate for smooth sliding surfaces. It is a single part, no assembly beyond press-fitting the pogo-pin connector.

---

## Internal Layout (Cross-Section, Front to Rear)

For spatial clarity, here is the arrangement along the insertion axis (Y), from front (user side) to rear (dock wall):

| Zone | Depth (Y) | Contents |
|------|-----------|----------|
| 0-15 mm | Finger bar slot, palm surface inset, lever long arms | User-facing squeeze surfaces and lever geometry |
| 15-25 mm | Lever pivots, return springs, over-center detent | Mechanism zone -- springs push release plate forward, levers pivot here |
| 25-35 mm | Release plate travel zone | The 3-4 mm of axial space the plate moves through |
| 35-50 mm | Release plate (at rest position), tube routing space | Plate sits here at rest; silicone tubes route from pump connectors to fittings |
| 50-80 mm | Pump heads (front face to mounting plate) | Pump rollerheads and tube barb connectors |
| 80-83 mm | Pump mounting plate (integral shelf in top shell) | 3 mm thick structural shelf with motor bores and screw holes |
| 83-150 mm | Motor bodies | The 63 mm motor cylinders extend rearward |
| 150-155 mm | Motor shaft nubs + clearance | 5 mm nub plus air gap to rear shell wall |
| 155-165 mm | Rear bulkhead | 3 mm wall with four PP1208W bulkhead fittings |
| 165-170 mm | Rear shell wall (external) | 2 mm external wall, four 7.5 mm tube entry holes |

Total depth: approximately 170 mm. This fits the synthesis estimate of 160-175 mm.

---

## Printability Flag

No printability conflicts with the settled interaction design were found. The 12-15 mm finger travel, flat squeeze surfaces, hidden mechanism, 4 quick connects, and rail-guided slide are all achievable with the print orientations and support strategies described above. The only designed supports are in the top shell motor bores and snap-fit undercuts -- both internal, both removable.
