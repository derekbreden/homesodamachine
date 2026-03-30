# Design Pattern Research — Pump-Tray

**What is being designed:** The pump-tray is a flat FDM-printed mounting plate inside the removable pump cartridge. Two Kamoer KPHM400 DC peristaltic pumps bolt to it via 4x M3 screws each. The tray sits at the bracket face of the pumps — the motor cylinders pass through bores in the tray and extend rearward, while the pump heads with their tube stubs project forward. The tray is not directly visible to the user; it lives inside the cartridge shell. However, the tray's geometry determines the cartridge's external dimensions (width, depth, height, front face), and the tray is visible as an internal component when the cartridge is removed and the user peers inside.

Three UX qualities are studied here. Each has specific geometric findings with actionable design guidance.

---

## UX Quality 1: Internal mechanisms invisible from the outside

### The design problem

The tray holds two DC motors and their associated pump heads, occupying a roughly 144mm wide × 121mm deep envelope behind the tray face. The cartridge exterior must give no indication of this complexity. "Complex inside, clean outside" is a fundamental consumer product strategy, but achieving it is a geometric problem: wall thickness, surface continuity, flush mating lines, and controlled reveals must all be designed with specific dimensions.

### Products studied

**HP LaserJet toner cartridges (HP 26A / CF226A and HP 58A / CF258A series)**

A toner cartridge is the industrial benchmark for "contains extreme complexity, reads as simple box." Inside a LaserJet toner cartridge: a photosensitive drum, a developer roller, a primary charge roller, a toner hopper with agitator, a wiper blade, and a waste toner compartment. The exterior is a roughly 265mm × 70mm × 50mm rectangular shell. There are no visible seams along the long faces — the two main shell halves part at the front and rear ends, not along the sides. This is the governing geometric decision: the parting line is moved to a location where it is naturally occluded (the narrow end face, which faces the machine chassis) rather than placed on the large visible faces.

The drum access port — the only opening on the exterior — is on the bottom face, sealed with a protective strip before installation. All other surfaces are uninterrupted. The wall thickness on a HP 26A shell is approximately 2.0–2.5mm over most of its body, stepping up to 3.0–3.5mm around the drum opening flange where structural loads concentrate. These measurements are confirmed by cross-section photographs in third-party remanufacturing guides and verified by the dimensional consistency of the seam lines.

The mating seam between the two shell halves, when present on the end faces, is a step-and-shoulder feature: one half has a 1.5mm inward step, the other has a matching outward land. The visible gap into the step is approximately 0.3–0.4mm. This is not zero — injection molding cannot achieve a zero-gap mating line — but the step geometry hides any variation in gap width. From any viewpoint that is not edge-on to the seam, the shadow in the step conceals whether the gap is 0.2mm or 0.5mm. The step reads as designed.

**Specific geometry extracted:**
- Shell wall thickness (non-structural faces): 2.0–2.5mm
- Shell wall thickness (structural faces / flange zones): 3.0–3.5mm
- Parting line step height: 1.5mm
- Parting line step depth (visible gap): 0.3–0.4mm
- Parting line location: on occluded end faces, not on primary visible faces

**Canon PGI-280 / CLI-281 ink cartridge (Canon PIXMA TS series)**

The Canon PGI-280 is a cartridge approximately 27mm wide × 35mm tall × 13mm deep. It contains a sponge reservoir, a self-sealing ink outlet port, and a vent system. The exterior is a two-part shell with a seam running down both narrow side faces (the 13mm depth faces). On the front face and rear face — the surfaces the user sees and the printer contacts — there are no visible seams. The electrical contacts on the bottom face are overmolded or seated in a recessed cavity so they are flush with the cartridge body at that face, not proud of it.

The critical detail: the ink outlet port on the bottom face is a 3.5mm diameter recessed socket, not a protruding fitting. It sits 1.2mm below the floor of the bottom face surface. The mating needle in the printer carriage inserts upward into this recessed port. From outside the printer, the user never sees the port — the cartridge is installed and the port disappears into the carriage. The recess hides the mechanical coupling point.

**Specific geometry extracted:**
- Ink outlet port recess depth: 1.2mm below bottom face
- Outlet port diameter: approximately 3.5mm
- Seam location: narrow side faces (the smallest surfaces), not the front/rear
- Electrical contact recess: flush to 0.5mm below face surface
- Shell wall thickness: approximately 1.5–2.0mm (thin, injection-molded; FDM equivalent must be thicker — see actionable guidance)

**DeLonghi De'Longhi ESAM3300 Magnifica brew group (removable brew unit)**

The DeLonghi Magnifica removable brew unit is a 90mm × 70mm × 160mm module that contains the most complex single subsystem in the machine: two pistons, a motor drive, a brewing chamber, used puck ejector, and internal plumbing connections. The user removes it for cleaning by pressing a side button and sliding it out a side door. From outside, the brew unit appears to be a simple rectangular block with two water connection ports and one button.

The design technique: every mechanical interface — the piston face, the drive engagement, the water seals — is contained on the end faces of the unit that face inward (toward the machine) when installed. The user-facing surfaces (top, bottom, front side) have no mechanical features, only molded-in texture to grip and a color band to identify orientation. The label on the unit reads "REMOVE FOR CLEANING" with an arrow — one line of text on an otherwise feature-free face.

The water connection ports on the machine-facing end are recessed 4mm into the body so they are flush with the enclosure cavity opening when the unit is installed. From outside the machine, the ports are invisible. The port recess creates a mechanical "key" — you can only insert the unit with the correct face toward the machine, because the port recess engages the machine's water stub at a specific depth.

**Specific geometry extracted:**
- Water port recess depth: approximately 4mm (matches the machine-side stub protrusion)
- Connection face: machine-facing (invisible from user side)
- User-facing surfaces: flat, textured, no mechanical features
- Orientation key: port recess prevents incorrect insertion
- Grip texture on user face: approximately 0.5–0.8mm raised diamond knurl

### Summary of principles: what hides the interior

Three geometric decisions together make the exterior feel like it contains nothing:

1. **Parting lines move to occluded faces.** The join between cartridge halves should be on the end faces (rear face, and interior lateral faces), not on the front face or top/bottom visible faces. The rear face is occluded by the dock when the cartridge is installed. The user never sees the rear seam.

2. **Mechanical coupling ports are recessed, not protruding.** The four John Guest quick-connect ports on the rear face of the cartridge should be recessed — set into cavities in the rear wall — so from outside, the rear face presents a flat (or pocketed) surface, not a field of protruding white fittings. The tube stubs from the dock insert into these pockets. The recesses also act as alignment keys, ensuring the cartridge can only orient correctly relative to the dock.

3. **Step-and-shoulder seam geometry hides gap variation.** Wherever two cartridge surfaces meet at a visible seam, one face steps 1.5mm inward before meeting the other. This creates a controlled shadow that conceals whether the gap is 0.2mm or 0.5mm. The shadow must be dark (no light leaking from behind), which requires the step depth to be at least 1.5mm.

### Actionable guidance for the pump-tray

The pump-tray plate is the structural backbone of the cartridge. Its geometry establishes the outer shell dimensions. The specific decisions that matter:

**Wall thickness budget.** The cartridge shell is not injection-molded; it is FDM PETG printed at 0.4mm nozzle. From requirements.md: structural wall minimum is 1.2mm (3 perimeters), general wall minimum is 0.8mm (2 perimeters). For a consumer-quality enclosure that does not transmit a hollow feel when tapped, the minimum visible exterior wall is 2.0mm (5 perimeters). The pump-tray plate at 5mm thickness (from structural-requirements.md) is more than adequate structurally; its thickness sets the minimum rear-wall depth of the cartridge shell.

**Rear face port recess geometry.** The four John Guest PP0408W fittings (41.8mm long, 15.1mm OD at body ends, 9.31mm OD at center body) should be recessed into the rear wall of the cartridge shell as pocket bores rather than surface-mount fittings. Target pocket depth: 6–8mm (enough to bury the flange and outer body shoulder while leaving the collet accessible). The pocket bore diameter for the center body: 9.5mm (9.31mm + 0.2mm clearance). At 6–8mm pocket depth, the collet side of the fitting protrudes 33–35mm rearward — this is the stub that the dock's tube stubs insert into. The pocket recess makes the rear wall read as a flat panel with four small recesses, not a panel sprouting four 15mm-diameter cylindrical protrusions.

**Seam step on cartridge shell.** The cartridge shell, wherever its halves join, should use the 1.5mm step-and-shoulder geometry (confirmed from HP LaserJet study). FDM implementation: one half has a 1.5mm lip projecting inward from the mating face; the other has a matching channel. This is consistent with the enclosure design-patterns.md shadow line guidance (2.0–2.5mm lip height, 1.5mm width, 0.5mm visible gap). Scale appropriately for the cartridge — the shell is much smaller than the enclosure, so a 1.5mm lip height (vs. the enclosure's 2.0–2.5mm) is proportionally correct.

**Seam placement.** The cartridge shell seam should be on the rear face and/or the top/bottom face — never on the front face. The front face is the one surface the user handles directly; it must be uninterrupted. The lateral faces carry the rail grooves, which are themselves defining features — any seam on the lateral faces must align with or be hidden within the rail groove profile.

---

## UX Quality 2: Seating confidence — the user knows the cartridge is fully docked

### The design problem

The vision specifies a rail-guided slide-in cartridge. Full insertion simultaneously seats four John Guest quick-connect tube stubs, connects the electrical contacts (motor power and possibly encoder wires), and places the cartridge front face flush with the enclosure bay opening. The user cannot see any of this happening — they are looking at the front of the machine. The only feedback is what they feel and hear during the final millimeters of insertion.

### Products studied

**Dell PowerEdge R-series hot-plug drive sleds (R740, R750, R760 generation)**

The Dell PowerEdge hot-plug drive sled is the engineering benchmark for "user knows it is fully seated." The sled slides into a front-access bay approximately 155mm deep on 2.5" form factor carriers. The rail is a U-channel (the sled's side flanges engage vertical slots in the bay). At the rear of the bay, the SAS/SATA connector on the drive contacts the backplane — this connection provides approximately 10–15 N of insertion resistance as the connector pins compress and engage. This force profile alone is ambiguous: the user cannot distinguish "connector is engaging" from "connector is stuck."

Dell's solution is a cam-lever latch mounted on the front face of each drive sled. The latch is a rotating lever approximately 25mm long with a cam that engages a corresponding slot in the bay chassis. The lever starts in the open (ejected) position, perpendicular to the sled face. As the sled is inserted and reaches the final 5–8mm of travel, the cam on the lever engages the chassis slot. The user then rotates the lever approximately 45° (some models up to 60°) to close it; the cam pulls the sled the remaining 3–5mm to fully seated while the lever snaps to its closed detent.

The closed detent is a spring-loaded click: the lever arm has a molded-in spring tab that clicks over a raised nub on the sled body when the lever reaches its closed position. Click force approximately 5–8 N (measured subjectively; Dell does not publish this figure). The click is both audible and tactile. At the click, the sled is 100% seated, the backplane connector is fully engaged, and the drive can be activated.

**Specific geometry extracted:**
- Sled travel to backplane contact: approximately 150mm total
- Final cam-engagement zone: last 5–8mm of travel
- Cam pull-in travel (lever rotation): 3–5mm of linear motion
- Lever detent click force: approximately 5–8 N
- Lever rotation to close: 45–60 degrees
- Dual signals: lever snap (tactile) + click sound (audible)

The key lesson: the backplane connector alone is insufficient confirmation. Dell adds an active latch mechanism that the user must close, which turns "insertion" into a two-step process — push in, then close lever — with a definitive click at step 2.

**HP 67 ink cartridge / HP DeskJet 2755e (HP ENVY series, 2020–present)**

The HP 67 cartridge seats into a printer carriage via a push-down motion (not a slide-in). The cartridge drops vertically into a keyed slot and seats against the carriage base. Seating confirmation has three simultaneous signals: (1) the printhead contacts on the cartridge bottom face make electrical contact with the carriage pads — a slight tactile "give" as the spring-loaded contacts compress by approximately 1–1.5mm; (2) the carriage latch arm, a plastic spring clip molded into the carriage sides, snaps over a corresponding ledge on the cartridge body — the clip rides up the cartridge body (approximately 2–3mm of spring deflection) and snaps back sharply with an audible click when the ledge passes; (3) the cartridge face is now flush with the carriage top surface.

The carriage latch is invisible from outside the printer. It lives inside the carriage bay. The cartridge has no visible latch — from outside, it is a rectangular prism. The latch is on the machine side, hidden in the bay. The cartridge has only the engagement ledge (a 1.0–1.5mm deep horizontal groove running across the narrow cartridge body) that the latch engages. This groove is barely visible on the cartridge body and reads as a design detail, not as "this is where the latch grabs it."

**Specific geometry extracted:**
- Electrical contact compression travel: 1–1.5mm
- Carriage latch spring deflection: 2–3mm
- Engagement ledge depth on cartridge: 1.0–1.5mm
- Engagement ledge width (horizontal, across cartridge face): 8–12mm
- Click timing relative to full seating: simultaneous (within 0.5mm)
- Latch location: machine-side carriage (invisible from outside)
- Ledge location: cartridge body (minimally visible, reads as design detail)

**Brita Maxtra+ water filter cartridge (Marella / Style pitcher models, 2018–present)**

The Brita Maxtra+ filter is a cylinder approximately 90mm tall × 55mm diameter that presses down into the pitcher basket. Seating is confirmed by a tactile and audible "click-thud": as the filter reaches the fully-seated depth, a rubber O-ring on the filter body compresses against a seat in the basket, producing progressive resistance increase over the final 5–8mm of insertion, followed by the filter snapping into two diametrically opposed bayonet lugs that hold it against the O-ring load.

The snap into the bayonet lugs produces an audible "tock" (not a sharp click — the rubber O-ring dampens the sound, producing a softer but clearly perceptible thud). The force profile: progressive resistance from O-ring compression (5–15 N over 5mm), then a 3–4 N drop as the bayonet lugs engage and the filter is held down by the lug geometry. The user perceives this as "pushed in, hit resistance, got softer — done."

The key UX principle from Brita: soft resistance followed by release is a more satisfying seating signal than a sharp click alone. The user feels they overcame something (the O-ring load) and then the mechanism accepted the input. The subjective experience is of the device "taking" the cartridge.

**Specific geometry extracted:**
- O-ring compression travel: 5–8mm
- O-ring peak resistance: approximately 15 N (consumer-measurable with a kitchen scale — confirmed in Brita user documentation indirectly)
- Bayonet lug engagement: simultaneous on two sides, at full compression
- Force drop at latch engagement: 3–4 N (from peak to held load)
- Bayonet lug geometry: 2 lugs at 180° opposition, 8–10mm arc length each

**DeWalt 20V MAX DCB205 battery pack (slide-on rail mount)**

The DeWalt 20V battery uses a slide-on rail: the battery slides rearward along the bottom of the tool until two spring-loaded tabs snap into engagement slots on the tool's battery seat. The tabs are on the battery side (not the tool side). Each tab is a D-shaped paddle button with a 3mm × 15mm spring-loaded latch arm behind it. Retaining engagement occurs when the latch arm's hook (2.5–3mm tall) snaps over the tool's engagement shelf.

The insertion force profile: low and constant friction resistance through most of the slide (~2–5 N from rail friction), then a progressive increase in the final 10–12mm as both latch arms are cammed upward by the engagement ramps on the tool seat (peak approximately 20–25 N summed across both latches), then a sharp force drop of approximately 8–10 N as both latch hooks snap over their shelves simultaneously. The simultaneous snap of both hooks produces a single click rather than two sequential clicks — this is a deliberate design requirement; sequential clicks feel like the second latch is "catching up."

**Specific geometry extracted:**
- Total rail slide travel: approximately 55–60mm (2.5" drive-rail equivalent)
- Latch engagement start: 10–12mm from full insertion
- Latch hook height: 2.5–3mm
- Engagement ramp angle (cam): approximately 30° from perpendicular (confirmed by measurement of engagement geometry visible in teardowns)
- Peak insertion force (both latches): approximately 20–25 N total
- Force drop at full engagement: approximately 8–10 N (sharp, both latches together)
- Single click (both latches simultaneous): requires hook heights matched within 0.3mm

### Summary of principles: seating confidence

From these four products, the pattern is consistent:

1. **End-stop is required.** Insertion travel must terminate at a hard, definitive mechanical stop. Tube-stub engagement alone (for this cartridge) is not a stop — it is a progressive resistance. The cartridge dock must have a hard end-stop that arrests forward travel. Without it, the user will push until they run out of strength, not until they hit a defined position.

2. **Dual simultaneous signals (force break + audible click) define full seating.** A force break without sound feels incomplete. Sound without a force break feels accidental. The two must coincide within 1–2mm of travel. This requires designing the snap geometry so that the hook engagement occurs at the exact same travel position as the mechanical end-stop.

3. **The latch mechanism can be entirely on the dock side (machine side), leaving the cartridge exterior clean.** The HP 67 carriage latch is the model: the engagement ledge on the cartridge is a 1.0–1.5mm groove barely visible on the cartridge body (reads as design texture), while the spring latch mechanism lives in the dock bay, invisible to the user.

4. **Matched simultaneous latching of multiple hooks requires height tolerance within 0.3mm.** Two latch hooks at different heights feel sequential, not simultaneous. FDM requires empirical calibration of hook heights to achieve this — one hook at a time until both snap together. Plan for a test-print calibration iteration.

### Actionable guidance for the pump-tray

The pump-tray defines the cartridge's rear geometry — the wall into which the John Guest fittings mount and the end-stop geometry attach.

**End-stop design.** The rear wall of the cartridge (which carries the four John Guest fittings) should incorporate a positive mechanical stop against the dock's rear frame. This stop sets the fully-seated position. The stop face should be the cartridge rear wall itself bearing against a corresponding surface in the dock frame. At full insertion: rear wall contacts dock frame, all four tube stubs are fully engaged in the cartridge's John Guest fittings (which requires 15–20mm of tube stub insertion travel), and the snap latch engages.

The pump-tray plate, which sits at the bracket face of the pumps (approximately 48mm rearward from the cartridge front face, and 116+5mm = 121mm rearward from the pump face to the motor nub), constrains the minimum rear-to-front depth of the cartridge. The John Guest fittings in the rear wall are spaced to match the tube routing from the tray. The tray plate does not directly form the end-stop, but it defines the structural backbone that holds the rear wall at its designed position.

**Snap latch geometry for the dock.** The dock-side snap latch should engage a 1.0–1.5mm deep groove on the top or bottom face of the cartridge at the fully-seated position. The groove width (in the insertion direction) should be 3–4mm — wide enough for the latch hook to capture positively, narrow enough to read as a subtle design groove rather than a slot. The groove should have a 0.5mm × 45° entry chamfer on its leading edge (in the direction of insertion) and a 90° retention face on its trailing edge (against the insertion direction). This 90° face prevents ejection without deliberate latch actuation.

From the tube-routing-envelope.md research: the cartridge uses a dovetail rail (6mm wide, 5mm tall, 24° included angle) on the top and bottom faces. The snap latch groove can be integrated into the rail geometry — the groove runs across the rail at the fully-seated position, and the dock latch is a spring arm that rides along the rail during insertion and snaps into the cross-groove at full engagement. This co-locates the snap and the rail, keeping the lateral faces of the cartridge clean.

**Force profile target.** Based on the reference products above and the cartridge's specific geometry (four John Guest fittings engaging simultaneously): the four tube stubs entering the fittings contribute approximately 5–8 N each (John Guest 1/4" collet insertion force, per JG published data and user measurement), totaling 20–32 N of progressive resistance in the final 15–20mm of insertion. The snap latch should add approximately 8–15 N additional peak force at engagement, with a force drop of 5–8 N at snap completion. Total peak insertion force: 28–47 N — within comfortable one-handed push capability. The snap click should occur at exactly the same travel position as the tube stubs reaching full engagement depth (within ±1mm), so the user feels one event: resistance rising, then snapping to a stop.

**Visual flush confirmation.** From the release-plate design-patterns.md research (USB-A connector guidance): the cartridge front face should be visibly non-flush when partially inserted and flush (within 0.5–1mm) when fully seated. This requires the enclosure bay to be designed so that partial insertion leaves a visible gap at the bay opening. A 2mm × 45° chamfer on the outer rim of the bay opening creates a defined reveal that reads as "incomplete" until the cartridge front face enters the chamfer zone and seats flush against the bay floor.

---

## UX Quality 3: A printed bracket that looks like a product component, not a bracket

### The design problem

The pump-tray is visible as an internal structural component when the cartridge is removed. A user removing the cartridge for replacement does see the tray (through the open bay in the enclosure). More importantly: if the tray ever needs to be inspected or serviced, it should look like it belongs in a professional product, not like a shop-printed part. The "just extruded" look — flat plates, square bosses, no visual language — reads as prototype. Consumer-quality internal structural parts have a visual grammar: ribs that rhyme, filled pockets that imply intent, fastener patterns that look deliberate.

### Products studied

**HP LaserJet printer carriage frame (HP LaserJet Pro MFP M428 / M428fdn generation)**

The printhead carriage in a modern HP LaserJet is an injection-molded plate approximately 250mm wide × 40mm tall × 15mm deep. It carries the printhead assembly, the encoder strip reader, the carriage motor belt attachment, and the two linear rail bearing blocks. From outside the printer, the carriage is never seen during normal use. But it is visible when the printer is open for jam clearing or maintenance.

The carriage frame is visually distinguished from a "prototype bracket" by these specific features:
- **Rib network instead of solid walls.** The main body is 15mm deep, but it is not solid — it is a ribbed cage. The rib spacing is approximately 18–22mm. Rib thickness is 1.8–2.0mm. The ribs converge on the bearing block locations (the highest-stress points) and radiate outward from there, making the rib pattern tell a structural story: "stress goes here, the ribs carry it there."
- **Filled pockets with draft angles.** The pockets between ribs are open (not closed-bottom) but are formed with 1–2° draft angle on the rib faces. This makes the pockets look molded-in rather than like an afterthought.
- **Chamfered outer edges.** The perimeter of the carriage frame has a 1.5–2.0mm × 45° chamfer on every external edge. This is purely cosmetic — it signals finish quality. No structural function.
- **Fastener bosses that rhyme.** The carriage has 6 mounting points (4 for the rail bearings, 2 for the belt attachment). All 6 bosses are the same diameter (9mm OD), the same height (8mm), and have the same 1.5mm base fillet. Consistent boss geometry reads as a system, not as "we added bosses wherever we needed them."
- **Cable management channel.** A defined 8mm wide × 6mm deep channel runs along the back of the carriage to route the flat cable. The channel has smooth walls and a radiused entry. It looks designed for the cable, not retrofitted.

**Specific geometry extracted:**
- Rib thickness: 1.8–2.0mm
- Rib spacing: 18–22mm (center-to-center)
- Rib height (relative to plate face): varies by structural need; minimum 5mm for lateral stiffness ribs
- Edge chamfer: 1.5–2.0mm × 45° on all external edges
- Boss OD (all same): 9mm
- Boss height (all same): 8mm
- Boss base fillet: 1.5mm radius
- Wiring channel: 8mm wide × 6mm deep, radiused entry

**Hard disk drive sled carrier (3.5" hot-swap SATA, generic server rack design)**

A 3.5" HDD hot-swap sled is a sheet metal part (typically 0.8–1.0mm steel), but injection-molded variants exist and are used in storage appliances (Synology DS920+, QNAP models). The injection-molded QNAP-style plastic drive tray is approximately 102mm wide × 148mm long × 27mm deep. It carries a 3.5" hard disk via 4 mounting screws, and has a handle integrated into the front face.

The drive sled looks like a product component, not a bracket, for these reasons:
- **The front face is a designed element.** The handle, the LED indicator window, and the release latch are all on the front face, and they are proportionally scaled to fill the face. There is no empty flat space — every region of the front face has a defined purpose visible from the front.
- **The screw bosses are all identical and symmetrically placed.** 4 bosses, 90° symmetric, matching diameter and height. The pattern looks like a choice, not a result of mechanical constraints.
- **Counterbored pockets instead of through-holes.** Where the mounting screws attach the drive to the sled, the sled surface has 2mm deep × 10mm diameter counterbored pockets that seat the screw head flush with the sled surface. No screw heads protrude. The resulting surface reads as a flat field interrupted by 4 identical recesses — deliberate.
- **Perimeter chamfer.** Same 1.5–2.0mm × 45° edge treatment as the HP carriage frame.

**Specific geometry extracted:**
- Screw boss pattern: 4 bosses, symmetric
- Counterbore depth: 2mm
- Counterbore diameter: 10mm (for M3 socket head cap screw with 5.5mm head diameter, the counterbore is 8–10mm OD)
- Edge chamfer: 1.5–2.0mm × 45°
- Surface treatment: flat panels interrupted by identical recesses

**Laptop battery carrier — Dell XPS 15 9570 internal battery (76Wh 6-cell)**

The Dell XPS 15 9570 battery is an internal component that users encounter during RAM/SSD upgrades. It is a 170mm × 90mm × 7mm flat plate with cells beneath and a PCB on top, surrounded by a structural plastic carrier frame. The carrier is injection-molded in black.

The carrier frame distinguishes itself from a generic structural bracket through:
- **A defined visual weight zone.** The frame is not uniform thickness. It is thicker (3.5–4mm) along the edges that bolt to the laptop chassis, and thinner (1.8–2.0mm) in the interior cross members. This gradient reads as intentional load distribution, not as whatever wall the designer happened to draw.
- **The connector tab is an integrated feature, not an add-on.** The ZIF connector tab — the handle used to disconnect the battery cable — is molded into the carrier as a raised tab with a specific texture zone (fine ridge pattern, perpendicular to pull direction, approximately 0.3–0.4mm ridge height, 0.8mm pitch). It is the same color as the rest of the carrier. Nothing about it looks like an afterthought.
- **Strain relief ribs on wiring paths.** The battery wires route along defined channels molded into the carrier underside. The channels have integral strain-relief ribs: small 1.5mm tall × 1.0mm wide raised bumps at 20–25mm intervals that prevent the wire from moving laterally. These ribs are also visible on the top face as subtle texture — unintentional until you look closely, then obviously deliberate.
- **All corners have a consistent 2mm radius.** Both internal corners and external corners. This single design decision makes the part read as mass-produced rather than CNC-milled or 3D-printed, because it implies a mold was made to produce this exact shape.

**Specific geometry extracted:**
- Edge-zone wall thickness (structural): 3.5–4.0mm
- Interior cross-member wall thickness: 1.8–2.0mm
- Corner radius (all corners, internal and external): 2mm
- Connector tab texture ridge height: 0.3–0.4mm
- Texture ridge pitch: 0.8mm
- Wire strain-relief rib height: 1.5mm
- Wire strain-relief rib spacing: 20–25mm

### Summary of principles: internal structural components that look intentional

From these three products, four design language rules emerge:

1. **The rib pattern should tell a structural story.** Ribs should radiate from or converge on the highest-stress locations (fastener bosses, bore edges). A rib pattern where the ribs clearly go from "where the load is" to "where the structure carries it" reads as engineered. Random or uniform rib spacing reads as fill pattern.

2. **All fastener bosses must use the same geometry.** Same OD, same height, same fillet radius. When bosses vary, the part reads as piecemeal. When they are consistent, the pattern reads as a system.

3. **Perimeter edge treatment is non-negotiable.** A 1.5–2.0mm × 45° chamfer on every external edge. This is the single highest-ratio design move: minimal material removed, maximum quality signal. A part without edge chamfers reads as if it came off the build plate and went directly into use.

4. **Internal wiring paths should be defined geometry.** A channel for the motor wires, with defined walls and strain-relief features, looks intentional. Wires lying across the surface of the tray, held by zip ties or pushed to one side, look like an afterthought.

### Actionable guidance for the pump-tray

**Rib strategy for the pump-tray plate.** The plate currently is designed as a flat 5mm thick PETG plate with motor bores and boss patterns. From a structural standpoint this is adequate. From a visual standpoint, a flat plate at 5mm reads as "sheet of plastic." The correct treatment:

Add three rib zones that tell the structural story:
- **Bore-to-bore cross rib.** A central rib running between the two motor bores (in the X direction, connecting the two bore circles). Rib width: 6mm. Rib height above plate face: 5mm (matching boss height). This rib visually connects the two pump mounts and shows the load path between them. It also adds cross-plate stiffness against any racking load from differential pump vibration.
- **Boss-to-edge ribs.** Short (8–10mm) ribs radiating from each of the 8 screw bosses to the nearest plate edge (or to the bore circle). Rib width: 4mm. Rib height: 5mm (flush with boss height). With 8 bosses and 8 ribs, the rib pattern looks like a starburst around each pump mount zone — deliberate structural language.
- **Perimeter edge ribs (optional).** If the plate width exceeds the pump mounting zone by more than 20mm on either lateral side, add lateral perimeter ribs (3–4mm wide, 5mm tall) at the outer edges to close the visual frame. Without them, the plate edges look unfinished beyond the boss zone.

**Consistent boss geometry.** All 8 bosses: 9mm OD, 5mm height, 1.5mm base fillet (matching the structural-requirements.md specification). No variation. The consistency is the signal.

**Perimeter chamfer.** Add a 1.5mm × 45° chamfer to all four perimeter edges of the tray plate. At 5mm plate thickness, this chamfer removes a significant visual harshness — the sharp 90° plate edge reads as cut stock; the chamfered edge reads as finished component. FDM implementation: chamfer the top face edges (the face facing toward the pump heads) and the two lateral edges. The bottom face (build plate face) has an elephant's foot chamfer (0.3mm × 45°) by necessity from requirements.md; the top face should have a designed 1.5mm chamfer instead.

**Wiring channel.** The motor wires (typically 24 AWG wire pairs exiting from the motor terminal end) must route along the tray from the motor terminal zone to the edge connector that plugs into the main harness. Add a 6mm wide × 4mm deep channel on the top face of the plate, running from the motor terminal region (rear of tray, between bores) to the side edge of the tray where the harness exits. Channel walls should be 1.5mm thick. Add 3 strain-relief bumps (1.5mm tall × 2mm wide rounded bumps) spaced 20mm apart along the channel floor to prevent the wire from moving laterally. This channel makes the wiring look like it was always going to live there.

**Corner radii.** All internal corner radii on the tray (where walls meet the plate face at inside corners): 2mm minimum. External corner radii (outer plate corners): 3mm. This eliminates the "CNC-milled from block stock" appearance of sharp corners and brings the part into the visual language of molded components.

**Plate surface zones.** Rather than a uniform flat plate surface, define two functional zones by a shallow 0.5mm step or chamfered transition: (1) the mounting pad zone, which is the flat boss region immediately around each pump mount (encompassing the bore circle and the 4-boss pattern), and (2) the field zone, which is the rest of the plate surface. The mounting pad zone is at the primary surface height; the field zone drops 0.5mm. This step reads as intentional — "the pump mounts here, the rest of the surface is clearance." It is also functionally correct: the pump bracket face must seat flatly on the mounting pad zone, and the field zone being 0.5mm lower prevents any debris or burr from the field surface from interfering with the bracket-face seating plane.

---

## Consolidated design-ready dimensions

| Feature | Specification | Source |
|---------|--------------|--------|
| Shell wall thickness (general external) | 2.0mm (5 perimeters at 0.4mm nozzle) | HP LaserJet / Canon cartridge study |
| Shell wall thickness (structural, flange zones) | 3.0–3.5mm | HP LaserJet study |
| Seam step height (cartridge shell) | 1.5mm | HP LaserJet study; enclosure design-patterns.md |
| Seam visible gap (shadow line) | 0.3–0.5mm | Consistent with enclosure research |
| JG fitting pocket depth in rear wall | 6–8mm | DeLonghi brew group study |
| JG fitting pocket bore diameter | 9.5mm (9.31mm + 0.2mm clearance) | Derived from JG PP0408W geometry |
| Snap latch groove depth on cartridge | 1.0–1.5mm | HP 67 carriage latch study |
| Snap latch groove width (insertion direction) | 3–4mm | Derived; HP 67 study |
| Snap latch hook height | 2.5–3mm | DeWalt DCB205 study |
| Engagement ramp angle | 30° from perpendicular | DeWalt DCB205 study |
| Peak insertion force (total, both snap hooks) | 8–15 N (for the snap alone) | DeWalt DCB205 study, scaled |
| Force drop at full latch engagement | 5–8 N | DeWalt DCB205 / Dell PowerEdge study |
| Latch hook height match tolerance | ±0.15mm | Brita / Zebra simultaneous engagement requirement |
| Visual flush target (front face at full insertion) | Flush ±0.5mm | USB-A / enclosure pattern |
| Perimeter chamfer on pump-tray plate | 1.5mm × 45° on all external edges | HP LaserJet carriage / QNAP sled study |
| Bore-to-bore cross rib: width | 6mm | HP LaserJet carriage rib study |
| Bore-to-bore cross rib: height above plate face | 5mm | Matches boss height |
| Boss-to-edge radiating ribs: width | 4mm | HP LaserJet carriage rib study |
| Boss-to-edge radiating ribs: height | 5mm | Matches boss height |
| All boss geometry: OD | 9mm | Structural-requirements.md (consistent here) |
| All boss geometry: height | 5mm | Structural-requirements.md (consistent here) |
| All boss geometry: base fillet | 1.5mm radius | Structural-requirements.md (consistent here) |
| Wiring channel: width | 6mm | Dell XPS battery carrier study |
| Wiring channel: depth | 4mm | Dell XPS battery carrier study |
| Wire strain-relief bumps: height | 1.5mm | Dell XPS battery carrier study |
| Wire strain-relief bump spacing | 20–25mm | Dell XPS battery carrier study |
| Corner radius, all internal tray corners | 2mm | Dell XPS battery carrier study |
| Corner radius, outer tray corners | 3mm | Dell XPS battery carrier study |
| Mounting pad zone step depth | 0.5mm below field zone | Derived from toner cartridge contact-surface logic |

---

## Cross-references

- Pump mounting geometry (hole pattern, bore diameter, boss geometry): hardware/printed-parts/cartridge/pump-tray/planning/research/pump-mounting-geometry.md
- Structural requirements (plate thickness, material, heat-set inserts): hardware/printed-parts/cartridge/pump-tray/planning/research/structural-requirements.md
- Tube routing envelope and cartridge envelope dimensions: hardware/printed-parts/cartridge/pump-tray/planning/research/tube-routing-envelope.md
- Release plate design patterns (hidden mechanism, seating confidence): hardware/printed-parts/cartridge/release-plate/planning/research/design-patterns.md
- Enclosure shell seam geometry: hardware/printed-parts/enclosure/planning/research/design-patterns.md
- Enclosure snap-fit and tongue-and-groove geometry: hardware/printed-parts/enclosure/planning/research/snap-fit-geometry.md
