# Enclosure — Conceptual Architecture

**Date:** 2026-03-29
**Inputs:** requirements.md, vision.md, synthesis.md, design-patterns.md, snap-fit-geometry.md, display-switch-dimensions.md, back-panel-ports.md, bag-frame/concept.md, pump-cartridge/concept.md
**Next step:** specification (per-part geometry definitions, dimensioned drawings)

---

## 1. Piece Count and Split Strategy

**Two printed parts: bottom half and top half.** The enclosure is 220 mm × 300 mm × 400 mm. The horizontal seam falls at 185 mm from the bottom.

### Build volume confirmation

| Half | Footprint | Print height | Build volume limit | Margin |
|---|---|---|---|---|
| Bottom half | 220 × 300 mm | 185 mm | 320 mm Z | 135 mm |
| Top half | 220 × 300 mm | 215 mm | 320 mm Z | 105 mm |

Both halves print in single-nozzle mode (325 × 320 × 320 mm). Neither half approaches any axis limit.

### Feature allocation by half

**Bottom half carries:**
- The full front-face component panel: three flush-mounted cutouts (RP2040 at 130 mm, S3 at 155 mm, KRAUS at 130 mm height from bottom). All three component faces are 30–55 mm below the seam. No component straddles the split.
- The dock opening in the front face (0–100 mm from the bottom), which gives cartridge access.
- The printed floor of the enclosure with snap pockets for the dock cradle.
- The 24 cantilever snap arms on the top seam edge.
- The 4 corner alignment pins on the seam face.
- The continuous tongue on the seam face (tongue grows upward in +Z — strongest print direction).
- An internal dividing wall at approximately 175 mm from the front face, separating the pump/valve zone from the bag zone. This wall serves as the rear stop for the dock cradle.
- Internal rib structure at the seam wall to resist warp across the 300 mm long faces.

**Top half carries:**
- All 5 rear wall ports (John Guest PP1208W-US bulkhead fittings) at 310 mm from the bottom, in three functional groups with recessed bays and directional icons.
- The 24 snap ledge pockets on the seam face.
- The 4 corner alignment pin sockets on the seam face.
- The continuous groove on the seam face (groove opens downward — prints as a slot without overhang when inverted).
- Two oval slots per inner side wall (4 total) for the bag-frame spine snap posts, at 235 mm and 275 mm from the bottom.
- Two contact-locating ledges per inner side wall (4 total) for the bag-frame cradle outboard edges, at 195 mm and 295 mm from the bottom. Each ledge is a 3 × 3 mm ridge running front-to-back, with a 45° chamfer on its underside.
- Two horizontal snap rails on the inner rear wall for the electronics tray, at 340 mm and 370 mm from the bottom.
- The full top face of the enclosure (400 mm from the bottom), including a reserved funnel-mount interface location.
- Boss reinforcement rings (22 mm OD) around each rear wall port hole on the interior face.

**Seam coherence:** The seam at 185 mm falls at the visual transition between the lower component zone and the upper bag zone. No functional feature spans the seam. All front-panel components, the dock opening, and the dock cradle are wholly in the bottom half. All rear wall ports, the spine slots, the cradle ledges, and the electronics rails are wholly in the top half.

---

## 2. Join Methods

### Who carries what

**Snap arms: bottom half.** The 24 cantilever arms protrude inward from the interior of the top edge of the bottom half's walls. Arms flex in the XY plane (parallel to the build plate when the bottom half prints base-down). The hook undercut faces downward in final assembly — inside the assembly cavity, accessible for designed break-away support removal before the halves are joined.

**Snap ledge pockets: top half.** Rectangular slots open downward into the top half's interior seam-face perimeter. These print as clean slots in a wall face — no overhang — when the top half is printed seam-face-down (inverted).

**Alignment pins: bottom half.** Four pins, one at each corner, 10 mm from each corner edge to pin centerline. Pins grow upward in +Z from the seam face of the bottom half.

**Alignment pin sockets: top half.** Four matching blind sockets open downward in the seam face of the top half, printed as pockets in a face-down build. No overhang.

**Tongue: bottom half.** Grows upward from the seam face of the bottom half, immediately inside the snap arm zone, 2 mm setback from the exterior wall face. Printed in the natural +Z growth direction — full layer support throughout its height.

**Groove: top half.** A continuous slot opening downward in the seam face of the top half. When the top half is printed seam-face-down, the groove prints as an upward-growing slot cavity. No overhang concern.

### Tongue-and-groove placement

The tongue-and-groove runs along the **interior** of the mating faces, not the exterior. It is set 2 mm inward from the exterior wall surface. This placement:
- Leaves the exterior wall surface continuous and uninterrupted (no tongue visible on the exterior)
- Keeps the tongue inside the snap arm zone where it is captured and braced
- Ensures the tongue enters the groove before the snap hooks engage (4 mm tongue height vs. 1.2 mm hook height means the halves are groove-located before any arm deflects)

### Assembly sequence

1. **Align on corner pins.** The assembler places the top half over the bottom half, locating the four corner pins into their sockets. The 1.0 mm × 45° chamfers on both pins and sockets guide entry. The halves are now constrained in X and Y; the seam is not yet closed.

2. **Tongue enters groove.** As the top half descends, the tongue (4 mm tall, 0.5 mm × 30° tip chamfer) enters the groove before the snap hooks are reached. At full tongue engagement the halves are further constrained laterally (±0.05 mm) and the seam face alignment is set. The user feels the tongue guiding entry as a smooth, consistent lowering resistance.

3. **Snap arms engage.** The 30° lead-in on each hook converts the remaining downward travel into lateral arm deflection. All 24 arms engage nearly simultaneously because the tongue-and-groove has already leveled the halves. The user presses both palms along the 300 mm faces — approximately 60 N per palm, 120 N total. All 24 hooks clear their ledge pockets and drop in within 1–2 mm of travel.

4. **Definitive stop.** All 24 hooks engage, the seam faces contact, and the joint stops moving. The assembler feels and hears a firm, dense click-stop — 24 snaps engaging in near-simultaneous progression as the palms walk the force along the 300 mm faces. There is no ambiguity: the halves either seat fully (firm stop) or do not seat (user can feel one face is proud). Partial engagement on a single face is detectable because the seam step is visible and tactile.

5. **Confirmation.** After pressing, the assembler can verify all four corners are flush and the 0.5 mm reveal is continuous around the full perimeter. Any unbridged gap indicates an unengaged snap, which can be located and pressed individually.

**No tools required.** The joint is permanent on engagement.

---

## 3. Seam Placement and Treatment

### Location

The seam runs around the full 1040 mm perimeter at exactly 185 mm from the bottom of the enclosure. This height is the visual boundary between:
- **Below:** the front-panel component zone (displays, air switch, pump cartridge dock)
- **Above:** the bag zone (bags on their diagonal cradles, spine, funnel)

The eye expects a line here because there is a real design change on either side of it. The seam does not fall in the middle of any featureless flat surface.

### Cross-section profile

The seam is a shadow-line detail. In cross-section, from outside the enclosure:

```
                    │← 0.5 mm reveal →│
  Top half          │                 │
  exterior wall ────┘                 │  ← top half exterior, ends 0.5 mm below seam plane
                                      │
                    ← shadow gap →    │  (0.5 mm dark recess, depth controlled by reveal)
                                      │
  Bottom half  ────────────────────────  ← bottom half exterior, flush to seam plane
  exterior wall
```

The top half's exterior wall extends **0.5 mm below the seam plane**, lapping over the bottom half's exterior wall. The bottom half's exterior wall terminates at the seam plane. The 0.5 mm step creates a consistent dark shadow that runs the full 1040 mm perimeter.

Inside the seam (not visible externally), from outer wall to inner wall:
- Exterior wall (2 mm nominal thickness)
- 2 mm setback to tongue-and-groove centerline
- Tongue (bottom half, 3.0 mm wide × 4.0 mm tall) in groove (top half, 3.1 mm wide × 4.2 mm deep)
- Snap arm zone inboard of tongue
- Interior enclosure volume

### Exterior appearance

The exterior at the seam shows a single, crisp, continuous dark line. The line is produced by the 0.5 mm shadow recess between the top half's lapping exterior wall and the bottom half's wall face. Viewed at normal standing distance (arm's length), this reads as a designed horizontal band — identical in language to the seam on the Nest Audio or similar consumer electronics. It does not read as a tolerance gap or a manufacturing parting line.

**Which half is proud:** The top half is proud by 0.5 mm. Its exterior wall extends below the seam plane, covering the bottom half's top edge and capturing any elephant's foot flare on the bottom half's top perimeter. This also means the top half's bottom edge is the visible design line — a crisp horizontal step running at 185 mm from the bottom, dividing the component zone from the bag zone.

**The seam is a design feature.** It coincides with the only real visual transition on the enclosure exterior. It requires no additional treatment (no color band, no tape, no texture change). The shadow line is sufficient.

Where snap arms interrupt the continuous shadow-line lip geometry, the lip tapers back to zero over 5 mm on each side of the arm location, per design-patterns.md guidance, so the exterior line remains consistent at those points.

---

## 4. User-Facing Surface Composition

### Front face

The front face is 220 mm wide × 400 mm tall. It presents two distinct horizontal zones, divided by the seam.

**Lower zone (0–185 mm from bottom) — component zone:**

Smooth, featureless matte black surface except for three flush-mounted circular/square cutouts in its upper portion and the dock opening at its bottom.

The three component cutouts occupy a band from approximately 107 mm to 179 mm from the bottom (from the bottom edge of the KRAUS/RP2040 cutout to the top edge of the S3 cutout). They are arranged left-to-right: RP2040 (small, 33 mm diameter, centered at 55 mm from left edge, 130 mm from bottom) — S3 (medium, 48.2 mm square cutout, centered at 110 mm from left, 155 mm from bottom) — KRAUS (medium, 31.75 mm through-hole with 47.6 mm cap sitting flush, centered at 165 mm from left, 130 mm from bottom). Each component face is flush with or 0.5 mm recessed behind the enclosure face. Each cutout opening has a 0.5 mm × 45° chamfer on the enclosure face edge.

The visual hierarchy reads: S3 is the dominant element (largest face diameter, centered, highest position in the band), flanked by the RP2040 and KRAUS at equal height slightly lower. The three elements are visually balanced without being mechanically symmetrical.

Between the seam at 185 mm and the top of the component band at approximately 179 mm, there is a 6 mm smooth face — a visual breathing margin between the component zone and the seam line.

The dock opening occupies the band from 0 to approximately 100 mm from the bottom. The cartridge front face is flush with the enclosure face when inserted. The dock opening is a rectangular opening sized to the dock cradle T-rails with a 2 mm × 45° chamfer on the enclosure face edge. It reads as an aperture, not as a hole — the cartridge fills it.

**Upper zone (185–400 mm from bottom) — bag zone:**

Smooth, featureless matte black surface. No cutouts, no protrusions, no visible features. The funnel is a separate mechanism above the enclosure top face — the front face of the upper zone is uninterrupted. This surface reads as a solid planar volume behind which something is contained.

### Side faces

Both side faces are smooth and featureless on the exterior. No cutouts, no grilles, no access points. Both faces are identical in exterior appearance.

Interior side walls carry structural features (spine slots, cradle ledges, snap arms) but these are not visible from the exterior.

No draft on exterior vertical walls (the surfaces are nearly 400 mm tall vertical walls that would require visible taper — at the scale of this enclosure, a 1° draft over 400 mm produces a 7 mm difference in width between top and bottom, which is visible and contradicts the appliance-grade monolithic reading). The walls print vertically and read as flat planes.

### Top face

The top face is the build-plate face of the top half (printed seam-face-down, so the top face is the last printed surface in +Z — actually it is the build-plate face of the top half's inverted print). Wait — when the top half is printed seam-face-down (inverted), the **top face of the enclosure** is on the build plate. This is the smoothest face.

The top face is smooth with one reserved interface: a funnel-mount opening or collar location at approximately 110 mm from the front face, centered left-to-right. The funnel sub-assembly is not yet designed; the top face reserves a zone (approximately 80 mm × 60 mm centered at that location) that the funnel assembly mounts into. No feature is designed here in this document — only the zone is reserved and must not be obstructed by internal top-face features.

**The top face is the primary quality surface** of the enclosure: smooth, flat, matte black, build-plate finish. It is the first face a user sees when looking down at a countertop-mounted device.

### Bottom face

The bottom face is the build-plate face of the bottom half. It is smooth from the FDM build-plate contact.

The bottom face carries four printed feet — small circular pads (approximately 15 mm diameter, 3 mm tall) at the four corners, inset 15 mm from each corner edge. Feet serve two purposes: they prevent the enclosure from sliding on smooth countertop surfaces (the feet have a flat top with space for adhesive-backed rubber pads if desired) and they protect the otherwise featureless bottom face from contact wear. The feet are printed integral to the bottom half floor — no separate parts.

The 0.3 mm × 45° elephant's foot chamfer is applied to the bottom perimeter edge of the bottom half to prevent first-layer flare from creating visible irregularity at the foot perimeter. This is standard for any build-plate-down print where the bottom edge is a design feature.

### Rear face

The rear face is smooth matte black with the five John Guest port fittings as the only features. The ports are organized in three functional groups:

**Group A (left):** Two ports — carbonated water inlet and outlet — in a 1.5 mm deep recessed rectangular bay. Bay margins 5 mm per side beyond the fitting group extent. An inward arrow icon below the inlet fitting and an outward arrow icon below the outlet fitting (raised 0.8 mm relief, 1.5 mm stroke width, 8 mm × 6 mm arrows, centered 5 mm below each port centerline).

**Group B (center):** One port — tap water inlet — with a shallow 1.0 mm boss recess (30 mm diameter) that visually distinguishes it from the grouped pairs at left and right. No directional arrow — a single isolated port communicates its role by isolation.

**Group C (right):** Two ports — Flavor 1 and Flavor 2 outlets — mirroring Group A. Recessed bay, same spec. Both arrows point outward.

The bilateral symmetry (two ports left, one port center, two ports right) makes the system legible before the user traces any tube: inlets on the left, the single utility connection in the center, outputs on the right. Combined with the directional icons, the rear panel reads as a designed interface, not a perforated surface.

All five fittings are at 310 mm from the bottom — in the upper portion of the top half (125 mm above the seam), all on one horizontal band.

---

## 5. Design Language

### Material: ASA

The enclosure uses **ASA**, matching the pump cartridge. Reasoning:

The pump cartridge concept chose ASA explicitly for UV stability (countertop placement near windows), surface crispness, and matte finish quality. The enclosure is the primary exterior surface — the largest visible face of the product. Using ASA on the enclosure and PETG on the cartridge would produce visibly different surface character between the two most-visible parts of the machine. The vision describes a unified appliance appearance: "it will look and feel amazing no matter where they put it." Material consistency between the enclosure and cartridge is required for this.

ASA on the Bambu H2C with the enclosure heated prints reliably with low warp and good layer adhesion. The enclosure's 300 mm long faces are at moderate warp risk in ASA (higher than PETG), but the seam wall box-section rib structure in the synthesis addresses this. The enclosure printer is already proven for ASA (per requirements.md support list).

Internal parts (bag frame spine, cradles, caps) may remain PETG — they are interior and share no visible surface with the exterior.

### Color: matte black throughout

Single color, consistent with the matte black faucet specified in the vision. Both halves are the same color — the seam line divides the enclosure into two visual zones without implying two different materials or identities. The shadow line seam reads as a horizontal register on a monolithic black surface.

### Surface finish

The highest-quality surface on each half is the build-plate face.

| Half | Build-plate face | What that face is |
|---|---|---|
| Bottom half | Bottom (feet) face | Bottom of enclosure — visible on countertop placement, but not the primary user-facing surface |
| Top half | Top face of enclosure | Seen from above on countertop placement — primary quality surface |

The front face of the bottom half is a vertical wall, printed in Z. It is not a build-plate face. At 0.1 mm layer height with the Bambu H2C's Lidar-based calibration, a vertical FDM wall in ASA at 0.1 mm layers is smooth enough to read as a consumer surface at normal viewing distance. No post-processing is required; the layer lines are below visual threshold at arm's length for 0.1 mm layers in a matte material.

The rear face of the top half is a vertical wall (when the top half is printed inverted). Same quality standard applies.

### Corner treatment

**Exterior vertical edge corners (the four long vertical edges of the enclosure body):** 3 mm fillet radius. Reasoning from design-patterns.md consumer precedents: the Nest Audio uses a soft-radius edge; the Vitamix base uses a similar 3–4 mm radius. A 3 mm radius at the FDM scale is well above the 0.4 mm minimum printable feature and reads as deliberately rounded rather than accidentally blunt. Below 2 mm reads as a sharp corner that was meant to be sharp. At 3 mm, the corner invites touch — consistent with the vision's "feel like a consumer product."

**Top and bottom horizontal edge corners:** 2 mm fillet radius. Slightly tighter than the vertical edges because the top and bottom faces are smaller in surface area; a 3 mm radius at those transitions would appear visually heavy relative to the face size.

**Seam edge (the 0.5 mm reveal):** No fillet. The reveal is a sharp horizontal step — the sharpness is what makes it read as a designed line rather than a soft transition. The 0.3 mm × 45° chamfer is on the leading (inner) edge of the reveal lip to ease assembly, but the exterior-facing edge of the reveal is sharp.

**Dock opening edges:** 2 mm × 45° chamfer around the perimeter. The chamfer communicates "insert here" and reads as an intentional opening frame.

### Draft angles

No draft on any exterior wall. The enclosure is 400 mm tall with a 220 × 300 mm footprint, and both halves print standing upright relative to the Z axis. Draft on a printed part is not required for release from the build plate (FDM is not injection molding — there is no mold to release from). Adding draft to a tall vertical wall of a consumer appliance would produce a trapezoid silhouette rather than a rectangular one, which contradicts the appliance design language. Vertical walls stay vertical.

Interior walls that carry locating ledges or snap features have 1° draft on non-functional faces only, for printability of those specific features — but this does not affect the exterior silhouette.

### Wall thickness

**Exterior walls: 2.4 mm nominal (6 perimeters at 0.4 mm nozzle).** Reasoning:
- The minimum structural wall is 1.2 mm (3 perimeters) per requirements.md. That is insufficient for an exterior enclosure wall that must resist handling loads, cosmetic dents, and the assembly force of 120 N distributed around the perimeter.
- The snap arms grow from the interior of the seam-edge wall. The wall must accommodate the snap arm root (2.0 mm arm thickness) on the interior face plus the exterior wall surface. With a 2.4 mm wall, the arm root is a feature that terminates before reaching the outer surface — the exterior wall remains uninterrupted.
- At 2.4 mm, the seam wall with a box-section rib (outer wall + inner wall + ribs at 40 mm intervals aligned with snap positions) achieves 8× bending stiffness over a single wall, per the snap-fit-geometry.md warp analysis. This is required for the 300 mm long faces.
- 2.4 mm is consistent with the pump cartridge's structural wall (which uses 1.6 mm for load-bearing elements and 1.5 mm for cosmetic surfaces). The enclosure exterior is not carrying the structural loads that the cartridge mounting plate carries, but it is the consumer-facing surface and 2.4 mm gives a confident, solid feel.

**Rear wall at port locations: 3.5 mm** (within the 3.0–4.0 mm recommended range from back-panel-ports.md for PP1208W fitting retention, while staying well under the 15–16 mm maximum panel thickness for the fitting).

**Floor of bottom half: 2.4 mm.** Carries the dock cradle snap pockets — local boss geometry around those pockets will build up to 5–6 mm where needed.

**Interior dividing wall (pump/valve zone): 2.0 mm.** Structural enough to serve as the dock cradle rear stop; not a cosmetic surface.

---

## 6. Service Access Strategy

### Pump cartridge dock opening

The pump cartridge is the only user-removable item. The dock opening is in the front face of the bottom half, at the bottom (0–100 mm from the enclosure base, full 220 mm face width minus the wall thickness on each side — approximately 215 mm wide × 95 mm tall, sized to match the dock cradle's T-rail opening with a 2 mm × 45° chamfer all around).

The cartridge slides in and out horizontally, parallel to the floor. The dock opening frames the cartridge front face: when inserted, the cartridge front face is flush with the enclosure front face. The cartridge is centered on the front face; its 155 mm width sits symmetrically within the 220 mm face width, with approximately 30 mm of solid enclosure wall on each side.

The user reaches in with one hand palm-up to squeeze and release. The opening is tall enough that the user's hand fits comfortably without touching the dock opening edges. There are no doors, no covers, no latches on the dock opening — it is always open, because the cartridge is always present (the only time it is absent is during replacement, which takes seconds).

### Display and air switch removal

The RP2040, S3, and KRAUS occupy circular or square through-cutouts in the front face. Each is retained by a printed mechanism behind the panel:
- **RP2040:** Twist-lock (bayonet-style) printed retention ring behind the 33 mm cutout. The user pushes the module slightly inward, rotates it, and it releases forward through the cutout. The 33 mm cutout diameter accommodates the full module exit from the front.
- **S3:** A printed bracket captures the M2.5 mounting holes. The bracket unclips from behind, and the module then passes forward through the 48.2 mm × 48.2 mm square cutout. The user accesses the bracket through the cutout by reaching behind the module with a finger.
- **KRAUS:** Self-retaining with its ABS nut. The user threads off the nut from behind the panel (accessed through the dock opening below, or the module can be pushed from behind), and the switch withdraws forward.

In all three cases, the user never opens the enclosure. Service is front-access through the existing cutouts.

### No other access provisions

The enclosure has no doors, no removable panels, no access hatches beyond the dock opening. The user never needs to open the enclosure — cleaning uses the dispensing pathway, bag filling uses the funnel at the top, and the only replacement event is the pump cartridge.

---

## 7. Manufacturing Constraints

### Bottom half

**Print orientation:** Base (bottom face) on the build plate. The bottom half prints standing upright: Z height is 185 mm, well within the 320 mm limit.

**Front-face component cutouts:** The three cutouts (RP2040 at 33 mm, S3 at 48.2 mm, KRAUS at 31.75 mm) are in the vertical front wall. When printed base-down, these cutouts are holes in a vertical wall — they print cleanly as through-holes with no overhang concern. The 0.5 mm × 45° chamfers on the cutout edges are on the exterior face, which is a vertical surface — no overhang. The inner face chamfers (if any) are also on vertical surfaces.

**Snap arms on the top edge:** The snap arms grow inward from the interior of the top seam-face perimeter wall. They are horizontal cantilever arms printed in the XY plane. The arm body (18 mm long, 2.0 mm thick, 8 mm wide) bridges horizontally at the top of the print — the arm is at the highest Z point of the part and prints after the wall body has been established. The hook at the arm tip has a 1.2 mm undercut on its lower face. This undercut faces downward in the print (since the arm is near the top of the Z stack). This requires a designed frangible support at the hook underside: a 0.2 mm interface gap with 0.3 mm × 0.3 mm break-away tabs at 2 mm and 6 mm from one edge per hook. The tabs are inside the assembly cavity and are snapped off before joining the halves.

**Dock opening in the front face:** The dock opening is a large rectangular cutout in the lower front wall (0–100 mm from the bottom, ~215 mm wide). When printed base-down, this opening is in a vertical wall — no overhang concern for the opening itself. The top edge of the dock opening (the horizontal lintel at ~100 mm from the base) is a horizontal feature in the print. At approximately 215 mm wide, this span far exceeds the 15 mm bridge limit. Resolution: the lintel is not a bridge — it is the top wall of the opening, and the opening itself means there is no surface to bridge across. The opening simply terminates the wall. The walls to each side of the opening carry the load to the floor. No support needed.

**Tongue on the seam face:** The tongue (4.0 mm tall, 3.0 mm wide) grows from the interior seam face at the top of the print. It grows from the top of the wall, which is the last material laid down. Full layer support throughout the tongue height. No overhang. The 0.3 mm × 45° chamfer at the tongue base and the 0.5 mm × 30° chamfer at the tongue tip both print cleanly as they are on the sides or top of an upward-growing feature.

**Alignment pins:** Four pins, one per corner, 4.0 mm diameter, 8.0 mm tall, growing from the seam face. Printed at the top of the Z stack. They are vertical cylinders with chamfered tips — no overhang, no support needed.

**Build volume check:** Bottom half bounding box: 220 × 300 × 185 mm. Fits within 325 × 320 × 320 mm with 105 mm X margin, 20 mm Y margin, 135 mm Z margin. **Confirmed.**

### Top half

**Print orientation:** Enclosure top face on the build plate, printed inverted. The seam face is the highest Z point. Z height is 215 mm, well within the 320 mm limit.

**Rear wall port holes:** The 5 PP1208W port holes (17.2 mm each) are in the rear vertical wall of the top half. When the top half is printed inverted (top face down), the rear wall prints as a vertical surface with the port holes as circles in a vertical plane — no overhang. The boss rings on the interior side of the rear wall are horizontal annular flanges. When printed inverted, these bosses are at height positions along the print (not at the top or bottom) — they are horizontal discs protruding inward from the rear wall. A horizontal disc protruding from a vertical wall is a 90° ledge — this is an overhang concern. Resolution: add a 45° chamfer on the underside of each boss ring (the face pointing toward the build plate in the inverted print). This converts the 90° ledge into a 45° ramp, eliminating the overhang. The chamfer does not affect the nut-clamping function; the flat face of the boss ring that contacts the locking nut is on the opposite (interior-facing) side.

**Groove on the mating face:** The groove (3.1 mm wide, 4.2 mm deep) opens downward in the final assembly — but when the top half is printed inverted, the groove is at the top of the print (the seam face is the last surface printed). The groove prints as an upward-opening slot cavity in the last few millimeters of the print. No overhang concern — the slot walls grow upward and the slot opening is at the top. Clean geometry.

**Snap ledge pockets:** These are rectangular slots in the seam face wall, opening downward in assembly but opening upward when the top half is printed inverted. They print as upward-opening pockets at the top of the Z stack. No overhang. The 90° ledge face that retains the snap hook faces downward in assembly — this is the underside of the pocket's retaining lip. When printed inverted, this face is on the upper side of the pocket — it prints with full support from the wall material below it. No overhang.

**Internal mounting features:**
- *Spine oval slots:* 10 mm × 6 mm oval openings, 8 mm deep, in the inner side walls. The inner side walls are vertical surfaces. When printed inverted, these are holes in a vertical wall — no overhang. The retaining rim (1.5 mm) is a lip inside the slot. This lip is a 90° ledge inside a hole in a vertical wall — it overhangs inward. A 45° chamfer on the leading (lower in assembly, upper in inverted print) edge of the retaining rim eliminates the overhang. Local wall thickening at the slot locations (10–12 mm total wall depth vs. 2.4 mm elsewhere) requires boss geometry on the inner side wall — these bosses print as vertical wall protrusions with no overhang.
- *Cradle locating ledges:* 3 × 3 mm ridges on the inner side walls, running front-to-back. When printed inverted, these are horizontal features on a vertical inner wall. They are horizontal ledges — overhangs. Per synthesis resolution, each ledge gets a 45° chamfer on its underside, converting the 90° overhang to a 45° ramp. The vertical stop face (the face the cradle edge butts against) remains perpendicular.
- *Electronics tray snap rails:* Horizontal ledges on the inner rear wall at 340 mm and 370 mm from the bottom. When printed inverted, these are at (400 − 370) = 30 mm and (400 − 340) = 60 mm from the build plate. They print as horizontal ledges on a vertical wall — 90° overhangs. Same resolution: 45° chamfer on the underside of each rail. The retaining lip (the feature the tray clips under) faces toward the build plate in the inverted print — also an overhang. The retaining lip receives a 0.2 mm interface gap frangible support (0.3 mm break-away tabs). These are interior surfaces, removal is accessible from the open seam face before assembly.

**Build volume check:** Top half bounding box: 220 × 300 × 215 mm. Fits within 325 × 320 × 320 mm with 105 mm X margin, 20 mm Y margin, 105 mm Z margin. **Confirmed.**

---

## Summary

### Part List

| Part | Qty | Material | Print orientation | Bounding box |
|---|---|---|---|---|
| Enclosure bottom half | 1 | ASA, matte black | Base on build plate | 220 × 300 × 185 mm |
| Enclosure top half | 1 | ASA, matte black | Top face on build plate (inverted) | 220 × 300 × 215 mm |

No hardware fasteners for the enclosure join. Printed-integral snap geometry throughout.

### Join Method Summary

- **24 cantilever snap arms** (bottom half) engaging **24 ledge pockets** (top half). 90° retention face. Permanent — requires arm fracture to disengage. Total assembly force ~120 N (comfortable two-palm press).
- **Continuous tongue-and-groove**, full 1040 mm perimeter. Tongue on bottom half (upward growth), groove on top half (downward opening). 4.0 mm tongue height ensures tongue locates the halves before snap arms engage.
- **4 corner alignment pins** (bottom half) in **4 corner sockets** (top half). 4.0 mm diameter, 8.0 mm tall. Pre-locate the halves in X and Y before any snap engagement.
- **0.5 mm exterior reveal**: top half exterior wall laps over bottom half, creating a designed shadow line seam. The top half is proud.

### Assembly Sequence (complete enclosure)

1. **Install dock cradle** into bottom half (snap pockets in floor, rear locating rib). Bottom half is face-up on the work surface.

2. **Place spine** into bottom half (2 snap posts into the left inner side wall slots, or the single side wall of the bottom half if split front-to-back — confirm spine engagement direction is lateral, not vertical).

3. **Install electronics tray** into top half (slide tray onto snap rails from the open side, before halves join). Top half is inverted, seam face up.

4. **Load cradle platforms** into spine (4 snap tabs each, press down from above into spine slots, through top of bottom half, or prior to top half placement depending on access).

5. **Load bags** into cradles; route tube connections; seat fold ends into spine front-face slots.

6. **Press upper caps** down onto cradles (4 snap arms each, tactile click). Bag frame is now complete.

7. **Close enclosure:** set top half over bottom half. Corner pins enter sockets. Tongue enters groove. Press both palms along 300 mm faces. 24 snaps engage — firm, definitive click-stop. Halves are permanently joined.

8. **Verify seam:** check that the 0.5 mm reveal runs continuously around the full perimeter. Any proud local section indicates an unengaged snap; press locally to engage.

### Design Conflicts Flagged for Specification

**Gap 1: Spine snap post engagement direction vs. enclosure assembly direction**

The bag-frame concept states the spine posts engage the enclosure half walls as the halves close laterally (in the X direction, as left and right half close around the spine). The current architecture has a top half and bottom half joining vertically (top half lowers onto bottom half in Z). These assembly directions are incompatible: the spine cannot be pressed laterally into a side wall during a vertical-close enclosure assembly.

The specification must resolve this. Options: (a) redesign the spine posts to engage in the Z direction (posts point up/down, slots open upward in the inner side walls of the top half), allowing the spine to be seated in the bottom half and captured by the descending top half; (b) retain lateral engagement but stage the assembly differently (spine posts into one half's slots from above before the top half is lowered). Option (a) is architecturally cleaner and consistent with all other mechanisms. This is the recommended resolution but the specification must confirm it and define the resulting post geometry.

**Gap 2: Bottom half spine engagement — which half gets which slots**

The synthesis (Section 5.1) places all spine slots in the top half. The bag-frame concept assumes the spine is in the bottom half during assembly and the second half closes over it. If the spine slots are only in the top half (inverted print, slots opening downward), the spine must hang from the top half before the halves close — which is mechanically fragile. A more stable staging has the spine seated in a feature of the bottom half first (even a simple ledge or contact surface, not a snap) and then the top half's snap slots capture it from above during the vertical close. The specification must define whether the bottom half carries any locating feature for the spine, even a non-snapping pocket, so the spine is stable during assembly.

**Gap 3: RP2040 retention ring — separate part or integral**

The display-switch-dimensions.md research flags the RP2040 as having no self-retention and recommends a twist-lock (bayonet) design. Whether this retention ring is a separate inserted part or a printed integral feature of the front panel wall has not been settled. If integral, the wall geometry at the RP2040 position becomes complex (the 33 mm through-hole must transition to a bayonet slot profile behind the panel face). If a separate part, it is an additional printed item. The specification must decide this and define the geometry either way.

**Gap 4: Funnel mount interface — no architecture defined**

The top face reserves a zone for the funnel mount interface but no geometry is specified. The funnel sub-assembly concept has not been written. The specification cannot finalize the top face until the funnel concept defines its mounting interface. The specification should carry the top face as a flat placeholder with the reserved zone marked, and update when the funnel concept is complete.

**Gap 5: Electronics tray snap rail geometry — deferred to tray concept**

The electronics tray concept has not been written. The top half's interior rear wall carries snap rail placeholders at 340 mm and 370 mm from the bottom, but the rail cross-section, depth, and retaining lip geometry depend on the tray's snap feature geometry. The specification should carry the rails as placeholder ledges and update when the tray concept is complete.
