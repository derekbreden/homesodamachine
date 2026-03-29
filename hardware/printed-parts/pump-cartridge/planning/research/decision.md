# Pump Cartridge Design Decision

## 1. Decision Summary

The pump cartridge is a front-loading, rail-guided assembly containing two Kamoer KPHM400 peristaltic pumps and four John Guest PP0408W quick-connect fittings. The user removes it by gripping the front face and squeezing a pull surface to release the tube connections, then sliding the cartridge out on rails. The cartridge is a 5-part printed assembly (tray, lid, front face, release plate, floor plate) plus blade electrical connectors, M3 heat-set inserts, and M3 screws.

---

## 2. Spatial Layout (Back to Front)

Ordering from dock (back wall of enclosure) toward user (front):

1. **Dock wall** — four 1/4" tube stubs protrude inward from the enclosure back
2. **Cartridge back wall** (part of tray) — tubes from dock pass through clearance holes
3. **Release plate** — slides on guide posts; tube clearance holes allow tubes to pass through
4. **John Guest fittings** — mounted in a fitting plate (integrated into tray rear wall); dock-facing collets face the release plate
5. **Tube routing zone** — 180-degree bends from pump barbs to fittings
6. **Pump mounting zone** — two pumps side by side, motors facing forward
7. **Front face** — user grip surface; pull tabs connect to release plate via linkage rods

---

## 3. Overall Cartridge Dimensions

| Dimension | Value | Rationale |
|-----------|-------|-----------|
| Width (X) | 160 mm | Two pumps at 68.6 mm bracket width + 5 mm gap + 2x 9 mm walls |
| Depth (Y) | 155 mm | Fittings (~42 mm) + tube routing (~50 mm) + pump head (~48 mm) + front face (~15 mm) |
| Height (Z) | 72 mm | Pump head (62.6 mm) + floor (4 mm) + lid clearance (5 mm) |

These fit comfortably within the 220 mm x 300 mm enclosure footprint. The cartridge occupies roughly the lower-front quadrant of the enclosure.

---

## 4. The Squeeze-Release Interaction

### Design

The front face is a flat panel (~160 mm wide x 72 mm tall x 8 mm thick) with a sculpted palm rest on its outer surface. It is rigidly attached to the tray body. On the left and right sides of the front face, finger channels (open slots, ~25 mm deep x 15 mm wide) provide access to pull tabs that are part of the release plate linkage.

The pull tabs are flat paddle surfaces (30 mm tall x 15 mm wide) that sit inside the finger channels, connected to the release plate by two rigid linkage rods running along the inside walls of the cartridge. The rods pass through guide slots in the tray walls.

**Squeeze action:** The user wraps their hand around the front face — palm on the flat outer surface, four fingers curling into the finger channels on one side. When they squeeze, the palm pushes the front face (and thus the whole cartridge) away from their hand while their fingers pull the pull tabs toward their palm. The pull tabs pull the linkage rods, which pull the release plate toward the fittings. The release plate's stepped bores engage the dock-facing collets, compressing them inward and releasing all four tubes simultaneously.

**Why both sides have pull tabs:** Either hand works. A right-handed user uses the right-side channel; left-handed uses the left. Both sides are connected to the same release plate.

### Grip Span

The distance from the outer surface of the front face to the pull tab surface is 50 mm (within the 45-55 mm ergonomic optimum). The squeeze closes this by only 1.5 mm (the plate travel), so the span is essentially constant — the user perceives a firm squeeze, not a closing motion.

### Force Budget

| Parameter | Value |
|-----------|-------|
| Total collet release force (4 collets) | 20-60 N |
| Female 5th percentile squeeze capability | ~150 N |
| Ergonomic margin | 3x-9x |

The squeeze is comfortable for nearly all adults.

### Tactile Feedback

The release plate bottoms out on a hard stop at 1.5 mm travel (with a 2.0 mm physical limit for over-travel protection). The sudden increase in resistance tells the user the release is complete. An optional snap detent on the guide posts (0.3 mm bump) adds an audible click if prototyping confirms it is perceptible.

### Return Mechanism

Primary: collet spring-back. The release plate rests against the extended collet faces at its default position. When the user releases the squeeze, all four collet springs push the plate back to rest. This provides 20-60 N of return force with zero additional parts.

Fallback: if tolerance stack-up creates an air gap between the plate and collets at rest, add 2-4 printed PETG cantilever springs (12 mm x 3 mm x 1 mm beams) to the tray frame, bearing against the release plate.

---

## 5. Cartridge Body Shape and Split Strategy

### 5 Printed Parts

1. **Tray** — the main structural body. Open-top box with:
   - Rear wall with fitting pockets (4x bores sized for John Guest center body press-fit at 9.5 mm)
   - Side walls with linkage rod guide slots
   - Floor with pump mounting bosses (heat-set insert pockets) and motor cradles
   - Guide post bosses (4x 3.5 mm posts rising from rear wall area, through release plate bores)
   - Tube routing channels molded into floor and walls
   - Rail features (T-rail tongues) on left and right outer walls for dock insertion

2. **Lid** — flat panel that snaps onto the tray top edges. Provides:
   - Enclosure of tube routing zone (keeps tubes from shifting during handling)
   - Structural rigidity (closes the open-top box into a torsion box)
   - Snap tabs along both long edges (4 per side), engaging detent ridges on tray walls
   - No fasteners — snap-fit only

3. **Front face** — the user-facing panel. Attaches to the front of the tray via snap tabs (2 on each side wall, 1 on floor, 1 on lid edge). Features:
   - Flat outer surface with subtle palm contour
   - Finger channel openings on left and right edges
   - Interior attachment points for lid and tray front edges
   - Cosmetic surface (print with the outer face on the build plate for best finish)

4. **Release plate** — flat plate (~55 mm x 55 mm x 5 mm) with:
   - 4x stepped bores (6.5 mm through / 9.8 mm collet engagement / 15.5 mm body end clearance)
   - 4x guide post bores (3.7-3.8 mm) at diagonal corners
   - 2x linkage rod attachment points (left and right edges)
   - Print flat (XY plane) so bore axes are in Z for best accuracy

5. **Floor plate** — removable bottom panel for the pump mounting zone only. Allows pump installation from below after the tray is assembled. Attaches with 2x M3 screws into heat-set inserts in the tray floor ribs.
   - Alternative: if the tray is printed with the open top facing up, pumps can be installed from above before the lid goes on, and the floor plate can be eliminated (reducing to 4 printed parts). Decide during prototyping.

### Why This Split

- **Tray is the backbone** — all precision geometry (fitting pockets, guide posts, rail features) is in one part, eliminating alignment errors between parts.
- **Lid snaps on** — no screws, easy to open for tube routing during assembly.
- **Front face is separate** — can be reprinted in different colors/textures for cosmetics without reprinting the tray. Also allows the finger channels to be molded without supports (print the front face standing up).
- **Release plate is separate** — must slide freely on guide posts, so it cannot be integral to any other part.
- **Floor plate is a maybe** — only needed if pump installation from the top is impractical.

---

## 6. Pump Mounting

### Approach: Bracket + Motor Cradle (Strategy B from research)

Each pump mounts to the tray floor via its factory stamped-metal bracket:

- 2x M3 heat-set inserts per pump (4 total), pressed into bosses on the tray floor at 49.45 mm center-to-center
- M3 x 8 mm socket head cap screws through bracket holes into inserts
- Semi-circular motor cradle (half-pipe, 35.5 mm ID, 0.5 mm clearance) printed as a rib rising from the tray floor behind each pump
- Cradle prevents rotation (even if bracket is 1x2 pattern) and supports motor against vibration
- No vibration isolation needed (short duty cycles, PETG compliance, enclosed appliance)

### Pump Orientation

Motors face forward (toward the user). This puts the tube barbs at the back of the pump zone, close to the fitting zone, minimizing tube routing distance. The 180-degree tube bends happen in the space between the pump barbs and the fittings.

Why motors forward: the motor bodies are cylindrical and nest cleanly into the front face area. The pump heads (square, with bracket ears) sit in the middle of the cartridge where there is more width. The tube barbs point rearward toward the fittings, and the tubes only need a short U-turn rather than running the full length of the cartridge.

### Two Pumps Side by Side

| Parameter | Value |
|-----------|-------|
| Bracket width per pump | 68.6 mm |
| Gap between brackets | 5 mm |
| Total pump zone width | 142.2 mm |
| Cartridge interior width | ~144 mm (160 mm - 2x 8 mm walls) |

The pumps fit with about 1 mm clearance on each side — snug but workable. If the gap between brackets is reduced to 3 mm, there is 3 mm clearance per side.

---

## 7. Tube Routing

### Route

Each pump has 2 barbed tube stubs (inlet and outlet) pointing rearward. Silicone tubing pushes onto the barbs and routes rearward to the John Guest fittings, which also face rearward (toward the dock).

Because both the barbs and the fittings face the same direction (rearward), the tubes run nearly straight from barbs to fittings. The only bend is a gentle lateral offset (the barbs are at pump-center spacing, the fittings are at 20 mm center-to-center). This means:

- No 180-degree turns needed
- Minimum bend radius of 25 mm is easily satisfied
- 4 tubes route through the space between the pump heads and the rear wall
- Tubes are held in printed U-channels (10 mm wide x 10 mm deep) molded into the tray floor
- Snap-over clips at 30 mm intervals prevent tubes from lifting out of channels

### Tube Length Inside Cartridge

From pump barb to fitting rear port: approximately 60-80 mm of tubing per line (depends on final pump position and lateral offset). With 4 lines, total internal tubing is ~280-320 mm.

---

## 8. John Guest Fitting Mounting

### Press-Fit in Tray Rear Wall

The John Guest PP0408W has a barbell profile: 15.10 mm body ends with a 9.31 mm center waist. The tray rear wall has 4x through-bores sized for the center body:

- **Bore diameter:** 9.5 mm (light press-fit on 9.31 mm center body)
- **Bore depth:** 12.16 mm (matches center body length exactly)
- The body end shoulders (15.10 mm OD) sit against the rear face of the bore on each side, providing axial location
- The dock-facing body ends protrude through the back wall toward the release plate
- The user-facing body ends protrude inward for tube connection

This is a clean, zero-fastener mounting. The press-fit on the center body plus the shoulder capture makes the fitting rigid in all 6 degrees of freedom.

### Fitting Pattern

4 fittings in a 2x2 grid at 20 mm center-to-center spacing. The active area is ~40 mm x 40 mm. This grid is centered on the tray rear wall.

---

## 9. Release Plate Geometry

Directly from the collet release research, with the verified spatial layout:

### Stepped Bore Design (per fitting)

1. **Tube clearance through-hole:** 6.5 mm diameter (between 6.30 mm tube OD and 6.69 mm collet ID)
2. **Collet engagement bore:** 9.8 mm diameter x 2 mm deep (just over 9.57 mm collet OD; lateral constraint)
3. **Body end clearance bore:** 15.5 mm diameter (clears 15.10 mm body end OD)

The annular face between the 6.5 mm through-hole and the 6.69 mm collet ID is what pushes the collet inward. The 0.19 mm engagement lip per side is the tightest tolerance — verify with a test print.

### Guide Posts

4x 3.5 mm diameter posts at diagonal corners of the plate, rising from bosses on the tray rear wall area. The plate has 3.7-3.8 mm bores for 0.2-0.3 mm sliding clearance.

### Linkage Attachment

The left and right edges of the plate have printed hooks or slots where the linkage rods attach. The rods are rigid PETG rods (4 mm diameter) that run along the inside of the tray side walls through guide slots, connecting to the pull tabs at the front.

---

## 10. Electrical Connection

### Blade/Spade Connectors

4x 6.3 mm blade terminals total (2 per pump: + and -):

- **Male blades** mounted on the dock (enclosure fixed side), oriented parallel to the cartridge insertion axis
- **Female spade terminals** crimped onto pump motor wires inside the cartridge
- Blades engage progressively during cartridge insertion (last ~5 mm of travel)
- **Polarity enforcement:** Asymmetric blade spacing — the two blades for pump 1 are at a different vertical spacing than pump 2. This also prevents swapping pump 1 and pump 2 connections.

### Cartridge Present Detection

A 5th blade pair (smaller, 2.8 mm or 4.8 mm) serves as a continuity loop for "cartridge present" detection by the ESP32. The dock side has both blades; the cartridge side has a wire jumper between the two matching spade terminals. When the cartridge is seated, the loop closes.

---

## 11. Guide Rail and Dock Alignment

### T-Rail System

The cartridge has T-shaped rail tongues running the full depth of both side walls (left and right). The dock has matching T-channels. This is the DeWalt battery pattern applied to the cartridge:

- **Rail cross-section:** T-shape, 6 mm wide tongue, 3 mm tall cap, 4 mm slot depth
- **Rail length:** Full cartridge depth (~155 mm)
- **Material:** PETG on both cartridge and dock sides
- **Clearance:** 0.3 mm per side (tight enough for smooth feel, loose enough for FDM tolerance)

The T-rails prevent the cartridge from lifting or tilting — it can only slide along the insertion axis. The rails also provide the blind-mate alignment for the blade connectors and tube-to-fitting engagement.

### Insertion End-Stop

A spring-loaded detent on the dock side engages a recess on the cartridge at end-of-travel. This provides:

- Audible click confirming full insertion
- Retention force preventing the cartridge from creeping out
- The detent does NOT need to be released for removal — the squeeze-release action only releases the tube collets. The detent force is low enough (5-10 N) that after the collets are released, pulling the cartridge overcomes the detent easily.

### Keying

The T-rails are not centered — they are offset vertically so the cartridge cannot be inserted upside down. Combined with the asymmetric blade spacing, the cartridge can only go in one way.

---

## 12. Assembly Sequence

1. Press 4x M3 heat-set inserts into tray floor bosses (soldering iron, 245C)
2. Press 4x John Guest fittings into tray rear wall bores (center body press-fit)
3. Place release plate over guide posts, verify it slides freely (1.5 mm travel)
4. Thread 2x linkage rods through tray wall guide slots, attach to release plate hooks
5. Mount pump 1: set bracket on bosses, insert 2x M3 screws, tighten into inserts. Repeat for pump 2.
6. Push silicone tubing onto pump barbs (4 connections)
7. Route tubing through channels, secure with snap clips
8. Push tubing into user-facing ports of John Guest fittings (4 connections — push-to-connect, no tools)
9. Snap lid onto tray
10. Snap front face onto tray (pull tabs align with linkage rods and attach via printed hooks)
11. (If floor plate is used) Attach with 2x M3 screws

Total fasteners: 4x M3 screws for pumps + 2x M3 screws for floor plate (if used) = 4-6 screws. Everything else is snap-fit or press-fit.

---

## 13. Bill of Materials (Per Cartridge)

### Printed Parts (PETG)

| Part | Qty | Estimated Print Time | Notes |
|------|-----|---------------------|-------|
| Tray | 1 | 4-6 hr | Largest part; contains all precision geometry |
| Lid | 1 | 1-2 hr | Flat panel with snap tabs |
| Front face | 1 | 1-2 hr | Cosmetic surface |
| Release plate | 1 | 0.5-1 hr | Small, flat, precision bores |
| Floor plate | 0-1 | 0.5-1 hr | Only if needed for pump access |
| Linkage rods (2x) | Printed integral with release plate or front face | — | Or cut from 4 mm PETG rod stock |

### Off-the-Shelf Parts

| Part | Qty | Source | Approx. Cost |
|------|-----|--------|-------------|
| Kamoer KPHM400 peristaltic pump | 2 | Amazon | — |
| John Guest PP0408W 1/4" union | 4 | Amazon | — |
| M3 x 5.7 mm brass heat-set insert | 4-6 | Amazon (CNC Kitchen style) | — |
| M3 x 8 mm socket head cap screw | 4-6 | Amazon / Home Depot | — |
| 6.3 mm male blade terminal | 5 | Amazon / Home Depot | — |
| 6.3 mm female spade terminal (insulated) | 5 | Amazon / Home Depot | — |
| 1/4" ID silicone tubing | ~320 mm | (from existing 6 m roll) | — |
| 22 AWG wire (cartridge-present jumper) | ~100 mm | Any | — |

### Tools for Assembly

- Soldering iron with M3 insert tip (for heat-set inserts)
- M3 hex key or driver
- Wire crimper (for spade terminals)

---

## 14. Design Patterns Applied

| Pattern (from research) | How Applied |
|------------------------|-------------|
| **Slide-Rail with Spring-Detent** (DeWalt, Dell) | T-rails on cartridge sides guide insertion; spring detent clicks at end-of-travel |
| **Squeeze-to-Release** (DeWalt battery buttons) | Palm-on-front-face + fingers-on-pull-tabs = bilateral squeeze releasing collets |
| **Blind-Mate Connector** (Dell backplane, DeWalt blades) | Rails align blade connectors and tube-to-fitting engagement; user never sees the connections |
| **Push-to-Lock / Squeeze-to-Release Asymmetry** (John Guest inherent) | Insertion is effortless (tubes push into collets). Removal requires deliberate squeeze. Prevents accidental disconnection |
| **Auto-Shutoff on Disconnect** (3M Aqua-Pure, John Guest inherent) | Collets re-grip when cartridge is removed — no dripping, no mess |
| **Keying Prevents Errors** (Staubli, 3M, printers) | Offset T-rails + asymmetric blade spacing = cartridge only goes in one way |
| **Click is Confirmation** (universal) | Spring detent click on insertion; hard stop on squeeze-release |

Every pattern from the research that applies to a linear-slide cartridge with fluid connections has been integrated. The design does not bolt on mechanisms — the rail is the alignment, the squeeze is the release, the collets are the lock.

---

## 15. Alternatives Considered and Rejected

### Lever-Amplified Release (Staubli Pattern)

A single lever on the front face that cams the release plate forward when pulled. This would provide mechanical advantage for the 20-60 N collet release force.

**Rejected because:** The ergonomic analysis shows the squeeze force is already within comfortable range for the 5th-percentile female (3x-9x margin). A lever adds a protruding mechanism to the front face, makes the interaction two-step (pull lever, then slide out), and introduces a pivot point that must be robust. The squeeze is simpler, more intuitive, and mechanically sufficient. A lever would only be justified if the collet release force turned out to be much higher than estimated (above ~100 N for all four), which is unlikely for finger-operable fittings.

### Bayonet / Quarter-Turn Lock

Rotate the cartridge to lock/unlock.

**Rejected because:** Incompatible with linear rail guidance. Rails constrain the cartridge to a single axis. Rotational mechanisms require a different dock geometry and lose the blind-mate alignment advantage.

### Magnetic Retention (JUUL Pattern)

Magnets in the dock and cartridge provide retention force; pull to remove.

**Rejected because:** The retention force must hold against 4 pressurized fluid lines. Magnets sufficient for this would make removal difficult, especially with the added tube-grip force from the collets. The squeeze-release explicitly decouples retention (detent) from connection release (collets), which is safer and more controllable.

### Single-Piece Cartridge Body (No Split)

Print the entire cartridge as one piece.

**Rejected because:** A single enclosed box cannot be printed without extensive supports. The tray + lid split allows the tray to print open-top-up with minimal supports, and the lid prints flat. The front face separation enables cosmetic reprints and support-free printing of the finger channels.

---

## 16. What Would Change This Recommendation

1. **Collet release force is much higher than estimated (>100 N total):** Would need to add a lever or cam mechanism for mechanical advantage. The finger channel geometry could accommodate a pivoting lever instead of a sliding pull tab.

2. **Motor diameter is significantly different from ~35 mm:** Would change cradle geometry but not the overall design.

3. **Bracket hole pattern is 2x2 (not 1x2):** Would change the heat-set insert pattern to 4 per pump (8 total) and eliminate the need for the motor cradle's anti-rotation function (though the cradle still adds vibration support, so keep it).

4. **Tube barb positions create crossing paths:** If the inlet and outlet barbs are positioned such that the tubes must cross each other, the tube routing zone needs to be deeper and the channels rearranged. This would increase the cartridge depth by 20-30 mm.

5. **The 0.39 mm bore tolerance (6.30-6.69 mm) is not achievable on the Bambu H2C:** Would need to widen the design window by using a slightly smaller tube (unlikely) or accepting that the release plate may not perfectly center on the collet (the engagement bore at 9.8 mm provides enough lateral constraint that this may not matter).

---

## 17. Open Physical Verification Needed Before CAD

These items from the research remain unverified and should be confirmed with calipers before starting detailed CAD:

1. Motor body diameter (currently ~35 mm, LOW confidence)
2. Bracket hole pattern (1x2 or 2x2)
3. Tube connector exit positions on pump front face (X/Z offsets)
4. Whether the bracket can be separated from the pump head
5. Motor flat orientation relative to bracket ears
