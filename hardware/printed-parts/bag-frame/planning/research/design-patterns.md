# Bag Frame Design Patterns Research

**Purpose:** Establish design language and geometric precedent for the bag frame mechanism — the lens-shaped cradle platforms, upper retention caps, and structural skeleton that constrains two Platypus Platy 2L collapsible bottles mounted diagonally at 35 degrees inside the soda machine enclosure.

**Research conducted:** March 2026

---

## Context: The Object Being Constrained

The Platypus Platy 2L bottle (19 cm wide × 35 cm tall, ~37 g empty) is a flat, heat-sealed nylon/polyethylene pouch. When filled, it does not form a cylinder — it billows outward from both flat faces into a lens or eye shape in cross-section: flat center panels that bow outward, with sealed edge seams acting as the perimeter boundary. At 25–30 mm constrained thickness (per the vision document) the cross-section is a shallow oval or eye, much wider than it is deep. As liquid is consumed the bottle loses internal pressure and the walls begin to go slack — without external constraint, the bag base can rise and the profile can become irregular. The goal of the cradle geometry is to prevent this entirely.

The bags are mounted at 35 degrees from horizontal, cap end down and toward the back of the enclosure, with the other end folded flat against the front wall.

---

## 1. Confident Seating for Flexible/Collapsible Containers

### 1.1 CamelBak Crux Reservoir — Hook-and-Baffle Upper Anchor

**Product:** CamelBak Crux (2L / 3L hydration reservoir, shipped since ~2015)

The Crux uses a two-point retention strategy. At the top, a rigid hook molded into the lid protrudes approximately 15–20 mm and engages a rigid sewn loop inside the hydration pocket of a pack. This hook is the single vertical load-bearing anchor — the bag hangs from it, full or empty. The hook geometry is a rounded J: the curve radius is large enough that the loop cannot disengage under sloshing load but small enough to thread onto the pack loop without tools.

At the interior, a center baffle is heat-welded from face to face, running vertically through the middle of the bag. This baffle does three things: it limits how far the faces bow apart under liquid pressure (controlling maximum thickness to roughly 40 mm for the 3L version), it prevents lateral water sloshing, and it creates a structurally stiffer bag that maintains its silhouette as the bag empties. Without the baffle, the faces would separate unpredictably and the bag would slump sideways.

**Design guidance extracted:**
- The upper anchor is a positive-capture hook geometry, not a friction fit or gravity rest. The bag cannot accidentally disengage without deliberate removal.
- The retention hook sits at the geometric top of the bag — the highest point of the closure — so gravity always seats the bag against the hook rather than lifting it off.
- The baffle controls cross-section profile, which the cradle then matches. A contour-matched cradle without an internal structure controlling the object's own shape will only work when the object is full.
- This suggests the bag frame should treat the bag's filled cross-section as the design shape, but the upper cap geometry must account for the bag losing thickness as it empties.

### 1.2 Osprey Hydraulics Reservoir — Backer Plate and HydraClip System

**Product:** Osprey Hydraulics 2L and 3L (introduced Spring 2023, patent pending)

The Osprey Hydraulics adds a rigid semi-flexible polypropylene backer plate to the rear face of the reservoir. The backer plate is approximately 1.5 mm thick and spans the full width of the bag. Its function is to prevent buckling and bending during insertion into a pack sleeve — it gives the soft bag enough column stiffness that it slides in and out as a unit rather than folding. Packed dimensions: 15 in × 6 in × 1.5 in (381 mm × 152 mm × 38 mm), substantially thinner and more controlled than an unrestrained bag.

At the top, the Slide-Seal closure has a built-in universal hanger tab — a rigid plastic extension, roughly 20 mm tall and 40 mm wide — that engages a dedicated HydraClip bar in Osprey packs. The HydraClip is a fixed horizontal bar inside the pack; the hanger tab loops over or clips onto this bar. The result is that the reservoir is captured at its top by positive clip engagement, and its back face is supported by the rigid plate pressed against the pack back panel.

The center baffle plus backer plate together constrain the bag's cross-section to a known profile during both full and empty states.

**Design guidance extracted:**
- A rigid backing surface on one face of the bag — even a thin one — eliminates the biggest source of unpredictable bag movement: the rear face shifting laterally. In the soda machine context, the rear cradle surface (against which the bag rests when partially empty) can function like the backer plate if it matches the bag's natural settled surface.
- Upper cap geometry should be a positive clip or tab form that prevents the bag from drifting upward or off-axis, not merely a lip that relies on gravity.
- The bag's natural packed thickness of ~38 mm for a 3L reservoir (the Platy 2L will be somewhat less, approximately 25–35 mm when constrained per the vision document) sets the minimum required clearance in the cradle.

### 1.3 HydraPak Contour Reservoir — Shape-Loc Baffles and 3D-Welded Bottom

**Product:** HydraPak Contour 2L and 3L (introduced 2024–2025)

The Contour takes the most aggressive approach to cross-section control. Two blue "Shape-Loc" baffles are welded transversely into the face panel — they run roughly parallel, spaced approximately 50–70 mm apart vertically, creating three horizontal zones across the front face. These baffles prevent any zone of the face from billowing beyond a controlled limit, making the filled profile far more regular than an unrestrained flat pouch. Dimensions: 2L model is 370 mm × 191 mm; 3L model is 429 mm × 190 mm. The near-constant 190–191 mm width across both sizes suggests the width is constrained to match a standard pack sleeve width, not simply derived from volume.

The 3D-welded bottom and side tube exit port prevent the classic collapsible-bag problem of the bottom seam pulling up as liquid drops — the 3D geometry gives the bottom structural continuity. When filled, "it flattens out more, taking up more space from left to right instead of front to back," producing a wide, thin profile distinctly different from a cylindrical bottle.

The Slide-Seal top has a universal hanger designed to work with clips, hooks, and loops from Gregory, The North Face, Salomon, and Osprey packs — a deliberately cross-compatible geometry.

**Design guidance extracted:**
- The constrained width of ~190 mm across both 2L and 3L models demonstrates that managing width-axis variability (left-right) is the primary design concern for a flat bag. The cradle side walls should match or slightly exceed the bag's natural filled width.
- Shape-Loc baffles function as internal "limit stops" on face expansion. If the Platypus Platy lacks these, the cradle's side lip geometry must perform the same function externally — the lip height and inset radius define how much the bag face is allowed to expand.
- The consistent 190 mm width across volumes suggests that a bag held in a correctly-sized cradle does not change significantly in the lateral dimension as it fills and empties — volume change is absorbed primarily by thickness change (face-to-face distance).

### Summary: What Creates the "Locked In" Feeling

Across all three products, the physical sensation that a soft bag is locked in — versus sitting loosely — comes from three simultaneous conditions:

1. **Positive upper capture:** The bag cannot lift upward or disengage without deliberate action. This is always a hook, clip, or tab, never a gravity-only rest.
2. **Profile match between bag and cradle:** The cradle shape matches the bag's natural filled cross-section closely enough that there is no lateral play. If the bag is 190 mm wide and the cradle is 220 mm wide, it floats; if the cradle is 194 mm wide, it sits.
3. **Supported face geometry:** At least one face of the bag (usually the rear) is in contact with a rigid surface across most of its area. Without this, the bag wobbles front-to-back.

**Actionable guidance for cradle design:**
- Upper cap retention should use a positive-capture tab or hook geometry that requires deliberate action to disengage. A simple lip that the bag rests over is insufficient.
- Cradle width (side walls) should be set to approximately filled bag width + 2–4 mm clearance. Too tight prevents insertion; too loose allows lateral float.
- The rear face of the cradle (the lens-shaped platform) should support the bag's rear face across most of its area. A surface that only contacts the bag at the perimeter leaves the center unsupported and allows the rear face to bow inward as liquid drops.
- The cradle lip height at the sides (the boundary between supported surface and free space) should be approximately 8–12 mm tall — enough to retain the bag under liquid sloshing, not so tall that it interferes with the bag being pressed flat against the front wall of the enclosure.

---

## 2. Lens-Shaped / Contour-Matched Support Surfaces

### 2.1 HydraPak Contour's Conforming Profile

The Contour's 3D welded bottom corner eliminates the flat pouch's tendency to have a sharp-angled seam at the base. Instead, the bottom transitions smoothly from the flat face into the side seam through a curved gusset — the outer boundary traces a radius of approximately 15–25 mm at the corner rather than a 90-degree seam fold. When this bag sits in a cradle, the cradle corners must match this curve or the bag will rock.

**Design guidance:** Cradle interior corners should not be sharper than the radius of the bag's seam fold when full. A sharp cradle corner pressing against a rounded seam creates a stress concentration in the bag film. Use a 15–20 mm interior corner radius at the cradle base corners to match the bag's natural settled shape.

### 2.2 The Silicone Baking Mold Analogy — Contour Fit vs. Approximate Fit

Professional silicone baking molds (Silikomart, Pavoni, Flexipan/Demarle) provide the clearest example of what makes a contoured support feel precision-fit rather than approximate. The key distinction: a precision-fit support surface is derived from the actual settled shape of the object at rest, while an approximate support surface is derived from a simplified geometric primitive (sphere, cylinder, rectangle) that encloses the object.

In silicone molds, the cavity walls contact the batter/product across their full area immediately when filled. There is no gap, no wobble zone, no place where the product can sag sideways. The design process starts from the product's resting shape, not from a convenient geometry.

For the Platypus Platy in its constrained state (25–30 mm thickness, ~190 mm wide, lens cross-section), the cradle surface should be derived from the actual profile of a filled bottle at 35 degrees inclination. The most reliable way to get this shape is to fill the bottle, lay it at the target angle, let it settle under its own weight, and then trace or measure the resulting lower surface profile. This becomes the cradle template.

**Design guidance:**
- The lens-shaped platform profile should be the actual settled lower surface of a filled Platypus Platy at 35 degrees — not a mathematical approximation. Measure it.
- The lip that transitions between "supported surface" and "free space" reads as intentional when it is a constant height above the supported surface all the way around the perimeter. A lip that varies in height or transitions with an unclear radius reads as accidental.
- A 2–3 mm reveal between the bag body and the cradle lip top edge (when the bag is seated) is the right visual register — it shows the bag is positively seated, not overflowing the lip.

### 2.3 IV Bag Holders — Wire Form Retention and Gravity Seating

IV pole bag holders are wire forms bent to match the perimeter of a standard IV bag. The wire is typically 3–4 mm diameter stainless steel, bent into a U or rectangular frame that matches the bag's width at approximately the bag's widest point (not the very top or very bottom). The bag hangs from a hook at the top; the wire frame catches the bag at its sides if it swings. The wire does not support the bag's face — it only constrains lateral movement.

This is the minimal-contact version of soft bag retention: one positive hook at the top, side constraint by peripheral wire, face unsupported. The bag hangs and drapes naturally. This works in medical settings because the bag is always substantially filled during use and the wire frame's primary job is to keep the bag vertical, not to control its profile shape.

**Design guidance (contrasting case):** IV wire frames are inadequate for the soda machine application because:
- They do not control face expansion, so the bag's thickness varies freely with fill level.
- They provide no face support, so the bag's rear face will slump as it empties.
- Wire frame retention is gravity-dependent — a tilted mounting (35 degrees) means the bag would sag toward the low end rather than against the frame.

The soda machine cradle must do more: full-face rear support, positive upper cap locking, and matched cross-section lips on the sides.

---

## 3. Consumer Appliance Interior Quality

### 3.1 Nespresso CitiZ — Interior as Product Continuation

**Product:** Nespresso CitiZ (De'Longhi version, continuously manufactured since 2010)

The CitiZ water tank mounts to the rear of the machine via two rigid plastic hooked bars that protrude from the machine body and engage matching slots in the tank's rear face. The tank slides downward onto these hooks — the geometry is a top-entry, gravity-retained slot. Once seated, the tank's weight keeps it engaged. Removal requires lifting the tank up and forward, which cams the hooks out of the slots. There are no springs, clips, or active retention mechanisms.

The internal surfaces visible during tank removal are textured to match the exterior surface finish. The tank cradle area uses the same wall ribbing pattern as the exterior panels — the ribs run vertically and have a consistent spacing of approximately 8–10 mm. Corner radii on the interior of the tank bay are approximately 2–3 mm — tight enough to read as clean and intentional, not so tight that they look sharp.

What makes the interior read as product rather than structure: there are no surfaces that are clearly "the back of the outer shell." Every surface that could be visible during normal maintenance has its own surface language — a rib pattern, a radius, a controlled draft angle. The machine looks like it was designed from the inside out, not from the outside in.

**Design guidance:**
- Interior surfaces visible during refilling — the lens-shaped platform face, the cradle side walls, the upper cap underside — should carry the same surface language as the enclosure interior. If the enclosure uses 0.6 mm parallel ribs for stiffening, the cradle does too.
- The corner radius between the platform face and the cradle side lip should be no smaller than 2 mm and no larger than 4 mm. Below 2 mm, it reads as a manufacturing artifact; above 4 mm, it reads as soft/imprecise.
- The seam between the cradle body and the enclosure snap connection should have a 1.5–2 mm reveal — a deliberate step that reads as "this is a component seated in a housing," not "this is a surface that collides with another surface."

### 3.2 Vitamix Container-to-Base Engagement — Bayonet Seating Quality

**Product:** Vitamix Ascent and 5200 series (continuously manufactured, 5200 since 2007)

The Vitamix container sits on the motor base through a four-point bayonet-type interface. The container blade base has four outward-facing tabs; the motor base has corresponding four slots. Placement: set the container on the base, rotate approximately 30 degrees clockwise until the container drops ~3 mm into the locked seats and the tabs engage behind retaining surfaces.

The engagement produces a specific tactile sequence: a light resistance during rotation, then a drop (approximately 3 mm) as the tabs clear the cam surface and seat into the retention detents, then a firm stop. This three-event sequence — resistance, drop, stop — communicates definitively that the container is locked. The user does not need to look; the hand tells them.

The alignment is assisted by the base socket geometry: the four slots are arranged symmetrically, and the slot entries are chamfered (approximately 15–20 degree lead-in), so there is a roughly 10-degree cone of placement error that still results in correct engagement. The container cannot be "almost locked" — it is either locked (with the drop and the stop) or it is not engaged at all.

**Design guidance:**
- The upper cap locking geometry should produce a similar two-or-three-event sequence: approach (cam-in), engagement (a small step or drop into the locked position), and a firm stop that communicates completion without requiring visual confirmation.
- The lead-in geometry on any retention tab should have a 10–15 degree chamfer to tolerate ±3–5 mm placement imprecision during assembly.
- A 2–3 mm travel into the locked position (after the cam-in ramp) makes the locked state clearly distinct from "partially engaged."

### 3.3 Breville Barista Express BES870 — Water Tank Rear Slide Cradle

**Product:** Breville Barista Express BES870 (current generation, produced since ~2013)

The water tank slides out from the rear of the machine on two vertical guide ribs, one on each side of the tank bay. The ribs are approximately 4–6 mm wide and protrude approximately 2 mm from the side walls of the bay, running the full vertical height of the tank opening. The tank has corresponding grooves on its left and right faces that accept these ribs with approximately 0.3–0.5 mm of clearance — a fit that is snug without being stiff, so the tank can be removed and replaced single-handed.

At the bottom of the travel, a spring-loaded water inlet probe engages the tank's rubber-sealed outlet port. The probe is recessed into the machine floor; when the tank is seated, the rubber seal on the tank compresses ~1.5 mm against the probe face. This compression serves as a secondary retention force — the tank is held not just by gravity but by the 1–2 N spring preload pressing the seal against the probe. The tank will not rattle even with the machine moved.

The interior of the tank bay is a flat-back, flat-floor space — no visible fasteners, no exposed wiring, no tube stubs above the water line. Everything below the tank waterline is sealed away behind the machine's internal wall. The single visible fitting (the water inlet probe) is centered and recessed, making it read as a designed feature rather than an exposed fitting.

**Design guidance:**
- Guide ribs on cradle side walls are preferable to guide slots in the bag film (the bag can't have grooves). Instead, the cradle should use inward-facing ribs that bracket the bag sides — the bag film is constrained between two ribs, not slid along them. Rib width: 3–5 mm. Rib height above cradle floor: 8–12 mm.
- The interior of the cradle bay should have no visible tubing, no fasteners, and no mechanical features that the user would not understand at a glance. The tube connections at the bag cap (bottom rear) should be below or behind the visible cradle volume when the bag is seated.
- Guide rib-to-bag clearance of 2–3 mm per side (4–6 mm total width tolerance) is appropriate for a soft bag insertion: too tight prevents seating, too loose allows the bag to shift under fill-level changes.

---

## 4. Stacked/Layered Container Organization

### 4.1 VintageView Evolution Wine Wall — Two-Column Visual Unity

**Product:** VintageView Evolution Wine Wall (current production, modular stainless steel system)

The Evolution system holds bottles label-forward using thin steel "wine rods" that pass through each bottle position. The rods run as continuous members from the top column cap to the bottom column cap — they are not interrupted between bottle positions. This single-member-per-row design is the primary visual device that unifies multiple individual bottle positions into a single mechanism. The eye reads the rod first, then notices the bottles resting on it, rather than reading individual cradles that happen to be near each other.

For two-column configurations: both columns share the same rod spacing and column cap hardware. The columns are mounted at a fixed center-to-center distance (approximately 115 mm for the standard bottle pitch). The horizontal visual continuity between the two columns is provided by a shared cap rail at top and bottom — the same aluminum extrusion spans both columns, creating a single horizontal datum that registers the entire structure as one element rather than two parallel stacks.

The 1-bottle-deep configuration is 4.25 in (108 mm) deep and the per-bottle vertical pitch is approximately 100 mm. The wine rod diameter is approximately 10 mm — large enough to see clearly and register as the primary structural element.

**Design guidance:**
- The two bag cradles should share continuous structural members — a single spine or a shared cap rail — rather than being two separate cradles that happen to be assembled at a similar location. The shared member is the primary visual element that reads as "one mechanism."
- A continuous rail or plate that spans both cradles horizontally (at either the upper cap or lower platform) unifies the two-bag assembly into one structure. This rail can be the snap-connection interface to the enclosure, making it both structural and visual.
- The per-bag pitch (center-to-center spacing between the two bag platforms) should be set by the visual and physical requirements, not by convenience, and should be consistent — both bags should be clearly the same component at the same offset from the shared spine.

### 4.2 Sorbus Stackable Can Organizer — Shared Geometry as Visual Unity

**Product:** Sorbus Soda Can Organizer (stackable, 12-can per unit, BPA-free, currently available on Amazon)

This organizer uses gravity-feed dispensing with an inclined floor and a front stop to prevent cans from rolling out. The key visual device that makes multiple stacked units read as one product rather than separate components: every face (top, bottom, front, back) uses the same wall thickness and the same ribbing pattern. When two or three are stacked, the rib pattern continues across the stack boundaries and the eye reads it as a single taller unit.

Each individual tray has a 5 mm perimeter wall with 1.5 mm ribs at approximately 15 mm spacing. The top face is open for can insertion; the bottom face has interlocking tabs that align with the top of the unit below, fixing the stack alignment. The tabs provide approximately 4 mm of lateral constraint between stacked units.

**Design guidance:**
- If the two bag platforms are printed separately and stacked or placed adjacent, the rib pattern, wall thickness, and draft angle on both should be identical — the parts should look like they came from the same mold. This requires both cradles to be designed as instances of the same part, not as independent components.
- The interlocking tab concept (used between stacked organizers) translates directly to the bag frame spine: a central vertical member that both bag platforms snap onto at defined, equally-spaced positions creates the same visual unity. The bags appear to be at uniform positions on a shared structure, not at arbitrary heights.

### 4.3 Fridge Slide-Rail Can Dispensers — Shared Rail as Unifying Spine

**Product:** Singtip 5-Row Drink Organizer (FIFO gravity-feed, adjustable, currently available)

Five-row organizers use a common rear wall and common front stop rail that spans all five rows continuously. Individual channel dividers are identical thin fins at regular pitch. The result is that all five channels read as subdivisions of one organizer, not five separate organizers placed side by side. The visual hierarchy is: (1) the organizer as a whole, (2) the rows, (3) the individual cans.

The channel fin height (the feature that separates rows) is approximately 25–30 mm — tall enough to prevent a can from migrating between channels under vibration, not so tall that the fins read as walls between separate containers. The fins also serve as visual separators — the user knows which channel belongs to which row without additional labeling.

**Design guidance:**
- For the two-bag frame, the structural "fins" or side walls that separate the bag positions from each other and from the enclosure walls should be a consistent, repeated height. The side wall height defines the visual rhythm. At 8–12 mm (matching the retention lip recommendation from Section 1), these walls read as intentional organizers, not as accidental barriers.
- A shared front face plate or front cap, spanning both bag positions, creates the clearest visual unity. Even if the actual bag cap connections are physically separate, a single visual element in front of both — a plate with two cutouts, for example — reads as one mechanism.

---

## 5. Consolidated Design Guidance for the Bag Frame

### Cradle Platform (Lens-Shaped Lower Support)

1. **Profile source:** Trace the actual settled lower surface of a filled Platypus Platy 2L at 35 degrees inclination. Use this as the platform face geometry, not a mathematical oval or cylinder approximation.

2. **Side lip geometry:** Side lips should be 8–12 mm tall measured from the lowest point of the platform surface. The interior face of the lip should have no draft (or minimal positive draft toward the bag) — this is the active retention surface. The exterior of the lip can have standard FDM draft (1–2 degrees). Round the top edge of the lip with a 1–1.5 mm radius to read as intentional, not sharp.

3. **Interior corner radii:** Platform floor-to-lip transitions: 2–4 mm radius. Lip top edge: 1–1.5 mm radius. Corner seam where platform meets the structural spine: 3–5 mm radius.

4. **Platform face texture:** If the enclosure interior has a surface texture, the platform face should use the same language. The platform is a featured interior surface, not structural backfill.

5. **Bag contact clearance:** Width between opposing side lips should be bag filled width + 3 mm per side = approximately 6 mm total slack. This allows easy insertion while preventing lateral float under fill changes.

### Upper Cap (Retention Geometry)

6. **Positive capture:** Upper cap must use a positive-capture form — a tab, hook, or slot that requires deliberate action to disengage. Not a friction fit, not a gravity-only lip.

7. **Engagement sequence:** The cap should produce at least two tactile events on closure: cam-in (approaching the locked zone, increasing resistance), and seat (the small step or drop into the locked state, with a firm stop). Travel into locked state should be 2–3 mm.

8. **Lead-in geometry:** Any cam-in ramp should be 10–15 degrees to tolerate ±3–5 mm placement imprecision.

9. **Reveal at cap seam:** The cap's visible seam against the cradle body or the enclosure should have a 1.5–2 mm reveal — a deliberate step that reads as "component seated in housing."

### Structural Spine and Two-Bag Unity

10. **Shared continuous member:** The two cradle platforms should snap onto, or integrate with, a single continuous spine or shared top/bottom rail. This member is the primary visual element that reads as one mechanism. The spine should be visible from the front — not hidden by the cradle platforms.

11. **Identical instances:** Both cradle platforms should be designed as the same part (mirrored if needed, but dimensionally identical). If they look the same, the user understands the structure immediately.

12. **Per-bag pitch:** The center-to-center vertical spacing between the two bag platforms should be set to the minimum that allows one bag to be fully constrained without contacting the other — and this spacing should be consistent and clearly intentional, not the minimum possible.

### Interior Quality Language

13. **No orphan surfaces:** Any surface visible during refilling or bag access should have its own surface treatment — ribs, radius, or both. No surface should look like the backside of a functional feature.

14. **Rib language:** If structural ribs are used on the cradle back wall, maintain consistent spacing (8–12 mm) and height (1.5–2 mm above the wall face). Ribs should run in one direction only per surface; mixing rib directions on a single surface reads as unsettled.

15. **Fastener concealment:** The cradle's snap connections to the enclosure should not be visible from the front during normal bag access. They can face toward the enclosure wall.

---

## Sources Referenced

- CamelBak Crux Reservoir (camelbak.com, outdoorsportswire.com, nailthetrail.com)
- Osprey Hydraulics 2L/3L Reservoir (cleverhiker.com, outdoorsportswire.com, osprey.com)
- HydraPak Contour 2L/3L Reservoir (gearjunkie.com, hydrapak.com product pages)
- Nespresso CitiZ water tank mechanism (ifixit.com, lemonfool.co.uk user forum)
- Breville Barista Express BES870 water tank cradle (breville.com instruction manual, siber-sonic.com disassembly, ereplacementparts.com)
- Vitamix 5200/Ascent container-to-base bayonet engagement (vitamix.com owners manuals, blendertampers.com)
- VintageView Evolution Wine Wall (vintageview.com product pages, wineracks.com)
- Sorbus Stackable Can Organizer / Singtip Drink Organizer (amazon.com)
- Platypus Platy 2L bottle geometry (trailspace.com reviews, cascadedesigns.com, backpackinglight.com forum)
- Firstmold.com: chamfer and fillet design guidance for consumer appliances
