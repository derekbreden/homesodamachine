# Bag Frame -- Conceptual Architecture

## Design Decision (settled)

Two-piece permanent cage per bag. Lower cradle + upper cap snap together around the Platypus 2L bag with ratcheting barbs. No hinge, no latch, no moving parts. Assembled once during build, never opened again. Two identical frames stacked vertically inside the enclosure.

---

## Exploration

### Shape of each half

**Dead end: full-surface lower cradle.** The decision document spec'd a 250 x 180 mm continuous smooth cradle. At 35 degrees with the bag diagonal, this footprint is correct for the bag's midsection, but a full continuous floor is unnecessary. The bag only needs support along its width at a few points -- the PE/nylon film bridges between supports. A continuous floor also traps condensation and prevents airflow around the bag.

**Dead end: curved cradle matching lenticular profile.** The bag-constraint-mechanics research shows the natural lenticular cross-section has a very gentle curve (R = 341mm, sag of ~7mm). Printing a precise curve adds complexity for minimal benefit -- the bag film conforms to flat surfaces just fine. The research explicitly recommends flat or very gently curved surfaces.

**Selected: ribbed tray lower half, open-frame upper half.** The lower half is a perimeter rail with 4-5 longitudinal ribs running the length of the bag zone, creating a tray that supports the bag's weight while allowing air circulation underneath. The upper half is a perimeter rail with 4 transverse cross-ribs that limit maximum thickness. Both halves share the same perimeter footprint and snap together at the perimeter.

### Where the bag cap exits

The bag is mounted at 35 degrees, cap end at the back-bottom of the enclosure. The cap/tubing must exit the frame cleanly without being pinched by the snap closure.

**Selected: open downhill end.** The lower cradle has a U-shaped open end at the cap side (downhill). The upper cap's perimeter rail stops short at the same end, leaving a slot ~35mm wide x 30mm tall for the cap and tubing to pass through. A small stop wall on the lower cradle, set back 15mm from the open end, prevents the bag from sliding downhill (resists the 11N gravity component) while leaving the cap/tubing path clear. The stop wall has a semicircular notch (15mm radius) for the tubing.

### Ratcheting barb geometry

**Dead end: barbs on posts extending from upper cap into holes in lower cradle.** This is what the decision document describes. The problem: posts extending downward from the upper cap require the upper cap to be printed ribs-down (so the posts point up on the print bed), which means the bag-contact surfaces of the ribs are the first layer -- rough. Flipping the print means the posts overhang.

**Selected: barbs integrated into the perimeter rail walls.** Instead of discrete posts, the upper cap's perimeter rail has inward-facing barb ridges along both long sides (2 barbs per side, 4 total). The lower cradle's perimeter rail has matching slots. When the upper cap is pressed down onto the cradle, the barb ridges slide into the slots and click past a ledge. The barb geometry is: 30-degree lead-in ramp, vertical lock face, 1.0mm engagement depth.

This approach is better because: (1) the barbs are part of the perimeter rail wall, which prints vertically with good layer adhesion -- the lock face is parallel to layer lines, maximizing shear strength; (2) no overhanging posts; (3) the upper cap prints ribs-up (bag-contact surfaces face the print bed = smooth first-layer finish); (4) alignment is automatic -- the perimeter rails nest together, self-centering before the barbs engage.

### Enclosure mounting

**Dead end: ledges molded into enclosure interior walls.** The decision document mentions horizontal ledges in the enclosure. This couples the bag frame geometry to the enclosure print, making iteration expensive.

**Selected: tongue-and-groove rails on enclosure side walls.** Two horizontal rails (one per side) are printed as part of each enclosure half's interior. The bag frame's lower cradle has outward-facing tongues along its long edges that slide into these rails from one end. The frame slides in during assembly and is captured when the enclosure halves close. This decouples the frame's cross-section from the enclosure -- only the rail interface matters.

The rails are angled at 35 degrees relative to horizontal, built into the enclosure side walls. The two bag frames mount on parallel rail pairs, one above the other, with ~40mm vertical separation between them (enough for tubing routing between frames).

### Sealed end (uphill) treatment

The sealed end of the bag (folded flat against the front wall per the vision) must be pinned. The bag film folds over itself here and tucks against the front enclosure wall.

**Selected: clip tab on upper cap.** The upper cap's uphill end extends 20mm past the constraint zone as a flat tab with a downward hook. This hook captures the folded bag film against the lower cradle's uphill wall, pinning the sealed end flat. The fold is outside the constraint zone so it does not affect the 27mm gap. The hook has a 3mm radius to avoid creasing the film.

---

## Settled Concept

### 1. Piece count and split strategy

**2 pieces per bag, 4 total.** Horizontal split at the bag's midplane. Lower piece (cradle) supports weight and defines the mounting interface. Upper piece (cap) constrains maximum thickness and locks to cradle permanently. Both pieces share a common perimeter rail footprint (~250 x 180mm). The split is at the widest point of the constrained bag cross-section, which means neither half needs to reach around the bag -- each half simply covers its own side.

### 2. Join methods

**Ratcheting barb ridges on the perimeter rail.** 4 barb points total (2 per long side). The upper cap's rail has inward-facing barb ridges; the lower cradle's rail has matching slot/ledge receivers. 30-degree lead-in, vertical lock face, 1.0mm engagement. Pressing the cap onto the cradle produces 4 sequential clicks as each barb engages. Full engagement leaves zero visible gap between the two perimeter rails. Partial engagement is obvious: a 1-2mm gap is visible and the cap rocks slightly.

Material: PETG. The barbs are loaded in shear parallel to layer lines, which is PETG's strongest printed orientation. 1.0mm engagement on a 2mm-wide barb ridge gives a pull-apart force of ~30-50N per barb (120-200N total), far exceeding the bag's ~10N upward force.

### 3. Seam placement

The horizontal seam between cradle and cap runs around the full perimeter of the frame, at the bag's midplane height (~13.5mm above the cradle floor). This seam is never visible to the user -- the frame is inside a permanently sealed enclosure. The seam is functional, not cosmetic: it is where the barb ridges engage.

The seam is continuous and planar (no jogs or steps), which means both halves sit flat on the print bed and the mating surfaces are first-layer quality (smooth, dimensionally accurate).

### 4. User-facing surface composition

**No user-facing surfaces exist.** The bag frame is assembled once during initial build and then sealed inside the enclosure permanently. The user never sees or touches the frame. All surfaces are functional: bag-contact surfaces are smooth with 0.4mm anti-adhesion ribbing; structural surfaces are standard FDM finish. No aesthetic treatment is needed or appropriate -- material spent on cosmetics here is material wasted.

### 5. Design language

The bag frame is an internal structural component. Its design language is: **minimal, functional, no wasted material.** Open frames and ribs rather than solid walls. Generous radii (3mm minimum) on all bag-contact edges -- not for aesthetics but to prevent film damage. PETG throughout for chemical resistance (food-contact syrup) and creep resistance under sustained bag pressure.

The frame's visual identity, to the extent it has one, comes from its ribbed openwork structure -- it looks like it was designed by an engineer who respected the loads and nothing else.

### 6. Service access strategy

**Tier 1 (never): normal operation.** The frame is sealed inside the enclosure. No access needed. No access provided.

**Tier 2 (rare, years apart): bag replacement.** The enclosure must be pried open (same as any internal service). Once open, the bag frame slides out of its enclosure rails. The permanent barbs are pried apart with a flat tool (screwdriver blade between the perimeter rails). The barbs will deform or break -- this is acceptable. The frame is 2 printed parts costing ~5 hours of print time. If the barbs break, reprint the damaged half. The barb geometry is designed to fail gracefully: the barb ridge snaps off cleanly rather than shattering the rail.

**Tier 3 (once, at build): initial assembly.** Drape bag on cradle, route cap/tubing through open end, press upper cap on until all 4 barbs click. Verify zero gap at all 4 barb points. Slide assembled frame into enclosure rails.

### 7. Manufacturing constraints

**Print bed:** Bambu H2C, 325 x 320 x 320mm single-nozzle. The frame footprint is ~250 x 180mm -- fits with 75mm margin on the long axis and 140mm on the short axis. Both halves fit on the bed simultaneously.

**Orientation:**
- Lower cradle: printed flat, ribs pointing up. The bag-contact surface (rib tops) benefits from being the top surface for smooth finish, but the bottom (first layer against bed) is actually smoother. Since the bag contacts the rib tops, not the floor between ribs, the rib tops are printed surfaces at 0.2mm layer height -- adequate smoothness for PE film contact with 0.4mm anti-adhesion texture applied.
- Upper cap: printed flat, ribs pointing up (away from bed). The bag-contact undersides of the cross-ribs are overhang surfaces, but at only 3mm rib width, the bridging is trivial for PETG.

**Supports:** None required for either piece. The lower cradle is a tray with upward-facing features. The upper cap is a frame with upward-facing ribs. No overhangs exceed 45 degrees.

**Material:** PETG. Selected for: (1) food-safe when printed (no toxic additives in standard PETG filament), (2) superior creep resistance vs PLA under sustained load, (3) better chemical resistance to acidic syrups than PLA, (4) prints well on the H2C without enclosure. PLA would work structurally but may creep at the barb engagement points over years of sustained bag pressure, eventually loosening the frame.

**Layer height:** 0.2mm. Standard for structural parts. The anti-adhesion ribbing (0.4mm pitch) is 2 layers tall -- printable as a surface texture without special settings.

**Infill:** 20% gyroid for the perimeter rails (the only solid volumes). The ribs are single-wall features that do not have infill.

**Estimated print time:** ~2-2.5 hours per cradle, ~1-1.5 hours per cap. Total for 4 pieces: ~7-8 hours.

---

## Key Dimensions Summary

| Parameter | Value |
|-----------|-------|
| Frame footprint (L x W) | ~250 x 180 mm |
| Constraint zone length | 200 mm (centered on midsection) |
| Constraint zone width | 170 mm (bag edges overhang freely) |
| Center gap (cradle floor to cap rib underside) | 27 mm |
| Entry taper (each end) | 40 mm, gap widens from 27 mm to 45 mm |
| Lower cradle height | ~15 mm (8mm rail + 7mm rib height) |
| Upper cap height | ~15 mm (8mm rail + 7mm rib depth) |
| Total closed frame height | ~30 mm (rails nest, gap is internal) |
| Perimeter rail width | 8 mm |
| Barb engagement | 1.0 mm, 4 points |
| Cap exit slot | ~35 mm wide x 30 mm tall, open downhill end |
| Enclosure rail angle | 35 degrees from horizontal |
| Vertical spacing between frames | ~40 mm (center-to-center ~70 mm) |
