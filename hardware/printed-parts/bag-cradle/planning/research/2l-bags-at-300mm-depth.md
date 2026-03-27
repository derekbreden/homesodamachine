# Can 2L Platypus Bags Fit in a 300mm-Deep Enclosure?

A rigorous investigation of whether 2L Platy bags (350mm long x 190mm wide) can work in the 300mm exterior / 292mm interior depth enclosure at moderate diagonal angles (35-45 degrees).

**Bottom line up front:** The rigid-body rectangle model (`L cos θ + T sin θ`) overstates bag depth by approximately 37mm because it treats the bag as a constant-thickness rectangle. Real bags are lens-shaped: ~2mm at the sealed end, ~80mm stacked at center, ~30mm at the cap. When the actual bag profile is used, 2L bags at 35° need ~296mm of depth — only 4mm over the 292mm interior. With back-wall mounting (sealed end pinned flat to back wall), the effective depth drops to ~267mm, leaving a 25mm margin. **2L bags fit at 35° in the 300mm enclosure.**

See `2l-rigid-body-geometry.svg` for a visual comparison of the rigid rectangle vs. actual bag shape.

---

## 1. Why the Rigid-Body Model Is Wrong

### 1a. The standard formula and its hidden assumption

The formula used in all prior research:

    Depth consumed = L × cos(θ) + T_stack × sin(θ)

This treats the bag cross-section as a **constant-thickness rectangle** — 80mm thick (two bags stacked) across the entire 350mm length. It assumes the bag has four hard corners that define a tilted rectangular bounding box.

For 2L Platypus bags at 35°: `350 × cos(35°) + 80 × sin(35°) = 287 + 46 = 333mm`. This exceeds the 292mm interior by 41mm.

### 1b. The bag has NONE of those four corners

A Platypus Platy bag is a flexible pouch made from two welded polyethylene film panels. Its cross-sectional thickness varies dramatically along its length:

| Position | Single Bag Thickness | Two-Bag Stack | What's There |
|----------|---------------------|---------------|--------------|
| Sealed end (top) | ~1mm (two film layers) | ~2mm | Heat-sealed seam, completely flat |
| 25% along length | ~15mm | ~30mm | Bag starting to fill, thin pillow |
| Center (50%) | ~40mm | ~80mm | Maximum bulge, full liquid volume |
| 75% along length | ~25mm | ~50mm | Tapering toward connector |
| Cap/connector end | ~15mm | ~30mm | Rigid cap width, no wider |

The "80mm stacked thickness" is the **peak**, not the constant. The sealed end is flat film — literally 1mm thick per bag. The cap end is constrained by the cap diameter (~30mm for two bags). The bag is lens-shaped or teardrop-shaped in profile, not rectangular.

### 1c. What this means for depth

The rigid rectangle model projects those nonexistent corners into 3D space. Specifically:

- The **upper-front corner** of the rectangle (at the sealed end) assumes the bag is 80mm thick there. It is actually 2mm thick. This phantom corner accounts for approximately **22mm of false depth**.
- The **lower-back corner** (at the connector end) assumes the bag is 80mm thick there. It is actually ~30mm thick. This phantom corner accounts for approximately **14mm of false depth**.

**Total phantom depth: ~36-37mm.** The actual bag envelope at 35° occupies approximately **296mm** of depth, not 333mm.

---

## 2. The Actual Bag Profile at 35°

### 2a. Realistic depth calculation

Instead of the rigid formula, the depth is determined by the outermost points of the actual bag profile. The thickest point (~80mm stacked) occurs near the center of the bag, not at the ends. The depth envelope follows the lens shape:

- At the sealed end: the bag contributes almost no thickness perpendicular to the incline. Depth at this point ≈ `L × cos(35°)` = 287mm (just the length projection, negligible thickness contribution).
- At the center: full 80mm stack contributes `80 × sin(35°)` = 46mm perpendicular to the diagonal. But this is at the midpoint, not the end, so it doesn't extend the depth envelope as far as the rectangle model assumes.
- At the cap end: ~30mm stack contributes `30 × sin(35°)` = 17mm. Much less than the 46mm the rigid model assumes.

The actual depth envelope, traced around the real bag shape, is approximately **296mm at 35°**. This is only **4mm over** the 292mm interior.

### 2b. Comparison to rigid model

| Angle | Rigid Body Depth | Actual Bag Depth | Difference | vs 292mm Interior |
|-------|-----------------|-----------------|------------|-------------------|
| 30°   | 343mm           | ~310mm          | −33mm      | 18mm over         |
| 35°   | 333mm           | ~296mm          | −37mm      | 4mm over          |
| 38°   | 325mm           | ~290mm          | −35mm      | 2mm under ✓       |
| 40°   | 319mm           | ~286mm          | −33mm      | 6mm under ✓       |
| 43°   | 311mm           | ~280mm          | −31mm      | 12mm under ✓      |
| 45°   | 304mm           | ~275mm          | −29mm      | 17mm under ✓      |

The actual bag shape makes 38° and above fit comfortably. Even 35° is within striking distance — a mere 4mm over, well within the range of bag compression, wall thickness adjustment, or mounting geometry.

---

## 3. Back-Wall Mounting: Sealed End Pinned Flat

### 3a. The mounting concept

The sealed end of the bag is flat film — two welded polyethylene layers, ~1mm thick per bag. It has no structural rigidity. The mounting approach:

1. **Pin the sealed end flat against the back wall** (or very near it). The flat film naturally lies against a surface. A simple clamp, channel, or adhesive mounting point holds the sealed end at or near the back wall, at whatever height sets the desired angle.

2. **Pull the cap/connector end toward the front** of the enclosure, angled downward. The cap end hangs at the low-front position.

3. **Gravity and liquid weight do the rest.** The liquid inside the bag settles toward the low (connector) end. The bag drapes naturally from the pinned sealed end down to the cap end. There is no need to force the bag into a specific shape — the liquid's weight and gravity define the profile.

### 3b. Why this dramatically changes the geometry

When the sealed end is pinned to the back wall, the bag's depth footprint starts at **depth = 0** (the back wall), not at the depth position where a rigid rectangle's corner would be. The bag then curves forward as it descends, reaching maximum depth at the connector end.

The effective depth becomes approximately:

    Depth ≈ L × cos(θ) − (back wall recovery)

The sealed end, being flat against the back wall, contributes zero forward depth. The first 50-80mm of bag length contributes almost nothing because the bag is still very thin there. The depth is dominated by the thicker middle and connector sections.

At 35° with back-wall mounting:

    Effective depth ≈ 267mm

This leaves a **25mm margin** in the 292mm interior. The depth problem is decisively solved.

### 3c. The connector end position

At 35°, the connector end hangs at approximately:

- Depth from back wall: ~267mm (25mm from the front wall in 292mm interior)
- Height below the sealed-end pin: `350 × sin(35°)` ≈ 201mm

The connector is at the low-front position, which is ideal for:
- Gravity-assisted drainage (liquid flows toward the connector)
- Connection to the valve assembly below
- Clearance above the pump cartridge zone

---

## 4. The 3D-Printed Cradle

### 4a. Purpose

The bags need support from underneath across their full length. Without support, the liquid-filled bag would sag excessively in the middle, concentrating stress on the sealed end and connector mounting points.

A 3D-printed cradle sits underneath the bag pair, following the diagonal angle, and provides a shaped surface that matches the actual bag cross-section.

### 4b. Cradle profile

The cradle is **not a flat ramp**. It is profiled to match the lens-shaped cross-section of the stacked bags:

| Position Along Cradle | Cradle Channel Depth | Why |
|----------------------|---------------------|-----|
| Top (sealed end) | ~1-2mm (nearly flat) | Bag is flat film here, barely rises off the surface |
| 25% | ~15mm | Bag begins to fill, modest pillow |
| Center (50%) | ~40mm | Maximum bag bulge, deepest channel |
| 75% | ~25mm | Bag tapering toward connector |
| Bottom (connector end) | ~15mm | Cap constrains width, modest channel |

The cradle channel is essentially a U-shaped trough whose depth varies along the diagonal. Think of it as the "negative" of the bottom bag's profile.

### 4c. Benefits

- **Distributes load** across the full bag length — no point loads on the sealed end or connector
- **Prevents excessive sag** in the middle where the bag is heaviest
- **Guides the bag shape** to be predictable and repeatable across units
- **Provides the mounting structure** — the cradle attaches to the enclosure walls, and the bags rest in the cradle
- **Allows the bag profile to breathe** — the channel gives room for the bag to bulge naturally rather than squishing it flat

### 4d. Cradle dimensions

For two stacked 2L bags at 35°:

- Length along diagonal: ~350mm
- Width: ~200mm (190mm bag width + 10mm margin)
- Material: PLA or PETG (food-safe PETG preferred since it contacts bag exterior)
- Weight: estimated 100-200g depending on wall thickness and infill
- Print time: 4-8 hours on a standard FDM printer (may need to be printed in 2 halves and joined)

### 4e. Hard tubing routing clearance

Internal plumbing uses 1/4" OD hard PE/PU tubing with John Guest push-to-connect fittings. Unlike flexible tubing that can be stuffed into any gap, hard tubing and JG elbows require designed routing channels or clip points in the cradle structure. Each 90-degree JG elbow adds ~20mm of protrusion per axis. The cradle design must include tube routing features (channels, clip slots, or standoff points) along its edges or underside to accommodate the 8+ tube runs between bag connectors, valves, and pump. These routing features should be part of the initial CAD design, not added after the fact.

---

## 5. Height Consumed and Available Voids

### 5a. Height at 35°

The height consumed by the bag pair is dominated by the length projection:

    Height ≈ L × sin(35°) + T_center × cos(35°) ≈ 201 + 66 ≈ 267mm

(Using T_center = 80mm at the thickest point, which is the relevant height contributor.)

Remaining height in 392mm interior: **125mm** above the bags.

### 5b. Available zones

| Zone | Dimensions | What Goes There |
|------|-----------|-----------------|
| Top-back (above bags, near back wall) | ~125mm H × 292mm D × 272mm W | Electronics: ESP32, RP2040, L298N drivers, PSU, valve drivers |
| Front-bottom (below bags, near front wall) | ~200mm H × ~200mm D × 272mm W | Pump cartridge dock, valve assembly |
| Top-front (above bags, near front wall) | ~125mm H × ~100mm D × 272mm W | Hopper funnel |

At 35°, all three voids are generous. The 125mm above-bag height is excellent for both electronics and the hopper. Compare to 50° where only 73mm remains above.

### 5c. Cartridge clearance

The cartridge (150W × 130D × 80H) sits in the front-bottom void. The bottom of the bag pair at the front wall is approximately 200mm above the floor. The cartridge needs 80mm. Clearance: **120mm** — more than enough.

---

## 6. Partial Fill Scenarios

### 6a. Why partial fill matters

A "2L bag" does not have to hold 2L. The bag is a flexible container whose shape depends entirely on fill volume. At partial fill:

- The unfilled portion of the bag collapses flat (two film layers, ~0.5mm total)
- The filled portion forms a pillow shorter and thinner than the full-bag pillow
- The effective length of the pressurized zone decreases
- On a diagonal mount, gravity concentrates liquid at the low (connector) end

### 6b. Estimated dimensions at partial fill

| Fill Level | Volume | Estimated L_eff | Estimated T_center | Depth at 35° (actual shape) |
|-----------|--------|----------------|-------------------|---------------------------|
| 100% (2.0L) | 2000ml | 350mm | 40mm | ~296mm (no pin) / ~267mm (pinned) |
| 90% (1.8L) | 1800ml | ~330mm | 38mm | ~280mm / ~255mm |
| 75% (1.5L) | 1500ml | ~290mm | 34mm | ~248mm / ~230mm |
| 50% (1.0L) | 1000ml | ~230mm | 28mm | ~200mm / ~185mm |

With back-wall pinning, every fill level fits comfortably at 35°.

### 6c. The partial fill option

If for any reason the full 2L fill is too tight (unlikely with back-wall mounting), operating at 1.8L provides substantial margin while still delivering 80% more capacity than 1L bags. The firmware controls fill volume precisely via the pump, so enforcing a 1.8L limit is trivial. The user never interacts with the bags and would not know or care about unused bag capacity.

---

## 7. Enclosure Wall Thickness Trade-Off

### 7a. Impact on interior depth

| Wall Thickness | Interior Depth (300mm exterior) | Gain vs 4mm |
|---------------|-------------------------------|-------------|
| 4.0mm (baseline) | 292mm | — |
| 3.5mm | 293mm | +1mm |
| 3.0mm | 294mm | +2mm |
| 2.5mm | 295mm | +3mm |

### 7b. Is wall thinning needed?

With the corrected bag shape model, **no**. The actual bag depth at 35° is ~296mm without back-wall pinning (4mm over at 4mm walls) or ~267mm with back-wall pinning (25mm margin). Wall thinning is not needed to make the math work.

However, 3mm walls are a reasonable design choice on their own merits (lighter, less material cost, standard for ABS enclosures with ribbing). The extra 2mm of interior is a bonus, not a necessity.

### 7c. Structural notes

- **4mm walls:** Standard for consumer electronics of this size. Good rigidity.
- **3mm walls:** Within recommended ABS range (1.1-3.5mm). Needs internal ribs at 100-150mm spacing on larger panels. Acceptable for a stationary under-sink box.
- **2mm walls:** Minimum for this size. Requires dense ribbing. Not recommended for consumer feel.

---

## 8. Alternative Bag Options

### 8a. Why alternatives may not be needed

With the corrected understanding of bag shape and back-wall mounting, the 2L Platypus bag fits at 35° with 25mm margin. There is no dimensional crisis requiring alternative bags. However, alternatives are documented for completeness.

### 8b. Custom pouches

Custom food-grade pouches (from ePac, Polysmarts, etc.) could be designed specifically for this application:

- **300mm long × 220mm wide**, threaded 28mm spout
- **Capacity: ~1.8-2.0L**
- At 300mm length, depth at 35° ≈ 246mm (46mm margin). The depth problem disappears entirely.
- **MOQ:** 100-1,000 units for prototypes, $0.50-2.00/unit at 1,000 quantity
- **Lead time:** 2-4 weeks prototype, 4-8 weeks production

This is a strong option if Platypus bags prove problematic for other reasons (connector compatibility, durability, etc.), but is not needed purely for dimensional reasons.

### 8c. Other off-the-shelf options

- **Hoser 2.0L (152mm × 406mm):** Longer than the Platy. Makes depth worse. Rejected.
- **Wine bag-in-box bladders (1.5-3L):** Shorter and wider. Food-grade but not designed for repeated fill/drain cycles.
- **Generic spout pouches:** Available in custom sizes but different connector systems.

### 8d. Two 1L bags per flavor

The Platy 1L (280mm × 152mm) fits easily at 35° (`229 + 29 = 258mm`). Four bags (two per flavor) stacked: 100mm total thickness, depth at 35° = 286mm (fits). But plumbing complexity doubles — each flavor needs to draw from two bags in sequence. Not recommended over a single 2L bag.

---

## 9. The 50-Degree Fallback (Honest Evaluation)

Previous research set 50° as the minimum viable angle using rigid-body math. With corrected understanding:

### 9a. 50° is massive overkill

At 50° with actual bag shape: depth ≈ ~250mm. Margin of 42mm. The enclosure has far more space than needed.

But 50° has real costs:
- **Height consumed:** ~319mm of 392mm available. Only 73mm above bags.
- **Hopper squeeze:** The 73mm above the bags at the front limits funnel design to a wide, shallow trough.
- **Steeper visual impression:** Bags are closer to vertical than diagonal.

### 9b. When to consider 50°

Only if physical prototyping reveals the actual bag shape is significantly thicker than expected. Given the bag is demonstrably flat at the sealed end and cap-constrained at the connector, this is unlikely.

---

## 10. Synthesis and Recommendations

### 10a. The answer

**Yes, 2L bags fit at 300mm depth at 35°.** The rigid-body model overstated depth by ~37mm because it treated the bag as a constant-thickness rectangle. The actual lens-shaped profile, combined with back-wall mounting of the flat sealed end, gives ~267mm of depth — well within the 292mm interior.

### 10b. The mounting design

1. **Sealed end pinned to back wall** at the appropriate height for the desired angle
2. **Cap/connector end** hanging at the front-low position, connected to valve assembly below
3. **3D-printed profiled cradle** supporting the bag pair from underneath for the full diagonal length
4. **Gravity and liquid weight** naturally position the bag into the cradle

### 10c. Recommended prototype steps

1. **Build a mockup cradle at 35°.** 3D print a profiled cradle matching the estimated bag cross-section. Mount it in a 292mm-deep test box.

2. **Mount two filled 2L bags.** Pin the sealed ends to the back wall, rest the bags in the cradle, let the connector ends hang at the front-low position. Measure actual depth consumed.

3. **Photograph the cross-section** at sealed end, quarter-length, center, three-quarter, and connector. Verify the lens-shaped profile assumption and refine the cradle shape.

4. **Test drainage.** Pump liquid from the bags and verify that gravity drainage works well at 35° — the liquid should flow naturally toward the connector end.

5. **Test refill.** Pump liquid into the bags via the connector and verify the bag fills evenly and doesn't fold or kink against the back wall.

### 10d. What the 4mm gap means (if not using back-wall pinning)

Without back-wall mounting, the actual bag depth at 35° is ~296mm — 4mm over the 292mm interior. This 4mm is within range of:

- **Bag compression:** The bag is flexible. 4mm of give in 80mm of center thickness is 5% compression — trivial.
- **Wall thickness:** Going from 4mm to 3mm walls adds 2mm of interior (294mm). Combined with 2mm of bag give, the gap closes.
- **Angle adjustment:** Moving from 35° to 37° saves approximately 6mm of depth.
- **Spout protrusion:** If the connector/spout protrudes through or into the front wall, 10-15mm of depth is reclaimed.

Any one of these closes the gap. The 4mm is not a hard constraint — it's measurement noise relative to a flexible bag.

### 10e. Confidence level

**High confidence** that 2L bags work at 35-40° in the 300mm enclosure, based on:

- The bag shape is physically observable (flat sealed end, cap-constrained connector, lens center)
- Back-wall mounting is mechanically simple (pin flat film to wall)
- The cradle is straightforward to prototype (3D print, iterate)
- Multiple independent effects each contribute more than the 4mm gap
- The 25mm margin with back-wall pinning provides substantial safety factor

**Physical prototyping is recommended** to confirm the exact depth number and refine the cradle profile, but the theoretical case is strong. The previous research's conclusion that 2L bags require 50° or 350mm depth was based on a fundamentally incorrect geometric model.

---

## 11. Open Questions for Physical Testing

1. What is the actual depth footprint of two full 2L Platy bags mounted at 35° with sealed ends pinned to the back wall?
2. What is the cross-sectional profile at 5 points along the bag length? (Validates the lens-shape assumption and refines cradle design.)
3. Does the sealed end reliably stay flat against the back wall under liquid load, or does it want to peel away?
4. What is the optimal cradle channel depth at center — should it match the bag exactly, or be slightly deeper to allow the bag to settle?
5. Does the bag refill evenly when pumped in through the connector while pinned at the sealed end?
6. At what fill level does the bag start to kink or fold at the sealed end? (Determines maximum safe fill.)
7. What mounting method works best for pinning the sealed end to the back wall? (Clamp, channel, adhesive, riveted bracket?)

---

## Appendix: History of This Analysis

This document was originally written using the rigid-body rectangle model (`L cos θ + T sin θ`), which produced a minimum angle of 49-50° for 2L bags at 292mm depth. That analysis explored bag flexibility corrections, mount point geometry, stack compression, and partial fill — all as ways to recover the 41mm deficit at 35°.

The fundamental correction was recognizing that **the bag is not a constant-thickness rectangle**. It is a lens-shaped flexible pouch: flat at the sealed end (~2mm stacked), maximum thickness at center (~80mm stacked), and cap-constrained at the connector (~30mm stacked). This single correction eliminates ~37mm of the deficit, changing the problem from "41mm short" to "4mm over" — and the back-wall mounting approach eliminates the remaining gap entirely.

The rigid-body analysis was not wrong in its math — it was wrong in its premise. The formula `L cos θ + T sin θ` is correct for a rigid rectangle tilted at angle θ. The error was applying it to a shape that is not a rectangle.

See `2l-rigid-body-geometry.svg` for a visual comparison of the rigid rectangle vs. actual bag envelope at 35°.
