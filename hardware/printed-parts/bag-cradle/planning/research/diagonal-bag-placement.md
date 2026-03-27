# Vision 1: Diagonal Bag Placement and Enclosure Dimensions

This document analyzes the diagonal interleave layout where bags stretch from the top-back wall to the bottom-front area of the enclosure, and other components occupy the triangular voids created by that diagonal slab. The cartridge sits in the front-bottom triangular void. Electronics occupy the top-back void.

**Critical design facts held throughout this analysis:**
- Bags are permanent fixtures, installed at manufacturing. The user never touches them. Refilling is via hopper/funnel at top.
- The cartridge goes in the front-bottom triangle, not above the bags.
- Depth is unconstrained. Under-sink cabinets have 480-510mm of usable depth. 300mm or 350mm costs nothing in compatibility.
- Corrected bag dimensions: Platy 1L = 280mm long x 152mm wide, 25mm thick per bag, 50mm stacked. Platy 2L = 350mm long x 190mm wide, 40mm thick per bag, 80mm stacked (at center -- less at ends).
- Cartridge envelope: 150W x 130D x 80H mm (standard orientation). Rotated: 80W x 150D x 130H mm.

**Critical correction: bag shape is lens-shaped, not rectangular.**

Real Platypus bags are not constant-thickness rectangles. They are lens-shaped / teardrop-shaped pouches. The thickness varies along the length:

| Position along bag | 1L per bag | 1L stacked | 2L per bag | 2L stacked |
|-------------------|-----------|-----------|-----------|-----------|
| Sealed end (top, 0%) | ~1mm | ~2mm | ~1mm | ~2mm |
| 25% along length | ~8mm | ~16mm | ~15mm | ~30mm |
| Center (50%) | ~25mm | ~50mm | ~40mm | ~80mm |
| 75% along length | ~15mm | ~30mm | ~25mm | ~50mm |
| Cap/connector end (100%) | ~10mm | ~20mm | ~15mm | ~30mm |

The sealed end is flat heat-sealed film -- essentially 1mm thick. The center bulge is where the maximum thickness occurs. The bag has NONE of the four corners that a rigid rectangle would have. The rigid-body rectangle formula `L cos(theta) + T sin(theta)` overstates depth significantly because it treats the bag as a constant-thickness slab across the entire length.

For the detailed depth derivation with actual bag shape, see `2l-bags-at-300mm-depth.md`. For the visual comparison of rigid-body vs actual bag envelope, see `2l-rigid-body-geometry.svg`.

---

## 1. Geometry of Diagonal Bag Placement

### 1a. Coordinate System and Orientation

```
    FRONT WALL                          BACK WALL
    (depth=0)                           (depth=D)

    height=H +------------------------------+
              |  *  sealed end              |
              |   \  (top-back)             |
              |    \                        |
              |     \  BAG SLAB             |
              |      \  (angle theta)       |
              |       \                     |
              |        \                    |
              |         \                   |
              |          \                  |
              |           *  connector end  |
    height=0  +------------------------------+
              depth=0                  depth=D
```

Bags stretch from the **top-back** corner (sealed end pinned to back wall, high) to the **bottom-front** area (connector end, low). The angle theta is measured from horizontal. The connector is at the lowest point, so gravity pulls liquid toward the outlet.

### 1b. Bounding Box Formulas

**Rigid-body model (rectangular cross-section):**

For two stacked bags modeled as a constant-thickness rectangle at angle theta from horizontal:

- **Depth consumed** = L x cos(theta) + T_stack x sin(theta)
- **Height consumed** = L x sin(theta) + T_stack x cos(theta)

Where L = bag length, T_stack = combined maximum thickness of two bags.

**Actual bag shape model (lens-shaped cross-section):**

Real bags are lens-shaped. The sealed end is flat film (~2mm stacked) and the thickness varies continuously, reaching maximum only at the center. When tilted, the actual depth envelope is significantly less than the rigid-body prediction because:

1. The sealed end contributes almost zero thickness projection (it is flat film pinned to the wall).
2. The thickness at any point along the bag is much less than the center maximum.
3. The bag has no "corners" -- the envelope is a smooth curve, not a rectangle.

The rigid-body model overstates depth by approximately 37mm at 35 degrees for 2L bags. The actual depth must be computed by integrating the lens-shaped profile along the bag length. See `2l-bags-at-300mm-depth.md` for the full derivation.

### 1c. Front-Bottom Triangle Geometry

The front-bottom triangular void is bounded by the front wall, the floor, and the lower surface of the bottom bag. The bag slab is positioned so its connector end (lower-front corner) sits near the floor toward the front of the enclosure.

The lower surface of the bag slab forms a line from:
- **Back-top**: (depth = interior_D, height = H_bag) -- sealed end pinned to back wall
- **Front-lower**: near the floor toward the front -- connector end

At any depth d from the front wall, the available height in the front-bottom void follows from the bag's lower surface geometry. When the enclosure is deeper than the bag's bounding box, there is a gap between the back wall and the bag's sealed end (or between the front wall and the connector end, depending on mounting), providing additional clearance for component placement.

### 1d. Angle Sweep: Platy 1L (L=280mm, T_stack=50mm)

1L bags are also lens-shaped, but the effect is less dramatic since they are thinner (25mm per bag vs 40mm). The rigid-body overstatement is smaller but still present.

| Angle | Rigid-Body Depth | Actual Shape Depth (est.) | Rigid-Body Height | Actual Shape Height (est.) |
|-------|-----------------|--------------------------|-------------------|---------------------------|
| 15    | 283             | ~270                     | 121               | ~118                      |
| 20    | 280             | ~266                     | 143               | ~139                      |
| 25    | 275             | ~260                     | 164               | ~159                      |
| 30    | 267             | ~252                     | 183               | ~177                      |
| 35    | 258             | ~243                     | 202               | ~195                      |
| 40    | 247             | ~232                     | 218               | ~211                      |
| 45    | 233             | ~219                     | 233               | ~225                      |
| 50    | 218             | ~205                     | 247               | ~239                      |
| 55    | 202             | ~190                     | 258               | ~250                      |
| 60    | 183             | ~173                     | 267               | ~260                      |
| 65    | 164             | ~156                     | 275               | ~269                      |
| 70    | 143             | ~137                     | 280               | ~275                      |
| 75    | 121             | ~117                     | 283               | ~279                      |

All values in mm. The "Actual Shape Depth" estimates account for the lens-shaped profile but are approximate for 1L -- the correction is smaller (~10-15mm) than for 2L bags because 1L bags are thinner.

### 1e. Angle Sweep: Platy 2L (L=350mm, T_stack=80mm)

| Angle | Rigid-Body Depth | Actual Shape Depth | Rigid-Body Height | Actual Shape Height |
|-------|-----------------|-------------------|-------------------|---------------------|
| 15    | 359             | ~325              | 168               | ~158                |
| 20    | 356             | ~320              | 195               | ~183                |
| 25    | 351             | ~314              | 220               | ~207                |
| 30    | 343             | ~306              | 244               | ~230                |
| 35    | 333             | ~296              | 266               | ~252                |
| 40    | 320             | ~285              | 286               | ~272                |
| 45    | 304             | ~272              | 304               | ~290                |
| 50    | 286             | ~257              | 320               | ~307                |
| 55    | 266             | ~241              | 333               | ~322                |
| 60    | 244             | ~223              | 343               | ~335                |
| 65    | 220             | ~205              | 351               | ~345                |
| 70    | 195             | ~185              | 356               | ~352                |
| 75    | 168             | ~163              | 359               | ~357                |

The rigid-body model overstates depth by ~37mm at 35 degrees. The corrected actual-shape depth of ~296mm at 35 degrees is only 4mm over the 292mm interior of the 300mm-deep enclosure -- and with back-wall mounting (see Section 3), the effective depth drops further to ~267mm.

### 1f. Key Geometric Observations

1. **Depth and height are symmetric at 45 degrees.** Below 45 degrees, bags consume more depth than height. Above 45 degrees, vice versa. Since depth is cheap and height is expensive, angles below 45 degrees are generally preferred.

2. **The front-bottom triangle grows taller as the angle increases.** At 35 degrees, the 1L triangle is ~155mm tall at the front wall (actual shape) -- enough for the cartridge (80mm) plus its lever (40mm). At 35 degrees for 2L, the triangle is ~195mm tall -- even more generous.

3. **The rigid-body model significantly overstates depth for 2L bags.** The ~37mm overstatement at 35 degrees is the difference between "doesn't fit" and "fits with margin." The actual lens-shaped profile must be used for depth-critical decisions.

4. **1L bags are also lens-shaped but the correction is smaller.** At ~10-15mm overstatement, the rigid-body model is conservative but not dangerously wrong for 1L bags. The 1L bags fit easily in the 300mm enclosure regardless of which model is used.

5. **The T_stack penalty.** Stacking two bags adds T_stack x sin(theta) to depth and T_stack x cos(theta) to height in the rigid-body model. In reality, the stacking penalty is less because the bags nest together somewhat -- the lens shapes interlock rather than stacking as rigid blocks. The actual penalty is ~60-70% of the rigid-body prediction.

---

## 2. Enclosure Dimension Analysis

Interior dimensions = exterior - 8mm per axis (4mm walls on each side).

### 2a. Enclosure A: 280W x 300D x 400H (Standard)

**Interior: 272W x 292D x 392H**

#### 1L Bags (L=280, T_stack=50)

All 13 angles (15-75 degrees) fit in both depth and height using either the rigid-body or actual-shape model. The 1L bags never exceed 283mm rigid-body depth (or ~270mm actual), both well within the 292D interior.

| Angle | Rigid-Body Depth | Actual Depth (est.) | Depth Margin | Bag Height (actual) | Top-Back Void Height |
|-------|-----------------|--------------------|--------------|--------------------|---------------------|
| 25    | 275             | ~260               | ~32          | ~159               | ~233                |
| 30    | 267             | ~252               | ~40          | ~177               | ~215                |
| 35    | 258             | ~243               | ~49          | ~195               | ~197                |
| 40    | 247             | ~232               | ~60          | ~211               | ~181                |
| 45    | 233             | ~219               | ~73          | ~225               | ~167                |
| 50    | 218             | ~205               | ~87          | ~239               | ~153                |

**Sweet spot: 30-40 degrees.** The cartridge fits comfortably in the front-bottom zone. The top-back void has 181-215mm of height for electronics (only ~40mm needed). Every angle from 25 to 75 degrees works with the actual bag shape, with generous margins throughout.

#### 2L Bags (L=350, T_stack=80)

**2L bags fit in this enclosure with the corrected bag shape model and back-wall mounting.**

The rigid-body model predicted 333mm depth at 35 degrees, exceeding the 292mm interior by 41mm. This led to the incorrect conclusion that 2L bags could not work. However:

- The actual-shape depth at 35 degrees is ~296mm (only 4mm over the 292mm interior).
- With back-wall mounting (sealed end pinned flat to back wall), the effective depth drops to ~267mm, leaving **25mm margin** in the 292mm interior.

See Section 3 for the back-wall mounting approach.

| Angle | Rigid-Body Depth | Actual Shape Depth | Back-Wall Mounted Depth | Depth Margin (292mm) | Bag Height (actual) | Top-Back Void Height |
|-------|-----------------|-------------------|------------------------|---------------------|--------------------|--------------------|
| 30    | 343             | ~306              | ~279                   | ~13                 | ~230               | ~162               |
| 35    | 333             | ~296              | ~267                   | ~25                 | ~252               | ~140               |
| 40    | 320             | ~285              | ~256                   | ~36                 | ~272               | ~120               |
| 45    | 304             | ~272              | ~246                   | ~46                 | ~290               | ~102               |

**At 35 degrees with back-wall mounting: effective depth ~267mm, margin ~25mm.** This is a comfortable fit. The top-back void at ~140mm provides ample room for electronics.

**At 30 degrees: margin is only ~13mm.** Tight but potentially workable with careful tolerancing.

**At 40-45 degrees: depth margins are generous (36-46mm) but height consumption increases**, reducing the top-back void to 102-120mm. Still adequate for electronics.

**Recommended: 35 degrees for 2L bags in this enclosure.** Best balance of depth margin and height economy.

### 2b. Enclosure B: 280W x 350D x 400H (2L Optimized)

**Interior: 272W x 342D x 392H**

#### 1L Bags

All angles fit easily. The 50mm extra depth over Enclosure A creates enormous front gaps and margins.

| Angle | Actual Depth (est.) | Depth Margin | Top-Back Void Height |
|-------|--------------------|--------------|--------------------|
| 25    | ~260               | ~82          | ~233               |
| 30    | ~252               | ~90          | ~215               |
| 35    | ~243               | ~99          | ~197               |
| 40    | ~232               | ~110         | ~181               |
| 45    | ~219               | ~123         | ~167               |

**Sweet spot: 25-35 degrees.** Shallower angles are viable here because the deeper enclosure provides ample room.

#### 2L Bags

With the actual bag shape (and without even needing back-wall mounting), 2L bags fit starting at 35 degrees with generous margins.

| Angle | Rigid-Body Depth | Actual Shape Depth | Depth Margin (342mm) | Bag Height (actual) | Top-Back Void Height |
|-------|-----------------|-------------------|---------------------|--------------------|--------------------|
| 30    | 343             | ~306              | ~36                 | ~230               | ~162               |
| 35    | 333             | ~296              | ~46                 | ~252               | ~140               |
| 40    | 320             | ~285              | ~57                 | ~272               | ~120               |
| 45    | 304             | ~272              | ~70                 | ~290               | ~102               |

With back-wall mounting, margins increase by an additional ~29mm. This enclosure provides enormous margin for 2L bags.

**Sweet spot: 35-40 degrees.** At 35 degrees, depth margin is 46mm (or ~75mm with back-wall mounting). The top-back void is 140mm. This is a very comfortable fit.

### 2c. Enclosure C: 280W x 300D x 380H (Shorter for Deep-Sink Compatibility)

**Interior: 272W x 292D x 372H**

#### 1L Bags

Same depth fit as Enclosure A (292mm interior). The reduced height (372mm vs 392mm) cuts 20mm from the top-back void.

| Angle | Bag Height (actual) | Top-Back Void Height |
|-------|--------------------|---------------------|
| 30    | ~177               | ~195                |
| 35    | ~195               | ~177                |
| 40    | ~211               | ~161                |
| 45    | ~225               | ~147                |

Still very comfortable for 1L bags. The top-back void is 147-195mm -- far more than the ~40-50mm needed for electronics.

**Verdict: This enclosure works well for 1L bags, giving up 20mm of headroom for better compatibility with deep sinks.** Angles 30-45 degrees all work.

#### 2L Bags

With back-wall mounting and corrected bag shape, 2L bags can fit here too, though margins are tighter than Enclosure A due to the reduced height.

| Angle | Back-Wall Mounted Depth | Depth Margin | Bag Height (actual) | Top-Back Void Height |
|-------|------------------------|--------------|--------------------|--------------------|
| 35    | ~267                   | ~25          | ~252               | ~120               |
| 40    | ~256                   | ~36          | ~272               | ~100               |
| 45    | ~246                   | ~46          | ~290               | ~82                |

**At 35 degrees: fits with 25mm depth margin and 120mm top-back void.** Workable but the reduced height leaves less room for electronics compared to the 400H enclosures.

### 2d. Enclosure D: 300W x 350D x 400H (Wider for 2L Side Clearance)

**Interior: 292W x 342D x 392H**

The extra 20mm of width (292mm vs 272mm) helps with 2L bag clearance and tubing routing.

#### 1L Bags

Identical depth/height fit to Enclosure B (same D and H). The extra width provides 292 - 152 = 140mm beside the bags. The cartridge in standard orientation (150mm wide) still doesn't fit beside the bags (152 + 150 = 302 > 292), but the rotated cartridge (80mm wide) fits easily (152 + 80 = 232 < 292, 60mm spare).

#### 2L Bags

Same depth/height performance as Enclosure B. The width picture changes:

- 2L bag (190mm) + cartridge standard (150mm) = 340mm -- doesn't fit beside (340 > 292)
- 2L bag (190mm) + cartridge rotated (80mm) = 270mm -- fits beside (270 < 292, 22mm spare)

**The extra width provides 102mm beside the 2L bags (292 - 190 = 102mm).** This is useful for tubing routing along the side walls. In the 272mm enclosure, there's only 82mm beside 2L bags -- tighter but still workable.

**Verdict: The extra 20mm of width is a comfort margin, not a necessity. It helps with tubing routing and assembly access but doesn't unlock any configurations that Enclosure B can't handle.**

### 2e. Summary Matrix

Viable angles where bags fit AND the cartridge (130D x 80H) fits in the front-bottom zone. Uses actual bag shape model; back-wall mounting noted where applicable.

| Enclosure | 1L Viable Angles | 1L Best Angle | 2L Viable Angles | 2L Best Angle |
|-----------|-----------------|---------------|------------------|---------------|
| 280x300x400 | 25-75          | 30-40         | 30-45 (back-wall mounted) | 35 |
| 280x350x400 | 25-75          | 25-35         | 30-50            | 35-40         |
| 280x300x380 | 25-75          | 30-40         | 35-45 (back-wall mounted) | 35 |
| 300x350x400 | 25-75          | 25-35         | 30-50            | 35-40         |

---

## 3. Back-Wall Mounting and Profiled Cradle

### 3a. Back-Wall Mounting Principle

The sealed end of a Platypus bag is flat heat-sealed film -- essentially 1-2mm thick even when stacked. When the sealed end is pinned flat against the back wall of the enclosure, it contributes almost zero depth projection. The cap/connector end, at the front-bottom position, is pulled forward by gravity and the weight of the liquid.

This mounting approach exploits the lens-shaped bag profile:

- **Back wall (sealed end):** Pinned flat. The bag lies flush against the wall at the top. Zero depth contribution from the sealed end's "thickness."
- **Mid-length:** The bag bulges outward from the wall as the thickness increases. The maximum bulge (~80mm stacked for 2L) occurs at the center of the bag.
- **Front (connector end):** The bag tapers back down to ~30mm stacked at the cap, then the connector hardware itself.

Gravity and liquid weight position the bag naturally -- the heavy center sags into the cradle, the flat sealed end stays against the wall, and the connector end hangs at the lowest point.

### 3b. Effective Depth with Back-Wall Mounting

With back-wall mounting at 35 degrees for 2L bags:

- The sealed end adds ~0mm to depth (it is flat against the back wall).
- The center bulge projects forward, but because the bulge is smooth and tapered (not a sudden rectangular step), the actual depth envelope follows a gentle curve.
- Effective depth: ~267mm, compared to ~296mm for the free-standing actual shape or ~333mm for the rigid-body model.
- In a 292mm interior, this leaves **~25mm margin**.

The depth savings from back-wall mounting come from eliminating the thickness projection at the sealed end and reducing it near the sealed end where the bag is thin.

### 3c. Profiled Cradle Design

A 3D-printed profiled cradle supports the bag pair from underneath for the full diagonal length. The cradle is contoured to match the lens-shaped bag cross-section at each point along its length:

- **Near sealed end:** Cradle channel is nearly flat (2-5mm deep). The bags are thin here.
- **At 25% length:** Channel depth ~15mm. The bags begin to bulge.
- **At center (50%):** Channel depth ~40mm. Maximum bag thickness. The cradle is deepest here.
- **At 75% length:** Channel depth ~25mm. Bags taper toward the connector.
- **Near connector end:** Channel depth ~15mm. Constrained by cap diameter.

The cradle provides continuous support along the entire bag length, preventing sag and ensuring the bags maintain their predicted envelope. It also acts as a positioning fixture during manufacturing -- the bags drop into the profiled channel and are held at the correct angle and position.

The cradle can be printed as a single piece (for bags up to ~280mm) or as two interlocking halves (for 350mm 2L bags that exceed typical print bed dimensions).

### 3d. Mounting Philosophy

Because bags are permanent fixtures installed during manufacturing, mounting can be robust and non-user-serviceable. There are no constraints around user replacement, tool-free access, or bag swapping. The mounting system can use screws, adhesive, welded brackets, permanent clips -- whatever provides the best support.

### 3e. Mount Points

**Top mount (sealed end, back-upper position):**
- The sealed end of the bag is a heat-sealed seam, typically 10-15mm wide.
- Pinned flat against the back wall, near the top of the enclosure.
- The flat film is clamped or adhesive-bonded to the wall surface. Since the sealed end is just flat film, it conforms naturally to the wall.

**Bottom mount (connector end, front-lower position):**
- The connector end has a 28mm threaded cap where the dip tube attaches.
- Positioned near the floor toward the front of the enclosure.
- The connector must be secured firmly because the fluid line connects here. Any movement risks disconnecting tubing.
- This is the low point -- gravity pulls all liquid here, so the full weight of a loaded bag hangs from this mount.

### 3f. Weight Analysis

A full 2L bag weighs approximately 2.0-2.2 kg (concentrate is slightly denser than water). A 1L bag weighs about 1.0-1.1 kg. Two stacked full bags = 2.0-2.2 kg for 1L, 4.0-4.4 kg for 2L.

At a 35-degree angle, the force components on the lower mount point are:
- Along the bag (tension): F_parallel = m x g x sin(35) = 2.2 x 9.8 x 0.574 = 12.4 N (for one 2L bag)
- Perpendicular to bag (sag force): F_perp = m x g x cos(35) = 2.2 x 9.8 x 0.819 = 17.7 N

The profiled cradle absorbs the perpendicular sag force entirely, distributing it across the full bag length rather than concentrating it at the mount points. The tension component is handled by the end mounts.

### 3g. Mounting for Two Stacked Bags

Two bags stack perpendicular to the incline surface within the profiled cradle. The lower bag rests in the cradle channel. The upper bag rests on top of the lower bag. A thin separator (1-2mm PETG sheet) between the bags prevents them from sticking or interfering with each other's collapse.

The cradle channel depth accommodates both bags at each cross-section point. At the center (deepest point), the channel is ~40mm deep -- enough for one bag's maximum thickness. The second bag sits above, adding another ~40mm. The total stack at center is ~80mm, tapering to ~2mm at the sealed end.

### 3h. Bag Flexibility and Deformation

Platypus bags are flexible pouches. When full, they're relatively rigid due to internal liquid pressure. As they drain, the bag collapses from the sealed end (high) toward the connector end (low). On a diagonal mount:

- **Full bag:** Essentially rigid, conforms to the cradle shape. No deformation concern.
- **Half-full bag:** The upper half collapses flat against the lower half. The lower half remains pressurized by the remaining liquid. The bag shortens along the incline but the weight concentrates at the lower mount.
- **Nearly empty bag:** The bag is mostly collapsed flat. Only a small puddle remains at the connector end. Minimal weight, minimal sag.

The worst-case sag occurs at full capacity. As the bag drains, sag decreases. The profiled cradle ensures that even at full capacity, the bags maintain their predicted depth envelope.

---

## 4. Drainage and Dip Tube Considerations

### 4a. Gravity Drainage by Angle

The connector end is at the bottom-front area (low point). Gravity pulls liquid toward the connector along the incline with force F = m x g x sin(theta).

| Angle | sin(theta) | Gravity Component (fraction of g) | Qualitative Drainage |
|-------|-----------|-----------------------------------|---------------------|
| 15    | 0.26      | 26%                               | Poor -- liquid pools in bag creases |
| 20    | 0.34      | 34%                               | Adequate with pump suction |
| 25    | 0.42      | 42%                               | Good |
| 30    | 0.50      | 50%                               | Good -- half of gravity drives drainage |
| 35    | 0.57      | 57%                               | Very good |
| 40    | 0.64      | 64%                               | Very good |
| 45    | 0.71      | 71%                               | Excellent |
| 50+   | 0.77+     | 77%+                              | Excellent, approaching full gravity |

Below 20 degrees, gravity drainage becomes unreliable. Liquid can pool in bag creases and folds rather than flowing to the connector. Pump suction compensates but can't overcome all trapped pockets.

Above 30 degrees, gravity reliably moves liquid toward the connector. The bag collapses from the sealed end downward in a controlled manner. The dip tube remains submerged until the bag is nearly empty.

### 4b. Dip Tube Routing

The Platypus Drink Tube Kit creates a sealed path from the connector into the bag interior. The dip tube (1/4" ID, ~6.35mm OD) extends from the 28mm threaded cap into the bag.

In the diagonal orientation:
- The dip tube enters at the connector (front-bottom area, lowest point).
- It extends upward along the incline toward the sealed end.
- The tube opening sits 100-150mm up the incline from the connector.

At various angles, the dip tube orientation relative to the liquid pool:

**Shallow angles (15-25 degrees):** The dip tube is nearly horizontal, extending into a thin, wide puddle of liquid. The tube opening stays submerged until the liquid level drops below the tube height (~10-15mm above the bag floor at the tube opening). Residual volume is higher because the shallow angle doesn't effectively concentrate liquid at the connector.

**Moderate angles (30-45 degrees):** The dip tube angles upward at a meaningful incline. Liquid concentrates at the connector end as a deeper, narrower puddle. The tube opening stays submerged longer. This is the optimal range for drainage efficiency.

**Steep angles (50+ degrees):** The dip tube is nearly vertical. Liquid falls rapidly to the connector. The puddle is deep and narrow. Drainage is excellent, but the near-vertical tube may trap air bubbles during refilling.

### 4c. Residual Volume Estimates

Residual volume is liquid that cannot be evacuated by gravity and pump suction combined. It includes liquid trapped in bag creases, below the dip tube opening, and in dead spots where the bag folds prevent flow.

These are rough estimates. Actual values require physical testing. The dip tube extends 100-150mm into the bag, which reaches well past the residual puddle at angles above 25 degrees. Pump suction (2-5 PSI) further reduces residual.

| Angle | 1L Estimated Residual | 1L % | 2L Estimated Residual | 2L % |
|-------|----------------------|------|----------------------|------|
| 20    | 70-80ml              | 7-8% | 140-160ml            | 7-8% |
| 25    | 55-65ml              | 5-7% | 110-130ml            | 5-7% |
| 30    | 45-55ml              | 4-6% | 90-110ml             | 4-6% |
| 35    | 40-50ml              | 4-5% | 80-100ml             | 4-5% |
| 40    | 35-40ml              | 3-4% | 70-80ml              | 3-4% |
| 45    | 30-40ml              | 3-4% | 60-80ml              | 3-4% |
| 50    | 30-35ml              | 3%   | 60-70ml              | 3%   |

Beyond 45 degrees, residual volume improvements are marginal. The dip tube and pump suction dominate over gravity at these angles. The practical floor is around 25-35ml for 1L and 50-70ml for 2L, limited by bag crease geometry rather than angle.

### 4d. Drainage Performance Summary

**Angles below 25 degrees are poor for drainage.** The gravity component is too weak to reliably move liquid through bag creases to the connector. Residual volume exceeds 5-7%.

**Angles 30-45 degrees are the drainage sweet spot.** Good gravity assistance, controlled bag collapse, reasonable residual volume (3-5%). The dip tube stays submerged until 90-95% of the bag is evacuated.

**Angles above 45 degrees offer diminishing returns.** Drainage improves marginally. The steep angle may cause the dip tube to trap air during refilling, complicating the fill cycle.

---

## 5. Width Analysis

### 5a. The Key Insight: Depth Separation

In Vision 1, the cartridge and bags occupy **different depth zones**. The cartridge sits in the front-bottom void (depth 0 to ~130mm from the front wall). The bags span diagonally from near the back wall to toward the front. Because they're at different depths, the cartridge and bags do not compete for width. The full enclosure width is available for each component independently at its respective depth.

This resolves the width conflict identified in previous research, which assumed the cartridge would be beside the bags at the same depth.

### 5b. Width Budget at Cartridge Depth (Front)

At the cartridge depth (0-130mm from front), the only width consumers are:
- Cartridge: 150mm wide (standard orientation)
- Tubing runs: ~20-30mm per side for plumbing to/from the cartridge

Total: ~200-210mm of 272mm interior. Remaining: 62-72mm. Comfortable.

### 5c. Width Budget at Bag Depth (Back)

At the bag depth, the only width consumers are:
- 1L bags: 152mm wide. Remaining: 120mm (60mm per side for tubing, airflow, mounting hardware).
- 2L bags: 190mm wide. Remaining: 82mm (41mm per side).

Both are workable. The 2L bags in the 272mm enclosure (41mm per side) are tighter but functional.

In the 292mm enclosure (300W exterior): 2L bags have 51mm per side -- more comfortable.

### 5d. Width Overlap Zone

There IS a zone where the cartridge and bags share the same depth: where the front of the bag slab overlaps the back of the cartridge. In this overlap zone, the cartridge is below the bags (in the triangle) and the bags are above. They share the same depth range but are separated vertically by the triangle geometry.

Width is not constrained in this overlap zone because the cartridge (150mm wide) and bags (152-190mm wide) are vertically separated, not side-by-side.

### 5e. Side-by-Side Placement (Alternative to Front-Back Separation)

If for some reason the cartridge needed to be beside the bags at the same depth:

| Configuration | Width Needed | 272mm Interior | 292mm Interior |
|--------------|-------------|----------------|----------------|
| 1L bag + cartridge standard | 302mm | No (-30mm) | No (-10mm) |
| 1L bag + cartridge rotated (80W) | 232mm | Yes (+40mm) | Yes (+60mm) |
| 2L bag + cartridge standard | 340mm | No (-68mm) | No (-48mm) |
| 2L bag + cartridge rotated (80W) | 270mm | Yes (+2mm) | Yes (+22mm) |

Side-by-side only works with the rotated cartridge (80mm wide), and is extremely tight for 2L bags in the 272mm enclosure (2mm clearance). **This is unnecessary in Vision 1 because the cartridge goes in the front-bottom void, not beside the bags.**

---

## 6. Recommended Configurations

### 6a. Configuration 1: 1L Bags at 35 degrees in 280W x 300D x 400H

**The compact workhorse.**

| Parameter | Value |
|-----------|-------|
| Enclosure exterior | 280W x 300D x 400H mm |
| Enclosure interior | 272W x 292D x 392H mm |
| Bag angle | 35 degrees |
| Bag depth (actual shape) | ~243mm |
| Depth margin | ~49mm |
| Top-back electronics void | ~197mm height |
| Enclosure volume | 33.6 liters |

**Why 35 degrees:** With the actual bag shape, depth is only ~243mm of 292mm, leaving 49mm margin. Height consumption is ~195mm of 392mm, leaving ~197mm above for electronics. The front-bottom triangle provides ample room for the cartridge plus its lever mechanism.

**Drainage:** sin(35) = 0.57. Good gravity drainage. Estimated residual: 40-50ml (4-5%). Acceptable.

### 6b. Configuration 2: 2L Bags at 35 degrees in 280W x 300D x 400H

**The high-capacity option in the compact enclosure.**

| Parameter | Value |
|-----------|-------|
| Enclosure exterior | 280W x 300D x 400H mm |
| Enclosure interior | 272W x 292D x 392H mm |
| Bag angle | 35 degrees |
| Bag depth (actual shape, back-wall mounted) | ~267mm |
| Depth margin | ~25mm |
| Top-back electronics void | ~140mm height |
| Enclosure volume | 33.6 liters |

**Why this works:** The corrected lens-shaped bag profile and back-wall mounting bring the effective depth to ~267mm, fitting within the 292mm interior with 25mm margin. The rigid-body model incorrectly predicted 333mm depth, leading to the earlier (wrong) conclusion that 2L bags required a 350mm-deep enclosure.

**Why 35 degrees:** Best balance of depth margin (~25mm) and height economy (~140mm top-back void). At 30 degrees, margin drops to ~13mm (tight). At 40 degrees, margin grows to ~36mm but height consumption increases, reducing the electronics void to ~120mm.

**Back-wall mounting is required.** Without it, the free-standing actual-shape depth is ~296mm, which is 4mm over the 292mm interior. Back-wall mounting eliminates the sealed-end thickness projection, saving ~29mm of depth.

**Drainage:** sin(35) = 0.57. Good gravity drainage. Estimated residual: 80-100ml (4-5%).

### 6c. Configuration 3: 2L Bags at 35-40 degrees in 280W x 350D x 400H

**The maximum-margin option.**

| Parameter | Value (at 35 deg) | Value (at 40 deg) |
|-----------|-------------------|-------------------|
| Enclosure exterior | 280W x 350D x 400H mm | 280W x 350D x 400H mm |
| Enclosure interior | 272W x 342D x 392H mm | 272W x 342D x 392H mm |
| Bag depth (actual shape) | ~296mm | ~285mm |
| Depth margin (no back-wall mount) | ~46mm | ~57mm |
| Depth margin (with back-wall mount) | ~75mm | ~86mm |
| Top-back electronics void | ~140mm | ~120mm |
| Enclosure volume | 39.2 liters | 39.2 liters |

**Why consider this:** If 25mm margin in the 300mm enclosure proves too tight in practice (bag deformation, manufacturing tolerances), the 350mm enclosure provides 46-86mm margin depending on angle and mounting approach. Back-wall mounting is optional here -- the bags fit even without it.

**Trade-offs:** The enclosure is 16.7% larger in volume (39.2L vs 33.6L) and 50mm deeper. For a product that can fit 2L bags in the 300mm-deep enclosure, the 350mm depth is unnecessary extra bulk.

### 6d. Configuration Comparison

| Parameter | Config 1 (1L/35/300D) | Config 2 (2L/35/300D) | Config 3 (2L/35/350D) |
|-----------|----------------------|----------------------|----------------------|
| Bag capacity | 2 x 1L | 2 x 2L | 2 x 2L |
| Enclosure (ext) | 280x300x400 | 280x300x400 | 280x350x400 |
| Volume | 33.6L | 33.6L | 39.2L |
| Depth margin | ~49mm | ~25mm (back-wall) | ~46mm (free) / ~75mm (back-wall) |
| Top-back void H | ~197mm | ~140mm | ~140mm |
| Drainage quality | Good (sin 35=0.57) | Good (sin 35=0.57) | Good (sin 35=0.57) |
| Residual | ~45ml (4.5%) | ~90ml (4.5%) | ~90ml (4.5%) |
| Risk | Low | Low-Medium | Low |
| Back-wall mount | Optional | Required | Optional |

### 6e. Product Variant Strategy

With the corrected bag shape analysis, **a single 280 x 300 x 400 enclosure can serve both 1L and 2L bags.** This is a significant simplification over the previous two-variant approach.

**Single enclosure (280 x 300 x 400):**
- 1L bags at 35 degrees: 49mm depth margin, very comfortable.
- 2L bags at 35 degrees with back-wall mounting: 25mm depth margin, workable.
- Same cartridge, electronics, front panel, hopper, and plumbing for both.
- Only the bag mounting cradle differs (profiled for 1L or 2L bag shapes).

**If a two-variant approach is still desired:**
- Standard (280 x 300 x 400): Works for both 1L and 2L.
- Extended (280 x 350 x 400): 2L with maximum margin, no back-wall mounting required. For customers who want the extra safety margin.

### 6f. Open Questions for Physical Testing

1. **Back-wall mounting verification:** Does the sealed end actually pin flat against the back wall as predicted? Measure the actual depth envelope of a back-wall-mounted bag pair at 35 degrees.

2. **Profiled cradle effectiveness:** Does the 3D-printed cradle maintain the predicted bag envelope? Measure bag bulge at center with full 2L load in the cradle vs free-standing.

3. **25mm margin adequacy:** With 2L bags at 35 degrees and back-wall mounting, is 25mm margin sufficient for manufacturing tolerances, bag deformation, and thermal expansion?

4. **Dip tube behavior at 35 degrees:** Does the dip tube stay submerged as the bag drains? At what fill level does air first reach the tube opening?

5. **Refilling at 35 degrees:** Can the pump push concentrate uphill through the dip tube into a bag that's angled at 35 degrees? The hydrostatic head is L x sin(theta) x density x g, which at 35 degrees for a 2L bag is 350 x 0.574 x 1.05 x 9.8 / 1000 = 2.1 kPa (0.30 PSI). The Kamoer pump can handle this easily.

6. **Bag collapse pattern:** Does the bag collapse cleanly from the sealed end toward the connector, or do random folds form that trap liquid? This is critical for residual volume estimates.

7. **1L bag shape correction validation:** Confirm the estimated ~10-15mm depth savings for 1L bags vs rigid-body model. Less critical since 1L bags have large margins regardless.
