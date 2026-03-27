# John Guest Push-to-Connect Collet Release Mechanics

Research document for the pump cartridge release plate design. Covers how John Guest 1/4" push-to-connect collets grip tubing, how release works mechanically, commercial tool geometry, failure modes, and implications for a custom multi-fitting release plate.

## Scope and Confidence

This document synthesizes manufacturer documentation, patent literature, and well-understood mechanical principles. Where specific numerical values are sourced from manufacturer specs, they are noted as **verified**. Where values are derived from measurement of physical fittings or reasonable engineering inference, they are noted as **measured/inferred**. This distinction matters for design decisions.

---

## 1. How Push-to-Connect Collets Grip Tubing

### Internal Components (from tube entry inward)

A John Guest push-to-connect port contains these components in order from the outside face inward:

1. **Collet / release sleeve** (acetal copolymer) -- the visible moving ring on the fitting face that the user pushes inward to release. OD: 9.57mm, wall: 1.44mm, ID: 6.69mm (caliper-verified). This is the external interface to the grip mechanism.

2. **Stainless steel gripper teeth** -- a stamped stainless steel ring with inward-angled teeth (sometimes called "grab ring" or "gripper ring"). The teeth are angled toward the interior of the fitting, meaning they allow insertion but resist withdrawal. The teeth are integrated into or seated against the collet.

3. **O-ring** (nitrile or EPDM) -- provides the pressure seal. Seated in a groove in the fitting body, deeper inside than the gripper teeth.

4. **Tube stop** -- an internal shoulder that limits insertion depth and ensures the tube is positioned correctly against the O-ring.

### Key Dimensional Specs (1/4" OD Fittings)

| Parameter | Value | Source |
|-----------|-------|--------|
| Tube OD | 0.250" (6.35 mm) | Verified -- spec |
| Tube OD tolerance | +0.001" / -0.004" | Verified -- John Guest spec |
| O-ring size | AS568-108 (7/16" OD x 1/4" ID x 3/32" CS) | Verified -- John Guest |
| Fitting body OD | Barbell profile: 9.31mm center body, 15.10mm body ends | Caliper-verified (see geometry-description.md) |
| Center body length | 12.16mm | Caliper-verified |
| Body end length | 12.08mm each | Caliper-verified |
| Insertion depth to tube stop | ~16mm per side | Industry convention, unverified |
| Body end OD | 15.10mm | Caliper-verified — the fixed housing section |
| Collet (release sleeve) OD | 9.57mm | Caliper-verified — the moving part that is pushed inward |
| Collet wall thickness | 1.44mm | Caliper-verified |
| Collet ID | 6.69mm | Derived: 9.57 - 2×1.44; tube passes through this |
| Tube OD (measured) | 6.30mm | Caliper-verified (nominal 6.35mm / 1/4") |
| Max working pressure | 150 PSI at 70F | Verified -- John Guest spec |

### Insertion Sequence

1. Tube is pushed into the fitting port.
2. Tube passes through the collet, which is in its relaxed (gripping) position.
3. The gripper teeth deflect slightly outward as the tube passes -- the teeth are angled to allow forward movement.
4. Tube slides past the O-ring, compressing it to create a seal.
5. Tube bottoms out against the tube stop.
6. The gripper teeth now rest against the tube's outer surface, angled inward. Any withdrawal force causes the teeth to bite harder into the tube -- the classic "Chinese finger trap" principle.

### Why It Holds

The gripper teeth are angled at approximately 15-30 degrees from perpendicular (inferred from patent US 8,025,318 and general collet design). This angle means:

- **Insertion**: force is applied along the tube axis toward the fitting. The tube pushes the teeth outward against their spring bias. Low insertion force.
- **Withdrawal**: force is applied along the tube axis away from the fitting. The teeth dig into the tube surface. The greater the pull force, the harder the teeth grip. Under system pressure, the water pressure pushes the tube outward, which makes the teeth grip even harder.

The system is designed so that **it grips before it seals** -- the teeth engage before the tube reaches the O-ring. This prevents a partially-inserted tube from having a seal but no grip (which would blow out under pressure).

---

## 2. How Collet Release Works Mechanically

### The Release Action

To release a tube, the collet is pushed **inward toward the fitting body** (in the same direction as tube insertion). This is a linear axial motion, not a twist or rotation.

What happens internally when the collet is pressed inward:

1. The collet slides axially into the fitting body.
2. The collet pushes against the back side of the gripper teeth ring, or the collet geometry changes the angle/position of the teeth.
3. The teeth are forced to a more perpendicular orientation relative to the tube -- they are pushed off the tube surface or their angle is neutralized so they no longer bite.
4. With the teeth disengaged, the tube can slide freely out of the fitting.

### Critical Detail: The Collet Must Be Held Depressed

The teeth re-engage as soon as the collet is released. The release is not a toggle -- it requires **sustained inward pressure** on the collet while simultaneously withdrawing the tube. Release the collet before the tube clears the teeth, and it re-grips.

### Travel and Force

| Parameter | Value | Confidence |
|-----------|-------|------------|
| Collet travel (axial, inward) | ~1.3mm per side (2.67mm total both ends) | Caliper-verified (41.80mm extended - 39.13mm compressed) |
| Release force (finger pressure) | ~2-5 N (0.5-1 lbf) | Inferred -- designed for tool-free hand release |
| Collet ring protrusion from body face | ~1.4mm per side (2.81mm total both ends, compressed) | Caliper-verified (39.13mm compressed - 36.32mm body) |

The travel is small (~1.3mm per side, caliper-verified) -- only enough to change the tooth engagement angle. The force is intentionally low because John Guest fittings are designed for hand operation without tools. However, the low force also means the release is sensitive to the **direction and evenness** of the applied force.

### Directionality

The force must be **axial** -- pushed straight into the fitting body, parallel to the tube. Any off-axis force component tilts the collet rather than translating it, which leads to partial release (Section 4).

---

## 3. Commercial Release Tool Geometry

### The John Guest PI-TOOL

The PI-TOOL (and similar clip-style release tools) is a small tool with a specific geometry that is not arbitrary. Understanding why it is shaped the way it is directly informs release plate design.

**Overall dimensions**: approximately 3" x 1" (76 mm x 25 mm). The PI-TOOL has a 1/4" end and a 3/8" end, one on each side.

### Shape: U-Shaped / Horseshoe with Inset Lip

The release tool for a given tube size has this cross-sectional profile:

```
         ┌─────────────────────────┐
         │     tool body           │
         │  ┌───────────────────┐  │
         │  │   inset lip       │  │
         │  │  ┌─────────────┐  │  │
         │  │  │             │  │  │
         │  │  │  tube hole  │  │  │
         │  │  │             │  │  │
         │  │  └─────────────┘  │  │
         │  └───────────────────┘  │
    ═════╝                         ╚═════
              (U-shaped opening)
```

Key geometric features:

1. **U-shaped opening (slot)**: The tool slides around the tube without requiring the tube to be disconnected from anything else first. The slot width is slightly larger than the tube OD (just over 1/4" for a 1/4" tool).

2. **Outer cradle**: The outer wall of the tool surrounds and engages the collet on its sides. This is not just for positioning -- it **prevents the collet from moving laterally** when force is applied. The outer diameter of this cradle matches the collet OD.

3. **Inset inner lip**: Inside the U-shape, there is a recessed lip that is narrower than the collet but wider than the tube. This lip is the surface that actually pushes the collet inward. The lip engages the collet face **evenly around its full circumference** (minus the U-slot gap).

4. **Depth/thickness**: The tool has enough axial depth to apply force over the full travel distance of the collet (~1.3mm per side, caliper-verified) without slipping off.

### Why This Geometry Exists

The geometry solves a specific mechanical problem: **the collet must be pushed perfectly axially (straight in) to release cleanly.** The tool achieves this through three mechanisms:

1. **Lateral constraint** (outer cradle): Prevents the collet from shifting sideways when force is applied. Without this, pressing on one side of the collet pushes the opposite side outward -- the collet pivots instead of translating.

2. **Even force distribution** (inset lip): The lip contacts the collet face around as much of its circumference as possible. This distributes the axial force evenly, preventing the collet from cocking/tilting.

3. **Tube centering** (U-slot): The slot slides around the tube and uses the tube itself as a centering reference, ensuring the tool is concentric with the fitting.

### Critical Dimensions of the Tool Relative to the Fitting

For a 1/4" OD tube fitting (all values measured/inferred):

| Dimension | Value | Purpose |
|-----------|-------|---------|
| Slot width (U opening) | ~7.5-8.0 mm (~5/16") | Clears 1/4" tube with slight margin |
| Inner bore (tube clearance) | Between 6.30mm and 6.69mm | Must clear tube OD (6.30mm caliper-verified) but be smaller than collet ID (6.69mm) — so tool face contacts collet end face |
| Collet-hugging bore | Just over 9.57mm | Must clear collet OD (9.57mm caliper-verified) — closely surrounds collet for lateral constraint. Tighter = better grip. |
| Outer cradle ID | Just over 15.10mm | Must clear body end OD (15.10mm caliper-verified) — surrounds body end for lateral constraint. Tighter = less wobble. |
| Tool thickness (axial) | ~3-4 mm | Enough depth to engage collet through full ~1.3mm travel |

The key relationships: The tool has **three concentric bores**. (1) The innermost bore is smaller than the collet ID (6.69mm), so the tool face around this bore contacts the collet's annular end face and pushes it inward. The design window here is only 0.39mm (6.30–6.69mm). (2) The collet-hugging bore is just larger than the collet OD (9.57mm), closely surrounding the collet to prevent lateral movement during the push. Should be as tight as manufacturing allows. (3) The outer cradle just clears the body end OD (15.10mm, caliper-verified) and constrains it laterally. Also as tight as manufacturing allows.

---

## 4. Failure Modes

### 4.1 Uneven Pressure on the Collet

**What happens**: When force is applied more to one side of the collet than the other, the ring tilts/cocks rather than translating axially. One side of the gripper teeth disengages while the other side grips harder.

**Result**: The tube feels stuck. Pulling harder causes the still-engaged teeth to dig in deeper. Users often resort to excessive force, which can damage the tube surface (scoring/gouging), damage the gripper teeth, or crack the collet.

**This is the most common release failure mode** and the primary reason release tools exist at all.

### 4.2 Pressing From Only One Side

**What happens**: Pressing the collet from a single point (e.g., with a fingertip on one edge) creates a moment about the collet's center. The collet pivots: the pressed side goes in, the opposite side stays put or pushes out.

**Result**: Same as uneven pressure -- partial tooth disengagement. In John Guest's small fittings (1/4", 3/8"), this is less of a problem because the collet is small enough that a fingertip covers most of its face. In larger fittings (1/2"+), it becomes a real issue, which is why release tools are more important for larger sizes.

### 4.3 Insufficient Travel

**What happens**: The collet is pressed inward, but not far enough to fully change the tooth engagement angle.

**Result**: Teeth are partially disengaged. Some teeth have reduced grip but still contact the tube. The tube can be pulled with moderate force, but the teeth score/damage the tube surface as it slides past partially-engaged teeth. The tube may also re-seat with a damaged surface that no longer seals properly against the O-ring.

### 4.4 Cocked/Tilted Collet

**What happens**: The collet gets pushed in at an angle (not perpendicular to the fitting face). This can happen from off-axis force, from the tool slipping, or from lateral force on the tube during release.

**Result**: The gripper teeth disengage unevenly around the circumference. Even if the tube can be removed, the collet may not return to its proper resting position. On reinsertion, the cocked collet may not grip evenly, potentially leading to a blow-out under pressure.

### 4.5 Partial Release (Some Teeth Disengage But Not All)

**What happens**: A subset of the gripper teeth (e.g., teeth on one semicircle) disengage while others remain engaged.

**Result**: The tube can rotate but not withdraw. Or the tube withdraws partway and then catches. Forceful removal with partial engagement is the scenario most likely to **permanently damage the fitting** -- the engaged teeth can be bent or broken, the collet can crack, and the tube surface gets scored.

### 4.6 Summary Table

| Failure Mode | Root Cause | Consequence | Severity |
|-------------|------------|-------------|----------|
| Uneven pressure | Off-center force application | Tube stuck, surface damage | High |
| One-sided press | Point force instead of distributed | Collet pivots, partial release | High |
| Insufficient travel | Tool too thin, not pressed far enough | Scored tube, poor re-seal | Medium |
| Cocked collet | Off-axis force, tube lateral load | Uneven grip on reinsert | Medium |
| Partial release | Combination of above | Broken teeth, cracked collet | High |

---

## 5. Multiple Simultaneous Collet Release

### Existing Products and Approaches

**There are no known commercial products designed to release multiple John Guest fittings simultaneously.** All existing release tools (PI-TOOL, clip-style tools, tong-style tools) are designed for single-fitting operation.

Relevant existing approaches:

1. **Manifold fittings**: John Guest and others make manifold blocks with multiple push-to-connect ports. These are designed for permanent or semi-permanent installation. Disconnecting tubes from a manifold is done one at a time with standard release tools.

2. **Disconnect tongs** (IWISS, PLATATO, SharkBite): Plier-style tools that squeeze around a fitting to press the release collar. These work on one fitting at a time. Some handle multiple sizes but not multiple fittings simultaneously.

3. **Locking clips**: John Guest makes locking clips that slide over the collet to prevent accidental release. These are per-fitting accessories, not multi-fitting tools.

### Why Simultaneous Release Is Uncommon

Push-to-connect fittings are overwhelmingly used in installation scenarios where tubes are connected one at a time during setup and rarely disconnected. The "quick-connect" label refers to assembly speed, not frequent disconnect cycles.

The pump cartridge use case -- **frequent disconnect of multiple fittings as part of normal operation** -- is unusual for these fittings. This means we are designing for a use case the fittings were not optimized for, which makes the release mechanism design more critical.

### What Would Be Needed

A mechanism to release 4 collets simultaneously must:

- Apply axial force to each collet independently and evenly
- Maintain that force on all 4 collets while 4 tubes are simultaneously withdrawn
- Accommodate slight differences in collet position/alignment between the 4 fittings
- Avoid transmitting lateral forces between fittings (one stuck fitting should not cock an adjacent one)

---

## 6. Implications for a Release Plate Design

### The Core Challenge

A release plate is essentially 4 built-in release tools that actuate together. Each "tool" must replicate the geometry of a single release tool -- the inset lip profile, the lateral constraint, and even force distribution.

### Hole Profile (Not Just a Simple Hole)

Each hole in the release plate needs a **stepped bore** that replicates the release tool geometry:

```
    Cross-section of one release plate hole:

    ←──── plate travel direction ────→

    ┌────────────────────────────────────────┐
    │            release plate               │
    │   ┌──────────────────────────────┐     │
    │   │    outer bore (cradle)       │     │
    │   │   ┌──────────────────────┐   │     │
    │   │   │  inner lip (stepped) │   │     │
    │   │   │   ┌──────────────┐   │   │     │
    │   │   │   │  tube hole   │   │   │     │
    │   │   │   └──────────────┘   │   │     │
    │   │   └──────────────────────┘   │     │
    │   └──────────────────────────────┘     │
    └────────────────────────────────────────┘
```

Three concentric diameters per hole:

| Feature | Constraint Window | Depth (axial) | Purpose |
|---------|-------------------|---------------|---------|
| Tube clearance hole | 6.30mm < D < 6.69mm | Through | Must clear tube (6.30mm caliper-verified) but be smaller than collet ID (6.69mm) so plate face contacts collet end face. **Only 0.39mm design window.** |
| Inner lip (collet hugger) | D > 9.57mm, as tight as possible | ~1.5-2 mm | Must clear collet OD (9.57mm caliper-verified). Closely surrounds collet for lateral constraint — tighter = less wobble during release. |
| Outer bore (body end cradle) | D > 15.10mm, as tight as possible | ~2-3 mm | Must clear body end OD (15.10mm caliper-verified). Closely surrounds body end for lateral constraint — tighter = less wobble. |

**How force is applied:** The plate face between the through-hole and the inner lip bore contacts the collet's annular end face. The collet face is an annulus from 6.69mm ID to 9.57mm OD (1.44mm wide = the collet wall thickness). The plate contacts the full face of this annulus, providing even, distributed push force. The tighter the inner lip bore is to 9.57mm, the more precisely the plate's contact annulus matches the collet face.

**The inner lip bore serves dual purpose:**
1. **Lateral constraint:** Closely hugs the 9.57mm collet, preventing sideways movement during the push (same principle as the PI-TOOL's outer cradle, but at the collet scale). Tighter fit = better constraint.
2. **Bore transition:** Defines the outer boundary of the contact annulus on the collet face.

**The through-hole is the most dimensionally critical feature:**
- Must be > 6.30mm (tube OD, caliper-verified) so the tube passes through
- Must be < 6.69mm (collet ID) so the plate face contacts the collet face
- **Design window: only 0.39mm.** This is at the edge of FDM accuracy — may require post-processing (drilling/reaming) after printing.

**Clearance philosophy:** All three bores should be as tight to their reference dimensions as manufacturing allows. The tightest constraint (0.39mm on the through-hole) limits overall lateral play; adding unnecessary clearance to the other bores would create more wobble without any benefit. The same precision target should apply to all three bores, bounded by what FDM can reliably produce.
- The inner lip bore must be deep enough to maintain engagement through full collet travel (~1.3mm per side, caliper-verified)

### Tolerances

The collet position relative to the fitting body face varies slightly between fittings. The release plate must accommodate this variation:

| Tolerance | Value | Notes |
|-----------|-------|-------|
| Collet ring protrusion variation | +/- 0.3 mm | Between fittings of same model |
| Fitting-to-fitting position (on cartridge body) | +/- 0.5 mm | Depends on cartridge manufacturing |
| Plate-to-fitting alignment | +/- 0.25 mm | Must be concentric to avoid cocking |

**Compliance is essential.** The plate must either:

1. Be manufactured to tight enough tolerances that all 4 holes engage their collets simultaneously (difficult), or
2. Include some compliance mechanism so each collet can be engaged independently even if they are not perfectly co-planar.

Option 2 is strongly preferred. Approaches:

- **Spring-loaded lips**: Each hole's inner lip is backed by a small spring, allowing independent travel per fitting. Adds complexity.
- **Elastomeric layer**: A thin rubber or silicone gasket between the rigid plate and the collets. Provides ~0.5-1 mm of compliance. Simpler, but may wear.
- **Overtravel**: Design the plate travel to exceed the maximum collet travel by enough margin that variation is absorbed. The first collets to engage simply bottom out while the plate continues to travel until the last collet engages. This works if the fitting body can tolerate slight compression and if the collet mechanism has a natural hard stop.

### Material Considerations

The release plate must be **rigid** enough to:

- Transmit force from a single lever actuation point to 4 collet positions without flexing
- Maintain the stepped bore geometry under load
- Not deform over thousands of actuation cycles

Candidate materials:

| Material | Pros | Cons |
|----------|------|------|
| Machined aluminum | Rigid, precise, durable | Cost, requires CNC |
| 3D printed (PETG/ABS) | Cheap, fast iteration | May flex, wear on lip edges, layer lines |
| 3D printed (resin, SLA) | Smooth, precise | Brittle under repeated stress |
| Injection-molded acetal | What John Guest uses for their tools | Only for production volumes |

For prototyping, **3D-printed PETG** is reasonable if the wall thickness of the inner lip is sufficient (~1.5 mm minimum). The lip edges should be printed with the bore axis perpendicular to the build plate so that layer lines do not create a weak shear plane at the lip.

For a production part, machined aluminum or injection-molded acetal.

### Lever Mechanism Considerations

A single lever must translate into even axial force on the release plate. Key constraints:

- The lever pivot point placement determines force multiplication and travel.
- The plate must move **purely axially** (no tilt). This likely requires a linear guide (pins in slots, or a rail).
- If the plate tilts even slightly, the first collets to engage will be on the side closest to the lever pivot, and the far collets may not fully release -- replicating the single-fitting "one-sided press" failure mode at the system level.
- A cam or toggle mechanism may be preferable to a simple lever, as it can provide a mechanical "over-center" detent that holds the plate in the released position while tubes are withdrawn.

### Design Validation Approach

Before committing to a full 4-fitting release plate, validate with a single-fitting test:

1. 3D print a single stepped-bore release sleeve that slides over tubing.
2. Test it against a John Guest fitting with tubing inserted.
3. Verify: does the collet release cleanly? Can you feel the release "click"?
4. Measure the force and travel required.
5. Intentionally test failure modes: press off-center, press with insufficient travel, tilt the sleeve.
6. Use these measurements to refine the bore dimensions before scaling to 4 fittings.

---

## 7. Summary of Key Design Parameters

For a 1/4" OD John Guest push-to-connect release plate:

| Parameter | Constraint | Source |
|-----------|-----------|--------|
| Tube clearance bore | 6.30mm < D < 6.69mm (only 0.39mm window) | Caliper-verified: tube OD 6.30mm, collet ID 6.69mm |
| Inner lip bore (collet hugger) | D > 9.57mm, as tight as manufacturing allows | Caliper-verified: collet OD 9.57mm |
| Outer bore (body end cradle) | D > 15.10mm, as tight as manufacturing allows | Caliper-verified: body end OD 15.10mm |
| Inner lip depth | ≥ 1.5mm (must maintain engagement through 1.3mm collet travel) | Caliper-verified travel |
| Collet travel (per side) | ~1.3 mm | Caliper-verified |
| Plate travel (stroke) | 3.0 mm | Design (~1.7mm margin over collet travel) |
| Plate parallelism during travel | < 0.3 mm deviation across plate | Design |
| Actuation force per fitting | ~3-5 N | Inferred |
| Total actuation force (4 fittings) | ~12-20 N (2.7-4.5 lbf) | Inferred |

**These are constraint-based starting values for prototyping.** All three bore diameters should be as tight to their reference dimensions as manufacturing allows — unnecessary clearance adds wobble with no benefit. The tube clearance bore has the tightest constraint (0.39mm window); the inner lip and outer bore have more room but should still be tight for best lateral constraint.

**FDM considerations:** FDM holes typically print undersized by 0.1–0.3mm (material squish into the bore). This means:
- The tube clearance bore should be designed slightly above center of the 6.30–6.69mm window to compensate for undersize, but may still need post-processing (drilling/reaming to size).
- The inner lip and outer bore will also print slightly undersized, which actually helps lateral constraint — but if too tight, the plate won't slide over the collet/body end.
- **Validate all three bore diameters with a single-bore test print** against the physical fitting before committing to the full plate.

---

## Sources

- [How John Guest Fittings Work -- ESP Water Products](https://espwaterproducts.com/pages/how-do-john-guest-fittings-work)
- [John Guest Collet Locking/Release Tool](https://www.johnguest.com/us/en/od-tube-fittings/accessories/collet-locking-release-tool)
- [John Guest PI-TOOL Release Tool -- ESP Water](https://espwaterproducts.com/products/john-guest-pi-tool-release-tool-for-quick-connect-collet-1-4-and-3-8)
- [US Patent 8,025,318 -- Push to connect fitting with formed gripper teeth](https://uspto.report/patent/grant/8,025,318)
- [Push Lock Fittings Failures -- Topo Automation](https://topoautomation.com/push-lock-fittings-failures-how-to-fix-them-2025/)
- [How to Fix Leaking Quick-Connect Fittings -- Fresh Water Systems](https://www.freshwatersystems.com/blogs/blog/how-to-fix-leaking-quick-connect-fittings)
- [John Guest OD Tube Fittings Technical Specifications](https://www.johnguest.com/sites/default/files/files/tech-spec-od-fittings-v2.pdf)
- [John Guest Speedfit Technical Specs Guide](https://www.johnguest.com/sites/jg/files/2022-01/RWC11339_JG-Speedfit-Technical-Specs-Guide_v11.pdf)
- [John Guest Replacement O-Ring Specs -- Isopure Water](https://www.isopurewater.com/products/john-guest-replacement-o-ring-for-quick-connect-fittings)
- [John Guest PP0408W Union Connector -- H2O Distributors](https://www.h2odistributors.com/product/pp0408w-john-guest-straight-union-connector/)
