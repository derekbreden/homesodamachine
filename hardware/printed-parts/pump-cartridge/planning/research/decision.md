# Pump Cartridge Design Decision

## Summary

**Recommendation: Front-slide on rails with a flip-down lever lock.**

The cartridge slides in from the front on parallel rails (like a Dell hot-swap drive carrier), and a lever on the cartridge front face flips down to cam the cartridge the final 3mm into full seat, locking it and completing all 4 fluid connections. Flipping the lever up cams a release plate that pushes all 4 John Guest collets simultaneously, then the cartridge slides out. The lever IS the handle for removal.

The pumps sit side by side with their long axes perpendicular to the insertion direction, motors facing rearward.

---

## Candidates Evaluated

### Candidate A: Front-Slide with Lever Lock (RECOMMENDED)

**Interaction:** The user grips the cartridge by its front face, aligns it with the dock opening, and slides it in on C-channel rails. The last 15mm of travel meets increasing resistance as tube stubs enter the John Guest fittings. A lever (integrated into the cartridge front face) starts in the "up" position. The user flips it down. A cam on the lever's pivot converts the 90-degree rotation into 3mm of rearward axial pull, drawing the cartridge body backward onto the tube stubs to full seat depth. The lever clicks into a detent at the locked position.

**To remove:** The user flips the lever up. The cam now pushes a release plate forward (toward the user), compressing all 4 collets simultaneously. At the top of the lever travel, a detent clicks. The cartridge is now free. The user grips the lever (which doubles as a pull handle) and slides the cartridge out on the rails.

**Fluid connections:** 4 tube stubs (1/4" OD hard PE, chamfered tips) protrude from the dock rear wall. They insert into 4 John Guest PP0408W fittings mounted in the cartridge rear face (center body press-fit in 9.5mm bores). Entry funnels (12mm mouth, 8mm depth) printed around each fitting bore guide the stubs in. Registration bosses on the dock wall engage tapered sockets in the cartridge before the tubes reach the fittings.

**Seating feedback:** Three-stage: (1) rails click into the dock opening with light snap-fit detent, (2) tube stubs enter fittings with tactile resistance increase, (3) lever clicks down into locked detent. The user cannot miss any stage.

**Pump arrangement:** Two Kamoer pumps side by side, long axes (motor shafts) pointing rearward (away from user), pump heads facing forward. The cartridge body is approximately 140mm wide x 120mm deep x 70mm tall.

**Why this wins on UX:**
- The slide-on-rails motion is the most intuitive blind insertion paradigm (Dell drive carrier, DeWalt battery, HP inkjet). The user cannot misalign because the rails only accept one orientation.
- The lever provides a binary locked/unlocked state with an audible click. There is zero ambiguity about whether the cartridge is seated.
- The lever doubles as the removal handle, so the user never searches for "how do I get this out." Flip up, pull.
- The lever-cam final seating means the user does not need to push hard to fully seat the fittings. The cam's mechanical advantage does the work, making insertion feel smooth rather than stiff.
- Sequential engagement (rails first, then alignment bosses, then fittings, then lever lock) gives the user progressive feedback at each stage rather than one ambiguous push.

**Mechanical feasibility:** The cam profile is a simple eccentric on the lever pivot shaft. The lever arm is ~40mm; the cam rise is 3mm. Mechanical advantage is roughly 13:1, meaning the 20-32N total collet force requires only 1.5-2.5N at the lever tip. The release plate is a flat plate with 4 stepped bores (per the John Guest geometry doc) that translates axially against the collet faces. Rails, lever pivot, cam, and release plate are all printable in PETG with no supports if the cartridge prints on its back (lever face up).

**Electrical connections:** Wiping blade contacts on the cartridge rear face mate with spring-loaded contacts in the dock. The contacts engage progressively during the slide-in (like DeWalt battery contacts), making connection before the lever is operated. Three contacts: motor A power, motor B power, common ground. A fourth contact (lock-sense) closes only when the lever reaches the locked position, confirming full seat to the ESP32.

### Candidate B: Bayonet (Push-and-Twist)

**Interaction:** The user pushes the cartridge into the dock and rotates it 45-90 degrees. Bayonet pins on the cartridge engage L-shaped slots in the dock. The twist portion of the L-slot includes a ramp that drives a release plate, compressing collets during insertion (releasing them during the reverse twist for removal).

**UX assessment:** Push-and-twist is familiar (camera lenses, light bulbs, water filters). The detent at the locked position provides clear feedback. Self-aligning via bayonet pins.

**Why it loses to Candidate A:**
- Requires two-handed operation in a tight space. The cartridge is at the bottom-front of the device. One hand must hold the cartridge while the other steadies the device (or the device must be heavy enough to resist torque). The lever in Candidate A requires no counter-torque on the device.
- Twist motions are awkward when reaching down to the bottom of an appliance, especially under a sink cabinet. A flip-lever is operable with one finger.
- No natural handle for removal. After the reverse twist, the user must grip the cartridge body to pull it out. With Candidate A, the lever IS the handle.
- The bayonet ramp must provide both retention AND collet actuation in one cam profile. This couples two functions that have different stroke requirements (retention needs maybe 10mm of engagement depth; collet release needs exactly 3mm of plate travel). Decoupling them (as in Candidate A, where rails handle retention and the lever handles collet actuation) is mechanically cleaner.

**Rank: #2.** A strong backup if the lever proves too bulky for the available space.

### Candidate C: Direct Pull with Side Latches

**Interaction:** The cartridge slides in on rails until latches on both sides snap into pockets in the dock walls. The latches hold the cartridge in place. To remove, the user squeezes both side latches inward (like a DeWalt battery release) and pulls the cartridge out. A release plate is attached to the dock (not the cartridge) and stays stationary; when the cartridge pulls forward, the plate pushes against the collets relative to the retreating fittings.

**UX assessment:** The squeeze-and-pull is familiar from battery packs and phone cases. One-axis motion (no twist).

**Why it loses to Candidate A:**
- Two-handed operation required (squeeze both latches while pulling). Or one-handed with a very deliberate grip.
- No force multiplication for collet release. The user must pull with 20-32N to overcome collet friction, and this force is applied while simultaneously squeezing side latches. Not hard in absolute terms, but it feels "stiff" rather than "smooth."
- The side latches must be accessible in the dock opening, competing for space with the dock walls and rails.
- No progressive engagement feedback. The user gets one click (latches) and then a tug. Contrast with Candidate A's three-stage feedback.

**Rank: #3.** Viable but inferior UX.

### Candidate D: Drawer with Screw-Down Clamp

**Interaction:** The cartridge sits in a tray that slides out on drawer slides (like a server rack). After sliding the tray in, the user turns a thumbscrew or knob on the front face that drives the cartridge rearward into the fittings via a threaded rod or cam.

**UX assessment:** The drawer slide feels premium (smooth, full-extension, soft-close possible). The thumbscrew provides controlled engagement.

**Why it loses to Candidate A:**
- Two discrete actions with no natural sequence: slide in, then screw down. Users will forget the screw step (or partially tighten) and wonder why the device leaks.
- Screw threads are slow. Even a fast thumbscrew (3mm pitch) requires a full turn for 3mm of engagement. The lever in Candidate A achieves the same in a 90-degree flip.
- 3D printed threads wear and bind. A cam on a pivot shaft is far more reliable in FDM plastic.
- The drawer slides add complexity, weight, and potential failure modes (bearings, detent mechanisms). The simple C-channel rails in Candidate A are zero-maintenance.

**Rank: #4.** Over-engineered for the problem.

---

## Decision Matrix

Criteria are ordered by priority per the vision document. Each candidate is scored 1 (worst) to 4 (best) relative to the others in this set.

| Criterion (priority order) | Weight | A: Lever Lock | B: Bayonet | C: Side Latches | D: Screw Clamp |
|---|---|---|---|---|---|
| 1. UX / premium feel | 5 | **4** | 3 | 2 | 1 |
| 2. Mechanical feasibility | 4 | **4** | 3 | 4 | 2 |
| 3. 3D printability | 3 | **4** | 3 | 3 | 1 |
| 4. Durability / cycle life | 2 | 3 | **4** | 3 | 2 |
| **Weighted total** | | **54** | **43** | **40** | **19** |

Candidate A wins on the primary criterion (UX) and ties or leads on all others.

---

## Recommended Design: Detailed Description

### Insertion Sequence (User's Experience)

1. **Pick up cartridge.** The front face has a lever that naturally serves as a grip. The cartridge weighs about 400-500g (two pumps plus plastic housing).
2. **Slide into dock.** The cartridge's side edges engage the dock's C-channel rails. The rails flare at the entry (5mm chamfer) so alignment is forgiving. The user feels the rails grab within the first 10mm of travel.
3. **Progressive engagement.** At about 80mm of insertion, the two registration bosses on the dock's rear wall enter tapered sockets in the cartridge's rear face. The user feels a slight centering pull as the bosses guide the cartridge into precise alignment.
4. **Fittings engage.** At about 95mm of insertion, the 4 chamfered tube stubs enter the entry funnels around the John Guest fittings. The user feels increasing resistance as the tubes push past the collets and O-rings. This tactile change signals "almost there."
5. **Cartridge bottoms out.** At full insertion (~120mm), the cartridge front face is flush with the dock opening. The tube stubs are fully seated in the fittings (16mm insertion depth).
6. **Flip the lever down.** The lever on the front face rotates 90 degrees downward. The cam on the lever's pivot shaft pulls the cartridge body 3mm rearward, fully compressing the fitting seals and engaging the electrical contacts at maximum pressure. A spring-loaded detent clicks at the locked position. The lever sits flush with the front face when locked.

### Removal Sequence (User's Experience)

1. **Flip the lever up.** The user hooks a finger under the lever and rotates it 90 degrees upward. The cam pushes the release plate forward (toward the user), compressing all 4 collets 3mm inward, fully disengaging the grab teeth. A detent clicks at the unlocked position.
2. **Pull.** With the lever still serving as a handle, the user pulls the cartridge straight out. The tubes slide cleanly out of the released fittings. The rails guide the cartridge out smoothly.

### How Fluid Connections Are Made

- **Dock side:** 4 rigid 1/4" OD polyethylene tube stubs protrude 20mm from the dock's rear wall. Tips are chamfered 1.5mm at 45 degrees. The stubs connect to the rest of the plumbing via John Guest fittings mounted in the dock's rear wall (permanent, user never touches these).
- **Cartridge side:** 4 John Guest PP0408W union fittings mounted in the cartridge's rear face. The center body (9.31mm OD) press-fits into 9.5mm bores in the rear wall. The 15.10mm body end sections protrude on both sides of the wall. Inside the cartridge, short lengths of silicone tubing connect from the fitting inner ports to the pump inlet/outlet barbs.
- **Connection:** When the cartridge slides in, each tube stub enters its corresponding fitting through the entry funnel and past the collet. The collet's grab teeth grip the tube. The lever cam provides the final 3mm of seating force.
- **Disconnection:** The lever cam pushes the release plate forward. The plate's stepped bores engage all 4 collets (inner bore clears 6.35mm tube, face contacts collet annular end from 6.69mm to 9.57mm, outer bore hugs 15.10mm body end). All collets compress simultaneously. The tubes slide out freely.

### How the Lever-Cam Works

The lever pivots on a horizontal shaft that spans the cartridge width near the front face. The shaft passes through the cartridge side walls. On each end of the shaft (inside the cartridge walls), an eccentric cam lobe converts rotation into axial displacement of the release plate.

- **Lever down (locked):** The cam lobes are rotated to their minimum-radius position. The release plate is pulled away from the collets (rearward). The plate does not touch the collets. The cam's minimum position also pulls the cartridge body tightly against the dock's datum surfaces.
- **Lever up (unlocked):** The cam lobes rotate to their maximum-radius position (3mm eccentric offset). The cam pushes the release plate forward, compressing all 4 collets. Simultaneously, the cartridge body is pushed 3mm forward (away from the dock rear wall), partially disengaging the tube stubs.

A spring-loaded ball detent (printed PETG ball in a pocket with a small compression spring) clicks into a notch on the cam at both the locked and unlocked positions.

### Pump Arrangement

Two Kamoer KPHM400 pumps mounted side by side:
- Long axes (motor shaft direction) parallel to the insertion axis, motors at the rear
- Pump heads face forward (toward the user)
- Mounting brackets screw to an internal cradle printed as part of the cartridge body
- M3 screws through the bracket mounting holes (49.45mm center-to-center per pump)
- Pump head front faces are set back from the cartridge front face to leave room for the lever mechanism
- Internal silicone tubing runs from pump head barbs to the rear-face John Guest fittings (2 per pump: one inlet, one outlet)

Cartridge approximate outer dimensions: 140mm wide x 120mm deep x 70mm tall. This fits within the 220mm enclosure width with 40mm per side for dock walls and rail structure.

### Electrical Connections

Three spring-loaded blade contacts on the dock rear wall mate with copper pads on the cartridge rear face:
- Motor A power (+12V switched)
- Motor B power (+12V switched)
- Common ground

A fourth contact (lock-sense) is actuated by the lever cam: a small conductive tab on the cam shaft contacts a pad on the cartridge wall only when the lever is in the locked position. This signal routes to the ESP32 to confirm cartridge lock state.

The blade contacts wipe during the last 10mm of insertion, self-cleaning the contact surfaces. Spring pressure ensures reliable contact. The contacts are recessed in the dock wall so they cannot be touched during cartridge handling.

### Alignment System (4-Stage Progressive)

Per the dock alignment research:

1. **C-channel rails** on dock side walls: constrain X (lateral), Z (vertical), roll, yaw. Entry chamfered 5mm. Rail-to-cartridge clearance: 0.3mm per side.
2. **Registration bosses** (2x, diagonal corners): tapered cylinders, 10mm diameter, 15mm long, protruding 10mm farther than tube stubs. Engage before tubes reach fittings.
3. **Entry funnels** printed around each fitting bore: 12mm mouth, 8mm depth, 15-degree taper. Provide 3mm capture radius per fitting.
4. **Tube chamfers:** 1.5mm at 45 degrees on each stub tip. Effective entry point ~3.4mm diameter into 6.69mm collet bore.

---

## Bill of Materials

### Printed Parts (PETG)

| Part | Qty | Print Orientation | Supports Needed |
|------|-----|-------------------|-----------------|
| Cartridge body (main shell) | 1 | Back face down (lever face up) | No |
| Cartridge rear wall (fitting mount plate) | 1 | Flat (fitting bores vertical) | No |
| Release plate | 1 | Flat | No |
| Lever + cam shaft (single piece or 2-part press-fit) | 1 | Lever flat on bed, shaft horizontal | Minimal (shaft bridge) |
| Pump cradle (internal mounting frame) | 1 | Flat | No |
| Dock body (rail structure + rear wall) | 1 | Back face down | No |
| Registration bosses (may be integral to dock rear wall) | 2 | N/A if integral | No |

### Purchased Hardware

| Part | Qty | Source | Notes |
|------|-----|--------|-------|
| John Guest PP0408W 1/4" union fitting | 4 | Already in stock | Press-fit into cartridge rear wall |
| M3 x 8mm socket head cap screw | 4 | Amazon | Pump bracket mounting |
| M3 nut or heat-set insert | 4 | Amazon | Pump bracket mounting |
| Compression spring (5mm OD x 8mm, light) | 2 | Amazon | Ball detent for lever (locked/unlocked positions) |
| Steel ball bearing (4mm) | 2 | Amazon | Ball detent |
| 1/4" OD PE tubing (for dock stubs) | ~80mm | Already in stock | Cut to 20mm x 4 stubs |
| Silicone tubing (internal cartridge routing) | ~400mm | Already in stock | Pump barb to JG fitting |
| Copper foil tape or PCB pads | 4 | Amazon | Electrical contact pads on cartridge rear face |
| Spring-loaded pogo pins or blade contacts | 4 | Amazon | Dock-side electrical contacts |

### Already Owned (Not Purchased)

| Part | Qty | Notes |
|------|-----|-------|
| Kamoer KPHM400 peristaltic pump | 2 | The pumps that go in the cartridge |
| John Guest fittings (dock-side, permanent) | 4 | Connect stubs to main plumbing |

---

## What Would Change This Recommendation

1. **If the enclosure bottom-front has less than 140mm of horizontal opening,** the side-by-side pump layout would not fit. The pumps would need to be stacked vertically (one above the other), making the cartridge taller and narrower. The lever-lock mechanism is unaffected, but the dock opening shape changes. Stacking would increase cartridge height to ~130mm and reduce width to ~75mm.

2. **If the device will routinely be used inside a deep cabinet with very limited vertical clearance above the dock opening,** the flip-up lever might not have room to open fully. In that case, Candidate B (bayonet twist) becomes preferred because it requires no vertical clearance above the cartridge.

3. **If testing reveals that the John Guest collet release force is significantly higher than estimated (e.g., 15N per collet instead of 5N),** the lever cam still handles it comfortably (60N total / 13:1 MA = 4.6N at lever tip), but the release plate and cam surfaces would need to be reinforced. The fundamental design is unchanged.

4. **If the 4-stage alignment system proves insufficient in FDM tolerance testing** (tube stubs miss fitting bores), adding compliance to the tube stubs (mounting them on short flexible sections rather than rigidly) would compensate. This is an incremental change, not a redesign.

5. **If the user base strongly prefers a "no-mechanism" interaction** (just push in and pull out, no lever), Candidate C (side latches with direct-pull release) becomes the answer. This trades premium feel for simplicity. It would only be preferred if user testing showed that people forget or refuse to operate the lever.

6. **If electrical connections prove unreliable with wiping blade contacts** (corrosion in a wet environment near a sink), switching to gold-plated pogo pins or magnetic pogo connectors would solve it. The cartridge geometry and lever mechanism are unaffected.
