# V1 Hopper Integration: Back-Wall Mounted Bags at 35 Degrees

Research on how the hopper/funnel system integrates with Vision 1's back-wall-mounted bag arrangement. The hopper is the primary user interaction point for refilling concentrate. Bags are permanent (installed once during manufacturing) and refilled via the hopper funnel.

Enclosure: 280W x 300D x 400H exterior, 272W x 292D x 392H interior (4mm walls).

See `2l-bags-at-300mm-depth.md` for the depth analysis proving 2L bags fit at 35 degrees in 300mm depth.

---

## 1. Hopper Position and Geometry

### 1a. Where the Space Is

Two 2L Platypus bags are mounted with sealed ends pinned flat to the back wall, cap/connector ends at the front-low position. A 3D-printed profiled cradle supports the bags from underneath at 35 degrees. The bags are lens-shaped (not rectangular), and back-wall mounting puts the effective bag depth at ~267mm, leaving 25mm margin in the 292mm interior.

The height consumed by the bag pair at 35 degrees:

    Height = L x sin(35) + T_center x cos(35) = 350 x 0.574 + 80 x 0.819 = 201 + 66 = 267mm

Remaining height above the bags: 392 - 267 = **125mm**.

Side cross-section (height vs. depth):

```
FRONT                                    BACK
┌────────────────────────────────────────────┐ 392mm
│                                            │
│   ★ HOPPER ZONE ★                    [E]  │
│   (~125mm above bags)                      │
│                                            │
267 ╲╲                                       │
│    ╲╲  bags slope downward                 │
│     ╲╲  (lens-shaped, 35deg)              │
│      ╲╲                                   │
│       ╲╲  3D-printed cradle               │
│        ╲╲  supports from below            │
│ [CART]  ╲╲                                │
│          ╲╲  ← cap/connector end          │
│           ╲╲    (front-low)         [pin] │ ← sealed end pinned to back wall
└────────────────────────────────────────────┘ 0mm
0mm                                    292mm
                   DEPTH →
```

The sealed (non-connector) ends of the bags are pinned flat to the back wall near the top. The bags descend at 35 degrees toward the front, with connector/cap ends at the front-low position. The hopper zone is the full-width space above the bag slab, approximately 125mm tall. This is generous — ample room for a proper funnel design with clearance to spare.

### 1b. Position Options

**Option 1: Hopper integrated into top panel (hinged or removable lid)**

The top panel of the enclosure contains the hopper opening. With a clamshell top or removable lid, the user pours directly into a funnel recessed in the top face. With 125mm of vertical clearance above the bags, the funnel sits comfortably below the lid.

- Pros: Maximum accessibility (the entire top surface is the pour zone), no internal volume competition, 125mm clearance is generous
- Cons: Requires a hinged or removable panel (mechanical complexity), seal integrity when closed

**Option 2: Hopper above the bag plane, spanning the full top**

A horizontal or gently sloped hopper mounted at the enclosure ceiling, above the diagonal bags entirely.

- Pros: Maximum volume, horizontal pour opening is natural
- Cons: Steals height from the 125mm zone, but a 70mm funnel still leaves 55mm clearance

**Option 3: Hopper at front-top edge, vertical orientation**

A small funnel mounted on the front face near the top, angled to receive a pour from the front.

- Pros: Most accessible from the cabinet opening, minimal internal space usage
- Cons: Small capacity (funnel only), awkward pour angle, splash risk

### 1c. Recommended Position

Option 1 (top-panel integration) combined with the slide-out tray access architecture. When the user pulls the tray forward, the top of the enclosure is fully accessible. A hinged lid or removable cap exposes the single hopper funnel. The user pours from above with both hands free, clear line of sight, and natural gravity-assist.

With 125mm of vertical clearance, even a 500ml reservoir funnel (85mm tall) fits with 40mm to spare. A 200-300ml funnel (60-70mm tall) fits with over 55mm clearance — no geometric conflict.

---

## 2. Fill Routing

### 2a. The Routing Challenge

Syrup enters the hopper at the TOP of the enclosure. The bag connectors (dip tube caps) are at the FRONT-LOW position. The fill path must traverse from the top of the enclosure down to the front-low connector area.

Route distances (approximate for 2L bags at 35 degrees in 300D x 400H):

| Hopper Location | Bag Connector Location | Straight-Line Distance | Tubing Run (with bends) |
|---|---|---|---|
| Top-center (~146D, ~380H) | Front-low (~25D, ~125H) | ~280mm | ~350-400mm |

### 2b. Fill Mechanism Options

**Gravity-only fill (through dedicated tubes)**

Syrup drains from the hopper down dedicated fill tubes to the bag connectors. No pump involvement.

- Driving pressure: Height differential of ~250mm = ~0.36 PSI (for water; syrup at 1.2-1.4 SG gives ~0.43-0.50 PSI)
- Flow rate limited by counter-current air displacement through the dip tube's 6.35mm bore
- Estimated fill time for 2L: 15-30 minutes
- Tubing dead volume: 400mm of 4.5mm ID tubing = ~6.4 ml per line (12.8 ml total for 2 lines)
- Pros: No electronics, no pump involvement, simple
- Cons: Slow, open-air system (ambient air enters bag during every refill), requires separate fill tubes, dead volume in long tubes wastes syrup

**Pump-assisted fill (through the existing pump circuit)**

The existing Kamoer peristaltic pump reverses direction to pull syrup from the hopper and push it into the bag. The hopper connects at TEE2 (pump outlet side) via a solenoid valve. A check valve at the dispensing point prevents air ingestion.

- Driving pressure: 2-5 PSI from the pump
- Estimated fill time for 2L: 5-10 minutes at 200-400 ml/min
- Tubing run: Hopper to TEE2 is ~200-300mm because TEE2 is near the pump (front-bottom area), and the existing pump-to-bag tubing handles the rest
- Dead volume: ~200-300mm of 4.5mm ID hopper tubing = ~3.2-4.8 ml per line
- Pros: 3-5x faster, sealed system (minimal air exchange), uses existing pump hardware, shorter dedicated tubing run
- Cons: Requires pump reversal firmware (trivial), check valves at dispensing point ($6-10), hopper solenoid valves (part of the 8 two-way NC valve set)

**Pump-assisted fill (dedicated fill pumps)**

Separate small peristaltic pumps on each hopper line push syrup into the bags.

- Cost: $10-24 for 2 small pumps + $1-3 for drivers
- Pros: Independent of main pump circuit, simpler topology (no pump reversal)
- Cons: $30-50 additional cost, 2 more pumps to mount and wire, GPIO pressure on ESP32, additional failure points

### 2c. Recommended Fill Mechanism

Pump-assisted fill through the existing pump circuit. The cost delta is minimal ($6-10 for check valves), fill time is 3-5x faster than gravity, and the sealed system preserves concentrate freshness. The pump drains the funnel as the user pours, enabling a continuous-pour workflow.

### 2d. Dead Volume Analysis

Dead volume = syrup trapped in tubing after hopper empties. Wasted on each refill unless flushed.

| Fill Approach | Dedicated Tube Run | Tube ID | Dead Volume (per line) | Total (2 lines) |
|---|---|---|---|---|
| Gravity (dedicated tubes) | ~400mm | 4.5mm | 6.4 ml | 12.8 ml |
| Pump-assist via TEE2 (hopper to TEE2 only) | ~250mm | 4.5mm | 4.0 ml | 8.0 ml |
| Pump-assist via dedicated pump | ~350mm | 4.5mm | 5.6 ml | 11.2 ml |

Pump-assist via TEE2 has the lowest dead volume because the hopper tube only needs to reach TEE2 — the existing pump-to-bag tubing handles the rest, and that tubing is already filled with concentrate from normal dispensing.

### 2e. Backflow Prevention

If a bag is pressurized (compressed air from a partial fill, or squeeze from the bag's own weight on the incline), concentrate could flow backward through the dip tube, through the tubing, through TEE2, and up into the hopper — especially if the hopper solenoid valve leaks.

Prevention:
- The hopper solenoid valves are normally-closed (NC). When de-energized, they seal by spring pressure. Backflow requires the solenoid to fail open.
- A check valve on the hopper line (oriented to allow flow FROM hopper TOWARD TEE2) provides passive backup. Cost: $3-5 per line.
- Bag pressure is low (~0.5-2 PSI from compressed trapped air). Even a weak check valve blocks this.

---

## 3. Two-Flavor Management

Two bags, two flavors. The user must direct syrup to the correct bag during refill. Cross-contamination (pouring cola syrup into the lemon-lime bag) is a real failure mode.

### 3a. Single Funnel with Firmware-Controlled Valve Selection (Recommended)

A single hopper funnel serves both flavors. The user selects the target flavor via display or button before pouring. Firmware opens the correct valve path; the other remains closed.

The valve topology uses **8 two-way normally-closed solenoid valves** (4 per pump), all housed in the main enclosure body. Each flavor line has its own hopper-side valve at TEE2. When the user selects a flavor and pours, firmware:

1. Opens the hopper solenoid valve for the selected flavor line
2. Reverses the corresponding pump to pull syrup from the funnel into the selected bag
3. Keeps the other flavor's hopper valve closed (NC default state)

The "all closed" default position (all 8 valves NC, de-energized) means no cross-contamination path exists when the system is idle. Each valve is independently controllable — no shared failure modes between flavor lines.

| Metric | Assessment |
|---|---|
| Cost | Zero additional beyond pump-assist topology (valves already present in the 8-valve set) |
| Complexity | Firmware only — valve + pump selection logic |
| User error risk | Low — user must select correctly on display/button, but firmware prevents pouring into wrong bag (wrong valve stays closed) |
| Cross-contamination | Shared-funnel risk — residue from previous pour remains in funnel. Mitigated by rinse between flavor changes |
| Cleaning | One funnel to clean |
| Space | One funnel, most compact |

### 3b. Why Not Two Separate Funnels?

Two funnels side by side would eliminate the shared-funnel residue issue, but:
- Since bags are permanent and refilled via hopper, the firmware-controlled single funnel is simpler
- Two funnels require 230mm of width (2 x 100mm + 30mm gap) versus ~100mm for one
- Two funnels mean two cleaning points
- The 8 two-way NC valve topology already provides per-line isolation at zero additional cost

Two funnels remain a viable fallback if cross-contamination from shared residue proves problematic in testing.

### 3c. Color-Coding

Regardless of funnel count, color-code everything: display labels, tubing, bag cradle positions, and any physical indicators on the enclosure. Consistent color coding (e.g., red = flavor 1, blue = flavor 2) reduces selection errors.

---

## 4. Hopper Capacity and Dimensions

### 4a. Funnel Role: Drains as User Pours

The hopper is a small funnel (~200-300 ml capacity). The pump pulls syrup out as fast as it enters, and the funnel never fills completely. The user watches the funnel level and pours at a matching rate. Pump-assisted fill drains the funnel continuously during the pour.

| Pump Fill Rate | Funnel Capacity | Pour Time for 2L |
|---|---|---|
| 200 ml/min | 200 ml | ~10 min (user pours steadily) |
| 400 ml/min | 200 ml | ~5 min |
| 400 ml/min | 300 ml | ~5 min (more buffer) |

With pump-assisted filling at 200-400 ml/min, a 200-300 ml funnel is sufficient. If the user pours faster than the pump drains, the funnel buffers the excess — 200-300 ml of buffer handles a fast 2-3 second glug from a bottle.

### 4b. Physical Dimensions

Approximate hopper dimensions (truncated cone / funnel shape):

| Capacity | Top Diameter | Bottom Diameter | Height | Approximate Volume |
|---|---|---|---|---|
| 200 ml | 90mm | 15mm (outlet) | 60mm | ~200 ml |
| 300 ml | 100mm | 15mm | 70mm | ~300 ml |
| 500 ml | 110mm | 15mm | 85mm | ~500 ml |

For a 200-300 ml funnel, the hopper is compact: ~100mm diameter, ~70mm tall. This fits easily within the 125mm vertical clearance above the bags, leaving 55mm of clearance for the lid mechanism and structure.

### 4c. Recommendation

**200-300 ml funnel** with pump-assisted filling. The pump drains the funnel fast enough that the user can pour continuously from a bottle. The refill experience: pull tray, open lid, select flavor on display/button, pour from bottle into funnel while pump runs, close lid, push tray. Total time: 3-10 minutes for a 2L refill depending on pump speed.

---

## 5. Access Architecture

### 5a. Slide-Out Tray (Recommended)

The enclosure sits on a pull-out shelf mounted in the cabinet. The user pulls the tray forward ~200-300mm, bringing the entire enclosure to the cabinet door opening under ambient room light.

```
CABINET (side view)

┌─────────────────────────────────┐ <- cabinet shelf
|                                 |
|    pulled-out position:         |
|                                 |
|    ┌───[LID]───┐               |
|    |  [FUNNEL] |               |
|    |           |               |
|    | enclosure |               |
|    |           |               |
|    └───────────┘               |
|    ════════════════  <- tray   |
|    (at cabinet door opening)   |
└─────────────────────────────────┘ <- cabinet floor
     ^ cabinet door
```

The user opens the cabinet door, pulls the tray, and the hopper funnel is right at the front edge, at waist height, in full light. Both hands are free for pouring.

### 5b. Clamshell Top (Complementary)

Combined with the slide-out tray, a clamshell top (hinged at the rear edge) exposes the hopper funnel from above. The user flips the lid with one hand and pours with the other.

Lid height: ~40-80mm (covers the funnel zone). In a 500mm cabinet with 400mm enclosure + 35mm tray height, the lid needs to open within ~65mm of vertical clearance. A 40mm lid opens to 90 degrees within this budget.

Alternative: a removable top panel (magnets or snap-fits) instead of a hinge. With the tray pulled out, the user lifts the panel off and sets it on the counter. This avoids the hinge mechanism entirely and has no height constraint.

### 5c. Fill Level Visibility

- **Translucent funnel:** Food-grade silicone or Tritan (copolyester) is naturally translucent. The user can see the syrup level through the funnel wall.
- **Display feedback:** The capacitive sensor on the hopper line detects when the funnel is empty. The display shows "Filling..." with a progress indicator, then "Complete" when the sensor detects air.
- **Audible feedback:** A brief tone when the fill cycle completes.

### 5d. Spill Containment

- **Funnel lip:** A raised rim (5-10mm) around the funnel opening catches minor spills.
- **Drip tray:** The top surface of the enclosure (below the lid) should be a shallow tray with raised edges, sloping toward a drain or collection point. Any spilled syrup pools here instead of dripping down the enclosure sides.
- **Overflow path:** If the funnel overflows, syrup goes into the drip tray. The drip tray should be removable for cleaning (lift out, rinse in sink).
- **Splash guard:** A short collar or baffle around the funnel opening prevents splashes during vigorous pouring.

Failure scenario: user selects the wrong flavor on the display, then pours. The bag receives the wrong concentrate. Recovery: run a clean cycle on the contaminated line, then refill with the correct flavor. This wastes one bag-volume of concentrate — annoying but not catastrophic. Color-coding and clear labeling are the primary mitigation.

---

## 6. Cleaning and Maintenance

### 6a. Hopper Funnel Cleaning

Syrup residue (sugar, flavoring, coloring) will accumulate on the funnel interior, especially at the narrow outlet. In a warm under-sink environment, this becomes a microbial growth risk within days.

**Cleaning approaches:**

| Approach | Method | Frequency | Effort | Effectiveness |
|---|---|---|---|---|
| Removable funnel | Lift out, wash in sink or dishwasher | Each refill or weekly | Low (30 seconds) | Excellent |
| Rinse-in-place | Pour hot water through the funnel, pump drains it | Each refill | Very low (10 seconds) | Good for sugar; insufficient for biofilm over time |
| Self-clean cycle | Firmware runs water through the hopper line during clean cycle | With scheduled clean cycle | Zero (automated) | Adequate if combined with periodic manual wash |
| Fixed funnel | User wipes with a cloth or brush | Weekly | Moderate | Fair — hard to reach the outlet |

**Recommendation:** Removable funnel. Food-grade silicone is ideal — flexible (pops out of a mounting ring), dishwasher safe, non-porous (resists biofilm), translucent (user can see residue), and inexpensive. A silicone funnel that press-fits into a hard mounting ring in the enclosure top gives the best combination of easy cleaning and secure mounting.

### 6b. Fill Tube Cleaning

The tubing between the hopper and TEE2 contains residual syrup after each fill cycle. Over time, this residue supports microbial growth.

**The pump-assist topology already supports hopper line flushing.** The user pours clean water into the funnel after the concentrate fill. Firmware runs the flush cycle, pushing water through the hopper line and out the dispensing point. This clears the ~4 ml of dead volume.

For the bag-side tubing (TEE2 to bag), the existing clean cycle already flushes this path.

### 6c. Microbial Risk Assessment

Sugar syrup at 50-67 Brix (the concentration of typical flavor syrups) has low water activity (aw ~0.80-0.86), which inhibits most bacterial growth. However:

- Diluted residue (from incomplete rinsing) has higher water activity and supports growth
- Mold species (Aspergillus, Penicillium) can grow at aw < 0.80
- The under-sink environment is warm (20-30C) and dark — ideal for mold
- Biofilm on tubing interior surfaces is the primary risk, not bulk liquid contamination

**Mitigation:**
- Regular clean cycles (weekly, automated by firmware schedule)
- Hopper line flush after each refill
- Removable funnel for periodic deep clean
- Smooth, non-porous materials throughout (hard PE/PU tubing internally, silicone only at pump heads and external runs, PP/Tritan funnel, no 3D-printed surfaces in the fluid path)

### 6d. Material Selection

| Component | Recommended Material | Why |
|---|---|---|
| Funnel body | Food-grade silicone (Shore 40-60A) | Flexible (removable), translucent, dishwasher safe, non-porous |
| Funnel mounting ring | PP or ABS (injection molded or machined) | Rigid support for silicone funnel, chemical resistant |
| Hopper tubing | 1/4" OD hard PE or PU with John Guest push-to-connect fittings | NSF 61 certified, does not absorb flavors, standard in RO/ice maker systems. Clean cycle flushes lines; the removable silicone funnel insert handles the critical food-contact surface |
| Funnel lid/cap | Food-grade silicone or PP | Snap-fit or press-fit, with optional duckbill valve for sealed hopper operation |
| Drip tray | PP or ABS | Rigid, chemical resistant, removable for washing |

---

## 7. Geometric Integration: 2L Bags at 35 Degrees in 280W x 300D x 400H

Interior dimensions: 272W x 292D x 392H (4mm walls).

From the `2l-bags-at-300mm-depth.md` analysis:
- Actual bag depth (back-wall mounted): ~267mm
- Depth margin: 292 - 267 = 25mm
- Bag height consumed: ~267mm
- Height above bag stack top: 392 - 267 = **125mm**

### 7a. Available Zones

| Zone | Dimensions | What Goes There |
|------|-----------|-----------------|
| Above bags (full width, 125mm tall) | ~125mm H x 292mm D x 272mm W | Hopper funnel, electronics (ESP32, drivers, PSU) |
| Front-bottom (below bag connector end) | ~125mm H x ~200mm D x 272mm W | Pump cartridge dock, valve assembly (8 two-way NC valves) |

The 125mm above-bag height is excellent for the hopper funnel. A 300ml funnel (100mm diameter, 70mm tall) uses 70mm of the 125mm, leaving 55mm for lid mechanism and structural clearance.

### 7b. Cross-Section Diagram

```
FRONT                                    BACK
┌────────────────────────────────────────────┐ 392mm
| ┌────┐                                    |
| |FNL | <- funnel (70mm tall,         [E]  |
| └─┬──┘   100mm dia)                       |
|   |tubing                                 |
|   |                              ╲╲       |
267 |                             ╲╲ [pin]  | <- sealed end pinned
|    ╲╲                          ╲╲         |     to back wall
|     ╲╲  2L bags (80mm stack) ╲╲           |
|      ╲╲  lens-shaped        ╲╲            |
|       ╲╲  35deg incline   ╲╲              |
|        ╲╲               ╲╲                |
| ┌───────╲╲╲╲          ╲╲                  |
| |CARTRIDG| ╲╲       ╲╲                    |
| |(150x130| [connectors]                   |
| | x80mm) |  (front-low)                   |
| └────────┘                                |
└────────────────────────────────────────────┘ 0mm
0mm                                    292mm
                   DEPTH ->
```

**Hopper zone clearance at top:** 125mm (ample for funnel + lid).

**Funnel pour opening** is at ~322-392mm height — accessible from above when lid is open.

**Key positions:**
- Sealed bag ends: pinned to back wall at ~267mm height
- Bag connector/cap ends: front-low, ~25mm from front wall, ~66mm above floor
- Funnel: centered in top zone, above bag midpoint
- 8 two-way NC valves: in front-bottom zone with pump cartridge

---

## 8. Comparison of Hopper Approaches

| Approach | Cost | Complexity | User Experience | Cleaning | Best For |
|---|---|---|---|---|---|
| **A. Single funnel, pump-assist, firmware select (8 two-way NC valves)** | $6-10 (check valves); valves already in BOM | Moderate — firmware UI for flavor selection | Very good — single pour point, fast fill, display-guided | 1 funnel to wash, low dead volume (4ml per active line) | Best balance of UX and cost (recommended) |
| **B. Two funnels, pump-assist fill** | $6-10 (check valves); valves already in BOM | Low — no flavor selection UI needed | Good — labeled funnels, pour-and-go | 2 funnels to wash, low dead volume (8ml) | If shared-funnel residue is unacceptable |
| **C. Single funnel with mechanical diverter** | $5-15 (diverter mechanism) | Moderate — custom moving part in fluid path | Fair — manual lever selection | Diverter body is hard to clean | Not recommended |

### 8a. Recommended Approach

**Approach A: Single funnel (200-300 ml), pump-assisted fill, firmware-controlled flavor selection via 8 two-way NC solenoid valves.** This is the natural outcome of combining:
- Pump-assisted filling (already recommended for speed and sealed operation)
- Single hopper (saves space, one cleaning point, one pour target)
- 8 two-way NC solenoid valves (4 per pump, already in BOM — simple, cheap, Amazon Prime, independent "all closed" position)
- Display/button-driven flavor selection (firmware only, no additional hardware)
- Permanent bags refilled via hopper (no bag removal or replacement)

The user experience: pull tray, flip lid, select flavor on display/button, pour from bottle into funnel while pump runs (3-10 min for 2L), display shows "Complete", optionally pour water to flush the line, close lid, push tray.

---

## 9. Open Questions

1. **Dip tube air counter-flow at 35 degrees:** The bag is tilted with the connector at the front-low end. During pump-assisted fill, concentrate is pushed through the dip tube into the bag interior. Air displaced from the bag must travel against the flow. At 35 degrees, air rises toward the sealed end (pinned at back-wall, high position), naturally separating from the dip tube opening at the low end. This geometry should help air displacement compared to a horizontal orientation.

2. **Hopper solenoid placement:** Where physically do the hopper-side valves sit? Near the funnel (top of enclosure) or near TEE2 (front-bottom area with the other valves)? Recommend near TEE2 to keep all 8 valves together in the main enclosure body and minimize dead volume in the always-pressurized section.

3. **Sealed vs. open hopper during fill:** The pump-assist topology supports a sealed hopper (silicone cap with duckbill valve). A sealed hopper prevents ambient air from entering the bag during fill. An open hopper is simpler (no cap) but allows air exchange. For weekly refills of sugar syrup, the freshness impact is likely minimal, but a sealed hopper is better practice.

4. **Funnel material for production:** Silicone is ideal for removability and cleaning, but injection-molded PP or Tritan is cheaper at scale. A hybrid (rigid PP funnel body with a silicone gasket at the mounting interface) may be the best production solution.

5. **Overfill detection:** Can the capacitive sensor on the hopper line detect a full bag? When the bag is full, pump pressure increases and flow rate drops. Firmware could monitor pump current draw or use a second capacitive sensor on the bag to detect fullness and stop the fill automatically. Without this, the user must estimate the correct pour volume.
