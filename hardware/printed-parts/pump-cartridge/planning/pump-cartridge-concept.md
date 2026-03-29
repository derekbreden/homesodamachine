# Pump Cartridge — Conceptual Architecture

## Design Intent

A slide-in cartridge that holds two peristaltic pumps, connects to four fluid lines and four electrical contacts via blind-mate, and releases with a one-handed squeeze gesture. The user experiences a rectangular box that slides onto rails, seats with firm resistance, and sits flush with the dock opening. To remove, they squeeze the front face and slide it out. Everything mechanical is hidden inside.

---

## Exploration and Dead Ends

### Link routing problem

The decision document describes the inset release panel at the front connecting to the release plate at the rear via "rigid links." These links must span the full cartridge depth (~160mm), passing through or around the pump and tubing zone. Three routing options were considered:

1. **Center gap (between the two pumps).** The gap between pumps is only ~15mm wide and is occupied by BPT tubing routing from the pump barbs to the rear JG fittings. Running rigid links here interferes with the tubes and creates a service access problem — the links block tube replacement.

2. **Outer sides (between pump and shell wall).** The shell wall is ~12mm from the pump head on each side. A 3mm rod fits, but the rod must pass through or around the internal mounting plate. Adding clearance holes to the plate weakens it at the screw pattern. And two rods at the outer edges create a wide moment arm — any slight friction difference between the two guide paths causes the release plate to rack (tilt), which is the exact failure mode the decision document warns about for uneven collet release.

3. **Through the mounting plate on the pump centerline axis.** Two rods pass through the mounting plate at the center of each pump's motor bore. The motor bore is ~37mm and the motor is ~35mm — there is ~1mm clearance. This does not work.

**Dead end:** Long rigid links from front to back are fragile, create routing conflicts, and risk racking the release plate. The longer the link path, the worse the tolerance stack-up.

### Relocated release mechanism

The decision document places the release plate near the rear (close to the JG fittings) and the user interface at the front. What if the release plate were at the front instead?

The JG fittings are mounted in the rear wall. The dock's tube stubs enter the fittings from the rear (dock side). The collets that grip those tube stubs are on the rear-facing ports of the fittings. The release plate must push those specific collets — the ones at the rear face of the cartridge. Moving the release plate to the front does not help; it would push the wrong collets (the internal ones that grip the pump-side tubes).

**Dead end confirmed:** The release plate must be at the rear, near the collets it actuates.

### Bowden-style cable actuation

Instead of rigid links, use flexible steel cables (like bicycle brake cables) in printed tube guides. The inset panel pulls the cables, which pull the release plate forward. Cables can route around obstacles and tolerate curves.

**Problem:** The release plate must be pushed rearward (toward the fittings), not pulled forward. The user pulls the inset panel toward themselves, which should push the release plate away from them (rearward). With cables, pulling at one end pulls at the other end — the force direction is the same at both ends. A cable from the inset panel to the release plate would pull the plate forward (toward the user), which is the wrong direction.

To reverse the force direction, an intermediate pivot (bell crank) would be needed. This adds complexity and a failure point.

**Dead end:** Cable actuation reverses naturally but in the wrong direction for this geometry. Would need a bell crank, adding parts and failure modes.

### Rethinking the force direction

The decision document says: "The user's fingers pull an inset panel that is connected to the release plate via internal links. The release plate translates rearward."

User pulls inset panel forward (toward themselves). Links transmit this as rearward motion of the release plate. This requires the links to reverse direction — which rigid links cannot do. Rigid links transmit force in the same direction: pull forward at one end, pull forward at the other end.

Wait. Re-reading more carefully: the inset panel is on the front face, set back 5mm into a recess. The user's fingers curl into the recess and pull the panel toward their palm. Their palm is on the outer shell face. So the panel moves rearward (toward the cartridge interior, away from the user) — not forward. The squeeze closes the gap between palm and fingers. The palm is the fixed reference (on the outer shell), and the fingers pull the panel inward.

**Correction:** The panel moves rearward (into the cartridge), not forward. The links connect the inset panel to the release plate, both moving rearward together. This is a straight push-pull — rigid links work. The user squeezes, pushing the panel inward; the links push the release plate inward (rearward toward the collets). No direction reversal needed.

This resolves the link routing concern. The links are in compression (pushed rearward) during the squeeze. Steel rods in printed guide bushings handle this cleanly.

### Settling on link routing

With the force direction clarified: two 3mm steel rods, running from the inset panel through the cartridge interior to the release plate. Both the panel and plate move rearward together when squeezed.

The rods run along the bottom of the cartridge interior, below the pump mounting plate, in printed channels molded into the bottom shell half. This zone is clear — the pumps sit on top of the mounting plate, and the tube routing runs above and to the sides of the pumps. The bottom of the cartridge is dead space suitable for the link rods.

Two rods spaced ~60mm apart (symmetric about the cartridge centerline) provide even force distribution on the release plate without racking. Printed slide bushings at 3 points along the rod length (front wall, mounting plate pass-through, rear zone) keep the rods parallel.

**Selected approach:** Bottom-routed steel link rods in printed guide channels.

---

## The Concept

### Overview

The cartridge is a 4-piece printed assembly (shell top, shell bottom, rear wall plate, inset release panel) plus one internal printed part (release plate). It holds two Kamoer pumps on a mounting shelf formed integrally into the bottom shell half, connects to the dock via 4 JG union fittings pressed into the rear wall plate, and makes electrical contact via pogo pin pads on the rear wall plate. The user squeezes the front face to actuate the release plate via two steel link rods routed along the bottom of the cartridge.

### Exterior dimensions (estimated)

| Dimension | Value | Driven by |
|-----------|-------|-----------|
| Width | 165mm | Two 62.6mm pump heads + 15mm center gap + 2x ~12mm shell walls with rail features |
| Height | 78mm | 62.6mm pump head + 2x ~3mm pump clearance + 2x ~3mm shell walls + 3mm release rod channel below |
| Depth | 200mm | Tube stubs (40mm) + pump head (48mm) + bracket/motor (68mm) + rear wall with JG fittings (25mm) + front wall with recess (19mm) |

All three dimensions fit within the 325 x 320 x 320mm print bed.

---

## 1. Piece Count and Split Strategy

**5 printed pieces total for the cartridge, plus 1 dock-side piece.**

### Piece 1: Shell Bottom

The primary structural piece. Includes:
- Bottom wall and lower half of both side walls
- Lower T-rail profiles on each side (the lower half of the T crossbar and stem)
- Integral pump mounting shelf — a flat horizontal ledge spanning the cartridge width at approximately mid-height, with two motor bore holes and two sets of 4x M3 screw holes at 48mm square spacing
- Two link rod channels (U-shaped grooves running front-to-back along the bottom interior surface, below the mounting shelf)
- Three pairs of printed slide bushings (cylindrical bores, 3.2mm ID) at front, middle, and rear to guide the link rods
- Lower half of the front wall, including the lower portion of the inset panel recess
- Snap-fit features along the top rim for joining with Shell Top

**Print orientation:** Upside down (bottom wall on the build plate). The T-rail features print vertically, which gives them layer strength along the slide axis. The mounting shelf prints as a horizontal bridge between the side walls — this is the widest internal bridge (~140mm). At 0.1mm layers this will sag. Instead, the mounting shelf should be slightly below the side wall top edge so it can be supported by the side wall geometry during printing. Alternatively, the shelf connects to both side walls and can be printed with the built-in taper strategy: the underside of the shelf has 45-degree gussets connecting it to the side walls, eliminating any unsupported overhang.

**Why the mounting shelf is integral to the bottom shell:** Separating the pump mounting plate as its own piece (as the decision doc suggested) adds a part and requires fasteners or snaps to hold it in the shell. An integral shelf eliminates that piece. The shelf is a horizontal plane spanning between the two side walls, structurally similar to a shelf in a bookcase. The gussets underneath make it rigid and printable. The pumps bolt down through the shelf from above; the motor cylinders pass through bores in the shelf and extend downward into the space between the shelf and the bottom wall. The link rod channels run along the very bottom, below the motor clearance zone.

Wait — if the motors extend downward through the shelf, and the link rods are at the very bottom, the motors (~35mm diameter, ~68mm long) occupy the space between the shelf and the bottom wall. The bottom wall to shelf distance must be at least 37mm (35mm motor + 1mm clearance per side). Adding the link rod channel (4mm tall for a 3mm rod + clearance) below the motors means the total height below the shelf is ~41mm. The pump head above the shelf is ~48mm tall. Total interior height: ~89mm. With 3mm walls top and bottom: ~95mm.

That is taller than the 78mm estimate. The problem: the motors extend below the mounting shelf and consume the space where the link rods would go.

**Revised layout: Motors extend rearward, not downward.**

The pumps mount with the bracket face against a vertical plate (perpendicular to the depth axis), not a horizontal shelf. The pump heads are forward, the motors extend rearward. The mounting plate is vertical — it spans the width of the cartridge, oriented in the XZ plane.

In this orientation:
- Pump heads occupy the front half of the cartridge (forward of the mounting plate)
- Motors occupy the rear half, extending toward the rear wall
- JG fittings are on the rear wall, which is behind the motor ends
- The motor ends and JG fittings must not collide

The two motors are at X = -37mm and X = +37mm (approximately). The JG fittings are a 2x2 grid at center. The motor end caps are ~35mm diameter; the JG body ends are 15.10mm OD. As analyzed above, the center gap between motors (~39mm wide) can hold 2 JG fittings side by side (~40mm needed for 25mm center spacing). The other 2 fittings go below (or above) the motors. There is room.

**With vertical mounting plate and motors rearward:** The link rods can run along the bottom of the cartridge (below the pump heads in front, below the motors in back). The pump heads are 62.6mm x 62.6mm — their bottom surface is at roughly Z = -31mm from center. The bottom shell wall is at Z = -39mm (31mm + 3mm clearance + 5mm wall). The link rods fit in the 8mm zone between the pump head bottoms and the bottom shell wall.

But the motors at the rear are only ~35mm diameter, centered on the pump axis. Their bottom surface is at Z = -17.5mm from center, leaving much more room below them. So the rods have clearance throughout.

**This is the correct layout.** Vertical mounting plate, motors rearward, link rods along the bottom. Revising the concept accordingly.

Now the "mounting shelf" becomes a **vertical mounting plate** — a wall spanning the cartridge width and height, located at roughly the 1/3 depth point. The pump heads protrude forward through cutouts (or the plate is simply a frame that surrounds the motor bores and screw holes). The motors and adapter plates protrude rearward.

**Making the vertical mounting plate integral to the shell** is harder than a horizontal shelf. A vertical internal wall is a natural feature of a top/bottom split shell — it can be molded into the bottom half as a vertical rib. But it needs to span the full cartridge height, which means the top half must have a matching slot or the plate must be a separate piece that gets captured when the shell halves close.

**Decision: The vertical mounting plate is a separate piece** (Piece 3 below, renamed from "internal mounting plate" to reflect its vertical orientation). It sits inside the shell and is captured by the shell halves when they snap together. The plate has printed locating features (tabs) that register into slots on the shell side walls, preventing any movement. The pump screws clamp it from the front side; the shell structure keeps it positioned.

**Revised piece count: 6 printed pieces for the cartridge.**

| # | Piece | Function |
|---|-------|----------|
| 1 | Shell Bottom | Bottom wall, lower side walls, lower T-rails, lower front wall, link rod channels with guide bushings |
| 2 | Shell Top | Top wall, upper side walls, upper T-rails, upper front wall (with upper portion of inset recess) |
| 3 | Mounting Plate | Vertical internal plate with 2x motor bores, 2x M3 screw patterns, locating tabs |
| 4 | Rear Wall Plate | JG fitting pockets (4x), pogo contact pads, release plate guide pin bores (2x), link rod pass-throughs (2x) |
| 5 | Release Plate | 4x stepped collet-actuating bores, 2x guide pin holes, 2x link rod attachment points |
| 6 | Inset Release Panel | The finger-pull surface, recessed into the front face, attached to the 2 link rods |

**Dock-side piece:**

| # | Piece | Function |
|---|-------|----------|
| 7 | Dock Bay | T-rail channels, tube stub alignment features, pogo pin header mount, rear wall for tube stubs |

### Why this split

- **Shell top/bottom split** is the standard approach for enclosing internal components. The seam runs horizontally at mid-height around all four sides. This is the easiest to print (each half prints open-side-up) and the easiest to assemble (drop components into bottom half, close top half).
- **Separate rear wall plate** is justified by dimensional precision. The JG fitting pockets must be accurate to ~0.2mm for a proper press-fit on the 9.31mm center body. A separate plate can be printed flat on the build plate with the pocket bores oriented vertically (best roundness). If the rear wall were integral to the shell bottom, the pockets would be oriented horizontally (printed as cylinders on their side), giving worse bore accuracy.
- **Separate mounting plate** is justified by the same precision argument. The M3 screw holes and motor bores need accuracy. Printing the plate flat (on the build plate) with holes vertical gives the best results.
- **Separate release plate** is required — it is a moving part.
- **Separate inset panel** is required — it is a moving part.

---

## 2. Join Methods

### Shell Top to Shell Bottom: Snap-Fit Clips

The top and bottom shell halves join along a horizontal seam at mid-height. The bottom half has snap-fit hooks (4 per long side, 2 per short side — 12 total) that engage matching ledges on the top half's inner rim. The hooks are oriented so that the top half pushes straight down onto the bottom half and clicks into place.

This is a permanent join for normal use. The snap-fit hooks have enough retention that the cartridge handles normally without opening. For pump replacement (the reason the cartridge exists), the user replaces the entire cartridge — they never open the shell. Only during initial assembly or factory service would the shell be opened, and the snap-fits can tolerate a few open/close cycles.

No screws, no glue. The snap-fit join is the simplest method that provides adequate retention for a handled, slid, and squeezed cartridge.

### Mounting Plate: Captured by Shell Halves

The vertical mounting plate has locating tabs (2 per side) that register into vertical slots molded into the shell side walls. When the shell halves are closed, the plate is captured — it cannot translate along any axis. The plate does not need its own fasteners; it is held in position by the shell geometry and clamped between the pump bracket faces (bolted from the front) and the shell structure.

### Rear Wall Plate: Snap-Fit into Shell Rear

The rear wall plate snaps into a rectangular pocket at the back of the shell. The pocket has a 1mm lip on all four edges; the plate has matching chamfered tabs that click past the lip. The plate is flush with the shell rear face when seated. This join must resist the rearward push from tube insertion (when the cartridge is pushed onto the dock stubs). Four snap-fit hooks (one per corner) plus the lip provide this retention.

JG fittings are pressed into the plate bores. The friction of the press-fit plus the shoulder contact (15.10mm shoulders bearing against the plate faces) provides axial retention. No adhesive needed.

### Release Plate: Free-Floating on Guide Pins

The release plate slides on 2x 3mm steel dowel pins that are press-fit into the rear wall plate. Compression springs (3mm ID, ~8mm free length) on each pin push the release plate forward (away from the JG fittings) to its rest position. The plate is not fastened — it is a captive floating element between the guide pins and springs.

### Inset Release Panel: Attached to Link Rods

The inset panel attaches to the two 3mm steel link rods. The rods press-fit into holes in the panel's rear face. The panel is captive in the recess in the front wall (the recess geometry constrains it to rearward translation only — it cannot fall out or tilt). The link rods pass through the cartridge interior and attach to the release plate at the rear.

### Link Rods to Release Plate: Threaded or Press-Fit

Each link rod passes through a clearance hole in the release plate and is retained by a small printed washer or E-clip on the far side. Alternatively, the rod press-fits into a blind hole in the release plate. Press-fit is simpler and has no loose parts.

---

## 3. Seam Placement

### Primary seam: Shell top/bottom split line

Runs horizontally around the entire cartridge perimeter at approximately mid-height. This seam is visible on the front face, both side faces, and the rear face.

**Front face:** The seam runs horizontally across the front wall, bisecting the inset release panel recess. The recess has a 1mm radius at all edges, and the seam falls along the top or bottom edge of the recess — not through the middle. Aligning the seam with a feature edge (the recess boundary) makes it read as an intentional design line rather than a manufacturing artifact.

**Side faces:** The seam runs horizontally along the sides, intersecting the T-rail grooves. The T-rail groove creates a natural visual interruption on the side face, so the horizontal seam is less noticeable. The seam and the rail groove are perpendicular, forming a clean intersection.

**Rear face:** Not user-visible during normal use. The seam here can be rougher without UX impact.

### Secondary seam: Rear wall plate to shell

This seam is a rectangular outline on the rear face where the plate meets the shell pocket. Since the rear face is never user-visible (it faces into the dock), this seam has no UX impact.

### Seam treatment

All user-visible seams are tight-fit (0.1mm gap target). The shell halves have a step joint (one half has a 0.5mm lip that overlaps the other) to prevent a visible through-gap and to self-align during assembly. The step joint runs continuously around the perimeter. On the user-facing surfaces (front and sides), this gives a hairline seam similar to consumer electronics enclosures.

---

## 4. User-Facing Surface Composition

The user interacts with three surfaces:

### Front face (primary interaction surface)

This is what the user sees when the cartridge is in the dock. It sits flush with the dock opening. The front face is a flat rectangle (~165mm wide x ~78mm tall) with one feature: the inset release recess.

**The recess** is a shallow (~5mm deep) rectangular pocket centered on the front face, approximately 90mm wide x 30mm tall. Its bottom edge is radiused (2mm radius) for finger comfort. Its side edges and top edge are crisp (0.5mm radius). The recess is the only indication that this surface does anything — it invites the user's fingers with its depth and curvature.

The rest of the front face is flat and featureless. The user's palm rests here during the squeeze gesture.

**Visual hierarchy:** One feature, one action. The recess says "put your fingers here." Everything else says "push against me."

### Side faces (secondary, visible but not interactive)

Two flat side walls with T-rail grooves running front-to-back. The grooves are subtle — 4mm wide, 4mm deep — and read as a geometric detail rather than a mechanical feature. The user does not need to understand the rails; they guide the cartridge automatically.

### Top face (tertiary, visible when cartridge is out of dock)

Flat, featureless. May include a small embossed or debossed label area for a product logo or cartridge identification marking. No functional features.

### Bottom face (not visible in dock)

Flat. Contains no user-facing features. May have a small arrow or "THIS SIDE DOWN" text embossed for assembly orientation, but this is a factory/service detail, not user-facing.

### Rear face (never visible to user)

Contains the 4 JG fitting ports (the tube entry holes) and the pogo contact pads. The user never sees this face — it is inside the dock. The fitting ports appear as 4 small circular openings (~6.5mm diameter, the collet bore). The pogo pads are flat copper squares below the fittings.

---

## 5. Design Language

### Surface finish

All exterior surfaces are smooth (0.1mm layer lines, oriented so that layer lines run horizontally on the side walls and front face). The front face is printed with the cartridge on its side (left or right wall on the build plate), so the front face layer lines are horizontal and fine. Alternatively, printing bottom-down means the front face has visible layer lines running vertically — either orientation is acceptable for PETG with 0.1mm layers.

No textures, no decorative features. The cartridge reads as a clean rectangular solid with one recessed element on the front face.

### Corner treatment

All exterior edges have a 1mm chamfer or 1mm radius fillet. This softens the box form and prevents the sharp edges that FDM tends to produce. The chamfers also prevent elephant's foot artifacts on the bottom edges from creating fit problems.

The inset recess has a 2mm radius on its bottom edge (where fingers contact) and 0.5mm radius on the remaining edges. This differentiation is functional: the bottom edge is the primary finger contact and must feel smooth; the other edges are visual boundaries.

### Material

PETG for all cartridge pieces. PETG provides:
- Good layer adhesion (important for snap-fit retention and structural integrity)
- Chemical resistance to food-grade flavorings and cleaning solutions
- Low warping (important for dimensional accuracy of JG pockets and screw patterns)
- Reasonable wear resistance for the T-rail sliding surfaces

The dock bay piece can be PLA or PETG — it does not experience the same handling forces.

### Color

Matte black. Matches the project's established dark navy/black design language (from the iOS app theme, S3 display, and vision document). Black PETG is widely available and hides layer lines better than light colors.

### What makes this a product

The cartridge is a featureless black box with exactly one inviting detail — the finger recess. There are no visible screws, no exposed mechanisms, no labels explaining what to do. The T-rail grooves on the sides are geometric accents, not instructions. The cartridge communicates through its form alone: it is a rectangle that slides into a rectangle-shaped opening, and it has a place for your fingers. That is the entire interface.

---

## 6. Service Access Strategy

### Tier 1: User-replaceable (the cartridge itself)

The entire cartridge is the replaceable unit. The user slides it out, discards it (or returns it), and slides in a new one. No tools, no disassembly, no awareness of internals. This is the only tier that matters for normal operation.

### Tier 2: Factory assembly (inside the cartridge)

During manufacturing/assembly, the cartridge is built in this order:
1. Press 4 JG fittings into the rear wall plate
2. Press 2 guide pins into the rear wall plate, add springs, slide release plate onto pins
3. Install 2 link rods through release plate and guide bushings, attach inset panel to rods
4. Place the rear wall plate into the shell bottom (snaps into rear pocket)
5. Route BPT tubes from JG fittings forward through the cartridge interior
6. Install brass barb reducers on BPT tubes
7. Place the vertical mounting plate into shell bottom (registers into side wall slots)
8. Bolt 2 pumps onto the mounting plate (4x M3 each, with rubber grommets)
9. Connect BPT tubes to pump barbs via the barb reducers
10. Solder motor wires to pogo contact pads on the rear wall plate
11. Route wires along the shell bottom
12. Close shell top onto shell bottom (snap-fit)

This sequence is one-directional — components go in from the top, and the shell top closes last. No component needs to be installed after the shell is closed.

### Tier 3: Repair (disassembling a cartridge)

Not a design goal. If a cartridge fails, it is replaced. The snap-fit shell can be pried open with a spudger for diagnostic purposes, but this is not a supported user operation. The snap-fit hooks are designed for ~5 open/close cycles before they lose retention — sufficient for factory rework but discouraging repeated disassembly.

---

## 7. Manufacturing Constraints

All values below are from `hardware/requirements.md`. No assumed or "typical" values are used.

### Print bed fit

Bambu H2C single-nozzle build volume: **325 x 320 x 320mm**.

The largest piece is the shell bottom at approximately 165mm x 200mm x 39mm. This fits the bed with margin in all axes regardless of orientation. All 6 cartridge pieces can be printed sequentially on the same printer. Multiple small pieces (release plate, inset panel, rear wall plate) could be batched on a single print.

### Print orientation per piece

| Piece | Orientation | Rationale |
|-------|-------------|-----------|
| Shell Bottom | Open side up (interior facing up) | T-rail features print vertically (strongest direction for rail shear loads). Interior features (link rod channels, guide bushings) are accessible for support removal. Bottom wall on the build plate gives best flatness. |
| Shell Top | Open side up (interior facing up) | Mirror of shell bottom logic. |
| Mounting Plate | Flat on bed (XZ face down) | Motor bores and screw holes print as vertical cylinders — best roundness accuracy. |
| Rear Wall Plate | Flat on bed (the face with JG pockets facing up) | JG pocket bores print as vertical cylinders. Pogo pad surface on the bottom (bed side) gives smooth finish. |
| Release Plate | Flat on bed | Stepped bores print as vertical cylinders. Guide pin holes are vertical — best roundness. |
| Inset Panel | Flat on bed (finger-contact surface on bed) | Bed-contact surface is smoothest — this becomes the finger touch surface. |

### Overhang and support analysis

- **Shell halves:** The T-rail features (T-shaped cross-section running along the side walls) require the rail head (the horizontal crossbar of the T) to be supported. The crossbar overhangs by ~2mm on each side of the 4mm stem. At 4mm overhang width from the stem, the overhang angle from horizontal is steep enough to require support. **Mitigation:** Add a 45-degree chamfer on the underside of the T crossbar edges. This converts the overhang into a printable slope. The chamfer runs the full rail length and does not affect rail function (the rail head's top surface and inner face are the mating surfaces; the underside chamfer is non-functional).
- **Mounting plate motor bores:** 37mm diameter holes printed vertically. The top of each hole is a bridge across the bore diameter. At 37mm span this will sag. **Mitigation:** The bore is a through-hole — there is no top to bridge. The plate is a flat piece with holes in it. No overhang issue.
- **Shell interior features (guide bushings, snap-fit hooks):** Snap-fit hooks have a small undercut (~1mm) for the hook lip. This overhang is local and small. **Mitigation:** Design the hook lip with a 45-degree lead-in face and a 0.2mm interface gap sacrificial support nub below the lip. The nub breaks away cleanly after printing.
- **Inset recess on front wall:** The recess ceiling (the 5mm deep pocket in the front wall) is a horizontal flat overhang. At 90mm width, this will sag without support. **Mitigation:** The recess ceiling is printed as the bottom face of the shell half (if printed open-side-up, the recess ceiling is actually above and interior). In practice, the recess forms naturally if the shell is oriented with the front wall vertical. However, the chosen print orientation (open-side-up) means the front wall is vertical and the recess is a horizontal pocket in a vertical wall — this prints cleanly as the layers build up the vertical wall and the recess is simply a region where the wall is thinner (recessed). No overhang issue.

### Minimum wall and feature sizes (0.4mm nozzle)

- Shell walls: 3mm (7+ perimeters, very robust). Minimum per requirements: 1.2mm for structural walls.
- T-rail stem: 4mm wide, well above 0.8mm minimum.
- Snap-fit hooks: 1.2mm wide at narrowest point (the hook lip). At minimum for structural features.
- Guide bushings: 3.2mm bore in a 6mm OD boss. Wall thickness: 1.4mm. Above 0.8mm minimum.
- Release plate: 5mm thick. The stepped bores have a minimum wall of ~1.5mm between the inner lip (9.8mm) and the outer bore (15.5mm): (15.5 - 9.8) / 2 = 2.85mm. Well above minimum.

### Dimensional accuracy

- JG fitting pocket bores (9.5mm for press-fit on 9.31mm center body): +0.1mm for press fit per requirements. Verify with test print.
- Motor bores in mounting plate (36mm for 35mm motor): +0.5mm clearance each side. Generous.
- Guide pin holes in rear wall plate (3.0mm for press-fit of 3mm dowel pins): +0.1mm per requirements.
- Link rod guide bushings (3.2mm for 3mm rod sliding fit): +0.2mm clearance per requirements.
- T-rail clearance between cartridge rail and dock channel: 0.2mm per side per requirements.
- Bottom edges of all pieces that sit on the build plate: 0.3mm x 45-degree chamfer to mitigate elephant's foot.

### Material selection

PETG for all cartridge pieces. PETG is listed as a supported material for the Bambu H2C in both standard and carbon-fiber-reinforced variants. Standard PETG is sufficient — no structural loads in this assembly approach the limits of PETG.

The dock bay piece (Piece 7) can be PLA. It is permanently installed in the enclosure, not handled, and does not experience chemical exposure from flavorings.

---

## Concept Summary

A **6-piece printed cartridge** (shell top, shell bottom, vertical mounting plate, rear wall plate, release plate, inset release panel) that slides into a dock on T-rails. Two Kamoer peristaltic pumps mount side-by-side on the vertical mounting plate with pump heads forward and motors extending rearward. Four JG union fittings press into the rear wall plate, connecting to dock tube stubs via blind-mate during insertion. Four pogo pin pads on the rear wall plate provide electrical contact. The user squeezes the front face to push an inset panel rearward, which drives two steel link rods along the bottom of the cartridge into a spring-loaded release plate that pushes all four JG collets simultaneously. The entire mechanism is hidden inside a featureless black PETG box with a single finger recess on the front face.
