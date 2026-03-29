# Wood Joinery Techniques Adapted for FDM 3D Printing

Research into traditional wood joinery adapted for FDM manufacturing, focused on assembling multiple 3D-printed parts into larger consumer appliance assemblies.

---

## 1. Traditional Wood Joints Adapted to 3D Printing

### Dovetail Joints

The dovetail is the most widely adapted wood joint for 3D printing. The trapezoidal wedge shape resists pull-apart forces in every direction except the sliding axis, making it a natural fit for multi-part assemblies.

**Adaptations for FDM plastic:**
- Angles must be recalibrated from traditional wood dovetail ratios. Wood dovetails use steep angles (1:6 to 1:8 slope); FDM dovetails work better with shallower angles because plastic deforms rather than compressing like wood grain.
- Add a 1-2 degree taper along the length of the dovetail. This creates a progressive friction lock -- the joint slides together easily at first, then tightens as it seats. This is a key adaptation: wood dovetails rely on a hammer tap to seat; plastic dovetails need to slide in smoothly.
- The female groove should be designed at nominal size; shrink the male tongue to create clearance. Offsetting only the male faces by 0.1-0.2 mm is more predictable than trying to offset both sides.
- Dovetails shorter than ~6 mm can require excessive force to overcome friction. Longer dovetails (15-25 mm) give more room for the taper to work.

**Best for:** Load-bearing assemblies, two-part enclosures, panel-to-panel connections, sliding drawers, tool mounts.

### Finger / Box Joints

One of the simplest interlocking joints. Box-shaped projections on one part fit into corresponding recesses on the other. The large contact area distributes load and provides excellent alignment.

**Adaptations for FDM:**
- The thin finger edges are vulnerable to breakage in brittle materials (PLA). Use PETG or ABS for functional box joints.
- Fingers should be at least 3-4 mm wide to survive handling and assembly forces on FDM parts.
- The Markforged "drop lock" design is an evolution of the finger joint: it adds an interlocking mechanism that increases contact area and eliminates the need for adhesives.

**Best for:** Right-angle panel connections, box construction, cases where alignment matters more than pull-apart resistance.

### Mortise and Tenon

The tenon (protruding tab) fits into the mortise (receiving pocket). In wood, this is the foundational structural joint. In 3D printing, it serves primarily as an alignment and location feature.

**Adaptations for FDM:**
- Layer lines on the tenon faces create friction -- this is generally beneficial for grip but can make insertion difficult. Light sanding or designed-in clearance (0.2-0.3 mm) compensates.
- The tenon should be printed so layers run along its length, not across it. A tenon printed vertically (layers perpendicular to its long axis) will shear apart at the layer boundaries under load.
- Academic research (Tankut & Tankut, published in Wood Material Science & Engineering, 2022) compared 3D-printed ABS connectors to traditional wooden mortise-and-tenon joints in chair construction. The 3D-printed connectors achieved lower absolute strength than wood M&T joints at similar dimensions, but were adequate for the loading requirements when geometry was optimized.
- A follow-up study (MDPI Materials, 2024) using PLA connectors with reinforcement achieved a 35% higher ultimate load than unreinforced joints.

**Best for:** Structural frame connections, right-angle joints, locating features where parts need to register precisely.

### Tongue and Groove

An extended profile on one part (the tongue) slides into a matching channel (the groove) on the other. Provides alignment along one axis and resists separation perpendicular to the groove.

**Adaptations for FDM:**
- The classic tongue-and-groove profile creates problematic overhangs for FDM printing. The groove's internal ceiling is a flat overhang that requires supports or bridging.
- **Solution:** Orient the groove opening perpendicular to the build plate (print it vertically), or redesign the cross-section to avoid overhangs -- for example, using a trapezoidal groove rather than a rectangular one.
- Bevel the tongue's leading edges to ease insertion. A 0.5-1.0 mm chamfer on the tongue's entry edges makes assembly dramatically easier.
- Tongue-and-groove is particularly useful for long seams (panel edges, enclosure halves) where you want alignment along the entire mating surface.

**Best for:** Long panel-to-panel seams, enclosure halves, any joint needing alignment along a line rather than at a point.

### Half-Lap Joints

Each part is cut to half its thickness at the joint, and the two halves overlap. Simple, strong, and easy to print.

**Adaptations for FDM:**
- Naturally FDM-friendly because the geometry involves only flat faces and right angles with no overhangs.
- The overlapping area provides a large bonding surface if adhesive is used, or sufficient friction area for a press fit.
- Minimum overlap length should be at least 2x the material thickness for adequate strength.

**Best for:** Frame construction, L-joints and T-joints where parts meet in the same plane, structural connections.

### Rabbet Joints

A step-shaped recess in one part receives the edge of another part. Similar to a half-lap but only one part is recessed.

**Adaptations for FDM:**
- Very printable geometry -- just a rectangular step. No overhangs, no complex angles.
- The step provides alignment in two axes (the part registers against both the bottom and the wall of the rabbet).
- Add 0.2-0.3 mm clearance to the rabbet depth and width for FDM.

**Best for:** Panel-to-frame connections, box corners, enclosure lids that sit flush.

### Miter Joints

Two parts meet at an angle (typically 45 degrees). In wood, miters are weak without reinforcement; the same is true in 3D printing.

**Adaptations for FDM:**
- A bare miter has minimal mechanical interlock. It must be reinforced with a spline, key, or secondary interlock feature.
- The angled face can be difficult to print cleanly due to stairstepping on FDM. Print orientation should minimize the visible miter face.
- A mitered corner with an internal tongue (miter + spline) gives both the aesthetic of a miter and the mechanical strength of a tongue joint.
- Not commonly used alone in 3D printing; more useful as an aesthetic treatment combined with other joints.

**Best for:** Visible corners where appearance matters, always combined with reinforcing geometry.

### Scarf Joints

A long, tapered overlap between two parts, traditionally used to extend the length of a beam. The taper distributes stress over a large area.

**Adaptations for FDM:**
- Scarf joints work well for joining parts that exceed the print bed size. The long taper area provides excellent bonding surface for adhesive.
- The taper angle should be shallow (5-10 degrees) for maximum strength. Steeper angles approach a butt joint in weakness.
- Interestingly, slicers have adopted the scarf joint concept internally: "scarf seams" in OrcaSlicer taper each layer's start/end to eliminate visible Z-seam lines, inspired by the same woodworking principle.

**Best for:** Extending parts beyond print bed limits, structural splices, any joint where length is more critical than corner geometry.

### Bridle Joints

Similar to mortise-and-tenon, but the mortise is open on one or more sides. One part has a slot; the other has a tongue that fits the slot.

**Adaptations for FDM:**
- The open mortise is easier to print than a closed one (no internal ceiling overhang).
- Provides good alignment but less pull-apart resistance than a closed mortise.
- The open sides allow visual inspection of fit during assembly.
- Minimum slot width should be at least 3-4 mm for printability with a 0.4 mm nozzle.

**Best for:** T-joints, frame connections, anywhere an open-sided mortise simplifies printing or assembly access.

---

## 2. FDM-Specific Considerations

### Layer Orientation vs. Joint Strength

This is the single most critical factor in joint design for FDM.

**The anisotropy problem:** FDM parts can achieve 70-90% of injection-molded strength in the XY plane, but Z-axis (interlayer) tensile strength is only 40-75% of XY strength, and Z-axis ductility drops to 10-30% of XY values. Put simply, parts are 4-5x weaker in tension along the Z axis.

**The rule:** Print joint features so layers run parallel to the joint's load path. A snap hook, dovetail tongue, or tenon that will experience tension should have its layers oriented along the tension direction, not perpendicular to it.

- A cantilever snap hook must bend in the XY plane (along the layer lines), never across them. If it bends across layers, it will snap at a layer boundary.
- A dovetail tongue that slides horizontally should be printed horizontally, with layers running along the tongue's length.
- A tenon that will be pulled out of its mortise needs layers running along its length.

**Practical consequence:** You may need to split a part into sub-components printed in different orientations, then assemble them -- this is itself a reason to use joinery.

### Print-in-Place vs. Post-Assembly Joints

**Print-in-place joints** are printed as a single piece with integrated clearance gaps, producing a functional mechanism right off the build plate. Examples: hinges, ball-and-socket joints, chain links.

- Requires precise printer calibration and good cooling
- Clearance must account for material stringing and oozing in the gap
- Minimum gap of 0.3-0.5 mm for FDM print-in-place
- Practical for hinges and simple articulations; rarely used for structural assembly

**Post-assembly joints** are printed as separate parts and assembled afterward. This is the more relevant category for consumer appliance enclosures.

- Allows optimal print orientation for each part independently
- Permits different materials for different parts
- Enables disassembly for service, repair, or upgrades
- Can achieve tighter effective tolerances because each part is printed in its optimal orientation

### Tolerance and Clearance Recommendations

Tolerances vary by printer, material, and settings. The values below represent consensus across multiple sources.

**FDM Clearance Starting Points:**

| Fit Type | Clearance per Side | Total Gap | Use Case |
|---|---|---|---|
| Interference / press fit | -0.05 to 0.0 mm | Near zero | Permanent connections, pins in holes |
| Snug friction fit | 0.1 to 0.15 mm | 0.2 to 0.3 mm | Dovetails, tongue-and-groove, locating features |
| Sliding fit | 0.2 to 0.25 mm | 0.4 to 0.5 mm | Drawers, sliding panels, removable covers |
| Loose / easy assembly | 0.25 to 0.5 mm | 0.5 to 1.0 mm | Parts that must be inserted/removed frequently |

**Scaling by feature size:**
- Small features (< 6 mm): add 0.1-0.3 mm clearance
- Medium features (6-25 mm): add 0.2-0.4 mm clearance
- Large features (> 25 mm): add up to 0.5-1.0 mm for loose fits

**Rule of thumb:** Start with clearance equal to 2x your layer height. For 0.15 mm layers, begin with 0.3 mm clearance.

**Snap-fit specific:** Use 0.5 mm clearance for FDM snap-fit connectors. This is a deliberate over-clearance that accounts for dimensional variability in the hook geometry.

### Material Considerations for Joint Durability

| Property | PLA | PETG | ABS | Nylon (PA) |
|---|---|---|---|---|
| Elongation at break | ~6% | 20-30% | 10-20% | 30-100%+ |
| Impact resistance | Low (brittle) | High | Medium-high | Very high |
| Snap-fit suitability | Poor | Excellent | Good | Excellent |
| Creep resistance | Good | Moderate | Good | Poor (under load) |
| Shrinkage | Low (~0.3%) | Low (~0.4%) | High (~0.7-0.8%) | High (~1.5-2%) |
| Moisture sensitivity | Low | Low | Low | High |
| Layer adhesion | Good | Very good | Good (with enclosure) | Very good |

**Key takeaway:** PLA is too brittle for functional snap fits and living hinges. PETG is the best general-purpose choice for joinery -- it has high elongation at break, good impact resistance, low shrinkage, and prints easily. ABS is acceptable but requires enclosure printing and has higher shrinkage to compensate for. Nylon is the strongest for joints but has significant shrinkage, moisture absorption, and printing difficulty.

### Infill Effects on Joint Strength

- **Walls matter more than infill.** Increasing wall/perimeter count has a greater effect on strength per increment than increasing infill density. Two extra perimeters often add more strength than raising infill from 20% to 30%.
- **Joint features should be 100% infill.** Any connector, tongue, hook, or finger that will bear load should be solid. This can be achieved by making the feature narrow enough that perimeters fill it completely (feature width <= nozzle diameter * wall count * 2), or by using modifier meshes in the slicer to force 100% infill in the joint region.
- **For non-joint regions:** 20-30% infill is usually sufficient. Forcing 100% infill everywhere raises weight ~50% with marginal strength gains.
- **For structural parts:** 3-6 perimeters plus 30-50% infill is a good range.
- **Infill-wall overlap:** 10-20% overlap between infill and walls improves bonding at the interface.

---

## 3. Existing Projects and Community Knowledge

### Authoritative Guides and References

**Markforged: "3D Printed Joinery: Simplifying Assembly" (2023)**
https://markforged.com/resources/blog/joinery-onyx
One of the most comprehensive industry guides. Covers dovetail joints, the "drop lock" (an evolution of the finger joint with interlocking mechanism), and angled geometry in general. Key insight: a two-part sliding box can accomplish the same restraint as a dovetail but with different aesthetics -- a plate with angled sides that includes a detent at the end to snap it shut. Published with their Onyx (micro-carbon-fiber nylon) material in mind, but principles apply broadly.

**Formlabs: "How to 3D Print Interlocking Parts and Assemblies"**
https://formlabs.com/blog/how-to-3d-print-interlocking-joints/
Covers six joint types: puzzle/tongue joints, dovetails, key joints, fingertip/comb joints, tenon joints, and scarf joints. Provides per-technology tolerance tables. Notes that key joints are not recommended due to tolerance accumulation across multiple parts, and fingertip/comb joints have thin edges prone to breakage.

**Siraya Tech: "3D Print Joints Guide: Connect Parts Like a Pro"**
https://siraya.tech/blogs/news/3d-print-joints
Covers snap-fits, dovetails, pin-and-hole, ball-and-socket, and print-in-place hinges. Provides specific clearance values (0.2-0.3 mm snug, 0.4-0.5 mm sliding for FDM). Key design tip: chamfer pin edges to guide insertion and accommodate first-layer elephant's foot expansion.

**HP: "Designing 3D Printed Joints"**
https://www.hp.com/us-en/printers/3d-printers/learning-center/3d-printed-joint-design.html
Ranks union configurations by bond area strength: dovetail/jigsaw features (strongest), square tongues, tooth patterns, butt joints (weakest). Notes that for parts under 1.7 mm thickness, dovetail/jigsaw features maximize bonding surface.

**Protolabs Network (Hubs): "How to Design Interlocking Joints"**
https://www.hubs.com/knowledge-base/how-design-interlocking-joints-fastening-3d-printed-parts/
Provides technology-specific tolerances: FDM 0.5 mm minimum, SLA 0.2 mm, SLS 0.2 mm. Covers three forces acting on joints: friction (primary holding force), tension (pull-apart), and shear (perpendicular tearing).

**3D Printerly: "How to 3D Print Connecting Joints & Interlocking Parts"**
https://3dprinterly.com/how-to-3d-print-connecting-joints-interlocking-parts/
Practical FDM-focused guide. Key specifications: connector minimum thickness of 5 mm in the Z direction for stiffness, 100% infill for stressed connectors, always use fillets/chamfers to eliminate fracture-initiating sharp corners.

**Eiki Martinson: "Mechanical Design for 3D Printing"**
http://eikimartinson.com/engineering/3dparts/
An engineer's practical guide. Advocates the "Goldilocks Principle" -- print three variants of critical dimensions (slightly larger, nominal, slightly smaller) and test which fits. Includes dimensioned drawings of dovetail joints for right-angle assembly. Notes that separate assembled parts (rather than monolithic prints) allow optimal orientation for each component.

**ColoringChaos: "3D Printing Joints" (CU Boulder)**
https://coloringchaos.github.io/form-fall-16/joints
Academic tutorial covering sliding fit, press-fit, cantilever snap joints, annular snap joints, and hinged pivots. Provides the clearance range of 0.1-0.3 mm for FDM desktop printers.

### Calibration and Test Models

**Dovetail Tolerance Calibration by ssd (Thingiverse)**
https://www.thingiverse.com/thing:3579313
A calibration model with matching dovetail tongue and groove pieces. The groove is rectangular and the tongue tapers at 0.1 mm per 1 cm, allowing calibration of gap tolerances between 0.0 and 0.5 mm with a single print.

**Dovetail Tolerance Test (MakerWorld)**
https://makerworld.com/en/models/132619-dovetail-tolerance-test
Similar tolerance test specific to dovetail profiles.

**Customizable 3D Tolerance Test by zapta (Thingiverse)**
https://www.thingiverse.com/thing:2318105
General tolerance test with parametric pin/hole sizes.

**Printer Tolerance Test by A_Str8 (Printables)**
https://www.printables.com/model/10116-printer-tolerance-test
Clearance test with labeled hole sizes for quick printer characterization.

### Academic Research

**Tankut & Tankut (2022) -- "Strength and stiffness of 3D-printed connectors compared with the wooden mortise and tenon joints for chairs"**
Published in *Wood Material Science & Engineering*. Developed FDM-printed ABS connectors to replace L-shaped chair joints. Found that 3D-printed connectors achieved lower strength than traditional wooden M&T joints at similar dimensions, but the bending moment under compression was about 58% lower. Conclusion: 3D-printed connectors are viable when geometry is optimized for the material.
https://www.tandfonline.com/doi/full/10.1080/17480272.2022.2086065

**MDPI Materials (2024) -- "Evaluation of 3D-Printed Connectors in Chair Construction"**
Follow-up study using PLA connectors with reinforcement. After installing reinforcement connectors, the average ultimate load reached 445.7 N -- a 34.9% improvement over unreinforced joints.
https://www.mdpi.com/1996-1944/18/1/201

**Wang et al. (2025) -- "Design and 3D Printing of Reinforcement Connectors for Mortise and Tenon"**
Published in *BioResources*. Investigated reinforcement strategies for 3D-printed mortise-and-tenon connections.
https://bioresources.cnr.ncsu.edu/

**PMC (2023) -- "Effects of Infill Density, Wall Perimeter and Layer Height in Fabricating 3D Printing Products"**
Demonstrated that wall perimeter count has greater per-increment impact on strength than infill density increases.
https://pmc.ncbi.nlm.nih.gov/articles/PMC9867140/

---

## 4. Fastener-Free Assembly Techniques

### Snap Fits Combined with Joinery

The most effective fastener-free approach combines geometric joinery (for alignment and primary interlock) with snap fits (for retention). This is the strategy used by most injection-molded consumer electronics enclosures.

**Cantilever snap fits:** A flexible beam with a hook deflects during insertion and snaps into a recess. The most common type for enclosures.
- Longer hooks reduce stress at the base
- Lower hook height reduces assembly/disassembly force
- Taper the hook profile (trapezoidal) rather than using parallel sides
- Strain limit for PETG: approximately 3-5% without permanent deformation
- Add a fillet at the base of the cantilever to prevent crack initiation

**Annular snap fits:** A ring-shaped interference fit. One part has a ridge, the other has a groove. Used for cylindrical connections. Can provide a watertight seal.

**U-shaped snap fits:** The cantilever bends back on itself, providing maximum flexibility for repeated assembly/disassembly. Common in electronics enclosures.

**Combined approach for enclosures:**
1. Tongue-and-groove or rabbet along the perimeter for alignment and seam control
2. Snap-fit hooks at intervals for retention
3. Alignment lugs (small extrusions, ~3 mm) to prevent the halves from sliding relative to each other

### Press Fits and Interference Fits

Press fits use slight dimensional interference to create friction-locked connections. The hole is slightly smaller than the pin.

- For FDM: interference of 0.05-0.1 mm (hole undersized relative to pin)
- Press fits work better for pins into holes than for flat-on-flat surfaces
- Risk of cracking the receiving part -- use ductile materials (PETG, ABS, Nylon)
- Pin chamfers (0.5-1.0 mm) are essential for guiding insertion
- Press fits are typically permanent or semi-permanent; not ideal for serviceable assemblies

### Captive Nut Pockets

Not technically fastener-free (the nut is a fastener), but eliminates visible external hardware. A hex-shaped pocket is designed into the print to capture a standard hex nut.

- Cavity should be 0.05 mm larger than the nut on each face
- The nut is pressed or dropped into the pocket during assembly
- Allows screw clamping force without any visible hardware on the exterior
- Can be combined with joinery: the joint provides alignment, the captive screw provides clamping force

### Living Hinges as Joint Elements

Living hinges are thin, flexible bridges that connect two rigid sections, allowing them to fold relative to each other.

**FDM design guidelines:**
- Hinge thickness: 0.4-0.6 mm (the sweet spot; under 0.3 mm is too fragile, over 0.8 mm will not flex properly)
- Hinge length: at least 8-12x the thickness (for a 0.5 mm hinge, minimum 4-6 mm long)
- Print orientation: the hinge's central axis should run in the Z direction (layers built up across the hinge width, not along it)
- Materials: TPU is the best choice; PETG is acceptable; Nylon (PA11, PA12) works well; PLA will crack quickly
- Multi-material printers can print the hinge in TPU and the rigid sections in PETG or PLA
- Use a generous radius at the fold point and a recess at the top to reduce stress during folding

### Printed Threads

3D-printed threads can be used for screw-together assembly without any metal fasteners.

- Minimum practical thread size for FDM: M8 or larger (M6 is marginal)
- Coarse threads (lower pitch) print more reliably than fine threads
- Add 0.2-0.3 mm clearance to the thread profile
- Printed threads wear out with repeated assembly/disassembly -- suitable for infrequent access, not daily use

---

## 5. Advantages Over Other Assembly Methods

### When Does Joinery Beat Screws / Bolts?

| Factor | Screws/Bolts | Joinery | Winner |
|---|---|---|---|
| Alignment precision | Requires separate alignment features (pins, bosses) | Inherent -- the joint IS the alignment | Joinery |
| Visible hardware | Screw heads visible unless countersunk/capped | No external hardware visible | Joinery |
| Parts count | Additional fasteners needed | Zero additional parts (geometry is free) | Joinery |
| Assembly speed | Requires tools | Tool-free snap/slide assembly | Joinery |
| Repeated disassembly | Threads can strip in plastic | Geometric joints can be cycled many times | Joinery (with snap fits) |
| Clamping force | High -- screws provide controlled compression | Lower -- friction/geometry only | Screws |
| Adjustability | Can be tightened/loosened | Fixed geometry | Screws |
| Load capacity | High, concentrated at fastener points | Distributed across joint area | Depends on design |
| Failure mode | Screw pullout or boss cracking | Joint deformation or breakage | Depends |
| Manufacturing cost | Metal fasteners + printed bosses | Geometry only (free to print) | Joinery |

### Specific Advantages for Consumer Appliance Enclosures

**Alignment:** A tongue-and-groove perimeter around an enclosure seam guarantees the two halves register perfectly every time. Screws alone allow halves to shift unless separate alignment pins are added.

**Aesthetics:** No visible screw heads or bolt holes on the exterior surface. The enclosure looks like a product, not a project.

**Serviceability:** Well-designed snap fits allow tool-free disassembly for maintenance. The user does not need screwdrivers, Allen keys, or knowledge of which screws to remove.

**Cost:** Every screw is an additional purchased part. Every captive nut pocket is a feature that must be installed during assembly. Geometric joinery adds zero parts and zero assembly steps beyond the snap itself.

**Structural benefit:** Joinery distributes load along the entire joint line rather than concentrating stress at screw bosses. This is particularly relevant for thin-walled FDM parts where screw bosses are stress risers.

### When to Still Use Screws

- When high clamping force is needed (sealing against gaskets, for instance)
- When parts must be adjustable after assembly
- When the joint must resist sustained vibration loads
- When the assembly will be disassembled only rarely and must be secure against accidental opening
- A hybrid approach (joinery for alignment + one or two screws for positive retention) often provides the best of both worlds

---

## 6. Practical Design Guidelines

### Minimum Dimensions for Joint Features

| Feature | Minimum Dimension | Notes |
|---|---|---|
| Wall thickness (supported) | 1.0 mm | 2-3x nozzle diameter (0.4 mm nozzle) |
| Wall thickness (unsupported) | 1.2 mm | Higher warping risk; needs extra thickness |
| Finger / tooth width | 3-4 mm | Narrower fingers break during assembly |
| Dovetail tongue width (narrowest) | 3 mm | Smaller cannot be printed reliably |
| Snap hook thickness | 1.0-1.5 mm | Thinner hooks break; thicker hooks do not flex |
| Snap hook length (cantilever) | 5-15 mm | Longer = less stress at base, less deflection force |
| Tenon / tongue thickness | 2-3 mm minimum | Must survive insertion forces without snapping |
| Connector Z-height | 5 mm minimum | Below this, stiffness is insufficient |
| Living hinge thickness | 0.4-0.6 mm | Two perimeter lines with 0.4 mm nozzle |

### Chamfers and Lead-Ins for Assembly

- Add 0.5-1.0 mm chamfers to all male features (tongues, tenons, pins) at their leading edges
- Chamfers serve as lead-ins that guide parts together and compensate for slight dimensional variation
- Use chamfers on edges parallel to the print surface; use fillets on edges perpendicular to it
- For dovetails, the 1-2 degree taper along the sliding direction serves as a progressive lead-in
- Pin-and-hole joints: chamfer the pin tip to avoid catching on first-layer elephant's foot expansion

### Handling Shrinkage and Warping

**Material shrinkage rates (approximate):**
- PLA: 0.3-0.5%
- PETG: 0.3-0.6%
- ABS: 0.7-0.8%
- Nylon: 1.5-2.0%

**Design strategies:**
- For ABS and Nylon, add extra clearance to joint dimensions (0.1-0.2 mm beyond the standard tolerance)
- Sharp corners concentrate shrinkage forces during cooling. Use corner radii of 4 mm or more on large features.
- Add ribs to thin-walled sections adjacent to joints to resist warping
- Joints at the edges of large flat panels are most vulnerable to warping. Placing joints away from corners or adding stiffening geometry (ribs, corrugation) nearby helps.
- Print tolerance tests in the same orientation, material, and settings as the final parts. Tolerance values from a test printed flat do not apply to a feature printed vertically.

### Draft Angles

- Traditional injection molding uses 1-3 degree draft angles for part removal. FDM does not require draft for moldability, but draft angles remain useful for joint assembly.
- A 1-2 degree draft on dovetail and tongue features eases insertion.
- For snap-fit hooks, a gentle taper on the insertion ramp (30-45 degrees) controls assembly force, while a steeper angle or overhang on the retention face (80-90 degrees) controls retention force.

### Recommended Testing Protocol

1. **Characterize your printer first.** Print a general tolerance test (pin-and-hole set with 0.0 to 0.5 mm clearances in 0.1 mm increments). Identify the smallest hole a pin slides into freely -- this is your sliding fit clearance.
2. **Print joint-specific calibration pieces.** Use the Thingiverse dovetail tolerance test (thing:3579313) or equivalent. Print in the orientation and material of your final part.
3. **Print and test at scale.** Clearances can change slightly with feature size. A tolerance that works at 10 mm may be too tight at 40 mm or too loose at 5 mm.
4. **Test assembly/disassembly cycles.** If the joint must be opened and closed repeatedly (e.g., enclosure service access), cycle it 20+ times and check for wear, deformation, or loosening.

---

## Summary of Key Design Rules

1. **Orient layers parallel to load.** Joint features must have their layers running along the direction of tension, never perpendicular to it.
2. **Start with 0.3 mm total clearance for FDM.** Adjust from there based on printer characterization.
3. **Use PETG for functional joints.** PLA is too brittle; PETG provides the best balance of printability, strength, and flexibility.
4. **Make joint features solid.** 100% infill in joint regions, achieved either by narrow geometry or slicer modifier meshes.
5. **Chamfer all leading edges.** 0.5-1.0 mm chamfers on male features; 1-2 degree taper on sliding joints.
6. **Fillet all stress concentrators.** Internal corners at the base of snap hooks, tenon shoulders, and finger roots need fillets.
7. **Design for 5 mm minimum Z-height** on connector features for adequate stiffness.
8. **Test tolerances empirically.** Print calibration pieces in the same material, orientation, and settings as the final part.
9. **Combine techniques:** Tongue-and-groove for alignment + snap fits for retention + captive nuts for critical clamping.
10. **Always print joint tests before committing to a full part.** The only reliable tolerance is one measured on your printer.
