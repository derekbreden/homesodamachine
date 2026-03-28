# Dock Alignment Research: Pump Cartridge Blind Fluid Connection

## Problem Statement

The pump cartridge (~130x70x120mm, containing 2 Kamoer KPHM400 peristaltic pumps) slides into a dock in the enclosure and must simultaneously mate with 4 tube stubs (1/4" OD, 6.35mm) protruding from the enclosure's rear wall. Each tube stub inserts into a John Guest PP0408W union fitting mounted in the cartridge's rear face. The collet ID is 6.69mm, giving only **0.17mm radial clearance per side** between each tube (6.35mm OD) and the collet bore (6.69mm ID).

This document investigates how to achieve reliable blind alignment for this connection.

---

## 1. Self-Aligning Cartridge Docking Mechanisms

### 1.1 Rail/Groove Systems (Drawer-Slide Principle)

**How it works:** The cartridge rides on parallel rails or in a channel that constrains 4 of 6 degrees of freedom (lateral X, vertical Z, roll, yaw), leaving only the insertion axis (Y) and pitch free. Progressive engagement narrows any remaining play as the cartridge advances.

**Real-world examples:**
- **Coca-Cola Freestyle cartridge trays:** Ingredient cartridges slide on guided trays into the dispenser cabinet, mating with O-ring-sealed fluid ports. The tray rail constrains lateral position; the cartridge seats against a datum face at full insertion. (Source: Coca-Cola CrewConnect technical documentation)
- **PCIe card slots:** Cards ride in a rail/groove that constrains lateral position, with a latch at the rear that confirms full engagement. The rail provides progressive alignment over ~90mm of travel before the edge connector engages.
- **Drawer slides:** Typical ball-bearing drawer slides provide lateral constraint with ~0.5mm total side-to-side play, narrowing as the drawer reaches full extension/closure.

**Applicable design pattern for our cartridge:**
- Two parallel rails (one on each side wall of the dock) running the full ~120mm depth of the cartridge
- The rail cross-section is a C-channel or dovetail that captures the cartridge edges
- Over the first ~80mm of insertion, the cartridge is guided but has no fluid connections
- The final ~40mm of travel drives the tube stubs into the John Guest fittings

**Key dimensional guidance (FACT from drawer slide industry):** Drawer slides typically require 12.7mm (1/2") side clearance per side. For our tighter application, a rail/groove with 0.2-0.3mm clearance per side (achievable with FDM at 0.1mm layer height) provides adequate constraint without binding.

### 1.2 Lead-In Tapers / Chamfered Funnels

**How it works:** An oversized opening at the dock entrance funnels the cartridge toward center as it's pushed in. The taper progressively narrows, transitioning from coarse alignment (several mm tolerance) to fine alignment (<0.2mm) at the point of connection.

**Real-world examples:**
- **Blind-mate connectors (TE Connectivity Micro MATE-N-LOK):** Feature a lead-in funnel structure that provides a large entry area and tapers to center, compensating for operator misalignment. (Source: TE Connectivity product documentation)
- **Die-making pilots:** A bullet-nose taper on the pilot enters a pre-punched hole and cams the workpiece into alignment as the press descends. The taper angle is typically 15-30 degrees (half-angle). (Source: toolmakingandmachining.com)
- **Inkjet cartridge guide features:** HP/Epson cartridges use tapered openings that progressively narrow, guiding the cartridge into precise position before fluid needle insertion. (Source: US Patent US20130155156A1)

**Applicable design pattern:** A pair of tapered lead-in guides on the dock's rear wall, surrounding each pair of tube stubs. The outer mouth is 5-8mm wider than the cartridge feature it captures; the taper narrows to final position over 15-20mm of depth.

**Taper angle guidance (ESTIMATE):** A 15-degree half-angle taper over 15mm of depth provides ~4mm of initial lateral capture range, narrowing to near-zero at the datum. This matches die pilot practice and blind-mate connector conventions.

### 1.3 Kinematic Coupling Principles

**How it works:** Three contact points in V-grooves constrain exactly 6 degrees of freedom. This is the gold standard for sub-micron repeatability in precision engineering.

**Performance (FACT):** Three-ball/three-groove kinematic couplings achieve repeatability below 1 micrometer. Quasi-kinematic variants achieve ~0.25 micrometer. (Source: MIT Precision Engineering Research Group, Slocum et al.)

**Applicability to our design:** Full kinematic coupling is overkill for our 0.17mm tolerance. However, the principle of **progressive constraint** applies:
- First contact: rails constrain 4 DOF (X, Z, roll, yaw)
- Second contact: rear wall datum constrains Y (depth)
- Third contact: tapered alignment features constrain remaining pitch

This is a **quasi-kinematic** approach: the rails provide overconstrained but compliant guidance, while the final alignment features provide precision location.

### 1.4 Registration Bosses (Pilot Before Engage)

**How it works:** Large, coarse-tolerance features engage first and position the cartridge before the fine-tolerance fluid connections are attempted. The registration feature is always longer than the fluid connection stubs.

**Real-world examples:**
- **Inkjet cartridge sequencing (FACT from US20130155156A1):** The patent explicitly describes a staged engagement sequence: (1) T-rail guide engages first, constraining motion to a single axis with ~3mm tolerance; (2) tapered fluid pen/socket pairs engage next with 3-5mm insertion depth; (3) electrical contacts engage last, sunken below the face so they only touch after fluid connections are secure.
- **Water filter cartridges (FACT):** Code 8 filter cartridges include a conical fin tip that enters the housing first, centering the cartridge before the O-ring seal engages. (Source: econefiltration.com)
- **Locating pins in manufacturing (FACT):** Pilot pins with bullet noses are standard practice. The pin enters the workpiece hole and cams the part into position before the full-diameter section engages. (Source: Carrlane engineering reference)

**Applicable design pattern for our cartridge:**
- Two registration bosses (tapered cylinders, ~10mm diameter, ~15mm long) on the dock's rear wall, positioned at diagonally opposite corners
- Corresponding tapered holes in the cartridge's rear face
- These bosses are 10-15mm longer than the tube stubs, so they engage and align the cartridge BEFORE any tube touches a fitting
- The bosses narrow from ~12mm entry diameter to ~10mm at the base, providing ~1mm centering range per boss

---

## 2. Blind Fluid Connection Strategies

### 2.1 Bag-in-Box (BIB) Beverage Connectors

**How it works:** BIB connectors use a QCD (Quick Connect/Disconnect) mechanism. A slide-on connector with a 3/8" barbed stem mates with a port on the syrup bag. The connector has a keyed profile that only accepts the correct orientation.

**Alignment method:** BIB connectors are NOT blind-mate in the same sense as our application. The operator visually aligns the connector and pushes it onto the bag port. However, the Coca-Cola Freestyle system DOES make blind connections: ingredient cartridges slide into guided trays and mate with O-ring-sealed ports at the rear of the tray slot. The tray rail provides alignment. (Source: Coca-Cola CrewConnect documentation)

**Relevant takeaway:** O-ring sealed stub-into-socket is the standard approach for blind beverage connections. The seal is forgiving of minor angular misalignment because the O-ring compresses radially.

### 2.2 Water Filter Cartridges (Push-In and Twist-Lock)

**How it works:** Under-sink water filter cartridges insert vertically into a filter head. The cartridge has an O-ring-sealed port at the top that mates with a corresponding socket in the head. A centering post in the head enters a recess in the cartridge top to guide alignment.

**Key design features (FACT from multiple sources):**
- **Centering post:** The filter head contains a centering post that enters a recess in the cartridge. One manufacturer's tip: insert a short piece of 1/2" ID x 3/4" OD PVC hose into the centering post to extend it below the head, making it easier to align the cartridge before the threads or O-ring engage. (Source: Boshart filter support)
- **O-ring groove:** The O-ring sits in a groove on the cartridge (not the housing), so it's captive and can't fall out during installation.
- **Push-in Type 222 seals:** Double O-rings seat into a matching socket, providing a push-in seal. The socket has a slight chamfer to guide the O-ring in.
- **Twist-lock Type 226:** Double gaskets with locking fins. The rotational compression provides positive engagement feedback. (Source: rfsolutions.it, viomi.com)

**Relevant takeaway:** A centering post that is longer than the fluid connection stub is the standard technique for guiding blind fluid connections in consumer filter products. This is exactly the "pilot before engage" strategy described in Section 1.4.

### 2.3 Medical IV Pump Cassettes

**How it works:** Medical infusion pump cassettes (e.g., ICU Medical Plum 360) are single-use cartridges that slide/snap into the pump body, making multiple fluid connections (inlet, outlet, sensor ports) simultaneously. The cassette is shaped to only fit one way (keyed).

**Alignment features:** The cassette body has rails/ribs that engage channels in the pump housing. The cassette is inserted with a downward hinge-and-snap motion that progressively engages the fluid interfaces. Auto-priming is handled by the pump after cassette insertion. (Source: ICU Medical Plum 360 documentation)

**Relevant takeaway:** Medical cassettes demonstrate that multiple simultaneous blind fluid connections are standard practice, achieved through keyed shapes + rail guidance + progressive engagement. The tolerances are managed by molding (injection-molded cassettes are held to tighter tolerances than FDM printing).

### 2.4 Inkjet Printer Cartridges

**How it works:** Inkjet cartridges make both fluid (ink supply needle) and electrical connections blind. The cartridge slides into a carriage that constrains it, and a latch locks it into final position.

**Alignment sequence (FACT from US Patent US20130155156A1):**
1. **T-rail guide** engages first, constraining motion to a single insertion axis. The rail has a tapered opening for easy reception. Tolerance: ~3mm perpendicular to insertion axis, ~3 degrees rotation.
2. **Fluid connections** engage next via tapered pen/socket pairs. Insertion depth: 3-5mm minimum.
3. **Electrical contacts** engage last. The circuit is "sunken with respect to the front face" so that contact only occurs after fluid connections are secure.

**Relevant takeaway:** The staged-engagement principle is well-proven. Guide features first, fluid connections second, and the most sensitive connections (electrical) last. The 3mm lateral tolerance at the guide stage is generous compared to our 0.17mm fitting tolerance, but the guides narrow that down before the fluid connections are attempted.

---

## 3. Tube-Into-Fitting Alignment Aids

### 3.1 Chamfered Tube Ends

**How it works:** A chamfer on the tube end creates a lead-in that helps the tube find the fitting bore even with slight misalignment.

**Standard practice (FACT):** Copper push-connect fitting instructions specify that the tube end should be deburred and chamfered for smooth insertion. The tube should be aligned straight with the fitting and inserted with a firm pushing and twisting motion. (Source: Copper Development Association, copper.org)

**For our application:** A 30-45 degree chamfer on the last 1-2mm of each 1/4" tube stub would increase the effective entry target from 6.69mm (collet ID) to approximately 8-9mm at the chamfer tip, significantly relaxing alignment requirements.

**Dimensional impact (ESTIMATE):** A 1.5mm x 45-degree chamfer on a 6.35mm tube creates an effective entry point of 6.35 - 2(1.5) = 3.35mm tip diameter, which can enter a 6.69mm bore with up to ~1.67mm radial offset. This is a massive improvement over the 0.17mm bare-tube clearance.

### 3.2 Funnel-Shaped Entry Guides Around Each Fitting

**How it works:** A conical or bell-shaped funnel is printed around each John Guest fitting port in the cartridge's rear face. The funnel's wide mouth captures the tube stub and guides it into the collet bore.

**Design parameters (ESTIMATE based on chamfer + taper principles):**
- Funnel mouth diameter: 12-15mm (provides 3-4mm capture radius around the 6.69mm bore)
- Funnel depth: 8-10mm (provides progressive narrowing before tube reaches collet)
- Taper half-angle: 15-20 degrees
- Funnel exit diameter: 6.69mm (matches collet ID exactly)

**Combined with tube chamfer:** The funnel mouth captures a misaligned tube, the taper centers it, and the tube chamfer provides final alignment into the collet bore. Together, these provide several millimeters of misalignment tolerance rather than 0.17mm.

### 3.3 Registration Bosses That Position Before Tubes Engage

This is the critical design strategy. Detailed in Section 1.4 above.

**Specific implementation for our cartridge:**
- Two tapered registration bosses on the dock's rear wall, positioned at diagonally opposite corners of the 4-fitting pattern
- Boss dimensions: 10mm nominal diameter, 15mm long, with a 3mm lead-in taper at the tip
- Corresponding tapered sockets in the cartridge rear face: 10mm nominal bore, 15mm deep
- The bosses protrude 10-15mm farther from the rear wall than the tube stubs
- When the bosses are fully seated, the cartridge is positioned within ~0.1-0.2mm of nominal (limited by FDM tolerance, not the design)
- Only then do the tube stubs begin entering the fitting funnels

### 3.4 Compliance / Spring-Loading

**How it works:** Instead of demanding perfect rigid alignment, one side (usually the mating connector, not the cartridge) floats on springs or flexures, allowing it to self-center as the connection is made.

**Real-world examples:**
- **Staubli CGO blind-mate fluid couplings (FACT):** Use "oscillation technology" to compensate for misalignment up to 0.5mm between axes (double oscillation) or 0.25mm (single oscillation). The coupling half floats within its housing. (Source: Staubli product specifications)
- **RAD pneumatic compliance devices (FACT):** Provide allowances for both lateral and rotational misalignment, allowing parts to automatically align upon striking a lead-in chamfer. (Source: RAD-RA compliance device documentation)

**Applicability to our design:** The tube stubs protruding from the dock's rear wall could be mounted on a slightly compliant base (e.g., flexible 3D-printed mounts, or simply relying on the inherent flexibility of 1/4" polyethylene tubing). However, since we're using rigid tube stubs inserted into John Guest fittings, compliance is limited. The better strategy is to get the alignment right through guides and funnels rather than relying on compliance.

**Alternative compliance approach:** The John Guest fittings themselves could be mounted in slightly oversized bores in the cartridge rear wall (e.g., 9.5mm bore for the 9.31mm center body gives 0.1mm radial float). This allows each fitting to self-center on its tube stub as the cartridge seats. This is a **recommended strategy** that works with, not against, the existing part geometry.

---

## 4. Tolerance Analysis

### 4.1 The Alignment Budget

**Given dimensions (FACT, caliper-verified):**
- Tube OD: 6.35mm (nominal, 6.30mm measured)
- John Guest collet ID: 6.69mm (derived from caliper measurements)
- Radial clearance per tube: (6.69 - 6.35) / 2 = **0.17mm per side**
- With measured tube: (6.69 - 6.30) / 2 = **0.195mm per side**

### 4.2 Angular Misalignment from Fitting Spacing

**Assumed fitting pattern:** 4 fittings in a rectangular pattern, approximately 50mm x 40mm (2 fittings per pump, 2 pumps side by side).

**Worst-case angular analysis:** If the cartridge is perfectly positioned at one fitting but angularly misaligned, the farthest fitting sees the largest offset.

For fittings spaced D mm apart, and an angular misalignment of theta radians about the center:
- Maximum radial offset at farthest fitting = (D/2) * sin(theta) approximately = (D/2) * theta for small angles

The maximum diagonal distance between fittings is approximately sqrt(50^2 + 40^2) = 64mm. The farthest fitting from the rotation center is at half the diagonal = 32mm.

**To keep radial offset below 0.17mm at the farthest fitting:**
- theta_max = 0.17mm / 32mm = 0.0053 radians = **0.30 degrees**

**This is extremely tight.** A third of a degree of angular misalignment consumes the entire radial clearance budget. This confirms that bare tubes into bare fitting bores is not viable without alignment aids.

### 4.3 With Alignment Aids (Funnels + Chamfers)

**With tube chamfers (1.5mm x 45 degrees) and entry funnels (12mm mouth, 8mm depth, 15 degree taper):**
- Effective capture radius per fitting: ~3mm (from funnel mouth to collet centerline)
- The funnel can correct up to 3mm of radial misalignment per fitting
- Angular tolerance becomes: theta_max = 3mm / 32mm = 0.094 radians = **5.4 degrees**

This is very comfortable and well within the capability of rail guides.

### 4.4 FDM Printing Tolerance

**FDM dimensional accuracy (FACT from multiple sources):**
- Typical FDM tolerance: +/-0.15mm to +/-0.3mm per feature
- With well-calibrated Bambu H2C at 0.1mm layer height: +/-0.1mm achievable
- Snap-fit clearance recommendation for FDM: 0.3-0.5mm

**Tolerance stack-up for rail-guided cartridge:**
- Rail-to-rail spacing on dock: nominal +/- 0.2mm
- Cartridge width at rail engagement: nominal +/- 0.2mm
- Worst-case lateral misalignment from rail fit: 0.4mm (RSS: 0.28mm)
- Registration boss-to-socket fit: nominal +/- 0.15mm per feature
- Worst-case lateral misalignment after boss engagement: 0.3mm (RSS: 0.21mm)

**Conclusion:** Rail guides alone get the cartridge within ~0.3-0.4mm. Registration bosses narrow that to ~0.2-0.3mm. Entry funnels with 3mm capture radius handle the remaining misalignment with ample margin.

### 4.5 Alignment Budget Summary

| Stage | Lateral Accuracy | Mechanism |
|-------|-----------------|-----------|
| No alignment (hand-placed) | ~5-10mm | User just pushing in general direction |
| Rail guides engaged | ~0.3-0.5mm | Parallel C-channel rails constrain X, Z |
| Registration bosses seated | ~0.15-0.3mm | Tapered pilot bosses fine-align |
| Funnel mouth captures tube | up to 3mm capture | 12mm funnels around each fitting bore |
| Tube chamfer enters collet | up to 1.5mm capture | 45-degree chamfer on tube ends |
| Tube fully seated in fitting | 0.17mm clearance | John Guest collet grips tube |

**The alignment chain is:** Rails (coarse) then Bosses (medium) then Funnels (fine) then Chamfer (final). Each stage works within the capture range of the next. The total system can absorb initial misalignment of ~5-10mm (hand placement accuracy) and reduce it to the 0.17mm required at connection.

---

## 5. Recommended Approach

Based on this research, the recommended dock alignment strategy is a **4-stage progressive alignment system:**

### Stage 1: Rail Guides (Coarse Alignment)
- Two parallel C-channel rails on the dock side walls
- Rails are the full ~120mm depth of the insertion path
- Constrain X (lateral), Z (vertical), roll, and yaw
- Entry is flared/chamfered for easy cartridge insertion
- Rail-to-cartridge clearance: 0.3-0.5mm per side (FDM tolerance)
- Gets cartridge within ~0.5mm of nominal position

### Stage 2: Registration Bosses (Fine Alignment)
- Two tapered cylindrical bosses on the dock's rear wall
- Positioned at diagonally opposite corners of the fitting pattern
- Boss length: 15-20mm (protrude 10-15mm farther than tube stubs)
- Engage BEFORE tubes reach fittings
- Taper: 3mm lead-in narrowing to 10mm nominal diameter
- Gets cartridge within ~0.2mm of nominal position

### Stage 3: Entry Funnels (Fitting-Level Alignment)
- Conical funnels printed into the cartridge's rear face around each John Guest fitting port
- Mouth diameter: 12-15mm
- Depth: 8-10mm
- Taper half-angle: 15-20 degrees
- Provides ~3mm capture radius per fitting
- Centers each tube stub toward the collet bore

### Stage 4: Tube Chamfers (Final Entry)
- 30-45 degree chamfer on the last 1-2mm of each tube stub
- Reduces effective tip diameter to ~3-4mm
- Provides final centering as tube enters the 6.69mm collet bore

### Fitting Mounting Strategy
- John Guest fittings press-fit into cartridge rear wall via center body (9.31mm OD in ~9.5mm bore)
- The 15.10mm body end sections protrude on both sides of the rear wall
- Slight clearance in the bore (0.1mm radial) allows each fitting to self-center on its tube stub, providing an additional compliance mechanism

---

## 6. Failure Modes and Concerns

### 6.1 Tube Stub Buckling
If a tube stub hits the side of a funnel instead of entering cleanly, the insertion force could bend the tube. **Mitigation:** Keep tube stubs short (~15-20mm protrusion) to maximize buckling resistance. Use 1/4" hard polyethylene tubing, not soft silicone, for the stubs.

### 6.2 FDM Dimensional Drift
Bambu H2C prints may drift over large parts. The 4 fitting bores in the cartridge's rear wall and the 4 tube stubs in the dock wall are on separate printed parts, and their relative spacing must match within the funnel capture radius. **Mitigation:** Print the rear wall portion of both parts in the same orientation (flat on the bed), and keep the fitting pattern compact (~50x40mm) to minimize drift.

### 6.3 Repeated Insertion Wear
FDM plastic rails will wear over many insertion/removal cycles. **Mitigation:** Use PETG or ABS for the dock rails (higher wear resistance than PLA). Consider printing rails in the XY plane so layer lines are parallel to the sliding direction.

### 6.4 Collet Damage
If a tube enters at a significant angle, it could damage the John Guest collet mechanism. **Mitigation:** The funnel + chamfer system ensures the tube enters near-axially. The funnels should be long enough (8-10mm) that the tube is well-aligned before it contacts the collet.

### 6.5 Four-Fitting Synchronization
All 4 tubes must enter their fittings approximately simultaneously. If one enters early and locks, the cartridge can't be adjusted for the remaining three. **Mitigation:** Tube stubs should all protrude the same length (+/-0.5mm). The funnel capture radius (3mm) is large enough to handle the positional tolerance of the remaining fittings even if one is slightly biased.

---

## 7. Sources

- Staubli CGO self-aligning blind-mate fluid couplings: https://www.staubli.com/us/en/fluid-connectors/products/quick-and-dry-disconnect-couplings/thermal-management/cgo-self-aligning.html
- US Patent US20130155156A1 (HP fluid cartridge alignment): https://patents.google.com/patent/US20130155156
- TE Connectivity Micro MATE-N-LOK blind-mate connector: https://www.te.com/content/dam/te-com/documents/appliances/global/micro-mate-n-lok-blind-mate-connector-flyer-en.pdf
- MIT Kinematic Coupling Design: http://pergatory.mit.edu/kinematiccouplings/documents/theses/hart_thesis/chapter2.pdf
- Slocum, A. "Kinematic couplings: A review of design principles and applications": https://dspace.mit.edu/bitstream/handle/1721.1/69013/Kinematic%20coupling%20review%20article.pdf
- Coca-Cola Freestyle cartridge management: https://crewconnect.coca-cola.com/wp-content/uploads/2019/05/CCFS-CartridgeManagement-Quick-Tip-1.pdf
- Copper Development Association push-connect joints: https://copper.org/applications/plumbing/cth/push-connect/cth_12push_install.php
- Water filter cartridge twist vs push-in designs: https://water.viomi.com/blogs/hydration-lab/fast-cartridge-change-twist-vs-push-in
- Filter cartridge end cap alignment (Code 8 conical fin): https://econefiltration.com/how-to-choose-filter-cartridge-end-caps/
- Boshart filter cartridge alignment tips: https://support.boshart.com/filter-cartridge-alignment-tips-tricks
- RAD compliance devices: https://rad-ra.com/rad-home/compliance-devices/compliance-devices-pneumatic/
- 3D printing snap-fit tolerance guidelines: https://www.hubs.com/knowledge-base/how-design-snap-fit-joints-3d-printing/
- FDM tolerance reference: https://formlabs.com/blog/understanding-accuracy-precision-tolerance-in-3d-printing/
- Hole alignment tolerance stacking: http://www.stat.washington.edu/fritz/Reports/holematch.pdf
- Carrlane locating pin engineering reference: https://www.carrlane.com/engineering-resources/technical-information/manual-workholding/locating-devices/locating-pins
- Parker push-to-connect cartridges: https://www.parker.com/us/en/divisions/fluid-system-connectors-division/industries/water-and-beverage-connectors/water-and-beverage-products/push-to-connect-cartridges.html
- ICU Medical Plum 360 cassette system: https://www.icumed.com/products/infusion-therapy/infusion-pumps-and-software/plum-large-volume-pumps/plum-360-large-volume-infusion-pump/
