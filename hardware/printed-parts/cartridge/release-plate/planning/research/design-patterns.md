# Design Pattern Research — Cartridge Release Plate

**Mechanism under study:** A pump cartridge that the user pulls out of the machine by squeezing two flat surfaces together — palm against the front face of the cartridge body, fingers curling upward to pull a release surface — while the entire collet-release mechanism remains invisible inside.

---

## 1. Hidden complexity behind minimal exterior

### The design problem

The vision specifies that from outside the cartridge, the user sees only: four barely-visible tube holes on the back, inset groove rails on the sides, and a squeeze grip on the front. No buttons, no visible latches, no protruding release handles. The exterior must read as a product, not as a housing that contains something.

The challenge is that minimal exteriors can fail in two opposite directions: they look unfinished (the seam reads as a manufacturing gap, not a designed feature), or they look like the product is sealed shut (the user cannot discover the release action). Successful products thread the needle by making the exterior geometry itself communicate the interaction.

### Products that hide release mechanisms behind flat surfaces

**DeWalt 20V MAX battery packs (DCB200 series and successors)**

The DeWalt 20V battery pack uses a dual-button squeeze release: two raised paddle buttons, one on each lateral face, that must be depressed simultaneously to disengage the pack from the tool. The mechanism behind those paddles is a pair of spring-loaded latches whose hooks engage corresponding slots in the tool's battery receiver. When both paddles are squeezed, the latch hooks are cammed inward, clearing the receiver slots, and the battery slides out under gravity or with a slight pull.

The key exterior detail: the buttons are not recessed flush with the face. They protrude approximately 2–3 mm from the battery side walls and have a fine ribbed texture running perpendicular to the squeeze direction. This protrusion accomplishes two things: it makes the button discoverable (the slight protrusion is the affordance), and it ensures the fingertip contacts the center of the button surface, not its edge. The button surface width is approximately 18–22 mm — wide enough for two fingers side by side. There is no visible gap between the button and the battery housing that would betray the latch mechanism behind it; the button perimeter has a uniform ~0.5 mm gap all around.

The exterior reads as: two matching ribbed panels, one per side, symmetrical. The symmetry and fine texture communicate intentionality. The latches, springs, and pivot points are completely invisible.

**Design guidance from DeWalt:** The release surface does not need to be flush to read as hidden — it can protrude 2–3 mm as long as the gap around it is narrow and uniform (under 1 mm). The protrusion is the affordance. Surface texture (fine ribs perpendicular to the actuation direction) marks the squeeze surface without calling attention to the mechanism behind it.

---

**Makita 18V LXT battery packs (BL1830/BL1850 series)**

Makita uses a single large release button centered on the narrow front face of the battery pack (the face opposite the tool contact face). The button occupies roughly 60% of the face width and sits flush with or 1 mm proud of the surrounding surface. The button is demarcated from the pack body by a subtle color shift (often slightly lighter gray) and a clean perimeter gap of approximately 0.6–0.8 mm.

The internal mechanism is a single pivoting latch with a over-center detent: pushing the button drives a cam that rotates the latch hook clear of the receiver groove. The spring return is stiff enough that the button rebounds firmly when released — approximately 15–20 N peak actuation force, approximately 5–7 mm travel.

The exterior face with the button reads as a complete surface interrupted by one intentional panel — not as a housing with a hole for a component. The reason is that the panel's proportions are designed to fill the face: it is not an afterthought shape (circle, small rectangle) dropped into a larger plane, but a shape that defines the plane.

**Design guidance from Makita:** When the release surface is a large panel rather than a small button, its perimeter gap and proportions matter more than texture. If the panel fills most of the face width, it reads as "this whole surface is the grip" rather than "there is a button here." This is relevant for the cartridge's front face: if the squeeze surface fills most of the front face, the user perceives the face, not a button within a face.

---

**HP 63 / HP 67 ink cartridges (HP DeskJet, ENVY series)**

HP ink cartridges use a snap-fit latch that is completely invisible from outside the cartridge. The cartridge exterior is a clean rectangular prism with only color-coded labeling and a small vent hole. The latch is a molded-in spring arm on the interior of the printer carriage that engages an internal ledge on the cartridge body. The user never sees the latch. To remove the cartridge, the user presses the cartridge in (further into the carriage, against the spring), which depresses the latch hook below the ledge, then pulls the cartridge out.

The exterior communicates nothing about the mechanism. The only communication is behavioral — a first-time user discovers "press then pull" through brief trial and error, or reads the printer manual. This works for low-stakes replaceable consumables where the user has time to learn. For the soda machine cartridge, this model is insufficient: a user who does not know "press inward first" will be confused. The soda machine cartridge needs the grip posture itself to communicate the action — the vision's palm-and-fingers geometry provides this without requiring any visible mechanism.

**Design guidance from HP cartridges:** Complete invisibility of mechanism is achievable and production-proven, but it shifts the discoverability burden entirely onto the grip affordance. The vision's palm-up grip posture — where the palm touches the fixed body and fingers naturally reach to pull the moving surface — is the affordance that replaces visible mechanism cues. This grip geometry must therefore be unambiguous: the surface the palm presses must feel structurally rigid (planted, not moving), and the surface the fingers contact must feel like it wants to move.

---

**What makes the exterior read as intentional**

From examining these three products, the common thread is: every visible surface element must appear to serve the form, not to accommodate a hidden mechanism. The seam gap between moving and fixed surfaces is the largest risk — if it is uneven, varies along its length, or is wider than 1 mm, it reads as slop or a manufacturing artifact. If it is narrow (0.5–0.8 mm), continuous, and has sharp edges on both sides, it reads as a designed parting line.

**For the cartridge specifically:** The gap between the squeeze surface (finger side) and the cartridge body (palm side) is the most critical exterior detail. It should be:
- Uniform width along its full perimeter: 0.6–1.0 mm (narrower reads better; below 0.5 mm is difficult to achieve with FDM at 0.4 mm nozzle without interference)
- Sharp edges on both sides of the gap (no fillets that would make the gap look like it was sanded or worn)
- The squeeze surface should be flush with or very slightly inset (0.5–1.0 mm) relative to the cartridge body face, not proud of it — inset reads as a designed recess, proud reads as an attached component

---

## 2. Satisfying squeeze feedback

### The problem

The release must feel and sound deliberate. Mushy travel with no clear endpoint creates uncertainty: "did it release? should I squeeze harder? is it stuck?" A clean release has a force profile with a clear inflection — rising force through the travel, then a distinct drop or snap at the moment of release.

### Reference products

**Milwaukee M18 battery packs (48-11-1850, 48-11-1820 series)**

The Milwaukee M18 battery is widely regarded among tradespeople as the most satisfying power tool battery release of the current generation. It uses a large single-button release on the front face with approximately 6–8 mm of button travel. The release mechanism includes a deliberately tuned over-center spring: as the button travels, force increases to a peak at approximately 5–6 mm of travel (approximately 18–22 N), then drops sharply by 30–40% as the latch hook clears its engagement shelf. This drop is accompanied by a perceptible click transmitted through the plastic housing.

The audible click is not from a separate click mechanism — it is the latch hook snapping past the engagement ledge. The sound is transmitted through the rigid ABS housing. The combination of force drop and audible snap gives dual confirmation: tactile and auditory simultaneously. This dual confirmation is what separates a "satisfying" release from a merely "functional" one.

**Design guidance from Milwaukee M18:** The force profile should have a sharp drop — not a gradual taper — at the moment of latch release. This requires the latch geometry to have a relatively steep release ramp (the face of the hook that cams clear of the engagement surface). A shallow ramp produces a gradual force taper; a steep ramp (60–80° from perpendicular) produces a sharp snap. A sharp drop of 30–50% of peak force over 1–2 mm of additional travel is the target. The inflection should occur at 5–7 mm of travel.

---

**Brita Longlast+ filter (pitcher filter, cartridge insertion)**

The Brita Longlast+ filter seats into the pitcher via a quarter-turn bayonet lock. At full engagement, there is a distinct audible and tactile "clunk" as the filter body seats against a rubber O-ring and the bayonet lugs engage their stops. The O-ring provides a simultaneously progressive resistance increase through the rotation and a definitive bottoming-out thud.

The key insight from the Brita mechanism applied to a linear squeeze: the "seated" confirmation is produced by two simultaneous signals — a force peak followed by sudden soft resistance (the O-ring compressed to full) — that overlap rather than occur in sequence. The user does not parse two events; they feel one event. The design deliberately makes the mechanical stop and the compliance of the seal occur at the same moment.

**Design guidance from Brita:** For the cartridge release, the release plate's travel should produce a force profile that ends not in free travel (the plate moving freely after the latches release) but in a soft stop — a feature that catches the plate at the end of its travel after release. A travel limiter with a thin elastomeric bumper (or a printed TPU stop pad) would provide the soft thud at end-of-travel. Without it, the plate would feel like it "runs away" after the latches let go.

---

**Zebra TC53e / TC51 handheld computer battery (referenced in product documentation)**

Zebra's enterprise handheld computers use a battery that presses down into a compartment until "the battery release latches snap into place" — their documentation language for the audible-tactile seating confirmation. The insertion is a vertical press with a dual-latch design. The user knows the battery is fully seated when both latches click simultaneously. Zebra specifies this as the user-facing confirmation; no visual indicator is provided.

**Design guidance from Zebra handhelds:** When a seating confirmation must occur without a visual indicator (as it does when pushing the soda cartridge inward to dock), the audible click is the primary signal. Both latches should engage simultaneously or within 1 mm of each other — sequential engagement feels incomplete and prompts the user to push harder. This means the latch hook heights must be matched to within 0.2 mm of each other. FDM tolerances require empirical calibration here.

---

**Summary: force profile targets**

Based on these products, the squeeze release should:
- Require 10–20 N of sustained finger pull force to initiate travel (comfortable for palm-up pinch grip; within the 22 N access-board guideline for consumer interaction forces)
- Peak at 15–25 N at approximately 5–6 mm of travel
- Drop sharply (30–50% force reduction) at the latch release point
- End with a soft stop at approximately 8–10 mm total travel

The audible signal should be produced by the latch geometry itself — steep release ramp on the latch hook — not by a separate click mechanism, which adds complexity without benefit.

---

## 3. Palm-up grip ergonomics

### The specified posture

The vision specifies: hand is palm-up (supinated), palm presses against the cartridge body front face, fingers curl upward to pull the release surface. This is a lateral pinch grip in a supinated forearm position — similar to how you hold a TV remote while pressing its far edge with the thumb and pulling its near edge with curled fingers.

### Why this posture works

The supinated (palm-up) position for a squeeze-to-release interaction has one key ergonomic advantage: the biceps and brachioradialis are the primary forearm supinators, and in the supinated position they are already pre-activated. This means finger-curl pull forces are generated against a stable base — the palm pushing against the rigid cartridge face — without requiring additional wrist stabilization. The user can produce 10–20 N of pull force with finger flexors without needing a power grip.

### Products that use this grip posture

**Server blade ejectors (HP ProLiant, Dell PowerEdge blade servers)**

HP ProLiant and Dell PowerEdge blade servers use a cam-lever ejector that operates in a palm-up grip. The technician's fingers engage a recessed pull tab from below (fingers curl upward) while the palm contacts the server blade faceplate. The ejector lever travel is 15–20 mm, well-distributed across the finger pads. The recessed pull tab is set 8–12 mm below the faceplate surface to provide clearance for the full finger pad, not just the fingertip.

The 8–12 mm inset depth is the critical detail. Fingertip-only contact on a shallow surface (2–4 mm inset) produces fatigue and uncertain purchase — the fingertip can slip off. Finger pad contact on a deeper inset (8–12 mm) distributes force across 25–35 mm of finger length and feels substantially more confident.

**Design guidance from blade ejectors:** The finger contact surface (release surface) should be inset at least 8 mm from the plane of the cartridge body face, measured perpendicular to the pull direction. This allows the user's finger pads — not just the tips — to curl around the surface and pull. At 8 mm inset, three adult fingers can obtain pad contact. At 12 mm inset, a four-finger grip is achievable. Given the cartridge width (bounded by the enclosure bay width), 10 mm inset is a reasonable target.

---

**Compact cassette tape (Philips/IEC format, all major manufacturers)**

The cassette tape uses a finger-curl grip for extraction from a cassette deck: the user inserts a fingertip into the center hub window and curls it toward themselves to pull the cassette. This interaction requires no squeeze — but the geometry is instructive. The window is 14–18 mm deep and 20–25 mm wide, sized to accept two finger pads simultaneously. The window edge toward the user (the pull edge) has a chamfer or fillet of 2–3 mm to prevent the finger from being cut against a sharp edge during pull.

**Design guidance from cassette tapes:** The finger contact edge — the edge the finger pad presses against when pulling — should have a chamfer or generous radius (minimum 2 mm, ideally 3–4 mm) to prevent finger pad discomfort during sustained pull. A sharp 90° edge concentrates force on a narrow strip of skin and reads as "harsh." A radiused edge feels like it was designed for a finger.

---

**Staples / office stapler staple strip loading (most mid-range desktop staplers)**

Many desktop staplers use a palm-up grip for loading: the stapler is flipped upside down, held palm-up, and the user pinches the magazine release with thumb and index while the palm supports the body. This is not identical to the cartridge interaction, but it represents a well-proven ergonomic template for light-force palm-up pinch release interactions in consumer products.

The grip clearance dimension in staplers: the distance between the underside of the stapler body and the nearest obstruction (desk surface or thumb pad) when held palm-up is typically 20–30 mm. This is the "hand entry depth" — how far the hand can penetrate toward the release surface before running out of room.

**Design guidance from staplers:** The cartridge needs to provide at least 20 mm of clearance between the release surface and the front edge of the enclosure opening (the bay). If the cartridge extends fully to the front face of the enclosure with no recess, there is no room for the hand to enter the palm-up grip posture. The vision's design already addresses this (the cartridge slides on rails into a bay), but the bay opening depth must accommodate the hand entry.

---

**Grip surface texture for the palm contact area**

The palm contact surface (the cartridge body front face, which the palm pushes against) should be matte, not glossy. A matte surface provides the tactile feedback that the palm is "planted" — glossy reads as slippery and creates doubt about the grip. Lightly embossed texture (0.3–0.5 mm raised geometry, diamond or hex pattern) is preferred over smooth matte for the palm zone because it provides both visual confirmation ("this is the grip zone") and tactile drag to stabilize the palm during the finger pull.

The finger contact surface (the release surface the fingers pull) should be smooth or very lightly textured — the finger pads need to slide slightly as they flex, and a heavily textured finger surface creates friction that fights the natural curl of the fingers during the pull stroke.

---

## 4. Confidence of cartridge seating

### The problem

When the user pushes the cartridge into the dock (inserting into the bay), the 1/4" tube stubs in the enclosure enter the quick-connect fittings on the back of the cartridge. The user needs to know the cartridge is fully seated — all four tubes are fully engaged — without being able to see the back of the cartridge during insertion.

### Reference products

**Nespresso Vertuo capsule seating (VertuoLine machines)**

The Nespresso Vertuo uses a centrifuge-based brewing method that requires the capsule to be exactly centered and fully seated before the head closes. The machine provides two simultaneous cues at full seating: a gentle mechanical "bump" (the capsule bottoming against the brew head recess) and a visible indicator (the lever arm reaches its closed stop with a definitive click). The bump and click are designed to occur within 2–3 mm of each other so they feel like one event.

The Nespresso cue is strong because it uses two signals simultaneously. For the cartridge dock, the tube stubs entering the quick-connects provide one signal (a progressive increase in insertion force as the collet engages the tube), but this alone may feel like the cartridge is "stuck" rather than "seated."

**Design guidance from Nespresso:** Add a second signal that coincides with full tube engagement. A snap-feature — a small latch hook that engages a detent at the cartridge's fully-inserted position — provides both the audible click and the force break that says "stop pushing." The tube stub engagement alone does not create a clear stop; the snap feature is the designed confirmation.

---

**SD card slot (virtually every laptop and camera, 2005–present)**

The SD card slot is the most thoroughly iterated slide-in cartridge design in consumer electronics. The interaction is: push card in, feel progressive resistance, feel a distinct "click" at full insertion as the spring-loaded eject mechanism latches. The card sits flush or slightly recessed. To eject, push again (push-push mechanism) — the eject spring fires the card out approximately 5–8 mm.

The SD card slot click comes from a spring-loaded pogo mechanism: a ramp on the card body compresses a coil spring as the card travels in, and at full insertion the spring is fully compressed and a detent catches the card. The click force and travel: approximately 5–10 N of insertion force, detent click at approximately 3–5 mm from full insertion, card then "snaps" the last 3–5 mm to flush.

The critical SD card detail: the card does not coast smoothly to a stop at full insertion. It "snaps" the final 3–5 mm because the spring drives the card forward against the detent stop. This snap is the tactile "you're done" signal — the user does not need to push the card to exact depth; the mechanism pulls it the rest of the way.

**Design guidance from SD cards:** The cartridge dock should have a snap-in feature that actively draws the cartridge the final 3–5 mm to fully-seated position once the quick-connect collets have engaged. This ensures full tube engagement even if the user's push force was slightly insufficient, and it produces the "snap in" feel that communicates full seating. The snap-in spring force must be chosen to not force the tubes into the quick-connects before the user has aligned the cartridge on the rails.

---

**USB-A connector (billions shipped)**

USB-A connectors use friction and a slight interference fit — no latch — to signal full insertion. The "fully inserted" state is communicated by: (a) a definitive stop when the connector bottoms against the port housing, (b) the disappearance of the small front gap visible when the connector is partially inserted, and (c) the tactile resistance increase in the final 1–2 mm of insertion.

The USB-A lesson for the cartridge: visual flush alignment is a powerful "fully seated" signal. If the cartridge front face aligns flush with the enclosure front face at full insertion, the user sees it is seated. This is the simplest possible confirmation and requires no additional mechanism — but it only works if the cartridge-to-bay clearance is tight enough that partial insertion looks obviously incomplete. If a partially-inserted cartridge's front face is only 3–5 mm shy of flush, the user may not notice. The flush indicator works best when the travel from "partial" to "full" crosses a visible threshold — a chamfered recess on the enclosure front face that the cartridge edge fits into is one way to make partial insertion obvious.

**Design guidance from USB-A:** Design the enclosure bay so the cartridge front face is visibly non-flush (recessed 5 mm or more) when partially inserted, and flush (or barely recessed, under 1 mm) when fully seated. This makes the visual "you're done" cue unambiguous.

---

## Summary of actionable design guidance

| UX Quality | Design Guidance | Derived from |
|---|---|---|
| Hidden mechanism — seam gap | 0.6–1.0 mm uniform perimeter gap between squeeze surface and body; sharp edges on both sides | DeWalt 20V, Makita 18V LXT |
| Hidden mechanism — squeeze surface | Inset 0.5–1.0 mm from body face plane, or flush; not proud | Makita 18V LXT |
| Hidden mechanism — surface proportion | Squeeze surface should fill most of front face width so it reads as "the face" not "a button" | Makita 18V LXT |
| Squeeze feedback — force profile | 10–20 N force to initiate; peak 15–25 N at 5–6 mm travel; sharp 30–50% drop at latch release; soft stop at 8–10 mm total | Milwaukee M18 |
| Squeeze feedback — audible click | Use steep latch release ramp (60–80° from perpendicular) so the hook snap produces the click; no separate click mechanism needed | Milwaukee M18 |
| Squeeze feedback — end-of-travel | Add soft stop (TPU pad or compliant bumper) so the plate does not feel like it runs away after release | Brita Longlast+ |
| Palm-up grip — finger contact depth | Release surface inset at least 8 mm from body face plane; 10 mm preferred for finger-pad (not fingertip) contact | HP/Dell blade ejectors |
| Palm-up grip — finger edge comfort | Chamfer or radius (2–4 mm) on the pull edge of the release surface | Compact cassette tape |
| Palm-up grip — palm texture | Matte with light embossed texture (0.3–0.5 mm, diamond or hex) on palm contact surface | Tool grip ergonomics literature |
| Palm-up grip — hand clearance | Bay opening must provide at least 20 mm of hand-entry depth to achieve palm-up posture | Desktop stapler grip template |
| Seating confidence — snap-in | Snap-in feature that actively draws cartridge the final 3–5 mm to full seating; prevents "almost seated" ambiguity | SD card slot |
| Seating confidence — dual signal | Snap click should coincide with tube engagement force peak within 2–3 mm so user feels one event | Nespresso Vertuo |
| Seating confidence — visual flush | Cartridge front face should be visibly recessed (5+ mm) when partially inserted and flush (under 1 mm) when fully seated | USB-A connector |
| Simultaneous latch engagement | Latch hook heights must be matched within 0.2 mm to ensure both hooks seat simultaneously; requires empirical calibration | Zebra TC53e/TC51 battery |
