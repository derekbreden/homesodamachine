# Collet Release Mechanics — Simultaneous 4-Fitting Release

## Problem Statement

The pump cartridge has 4 John Guest PP0408W 1/4" union fittings mounted in its rear wall. When the user removes the cartridge, all 4 collets must be pushed inward ~1.3mm simultaneously to release the tubes. This document investigates the force per collet, the total force for 4 collets, ergonomic constraints, and mechanism options for converting a single user action into that simultaneous release.

---

## 1. John Guest Collet Release Force

### 1.1 What John Guest Publishes

John Guest does not publish the collet release force (the axial force required to push the collet sleeve inward to disengage the stainless steel grab teeth). Their technical documentation covers pressure ratings (150 psi at 70F for polypropylene fittings), tube pull-out strength, and installation procedures, but not collet actuation force.

Sources searched:
- John Guest OD Fittings Technical Specifications PDF (https://www.johnguest.com/sites/default/files/files/tech-spec-od-fittings-v2.pdf) — logo file, not a spec sheet
- JG Speedfit Technical Specs Guide (https://www.johnguest.com/sites/jg/files/2022-01/RWC11339_JG-Speedfit-Technical-Specs-Guide_v11.pdf) — no force data extractable
- ESP Water Products fitting guide (https://espwaterproducts.com/pages/how-do-john-guest-fittings-work) — describes procedure, no force values
- SMC KQ2 one-touch fitting datasheets — describe "low disconnection force" qualitatively, no newton values
- Parker Legris push-in fitting catalogs — no release force published

**Conclusion: No manufacturer publishes the collet release force for small-diameter push-to-connect fittings.** This appears to be proprietary/untested data. The force must be estimated from the mechanism geometry and material properties.

### 1.2 Engineering Estimate of Single-Collet Release Force

#### Mechanism description
The John Guest collet contains a stainless steel split ring (grab ring) with inward-pointing teeth. When a tube is inserted, the teeth flex outward to pass over the tube, then spring back to grip the tube surface. The collet sleeve (acetal, OD 9.57mm, wall 1.44mm) sits over the grab ring. Pushing the collet sleeve inward compresses the grab ring axially, which lifts the teeth off the tube surface.

The grab ring is a C-shaped (split) ring of spring-temper stainless steel (likely 301 or 302 SS). For a 1/4" fitting:
- Ring sits in an annular space between the tube (6.30mm OD) and the body bore
- Ring has small teeth stamped or bent inward at ~15-20 degree angle
- The collet sleeve's inward face has a taper or step that cams the teeth outward (radially) when pushed axially inward

#### Force estimation approach
The force to push the collet is governed by:
1. **Friction** between the acetal collet sleeve and the stainless steel grab ring / acetal body bore
2. **Spring force** of the grab ring teeth resisting deflection
3. **O-ring friction** (the collet sleeve slides past the O-ring area)

For a 1/4" fitting (6.35mm tube), the grab ring is small — approximately 8mm OD, 0.3-0.4mm thick spring steel. The teeth are perhaps 2-3mm long cantilevers that need to deflect ~0.3mm radially to release the tube.

**Cantilever beam estimate for one tooth:**
- Beam length L ~ 2.5mm
- Width w ~ 1.5mm
- Thickness t ~ 0.3mm
- Deflection delta ~ 0.3mm
- E (spring steel 301 SS) ~ 193 GPa
- Force per tooth: F = (3 * E * I * delta) / L^3
  - I = w * t^3 / 12 = 1.5 * 0.3^3 / 12 = 0.0034 mm^4
  - F = (3 * 193000 * 0.0034 * 0.3) / 2.5^3
  - F = (592) / (15.6) = ~38 mN per tooth

With 6-8 teeth around the ring, total radial spring force ~ 0.23 - 0.30 N. But this radial force is converted to axial force through the cam angle of the collet sleeve taper (perhaps 30-45 degrees), adding a factor of 1/tan(angle) ~ 1.2-1.7x, plus friction (coefficient ~0.15-0.25 for steel-on-acetal).

**This analysis suggests the spring force component alone is very small — well under 1N per collet.**

The dominant force is likely **friction**: the collet sleeve sliding against the body bore and past the O-ring. Typical O-ring friction for a small static seal being broken is 1-5N depending on squeeze and lubrication.

#### Practical calibration
Qualitative reports from plumbing forums and product descriptions consistently describe the collet release as easily done with one finger or thumb, even without the PI-TOOL release aid. The PI-TOOL exists for convenience in tight spaces and repeated disconnections, not because the force is high. John Guest's own instructions simply say "push the collet toward the fitting body" with no mention of requiring tools or significant force.

**The fact that a single index finger can comfortably push one collet while simultaneously pulling the tube out with the other hand constrains the force to roughly the range of comfortable one-finger push force.**

#### Estimated single-collet release force

| Parameter | Value | Basis |
|-----------|-------|-------|
| Spring component | 0.3 - 1 N | Cantilever beam analysis of grab ring teeth (DERIVED) |
| O-ring breakaway friction | 1 - 5 N | Typical for small static O-ring seals (ENGINEERING REFERENCE) |
| Sliding friction (collet in bore) | 0.5 - 2 N | Acetal-on-acetal, light interference fit (ENGINEERING REFERENCE) |
| **Total per collet** | **2 - 8 N** | **Sum of components** |
| **Best estimate** | **~5 N (~1.1 lbf)** | **Consistent with "easy one-finger push" reports** |

The 5N best estimate corresponds to roughly 500g-force — easily within one-finger capability (a comfortable index finger push is 10-20N).

### 1.3 Four-Collet Total Force

| Scenario | Force per collet | Total (4 collets) |
|----------|-----------------|-------------------|
| Low estimate | 2 N | 8 N (1.8 lbf) |
| Best estimate | 5 N | 20 N (4.5 lbf) |
| High estimate (stiff O-rings, new fittings) | 8 N | 32 N (7.2 lbf) |

**The 4-collet total force is estimated at 20N (4.5 lbf), with an upper bound of 32N (7.2 lbf).**

---

## 2. Ergonomic Force Budget

### 2.1 Human Capability Data

| Action | Comfortable force | Maximum force | Source |
|--------|------------------|---------------|--------|
| One-handed sustained pull | 24 lbs (107 N) | 44 lbs (196 N) initial | Ergoweb force guidelines |
| One-finger push | 10-20 N | 40-70 N | International Encyclopedia of Ergonomics |
| Pinch force (thumb + finger) | 40 N (9 lbs) | 70-90 N | Ergoweb |
| One-handed twist (wrist torque) | 2-4 Nm comfortable | 8-12 Nm max | General ergonomic references |
| One-handed pull (short stroke) | 50-100 N comfortable | 200-400 N max | ResearchGate pulling force study |

Source: Ergoweb force guidelines (https://ergoweb.com/force-guidelines/), Meadinfo ergonomic recommendations (https://www.meadinfo.org/2009/05/recommended-maximum-force-for-human.html)

### 2.2 Force Budget Summary

The 20N (best estimate) to 32N (worst case) total collet force is well within comfortable one-handed capability for any mechanism type:

- **Direct pull:** 20-32N is trivial compared to 107N comfortable pull force. No force multiplication needed.
- **Lever/cam:** Could provide 2-5x multiplication, but unnecessary for force — valuable for converting rotation to axial displacement.
- **Screw thread:** Massive force multiplication available (10-50x) but unnecessary and slow.

**The mechanism choice is driven by kinematics (converting user action to 1.3mm axial displacement on 4 collets), not by force multiplication needs.**

---

## 3. Simultaneous Multi-Fitting Release: Prior Art

### 3.1 John Guest PI-TOOL

The PI-TOOL is a simple flat plastic tool with different-sized U-shaped openings (1/4" and 3/8"). It slides over the tube and pushes the collet inward. It operates on one fitting at a time — no simultaneous release capability. The design confirms that collet release requires only a simple axial push against the collet face.

Source: John Guest collet release tool page (https://www.johnguest.com/us/en/od-tube-fittings/accessories/collet-locking-release-tool)

### 3.2 Industrial Multi-Coupling Plates (Stucchi, etc.)

Stucchi manufactures multi-coupling plates (GR, DP, SV2 series) that simultaneously connect/disconnect 2-10 hydraulic lines with a single lever motion. Key design principles:

- **Lever/cam actuation:** A single lever rotates a cam that provides linear displacement to all couplings simultaneously
- **Guided plate motion:** One plate slides relative to another; all couplings are mounted in one plate and their mating halves in the other
- **Self-alignment:** Tapered guide pins ensure correct alignment before fluid connections engage
- **Anti-cross-connection:** Asymmetric pin patterns prevent wrong orientation

The lever provides force multiplication (typically 3-5x) and converts ~90 degrees of rotation into 10-20mm of linear plate travel. This is overkill for our 1.3mm collet stroke but the principle — plate-on-plate with lever actuation — is directly applicable.

Source: Stucchi multi-coupling plates (https://www.stucchiusa.com/multi-coupling-plates/)

### 3.3 Multi-Tube Manifold Quick Connects (Twintec)

Twintec's BC Series manifolds use integral push-to-connect fittings in a manifold block. Connection is individual (push each tube in). Disconnection uses a release plate — a sliding plate that simultaneously depresses all collets when pushed. This is the closest prior art to our design:

- Multiple push-to-connect fittings in a fixed block
- Single sliding plate releases all collets at once
- Linear motion, no rotation needed

Source: Twintec multi-tube manifolds (https://www.twintecinc.com/)

### 3.4 Water Filter Cartridge Housings

Many under-sink water filter systems use twist-off cartridge housings where the housing twist disconnects the internal fluid connections. The Weddell Duo shower filter uses a counterclockwise twist to release cartridge housings with integrated fluid connections. These demonstrate the twist-to-release paradigm for consumer products.

### 3.5 Bag-in-Box (BIB) Beverage Connectors

BIB QCD (Quick Connect/Disconnect) connectors use a push-twist bayonet-style connection for single fluid lines. The Vitop S-Connector includes auto-shutoff valves. These are single-line devices — no simultaneous multi-line release — but they demonstrate that push-twist is the standard consumer beverage connection paradigm.

---

## 4. Mechanism Options

### 4.1 Option A: Sliding Release Plate (Direct Pull)

**How it works:** A flat plate sits against the collet faces of all 4 fittings. The plate has stepped bores that engage each collet (as described in the geometry document). Pulling the cartridge straight out slides the plate inward relative to the fittings, pushing all 4 collets simultaneously.

**Kinematics:**
- User pulls cartridge toward themselves
- The plate is constrained to the dock (or to the tubes), so relative motion pushes collets inward
- 1.3mm of cartridge travel = 1.3mm of collet displacement

**Force:** 20-32N total, applied as a direct pull. Trivially comfortable.

**Pros:**
- Simplest mechanism — no moving parts beyond the plate itself
- Natural motion (pull to remove)
- No rotation needed
- Plate can be integral to the dock rather than the cartridge

**Cons:**
- Need a latch or detent to hold the cartridge in place during operation
- No tactile "unlocked" signal beyond the latch release
- The plate-to-collet interface must be precise — all 4 collets must contact the plate simultaneously

**Assessment:** Strong candidate. The release plate is already in the design (from the geometry document). The question is how it's actuated.

### 4.2 Option B: Cam Lever (Quarter-Turn)

**How it works:** A lever on the cartridge or dock rotates ~90 degrees. A cam profile on the lever converts rotation to 1.3mm+ of axial plate displacement. The plate then pushes all 4 collets.

**Kinematics:**
- Lever arm: 30-50mm (constrained by cartridge width)
- Cam rise: 1.3mm minimum, 3mm with margin
- Rotation: 60-90 degrees
- Mechanical advantage: lever arm / cam radius, typically 3-10x

**Force multiplication:**
- With a 40mm lever arm and 3mm cam rise at a 10mm cam radius:
  - Torque at lever tip for 32N axial: T = 32N * 0.003m / (2*pi*0.01/0.25) = negligible
  - More practically: user applies ~5-10N at the lever tip, cam delivers 20-50N axially

**Pros:**
- Clear "locked" and "unlocked" positions
- Tactile feedback (lever snaps between positions)
- Can include a detent/latch in the cam profile
- Proven in industrial multi-coupling systems (Stucchi)
- The lever doubles as the cartridge retention mechanism

**Cons:**
- More complex geometry (cam profile)
- Lever protrudes from cartridge or dock (space claim)
- Must be printable — cam surfaces need to be smooth

**Assessment:** Strong candidate. Already contemplated in the project vision ("cam or screw mechanism that unlocks the cartridge"). The lever provides both the retention latch and the collet release in one mechanism.

### 4.3 Option C: Screw Thread (Twist-to-Release)

**How it works:** The cartridge has external threads (or a threaded collar) that mate with the dock. Twisting the cartridge unscrews it, and the thread pitch converts rotation into axial displacement that pushes the collets.

**Kinematics:**
- Thread pitch: 2mm (standard coarse for this size range)
- 1.3mm displacement = 234 degrees of rotation (0.65 turns)
- With 3mm pitch: 156 degrees (0.43 turns)

**Force multiplication:**
- For an M20 thread (reasonable for cartridge OD) with 2mm pitch:
  - Ideal MA = 2 * pi * 10mm / 2mm = 31.4x
  - With friction (efficiency ~30%): effective MA ~ 10x
  - 32N axial / 10 = 3.2N tangential force at the thread radius
  - At a 30mm grip radius (cartridge body): 3.2 * 10/30 = ~1N of user force
- Massively over-engineered for this force level

**Pros:**
- Self-locking (thread friction prevents accidental release under vibration)
- Very high force multiplication (unnecessary here but provides margin)
- Familiar consumer paradigm (unscrew to remove)

**Cons:**
- Slow — requires 0.5-1 full turn to release
- Hard to 3D print clean threads that mate smoothly (especially with FDM layer lines)
- No clear tactile "click" at locked/unlocked positions without additional detent
- Thread wear over repeated cycles
- Counter-intuitive if combined with pull-to-remove (twist then pull is two actions)

**Assessment:** Viable but over-complex. The force multiplication is unnecessary, the speed is poor, and 3D printed threads are unreliable for smooth operation.

### 4.4 Option D: Bayonet (Twist-and-Pull)

**How it works:** Bayonet pins on the cartridge engage L-shaped slots in the dock. Push in, twist ~45-90 degrees to lock. Reverse to unlock. The twist portion of the L-slot can include a ramp that provides 1.3mm of axial displacement.

**Kinematics:**
- Twist angle: 30-90 degrees
- Axial ramp in slot: 1.3-3mm rise over the twist arc
- The ramp angle determines the force multiplication

**Force multiplication:**
- For a 30mm radius bayonet pin at 45 degree twist with 2mm ramp:
  - Arc length = 30mm * pi/4 = 23.6mm
  - Ramp rise = 2mm
  - Ideal MA = 23.6/2 = 11.8x (before friction)
  - With friction: effective MA ~ 5-8x

**Pros:**
- Fast (push + quarter turn)
- Tactile click at locked position (pin drops into detent at end of L-slot)
- Well-proven in consumer products (camera lenses, light bulbs, gas masks)
- Self-aligning (pins guide the cartridge into correct orientation)
- The ramp provides collet displacement directly during the twist
- 3D printable — L-slots are simple geometry

**Cons:**
- Requires two motions (push + twist), though they can be nearly simultaneous
- Pin/slot wear over many cycles (can be mitigated with smooth surfaces)
- Ramp angle must be steep enough to prevent self-locking (or designed to self-lock intentionally in the locked position)

**Assessment:** Strong candidate. Combines alignment, retention, and collet actuation in one elegant mechanism. The L-slot ramp directly cams the release plate during the twist motion.

---

## 5. Mechanism Comparison

| Criterion | Sliding Plate (Pull) | Cam Lever | Screw Thread | Bayonet |
|-----------|---------------------|-----------|--------------|---------|
| User action | Pull | Flip lever, then pull | Twist, then pull | Push + twist |
| Actions to release | 1 (with latch) or 2 (unlatch + pull) | 2 (flip + pull) | 2 (twist + pull) | 1 (twist includes axial) |
| Force multiplication | 1x | 3-10x | 10-30x | 5-12x |
| Force needed (user) | 20-32 N pull | 3-10 N lever tip | 1-3 N twist | 3-6 N twist |
| Tactile feedback | Latch click only | Lever detent click | None (continuous) | Pin-in-slot click |
| Self-locking | Needs separate latch | Cam detent | Yes (friction) | Yes (ramp + detent) |
| Printability (FDM) | Easy | Moderate (cam surface) | Hard (threads) | Easy (slots are simple) |
| Compactness | Best (no protrusions) | Lever protrudes | Good | Good (pins are small) |
| Alignment provision | Needs separate rails | Needs separate rails | Thread is self-centering | Pins self-center |
| Collet actuation | Plate is separate concern | Cam drives plate | Thread drives plate | Ramp drives plate |

---

## 6. Failure Modes and Concerns

### 6.1 Collet-Related Failures

- **Uneven collet engagement:** If the release plate is not perfectly parallel to the fitting faces, some collets may release before others. The user might then pull at an angle, jamming the remaining collets. **Mitigation:** Guide rails or posts that enforce parallel plate travel; generous plate-to-collet engagement depth.

- **Collet stuck (dry O-ring, corrosion):** Over time, the O-ring may stick or the grab ring may corrode slightly, increasing release force. **Mitigation:** Design for 2x the nominal force budget (64N total = still well within comfortable one-handed pull at 107N).

- **Collet not fully released:** If the plate travel is insufficient (less than 1.3mm), the teeth won't fully disengage. The user will feel resistance and may force the tube, damaging it. **Mitigation:** Design for 3mm plate travel (geometry document already specifies this, providing 1.7mm margin).

### 6.2 Mechanism-Related Failures

- **Cam/ramp wear:** Repeated actuation wears the cam surface. PLA and PETG are poor for cam surfaces. **Mitigation:** Use PETG or ABS for wear surfaces; keep cam angles gentle (< 30 degrees); design for replacement.

- **Bayonet pin breakage:** Thin pins under repeated load can fatigue-crack. **Mitigation:** Size pins generously (3-4mm diameter); use PETG for toughness; keep forces low (they already are).

- **Thread cross-threading:** 3D printed threads are rough and easily cross-threaded. **Mitigation:** Avoid threaded mechanism; if used, print threads oversized and use coarse pitch (3mm+).

### 6.3 User Error Modes

- **Pulling without releasing:** User forgets to actuate the release mechanism and yanks the cartridge. The fittings resist (tubes are gripped), and the user may damage tubes or fittings. **Mitigation:** The release mechanism must be in the natural path of removal (e.g., bayonet twist is required before pull is possible; lever must be flipped before cartridge can slide out).

- **Partial insertion:** User pushes cartridge in but doesn't complete the locking motion. Fittings are partially engaged and may leak. **Mitigation:** Tactile/audible click at full lock; visual indicator (alignment mark); consider a switch that detects full lock (already in the design — lock switch for ESP32).

---

## 7. Recommendations

### Primary recommendation: Bayonet mechanism

The bayonet mechanism is the strongest overall candidate because:

1. **Single compound action** — push and twist is a natural, familiar motion (light bulbs, garden hose fittings, camera lenses)
2. **Self-aligning** — bayonet pins guide the cartridge into the correct orientation during insertion
3. **Integrated collet actuation** — the twist ramp directly drives the release plate, no separate mechanism needed
4. **Tactile locking** — pin-in-slot detent provides clear "locked" and "unlocked" positions
5. **Easy to 3D print** — L-slots and pins are simple prismatic geometry, no curved cam surfaces or threads
6. **Force budget is comfortable** — even at worst-case 32N total collet force, a 5mm ramp on a 30mm radius bayonet requires only ~6N of twist force
7. **Prevents pull-without-release** — the cartridge physically cannot be pulled out until the bayonet pins clear the L-slot (unlike a simple latch that can be forgotten)

### Secondary recommendation: Cam lever

If the bayonet proves awkward in the tight space at the bottom-front of the enclosure, a cam lever is the backup. It provides more force multiplication (unnecessary but harmless), clear tactile feedback, and proven industrial precedent (Stucchi multi-coupling plates). The tradeoff is a protruding lever and more complex geometry.

### Not recommended: Screw thread

The force multiplication is unnecessary, 3D printed threads are unreliable, and the slow twist-to-release motion is a poor UX for a cartridge that should feel snappy to remove.

---

## 8. Key Numbers for Downstream Design

| Parameter | Value | Confidence |
|-----------|-------|------------|
| Collet travel needed | 1.3 mm | HIGH (caliper-verified) |
| Design plate travel | 3.0 mm | HIGH (1.7mm margin) |
| Release force per collet | ~5 N (2-8 N range) | MEDIUM (engineering estimate, not measured) |
| Total release force (4 collets) | ~20 N (8-32 N range) | MEDIUM |
| Design force budget | 64 N (2x worst case) | HIGH (conservative engineering margin) |
| Comfortable one-hand pull | 107 N (24 lbf) | HIGH (Ergoweb published guideline) |
| Comfortable one-hand twist (at 30mm radius) | 60-120 N tangential | HIGH (2-4 Nm wrist torque / 0.03m) |
| Bayonet ramp rise | 3 mm over 45-90 deg arc | DERIVED |
| Bayonet pin radius | ~30 mm (half cartridge width) | ESTIMATED |
| Required user twist force (bayonet) | 3-6 N | DERIVED from force budget + ramp geometry |

---

## Sources

### Manufacturer / Product Sources
- John Guest OD Tube Fittings — Collet Locking/Release Tool: https://www.johnguest.com/us/en/od-tube-fittings/accessories/collet-locking-release-tool
- John Guest Speedfit Collet: https://www.johnguest.com/gb/en/products/jg-speedfit/accessories/collet
- ESP Water Products — How John Guest Fittings Work: https://espwaterproducts.com/pages/how-do-john-guest-fittings-work
- Stucchi Multi-Coupling Plates: https://www.stucchiusa.com/multi-coupling-plates/
- Stucchi GR Series: https://www.stucchiusa.com/products/multi-coupling-plates/gr-series/
- Twintec Multi-Tube Manifolds: https://www.twintecinc.com/
- SMC KQ2 One-Touch Fittings: https://www.smcusa.com/products/connectors/fittings/one-touch-fittings/kq2-new-series~87051

### Ergonomic / Human Factors Sources
- Ergoweb Force Guidelines: https://ergoweb.com/force-guidelines/
- Meadinfo — Recommended Maximum Force for Human Hand: https://www.meadinfo.org/2009/05/recommended-maximum-force-for-human.html
- ResearchGate — Maximum Pulling Hand Force Capability: https://www.researchgate.net/figure/The-maximum-pulling-hand-force-capability-N-and-standard-deviation-for-each_fig4_235796926

### Engineering / Mechanism Sources
- Kelston Actuation — Screw Threads and Mechanical Advantage: https://www.kelstonactuation.com/knowledge-base/screw-threads-and-mechanical-advantage
- Wikipedia — Bayonet Mount: https://en.wikipedia.org/wiki/Bayonet_mount
- Amissiontech — Bayonet vs Threaded vs Push-Pull Locking Mechanisms: https://www.amissiontech.com/news/differences-between-bayonet-threaded-and-push-pull-locking-mechanisms.html
- IQS Directory — Quick Release Couplings: https://www.iqsdirectory.com/articles/quick-connector.html
