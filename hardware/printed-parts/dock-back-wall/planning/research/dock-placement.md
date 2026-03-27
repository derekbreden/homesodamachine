# V1 Cartridge Dock Placement: Front-Bottom Triangular Void

Research into placing the cartridge dock in the triangular void created by diagonal bag mounting in the Vision 1 (diagonal interleave) layout. The diagonal bag slab runs from the top-front corner to the bottom-back corner, creating a wedge-shaped void between the front wall, the floor, and the underside of the lower bag. The cartridge dock sits in this void.

This is a fundamentally different placement than the zone-based research, where the cartridge sat in a horizontal slot at mid-height. Here, the cartridge is at the bottom of the front face, below and in front of the diagonal bags.

---

## 1. Front-Bottom Triangle Geometry

### How the Triangle Forms

Looking at the enclosure from the side (height vs. depth cross-section), the diagonal bag slab creates a right triangle at the front-bottom:

```
FRONT                                              BACK
top ┌──────────────────────────────────────────────────┐
    │  sealed end of bags                              │
    │    ╲                                             │
    │     ╲  bag slab (2 bags stacked)                 │
    │      ╲                                           │
    │       ╲                                          │
    │        ╲                                         │
    │         ╲                                        │
    │  ┌───────╲                                       │
    │  │ CART-  ╲    connector end of bags (low point) │
    │  │ RIDGE   ╲                                     │
    │  │  DOCK    ╲____________________________________│
    └──┴───────────────────────────────────────────────┘
    ▲              ▲
    front wall     triangle hypotenuse = underside of lower bag
```

The triangle vertices are:
- **Bottom-front corner** of the enclosure interior (origin)
- **Point where the bag's lower-front edge meets the front wall** (gives the triangle height)
- **Point where the bag's lower-front edge meets the floor** (gives the triangle depth)

### Geometry Formulas

For bags mounted at angle theta from horizontal, with sealed end at top-front and connector at bottom-back:

The bag slab occupies a parallelogram in the depth-height plane. The lower surface of the bottom bag forms the hypotenuse of our triangle. The key points:

- The bag's connector end (bottom-back) sits near the floor at the back of the enclosure
- The bag's sealed end (top-front) sits near the top of the front wall
- The lower-front corner of the bag slab determines the triangle

For a bag of length L at angle theta, with a stack thickness T (two bags):

The bottom surface of the lower bag is offset inward from the bag centerline by T/2 (half the stack is below center). But since we care about the lower surface of the entire slab, the lower boundary runs parallel to the diagonal, shifted perpendicular to it by T (full stack thickness).

**Coordinate system:** Origin at interior bottom-front corner. X = depth (front to back), Y = height (floor to top).

The bag slab's upper-front point is at (0, H_interior) or nearby. The bag slab's lower-back point is at (D_interior, 0) or nearby. In practice the bag endpoints are constrained by the interior dimensions.

For a bag mounted from corner to corner of the available space, the diagonal angle is determined by the enclosure. But in our case, we specify the angle and compute where the bag lands.

**Bag lower surface line:** If the bag centerline runs at angle theta from horizontal, the lower surface of the slab is displaced perpendicular to the centerline by T/2 (for one bag) or T for the full stack measured from the top surface. Since we want the lower boundary of the bottom bag:

The perpendicular offset from the top-of-slab line to the bottom-of-slab line = T_stack (both bags).

The lower surface line, in our coordinate system where the sealed end is at the top-front:
- The top surface of the top bag starts at approximately (0, H_top) where H_top is near the enclosure ceiling
- The lower surface of the bottom bag is offset perpendicular to the diagonal by T_stack

For the triangle at the front-bottom, we need two values:
- **Triangle height at front wall (x=0):** The height where the lower bag surface intersects the front wall
- **Triangle depth at floor (y=0):** The depth where the lower bag surface intersects the floor

Given:
- Bag length L, stack thickness T_stack, angle theta
- Enclosure interior: W_int x D_int x H_int

If the sealed (top) end of the top bag is anchored at position (x=0, y=H_int) -- the top-front corner -- then the bag centerline descends at angle theta. The connector end is at:
- x_connector = L * cos(theta)
- y_connector = H_int - L * sin(theta)

The lower surface of the bottom bag is parallel to the centerline but offset perpendicular downward-and-forward by T_stack. The perpendicular offset in cartesian coordinates:
- dx = -T_stack * sin(theta) ... (shifts toward front, i.e., negative x)
- dy = -T_stack * cos(theta) ... (shifts downward, i.e., negative y)

So the lower bag surface line passes through:
- Top-front point: (0 - T_stack * sin(theta), H_int - T_stack * cos(theta)) = (-T_stack * sin(theta), H_int - T_stack * cos(theta))

Since x cannot be negative (that's outside the enclosure), the line intersects x=0 at:
- y at x=0: We need the line equation.

The lower bag surface line has slope = -tan(theta) (descending from front to back, same as the bag centerline). It passes through the point:
- (x0, y0) = (-T_stack * sin(theta), H_int - T_stack * cos(theta))

Line equation: y - y0 = -tan(theta) * (x - x0)

At x = 0:
- y_front = y0 + tan(theta) * x0
- y_front = (H_int - T_stack * cos(theta)) + tan(theta) * (-T_stack * sin(theta))
- y_front = H_int - T_stack * cos(theta) - T_stack * sin(theta) * tan(theta)
- y_front = H_int - T_stack * cos(theta) - T_stack * sin^2(theta) / cos(theta)
- y_front = H_int - T_stack * [cos^2(theta) + sin^2(theta)] / cos(theta)
- **y_front = H_int - T_stack / cos(theta)**

At y = 0:
- 0 = y0 + tan(theta) * (x0 - x_floor)
- x_floor = x0 + y0 / tan(theta)
- x_floor = -T_stack * sin(theta) + [H_int - T_stack * cos(theta)] / tan(theta)
- x_floor = -T_stack * sin(theta) + H_int / tan(theta) - T_stack * cos(theta) / tan(theta)
- x_floor = H_int / tan(theta) - T_stack * [sin(theta) + cos^2(theta)/sin(theta)]
- x_floor = H_int / tan(theta) - T_stack * [sin^2(theta) + cos^2(theta)] / sin(theta)
- **x_floor = H_int / tan(theta) - T_stack / sin(theta)**

Or equivalently:
- **x_floor = (H_int - T_stack / sin(theta) * ... )** -- let me simplify.
- x_floor = H_int * cos(theta) / sin(theta) - T_stack / sin(theta)
- **x_floor = (H_int * cos(theta) - T_stack) / sin(theta)**

So the front-bottom triangle dimensions are:
- **Height at front wall** = y_front = H_int - T_stack / cos(theta)
- **Depth at floor** = x_floor = (H_int * cos(theta) - T_stack) / sin(theta)

Wait -- these are the coordinates where the lower bag surface hits the front wall and floor, but the *triangle* is the region BELOW and IN FRONT of the bag surface, bounded by the front wall and floor. The usable triangle is:

- **Usable height (at front wall)** = y_front = H_int - T_stack / cos(theta)

That's the height of the intersection point -- but the triangle extends from the floor (y=0) UP to y_front. So the triangle height IS y_front:

- **Triangle height** = H_int - T_stack / cos(theta)

And the triangle depth (at floor level) = x_floor:

- **Triangle depth** = (H_int * cos(theta) - T_stack) / sin(theta)

These are quite large numbers because the bag surface intersects the front wall quite high up and the floor quite far back. The entire lower-front region of the enclosure is available. Let me verify with a sanity check.

**Sanity check: 1L bags at 45 degrees in 280W x 300D x 400H (interior 272 x 292 x 392):**
- T_stack = 50mm, theta = 45 degrees, H_int = 392mm
- Triangle height = 392 - 50/cos(45) = 392 - 50/0.707 = 392 - 70.7 = **321mm**
- Triangle depth = (392 * cos(45) - 50) / sin(45) = (277.2 - 50) / 0.707 = 227.2 / 0.707 = **321mm**

At 45 degrees the triangle is isoceles, which makes sense. And 321mm is most of the enclosure in both dimensions -- the bag surface only clips the upper-back region. The cartridge has enormous room. This confirms the diagonal interleave concept frees up the front-bottom massively.

### Triangle Dimension Tables

Interior dimensions = exterior - 8mm (4mm walls all sides).

#### 1L Bags (L=280mm, T_stack=50mm) in 280W x 300D x 400H (interior 272 x 292 x 392)

| Angle | Triangle Height (mm) | Triangle Depth (mm) | Hypotenuse Length (mm) | Notes |
|-------|---------------------|---------------------|----------------------|-------|
| 30° | 334 | 593 | 681 | Depth exceeds enclosure (292mm) -- floor intersection is outside. Usable depth = 292mm, height at back wall ~224mm |
| 35° | 331 | 510 | 608 | Depth exceeds enclosure. Usable depth = 292mm |
| 40° | 327 | 436 | 545 | Depth exceeds enclosure. Usable depth = 292mm |
| 45° | 321 | 321 | 454 | Triangle fits entirely inside enclosure |

At shallow angles (30-40 degrees), the lower bag surface intersects the floor BEHIND the back wall of the enclosure, meaning the bag surface never reaches the floor within the enclosure. The entire floor is available, and the triangle is actually a trapezoid bounded by the back wall. The cartridge has access to the full floor depth.

**Revised table -- actual available space within enclosure bounds (depth capped at 292mm):**

| Angle | Height at Front Wall (mm) | Depth at Floor (mm) | Height at Back Wall (mm) | Shape |
|-------|--------------------------|---------------------|-------------------------|-------|
| 30° | 334 | 292 (full) | 224 | Trapezoid (bag doesn't reach floor) |
| 35° | 331 | 292 (full) | 127 | Trapezoid |
| 40° | 327 | 292 (full) | 38 | Nearly triangular (bag almost reaches floor at back) |
| 45° | 321 | 321 (capped to 292) | 0 (bag hits floor at 321mm, beyond back wall at 292) | Still trapezoidal, height at back wall = 392 - (292 * tan(45) + 50/cos(45)) = 392 - (292 + 70.7) = 29mm |

Let me recompute the height at the back wall more carefully. At x = D_int (back wall), the lower bag surface height is:

y_at_back = y_front - tan(theta) * D_int

where y_front = H_int - T_stack / cos(theta)

| Angle | y_front (mm) | y at back wall (mm) | Available at back wall |
|-------|-------------|--------------------|-----------------------|
| 30° | 334 | 334 - 292 * tan(30) = 334 - 168.6 = 166 | 166mm height under bag at back |
| 35° | 331 | 331 - 292 * tan(35) = 331 - 204.4 = 127 | 127mm |
| 40° | 327 | 327 - 292 * tan(40) = 327 - 245.1 = 82 | 82mm |
| 45° | 321 | 321 - 292 * tan(45) = 321 - 292 = 29 | 29mm |

So the available void is a large trapezoid in all cases, with substantial height at the front and decreasing height toward the back. The cartridge sits comfortably in the front portion.

#### 1L Bags (L=280mm, T_stack=50mm) in 280W x 300D x 400H -- Final Table

| Angle | Height at Front (mm) | Height at Mid-depth (146mm) (mm) | Height at Back (mm) | Full Floor Depth? |
|-------|---------------------|--------------------------------|--------------------|--------------------|
| 30° | 334 | 250 | 166 | Yes (292mm) |
| 35° | 331 | 229 | 127 | Yes (292mm) |
| 40° | 327 | 205 | 82 | Yes (292mm) |
| 45° | 321 | 175 | 29 | Yes (292mm) |

**Interpretation:** Even at 45 degrees, the front-bottom void has 321mm of height at the front wall and 175mm at mid-depth. The cartridge (80mm tall in current form) fits trivially. There is no geometric constraint on the cartridge from the triangle -- the void is far larger than needed.

#### 2L Bags (L=350mm, T_stack=80mm) in 280W x 350D x 400H (interior 272 x 342 x 392)

| Angle | Height at Front (mm) | Height at Mid-depth (171mm) (mm) | Height at Back (mm) | Full Floor Depth? |
|-------|---------------------|--------------------------------|--------------------|--------------------|
| 30° | 300 | 201 | 95 | Yes (342mm); y at back = 300 - 342*tan(30) = 300 - 197 = 103. Correction: 103mm |
| 35° | 295 | 175 | 55 | Yes; y at back = 295 - 342*tan(35) = 295 - 239 = 56mm |
| 40° | 288 | 144 | 1 | Yes; y at back = 288 - 342*tan(40) = 288 - 287 = 1mm. Bag barely clears floor at back |
| 45° | 279 | 108 | -63 | No -- bag intersects floor at depth (279/tan45) = 279mm. Usable depth = 279mm |

Recomputing y_front for 2L: H_int - T_stack/cos(theta)
- 30 deg: 392 - 80/0.866 = 392 - 92.4 = 299.6 -> 300mm
- 35 deg: 392 - 80/0.819 = 392 - 97.7 = 294.3 -> 294mm
- 40 deg: 392 - 80/0.766 = 392 - 104.4 = 287.6 -> 288mm
- 45 deg: 392 - 80/0.707 = 392 - 113.1 = 278.9 -> 279mm

**Corrected 2L table:**

| Angle | Height at Front (mm) | Height at Mid-depth (171mm) (mm) | Height at Back (mm) | Depth at Floor (mm) |
|-------|---------------------|--------------------------------|--------------------|---------------------|
| 30° | 300 | 201 | 103 | Full (342mm) |
| 35° | 294 | 174 | 55 | Full (342mm) |
| 40° | 288 | 144 | 1 | Full (342mm) -- bag just touches floor at back wall |
| 45° | 279 | 108 | n/a | 279mm (bag hits floor before back wall) |

**Key finding:** Even with the larger 2L bags and their 80mm stack thickness, the front-bottom void provides 279-300mm of height at the front wall and 144-201mm at mid-depth. The cartridge fits easily regardless of angle in the 30-45 degree range.

### Summary of Triangle Geometry

The front-bottom void is not a tight, constrained triangle -- it is a massive trapezoidal region consuming most of the enclosure volume. The diagonal bag slab only clips the upper-back corner. This means:

1. **The cartridge placement is not geometrically constrained by the triangle.** Any reasonable cartridge envelope fits.
2. **The interesting question is not "does it fit?" but "where exactly in this large void should it go?"** -- which is driven by ergonomics, tube routing, and front panel layout, not by geometric clearance.
3. **The triangle geometry matters more for understanding what ELSE can share this space** -- solenoid valves, flow meters, tube routing channels, drip management.

---

## 2. Cartridge Envelope Optimization

### Current Envelope: 150W x 130D x 80H mm

This was designed for a horizontal zone with tight height budgets. In the triangular void, height is abundant and width is the real constraint.

### Width Analysis

The bags and cartridge must share the enclosure's interior width (272mm). Two configurations:

**A. Cartridge beside bags (side-by-side in width):**

| Bag Type | Bag Width | Remaining Width | Cartridge Fits? |
|----------|-----------|-----------------|-----------------|
| 1L Platy | 152mm | 120mm | No at 150mm. Yes if narrowed to 120mm or less. |
| 2L Platy | 190mm | 82mm | No at 150mm. Requires major redesign to 82mm wide. |

A side-by-side placement forces a narrow cartridge. At 82mm wide (for 2L compatibility), the two Kamoer pumps (68.6mm each) cannot sit side-by-side. They would need to stack vertically (137.2mm tall x 68.6mm wide) -- which conflicts with the current side-by-side pump layout but is now geometrically possible because height is no longer constrained.

**B. Cartridge in front of bags (same width zone, different depth):**

The bags start some distance from the front wall (the sealed end is at top-front, but at lower heights the bag surface is set back from the front). At the cartridge's height (say 0-80mm from the floor), the bag surface is far back:

For 1L at 35 degrees, the bag lower surface at y=80mm is at:
- x = (y_front - 80) / tan(35) = (331 - 80) / 0.700 = 251/0.700 = 359mm

This is past the back wall. The bags are nowhere near the front at cartridge height. The cartridge can use the **full enclosure width** (272mm) because at the floor level, the bags haven't descended that far yet.

**This is the correct configuration.** The cartridge sits on the floor at the front, spanning the full width. The bags are above and behind it. There is no width competition.

### Envelope Options for the Triangular Void

With width no longer constrained (full 272mm available) and height abundant (279-334mm), the cartridge envelope can be optimized purely for internal packaging and ergonomics.

| Option | W x D x H (mm) | Volume (L) | Pump Layout | Pros | Cons |
|--------|----------------|------------|-------------|------|------|
| **A. Current** | 150 x 130 x 80 | 1.56 | Side-by-side, motors along depth | Proven layout, all existing research applies | Taller than needed in new context, wastes width |
| **B. Wider + shorter** | 200 x 130 x 60 | 1.56 | Side-by-side, more spacing between pumps | Lower profile, leaves more height above for bags | Wider footprint on front panel |
| **C. Wider + shallower** | 200 x 100 x 80 | 1.60 | Side-by-side, shorter depth | Shallower insertion = faster swap | Pumps (115.6mm deep) don't fit at 100mm depth |
| **D. Full-width** | 250 x 100 x 60 | 1.50 | Side-by-side with generous spacing | Minimal protrusion, drawer-like form factor | Very wide slot on front panel, harder to seal |
| **E. Compact** | 150 x 130 x 80 | 1.56 | No change | Smallest front panel slot, existing design | No benefit from available space |

**Option C is invalid** -- the pumps are 115.6mm long (motor axis), so depth must be at least 125-130mm.

**Recommended envelope: 150W x 130D x 80H (no change).** Rationale:
- The pumps dictate minimum depth (~130mm) regardless of available space
- Making the cartridge wider provides no internal benefit (pumps are 137mm side-by-side; 150mm already has adequate margin)
- A smaller front panel slot is easier to seal against moisture and dust
- All existing cartridge research (mating face, release plate, cam lever, guide rails) remains valid without modification
- The triangular void has room for the cartridge PLUS additional components (valves, routing) beside or above it

---

## 3. Cartridge Loading and Unloading

### Front Panel Slot Position

The cartridge sits on the floor of the enclosure, at the front. The slot occupies:

- **Height range on front face:** 0mm (floor) to ~84mm (cartridge 80mm + 4mm clearance)
- **Width range:** Centered, ~61mm to 211mm across the 272mm interior (for 150mm-wide cartridge)
- **If lever is included:** Add 40mm above the cartridge slot = 0 to ~124mm

This puts the cartridge slot at the very bottom of the front panel. For comparison, the zone-based layout had the slot at 186-306mm (mid-height).

### Ergonomic Assessment

The user is crouching or kneeling in front of an under-sink cabinet. The enclosure sits on the cabinet floor.

**Advantages of bottom placement:**
- The cartridge slot is at the lowest point, closest to the user's hands when crouching
- Reaching the bottom of the enclosure requires less extension than reaching mid-height
- The user can rest the cartridge on the cabinet floor while aligning it -- no need to hold it at mid-height while aiming
- Gravity assists: if the cartridge is slightly loose during insertion, it settles downward into the slot rather than falling out
- The slot is below the displays and hopper access, keeping the "maintenance zone" separate from the "interaction zone"

**Disadvantages:**
- If the cabinet floor is dirty or wet, the cartridge rests in the mess during the swap
- Less visible than a mid-height slot (the user must look down, not straight ahead)
- If the enclosure is pushed against the back wall, the user must reach past the enclosure's upper portion to access the bottom

**Net assessment:** Bottom placement is ergonomically neutral to slightly positive. The key improvement over mid-height placement is that the user does not need to hold the 820g cartridge at arm's length while aligning tube stubs with fittings. They can slide it along the cabinet floor into the enclosure slot.

### Guide Rail Design

The cartridge slides in on guide rails integrated into the dock floor and/or side walls. For bottom placement:

**Floor rails:** Two parallel rails on the enclosure floor, running front-to-back. The cartridge has matching grooves on its underside. This is the simplest configuration because the cartridge rests on the floor by gravity -- no need for side wall rails to prevent the cartridge from dropping.

**Side wall rails:** Rails on the left and right walls of the cartridge slot. Provides lateral guidance and prevents the cartridge from tilting during insertion. Can be combined with floor rails.

**Recommended: Floor rails + side wall guides.**
- Floor rails (2mm tall, 3mm wide, full slot depth) carry the cartridge weight and provide primary depth guidance
- Side wall guides (1.5mm wide rails, 0.3-0.5mm clearance per side) prevent lateral wobble
- 5mm chamfer on slot entrance for blind insertion

### Retention Mechanism

Once inserted, the cartridge must stay put. Options:

| Mechanism | Complexity | Retention Force | Release Method |
|-----------|-----------|-----------------|----------------|
| **Cam lever (chosen)** | High | 20-40N | Flip lever (drives release plate) |
| **Spring latch** | Low | 5-15N | Push to release, or pull past detent |
| **Magnetic catch** | Low | 3-10N | Pull to overcome magnets |
| **Friction fit (O-ring on rails)** | Very low | 2-5N | Pull to overcome friction |
| **JG collet grip alone** | None (inherent) | ~20N (4 fittings) | Requires collet release |

The collet grip on the tube stubs provides substantial retention force (~5N per fitting x 4 = 20N). The cam lever is needed for simultaneous collet release. The lever also provides the over-center lock that prevents vibration-induced withdrawal.

---

## 4. Fluid Connections

Four bulkhead-mount John Guest 1/4" push-to-connect fittings are installed in the dock back wall. The cartridge's tube stubs (1/4" OD hard nylon, ~30mm protrusion) insert into the fittings as the cartridge slides in. Collets grip automatically on insertion.

**Release in this geometry:** The cam lever on the cartridge front face drives a push rod through the cartridge body to the release plate on the rear face. This mechanism is identical to the zone-based design -- the triangular void placement does not change the internal cartridge mechanics.

The release plate has four stepped bores (8.0/10.5/12.5mm) that engage the JG body ends simultaneously. When the lever is flipped, the plate pushes rearward ~3mm, depressing all four collets. The user then pulls the cartridge forward by the lever handle.

**Geometry-specific note:** In the triangular void, the dock back wall is at the rear of the cartridge slot. With 130mm cartridge depth + 35mm dock back wall = 165mm total from front panel to fitting rear. At floor level in a 292mm-deep enclosure (1L bags at 35 deg), this leaves 127mm behind the fittings for tube routing -- generous.

### Tube Routing: Cartridge to Bags

The cartridge sits at the front-bottom. The bag connectors are at the bottom-back (bags drain downward to the connector end at the low point of the diagonal).

Routing path:
1. Fluid exits the cartridge pump outlets at the rear of the cartridge (dock back wall)
2. Tubes run from the dock fittings rearward and upward along the enclosure floor/back wall
3. Tubes connect to the bag inlet fittings at the bottom-back of the enclosure

| Configuration | Tube Run Length | Dead Volume (2 lines, 6.35mm ID) | Notes |
|---------------|----------------|----------------------------------|-------|
| 1L at 35 deg, 300D | ~200mm | 12.7ml | From dock wall (~165mm from front) to bag connectors (~280mm from front) |
| 1L at 45 deg, 300D | ~180mm | 11.4ml | Bag connectors closer due to steeper angle |
| 2L at 35 deg, 350D | ~250mm | 15.9ml | Longer enclosure, longer runs |
| 2L at 40 deg, 350D | ~220mm | 13.9ml | Moderate |

Dead volume is comparable to the zone-based layout (12.7ml baseline). The tube runs are slightly longer due to the front-to-back routing, but the difference is small (10-25%).

**Routing strategy:** Tubes run along the enclosure floor from the dock wall to the back wall, then turn upward to the bag connectors. A printed channel or clip track on the floor keeps tubes organized and prevents kinking.

---

## 5. Electrical Connections

### Pogo Pin Configuration

The existing design places 3 pogo pins on the dock ceiling contacting flat pads on the cartridge top face. This works identically in the triangular void placement.

**Pin layout:** 3 spring-loaded pogo pins (GND, Motor A+, Motor B+) mounted in the ceiling of the cartridge slot, pressing downward onto 3 nickel-plated brass pads (8mm x 5mm each, 10mm center-to-center) on the cartridge top face.

**Why top-face placement still works:**
- The cartridge slides in along the floor. The slot ceiling is a flat surface directly above.
- Gravity pulls water downward, away from the ceiling-mounted pins.
- The fluid connections (rear face) are physically separated from the electrical contacts (top face).
- Self-cleaning wipe action occurs naturally as the cartridge slides in -- the pin tip drags across the elongated pad.

### Connection Count

| Contact | Function | Max Current |
|---------|----------|-------------|
| GND | Common ground for both motors | ~1.7A |
| Motor A+ | Pump 1 positive, 12V | ~0.85A |
| Motor B+ | Pump 2 positive, 12V | ~0.85A |

**Minimum: 3 contacts.** This is sufficient for the two-pump configuration with shared ground.

**Optional additions:**
- **Cartridge ID pin (4th contact):** A resistor divider on the cartridge could identify the cartridge type or revision to the firmware. Useful if different cartridge variants are introduced later.
- **Temperature sensor (5th-6th contacts):** A thermistor on the cartridge could monitor pump temperature. Not needed for the current design but trivial to add with pogo pins.
- **Recommendation:** Start with 3 contacts. Add a 4th for cartridge ID if the firmware supports it. The pogo pin approach scales trivially -- adding pins costs ~$1-2 each.

### Alignment Tolerance

Pogo pins on oversized pads tolerate 2-3mm of lateral misalignment. The guide rails position the cartridge within ~0.5mm. The tapered alignment pins (if retained) further refine positioning to <0.5mm at the mating face. Electrical contact is effectively guaranteed.

### Moisture Separation

In the triangular void, the electrical contacts (top of cartridge) are above the fluid connections (rear face) and above the enclosure floor. Water from fitting disconnection or condensation drips downward to the enclosure floor, away from the pogo pins. The physical separation is even better than in the zone-based layout because the cartridge is at the very bottom -- there is nothing below it to drip onto the contacts.

The only moisture risk is condensation on the slot ceiling directly above the pogo pins. A small drainage channel molded into the slot ceiling, sloping away from the pin pockets, mitigates this.

---

## 6. Interaction with the Bag Diagonal

### Clearance Between Cartridge and Lower Bag

The cartridge top surface is at approximately 80mm from the enclosure floor. The lower bag surface height at the cartridge's rear edge (x = ~165mm from front, accounting for cartridge + dock):

For 1L bags at 35 degrees (y_front = 331mm):
- y at x=165 = 331 - 165 * tan(35) = 331 - 115.5 = **215.5mm**

Clearance above cartridge at the dock wall: 215.5 - 80 = **135.5mm**

For 2L bags at 35 degrees (y_front = 294mm):
- y at x=165 = 294 - 165 * tan(35) = 294 - 115.5 = **178.5mm**

Clearance: 178.5 - 80 = **98.5mm**

Even in the tightest case (2L bags at 45 degrees), the clearance is:
- y_front = 279, y at x=165 = 279 - 165 * tan(45) = 279 - 165 = 114mm
- Clearance: 114 - 80 = **34mm**

**The bags are nowhere near the cartridge.** Minimum clearance is 34mm (2L at 45 degrees) and typically 100-135mm. There is no interference concern.

### Bag Sag Prevention

Even though the bags are far above the cartridge, the lower bag could sag under the weight of liquid. A full 1L bag weighs ~1kg; a 2L bag weighs ~2kg. The bag is supported at its two endpoints (sealed end at top-front, connector at bottom-back), and liquid weight causes the middle to sag below the straight-line diagonal.

**Sag estimate:** A 1L bag at 35 degrees with 1kg of liquid, supported at endpoints 280mm apart:
- This is a catenary problem, but simplified as a uniform load on a flexible membrane
- Maximum sag at midpoint: approximately 15-25mm below the straight diagonal line (depends on bag stiffness and fill level)
- Even with 25mm of sag, the bag midpoint is still well above the cartridge

**Prevention strategies (for general bag management, not specifically for cartridge clearance):**
1. **Angled shelf/cradle under the bags:** A rigid printed or bent-sheet support surface follows the diagonal angle, preventing sag. The bags rest on this surface rather than hanging freely.
2. **Intermediate support rail:** A single rail at the bag midpoint, running across the width, limits sag to the distance between supports.
3. **Rigid mesh panel:** A lightweight diagonal panel with drain holes supports the bags while allowing airflow and drainage.

**Recommendation:** An angled cradle or shelf is recommended regardless of cartridge clearance, because bag sag creates uneven drainage (liquid pools in the belly rather than flowing to the connector). A rigid cradle under the bags ensures consistent drainage and prevents contact with any components below.

### Tube Routing Path

Tubes route from the cartridge (front-bottom) to the bag connectors (bottom-back):

```
FRONT                                              BACK
    ┌──────────────────────────────────────────────────┐
    │                                                  │
    │         ╲  bags on diagonal cradle            ╲  │
    │          ╲                                     ╲ │
    │           ╲                                     ╲│
    │  CARTRIDGE ╲                            bag conn ╲
    │  ┌────┐     ╲                              ●●   ╲│
    │  │    │══════════════════════════════════►●●     │
    │  │    │  tubes along floor                       │
    │  └────┘                                          │
    └──────────────────────────────────────────────────┘
```

Tubes exit the dock wall, run along the enclosure floor (in a printed channel), and connect to the bag inlets at the bottom-back. Total run: 120-180mm depending on enclosure depth and angle. The tubes are entirely below the bag slab, protected by the floor channel.

---

## 7. Comparison: Triangle vs. Above-Bags vs. Beside-Bags Placement

### A. Cartridge in Front-Bottom Triangle (Vision 1)

**How it works:** Cartridge sits on the floor at the front of the enclosure. Bags are above and behind on a diagonal. Cartridge slot is at the bottom of the front panel.

| Criterion | Assessment |
|-----------|------------|
| Height budget competition | None -- cartridge is below the bags, not competing for vertical space |
| Depth budget | 130mm of ~292mm (1L) or ~342mm (2L). No competition. |
| Width budget | Full enclosure width available (bags are above, not beside) |
| Front-panel access | Bottom of front face. User slides cartridge along cabinet floor. |
| Gravity and drainage | Bags drain downward toward connector (bottom-back). Cartridge is below bags -- any bag leaks drip onto cartridge top, but this is contained within the enclosure. Cartridge fluid connections drain downward to enclosure floor. |
| Tube routing | Floor-level run from front to back. Clean, short, accessible. |
| Ergonomics | User crouches and slides cartridge at floor level. Low effort, low precision needed. |
| Structural role | Cartridge slot can integrate with enclosure floor structure. Dock is a floor-level shelf. |

### B. Cartridge Above Bags (Zone-Based Layout)

**How it works:** Cartridge sits in a horizontal slot at mid-height (186-266mm in the zone layout). Bags are in a horizontal zone below.

| Criterion | Assessment |
|-----------|------------|
| Height budget competition | Direct -- cartridge zone (120mm including lever) competes with electronics zone above and bag zone below |
| Depth budget | Shares full enclosure depth (130mm cartridge of ~242mm total) |
| Width budget | Full enclosure width available |
| Front-panel access | Mid-height on front face. User holds cartridge at arm's length while crouching. |
| Gravity and drainage | Cartridge is above bags. Any cartridge drips fall onto bags (benign -- bags are sealed). |
| Tube routing | Short vertical runs from dock to bags directly below. |
| Ergonomics | Holding 820g at mid-height in a crouching position while aligning tube stubs. More demanding than floor-level. |
| Structural role | Dock is a structural shelf dividing bag zone from electronics zone. |

### C. Cartridge Beside Bags (Side-by-Side)

**How it works:** Cartridge and bags occupy different width zones at the same height and depth.

| Criterion | Assessment |
|-----------|------------|
| Height budget competition | None (shares height with bags rather than stacking) |
| Depth budget | Both need full depth -- no conflict |
| Width budget | Severe constraint -- bags (152-190mm) + cartridge (150mm) = 302-340mm, exceeds 272mm interior. Requires cartridge rotation to 80mm wide or enclosure widening. |
| Front-panel access | Side of front face. Cartridge slot beside bag access. |
| Tube routing | Very short (cartridge is adjacent to bags). Minimal dead volume. |
| Ergonomics | Depends on which side. Acceptable. |
| Structural role | No structural benefit -- neither divides zones. |

### Why Triangle Placement is Preferred for Vision 1

1. **No competition for any dimensional budget.** The cartridge occupies space that nothing else needs (front-bottom). In the zone layout, every millimeter of height is contested between bags, dock, lever, and electronics. In the side-by-side layout, width is the bottleneck. The triangle placement eliminates all dimensional conflict.

2. **Front-accessible at the easiest height.** Floor-level is the most accessible position under a sink because the user can rest the cartridge on the cabinet floor during alignment rather than holding it in the air.

3. **Gravity assists drainage.** Bags drain to the bottom-back (toward the cartridge inlet). The tube run from bag connector to cartridge is downhill or level, ensuring gravity priming of the pump inlets. In the above-bags layout, the pump inlets are above the bags and require suction priming.

4. **Simplifies the enclosure structure.** No mid-height shelf needed to support the dock. The dock is at the floor, which is the strongest structural position (the enclosure floor already supports the entire unit's weight).

5. **Compatible with both 1L and 2L bags without redesign.** The cartridge envelope and position are identical regardless of bag size. Only the bag mounting angle and enclosure depth change.

### When Triangle Placement Does Not Work

1. **Very steep angles (>55 degrees).** At steep angles, the bag surface descends so rapidly that the void becomes a thin sliver. At 60 degrees with 2L bags, the height at mid-depth is only ~80mm -- just barely enough for the cartridge with no room above. However, angles above 50 degrees are already outside the recommended range for other reasons (excessive height consumption).

2. **Very shallow angles (<25 degrees).** The triangle void becomes nearly the entire enclosure (the bags only clip a thin upper-back strip). This is not a problem for the cartridge, but it means the bags are nearly horizontal, which reduces drainage effectiveness and requires a deeper enclosure. This is a bag problem, not a cartridge problem.

3. **Enclosure height under ~300mm.** In a very short enclosure, the bag diagonal is compressed and the triangle void shrinks proportionally. Below ~300mm height, the void at the front wall may be too short for the 80mm cartridge plus clearance. This is unlikely in practice (the minimum enclosure height for 1L bags at useful angles is ~350mm).

4. **If the user needs to see the cartridge slot.** The bottom of the enclosure is the least visible position. Under a sink, the user may not see the slot without crouching low or using a flashlight. Mitigations: LED indicator around the slot, high-contrast color for the cartridge handle, tactile guide rails that make blind insertion feasible.

---

## 8. Open Design Questions

### 8a. Dock Wall Position

The dock back wall (holding fittings and alignment features) is currently at the rear of the cartridge slot. In the triangle placement, this wall could alternatively be:

- **On the enclosure floor** (cartridge drops in from above, fittings on the floor pointing up) -- rejected because this traps water under the fittings
- **On the enclosure ceiling of the cartridge slot** (fittings point down) -- rejected because water drips onto fittings
- **At the rear of the cartridge slot** (current design) -- preferred because fittings are on a vertical wall, any drips fall to the floor (away from fittings), and the insertion motion is horizontal

### 8b. Drip Management

The firmware enforces a mandatory clean cycle before the cartridge can be unlocked. After the clean cycle, the fluid lines contain only water or air -- no flavor concentrate remains. A few drops of water during a swap are inconsequential.

**Mitigation:** A shallow drip tray or channel molded into the enclosure floor, sloping toward a drain hole or absorbent pad, catches any residual water.

### 8c. Solenoid Valve Placement

In the zone-based layout, solenoid valves sit beside the dock on the same shelf. In the triangle placement, valves can go:

- **Beside the cartridge on the enclosure floor:** Plenty of room (the cartridge is 150mm wide in a 272mm enclosure). Valves (typically ~30mm wide each) fit beside the cartridge with margin.
- **Behind the dock wall:** In the space between the dock back wall and the bag connectors. Keeps valves on the same tube run.
- **On the back wall:** Mounted vertically, with tubes running from the dock rearward and then up to the bags.

---

## Sources

- cartridge-envelope.md -- pump dimensions, side-by-side arrangement, depth budget
- mating-face.md -- tube port layout, release plate stepped bores, pogo pin placement
- fitting-alternatives.md -- fitting type survey and JG selection rationale
- diagonal-stacking-geometry.md -- angle sweep tables, corrected bag dimensions, enclosure fit analysis
- diagonal-interleave.md (Vision 1) -- conceptual layout, spatial description
- dock-mounting-strategies.md -- zone-based dock as structural shelf, three-zone architecture
- electrical-mating.md -- pogo pin recommendation, moisture separation, contact specs
- guide-alignment.md -- rail clearances, tapered pin geometry, two-stage alignment
- Kamoer KPHM400 specifications: 115.6 x 68.6 x 62.7mm, 306g, 10W
- Platypus bag dimensions: 1L = 280 x 152mm, 2L = 350 x 190mm
