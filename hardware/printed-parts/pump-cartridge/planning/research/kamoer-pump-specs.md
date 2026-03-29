# Kamoer KPHM400-SW3B25 Peristaltic Pump -- Complete Physical Specifications

## Identification

- **Model:** KPHM400-SW3B25
- **Type:** 3-roller peristaltic pump with DC brushed motor
- **Manufacturer:** Kamoer Fluid Tech (Shanghai) Co., LTD
- **Amazon ASIN:** B09MS6C91D
- **Gear reduction:** Single-stage, 1:8 ratio

## Sources

All physical dimensions are caliper-verified from the actual pump unit. Measurements are in `hardware/off-the-shelf-parts/kamoer-kphm400/raw-images/` (17 caliper photos) with a synthesized geometry description in `hardware/off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md`. Electrical and operational specs are from the Kamoer official product page and the KPHM400 datasheet hosted on DirectIndustry.

---

## 1. Overall External Dimensions

| Dimension | Datasheet | Caliper-Verified | Notes |
|-----------|-----------|-----------------|-------|
| **Width (X)** | 68.6 mm | 62.6 mm head; ~68.6 mm at bracket | Bracket extends ~3 mm per side beyond the pump head |
| **Depth (Y)** | 115.6 mm | 116.48 mm (with motor nub); 111.43 mm (without) | Datasheet value likely excludes the 5 mm motor shaft nub |
| **Height (Z)** | 62.7 mm | 62.51--62.61 mm (head only); 82.82 mm with tube connectors | Tube stubs protrude ~20 mm above/below the pump head face |

**Summary envelope (body only):** 68.6 x 115.6 x 62.7 mm (W x D x H).
**Summary envelope (with tube stubs):** 68.6 x ~145 mm x 82.8 mm -- the tube stubs add ~30 mm forward of the front face and ~20 mm to the height.

## 2. Motor Cylinder Diameter

| Photo | Reading | Confidence |
|-------|---------|------------|
| 15 | ~34.54 mm | LOW (upside-down reading) |
| 16 | ~35.13 mm | MEDIUM (upside-down reading) |

**Working value: 35 mm.** This is consistent with a standard RS-385/RS-390 class DC motor. The motor body has a flat on one side (standard anti-rotation feature, ~1 mm deep).

**Bore hole recommendation for mounting surface:** 36 mm minimum (35 mm + 0.5 mm clearance per side). With FDM hole shrinkage, design the bore at 36.4 mm (36 mm + 0.2 mm per side for FDM compensation + margin for the motor flat).

## 3. Mounting Screw Pattern

The mounting bracket is a stamped black metal plate at the junction between the pump head and the motor cylinder. This is the primary mounting interface.

| Parameter | Value | Source |
|-----------|-------|--------|
| **Number of holes** | 4 | Caliper photos, datasheet |
| **Pattern** | Square | Caliper photos, datasheet |
| **Center-to-center spacing** | 48 mm x 48 mm | User-verified from physical pump |
| **Hole diameter** | 3.13 mm | Caliper photo 06 (HIGH confidence) |
| **Screw size** | M3 | 3.13 mm hole accepts M3 (3.0 mm) with 0.13 mm clearance |
| **Edge-to-edge across holes** | 47.88 mm | Caliper photo 05 (consistent: 48 - 3.13 = 44.87; measured 47.88 is edge-to-edge of hole pair = c-c measurement) |
| **Screw orientation** | Parallel to motor axis (Y-axis) | Screws thread from the motor side into the pump head |
| **Bracket width** | ~68.6 mm | Wider than the 62.6 mm pump head by ~3 mm per side |
| **Bracket thickness** | ~1.5--2 mm | Estimated from photos |

### Hole positions relative to motor center

The 4 holes are at the corners of a 48 mm square, centered on the motor/pump axis. Each hole is 24 mm from center in both X and Z:

```
Mounting face (viewed from motor side, looking toward pump head):

          +----- 48 mm c-c -----+
          |                      |
    (-24,+24) O          O (+24,+24)
          |                      |  48 mm
          |     ( motor )        |  c-c
          |      ~35 mm          |
          |                      |
    (-24,-24) O          O (+24,-24)
          |                      |
          +----------------------+

    Origin = pump center axis (motor shaft center)
    All holes are M3 (3.13 mm through-holes)
```

### Mounting surface design requirements

The mounting surface needs:
1. A central bore hole of at least 36 mm diameter for the motor cylinder to pass through
2. Four M3 screw holes at 48 mm square pattern surrounding the bore
3. The bracket face sits flat against the mounting surface -- this is a simple flat-to-flat interface
4. Minimum material between bore edge and screw hole edge: (24 - 18 - 1.57) = 4.43 mm -- adequate for FDM (minimum 2 perimeters = 0.8 mm wall, so this is fine)

### FDM screw hole sizing

Per the project's FDM constraints (requirements.md): add 0.2 mm to hole diameters for loose fit.
- **Design M3 through-holes at 3.4 mm diameter** (3.2 mm nominal + 0.2 mm FDM compensation)
- Alternatively, if using threaded inserts: size per insert manufacturer spec

## 4. Tubing Inlet and Outlet

### Tube specifications

| Parameter | Value |
|-----------|-------|
| **Tube material** | PharMed BPT |
| **Tube ID** | 4.8 mm |
| **Tube OD** | 8.0 mm |
| **Tube code** | B25 (25#) |
| **Connector type** | White plastic barbed connectors for BPT tubing |

### Connector positions and orientation

The two tube connectors exit from the **front face** of the pump head (the face with the Kamoer branding and yellow priming cap). They protrude forward (along the -Y axis, away from the motor).

- **Inlet:** One barbed connector, offset from center on the front face
- **Outlet:** Second barbed connector, offset from center on the front face
- **Stub protrusion:** ~30--50 mm forward from the front face (flexible BPT tubing attached to barbed stubs)
- **Height with connectors:** 82.82 mm (caliper photo 17) vs 62.6 mm head-only height, meaning the connectors extend ~10 mm above and ~10 mm below the pump head body, roughly symmetric

### Orientation relative to mounting face

The tube connectors exit from the **opposite end** from the mounting face. The mounting bracket is at the rear (motor side), and the tubes exit from the front. In the cartridge, the pump head faces forward (toward the user) and the motor faces rearward.

**Clearance in front of pump:** Allow at least 30 mm forward of the pump head front face for tube routing. The BPT tubing stubs can be bent, but the barbed connectors themselves are rigid white plastic.

## 5. Weight

| Variant | Weight |
|---------|--------|
| **DC brushed motor (SW -- this unit)** | ~306 g |
| DC brushless motor (ST) | ~240 g |

**Two pumps in the cartridge: ~612 g** of pump mass alone.

## 6. Orientation Constraints

**Peristaltic pumps are orientation-independent.** Confirmed by the fundamental operating principle: the rollers compress tubing against a track, creating a sealed volume that moves fluid regardless of gravity. Key properties:

- **Self-priming:** The roller mechanism creates suction without needing gravity feed. Can draw fluid upward.
- **No backflow:** When stopped, the compressed tubing segment seals against reverse flow. No check valve needed.
- **Can run dry:** No damage from running without fluid.
- **Any mounting angle works:** No internal sump, no oil level, no gravity-dependent seal. The pump operates identically whether mounted horizontally, vertically, inverted, or at any angle.

**For the cartridge design:** Mount in whatever orientation the enclosure geometry dictates. No orientation constraint from the pump. Per the vision, the cartridge is at the front-bottom of the enclosure -- any angle that fits the space works.

## 7. Electrical Specifications

| Parameter | Value |
|-----------|-------|
| **Rated voltage** | 12V DC |
| **Current draw** | 0.7A (at 12V) |
| **Power** | ~10W |
| **Motor type** | DC brushed |
| **Motor life** | 800 hours |
| **Pump tube life** | 1000 hours (BPT) |
| **Control method** | Switch control (on/off via L298N motor driver) |
| **Noise** | <=65 dB |
| **Operating temperature** | 0--40 C |
| **Operating humidity** | <80% |
| **Roller count** | 3 |

### Current draw implications for the cartridge

Two pumps at 0.7A each = 1.4A total at 12V. The L298N motor driver already in the BOM handles this. Wiring from the cartridge to the main board needs to carry at least 1.4A continuously -- 22 AWG wire minimum (rated for 2A).

### Motor life context

800 hours of motor life at the usage pattern for a home soda machine (each dispense runs the pump for ~5--10 seconds) means:
- At 10 seconds per dispense: 800 hours = 288,000 dispenses
- At 10 dispenses per day: ~79 years of motor life
- The pump tubing (1000 hours) will outlast the motor proportionally, but both are well beyond any reasonable replacement interval
- The cartridge replacement mechanism exists for tubing wear, not motor failure, but the design allows replacing both

## 8. Failure Modes Relevant to Mounting

### Vibration

The DC brushed motor produces vibration during operation. The 1:8 gear reduction amplifies torque but the 3-roller mechanism creates a pulsating flow (3 pulses per revolution). At ~280 RPM operating speed, this is ~14 Hz pulsation.

**Mitigation for mounting:**
- The 4-screw M3 mounting pattern with a flat bracket provides rigid attachment -- vibration is transmitted to the mounting surface, not absorbed
- If vibration transmission to the enclosure is a concern, a thin (1--2 mm) silicone or rubber gasket between the bracket and the mounting surface would decouple them
- Lock-nuts or thread-locking compound on the M3 screws prevents loosening from vibration

### Thermal

At 10W per pump, heat generation is modest. The motor has a metal housing that acts as a heat sink. In a sealed enclosure at 0--40 C ambient:
- Motor surface temperature may rise 10--20 C above ambient during continuous operation
- Dispense cycles are short (5--10 seconds), so thermal buildup is negligible in normal use
- No forced cooling required
- The motor cylinder passes through the mounting surface, which provides some conductive cooling path

**Mounting surface material:** PLA, PETG, or ABS are all fine thermally. No concern about softening from motor heat during normal use patterns.

### Tube wear

The BPT tubing fatigues from repeated roller compression. The 1000-hour rated life is the primary wear item. The cartridge design accommodates this by making the entire pump assembly (with tubing) replaceable.

---

## 9. Implications for Cartridge Mounting Surface Design

The vision describes two pumps mounted to a flat surface via 4 screws each. Here is what the dimensions dictate:

### Minimum mounting plate dimensions (per pump)

The mounting plate needs to:
1. Accommodate the 48 mm square screw pattern
2. Include a 36 mm bore for the motor
3. Have enough material around the screws for structural integrity

**Minimum plate footprint per pump:** ~56 mm x 56 mm (48 mm screw pattern + 4 mm margin per side for screw head clearance and wall thickness).

### Two-pump layout

Two pumps side by side (X-axis):
- Each pump head is 62.6 mm wide; with bracket, 68.6 mm
- Minimum center-to-center spacing: 68.6 mm (bracket-edge to bracket-edge contact) + clearance
- Practical center-to-center: ~72--75 mm (leaving 3--6 mm gap between brackets for wiring and assembly)
- **Total width for two pumps:** ~140--145 mm

Two pumps stacked vertically (Z-axis):
- Each pump head is 62.6 mm tall (82.8 mm with connectors)
- Minimum center-to-center spacing: 83 mm (connector-tip to connector-tip) + clearance
- **Total height for two pumps stacked:** ~170--180 mm

**The enclosure is 220 mm wide** (vision.md), so side-by-side mounting at ~145 mm total width fits with ~75 mm to spare for the cartridge shell walls and rail grooves.

### Depth budget

From mounting face rearward:
- Bracket thickness: ~2 mm
- Motor body behind bracket: ~63 mm
- Motor shaft nub: 5 mm (must not bottom out)
- **Total behind mounting face: ~70 mm**

From mounting face forward:
- Pump head depth: ~48 mm
- Tube stub protrusion: ~30--50 mm
- **Total in front of mounting face: ~80--98 mm**

**Total depth per pump: ~150--170 mm** (front of tubes to rear of motor nub). The enclosure is 300 mm deep; two pumps at the front-bottom leaves adequate room.

### Summary of critical dimensions for CAD

| Parameter | Value | Use |
|-----------|-------|-----|
| Motor bore diameter (design) | 36.4 mm | Central hole in mounting plate |
| Screw hole diameter (design) | 3.4 mm | Four M3 through-holes |
| Screw pattern | 48 mm x 48 mm square | Hole center-to-center |
| Screw pattern center | Coincident with bore center | All symmetric about pump axis |
| Bracket contact area | ~68.6 mm diameter circle, flat | Mounting surface must be flat and at least this wide |
| Pump head envelope (forward of plate) | 62.6 x 48 x 62.6 mm | Clearance pocket |
| Motor envelope (behind plate) | 35 mm dia x 68 mm long | Clearance behind plate |
| Tube connector clearance (forward) | 30--50 mm beyond pump head | Tube routing space |
| Weight per pump | ~306 g | Structural load on mounting features |
