# Design Pattern Research — Soda Flavor Injector Enclosure

This document records findings from research into how real consumer products achieve the three specific UX qualities the enclosure must deliver. Each section names the products studied, describes the concrete geometric and mechanical details that produce the quality, and closes with actionable design guidance specific to this enclosure.

---

## Quality 1: The split seam reads as intentional product feature, not manufacturing artifact

The enclosure prints in two halves — a bottom half and a top half — that snap together permanently. There is a visible horizontal seam running around the perimeter. The goal is for that seam to read as a deliberate design choice, not as evidence that two parts were put together.

### The core problem

When two halves of a plastic part are joined, their mating faces are never perfectly flat. Print warp, slight dimensional variation, and surface irregularity mean the two surfaces touch inconsistently — resulting in a seam that varies in gap width and alignment around the perimeter. The eye reads inconsistency as "cheap" or "accidental."

The solution used across all mass-market consumer products is a **shadow line** (also called a shadow gap or witness line). Rather than trying to make two flat faces meet perfectly, one half has a small inward-stepping lip (the "underbite") and the other has a matching outward step (the "overbite"). This geometry accomplishes three things simultaneously: it makes the parts self-locate during assembly, it hides any gap variation within a controlled dark shadow, and it creates a sharp, consistent line that reads as designed-in.

### Products studied

**Nest Learning Thermostat (2nd Generation)**

The Nest thermostat is built from two primary sub-assemblies: a wall-mounted base and a snap-on display unit. The display unit's rear panel separates from the display ring via screws — when re-seated, it forms a tight press-fit, and iFixit's teardown describes the join as requiring a spudger inserted "into the seam between the front and back housing." The key detail: the display unit is surrounded by a "hefty steel ring" that defines the visible perimeter of the device. The ring itself becomes the seam — its edge is the only split line visible from the front. By making the ring a precision-machined steel part rather than a plastic parting line, Nest converts what would be an injection-molding artifact into a primary design element. The seam gap between the ring and the display housing is tightly controlled; the steel ring's mass and rigidity prevent the variation that makes plastic-to-plastic seams look accidental.

Design principle extracted: When the split line cannot be hidden, make the part that defines it from a material or process that delivers the precision needed for it to read as intentional. Alternatively, integrate the seam into a feature (a groove, a band, a color change) that contextualizes it visually.

**Google Nest Audio**

The Nest Audio front cover is press-fit onto the back housing. The iFixit teardown describes inserting "a simple pick into the seam between the front and back housing and gently pry along the seam." The seam is sealed with a thin black tape strip along the perimeter, meaning the joint line is a narrow, consistent dark line rather than a variable gap. The front fabric-wrapped shell meets the back housing at a crisp horizontal line. The tape serves as both an acoustic seal and a visual gap-filling element: it fills any mating inconsistency with a uniform dark line. The result is a seam that looks like a design decision because it is uniform.

Design principle extracted: A narrow, consistent dark line (0.5–1mm) reads as designed. A variable gap with visible misalignment reads as accidental. The color of the shadow matters: a dark recess conceals variation that a light-colored gap would expose.

**Sonicare DiamondClean Toothbrush**

The Sonicare housing is a two-piece snap-fit ovoid cylinder, bonded with adhesive for waterproofing. Disassembly threads describe applying vise pressure at the ovoid's "slightly more pointed sides" until the housing "suddenly pops open." This indicates an interference snap-fit with no screw. The exterior shows a single circumferential seam line. The ovoid cross-section is the design element that makes the seam tolerable: because the cross-section is not circular, the eye expects to see a line at the widest flat zone of the ovoid. The seam is positioned there. The seam does not fight the geometry — it follows it.

Design principle extracted: Seam position matters as much as seam geometry. A seam at a geometric transition (a corner, the widest point of a form, the edge where two materials meet) reads as "where the design told me to put this." A seam in the middle of a flat face reads as "where the mold line happened to land."

**Automotive body panel standard (reference)**

Automotive body panel gap specifications define the cultural baseline for what "designed gap" means to consumers. Standard consumer vehicle panel gaps (door to body, hood to fender) run 3–4mm consistently. Luxury vehicles use tighter tolerances — 2.5–3mm — and their quality is perceived partly because the gaps are more uniform, not just because they are smaller. Industry quality checks specify that gap variation must stay within 0.5mm to read as intentional. The critical insight from automotive work: a gap that is larger but uniform reads better than a gap that is small but varies. Consistency is the quality signal, not tightness.

For a sealed FDM enclosure split, the automotive standard does not apply directly (those gaps accommodate thermal expansion and door swing clearance that a fixed enclosure does not need). The relevant transfer is the consistency principle: whatever gap dimension is designed into the shadow line, it must be uniform around the full perimeter.

### Dimensional guidance for the shadow line

Based on the research above and the Wikifactory enclosure design reference (which specifies "a small gap of 0.5–1mm between both lips"), the shadow line for this enclosure should be designed as follows:

**Lip geometry:**
- One half carries a protruding lip (the "overbite"), 2.0–2.5mm tall, 1.5mm wide.
- The mating half has a corresponding recessed channel 0.2mm wider and 0.2mm deeper than the lip for clearance.
- The visual gap — the distance from the face of the overbite step to the face of the underbite step, measured perpendicular to the wall — should be **0.5mm**. This creates a shadow that hides mating inconsistency while remaining narrow enough to read as deliberate.

**Position of the seam:**
Place the seam at a horizontal line that corresponds to a visible design change — ideally at the transition between the upper section (which houses the bags and is visually taller) and the lower section (which houses the displays, pumps, and valves). If the enclosure has a color or surface texture change between halves, align it with the seam. Do not place the seam in the middle of an otherwise featureless flat face.

**Alignment:**
The lip-and-channel shadow line provides automatic self-location. No additional alignment pins are needed if the lip runs continuously around the full perimeter. However: the lip must be uninterrupted. Any break in the lip (for snap clips, internal features, or service cutouts) produces a visible seam gap irregularity at that location. Where snap clips interrupt the lip, taper the lip back to zero over 5mm on either side of the clip location so the transition is gradual rather than abrupt.

**FDM-specific note:**
With a 0.4mm nozzle and the tolerances in requirements.md (0.2mm clearance for sliding fits), size the lip channel 0.2mm wider than the lip in both X and Y. The 2.0mm lip height provides enough contact depth that elephant's foot (first-layer flare of 0.2–0.3mm) does not prevent the halves from seating. Add a 0.3mm × 45° chamfer to the leading edge of the lip to guide assembly.

---

## Quality 2: Flush-mounted components (displays, switch) that look like they belong

The front face carries three components: the Waveshare RP2040 0.99" round display (22.4mm diameter), the Meshnology ESP32-S3 1.28" round rotary display (40mm diameter with knob surround), and the KRAUS air switch button (44.5mm diameter body, mounts through a standard 31.75mm / 1-1/4" faucet hole). These must look like they were designed into the face of the appliance, not inserted into holes cut for them.

### The core problem

A component mounted into a hole looks "installed" when:
- The hole is slightly larger than the component, leaving an irregular gap around the perimeter that is neither the enclosure color nor the component color
- The component face sits at a different depth than the enclosure face, with no designed transition
- The component edge has a sharp 90° corner that visually reads as "this component ends here and the enclosure begins there"

A component looks "designed-in" when:
- The enclosure face transitions to the component face through a deliberate geometric feature (a chamfer, a step, a recess)
- The gap between the component edge and the enclosure opening edge is uniform and controlled
- The component face is either flush with the enclosure face or deliberately recessed by a specific, consistent depth

### Products studied

**Nest Learning Thermostat (2nd Generation) — circular display flush mount**

The Nest display is the defining example of a circular element that reads as designed-in rather than installed. The front glass is a plano-convex lens — slightly curved — adhesively bonded to the surrounding plastic frame. The LCD is bonded to the back of the glass. The teardown notes that "adhesive secures the glass to the frame and the LCD to the glass." The important visual detail: the glass extends to the full outer diameter of the display assembly, meaning the steel ring that surrounds it contacts the glass edge, not a gap. There is no visible clearance between the circular glass face and the steel ring surrounding it. The steel ring itself becomes the designed transition from "display" to "enclosure."

Dimensional transfer: The transition from component to enclosure face should be a precision-fit bezel feature — not a clearance gap. If the enclosure opening is 1mm larger in radius than the component, that 1mm of gap needs to be designed as a chamfered recess, not left as an open slot.

**KRAUS KWDA-100 Air Switch Button — countertop flush mount**

The KRAUS air switch button body is 1-3/4" (44.5mm) in diameter. It mounts through a standard 1-1/4" (31.75mm) faucet hole. The button's circular flange sits proud of the mounting surface — the flange diameter is larger than the hole, so the flange covers the hole edge completely. The threaded housing below the flange clamps to the underside of the countertop. From above, the user sees only the button face and its surrounding flange — the hole in the countertop is invisible because the 6.35mm radius difference (44.5mm body vs 31.75mm hole = 6.35mm radius of flange overhang) completely covers it.

This is the "flange cover" approach to flush mounting: the component's own flange is the designed transition, and it is wide enough to fully conceal the opening edge. The flange face is the surface that meets the enclosure — there is no visible gap between the flange and the countertop.

Dimensional transfer: For any circular component, the recess in the enclosure face should be sized so that the component's flange or body sits in it with a clearance of no more than 0.3–0.5mm on the radius. This means the recess diameter should be the component body diameter + 0.6–1.0mm total (0.3–0.5mm per side). The component face — whether the flange or the bezel — should sit either exactly flush with the enclosure face or recessed by 0.5–1.5mm, not protruding beyond it.

**Bulgin 8300VR Series — IP-rated panel mount button (reference for industrial-to-consumer scaling)**

The Bulgin 8300VR series push-button switch uses a 12mm panel cutout and a 17.5mm bezel diameter. The bezel overhang is (17.5 − 12) / 2 = 2.75mm on each side. The IP65/IP67 seal is achieved by the bezel gasket pressing against the panel face, which requires the bezel to sit slightly proud of the panel face (approximately 0.5mm) so the gasket compresses. This is the opposite of the aesthetic goal — the industrial approach makes the component protrude. For the consumer approach, the same principle applies in reverse: design the recess to seat the component bezel flush, with a 45° chamfer on the recess edge to transition cleanly between the component face and the enclosure face.

**Apple iPhone / Nest thermostat — stepped recess pattern**

Across Apple products and the Nest thermostat, components that must be exactly flush (camera glass, sensor windows) are seated in precision-molded recesses with these characteristics:
- The recess is the exact diameter of the component, within ±0.1–0.2mm
- The recess depth equals the component bezel or flange thickness exactly, seating the component face flush with the enclosure face
- The recess edge has a 0.3–0.5mm × 45° chamfer, so the optical transition from enclosure surface to component face is a small visible angle rather than a sharp corner

### Dimensional guidance for flush-mounted components

**For the RP2040 round display (22.4mm diameter):**
- Recess opening diameter: 22.4 + 0.6 = 23.0mm (0.3mm clearance per side)
- Recess depth: equal to the depth of the display bezel/PCB edge that sits inside the enclosure. Measure the actual part — the display face should sit flush with or 0.5mm below the enclosure face.
- Recess edge treatment: 0.5mm × 45° chamfer on the outer rim of the recess opening, machined into the enclosure face.

**For the S3 rotary display (40mm diameter body):**
- Recess opening diameter: 40 + 0.8 = 40.8mm (0.4mm clearance per side, slightly larger clearance to accommodate the rotary knob mechanism tolerance)
- Recess depth: same principle — display face flush with or 0.5mm below enclosure face
- Recess edge treatment: 0.5mm × 45° chamfer

**For the KRAUS air switch (44.5mm body, 31.75mm hole):**
- The switch uses a threaded-nut clamping mount, so the enclosure needs a through-hole for the body's lower section and a surface pocket for the flange.
- Through-hole diameter: 31.75 + 0.4 = 32.15mm (0.2mm clearance per side for the press-fit threading section)
- Surface pocket diameter: the full flange diameter + 0.6mm clearance, depth equal to flange thickness. The flange face should sit either flush with or 0.5mm below the enclosure face.
- Pocket edge treatment: 0.5mm × 45° chamfer

**General rule for all three components:**
The maximum acceptable gap between the component edge and the enclosure recess wall, as seen from the front face, is 0.5mm. Gaps larger than this read as clearance holes. Gaps at 0.5mm or less read as precision fit.

---

## Quality 3: Rear panel connection ports that make installation obvious

The back panel carries 5 ports: carbonated water inlet, carbonated water outlet, tap water inlet, flavor 1 outlet, and flavor 2 outlet. All use 1/4" OD push-fit fittings (John Guest PP1208W bulkhead connectors, mounting hole 0.67" / 17mm, body OD approximately 22mm with flange). The design goal is for the port layout to make correct connection obvious without text, and for the panel to read as designed rather than as a flat plate with holes drilled in it.

### The core problem

A panel with five identical ports, arranged without visual hierarchy, forces the user to trace each tube to understand the system. "This port is where the flow meter is" is the anti-pattern the vision explicitly rejects. The correct framing is "give us an input and we give you an output." That framing — system boundary, not component — must be legible from the port layout itself.

### Products studied

**iSpring RCC7 Reverse Osmosis System — color-coded tubing by function**

The iSpring RCC7 uses a well-documented color-coding system on its connection tubing: red tubing connects the feed water inlet, black tubing connects the drain/waste outlet, yellow tubing connects to the storage tank, and blue tubing connects to the drinking water faucet. The ports themselves are not color-coded — the tubing is. The color coding makes the installation diagram redundant: the user can follow the colors without reading any text.

This approach works because the tubing color is visible at the port connection point. When the user approaches the machine from behind to connect tubes, the colors on the existing tubing immediately tell them which port is which. The design does not require the port itself to carry labeling — the tubing carries the label.

Transfer principle: In the soda injector, the 1/4" silicone or PTFE tubing connected to each port could use distinct colors to communicate port function. Alternatively, the ports can use spatial grouping and positional convention (left = inlet, right = outlet) to create a layout that does not require color — but the layout must be unambiguous.

**Aquasana SmartFlow Reverse Osmosis — spatial grouping by flow direction**

The Aquasana SmartFlow uses blue tubing for filtered output and red tubing for inlet, following the plumbing convention that blue = cold/clean and red = feed/source. The port labels follow this color convention. Spatially, the inlet port (where source water enters the system) is positioned separately from the filtered water outlet. The drain connection exits at the back, away from the user-facing connections.

Transfer principle: Spatial separation by function (inlets grouped together, outlets grouped together) reduces the cognitive load of connection. A user who connects both inlets first, then both outlets, makes fewer errors than a user who must identify each port individually.

**Water filter systems — universal port design language (industry convention)**

Across residential water filtration systems (Aquasana, iSpring, Frizzlife, Pentair Everpure), the following conventions are consistent enough to be considered industry defaults that an informed consumer will recognize:
- Blue or white = inlet (source water in)
- Yellow or clear = filtered output
- Black = drain/waste
- Color is carried on the tubing, not the fitting itself

For the soda injector, which must be languageless (the vision does not specify this explicitly, but the product targets a US home market and the ports will be unlabeled or icon-labeled), the most robust approach borrows from this convention while adapting it to the specific five-port configuration.

**John Guest PP1208W Bulkhead Connector — the port fitting itself as a design element**

The John Guest PP1208W (confirmed: 17mm / 0.67" mounting hole, white polypropylene body, EPDM O-ring, NSF61 listed) is the fitting used on this device. Its physical form is a cylindrical body that protrudes from the panel face and terminates in the push-fit collet. When five of these are arrayed on a flat panel, the panel reads as a field of identical white cylinders — without spatial structure, this looks industrial and unmotivated.

The distinction between "designed" and "drilled" at a port panel comes from: (1) the ports being recessed into a positive feature (a protruding group or zone, a recessed bay, a panel element) rather than sitting on a featureless flat surface; and (2) the visual grouping communicating the port count and arrangement before the user begins connecting.

### Dimensional guidance for rear panel port layout

**Port fitting dimensions (confirmed):**
- John Guest PP1208W mounting hole: 17mm (0.67")
- Body OD: approximately 22mm with wrench flats, 19mm body
- Flange (if used): approximately 26mm OD
- Panel thickness requirement: up to 7.5mm (the bulkhead nut clamps from the inside)

**Port spacing:**
The minimum center-to-center spacing between adjacent ports must be at least 30mm to allow a finger to grip the tubing for insertion and removal. 35mm center-to-center is preferable for comfortable one-handed tube insertion. At 35mm spacing, five ports in a row span 140mm — acceptable within the 300mm enclosure width.

**Grouping and visual hierarchy:**

Divide the five ports into functional groups using recessed bays:

- **Group A — Flow-through pair** (2 ports): Carbonated water inlet + carbonated water outlet. These carry the same fluid (chilled carbonated water) through the flow sensor. They are physically paired — the water enters, the sensor reads, the water exits toward the faucet. Position them together at one end of the rear panel (left, from behind), aligned horizontally. A shallow recessed bay (1.5–2mm recess, 10mm border around the group) groups them visually without text. An arrow motif molded into the bay — an inward arrow for inlet, outward arrow for outlet — communicates direction without words. Arrow relief depth 0.8mm, 1.5mm stroke width (minimum printable).

- **Group B — Tap water inlet** (1 port): Tap water for the clean cycle. Position this port in the center of the rear panel, isolated from both groups. Its isolation communicates "this one is different." No arrow needed — there is only one tap water connection and it is always used for the clean cycle.

- **Group C — Flavor outlets** (2 ports): Flavor 1 and Flavor 2 dispensing lines to the faucet. Position these together at the other end of the rear panel (right, from behind), aligned horizontally. They mirror Group A spatially — two ports at the right end, two ports at the left end, one port in the center. The bilateral symmetry of the port layout communicates the system: water comes in on the left, flavor goes out on the right, clean water in the middle.

**Bay geometry:**

Each recessed bay is a 1.5mm deep, 0.5mm-radius corner-fillet rectangular pocket into the rear panel face. The pocket is 10mm larger than the port group extent in both X and Y (5mm margin per side). The bay floor is flat. The John Guest fittings mount through the bay floor, with their flanges sitting against the bay floor (recessed 1.5mm from the outer panel face). This means the port bodies protrude from a recessed surface, making the group legible as a zone while removing the fittings from the primary outer panel face.

**FDM overhang note:**

The 1.5mm deep bay is a simple horizontal recess with no overhang if the rear panel prints with its outer face down. If the rear panel prints vertically (outer face facing the build plate), the bay creates a slight overhang — add a 45° chamfer to the bay rim to eliminate this.

**Port labeling (icon-based):**

For the inward/outward arrows in Groups A and C, use relief (raised 0.8mm) rather than engraved text, since relief prints more cleanly than engraved features at 0.4mm nozzle. Arrow dimensions: 8mm long, 6mm wide at the widest point, 1.5mm stroke width. Center each arrow below its respective port, 5mm below the port centerline. The Group A arrows point inward (into the enclosure) and outward (away from the enclosure). The Group C arrows both point outward (flavor flows out to the faucet). This is unambiguous: arrows that point toward the enclosure mean "connect your incoming line here," arrows that point away mean "your output goes here."

---

## Summary of actionable dimensions

| Feature | Specification |
|---|---|
| Shadow line lip height | 2.0–2.5mm |
| Shadow line lip width | 1.5mm |
| Shadow line channel clearance | 0.2mm wider and deeper than lip |
| Shadow line visual gap (dark recess) | 0.5mm |
| Shadow line lip lead chamfer | 0.3mm × 45° |
| Component recess opening clearance (per side) | 0.3–0.5mm |
| Component face recess depth (below enclosure face) | 0.0–0.5mm (flush to 0.5mm deep) |
| Component recess edge chamfer | 0.5mm × 45° |
| Port center-to-center spacing | 35mm minimum |
| Port bay recess depth | 1.5mm |
| Port bay margin beyond port group | 5mm per side |
| Port bay corner radius | 0.5mm |
| Icon arrow relief height | 0.8mm |
| Icon arrow stroke width | 1.5mm |
| Minimum gap reading as "designed" | ≤ 0.5mm visible gap |
| Gap consistency tolerance | ±0.2mm around perimeter |
