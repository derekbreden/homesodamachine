# Front Panel Component Dimensions
## RP2040 Round LCD, S3 Rotary Display, KRAUS Air Switch

**Research question:** What are the exact physical dimensions of all three front-panel user-interface components, so that the enclosure front panel cutouts can be specified correctly?

**Sources consulted:**
- Waveshare official dimension drawing (CNX Software rehost, March 2024): `RP2040-LCD-0.99-B-details-size.jpg`
- Waveshare wiki: `waveshare.com/wiki/RP2040-LCD-0.99-B` (features confirmed, dimension image not rendered in text)
- CNX Software article on RP2040-LCD-0.99-B (March 2024)
- Elecrow official product page: `elecrow.com/crowpanel-1-28inch-hmi-esp32-rotary-display`
- Elecrow wiki: `elecrow.com/wiki/CrowPanel_1.28inch-HMI_ESP32_Rotary_Display.html`
- CNX Software article on CrowPanel rotary displays (September 2025), including official dimension drawing
- KRAUS KWDA-100 Specification Sheet (PDF, January 2024 revision)
- KRAUS product page: `kraususa.com/garbage-disposal-air-switch-kit-in-mb`

---

## 1. Waveshare RP2040-LCD-0.99-B (Amazon B0CTSPYND2)

### Overall assembly dimensions

The RP2040-LCD-0.99-B ships inside a CNC-machined aluminum case with an acrylic matte bottom plate. The assembly is entirely circular in plan view.

| Dimension | Value |
|-----------|-------|
| Outer diameter (full assembly) | **Φ 33.0 mm** |
| Total depth (front face to back plate) | **9.8 mm** |
| Main body depth (cylindrical CNC case) | **8.0 mm** |
| Front lip overhang (top of case, chamfered) | **1.75 mm** |
| Rear ledge / acrylic back plate protrusion | **~1.8 mm** (9.8 − 8.0) |

Source: Official Waveshare dimension drawing, confirmed by CNX Software article specification ("Dimension – 33 x 9.8 mm").

### Display window

The 0.99-inch IPS LCD is circular with a flat-cut bottom edge (not a full circle — Waveshare describes it as "with flat bottom" in the display area). Specifications:

| Dimension | Value |
|-----------|-------|
| Display active area diameter | **Φ 33.0 mm** (outer case matches display active area — the display fills the face) |
| Resolution | 128 × 115 pixels |
| Controller | GC9107 via SPI |

The display window is the entire front face of the CNC case. There is no separate bezel ring inset — the display glass sits flush with or slightly recessed behind the front rim of the aluminum case.

### Mounting holes

No mounting holes are visible on the PCB in the official interface diagram. The CNC case has two small Phillips screws visible on the bottom face (acrylic plate), used for assembly of the case itself. These are not panel-mounting features. **The module has no integral panel-mounting holes.**

### Connector type, position, and clearance

The bare PCB inside the CNC case carries two connectors, both of which exit through cutouts in the CNC case wall:

| Connector | Type | Position on circular PCB | Clearance required |
|-----------|------|--------------------------|-------------------|
| USB Type-C | USB-C receptacle | Bottom edge of the circular PCB | ~9 mm wide × ~4 mm tall cutout in case wall at bottom |
| SH1.0 6-pin | JST SH 1.0 mm pitch, 6 positions, vertical | Left edge of the circular PCB | ~8 mm wide × ~3 mm tall cutout in case wall at left |

Both connectors face radially outward through slots in the side wall of the CNC case. Cables connecting to them run perpendicular to the panel face (i.e., straight back into the enclosure). A cable attached to either connector requires roughly **15–20 mm of clearance** behind the panel for the cable bend radius, in addition to the 9.8 mm module depth.

The SH1.0 6-pin connector carries: GND, 3V3, GP26, GP27, GP28, GP29.

The BOOT button is accessible through a small hole in the side wall of the CNC case, visible in the dimension side-view drawing.

### Total depth behind panel face

| Condition | Depth |
|-----------|-------|
| Module body only (flush with panel front) | 9.8 mm |
| With USB-C cable attached (minimum bend) | ~30 mm |
| With SH1.0 cable attached (minimum bend) | ~25 mm |

The 9.8 mm module depth is the governing dimension for the panel cutout pocket depth. Cable management behind the panel needs ~30 mm total clearance.

### Bezel / lip geometry

The CNC aluminum case has a small chamfered front rim. From the dimension drawing:
- The top of the case (front face side) has a **1.75 mm** beveled/chamfered profile that reduces from the 33.0 mm outer diameter to the display glass surface.
- The rear has a **~1.8 mm** step where the acrylic back plate sits proud of the cylindrical case body.

This 1.75 mm front chamfer acts as a natural lip that can rest against the front face of a panel cutout. If the panel has a 33.0 mm through-hole, the module will drop straight through. The enclosure must provide a **retention ledge** behind the panel face — the module has no self-locking feature.

### Cutout geometry for flush, removable installation

**Panel cutout:** Circular hole, **Φ 33.0 mm** (nominal). The module drops in from the front.

**Retention:** The CNC case has no snap tabs or threading. Retention must be provided by the enclosure — a printed retaining ring or rear bracket that the module rests against, with the panel face acting as the front stop via the 1.75 mm front chamfer. A three-point printed clip behind the panel, or a printed retention ring with an interference fit, are the practical options.

**Removal:** The module can be pushed out from behind (retracting cable application) or pulled from the front if the front chamfer is accessible (e.g., a notch in the panel cutout rim).

**Self-retention: None. The enclosure must provide retention.**

---

## 2. Meshnology ESP32-S3 1.28" Round Rotary Display (Amazon B0G5Q4LXVJ)

This is a resale of the Elecrow CrowPanel 1.28-inch HMI ESP32-S3 Rotary Display. Elecrow is the original manufacturer; Meshnology sells this exact product under their brand. All dimensional data below is from Elecrow's official sources.

### Overall assembly dimensions

The assembly consists of: a circular PCB, a square aluminum alloy housing frame, an acrylic front layer, and a **rotary knob** — a large knurled aluminum ring that rotates around the circumference of the circular display and also presses for click input.

| Dimension | Value |
|-----------|-------|
| Outer housing footprint (square) | **48 mm × 48 mm** |
| Outer housing diameter (circular face) | **Φ 47.3 mm** |
| Total depth (front face to back of PCB) | **33.1 mm** |
| Quoted overall size | 48 × 48 × 33 mm (Elecrow spec) |
| Weight | 50 g |
| Shell materials | Aluminum alloy + plastic + acrylic |

Source: Elecrow official product page, Elecrow wiki, CNX Software dimension drawing (September 2025).

### Display window and knob geometry

From the CNX Software dimension drawing (front view, labeled):

| Feature | Dimension |
|---------|-----------|
| Outer aluminum housing diameter | **47.3 mm** |
| Bezel inner ring (glass outer edge) | **42.1 mm** |
| Active display window (visible IPS area) | **Φ 32.4 mm** |
| Rotary knob | The knurled aluminum ring is the **outer rim of the housing** — it rotates as a unit around the circular body. Knob outer diameter = 47.3 mm. Knob is not a separate protruding shaft. |
| Display type | 1.28-inch IPS, 240 × 240 pixels |
| Touch type | Capacitive (CST816D) |
| Display controller | GC9A01 |

The rotary knob is the full outer aluminum ring of the device. It does not protrude from the front face as a shaft. It rotates around the display face in-plane. **The depth of the assembly (33.1 mm) accounts for the full electronics stack including the encoder mechanism.**

### Mounting holes

Two **M2.5 threaded screw terminals** are visible on the PCB in the CNX hardware overview diagram, approximately at the 8 o'clock and 2 o'clock positions on the circular PCB. These are panel-mount candidates.

**The module has integral M2.5 mounting holes.**

### Connector type, position, and clearance

All connectors are on the **rear face** of the circular PCB (the face opposite the display). From the CNX hardware overview diagram:

| Connector | Type | Position on rear PCB face |
|-----------|------|--------------------------|
| USB IN (5V) | MX 1.25 mm 4-pin (ZX-MX 1.25-4P) | Top of PCB rear |
| UART | MX 1.25 mm 4-pin (ZX-MX 1.25-4P) | Right side of PCB rear |
| I2C | MX 1.25 mm 4-pin (ZX-MX 1.25-4P) | Bottom-right of PCB rear |
| FPC | 12-pin FPC, 0.5 mm pitch | Left side of PCB rear |
| BOOT button | Tactile switch | Top edge of PCB rear |
| Reset button | Tactile switch | Top edge of PCB rear |

All connectors face rearward (away from the display). Cables attach to the back of the module and run straight back into the enclosure. No connectors exit the side wall.

Cable clearance: MX 1.25 mm connectors require ~10–15 mm behind the PCB for connector body height plus cable bend radius. The FPC requires ~15 mm. Total recommended clearance behind the module: **~50 mm** from panel face (33.1 mm module + 15 mm cable bend).

### Bezel / lip geometry

The front face presents a **silver aluminum bezel ring** (Φ 47.3 mm outer, with the 42.1 mm inner glass opening) that will sit flush against the panel front face. The housing has a square 48 mm × 48 mm footprint, meaning the corners of the aluminum housing extend ~0.35 mm beyond the circular 47.3 mm face in a square profile. A panel cutout that is circular at Φ 47.3 mm will be very close to the housing — the corners of the square housing would catch on a square cutout at 48 mm.

### Total depth behind panel face

| Condition | Depth |
|-----------|-------|
| Module body only | 33.1 mm |
| With MX 1.25 mm cable attached | ~48 mm |
| With FPC cable attached | ~50 mm |

### Cutout geometry for flush, removable installation

**Panel cutout:** Circular hole, **Φ 47.3 mm** allows the circular housing face to drop flush. The square corners (48 mm footprint) will not pass through a circular 47.3 mm hole, so the module cannot be inserted or removed from front through a circular cutout. The module must be inserted/removed from behind (snap-in from back, panel opening shows only the face).

Alternatively, a **square 48 mm × 48 mm cutout** allows front removal. Either geometry is viable depending on the retention strategy.

**Retention:** The M2.5 mounting holes in the PCB provide positive mechanical retention. A printed bracket that captures the M2.5 holes and clamps the module to the panel from behind is the correct approach. The module's front bezel ring rests against the panel front face as a flush stop.

**Self-retention: Partial — M2.5 holes exist for positive mounting. The enclosure bracket should use these.**

---

## 3. KRAUS KWDA-100MB Air Switch (Amazon B096319GMV)

Source: KRAUS KWDA-100 Specification Sheet (official PDF, REV. January 17, 2024).

### Air switch button dimensions

| Dimension | Value (imperial) | Value (metric) |
|-----------|-----------------|----------------|
| Button cap outer diameter | **1 7/8"** | **47.6 mm** |
| Button housing / threaded body diameter | **1 3/4"** | **44.5 mm** |
| Total button assembly height | **3 5/8"** | **92.1 mm** |
| Below-panel threaded stem length | **1 1/2"** | **38.1 mm** |

The spec sheet states: "Button Dimensions: 1 3/4" x 3 5/8"" — this is housing diameter × total height. The cap (visible button face) is **1 7/8" (47.6 mm)** per the dimension drawing, which is slightly larger than the 1 3/4" housing body diameter. The cap overhangs the threaded body by approximately 1/16" (1.6 mm) per side.

### Panel hole required

The spec sheet states: "installs into standard hole in sink deck or countertop... using a standard **1 1/4" faucet hole**."

| Dimension | Value (imperial) | Value (metric) |
|-----------|-----------------|----------------|
| Required panel hole diameter | **1 1/4"** | **31.75 mm** |
| Maximum panel thickness | **1 1/2"** | **38.1 mm** |

The threaded stem passes through the 1 1/4" (31.75 mm) hole. The button cap (47.6 mm) is larger than the hole and acts as the front stop, sitting flush on the panel surface.

### Total depth behind panel face

The threaded stem extends below the panel face. An ABS nut threads onto the stem from below to clamp the switch to the panel:

| Dimension | Value |
|-----------|-------|
| Threaded stem length (below panel) | **38.1 mm (1 1/2")** |
| ABS nut height (estimated) | ~10–15 mm |
| Air tube connection at stem bottom | Pneumatic tube barb at bottom of stem |
| AC adapter box (separate, remote) | 140 mm × 73 mm × 48 mm (5 1/2" × 2 7/8" × 1 7/8") |

**Total minimum depth** required behind the panel face for the button mechanism: **~50 mm** (38.1 mm stem + nut + tube fitting). The AC adapter box mounts anywhere along the 60" (1524 mm) air tube and does not need to be near the panel.

### Pneumatic tube connector

The spec sheet notes a **Ø 1.9 mm** pneumatic tube port at the base of the threaded stem. The included air tube is PVC, 60" (1524 mm) long, connecting the button to the AC adapter box. The tube is flexible and can route in any direction. No specific fitting diameter is called out on the panel — the tube attaches directly to the barb at the bottom of the stem.

### Mounting retention

The KRAUS air switch has **integral self-retention**: the threaded stem + ABS lock nut clamps the switch to any panel up to 1 1/2" thick. No printed retention feature is required — the switch mounts exactly as it would in a countertop.

**Self-retention: Yes. ABS nut locks to threaded stem. Enclosure provides no retention — the switch mounts itself.**

---

## Summary Table: Panel Cutout Specifications

| Component | Cutout Shape | Cutout Diameter | Depth Pocket Required | Self-Retention |
|-----------|-------------|-----------------|----------------------|----------------|
| RP2040 LCD-0.99-B | Circle | **Φ 33.0 mm** | 9.8 mm min (module body) | **None** — enclosure must provide |
| S3 CrowPanel 1.28" Rotary | Circle or Square | **Φ 47.3 mm** circular / **48 mm sq.** | 33.1 mm min (module body) | **Partial** — M2.5 holes for bracket |
| KRAUS KWDA-100MB | Circle | **Φ 31.75 mm (1 1/4")** | 38.1 mm stem below panel | **Yes** — ABS nut self-locks |

---

## Design Implications

### RP2040 LCD-0.99-B (33 mm circular cutout)

The module is extremely compact — 33 mm diameter, 9.8 mm total depth. A 33 mm circular through-hole in the front panel accommodates it. The 1.75 mm front chamfer of the CNC case sits against the panel face, providing a flush flush fit. The enclosure must provide a printed retention ring or clip behind the panel; a simple three-tab snap ring at ~32 mm inner diameter can hold the module in a 33 mm hole. The USB-C and SH1.0 connectors exit the side wall of the module at the bottom and left positions respectively — cable routing from these connectors runs laterally away from the module before bending back into the enclosure. Plan for at least 25 mm of lateral clearance behind the panel at the bottom and left of the RP2040 module position.

The vision calls for this module to be "as easily mounted to the wood panel in front of my sink as is the air switch." A 33 mm hole in a wood panel and a printed snap-ring adapter bracket behind it achieves this exactly. The module drops into the hole, the snap ring clips behind, and a retracting cable connects at the side.

### S3 CrowPanel 1.28" Rotary (47.3 mm / 48 mm cutout)

This module is substantially larger — 47.3 mm face diameter, 33.1 mm deep — because the rotary knob ring wraps the full circumference of the housing. The 33.1 mm total depth is the governing constraint for the enclosure front panel section: this is ~3.4× deeper than the RP2040, meaning the front panel wall must either be a deep pocket or the module must be recessed into the enclosure body. For flush mounting, the front panel needs a pocket at least 33.1 mm deep at the S3 position.

All cables exit the rear face of the PCB, making cable routing straightforward — cables go straight back into the enclosure with no lateral routing required.

The M2.5 mounting holes allow positive fastening to a printed bracket. The enclosure design should include a printed mounting bracket that captures the M2.5 holes and sandwiches the module against the panel from behind.

For external mounting (vision: user mounts on countertop or wall), a 47.3 mm circular hole or 48 mm square hole in any panel surface accepts the module. The M2.5 holes provide external mounting retention.

### KRAUS KWDA-100MB Air Switch (31.75 mm circular hole)

Standard 1 1/4" faucet/soap dispenser hole. This is an extremely common dimension — any countertop drill bit for soap dispensers produces exactly this hole. The switch self-mounts with its ABS lock nut; no printed retention feature is needed. The enclosure front panel needs a 31.75 mm (nominal) through-hole at the air switch position, and ~50 mm of clear depth behind the hole for the threaded stem + nut + tube fitting. The AC adapter box (140 mm × 73 mm × 48 mm) mounts elsewhere in the enclosure interior along the air tube.

The button cap (47.6 mm diameter) sits flush on the panel face. If the panel face is painted or finished, the 47.6 mm cap will cover the hole and ~8 mm of panel surface around it on each side.

For external mounting (vision: user mounts air switch on kitchen panel), the user drills a standard 1 1/4" hole and the switch self-installs identically to any sink application. No special bracket is needed.

---

## Concerns and Failure Modes

**RP2040 retention reliability:** The CNC case is smooth-sided with no retention features. A printed snap ring relying on FDM layer-to-layer adhesion for the snap hooks could crack under repeated insertion/removal cycles. Orient snap arms parallel to the build plate. Consider a twist-lock design (bayonet-style) rather than pure snap, since the module is cylindrical and rotation is natural.

**S3 depth conflict with enclosure wall:** 33.1 mm of module depth requires a thick front panel section or a recessed pocket. This is a significant spatial claim. The enclosure front panel at the S3 position will be a through-pocket, not a simple cutout. The front panel wall at that location must accommodate the full 33.1 mm depth without conflicting with internal components. Verify against the enclosure interior layout before finalizing panel thickness.

**S3 knob clearance:** The rotary knob ring (47.3 mm outer) needs to rotate freely. Any mounting bracket or panel cutout edge must have a radial clearance gap of at least 0.5 mm from the rotating aluminum ring. A 47.8 mm cutout diameter (47.3 + 0.5 mm clearance per side) is the minimum for free knob rotation.

**KRAUS tube routing:** The 60" (1524 mm) PVC air tube is long enough to reach the AC adapter box anywhere in the enclosure. The tube connects at the bottom of the threaded stem. If the air switch is mounted near the bottom of the front panel, the tube exits downward into the enclosure — favorable. If near the top, the tube must bend back up and over, requiring adequate radius clearance.

**Cable retraction for all three components:** The vision describes a "retracting 1m or 2m CAT6 cable." CAT6 cable (OD ~6–7 mm) has a minimum bend radius of approximately 25–35 mm. Any cable management channel or retract spool behind the front panel must accommodate this. The RP2040 uses SH1.0 and USB-C, which will require an adapter or purpose-built cable assembly. The S3 uses MX 1.25 mm connectors, likewise requiring a custom cable. The KRAUS uses its own PVC pneumatic tube (not a signal cable) — the pneumatic tube is flexible and requires no electrical connection, only pneumatic continuity.
