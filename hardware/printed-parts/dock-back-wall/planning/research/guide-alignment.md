# Guide & Alignment Mechanisms — Research

Research into mechanism families for guiding a replaceable pump cartridge into a dock. The cartridge must align 4 tube stubs with 4 John Guest 1/4" push-to-connect fittings within ~1mm tolerance. Environment: under a kitchen sink, limited visibility, awkward reach, possibly wet hands. Front insertion, one-handed operation ideal. Prototype via FDM 3D printing.

---

## 1. Tapered Pins / Cone-and-Socket

### How they work

A tapered pin on one part mates with a matching socket (cone, countersunk hole, or bushing) on the other. The taper provides a progressively tighter fit as the pin advances. The geometry is rotationally symmetric, so misalignment in any radial direction is corrected as the cone slides deeper into the socket.

### Taper geometry

- **Standard metric taper pins** (ISO 2339, DIN 1): 1:50 taper, meaning 1mm diameter change per 50mm of length. Per-side angle: arctan(1/50) = 1.15 degrees. This is a self-locking taper — friction prevents withdrawal without force.
- **Morse tapers** (machine tools): approximately 1:20 (2.86 degrees per side). Also self-locking. Used in drill chucks, lathe tailstocks.
- **Self-locking threshold**: a taper is self-locking when the per-side angle is less than arctan(coefficient of friction). For steel-on-steel (mu ~0.15-0.3), that is roughly 8-17 degrees. For plastics (mu ~0.2-0.4), roughly 11-22 degrees.
- **Non-locking tapers** (for easy insertion/removal): per-side angle of 15-30 degrees. These guide and center but do not wedge.

### Tolerances achieved

- **Machined steel**: sub-micron centering repeatability. Morse tapers in machine tools achieve <5 micron TIR (total indicated runout).
- **3D printed (FDM)**: centering repeatability of 0.1-0.3mm is realistic with pins of 8-15mm diameter and moderate taper angles. The taper compensates for the coarse surface finish by sliding past high spots.

### Pros

- Simple geometry, easy to model and print.
- Self-centering in all radial directions simultaneously.
- Forgiving of initial misalignment proportional to the socket entrance diameter.
- No moving parts.
- Can be combined with other mechanisms (tapered pins at the mating face, rails for coarse guidance).

### Cons

- Each pin constrains only 2 degrees of freedom (X and Y translation at that point). A single pin does not constrain rotation or Z-axis position.
- Two pins constrain X, Y, and rotation but not Z or tilt (5 DOF constrained if pins are spaced apart).
- Self-locking tapers (shallow angles) require force to extract — undesirable for quick-change cartridge.
- FDM surface roughness increases insertion friction on shallow tapers.
- Tight-tolerance sockets are hard to print accurately in FDM; conical holes print with stairstepping artifacts.

### When to use

Best as a **fine alignment** feature at the mating face, combined with coarse guidance (rails, funnel). Two tapered pins spaced 50-100mm apart, with 15-20 degree per-side taper and 10-15mm socket entrance diameter, would correct ~5-7mm of misalignment over the last 15-20mm of travel — well suited for the ~1mm final alignment needed here.

---

## 2. V-Grooves and Kinematic Couplings

### The 3-2-1 constraint principle

A rigid body has 6 degrees of freedom (3 translation, 3 rotation). To position it exactly, you need exactly 6 contact points — no more (overconstrained = binding), no fewer (underconstrained = wobble). This is the kinematic constraint principle.

- **3 points** constrain one plane (e.g., Z translation + 2 tilts).
- **2 points** constrain a line (e.g., Y translation + 1 rotation).
- **1 point** constrains a single axis (e.g., X translation).

### Maxwell kinematic coupling

Three V-grooves arranged on one surface, oriented toward the center (120 degrees apart). Three spheres (or curved surfaces) on the mating part rest in the grooves. Each V-groove provides 2 contact points, for 6 total. The result: perfectly repeatable positioning in all 6 DOF.

- **Repeatability**: sub-micron. Published data shows 0.1-0.3 micron (3-sigma) with hardened steel balls and V-grooves under 1500N preload. Even with mild steel, <2 micron repeatability is achievable.
- **Thermal stability**: because all three grooves point at the center, thermal expansion moves the mating part radially but symmetrically — the center point stays fixed.

### Kelvin clamp

A variation using three different constraint features instead of three identical V-grooves:

- **Tetrahedral socket** (cone or 3 balls forming a cup): 3 contact points.
- **V-groove** (pointing toward the tetrahedron): 2 contact points.
- **Flat surface**: 1 contact point.
- Total: 6 contact points = exact constraint.

The Kelvin clamp is less symmetric than Maxwell but allows one sphere to be located more precisely (at the cone), which can be useful when one axis matters more.

### Quasi-kinematic couplings

A practical compromise: instead of point contacts (which have high Hertzian stress), use small contact patches. Repeatability is slightly reduced (0.25-0.67 micron typical) but load capacity is much higher. Used in precision automotive assemblies.

### Practical at hobby/3D-print scale?

**Mostly no, for the precision they are designed for.** The sub-micron repeatability of kinematic couplings relies on smooth, hard contact surfaces (hardened steel, ceramic). FDM-printed V-grooves have:

- Layer lines creating ~0.1-0.2mm ridges.
- Dimensional variability of +/-0.2mm.
- Plastic deformation under repeated loading (especially PLA).

However, kinematic coupling **principles** are still useful at hobby scale:

- A simplified 3-groove-and-ball system printed in PETG with steel ball bearings (cheap, smooth, hard) dropped into printed sockets can achieve 0.2-0.5mm repeatability — far from sub-micron but potentially adequate.
- The **concept** of exact constraint (don't overconstrain) is universally applicable. Even a rail system should ideally constrain exactly the DOFs needed and leave the others free.

### When to use

Full kinematic couplings are overkill for this application (we need ~1mm, not microns) and poorly suited to FDM printing. But the constraint principles should inform whatever mechanism is chosen. A simplified kinematic-inspired approach (e.g., two V-grooves for lateral centering + a flat stop for Z) could work well.

---

## 3. Rail Systems

### Types

**Drawer slides (ball bearing):**
- Two telescoping members with ball bearing races between them.
- Typical clearance: 12.5-13.5mm per side between cabinet and drawer (about 1mm tolerance for installation).
- Self-centering: minimal. The drawer must be guided squarely; cross-racking causes binding.
- Force: smooth when aligned, high friction when misaligned.
- Applicable principle: a pair of parallel rails provides excellent guidance along one axis while constraining 4 DOF (two translations perpendicular to the rail, two rotations).

**Server blade chassis:**
- Blades slide into bays on stamped sheet metal rails.
- **Two-stage alignment**: coarse rail guidance along the length of the bay, then guide pins and alignment features at the backplane achieve fine alignment for connector mating.
- Midplane connectors are aligned by guide pins and edges in all three axes (Dell PowerEdge M1000e documentation).
- Connectors use receptacles on the midplane and pins on the blades — bent-pin risk is limited to the replaceable blade, not the chassis.
- Ejector handles (levers) provide mechanical advantage for final seating and extraction.
- Directly analogous to the cartridge problem: coarse rail + fine pin alignment + lever for seating/extraction.

**PCIe slot guides:**
- Card edge guided by the slot opening (chamfered edges on the slot).
- Rear bracket provides a physical reference plane.
- Retention clip/latch at the far end of the slot locks the card.
- Very simple: the slot itself is the guide, and the tight fit of the edge connector provides final alignment.
- Relevant principle: the slot entrance can be wider than the card (0.5-1mm clearance), providing coarse guidance, while the connector itself provides fine alignment as it seats.

### Tolerances and clearances

- Ball bearing drawer slides: typically 1/16" (1.6mm) total lateral clearance per side. Manufacturing tolerance of the slide itself: ~0.5mm.
- Server blade rails: stamped steel, ~0.5-1mm clearance between blade and bay walls. Guide pins at the backplane tighten this to <0.5mm at the connector interface.
- For 3D printing: rail clearance of 0.3-0.5mm per side (0.6-1.0mm total gap) allows smooth sliding in FDM. Tighter than 0.2mm per side will bind; looser than 0.6mm per side allows excessive wobble.

### Pros

- Excellent at constraining motion to a single axis (slide in/out).
- Natural and intuitive — users understand "slide it in."
- Can be long (100-200mm travel), providing guidance over the entire insertion stroke.
- Easy to 3D print as extruded profiles (constant cross-section).

### Cons

- Parallel rails must be printed accurately — warping or bed adhesion issues can cause rails to bow.
- Cross-racking (binding from asymmetric force) is a real problem with 3D-printed rails due to dimensional variation.
- Rails alone provide coarse alignment (0.5-1mm lateral play) but not the fine alignment needed at the mating face.
- Wear: PLA rails will wear and develop slop over time. PETG is better.

### When to use

Rails are the best choice for **coarse guidance** — getting the cartridge from "roughly aimed at the opening" to "within a few mm of the final position." They should be combined with a fine alignment feature at the mating face.

---

## 4. Dovetail Slides

### Geometry

A dovetail is a trapezoidal cross-section where the wider end is at the bottom (or interior). The male dovetail slides into a matching female channel. The angled sides prevent separation perpendicular to the slide axis while allowing free motion along it.

- **Typical dovetail angle**: 45-60 degrees (the angle of the sloped sides from vertical). 55 degrees is the most common for 3D-printed sliding dovetails.
- **Slight taper along length**: 1-2 degrees taper over the length of the dovetail creates a friction-lock fit — loose at entry, progressively tighter. This is a useful design trick for cartridge applications: easy to start inserting, snug when fully seated.

### Constraint properties

A dovetail constrains 4 DOF:
- X translation (perpendicular to slide, horizontal)
- Y translation (perpendicular to slide, vertical — the "anti-lift" direction)
- Rotation about the slide axis
- Rotation about the vertical axis

It leaves free:
- Z translation (along the slide axis)
- Rotation about the horizontal axis (pitch) — weakly constrained by friction

Compared to simple rectangular rails, dovetails add the critical anti-lift constraint. The cartridge cannot be pulled away from the dock perpendicular to the slide direction — it must be slid out.

### 3D printing considerations

- **Clearance**: 0.2-0.3mm per side for a snug sliding fit; 0.3-0.5mm for free sliding. Total gap of 0.4-0.6mm typical.
- **Male vs. female offset**: offset the male (make it smaller) rather than expanding the female. This is simpler in CAD and more predictable in print.
- **Corner fillets**: essential. A sharp internal corner on the female channel will have a radius from the FDM process anyway; adding an explicit fillet (0.5-1mm) on the female and a matching chamfer on the male prevents corner interference.
- **Print orientation**: the dovetail cross-section should be in the XY plane (printed flat) so that the angled sides are formed by the perimeter paths, not by layer stairstepping. Printing the dovetail vertically (angled sides formed by layer lines) produces a rough, stepped surface that binds.
- **Post-processing**: light sanding with 400-grit sandpaper on mating surfaces significantly improves sliding feel.

### Pros

- Simple geometry, natural fit for a slide-in cartridge.
- Anti-lift constraint is inherently provided.
- Self-centering in the lateral direction as the dovetail tapers engage.
- Single-piece printable (no hardware needed).
- Taper-along-length trick provides progressive snugging.

### Cons

- Requires more precise printing than rectangular rails (angled surfaces are less forgiving).
- Female channel must be printed open-side-up or with supports.
- Wear on plastic dovetails develops slop over time.
- Cross-section must be uniform along the length (or intentionally tapered), which constrains the overall design.

### When to use

A dovetail is a strong candidate for this application: it provides slide-in guidance with anti-lift, and the progressive taper can provide a snug seated feel. It could serve as the primary guide mechanism, with tapered pins at the mating face for final precision alignment of the tube stubs.

---

## 5. Tapered Lead-In / Funnel Approaches

### Principle

The entrance to the dock is oversized (funnel-shaped), and the channel narrows progressively until the cartridge is constrained to its final position. The user aims roughly at the opening; the geometry does the rest.

### Taper angles and their effects

The relationship between taper angle and behavior:

| Per-side angle | Total included angle | Character | Typical use |
|---|---|---|---|
| 5-10 degrees | 10-20 degrees | Very gradual, long lead-in. Low lateral force. | Long-range guidance (>50mm capture range) |
| 10-20 degrees | 20-40 degrees | Moderate. Good balance of capture range and centering force. | General-purpose lead-in funnels, magazine wells |
| 20-30 degrees | 40-60 degrees | Aggressive centering. Higher lateral force component. | Short lead-in where space is limited |
| 30-45 degrees | 60-90 degrees | Very aggressive. Quick centering but requires more insertion force. | Tight spaces, very coarse initial alignment |

### Design heuristics

- **Capture range**: the funnel entrance should be at least 2-3x the expected misalignment. If the user might be off by 10-15mm (realistic for blind under-sink insertion), the funnel entrance should be 25-40mm wider than the cartridge on each side.
- **Transition to final fit**: the funnel narrows to the final clearance (0.3-0.5mm for FDM rail fit) over the last 10-20mm. This transition should be smooth (tangent arc or gentle curve), not a sharp angle change, to prevent catching.
- **Fillet at the entrance**: a 1.5-3mm radius at the funnel lip prevents snagging and feels better in hand. Sharp edges on the funnel lip catch and are uncomfortable.
- **Two-stage**: a wide funnel (30-degree taper) at the entrance for coarse capture, transitioning to a shallow taper (5-10 degrees) for the last 15-20mm of fine centering. This is the "shotgun then rifle" approach.

### Insertion force considerations

A steeper taper generates more lateral centering force but also more friction (the cartridge is pushed harder against the funnel walls). For one-handed insertion with possibly wet hands:

- Keep total taper angle under 40 degrees to avoid excessive friction.
- PETG-on-PETG has a lower friction coefficient (~0.1-0.2) than PLA-on-PLA (~0.2-0.3), so PETG is preferred for funnel surfaces.
- A light silicone spray on printed funnel surfaces can dramatically reduce friction.

### Real-world examples

- **Firearm magazine wells**: aftermarket magwells use 15-25 degree tapers, with 1.5-3mm entrance fillets, to guide magazine insertion under stress. Prioritize speed over precision.
- **Electrical connector shrouds**: D-sub connectors, USB-A ports, etc. use chamfered or tapered housings at 15-30 degrees for the first 2-5mm of insertion.
- **Automotive ECU connectors**: wide funnel entrance, 10-15 degree taper, for blind mating in engine bays.

### When to use

A tapered lead-in is almost always the right choice for the **entrance** to a cartridge dock, especially in limited-visibility environments. It is a coarse guidance mechanism and must be combined with a tighter-tolerance feature (rails, dovetails, or pins) for final positioning.

---

## 6. Combination Approaches

### The general pattern

Most real-world docking systems use a **multi-stage** alignment strategy:

1. **Coarse capture** (funnel/chamfer): accepts misalignment of 10-20mm, guides toward the opening.
2. **Guided travel** (rails/dovetails): constrains motion to a single axis with 0.5-2mm lateral clearance.
3. **Fine alignment** (tapered pins/cones at the mating face): corrects the remaining 0.5-2mm of error to sub-mm precision as the last 10-20mm of travel seats.

This layered approach is robust because each stage only needs to reduce error by a factor of 3-10x, which is achievable even with coarse manufacturing (FDM).

### Spacecraft docking (instructive extreme case)

Published research on two-stage docking mechanisms describes:

1. **Capture jaws** interact with V-shaped grooves for coarse alignment.
2. **Two pins and holes** provide fine alignment as the mechanism draws closer.
3. **Final locking** after fine calibration, with floating electrical/hydraulic connectors mating last.

The principle — coarse capture, fine pins, then connector mating — scales directly down to a kitchen-sink cartridge.

### Common combinations in consumer products

| Product | Coarse guidance | Fine alignment | Locking |
|---|---|---|---|
| Server blade | Sheet metal rails | Guide pins at backplane | Ejector lever |
| Power tool battery | Shaped rail profile | Terminal alignment ribs | Spring detent/latch |
| Inkjet cartridge | Carriage slot walls | Locating ribs + spring | Spring latch over rear |
| Water filter | Housing bore | O-ring centering | Quarter-turn bayonet |
| Laptop dock (legacy) | Tapered side guides | Connector pins in shroud | Latch hook |
| PCIe card | Slot opening | Edge connector + bracket | End clip |

### Design recommendation for this project

A three-stage combination is the most promising approach:

1. **Funnel entrance** (20-30 degree taper, ~15mm wide capture zone per side) catches the cartridge even with sloppy aim.
2. **Dovetail or rectangular rails** (~100mm long, 0.3-0.5mm per-side clearance) guide the cartridge along the insertion axis.
3. **Two tapered pins** (15-20 degree per-side taper, 8-10mm base diameter) at the mating face provide final ~1mm alignment for the tube stubs as the last 15mm of travel seats.

---

## 7. Prior Art in Consumer Products

### Inkjet printer cartridges

**Mechanism**: the print cartridge slides down into a carriage slot from above (or from the front on some models). The carriage has:

- **Slot walls**: parallel vertical surfaces that constrain the cartridge laterally. Clearance is tight (~0.5mm per side).
- **Locating ribs**: small raised features on the carriage walls that the cartridge clicks past, providing a tactile "seated" feel and preventing the cartridge from backing out.
- **Spring-loaded latch**: a stamped stainless steel spring clamp applies downward force on the rear top of the cartridge. The spring geometry (serpentine arms for a compact, long-deflection spring) holds the cartridge firmly seated. This clamp is the primary retention mechanism.
- **Electrical contact**: a flexible PCB with spring contacts presses against pads on the cartridge face. The spring force from the latch ensures consistent contact pressure.

**Lessons for this project**:
- The latch spring provides both retention and electrical contact pressure — dual purpose.
- Slot walls provide coarse alignment; the contact pads and ink nozzle interface provide fine alignment.
- Toolless insertion/removal (push in, flip latch to release).
- The ink nozzle alignment to the paper path is achieved within ~0.1mm by the precision of the molded plastic carriage — injection molding can hold +/-0.05mm, which FDM cannot match.

### Power tool battery packs (DeWalt, Milwaukee)

**Mechanism**: the battery slides onto the tool along a shaped rail profile.

- **DeWalt 20V MAX**: battery slides forward onto the tool along T-shaped rails. The rails have angled teeth that grip the battery. A spring-loaded latch at the front catches a detent on the tool, locking the battery. A push-button on the battery releases the latch.
- **Milwaukee M18**: similar rail-and-latch system. Two fang-shaped rails on the battery engage matching channels on the tool. Five terminal divots in a recessed center panel provide electrical connection.
- **Rail profile**: the rail cross-section is intentionally asymmetric or keyed so the battery can only be inserted in one orientation (polarity protection).
- **Clearance**: the rail fit is moderately loose (~0.5-1mm) for easy insertion even with dirty/gloved hands. Final alignment of the electrical contacts is achieved by the terminal geometry itself (tapered contact pins self-center in the divots).

**Lessons for this project**:
- Rail-and-detent is proven for one-handed, blind operation in harsh conditions (construction site, dirty hands).
- The rail provides coarse guidance; the electrical contacts do their own fine alignment.
- A keyed profile prevents wrong-orientation insertion.
- Audible and tactile click on latch engagement gives user confidence.

### Server blade chassis

**Mechanism**: blades slide into bays on stamped sheet metal rails, with a two-stage alignment system.

- **Rails**: stamped steel flanges on the top and bottom of the bay guide the blade. Clearance is ~0.5-1mm.
- **Guide pins at the backplane**: two or more tapered pins on the backplane (or blade) mate with corresponding holes. These provide fine alignment (sub-mm) as the blade approaches the connector.
- **Midplane connectors**: aligned by guide pins and edges in all three axes. Receptacles on the midplane, pins on the blade — so bent-pin risk is isolated to the replaceable blade.
- **Ejector handles**: cam-action levers that provide mechanical advantage (~3:1 to 5:1) for the final push to seat connectors and for extraction. This is directly relevant to the cartridge lever.

**Lessons for this project**:
- The most directly analogous consumer product to the cartridge dock.
- Two-stage (rail + pins) alignment is the standard approach.
- Ejector/cam levers solve the "last push" problem of seating connectors that require force.
- Design the connector interface so damage from misalignment affects the replaceable part (cartridge), not the dock.

### Under-sink water filter housings

**Mechanism**: varies by manufacturer, but common approaches are:

**Twist-lock (quarter-turn bayonet)**:
- The filter cartridge has fins or tabs.
- User aligns the fins with slots in the housing head, pushes up, and rotates 90 degrees.
- The rotation compresses O-ring seals and locks the cartridge.
- Advantages: strong retention, watertight seal, one-hand operation.
- Disadvantages: requires rotational motion (not pure slide-in), alignment of fins to slots requires some visibility or tactile feel.

**Drop-in with threaded sump**:
- The cartridge drops into a cylindrical sump housing.
- The sump screws onto the housing head.
- Alignment is provided by the cylindrical bore; the cartridge self-centers.
- This is the traditional "big blue" style. Less relevant (requires two hands, a wrench, and is not quick-change).

**Push-in (newer designs)**:
- Some modern systems (e.g., certain 3M Aqua-Pure, GE SmartWater) use a push-in design where the filter cartridge pushes straight into a manifold.
- The cartridge has a shaped nose that mates with a shaped receptor.
- O-rings provide the seal; a twist or latch locks it in place.

**Lessons for this project**:
- Under-sink environment validated: manufacturers design for limited visibility, wet hands, one-handed operation.
- O-ring centering is effective — the O-ring itself provides ~1mm of self-centering as it compresses.
- Tactile and audible "click" on locking is a universal design choice.
- Cylindrical geometry provides natural centering, but the cartridge has rectangular constraints (2 pumps), so cylindrical is not directly applicable.

### Laptop docking stations (legacy mechanical docks)

**Mechanism** (e.g., Dell E-Port, Lenovo ThinkPad dock):

- **Tapered side guides**: the dock has angled walls that narrow toward the center. The laptop slides along these guides, which correct left-right and front-back misalignment.
- **Connector alignment**: a proprietary connector on the bottom of the laptop mates with a matching connector on the dock. The connector shroud has tapered lead-ins (~15-20 degrees) that center the laptop over the connector for the last ~5mm of travel.
- **Latch hook**: a spring-loaded hook on the dock engages a slot on the laptop, locking it in place. A slider or button on the dock releases the hook.

**Lessons for this project**:
- Tapered side guides (funnel approach) work well for single-axis alignment.
- The connector itself has a tapered shroud for fine alignment — the same principle as tapered pins.
- The latch provides both retention and a satisfying "docked" feel.

**Modern docks** (USB-C/Thunderbolt) have abandoned mechanical alignment entirely — a single cable provides connection. Not relevant to this project.

---

## 8. 3D Printing Considerations

### FDM tolerances for sliding fits

| Feature | Typical FDM accuracy | Notes |
|---|---|---|
| XY dimensional accuracy | +/- 0.2mm | Well-calibrated printer, PLA or PETG |
| Z dimensional accuracy | +/- 0.1-0.2mm | More consistent than XY due to stepper resolution |
| Hole diameter (small, <10mm) | Prints ~0.1-0.2mm undersized | Compensate in CAD or drill to size |
| Hole diameter (large, >10mm) | Prints ~0.2-0.3mm undersized | Less predictable |
| Surface roughness (side walls) | ~0.1mm Ra at 0.2mm layer height | Layer lines visible and tactile |
| First layer (elephant foot) | 0.15-0.25mm wider than nominal | Enable elephant foot compensation in slicer |

### Recommended clearances for sliding fits

| Fit type | Per-side clearance | Total gap | Character |
|---|---|---|---|
| Press fit | 0.0-0.1mm | 0.0-0.2mm | Requires force to assemble, may crack |
| Snug/friction fit | 0.1-0.15mm | 0.2-0.3mm | Stays together, can be separated by hand |
| Sliding fit | 0.15-0.25mm | 0.3-0.5mm | Slides freely with minimal play |
| Clearance fit | 0.25-0.4mm | 0.5-0.8mm | Loose, rattles slightly |

For the cartridge dock rails: **0.2-0.3mm per side (0.4-0.6mm total gap)** is the sweet spot. This allows smooth sliding even with minor warping or dimensional variation, while keeping lateral play under 1mm.

### Which mechanisms are most forgiving of FDM tolerances?

**Most forgiving (best for FDM):**
1. **Tapered lead-in / funnel**: the wide entrance inherently accommodates dimensional variation. Even if the funnel is off by 0.5mm, it still works.
2. **Tapered pins with generous taper**: a 15-20 degree taper self-centers despite surface roughness and dimensional error.
3. **Rectangular rails**: simple geometry, easy to print, easy to sand to fit. Less precision-dependent than dovetails.

**Moderately forgiving:**
4. **Dovetail slides**: work well if printed flat (dovetail cross-section in XY plane). The angled surfaces are formed by perimeter paths, which are smoother than layer-line surfaces. Requires careful clearance tuning.

**Least forgiving (worst for FDM):**
5. **Kinematic couplings**: requires smooth, precise contact surfaces that FDM cannot provide. Steel balls in printed sockets is a workable hybrid, but not truly kinematic precision.
6. **Tight-tolerance pin-and-hole**: straight (non-tapered) pins in holes have almost zero tolerance for error. Avoid.

### Material selection

**PETG (recommended for sliding surfaces):**
- Lowest friction coefficient of common FDM materials (~0.1). Published research shows superlubric potential.
- Good dimensional stability (moderate shrinkage, between PLA and ABS).
- Excellent wear resistance — significantly better than PLA for repeated sliding.
- Slight flexibility absorbs minor misalignment without cracking.
- Moisture resistant (under-sink environment).
- Prints at 230-250 degrees C, bed at 70-80 degrees C. Slightly trickier than PLA but well within typical FDM capability.

**PLA:**
- Lowest shrinkage, best dimensional accuracy of common materials.
- Rigid — good for structures that must hold precise dimensions.
- Brittle — snaps rather than flexes under impact or overconstraint.
- Higher friction coefficient than PETG.
- Not moisture resistant. Under a kitchen sink, PLA will absorb moisture over months and weaken.
- Best for: initial prototyping and fit-testing, not for final parts in a wet environment.

**ABS:**
- Highest shrinkage and warping tendency — hardest to hold dimensions.
- Good wear resistance and impact strength.
- Higher friction than PETG.
- Requires enclosure for reliable printing.
- Not the best choice here due to dimensional challenges.

**Recommendation**: print rails and dovetails in PETG for the final version. Use PLA for quick-iteration prototyping of fits and clearances (cheaper, faster to print, easier to sand).

### Print orientation for rail and guide features

**Critical rule**: FDM parts are 4-5x weaker across layer lines than along them. Tensile strength in the XY plane is typically 30-50 MPa; across layers (Z direction) it drops to 8-15 MPa.

For rail features:
- **Rails that run horizontally** (parallel to the print bed): print the part with rails in the XY plane. The rail cross-section is formed by perimeter paths (strong) and the rail length is along the layer stack (acceptable for compressive loads but weak for lateral shear).
- **Rails that must resist lateral forces**: orient so the force is parallel to the layer lines, not perpendicular. A rail that will be pushed sideways during insertion should have its layers running perpendicular to the insertion direction, so the shear force is carried by the perimeters, not the inter-layer bonds.
- **Anti-lift features** (dovetail overhangs, latch catches): these experience tension across the overhang. Print them so the tension is in the XY plane. If the overhang is perpendicular to the bed, it will delaminate under load.

**Practical guideline**: print the dock half with the rail opening facing up. Print the cartridge half with the rail features facing down (on the bed) for best surface finish and dimensional accuracy on the mating surfaces.

### Post-processing to tune fit

- **400-600 grit sandpaper**: light sanding on mating surfaces removes high spots from layer lines and improves sliding feel dramatically.
- **Filing**: a flat needle file is effective for adjusting tight spots on rails.
- **Heat gun (cautiously)**: briefly warming a tight PETG surface can smooth it, but risk of warping. Not recommended for precision fits.
- **Silicone lubricant spray**: thin coat on sliding surfaces reduces friction significantly. Safe on PETG and PLA.
- **Test prints**: always print a small section of the rail cross-section (50mm long) as a test piece before printing the full part. Adjust clearance in CAD based on the test fit.

---

## 9. Evaluation for This Application

### Requirements recap

- 4 tube stubs must align within ~1mm of 4 John Guest fittings at the mating face.
- Under-sink, limited visibility, one hand, possibly wet.
- FDM 3D printed prototype.
- Front insertion (slide in along one axis).
- Lever provides final seating force and release.

### Evaluation matrix

| Mechanism | Capture range | Final precision | FDM-friendly | Blind/one-hand | Complexity | Verdict |
|---|---|---|---|---|---|---|
| Tapered pins only | 5-10mm | <0.5mm | Good | Poor (must find pins) | Low | Fine alignment only |
| Kinematic coupling | Near-zero | <0.001mm | Poor | Poor | Medium | Overkill, wrong material |
| Rectangular rails | 2-5mm (at entrance) | 0.5-1mm | Excellent | Good | Low | Good coarse guidance |
| Dovetail slide | 2-5mm (at entrance) | 0.3-0.5mm | Good | Good | Medium | Good all-around |
| Funnel entrance | 15-30mm | 5-10mm | Excellent | Excellent | Low | Coarse capture only |
| Rails + tapered pins | 2-5mm / 5-10mm | <0.5mm | Good | Good | Medium | Strong candidate |
| Funnel + dovetail + pins | 15-30mm / 2-5mm / 5-10mm | <0.5mm | Good | Excellent | Medium-High | Best overall |

### Most promising approaches

**Option A: Funnel entrance + rectangular rails + tapered pins at mating face**

The simplest multi-stage approach. A chamfered/tapered entrance to the dock (20-30 degrees, 15-20mm wide capture zone) catches sloppy initial aim. Rectangular rails (100-150mm long, 0.3mm per-side clearance) guide the cartridge along the insertion axis. Two tapered pins (15-20 degree per-side, 10mm base) on the dock mating face engage matching conical sockets on the cartridge for the last 15-20mm of travel, correcting the remaining 0.5-1mm of lateral error.

- Pros: simple to print, each stage is individually tunable, rectangular rails are the most forgiving geometry.
- Cons: rectangular rails provide no anti-lift (the cartridge can be pulled away from the dock perpendicular to the slide axis, though the John Guest fittings provide retention once seated).

**Option B: Funnel entrance + dovetail slide + tapered pins at mating face**

Same as Option A but replaces rectangular rails with a dovetail profile. This adds anti-lift constraint — the cartridge cannot be lifted out of the dock, only slid out.

- Pros: anti-lift is inherently provided. More rigid connection during use.
- Cons: dovetail requires more careful printing and clearance tuning. Print orientation is constrained. The taper-along-length trick (1-2 degrees over the dovetail length) could provide a progressively snugging fit that gives a "seated" feel even without the lever.

**Option C: Wide funnel entrance + long tapered channel (no separate pins)**

Instead of distinct rails + pins, the dock is a single tapered channel that narrows from a wide entrance (~40mm wider than the cartridge) to the final fit clearance (0.3mm per side) over the full insertion length (~100-150mm). This is essentially a long, gradual funnel.

- Pros: simplest geometry. No discrete rail/pin features to align. Very forgiving of sloppy initial aim.
- Cons: long shallow taper requires more depth (insertion length). Friction increases progressively. Less rigid at the midpoint of travel (the cartridge can wobble until nearly fully inserted). Final precision depends on the quality of the narrowest section, which is hard to print consistently over a long length.

### Recommendation

**Option A (funnel + rectangular rails + tapered pins)** is the best starting point for a 3D-printed prototype. It separates coarse guidance from fine alignment, making each independently tunable. The rectangular rail geometry is the most forgiving of FDM tolerances and the easiest to adjust by sanding. The tapered pins at the mating face handle the precision alignment (~1mm) that the rails cannot achieve alone.

If anti-lift becomes a requirement (the cartridge needs to stay constrained before the John Guest fittings engage), switch to **Option B** (dovetail variant).

Print a test rail cross-section first (50mm long) to dial in clearance before printing the full dock.

---

## Sources

- [Kinematic coupling - Wikipedia](https://en.wikipedia.org/wiki/Kinematic_coupling)
- [3D Printable Kinematic Couplings | Hackaday](https://hackaday.com/2020/08/11/3d-printable-kinematic-couplings-ready-to-use/)
- [Kinematic couplings: A review of design principles and applications (MIT)](https://dspace.mit.edu/bitstream/handle/1721.1/69013/Kinematic%20coupling%20review%20article.pdf)
- [Precision assembly of additively manufactured components using integral kinematic couplings](https://www.sciencedirect.com/science/article/abs/pii/S0141635919300662)
- [3D Printing Tolerances & Fits - 3DChimera](https://3dchimera.com/blogs/connecting-the-dots/3d-printing-tolerances-fits)
- [Guide to 3D Printing Tolerances, Accuracy, and Precision | Formlabs](https://formlabs.com/blog/understanding-accuracy-precision-tolerance-in-3d-printing/)
- [3D Print Tolerance & Fit Calculator | GrandpaCAD](https://grandpacad.com/tools/tolerance-fit-calculator)
- [How to 3D Print Interlocking Parts | Formlabs](https://formlabs.com/blog/how-to-3d-print-interlocking-joints/)
- [3D Printed Joinery: Simplifying Assembly | Markforged](https://markforged.com/resources/blog/joinery-onyx)
- [Dovetail tolerance test - MakerWorld](https://makerworld.com/en/models/132619-dovetail-tolerance-test)
- [Designing 3D printable dove tail joints - Autodesk Community](https://forums.autodesk.com/t5/fusion-design-validate-document/designing-3d-printable-dove-tail-joints/td-p/9494533)
- [Locating and Fixturing Pins Selection Guide | GlobalSpec](https://www.globalspec.com/learnmore/manufacturing_process_equipment/machine_tool_accessories/jig_fixturing_components/locating_fixturing_pins)
- [Principles of Positioning | MISUMI](https://us.misumi-ec.com/maker/misumi/mech/tech/locating_pins_tutorial/)
- [Taper pin - Wikipedia](https://en.wikipedia.org/wiki/Taper_pin)
- [Self-locking taper angle | Eng-Tips](https://www.eng-tips.com/threads/self-locking-taper-angle.526713/)
- [Structural design of a two-component docking mechanism | Scientific Reports](https://www.nature.com/articles/s41598-025-88757-z)
- [Dell PowerEdge M1000e Technical Guide](https://i.dell.com/sites/content/business/solutions/engineering-docs/en/Documents/server-poweredge-m1000e-tech-guidebook.pdf)
- [US Patent 6,692,107 - Ink cartridge body and carrier assembly](https://patents.justia.com/patent/6692107)
- [US Patent 5,392,063 - Spring cartridge clamp for inkjet printer carriage](https://patents.google.com/patent/US5392063A/en)
- [US Patent 6,247,805 - Ink cartridge insertion mechanism](https://patents.google.com/patent/US6247805B1/en)
- [Fast Cartridge Change Designs: Twist vs Push-In | Viomi](https://water.viomi.com/blogs/hydration-lab/fast-cartridge-change-twist-vs-push-in)
- [PETG vs PLA vs ABS: 3D Printing Strength Comparison | Ultimaker](https://ultimaker.com/learn/petg-vs-pla-vs-abs-3d-printing-strength-comparison/)
- [Print Orientation Affects Strength | Polymaker](https://wiki.polymaker.com/the-basics/fun-3d-printing-facts/print-orientation-affects-strength)
- [How 3D Printing orientation affects strength | FacFox](https://facfox.com/docs/kb/how-3d-printing-direction-orientation-affects-strength)
- [Mechanical Design for 3D Printing | Eiki Martinson](http://eikimartinson.com/engineering/3dparts/)
