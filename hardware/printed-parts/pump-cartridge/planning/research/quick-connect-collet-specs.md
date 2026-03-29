# John Guest 1/4" Push-to-Connect Collet Release Mechanism

Research for the pump cartridge release plate design. The cartridge has 4 quick connects that must be simultaneously released by a single plate actuated by the user's hand squeeze.

## 1. Fitting Identification

The device uses John Guest polypropylene (PP) range fittings for 1/4" OD tube. The relevant part numbers are:

- **PP0408W** -- Union Connector, 1/4" x 1/4" (inline tube-to-tube)
- **PP1208W** -- Bulkhead Union, 1/4" x 1/4" (panel-mount, tube-to-tube)

The cartridge dock likely uses the bulkhead union (PP1208W) or a similar panel-mount fitting so that tubes pass through the dock wall, with the collet face accessible from the cartridge side.

Materials: polypropylene body, EPDM O-ring (food grade), acetal copolymer or polypropylene collet with stainless steel teeth.

## 2. Collet Mechanics -- How the Grip Works

### Internal Components (from tube entry face inward)

1. **Collet (gripper)** -- A ring-shaped component made of acetal copolymer or polypropylene with embedded stainless steel teeth angled inward. The teeth are arranged circumferentially around the tube bore.
2. **O-ring** -- Sits deeper in the body, behind the collet. Provides the leakproof seal against the tube OD.
3. **Tube stop** -- An internal shoulder that limits tube insertion depth.

### Grip Mechanism

- When the tube is pushed in, it passes through the collet (the angled teeth flex outward to allow entry) and past the O-ring to the tube stop.
- The stainless steel teeth are angled so that any pull-out force causes the teeth to bite harder into the tube OD. This is a self-energizing grip -- system pressure pushing the tube outward increases the collet's grip.
- The collet does not deform the tube or restrict flow. The grip is entirely on the outer surface of the tube.

### Collet Geometry

The collet for 1/4" OD tube is a small annular ring:
- **Inner bore:** Sized to pass 1/4" (6.35mm) OD tube with the teeth providing interference
- **Outer diameter:** Approximately 10-11mm (fits within the 12.7mm body bore with clearance for the collet to slide axially)
- **Stainless steel teeth:** Multiple teeth (typically 4-8) arrayed around the circumference, angled inward at approximately 15-20 degrees from the tube axis
- **Collet face:** The annular ring face visible at the fitting entry -- this is what the release plate must press against

The collet cover for 1/4" OD is part number PI1908S-US, which slips over the collet face and the tube, confirming the collet face is an annular ring concentric with the tube.

## 3. Release Mechanism

### How Release Works

To disconnect a tube, the collet must be pushed axially toward the fitting body (toward the O-ring / tube stop direction). This axial movement causes the angled stainless steel teeth to move away from the tube surface, releasing their grip. With the collet held depressed, the tube slides out freely.

The official instruction: "Push the collet square against the face of the fitting. With the collet held in this position, the tube can be removed."

### Release Travel (Collet Depression Distance)

John Guest does not publish the exact collet travel distance. Based on the geometry of the angled stainless steel teeth and analysis of cross-section images from the John Guest Speedfit Technical Guide and Fluid System Catalog:

- The teeth must retract far enough that their tips no longer protrude past the tube bore diameter
- For a tooth angled at ~15-20 degrees with ~1mm of radial engagement, the axial travel required is approximately **1.5-2.5mm**
- **Design value: 2mm nominal, 3mm maximum travel to ensure full release**

This is consistent with the visible gap between collet face and fitting body in JG cross-section diagrams, and with the depth of the collet locking clip (PIC1808R-US for 1/4") which engages this same travel range.

### Release Force (Per Fitting)

John Guest does not publish collet release force specifications. The release force is determined by:

1. **Spring-back force of the collet fingers** -- The collet is a split ring that must be compressed axially. The polypropylene/acetal material provides the spring force.
2. **Friction of the collet sliding in the body bore** -- Minimal, as the collet is designed to slide freely.
3. **Stainless steel teeth friction against the tube** -- When depressing the collet, the teeth must slide along the tube surface.

Based on the following evidence:
- The release is routinely performed with one thumb pressing the collet while the other hand pulls the tube
- The PI-TOOL release tool is a simple flat-ended plastic tool requiring no mechanical advantage
- The collet is small (1/4" size is the smallest in the range)
- JG documentation mentions that "pressure in a system could increase the grip of the collet" and offers a "release aid" tool for pressurized systems -- but the cartridge will be depressurized during removal

**Estimated release force per fitting: 5-15 N (1.1-3.4 lbf)**

This estimate is based on:
- The force is easily overcome by a single thumb press
- Typical thumb press force capacity is 40-80 N, and users describe the release as easy
- The 1/4" size has the smallest collet and lowest spring force in the range
- No system pressure assist (depressurized during cartridge removal)

**Conservative design value: 15 N per fitting (worst case, accounting for material aging and manufacturing variation)**

## 4. Fitting External Dimensions

### PP0408W Union Connector (1/4" x 1/4")
- **Overall length:** 1.5 inches (38.1mm)
- **Body diameter:** 0.5 inches (12.7mm)
- **Collet face diameter:** Approximately 10-11mm (the annular ring visible at each end)
- **Tube bore at entry:** 6.35mm (1/4" OD tube)

### PP1208W Bulkhead Union (1/4" x 1/4")
- **Mounting hole diameter:** 0.67 inches (17.0mm)
- **Panel thickness range:** Standard for thin-wall panel mounting
- **Retention:** Internal nut/shoulder clamps on both sides of panel

### Tube Insertion Depth
For the OD tube (PP/PI) range at 1/4" size:
- **Estimated tube stop distance: 15-16mm from fitting face**
- This is extrapolated from the Speedfit plumbing range where 10mm pipe = 20mm stop distance, with smaller fittings having proportionally shorter insertion depths
- The tube must pass the collet teeth and the O-ring before reaching the stop

### Collet Face Position
- The collet sits at the very entry of the fitting, with its face approximately flush with the fitting body end
- The collet face is set back approximately 0.5-1mm from the body face (visible as a slight recess in product photos)
- The collet has approximately 2-3mm of axial travel before bottoming out against the O-ring seat

## 5. Release Tool Geometry

### PI-TOOL (TSPITOOL) -- Official John Guest Release Tool
- **Overall dimensions:** 3 inches x 1 inch (76mm x 25mm)
- **Dual-ended:** One end for 1/4" fittings, other end for 3/8" fittings
- **Tool geometry:** A flat horseshoe/U-shaped end that slides over the tube and presses the annular collet face

### How the PI-TOOL Works
The tool has a slot that fits around the tube (slot width slightly larger than 6.35mm tube OD). The flat face of the tool contacts the annular collet face surrounding the tube. Pushing the tool toward the fitting body depresses the collet uniformly around its circumference.

### ICLT/2-US -- Collet Locking/Release Tool (Multi-Size)
- **Size range:** 3/16" to 1/2"
- **Design:** A set of graduated flat-ended tools, one side tapered for locking, the other flat for release
- **Function:** Same principle -- flat contact surface presses the collet face

### What This Means for the Release Plate

The release plate must replicate what the PI-TOOL does at 4 positions simultaneously:

1. **Contact surface:** A flat surface with 4 holes (for the tubes to pass through), where the flat annular area around each hole contacts the collet face
2. **Hole diameter in plate:** Must clear the tube (> 6.35mm) but be smaller than the collet face OD (~10-11mm) so the plate presses on the collet ring
3. **Recommended hole diameter: 7.0-7.5mm** (clears the 6.35mm tube with tolerance, contacts the collet across most of its face)
4. **Contact annulus:** The plate contacts the collet on a ring from ~7.0mm ID to ~10.5mm OD, giving approximately 2mm of radial contact width all around

## 6. Tube Retention Force

### Pull-Out Resistance (Tube Gripped, Collet Not Depressed)
The stainless steel teeth create a self-energizing grip. The retention force depends on:
- Number and geometry of teeth
- Tube material (harder tubes = less tooth penetration = lower grip initially)
- System pressure (pressure pushes tube outward, increasing tooth grip)

At zero pressure, the static retention force for a 1/4" tube is sufficient to pass a "tug test" -- John Guest recommends pulling on the tube after insertion to verify the connection is secure.

**Estimated zero-pressure retention force: 30-70 N (7-16 lbf)**

This is consistent with:
- Parker Prestolok data noting 13 lbs (58 N) of force from system pressure alone at 250 psi on 1/4" tube
- The teeth must hold the tube against this pressure force plus any dynamic loads
- The grip increases with pull-out force (self-energizing) and with system pressure

At operating pressure (150 psi / 10 bar), the retention force is substantially higher -- the teeth bite deeper as pressure tries to push the tube out.

**Key point for the release plate: The release plate only needs to overcome the collet spring force (5-15 N per fitting), NOT the tube retention force. The tube retention and collet depression are independent -- depressing the collet retracts the teeth, and then the tube slides out with near-zero force.**

## 7. Panel Mounting -- Bulkhead Union PP1208W

### Mounting Configuration
- The bulkhead union passes through a panel via a 0.67" (17.0mm) diameter hole
- One push-fit connection on each side of the panel
- An internal nut or shoulder on the fitting body clamps against the panel to secure it
- The fitting is rated for panel thicknesses typical of enclosure walls

### For the Cartridge Dock
The 4 fittings in the dock need to be arranged so that:
- Their collet faces are accessible from the cartridge side
- The tube stubs protrude from the dock into the cartridge space
- The fitting bodies are secured in the dock wall
- Spacing between fittings must accommodate the release plate contact area (~11mm diameter per fitting) plus clearance for the plate structure

**Minimum center-to-center spacing: 15-17mm** (11mm contact + 4-6mm structural wall between fittings)

## 8. Force Budget and Release Plate Design Requirements

### Total Release Force
- Per fitting: 15 N (conservative estimate)
- 4 fittings simultaneous: **60 N total**
- With safety factor of 1.5 for aged/stiff collets: **90 N design target**

### User's Hand Force Context
The user operates palm-up, fingers curling up to pull the release surface while palm pushes against the cartridge body. This is a palmar pinch / squeeze motion.

Human hand force capability (from MIL-STD-1472 and ergonomic research):
- 5th percentile male sustained palmar grip: 35 N
- Average male pinch grip: 84 N
- Average female pinch grip: 66 N
- Typical one-hand squeeze: 40-80 N comfortable range

**Assessment:** 60 N (4 fittings, no safety factor) is within comfortable range for most users. 90 N (with 1.5x safety factor) approaches the upper end of comfortable squeeze force for smaller-handed users. This is the hardest the mechanism should ever be.

**Mitigation options if force is too high:**
- Increase mechanical advantage in the squeeze mechanism (longer lever arm)
- Use a cam or toggle mechanism that converts a longer, lower-force squeeze into a shorter, higher-force collet depression
- Reduce friction with PTFE or silicone lubricant on collet sliding surfaces

### Release Plate Travel
- Per fitting collet depression: 2mm nominal, 3mm maximum
- The release plate moves as a rigid body, so all 4 collets are depressed the same distance
- **Release plate travel: 3mm minimum, 4mm recommended** (extra 1mm ensures full depression even with manufacturing tolerance on collet position)

### Release Plate Geometry Summary
- Flat plate with 4 through-holes at the fitting spacing
- Hole diameter: 7.0-7.5mm (clears tube, contacts collet face)
- Plate thickness: minimum 2mm for rigidity (per FDM constraints: 1.2mm minimum structural wall)
- Contact surface must be flat and perpendicular to the tube axes
- The plate translates 3-4mm along the tube axis toward the fittings to depress all 4 collets simultaneously

## 9. Failure Modes

### Partial Collet Depression
If the release plate does not depress the collet fully (< 1.5mm travel), the teeth may partially retract but still grip the tube. The user would feel resistance when pulling the tube out, potentially damaging the tube surface or the collet teeth. The tube might release on some fittings but not others.

**Mitigation:** Design for 3-4mm travel (generous margin over the ~2mm needed). Use a mechanical stop or detent at full depression so the user can feel when the collets are fully released.

### Misaligned Release (Non-Square Depression)
If the release plate is not perpendicular to the tube axes, one side of the collet depresses further than the other. The teeth on the undepressed side continue to grip.

**Mitigation:** The release plate must be guided on rails or pins to maintain perpendicularity. The 4-fitting arrangement inherently helps -- if the plate contacts all 4 collets, it self-centers. The plate should have generous clearance around each tube hole (7.0mm hole for 6.35mm tube = 0.33mm annular clearance) to avoid binding.

### Repeated Cycling
The collet is designed for reuse -- JG documentation states fittings can be disconnected and reconnected. However:
- Stainless steel teeth may eventually dull after many cycles, reducing grip
- Polypropylene collet material may fatigue after hundreds of cycles, reducing spring-back force (which makes release easier but grip weaker)
- O-ring may wear from repeated tube insertion/removal

**Assessment:** For a consumer appliance where the cartridge is replaced perhaps 1-2 times per year, the fittings will far outlast the product lifetime. John Guest fittings are routinely reused dozens of times in RO/water filtration systems.

### Tube Damage from Teeth
If the tube is repeatedly inserted and removed, the stainless steel teeth create score marks on the tube OD. These marks can cause O-ring leaks on the next insertion if the scored area sits under the O-ring.

**Mitigation:** The tube stubs in the dock are permanent -- they are inserted once during assembly and never removed. Only the cartridge-side insertion/removal cycles matter, and those stubs are also relatively permanent (replaced only with the cartridge).

## 10. Connection to the Vision

### Release Plate Travel
The release plate needs **3-4mm of axial travel** toward the fittings. This is a very short stroke. The squeeze mechanism converts the user's finger-pull motion (which might be 10-20mm of finger travel) into this 3-4mm plate translation. This ratio provides mechanical advantage that reduces the user's required force.

### Total Squeeze Force
The user must overcome **60-90 N** through the squeeze mechanism. With mechanical advantage from the lever/squeeze geometry, the actual finger pull force can be reduced to 30-45 N, well within comfortable one-hand operation.

### Release Plate Contact Surface
The plate needs 4 flat annular contact zones, each approximately 10.5mm OD with a 7.0-7.5mm central hole. The plate is a rigid body that translates axially. It must be guided to prevent tilting.

### Fitting Arrangement in the Dock
4 bulkhead unions (PP1208W or equivalent) mounted through the dock rear wall at minimum 15-17mm center-to-center spacing. The tubes stub out toward the cartridge interior. The collet faces face toward the front of the cartridge (toward the user), where the release plate sits.

## Sources

- John Guest Fluid System Products Catalog 2025 (chesterpaul.com)
- John Guest Speedfit Technical Specs Guide v11 (johnguest.com)
- John Guest Technical Specifications for OD Fittings (johnguest.com)
- ESP Water Products: How John Guest Fittings Work
- Parker Prestolok Technical Info (mfcp.com): 13 lbs pressure force on 1/4" at 250 psi
- MIL-STD-1472 Human Engineering: palmar grip force data
- Grip force and pinch grip research (PubMed PMID 21355705)
- Ergoweb Force Guidelines (ergoweb.com)

## Open Questions Requiring Physical Measurement

The following values are estimated from cross-section analysis and engineering judgment. They should be verified by measuring an actual PP0408W or PP1208W fitting with calipers:

1. **Collet face outer diameter** -- Estimated 10-11mm, measure with calipers
2. **Collet depression travel** -- Estimated 2-3mm, measure by pressing collet flush and measuring travel
3. **Release force per fitting** -- Estimated 5-15 N, measure with a small spring scale
4. **Tube insertion depth** -- Estimated 15-16mm for 1/4" OD, measure by inserting a tube and marking
5. **Collet face recess depth** -- Estimated 0.5-1mm from body face, measure with depth gauge
