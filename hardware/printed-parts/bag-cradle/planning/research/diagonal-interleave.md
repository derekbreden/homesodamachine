# Vision: Diagonal Interleave Layout

**Origin:** Product owner's conceptual vision, captured March 2026. Not a design decision — a possibility to inform and challenge existing research.

## The Core Idea

Instead of isolating components into horizontal zones (bags at bottom, dock in middle, electronics on top), components share vertical and depth space by using the full diagonal of the enclosure. Bags stretch from one corner to the opposite corner. Other components nestle into the spaces created by the bag angles.

This is a rejection of the "layer cake" assumption that pervades all current research.

## Spatial Description

Imagine looking at the enclosure from the right side (a cross-section showing height vs. depth):

```
FRONT                                          BACK
┌──────────────────────────────────────────────────┐ ← top
│ [HOPPER FUNNEL]  (angled piece,               [E]│
│   wide at front,  slanting down           [LCTRNX]│
│    toward back)                          [& FUSE] │
│ ○ ○ displays                                      │
│                                                   │
│ [CARTRIDGE]   ╲  top bag stretches diagonally  ╲  │
│  (front,       ╲   from top-front to            ╲ │
│   mid-height)   ╲    lower-back                  ╲│
│                  ╲  bottom bag below, same angle  ╲│
│                   ╲                               ╲│
└──────────────────────────────────────────────────┘ ← bottom
```

### Bags
- **Top bag:** Sealed (no-hole) end mounts at the top-front corner of the enclosure. Stretches diagonally down toward the lower-back corner, where the connector end sits at the low point for drainage.
- **Bottom bag:** Mounted directly below the top bag, same diagonal angle, one on top of the other.
- The bags use nearly the full diagonal of the enclosure (~470mm diagonal in a 280x250x400mm box), which could comfortably accommodate 2L bags (~350mm long) with room to spare for mounting hardware and clearance.
- The diagonal approach means bags don't compete with other components for vertical "zones" — they pass *through* the space that other components also occupy at different depths.

### Hopper Funnel
- Sits on the top side of the enclosure, angled to match or complement the bag angle below.
- The funnel is wide at the front (where the user pours) and narrows toward the back, with its lower surface sweeping across the space above where the top bag angles below it.
- This means the hopper can reach nearly to the front of the device for easy access, while its slanted body nests above the diagonal bag without wasting vertical space.

### Pump Cartridge
- Front-loading, positioned at the mid-section of the front face, or lower.
- Because the bags are diagonal (not occupying a full horizontal slice), the cartridge doesn't need to be above or below the "bag zone" — it shares some of the same vertical range, just at a different depth (front vs. the bag's mid-to-back diagonal).

### Displays
- Mounted on the front face, near the mid-section or higher.
- Round displays are thin — they take up almost no depth when flush-mounted.
- They coexist vertically with the cartridge and bags because they occupy a few millimeters of the front face, not a full horizontal zone.

### Electronics and Fuse Box
- Tucked into the top-back corner of the enclosure.
- The bags' diagonal path leaves the upper-back area open (bags are at their high point at the front, not the back).
- Electronics don't need to be in a full horizontal layer — they just need a pocket of space with ventilation.

## Why This Matters

### What it challenges
Every existing research document assumes a "zoned" architecture:
- `layout-spatial-planning.md` defines floor (0-4mm), bag zone (4-180mm), dock shelf (180-186mm), cartridge cavity (186-266mm), lever clearance (266-306mm), electronics shelf (306-310mm), electronics (310-400mm).
- Each zone is a horizontal slice. Components are confined to their slice.
- This means components compete for vertical budget. A taller bag zone steals from the dock zone. A taller electronics zone steals from lever clearance.

The diagonal interleave layout breaks this constraint. Components share vertical ranges by occupying different depths within the same height band. The bags pass through the middle of the enclosure diagonally, the cartridge sits at the front of that same mid-section, and electronics sit at the back of the upper section.

### What it enables
- **2L bags in a 400mm (or shorter) enclosure.** The diagonal of a 250D x 400H cross-section is ~472mm. A 2L Platypus bag at ~350mm fits easily along this diagonal with room for mounting hardware. No need to increase enclosure height.
- **More relaxed component placement.** Without rigid zone boundaries, the cartridge and electronics aren't fighting the bags for vertical space.
- **Hopper integration.** The angled hopper nests above the angled bags, using the same spatial principle — components following the diagonal rather than stacking horizontally.
- **Front face flexibility.** Displays, cartridge slot, and hopper access can be arranged vertically on the front face without each needing its own dedicated horizontal zone behind it.

### What it complicates
- **Tube routing.** Bags are no longer neatly below the dock — tubing must route from the bag connector (lower-back) to the cartridge (front-mid). This is a longer run but not necessarily problematic.
- **Internal structure.** No simple horizontal shelves to mount things on. Internal mounting becomes more 3D — brackets, angled supports, corner pockets.
- **Bag installation.** Diagonal mounting points are at two different heights and depths. User must stretch bag from one corner to another. May be less intuitive than hanging or laying flat.
- **Research invalidation.** The entire zone-based layout research (`layout-spatial-planning.md`, `bag-zone-geometry.md`, `dock-mounting-strategies.md`) would need rethinking. Not necessarily discarding — the component relationships still hold — but the spatial arrangement changes fundamentally.

## Open Questions

1. What does bag installation look like? User opens the front (or top?) panel, stretches the bag from front-upper mount to back-lower mount?
2. How does the cartridge dock coexist spatially with the diagonal bag path? Do they pass beside each other (bags to the sides, cartridge centered) or is the cartridge fully in front of the bags?
3. Can the hopper funnel drain into the bag connection point given the geometry? The bag connector is at the lower-back; the hopper is at the upper-front. Tubing must route between them.
4. Does this layout work better with bags side-by-side (left and right, both diagonal) rather than stacked (one above the other)?
5. What internal structural members are needed? Angled rails for bag mounting? Corner brackets for electronics?

## Relationship to Decision Points

This vision doesn't resolve the DPs — it suggests that the possibility space is wider than currently explored:

- **DP1:** A diagonal layout might allow a *shorter* enclosure while still fitting 2L bags, because bags use the diagonal, not the height.
- **DP2:** 2L bags become viable without increasing enclosure height, because they're not confined to a horizontal zone. The "1L was forced by 400mm height" logic breaks.
- **DP3:** Cartridge interface isn't fundamentally affected, but dock position and orientation might change.
- **DP4:** Fluid routing paths change (longer runs from bag connector to cartridge), but topology is the same.
