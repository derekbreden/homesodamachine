# Pump Cartridge Dock — Sub-Component Decomposition

Step 6d evaluation for all 3 dock printed parts.

---

## Part 1: Dock Cradle — PASS THROUGH

**Decision: No decomposition needed. Proceed to Step 6g with the full parts-dock.md.**

**Rationale:** The dock cradle is a single geometric paradigm: prismatic extrude-and-cut with simple cylinder and cone unions. Every feature is either a rectangular solid operation or a basic axially symmetric shape:

- **Side walls + rear wall** — box extrude minus interior cut to form U-shaped channel. Pure 2.5D.
- **Floor ledge** — the bottom 5 mm forms a perimeter shelf via a stepped interior cut (narrower interior below Z = 5). Prismatic.
- **C-channel rail grooves** — rectangular channels cut into side wall inner faces, running along Y. Prismatic cuts.
- **Groove entry chamfers** — linearly tapered widening of the grooves over the last 5 mm at the front opening. Achievable with angled cuts or lofted rectangles over a short 5 mm span. Simple 2.5D.
- **Tube stub through-holes (x4)** — cylindrical holes through the 7 mm rear wall along Y. Prismatic cylinder cuts.
- **Registration bosses (x2)** — tapered cones protruding from the rear wall inboard face, 10 mm base to 7 mm tip over 25 mm. A simple revolved trapezoid or CadQuery `circle().workplane(offset).circle().loft()`. Linear taper at 3.4-degree half-angle — no helical geometry, no complex sweeps.
- **Blade contact pockets (x4)** — rectangular blind pockets in the rear wall inboard face. Prismatic cuts.
- **Wire routing holes (x4)** — small cylindrical holes through the remaining 2 mm of rear wall behind each pocket. Prismatic cuts.
- **Snap-fit mounting lugs (x4)** — rectangular tabs with 45-degree lead-in ramps on the outer side walls. Box unions with angled cuts. Prismatic.
- **Floor plate snap tab pockets (x2)** — small rectangular recesses in the ledge top surface. Prismatic cuts.

No feature requires sweeps, lofts, helical geometry, or multi-axis curved surfaces. The tapered registration bosses are the most geometrically complex feature, but they are simple linear cone tapers — axially symmetric around Y at fixed X,Z positions. CadQuery handles these natively with a revolved trapezoidal profile or a two-circle loft.

All features are tightly coupled to the cradle body. The rear wall (7 mm thick) simultaneously houses tube holes, boss bases, blade pockets, and wire holes — decomposing through the wall would create problematic composition boundaries. The side walls contain both rail grooves and mounting lugs referencing the same surfaces. The part is geometrically complex in feature count (~12 distinct features) but uniform in paradigm — every operation is extrude, cut, cylinder, or simple cone.

---

## Part 2: Dock Floor Plate — PASS THROUGH

**Decision: No decomposition needed. Proceed to Step 6g with the full parts-dock.md.**

**Rationale:** The floor plate is a trivially simple part: a flat 150 x 120 x 3 mm rectangular plate with two small rectangular snap tabs (5 x 5 x 1 mm) on the underside and 0.5 mm edge chamfers. This is a single box extrusion with two box unions and chamfer operations. A single CadQuery agent will handle this in under 20 lines of modeling code.

---

## Part 3: Dock Face Frame — PASS THROUGH

**Decision: No decomposition needed. Proceed to Step 6g with the full parts-dock.md.**

**Rationale:** The face frame is a simple rectangular bezel: a 170 x 5 x 90 mm outer box with a 142 x 5 x 72 mm inner rectangular opening cut through it, plus 30-degree entry chamfers on the four inner edges (full 5 mm depth) and fillet treatments on exposed edges. All operations are prismatic:

- **Outer frame body** — box extrusion. Prismatic.
- **Inner opening** — rectangular through-cut. Prismatic.
- **Entry chamfers** — angled cuts or a lofted rectangular opening from the outer face dimensions (approximately 148 x 78 mm) to the inner face dimensions (142 x 72 mm) over the 5 mm depth. Single-direction loft between two rectangles — a basic CadQuery operation.
- **Edge fillets** — 3 mm on user-facing edges, 1.5 mm on inner opening edges. Native CadQuery fillet operations.

No decomposition boundary exists — the part is a single solid with uniform prismatic operations.
