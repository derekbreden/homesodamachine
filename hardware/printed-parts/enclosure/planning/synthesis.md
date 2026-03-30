# Enclosure — Synthesis
**Date:** 2026-03-29
**Inputs:** requirements.md, vision.md, design-patterns.md, snap-fit-geometry.md, display-switch-dimensions.md, back-panel-ports.md, bag-frame/concept.md, pump-cartridge/concept.md
**Next step:** specification (per-part geometry definitions, dimensioned drawings)

---

## 1. Split Plane Location

**The horizontal seam falls at 185 mm from the bottom of the enclosure.**

### Reasoning

**Component layout constraint:**

The vision places components in these vertical zones:
- Pump cartridge: front-bottom. The cartridge concept establishes a 75 mm tall cartridge body in a dock cradle. Accounting for the dock cradle and floor clearance, the pump zone occupies approximately 0–100 mm from the floor.
- Displays and air switch: middle-front, directly above the pump cartridge. The S3 module is 33.1 mm deep; the front panel section behind the displays requires ~50 mm of interior clearance (module depth + cable bend). Component face diameters are 47.3 mm (S3), 33.0 mm (RP2040), 47.6 mm cap (KRAUS). A reasonable panel section accommodating all three centered on the front face requires a vertical band of approximately 80–90 mm to give each component generous visual breathing room. Centered in the range of 100–185 mm, this zone spans approximately 100–185 mm from the bottom.
- Bags: diagonal from back-bottom to front-wall, each bag projects 201 mm vertically. The two bags are stacked one above the other, each in a separate cradle. The lower bag's cradle sits at approximately 100–130 mm from the bottom (above the pump cartridge zone). The upper bag's cradle sits 100–130 mm above the lower one, placing the upper bag zone top at approximately 330–360 mm from the bottom. The electronics (back-top) occupy approximately 330–400 mm from the bottom at the rear.
- The spine snaps to both enclosure halves. Its snap posts engage oval slots in the inner side walls. Per the bag-frame concept, the spine spans the full enclosure width and the posts are distributed across both halves. The seam must fall at a height where the spine's posts are divided between halves — with the lower posts below the seam (in the bottom half) and the upper posts above the seam (in the top half).

**Design-patterns guidance:**

Place the seam at the visual transition between the upper bag zone and the lower component zone — not in the middle of either. At 185 mm, the seam falls just above the display/switch panel section (which occupies roughly 100–185 mm) and just below the floor of the bag zone (which begins at approximately 185–200 mm as the bags start their diagonal from the front wall). This is the natural visual boundary.

**Printability constraint:**

Each half must fit within 325 × 320 × 320 mm (single-nozzle build volume). The enclosure footprint is 220 × 300 mm.

- **Bottom half:** 220 mm × 300 mm × 185 mm. Printed with the base on the build plate. Height is 185 mm, well within the 320 mm Z limit. Fits in the 325 × 320 × 320 envelope.
- **Top half:** 220 mm × 300 mm × 215 mm. Printed with the seam face on the build plate (seam-face-down). Height is 215 mm, within the 320 mm Z limit. Fits in the 325 × 320 × 320 envelope.

Both halves are printable within the single-nozzle volume. A seam at 185 mm from the bottom gives both halves comfortable Z-height margins (135 mm margin for the bottom half, 105 mm margin for the top half).

**Result:**

| Half | Height | Print orientation | Z-height vs. 320 mm limit |
|---|---|---|---|
| Bottom half | 185 mm | Base on build plate | 135 mm margin |
| Top half | 215 mm | Seam face on build plate | 105 mm margin |

The seam at 185 mm from the bottom satisfies all three constraints simultaneously. It falls at the visual boundary between the component zone (below) and the bag zone (above), places the bag zone's primary structural anchor (the spine) in the top half where it can snap to both halves, and keeps both halves within the single-nozzle build envelope.

---

## 2. Snap-Fit Join Specification

All dimensions directly from snap-fit-geometry.md, confirmed for PETG FDM on the Bambu H2C.

### Snap arm geometry (24 arms total)

| Parameter | Value |
|---|---|
| Arm length (L) | 18.0 mm |
| Arm thickness at root (h) | 2.0 mm |
| Arm thickness at tip | 1.4 mm (tapered) |
| Arm width (b) | 8.0 mm |
| Hook height (δ) | 1.2 mm |
| Lead-in angle (α) | 30° |
| Retention face angle (β) | 90° — permanent assembly |
| Hook depth (horizontal) | 1.2 mm |
| Root fillet | 0.3 mm radius |
| Hook undercut support interface gap | 0.2 mm |
| Break-away tab size | 0.3 mm wide × 0.3 mm tall, 2 tabs per hook at 2 mm and 6 mm from one edge |

**Snap arms are on the bottom half.** Receiving ledge pockets are on the top half. This keeps the hook undercut support accessible from inside the assembly cavity before the halves are joined.

### Snap count and spacing

| Face | Length | Snap count | Spacing |
|---|---|---|---|
| 220 mm faces (× 2) | 220 mm | 5 snaps each | 40 mm c-to-c |
| 300 mm faces (× 2) | 300 mm | 7 snaps each | 40 mm c-to-c |
| **Total** | — | **24 snaps** | — |

Corner clearance: ≥ 15 mm from the nearest corner to the nearest snap on each face. Snaps on the 220 mm faces are at positions 40, 80, 120, 160, 200 mm from one end. Snaps on the 300 mm faces are at positions 40, 80, 120, 160, 200, 240, 280 mm from one end.

### Force summary

| Metric | Value |
|---|---|
| Assembly force per snap | ~5 N |
| Total assembly force | ~120 N (comfortable two-palm press) |
| Retention force per snap | ~640 N (arm fracture-limited) |
| Total retention force | ~15,360 N (permanent) |

### Alignment pins (4 total, one per corner)

| Parameter | Value |
|---|---|
| Pin diameter | 4.0 mm |
| Pin height | 8.0 mm |
| Pin-to-socket clearance | 0.15 mm |
| Pin tip chamfer | 1.0 mm × 45° |
| Socket entry chamfer | 1.0 mm × 45° |
| Location from corner | 10 mm from each corner edge (to pin centerline) |

Alignment pins are on the bottom half; sockets are in the top half (same half as the receiving ledges — both are mating-face features on the top half).

### Tongue-and-groove (continuous, full perimeter)

| Parameter | Value |
|---|---|
| Tongue width | 3.0 mm |
| Tongue height | 4.0 mm |
| Groove width | 3.1 mm (0.1 mm snug clearance) |
| Groove depth | 4.2 mm (0.2 mm bottom clearance) |
| Tongue base chamfer | 0.3 mm × 45° (prevents elephant's foot interference) |
| Tongue tip chamfer | 0.5 mm × 30° (guides entry) |

**Tongue is on the bottom half** (grows upward in +Z, maximally strong print direction). Groove is in the top half (opens downward, prints as a slot without overhang).

### Seam reveal treatment

The top half's exterior wall extends **0.5 mm below the seam plane**, lapping over the bottom half's exterior wall. This creates a designed shadow line — the visible seam is the reveal shadow, not a tolerance-accumulation gap. The lap-over captures any elephant's-foot flare on the bottom half's top edge, preventing it from pushing the halves apart.

**Shadow line geometry (from design-patterns.md):**

| Feature | Value |
|---|---|
| Shadow line visual gap (dark recess) | 0.5 mm |
| Lip height | 2.0–2.5 mm |
| Lip width | 1.5 mm |
| Channel clearance vs. lip | +0.2 mm in both X and Y |
| Lead-in chamfer on lip | 0.3 mm × 45° |

The seam at 185 mm places this designed shadow line at the transition between the lower component panel and the upper bag zone — a geometric transition where the eye expects a line, per design-patterns.md guidance. It does not fall in the middle of a featureless flat face.

Where snap clips interrupt the continuous lip, taper the lip back to zero over 5 mm on each side of the clip location to prevent visible gap irregularities at those points.

**Assembly sequence:**
1. Locate via four corner alignment pins — halves constrained in X and Y.
2. Tongue enters groove (at 4 mm depth, before snaps engage) — halves constrained in Z position and lateral shift.
3. Lower top half, 30° lead-in engages all snap arms simultaneously.
4. User presses both palms along the 300 mm faces — 120 N total, comfortable.
5. All 24 snaps engage within ~1–2 mm of travel. Definitive tactile click-stop at full engagement.

---

## 3. Front Face Component Layout

### Component dimensions summary (from display-switch-dimensions.md)

| Component | Face diameter | Panel cutout | Module depth | Below-panel depth | Self-retention |
|---|---|---|---|---|---|
| RP2040 (Waveshare 0.99") | 33.0 mm | Φ 33.0 mm circle | 9.8 mm | ~30 mm w/ cable | None — enclosure provides |
| S3 CrowPanel 1.28" Rotary | 47.3 mm circular face (48 mm sq. housing) | Φ 47.3 mm circle (see note) | 33.1 mm | ~50 mm w/ cable | Partial — M2.5 mounting holes |
| KRAUS KWDA-100MB | 47.6 mm cap (44.5 mm body) | Φ 31.75 mm (1-1/4") | 38.1 mm stem below panel | ~50 mm w/ nut | Yes — ABS nut self-locks |

### Zone allocation

The front face component panel occupies approximately **100–185 mm from the bottom** (the full height of the bottom half's front face above the pump cartridge zone). The pump cartridge dock occupies 0–100 mm, leaving 85 mm of front face height for the three components.

Within this zone:

**S3 CrowPanel (1.28" rotary display):** Center of face, at approximately **155 mm from the bottom** (within the bottom half, 30 mm below the seam). The S3 is the visual anchor of the panel — largest face diameter, rotary knob, full settings interface. Centering it vertically in the upper portion of the component zone makes it the dominant feature of the panel.

**RP2040 (0.99" round display):** Left of center, at approximately **130 mm from the bottom** (within the bottom half, 55 mm below the seam). The RP2040 is the secondary status display, smaller, and positioned slightly lower than the S3 to create visual hierarchy rather than a rigid horizontal row.

**KRAUS air switch:** Right of center, at approximately **130 mm from the bottom** (within the bottom half, 55 mm below the seam, mirroring the RP2040). The air switch is operationally symmetric with the RP2040 in importance — both are the everyday user interface for the device — so they flank the S3 at the same height.

**All three components are entirely within the bottom half.** This is important because:
- The seam at 185 mm places it above all three component faces (RP2040 at 130 mm, S3 at 155 mm, KRAUS at 130 mm, all well below 185 mm)
- No component straddles the seam
- The component cutouts and their retention features are all in a single continuous printed part

### Left-to-right arrangement (viewed from front)

From left to right: **RP2040 — S3 — KRAUS**

| Component | X-center (from left edge, on 220 mm face) | Height from bottom |
|---|---|---|
| RP2040 | 55 mm | 130 mm |
| S3 | 110 mm (centered on face) | 155 mm |
| KRAUS | 165 mm | 130 mm |

Spacing: RP2040 to S3 center-to-center = 55 mm. S3 to KRAUS center-to-center = 55 mm. Minimum face edge clearances: RP2040 right edge to S3 left edge: 55 − (33.0/2) − (47.3/2) = 55 − 16.5 − 23.65 = **14.85 mm** — sufficient spacing for visual separation. S3 right edge to KRAUS left edge: same by symmetry, **14.85 mm**.

### Panel clearance depths

The front panel at each component location must provide the stated depth behind the panel face for the module body and its cable exits.

| Component | Required clearance depth | Governing factor |
|---|---|---|
| RP2040 | ~30 mm | SH1.0 cable exits side wall of module — 25 mm lateral clearance behind panel at left and bottom of module |
| S3 | **~50 mm** | Module body 33.1 mm + MX1.25 cable bend behind PCB; S3 depth is the critical constraint for the front panel section |
| KRAUS | ~50 mm | 38.1 mm threaded stem + ABS nut + air tube fitting below panel |

**The S3's 33.1 mm module depth is the critical clearance constraint.** The front panel section at the S3 location must be a through-pocket at least 33.1 mm deep, meaning the interior face of the front panel wall behind the S3 must be at least 33.1 mm from the exterior face. Given that the enclosure is 220 mm deep and the S3 is centered on the front face, there is 220 − 33.1 = 186.9 mm of remaining interior depth behind the S3 for internal components — well within the available space.

**The KRAUS requires 38.1 mm of depth** for the threaded stem. This is slightly more than the S3 at 33.1 mm. The KRAUS is self-retaining (ABS nut), so no printed retention feature is needed behind the panel. The panel at the KRAUS location is a simple through-hole (Φ 31.75 mm) with ~40 mm of clear depth behind it for stem, nut, and tube fitting. The AC adapter box (140 × 73 × 48 mm) mounts on the air tube anywhere inside the enclosure — it does not need to be adjacent to the panel.

### Component recess geometry (from design-patterns.md)

**RP2040 (Φ 33.0 mm cutout):**
- Through-hole: Φ 33.0 mm nominal
- Recess edge chamfer: 0.5 mm × 45° on outer rim
- Retention: printed snap-ring at ~32 mm inner diameter behind panel (three-tab or bayonet twist-lock preferred over pure snap for reliability of repeated removal cycles)
- The 1.75 mm front chamfer of the CNC aluminum case seats against the panel face as the front stop

**S3 (Φ 47.3 mm circular cutout, or 48 mm square):**
- Circular cutout Φ 47.3 mm + 0.5 mm knob clearance = **Φ 47.8 mm minimum** for free knob rotation
- Recess edge chamfer: 0.5 mm × 45°
- Retention: printed bracket with M2.5 screw capture, sandwiching module against panel from behind
- Square housing corners (48 mm sq.) do not pass through a circular 47.8 mm hole — module inserts and removes from behind; the front opening shows only the circular face and knob

**KRAUS (Φ 31.75 mm through-hole):**
- Panel hole: Φ 31.75 mm (standard 1-1/4" faucet hole)
- No recess required — the 47.6 mm cap sits flush on the panel outer face and covers the hole edge completely
- The ABS locking nut clamps from behind; no printed retention feature needed
- Surface pocket around the hole is not required if the panel is flat and the cap simply rests on the panel face

---

## 4. Rear Wall Port Layout

### Fitting specification

All 5 ports use **John Guest PP1208W-US** bulkhead union fittings.

| Parameter | Value |
|---|---|
| Part number | PP1208W-US |
| Material | White polypropylene body, EPDM O-ring, acetal collet |
| NSF listing | NSF 51 and NSF 61 (food-contact safe) |
| Panel hole diameter (nominal) | 17.0 mm (0.67") |
| Panel hole diameter (print target) | **17.2 mm** (+0.2 mm FDM loose-fit correction) |
| Recommended wall thickness | 3.0–4.0 mm |
| Fitting overall length | ~35 mm |
| Exterior protrusion from panel face | ~18–20 mm |
| Interior protrusion into enclosure | ~12–14 mm |
| Interior boss OD (reinforcement ring) | 22 mm (provides ≥ 3 perimeters of wall around 17.0 mm hole) |
| Retention method | Threaded body + hex locking nut (supplied with fitting) |

### Port count and grouping

5 ports total, divided into 3 functional groups per design-patterns.md guidance:

**Group A — Flow-through pair (2 ports), left side of rear panel:**
- Carbonated water inlet (external plumbing in)
- Carbonated water outlet (to faucet)
- These carry the same fluid through the flow sensor. Grouped left.
- Recessed bay: 1.5 mm deep rectangular pocket, 5 mm margin around group, 0.5 mm corner radius
- Directional arrow icons: inward arrow below inlet port, outward arrow below outlet port
- Arrow spec: 8 mm long, 6 mm wide at widest, 1.5 mm stroke, 0.8 mm relief height, centered 5 mm below port centerline

**Group B — Tap water inlet (1 port), center of rear panel:**
- Tap water for the clean cycle
- Isolated, no arrow icon — single port function is unambiguous
- No recessed bay required for a single port, but a shallow 1.0 mm boss recess (boss diameter 30 mm) distinguishes it from Groups A and C

**Group C — Flavor outlets (2 ports), right side of rear panel:**
- Flavor 1 outlet (to faucet)
- Flavor 2 outlet (to faucet)
- Both ports exit the device toward the faucet; grouped right, mirroring Group A
- Recessed bay: same spec as Group A
- Both arrows point outward (away from enclosure)

### Port spacing and layout

**Center-to-center spacing:** 35 mm (from design-patterns.md, preferred over the 30 mm minimum for comfortable one-handed tube insertion). At 35 mm pitch:

| Span | Calculation |
|---|---|
| Group A internal span | 1 × 35 mm = 35 mm |
| Group A to Group B gap | 50 mm (larger gap visually separates the groups) |
| Group B to Group C gap | 50 mm (symmetric) |
| Group C internal span | 1 × 35 mm = 35 mm |
| Total span (outermost port to outermost port) | 35 + 50 + 0 + 50 + 35 = **170 mm** |

Centered on the 220 mm rear wall: 25 mm margin on each side. This provides adequate clearance for the enclosure corner walls and the half-split seam at the rear face.

**Port X-positions from left edge of rear face:**

| Port | Group | X-position (from left) |
|---|---|---|
| Carb water inlet | A | 25 mm |
| Carb water outlet | A | 60 mm |
| Tap water inlet | B | 110 mm (center) |
| Flavor 1 outlet | C | 160 mm |
| Flavor 2 outlet | C | 195 mm |

### Vertical position of rear ports (height from bottom)

All 5 ports are **in the top half** of the enclosure, at approximately **310 mm from the bottom** (125 mm from the top). Reasoning:

- The ports must be high enough on the rear wall to avoid the pump cartridge zone (0–100 mm) and the bag frame cradle zone (100–300 mm at the rear, where tubing exits the cap pockets).
- The vision places the electronics at back-top (330–400 mm range). The ports at 310 mm are just below the electronics tray zone and above the bag zone — in the top half (185–400 mm range), but below the electronics zone.
- All 5 ports being in the same half means the rear wall port boss geometry is entirely in one part (no port spans the seam, no split-half alignment complications at the port locations).
- The 310 mm height from the bottom means the ports are 310 − 185 = **125 mm above the seam** — well within the top half.

### Boss geometry (from back-panel-ports.md)

Each hole has a raised interior boss (recessed 0 mm on exterior, raised on interior) at 22 mm OD. The boss provides at least 2.5 mm of radial wall thickness around the 17.2 mm hole (22 mm OD − 17.2 mm ID = 4.8 mm wall, or 2.4 mm per side — meeting the 3-perimeter minimum at 0.8 mm/perimeter). A metal or steel washer on the interior face between the nut and the printed boss is recommended to distribute nut clamping load and prevent cracking.

---

## 5. Internal Mounting Provisions

### 5.1 Bag frame spine snap posts — enclosure inner side walls

The spine concept specifies oval posts (10 mm × 6 mm cross-section, 8 mm long) with a 1.5 mm circumferential retaining hook flange protruding from the spine's end faces. The enclosure inner side walls carry the matching oval slots (10 mm × 6 mm opening, with 1.5 mm retaining rim).

**Which half carries the slots:**

The spine snaps to both halves simultaneously as the enclosure halves close — per the bag-frame concept, the spine is placed in the bottom half first (2 posts engaging the left-half wall slots), then the right half closes (2 posts engaging the right-half wall slots). This means:
- The left half (assuming assembly from the left) and the right half each carry 2 oval slots on their inner side walls.
- Because the spine spans the full enclosure width and its posts are at both ends, each half carries slots on one side wall only (left half: left inner wall; right half: right inner wall).

**Height location of the oval slots:**

The spine concept places one post at the upper portion and one at the lower portion of each spine end, with approximately 40 mm vertical separation between the two posts on each side. The spine must be positioned in the bag zone — above the seam (185 mm), in the top half's inner walls. Given the bag zone occupies approximately 185–350 mm from the bottom, and the spine needs to resist both the bag weight (distributed load) and the bag frame cradle-to-spine moment, centering the spine vertically in the bag zone is appropriate.

**Spine center height:** approximately 255 mm from the bottom (midpoint of 185–325 mm zone above the seam and below the electronics tray).

**Oval slot locations in each side wall (measured from bottom of enclosure):**
- Lower slot: approximately **235 mm from the bottom** (spine lower post)
- Upper slot: approximately **275 mm from the bottom** (spine upper post, 40 mm above lower post)

Both slots are in the **top half** (above the 185 mm seam). The slot depth is 8 mm into the inner wall face (matching post length). The slot retaining rim (1.5 mm) engages the post's hook flange on the interior side of the post after assembly.

### 5.2 Bag frame cradle locating ledge — enclosure inner side walls

The bag-frame concept specifies a 3 mm × 3 mm ridge on each enclosure inner side wall that the outboard long edge of each cradle platform rests against. This is a contact locator, not a snap — it prevents the cradle from rotating about its inboard snap tabs.

There are **two cradles stacked vertically** (one per bag), each with its own locating ledge. The ledges are longitudinal (running along the bag axis direction, front-to-back).

**Ledge locations:**
- **Lower cradle ledge:** at approximately **195 mm from the bottom** — just above the seam (10 mm of wall in the top half above the seam), running the full front-to-back span of the cradle contact zone (~200 mm along the wall in the depth direction).
- **Upper cradle ledge:** at approximately **295 mm from the bottom** — 100 mm above the lower ledge (matching the vertical separation between the two bag positions), running the same front-to-back span.

Both ledges are in the **top half**. The 3 × 3 mm cross-section provides a printable feature (7.5 perimeters × 0.4 mm wide, with 0.8 mm structural minimum satisfied by the 3 mm height). Add a 45° chamfer on the lower face of the ledge to eliminate the 90° overhang: the ledge prints as a 45° ramp transitioning to a vertical stop face.

### 5.3 Pump cartridge dock cradle — front-bottom of enclosure

The dock cradle (per the pump-cartridge concept) is a **separate printed part**. It is not integrated into the enclosure walls. It mounts in the front-bottom zone of the enclosure (0–100 mm from the bottom), entirely within the **bottom half**.

**Mounting method: snap pockets in the bottom half floor and front inner wall.**

The dock cradle provides T-profile rails running front-to-back. The dock itself mounts to the enclosure via:
- Two snap clips on the dock's underside that engage matching rectangular pockets in the enclosure floor — these pockets are molded into the floor of the bottom half, 20 mm from the front inner wall.
- One locating rib on the dock's rear face that fits into a matching channel in the bottom half's interior back-of-pump-zone wall (the vertical internal wall at approximately 175 mm from the front, which separates the pump zone from the bag/valve zone).

This three-point engagement (two floor snap pockets + one rear locating rib) constrains the dock in X, Y, and rotation. No screws. No fasteners. The dock drops in from above during initial assembly and snaps into place before the enclosure halves are joined.

**Why snap pockets rather than screw bosses:** The vision specifies every internal mechanism mounts via snap connections to the enclosure walls with no exposed fasteners inside. Screw bosses are consistent with the vision's intent only if the screws are fully internal and inaccessible; snap pockets are simpler and match the pattern used throughout all other mechanisms.

### 5.4 Electronics tray — back-top of enclosure

The electronics tray (ESP32-DevKitC, L298N motor driver, solenoid valve controllers) mounts at back-top, in the **top half**, above the bag zone and behind the display/front panel area.

**Target zone:** approximately 330–390 mm from the bottom (60 mm tall band at the rear-top of the enclosure, 30 mm forward from the rear wall).

**Mounting interface: two snap rails on the top half's interior rear wall.**

The tray snaps onto horizontal snap rails integrated into the rear inner wall of the top half. Each rail is a horizontal cantilever ledge (3 mm × 3 mm cross-section), running left-to-right, at:
- Lower rail: approximately **340 mm from the bottom** (55 mm above the seam in the top half)
- Upper rail: approximately **370 mm from the bottom**

The tray slides in from the side (X direction, before the enclosure halves are joined) and snaps onto both rails with a positive click. The tray cannot be removed once the enclosure is closed — this is consistent with the vision's permanent-assembly architecture. The ESP32 and other electronics are not user-serviceable.

The snap interface on the tray: two horizontal ledge-grip features (one per rail) that flex over the rail during sideways insertion and then lock under the rail's retaining lip. Flex direction is in the XY plane (parallel to build plate per requirements.md). Hook geometry matches the rest of the mechanism family: 1.2 mm hook height, 30° lead-in, 90° retention face.

---

## 6. Flags for Conflicts

### Flag 1: S3 module insertion direction vs. circular front-face cutout

**Conflict:** The S3's square 48 mm housing cannot pass through a circular Φ 47.8 mm cutout from the front — the square corners catch. Per display-switch-dimensions.md: "The module must be inserted/removed from behind (snap-in from back, panel opening shows only the face)."

**Impact:** The S3 cannot be removed from the front without tool access to the rear bracket. The vision states the S3 can be "snapped out and placed elsewhere" by the user.

**Proposed minimum modification:** The front-face cutout at the S3 position is **square at 48.2 mm × 48.2 mm** (48 mm + 0.2 mm FDM clearance per side). This allows the module to pass through the opening from the front, enabling front-access removal as the vision requires. The circular bezel ring of the S3 (Φ 47.3 mm) is inset relative to the 48.2 mm square opening by (48.2 − 47.3) / 2 = 0.45 mm per side — this gap is visible as a 0.45 mm shadow at the four corners of the opening. Per design-patterns guidance, 0.45 mm is at the upper edge of the ≤ 0.5 mm gap that reads as "designed." This is acceptable. The M2.5 bracket retention behind the panel holds the module when installed. The user pushes the module out from behind (or unclips the bracket) to remove it.

**No wholesale redesign required.** Square cutout instead of circular.

### Flag 2: KRAUS air switch depth vs. front panel wall section

**Conflict:** The KRAUS threaded stem requires 38.1 mm of depth below the panel face for the stem + nut. The S3 requires 33.1 mm. Both components are at approximately the same horizontal height on the front face. The front panel wall at the KRAUS position must be at least 38.1 mm of clearance from the panel face to the first internal obstruction behind the KRAUS position. If internal components (valves, tubing) occupy the front-bottom zone at the same horizontal band as the KRAUS, there could be a depth conflict.

**Assessment:** The KRAUS is at 130 mm from the bottom, X-position 165 mm from left. The pump cartridge zone occupies 0–100 mm from the bottom and approximately 0–175 mm depth (from front wall). At 130 mm height, the zone directly behind the front panel is above the pump cartridge's top shell. The vision places valves behind the pump cartridge, not at the front-bottom panel face. The 38.1 mm KRAUS depth at 130 mm height conflicts only if valves or large components occupy the first 40 mm behind the front panel at that location.

**Resolution:** Reserve a 40 mm × 60 mm × 50 mm (W × H × D) clear pocket behind the KRAUS position on the front face. This pocket is above the dock cradle zone and below the bag frame zone. The AC adapter box for the KRAUS (140 × 73 × 48 mm) is routed along the air tube to the rear of the device, not behind the front panel — the 60" (1524 mm) air tube has ample length to route the adapter box elsewhere.

### Flag 3: Rear wall port height vs. bag tube routing

**Conflict potential:** Tubing from the Platypus bag cap pockets must route from the cap ends (at approximately 100–150 mm from the enclosure floor at the rear of the enclosure) to the rear wall ports (at 310 mm from the bottom). The tube must run upward ~160 mm along the rear wall interior before connecting to the ports. This routing is achievable but requires the rear wall interior to be clear of obstructions in a ~44 mm depth band along the rear wall between 100 and 310 mm heights.

**No conflict — this is an acceptable routing path.** The 44 mm minimum clearance for tube bend radius (from back-panel-ports.md) is satisfied by the enclosure depth. The tube routing runs vertically along the interior rear wall face, which has no large obstructions in this zone (valves are approximately 100–175 mm from the front wall per the vision, not at the rear wall). This flag is a routing note, not a geometry conflict requiring modification.

### Flag 4: Seam at 185 mm vs. display-switch-dimensions panel depth constraint

**Potential issue:** The RP2040 and KRAUS are at 130 mm from the bottom, 55 mm below the seam. The S3 is at 155 mm, 30 mm below the seam. All three components are in the bottom half, which is correct. However, the S3's module depth is 33.1 mm — the printed pocket accommodating it extends from the front face inward 33.1 mm. At 155 mm height, the pocket's interior back face is at the same height as the seam ± a few mm depending on pocket geometry. The seam tongue-and-groove runs continuously around the perimeter; if the S3 pocket's interior back wall interrupts the inner perimeter seam at 185 mm, the tongue-and-groove must be interrupted at that location.

**Minimum modification:** The S3 pocket (33.1 mm deep, centered at 155 mm height) extends to approximately 155 + 47.3/2 = 178.65 mm at its top edge — still 6.35 mm below the 185 mm seam. The pocket does not reach the seam height. No interruption to the seam tongue-and-groove occurs. This conflict is resolved by the chosen seam height of 185 mm placing it 6 mm above the top of the S3 pocket.

**No modification required.** The 185 mm seam height was chosen with sufficient margin above the S3 face.

---

## 7. Bill of Materials

This BOM covers only the enclosure itself. Internal mechanisms (bag frame, pump cartridge, dock cradle, electronics tray) have their own BOMs.

| Item | Qty | Material | Notes |
|---|---|---|---|
| Enclosure bottom half | 1 | PETG | 220 × 300 × 185 mm, printed base-down. Carries: 24 snap arms, 4 alignment pins (corner posts), continuous tongue on seam face, front-face component cutouts, dock cradle snap pockets in floor, 3 × 3 mm cradle locating ledges on inner side walls (none — ledges are in top half) |
| Enclosure top half | 1 | PETG | 220 × 300 × 215 mm, printed seam-face-down. Carries: 24 snap ledge pockets, 4 alignment pin sockets, continuous groove on seam face, 5 × PP1208W port holes with boss rings in rear wall, spine oval slot pairs on inner side walls, cradle locating ledges on inner side walls, electronics tray snap rails on inner rear wall |
| (No hardware fasteners for the enclosure join itself) | — | — | The join is entirely printed-integral snap geometry + tongue-and-groove. No alignment pins purchased separately — alignment pins are printed integral to the bottom half. |

**Optional hardware (assembly aids, not structural):**

| Item | Qty | Notes |
|---|---|---|
| PP1208W-US John Guest bulkhead union | 5 | For the rear wall ports. Not an enclosure BOM item — these are plumbing hardware. Listed here for completeness of the enclosure rear wall assembly. |
| M3 × 8 mm steel washer | 5 | One per rear wall port, interior face, under the PP1208W locking nut. Distributes clamping load on the 3–4 mm printed wall. |

---

## 8. Open Questions

The following technical details were not fully resolved by the research documents and must be addressed in the specification step.

**8.1 Spine oval slot exact wall depth — top half inner wall**

The oval slots for the spine snap posts are specified at 10 mm × 6 mm opening, 8 mm deep, with a 1.5 mm retaining rim. The inner wall of the enclosure must be thick enough at these locations to accommodate the 8 mm slot depth plus the outer enclosure wall thickness. If the enclosure walls are 2 mm thick, the slot can only be 2 mm deep — far less than the required 8 mm. A local boss or thickening (approximately 10–12 mm total wall depth at the slot location) is required. The specification must define the boss geometry on the inner side walls of the top half at the two spine snap post locations.

**8.2 RP2040 retention ring design**

The RP2040 has no self-retention (smooth CNC case, no tabs, no threads). The display-switch-dimensions.md research flags the risk of printed snap-ring failure under repeated removal cycles and recommends a twist-lock (bayonet-style) design. The specification must define the RP2040 retention ring geometry: whether snap-ring or bayonet, the arm count, arm dimensions, twist angle, and whether the ring is a separate part or integrated into the front panel wall.

**8.3 S3 mounting bracket geometry**

The S3 uses M2.5 mounting holes for positive retention. The specification must define the printed mounting bracket: whether it is a separate bracket that screws into the M2.5 holes or an integral clamp. The bracket must clear the rotary knob ring (47.3 mm OD, must not contact the rotating aluminum ring — 0.5 mm radial clearance minimum). With a square 48.2 mm front-face cutout and the 47.3 mm face, the bracket must reach behind the 48.2 mm opening edge to clamp the module without the bracket face being visible from the front.

**8.4 Dock cradle snap pocket geometry in bottom half floor**

The dock cradle concept defines two snap clips on its underside and a rear locating rib. The enclosure specification must define the matching floor pockets: their X-Y positions, depth, and opening geometry. These pockets must not conflict with the enclosure floor's structural rib pattern (if any) and must not create thin floor sections that reduce structural integrity.

**8.5 Electronics tray snap rail geometry**

The electronics tray is not yet specified in detail. The snap rails on the top half's interior rear wall (at 340 mm and 370 mm from the bottom) must be defined in the tray specification before the enclosure specification can finalize the rail cross-section, depth, and retention lip geometry. The enclosure specification should carry a placeholder for these rails and update once the electronics tray concept is complete.

**8.6 PP1208W locking nut hex size — physical measurement required**

The locking nut across-flats dimension is estimated at 21–22 mm from catalog photos. This dimension determines whether the interior boss (22 mm OD) provides enough clearance for a wrench. If the nut requires a wrench for final torquing and the boss OD is too close to the nut OD, the boss must be revised upward. This requires physical measurement of a PP1208W fitting before the specification is finalized.

**8.7 Front-face exterior color and surface finish language**

The vision specifies a consumer appliance. The enclosure exterior material is PETG; the pump cartridge is ASA (matte black, per cartridge concept). The enclosure color relative to the cartridge color has not been specified. The enclosure specification must define the exterior surface language: color, whether the top and bottom halves are the same color (reinforcing monolithic reading) or different colors (emphasizing the seam as a design feature), and whether the front panel face uses any texture differentiation from the enclosure body.

**8.8 Funnel mount interface on top of enclosure**

The vision places the funnel directly on top of the bags, on the top side of the device. The funnel is a separate sub-assembly (not yet specified) but will require a mounting interface with the enclosure top. The enclosure specification should include a placeholder feature (likely a circular collar or a slot opening in the top face) that the funnel assembly mounts into. This interface cannot be designed in the enclosure specification until the funnel sub-assembly concept is defined, but the location must be reserved.
