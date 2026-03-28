# Enclosure Concept Architecture

220W x 300D x 400H mm. PETG, FDM printed, dark matte finish. Multiple pieces required (depth and height both exceed 256mm bed).

---

## 1. Piece Split: Structural Tub + Cosmetic Front Panel + Removable Top

Three primary pieces, not two halves.

**Tub (structural monocoque):** A five-sided open-top box — floor, left wall, right wall, back wall, and a partial front wall that forms the lower front face (cartridge slot zone, Z=0 to ~130). The tub is the only structural piece. Every internal sub-assembly mounts to it: valve rack screws to the floor, bag cradle brackets mount to side walls and back wall, electronics shelf mounts to upper back wall. The tub carries all loads and defines all internal geometry. It prints in two halves split along a horizontal plane at approximately Z=200 (mid-height), joined permanently with alignment pins + CA glue + a tongue-and-groove lap joint. The seam falls behind the bags at mid-height — hidden from every viewing angle by the bags and cradle structure in front and the side walls around it.

**Rationale for horizontal split at Z=200:** The tub's depth is 300mm and height is 400mm, both exceeding the 256mm bed. Splitting horizontally at Z=200 yields two halves each approximately 300D x 200H, which fit on the bed printed on their backs (largest flat face down — the flat-on-bed pattern from the research). The 220mm width fits within 256mm. Each half prints with the exterior side wall on the build plate, giving smooth outer surfaces. The Z=200 seam is at bag-slab height, hidden by the diagonal cradle structure.

**Front panel (cosmetic, removable):** A single flat panel covering the upper front face from approximately Z=130 to Z=400 (the full width, 220mm). This panel carries the two display dock recesses (magnetic puck seats with cable exit holes) and the hopper funnel lip/bezel. It attaches to the tub via four cantilever snaps along its perimeter edges (two per side, snapping inward onto tub wall flanges) plus a tongue-and-groove along the bottom edge where it meets the tub's partial front wall. The snap hooks are internal — the exterior shows only a reveal-line seam at Z=130. This panel is removable for service access to the display reels, cable routing, and the upper interior.

**Rationale for the split at Z=130:** This height is where the cartridge dock zone ends and the bag/display/hopper zone begins. The seam falls at a natural functional boundary — the lower front face is the cartridge interaction zone (dock slot + knob), the upper front face is the display/visual zone. The functional transition makes the seam read as intentional design language rather than a manufacturing artifact (sharp-edge seam placement pattern). The lower tub front wall integrates the cartridge slot opening directly — no panel-over-slot alignment issues.

**Top panel (removable):** A flat lid with the hopper opening (100mm diameter hole, centered). Attaches to the tub upper rim via tongue-and-groove fit with two magnetic retention points (6x3mm neodymium discs). The top panel is removed for bag installation during manufacturing, hopper silicone insert removal for cleaning, and electronics access. It meets the front panel at Z=396-400 with a flush joint. The hopper funnel body mounts to the underside of this panel, hanging down into the interior.

**Total piece count:** 5 printed pieces (2 tub halves, 1 front panel, 1 top panel, 1 hopper funnel body). Plus the hopper silicone insert (purchased/cast, not printed).

---

## 2. Permanent Joins

**Tub halves to each other:** Alignment pins (4mm pegs into 4.3mm holes, four pairs along the perimeter) plus tongue-and-groove lap joint (3mm tongue, 4mm groove depth) along the entire split perimeter. Secured with CA glue. Once joined, the tub is one piece forever. The glue joint is non-serviceable by design — there is nothing inside the tub that requires splitting it. All service-accessible components are reached from the front (panel removal) or top (lid removal).

**Rationale:** The Mac Pro and Dyson patterns both separate permanent structure from removable access surfaces. The tub is permanent structure. Making it two pieces is a printing constraint, not a service constraint, so the join should be invisible and permanent. CA glue with alignment pins is fast, strong enough (the tub walls carry only static loads — bag weight, valve rack, electronics), and produces a nearly invisible seam when placed at Z=200 behind the bag cradle.

---

## 3. Seam Treatment

Three visible seams on the exterior:

**Seam A — Tub halves (Z=200, horizontal, all four exterior faces):** Tongue-and-groove with 0.1mm interference fit, glued. Post-assembly, this seam is sanded flush and becomes a hairline. On left, right, and back faces, this seam is at mid-height — a thin horizontal line on dark matte PETG. On the front face, this seam is hidden behind the front panel (which covers Z=130-400). Net: invisible on the front, hairline on the sides and back.

**Seam B — Front panel to tub (Z=130, horizontal across the front face):** A 2mm reveal line — intentionally wide, consistent, backed by a tongue-and-groove overlap that prevents light leakage. This is the primary design seam on the product. It separates the lower cartridge zone (with the 60mm knob as its centerpiece) from the upper display/hopper zone. The reveal line is a deliberate shadow line that reads as a designed element, following the PS5 reveal-line pattern. The 2mm width easily absorbs FDM tolerance variation.

**Seam C — Top panel to tub and front panel (Z=396-400, horizontal around the top perimeter):** A 1.5mm reveal line on three sides (left, right, back). On the front, the top panel meets the front panel — this joint is a continuation of the front panel's top edge and reads as a single crease around the product. The consistent width around the full perimeter makes it look intentional.

**All seams are horizontal.** No vertical seams on any face. The product reads as horizontal layers — a base (tub), a front surface (panel), a cap (lid) — stacked cleanly. Horizontal seams align with FDM layer lines rather than cutting across them, which produces cleaner edges.

---

## 4. Front Face Composition

The front face has two zones separated by Seam B at Z=130:

**Lower zone (Z=0 to Z=130) — Cartridge zone:** Part of the tub structure. Contains the cartridge slot opening (148W x 84H mm, centered in X). The 60mm knurled disc knob sits dead center of this zone, protruding 12mm from the surface. The knob is the visual anchor of the entire front face — the largest, most prominent element, and the only thing a user needs to find in a dark cabinet. The slot opening surrounds the knob with a 5mm chamfered frame that reads as a purposeful aperture (chamfered guide slot pattern). When the cartridge is inserted, its front face is flush with the enclosure front wall, and the knob appears to emerge directly from the enclosure surface. The remaining front wall area around the slot (36mm on each side, 46mm above the slot to Seam B) is flat, uninterrupted dark matte PETG.

**Upper zone (Z=130 to Z=400) — Display and hopper zone:** The removable front panel. Two circular display dock recesses (50mm diameter, 5mm deep) sit at Z=250-300, symmetrically placed. These are flush magnetic puck seats — when displays are docked, they sit flush with the panel surface, their round faces visible through the circular openings. When displays are removed (on their retractable cables), the recesses are shallow circular depressions — they read as designed features, not holes. A flat cat6 cable exit hole (8mm) at the center of each recess feeds the retractable reel behind the panel. Above the display docks, the panel is flat up to the top edge where it meets the top panel and hopper opening.

**Visual hierarchy (automotive dashboard pattern):** The knob dominates at the bottom — it is the largest single element on the front face, high-contrast (knurled texture vs smooth wall), and positioned at hand height in a cabinet. The two display pucks are secondary — smaller, symmetric, recessed, and positioned above the knob. The hopper opening is tertiary, partially hidden on the top surface, not visible from the front at all. A stranger sees: a dark surface with a big dial at the bottom and two small round screens above it.

---

## 5. Design Language

**Surface:** Dark matte PETG throughout. A single color, single material, consistent finish on every exterior surface. No color breaks, no contrasting accents, no secondary materials. The dark navy (#1a1a2e) from the iOS app and S3 display theme carries into the physical product if dark navy PETG filament is available; otherwise, matte black. The matte finish masks FDM layer lines (designed-in texture pattern from research), hides fingerprints in a dark cabinet, and reads as a unified product surface.

**Corners:** 6mm radius on all exterior vertical edges. 4mm radius on all exterior horizontal edges (top and bottom). The radii prevent warping during printing (controlled warping mitigation pattern), soften the form, and make the product feel finished rather than fabricated. No sharp corners anywhere on the exterior.

**Proportions:** The 220W x 300D x 400H box is a tall, narrow, deep form — roughly a 5:7:9 ratio. It reads as a vertical appliance (like a Breville espresso machine or a tower PC), not a squat box. The vertical orientation places the knob at the bottom (gravity-assisted cartridge seating) and the hopper at the top (gravity-assisted pour).

**The knob as design statement:** The 60mm knurled disc is the single expressive element on an otherwise restrained, dark, featureless surface. This contrast is the design language — minimal product surface, one deliberate tactile interaction point. The knob reads like a volume dial on a premium amplifier or the control knob on a Breville. It says "this is where you interact" without labels or instructions.

---

## 6. Service Access

Matched to access frequency per the research theme (tool-free for frequent, tools for rare):

**Hopper refill (weekly):** Lift top panel (magnetic retention, no tools). Pour flavor into funnel. Replace lid. The magnets provide enough hold for daily use but release with a firm upward pull. Two magnets, not four — the lid should feel light to remove, not like prying. The silicone funnel insert lifts out of the funnel body for rinsing.

**Display repositioning (occasional):** Pull display puck from front panel dock. The retractable cable extends to 1m. Place display anywhere (magnetic back adheres to fridge, cabinet door). To re-dock, just bring the puck near the dock recess — magnets self-align (MagSafe alignment pattern).

**Cartridge replacement (18-36 months):** Twist knob, pull cartridge. Fully tool-free, one-handed, in a dark cabinet. Already designed in the cartridge architecture.

**Bag installation (manufacturing only):** Remove top panel. Remove front panel (release four snaps by pressing inward at marked points on the panel edges — a firm push with thumbs releases each snap sequentially). This exposes the full interior from the front and top. Bags, cradle, and all tubing are accessible. This is a manufacturing/setup operation, not a user operation.

**Electronics service (rare, repair only):** Same as bag installation — remove top panel and front panel. Electronics are at the upper rear, accessible from above once the top panel is off. If deeper access is needed (PSU swap, rewiring), the front panel removal opens the full interior. No captive screws, no quarter-turn fasteners — the four snaps on the front panel are adequate for a once-a-year-or-never service event.

**Back panel (install only):** All back panel connections (water, soda, power, flavor lines) are permanent after installation. The back wall is part of the tub — it never comes off. Bulkhead fittings and cable glands are accessed from the rear of the cabinet during setup. No service panel needed on the back.

---

## 7. Top Surface and Hopper Treatment

The top panel is a flat lid with a single 100mm circular opening, centered in X, biased toward the front in Y (Y=8 to Y=78, per the spatial layout). The hopper funnel body hangs from the underside of this panel — it prints as a separate piece and attaches to the lid with screws from above (hidden by the silicone insert that sits inside the funnel).

The funnel opening sits flush with the top surface. A 3mm raised lip around the opening prevents spills from running across the top surface — it channels any drips inward. The silicone insert (removable, dishwasher-safe) sits inside the funnel body with its rim resting on the raised lip, flush with or 1mm above the top surface.

The rest of the top surface is flat, featureless dark matte PETG. When the silicone insert is in place, the top reads as a smooth surface with a single round opening — minimal, clean, functional. The hopper does not dominate the product form; it is a feature embedded in the surface, not a protrusion bolted on top.

---

## Key Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Split philosophy | Structural tub + cosmetic panels | Separates structure from surface (Theme 1). Tub is permanent; panels are removable for access. |
| Tub split plane | Horizontal at Z=200 | Both halves fit 256mm bed. Seam hidden behind bags. Exterior seam is hairline on sides, invisible on front. |
| Tub join method | Alignment pins + tongue-and-groove + CA glue | Permanent, invisible, adequate for static loads. |
| Front face split | Z=130, horizontal reveal line | Functional boundary (cartridge zone / display zone). 2mm reveal absorbs FDM tolerance. |
| Front panel attachment | 4x cantilever snaps + bottom tongue-and-groove | Tool-free removal for service. Snaps are internal, invisible from outside. |
| Top panel attachment | Tongue-and-groove + 2x magnetic retention | Tool-free removal for hopper access (weekly). Light hold, easy lift. |
| Design language | Dark matte mono-material, 6mm corner radii, knob as sole expressive element | FDM-friendly. Layer lines masked. Single material = unity. Knob contrast = interaction point. |
| Piece count | 5 printed (2 tub halves, front panel, top panel, hopper funnel) | Minimum pieces that satisfy bed constraints + service access needs. |
| Seam strategy | All horizontal, reveal lines at functional boundaries | Horizontal = aligns with layer lines. Reveal lines = forgiving of FDM tolerance. No vertical seams. |
| Service hierarchy | Top lid (magnetic, weekly) > front panel (snaps, rare) > tub (permanent, never) | Frequency determines mechanism (Theme 3). |
