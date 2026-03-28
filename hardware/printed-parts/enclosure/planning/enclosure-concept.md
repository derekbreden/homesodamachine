# Enclosure Concept

## The Design

A vertical rectangular tower, approximately 220 mm wide x 200 mm deep x 400 mm tall, with 8 mm radius edges and a subtle 3-degree draft on the side walls (narrower at the top). The enclosure splits horizontally into two pieces — a **tub** (lower 200 mm) and a **cap** (upper 200 mm) — joined permanently at a horizontal seam around the perimeter. The front face is the interaction face. The back face carries all plumbing connections. The pump cartridge slides in from the front bottom.

---

## 1. Piece Count and Split Strategy

**Two pieces: Tub and Cap.**

The target envelope is ~220 x 200 x 400 mm. The H2C build volume is 325 x 320 x 320 mm. At 400 mm tall, the enclosure cannot print as a single piece in any orientation. A horizontal split at the midpoint produces two halves of ~200 mm height each, both well within the 320 mm Z limit. Each half prints upright (open face up) with its footprint of ~220 x 200 mm fitting comfortably within the 325 x 320 mm XY bed.

Why horizontal, not vertical: A vertical split (left/right halves) would place the seam down the center of the front face — the most visible surface. A horizontal split places the seam at waist height, where it can follow a designed reveal line that reads as an intentional belt around the product. Horizontal also means both halves print as open-top tubs with no overhangs on their exterior walls, eliminating the need for support material on cosmetic surfaces.

Why two pieces and not more: Two pieces means one seam. Every additional piece adds a seam that must be made invisible. The solvent-weld-plus-vapor-smooth process erases seams, but fewer seams means less risk of a visible trace surviving. Two pieces also means two prints, two vapor-smoothing sessions (one per half, before assembly), and one welding operation. Three or four pieces would multiply every step of the finishing process.

**Depth rationale (200 mm):** The vision document suggested 300 mm deep, but the internal components do not require it. Two pumps at 117 mm depth plus tube routing clearance (30 mm front, 20 mm rear) fit within ~170 mm. Solenoid valves at 51 mm depth sit beside or behind the pumps. The Platypus 2L bags when filled are approximately 100 mm thick at their widest — they compress and conform. A 200 mm depth keeps the product's footprint compact (roughly the depth of a toaster) while providing adequate internal volume. If bag clearance proves tight during detailed layout, depth can grow to 220 mm without exceeding the bed.

### Internal Layout (Front to Back, Bottom to Top)

**Tub (lower half):**
- Front bottom: Pump cartridge dock (two Kamoer pumps side by side, cartridge slides in horizontally from the front face)
- Behind the pumps: Valve block (up to 10 Beduan solenoids in two rows of 5, oriented with tube ports facing left and right for manifold routing)
- Above the valve block, filling the remaining tub volume: Tubing routing channels and John Guest bulkhead fittings for the cartridge dock interface

**Cap (upper half):**
- Lower zone (just above the seam): Two Platypus 2L bags, stacked vertically or side by side depending on final bag-support cradle design. Bags hang from snap-fit clips at the top of the cap, with their outlet tubes routed downward through the seam plane into the tub's valve block.
- Upper zone: Funnel/hopper opening on top, with a removable dishwasher-safe funnel insert. The funnel throat routes into the bag fill line.
- Back wall (cap portion): Electronics shelf — ESP32, L298N motor drivers, DS3231 RTC, wiring harness. Positioned at the top rear where heat rises naturally and where the components are farthest from any liquid.

**Front face elements (spanning both halves):**
- RP2040 display and S3 display mount into the front face of the cap, in the zone between the bag area and the seam line. Both are flush-mount with snap-in retention from behind, and detachable via retractable cable.
- Air switch mounts into the front face between or beside the displays, same flush-mount system.
- Pump cartridge opening occupies the lower-center of the tub's front face.

---

## 2. Join Methods

**Perimeter seam (tub-to-cap): Tongue-and-groove solvent weld + interior snap-fits.**

The tub's top rim carries a continuous tongue (1.5 mm wide, 3 mm tall) running the full perimeter. The cap's bottom rim carries the matching groove. Acetone is applied to both mating surfaces with a fine brush. The halves are pressed together and held with clamps or tape for 60 seconds while the weld sets. The tongue-and-groove provides three functions: self-alignment during assembly, increased bonded surface area (the weld acts on the vertical faces of the tongue, not just the horizontal mating plane), and solvent containment (excess acetone wicks into the groove interior rather than squeezing onto visible exterior surfaces).

**Interior snap-fits** (6-8 permanent snaps distributed around the perimeter interior) provide mechanical retention independent of the weld. These are 90-degree-catch cantilever snaps molded into the tub's inner walls, engaging ledges on the cap's inner walls. They click during assembly and cannot be disengaged without breaking.

**Interior component mounting: Snap-fit clips and cradles printed into both halves.** Every internal component (valve block, electronics shelf, bag clips, display mounts) attaches to integral features of the tub or cap walls. No separate fasteners. Valve cradles are U-shaped channels with snap-over retention bars. The electronics shelf is a recessed pocket with snap tabs. Bag clips are hook features with living-hinge retention.

**Pump cartridge dock: Printed rails in the tub with John Guest fittings press-fit into the rear wall.** The cartridge slides on rails and seats against 4 tube stubs. The cam lever on the cartridge handles collet release. The dock is integral to the tub — no separate parts.

---

## 3. Seam Placement

**One exterior seam: the horizontal belt line where tub meets cap.**

This seam encircles the product at approximately 200 mm height (roughly the midpoint). It is designed as a **reveal line** — a deliberate 0.8 mm step or shadow gap that reads as an intentional design feature rather than a construction joint. The reveal is formed by the cap's lower edge being inset 0.8 mm from the tub's upper edge, creating a continuous shadow line around the perimeter.

**Why a reveal rather than flush:** A perfectly flush joint that fails to be perfectly flush (due to any print dimensional variance) looks like a defect. A designed reveal absorbs dimensional variance — the shadow gap can be 0.6-1.0 mm and still look intentional. The design-patterns research confirms this: the Nespresso CitiZ routes panel seams along its angular facets; the Breville places joints along finish-change boundaries. A deliberate line is better than a failed-invisible one.

**Vapor smoothing treats the seam:** After assembly, the entire enclosure is vapor-smoothed. The acetone vapor softens the edges of the reveal, rounding them slightly and giving them the same glossy-then-matte-cleared finish as every other surface. The reveal remains visible as a design line, but its edges feel smooth rather than sharp. The solvent weld itself (inside the tongue-and-groove) is fully fused and invisible — only the deliberate exterior step remains.

**No other exterior seams.** The tub is one piece. The cap is one piece. The cartridge opening and display cutouts are not seams — they are apertures with finished edges.

---

## 4. User-Facing Surface Composition

**Front face (the interaction face):**

Visual hierarchy, top to bottom:
1. **Funnel opening** — a smooth circular aperture at the top, inset with a contrasting material funnel insert (translucent or light-colored, signaling "pour here"). This is the topmost element but not visually dominant when the user faces the front.
2. **Displays and air switch** — the primary interaction zone. The RP2040 (0.99" round) and S3 (1.28" round with rotary knob) are flush-mounted circular elements set into the flat front face, slightly above the belt line. The air switch sits between or beside them. These three elements are the visual focal point of the front face — the only circles on an otherwise rectilinear form. Their dark screens against the dark navy body create subtle contrast; when illuminated, they are the brightest elements.
3. **Belt line (seam reveal)** — a thin horizontal shadow line spanning the full width, visually separating the upper "brain" zone from the lower "mechanical" zone.
4. **Pump cartridge door** — a rectangular panel at the bottom of the front face, flush with the surrounding surface. A finger pull (a shallow scoop, not a handle) allows the user to pull the cartridge forward. This panel is the cartridge's front face and moves with it.

**Side faces:** Continuous flat (slightly drafted) ASA surfaces. No features, no vents, no labels. The vapor-smoothed matte surface is the entire story.

**Top face:** The funnel opening, slightly recessed from the top surface edges, with a 2-3 mm lip to prevent drips from running down the sides. The rest of the top is a flat panel.

**Back face:** Utilitarian. Tube pass-throughs (PG7/PG9 cable glands) for water inlet, carbonated water pass-through (inlet and outlet), and two flavor dispensing outlets. A power cable entry. These are arranged in a grid with printed labels molded into the surface (debossed icons, not text — per the languageless icon principle). The back face is never visible in normal installation (under-sink or against a wall).

**Bottom face:** Flat, with 4 rubber feet (press-fit silicone bumpers). No visible fasteners.

---

## 5. Design Language

**Form:** Rectangular tower with 8 mm radius on all vertical edges. The top face transitions to the sides via a 5 mm radius, giving a slightly softer top. The bottom edges are a sharp 2 mm radius (the product sits firm). The 3-degree side draft makes the product subtly narrower at the top — it reads as stable and grounded without being obviously tapered.

**Surface:** Single material, single color, single texture across the entire exterior. Dark ASA (near-black or dark charcoal — matched as closely as possible to #1a1a2e), vapor-smoothed to eliminate layer lines, then matte 2K clear-coated. The result is a uniform satin-matte surface with no visible print artifacts. Under raking light, it reads as injection-molded plastic.

**Transitions:** Every aperture (display cutouts, cartridge opening, funnel opening, rear pass-throughs) has a 1 mm chamfer on its visible edge. No raw-cut holes. The chamfer signals "this was designed" rather than "this was cut."

**Contrast strategy:** The product body is a dark monolith. The only visual contrast comes from the display screens (illuminated), the funnel insert (lighter material), and the rear cable glands (black rubber against dark plastic — nearly invisible). This follows the single-texture rule from the design-patterns research: one dominant surface, with functional elements as subtle punctuation.

**No logos, no text, no labels on any user-facing surface.** The product identity comes from its form and material quality. Back-face connection labels are debossed icons only.

---

## 6. Service Access Strategy

**The pump cartridge is the only serviceable part.**

The cartridge slides into a horizontal dock that occupies the lower-center of the tub's front face. The dock consists of two printed rails (left and right) with a smooth floor. The cartridge's rear face carries 4 John Guest fittings (2 per pump: inlet and outlet). The dock's rear wall carries 4 matching tube stubs. When the cartridge is fully inserted, the fittings seat onto the tube stubs and the John Guest collets grip automatically.

A cam lever on the cartridge (see the cartridge research documents) provides insertion feel (a satisfying click at full seat) and actuates collet release during removal. The user pulls the lever, which retracts the collet rings, then slides the cartridge forward and out.

The cartridge opening in the front face is ~140 mm wide x ~70 mm tall (sized for two pumps side by side at 68.6 mm width each, plus a center divider and side clearance). The opening has a 1 mm chamfer and the cartridge's front face sits flush with the enclosure surface when docked.

**Everything else is permanent.** The valve block, wiring, bags, displays, tubing — all are assembled into the tub and cap before the two halves are welded together. There is no maintenance access to anything other than the cartridge. The bag fill operation uses the funnel (top, always accessible). Cleaning uses the automated clean cycle (firmware-controlled, no physical access needed). If a solenoid valve fails after years of use, the enclosure is the lifetime of the product — it does not come apart.

---

## 7. Manufacturing Constraints

### Print Orientation

**Tub:** Prints upright, open face up (the top rim where the cap attaches faces the ceiling). The exterior walls print as vertical surfaces — no overhangs, no supports on cosmetic faces. Interior features (valve cradles, cartridge rails, snap-fit ledges) may require supports, but these are interior and not visible after assembly.

**Cap:** Prints upright, open face up (the bottom rim where it meets the tub faces the ceiling). Same rationale — exterior walls are vertical, interior features may need supports. The funnel opening and display cutouts in the cap's front face are through-holes that require no supports (they are open to the interior).

### Support Requirements

- **Exterior surfaces: zero supports.** Both halves are open tubs. All exterior walls are vertical or nearly vertical (3-degree draft is well within ASA's 45-degree overhang limit).
- **Interior: supports likely needed** for horizontal shelves (electronics shelf), snap-fit ledge undersides, and the cartridge dock floor if it spans unsupported. PVA or BVOH soluble support (H2C dual-nozzle capable) is an option for complex interior geometry, but increases print time. Tree supports in ASA with manual removal is the simpler path for interior-only structures.
- **Display cutouts:** Through-holes in the front face of the cap. Printed as vertical walls — no supports needed.
- **Cartridge opening:** Through-hole in the front face of the tub. Same — vertical walls, no supports.

### Vapor Smoothing Considerations

- **Each half is vapor-smoothed individually before assembly.** This is safer than smoothing the assembled enclosure: each half is smaller, more uniform exposure, less risk of sagging on large flat panels.
- **Interior surfaces are masked or left unsmoothed.** Only exterior faces need the smooth finish. Interior structural features (snap catches, tongue-and-groove surfaces) should NOT be smoothed — the acetone would soften precision-fit surfaces and weaken snap-fit engagement. Interior masking is achieved by placing each half open-face-down in the vapor chamber, so the vapor primarily contacts the exterior.
- **The seam itself is welded after smoothing.** The tongue-and-groove surfaces are raw (unsmoothed) ASA, which welds better than glossy smoothed ASA (the solvent needs to penetrate the surface). The exterior reveal line is already smooth from the individual vapor treatments; the weld is internal.
- **Dimensional budget:** Vapor smoothing adds +0.05 to +0.15 mm per surface. Display cutouts and cartridge opening are designed with 0.2 mm extra clearance to absorb this. The tongue-and-groove joint is unaffected (interior, masked from vapor).

### Print Time Estimate

At 0.12 mm layer height with 4 walls and 20% gyroid infill, each half is approximately 200 mm tall with a ~220 x 200 mm footprint. Estimated print time per half: 18-30 hours depending on wall complexity. Total print time for both halves: 36-60 hours (two consecutive prints on the H2C). This is a weekend-plus commitment, which is normal for a part of this scale.
