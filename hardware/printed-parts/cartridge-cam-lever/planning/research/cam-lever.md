# Cam & Lever Mechanisms + Prior Art Survey

Research for the replaceable pump cartridge release mechanism. The cartridge has 4 John Guest 1/4" push-to-connect fittings whose collets need simultaneous release (~2-3mm inward travel, ~1-2 lbs per fitting, ~4-8 lbs total). A lever mechanism converts user hand force into this displacement. Environment is under a kitchen sink.

---

## Part 1: Cam & Lever Mechanisms

### 1. Eccentric Cam Lobes

#### How It Works

An eccentric cam is a disc (or partial disc) whose center of rotation is offset from its geometric center. As the cam rotates, it pushes a follower through a linear stroke. The bicycle quick-release skewer is the canonical consumer example:

- A lever arm is attached to a rod via an eccentric cam
- The cam sits inside (internal cam) or outside (external cam) the lever body
- When the lever is flipped from open to closed, the cam rotates and draws the skewer tight against the bicycle dropouts
- The lever's length (~100mm) amplifies the torque applied by the hand

#### Displacement vs. Eccentricity

The fundamental relationship is:

- **Stroke = 2 x eccentricity** (for a full 180-degree rotation)
- **Displacement at angle theta: d = e * sin(theta)**, where e is the eccentricity
- For a partial rotation (like a quick-release lever that swings ~180 degrees), the effective displacement equals twice the offset distance between the cam's rotation axis and its contact point

For our application needing 2-3mm of displacement: an eccentricity of 1-1.5mm would provide exactly this range with a 180-degree lever swing. This is a very small eccentricity, easily achievable.

#### Force Multiplication

The mechanical advantage comes from two sources:
1. **Lever arm ratio**: The long handle (~80-100mm) vs. the short cam radius (~5-10mm) gives roughly 10:1 to 20:1 mechanical advantage
2. **Cam geometry**: As the cam approaches its maximum displacement, the rate of linear displacement per degree of rotation decreases, further multiplying force near the locked position

A typical bicycle QR produces 5-7.5 N*m of clamping torque from a comfortable hand squeeze. With our ~4-8 lbs (18-36N) total force requirement, even a short lever (50mm) with modest eccentricity would be more than adequate.

#### Over-Center Behavior

This is the key insight from bicycle quick-releases: the cam goes "over the top." When the lever passes the point of maximum displacement and continues slightly further:

- The cam actually loosens very slightly (fractions of a millimeter)
- This means vibration tends to push the lever further closed rather than opening it
- The lever rests against a stop in a slightly past-center position
- **Result**: self-locking in the closed position -- it cannot vibrate open

This over-center property means the cam provides a definite "locked" state without any separate latch. The lever must be intentionally pulled past center to release.

#### Internal vs. External Cam

- **Internal cam**: All mechanism parts enclosed inside the lever body. Stronger clamping force, more robust, but harder to manufacture. Better for high-force applications.
- **External cam**: Cam is visible outside the lever body. Lighter, cheaper, easier to make. Adequate for lower forces. Internal cam QRs can be 30-40% stronger than external cam designs.

For a 3D-printed mechanism at 4-8 lbs total force, an external cam is likely sufficient and much easier to print.

#### Typical Displacement Range

- Bicycle QR skewers: ~2-5mm of effective clamping displacement
- With eccentricity of 1-2mm and ~180 degrees of lever travel, displacement is precisely controllable
- The small displacement range (2-3mm) is well within what eccentric cams handle best

#### Relevance to Our Application

Eccentric cams are a strong match. A lever with 1.5mm eccentricity rotating ~180 degrees delivers exactly 3mm of displacement with significant force multiplication and over-center locking. The mechanism is simple enough to 3D print as a single moving part plus a pivot pin.

---

### 2. Over-Center Toggle Mechanisms

#### How It Works

A toggle clamp uses a system of links (typically a four-bar linkage) where the operating handle drives two links that straighten into a line and then pass slightly beyond it:

1. **Open position**: Links are bent at an angle, clamp is released
2. **Approaching center**: As the handle is pushed, the links straighten. The force required increases but the mechanical advantage also increases dramatically
3. **At dead center**: The links form a perfectly straight line. Mechanical advantage is theoretically infinite
4. **Past center (locked)**: The links have passed the straight-line position and now rest against a hard stop. Any force from the workpiece pushes the links further past center rather than back open

#### The "Snap" Feel

The snap action comes from the geometry crossing the dead-center line:
- Just before center: High resistance, building tension
- At center: Instantaneous transition point
- Past center: Links "snap" into the locked position with a tactile and often audible click
- This provides unmistakable feedback that the mechanism is locked

#### Force Multiplication

- **Mechanical advantage ranges from 2:1 to 10:1** in typical toggle clamps
- Two sources of multiplication: (1) handle length vs. link length ratio, (2) the trigonometric amplification as links approach the straight-line position
- As the toggle angle approaches 180 degrees (dead center), the mechanical advantage approaches infinity
- Practical MA at the lock point is typically 5:1 to 10:1

#### Self-Locking

Once past center, the clamp is self-locking:
- The clamping force from the workpiece pushes the linkage further into its over-center position
- It cannot open unless the handle is deliberately pulled back past the dead-center line
- This is fundamentally different from a friction lock -- it is a geometric lock

#### Consumer Product Examples

Toggle mechanisms appear everywhere:
- **Toolbox latches**: Over-center draw latches on Pelican cases, ammo cans, equipment cases
- **Ski boot buckles**: Toggle lever with adjustable cable for progressive clamping
- **Trailer tongue latches**: Over-center lever secures the coupler ball socket
- **Suitcase latches**: Classic over-center snap closure
- **HVAC access panels**: Quick-release panel fasteners
- **Vise-Grip locking pliers**: Toggle action with adjustable over-center lock point

#### Relevance to Our Application

Toggle mechanisms provide the clearest "locked / unlocked" feedback of any mechanism family. The snap action is unmistakable. However, they are more complex than a simple eccentric cam (more links, more pivot points), and the force vs. displacement curve is non-linear. For 2-3mm of displacement with clear state feedback, a toggle is somewhat over-engineered unless the user feedback aspect is prioritized.

---

### 3. Wedge / Ramp Mechanisms

#### How It Works

A wedge converts motion in one direction into a smaller motion in a perpendicular direction. The key relationships:

- **Mechanical advantage = length / thickness** (or equivalently, 1 / tan(ramp angle))
- A shallow ramp angle gives high force multiplication but requires more travel
- A steep ramp angle gives less force multiplication but more displacement per unit of travel

#### Displacement Conversion

For a ramp with angle theta:
- **Perpendicular displacement = input travel x tan(theta)**
- A 10-degree ramp with 20mm of sliding travel produces: 20 x tan(10) = 3.5mm of perpendicular displacement
- A 15-degree ramp with 15mm of travel: 15 x tan(15) = 4.0mm

#### Self-Locking Properties

A wedge is self-locking when the ramp angle is less than the friction angle:
- **Self-locking condition: theta < arctan(mu)**, where mu is the friction coefficient
- For 3D-printed PLA on PLA: mu is roughly 0.3-0.5, giving a self-locking angle of 17-27 degrees
- For 3D-printed PLA on smooth surface (greased): mu drops to ~0.1-0.2, self-locking at 6-11 degrees
- **At angles below the self-locking threshold, the wedge stays put when force is removed** -- no separate latch needed

#### How It Could Work for Our Application

A lever rotates a piece with a ramp profile:
1. Lever is in the "locked" position -- ramp piece is at its high point, pushing a release plate into the collets
2. User rotates lever -- ramp rotates, high point moves away
3. Release plate retracts (springs or collet spring-back provide return force)
4. Collets release, cartridge can be removed

Alternatively, a sliding wedge:
1. A cam or lever moves a wedge block laterally
2. The wedge's angled face pushes a plate perpendicular to the slide direction
3. Reversing the slide retracts the plate

#### Advantages

- Very simple geometry -- easy to 3D print
- Self-locking at low angles eliminates the need for a separate latch
- Smooth, progressive force application (no sudden snap)
- Ramp angle is a single design parameter that trades off force multiplication vs. travel

#### Disadvantages

- No distinct "snap" feel between states (smooth transition)
- Requires a return mechanism (springs or inherent elasticity)
- Sliding friction surfaces may wear over time in 3D-printed parts
- Less clear tactile feedback than over-center mechanisms

#### Relevance to Our Application

Wedge/ramp mechanisms are attractive for their simplicity. A 10-15 degree ramp integrated into a rotating lever would deliver the needed 2-3mm displacement with good force multiplication. The main concern is the lack of clear tactile state feedback -- the user might not know definitively whether the mechanism is locked or released without a visual indicator.

---

### 4. Lever + Linkage

#### Simple Lever Arm

The simplest approach: a lever pivots on a pin and directly pushes a release plate.

- **Mechanical advantage = lever arm length / distance from pivot to plate contact**
- A lever with the pivot 10mm from the plate and a handle 80mm from the pivot gives 8:1 MA
- For 2-3mm plate displacement: the lever tip needs to move only 16-24mm (easily achievable in a comfortable grip arc)

This is mechanically the simplest option but provides no self-locking -- the lever must be held or latched separately.

#### Four-Bar Linkages

A four-bar linkage connects four rigid links with four pivot joints to create controlled motion paths:

- **Crank-rocker**: Input link rotates fully, output link oscillates. Good for converting rotation to a defined sweep.
- **Double-rocker**: Both input and output oscillate. Good for limited-range motions with specific displacement profiles.
- **Parallel linkage**: Maintains output orientation. Could keep a release plate parallel while displacing it.

Four-bar linkages can be designed to have near-linear output for a portion of their travel, or to have over-center positions, or to amplify displacement in specific ranges.

#### When Is a Linkage Better Than a Direct Cam?

- When you need a specific motion profile (not sinusoidal like a cam)
- When you need to transmit motion around a corner or to a remote location
- When you need to combine displacement with a specific angular relationship
- When the cam's sinusoidal displacement profile doesn't match the application need

For our application (simple linear push of 2-3mm), a direct cam or lever is probably simpler than a full linkage. A linkage would only be justified if geometric constraints require the handle to be in a location that can't directly reach the release plate.

#### Relevance to Our Application

A simple pivoting lever is the baseline. It works, but needs a separate latch to hold it in position. Adding a single link to create an over-center toggle adds reliable locking. A full four-bar linkage is likely overkill for 2-3mm of linear displacement in an accessible location.

---

### 5. Mechanism Comparison for This Application

#### Requirements Recap

| Requirement | Value |
|---|---|
| Displacement | 2-3mm (collet release travel) |
| Force output | 4-8 lbs (4 fittings x 1-2 lbs each) |
| Tactile states | Clear "locked" and "released" positions |
| Operation | One-handed, under a sink |
| Manufacturing | 3D printable (FDM) |
| Environment | Under kitchen sink (occasional moisture) |

#### Comparison Matrix

| Mechanism | Displacement Control | Force Multiplication | Tactile Feedback | Self-Locking | Simplicity (3D Print) | One-Hand |
|---|---|---|---|---|---|---|
| Eccentric cam | Excellent (precise) | Very good (10:1+) | Good (over-center) | Yes (over-center) | Excellent (1 moving part) | Yes |
| Toggle clamp | Good | Excellent (up to 10:1) | Excellent (snap) | Yes (geometric) | Moderate (3+ links) | Yes |
| Wedge/ramp | Good (tunable) | Very good (angle-dependent) | Poor (smooth) | Yes (friction) | Good (2 parts) | Yes |
| Simple lever | Good | Good (ratio-dependent) | Poor (no detent) | No (needs latch) | Excellent (1 part) | Marginal |
| Four-bar linkage | Excellent (designable) | Good | Moderate | Optional | Poor (4+ parts) | Yes |

#### Recommendation Ranking

**1. Eccentric cam (best overall)**
- The 2-3mm displacement range is the sweet spot for eccentric cams
- Over-center locking provides clear "locked" feedback without extra parts
- Single moving part (lever + integral cam) is trivially 3D printable
- Force multiplication is more than adequate
- Proven in millions of bicycle quick-release skewers
- Closest to the bicycle QR experience users already understand intuitively

**2. Over-center toggle (best feedback)**
- If the "snap" feel is the highest priority, toggles win
- More complex to 3D print (multiple pivot pins, tighter tolerances)
- Risk: tolerance stack-up in 3D-printed pivot holes could make the over-center feel sloppy
- Best if the mechanism is visible and used as a positive lock indicator

**3. Hybrid: eccentric cam + detent**
- An eccentric cam with a small bump or detent at the locked position
- Combines the simplicity of a cam with a more positive click feel
- The detent can be printed as a small raised feature on the cam track

**4. Wedge/ramp (simplest if feedback doesn't matter)**
- If a visual indicator (colored stripe, window showing lock state) replaces tactile feedback
- Very forgiving of 3D print tolerances
- Self-locking at low ramp angles is robust

---

## Part 2: Prior Art Survey

### 6. Inkjet Printer Cartridges

#### Guide and Alignment

Printer cartridges are the canonical example of a consumer dock/cartridge system:

- **Keyed shape**: Each cartridge has a unique profile (different widths, tab positions) so only the correct cartridge fits in each slot. This is "poka-yoke" -- mistake-proofing through geometry.
- **Vertical insertion**: Most designs have the cartridge drop into a well from above, guided by side walls that funnel it into position. The well is slightly wider at the top for easy entry.
- **Registration features**: Small ribs, notches, or chamfered edges guide the cartridge into exact lateral position as it slides down. The last few millimeters of travel are tightly constrained.

#### Electrical Contact

- **Spring-loaded contact pins**: The printer carriage has an array of spring-loaded pogo pins (gold-plated) that press against flat copper pads on the cartridge's flex circuit.
- **HP 45 cartridge**: 14 primitive selects, 14 primitive grounds, and 22 address selects -- 50 electrical connections made simultaneously by spring pressure alone.
- **Self-wiping**: The sliding insertion motion causes the pins to wipe across the pads, cleaning oxide from the contact surfaces.
- **No latching force needed for electrical contact**: The spring pins provide their own contact force; the latch only keeps the cartridge from lifting out.

#### Lock/Release Mechanism

- **Lever latch**: Most HP and Canon designs use a hinged lever (the "ink cartridge lock lever") that swings over the top of the cartridge after insertion. Pushing it down until it clicks locks the cartridge.
- **Spring tab latch**: Some designs use a molded plastic spring tab that snaps over a feature on the cartridge. Push the cartridge down and the tab catches; push the tab to release.
- **Epson sliding lever**: Some Epson designs use a sliding lever that moves laterally to lock/unlock all cartridges simultaneously.

#### Lessons for Our Design

- Keyed geometry for mistake-proofing is universally used and costs nothing in a 3D print
- Spring-loaded contacts that self-wipe during insertion are elegant (though we have fluid, not electrical connections)
- The lever latch is a proven, simple mechanism for holding a cartridge in a well
- Vertical insertion with side-wall guidance is the simplest alignment approach

---

### 7. Under-Sink Water Filter Housings

This is the closest direct analog to our cartridge: water connections, removable module, under-sink environment.

#### Traditional Screw-On Housing

The classic RO filter housing:
- **Threaded sump**: A cylindrical canister screws onto a fixed head with a large-diameter thread
- **O-ring seal**: A rubber O-ring in the head seals against the sump rim
- **Wrench removal**: A special wrench grips the canister body for unscrewing (4-tooth equal-grip design)
- **Cartridge drops in**: The filter element simply sits inside the canister, retained by the screw-on closure

Drawbacks: Two-handed operation, wrench required, O-ring maintenance (silicone grease), water must be shut off, sump drips when removed.

#### Quick-Change Twist-Lock Systems

Modern RO systems (3M, Waterdrop, GE, DuPont QuickTwist) use a dramatically simpler approach:

- **Quarter-turn bayonet**: The filter cartridge twists ~90 degrees into a fixed head. Lugs on the cartridge engage slots in the head.
- **Integrated seal**: The O-ring is part of the cartridge (disposable), not the head. No reusable O-ring to maintain.
- **Self-sealing valve**: Many designs have an automatic shutoff valve in the head that closes when the cartridge is removed, so the water supply doesn't need to be turned off.
- **Replacement time**: Advertised as 3 seconds (Waterdrop) to 30 seconds. No tools, no wrench, no dripping.
- **Fully sealed cartridge**: The entire filter is enclosed in the cartridge body. The user never touches filter media or gets wet.

#### How Twist-Lock Alignment Works

1. Cartridge has protruding lugs (typically 2) at the top
2. Head has matching slots -- wider entry slots transition to narrower retention slots
3. User pushes cartridge up into head, aligns lugs with wide slots
4. Quarter turn rotates lugs into narrow retention slots
5. An internal spring or ramp pulls the cartridge up tight, compressing the O-ring
6. Some designs have a click detent at the locked position

#### Lessons for Our Design

- **Quarter-turn bayonet is the gold standard** for under-sink filter replacement. It is proven, intuitive, and tool-free.
- **Integrated disposable seals** in commercial filters eliminate a maintenance step and a failure mode.
- The push-up-and-twist motion works well under a sink where headroom is limited.
- **This is the strongest prior art for our application.** The cartridge dock should feel like changing a water filter: push in, twist, done.

---

### 8. Power Tool Battery Packs

#### Rail and Slide System

DeWalt, Milwaukee, and Makita all use a rail-slide system:

- **T-shaped rails**: The battery has protruding rails that slide into matching grooves on the tool. The rail cross-section is designed so the battery can only enter from one direction (typically the back).
- **Progressive engagement**: As the battery slides forward, electrical terminals engage progressively. The last few millimeters seat the power terminals.
- **Proprietary profiles**: Each manufacturer uses a unique rail profile specifically designed to be incompatible with other brands. Milwaukee uses rounded, fang-shaped rails; DeWalt uses sharper-angled rails with teeth that jut outward.

#### Latch and Click

- **Spring-loaded latch**: A molded plastic latch with an internal spring clips over a feature on the tool when the battery is fully seated. This produces the satisfying "click."
- **Release button**: Pressing the button retracts the latch, freeing the battery to slide out.
- **Single-action**: Slide in until it clicks (one motion). Press button and slide out (two motions -- intentional asymmetry makes accidental removal harder).

#### Milwaukee M18 Internals

- The top cap houses spring clips that latch the battery into tools
- The clips are integral to the battery housing, not separately serviceable
- Design was significantly updated between 2012-2014 for improved reliability
- Newer designs are more robust but require more complex assembly

#### Lessons for Our Design

- **Rail slides are the most intuitive dock mechanism**: users understand "slide it in until it clicks" from phone cases, laptop docks, and every battery tool they own.
- The asymmetric insert/remove experience (easy in, intentional out) is good safety design.
- **The "click" is essential feedback** -- users trust the connection is made when they hear/feel it.
- Rail slides work best for horizontal or angled insertion, which may suit an under-sink cartridge that slides in from the front.
- Spring-loaded latches are straightforward to 3D print (living hinge or separate spring).

---

### 9. Server Blade Chassis

#### Why This Matters

Server blades must make dozens to hundreds of electrical connections reliably, with high insertion forces, in a hot-swappable environment. The mechanical engineering is highly evolved.

#### Guide Rail System

- Blades slide on precision guide rails mounted in the chassis
- The rails provide coarse alignment (getting the blade into roughly the right position)
- The last ~10-20mm of travel engages fine alignment features (chamfered pins, tapered connectors) that pull the blade into exact position
- This two-stage alignment (coarse then fine) is a universal pattern in high-reliability docking

#### Cam Lever Ejector

This is the most relevant mechanism for our application:

- **Ejector levers** are mounted on the front panel of each blade
- The lever has an **ejector cam** -- rotating the lever rotates the cam, which pushes against the chassis frame
- The cam converts the lever's rotational input into linear insertion/extraction force
- **Force multiplication is extreme**: an input force of 10-20 lbs can produce 400-500 lbs of insertion force (20:1 to 25:1 mechanical advantage)
- The cam is typically a dual-cam design for balanced force on both sides of the blade

#### Southco Inject/Eject Mechanisms

Southco is the dominant supplier of blade server inject/eject hardware:
- Standard 10mm (0.39") of linear travel between fully extended and retracted
- Smooth, controlled cam action
- Integrated locking -- the lever clicks into place at the fully inserted position
- ATCA, AMC, MicroTCA, and CompactPCI form factors all standardized

#### Backplane Connection

- Backplane connectors use female contacts on the blade side and male pins on the backplane
- Self-aligning connector housings absorb minor misalignment
- The high insertion force from the cam lever ensures all pins seat fully
- Connectors are designed to survive thousands of insertion cycles

#### Lessons for Our Design

- **The cam lever is exactly what we need**: small rotation converts to small linear displacement with high force multiplication
- Two-stage alignment (coarse rail + fine taper) is worth borrowing
- The Southco-style 10mm travel range is more than we need (2-3mm), but the mechanism principle scales down perfectly
- **This is the most direct mechanical analog**: a lever on the front of the cartridge that cams against the dock frame to release/engage the fittings

---

### 10. Espresso Machine Portafilters

#### Bayonet / Twist-Lock Mechanism

The portafilter uses a bayonet fitting to lock into the group head:

- **Metal lugs ("ears")**: The portafilter has 2-3 protruding metal wings
- **Group head receiver**: The group head has a ring with matching slots
- **Insertion**: Lugs are aligned with the wide entry slots and pushed upward
- **Locking rotation**: The portafilter is twisted 30-45 degrees clockwise until the lugs slide under the narrower retention portions of the ring
- **Seal compression**: The rotation pulls the portafilter up tight against a rubber gasket in the group head, creating the pressure seal needed for espresso extraction (9 bar / 130 psi)

#### The Feel

What makes a good portafilter lock feel "right":

- **Progressive resistance**: Light force at the start of rotation, increasing as the gasket compresses
- **Definite stop**: Clear mechanical endpoint when the lugs reach their stops
- **Snug and secure**: No wobble, no play in the locked position
- **Smooth metal-on-metal**: The brass/steel lugs sliding against the brass group ring should feel polished, not gritty
- **Weight in the hand**: A solid, heavy portafilter feels premium and inspires confidence

#### Relevant Design Details

- The bayonet angle (slot geometry) determines how much rotation is needed
- Steeper slots = less rotation but higher insertion force
- Shallower slots = more rotation but easier insertion
- The gasket compression provides the "increasing resistance" feel that tells the user they're locking properly
- **No separate latch needed**: The twist-lock is inherently self-retaining under the operating pressure (which pushes the portafilter into the group head)

#### Lessons for Our Design

- **Quarter-turn with progressive resistance is the most satisfying dock feel** for consumer products
- The bayonet principle (lugs engaging slots via rotation) is simple, robust, and proven at pressures far beyond our needs
- Gasket compression providing tactile feedback is elegant -- for our design, the collet spring resistance could serve the same role
- The portafilter demonstrates that a twist-lock can be extremely reliable without any separate latch mechanism

---

### 11. Lab / Medical Equipment

#### Centrifuge Rotors

Centrifuge rotors must be installed precisely (imbalance at 15,000+ RPM is destructive):

- **Drive pin alignment**: Rotors have pins in the drive hole that mesh with teeth on the centrifuge drive spindle. Pins must be properly seated (not sitting ON the spindle pins).
- **Drop-on installation**: The rotor is lowered straight onto the spindle, then slowly rotated to seat the pins.
- **Retaining ring**: A locking ring with pointed teeth secures the rotor axially. Alignment members (centering projections) position the ring on the rotor body.
- **Lubrication requirement**: Metal threads and O-rings must be lubricated with silicone vacuum grease.
- **Safety interlocks**: The centrifuge lid won't close (and thus won't spin) unless the rotor is properly seated and locked.

#### Point-of-Care Diagnostic Cartridges

Modern medical diagnostics use disposable cartridges that dock with an analyzer:

- **Spring-loaded pogo pin electrical contacts** aligned to pads on the cartridge -- the same principle as inkjet printers
- **Magnetic alignment**: Some microfluidic chips use magnetic force to align channels on top of a reusable sensing chip
- **Fluid connections**: Sealed fluid channels in the cartridge mate with ports in the analyzer via compression seals (O-rings or gaskets compressed by the cartridge's insertion force)
- **Rotational indexing**: Some systems (like the Abaxis Piccolo) use a spinning disc cartridge with radial chambers -- insertion is a simple drop-in with the disc's center hole aligning to a spindle

#### Spectrophotometer Cuvette Holders

- **Slot insertion**: Cuvettes drop into a precisely machined slot
- **Spring-loaded clamp**: A sprung plate pushes the cuvette against a reference face for repeatable positioning
- **Optical alignment**: The slot geometry ensures the cuvette's optical faces are perpendicular to the light path
- **No latch**: The slot walls and gravity retain the cuvette; the spring clamp provides positioning force

#### Lessons for Our Design

- **Drive pin + rotation alignment** (centrifuge) is a robust pattern for precise axial positioning
- Safety interlocks that prevent operation with an improperly seated module are worth considering (maybe a microswitch or hall sensor that detects the lever position)
- **Spring-loaded contacts for self-aligning connections** appear in both printers and medical devices -- universal pattern
- Magnetic alignment is interesting but unnecessary for our force levels and manufacturing method
- The cuvette holder pattern (slot + spring) is the simplest possible dock, relevant if our cartridge needs minimal alignment complexity

---

### 12. Key Lessons from Prior Art

#### Universal Patterns

These patterns appear in nearly every successful dock/cartridge system surveyed:

1. **Two-stage alignment**: Coarse guidance (rails, walls, funnels) gets the module roughly in place. Fine alignment (tapered pins, chamfered edges, keyed features) pulls it into exact position in the last few millimeters. Never ask the user to achieve fine alignment by hand.

2. **Positive feedback at lock**: Every good dock provides unmistakable confirmation of a successful connection -- a click, snap, increasing resistance, or a definite mechanical stop. The user must never wonder "is it in?"

3. **Asymmetric insert/remove**: Insertion is easy and intuitive (slide, push, twist). Removal requires a deliberate secondary action (press button, flip lever, twist opposite direction). This prevents accidental dislodging.

4. **Poka-yoke (mistake-proofing)**: Keyed geometry prevents incorrect orientation. If it fits, it's right. Printer cartridges, battery packs, and filter cartridges all use this.

5. **Spring-loaded contacts for self-alignment**: Whether electrical (pogo pins) or fluid (compression seals), the connection elements themselves provide compliance. Rigid-to-rigid mating is fragile; spring-loaded elements absorb tolerance.

#### What Makes the Good Ones Feel Good

- **Confidence**: The user knows the connection is made. No ambiguity.
- **Effortlessness**: The mechanism amplifies hand force so the user barely feels the resistance. Water filter quarter-turn, battery slide-and-click, lever flip.
- **Single motion**: The best designs are one continuous motion (slide until click, push and twist, flip lever). Multi-step sequences feel fiddly.
- **Reversibility**: Easy to undo and redo if something feels wrong. No tools, no damage.

#### Universal vs. Application-Specific Design Choices

**Universal (borrow these):**
- Keyed geometry for orientation
- Two-stage coarse-then-fine alignment
- Positive lock feedback (click or stop)
- Lever or cam for force multiplication
- Self-aligning connection elements

**Application-specific (evaluate for our case):**
- Quarter-turn bayonet vs. linear slide (depends on cartridge orientation and access angle)
- Over-center cam vs. spring latch (depends on required holding force)
- Integrated vs. separate seals (depends on cartridge cost and replacement frequency)
- Safety interlocks (depends on failure consequences)

#### What We Can Directly Borrow

1. **From water filters**: Quarter-turn or lever-operated mechanism is the right UX for under-sink. Users already associate this motion with water system maintenance. Tool-free replacement is essential.

2. **From server blades**: Cam lever for force multiplication. A small lever on the front of the cartridge that cams against the dock frame provides exactly the displacement and force we need. The 10:1+ mechanical advantage means the 4-8 lbs of collet release force feels like nothing.

3. **From battery packs**: Rail-slide for coarse alignment with a click detent for lock confirmation. The slide-until-click paradigm is universally understood.

4. **From printer cartridges**: Keyed geometry to prevent misorientation. If we have two fluid connections per side (4 total), each pair can have a unique key profile.

5. **From portafilters**: Progressive resistance as the final alignment indicator. As the lever approaches the locked position and starts to push the collets, the user feels increasing resistance that confirms engagement.

#### Recommended Mechanism Architecture

Based on this research, the strongest design combines elements from multiple prior art categories:

**Primary mechanism: Eccentric cam lever (from bicycle QR + server blade ejectors)**
- A lever on the front face of the cartridge (or on the dock)
- Rotating the lever drives an eccentric cam that pushes a release plate into the 4 collets
- Over-center position locks the lever
- 1.5mm eccentricity gives 3mm of displacement -- exactly what the collets need
- Force multiplication of ~10:1 makes the 4-8 lbs feel effortless

**Alignment: Rail slide (from battery packs + server blades)**
- Cartridge slides into the dock on guide rails
- Rails provide coarse lateral and vertical alignment
- John Guest fittings provide fine alignment as the tubing pushes into the collets (self-centering push-to-connect)

**Orientation: Keyed geometry (from printer cartridges)**
- Asymmetric rail profile or keying tab prevents upside-down or reversed insertion

**Feedback: Click detent at lock point (from battery packs)**
- A small molded bump on the cam track provides tactile and audible confirmation
- Combined with the over-center cam position for self-locking

---

## Sources

### Part 1: Mechanisms
- [Bicycle Quick-Release Mechanisms (Sheldon Brown)](https://sheldonbrown.com/skewers.html)
- [Quick Release Skewer (Wikipedia)](https://en.wikipedia.org/wiki/Quick_release_skewer)
- [Internal vs. External Cam QR Skewers (Brainy Biker)](https://brainybiker.com/archives/21848)
- [Hands On Bike: Good and Bad QR Skewers](https://handsonbike.blogspot.com/2013/08/difference-between-good-and-bad-qr.html)
- [How Toggle Clamps Work (Roche Handle)](https://www.rochehandle.com/blog/how-do-toggle-clamps-work/)
- [Toggle Clamp Force Calculation (Kunlong)](https://www.kunlonghardware.com/toggle-clamp-force-calculation/)
- [Toggle Clamp Functions (OneMonroe)](https://monroeengineering.com/info-toggle-clamps-functions.php)
- [Calculate Applied Force on Toggle Clamps (Reid Supply)](https://www.reidsupply.com/en-us/industry-news/calculate-applied-force-on-toggle-clamps)
- [Guide to Over-Center Toggle Latches (Goebel)](https://www.goebelfasteners.com/a-guide-to-over-center-toggle-latches/)
- [Guide to Toggle Latches (Essentra Components)](https://www.essentracomponents.com/en-us/news/solutions/access-hardware/guide-to-toggle-latches)
- [Wedges (Engineering Statics)](https://engineeringstatics.org/Chapter_09-block-and-wedge-friction.html)
- [Eccentric Cam Mechanism (NITK Virtual Lab)](https://mm2-nitk.vlabs.ac.in/exp/eccentric-cam-mechanism/theory.html)
- [Eccentric Cam (DT Online)](https://wiki.dtonline.org/index.php/Eccentric_Cam)
- [Eccentric-and-Rod Mechanism (Britannica)](https://www.britannica.com/technology/eccentric-and-rod-mechanism)

### Part 2: Prior Art
- [HP Ink Jet Printer Cartridge Anatomy (Wandel)](https://wandel.ca/hp45_anatomy/)
- [Canon Cartridge Replacement Manual](https://ij.manual.canon/ij/webmanual/Manual/All/TR4600%20series/EN/UG/ug-127.html)
- [Quick Change Twist-Lock RO Filters](https://www.home-water-purifiers-and-filters.com/quick-change-ro.php)
- [3M Under Sink RO Systems (Solventum)](https://www.solventum.com/en-us/home/f/b5005118094/)
- [DuPont QuickTwist Filtration (Amazon)](https://www.amazon.com/DuPont-WFQT390005-QuickTwist-Drinking-Filtration/dp/B007VZ2PH8)
- [Dual-Cam Ejector Assembly (US Patent 8435057)](https://patents.google.com/patent/US8435057)
- [Cam and Lever Ejector Assembly (US Patent 7297008)](https://patents.google.com/patent/US7297008B2/en)
- [High Insertion Force Ejector (US Patent App 2014/0187068)](https://patents.google.com/patent/US20140187068)
- [Southco Inject/Eject Mechanisms](https://southco.com/en_us_int/fasteners/inject-eject-mechanisms)
- [Portafilter Lock Mechanism (FoodDrinkTalk)](https://fooddrinktalk.pro/what-does-the-portafilter-lock-into/)
- [Espresso Portafilter Guide (Majesty Coffee)](https://majestycoffee.com/pages/what-is-a-portafilter)
- [All About Espresso Portafilters (Espresso Setup Builder)](https://espressosetupbuilder.com/learn/all-about-espresso-portafilters)
- [Centrifuge Rotor Installation (Beckman Coulter)](https://www.manualslib.com/manual/1277675/Beckman-Coulter-Ja-14-50.html?page=19)
- [Centrifuge Rotor Locking Mechanism (Patent CN112238000A)](https://patents.google.com/patent/CN112238000A/en)
- [ToolGuyd Milwaukee M18 Battery Teardown](https://toolguyd.com/peek-inside-milwaukee-m18-xc-cordless-power-tool-batteries-042020/)
