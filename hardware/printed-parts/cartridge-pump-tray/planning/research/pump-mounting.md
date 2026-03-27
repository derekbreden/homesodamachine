# Pump Mounting Inside the Cartridge Body

Research document for how two Kamoer KPHM400-SW3B25 peristaltic pumps physically attach to a 3D printed surface inside the replaceable cartridge body. Covers pump mounting features, vibration management, print design for screw bosses, tubing strain relief, wire routing, and integration with the cartridge shell.

## Scope and Confidence

This document synthesizes the Kamoer KK series product manual (KKDD/TS, version A/3), the KPHM400 product page specifications, Amazon listing data, caliper measurements of the physical pumps, and established 3D printing design guidelines. Critical mounting dimensions (pump head size, mounting hole pattern, total length) are **caliper-verified** from the actual KPHM400-SW3B25 units in hand. Where values are inferred from the KK series manual or from general engineering practice, they are noted as **inferred**.

---

## 1. Kamoer KPHM400-SW3B25 Mounting Features

### Overall Dimensions

| Parameter | Value | Source |
|-----------|-------|--------|
| Overall size (L x W x H) | 116.48 x 68.6 x 62.6 mm (caliper-verified; 111.43mm without motor nub) | Caliper-verified (supersedes datasheet 115.6mm) |
| Weight (brushed DC variant) | ~306 g | Verified -- Kamoer specs |
| Pump tube | BPT 25# (4.8 mm ID x 8.0 mm OD) | Verified -- model suffix B25 |
| Motor type | 12V DC brushed | Verified -- model suffix SW |
| Number of rollers | 3 | Verified -- Kamoer specs |
| Power consumption | 10W | Verified -- Kamoer specs |
| Current draw (12V) | ~0.83A typical | Inferred -- 10W / 12V |
| Noise | <=65 dB | Verified -- Kamoer specs |

### Mounting Bracket (Caliper-Verified)

The KPHM400-SW3B25 ships with a black stamped metal mounting bracket sandwiched between the pump head and motor. The bracket extends beyond the pump head body on two sides, providing mounting ears with screw holes.

| Parameter | Value | Source |
|-----------|-------|--------|
| Bracket total width (including ears) | **68.6 mm** | Caliper-verified (matches datasheet) |
| Pump head width (square cross-section) | **62.6 mm** | Caliper-verified (multiple readings: 62.51-62.61mm) |
| Ear overhang per side | **~3 mm** | Derived: (68.6 - 62.6) / 2 |
| Mounting holes | **2x M3 through-holes** (one per ear) | Caliper-verified |
| Mounting hole diameter | **3.13 mm** | Caliper-verified |
| Mounting hole center-to-center | **49.45 mm** | Caliper-verified (47.88mm edge-to-edge + 3.13mm) |
| Bracket thickness | ~1.5-2 mm | Estimated from photos |

**Note:** The 49.45mm c-t-c measurement is along one axis only (the bracket ear axis). The bracket appears to have only 2 holes total (1 per ear), not a 2x2 pattern. If a second axis exists, that spacing is TBD.

### Tube Exit Points

The pump tubing (BPT, 4.8 mm ID x 8.0 mm OD) exits from the pump head at the front of the unit. Inlet and outlet are on the same face (the pump head cover), exiting roughly parallel to each other, spaced apart by the pump head geometry. The tube stubs extend approximately 30-50 mm from the pump head (these are the soft BPT tubes that connect to the rest of the fluid path).

**Interdependency with cartridge design:** These BPT tube stubs must connect to hard 1/4" OD tubing inside the cartridge before reaching the push-to-connect fittings on the mating face. Soft silicone/BPT tubing does not hold in John Guest push-connect fittings (established constraint from Round 1). The connection between BPT pump tubing and 1/4" hard tubing will require barb fittings or a short transition section.

---

## 2. Vibration Analysis

### Source of Vibration

Peristaltic pumps generate pulsating vibration from two mechanisms:

1. **Roller compression**: Each of the 3 rollers sequentially compresses and releases the tubing against the pump housing. At typical operating speeds (~200-350 RPM for the KPHM400), this produces a pulsation frequency of 10-17 Hz (3 rollers x RPM / 60). This is a low-frequency mechanical pulse.

2. **Motor vibration**: The DC brushed motor produces higher-frequency vibration from commutator switching and rotor imbalance. Brushed motors are inherently noisier than brushless -- the KPHM400 is rated at <=65 dB.

3. **Resonance coupling**: If the pump mounting structure has a natural frequency near the roller pulsation frequency, vibration amplifies significantly. A rigid 3D printed housing with the right (wrong) geometry could act as a sounding board.

### Impact on Mounting Design

| Concern | Severity | Mitigation |
|---------|----------|------------|
| Vibration transmitted to dock | Medium | Rubber isolation between cartridge shell and dock rails |
| Buzzing/rattling noise amplification | High | Avoid thin unsupported panels in the cartridge body |
| Screw loosening | Medium | Use lock washers, nyloc nuts, or thread-locking compound |
| Tubing fatigue at connections | Low | BPT tubing is inherently flexible; barb connections are secure |
| Structural fatigue of 3D print | Low | PETG handles cyclic loading well at these force levels |

### Vibration Isolation Options

**Option A: Rigid mount (no isolation)**
- Pump screwed directly to a 3D printed internal plate
- Simplest design, fewest parts
- Vibration transmits through cartridge body to dock
- Acceptable if the dock itself sits on rubber feet or compliant pads
- The cartridge sliding rails already provide some decoupling

**Option B: Rubber grommet isolation**
- M3 screws pass through rubber grommets (standard neoprene, ~6-8 mm OD, ~3 mm ID)
- Pump "floats" on compliant mounts
- Reduces vibration transmission by 60-80% for frequencies above 30 Hz
- Adds ~2 mm to mounting stack height
- Standard rubber grommets available from McMaster or Amazon for pennies each
- Grommet isolators work best when the disturbing frequency is at least 2-3x the natural frequency of the isolated system

**Option C: Compliant 3D printed flexures**
- Print thin-walled flexure bridges between the pump mount and the cartridge shell
- Essentially 3D printed "springs" that decouple vibration
- No additional parts needed
- Harder to tune -- requires iteration
- Risk of fatigue cracking at flexure roots if geometry is wrong

**Recommendation:** Option B (rubber grommets) is the best balance of simplicity and effectiveness. Four small rubber grommets per pump (8 total) add negligible cost and weight, provide proven vibration isolation, and don't require design iteration. Option A is acceptable as a starting point for prototyping -- if vibration is not objectionable in practice, skip the grommets.

---

## 3. Mounting Surface Design for 3D Printing

### Material Selection

PETG is the recommended material (established in guide-alignment.md for sliding surfaces). It also has excellent properties for mounting:

| Property | PLA | PETG | ABS |
|----------|-----|------|-----|
| Layer adhesion | Poor | Good | Good |
| Screw pull-out resistance | Low | Medium | Medium |
| Creep resistance | Poor | Good | Good |
| Impact resistance | Low | High | Medium |
| Chemical resistance (water) | Adequate | Good | Good |
| Recommended for pump mounts | No | **Yes** | Acceptable |

### Screw Boss Design Rules

For M3 screws into a 3D printed PETG mounting surface:

**Direct screwing into printed plastic (self-tapping)**:
- Pilot hole: 2.5 mm diameter for M3 self-tapping screw
- Boss OD: minimum 7 mm (2.5 mm hole + 2x 2.25 mm wall)
- Boss height: minimum 6 mm for adequate thread engagement
- Works for prototyping but strips after 3-5 reassembly cycles

**Heat-set threaded inserts (recommended)**:
- Insert: M3 x 4 mm or M3 x 5 mm brass knurled insert
- Pilot hole: 4.0 mm diameter for M3 insert in PETG
- Boss OD: minimum 8 mm (4.0 mm hole + 2x 2.0 mm wall)
- Boss height: minimum 6 mm (insert length + 1 mm clearance)
- Installation: soldering iron at 245C for PETG, press insert into hole
- Withstands unlimited reassembly cycles
- Pull-out strength: 200-400N per insert in PETG
- **This is the right choice for a replaceable cartridge** -- the user may never disassemble it, but the designer will during prototyping

**Captive nut (alternative)**:
- Hex recess printed into the boss for an M3 nut
- Nut drops into recess, screw threads in from opposite side
- No heat tools needed
- Slightly bulkier but very strong
- Good option if you don't have a soldering iron available during assembly

### Print Orientation and Layer Line Effects

```
STRONG (screw parallel to layers):        WEAK (screw perpendicular to layers):

    Screw                                      Screw
      |                                          |
      V                                          V
  =========  <-- layer                       |||||||||  <-- layer lines
  =========  <-- layer                       |||||||||      run across
  =========  <-- layer                       |||||||||      the screw
  =========  <-- layer                       |||||||||      axis

  Shear load distributed                     Pull-out splits
  across many layers                         between layers
```

**Rule:** Orient the mounting plate so that screw axes run **parallel** to (or at a shallow angle to) the layer lines. This means the mounting plate should be printed as a horizontal surface (screw holes pointing up during printing). This distributes pull-out loads across many layer bonds rather than trying to separate individual layers.

If the cartridge geometry forces a vertical mounting plate (screws going horizontally into a wall), increase wall thickness to at least 4 mm around each boss and use heat-set inserts rather than self-tapping screws.

### Minimum Mounting Surface Specs

| Parameter | Minimum | Recommended |
|-----------|---------|-------------|
| Plate thickness | 4 mm | 6 mm |
| Boss wall around insert | 2.0 mm | 2.5 mm |
| Boss height | 5 mm | 6 mm |
| Infill density in mount area | 40% | 60-100% |
| Perimeter/wall count | 3 | 4 |
| Screw-to-edge distance | 4 mm | 6 mm |
| Material between adjacent bosses | 3 mm | 5 mm |

### Surface Area for Stability

Each KPHM400 weighs ~306g and has a footprint of roughly 116.5 x 68.6 mm (caliper-verified). The mounting plate needs to support this weight plus dynamic loads from vibration (~2-3x static weight as a conservative estimate for impulse loads).

Minimum contact area per pump: the mounting bracket's full footprint (~68.6 x bracket depth). The 3D printed receiving surface should match or exceed this area and be well-supported by the cartridge shell walls.

---

## 4. Tubing Strain Relief

### The Problem

Each pump has two tube stubs (inlet and outlet) made of soft BPT tubing (4.8 x 8.0 mm). Inside the cartridge, these connect to hard 1/4" OD tubing that terminates at the push-to-connect fittings on the mating face. The connection points are vulnerable to:

1. **Pull force during insertion**: When the cartridge slides into the dock and the tubes engage the push-connect fittings, there's a brief insertion force. The release plate and cam mechanism handle the locking, but during insertion the tube stubs experience axial load.

2. **Vibration fatigue**: Pump vibration causes micro-movement at every tubing connection. Over thousands of hours, an unsupported connection can fatigue and leak.

3. **Assembly stress**: When the user (or you, during prototyping) connects the BPT pump tubes to the internal hard tubing, there's a risk of pulling the tube off the pump port if there's no strain relief.

### Strain Relief Features

**Option A: Printed channel/clip restraints**

```
Top view of cartridge interior:

  +------------------------------------------+
  |                                          |
  |   [PUMP 1]====BPT=====[barb]=hard tube====> to fitting
  |              ^         ^                 |
  |              |         |                 |
  |           clip 1    clip 2               |
  |                                          |
  |   [PUMP 2]====BPT=====[barb]=hard tube====> to fitting
  |              ^         ^                 |
  |              |         |                 |
  |           clip 1    clip 2               |
  |                                          |
  +------------------------------------------+
```

- Print C-shaped clips or U-channels along the tubing path
- Clips grip the tubing OD (8.0 mm for BPT, 6.35 mm for 1/4" hard tube)
- Minimum 2 clips per tube run: one near the pump port, one near the barb connection
- Clip ID = tube OD + 0.3 mm (press-fit snap)
- Clip opening width = tube OD - 1.5 mm (allows snap-in but resists pull-out)
- Printed as part of the cartridge body walls -- no separate fasteners

**Option B: Zip-tie anchors**

- Print small loops or tie-down posts on the cartridge interior walls
- Route standard zip ties around the tubing at anchor points
- Quick, adjustable, but less elegant
- Useful for prototyping before finalizing the clip geometry

**Option C: Printed tube routing channels**

- Full half-round channels molded into the cartridge floor or walls
- Tubing snaps into channels and is constrained along its entire length
- Most robust but hardest to design and print (requires very accurate tube path planning)
- Best for the final production design, not the first prototype

### BPT to Hard Tube Transition

The BPT pump tube (4.8 mm ID x 8.0 mm OD) must connect to 1/4" OD (6.35 mm) hard tubing inside the cartridge. Options:

| Method | Description | Reliability |
|--------|-------------|-------------|
| Barb fitting | Brass or nylon barb with hose clamp | High -- standard plumbing approach |
| Press-fit overlap | BPT tube stretched over hard tube stub (hard tube acts as barb) | Medium -- only if ODs match well |
| Printed manifold | 3D printed block with barbed ports for both tube sizes | Low -- layer lines leak under pressure |

**Recommendation:** Use small brass barb fittings (1/4" barb x 3/16" barb, or similar size matching the BPT ID and hard tube OD). Secure with small hose clamps or cable ties. Place the barb connection where a printed clip provides strain relief on both sides of the joint.

### Tube Routing Geometry

The tube path from pump head to mating face should:
- Avoid tight bends (minimum bend radius for BPT 25# tubing: ~20 mm, roughly 2.5x OD)
- For 1/4" OD hard PE/PU tubing (post-barb transition): minimum cold-bend radius ~25 mm (4x OD). Inside the cartridge, the hard tubing runs are short (barb fitting to JG fitting on rear wall), so bends are typically avoidable with straight runs. If a direction change is needed, a single 90° JG elbow is preferred over a cold bend.
- Keep tube runs as short as practical to minimize internal dead volume
- Route tubes along cartridge walls where printed clips can anchor them
- Avoid crossing tube paths between the two pumps (prevents tangling and simplifies the routing)

---

## 5. Electrical Routing

### What Needs to Route

Each pump has 2 motor wires (DC+ and DC-). With 2 pumps sharing a common ground, the cartridge needs 3 electrical contacts total (established in electrical-mating.md):

| Contact | Function | Max Current |
|---------|----------|-------------|
| GND | Common ground for both motors | ~1.7A (both pumps) |
| Motor A+ | Pump 1 positive, 12V | ~0.85A |
| Motor B+ | Pump 2 positive, 12V | ~0.85A |

### Wire Routing Inside the Cartridge

```
Side cross-section:

  +--[ PUMP 1 ]--wire--+
  |                     |     +--[ pogo pad face ]
  |  (interior)         +---->|  [GND] [A+] [B+]
  |                     +---->|
  +--[ PUMP 2 ]--wire--+     +------------------
```

The motor wires must route from the rear of each pump (where the motor leads exit) to the electrical mating face. From electrical-mating.md, the recommendation is to place electrical contacts on a **different face** than the water fittings, or if on the same face, place electrical contacts above water with a dam/channel between.

**Wire routing options:**

**Option A: Through-channel in cartridge wall**
- Print a channel or conduit in the cartridge body wall
- Wires press-fit into the channel during assembly
- Channel has a snap-on cover or is printed as a closed tunnel with a wire-pull slot
- Clean routing, protected wires

**Option B: Surface-mount wire clips**
- Print small clips on the cartridge interior walls
- Wires run along the wall surface, held by clips every 20-30 mm
- Simpler to print, easier to assemble
- Wires are exposed inside the cartridge (acceptable -- the cartridge is sealed)

**Option C: Wire harness with connector**
- Pre-assemble a short wire harness with JST or Molex connectors
- One end connects to the pump motor leads, other end solders to pogo target pads
- Allows pump replacement without re-soldering
- Overkill for a disposable cartridge, but useful during prototyping

### Strain Relief at the Mating Face

Where wires terminate at the pogo pin target pads (on the cartridge mating face), they need strain relief to prevent:
- Solder joint fatigue from repeated insertion/removal cycles
- Wire pull-out if the cartridge is handled roughly

**Recommended approach:**
- Solder wires to a small PCB (~15 x 30 mm) that serves as the pogo target pad array
- Mount the PCB in a recessed pocket on the cartridge mating face
- Print a wire entry slot in the pocket wall with a strain relief notch (wire bends 90 degrees through a tight channel before reaching the solder joint)
- Optionally pot the solder joints with hot glue or silicone for moisture protection

### Wire Gauge

For ~1A at 12V over a short run (<200 mm inside the cartridge), 22 AWG stranded wire is adequate. The pump motor leads are likely 24-26 AWG; if so, splice to 22 AWG with solder+heatshrink at the pump end for better current handling and mechanical robustness.

---

## 6. Pump Arrangement Inside the Cartridge

### Arrangement Options

Two KPHM400 pumps (each 116.5 x 68.6 x 62.6 mm, caliper-verified: 116.48mm total length with motor nub, 68.6mm bracket width, 62.6mm square pump head) must fit inside the cartridge body. Since peristaltic pumps work in any orientation (confirmed with parts in hand), the arrangement is driven by cartridge envelope constraints and tube routing simplicity.

**Option A: Side-by-side, motors facing same direction**

```
Top view:
  +---------------------------------------+
  |  [PUMP 1]  |  [PUMP 2]               |
  |  motor->   |  motor->                |
  |  tubes <-  |  tubes <-               |
  +---------------------------------------+
  Width: ~137 mm (68.6 x 2)
  Depth: ~117 mm (116.48 with motor nub)
  Height: ~63 mm
```

- Widest arrangement (~137 mm minimum internal width)
- Simplest tube routing (both pump heads face the same direction)
- Motors and pump heads aligned -- easy to mount on a single flat plate
- Electrical leads exit from the same side

**Option B: Side-by-side, motors facing opposite directions**

```
Top view:
  +---------------------------------------+
  |  [PUMP 1]  |  [2 PMUP]               |
  |  motor->   |   <-motor               |
  |  tubes <-  |   -> tubes              |
  +---------------------------------------+
  Width: ~137 mm
  Depth: ~117 mm
```

- Same footprint as Option A
- Tube exits on opposite ends -- requires more complex routing
- No real advantage over Option A

**Option C: Stacked vertically**

```
Front view:
  +--------------------+
  |    [PUMP 1]        |
  |    motor->         |
  |--------------------|
  |    [PUMP 2]        |
  |    motor->         |
  +--------------------+
  Width: ~69 mm
  Depth: ~117 mm
  Height: ~125 mm (62.6 x 2)
```

- Narrowest cartridge (~69 mm width)
- Tallest cartridge (~126 mm minimum internal height)
- Under-sink vertical space is usually plentiful
- Tube routing from bottom pump is slightly longer
- Mounting requires two shelves or a vertical plate with brackets at two heights

**Option D: Inline (end-to-end)**

```
Top view:
  +--------------------------------------------------+
  |  [PUMP 1] motor-> | [PUMP 2] motor->             |
  +--------------------------------------------------+
  Width: ~69 mm
  Depth: ~233 mm (116.48 x 2)
  Height: ~63 mm
```

- Very long and narrow cartridge
- Poor use of space
- Only considered if the dock geometry demands a narrow slot

### Envelope Summary

| Arrangement | Min Width | Min Depth | Min Height | Tube routing complexity |
|-------------|-----------|-----------|------------|------------------------|
| Side-by-side (same dir) | ~140 mm | ~120 mm | ~65 mm | Low |
| Stacked | ~72 mm | ~120 mm | ~128 mm | Medium |
| Inline | ~72 mm | ~236 mm | ~65 mm | Low |

Add ~5-10 mm to each dimension for cartridge wall thickness, clearance, and mounting hardware.

**Interdependency:** The mating face has 4 push-to-connect fittings (2 inlets, 2 outlets) in a pattern defined by collet-release.md. The fitting body OD is ~12.7 mm, and the release plate needs specific bore spacing. The pump arrangement must place tube exits within routing distance of the mating face fittings without tight bends or crossings.

---

## 7. Integration with Cartridge Shell

### One-Piece vs Multi-Part Body

**Option A: Monolithic print (one piece + lid)**
- Cartridge body is a single print with integrated pump mounting bosses, tube clips, wire channels, and rail features
- Lid screws or snaps on for access during assembly
- Fewest parts, fastest assembly
- Print time: long (large single piece), but only one print job
- Risk: if any feature fails dimensionally, the whole body is scrapped
- FDM constraint: internal features (bosses, clips) may need support material

**Option B: Tray + shell assembly**
- Internal pump tray (flat plate with mounting bosses, tube clips) prints separately
- Outer shell (rails, walls, mating face pocket) prints separately
- Tray slides or screws into shell during assembly
- Allows re-printing just the tray if mounting dimensions change
- Better print orientation control (tray prints flat for strongest screw bosses)
- More assembly steps but more design flexibility

**Option C: Multi-section shell**
- Body splits into 2-3 sections along the long axis
- Sections join with printed dovetails, screws, or snap-fits
- Each section is small enough to print quickly and fit on smaller build plates
- Most complex assembly but maximum print flexibility

### Recommended Approach for Prototyping

**Option B (tray + shell)** is the best starting point:

1. **Pump tray**: A flat plate (~140 x 120 x 6 mm for side-by-side arrangement) with 4-8 heat-set insert bosses for the two pump mounting brackets. Includes printed tube clips along the edges and a wire routing channel. Prints flat (horizontal) for maximum screw boss strength.

2. **Outer shell**: A rectangular box open on one side, with slide rails on the exterior (per guide-alignment.md: rectangular rails, 0.3-0.5 mm clearance per side). The mating face wall has pockets for push-to-connect fittings and a recess for the pogo target PCB. The tray inserts into the shell and is secured with 2-4 screws.

3. **Lid**: A flat plate that closes the open side of the shell. Secured with screws or snap clips. Provides access for pump installation and wiring.

```
Exploded view (side):

            +===========+
            |    LID    |
            +===========+
                  |
    +===========================+
    |   OUTER SHELL             |
    |   (rails on outside)      |
    |   (fitting pockets on     |
    |    mating face wall)      |
    |                           |
    |   +-------------------+   |
    |   |   PUMP TRAY       |   |   <-- tray drops in, screws to shell floor
    |   |  [P1]     [P2]    |   |
    |   |   bosses, clips   |   |
    |   +-------------------+   |
    |                           |
    +===========================+
```

### Connection Between Tray and Shell

The pump tray must be firmly attached to the shell to prevent rattling and maintain alignment with the mating face fittings:

- 4x M3 screws with heat-set inserts (2 per end of tray)
- Tray rests on printed ledges inside the shell (distribute weight, prevent sagging)
- Tray alignment: printed locating pins or tabs on the tray edges that key into slots in the shell walls

### Integration with Mating Face Components

The mating face of the cartridge must accommodate:

| Component | Space needed | Reference |
|-----------|-------------|-----------|
| 4x push-to-connect fittings | ~12.7 mm OD each, spaced per release plate design | collet-release.md |
| Release plate travel zone | 3.0 mm axial travel behind fittings | collet-release.md |
| Pogo target pads (3 contacts) | ~15 x 30 mm PCB recess | electrical-mating.md |
| Wire entry to pogo PCB | Small slot in mating face wall | Section 5 above |

The internal tube routing from the pump tray must reach the back side of each push-to-connect fitting. The hard 1/4" OD tube stubs press into the fittings from inside the cartridge -- these must be permanently installed during cartridge assembly (the user never touches them).

---

## 8. Recommendation Ranking

### Mounting Method

| Rank | Method | Rationale |
|------|--------|-----------|
| 1 | **Heat-set M3 inserts in PETG tray** | Best pull-out strength, unlimited reassembly, standard hardware |
| 2 | Captive M3 nuts in printed recesses | No heat tools, strong, slightly bulkier |
| 3 | Self-tapping M3 screws into PETG | Fast prototyping, but strips after a few cycles |

### Vibration Management

| Rank | Method | Rationale |
|------|--------|-----------|
| 1 | **Rubber grommet isolators on mount screws** | Cheap, effective, no design iteration needed |
| 2 | Rigid mount (no isolation) | Simplest; try this first, add grommets if noise is objectionable |
| 3 | Printed flexures | Requires tuning, risk of fatigue cracking |

### Pump Arrangement

| Rank | Arrangement | Rationale |
|------|-------------|-----------|
| 1 | **Side-by-side, motors same direction** | Simplest routing, reasonable envelope, symmetric design |
| 2 | Stacked vertically | Narrower cartridge if width is constrained |
| 3 | Inline | Too long for most practical enclosures |

### Tubing Strain Relief

| Rank | Method | Rationale |
|------|--------|-----------|
| 1 | **Printed C-clips integrated into tray/walls** | No extra parts, reliable, clean design |
| 2 | Zip-tie anchors | Good for prototyping, easy to adjust |
| 3 | Full tube routing channels | Best long-term but hardest to get right initially |

### Cartridge Body Construction

| Rank | Method | Rationale |
|------|--------|-----------|
| 1 | **Tray + shell assembly** | Best print orientation control for mounting bosses, iterable |
| 2 | Monolithic print + lid | Fewer parts but higher risk per print |
| 3 | Multi-section | Unnecessary complexity at this stage |

### Wire Routing

| Rank | Method | Rationale |
|------|--------|-----------|
| 1 | **Through-channel in cartridge wall** | Protected, clean, prints as part of the shell |
| 2 | Surface-mount clips | Simpler to print, adequate for prototype |
| 3 | Pre-made harness with connector | Overkill for disposable cartridge |

---

## 9. Open Questions for Physical Verification

Caliper measurements have resolved the critical mounting dimensions. Remaining unknowns before finalizing the cartridge CAD model:

1. ~~**Exact mounting hole pattern**~~ **RESOLVED:** 2x M3 holes, 3.13mm diameter, 49.45mm center-to-center (one axis). Second axis TBD if bracket has 2x2 pattern (appears to be 2 holes total).
2. ~~**Bracket dimensions**~~ **RESOLVED:** 68.6mm total width, pump head 62.6mm square, ~1.5-2mm bracket thickness.
3. **Tube exit positions**: Distance from pump mounting face to each tube exit center, and spacing between inlet and outlet tubes.
4. **Motor lead exit point**: Where do the motor wires exit the motor housing? Length of factory leads.
5. **Overall envelope with tubes**: Measure the full extent of the pump with tubes attached (tubes add to the pump head side).
6. ~~**Motor protrusion**~~ **PARTIALLY RESOLVED:** Total length 116.48mm (with 5.05mm motor nub) or 111.43mm (without nub). Motor protrusion behind the bracket is ~63-68mm.

---

## Sources

- [Kamoer KK Series Product Manual (KKDD/TS), Version A/3](https://m.media-amazon.com/images/I/91kVMb3kOxL.pdf) -- dimensional drawings, assembly breakdown, tube specifications
- [Kamoer KPHM400 Product Page](https://www.kamoer.com/us/product/detail.html?id=10014) -- overall dimensions, weight, technical parameters
- [Kamoer KPHM400 Technical Parameters](https://www.kamoer.cn/us/product/params.html?id=10014) -- tube size, flow rate, motor specs
- [KPHM400 Peristaltic Pump Data Sheet (DirectIndustry)](https://pdf.directindustry.com/pdf/kamoer-fluid-tech-shanghai-co-ltd/kphm400-peristaltic-pump-data-sheet/242598-1017430.html) -- dimensional drawing with mounting holes (PDF, image-based)
- [Amazon KPHM400-SW3B25 Listing](https://www.amazon.com/peristaltic-Brushed-Kamoer-KPHM400-Liquid/dp/B09MS6C91D) -- product photos, weight confirmation
- [CNC Kitchen: Tips for Heat-Set Inserts in 3D Printing](https://www.cnckitchen.com/blog/tipps-amp-tricks-fr-gewindeeinstze-im-3d-druck-3awey) -- insert installation temperatures, boss design
- [Bambu Lab Forum: How to Design Screw Holes for 3D Printing](https://forum.bambulab.com/t/how-to-design-screw-holes-for-3d-printing/217352) -- layer orientation, boss wall thickness, tolerances
- [Formlabs: Adding Screw Threads to 3D Printed Parts](https://formlabs.com/blog/adding-screw-threads-3d-printed-parts/) -- heat-set insert design guidelines
- [PCTflow: Pulsation in Peristaltic Pumps](https://www.pctflow.com/applications/pulsation-in-peristaltic-pumps-and-in-other-type-of-positive-displacement-pumps/) -- vibration characteristics of peristaltic pumps
- [RPM Rubber Parts: Grommet Isolators](https://www.rpmrubberparts.com/stock-parts/vibration-control-products/grommet-isolators) -- rubber grommet vibration isolation specs
