# Joining Techniques for FDM-Printed Parts

Research into methods for permanently joining FDM-printed parts into what looks and feels like a single piece. All methods evaluated against the Bambu Lab H2C and its supported material set.

Printer materials (standard): PLA, PETG, TPU, PVA, BVOH, ABS, ASA, PC, PA, PET, PPS, PPA
Printer materials (fiber-reinforced): PLA-CF, PETG-CF, PA-CF, PET-CF, PC-CF, ABS-CF, ASA-CF, PPS-CF


## 1. Solvent Welding

### How it works
A solvent (acetone, MEK, dichloromethane) is applied to mating surfaces, dissolving the top layer of plastic. The parts are pressed together while the surfaces are liquid. As the solvent evaporates, the polymer chains re-entangle across the joint, creating a true molecular weld — not an adhesive bond sitting between two surfaces.

### Material compatibility
| Solvent | Works with | Does NOT work with |
|---------|-----------|-------------------|
| Acetone | ABS, ASA | PLA, PETG, PA, PC, PET |
| MEK (methyl ethyl ketone) | ABS, ASA (more aggressive than acetone) | PLA, PETG, PA, PET |
| Dichloromethane (Weld-On #4/#16) | PETG, PC, ABS, ASA, PET | PLA, PA, TPU |
| 3D Gloop (dissolved filament in solvent) | PLA variant, ABS variant, PETG variant (material-specific formulas) | Cross-material bonds |

### Joint strength
- ABS + acetone: CNC Kitchen testing showed bond strength of ~17 MPa (single joint), comparable to the 19 MPa interlayer adhesion of ABS itself. In 2 of 3 test samples, the part broke next to the bond rather than at it.
- PETG + Weld-On 16: Qualitative reports consistently describe bonds "as strong as the material itself." No published lap-shear MPa numbers found, but failures occur in the parent material rather than at the joint line.
- 3D Gloop (PETG formula): Same mechanism — dissolved polymer re-fuses. Reported as stronger than the printed part.

### Seam visibility
**Can be made nearly invisible.** Because the joint is a true material weld, there is no adhesive layer with a different refractive index or color. If parts are printed in the same material and color, a well-executed solvent weld leaves only a faint line where the two surfaces met. Combined with acetone vapor smoothing (for ABS/ASA), the seam can disappear entirely.

### Tolerances
- Mating surfaces should be flat and flush, ideally with 0.0-0.1 mm gap
- A thin, even film of solvent is applied — excess pools at the seam and leaves visible marks
- Butt joints work; tongue-and-groove joints increase bonded area and self-align

### Tools and consumables
- Acetone: widely available, inexpensive
- MEK: hardware/paint stores, moderate toxicity
- Weld-On #4 or #16: specialty purchase (plastics supplier or Amazon)
- 3D Gloop: specialty purchase, ~$15-20 per bottle
- Fine brush or needle applicator for controlled application
- Ventilation or respirator (organic vapor cartridges) required for all solvents

### Failure modes
- Insufficient dwell time: solvent evaporates before polymer chains entangle, resulting in weak surface bond
- Excess solvent: pools at visible surfaces, causing crazing, hazing, or surface deformation
- Wrong solvent for material: no dissolution occurs, zero bond
- Uneven application: partial bond, stress concentrations at unbonded regions

### Seam elimination workflow (ABS/ASA)
1. Solvent-weld parts together with acetone/MEK
2. Acetone vapor smooth the entire assembled part (15-60 min exposure)
3. The vapor dissolves the seam line along with layer lines across the entire surface
4. Result: glossy, injection-molded appearance with no visible seam
5. Dimensional accuracy loss: ~0.1-0.2 mm of surface detail

**This is the strongest candidate for invisible permanent joins in ABS/ASA.**


## 2. Adhesive Bonding (CA, Epoxy, Structural Acrylic)

### How it works
An adhesive is applied between mating surfaces, cures (chemically or via evaporation), and forms a mechanical bond to both parts. Unlike solvent welding, the adhesive remains as a distinct layer between the substrates.

### Material compatibility
All adhesive types bond to all printable thermoplastics (PLA, PETG, ABS, ASA, PC, PA, TPU, PET). Surface preparation (sanding with 100-220 grit) improves bond quality for all combinations.

### Joint strength (Prusa Research lap-shear testing, MPa)

| Adhesive type | PLA | PETG | ASA |
|--------------|-----|------|-----|
| Medium CA (Peckalep) | 10.2 | 12.6 | 7.2 |
| CA (Alteco Super Glue) | 9.8 | 13.1 | 9.4 |
| 5-min epoxy (Super Glue brand) | 6.3 | 5.1 | 2.0 |
| Z-poxy (slow-cure epoxy) | 5.0 | 3.7 | 2.7 |
| Tamiya Extra Thin (solvent cement) | 4.4 | 2.2 | 6.1 |
| Humbrol Poly Cement (solvent) | 3.2 | 3.5 | 7.4 |

Additional data (Forerunner3D, Loctite HY4070 epoxy):
- FDM ABS to FDM ABS shear: 394 lbf (~1,753 N)
- MJF PA-12 to MJF PA-12 shear: 176 lbf (~783 N)

### Key findings
- **CA glue is stronger than epoxy on PLA and PETG** in lap-shear. Medium-viscosity CA achieved 10-13 MPa across materials.
- **Epoxy is a gap-filler** — useful when surfaces are not perfectly flat (common with FDM). CA requires tight contact.
- **Structural acrylics (MMA)** like Permabond TA4550 bond well to nylon without surface treatment, which is notable since nylon is otherwise difficult to bond.
- For reference, FDM interlayer adhesion is typically 15-25 MPa depending on material and print settings — so a good CA bond approaches parent material strength.

### Seam visibility
**Visible unless post-processed.** CA dries clear but leaves a thin glue line visible at the seam. Epoxy leaves a thicker, often slightly yellowed line. The seam requires filler + sanding + paint to become invisible.

### Tolerances
- CA: requires near-zero gap (< 0.1 mm) for best strength; gap-filling CA formulas tolerate up to ~0.3 mm
- Epoxy: excellent gap-filler, tolerates 0.5-1.0 mm gaps while maintaining strength
- Both benefit from tongue-and-groove or lap joint geometry to increase bonded area

### Tools and consumables
- CA glue: $5-15, instant bond, optional accelerator spray ($8)
- Two-part epoxy: $8-20, 5-60 min working time
- Sandpaper (100-220 grit) for surface prep
- Clamps or tape to hold parts during cure

### Failure modes
- CA on unprepped surfaces: brittle bond, pops apart under impact or peel loading
- CA + PETG: some CA formulas weaken PETG (stress cracking); test before committing
- Epoxy: weak against peel forces (strong in shear only)
- Both: adhesive failure (peeling off surface) if oil, dust, or release agents contaminate the surface


## 3. Heat Staking

### How it works
One part has protruding pins or posts that pass through holes in the mating part. A heated tool (soldering iron with a broad tip) melts the protruding plastic, forming a mushroom-shaped head that locks the parts together mechanically. A countersink around the hole allows the melted material to sit flush with the surface.

### Material compatibility
All thermoplastics: PLA, PETG, ABS, ASA, PC, PA, TPU, PET. Works with fiber-reinforced variants too, though the fiber makes the melt less controllable.

### Joint strength
No standardized MPa data published for FDM heat staking. Practical strength depends on:
- Pin diameter and count
- Depth of engagement
- Number of stake points distributed across the joint

Comparable to snap-fit joints in holding force. The mechanical interlock prevents pull-through, and the melted plastic provides a permanent connection.

### Seam visibility
**Flush on one side, stake heads visible on the other.** If the countersink is properly designed and the melt is controlled, the staked side can be made flush with the surface. The opposite side (where the pin exits) shows the seam between parts. The stake-head side must be an interior or non-visible surface.

### Tolerances
- Pin diameter: nominal hole diameter minus 0.3-0.5 mm clearance for easy insertion
- Pin length: extends 1.5-2x the wall thickness beyond the mating surface (material that gets melted into the head)
- Countersink depth: 0.5-1.0 mm to capture mushroomed material flush

### Tools and consumables
- Soldering iron (40W minimum), broad chisel tip or flat tip
- Kapton tape wrapped around iron tip to prevent plastic sticking
- No consumables — the joint material is the printed plastic itself

### Failure modes
- Overheating: burns the plastic, creating a charred, brittle joint
- Underheating: insufficient melt, pin pulls through under load
- Misalignment: pin doesn't sit straight in hole, creating uneven load distribution
- Plastic-specific: PLA is brittle when re-melted; ABS/ASA/PETG perform better


## 4. Snap-Fit Joints (Permanent Design)

### How it works
A cantilever beam with a hook on one part deflects during assembly and locks behind a catch on the mating part. For permanent assembly, the catch angle is set to 90 degrees (vertical wall), creating a positive lock that requires destruction to separate.

### Material compatibility
Best materials for snap-fits (ductile, high strain tolerance):
- **PETG**: excellent — tough, flexible, fatigue-resistant
- **ABS/ASA**: good — moderate flexibility, well-characterized
- **PA (nylon)**: excellent — highest elongation at break, very durable snaps
- **PC**: good — strong but requires careful strain calculations
- **TPU**: too flexible for structural snaps, but useful for sealing features

Poor snap-fit materials:
- **PLA**: too brittle, snaps break during assembly
- **PPS/PPA**: very stiff, limited deflection before failure

### Joint strength
Depends entirely on geometry. A well-designed snap-fit array distributes load across many engagement points. Published design guidelines:
- Cantilever max strain: 2-5% for ABS, 4-7% for PA, 2-4% for PETG
- Holding force scales with engagement depth, beam width, and material modulus

### Seam visibility
**Seam line visible but can be minimized.** The parting line between two snap-fit halves is inherently visible — this is the line seen on every injection-molded consumer product (phones, remotes, appliances). Minimizing visibility:
- Design a tongue-and-groove perimeter around the snap-fit joint so the seam sits in a controlled channel
- Match print orientation so layer lines on both halves align at the seam
- Add a designed reveal (0.5-1.0 mm chamfer or step) along the seam so it reads as an intentional design feature rather than a flaw
- Post-process with filler + paint if a truly invisible seam is required

### Tolerances
- FDM snap-fits: 0.5 mm clearance between hook and catch
- Sliding/mating surfaces: 0.3-0.5 mm clearance
- Build orientation: print cantilevers in XY plane (not Z-axis) for maximum strength

### Tools and consumables
None — snap-fits are purely geometry. No adhesive, no heat, no fasteners.

### Failure modes
- Brittle material (PLA): snap arm fractures during assembly
- Z-axis printing: snap arm delaminates along layer lines under deflection
- Insufficient draft angle: parts bind during assembly, requiring excessive force
- Creep: over months/years, some thermoplastics relax, reducing holding force (PA and PETG resist this better than ABS)


## 5. Press-Fit with Interference (Crush Ribs)

### How it works
One part has a slightly oversized feature (shaft, post, or rail) that is forced into a slightly undersized pocket on the mating part. Because FDM dimensional accuracy (~0.2 mm) makes true interference fits unreliable, the preferred approach uses **crush ribs**: small raised ridges (0.2 mm tall, spaced along the joint) that deform plastically during assembly, providing controlled interference without stressing the bulk geometry.

### Material compatibility
All rigid thermoplastics. Best with ductile materials (PETG, ABS, ASA, PA) that deform rather than crack. PLA tends to crack rather than crush.

### Joint strength
Depends on contact area, interference amount, and material stiffness. Crush ribs provide:
- Reliable friction hold even with FDM dimensional variability
- Effectively permanent for one-time assembly (ribs deform and cannot re-engage after removal)

### Seam visibility
**Seam line visible.** The joint line between the inserted and receiving parts is visible as a butt joint. Can be minimized with the same strategies as snap-fits (designed reveals, filler + paint).

### Tolerances
- Crush rib height: 0.2 mm above nominal surface
- Nominal clearance (without ribs): 0.1-0.2 mm
- For pure interference (no ribs): -0.05 to -0.2 mm, but requires extensive printer calibration and test coupons per material
- Size-dependent: small features (< 6 mm) need 0.1-0.3 mm clearance; large features (> 25 mm) need up to 0.5-1.0 mm

### Tools and consumables
- Mallet or arbor press for assembly (hand pressure often sufficient for smaller features)
- No consumables

### Failure modes
- Cracking: if interference is too high or material is brittle
- Loose fit: if printer under-extrudes or dimensions are off, ribs don't engage
- One-shot: once assembled and ribs are crushed, disassembly destroys the joint


## 6. 3D Pen Welding / Filament Welding

### How it works
A 3D pen (handheld filament extruder) is used to lay down molten filament along the seam between two parts, fusing the new material to both surfaces. The pen melts the mating surfaces slightly on contact, and the deposited filament bridges the gap. This is functionally the same process as FDM printing, applied manually.

### Material compatibility
Any material available as 3D pen filament: PLA, ABS, PETG. The deposited filament should match the part material for best fusion. PCL (low-temp) pens exist but produce weaker joints.

### Joint strength
No published MPa data. Practical reports indicate strength is comparable to or slightly below FDM interlayer adhesion, since the manual process cannot match the controlled temperature and pressure of a print nozzle. Sufficient for structural joining when applied on interior surfaces with adequate bead width.

### Seam visibility
**Visible and rough without post-processing.** The deposited bead is irregular compared to machine-laid filament. However, because the material is identical to the part, color matching is inherent. After sanding, the joint is the same material and color as the part — filler primer + paint makes it invisible.

### Tolerances
- Gap-tolerant: can bridge gaps of 1-3 mm
- Surfaces don't need to be precision-fit
- Primarily used on interior seams or as supplementary reinforcement behind an adhesive or solvent weld on the visible side

### Tools and consumables
- 3D printing pen: $20-60
- Matching filament
- Sandpaper for finishing the bead

### Failure modes
- Insufficient surface heating: deposited filament sits on top without fusing, peels off
- Wrong temperature: too hot chars the material, too cold doesn't bond
- Material mismatch: different filament than the part doesn't fuse properly


## 7. Threaded Inserts + Screws (Clamping Force Join)

### How it works
Brass threaded inserts are heat-set into one part using a soldering iron. A screw through the mating part threads into the insert, clamping the parts together. This is not a permanent weld — it is a fastener-based assembly — but it provides high clamping force and is widely used in consumer products.

### Material compatibility
All rigid thermoplastics. The brass insert melts into the surrounding plastic and knurling locks it in place. Works well with PLA, PETG, ABS, ASA, PC, PA, PET, and their fiber-reinforced variants.

### Joint strength
- CNC Kitchen testing: CA-glued inserts held ~56 kg (550 N), epoxy-glued inserts ~59 kg (579 N) in Prusa Tough resin; up to 100+ kg (981+ N) in transparent resin
- Pull-out strength depends on insert size, hole design, and wall thickness
- Clamping force between parts depends on screw torque

### Seam visibility
**Screw heads visible.** Unless screw holes are on interior/hidden surfaces, the fastener is visible. Can be covered with:
- Printed caps that snap over the screw head
- Countersunk screws with plugs
- Placing all fasteners on the bottom or back face

The seam line between clamped halves behaves identically to snap-fit seams (visible parting line).

### Tolerances
- Insert hole: tapered cavity per manufacturer spec (varies by insert size)
- Screw clearance hole: nominal screw diameter + 0.3-0.5 mm
- Mating surface: benefits from a locating ridge or tongue-and-groove for alignment

### Tools and consumables
- Brass threaded inserts: ~$10-15 for 100-pack (M3 common size)
- Soldering iron with insert tip: $25-50
- Matching screws
- Installation temperature: 343-399 C (650-750 F)

### Failure modes
- Insert installed crooked: cross-threading, weak pull-out
- Overheated: too much plastic melted, insert sinks past intended depth
- Under-heated: insert not fully seated, spins under torque
- Over-torqued screw: cracks surrounding plastic (especially PLA)


## 8. Acetone Vapor Smoothing as Seam Elimination (ABS/ASA Only)

### How it works
Not a joining method per se, but a post-processing step that eliminates seam visibility after any joining method. The assembled part is placed in a sealed container with acetone-soaked paper towels (cold vapor) or heated acetone (warm vapor). The acetone vapor dissolves the outer surface layer uniformly, causing layer lines AND seam lines to flow together and re-solidify as a smooth, glossy surface.

### Material compatibility
**ABS and ASA only.** No effect on PLA, PETG, PA, PC, TPU, PET, or any other material in the H2C's repertoire.

### Effect on seams
- Surface roughness reduction: 72-81%
- Layer lines disappear entirely
- Seam lines at joints dissolve into the surrounding surface
- Result: glossy, injection-molded appearance
- Dimensional accuracy loss: ~0.1-0.2 mm of fine detail

### Process
1. Assemble parts (solvent weld, adhesive, snap-fit, etc.)
2. Fill any remaining gaps with filler or additional solvent
3. Place in vapor chamber (15-60 min depending on part size)
4. Remove and cure 12-24 hours in ventilated area
5. Optional: light 800+ grit sanding for matte finish

### Safety
- Acetone is flammable (flash point -20 C)
- Requires organic vapor respirator, gloves, eye protection
- Must use in well-ventilated area or outdoors
- Never heat acetone with open flame


## Summary: Method vs. Goal Matrix

| Method | Invisible seam possible? | Strength | Materials | Complexity |
|--------|------------------------|----------|-----------|------------|
| Solvent weld + vapor smooth | Yes (ABS/ASA) | Equals parent material | ABS, ASA, PETG (with DCM), PC | Medium |
| CA adhesive + filler/paint | Yes (any material, with post-processing) | 10-13 MPa (near parent) | All | Medium |
| Epoxy + filler/paint | Yes (any material, with post-processing) | 5-6 MPa | All | Medium |
| Heat staking | One side only | Mechanical lock | All | Low |
| Permanent snap-fit | Designed parting line | Geometry-dependent | PETG, ABS, ASA, PA, PC | Low |
| Press-fit / crush ribs | No (visible parting line) | Friction hold | All rigid | Low |
| 3D pen weld + sand/paint | Yes (with heavy post-processing) | Moderate | PLA, ABS, PETG | Medium |
| Threaded inserts + screws | No (fasteners visible) | High (clamping) | All | Low |
| Vapor smoothing (post-process) | Eliminates seam | N/A (post-process) | ABS, ASA only | Medium |


## Recommendation for the Enclosure

The enclosure is two halves joined permanently (per vision.md). The goal is a single-piece appearance.

**Primary strategy: ABS or ASA + solvent weld + vapor smooth.**
- Print both halves in ABS or ASA
- Solvent-weld with acetone along a tongue-and-groove perimeter joint
- Add permanent snap-fits as mechanical reinforcement (the weld carries the cosmetic burden, the snaps carry the structural burden)
- Vapor smooth the entire assembled enclosure
- Result: no visible seam, no visible fasteners, glossy uniform surface, injection-molded appearance

**Fallback for PETG (if ABS/ASA warping is problematic on large parts):**
- Solvent-weld with Weld-On 16 (dichloromethane-based)
- Snap-fit mechanical reinforcement
- Fill seam with CA + baking soda or automotive filler
- Sand, prime, paint
- Result: invisible seam, but requires paint (cannot stay bare filament color)

**Why not the other methods alone:**
- Snap-fits alone leave a visible parting line
- Threaded inserts require visible fastener access
- Heat staking leaves visible stake heads on one side
- Adhesive alone (without filler/paint) leaves a visible glue line
