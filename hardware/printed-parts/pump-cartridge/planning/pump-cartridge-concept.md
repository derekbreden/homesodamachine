# Pump Cartridge — Conceptual Architecture

## Design Summary

The pump cartridge is a front-removable module containing two Kamoer KPHM400 peristaltic pumps. It slides into a dock at the bottom-front of the enclosure on C-channel rails, makes 4 fluid connections (John Guest PP0408W fittings) and 4 electrical contacts at the rear face, and locks via a flip-down lever whose cam shaft both seats the cartridge and drives a release plate for collet disengagement.

The assembly consists of 8 printed parts (5 cartridge, 3 dock) plus off-the-shelf hardware.

---

## 1. Piece Count and Split Strategy

### Cartridge (5 printed parts)

**Cartridge Tray (1x)** — The structural backbone. An open-top U-shaped tray that holds both pumps side by side. The tray floor has two pump pockets with M3 bosses matching the 49.45mm mounting hole spacing. The tray side walls carry the C-channel rail engagement ribs (male T-profile, full depth). The rear wall is integral to the tray and holds the 4 John Guest fitting bores (9.5mm for center body press-fit) plus 2 registration boss sockets (tapered, 10mm nominal). The rear wall also carries 4 recessed copper contact pads for electrical connection. The tray prints on its back (rear wall down), so the pump pockets, rail ribs, and fitting bores all build upward with no supports.

**Cartridge Lid (1x)** — A flat plate that snaps onto the tray's top edges, capturing the pumps from above. The lid has 4 snap-fit clips (2 per side) that engage detent ridges on the tray side walls. The lid's top surface is the only part visible when the cartridge is docked (if the enclosure front panel has any gap above the lever). The lid prevents the pumps from lifting during removal and keeps the internal silicone tubing routed.

**Lever (1x)** — A single piece that spans the full cartridge width (~130mm). The lever has a flat paddle face (the user's grip surface and the cartridge's front-face identity when locked) and two integral cam lobes at its pivot ends. The pivot shaft is integral — two cylindrical stubs extending from each end of the lever body that press into bearing holes in the tray side walls. The cam lobes are eccentric by 3mm relative to the pivot axis. The lever prints flat on its paddle face; the pivot stubs are short cylinders that print vertically (no supports needed, bridge spans are under 6mm).

**Release Plate (1x)** — A flat PETG plate (~120mm wide x ~50mm tall x 3mm thick) that sits between the tray rear wall and the John Guest fittings' inboard body ends. It has 4 stepped bores (inner: 6.5mm clears tube, face contacts collet annulus from 6.69mm to 9.57mm, outer lip: 9.8mm hugs collet, relief bore: 15.5mm clears body end). Two vertical slots at the plate edges ride on guide posts molded into the tray rear wall, constraining the plate to pure axial (Y-axis) travel. The cam lobes push the plate forward (toward user) when the lever flips up. The plate prints flat — it is a simple 2D profile with stepped holes.

**Front Bezel (1x)** — A cosmetic frame that press-fits onto the tray's front opening, covering the raw edges where the tray walls meet the lever pivot area. The bezel has a rectangular cutout for the lever paddle and two detent notches (locked and unlocked positions) that receive a small printed spring tab on the lever. The bezel is the user-facing surface — it receives the most visual attention. It prints face-down for a smooth front surface.

### Dock (3 printed parts)

**Dock Cradle (1x)** — A U-shaped channel that mounts inside the enclosure at the bottom-front. The cradle's two side walls carry the C-channel rail grooves (female, matching the tray's male T-ribs). The cradle's rear wall holds 4 tube stubs (1/4" OD PE, 20mm protrusion, chamfered tips) and 2 tapered registration bosses (10mm diameter, 15mm long, protruding 10mm farther than the tube stubs). The rear wall also holds 4 spring-loaded blade contacts (recessed in pockets so they cannot be touched during cartridge handling). The cradle prints on its back wall (opening facing up), so the rail grooves build cleanly in layer lines parallel to the insertion axis.

**Dock Floor Plate (1x)** — A flat plate that closes the bottom of the dock cradle, providing a smooth surface the cartridge tray slides on. Separate from the cradle so the cradle's rail geometry prints cleanly without bridging the floor span. The floor plate snaps into a ledge on the cradle's inner bottom edges.

**Dock Face Frame (1x)** — A cosmetic bezel that mounts to the enclosure front panel around the dock opening, framing the cartridge's front bezel when docked. The face frame's inner dimensions are 2mm larger than the cartridge front bezel on each side, creating a uniform 1mm reveal gap. The frame has entry chamfers (5mm at 30 degrees) on all four inner edges that funnel the cartridge into the rail opening.

---

## 2. Join Methods

| Joint | Method | Rationale |
|-------|--------|-----------|
| Pumps into tray | M3 x 8mm SHCS + heat-set inserts (4 per pump, 8 total) | Pumps are the heaviest components; screws provide vibration-proof retention. Heat-set inserts in PETG are durable and re-threadable. |
| Lid onto tray | Snap-fit clips (4x) | Lid removal is infrequent (only to replace pumps). Cantilever snaps with 0.8mm hook depth, 2mm deflection, 45-degree lead-in. |
| Lever into tray | Press-fit pivot stubs into tray side-wall bearing holes | The lever is captive once the lid is on (lid covers the top of the pivot area). Pivot hole is 0.1mm oversize for smooth rotation. |
| Release plate onto guide posts | Sliding fit on 2 vertical posts | Posts are integral to tray rear wall. Plate slots are 0.3mm oversize for free axial travel. Plate is captive between rear wall and fitting body ends. |
| Front bezel onto tray | Press-fit with 2 snap tabs | Cosmetic part; press-fit is sufficient. Tabs prevent rattling. |
| John Guest fittings into tray rear wall | Press-fit (9.31mm body in 9.5mm bore) | The barbell shoulders (15.10mm) provide axial retention on both sides of the wall. The 0.1mm radial clearance allows self-centering on tube stubs during insertion. |
| Dock cradle into enclosure | Snap-fit lugs engaging enclosure inner wall features | Dock is permanent. 4 lugs (2 per side wall) engage rectangular pockets in the enclosure half-shells. |
| Dock floor plate into cradle | Snap-fit ledge | Flat plate drops in and clicks. |
| Dock face frame onto enclosure | Press-fit into front panel cutout | Cosmetic frame; adhesive backup if needed. |
| Tube stubs into dock rear wall | John Guest fittings (permanent, dock side) | The dock's tube stubs are the short exposed ends of tubes that run to the rest of the plumbing. They pass through JG fittings mounted permanently in the dock rear wall. |
| Electrical contacts (dock side) | Spring-loaded blade contacts pressed into pockets | Retained by interference fit in printed pockets. Wires soldered to contact tails, routed through dock rear wall to the L298N motor driver. |
| Electrical contacts (cartridge side) | Copper foil tape pads adhered to tray rear wall | Self-adhesive copper tape in recessed pockets (flush with wall surface). 4 pads: motor A+, motor A-, motor B+, motor B-. |

---

## 3. Seam Placement

**Cartridge visible seams (when docked, lever locked):**
- Front bezel-to-lever junction: horizontal seam at top and bottom of lever paddle cutout. The bezel's cutout has a 0.5mm step-in (rebate) so the lever paddle sits 0.5mm recessed, creating a shadow line rather than a flush butt joint.
- Front bezel-to-dock face frame gap: 1mm uniform reveal all around. This is the primary visual seam — it communicates "this part is removable."

**Cartridge internal seams (visible only when cartridge is out):**
- Lid-to-tray: top edge, all around. Not cosmetically treated — this is a service seam.
- Front bezel-to-tray: front edge. Hidden when docked.

**Dock seams:**
- Dock face frame-to-enclosure front panel: flush mount with 0.5mm reveal. The face frame is visually part of the enclosure.
- Dock cradle-to-enclosure interior: fully hidden.

**Seam treatment philosophy:** The only seam the user regularly sees is the cartridge-to-dock reveal gap at the front face. This gap is uniform and deliberate — it signals removability. All other seams are either hidden or only visible during service.

---

## 4. User-Facing Surface Composition

**What the user sees (cartridge docked, front of device):**

A rectangular face at the bottom of the enclosure front panel. From outside in:
1. Dock face frame (part of enclosure visual language, same material and finish)
2. 1mm reveal gap (shadow line, communicates removability)
3. Front bezel (cartridge identity surface)
4. Lever paddle (centered in the bezel, flush when locked, protruding ~15mm when unlocked)

**Visual hierarchy:**
- The lever paddle is the primary interactive element. It should be subtly differentiated — either a contrasting surface texture (smooth vs. the bezel's light texture) or a very slight color shift if dual-material printing is used. For single-material, a directional texture change (print line direction perpendicular to the bezel) provides differentiation.
- The front bezel is secondary — it frames the lever and carries no information.
- The dock face frame is tertiary — it blends with the enclosure.

**What the user touches:**
- Lever paddle: gripped for insertion/removal, flipped for lock/unlock. Must feel substantial — minimum 4mm thick at the grip edge, with a finger-hook radius at the bottom edge (3mm fillet) for flip-up.
- Cartridge body (tray sides): touched during insertion when guiding the cartridge into the rails. Smooth surfaces, no sharp edges. The rail ribs are on the outer faces of the tray walls but are captured inside the dock's C-channels and never touched.

---

## 5. Design Language

**Material:** PETG throughout. Chosen for chemical resistance (near a sink, possible contact with flavoring), toughness (snap-fits, cam surfaces), and printability on the Bambu H2C.

**Corner treatment:** All user-facing edges have 1.5mm fillets minimum. Internal functional edges (rail ribs, guide posts, fitting bores) are sharp for precision. The front bezel and lever paddle have 3mm fillets on all exposed edges for a smooth, appliance feel.

**Surface finish:** All user-facing surfaces print against the bed or with ironing enabled for a smooth face. The front bezel prints face-down; the lever prints paddle-face-down. The dock face frame prints face-down.

**Color:** Matte black PETG to match the project's dark navy/black design language (consistent with the iOS app theme, S3 display theme, and planned enclosure). The copper contact pads and the lever detent notches are the only non-black elements visible at close inspection.

**What makes this feel like a product, not a project:**
- The 1mm reveal gap around the cartridge front face is uniform and deliberate, like a phone battery cover or a premium appliance panel.
- The lever has two distinct positions with audible clicks — no ambiguity.
- The insertion motion is smooth and guided — the rails do all the alignment work.
- The cartridge has a single obvious grip point (the lever) and a single obvious action (flip).
- No screws, no tools, no instructions beyond "slide in, flip down."

---

## 6. Service Access Strategy

**Tier 1 — User (no tools, every 1-2 years): Replace pump cartridge.**
- Flip lever up (click). Pull cartridge out on rails. Slide new cartridge in. Flip lever down (click). Done.
- The user never opens the cartridge. Pump cartridges ship pre-assembled.

**Tier 2 — Builder/advanced user (tools needed, cartridge lifespan): Replace pumps inside a cartridge.**
- Remove cartridge from dock (Tier 1 steps).
- Pry lid off (flex snap clips with a flat tool or fingernail).
- Disconnect silicone tubing from pump barbs (pull off).
- Unscrew 4x M3 screws per pump (8 total).
- Lift pumps out.
- Reverse to install new pumps.
- This is a workbench operation, not something done in-situ.

**Tier 3 — Builder (initial assembly or dock repair):**
- Dock is permanently mounted in the enclosure. If the dock needs service, the enclosure half-shells must be separated (a separate, much larger operation).
- Electrical contacts and tube stubs in the dock are accessible from inside the enclosure if needed.

---

## 7. Manufacturing Constraints

### Print Bed Fit (Bambu H2C: 325 x 320 x 320mm)

| Part | Approximate Dimensions | Fits Single Nozzle? | Print Orientation |
|------|----------------------|---------------------|-------------------|
| Cartridge Tray | 140 x 120 x 70mm | Yes | Back (rear wall) down |
| Cartridge Lid | 140 x 120 x 4mm | Yes | Top surface down |
| Lever | 140 x 40 x 15mm | Yes | Paddle face down |
| Release Plate | 120 x 50 x 3mm | Yes | Flat |
| Front Bezel | 140 x 70 x 5mm | Yes | Face down |
| Dock Cradle | 160 x 130 x 80mm | Yes | Back wall down |
| Dock Floor Plate | 150 x 120 x 3mm | Yes | Flat |
| Dock Face Frame | 170 x 80 x 5mm | Yes | Face down |

All parts fit comfortably within the print bed. No part exceeds 170mm in any dimension.

### Orientation and Support Strategy

Every part is designed to print without supports:
- The tray prints rear-wall-down. The pump pockets are open-top cavities. The rail ribs are vertical extrusions along the side walls. The fitting bores are vertical holes in the (now horizontal) rear wall.
- The lever prints paddle-down. The pivot stubs are short vertical cylinders. The cam lobes are eccentric profiles that build layer by layer with no overhangs beyond 45 degrees.
- The release plate is a flat part with through-holes — trivially supportless.
- The dock cradle prints back-wall-down. The C-channel grooves run vertically up the side walls (no overhangs).

### Material Selection

PETG for all parts. Specific considerations:
- Cam surfaces (lever cam lobes pushing release plate): PETG's toughness handles the repeated sliding contact. The cam angle is gentle (~15 degrees), minimizing shear stress on layer lines.
- Snap-fit clips (lid to tray): PETG's 5-7% elongation at break provides adequate flex for 0.8mm hook depth with 2mm cantilever deflection.
- Rail ribs: Layer lines run parallel to the insertion direction (Y-axis), so sliding friction acts along, not across, layer boundaries. PETG-on-PETG static friction coefficient is ~0.4; the rail clearance (0.3mm per side) prevents binding.
- Heat-set inserts: PETG accepts M3 heat-set inserts well with a soldering iron at 230C.

### Critical Tolerances

| Feature | Nominal | Tolerance | Notes |
|---------|---------|-----------|-------|
| Rail rib width | per dock groove | +0/-0.3mm | Undersize preferred; binding is worse than wobble |
| Fitting bore (center body) | 9.5mm | +0.2/-0mm | Slight oversize allows self-centering |
| Registration boss socket | 10.0mm | +0.2/-0mm | Taper handles the rest |
| Guide post to plate slot | 4.0mm post in 4.3mm slot | 0.3mm clearance | Ensures free axial travel |
| Lever pivot hole | pivot stub OD + 0.1mm | +0.1/-0mm | Smooth rotation without slop |

---

## Mechanism Detail: How the Lever-Cam-Plate System Works

The lever is the central mechanism. Here is the kinematic chain:

1. **Lever up (unlocked):** The cam lobes are at maximum radius (3mm eccentric from pivot axis). The cam lobe faces push the release plate forward (toward user). The plate's stepped bores compress all 4 collets ~3mm inward, disengaging the grab teeth. Simultaneously, the cam reaction pushes the cartridge tray body ~3mm forward, partially withdrawing the tube stubs from the fittings. The cartridge is free to slide out.

2. **Lever down (locked):** The cam lobes rotate to minimum radius. The release plate retracts (moves away from user, toward dock rear wall), pulled by small return springs or simply by gravity and the fitting body ends pushing it back. The plate no longer contacts the collets. The cartridge body is pulled ~3mm rearward by the cam, fully seating the tube stubs in the fittings and pressing the electrical contacts together.

**Detent mechanism:** The front bezel has two small V-notches (one at lever-up position, one at lever-down). A printed cantilever tab on the lever's paddle edge snaps into these notches, providing the audible/tactile click at both positions. The cantilever is a 12mm long, 2mm wide, 1.5mm thick PETG finger — well within elastic deflection limits for the ~0.5mm detent depth.

**Cam geometry:** Each cam lobe is a kidney-shaped profile on the pivot stub. The lobe pushes the release plate via a flat face on the plate's side slot. The contact is a flat-on-flat sliding interface — no point loads, no Hertzian stress concerns. The cam rise is distributed over 90 degrees of rotation, giving a gradual ramp that feels smooth to the user.

---

## Electrical Contact Strategy

4 blade contacts, not 3. Each pump motor gets dedicated + and - wires (no shared ground) for independent PWM control. This matches the L298N motor driver's output architecture (2 H-bridges, 4 output wires).

**Dock side:** 4 spring-loaded phosphor bronze blade contacts, recessed 2mm behind the dock rear wall face. Each blade is ~15mm long x 4mm wide, mounted in a printed pocket with the spring behind it. The blade tip protrudes ~1mm from the wall face at rest; spring travel is 3mm. The contacts self-clean via wiping action during the last 10mm of cartridge insertion.

**Cartridge side:** 4 adhesive copper foil tape pads (10mm x 5mm each), recessed in shallow pockets (0.1mm deep) in the tray rear wall so they sit flush. The pads connect to the pump motor terminals via short lengths of silicone-insulated wire routed along the tray floor, soldered to the motor tabs.

**Lock-sense:** Rather than a separate contact, the ESP32 detects cartridge presence and lock state by measuring continuity across the motor contacts. When the cartridge is absent, all contacts are open. When present but unlocked, the contacts may be intermittent. When locked, the cam's final seating force ensures solid contact pressure. A simple firmware check (attempt a brief low-current pulse, measure response) distinguishes the states.

---

## Assembly Sequence (Builder, First Time)

1. Press 8 heat-set inserts into the tray's pump pocket bosses (soldering iron).
2. Press 4 John Guest fittings into the tray rear wall bores (push by hand; barbell shoulders lock axially).
3. Drop the release plate onto the guide posts in the tray rear wall.
4. Set both Kamoer pumps into the tray pockets, motor-end rearward. Secure with 8x M3 screws.
5. Route silicone tubing from each pump barb to its corresponding John Guest fitting inboard port. Push tubing onto barbs and into fittings.
6. Solder wires from motor terminals to copper tape pads on the rear wall (or use pre-soldered leads).
7. Press the lever pivot stubs into the tray side wall bearing holes.
8. Snap the front bezel onto the tray front.
9. Snap the lid onto the tray top.

The dock is assembled separately (tube stubs, blade contacts, wiring) and mounted in the enclosure during enclosure assembly.
