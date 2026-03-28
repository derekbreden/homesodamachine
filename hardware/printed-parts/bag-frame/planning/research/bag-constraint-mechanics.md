# Bag Constraint Mechanics Research

Research into constraining a Platypus 2L collapsible water bottle within a rigid frame, mounted diagonally at ~35 degrees, maintaining 25-30mm midsection thickness.

## 1. Platypus 2L Physical Dimensions

**Manufacturer specifications:**
- Flat dimensions: 190mm wide x 350mm long (7.5" x 13.8")
- Weight empty: 37g (1.3 oz)
- Material: BPA-free polyethylene film, nylon outer layer, polypropylene cap
- Film thickness: approximately 0.1mm (typical for PE/nylon laminate pouches)
- Capacity: 2000mL (70 fl oz)

**Filled shape (unconstrained, lying flat on a surface):**
- The bag is made from two flat PE/nylon sheets heat-sealed around the perimeter
- When filled and laid flat, the cross-section is lenticular (lens-shaped): two convex arcs meeting at thin edges defined by the perimeter heat seal
- The heat seals form a rigid edge approximately 5-8mm wide around the perimeter where the two sheets are bonded together -- the bag cannot expand at these edges, which is why the cross-section is lenticular rather than circular
- Maximum unconstrained thickness at the center of the midsection: approximately 40-50mm when filled with 2L and lying flat
- The thickness profile tapers from maximum at center to zero at the sealed edges

**Deriving the unconstrained cross-section geometry:**

The bag's width is 190mm. When filled with 2L across a 350mm length, the average cross-sectional area is:

    A = 2,000,000 mm^3 / 350 mm = 5714 mm^2

For a lenticular cross-section (two circular arc segments), with chord width w=190mm and maximum thickness t, the area is approximately:

    A = (2/3) * w * t  (for a reasonable arc)

Solving: t = (3 * 5714) / (2 * 190) = 45mm

This confirms the ~40-50mm unconstrained center thickness at mid-bag. The actual profile is not uniform along the length -- the cap end and sealed top end are thicker relative to their width because the bag narrows there, so liquid pools deeper at those regions.

## 2. Compression from 40-50mm Down to 25-30mm

**What happens to the displaced volume:**

Water is incompressible. When you compress the midsection from ~45mm to 25-30mm, you reduce the cross-sectional area at the center by roughly 35-45%. The 2L of liquid must go somewhere. Three things happen simultaneously:

1. **Lateral widening**: The bag film bulges outward at the sides, making the bag wider. However, this is limited by the heat-sealed perimeter -- the bag cannot stretch significantly beyond its flat 190mm width. The film can only bulge slightly outward between the upper and lower constraint surfaces at the edges.

2. **Longitudinal extension**: Liquid is pushed toward the ends -- both toward the cap and toward the sealed top. The bag gets "longer" in the sense that the inflated region extends further toward the extremities. With the bag mounted at 35 degrees (cap down), gravity assists flow toward the cap end, so the cap end will become the primary overflow zone.

3. **End bulging**: The cap end and sealed end, which are outside the constraint surfaces, will bulge outward (thicker than the constrained 25-30mm) unless those regions are also constrained. The cap end in particular will become a thick, taut pocket of liquid.

**Pressure implications:**

Compressing from 45mm to 27mm creates approximately 0.01-0.03 bar of internal pressure (the film tension is low, so the pressure needed to deform the film is small). This is negligible for structural purposes but enough to make the bag feel firm and taut. The bag will press against the constraint surfaces with roughly 50-150g/cm^2 of force, depending on how tight the constraint is.

**Key design consequence:** The constraint surfaces do NOT need to be the full 350mm length of the bag. In fact, they should leave the cap-end region unconstrained (or with a wider gap) to give displaced liquid somewhere to go. A constraint zone of roughly 200-250mm centered on the midsection is appropriate, with the cap end and sealed end having looser or no constraint.

## 3. Cross-Section Shape of the Constraint Surfaces

**Natural lenticular profile:**

The constrained cross-section is still lenticular, but flatter. With a 25-30mm maximum thickness and 190mm width, the surfaces should follow a gentle convex curve:

- Center gap: 25-30mm
- Edge gap (at the 190mm width boundary): 0mm (the sealed edge sits flat)
- Profile: a shallow circular arc or elliptical arc

For a 27mm center height across 190mm width, the radius of curvature of each constraint surface arc is approximately:

    R = (w/2)^2 / (2 * h/2) + h/4
    R = 95^2 / 27 + 6.75 = 334 + 6.75 = 341mm

This is a very gentle curve -- nearly flat. Each constraint surface has a sag of about 6-7mm from edge to center (half the total 27mm gap, minus the straight-line approximation).

**Simplified approach:** Rather than machining a precise arc, each constraint surface can be a flat plate with raised edges (lips or rails) at the 190mm width boundary. The bag's internal pressure will naturally push the film into a lenticular shape between the two flat plates. The result is a controlled-thickness bag that self-distributes pressure.

**Flat plates vs curved surfaces -- the tradeoff:**

- Flat plates: simpler to print, the bag film conforms naturally, but the contact area with the plates is concentrated at the center (highest pressure point). This is fine for PE/nylon film -- it will not be damaged by flat contact.
- Curved surfaces matching the natural lenticular profile: distribute contact pressure more evenly, reduce local stress on the film. Better if the bag will be compressed tightly (25mm rather than 30mm).
- Recommendation: use flat or very gently curved surfaces. The bag film is robust enough to handle flat contact. A 1-2mm radius on edges and transitions is sufficient to prevent cutting.

## 4. Upper vs Lower Constraint Surface Design

**Lower surface (supports weight):**

- Must support the full weight of the liquid: 2kg (2L of water/syrup at ~1.0-1.05 g/mL)
- At 35 degrees, the normal force on the lower surface is: 2kg * 9.8 * cos(35) = 16N (approximately 1.6 kgf)
- The parallel (sliding) force is: 2kg * 9.8 * sin(35) = 11N -- this is the force trying to slide the bag downhill toward the cap end
- The lower surface should be a smooth, continuous cradle with no gaps or sharp edges
- Shallow raised side rails (5-8mm tall) at the width boundaries prevent the bag from sliding sideways
- A lip or stop at the downhill (cap) end prevents the bag from sliding out
- Surface should be smooth -- PE film slides easily on smooth PLA/PETG, friction coefficient ~0.2-0.3
- Drainage channels or perforations are NOT needed (the bag is sealed, not open)

**Upper surface (prevents bulging):**

- Must resist the upward force from internal pressure when the bag wants to expand beyond 25-30mm
- This force is modest: at 0.02 bar over ~190mm x 250mm, roughly 10N total
- Can be lighter/thinner than the lower surface
- Does NOT need to be a continuous surface -- a series of cross-ribs or a lattice works fine and saves material
- Must have smooth contact surfaces where it touches the bag film
- Should have some compliance or adjustability: if the gap is too tight, it creates unnecessary pressure and risk of pinching at the edges

**Critical difference:** The lower surface cradles and supports; the upper surface only limits maximum thickness. The upper surface can be an open frame with 3-5 cross-ribs spanning the width, while the lower surface should be more continuous to distribute the bag's weight evenly.

## 5. Bag Shape Changes During Fill/Empty Cycle

**Full (2L):**
- Bag is taut throughout, firmly pressed against both upper and lower constraint surfaces in the midsection
- Even thickness profile along the constrained region
- Cap end (low, at 35 degrees) is taut and thick
- Sealed end (high) is taut

**Three-quarters full (1.5L):**
- At 35 degrees, liquid settles toward the cap end
- The upper (sealed) end of the bag begins to collapse -- the two film layers come together and go slack
- The midsection remains mostly filled but may begin to show slight sagging at the high end
- The cap end remains fully pressurized and taut

**Half full (1.0L):**
- The upper half of the bag (the sealed end, which is the high point) is collapsed flat -- the two film layers are in contact with each other, possibly with some trapped air
- The lower half (cap end) is still fully filled and taut
- The transition zone where the bag goes from filled to collapsed moves upward as liquid drains
- The bag's thickness in the collapsed zone drops to essentially 0mm (two layers of 0.1mm film)
- The constraint surfaces in the collapsed zone are no longer in contact with a pressurized bag

**Quarter full (0.5L):**
- Only the bottom quarter (cap end, lowest point at 35 degrees) contains liquid
- The rest of the bag is collapsed flat
- The filled region is taut and may bulge slightly since all 0.5L is concentrated in a short section

**Near-empty:**
- A small pool of liquid remains at the lowest point near the cap
- The pump draws from the cap, so this is ideal -- the last liquid is right at the outlet
- Air pockets can form if the bag film sticks to itself (PE film can be slightly tacky), potentially trapping small amounts of liquid in the upper regions

**Key design implications:**

1. The 35-degree tilt is advantageous -- it ensures liquid always drains toward the cap (outlet) and the bag collapses predictably from the top down
2. The upper constraint surface only contacts the bag when it is more than ~50% full in that region. It does not need to support the bag at low fill levels
3. The lower constraint surface must still support the bag even when partially collapsed -- it acts as a resting surface for the limp film
4. Air management: as liquid is pumped out, air must be able to enter (through the cap/tubing system) or the bag will resist collapsing and the pump will cavitate. The Platypus cap has a small vent or the tubing system must allow air ingress

## 6. Thickness Profile Along Length at 35 Degrees

**Hydrostatic pressure gradient:**

At 35 degrees, the liquid column creates a pressure gradient along the bag's length. For a 350mm bag:

    Height difference = 350mm * sin(35) = 201mm
    Pressure difference = 0.201m * 1000 kg/m^3 * 9.8 = 1970 Pa = 0.020 bar

This is small but measurable. The cap (low) end has 0.020 bar more internal pressure than the sealed (high) end.

**Effect on thickness:**

- The cap end wants to be slightly thicker than the sealed end because of higher internal pressure
- Without constraints, this difference is approximately 2-5mm (cap end at ~47mm, sealed end at ~42mm for a full bag)
- With rigid constraint surfaces, the surfaces enforce uniform thickness -- the pressure difference simply means the bag pushes slightly harder against the constraints at the cap end
- The force difference is negligible for structural design (about 4N total additional force at the cap end)

**Practical impact:** The constraint surfaces can be parallel (same gap everywhere). The hydrostatic gradient is too small to require tapering the gap. However, if the gap is borderline tight (25mm), the cap end will feel slightly more resistant to compression than the sealed end.

## 7. Kinking, Pinching, and Film Damage Risks

**Pinch points at constraint edges:**

The highest risk of kinking or pinching occurs where the constraint surfaces end -- the transition from constrained (25-30mm) to unconstrained (40-50mm). At these boundaries, the bag film must bend sharply, and if the constraint edge is sharp, it concentrates stress on the film.

Mitigation:
- Minimum 3mm radius on all edges of constraint surfaces that contact the bag
- Taper the constraint gap gradually at the entry/exit: over the last 30-50mm of the constraint zone, the gap should widen from 27mm to 40mm+ using a gentle ramp
- Never create a sharp step from constrained to unconstrained

**Side-edge pinching:**

Where the upper and lower constraint surfaces meet at the sides (the 190mm width boundary), the bag's heat-sealed edge passes through. If the gap between upper and lower surfaces at the sides is zero or negative, the seal edge gets crushed.

Mitigation:
- Maintain a minimum 3-5mm gap at the side edges, even if the center gap is 27mm
- The constraint surfaces should be slightly narrower than the bag (170-180mm rather than 190mm), so the sealed edges of the bag overhang freely

**Film fold kinking:**

When the bag is partially empty, the collapsed film above the liquid level can fold on itself. If these folds pass under a constraint surface edge, they create a multi-layer pinch point. PE/nylon film is durable enough to handle this (it will not tear), but repeated folding in the same location could create crease lines over months of use.

Mitigation:
- The upper constraint does not need to press tightly -- a 2-3mm clearance above the expected bag thickness allows folds to form without being crushed
- Smooth surfaces on both constraints reduce friction that could grab and bunch the film

**Adhesion/sticking:**

PE film can stick to smooth PLA or PETG surfaces, especially when wet. This can cause the bag to bunch up or resist sliding during fill/empty cycles.

Mitigation:
- Light texture on constraint surfaces (0.3-0.5mm ribbing or stippling) reduces contact area and prevents adhesion
- Alternatively, a fabric or felt liner between bag and constraint surface prevents sticking entirely -- but adds complexity

## 8. Real-World Analogues and Lessons

**Medical IV pressure infuser bags:**
- Wrap around an IV bag (typically 1000mL) and compress it with an inflatable bladder
- Apply 0.04 bar (300 mmHg) of uniform pressure
- Key lesson: they use a flexible bladder (not a rigid plate) to distribute pressure evenly around the bag. They include a clear window to monitor bag contents. The rigid component is only the outer shell; the inner contact surface is always soft/flexible.

**Hydration bladder frame mounts (Apidura, Hydrapak Seeker):**
- Bladders are designed to fit inside bike frame bags, constrained by the triangular frame
- The Apidura bladder has a uniform 65mm thickness profile rather than tapering to a single seam -- this prevents the bladder from being too thick in the middle and too thin at the edges
- Key lesson: purpose-designed bladders for frame mounting have gusseted sides (box construction) rather than flat-seal construction. The Platypus is flat-seal, so it behaves differently -- more lenticular, less box-shaped.

**Bag-in-box wine/beverage systems:**
- 3L-5L bladders inside cardboard boxes
- The box constrains the bag from all sides
- As wine is dispensed, the bag collapses inward (vacuum-sealed, no air ingress)
- Standard 5L bag dimensions: approximately 330mm x 330mm, pillow-shaped when full
- Key lesson: the box provides rigid constraint on all six sides. The bag collapses from the side farthest from the spigot. No issues with kinking because the box walls are flat and smooth. The rigid box is the simplest effective constraint.

**Hydration pack bladders (CamelBak, Osprey):**
- The Osprey Hydraulics uses a rigid backplate (one constrained side) with the other side free
- CamelBak designs use a baffle down the center to prevent the bladder from ballooning too far from the back
- Key lesson: one rigid surface + one flexible/open surface works well. The rigid surface provides the structural reference; the opposite side is allowed to vary in thickness as the bladder fills/empties.

## 9. Design Recommendations Summary

| Parameter | Recommendation | Rationale |
|-----------|---------------|-----------|
| Center gap | 27mm | Midpoint of 25-30mm target; allows for manufacturing tolerance |
| Constraint zone length | 200-250mm | Leaves cap end and sealed end with 50-75mm of unconstrained overhang each |
| Constraint zone width | 170-180mm | Narrower than 190mm bag width to avoid pinching sealed edges |
| Edge gap (sides) | 5mm minimum | Prevents pinching the heat-sealed perimeter |
| Entry/exit taper | 30-50mm ramp from 27mm to 45mm+ | Prevents kinking at constraint boundaries |
| Edge radius | 3mm minimum on all bag-contact edges | Prevents film cutting and stress concentration |
| Lower surface | Continuous smooth cradle | Supports 2kg bag weight distributed over area |
| Upper surface | Open frame with 3-5 cross-ribs | Only needs to limit max thickness, not support weight |
| Surface texture | 0.3-0.5mm ribbing or stippling | Prevents PE film adhesion to print surface |
| Gap uniformity along length | Parallel (no taper needed) | Hydrostatic gradient too small to matter |
| Cap-end constraint | Loose or absent | Allow displaced liquid to pool at low point |
| Sealed-end constraint | Loose or absent | Allow bag to collapse freely here first |

## 10. Failure Modes to Design Against

1. **Pinching at side edges**: gap too tight at the width boundary crushes the heat seal. Fix: widen constraint to leave sealed edge free.
2. **Kinking at constraint entry/exit**: sharp step in thickness. Fix: taper the gap over 30-50mm.
3. **Bag sliding downhill**: at 35 degrees, 11N pulls the bag toward the cap. Fix: stop/lip at the cap end of the lower cradle, or friction features.
4. **Air pocket trapping**: if air cannot enter as liquid is pumped out, the bag resists collapsing and the pump cavitates. Fix: ensure tubing system allows air ingress at the cap.
5. **Film adhesion to constraint surface**: wet PE sticks to smooth PLA. Fix: textured surface or liner.
6. **Uneven emptying with residual pockets**: film sticks to itself trapping liquid. Fix: smooth lower cradle with no features that could create valleys or channels where liquid pools away from the outlet.
7. **Over-constraint creating excessive internal pressure**: gap too tight adds unnecessary pressure and force on the frame. Fix: 27mm gap is conservative; 30mm is safer if unsure.
