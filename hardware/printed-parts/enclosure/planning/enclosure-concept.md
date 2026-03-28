# Enclosure Concept

## The Design

A vertical rectangular tower, approximately 220 mm wide x 300 mm deep x 400 mm tall, with 8 mm radius vertical edges and a subtle 3-degree draft on the side walls (narrower at top). The enclosure splits horizontally into two pieces -- a **tub** (lower ~200 mm) and a **cap** (upper ~200 mm) -- joined permanently at a horizontal seam. The front face is the interaction face. The back face carries all plumbing connections. The pump cartridge slides in from the front bottom.

### Why this envelope

The 300 mm depth comes from the Platypus 2L bags. When filled, each bag is roughly 330 mm long x 180 mm wide x 80 mm thick. The vision document proposes diagonal mounting with caps at the back-bottom and bag tops pinned to the front wall. In this orientation the bag's 330 mm length projects onto both the depth and height axes -- at roughly 45 degrees, the depth projection is ~235 mm and the height projection is ~235 mm. With wall thickness (4 mm per side) and clearance for the bag cradle structure, 300 mm of depth accommodates the diagonal bag span with margin for tube routing behind the bags. A shallower enclosure (200 mm) would force the bags to be nearly vertical, wasting their natural filled shape and risking kinks at the cap end.

The 220 mm width holds two pumps side by side (each 68.6 mm wide including bracket ears = 137 mm for the pair, plus a center divider and side clearance) and provides space for display cutouts on the front face.

The 400 mm height provides the vertical span for bags (upper zone) above the mechanical layer (pumps, valves, electronics in the lower zone), with the seam between tub and cap falling at the boundary between these two functional zones.

---

## 1. Piece Count and Split Strategy

**Two pieces: Tub and Cap.**

At 400 mm tall, the enclosure cannot print as one piece in any orientation on the H2C (320 mm Z limit). A horizontal split at ~200 mm produces two halves that each fit the bed:

- **Tub** (~220 x 300 x 200 mm): prints upright, open face up. Footprint 220 x 300 fits within 325 x 320 bed.
- **Cap** (~220 x 300 x 200 mm): prints upright, open face up (the bottom rim faces the ceiling). Same footprint.

Why horizontal, not vertical: A vertical (left/right) split places the seam down the center of the front face -- the most visible surface. A horizontal split places the seam at a designed belt line around the waist of the product.

Why two, not more: One seam is one risk. Each additional piece multiplies welding operations, alignment challenges, and potential for visible traces after vapor smoothing. Two pieces = one seam = one welding pass = one thing to get right.

### Internal Layout (Front to Back, Bottom to Top)

**Tub (lower half, ~200 mm tall):**
- Front-bottom: Pump cartridge dock. Two Kamoer pumps side by side in the cartridge, sliding in horizontally from the front face. The dock floor is ~20 mm above the enclosure bottom (space for feet and cable routing beneath). Pumps are ~63 mm tall and ~117 mm deep -- the dock occupies roughly the lower 80 mm x full depth of the tub.
- Behind and above the pumps: Valve block. Up to 10 Beduan solenoids arranged in two rows of 5. Each valve is 33 mm wide x 51 mm deep x 56 mm tall. Five valves across at 33 mm pitch = 165 mm, which fits within the 212 mm interior width (220 mm minus 2x 4 mm walls). Two rows at 56 mm height = 112 mm. The valve block sits above the pump dock, filling the upper portion of the tub.
- Rear wall of tub: John Guest bulkhead fittings for the cartridge dock interface (4 tube stubs) and valve block tube routing channels.

**Cap (upper half, ~200 mm tall):**
- Primary volume: Two Platypus 2L bags mounted diagonally. Each bag sits in a lens-shaped cradle that matches its natural filled profile. The bag caps (outlet fittings) are at the back-bottom of the cap, with tubes routed downward through the seam plane into the tub's valve block. The bag tops are pinned to the front wall.
- Upper rear: Electronics shelf -- ESP32, L298N motor drivers (3 boards), DS3231 RTC, wiring harness. Positioned at the top rear where heat rises and components are farthest from liquid.
- Top surface: Funnel/hopper opening with a removable dishwasher-safe funnel insert. The funnel throat routes into the bag fill line that runs down behind the bags.

**Front face elements (spanning both halves):**
- Cap front face: RP2040 display (0.99" round) and S3 display (1.28" round with rotary knob), flush-mounted with snap-in retention from behind. Air switch mounted in the same fashion. These sit in the lower portion of the cap's front face, in the zone between the bag cradles above and the seam line below. All three are detachable via retractable cable (snap out for external mounting).
- Tub front face: Pump cartridge opening occupies the lower-center.

---

## 2. Join Methods

**Perimeter seam (tub-to-cap): Tongue-and-groove solvent weld + interior snap-fits.**

The tub's top rim carries a continuous tongue (1.5 mm wide, 3 mm tall) running the full perimeter. The cap's bottom rim carries the matching groove. Acetone is applied to both mating surfaces with a fine brush before pressing the halves together. The tongue-and-groove provides self-alignment, increased bonded surface area (weld acts on vertical tongue faces), and solvent containment (excess acetone wicks into the groove interior rather than onto visible exterior surfaces).

**Interior snap-fits:** 8 permanent snaps distributed around the perimeter interior (2 per side, front, and back). These are 90-degree-catch cantilever snaps molded into the tub's inner walls, engaging ledges on the cap's inner walls. They click during assembly and require destruction to separate. The weld carries the cosmetic burden; the snaps carry the structural burden.

**Internal component mounting:** All interior components attach to integral printed features -- no separate fasteners.
- Valve cradles: U-shaped channels with snap-over retention bars, printed into the tub walls.
- Electronics shelf: Recessed pocket with snap tabs, printed into the cap's rear wall.
- Bag cradles: Lens-shaped shells with living-hinge retention clips, printed into the cap's side walls.
- Display and air switch mounts: Stepped circular pockets in the cap's front face with snap-ring retention from behind.

**Pump cartridge dock:** Printed rails in the tub floor with John Guest fittings press-fit into the rear wall. The cartridge slides on rails, seats against 4 tube stubs, and the collets grip automatically. A cam lever on the cartridge handles release.

---

## 3. Seam Placement

**One exterior seam: the horizontal belt line where tub meets cap.**

This seam encircles the product at approximately 200 mm height. It is designed as a **reveal line** -- a deliberate 0.8 mm step where the cap's lower edge is inset from the tub's upper edge, creating a continuous shadow gap around the perimeter.

Why a reveal rather than flush: A perfectly flush joint that misses by 0.1 mm looks like a defect. A designed reveal absorbs dimensional variance (0.6--1.0 mm range still reads as intentional). The Nespresso CitiZ routes seams along geometric facets; the Breville places joints along finish-change boundaries. A deliberate line is better than a failed-invisible one.

Vapor smoothing treats the seam: After individual smoothing and assembly, the reveal's edges are already rounded from the per-half vapor treatment. The reveal remains as a crisp design line with smooth edges. The solvent weld inside the tongue-and-groove is fully fused and invisible -- only the deliberate exterior step remains.

No other exterior seams. The cartridge opening, display cutouts, and funnel aperture are not seams -- they are designed apertures with chamfered edges.

---

## 4. User-Facing Surface Composition

**Front face (interaction face), top to bottom:**

1. **Displays and air switch** -- the visual focal point. Two flush-mounted circular displays (RP2040 0.99", S3 1.28") and the air switch sit in the upper portion of the front face, above the belt line. When illuminated, they are the brightest elements on the dark body. When the product is off or under a sink, they are subtle dark circles. This is the primary interaction zone.
2. **Belt line** -- the 0.8 mm reveal, spanning full width. Visually separates the upper "intelligence" zone from the lower "mechanical" zone.
3. **Pump cartridge door** -- a rectangular panel at the bottom-center of the front face, flush with the surrounding surface. A shallow finger-scoop (not a handle) allows the user to pull the cartridge out. The cartridge's front face is the door and moves with it.

**Top face:** The funnel opening, slightly recessed with a 2--3 mm lip to contain drips. A removable dishwasher-safe funnel insert (contrasting translucent or light-colored material) sits in the opening, signaling "pour here." The rest of the top is a flat panel.

**Side faces:** Continuous flat (3-degree drafted) surfaces. No features, no vents, no labels. Pure material.

**Back face:** Utilitarian. Pass-throughs for: carbonated water inlet and outlet (flow-through), tap water inlet (clean cycle), two flavor dispensing outlets, power cable. All connections use John Guest quick-connect fittings on tube stubs protruding from the back wall. Debossed languageless icons (not text) label each connection. This face is never visible in normal use.

**Bottom face:** Flat, with 4 press-fit silicone rubber feet. No visible fasteners.

---

## 5. Design Language

**Form:** Rectangular tower with 8 mm radius on all 4 vertical edges. Top-face-to-side transitions use a 5 mm radius (slightly softer crown). Bottom edges use a 2 mm radius (firm, grounded). The 3-degree draft makes the product subtly narrower at the top, creating visual stability without being obviously tapered.

**Surface:** Single material (ASA), single color (dark charcoal/near-black, closest available match to the #1a1a2e dark navy theme), single texture across the entire exterior. Vapor-smoothed to eliminate layer lines, then matte 2K urethane clear-coated. The result is a uniform satin-matte surface. Under raking light, it reads as injection-molded plastic.

**Transitions:** Every aperture -- display cutouts, cartridge opening, funnel opening, rear pass-throughs -- has a 1 mm chamfer on its visible edge. No raw-cut holes. The chamfer signals intentional design.

**Contrast strategy:** The body is a dark monolith. The only visual contrast comes from the display screens (illuminated circles), the funnel insert (lighter translucent material), and the cartridge's front face (same material, differentiated only by the finger-scoop shadow and the subtle parting line around it). This follows the single-texture rule from the design-patterns research: one dominant surface, with functional elements as subtle punctuation.

**No logos, text, or labels on any user-facing surface.** Product identity comes from form and material quality. Back-face connection labels are debossed icons only.

---

## 6. Service Access Strategy

**The pump cartridge is the only serviceable part.**

The cartridge occupies a horizontal dock in the lower-center of the tub. Two printed rails (left and right) guide the cartridge in. The cartridge's rear face carries 4 John Guest fittings (inlet and outlet per pump). The dock's rear wall carries 4 matching tube stubs. On full insertion, the fittings seat onto the stubs and the collets grip automatically.

The cam lever on the cartridge provides tactile confirmation (a click at full seat) and actuates collet release for removal. The user rotates the lever, which retracts the collet rings via the release plate, then slides the cartridge forward and out.

The cartridge opening in the front face is approximately 150 mm wide x 75 mm tall (two pumps side by side at ~68.6 mm each plus center divider and clearance, by ~63 mm pump height plus rail and floor clearance). The opening has a 1 mm chamfer. The cartridge's front face sits flush when docked.

**Everything else is permanent.** Valves, wiring, bags, displays, tubing -- all assembled before the two halves are welded. No maintenance access exists to any internal component other than the cartridge. Bag filling uses the funnel (always accessible). Cleaning uses the automated firmware-controlled clean cycle. If a solenoid fails after years, the enclosure has reached end of life.

---

## 7. Manufacturing Constraints

### Print Orientation

**Tub:** Prints upright, open face up (the top rim where the cap joins faces the ceiling). Exterior walls are vertical -- no overhangs on cosmetic surfaces. Interior features (valve cradles, cartridge rails, snap-fit ledges) may need supports, but these are interior-only and invisible after assembly.

**Cap:** Prints upright, open face up (the bottom rim faces the ceiling). Same logic. The funnel opening and display cutouts are through-holes that print as vertical walls -- no supports needed.

### Support Requirements

- **Exterior surfaces: zero supports.** Both halves are open tubs with vertical or near-vertical (3-degree draft) exterior walls -- well within ASA's ~45-degree overhang capability.
- **Interior: tree supports in ASA** for horizontal shelves (electronics shelf), snap-fit ledge undersides, and the cartridge dock floor. These are removed after printing and before assembly. Soluble support (PVA/BVOH via H2C dual nozzle) is available for complex interior geometry but adds print time; tree supports with manual removal are preferred for most features.
- **Display cutouts and cartridge opening:** Through-holes in the front face. Vertical walls, no supports needed.

### Vapor Smoothing Considerations

- **Each half is vapor-smoothed individually before assembly.** Smaller parts mean more uniform exposure and less risk of sagging on large flat surfaces.
- **Exterior surfaces only.** Each half is placed open-face-down in the vapor chamber so vapor primarily contacts the exterior. Interior surfaces (snap catches, tongue-and-groove, component mounting features) remain raw for dimensional accuracy and weld quality.
- **Dimensional budget:** Vapor smoothing adds +0.05 to +0.15 mm per surface. Display cutouts, cartridge opening, and the tongue-and-groove joint are designed with tolerance to absorb this. The tongue-and-groove surfaces themselves are unaffected (interior, shielded from vapor).
- **Seam welded after smoothing:** The tongue-and-groove mating surfaces are raw ASA, which welds better than glossy smoothed ASA (the solvent needs to penetrate the surface layer). The exterior reveal line edges are already smooth from individual vapor treatment.

### Bed Fit Verification

| Piece | Footprint | Height | H2C Bed (325 x 320 x 320) | Fits? |
|-------|-----------|--------|---------------------------|-------|
| Tub   | 220 x 300 | ~200   | 325 x 320 x 320           | Yes (220 < 325, 300 < 320, 200 < 320) |
| Cap   | 220 x 300 | ~200   | 325 x 320 x 320           | Yes (same) |

The 300 mm depth is the tightest dimension against the 320 mm bed limit, leaving 20 mm of margin. This is adequate but not generous -- if the final detailed design grows in depth, it will need to stay under 316 mm (320 mm bed minus ~4 mm for brim adhesion margin).

### Print Time Estimate

At 0.12 mm layer height, 4 walls, 20% gyroid infill, each half is approximately 200 mm tall with a 220 x 300 mm footprint. Estimated print time per half: 24-36 hours. Total for both halves: 48-72 hours (two consecutive prints). This is a multi-day commitment, typical for parts at this scale.
