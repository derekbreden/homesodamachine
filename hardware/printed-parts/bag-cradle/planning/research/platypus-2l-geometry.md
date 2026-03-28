# Platypus 2L Platy Bottle — Physical Geometry

Product: Platypus Platy 2-Liter Flexible Water Bottle
Amazon ASIN: B000J2KEGY
Manufacturer: Cascade Designs (Platypus brand)

Note: The ASIN B000J2KEGY is the **Platy Bottle** (rectangular body, narrow threaded opening at top), not the SoftBottle (hourglass shape, available in 0.5L and 1L only). The Platy Bottle is the 2L model used in this project.


## 1. Overall Dimensions

### Manufacturer-stated (confirmed across Amazon, REI, Trailspace, Garage Grown Gear)

| Dimension | Imperial | Metric |
|-----------|----------|--------|
| Width | 7.5 in | 190 mm |
| Length (height) | 13.8 in | 350 mm |
| Weight (empty) | 1.3 oz | 36–37 g |
| Capacity | 70 fl oz | 2.0 L |

### Packed size when empty (user-measured, CleverHiker)

7.5 x 2.25 x 0.5 inches (190 x 57 x 13 mm) — rolled/folded flat.

### Filled thickness (calculated — no manufacturer or reviewer data exists)

No source provides a direct measurement of thickness when filled. This must be estimated geometrically.

**Model:** Two flat rectangular sheets (190 mm x 350 mm) heat-sealed at the perimeter, inflated to 2L. The cross-section is approximately elliptical (lenticular / lens-shaped).

For an idealized rectangular pillow with elliptical cross-section:

    V = (pi/4) * thickness * width * length
    thickness = 4V / (pi * W * L)
    thickness = 4 * 2,000,000 mm^3 / (pi * 190 mm * 350 mm)
    thickness = 8,000,000 / 208,810
    thickness ≈ 38.3 mm

**Corrections to the ideal model:**
- The heat-sealed seam band (~5–8 mm wide) around the perimeter reduces effective inflatable area
- The cap/spout end narrows the usable width near the top by roughly 30–40 mm
- The film material has some compliance but doesn't stretch significantly — it can't exceed the flat dimensions
- Gravity redistributes water when the bag is not laid flat

**Estimated filled thickness: 40–50 mm (1.6–2.0 inches) at the center when laid flat.**

The 38mm geometric minimum assumes perfect uniform inflation. Real-world behavior pushes it higher because the seam perimeter is non-inflatable, concentrating volume into a smaller area. The bag is also not perfectly rectangular — the corners have radius from the heat seal, further reducing effective area.

**Confidence: MEDIUM.** This is a physics-based estimate, not a direct measurement. The range 40–50 mm should be correct within +/- 5 mm. A physical measurement of the actual bag would confirm.


## 2. Cross-Section Profile

### Front view (width x length plane)
Rectangular with rounded corners. The heat-sealed seam runs the entire perimeter. The cap protrudes from the top center. When filled and laid flat, the silhouette is approximately 190 mm wide x 350 mm tall with ~10 mm corner radii at the seam.

### Side view (thickness x length plane)
Lenticular (lens-shaped). When filled and laid flat on a surface:
- The bottom surface conforms to the flat surface
- The top surface bulges upward in a smooth convex arc
- Maximum thickness is at the center of the bag
- Thickness tapers to zero at the heat-sealed edges

### Cross-section (width x thickness plane, at mid-height)
**Approximately elliptical.** The cross-section of a pressurized flexible pouch between two flat sheets is close to an ellipse, with:
- Major axis ≈ 190 mm (the full width)
- Minor axis ≈ 40–50 mm (the filled thickness)

Under gravity (bag laid flat), the bottom half flattens slightly against the support surface, making the actual shape closer to a **half-ellipse on top of a flat bottom** rather than a symmetric ellipse. This is the natural resting shape and the shape a cradle should match.

### How thickness varies from center to edge
- Center (mid-width, mid-height): maximum thickness, ~40–50 mm
- Moving toward any edge: thickness decreases smoothly, reaching zero at the heat-sealed seam
- The transition is smooth and continuous — no sharp changes
- Near the cap end (top ~30 mm): thickness decreases as the bag narrows to the rigid spout


## 3. Cap / Outlet Geometry

### Cap type
Threaded closure cap (screw-on/screw-off). The product ships with a simple polypropylene closure cap. A push-pull sport cap (polypropylene/polyethylene) is available separately.

### Thread standard
**28mm thread diameter** — this is a widely-used narrow-mouth hydration standard. Compatible with Sawyer filters, Platypus drink tubes, and other 28mm threaded accessories. Thread pitch: 5/32 inch.

### Cap dimensions (from Amazon listing for push-pull cap accessory)
1.2 x 1.2 x 1.0 inches (30 x 30 x 25 mm)

### Spout / collar
The cap threads onto a rigid polyethylene spout that is heat-welded to the top center of the bag. The spout:
- Is approximately 28 mm outer diameter at the thread
- Has a short rigid collar (~15–20 mm tall) that transitions to the flexible film
- Is located at the **top center** of the rectangular bag
- The transition from rigid spout to flexible film is a heat-sealed joint

### Spout position
Centered on the short (190 mm) dimension, at the very top of the long (350 mm) dimension.


## 4. Material and Flexibility

### Film construction
- **Triple-layer laminate:** nylon / polyethylene / nylon (or similar multi-layer)
- Inner layer: food-grade polyethylene (taste-free, BPA/BPS/phthalate-free)
- Outer layer: nylon (abrasion and puncture resistance)
- The film does not stretch significantly — it is flexible but not elastic

### Stiffness when filled
- Described by reviewers as "squishy and jiggly"
- Requires two hands to drink from when full (no structural rigidity)
- Can stand upright when filled (base expands enough for stability on a flat surface)
- Does NOT hold its shape against lateral forces — it deforms readily
- **The bag absolutely needs external support** in any orientation other than standing upright on a flat surface

### Seam construction
- Heat-welded (RF welded) perimeter seam
- Seam band is approximately 5–8 mm wide
- This is the primary structural join and the most likely failure point after extended use
- A reviewer noted the seam as the main durability concern

### Durability reference
Survived a 12-foot drop onto concrete with no damage. Ruptured after two baseball bat strikes. The film is tough but not rigid.


## 5. Behavior When Tilted

### Liquid redistribution
When tilted 30–45 degrees from horizontal, liquid redistributes immediately to the lowest point. The bag is essentially a flexible membrane — it has no internal structure to resist flow. Water moves freely inside.

### Cross-section changes
- The upper portion (now higher) thins as water drains down
- The lower portion (now lower) bulges as water accumulates
- The overall shape becomes asymmetric: thick at the bottom, thin at the top
- At 45 degrees, the bottom third of the bag may contain most of the liquid

### Weight concentration
All weight concentrates at the lowest point. For the project's intended mounting (cap at back-bottom, top of bag pinned to front wall, bag tilted diagonally), this means:
- Weight concentrates near the cap end (back-bottom)
- The sealed end (pinned to front wall) carries little weight
- The cradle must support the full 2 kg (4.4 lb) of water weight primarily at the low point

### Implications for cradle design
The cradle must:
1. Support the bag's full weight at the low (cap) end
2. Prevent the bag from sliding downward
3. Match the bag's cross-section at the heavy end (where it's thickest)
4. Allow the bag to thin naturally toward the top without constraining it
5. Not pinch or kink the spout area — the tubing connects here


## 6. Top vs Bottom of the Bag

### Cap end (bottom in our mounting orientation)
- Rigid spout protrudes ~15–20 mm
- Stiffest part of the bag due to the spout weld
- When filled and tilted, this end is heaviest
- The spout creates a small non-inflatable zone (~30 mm diameter) around it
- Tubing connects here — must remain accessible and un-kinked

### Sealed end (top in our mounting orientation)
- Fully flexible — no rigid elements
- Heat-sealed edge with the same ~5–8 mm seam band
- Thinnest part when bag is tilted (liquid drains away)
- Can be pinned flat against a wall with minimal force
- Slightly rounded corner profile from the heat seal

### Shape difference
The cap end has a local stiffening effect from the rigid spout. The sealed end is uniformly flexible. Otherwise the bag is symmetric about its long axis — left and right sides are identical.


## 7. Summary Dimensions for Cradle Design

| Parameter | Value | Source |
|-----------|-------|--------|
| Bag width | 190 mm | Manufacturer spec |
| Bag length | 350 mm | Manufacturer spec |
| Filled thickness (center, laid flat) | 40–50 mm | Calculated estimate |
| Cap thread diameter | 28 mm | Industry standard, confirmed |
| Cap outer diameter | ~30 mm | Amazon listing |
| Spout collar height | ~15–20 mm | Estimated from photos |
| Seam band width | ~5–8 mm | Estimated from reviews/photos |
| Bag weight empty | 37 g | Manufacturer spec |
| Bag weight filled (water) | ~2,037 g | Calculated (2L water + bag) |
| Film material | Nylon/polyethylene laminate | Manufacturer spec |

### What still needs physical measurement
- **Filled thickness** — the 40–50 mm estimate should be verified with the actual bag and a ruler
- **Spout collar exact height and diameter** — measure the rigid portion
- **Seam band exact width** — measure at several points around the perimeter
- **Corner radii** — measure the heat-seal corner rounding
- **Cross-section profile under gravity** — lay the filled bag on a flat surface and trace or photograph the side profile to confirm elliptical vs flattened-bottom shape
