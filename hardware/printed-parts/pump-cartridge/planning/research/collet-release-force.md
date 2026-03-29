# Collet Release Force — John Guest PP0408W 1/4" Union

## Purpose

Determine the force and travel required to depress the collet (release sleeve) on the John Guest PP0408W union fitting with a tube inserted, and evaluate what this means for a release plate that must simultaneously depress 4 collets inside the pump cartridge.

## Summary of Findings

No manufacturer of push-to-connect fittings — John Guest, SMC, Festo, SharkBite, Parker — publishes collet release force specifications. This data is not in any publicly available datasheet, technical guide, or catalog. ISO 14743:2020 (the international standard for pneumatic push-in connectors) defines a "disconnecting force test" in Section 9.7, but the standard itself is paywalled and the specific pass/fail force values are not published in the free preview. The absence of published data is itself a finding: the force is low enough that manufacturers consider it a non-specification, because any adult can do it with one thumb on any size from 1/4" to 1/2".

The estimate below is derived from first-principles analysis of the mechanism, ergonomic hand force data, practical experience descriptions from plumbing professionals, and the physical geometry of the PP0408W measured with calipers.


## 1. Single Collet Release Force Estimate

### What the collet mechanism actually does

The collet (release sleeve) is a thin-walled acetal ring (OD 9.57mm, wall 1.44mm, ID 6.69mm) that sits at the end of the fitting body. Inside the body, behind the collet, is a stainless steel grab ring — a split ring with inward-angled teeth that grip the tube's outer surface. When the tube is inserted, the grab ring's teeth bite into the tube OD and resist withdrawal.

When the collet is pushed inward (toward the fitting center), it slides over the grab ring and forces the ring's teeth to deflect radially outward, away from the tube surface, releasing the grip. The collet does NOT compress a spring — it overcomes the radial stiffness of the stainless steel grab ring teeth. The "spring" in this mechanism is the elastic restoring force of the split steel ring itself.

### Force estimation approach

**Lower bound (no tube inserted):** With no tube, the collet slides freely against the body bore with only friction. This is near-zero force — 1-2 N at most.

**Upper bound (tube inserted, grab ring engaged):** The collet must push the grab ring teeth outward against their spring stiffness. The relevant forces are:

1. **Grab ring radial stiffness:** The stainless steel teeth (typically 0.3-0.5mm thick, 3-5mm long cantilevers) deflect ~0.2mm radially to release from the tube surface (6.35mm tube needs teeth to move from gripping at ~6.3mm to clearing at ~6.5mm). For a thin steel cantilever of these dimensions, the force per tooth is on the order of 0.5-2 N.

2. **Number of teeth:** A 1/4" grab ring typically has 4-6 teeth arranged radially.

3. **Collet-to-grab-ring friction:** The collet slides axially over the grab ring, with a wedging action. The friction coefficient between acetal and stainless steel is approximately 0.2-0.3.

4. **Practical validation:** Every plumbing guide, manufacturer instruction, and user forum describes the release action as something done easily with one thumb. The JG Speedfit technical guide (page 9) states that a "release aid" exists to provide "a firmer grip on the collet" — implying the difficulty is gripping the small collet, not overcoming force. The PI-TOOL is marketed as a convenience for access in tight spaces, not as a force multiplier.

5. **Ergonomic context:** A single thumb push typically produces 20-50 N comfortably, with 60+ N achievable momentarily. If the collet required even half of comfortable thumb force (10-25 N), John Guest would not describe the operation as trivially easy, and the PI-TOOL (a simple plastic ring with no mechanical advantage) would not work.

### Best estimate for single 1/4" collet release force

| Parameter | Value | Confidence |
|-----------|-------|------------|
| Release force, no tube | 1-2 N | HIGH — friction only |
| Release force, tube inserted, unpressurized | **5-15 N** | MODERATE — derived from mechanism analysis and ergonomic bounds |
| Release force, tube inserted, pressurized (12 bar) | 10-25 N | LOW — JG Speedfit guide notes pressure increases grip |
| Collet travel required | 1.3 mm (caliper-verified) | HIGH |

**The working estimate for design purposes is 10 N per collet** (unpressurized, tube inserted). This is a conservative mid-range value. The system will always be depressurized before cartridge removal, so the pressurized case is not relevant.

### Sources for this estimate

- Mechanism analysis: stainless steel split ring cantilever deflection mechanics
- Ergonomic data: thumb push force 20-50 N comfortable (Ergoweb force guidelines)
- JG Speedfit Technical Specs Guide (RWC, 2022): release aid described as grip assistance, not force multiplication
- ISO 14743:2020 Section 9.7: defines a disconnecting force test (specific values paywalled)
- Practical consensus from plumbing forums and manufacturer guides: single-thumb operation on all sizes 1/4" through 1/2"


## 2. Four Collets Simultaneously

### Force requirement

At 10 N per collet, 4 collets require **40 N total** (approximately 4 kgf / 9 lbf).

With worst-case estimate of 15 N per collet: **60 N total** (approximately 6 kgf / 13.5 lbf).

### Is this achievable with a finger squeeze?

The vision specifies the user squeezes two flat surfaces together — palm pushes one surface, fingers pull the other. This is essentially a grip/squeeze action.

Ergonomic grip force data:
- Average adult grip strength: 250-450 N (full hand)
- Pinch grip (thumb + fingers): 60-100 N comfortable
- Squeeze between palm and curled fingers at the scale of this cartridge: 60-120 N easily achievable

**40-60 N is well within comfortable one-hand squeeze range.** Even the worst-case 60 N is less than half of a comfortable pinch grip. The user will not perceive this as difficult.

### Mechanical advantage consideration

The vision describes the user squeezing two flat surfaces, which pulls the release plate toward the collets. If the squeeze mechanism translates directly (1:1 ratio), the user's finger force equals the plate force. No mechanical advantage is needed at 40-60 N. If the geometry happens to provide any mechanical advantage (even 1.5:1), the force drops to 27-40 N at the fingers — essentially effortless.


## 3. Travel Distance Analysis

### Measured collet travel

From caliper measurements of the actual PP0408W fitting:
- Collets extended (default): 41.80mm overall
- Collets compressed (pushed in): 39.13mm overall
- **Travel per side: ~1.3mm** (2.67mm total / 2)

### Is 1.3mm sufficient?

Yes. The collet only needs to slide far enough inward to push the grab ring teeth past the tube surface. The grab ring teeth deflect radially by approximately 0.2mm — the axial travel of 1.3mm provides a generous cam angle for this radial displacement.

John Guest installation guides do not specify any minimum depression distance beyond "push the collet square against the face of the fitting." The 1.3mm measured travel represents the full mechanical range of the collet — pushing it further is physically impossible (it hits the internal stop).

### Release plate travel budget

The geometry description document notes the existing mechanism design provides 3mm of plate travel. With 1.3mm needed:

| Item | Value |
|------|-------|
| Collet travel required | 1.3 mm |
| Plate travel available | 3.0 mm |
| **Margin** | **1.7 mm** |

This 1.7mm margin serves two purposes:
1. **Take-up:** The plate must first contact all 4 collet faces before any collet begins to compress. Manufacturing tolerances in the plate, fitting positions, and collet resting positions mean the plate will contact some collets before others. The margin absorbs this.
2. **Overtravel confidence:** The user pushes until they feel resistance stop, not until they hit exactly 1.3mm. The extra travel means "push it all the way" always works.


## 4. Angular Tolerance and Uneven Force

### The problem

The release plate must press 4 collets simultaneously. If the plate is not perfectly parallel to the collet faces, it will contact some collets before others. The plate could tilt, depressing 2-3 collets while barely touching the 4th.

### Collet geometry constraints

Each collet face is an annular ring:
- Collet OD: 9.57mm
- Collet ID: 6.69mm
- **Annular contact width: 1.44mm** (the collet wall thickness)

The release plate contacts this 1.44mm-wide annular face. For the plate to successfully depress a collet, it must engage at least a portion of this face with enough force to push the collet past the grab ring.

### Tolerance analysis

Consider the 4 fittings arranged in a pattern (2x2 or linear). The maximum span between outermost collet centers determines how much angular error the system can tolerate.

For a 2x2 pattern with ~20mm center-to-center spacing:
- Diagonal span: ~28mm
- With 1.7mm of margin and 1.3mm of required travel, the plate can be up to 1.7mm closer to one side than the other before it fails to fully depress the far collets
- Angular tolerance: arctan(1.7/28) = **~3.5 degrees of tilt**

This is a relatively generous angular tolerance, but it relies on:
1. The plate being guided so it translates axially rather than tilting
2. The fitting positions being reasonably precise (within ~0.5mm)
3. The plate not binding on one side when load is applied

### Guidance requirements

The release plate MUST be guided to prevent tilt. Without guidance, the user's squeeze force will almost certainly be off-center (fingers are not symmetric), and the plate will tilt, jamming some collets while under-depressing others.

Options for plate guidance:
- **Rails or slots** in the cartridge body that constrain the plate to axial translation only
- **Multiple guide pins** that prevent rotation and tilt
- **The collet hugger bores themselves** acting as guides — if the plate's inner lips (just over 9.57mm) closely surround each collet, the 4 collets collectively guide the plate

The collet-hugger approach is attractive because it combines guidance with the functional bore geometry already required by the design. If all 4 inner lip bores slide along their respective collets with 0.1-0.2mm clearance, the plate is constrained in X and Y while free to translate in Z (axial direction). This is a 4-point kinematic constraint that prevents both translation and tilt in the plane perpendicular to travel.


## 5. Failure Modes

### Partial collet depression

**What happens:** If the release plate only partially depresses a collet (~0.5mm instead of 1.3mm), the grab ring teeth are partially deflected but still in contact with the tube. The tube is neither fully gripped nor fully released.

**Consequence:** The user pulls the cartridge and the partially-released tube either:
- Comes free with extra pull force (likely for 1/4" tubing — the grip force is low)
- Stays stuck, and the user perceives the cartridge as jammed

**Mitigation:** This is primarily a guidance problem (see Section 4). If the plate is guided, all 4 collets depress simultaneously and fully. The 1.7mm margin means the user can push well past the required 1.3mm, ensuring full depression.

### Collet stuck in depressed position

**What happens:** If the release plate jams in the forward (depressed) position, all 4 collets remain depressed and the tubes are free to slide out with no retention.

**Consequence:** Tubes could slip out during handling or if the cartridge is bumped. This is a nuisance, not a safety issue — the system is depressurized during cartridge operations and the tubes are dry (flavoring residue only).

**Mitigation:** The collet grab rings provide their own restoring force. Once the plate is retracted, the grab rings snap back and re-grip. The plate return mechanism (whatever pulls it back from the collets when the user releases the squeeze) should be positive — a return spring or elastic element, not relying on gravity.

### Tube trapped (cannot remove)

**What happens:** If the release plate mechanism fails entirely (broken linkage, jammed guides), the user cannot depress the collets and cannot remove the cartridge from the dock.

**Consequence:** The cartridge is stuck. The user has no way to access the collets because the vision specifies they are entirely inside the cartridge, hidden from the user.

**Mitigation options:**
1. **Emergency access hole:** A small hole in the cartridge body, covered by a label or plug, that allows a screwdriver or pin to push each collet individually. Not elegant, but functional.
2. **Robust mechanism design:** The squeeze-to-release mechanism is simple (flat surface pulls plate via linkage). If the linkage is a rigid connection (not a cable or flexible element), the failure mode is essentially "the plastic broke," which is unlikely in normal use.
3. **Replaceable cartridge:** If the cartridge is inexpensive to print, a jammed release plate means the user prints or orders a new cartridge shell, not that they are stuck permanently.

### Uneven wear over many cycles

**What happens:** Over hundreds of insertion/removal cycles, the collet contact surfaces and grab ring teeth wear. Acetal-on-stainless and stainless-on-polyethylene (tube) are both low-wear combinations, but eventual degradation is possible.

**Consequence:** Release force decreases (easier to remove), grip force decreases (tubes may slip under pressure), and eventually the fitting fails to hold.

**Mitigation:** The fittings are inside a replaceable cartridge. When the pumps wear out (the primary reason to replace the cartridge), the fittings are replaced along with them. This is a non-issue if the fitting lifespan exceeds the pump lifespan. Kamoer peristaltic pumps typically last 500-2000 hours of operation. At 30 seconds per dispense, that is 60,000-240,000 dispenses. The cartridge will be replaced for pump wear long before fitting wear matters.


## 6. Implications for the Vision

### Release plate force budget

| Parameter | Value |
|-----------|-------|
| Single collet release force (design value) | 10 N |
| 4 collets simultaneously | 40 N |
| Worst-case (15 N each) | 60 N |
| Comfortable one-hand squeeze | 60-120 N |
| **Force margin** | **1.5-3x** |

The squeeze mechanism does not need mechanical advantage. Direct 1:1 transmission of finger force to plate force is sufficient.

### Release plate travel budget

| Parameter | Value |
|-----------|-------|
| Collet travel required | 1.3 mm |
| Tolerance take-up allowance | 0.5-1.0 mm |
| Total plate travel needed | ~2.0 mm minimum |
| Available plate travel (3mm stroke) | 3.0 mm |
| **Margin** | **1.0 mm** |

The 3mm stroke is adequate but not lavish. The mechanism should be designed to use the full 3mm, with the understanding that the first ~0.5-1.0mm is take-up and the last 1.3mm is active collet depression.

### Critical design requirements identified

1. **Plate guidance is mandatory.** The plate must translate axially without tilting. The collet-hugger bore geometry provides natural guidance if the bores are tight (0.1-0.2mm clearance on 9.57mm collet OD).

2. **Return mechanism is needed.** The plate must return to its rest position when the user releases the squeeze. The grab ring springs provide some restoring force, but a positive return element (spring, elastomer, or flexure) is recommended.

3. **No mechanical advantage required.** 40-60 N is well within comfortable squeeze range. Keep the linkage simple and direct.

4. **Depressurize before removal.** The JG Speedfit technical guide warns that pressure increases collet grip force. The iOS app or S3 interface should enforce or prompt depressurization before cartridge removal.

5. **Fitting position precision matters.** The 4 fittings must be positioned accurately (within ~0.5mm) in the cartridge rear wall so the release plate contacts all 4 collets within the take-up margin. Press-fitting the 9.31mm center body into a 9.5mm bore (as specified in the geometry description) provides this precision inherently.

### What is NOT a concern

- **Force magnitude:** 40-60 N for 4 collets is easy for any adult.
- **Travel distance:** 1.3mm per collet with 3mm available is generous.
- **Collet wear:** Fittings will outlast the pumps by a wide margin.
- **Tube trapping:** If the mechanism works at all, it works fully — partial depression is a guidance problem, not a force problem.


## 7. Recommendation: Empirical Verification

The force estimate of 10 N per collet is derived from first-principles analysis, not from direct measurement. Before finalizing the release plate and squeeze mechanism design, the following test should be performed:

**Test procedure:**
1. Insert a 16mm length of 1/4" OD polyethylene tubing into one port of a PP0408W union
2. Using a kitchen scale or force gauge, press the collet inward while noting the peak force
3. Repeat 5 times, average the readings
4. Multiply by 4 for the release plate force requirement

This test takes 5 minutes with parts already on hand and eliminates the uncertainty in the estimate. If the measured force is significantly different from 10 N (e.g., 25 N per collet = 100 N for 4), the squeeze mechanism may need mechanical advantage or a different approach.

**Equipment needed:** PP0408W fitting (on hand), 1/4" OD tubing (on hand), kitchen scale or luggage scale capable of reading in the 0-5 kg range.
