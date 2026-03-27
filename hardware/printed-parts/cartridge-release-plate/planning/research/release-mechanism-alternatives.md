# Release Mechanism Alternatives — Full Solution Space Exploration

The current design uses a cartridge-side release plate with stepped bores, driven by an eccentric cam lever, pressing 4 John Guest collets simultaneously. The dock is entirely passive. This architecture was derived from strong prior art (bicycle QR, server blade ejectors, power tool batteries) and extensive analysis of collet release mechanics.

This document challenges every assumption in that design. The goal is not to prove the current design wrong, but to understand what was left on the table and why. Some alternatives explored here are clearly worse — they are included anyway so the full solution space is documented.

**System context**: Soda flavor injector under a kitchen sink. Cartridge holds 2 peristaltic pumps (150 x 80 x 130mm, ~1.8 lbs / 820g). 4 fluid connections (2 per pump: inlet and outlet). Swap frequency: maybe once every few weeks to months (pump tubing replacement, deep cleaning). Not a daily operation. A clean cycle always runs before cartridge removal (software-enforced or physically locked), so residual fluid in the cartridge and dock is water/air, not sticky concentrate.

---

## 1. Do We Even Need a Release Plate?

The release plate is the most complex part of the current design — stepped bores with three concentric diameters, tight tolerances on lip width (2.25mm annular), linear guide features to prevent tilt, and a cam-to-plate interface. It demands careful 3D print orientation and may need multiple iterations to get the bore dimensions right. Is all of this necessary?

### 1a. "Just Pull" — Individual Hand Disconnects

John Guest fittings are designed for tool-free hand disconnect. The user pushes the collet with a fingertip and pulls the tube out. For 1/4" fittings, the collet is small enough that a fingertip covers most of its face, making one-sided press failure (Section 4.2 of collet-release.md) less of a concern than with larger fittings.

**How long does one disconnect take?**

With practice, a single John Guest 1/4" disconnect takes approximately 3-5 seconds: position fingertip on collet, push inward (~2-3N, very light), pull tube with other hand. First-timers take 8-15 seconds as they learn the feel. The main time cost is not the physical action but the cognitive overhead of "did I push hard enough? Is it released?"

**Four sequential disconnects:**

- Practiced user: 4 x 5 seconds = 20 seconds, plus repositioning between fittings, call it 30-40 seconds total
- First-timer: 4 x 15 seconds = 60 seconds, plus fumbling
- Under a sink (awkward angle, poor visibility, reaching overhead or into a cabinet): add 50-100% to above times

**Total cartridge swap time comparison:**

| Phase | With Release Plate | Without (Hand Disconnect) |
|---|---|---|
| Open cabinet, locate cartridge | 10s | 10s |
| Release mechanism | 2s (flip lever) | 30-60s (4 individual disconnects) |
| Withdraw cartridge | 2s | 2s |
| Insert new cartridge | 3s (slide in, tubes auto-engage) | 3s + 30-60s (4 individual reconnects) |
| Lock mechanism | 2s (flip lever) | 0s (auto-locked by collets) |
| **Total** | **~19 seconds** | **~75-135 seconds** |

The time difference is real but not enormous. The bigger issue is **user experience under adverse conditions**:

- Under a sink, the fittings face a wall. The user reaches in, often working by feel. Individual collet presses require fingertip precision on a 15.10mm ring while simultaneously pulling a tube straight out — this is a two-handed operation per fitting.
- The release plate + lever converts this to a one-handed operation (flip lever, slide cartridge).
- For a product that someone else might use (spouse, renter, property manager), "flip lever and pull" is dramatically more approachable than "push each of these 4 tiny rings while pulling the tubes."

**Failure modes comparison:**

| Failure Mode | Hand Disconnect | Release Plate |
|---|---|---|
| Collet tilt from uneven press | Moderate risk (fingertip covers most of collet) | Low risk (stepped bore constrains collet) |
| Tube scored by partial release | Moderate (user pulls before fully releasing) | Low (cam holds plate in position) |
| One fitting left connected | Possible (user forgets one) | Impossible (all 4 release together) |
| Mechanism jam | N/A | Possible (plate binding, cam wear) |

**Verdict**: Hand disconnect is viable and eliminates the entire release plate mechanism. It is clearly worse for user experience but acceptable if the swap frequency is low enough (monthly or less) and the user is technically comfortable. For a product intended for non-technical users, the release plate justifies its complexity.

### 1b. Permanent Release Sleeves in the Dock

What if the dock has fixed cylindrical sleeves permanently positioned around each John Guest fitting, and the act of withdrawing the cartridge somehow engages these sleeves to release the collets?

**The fundamental problem**: When the cartridge is withdrawn, the tube moves WITH the cartridge — away from the fitting. The collet must be pushed TOWARD the fitting (inward) to release. So the release motion is in the opposite direction from the withdrawal motion. A fixed sleeve around the fitting doesn't help because the tube is moving away, not pushing anything toward the fitting.

**Could a ramp on the cartridge body engage a dock-side plate?**

```
    CARTRIDGE                          DOCK

    ┌──────────┐                      ┌───────────┐
    │          │   ramp surface        │  fitting  │
    │     /════╗  ←──────────────     │  collet   │
    │    /     ║  dock plate rides    │           │
    │   /      ║  up ramp as cart-    │           │
    │  /       ║  ridge withdraws     │           │
    └──────────┘                      └───────────┘
         ← withdrawal direction
```

As the cartridge is pulled back (left), the dock plate would ride along the ramp surface. If the ramp converts the horizontal withdrawal motion into a forward push on the plate (toward the fittings), this could work. But:

1. The ramp angle must convert ~20mm of cartridge withdrawal travel into ~3mm of plate forward travel. That is a 3/20 = 15% grade, or about 8.5 degrees. Mechanically feasible.
2. The plate must be spring-returned (pushed back away from fittings when the cartridge is fully inserted, so the collets can grip).
3. The dock now has moving parts (the plate + springs). This violates the "passive dock" principle.
4. There is a chicken-and-egg problem: the collets grip the tubes, preventing withdrawal. For the ramp to engage the release plate, the cartridge must already be moving. But the cartridge cannot move until the collets release.

Problem #4 is the fatal flaw. The collets must release BEFORE the tubes can move, but the ramp-driven mechanism requires the tubes to move BEFORE the collets release. There is no geometry that resolves this. You would need an initial "break-free" mechanism (like a lever) to start the motion, at which point you already have a lever and might as well use it directly.

**Verdict**: Dock-side fixed sleeves do not work with John Guest fittings because the release motion opposes the withdrawal motion. The chicken-and-egg problem makes ramp-driven release impossible without a separate initial release action.

### 1c. Modified Fittings — Alternatives to John Guest Push-to-Connect

What if we abandon John Guest fittings entirely and use a different fluid coupling technology? This section surveys alternatives.

#### Dry-Break Quick-Disconnect Couplings (Hansen, Parker, etc.)

Dry-break couplings are used in applications where zero spillage during disconnect is critical (racing fuel, medical, chemical transfer). Both halves contain spring-loaded valves that seal when disconnected.

**Hansen Beverage series:**

| Parameter | Value |
|---|---|
| Material | 316 stainless steel |
| Valve | Double shut-off (both halves seal) |
| Connection sizes | 1/4" and 3/8" NPT or hose barb |
| Disconnect method | Pull-to-disconnect (sleeve retraction) |
| Price | ~$30-60 per coupling pair |
| Price for 4 connections | ~$120-240 |

**Parker Legris dry-break**: Similar pricing, available in plastic (cheaper) and metal. The 9000 series offers food-grade options.

**Pros:**
- Zero drip on disconnect — cleanest possible swap
- Extremely robust, designed for thousands of cycles
- Positive click engagement

**Cons:**
- Extremely expensive ($120-240 for 4 connections)
- Massive overkill for a gravity-fed, near-zero-pressure system
- Heavy (stainless steel versions)
- Still individual disconnect per coupling

**Verdict**: Dry-break couplings solve a problem we do not have (zero-drip at pressure). The cost is prohibitive for a hobby/prototype project.

#### Barb Fittings with Spring Clips

The simplest possible fluid connection: a barbed fitting pushed into soft tubing, retained by a spring clip or zip tie.

| Parameter | Value |
|---|---|
| Connection type | Push barb into soft tubing |
| Disconnect method | Remove clip, pull tubing off barb |
| Force to disconnect | ~10-30N depending on barb profile and tubing stiffness |
| Price | ~$0.50-1 per barb fitting, ~$0.10 per spring clip |
| Price for 4 connections | ~$2-4 |

**Pros:**
- Cheapest possible option
- No mechanism needed — purely manual
- Extremely reliable seal (barb + soft tubing + clip)

**Cons:**
- Not quick-change at all — removing tubing from barbs requires significant force and often damages tubing
- Spring clip removal and reinstallation is fiddly
- Tubes must be soft (silicone/BPT) at the connection point — cannot use hard nylon stubs
- Not a viable "cartridge swap" mechanism; this is permanent installation hardware

**Verdict**: Barb fittings are for permanent connections, not swappable cartridges. Not viable.

#### O-Ring Compression Fittings (Custom)

A custom fitting where a hard tube stub pushes into a bore containing an O-ring. The O-ring provides the seal via compression. Retention via friction, magnetic force, or mechanical latch.

```
    Cartridge side:        Dock side:

    ─────┐                ┌──────────
         │   O-ring       │
    tube ├═══╤═══════════>│  bore
    stub │   O-ring       │
    ─────┘                └──────────
```

| Parameter | Value |
|---|---|
| Seal mechanism | O-ring compressed between tube OD and bore ID |
| Typical O-ring: AS568-010 | 5/16" ID x 7/16" OD x 1/16" cross-section |
| Tube OD | 6.35mm (1/4") |
| Bore ID | 6.35mm + 2x O-ring compression = ~7.5mm |
| Insertion force | ~2-5N per fitting (O-ring friction) |
| Withdrawal force (friction only) | ~2-5N per fitting |
| Retention at pressure | Poor without mechanical retention |

**Pros:**
- Extremely simple dock geometry (just a bore with an O-ring groove)
- Easy to 3D print and iterate
- Cheap

**Cons:**
- O-ring friction alone does not retain the tube reliably — any vibration or accidental bump could pull a tube loose
- Must be combined with a mechanical retention method (latch, magnet, etc.)
- This is essentially reinventing push-to-connect fittings but worse

**Verdict**: O-ring seals are a viable sealing mechanism but require a separate retention system. John Guest fittings are essentially this concept perfected and mass-produced. Using raw O-rings instead of John Guest fittings only makes sense if the retention mechanism is fundamentally different (see Section 4: Magnetic Retention).

#### Bayonet-Style Fluid Connectors

Used in industrial and military applications. A short push-and-twist motion locks the coupling.

These exist commercially (Staubli, Rectus, Parker) but are designed for high-pressure hydraulic applications and cost $50-200+ per coupling. They are massive overkill for a gravity-fed beverage system. No food-grade 1/4" bayonet fluid connectors exist at consumer price points.

**Verdict**: No viable consumer/hobbyist bayonet fluid connectors exist in the right size and price range. The twist-lock concept is better applied at the cartridge level (see Section 2) rather than per-fitting.

### 1c Summary Table

| Fitting Type | Cost (4 connections) | Quick-Change? | Release Plate Needed? | Viability |
|---|---|---|---|---|
| John Guest push-to-connect | $8-12 | Yes (with plate) | Yes | Chosen design |
| John Guest (hand disconnect) | $8-12 | Slow (individual) | No | Viable, poor UX |
| Hansen dry-break | $120-240 | Slow (individual) | No | Too expensive |
| Barb + spring clip | $2-4 | No | No | Not quick-change |
| Custom O-ring | $1-2 | Depends on retention | No | Needs retention system |
| Bayonet fluid connector | $200-800 | Yes | No | Way too expensive |

**Key insight**: Every off-the-shelf alternative to John Guest fittings either costs dramatically more or still requires individual per-fitting disconnects. The release plate mechanism is the cheapest way to achieve simultaneous disconnect of 4 connections.

---

## 2. Twist-Lock (Quarter-Turn Bayonet)

The cam-lever.md research identified quarter-turn bayonet as extremely strong prior art for under-sink cartridges. Water filter cartridges (3M, Waterdrop, GE, DuPont QuickTwist) use exactly this: push up, twist 90 degrees, locked. But the current mating-face.md design chose an eccentric cam lever instead. Why?

The answer is in the tube connection physics. Water filter cartridges have their fluid connections made by O-ring seals that are concentric with the rotation axis. The twist motion compresses the O-rings axially. John Guest push-to-connect fittings have tubes that insert linearly. A twist after insertion torques the tubes, which is a problem.

### How a Twist-Lock Could Work

**Architecture**: The cartridge pushes into the dock, then rotates 90 degrees around the insertion axis. Bayonet lugs on the cartridge engage retention slots in the dock. The rotation provides both retention (lugs in slots) and, potentially, collet release (via a helical cam surface).

```
    FRONT VIEW OF DOCK (looking into the dock cavity)

    ┌──────────────────────────────────────┐
    │                                      │
    │    ╔═══╗  bayonet        ╔═══╗      │
    │    ║   ║  slot           ║   ║      │
    │    ╚══>║                 ╚══>║      │ Lugs enter wide opening,
    │        ║                     ║      │ rotate into narrow slot
    │   ┌─fitting──┐  ┌─fitting──┐        │
    │   │  ○  ○    │  │  ○  ○   │        │ 4 John Guest fittings
    │   └──────────┘  └─────────┘        │ in dock wall
    │                                      │
    │    ╔══<║                 ╔══<║      │
    │    ║   ║                 ║   ║      │
    │    ╚═══╝                 ╚═══╝      │
    │                                      │
    └──────────────────────────────────────┘
```

### The Tube Torsion Problem

When the cartridge rotates 90 degrees, the tube stubs (rigidly fixed to the cartridge) rotate with it. But the tubes are already inserted into the John Guest fittings (fixed to the dock). The result:

- 4 hard nylon tubes, each inserted ~15mm into a fitting, experience 90 degrees of torsion at their fixed end
- A 1/4" OD hard nylon tube inserted 15mm into a collet fitting: the tube cannot rotate freely because the collet teeth grip its surface
- The torsion would either: (a) score the tube surface against the collet teeth, (b) break the tube, or (c) require enough force to overcome collet friction, defeating the purpose

**This is the fatal flaw for "insert then twist" with John Guest fittings.** The collet teeth are specifically designed to resist tube movement. Twisting a tube that is gripped by collet teeth is mechanically fighting the fitting's core function.

### Could Twist Happen Before Tube Engagement?

A two-stage approach: cartridge enters the dock and twists to lock onto bayonet lugs FIRST, then a separate axial motion pushes the tubes into the fittings.

```
    Stage 1: Insert and twist (no tube engagement)

    ┌──────────┐          gap          ┌──────┐
    │ cartridge│                       │ dock │
    │   body   │   tube stubs          │ wall │
    │   ═══>   │   ════════>   ←gap→  │fitting│
    │          │                       │      │
    └──────────┘                       └──────┘
                  bayonet lugs
                  engage during twist

    Stage 2: Axial push (lever or cam drives cartridge forward)

    ┌──────────┐                       ┌──────┐
    │ cartridge│   tube stubs          │ dock │
    │   body   │   ══════════════════=>│fitting│
    │          │                       │collet │
    └──────────┘                       └──────┘
```

This eliminates the torsion problem because the tubes only experience linear insertion, never rotation. But it creates new problems:

1. **Two-stage operation**: The user must push, twist, then push again. Three distinct motions instead of one. This is worse UX than the current "slide in, flip lever" (two motions).
2. **The second axial push still needs force amplification** to overcome 4 John Guest insertion forces (~5-10N each = 20-40N total). A cam or lever is still needed for this push. So we have bayonet lugs PLUS a cam/lever — more complexity than the current design.
3. **The release sequence is the reverse**: lever/cam retracts tubes from fittings, then twist to unlock bayonet, then pull out. But retracting tubes from John Guest fittings still requires collet release. We are back to needing a release plate.

### Twist-Lock With Helical Cam Driving Release Plate

The most interesting variant: the 90-degree twist itself drives a release plate forward via a helical cam ramp on the cartridge body.

```
    Side view (cross-section):

    Cartridge body (rotates)          Dock frame (fixed)

    ┌──────────────────┐              ┌──────────┐
    │  helical ramp    │              │ follower  │
    │  ╱               │              │  pin      │
    │ ╱  (rises 3mm    │              │  │        │
    │╱    over 90 deg) │              │  ▼        │
    │                  │              │ [release  │
    │                  │              │  plate]   │
    └──────────────────┘              └──────────┘

    As cartridge rotates, ramp pushes follower pin,
    which pushes release plate into collets
```

But this puts the release plate in the dock, not the cartridge. The dock is no longer passive. And the dock must have a guided release plate, follower pin, and return spring. This is more complex than the current design (where the plate is on the cartridge).

### Dimensional Analysis

For a 150mm wide cartridge, bayonet lugs would be positioned near the corners:

| Parameter | Value |
|---|---|
| Cartridge diameter (inscribed circle) | ~80mm (H dimension) |
| Lug size (typical) | 8-12mm wide x 4-6mm deep |
| Slot depth | 3-5mm |
| Rotation angle | 90 degrees |
| Arc length at 40mm radius over 90 deg | ~63mm |
| Ramp rise (for 3mm plate travel) | 3mm over 63mm arc = 2.7 degree helix angle |

The 2.7-degree helix angle is extremely shallow — practically self-locking under friction. The user would need to twist with significant force to overcome the release plate springs plus collet release force, all through a 2.7-degree ramp. Estimated torque: (20N release force) / tan(2.7deg) = ~424N at the ramp contact, requiring ~17 N*m of torque at the cartridge OD. That is a firm two-handed grip twist — not one-handed operation.

### Verdict on Twist-Lock

The twist-lock is elegant for water filter cartridges where the fluid connections are O-ring seals concentric with the rotation axis. It does not work well with John Guest push-to-connect fittings because:

1. Tubes cannot be twisted after insertion (collet teeth resist rotation)
2. Two-stage insert-twist-push adds complexity and operations
3. Helical cam driving a release plate requires the dock to have moving parts
4. The shallow helix angle needed for 3mm of travel results in high torque requirements
5. One-handed operation is difficult with a twist-lock under a sink

The current eccentric cam lever is superior for this application because it decouples the retention mechanism (cam over-center lock) from the fluid connection mechanism (linear push-to-connect), and both are operated with a single lever flip.

---

## 3. Dock-Side Release Mechanisms

The current design follows the "ejector on the blade" pattern: all mechanism is on the cartridge. But there are valid reasons to put mechanism on the dock instead.

### 3a. Dock-Side Lever

A lever permanently mounted on the dock frame — like a stapler handle or paper cutter lever. The user flips it to release all collets, pulls out the cartridge, inserts a new one, and flips the lever to lock.

```
    Side view:

    ┌─── lever (pivots here) ──────────────╗
    │                                      ║ handle
    │   ┌─────────────┐    dock            ║ (lifts up
    │   │ release     │    frame           ║  to release)
    │   │ plate       │◄──cam──╗           ║
    │   │  (pushes    │        ║           ║
    │   │   collets)  │    ╔═══╝           ║
    │   └─────────────┘    ║               ║
    │                      ╚═══════════════╝
    │
    └── fittings in dock wall ──
```

**The collet direction problem**: John Guest fittings mount in the dock wall with their collet faces pointing OUTWARD (toward the cartridge). A dock-side release plate must push the collets INWARD (toward the dock interior — the same direction the tubes enter from). This means the release plate sits on the cartridge side of the fittings, between the fittings and the cartridge.

This is actually the same position as the current cartridge-side release plate. The difference is ownership: the plate stays with the dock, not with the cartridge.

**Pros:**
- Lever is always in the same place (user doesn't have to find it on each cartridge)
- Cartridge becomes a simple dumb tube-and-pump assembly — cheaper to manufacture, easier to iterate
- The lever is in a fixed, known position for blind operation
- One lever serves all cartridges forever (vs. one lever per cartridge in the current design)

**Cons:**
- Dock has moving parts (plate, cam, lever pivot) that can wear or break
- If the dock mechanism breaks, ALL cartridges are affected (single point of failure in a permanent installation)
- The release plate must clear the cartridge during insertion/removal — it needs to retract far enough that tube stubs pass through freely
- More complex dock manufacturing and assembly

**Practicality assessment**: This is a viable architecture. The lever could mount on top of the dock frame, flipping upward to push the release plate forward (into the collets). The plate retracts via a return spring when the lever is lowered. The main downside is the dock is no longer a simple "box with fittings" — it becomes a mechanism in its own right.

### 3b. Cartridge Insertion/Removal Drives Dock Mechanism

The ultimate "zero extra actions" ideal: pushing the cartridge in connects everything, pulling it out disconnects everything. No lever, no twist, no button.

**The fundamental constraint**: John Guest fittings provide push-in connection automatically. The challenge is release. The collets must be actively released before the tubes can be withdrawn. Pulling the cartridge without releasing collets = the collets grip harder.

**Could the first few millimeters of withdrawal drive a release plate?**

Imagine a dock-side release plate connected to the cartridge body via a lost-motion coupling. When the cartridge starts to pull back, the coupling engages and pushes the plate forward:

```
    Fully inserted:

    cartridge ──────plate──fittings
               │    ↑
               │    plate retracted (collets grip)
               │

    Partially withdrawn (first 3mm):

    cartridge ←─────plate──fittings
               │    ↑
               lost-motion hook pulls plate forward
               plate pushes collets (release!)

    Further withdrawn:

    cartridge ←←←←←──plate──fittings
                      ↑
                      plate held forward by spring detent
                      tubes slide out freely
```

The problem is that the tube stubs are rigid — they cannot compress or stretch. If the cartridge moves back 3mm, the tubes move back 3mm. With collets still gripping, the tubes cannot move at all. So the cartridge cannot create the initial 3mm of "lost motion" separation because the collets prevent any tube movement.

**A compliant tube connection could solve this**: If the tube stubs had 3mm of spring-loaded axial compliance (a spring between the tube stub and the cartridge body), then the cartridge could move back 3mm while the tubes stay put (compressed against their springs). During those 3mm, the lost-motion coupling pushes the release plate forward. Once the collets release, the springs push the tubes out of the fittings as the cartridge continues to withdraw.

This is mechanically possible but adds 4 spring-loaded tube mounts to the cartridge — similar complexity to the release plate, but distributed across 4 points instead of one plate.

**Verdict**: Zero-extra-action dock mechanisms are theoretically possible but require compliant tube mounts that add as much complexity as they remove. The "lost motion" approach is an interesting concept that might be worth exploring if the spring-loaded tube mount can be made simple enough.

### 3c. Spring-Loaded Dock Plate (Normally-Released)

A dock-side release plate that is spring-loaded into the collet-release position (plate pushes collets inward). The fittings are normally released. When the cartridge is inserted, the cartridge body pushes the plate back against the springs, allowing the collets to grip the tubes.

**Sequence analysis:**

1. **Cartridge out, plate forward (springs extended)**: The plate pushes all 4 collets inward. The fittings are in a permanent "released" state. No tubes are gripped.

2. **Cartridge inserting**: The cartridge's front face contacts the plate. As the cartridge pushes further in, it pushes the plate backward (compressing springs), pulling the plate away from the collets. The collets return to their gripping position.

3. **Tubes enter fittings**: While the cartridge pushes the plate back, the tube stubs extend through the plate holes and into the now-gripping fittings. The collets grab the tubes.

4. **Fully inserted**: The cartridge holds the plate compressed. The collets grip the tubes. Everything is connected.

5. **Cartridge removal**: The user pulls the cartridge back. As the cartridge moves back, the springs push the plate forward into the collets. The collets release. The tubes slide out freely.

**Wait — does this actually work?**

The critical moment is step 5. As the user pulls the cartridge back, two things happen simultaneously:
- Springs push the plate forward (toward fittings), releasing collets
- Cartridge (with tubes) moves backward (away from fittings)

The timing is key. The plate must push the collets into release BEFORE the tubes move far enough to clear the collet teeth (and get scored). With ~1.5-2mm of collet travel and tubes inserted ~15mm, there is ample margin — the springs can release the collets in the first 1-2mm of cartridge withdrawal, and the tubes still have 13mm of insertion depth remaining.

**This actually works.** The springs must be strong enough to depress 4 collets (~12-20N total) plus overcome friction. The cartridge insertion force must overcome the springs (12-20N extra, on top of the ~20-40N tube insertion force). Total insertion force: ~32-60N (7-13 lbf). This is a firm push but manageable.

**Potential problems:**

1. **Timing sensitivity**: If the user jerks the cartridge out quickly, the springs may not depress the collets fast enough. Small spring mass and short travel (2mm) means the spring response time is on the order of milliseconds — not a real concern.

2. **Plate alignment**: The plate must remain parallel to the fitting faces. Same tilt concern as the cartridge-side plate, requiring guide pins/rails.

3. **Insertion force**: 32-60N (7-13 lbf) is noticeably harder than the current design where the lever provides mechanical advantage. A firm push with one hand is possible but less elegant.

4. **Partial insertion**: If the cartridge is not pushed in far enough, the plate may not fully retract, leaving collets partially released. The tubes would be in a partially-gripped state. A detent or latch at the fully-inserted position would mitigate this.

5. **No positive lock**: The cartridge is held only by collet grip + friction with the dock. There is no over-center cam or mechanical latch. Accidental bumps could partially dislodge the cartridge.

**This is the most interesting alternative in this entire document.** It eliminates the lever, cam, and cartridge-side mechanism entirely. The trade-offs are higher insertion force and no positive lock feedback.

**To make it work well, add a simple latch**: A spring-loaded latch tab on the dock that clicks over a feature on the cartridge when fully inserted. Press the tab to release. Now you have:
- Push to insert (springs + tube insertion = firm push)
- Click confirms full insertion
- Press tab and pull to remove (tab releases latch, springs release collets, cartridge slides out)

This is the power tool battery paradigm: slide until click, press button and slide out.

---

## 4. Magnetic Retention Without Collet Release

What if we eliminate John Guest fittings entirely and use the simplest possible fluid connection: a tube pushing into an O-ring bore, retained by magnets?

### Architecture

```
    CARTRIDGE                         DOCK

    ┌──────────┐                     ┌──────────┐
    │          │   tube stubs         │  O-ring  │
    │  [N52    │   ═══════════>      │  bores   │
    │  magnets]│   ═══════════>      │          │
    │          │                     │  [steel  │
    │          │                     │   plate] │
    └──────────┘                     └──────────┘

    Magnets in cartridge face attract steel plate
    behind dock wall. Pulls cartridge firmly into dock.
    O-rings in dock bores seal around tube stubs.
```

### Force Analysis

**Water pressure force trying to push tubes out:**

The system is gravity-fed from bags above (hopper system). Maximum head pressure is approximately:
- Bag height above fittings: ~12 inches (0.3m)
- Pressure: 0.3m x 9810 N/m^3 = ~2940 Pa = ~0.43 PSI
- Force on each tube stub (area = pi x (3.175mm)^2 = 31.7 mm^2):
  - F = 2940 Pa x 31.7e-6 m^2 = 0.093 N per tube
  - Total for 4 tubes: 0.37 N

This is essentially nothing. Even the peristaltic pump's suction/discharge pressure adds only ~1-3 PSI, which translates to ~0.2-0.7 N per tube. Total ejection force from water pressure across all 4 tubes: **~1-3 N (0.2-0.7 lbf)**.

**O-ring friction (retention):**

A standard AS568-010 O-ring (1/16" cross-section) compressed ~15% around a 1/4" tube generates ~1-3N of friction force per seal. With 4 seals: ~4-12N total friction retention.

**Magnetic force needed:**

The magnets need to resist: water pressure (~3N) + accidental bump forces (~5-20N) minus O-ring friction (~4-12N). Net magnetic force needed: ~10-25N to feel secure.

**Achievable magnetic force:**

A single 1/2" diameter x 1/4" thick N52 neodymium disc magnet pulls ~6-8 lbs (27-36N) against a steel plate at contact. Four such magnets (one near each tube) would provide ~108-144N of pull — vastly more than needed.

Even 1/4" diameter x 1/8" thick N52 magnets pull ~2-3 lbs (9-13N) each. Four of these: 36-52N total — still plenty.

**Cost**: N52 disc magnets from K&J Magnetics: ~$1-3 each. Four magnets: ~$4-12.

### O-Ring Seal Design

Each dock bore needs:

| Parameter | Value |
|---|---|
| Bore ID | 6.35mm + O-ring compression clearance = ~6.8-7.0mm |
| O-ring | AS568-007 (3/16" ID x 5/16" OD x 1/16" CS) or similar |
| O-ring material | Silicone (FDA-grade) or EPDM |
| Tube stub insertion depth | 8-12mm (enough for stable O-ring seal) |
| Seal reliability | Good for static seal at low pressure |

The O-ring must be captured in a groove in the dock bore. This groove is easy to machine or 3D print (SLA preferred for bore surface finish; FDM layer lines may compromise the seal).

### Disconnect Sequence

1. User grips cartridge and pulls straight out
2. Pull force must overcome: magnetic attraction + O-ring friction = ~50-150N total (11-34 lbf)
3. This is a firm pull but manageable

**Problem**: 50-150N of pull force is too much for comfortable one-handed operation. The magnets that provide secure retention also make removal difficult. This is the fundamental tension of magnetic retention: strong enough to hold = hard to remove.

**Mitigation — Peel instead of pull**: If the cartridge pivots (tilts) rather than pulling straight out, the magnets break contact progressively rather than all at once. Peeling 4 magnets off a plate one-at-a-time requires roughly 1/4 of the straight pull force. A tilting removal motion (grab one edge, tilt upward) reduces the removal force to ~12-38N (3-8 lbf) — much more comfortable.

But tilting the cartridge means the tubes withdraw at an angle, not straight. O-ring bores tolerate some angular misalignment (maybe 5-10 degrees), but the tubes are rigid. At 10 degrees of tilt across 4 tubes spaced 15mm apart, the differential withdrawal distance is 15mm x sin(10deg) = ~2.6mm. This could cause one tube to bind in its bore while the opposite tube is already out.

### Assessment

| Aspect | Rating | Notes |
|---|---|---|
| Mechanical complexity | Excellent | No moving parts. Magnets + O-rings only. |
| Seal reliability | Moderate | O-ring in 3D-printed bore may leak at layer lines. SLA print or machined bore needed. |
| Insertion feel | Good | Magnets snap cartridge into alignment at close range. Satisfying. |
| Removal effort | Poor to Moderate | Straight pull is too high; peel/tilt is manageable but risks tube binding. |
| Drip management | Acceptable | Tubes drip when pulled, but the firmware enforces a clean cycle before removal -- the drip is water only. |
| Retention security | Good | Magnets won't accidentally release. |
| Prototype cost | Excellent | ~$15-20 total (magnets + O-rings + steel plate) |

**Verdict**: Magnetic retention with O-ring seals is the simplest possible mechanism and works at the near-zero pressures of this system. The main weakness is removal force -- magnets strong enough to feel secure are hard to pull off. The firmware enforces a clean cycle before removal, so any drip is a few mL of water -- a minor concern. For a prototype/proof-of-concept, this is worth trying because it proves whether the O-ring seal works before investing in John Guest fittings and a release plate. If the O-ring seal works, the design could evolve to add a lever-actuated separation mechanism later.

---

## 5. Captive-Tube Designs

What if the tubes never disconnect during a cartridge swap?

### Flexible Tube Bridges

Short lengths of flexible silicone tubing (4-6 inches) connect the dock fittings to the cartridge. The cartridge slides out on rails, and the flexible tubes bend/stretch to allow access.

```
    DOCKED:

    ┌──────────┐  flex tube  ┌──────────┐
    │ cartridge│═════════════│   dock   │
    │          │═════════════│  (fixed) │
    └──────────┘             └──────────┘

    EXTENDED ON RAILS:

    ┌──────────┐                          ┌──────────┐
    │ cartridge│═══╗  flexible tubes      │   dock   │
    │          │   ║  bend/stretch         │  (fixed) │
    └──────────┘   ╚══════════════════════└──────────┘
                   ← 4-6" of extension →
```

**Silicone tubing flexibility**: 1/4" OD silicone tubing has a minimum bend radius of approximately 1-1.5 inches (25-38mm). A 4-inch length of tubing can accommodate a ~90 degree bend without kinking. If the cartridge slides out 6 inches on rails, 4-inch tubes would be at roughly 90 degrees of bend — at the limit of their capability.

**Would this provide enough access?** If the cartridge slides out 6 inches, the user can access the cartridge body from the front and top. For pump tubing replacement (the primary swap reason), the user needs to open the cartridge housing and swap the pump head tubing. This requires two-hand access to the cartridge. Six inches of extension should be sufficient for this.

**The key realization**: With captive tubes, the cartridge never fully separates from the dock. Pump maintenance is done in-place (like an oil change on a car — you access the engine, you don't remove it). This works if:
1. The cartridge housing opens easily (hinged lid or removable top)
2. Pump tubing can be swapped without removing the pump from the cartridge
3. The 6-inch extension provides enough room

**When full disconnection IS needed** (deep cleaning, replacing a pump motor, etc.), the user disconnects the John Guest fittings individually — the "just pull" approach from Section 1a. This is an infrequent operation (annually or less), so the slow individual disconnect is acceptable.

**Pros:**
- Eliminates the release plate, cam, lever — the entire release mechanism
- No dripping during routine maintenance (tubes stay connected)
- Tubes are never stressed by disconnect/reconnect cycles
- Simplest possible dock (just rails and a fixed tube routing)

**Cons:**
- Cartridge never fully separates during routine maintenance — can't swap in a pre-loaded cartridge
- 4-6 flexible tubes constrain how far the cartridge can slide out
- Tubes experience repeated flexing during slide-in/slide-out cycles — fatigue over time
- Tube routing becomes messy (4 flexible tubes draped between two positions)
- The "pre-loaded spare cartridge" concept does not work — you can't have a second cartridge ready to swap in

**Verdict**: Captive-tube designs work well if the primary maintenance operation is in-place pump tubing replacement, not whole-cartridge swapping. This is actually a legitimate architecture — many industrial pump systems are maintained in-place rather than swapped. The trade-off is losing the "grab and go" quick-swap experience. Whether this matters depends on how the user wants to interact with the system.

---

## 6. The "Drawer" Approach

What if the dock is mounted on drawer slides, and pulling it out brings the cartridge to the user?

### Architecture

```
    CLOSED (normal operation):

    ┌─ cabinet wall ─────────────────────────────────────┐
    │                                                     │
    │    ┌── drawer slide ──────────────────────────┐     │
    │    │                                          │     │
    │    │   ┌─────────────┐  ┌──────────────────┐  │     │
    │    │   │  cartridge  │  │      dock        │  │     │
    │    │   │             │  │                  │  │     │
    │    │   └─────────────┘  └──────────────────┘  │     │
    │    │                                          │     │
    │    └──────────────────────────────────────────┘     │
    │                                                     │
    └─────────────────────────────────────────────────────┘

    OPEN (pulled out for cartridge swap):

    ┌─ cabinet wall ───────────────────────────────────────────┐
    │    ┌─ slide rail (fixed) ────────────────────────┐       │
    │    │                                             │       │
    │    └─────────────────────────────────────────────┘       │
    │                                                           │
    │    ┌── drawer (extended) ──────────────────────────┐      │
    │    │                                              │      │
    │    │   ┌─────────────┐  ┌──────────────────────┐  │      │
    │    │   │  cartridge  │  │      dock            │  │      │
    │    │   │  (now       │  │                      │  │      │
    │    │   │  accessible)│  └──────────────────────┘  │      │
    │    │   └─────────────┘                            │      │
    │    │                                              │      │
    │    └──────────────────────────────────────────────┘      │
    └──────────────────────────────────────────────────────────┘
```

### Drawer Slides for Under-Sink

Appropriate drawer slides:

| Parameter | Requirement | Available Options |
|---|---|---|
| Weight capacity | ~10 lbs (dock 3-5 lbs + cartridge 1.8 lbs + tubing/fittings) | 50-100 lb slides are standard and cheap |
| Extension length | 12-18 inches (full extension) | Standard 12", 14", 16", 18" full-extension slides |
| Corrosion resistance | Under-sink moisture exposure | Zinc-plated, stainless steel, or powder-coated options |
| Width | Side-mount, standard profile | 1/2" profile side-mount slides |
| Price | Budget-friendly | $8-15 per pair (Amazon, Home Depot) |

Recommended: **12-inch full-extension ball-bearing slides**, zinc-plated or powder-coated. 50+ lb capacity. Available from multiple brands (Liberty, Everbilt, VADANIA) for ~$10-15 per pair at Home Depot or Amazon.

### Tube Routing with Drawer Slides

The dock connects to the house plumbing (water supply, flavor bags). If the dock slides out on rails, those connections must flex:

- **House-side connections**: Flexible tubing from the back wall to the dock. When the dock slides out 12 inches, this tubing must accommodate 12 inches of linear movement.
- **Solution**: Use 18-24 inches of flexible 1/4" silicone or polyethylene tubing in a service loop. When the dock is pushed in, the loop is coiled loosely. When pulled out, the loop straightens.

```
    Side view:

    Wall ──── flex tubing loop ──── dock on slides
    │                                    │
    │    ╔══════════╗                    │
    │    ║ service  ║ ←─ coiled when     │
    │    ║  loop    ║    dock is closed  │
    │    ╚══════════╝                    │
    │                                    │
```

This is the same approach used in pull-out kitchen faucets and under-sink organizer plumbing. It works reliably.

### How This Changes the Release Mechanism

With the drawer pulled out, the user has full access to the cartridge from above, the front, and both sides. Now ANY release mechanism works well because "can I reach the lever?" is no longer a constraint:

- A top-mounted lever (like a stapler) is easily accessible
- Side-mounted lever works with full arm extension
- Even individual hand disconnects of John Guest fittings are easier because the user can see and reach all fittings
- The "blind operation" requirement that drives much of the release plate design complexity is eliminated

The drawer approach does not eliminate the need for a release mechanism, but it makes every mechanism option more viable by solving the access problem.

### Assessment

| Aspect | Rating | Notes |
|---|---|---|
| Access for swap | Excellent | Full access from multiple angles |
| Mechanical complexity | Moderate | Drawer slides + service loop + dock |
| Cost | Low | $10-15 for slides, service loop tubing ~$5 |
| Reliability | Good | Ball-bearing slides rated for 50,000+ cycles |
| Space consumption | Moderate | Slides add ~1" width per side |
| Tube routing | Moderate | Service loop adds tubing length and a coil to manage |
| Under-sink fit | Good | Pull-out organizers are already common under sinks |
| One-handed operation | Pull: yes. Release: depends on mechanism | Pulling the drawer is one-handed; cartridge release still needs a mechanism |

### Prior Art

Pull-out under-sink organizers are a mature consumer product category:
- **TRINITY Sliding Undersink Organizer** (Home Depot, ~$30-40): Chrome wire basket on ball-bearing slides, fits under sink
- **Hold N' Storage Under Sink Organizer**: 2-tier pull-out, 50 lb capacity, ball-bearing tracks
- **Pull-out trash cans**: Same slide mechanism, heavier duty

These products demonstrate that slide-mounted systems work well in the under-sink environment.

**Verdict**: The drawer approach is a genuine architectural alternative that changes the fundamental constraint set. By solving the access problem externally (bring the cartridge to the user), it relaxes the requirements on the release mechanism itself. The trade-off is increased system complexity (slides, service loop, larger footprint) and the permanent installation of slide hardware in the cabinet. This is most attractive if the user is already doing custom under-sink work (which they are, for this project).

---

## 7. Comparison Matrix

Scoring: 1-5 (5 = best). Weights reflect the priorities for an under-sink soda flavor injector swapped monthly.

| Criterion | Weight | Current Design (Cam + Plate) | Hand Disconnect (No Plate) | Spring-Loaded Dock Plate | Magnetic + O-Ring | Captive Tube + Rails | Drawer + Any Release | Twist-Lock |
|---|---|---|---|---|---|---|---|---|
| Mechanical complexity | 4 | 3 | 5 | 3 | 5 | 4 | 2 | 2 |
| User effort (time + force) | 5 | 5 | 2 | 4 | 3 | 4 | 4 | 3 |
| Reliability | 4 | 4 | 4 | 3 | 3 | 4 | 4 | 3 |
| Manufacturability (3D print) | 3 | 3 | 5 | 3 | 4 | 4 | 3 | 2 |
| Water safety (drip mgmt) | 3 | 3 | 2 | 3 | 2 | 5 | 3 | 3 |
| Blind operation (by feel) | 4 | 4 | 2 | 4 | 4 | 3 | 5 | 3 |
| One-handed operation | 4 | 5 | 1 | 4 | 3 | 3 | 4 | 2 |
| Works at cabinet depth | 3 | 4 | 3 | 4 | 4 | 4 | 5 | 4 |
| Cost | 2 | 4 | 5 | 4 | 5 | 4 | 3 | 4 |
| **Weighted Score** | | **126** | **97** | **110** | **109** | **118** | **115** | **84** |

### Ranking

1. **Current Design (Cam + Release Plate on Cartridge)** — Score 126. Wins on user effort and one-handed operation. The release plate complexity is real but justified by the UX advantage. The eccentric cam provides the mechanical advantage, over-center locking, and positive feedback that no other mechanism matches in a single part.

2. **Captive Tube + Rails** — Score 118. Surprisingly strong. Eliminates the release mechanism entirely for routine maintenance. Best water safety (no disconnection = no drips). Loses the "quick-swap" ability but may not need it if in-place maintenance is sufficient.

3. **Drawer + Any Release** — Score 115. Solves the access problem from the outside, making every release mechanism easier. High total system complexity but uses proven consumer hardware (drawer slides). Best "blind operation" score because pulling a drawer is the simplest possible first action.

4. **Spring-Loaded Dock Plate** — Score 110. The most interesting "new" mechanism. No lever needed — push in, pull out. Lacks the positive lock feedback of the cam design. Could be improved with a simple latch to reach near-parity with the current design.

5. **Magnetic + O-Ring** — Score 109. Simplest possible mechanism. Viable at the near-zero pressures of this system. Limited by removal force. Drip management is less of a concern with clean-before-remove (residual is water, not concentrate). Best as a proof-of-concept prototype to validate the O-ring seal before committing to John Guest fittings.

6. **Hand Disconnect** -- Score 97. The baseline. Viable if the user is technically comfortable and swap frequency is low. Not suitable for a consumer product.

7. **Twist-Lock** -- Score 84. Does not work well with John Guest push-to-connect fittings due to tube torsion. Strong prior art for water filters (O-ring seals) does not transfer to this application. Would require fundamental redesign of the fluid connection to be viable.

### Recommended Path

**Build the current design (cam + release plate) as the primary architecture.** It scores highest and has the best UX for the target user. However:

1. **Consider prototyping the magnetic + O-ring approach first** as a low-cost proof-of-concept. If O-ring seals work reliably with 3D-printed bores at near-zero pressure, this validates the simplest possible fluid connection before investing in John Guest fittings and release plate tooling.

2. **Keep the spring-loaded dock plate in mind** as a simplification option. If the release plate works but the cam lever feels over-engineered, a dock-side spring plate with a simple latch could provide 90% of the UX at lower per-cartridge cost (no lever or cam on the cartridge).

3. **The drawer approach is orthogonal** -- it can be combined with any release mechanism. If the under-sink access proves difficult during testing, adding drawer slides is a ~$15 retrofit that solves the problem.

---

## Sources

### Quick-Disconnect Couplings
- [Quick Release Couplings for Food and Beverage -- Tubes International](https://www.tubes-international.com/products/industrial-fittings/quick-release-couplings-for-food-and-beverage/) -- Hansen Beverage dry-break couplings
- [Beer Quick Disconnect 1/4" Barb -- MoreBeer](https://www.morebeer.com/products/beer-gas-quick-connect-14-barb-female-shutoff.html) -- Homebrew QD pricing reference

### Swagelok Quick Connects
- [Swagelok QC Series Quick Connects](https://products.swagelok.com/en/all-products/valves/quick-connects/c/206?clp=true) — Industrial quick connect overview
- [Swagelok QC, QF, QM, QTM Series Catalog (PDF)](https://www.swagelok.com/downloads/webcatalogs/en/ms-01-138.pdf) — Technical specifications

### Water Filter Twist-Lock Mechanisms
- [Fast Cartridge Change: Twist vs Push-In — Viomi](https://water.viomi.com/blogs/hydration-lab/fast-cartridge-change-twist-vs-push-in) — Comparison of twist-lock and push-in filter designs
- [How to Use Twist Lock Fittings — H2O Distributors](https://www.h2odistributors.com/info/how-to-use-twist-lock/) — Twist-lock fitting operation
- [DuPont QuickTwist Filtration on Amazon](https://www.amazon.com/DuPont-WFQT390005-QuickTwist-Drinking-Filtration/dp/B007VZ2PH8) — Consumer twist-lock filter cartridge

### Drawer Slides and Under-Sink Hardware
- [Full Extension Drawer Slides — Home Depot](https://www.homedepot.com/b/Hardware-Cabinet-Hardware-Drawer-Slides/Full-Extension/N-5yc1vZc2bqZ1z25ckx) — Drawer slide options and pricing
- [TRINITY Sliding Undersink Organizer — Home Depot](https://www.homedepot.com/p/TRINITY-Sliding-Undersink-Organizer-TBFC-2204/300012011) — Pull-out under-sink prior art
- [Hold N' Storage Under Sink Organizer](https://www.holdnstorage.com/products/hold-n-storage-under-sink-organizers-and-storage-2-tier-slide-out-cabinet-organizer-with-sliding-drawers-for-inside-cabinets-12w-x-18d-x-15-h-chrome) — 50 lb capacity pull-out organizer

### Magnets
- [K&J Magnetics Pull Force Calculator](https://www.kjmagnetics.com/magnet-strength-calculator.asp) — Neodymium magnet force calculations
- [Dura Magnetics Pull Force Calculator](https://www.duramag.com/neodymium-magnets-ndfeb/neodymium-magnetic-pull-force-calculator/) — Magnetic pull force estimation

### Tubing and Seals
- [Bend Radius Reference — Zeus Inc.](https://www.zeusinc.com/resources/summary-material-properties/bend-radius/) — Tubing bend radius engineering data
- [Silicone Tubing 1/4" ID x 3/8" OD — Amazon](https://www.amazon.com/Pure-Silicone-Tubing-High-Kink-Free/dp/B07V5T2ZY1) — Silicone tubing specifications
