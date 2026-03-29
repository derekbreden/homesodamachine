# Design Pattern Research: Pump Cartridge Mechanism

This document captures how existing consumer products achieve the three UX qualities the vision demands for the pump cartridge: satisfying squeeze-to-release, confident slide-in seating, and minimal exterior surfaces hiding internal complexity.

---

## 1. Satisfying Squeeze-to-Release with Hidden Mechanism

The vision specifies: the user squeezes two flat surfaces (palm pushing against cartridge body, fingers pulling release surface, hand palm-up). The entire release mechanism is hidden inside the cartridge. The squeeze must feel deliberate and clean, not accidental.

### Product Studies

#### Southco 60-Series Squeeze-Release Latches

Southco's 60-series latches are the closest industrial analog to the vision's interaction. The user squeezes protruding tabs to unlatch, then pulls to open; pushing closes the latch with a snap.

**Key specifications (model 60-10-101-12):**
- Material: black acetal (similar stiffness/feel to PETG or ABS)
- Total width: 14 mm
- Maximum panel thickness: 1.3 mm
- Grip range: 1.0 mm to 3.1 mm
- Maximum load between panels permitting unlatching: 13.5 N (3 lbs)
- Maximum intermittent working load: 170 N (35 lbs)

**What produces the UX quality:** The unlatching force of 13.5 N is low enough for comfortable one-handed operation but high enough to prevent accidental release from bumps or vibration. The acetal material produces a crisp, clean snap sound on re-engagement. The latch tabs are the only external indication of the mechanism; everything structural is behind the panel.

**Actionable guidance:** The squeeze-to-release force should be in the range of 10-20 N. Below 10 N risks accidental release; above 20 N becomes uncomfortable for repeated one-handed operation. Acetal or ABS produces crisper tactile feedback than polypropylene or PETG for the latch surfaces.

#### Epson XP-Series Ink Cartridge Release

Epson printers use a squeeze-tab mechanism for cartridge removal. The user squeezes a small tab on the end of the cartridge and pulls upward. A spring holds the cartridge seated against electrical contacts (the CSIC terminal).

**Key mechanical details:**
- The tab is a cantilevered plastic arm, approximately 8-12 mm long
- A small spring behind the cartridge provides retention force, keeping the cartridge pressed forward against contacts
- The squeeze deflects the cantilever approximately 1.5-2 mm to clear the retention hook
- The release is one-axis: squeeze inward, pull upward. No rotation or complex motion.

**What produces the UX quality:** The spring provides constant background retention force so the cartridge feels "held" at all times. The squeeze tab deflects a small, precise distance and releases cleanly. There is a distinct tactile boundary between "latched" and "free" because the cantilever hook either engages the catch or it does not -- there is no intermediate state.

**Actionable guidance:** The engagement hook depth (the distance the cantilever must deflect to clear the catch) should be at least 1.5 mm to provide a clear tactile boundary between latched and free states. A hook depth under 1 mm feels ambiguous.

#### Dyson Vacuum Bin Release (Ball and V-Series)

Dyson uses two distinct release mechanisms across its product lines:

**Ball Upright:** A spring toggle mechanism that rocks to release the cyclone assembly. The user pushes a single red button; the mechanism inside rocks a toggle past a detent. The button is ABS, colored red to contrast with the grey/purple body. The release is a push-button, not a squeeze, but the principle of a hidden toggle behind a simple exterior surface is directly relevant.

**V-Series Cordless (V7/V8/V10/V11/V15):** Wand attachments use a clip latch tab with an internal spring. The tab sits flush with the wand surface when engaged. To release, the user pushes the tab (approximately 2-3 mm travel), which deflects an internal spring clip past a retention hook, freeing the attachment. Replacement parts confirm the mechanism is a small plastic clip with a separate compression spring.

**What produces the UX quality:** The red color makes the release surface impossible to miss, but the mechanism itself is entirely hidden behind the button surface. The spring toggle in the Ball model creates a crisp over-center snap: the force rises to a peak, then drops sharply as the toggle passes center. This force profile (rise, peak, sudden drop) is what creates the sensation of a deliberate, clean release.

**Actionable guidance:** An over-center or detent-based force profile (force rises during squeeze, peaks, then drops sharply at release) produces a more satisfying release than a linear spring. The force peak should be at 60-80% of the total travel distance, with a rapid force drop in the final 20-40%. The squeeze surface should be visually distinct (color, texture, or inset) from the rest of the cartridge even if both surfaces are flat.

#### SodaStream Quick Connect Cylinder

The newer SodaStream machines use a push-to-lock cylinder insertion that releases with a squeeze of a collar.

**Key mechanical details:**
- Spring-loaded clamps with precision-molded grooves
- Dual-stage sealing with primary O-ring and secondary silicone gaskets
- Distinct audible click on engagement
- Clear visual alignment guides (arrow markers aligned with intake slot)

**What produces the UX quality:** The spring-loaded clamps create a definitive locked/unlocked state with no intermediate condition. The audible click provides confirmation without requiring the user to visually inspect the connection. The collar squeeze is the sole external moving part; all clamps and springs are hidden inside.

**Actionable guidance:** Spring-loaded clamp mechanisms that produce an audible click at the lock/unlock transition provide the strongest confirmation feedback. The click should be sharp (short duration, rapid force transition) rather than soft (gradual). If the squeeze mechanism can include a small detent or over-center element that produces a click at the moment of release, this will significantly increase user confidence.

### Ergonomic Force Guidelines for Squeeze

Research from the Canadian Centre for Occupational Health and Safety and the International Encyclopedia of Ergonomics provides these boundaries:

- **Maximum comfortable hand force:** 45 N for general use
- **Recommended for occasional short actions:** less than one-third of maximum grip strength (approximately 50-80 N for a brief squeeze)
- **Preferred handle span for one-handed two-surface squeeze:** 51 mm (2 inches) minimum, 76 mm (3 inches) preferred, 102 mm (4 inches) maximum
- **Sustained or repetitive squeeze actions:** keep below 30% of maximum muscle capacity

**Actionable guidance for the cartridge:** The cartridge squeeze span (distance between the two flat surfaces at rest) should be 50-80 mm. The release force should be 10-25 N. The squeeze travel (how far the surfaces move toward each other before release occurs) should be 3-6 mm: enough travel to feel intentional, but not so much that the user's hand fatigues or the motion feels sloppy.

### Synthesis: What Makes a Squeeze Feel Intentional vs. Accidental

Across all products studied, the following geometric details consistently separate deliberate from accidental squeeze interactions:

1. **Travel distance of 3-6 mm.** Under 2 mm feels twitchy and can be triggered accidentally. Over 8 mm feels effortful and imprecise.
2. **Force peak followed by sharp drop.** The force profile should rise smoothly during squeeze, peak at 10-25 N, then drop sharply at the release point. This over-center profile creates the sensation of "breaking through" a threshold.
3. **No intermediate state.** The mechanism is either latched or free. There is no "partially engaged" condition.
4. **Audible or tactile click at release.** A sharp click at the moment of release provides confirmation even without visual inspection. ABS and acetal produce sharper clicks than PP or PETG.
5. **Squeeze surfaces are visually distinct.** Even when both surfaces are flat (as the vision requires), they should differ from adjacent surfaces through inset depth, texture, or color contrast.

---

## 2. Slide-In Seating Confidence

The vision specifies: the cartridge slides in on rails with inset grooves. Four tubes push into quick connects upon insertion. There is no collet manipulation needed for reinsertion. The user must know, without looking, that the cartridge is fully seated.

### Product Studies

#### DeWalt 20V MAX Battery System

DeWalt's 20V MAX batteries use a slide-rail interface with a spring-loaded latch. The battery slides along two parallel rails into the tool, and a spring latch clicks into a detent at full engagement.

**Key mechanical details:**
- Two parallel T-shaped rails guide the battery on a single axis
- The slide travel is approximately 40-50 mm (the full length of the rail engagement)
- A spring-loaded plastic latch at the front of the tool engages a notch on the battery at full insertion
- The latch produces an audible click
- Removal requires pressing the latch button (approximately 15 mm wide) while pulling the battery backward along the rails
- The resistance curve during insertion: low friction glide along the rails, then a slight force increase at the last 3-5 mm as the latch deflects, followed by a click as it seats

**What produces the UX quality:** The rails eliminate all degrees of freedom except the insertion axis, so the user cannot seat the battery incorrectly. The increasing force at the end of travel (latch deflection) gives tactile warning that seating is imminent. The click at full engagement is definitive. The battery sits flush with the tool housing when fully seated, providing visual confirmation.

**Actionable guidance:** Rails should constrain all movement to a single axis. The last 3-5 mm of travel should have increased resistance (from a latch, detent, or spring compression) followed by an audible click. Flush alignment of the cartridge face with the enclosure dock surface provides visual confirmation of full seating.

#### Canon/Nikon Camera Battery Insertion

Camera batteries use a spring-loaded latch in a compartment. The battery slides in along a guided channel, pushes an orange (Nikon) or grey (Canon) spring latch to the side, and the latch snaps back to lock the battery in place.

**Key mechanical details:**
- The battery compartment has molded guide rails that accept only the correct orientation (keyed geometry)
- Insertion travel: approximately 25-35 mm for typical DSLR batteries
- The latch is a leaf-spring type, deflected by a ramp on the battery during insertion
- The latch snaps into a notch at full insertion with a tactile click
- Removal: push the latch sideways (Nikon) or press a button (Canon) and the battery ejects partially via spring pressure
- Spring-ejection on release gives the user confidence that the mechanism is active

**What produces the UX quality:** The keyed geometry makes wrong-way insertion physically impossible. The ramp-and-notch latch profile means the user feels smoothly increasing resistance, then a sudden snap at full engagement. The partial spring ejection when the latch is released confirms the spring mechanism is working. The battery clicks in and pops out: both transitions are crisp.

**Actionable guidance:** The cartridge should be keyed so that wrong-orientation insertion is physically impossible. A ramp leading to a notch (rather than a simple catch) creates a smooth force ramp followed by a definitive snap. If the mechanism includes quick connects that require push-in force, the snap of the latch should coincide with or immediately follow the full seating of the quick connects, so the click confirms both mechanical retention and fluid connection.

#### Samsung Refrigerator Water Filter (HAF-QIN)

Samsung's newer refrigerator water filters use a push-and-twist-lock mechanism. The filter pushes into a socket, then rotates clockwise until it clicks into a locked position.

**Key mechanical details:**
- Square-shaped body with three staggered teeth designed for high water pressure
- Push-in distance: approximately 20-30 mm
- Quarter-turn to lock (approximately 90 degrees)
- Audible click at lock position
- Locked symbol aligns with indicator line when properly seated (visual confirmation)
- O-ring seal engages during the push-in phase

**What produces the UX quality:** The two-phase insertion (push, then twist) provides two separate confirmation opportunities. The visual alignment of symbols at lock position provides confirmation even in poor lighting. The click is unambiguous.

**Note for our application:** The vision specifies a straight slide-in, not a push-and-twist. The relevant takeaway is the principle of multi-signal confirmation: the user receives tactile (click), visual (flush surface or aligned marking), and sometimes audible (snap) feedback simultaneously. All three signals agree, which produces confidence.

#### Apple MagSafe Connector

While MagSafe uses magnetic rather than mechanical retention, its alignment and seating feedback is highly relevant.

**Key specifications:**
- Self-alignment within 1.55 mm radial maximum
- Retention force: 800-1100 gf (7.8-10.8 N) to dislodge
- Magnets: N45SH NdFeB with 7-13 micrometer NiCuNi plating
- Haptic feedback confirms engagement
- The magnetic pull-in creates a "snap to center" effect in the last 2-3 mm of approach

**What produces the UX quality:** The self-centering means the user does not need to visually align the connector. The magnetic snap-in in the last 2-3 mm creates a definitive "it pulled itself in" sensation. The retention force is high enough to feel secure but low enough to disconnect cleanly. The iPhone provides a haptic buzz at connection, adding a fourth confirmation channel (sight, sound, touch, haptic).

**Actionable guidance:** If the cartridge can incorporate any self-centering feature in the last few millimeters of insertion (chamfered rail entries, tapered quick-connect approaches), this will significantly improve the seating experience. The rails should funnel the cartridge into precise alignment rather than requiring the user to achieve alignment before insertion begins.

### Synthesis: What Creates Seating Confidence

Across all products studied:

1. **Single-axis constraint.** Rails or channels eliminate all degrees of freedom except the insertion axis. The user pushes in one direction; everything else is handled by geometry.
2. **Ramped force profile ending in a click.** The last 3-5 mm of insertion should have smoothly increasing resistance, followed by a sharp snap as the latch engages. This profile means "almost there... almost... seated."
3. **Multi-channel confirmation.** The most confident-feeling products combine at least three channels: tactile (click felt in the hand), audible (snap sound), and visual (flush surface, aligned marking, or indicator light). Two channels is adequate. One channel (tactile only) is the minimum for acceptable seating confidence.
4. **Keyed geometry preventing wrong insertion.** If the cartridge can only go in one way, the user never wonders "did I put it in backward?"
5. **Self-centering in the final approach.** Chamfers, tapers, or funnels that guide the cartridge into precise alignment in the last 5-10 mm of travel reduce the cognitive load on the user and produce a feeling of the mechanism "pulling itself in."
6. **Flush surface at full engagement.** When the cartridge face sits flush with the enclosure dock, the user can see at a glance that it is fully seated.

**Specific guidance for the pump cartridge:** The four tube stubs pushing into quick connects will create insertion resistance. This resistance should be designed to ramp smoothly (chamfered tube ends, tapered quick-connect entries) rather than hitting a wall. The retention latch should click at the same moment the tubes reach full engagement depth in the quick connects, so the click means "tubes are connected AND cartridge is locked." If these two events are separated in time, the user will not know which event the click corresponds to.

---

## 3. Minimal External Surfaces Hiding Internal Complexity

The vision specifies: the user sees two flat squeeze surfaces, rail grooves on the sides, and four small tube holes on the back. The release plate, quick connects, springs, and all mechanism components are entirely hidden. The exterior reads as a simple block with obvious functional surfaces.

### Product Studies

#### Apple iPad Pro Enclosure

Apple's iPad Pro manufacturing process is the benchmark for hiding complexity behind minimal surfaces.

**Key manufacturing details:**
- Co-molding process: plastic injected into precisely milled channels in aluminum, bonding to micro-pores
- After co-molding, the entire enclosure is CNC-finished to a unified surface
- Flatness tolerance: 400 micrometers (0.4 mm) across the full length of any side
- Camera Control air gap: under 50 micrometers (0.05 mm), with Apple recommending zero gap
- No visible fasteners on any external surface
- All antennas, speakers, and microphones are hidden behind precisely machined apertures

**What produces the UX quality:** The absence of visible fasteners, seams, and mechanism indicators makes the device read as a monolithic object. The sub-millimeter tolerances mean surfaces meet so precisely that joints are nearly invisible. The user sees a flat slab; the complexity (processor, battery, cameras, antennas, speakers) is entirely hidden.

**Actionable guidance for FDM:** FDM cannot achieve 0.05 mm gap tolerances, but it can achieve the principle. External seams between cartridge body parts should be under 0.3 mm. Surfaces that the user touches should be printed face-down on the build plate for the smoothest possible finish. No fastener heads (screws, bolt heads) should be visible on any external surface.

#### Dyson V-Series Cordless Vacuum Body

Dyson cordless vacuums hide motor, cyclone, filter, battery, PCB, and wiring behind smooth polycarbonate and ABS shells.

**Key design details:**
- Cosmetic surfaces: ABS (smooth, paintable, consistent finish)
- Structural components: glass-filled polypropylene (GFPP) and polycarbonate (PC), hidden behind cosmetic shells
- The wand is extruded aluminum with plastic end caps -- the tube reads as a simple cylinder despite containing wiring and air channels
- Release buttons are the only moving parts visible externally; they are colored red or orange to contrast with the body
- All internal structure (motor mount, PCB bracket, wiring channels, filter housing) is molded into the interior of the shell halves and is invisible from outside

**What produces the UX quality:** The material strategy is key: cheap, strong structural material inside; smooth, consistent cosmetic material outside. The user sees clean surfaces in one or two colors. The only interruptions are functional (buttons, ports, indicators), and those interruptions are deliberately highlighted with contrasting color so the user understands their purpose.

**Actionable guidance:** Use a two-material or two-finish strategy: external surfaces smooth and consistent, internal structure can be rougher and functional. Any external feature that interrupts the smooth surface should be there for a reason the user can immediately understand. If the squeeze surfaces are inset into the cartridge body, the inset itself communicates "squeeze here" without requiring a label.

#### Nespresso Machine Capsule Chamber

Nespresso machines hide a complex brewing mechanism (water injection needle, pressure seal, capsule puncture, ejection arm) behind a single lever and a smooth exterior.

**Key design details:**
- The user interacts with one lever and a capsule slot
- Behind the lever: a cam mechanism that raises the injection head, punctures the capsule bottom, seals the chamber at approximately 19 bar, and ejects the spent capsule
- External surfaces are smooth, typically chromed or matte-painted ABS/PC blend
- The capsule slot is a simple rectangular opening; the user sees no needles, springs, or seals
- All complexity is accessed only via a maintenance panel on the underside or back

**What produces the UX quality:** The user's mental model is "put capsule in, close lever, press button." The actual mechanism (seal, puncture, pressurize, brew, eject) has at least six moving parts, but the user interacts with exactly one (the lever) and sees exactly two surfaces (the slot and the lever). The ratio of internal complexity to external simplicity is very high.

**Actionable guidance:** The pump cartridge should aim for a similar ratio. The user sees: two flat squeeze surfaces, rail grooves, tube holes. That is the complete external interface. Every internal component (release plate, quick connect collets, springs, pump mounts) should be invisible from any angle the user encounters during normal use. If the cartridge body has internal structure (ribs, bosses, channels), it should be hidden by the outer shell, not exposed through gaps or translucent material.

#### Breville/Sage Espresso Machine Portafilter Dock

Breville espresso machines use a portafilter that locks into the group head via a bayonet mount. The user sees a smooth, chromed portafilter handle and a flat group head face.

**Key design details:**
- The bayonet mount mechanism (spring-loaded ball detents, precisely machined lugs, silicone gasket) is entirely hidden behind the flat face of the group head
- The portafilter handle is a simple cylinder; the locking lugs are on the basket end, which the user does not see during normal operation
- The group head face presents as a flat, polished surface with a single circular opening
- Insertion resistance increases smoothly during the quarter-turn lock
- A spring-loaded ball detent provides a click at the fully locked position

**What produces the UX quality:** The "black box" quality comes from the group head face: a flat polished disc with one opening. No springs, detents, or lugs are visible. The user inserts, twists, and feels a click. The mechanical sophistication is entirely behind the flat face.

**Actionable guidance:** The enclosure dock face (the surface inside the enclosure that the cartridge slides into) should present as a flat surface with four tube stubs and rail channels, nothing more. All retention mechanism components (springs, latches, catches) should be behind this face, invisible to the user even when the cartridge is removed.

### Synthesis: How to Hide Complexity Behind Simple Surfaces

1. **Seam gaps under 0.3 mm.** For FDM printing, this is achievable with careful tolerance design. At 0.3 mm, seams are visible on close inspection but do not read as "gaps" at arm's length. At 0.5 mm and above, seams begin to look like separate parts rather than a unified object.

2. **No visible fasteners.** Screws, bolts, and clips should be internal. The cartridge body should be assembled with internal snap fits or adhesive, not external screws. If screws are necessary for assembly or service, they should be accessible only from the interior (e.g., through the tube-hole end).

3. **Functional surfaces only.** Every surface feature the user can see should have an obvious purpose. Rail grooves say "I slide." Tube holes say "tubes go here." Flat squeeze surfaces say "squeeze here" (especially if inset). There should be no decorative vents, unnecessary seams, visible ribs, or cosmetic-only features.

4. **Material and finish consistency on external surfaces.** All external surfaces should be the same material and finish. Mixed finishes (matte next to glossy, different colors on adjacent surfaces) make the object look assembled rather than monolithic.

5. **Internal ribs and structure are invisible.** If the cartridge body needs internal ribs, bosses, or gussets for strength, they must not create visible sink marks, read-through, or surface distortion on the exterior. Wall thickness should be consistent enough to avoid sink marks (minimum 1.2 mm walls for FDM).

6. **The squeeze inset is the deliberate exception.** The two flat squeeze surfaces are inset into the cartridge body (per the vision). This inset is the one intentional surface interruption, and it communicates function. The depth of the inset should be 1-2 mm: deep enough to be felt by fingertip, shallow enough that it reads as part of the surface rather than a separate component.

---

## Summary of Actionable Design Parameters

| Parameter | Recommended Range | Source |
|-----------|------------------|--------|
| Squeeze travel distance | 3-6 mm | Southco latches, Dyson release buttons, ergonomic guidelines |
| Squeeze release force | 10-25 N | Southco 60-series (13.5 N unlatch), ergonomic guidelines (max 45 N) |
| Squeeze span (distance between surfaces) | 50-80 mm | Ergonomic handle guidelines (preferred 76 mm) |
| Force profile | Rising, peak at 60-80% travel, sharp drop | Dyson toggle, snap-fit research |
| Retention hook depth | >= 1.5 mm | Epson cartridge, snap-fit design guides |
| Snap-fit deflection for latch | 2-3 mm | Snap-fit design guides (ABS, 3 mm undercut example) |
| Latch retention force | 15-25 N | Snap-fit design guides, SodaStream quick connect |
| Rail-guided insertion (degrees of freedom) | 1 (single axis) | DeWalt battery, camera batteries |
| End-of-travel resistance zone | Last 3-5 mm of insertion | DeWalt battery, Canon/Nikon batteries |
| External seam gap | <= 0.3 mm | Apple tolerances adapted for FDM |
| Squeeze surface inset depth | 1-2 mm | Dyson button inset, Nespresso lever recess |
| Minimum wall thickness (external cosmetic) | 1.2 mm | FDM requirements (3 perimeters at 0.4 mm nozzle) |
| Quick-connect entry chamfer | 1-2 mm x 30-45 degrees | MagSafe self-centering principle, standard QC fitting practice |

---

## Key Design Principles (Ranked by Impact)

1. **The latch click must coincide with full tube engagement in the quick connects.** If the click happens before or after the tubes are fully seated, the click loses its meaning. This is the single most important timing detail in the mechanism.

2. **The force profile during squeeze-to-release must be non-linear: rise, peak, drop.** A linear spring feel is functional but unsatisfying. An over-center detent, cam, or snap-through element creates the deliberate, clean release the vision demands.

3. **Rails constrain to one axis; chamfers self-center.** The user should be able to insert the cartridge without looking by feel alone. Tapered rail entries and chamfered tube ends guide everything into place.

4. **Every visible surface has an obvious purpose.** Rail grooves, tube holes, squeeze surfaces: the user understands each at a glance. No surface exists without communicating function.

5. **All mechanism components are behind the exterior shell.** Release plate, springs, quick-connect collets: none of these are visible from any user-facing angle.
