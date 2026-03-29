# Design Pattern Research: Pump Cartridge UX

How existing consumer products achieve the three UX qualities the pump cartridge demands: squeeze-to-release between flat surfaces, hidden mechanism behind minimal exterior, and seating confidence on slide-in.

---

## 1. Squeeze-to-Release Between Two Flat Surfaces

The cartridge vision specifies: the user's palm pushes against one flat surface (attached to the quick connect mount), their fingers pull another flat surface (attached to the release plate). Both surfaces can be perfectly flat. The squeeze must feel deliberate and the release must feel clean.

### 1.1 Side-Release Buckles (ITW Nexus, Duraflex)

The side-release buckle, invented by ITW Nexus in 1977, is the most widely deployed squeeze-to-release mechanism in consumer products. The female half contains two cantilever arms with hook features at their tips. Squeezing the arms inward deflects them enough to clear the male component's center bar, allowing separation.

**Geometric details (ITW Nexus 1" / 25mm buckle):**
- Slot width: 25.05 mm
- Body thickness at widest: 11.75 mm
- Overall length: 69.30 mm end to end
- Outside dimension of slot: 31.65 mm
- The squeeze arms are approximately 20-25 mm long cantilever beams
- Deflection required to disengage: approximately 1.5-2.5 mm per side

**Force and feel characteristics:**
- Designed center-bar wings prevent over-flexure of the arms and prevent release under impact loading. This is a critical detail: the mechanism has a built-in deflection stop so the user cannot over-squeeze, which bounds the force curve and prevents the spongy feeling of unlimited travel.
- Measured push-in engagement force on a snap-fit buckle analysis: approximately 2.94 N (using a digital spring scale). This is the force to engage, not release; release force is typically higher because the hook geometry is asymmetric (shallow entry ramp, steeper exit face).
- The material is typically acetal (POM) or glass-filled nylon, chosen for low friction, dimensional stability, and fatigue resistance over thousands of cycles.

**What makes the squeeze feel deliberate:**
- The cantilever arms have a defined engagement point. Before that point, the user feels increasing resistance (elastic deflection of the beam). At the engagement point, the hooks clear and the force drops sharply. This is an over-center force profile: force rises to a peak, then drops. The peak-to-trough ratio is what produces the sensation of a decisive release rather than a gradual slide.
- The arms are short enough (20-25 mm) that the travel is small (under 3 mm per side) and the force is concentrated. Long, compliant arms would feel mushy.

**What makes the release feel clean:**
- The male component ejects under slight spring bias or simply falls free once the hooks clear. There is no intermediate state: the buckle is either locked or free. The binary nature of the engagement produces a clean release.

### 1.2 HP Inkjet Cartridge Spring Clamp (US Patent 5,392,063)

HP's cartridge carriage uses a metallic spring latch to hold ink cartridges in precise registration. This is relevant because it uses a squeeze-activated latch to release a module from a dock, with tight tolerances.

**Geometric details:**
- Cartridge dimensions: 78 mm tall (excluding snout) x 60 mm deep x 19.18 mm wide
- Cartridge mass: approximately 115 g
- Latch material: full hard stainless steel spring
- Cam material: PTFE-filled acetal (20% PTFE, 80% acetal) for low friction at the latch interface
- Leaf spring material: 1050 spring steel with nickel coating
- Leaf spring uncompressed angle: approximately 7.5 degrees
- Leaf spring precision bend: approximately 12 degrees

**Force values:**
- Sideways bias force (registration): approximately 13 N
- Forward seating force: 11 N
- Latch spring constant force: approximately 17.3 N over the deflection range
- Required sideways force to disengage (frictionless): approximately 2.5 N

**Tolerance specifications:**
- Supporting surface tolerance: +/-0.025 mm
- Alignment tolerance: +/-0.0125 mm from reference plane
- Datum surface tolerance: +/-0.020 mm deviation

**What this teaches:**
- The latch force (17.3 N) is high enough to feel substantial but low enough for comfortable one-handed operation. The PTFE-filled acetal cam surfaces reduce friction so the force curve is dominated by the spring snap, not sliding friction. Friction flattens the force curve and makes the release feel sloppy.
- The tolerances (+/-0.025 mm) are far tighter than FDM can achieve, but the principle holds: the latch engagement depth must be consistent to produce a consistent release feel. In FDM, this means the snap-fit hook geometry should be a separate calibration feature, not buried deep in the part where shrinkage and warping accumulate.

### 1.3 Snap-Fit Cantilever Design (Applicable to FDM)

Since the cartridge will be 3D printed, the squeeze-to-release mechanism will be a cantilever snap-fit or a linkage driven by cantilever flexure. Published design data for plastic snap-fits provides the quantitative framework.

**Cantilever snap-fit formulas (from Fictiv, Synectic, Protolabs):**

Maximum allowable deflection:
```
Y = 0.67 * (strain * L^2) / H
```
Where L = beam length, H = beam thickness at root, strain = maximum permissible strain for the material.

Snap deflection force:
```
P = (B * H^2 * E * strain) / (6 * L)
```
Where B = beam width, E = modulus of elasticity.

**Worked example (polycarbonate, from Synectic):**
- Beam length: 8 mm
- Beam width: 1.5 mm
- Beam thickness: 3 mm
- Material: polycarbonate (E = 2,350 MPa, strain limit = 4%)
- Calculated maximum deflection: 1.14 mm (1.0 mm with 10% safety factor)
- Calculated snap deflection force: 13 N
- Calculated snap assembly force (including friction): 54 N

**Material strain limits for FDM-relevant materials:**
| Material | Permissible Strain |
|----------|-------------------|
| ABS | 7% |
| PLA | 4-8% |
| Nylon (PA) | 4-15% |
| PETG | ~5-8% |

**FDM-specific guidance:**
- Clearance for close-fit snap joints: 0.3 mm
- Clearance for tight fits: 0.2 mm
- Clearance for slide fits: 0.4 mm
- Fillet radius at cantilever root: at least 0.5x the base thickness (minimum 0.4 mm)
- Entry angle on snap hook: less than 45 degrees
- Tapered beam tip thickness: half the root thickness
- Draft angle on snap arms: 1-2 degrees on both sides
- Print orientation: snap arms parallel to build plate whenever possible. Z-axis cantilevers should have allowable stress/strain reduced by 50% due to reduced interlayer strength.
- For FDM, make snap arms 1.2-2x the thickness used in injection molding to compensate for reduced material properties.

### 1.4 Design Guidance for the Cartridge Squeeze Mechanism

**Squeeze travel should be 2-4 mm.** Side-release buckles achieve clean release in under 3 mm of arm deflection. The HP cartridge latch disengages with approximately 2.5 N over a similarly small travel. Less than 2 mm feels like a hair trigger; more than 5 mm feels sluggish and uncertain.

**Peak squeeze force should be 10-20 N (1-2 kgf).** The HP latch operates at 17.3 N spring force. The snap-fit example produces 13 N deflection force. This range is comfortable for a one-handed palm-plus-fingers squeeze. Below 5 N, the mechanism may release accidentally from bumps or handling. Above 25 N, it becomes fatiguing.

**The force curve must have a sharp drop at release.** The over-center profile (force rises, peaks, drops) is what separates a satisfying click from a gradual slide. The peak-to-released force ratio should be at least 3:1. Research on snap-fit tactile feedback found that higher "engagement signal-to-hold-force ratio" corresponds to higher user confidence in assembly/disassembly.

**Use low-friction contact surfaces at the latch interface.** HP uses PTFE-filled acetal. For FDM, this means the snap hook face and mating ramp should be oriented so layer lines do not create ridges perpendicular to the sliding direction. Alternatively, a small PTFE or nylon insert at the hook contact point would reduce friction.

**Include a deflection stop.** ITW Nexus buckles have wings that prevent over-flexure. Without a stop, the user can squeeze past the release point and the force curve continues rising, which feels wrong. The stop should engage within 1 mm past the release point.

**Cantilever beam length for 3 mm deflection in PETG (E ~ 2,100 MPa, strain 5%, thickness 2 mm):**
```
L = sqrt(Y * H / (0.67 * strain))
L = sqrt(3 * 2 / (0.67 * 0.05))
L = sqrt(6 / 0.0335)
L = sqrt(179)
L ~ 13.4 mm
```
A 13-14 mm cantilever at 2 mm thickness produces approximately 3 mm of deflection within strain limits. This is a reasonable dimension for the cartridge geometry.

---

## 2. Hidden Mechanism Behind Minimal Exterior

The vision specifies: the release plate, collets, quick connects are all inside the cartridge. The user sees only 4 small holes on the back (for tubes), grooves on the sides (for rails), and the squeeze surfaces on the front. Everything visible has a purpose the user can understand at a glance.

### 2.1 Inkjet Printer Cartridges (HP, Canon, Epson)

Inkjet cartridges are perhaps the closest analogue: a self-contained module with hidden internal complexity (ink reservoir, print head, electrical contacts, foam wicking system, air management) that presents to the user as a simple block with a few visible features.

**What the user sees on an HP 45 cartridge:**
- A smooth plastic shell with one flat face bearing electrical contacts (gold pads)
- A nozzle plate on the bottom (barely visible)
- A label identifying the cartridge number
- A latch tab or grip feature for insertion/removal

**What is hidden:**
- Internal foam reservoir with precisely controlled capillary pressure
- Thermal inkjet array with hundreds of nozzles
- Ink channels and air management passages
- Spring contacts for electrical registration

**What makes it feel like a product, not a DIY project:**
- Uniform wall surfaces with no visible fasteners. The shell is ultrasonically welded or snap-fit from the inside. No screws, no exposed clips, no visible parting lines on the user-facing surfaces.
- Tight seam gaps. Injection-molded consumer electronics achieve seam gaps of 0.03-0.1 mm for premium products. Standard consumer products target under 0.3 mm. FDM cannot achieve 0.03 mm, but can achieve 0.2-0.3 mm with careful design and calibration.
- Every visible feature has an obvious function. The gold contacts are clearly electrical. The nozzle plate is clearly where ink comes out. The label clearly identifies the product. There are no mysterious holes, slots, or bumps.

### 2.2 Brita Filter Cartridges

Brita water filter cartridges hide a complex internal structure (activated carbon, ion exchange resin, mesh screens, flow distribution channels) behind a simple exterior.

**Exterior features the user sees:**
- A smooth plastic housing
- A groove that aligns with a ridge in the reservoir (keying feature)
- For some models: a locking handle that turns until it engages

**Design principle: groove-as-keying.**
The groove is simultaneously a mechanical alignment feature and a user instruction. The user sees the groove on the cartridge and the ridge on the reservoir and understands immediately how to orient the cartridge. The groove does not look decorative or accidental. It is clearly functional.

This maps directly to the cartridge's side rail grooves. The grooves should be wide enough and deep enough to be visually obvious (not hairline slots that could be mistaken for parting lines), and their geometry should suggest the direction of insertion. A tapered lead-in on the groove communicates "slide this way."

### 2.3 Apple MagSafe

Apple MagSafe (both the laptop connector and the iPhone charging system) hides a complex magnet array, spring-loaded pins, and alignment mechanisms behind a smooth, featureless exterior.

**What the user sees:** A flat circular surface (iPhone MagSafe) or a thin rectangular connector (laptop MagSafe). No visible moving parts, no levers, no buttons.

**What is hidden:**
- Concentric rings of magnets with precisely alternating polarity for radial alignment
- Spring-loaded pin contacts
- NFC identification coil
- Ferrite shielding

**Design principle: alignment should be passive.**
MagSafe achieves alignment through magnetic attraction rather than requiring the user to visually align features. For the pump cartridge, the rail-and-groove geometry serves this purpose: the rails constrain 4 of 6 degrees of freedom, so the user only needs to push in the right direction. The quick connects handle the final alignment as the tubes enter the fittings.

**Design principle: the exterior should be a single continuous surface where possible.**
The MagSafe charger face is one unbroken circle. No seams cross the user-facing surface. For the cartridge, this means the squeeze surfaces (palm face and finger face) should each be a single surface with no seams, split lines, or visible internal structure. Any parting lines from the print should be on the sides or back, not on the surfaces the user touches.

### 2.4 Dyson Vacuum Attachments (V7 and later)

Dyson cordless vacuum attachments use a red-button click system. The release mechanism is a cantilever latch inside the attachment barrel, activated by a button on the exterior. The button is the only visible moving part.

**Design evolution (V6 to V7+):**
- V6: release mechanism was on the vacuum body. The user had to find and operate a lever on the wand.
- V7+: release mechanism moved to the tool itself. A single red button on the attachment is the only control.

**Design principle: the release control should be on the removable part, not the dock.**
For the pump cartridge, the squeeze mechanism is on the cartridge itself, which is correct. The dock (the enclosure mount with tube stubs) should have no moving parts and no user-operated controls. The dock should look like a simple receptacle: tube stubs and rails, nothing else.

**Design principle: color-code the single interactive element.**
Dyson uses red for the release button, contrasting with the gray/purple body. This communicates "press here" without labels. For the cartridge, the squeeze surfaces could use a contrasting material color or texture to communicate the interaction point.

### 2.5 Design Guidance for the Cartridge Exterior

**Seam gaps should be under 0.3 mm.** Premium injection-molded products achieve 0.03-0.1 mm. FDM with a 0.4 mm nozzle can reliably achieve 0.2-0.3 mm with proper calibration and design (mating faces printed on the build plate, elephant's foot chamfer per requirements.md). Seam gaps above 0.5 mm read as "homemade."

**No visible fasteners on user-facing surfaces.** All assembly should be snap-fit from the inside, or the cartridge should be a two-piece shell joined on a non-visible edge. The vision's requirement that the cartridge look like a black box means the user should not see how it was assembled.

**Every visible feature must be self-explanatory:**
- 4 holes on the back: clearly for tubes (size them to the tube OD with minimal clearance so they look intentional, not oversized)
- Side grooves: clearly rails (make them 3-5 mm wide and 2-3 mm deep so they are visually distinct from parting lines)
- Squeeze surfaces: clearly grip areas (flat, possibly with a subtle texture change from the surrounding shell)

**The tube holes on the back should be chamfered or countersunk.** Raw FDM holes look rough. A 0.5-1.0 mm chamfer on the entry of each hole makes them look finished and also serves as a lead-in for tube insertion.

**Parting lines should follow natural edges.** If the cartridge is printed as two halves joined together, the seam should run along an edge or a step change in the surface, not across a flat face. A 0.3-0.5 mm step (one surface recessed slightly from the other) hides the seam better than trying to make two surfaces perfectly flush.

---

## 3. Seating Confidence on Slide-In

The cartridge slides in on rails and the tubes push into the quick connects. The user needs to know when the cartridge is fully seated without looking inside.

### 3.1 Power Tool Battery Packs (DeWalt 20V MAX, Makita 18V LXT)

Power tool battery packs are the strongest analogue for the cartridge's slide-in interaction. The battery slides along rails on the tool body until a spring-loaded latch clicks into a detent, locking the battery in place.

**Mechanical description (DeWalt 20V MAX system):**
- The battery slides along T-shaped rails molded into the tool's battery receptacle
- A spring-loaded latch button on the battery engages a corresponding aperture in the tool body
- The latch mechanism uses a linkage (class 2 lever for the button, class 3 lever for the pawl) that amplifies button force at the locking pawl (US Patent 10,158,105)
- The latch spring is a resilient metal member providing consistent return force despite short travel

**Seating feedback sequence:**
1. Initial alignment: rails guide the battery so the user cannot insert it crooked. The T-slot geometry prevents rotation.
2. Sliding resistance: light friction from the rail contact provides continuous feedback that the battery is moving along the correct path.
3. Increasing resistance: as the battery approaches the seated position, the spring-loaded latch begins to ride over the engagement ramp, adding resistance.
4. Click: the latch snaps into the detent. The user feels and hears a distinct click.
5. Flush surface: the battery sits flush with the tool body. Visual confirmation that insertion is complete.

**Design principle: the click IS the confirmation.**
The latch engagement produces both tactile feedback (the force drop as the latch snaps past the detent) and audible feedback (the click sound from the latch impacting the detent wall). Users learn to associate this click with "done" within one or two uses.

**Dimensional implications:**
- Rail width for a battery pack of this size: typically 8-12 mm T-slot width
- Latch engagement depth (hook overhang past the detent edge): typically 1.5-2.5 mm. Less than 1 mm feels insecure; more than 3 mm requires excessive force to release.
- The battery body is slightly wider than the rail slot so there is zero lateral play when seated. This eliminates wobble, which would undermine seating confidence.

### 3.2 HP Inkjet Cartridge Docking (US Patent 6,196,665)

HP's cartridge docking uses a biasing member with ramps that ride against the back of the cartridge as a frame pivots from a canted position to upright. When the frame reaches vertical, flat sections on the ramps snap over into alignment with the cartridge back wall, urging the cartridge into positive registration.

**Seating feedback sequence:**
1. The cartridge drops into a slot (vertical alignment by gravity and slot walls).
2. A frame is pivoted upward. As it rises, ramps on the biasing member contact the cartridge back and push it forward.
3. At the fully upright position, the ramps snap over-center into a flat-against-flat lock. This is felt as a distinct click.
4. Compression springs add forward bias, pressing the cartridge firmly against registration datums.

**Design principle: use registration datums to produce flush alignment.**
The cartridge is biased against datum surfaces with tolerances of +/-0.020-0.025 mm. While FDM cannot achieve these tolerances, the principle applies: the cartridge should be biased (by spring force, rail friction, or gravity) against a hard stop at the fully seated position. The hard stop should be a surface the user can see (the cartridge face is flush with the dock face) or feel (the cartridge stops moving and cannot be pushed further).

### 3.3 Push-to-Connect Tube Fittings (John Guest, Clippard)

Since the cartridge's tubes must push into John Guest quick connects during insertion, the insertion feel of push-to-connect fittings is directly relevant.

**Insertion feel of John Guest 1/4" push-fit fittings:**
- The user pushes the tube into the fitting and feels "slight resistance" as the tube passes the O-ring seal
- Additional pressure is needed to advance the tube "a couple more millimeters" past the collet teeth
- The tube must be pushed until it reaches the internal tube stop
- Pull-out force (tube retention) for comparable push-to-connect fittings: greater than 20 lbs (89 N) at 75 F per Clippard specifications

**Insertion force profile:**
1. Free travel as the tube enters the fitting bore
2. First resistance bump as the tube tip contacts the O-ring (sealing element)
3. Slight increase as the tube pushes past the O-ring and collet teeth grip the tube
4. Hard stop when the tube reaches the internal depth stop

**Design implication for the cartridge:**
- With 4 tubes pushing into 4 quick connects simultaneously, the total insertion force is 4x the single-tube force. If each tube requires 5-10 N to push past the O-ring, the total insertion force is 20-40 N. This is significant and must be accounted for in the rail friction and in the user's expectation of how hard to push.
- The hard stop (tube depth stop inside the fitting) provides a definitive "you're done" signal. The cartridge stops moving when all 4 tubes are fully seated.
- The resistance profile (free travel, then increasing resistance, then hard stop) naturally communicates progress to the user. The user feels the cartridge sliding easily on rails, then encountering resistance from the O-rings, then stopping.

### 3.4 Nespresso Capsule Insertion

Nespresso Original line machines use a lever to close the brew chamber around a capsule. The user drops the capsule into a holder and closes the lever.

**Seating feedback sequence:**
1. The capsule drops into a shaped holder (alignment by gravity and holder geometry).
2. The user closes a lever. The lever drives a piercing needle into the capsule lid and presses the capsule against a bottom needle.
3. The lever reaches a closed position with a tactile detent or over-center latch.
4. A spring mechanism controls holder tension.

**Design principle: increasing resistance followed by a stop communicates completion.**
The lever provides a continuously increasing force as the piercing needles engage the foil, followed by a definitive stop at the closed position. The user feels progress (resistance increasing) and completion (movement stops). There is no ambiguity about whether the machine is ready.

### 3.5 Design Guidance for Cartridge Seating Confidence

**The cartridge must have a definitive hard stop at the seated position.** Options: (a) the cartridge face contacts the dock face (flush stop), (b) the rail grooves have a detent at the end, (c) the tubes bottom out in the quick connects. Option (c) happens naturally (the John Guest fittings have internal tube stops), but it should be supplemented by option (a) or (b) so the user has multiple confirmation signals.

**Include a latch with an audible click at the seated position.** Power tool batteries universally use this, and users report that the click is the primary confirmation signal. A cantilever snap-fit on the cartridge rail groove that engages a detent on the dock rail produces this. The latch engagement depth should be 1.5-2.0 mm (enough to be felt and heard, not so much that release force becomes excessive).

**Rail geometry should produce zero lateral play when seated.** The T-slot or dovetail rail should be sized so the cartridge does not wobble side-to-side or up-down when fully inserted. Clearance of 0.2 mm per side (per FDM tolerance requirements) is acceptable for sliding, but the latch or a tapered section at the end of the rail should take up this clearance when seated.

**The insertion force profile should have three distinct phases:**
1. Free slide on rails (low friction, 2-5 N) - communicates "you're on the right track"
2. Resistance increase from tube-into-fitting engagement (20-40 N total for 4 tubes) - communicates "almost there"
3. Hard stop plus click (tube depth stop plus latch engagement) - communicates "done"

**The seated position should be visually obvious.** The cartridge face should sit flush with the dock opening (within 0.5 mm). If the cartridge is not fully seated, it should protrude visibly (at least 3-5 mm) so the user can see at a glance that something is wrong. There should be no position where the cartridge is "almost in" but looks like it might be in.

**Lead-in geometry on the rails should be generous.** A 2-3 mm chamfer or taper at the start of the rail slot allows the user to engage the cartridge without precise alignment. Power tool batteries use a flared entry on the T-slot for this purpose. The cartridge's rail grooves should have a matching chamfer at their leading edge.

---

## Summary of Actionable Design Parameters

| Parameter | Recommended Range | Source |
|-----------|------------------|--------|
| Squeeze travel to release | 2-4 mm | Side-release buckles, HP latch |
| Squeeze release force (peak) | 10-20 N | HP spring clamp (17.3 N), snap-fit example (13 N) |
| Force drop ratio at release (peak:released) | At least 3:1 | Snap-fit tactile feedback research |
| Cantilever beam length (2 mm thick PETG, 3 mm deflection) | ~13-14 mm | Cantilever formula calculation |
| Snap hook entry angle | Less than 45 degrees | Snap-fit design guidelines |
| Fillet radius at cantilever root | At least 0.5x base thickness | Fictiv, Synectic |
| Seam gap (exterior surfaces) | Under 0.3 mm | Injection molding tolerance standards |
| Visible feature minimum size (rail grooves) | 3-5 mm wide, 2-3 mm deep | Must be visually distinct from parting lines |
| Tube hole chamfer | 0.5-1.0 mm | FDM surface finish requirement |
| Latch engagement depth (seating click) | 1.5-2.0 mm | Power tool battery packs |
| Rail clearance (sliding) | 0.2 mm per side | FDM dimensional accuracy requirements |
| Rail lead-in chamfer | 2-3 mm | Power tool battery entry geometry |
| Total tube insertion force (4 tubes) | 20-40 N | John Guest / Clippard push-fit data |
| Flush protrusion tolerance (seated vs. not) | Flush within 0.5 mm seated, 3-5 mm protruding when not | Visual confirmation requirement |
| Snap arm print orientation | Parallel to build plate | FDM interlayer strength limitation |
| FDM snap arm thickness multiplier vs. injection molding | 1.2-2.0x | Protolabs, Fictiv FDM guidelines |
| Deflection stop past release point | Within 1 mm | ITW Nexus over-flexure prevention |
