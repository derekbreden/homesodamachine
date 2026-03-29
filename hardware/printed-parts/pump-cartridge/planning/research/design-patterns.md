# Design Pattern Research: Replaceable Cartridge Mechanisms

Research into how real consumer and industrial products implement squeeze-release, slide-release, and push-to-connect cartridge interactions. The goal is to understand the landscape of mechanical solutions before designing a pump cartridge for a home soda machine.

---

## Product Studies

### 1. DeWalt 20V MAX Slide Battery (Power Tools)

**Domain:** Cordless power tools
**Source:** DeWalt product documentation, US Patent 10,027,078

**Insertion/removal interaction:**
The battery slides onto the tool along parallel T-shaped rails running the full length of the battery foot. To insert, the user aligns the rails and pushes the battery forward until it clicks. To remove, the user presses a release button (located on one side or the back of the battery, depending on tool model) and slides the battery straight out. One-handed operation is common for smaller batteries; larger packs sometimes require two hands for the slide motion.

**Alignment/guidance:**
Two parallel T-rails on the battery foot mate with corresponding T-channels on the tool. The rails prevent any motion except the intended slide axis. The cross-section of the T-rail prevents lift-off in the normal direction --- the battery can only exit along the slide axis.

**Connections made/broken:**
Electrical contacts (power, thermistor, ID, cell-balancing lines) are blade-style terminals arranged in a row perpendicular to the slide direction. As the battery slides in, the blade contacts engage progressively. No fluid connections.

**What provides the "locked" feeling:**
A spring-loaded detent on the battery engages a recess on the tool body at the end of travel. The detent clicks into place, providing audible and tactile confirmation. The spring also acts as a shock absorber during insertion, cushioning the final engagement.

**What provides the "released" feeling:**
Pressing the release button actuates the detent out of the recess. A compressed spring (loaded during insertion) then pushes the battery toward the disengaged position. The user feels the battery begin to slide out under spring force as soon as the button is pressed.

**One-handed or two-handed:**
Primarily one-handed. The user grips the tool with one hand and operates the release button with a thumb or finger on the same hand, then pulls the battery out.

---

### 2. HP OfficeJet Pro Inkjet Cartridges (Printers)

**Domain:** Consumer inkjet printers
**Source:** HP support documentation, HP Support Community

**Insertion/removal interaction:**
The user opens an access door, which causes the carriage to auto-center. Each cartridge sits in a vertical slot. To insert, the user angles the cartridge slightly and pushes it into the slot until it clicks. To remove, the user presses down gently on the top of the cartridge, which depresses a spring-loaded latch, then pulls the cartridge straight up and out. Some models use a hinged latch arm over each cartridge slot that the user lifts.

**Alignment/guidance:**
Each cartridge slot is keyed by size and shape --- different ink colors have slightly different cartridge geometries or keying features to prevent wrong-slot insertion. The slot walls act as close-fitting guides. The cartridge is tapered or chamfered at the leading edge to self-center during insertion.

**Connections made/broken:**
Electrical contacts (a row of gold pads on the cartridge face) press against spring-loaded pins in the carriage. The ink port (a small opening on the cartridge underside) mates with a needle or seal in the carriage that pierces or mates with the cartridge's ink outlet. Both connections are made simultaneously at the end of the insertion stroke.

**What provides the "locked" feeling:**
A spring-loaded plastic latch on the carriage snaps over a ridge on the cartridge. The user hears and feels a click.

**What provides the "released" feeling:**
Pressing down on the cartridge top deflects the latch, freeing the cartridge. A small spring pushes the cartridge upward slightly, making it easy to grip and pull out.

**One-handed or two-handed:**
One-handed. The press-down-and-pull motion is done with one hand.

---

### 3. 3M Aqua-Pure SQC Under-Sink Water Filter (Water Filtration)

**Domain:** Under-sink water filtration
**Source:** 3M/Solventum product documentation

**Insertion/removal interaction:**
The encapsulated filter cartridge is a cylinder roughly 25 cm long. The user grasps the cartridge body and gives it a quarter-turn (90 degrees) to unlock it from the filter head, then pulls it straight down and out. Installation is the reverse: push the cartridge up into the head and quarter-turn to lock. The entire operation takes seconds with one hand.

**Alignment/guidance:**
The cartridge has a bayonet-style interface at the top: lugs on the cartridge engage L-shaped slots in the filter head. The user pushes the cartridge up until the lugs bottom out in the vertical portion of the L-slots, then rotates to engage the horizontal portion. The geometry prevents the cartridge from being installed at the wrong angle or in the wrong orientation.

**Connections made/broken:**
Two water ports (inlet and outlet) on the top of the cartridge mate with corresponding ports in the filter head. O-ring seals on the cartridge compress against the head when the bayonet lock is engaged. A built-in shut-off valve in the filter head automatically closes when the cartridge is removed, so no water shutoff is needed.

**What provides the "locked" feeling:**
The bayonet lock reaches a hard stop at the end of the quarter-turn. Some versions have a detent or increased friction at the locked position.

**What provides the "released" feeling:**
The quarter-turn in the opposite direction moves the lugs back to the vertical slot, and the cartridge drops slightly under gravity, signaling it is free.

**One-handed or two-handed:**
One-handed. Grasp, twist, pull --- all with one hand.

---

### 4. Brita MAXTRA+ Pitcher Filter Cartridge (Water Filtration)

**Domain:** Consumer water filter pitchers
**Source:** Brita product documentation

**Insertion/removal interaction:**
The user drops the disc-shaped cartridge into a funnel recess in the pitcher and pushes straight down until it clicks. Removal is a straight pull upward. No twisting, no buttons.

**Alignment/guidance:**
The cartridge and funnel recess are shaped so the cartridge can only sit in one orientation. A ring of features around the cartridge perimeter mates with corresponding geometry in the funnel.

**Connections made/broken:**
The only "connection" is the water flow path: the cartridge body contains the filter media, and water must pass through it. The click-fit ensures a seal so unfiltered water cannot bypass the cartridge. No electrical connections.

**What provides the "locked" feeling:**
A snap-fit detent on the cartridge engages a ridge in the funnel recess. The audible click confirms proper seating. Brita calls this their "PerfectFit" system --- the click is both the alignment confirmation and the bypass-prevention seal.

**What provides the "released" feeling:**
Pulling upward overcomes the snap-fit detent force. The cartridge pops free with modest force.

**One-handed or two-handed:**
One-handed. Push down to lock, pull up to release.

---

### 5. SodaStream Quick Connect CO2 Cylinder (Beverage Appliances)

**Domain:** Home carbonation appliances
**Source:** SodaStream product documentation

**Insertion/removal interaction:**
The user holds the CO2 cylinder by its pink handle, inserts the nozzle into the adapter port, and pushes until the spring-loaded connectors engage with a click. No twisting required on the newer Quick Connect models (DUO, Terra, Art). Older models used a screw-in thread that required precise alignment and torque. The Quick Connect is explicitly designed to eliminate that friction.

**Alignment/guidance:**
The nozzle and adapter port are circular and self-centering. The user inserts at 90 degrees to the adapter face. Internal geometry prevents cross-threading or misalignment (which was a common complaint with the older screw-in system).

**Connections made/broken:**
A single high-pressure CO2 gas connection. Upon insertion, internal pins depress the cylinder's safety seal. An external collar rotates approximately 15 degrees to form a gas-tight seal. Spring-loaded connectors automatically secure the cylinder.

**What provides the "locked" feeling:**
The spring-loaded connectors click into place. The user feels a distinct snap as the collar completes its micro-rotation.

**What provides the "released" feeling:**
Pulling the cylinder overcomes the spring retention. The collar disengages and the safety seal re-closes.

**One-handed or two-handed:**
One-handed. The push-to-lock design was specifically chosen over the older two-handed screw-in to improve UX.

---

### 6. Staubli RMI Multi-Coupling Plate (Industrial)

**Domain:** Industrial mold temperature control / hydraulic multi-connection
**Source:** Staubli fluid connectors documentation

**Insertion/removal interaction:**
A flat plate carrying multiple fluid couplings (4, 6, 8, or more) is brought face-to-face with a matching plate on the mold or machine. The operator aligns the plates using guide pins, then rotates a single lever on the coupling plate. One lever rotation simultaneously connects all fluid circuits. Disconnection is the reverse: rotate the lever, pull the plate away.

**Alignment/guidance:**
Precision guide pins and bushings on the plate edges ensure the two halves align before any couplings engage. A foolproof keying system (asymmetric pin placement) prevents the plate from being connected in the wrong orientation or to the wrong mold, eliminating cross-connection errors.

**Connections made/broken:**
Multiple fluid connections (typically 4-16 circuits) are made simultaneously. Each coupling has an internal poppet valve that opens when mated and closes automatically when separated --- this is the "dry disconnect" that prevents fluid spill during connection/disconnection.

**What provides the "locked" feeling:**
A robust ball-locking mechanism engages at the end of the lever rotation. The lever reaches a hard stop and the ball locks click into detents on the mating plate.

**What provides the "released" feeling:**
Rotating the lever in the opposite direction releases the ball locks. The internal poppet valves close, and the user can pull the plate away cleanly.

**One-handed or two-handed:**
Two-handed for the approach and alignment, but the lever operation itself is one-handed. The plates are often heavy, so two-handed handling is typical in practice.

---

### 7. JUUL Pod System (Consumer Electronics)

**Domain:** Consumer vaporizer devices
**Source:** JUUL product documentation

**Insertion/removal interaction:**
The user drops the pod into the top of the battery device. Magnets pull the pod into alignment and hold it in place. Removal is a straight pull upward. No buttons, no levers, no twisting.

**Alignment/guidance:**
Magnets embedded in both the pod and the device body provide self-alignment. As the pod approaches the socket, magnetic force pulls it into the correct position and orientation. The socket geometry (a close-fitting rectangular recess) prevents rotation.

**Connections made/broken:**
Two electrical contacts on the pod base align with spring-loaded pins in the device. The magnetic force ensures consistent contact pressure. A fluid path (e-liquid from the pod to the atomizer coil) is also established by the pod's physical seating.

**What provides the "locked" feeling:**
The magnetic snap. The pod accelerates slightly at the end of insertion as the magnets close the gap, providing a satisfying tactile "thunk."

**What provides the "released" feeling:**
The user overcomes the magnetic force with a straight pull. There is a distinct moment where the pod breaks free of the magnetic field.

**One-handed or two-handed:**
One-handed. The entire interaction is tool-free and requires minimal force.

---

### 8. Dell PowerEdge Server Hot-Swap Drive Carrier (Computing)

**Domain:** Enterprise server hardware
**Source:** Dell support documentation

**Insertion/removal interaction:**
The user presses a release button on the front face of the drive carrier, which springs open a lever handle. The user grips the handle and pulls the carrier straight out of the drive bay along guide rails. Installation is the reverse: slide the carrier in along the rails until it seats against the backplane, then close the lever handle until it clicks.

**Alignment/guidance:**
The drive carrier rides on precision guide rails molded into the server chassis. The rails constrain the carrier to a single axis of motion. At the back of the carrier, a connector is positioned to engage the backplane connector at the end of travel. The rails self-center the connector alignment.

**Connections made/broken:**
A multi-pin electrical connector (SAS/SATA/NVMe data + power) mates with the backplane at the end of insertion travel. The connector is "blind-mate" --- the guide rails ensure alignment before the pins engage, so no user precision is required.

**What provides the "locked" feeling:**
The lever handle closing over the carrier front face. The lever has a cam mechanism that pulls the carrier the final few millimeters into the backplane connector, providing firm seating and a click.

**What provides the "released" feeling:**
Pressing the release button springs the lever open. The lever's cam releases the carrier slightly forward, giving it enough movement to clear the backplane connector. The user then slides the carrier out.

**One-handed or two-handed:**
One-handed. Press button, grip handle, pull. The standardized carrier size and single-axis rail system make this very fast.

---

### 9. BD Alaris Infusion Pump Module (Medical)

**Domain:** Medical infusion therapy
**Source:** BD Alaris documentation

**Insertion/removal interaction:**
The pump module has a hinged door on the front face. The user pulls a latch toward themselves to open the door, loads the IV tubing set into molded fitment recesses inside the door cavity (upper fitment first, then safety clamp fitment), then gently lowers the door latch to close. The door mechanism simultaneously engages the tubing into the peristaltic pump mechanism.

**Alignment/guidance:**
Molded fitment recesses inside the pump module ensure the tubing set is positioned precisely. Each fitment has a specific shape that only accepts the correct tubing component. The upper fitment goes in first, establishing the reference position for the lower safety clamp fitment.

**Connections made/broken:**
The tubing set is a continuous fluid path; the pump module does not make or break fluid connections. Instead, the door closure engages the peristaltic pump mechanism onto the tubing and positions the tubing across the air-in-line detector. The "connection" is mechanical clamping of the tubing into the pump.

**What provides the "locked" feeling:**
The door latch clicks into the closed position. The door closure is firm and deliberate.

**What provides the "released" feeling:**
Pulling the front latch opens the door, releasing the tubing from the pump mechanism. The user must not touch the tubing while closing the door (per safety requirements), emphasizing that the door mechanism itself handles all the precision alignment.

**One-handed or two-handed:**
Two-handed. One hand holds the pump module steady, the other operates the latch and loads tubing. In practice the pump is mounted to an IV pole, so the user has both hands free.

---

## Cross-Product Patterns

### Pattern 1: Slide-Rail with Spring-Detent Release

**Found in:** DeWalt/Milwaukee batteries, Dell server drive carriers
**Mechanism:** Parallel rails constrain motion to a single axis. A spring-loaded detent snaps into a recess at end-of-travel to lock. A button or lever releases the detent. A compressed spring assists ejection.
**Why it works for this cartridge:** The pump cartridge needs a linear insertion/removal path on guides or rails. The spring-detent provides the satisfying click on insertion and the positive release feeling. The spring-assisted ejection means the cartridge begins to emerge the moment the user releases it --- no fumbling.
**UX contribution:** Tactile click on lock, assisted ejection on release, single-axis motion prevents misalignment. The interaction is simple enough to learn on the first try.

### Pattern 2: Squeeze-to-Release (Bilateral Compression)

**Found in:** DeWalt/Milwaukee batteries (side buttons), inkjet cartridges (press-down tabs)
**Mechanism:** Two symmetric release points on opposite sides of the cartridge are squeezed simultaneously. The squeeze action deflects spring-loaded latches inward, freeing the detent mechanism. The user's natural grip (palm on one side, fingers curling around to the other) provides the squeeze force.
**Why it works for this cartridge:** The vision describes exactly this interaction: palm pushes against the front face, fingers curl around and pull a release surface. The squeeze is intuitive, requires no tools, and provides a distinct "I'm deliberately releasing this" gesture that prevents accidental removal.
**UX contribution:** Intentional gesture prevents accidental release. Symmetric force distribution. Natural grip ergonomics.

### Pattern 3: Bayonet / Quarter-Turn Lock

**Found in:** 3M Aqua-Pure SQC filters, SodaStream (partial --- 15-degree micro-rotation)
**Mechanism:** Lugs on the cartridge engage L-shaped slots in the dock. Push in, then rotate to lock. The rotation moves the lugs into the horizontal portion of the L-slot, creating a mechanical interlock that cannot be defeated by linear pull alone.
**Why it works for this cartridge:** The pump cartridge has internal quick-connect fittings that need firm seating pressure. A bayonet lock can provide the final clamping force that holds the cartridge against the tube stubs. However, it requires rotational motion which conflicts with the linear rail system.
**UX contribution:** Very positive lock/unlock feel. Built-in auto-shutoff capability (as in the 3M filter). The quarter-turn is a deliberate action that communicates "locked" unambiguously.

### Pattern 4: Push-to-Lock / Pull-to-Release (Magnetic or Spring-Assist)

**Found in:** JUUL pods, Brita MAXTRA cartridges, SodaStream Quick Connect
**Mechanism:** The cartridge is pushed into position. Internal springs, magnets, or snap-fits grab it at end-of-travel. Removal is a straight pull that overcomes the retention force. No buttons, no levers, no rotation.
**Why it works for this cartridge:** The pump cartridge's quick-connect fittings already work this way --- push a tube into a collet and it grabs; press the collet to release. This pattern would make the cartridge interaction mirror the fitting interaction. The cartridge slides in, the tube stubs enter the quick-connects, and the collets grab automatically. No separate locking step.
**UX contribution:** Absolute minimum interaction complexity. Insert and done. The risk is that the pull-to-release force might be uncomfortably high if four quick-connects must be released simultaneously.

### Pattern 5: Lever-Amplified Force

**Found in:** Staubli RMI multi-couplers, Dell server drive carriers (cam lever), Nespresso Vertuo (lever lock)
**Mechanism:** A lever or cam converts the user's low-effort input into the high force needed to mate or unmate multiple connections. The lever provides mechanical advantage and a clear "open/closed" state.
**Why it works for this cartridge:** Four quick-connect fittings must be disconnected simultaneously. The force to press four collets at once could be significant. A lever or cam mechanism could amplify the user's squeeze force to press all four collets reliably. The Staubli pattern is particularly relevant --- a single lever simultaneously connects/disconnects multiple fluid circuits.
**UX contribution:** Reduces user effort. Provides unambiguous state indication (lever open = released, lever closed = locked). Allows simultaneous disconnection of multiple connections.

### Pattern 6: Blind-Mate Connector with Rail Guidance

**Found in:** Dell server drives (backplane connector), power tool batteries (blade contacts)
**Mechanism:** The connections are made at the back/bottom of the cartridge, completely hidden from the user. Precision guide rails ensure alignment before any connection is attempted. The user simply slides the cartridge in; the rails handle all connector alignment.
**Why it works for this cartridge:** The tube stubs in the dock and the quick-connect fittings inside the cartridge are internal connections the user never sees. The rails guide the cartridge so the tube stubs enter the quick-connects cleanly. No user precision needed.
**UX contribution:** The user only thinks about one action (slide in/out). All connection complexity is hidden. Alignment errors are mechanically impossible if the rails are properly designed.

### Pattern 7: Auto-Shutoff on Disconnect

**Found in:** 3M Aqua-Pure (water shut-off valve), Staubli RMI (poppet valves)
**Mechanism:** Internal valves close automatically when the cartridge is removed, preventing fluid spill or system contamination. The user does not need to shut off flow before removing the cartridge.
**Why it works for this cartridge:** The existing John Guest quick-connect fittings already provide this --- when the tube is pulled from the fitting (after collet release), the collet returns to its closed position and the fitting does not leak. This pattern is built into the component choice.
**UX contribution:** No preparation step before cartridge removal. No dripping. No mess. The user can remove the cartridge confidently.

---

## Key Takeaways for a Pump Cartridge

1. **Rails are the foundation.** Every product that handles cartridge insertion/removal along a linear path uses precision guide rails. The rails serve double duty: constraining the motion to a single axis and aligning internal connections before they engage (blind-mate pattern).

2. **The squeeze-release interaction is well-established in power tool batteries.** The DeWalt/Milwaukee pattern of bilateral squeeze buttons releasing a spring-loaded detent is the closest analog to the envisioned pump cartridge interaction. It is one-handed, intentional, and provides clear tactile feedback.

3. **Force amplification matters with multiple connections.** The Staubli RMI and Dell cam-lever patterns show that when multiple connections must be made/broken simultaneously, a lever or cam mechanism reduces user effort and ensures all connections release together. Four quick-connects releasing simultaneously may need mechanical advantage.

4. **Push-to-connect, squeeze-to-release is asymmetric by design.** Insertion should be effortless (push in, connections auto-engage). Removal should require a deliberate gesture (squeeze to release collets, then pull). This asymmetry prevents accidental removal while keeping insertion simple. This matches how the John Guest quick-connects already work at the component level.

5. **The click is the confirmation.** Across all products, the audible/tactile click at end-of-travel is the universal signal that the cartridge is properly seated. A spring-detent, snap-fit, or magnetic snap provides this. The cartridge design must include a click.

6. **Auto-shutoff is already solved.** Quick-connect fittings inherently provide the auto-shutoff behavior seen in premium water filter and industrial coupling systems. This is a free UX win.

7. **Keying prevents errors.** Asymmetric guide pins, shaped cartridge profiles, and orientation-specific features (seen in Staubli, 3M, and printer cartridges) ensure the cartridge can only be inserted one way. For a consumer appliance, this is essential --- the user should not be able to force the cartridge in wrong.
