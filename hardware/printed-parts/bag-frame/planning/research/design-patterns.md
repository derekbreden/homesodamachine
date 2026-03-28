# Design Patterns: Holding Deformable Pouches in Consumer Products

How do shipped consumer products hold flexible, liquid-filled bags in a fixed position inside an enclosure? This document catalogs mechanical strategies from real products, organized by the interaction problem they solve.

---

## 1. Bag-in-Box Beverage Systems (Commercial Soda Fountains, Wine Dispensers)

### 1a. Commercial BIB Syrup Racks (Coca-Cola, Pepsi fountain systems)

**How the bag is held:** The 5-gallon BIB (11" x 15" x 8" box) sits on a metal wire rack. The rack provides slanted shelves that tilt the box toward the connector end. The rigid cardboard box is the primary structural element -- the bag itself is never touched or constrained by the rack. The bag simply hangs inside the box under gravity.

**Complete drainage:** The slanted shelf angles the box so the connector fitment sits at the lowest point. Gravity pulls remaining liquid toward the outlet. Scholle IPN (the dominant BIB bag manufacturer) claims over 99% product evacuation through their fitment geometry and bag film properties. The bag collapses inward as liquid exits -- atmospheric pressure on the outside pushes the bag walls together, preventing air ingress and eliminating headspace. No vacuum pump is needed; the collapsing bag is itself the air-exclusion mechanism.

**Integration with product exterior:** In commercial installations, the BIB rack lives in a back room or under a counter -- completely hidden. The user-facing element is only the dispensing nozzle. The rack is utilitarian steel wire with no aesthetic consideration.

**Assembly:** The bag connector is brand-specific (Coke and Pepsi connectors are mechanically incompatible). The connector pushes onto the bag fitment and locks with a quarter-turn. The box drops onto the shelf. No tools, no fasteners.

**Product unity:** None. The rack, box, bag, connector, and tubing are all separate vendor products that happen to work together. This is an industrial system, not a consumer product.

**Pattern:** *Rigid shell as proxy constraint.* The bag is never directly constrained. Instead, a rigid outer shell (cardboard box) provides the shape boundary, and gravity plus atmospheric pressure handle the rest.

---

### 1b. Boxxle Wine Dispenser (US Patent 8,763,857)

**How the bag is held:** The user opens the top of the stainless steel housing and drops the wine bladder (extracted from its cardboard box) inside, with the spigot oriented upward. A spring-loaded platform sits beneath the bag. When the lid closes, a trigger releases the spring, and the platform rises to press against the underside of the bag. The bag is suspended from above by its spigot, which protrudes through a shaped opening in the housing, and compressed from below by the rising platform.

**Complete drainage:** The spring-loaded platform continuously compresses the bag as it empties, maintaining constant pressure on the remaining liquid. This pushes liquid upward toward the spigot and prevents the bag from going slack or developing air pockets. The spring force is calibrated to provide enough pressure for a smooth pour without manual squeezing, and to extract nearly all liquid from the bag.

**Integration with product exterior:** The entire mechanism is hidden inside a polished stainless steel or painted housing. The only visible element is the spigot protruding from the front face. The housing reads as a single solid object -- a countertop appliance, not a bag holder.

**Assembly:** Open lid, drop bag in, close lid. The spring mechanism is automatic. No clips, no alignment features beyond the spigot opening. The simplicity of loading is a core design value.

**Product unity:** High. The Boxxle transforms an industrial BIB bag into something that looks and feels like a countertop beverage appliance. The bag is invisible. The interaction model is: open, drop, close, pour.

**Pattern:** *Spring-loaded compression platform.* A rising floor continuously compresses the bag, maintaining pressure and shape as volume decreases. The bag is constrained between a fixed ceiling (the housing) and a moving floor (the spring platform).

---

## 2. Medical Pressure Infuser Bags (Merit Medical PIB, SunMed Infu-Surg, ICU Medical Clear-Cuff)

**How the bag is held:** An IV fluid bag (500mL to 3000mL) is placed inside a pressure envelope -- a two-layer sleeve consisting of an inflatable bladder on one side and a nylon mesh or clear window on the other. The IV bag slides between these two layers. The envelope wraps around the IV bag like a book cover. When the hand bulb is pumped, the bladder inflates and compresses the IV bag uniformly from one side against the mesh backing.

**Complete drainage:** The uniform pressure (typically 300 mmHg) compresses the IV bag evenly across its entire surface area, forcing fluid out at 2-2.5x the rate of gravity alone. The mesh backing distributes the reaction force, preventing the IV bag from bulging or developing unpressed pockets. The IV bag is hung vertically on a pole, so gravity assists drainage toward the bottom outlet.

**Integration with product exterior:** The pressure infuser is a standalone device that wraps around the IV bag -- it does not hide inside an enclosure. Visibility is a feature: the nylon mesh or clear panel lets clinicians monitor fluid level. The inflation bulb, pressure gauge, and stopcock are external. This is a tool, not an appliance.

**Assembly:** Slide IV bag into the envelope sleeve. Close the envelope (typically a hook-and-loop or snap closure along one edge). Hang on IV pole via a blunt hook. Inflate with hand bulb. One-handed operation is a key design constraint.

**Product unity:** The infuser bag is designed to disappear around the IV bag -- it is a compression wrapper, not a container. Unity comes from the fact that the assembled unit (infuser + IV bag) reads as a single hanging object on the pole.

**Pattern:** *Inflatable bladder envelope.* A two-sided sleeve where one side is rigid/transparent (observation) and the other is an inflatable bladder (compression). The flexible container is sandwiched between these two surfaces. Pressure is uniform and adjustable.

---

## 3. Hydration Pack Bladder Compartments

### 3a. Osprey Hydraulics Reservoir (2L / 3L)

**How the bladder is held:** The Osprey Hydraulics uses a rigid plastic backer plate bonded to the rear face of the bladder. This backer plate is the key structural innovation -- it prevents the filled bladder from folding, bending, or buckling when inserted into a loaded backpack. A center baffle runs vertically through the interior of the bladder, dividing it into two connected chambers. This baffle serves two purposes: it reduces the cross-sectional thickness of the filled bladder (making it flatter), and it prevents water from sloshing side-to-side during motion. The bladder slides into a dedicated sleeve compartment in the backpack, where the backer plate sits flat against the user's back panel. An ergonomic plastic handle at the top allows the bladder to be pulled out for filling.

**Complete drainage:** The quick-disconnect hose attaches near the top of the bladder. The center baffle channels water toward the outlet but also creates internal surfaces where water can pool. Osprey's own design acknowledges this tradeoff: the internal walls tend to stick together when wet, impeding both drainage and drying. The sliding closure restricts airflow, contributing to extended drying times. Complete drainage is not a primary design goal -- the bladder is refilled, not emptied to the last drop.

**Integration with product exterior:** The bladder is completely hidden inside the backpack. The only visible element is the drink tube, which routes through a port in the pack and clips to the shoulder strap via a magnetic bite valve attachment. The reservoir compartment is a shaped fabric sleeve sewn into the pack's back panel.

**Assembly:** Slide bladder into sleeve compartment (backer plate guides the insertion). Route hose through pack port. Clip bite valve to shoulder strap magnet. All tool-free, all by feel.

**Product unity:** High within the Osprey ecosystem. The bladder, sleeve, hose port, and magnetic clip are designed as a system. The backer plate is the key enabler -- without it, the bladder would deform unpredictably and the slide-in interaction would feel imprecise.

**Pattern:** *Rigid backer plate + internal baffle.* One face of the flexible container is stiffened with a bonded rigid panel. Internal baffles subdivide the volume to control shape, reduce slosh, and maintain a low profile. The rigid face provides a datum surface for insertion into a shaped sleeve.

---

### 3b. CamelBak Crux Reservoir (1.5L / 2L / 3L)

**How the bladder is held:** Unlike Osprey, CamelBak's Crux has no rigid backer plate. Instead, it uses an internal center baffle that runs down the middle of the bladder's interior, creating a lower-profile shape by distributing the water volume across a wider, thinner footprint. The bladder is entirely flexible. It sits in a fabric sleeve in the backpack, held in place primarily by friction and the compression of surrounding gear.

**Complete drainage:** The center baffle improves drainage by channeling water toward the hose attachment point and preventing large pools from forming in dead zones. CamelBak optimized the baffle geometry and increased tube diameter at the bladder connection to improve flow rate without requiring harder suction. The baffle also reduces sloshing, which indirectly helps drainage by keeping water distributed rather than pooled.

**Integration with product exterior:** Same as Osprey -- completely hidden inside the pack. Hose routes through a port, bite valve clips to strap.

**Assembly:** The fully flexible bladder can be rolled or folded to fit into tight spaces, which CamelBak positions as an advantage over rigid-backed competitors. Trade-off: less predictable shape during insertion, but more forgiving of varied pack geometries.

**Product unity:** The flexibility is the design statement. CamelBak trusts the backpack sleeve to provide external shape constraint, and focuses the bladder design on flow performance and ease of cleaning.

**Pattern:** *Internal baffle without rigid structure.* The flexible container uses only internal geometry (welded baffles) to control its shape and drainage characteristics. External constraint is delegated to whatever compartment receives it.

---

## 4. Coffee Capsule Clamping Systems

### 4a. Keurig K-Cup Pod Holder Assembly

**How the pod is held:** The K-Cup sits in a molded plastic cradle (the pod holder) that matches the cup's tapered cylindrical geometry exactly. The cradle is a 3-part assembly: pod holder cup, housing, and base. The pod drops into the holder by gravity, with the tapered walls centering it automatically. When the brew head closes (lever-actuated), an upper needle pierces the foil lid from above, and a lower needle (integrated into the holder base) pierces the plastic bottom from below. The closing action clamps the pod rim between the brew head gasket and the holder rim, creating a pressure seal.

**Complete drainage:** Water enters through the upper needle, pressurizes the pod interior, and forces brewed liquid out through the lower needle. The pod is designed for single-use total extraction -- there is no "draining" in the gravity sense. Pressure does all the work.

**Integration with product exterior:** The pod holder is accessible through a lift-up brew head. When closed, the mechanism is completely hidden behind the machine's plastic shell. The user sees only the lever and the drip tray. The pod holder can be removed for cleaning by pressing a release tab and pulling up.

**Assembly:** Drop pod into holder, close lever. The tapered geometry is self-aligning. The snap-out pod holder uses a spring clip for retention -- press the circle on the bottom, pull up to remove. No tools.

**Product unity:** The entire interaction -- lift, drop, close, brew -- feels like operating a single mechanism. The pod holder's snap-fit retention and the lever's cam action make the multi-part assembly feel monolithic.

**Pattern:** *Geometry-matched cradle with clamp seal.* A rigid cradle matches the container's exact outer geometry. A closing mechanism applies clamping force that simultaneously seals, pierces, and locks the container in position.

---

### 4b. Nespresso Vertuo Capsule System

**How the capsule is held:** The dome-shaped Vertuo capsule is larger than a K-Cup and is inserted into a shaped receptacle in the brew head. The machine reads a barcode printed around the capsule's rim (printed 5 times around the circumference so orientation does not matter). The capsule is clamped and sealed, then spun at up to 7,000 RPM by the Centrifusion mechanism. The spinning distributes hot water through the coffee grounds via centrifugal force rather than simple pressure.

**Complete drainage:** Centrifugal force drives extraction radially outward through the capsule walls. The high-speed rotation ensures uniform contact between water and grounds across the entire capsule volume, achieving more complete extraction than gravity or pressure alone.

**Integration with product exterior:** The capsule insertion point is a small opening on the machine's top surface. The entire spinning mechanism is hidden. The barcode system eliminates any need for the user to align or orient the capsule -- any rotation works.

**Product unity:** The barcode-driven automatic parameter adjustment (water volume, temperature, spin speed, brew time) means the user's only interaction is insert and press. The machine adapts to the capsule, not the other way around. This is the highest-unity capsule system in the market.

**Pattern:** *Orientation-independent receptacle with active reading.* The container can be inserted in any rotational orientation. The machine reads the container's identity and adapts its behavior. The user never needs to align anything.

---

## 5. Juicero Press (Yves Behar / Ammunition design, teardown by Bolt.io)

**How the pack is held:** A flat, pillow-shaped juice pack (roughly the size of a paperback book) is inserted through a front door. The pack hangs from a registration feature at the top and rests against silicone alignment pads that survive repeated four-ton compressions. The front door of the machine is the press platen -- when the door closes and locks (via solenoid-actuated aluminum latch), the entire back wall of the machine advances toward the door via an ACME leadscrew driven through a multi-stage hardened steel gear train. The pack is compressed between the advancing back wall and the locked door across its full 64 square inches of surface area simultaneously.

**Complete drainage:** The uniform full-surface compression squeezes the pack flat, forcing all juice out through a single outlet at the bottom. The pressing force (approximately 8,000 lbs distributed across 64 square inches) leaves the pack as a nearly dry, flat sheet of compressed pulp. There are no air pockets because the pack is pressed from full thickness to nearly zero thickness.

**Integration with product exterior:** The machine is a countertop appliance designed by Yves Behar (Ammunition Group). The massive internal aluminum drivetrain is completely hidden behind smooth exterior panels. The door opens and closes like a small appliance door. The only user-facing elements are the door, a WiFi indicator, and a drip tray.

**Assembly:** Open door, hang pack on registration feature, close door, press button. The machine auto-locks the door, presses, and unlocks when done. The registration feature ensures the pack's outlet aligns with the juice channel.

**Product unity:** Extremely high from the outside -- the Juicero looked like a premium small appliance. However, the internal engineering was infamously over-built (custom machined aluminum components, precision gear trains, solenoid locks) for what turned out to be a problem solvable by hand. The lesson: product unity on the outside does not require engineering complexity on the inside.

**Pattern:** *Full-surface compression between fixed platen and advancing wall.* The flexible container is pressed flat between two rigid surfaces. One surface is fixed (the door), the other advances via a linear actuator. Registration features align the container's outlet with the machine's juice channel.

---

## 6. Breast Pump Milk Bag Adapters (Maymom, Motif Medical, Papablic)

**How the bag is held:** A polypropylene adapter with stainless steel spring clips attaches between the breast shield (flange) and a standard milk storage bag. The adapter redirects pumped milk from the normal bottle path into the bag. The spring clips grip the bag's opening with enough force to hold the bag securely during pumping and support the weight of filling milk, but release easily when the user intentionally disengages them.

**Complete drainage:** Not applicable in the fill direction -- these systems fill bags, not drain them. However, the adapter geometry is designed so milk flows downward by gravity from the shield into the bag, preventing pooling in the adapter body.

**Integration with product exterior:** The adapter is a small, visible accessory that clips between existing components. It is not hidden -- it is designed to be as unobtrusive as possible while remaining accessible for frequent bag changes.

**Assembly:** Clip adapter onto breast shield, clip bag opening into spring jaws. The stainless steel springs provide tactile feedback (a click) when the bag is seated. The entire assembly is one-handed operable -- a critical constraint given the use context.

**Product unity:** Moderate. The adapter is clearly a third-party accessory bridging two systems (pump and bag). But the spring-clip mechanism is satisfying and confident in use, which compensates for the visual complexity.

**Pattern:** *Spring-jaw clip at transfer point.* A spring-loaded clip grips the flexible container at its opening, holding it in position relative to a fluid transfer interface. The clip provides both retention force and tactile confirmation of engagement.

---

## Cross-Product Pattern Analysis

### Pattern A: Rigid Shell as Shape Proxy
**Products:** Commercial BIB racks, Keurig pod holder
**Mechanism:** The flexible element is placed inside a rigid container that defines its shape boundary. The outer system constrains the rigid shell, not the bag directly.
**UX implication:** The user handles a rigid object, not a floppy one. This makes insertion predictable and satisfying.
**Product unity:** High when the shell is part of the product design (Keurig). Low when the shell is disposable packaging (cardboard BIB box).

### Pattern B: Compression Between Two Surfaces
**Products:** Boxxle (spring platform + housing ceiling), Juicero (advancing wall + door), medical pressure infusers (inflatable bladder + mesh backing)
**Mechanism:** The bag is sandwiched between two surfaces. At least one surface moves or inflates to maintain contact as the bag changes volume.
**UX implication:** The user does not need to handle the bag during use. The mechanism maintains shape and pressure automatically.
**Product unity:** Very high. The compression mechanism is hidden inside the enclosure. The bag is invisible during operation.
**Drainage:** This pattern directly serves complete drainage -- continuous compression forces liquid toward the outlet and prevents slack/pooling.

### Pattern C: Rigid Backer with Shaped Sleeve
**Products:** Osprey Hydraulics reservoir, Platypus Big Zip (handle mount)
**Mechanism:** One face of the flexible container is stiffened (bonded rigid plate or integrated handle/spine). This rigid face slides into a shaped fabric or plastic sleeve, providing a datum surface for positioning.
**UX implication:** The rigid face makes insertion directional and confident. The user pushes a flat panel into a slot, not a floppy bag into a hole.
**Product unity:** High when the sleeve and backer are designed together. The backer-plus-sleeve interaction can feel like inserting a drawer.

### Pattern D: Internal Baffles for Shape Control
**Products:** Osprey Hydraulics (center baffle), CamelBak Crux (center baffle)
**Mechanism:** Welded seams inside the flexible container divide the interior volume, controlling cross-sectional shape and preventing the bag from ballooning unevenly.
**UX implication:** The bag maintains a predictable footprint as it fills and empties. Internal geometry replaces external constraint.
**Drainage:** Baffles can channel liquid toward an outlet, but they also create internal surfaces where liquid can pool or walls can stick together. There is a tradeoff between shape control and drainage completeness.

### Pattern E: Gravity Angle + Atmospheric Collapse
**Products:** BIB syrup racks (slanted shelves), wine bag-in-box (collapsing bag)
**Mechanism:** The bag is tilted so the outlet is at the lowest point. As liquid exits, atmospheric pressure collapses the bag walls inward, preventing air ingress and maintaining contact between bag walls and remaining liquid.
**UX implication:** Passive -- no moving parts, no user action required during dispensing. The physics are invisible.
**Product unity:** Neutral -- the tilt angle is a property of the mounting surface, which can be integrated into any enclosure shape.
**Drainage:** Very effective for complete evacuation. Scholle IPN achieves 99%+ evacuation through gravity angle combined with bag film properties that promote uniform collapse.

### Pattern F: Registration Feature at Transfer Point
**Products:** Juicero (pack hangs from top registration), Keurig (tapered geometry self-centers), Nespresso Vertuo (barcode eliminates orientation), breast pump adapters (spring clip at bag opening)
**Mechanism:** A specific geometric feature on the flexible container mates with a matching feature on the holder, ensuring the container's inlet/outlet aligns precisely with the machine's fluid path.
**UX implication:** Alignment is automatic or impossible to get wrong. The user drops/inserts the container and the geometry does the rest.
**Product unity:** Very high. When alignment is effortless, the insertion feels like two halves of a single mechanism coming together.

---

## Key Observations for Appliance Design

1. **The highest-unity products hide the bag entirely.** Boxxle, Juicero, and Keurig all make the flexible element invisible during normal operation. The user interacts with rigid surfaces (doors, lids, levers), never with the bag itself.

2. **Complete drainage requires either compression or gravity angle (or both).** Passive atmospheric collapse works well when the bag is oriented correctly. Active compression (spring, actuator, inflatable bladder) works regardless of orientation but adds mechanical complexity.

3. **A rigid datum surface transforms the insertion experience.** Osprey's backer plate and Keurig's pod geometry both solve the same UX problem: making the insertion of a flexible/small element feel precise and confident. Without a datum surface, the user is stuffing a floppy bag into a hole.

4. **Internal baffles are a double-edged sword.** They control shape and prevent sloshing, but they create internal surfaces that can trap liquid or cause walls to adhere. For a system where complete drainage matters, baffles should channel toward the outlet, not create dead zones.

5. **The best loading interactions are single-axis motions.** Drop in (Boxxle, Keurig), slide in (Osprey), hang and close (Juicero). Multi-step alignment procedures (rotate, then tilt, then clip) erode the feeling of product unity.

6. **Continuous compression maintains bag shape as volume changes.** This is the Boxxle insight: a spring-loaded surface that tracks the bag as it empties prevents the bag from going slack, pooling, developing air pockets, or shifting position. The bag's shape is controlled throughout its entire fill-to-empty cycle, not just when full.
