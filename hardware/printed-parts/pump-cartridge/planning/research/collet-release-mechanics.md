# John Guest Push-Fit Collet Release Mechanics

Research for pump cartridge release plate design. Focuses on the PP0408W 1/4" union fitting used in this project, but draws on general push-to-connect fitting engineering where JG-specific data is unavailable.

## 1. Internal Mechanism — How Push-Fit Collets Work

### Components (from tube entry inward)

A John Guest push-fit port has three functional elements arranged concentrically inside the acetal copolymer body:

1. **Collet (release sleeve):** The visible moving ring at the port face. Made of acetal copolymer. This is what the user (or release plate) pushes inward to release the tube. On the PP0408W: OD 9.57 mm, wall thickness 1.44 mm, ID 6.69 mm (caliper-verified).

2. **Gripper ring (stainless steel teeth):** A split ring of 301 stainless steel with inward-pointing teeth. The teeth are angled so they flex outward to allow tube insertion but bite into the tube OD when the tube is pulled. The collet sits over and constrains these teeth — when the collet is in its default (extended) position, the teeth are held in their gripping position against the tube. When the collet is pushed inward, it slides past the teeth and allows them to flex radially outward, releasing their grip.

3. **O-ring (EPDM):** Sits deeper inside the body, behind the gripper ring. Compressed between the fitting bore wall and the tube OD to create a static seal. The O-ring provides the leak-proof seal; the gripper ring provides the mechanical retention. These are independent functions — the O-ring does not contribute to tube retention, and the gripper does not contribute to sealing.

4. **Tube stop:** A fixed internal shoulder at the deepest point of the port. Defines the correct insertion depth. The tube must be pushed past the collet, past the gripper ring, past the O-ring, and against this stop to be fully seated.

### How Insertion Works

When a tube is pushed into the port:
- It enters through the collet bore (ID 6.69 mm vs tube OD 6.30 mm — 0.39 mm clearance).
- It encounters the gripper ring teeth, which flex outward momentarily to allow passage (the teeth are angled for one-way entry).
- It passes through the O-ring, which compresses around it forming the seal.
- It bottoms out against the tube stop.
- The user feels two distinct points of resistance: one at the gripper ring, one at the O-ring.
- Insertion requires firm hand pressure only — no tools.

### How the Grip Works

Once inserted, the gripper ring teeth bite inward against the tube OD. Any pull force on the tube causes the teeth to dig in harder (self-reinforcing wedge action). System pressure further reinforces the seal by pushing the O-ring tighter against the tube.

### How Release Works

To release a tube:
1. Push the collet inward (toward the fitting body), squarely against the port face.
2. The collet's inner bore slides over the gripper ring teeth, pushing them radially outward (away from the tube surface).
3. With the collet held in this depressed position, the tube can be pulled straight out.
4. Releasing the collet allows it to spring back to its default (extended) position, re-engaging the teeth.

The key mechanical principle: the collet acts as a camming sleeve. In its default position, it constrains the gripper teeth inward against the tube. When pushed inward, it releases that constraint by moving its bore past the teeth tips.

## 2. Release Force

### Collet Push Force (to depress the collet)

Manufacturer data for specific force values in newtons is not published by John Guest for the PP0408W or similar 1/4" fittings. However, the following can be established from multiple sources:

- **Designed for finger operation:** John Guest and all comparable push-to-connect fittings are explicitly designed so that collet release requires only finger pressure — no tools necessary. The PI-TOOL is a convenience aid, not a necessity.
- **Estimated force range: 5-15 N (1-3.5 lbf) for 1/4" fittings.** This estimate is based on:
  - The collet must overcome the spring-back force of the 301 stainless steel gripper ring teeth (thin stamped fingers, small elastic deflection).
  - For a 1/4" fitting, the gripper ring is very small (fits inside the 15.10 mm body end OD) with perhaps 4-8 teeth of very thin spring steel.
  - Users routinely depress these collets with a single thumb while simultaneously pulling the tube with the other hand.
  - The force is comparable to pressing a moderately stiff snap button.
- **Force scales with fitting size.** Larger fittings (3/8", 1/2") have proportionally more/larger teeth and require more force. The 1/4" size is at the low end.
- **No significant pressure dependency for release force.** The collet force opposes the gripper ring spring, not system pressure. However, system pressure on the tube creates a small axial force pushing the tube outward (pressure x tube cross-section area). At 150 psi on 1/4" tube: ~1.3 lbf (5.8 N). Best practice is to depressurize before disconnecting.

### Tube Pull-Out Force (without depressing collet)

When the collet is NOT depressed, the gripper teeth hold the tube with considerable force. Pull-out force without releasing the collet is destructive — it damages the tube surface and potentially the teeth. This force is much higher than the collet release force and is not the design operating mode.

## 3. Collet Travel (Stroke)

### Caliper-Verified Data (PP0408W)

From the project's own caliper measurements:

| Measurement | Value | Source |
|---|---|---|
| Overall length, collets extended | 41.80 mm | Photo 08 |
| Overall length, collets compressed | 39.13 mm | Photo 07 |
| Body length (without collets) | 36.32 mm | Calculated |
| **Total collet travel (both ends)** | **2.67 mm** | 41.80 - 39.13 |
| **Collet travel per side** | **~1.3 mm** | 2.67 / 2 |
| Collet protrusion when extended | ~2.74 mm per side | (41.80 - 36.32) / 2 |
| Collet protrusion when compressed | ~1.4 mm per side | (39.13 - 36.32) / 2 |

### Interpretation for Release Plate Design

- The release plate must push the collet inward by **~1.3 mm** to fully release the gripper teeth.
- The collet does not need to be pushed flush with the body — it still protrudes ~1.4 mm even when fully compressed.
- A release plate stroke of **2-3 mm** provides comfortable margin (the cartridge design specifies 3 mm cam lever travel, yielding ~1.7 mm of margin beyond the required 1.3 mm).
- The collet must be pushed **squarely** (perpendicular to the port face). Off-axis pressure risks damaging the collet or incomplete release. The release plate's stepped bore design (inner lip hugging the 9.57 mm collet OD) ensures axial alignment.

## 4. Geometry of the Collet Mechanism

### PP0408W Specific Dimensions (Caliper-Verified)

```
CROSS SECTION — ONE END OF PP0408W UNION
(rotationally symmetric about tube centerline)

                     ◄── 15.10 mm body end OD ──►

                     ┌─────────────────────────────┐
                     │         BODY WALL            │
                     │    (acetal copolymer)         │
    Tube             │  ┌───────────────────────┐   │
    entry  ──────────┤  │   GRIPPER RING        │   │
    face             │  │ (301 SS teeth,        │   │
                     │  │  inward-pointing)     │   │
         ┌──┐        │  │                       │   │
         │C │        │  │   ┌───────────┐       │   │
         │O │ 9.57mm │  │   │  O-RING   │       │   │  ◄── Tube
         │L │  OD    │  │   │  (EPDM)   │       │   │      stop
         │L │        │  │   └───────────┘       │   │
         │E │        │  │                       │   │
         │T │        │  └───────────────────────┘   │
         └──┘        │                              │
                     └─────────────────────────────┘

    ◄ 1.3mm ►
     travel           ◄─── 12.08 mm body end length ──►

    Collet wall: 1.44 mm
    Collet ID: 6.69 mm (tube 6.30 mm passes through with 0.39 mm clearance)
    Collet protrusion: 2.74 mm extended, 1.4 mm compressed
```

### Material Specifications

| Component | Material | Notes |
|---|---|---|
| Body | Acetal copolymer (Delrin-like) | White or gray, NSF 51/61 listed |
| Collet (release sleeve) | Acetal copolymer | Same material as body; may be blue on some variants |
| Gripper ring | 301 stainless steel | Spring-tempered, stamped teeth |
| O-ring | EPDM rubber | Standard for potable water; Nitrile available for OEM |
| Tube stop | Integral to body | Molded shoulder inside bore |

### Gripper Ring Teeth Geometry

The gripper ring is a split ring (not a continuous circle) of spring-tempered 301 stainless steel. Key characteristics:

- **Teeth angle inward** toward the tube centerline, creating a one-way ratchet effect: tubes slide in past the teeth but cannot pull back out.
- **Teeth are thin stamped fingers**, typically 4-8 per ring for 1/4" fittings, evenly spaced around the circumference.
- **Tooth tip engagement:** Each tooth tip digs into the tube OD surface. The grip is friction-based — the teeth do not cut into the tube material (the system is designed not to deform or restrict the tube).
- **Spring action:** When the collet is pushed inward, its bore slides past the teeth tips, allowing the teeth to flex radially outward (away from the tube). The teeth have enough spring tension to return to their gripping position when the collet releases.
- **The split in the ring** allows it to expand/contract slightly during assembly into the fitting body. It does not affect function during normal operation.

## 5. Tools and Products for Collet Release

### John Guest PI-TOOL

The official John Guest release tool. Dual-ended: 1/4" on one side, 3/8" on the other.

- **Release function:** A U-shaped or horseshoe-shaped plastic piece that slides over the tube and presses against the collet face, depressing it uniformly. The tool ensures the collet is pushed squarely, reducing the risk of damage.
- **Locking function:** The opposite end has a tapered edge that slides under the collet (between collet and body face), wedging the collet in its depressed position. This is a safety feature for transport — it prevents accidental tube release from vibration.
- **The PI-TOOL demonstrates that collet release is purely a matter of applying uniform axial force to the collet face.** No rotation, no special engagement geometry — just push inward, squarely.

### SharkBite Disconnect Clips

SharkBite (same parent company as John Guest — both RWC brands) uses a similar mechanism for larger fittings. Their disconnect clips are C-shaped plastic pieces that wrap around the pipe and push against the release collar. For 1/2" and larger fittings, a tong-style tool (like the IWISS CRQ01) provides leverage for the higher release forces of larger fittings.

### Implications for Automated/Plate-Based Release

The key insight from existing tools: **collet release requires only a flat surface pushing axially inward on the collet face.** There is no need for:
- Rotation
- Engagement teeth or hooks
- Precise angular alignment (beyond being roughly perpendicular)
- High force

A flat release plate with a bore sized between the tube OD (6.30 mm) and collet ID (6.69 mm) will contact the collet's annular end face and push it inward when the plate translates toward the fitting. This is exactly the approach used in the cartridge release plate design.

## 6. Failure Modes

### Tube Not Fully Seated

**The most common failure mode.** If the tube is not pushed past both the gripper ring and the O-ring to the tube stop:
- The O-ring may not be fully compressed around the tube, causing a slow leak.
- The gripper ring may have fewer teeth engaged, reducing pull-out resistance.
- Users report feeling "two grabs" during proper insertion — one at the gripper ring, one at the O-ring. Missing the second grab indicates incomplete insertion.
- **Mitigation:** Mark insertion depth on the tube before inserting. For 1/4" fittings, industry standard insertion depth is approximately 15-16 mm (to the tube stop). Verify by tugging the tube after insertion — it should not move.

### Damaged or Worn O-Ring

- **Chemical degradation:** Chloramines in treated water supply slowly erode EPDM O-rings. Develops as slow drip over months/years.
- **Mechanical damage from burrs:** If the tube end is not cut cleanly (square cut, no burrs), the tube edge can nick or slice the O-ring during insertion, causing an immediate or near-immediate leak.
- **Stress from angled tube:** If the tube exits the fitting at a sharp angle (not straight), it applies a side load that flattens the O-ring unevenly. Over time, the compressed side develops a permanent set and leaks.
- **Mitigation:** Clean square cuts (razor blade or tube cutter), no burrs, ensure tube is straight and not side-loaded at the fitting. O-rings are replaceable — the collet and gripper ring can be removed (pull collet out with fingers, no tools), O-ring extracted with a thin blade or toothpick, and a new O-ring pressed in.

### Collet Damage

- **Cracked collet:** If the acetal collet cracks (from impact, over-tightening, or chemical attack), the gripper ring loses its constraint and cannot hold the tube. Can cause undetected slow leaks or sudden tube ejection under pressure.
- **Collet jammed:** Debris or mineral deposits can prevent the collet from sliding smoothly. Release may require more force than normal or may be incomplete.
- **Off-axis release pressure:** Pushing the collet at an angle (not square to the port face) can cock it sideways in the bore, jamming it or causing uneven tooth release. The tube may appear released on one side but still be gripped on the other.
- **Mitigation:** Always push the collet squarely. Keep fittings clean and protected before installation (store in bags). The release plate's stepped bore design with collet-hugging inner lip prevents off-axis issues in the cartridge context.

### Gripper Ring Issues

- **Teeth worn smooth:** After many insertion/removal cycles, the tooth tips can dull. John Guest fittings are rated for reuse, but repeated cycling eventually degrades grip. Not a concern for the pump cartridge (replaced as a unit, not cycled frequently).
- **Ring displaced:** If the gripper ring shifts axially inside the body (from excessive force or incorrect reassembly after O-ring replacement), it may not align with the collet's camming action. Rare in normal use.

### Tube-Related Failures

- **Out-of-spec tube OD:** The fitting requires tube OD within tight tolerances (1/4" nominal = 6.35 mm, tolerance +0.001/-0.004 inches per JG spec = 6.325 to 6.375 mm). Undersized tube may not seal or grip properly. Oversized tube may not insert.
- **Tube surface damage:** Scratches, kinks, or flattened sections on the tube at the fitting engagement point reduce grip and may compromise the O-ring seal.

## 7. Design Implications for the Pump Cartridge Release Plate

Based on this research, the cartridge release plate design in `geometry-description.md` is sound:

1. **Stroke is adequate.** The 3 mm cam lever travel exceeds the 1.3 mm collet travel by 1.7 mm margin.
2. **Force is manageable.** Four 1/4" collets require an estimated 20-60 N total (4 x 5-15 N each), well within comfortable hand-squeeze range.
3. **Flat plate contact is correct.** The collet release mechanism requires only uniform axial pressure on the collet face — exactly what a translating flat plate provides.
4. **Stepped bore design is well-matched.** The tube clearance hole (between 6.30 and 6.69 mm) contacts the collet face; the inner lip (~9.6 mm) hugs the collet OD for alignment; the outer bore (~15.2 mm) clears the body end.
5. **No rotation or special tooling needed.** The release plate is a purely translating element.
6. **Square push is critical.** The plate must translate axially (parallel to tube/fitting axis). The collet-hugging bore ensures this alignment mechanically.
7. **Re-insertion is free.** When pushing the cartridge back into the dock, the tubes push into the fittings through the collets — no need to manipulate the collets. The release plate position is irrelevant for insertion.

### Risk Items for Prototyping

- **Verify collet release force empirically.** Build a test jig with a spring scale before committing to the cam lever ratio.
- **Verify that all 4 collets release simultaneously.** Manufacturing variation in fittings could cause one collet to be stiffer than others. The plate must maintain contact with all 4 collets throughout the stroke.
- **Test tube re-insertion force.** When the cartridge is pushed back into the dock, all 4 tubes must insert simultaneously. Any tube misalignment (even 1-2 mm lateral offset) could prevent insertion.
- **O-ring lubrication.** Dry O-rings increase insertion force. If tubes are stored dry for extended periods, a drop of silicone grease on the tube ends may help. Or design the tube stubs to remain inserted in the fitting body at all times (only one side of each union is connected to the cartridge — the other side stays in the dock).
