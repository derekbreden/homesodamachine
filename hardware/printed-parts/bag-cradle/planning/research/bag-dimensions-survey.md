# Platypus Bag Dimensions Survey

Actual manufacturer-stated dimensions for Platypus flexible bottles. All dimensions from Cascade Designs (Platypus parent company), confirmed across multiple retailers.

**CRITICAL: Thickness when full is NOT published anywhere.** Geometric estimates are provided but physical measurement is required.

---

## Measured Dimensions

### Key Models for This Project

| Model | Width | Length | Weight (empty) | Capacity |
|---|---|---|---|---|
| **Platy 1.0L** | **152mm (6")** | **280mm (11")** | 24g | 1.0L |
| **SoftBottle 1.0L** | **152mm (6")** | **330mm (13")** | 34g | 1.0L |
| **Platy 2.0L** | **190mm (7.5")** | **350mm (13.8")** | 36g | 2.0L |
| SoftBottle 0.5L | 127mm (5") | 305mm (12") | 23g | 0.5L |
| Hoser 2.0L | 152mm (6") | 406mm (16") | 102g (w/ tube) | 2.0L |
| Hoser 3.0L | 178mm (7") | 419mm (16.5") | 108g (w/ tube) | 3.0L |

### How Previous Research Was Wrong

| Dimension | Previous Estimate | Actual Value | Error |
|---|---|---|---|
| 1L bag width | 140mm | **152mm** | 12mm wider |
| 1L bag length | 250mm | **280-330mm** (model dependent) | 30-80mm longer |
| 2L bag width | 140mm | **190mm** | **50mm wider** |
| 2L bag length | 350mm | **350mm** | Correct |

The 2L bag is **50mm wider than assumed**. This is the single biggest dimensional error in the project.

### What This Means

- **Two 2L bags side-by-side: 380mm** — far exceeds 280mm enclosure width. Not feasible without a much wider enclosure.
- **Two 1L bags side-by-side: 304mm** — exceeds 280mm enclosure width by 24mm. Marginal even with a wider enclosure.
- **Stacked 2L bags: 190mm wide** — fits in 280mm enclosure with 90mm remaining. But the cartridge needs ~150mm wide, so cartridge cannot sit beside the bags. It must go above, below, or in front.
- **Stacked 1L bags: 152mm wide** — fits in 280mm enclosure with 128mm remaining. Cartridge (150mm) barely fits beside at this width. Extremely tight.

---

## Thickness Estimates (NOT MEASURED — PHYSICAL TEST REQUIRED)

Using elliptical pillow approximation (V = π/4 × W × L × T):

| Model | Calculated T (center) | Estimated Real T | Notes |
|---|---|---|---|
| Platy 1.0L | ~30mm | ~30-40mm | Shorter bag, more uniform fill |
| SoftBottle 1.0L | ~25mm | ~25-38mm | Longer bag, thinner profile |
| **Platy 2.0L** | **~38mm** | **~38-50mm** | Owner reports ~60mm max, 40mm compressed |

The owner has physical experience with these bags and reports:
- Full thickness: ~60mm max
- Compressed (light hand pressure, no spillage): ~40mm across full length
- These numbers are for the design — but should be verified with 2L Platy specifically

---

## Cap / Connector System

- **Thread: 28mm nominal** (PCO-like but with coarser pitch ~5/32" vs standard PCO 1810 at ~3.18mm)
- All Platypus narrow-mouth bottles use the **same threaded spout** — caps interchangeable across all sizes and models
- Cap OD: ~30mm
- Compatible with Platypus Drink Tube Kit (see below)
- **NOT perfectly compatible with standard soda bottle caps** (internal groove differences cause leaks)

---

## Drink Tube Kit

| Spec | Value |
|---|---|
| Tube ID | 6.35mm (1/4") |
| Tube OD | ~9.5mm (3/8") |
| Tube length | 1020mm (40") |
| Tube material | Polyurethane (PU) |
| Connector | Threaded closure (same 28mm thread) |
| Kit weight | 57g |

---

## Implications for Layout Research

### The 2L Width Problem

At 190mm wide, a 2L Platy bag is substantially wider than assumed. This has cascading effects:

**For stacked diagonal layout:**
- Bags consume 190mm of the 280mm width → only 90mm remaining
- Cartridge at 150mm wide cannot fit beside the bags
- **Options:** (a) widen enclosure to 340mm+ (190 + 150), (b) place cartridge above/below/in-front of bag stack, (c) use 1L bags instead, (d) accept that bags and cartridge share width at different depths

**For horizontal zone layout:**
- Side-by-side 2L bags = 380mm. Does not fit in any reasonable enclosure width.
- Stacked 2L bags in horizontal zone: 190mm wide, fine for width, but 350mm long at 18° incline needs ~332mm horizontal run + ~114mm vertical rise. Horizontal run exceeds 280mm enclosure width if bags run front-to-back (they run along depth, not width — 332mm exceeds 250mm depth, but fits in 300mm depth)

**The depth finding from under-sink research becomes even more important.** At 300mm depth, a 350mm bag at 18° incline has a 332mm horizontal run — fits with some compression or slight angle adjustment. At 250mm depth, it does not fit at all.

### 1L as Fallback

The Platy 1.0L at 152mm x 280mm is more manageable:
- Width: 152mm stacked, leaves 128mm beside — cartridge barely fits
- Length: 280mm at 63° diagonal needs only 127mm depth and 249mm height for stacking (with 80mm perpendicular thickness). This fits very comfortably.
- But 1L means more frequent refills (weekly for moderate users, twice-weekly for families)

### The Hoser 2.0L Alternative

The Hoser 2.0L is 152mm wide (same as 1L Platy!) but 406mm long. It includes the drink tube. It's wider capacity at the same width, achieved by being much longer. At 406mm, it exceeds the enclosure diagonal in any dimension unless the enclosure is taller or deeper. But if bags are permanent fixtures (assembled once in a well-lit workspace), the length might be manageable in a curved cradle.

---

## Data Gaps

1. **Thickness when full** — not published anywhere. Must measure physically.
2. **Thickness when compressed while full** — no data. Owner reports 40mm for what appears to be a 2L bag.
3. **Exact thread pitch** — one forum source says 5/32" (coarser than PCO 1810). Not manufacturer-confirmed.
4. **Spout neck outer diameter** — not found. Cap OD ~30mm but neck itself is smaller.
5. **Film thickness / material gauge** — not published.
6. **Whether the Platy 2.0L and SoftBottle 2.0L have different dimensions** — only the Platy 2.0L dimensions were found. A SoftBottle 2.0L may exist with different proportions.
