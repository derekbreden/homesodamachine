# Design Patterns: Converting User Action into Hidden Linear Translation

Research into how shipped consumer products solve the interaction problem of converting a compact user-facing action into linear translation behind a wall, where the mechanism is invisible during normal use.

---

## Pattern 1: Bayonet Mount (Twist-to-Lock with Cam Ramps)

### Products
- **Canon EF/RF lens mounts** (1987-present): three asymmetric bayonet tabs, ~60-degree rotation, spring-loaded locking pin
- **GU10 light bulb sockets**: two-pin push-and-twist, ~90-degree rotation to lock
- **Espresso machine portafilters** (La Marzocco, Breville): large-diameter bayonet with gasket compression

### Mechanical Geometry
The bayonet mount uses radial tabs on one part that slide into L-shaped slots on the mating part. The "L" shape consists of an axial entry channel (the user pushes straight in) followed by a circumferential locking channel (the user twists). The circumferential channel may include a slight axial ramp, so the twist motion pulls the two parts together by a few millimeters --- converting rotation into linear clamping force. A spring-loaded pin (Canon) or detent (GU10) catches at the end of travel to prevent back-rotation.

On the Canon EF mount, three tabs are arranged asymmetrically around the circumference so the lens can only enter in one orientation. The locking groove at the 9-o'clock position houses a spring-loaded pin that clicks into a notch on the lens barrel, providing both tactile feedback and positive retention. The entire rotation arc is roughly 60 degrees.

On GU10 sockets, two short thick pins on the bulb push into slots and twist 90 degrees. The pins have a "U" profile that acts as the cam surface, and gravity plus a small detent hold the bulb in place.

La Marzocco's KB90 portafilter replaced the traditional bayonet twist with a straight-insert mechanism, specifically because the repetitive wrist-twisting motion of the bayonet caused barista injury --- a data point about ergonomic limits of twist actions under heavy load.

### Surface Integration
On a camera, the mount flange is visible but reads as a structural element of the product, not a mechanism. On GU10 recessed downlights, the socket is entirely hidden inside the ceiling fixture; only the bulb face is visible. On espresso machines, the portafilter handle protrudes but the bayonet ring is hidden behind the group head body.

### Affordance Communication
Canon: a red dot on the lens aligns with a red dot on the body to indicate insertion orientation. An audible and tactile click confirms lock. GU10: no markings; the two pins self-locate into the only possible slot orientation. Espresso portafilters: haptic resistance from gasket compression provides progressive feedback; the handle points to a specific clock position when locked.

### To an Uninitiated Observer
A camera mount looks like a metal ring with a few notches. Nothing about it suggests it is a mechanism. A GU10 recessed light shows only a flat lens surface; the connection is invisible. An espresso group head looks like a solid metal cylinder; the portafilter appears to simply hang from it.

---

## Pattern 2: Push-Push Heart Cam (SD Cards, Battery Doors)

### Products
- **SD card slots** in cameras, laptops, and game consoles (every major electronics manufacturer)
- **SIM card trays** (Apple iPhone, Samsung Galaxy)
- **Retractable ballpoint pens** (Parker Jotter, etc.)

### Mechanical Geometry
The push-push mechanism uses a heart-shaped cam groove milled into a slider, with a spring-loaded cam follower (a small pin) that traces the groove. On the first push, the follower travels one path through the heart shape and lands in a detent notch, latching the card in position. On the second push, the follower is dislodged from the detent and follows a different return path, releasing the compressed spring which ejects the card.

The entire mechanism fits within a 2.4mm-tall profile in a standard SD connector. Components: an insulator body, a compression coil spring, a cam follower pin, and the heart-cam groove machined into the slider frame. The spring provides both the ejection force and the return bias.

Apple's SIM tray variant replaces the heart cam with a simpler pushrod-and-pivot: a pin inserted into a 0.8mm hole presses a pushrod, which rotates an ejector arm about a pivot point. The arm applies lateral force to pop the tray out of its flush cavity. The pushrod sits in a spring-loaded slot adjacent to the tray cavity.

### Surface Integration
The SD card slot typically presents as a thin horizontal slit, sometimes behind a spring-loaded dust cover that sits perfectly flush with the device housing. The SIM tray is flush with the phone's edge, visible only as a thin seam line and a pinhole. When the card or tray is seated, the mechanism is entirely invisible --- the card's rear face or tray's edge completes the product surface.

### Affordance Communication
SD slots: the card itself acts as the tool; pushing it produces a tactile click at the latch point. SIM trays: a small pinhole is the only visual cue; Apple includes a dedicated ejector tool. Both mechanisms communicate state through position: card flush = locked, card proud = ejected.

### To an Uninitiated Observer
An SD slot looks like a thin line in the device housing. A SIM tray looks like a seamless part of the phone's edge with a mysterious tiny hole nearby. Neither suggests a mechanism exists until actuated.

---

## Pattern 3: Lever-Actuated Cam Linkage (Nespresso, Dyson)

### Products
- **Nespresso Vertuo** coffee machines (Breville/De'Longhi): lever-operated capsule clamping
- **Dyson V10/V11/V15** cordless vacuums: lever-operated bin release
- **Keurig K-Cup brewers**: handle-operated pod piercing and clamping

### Mechanical Geometry
These products use a user-operated lever or handle that drives an internal cam or toggle linkage to produce linear clamping or release motion perpendicular to the lever's arc.

On the Nespresso Vertuo, the user turns a lever from the "unlock" icon to the "lock" icon. This rotation drives a toggle mechanism comprising tie-bars, arms, and rods (per Nespresso patent NZ594282A). The toggle converts the lever's arc into straight-line thrust, clamping the capsule against the extraction plate. The capsule must withstand 4000 RPM centrifugal extraction, so the clamping force is substantial --- yet the lever effort is modest because the toggle linkage provides mechanical advantage at the end of travel (the toggle approaches over-center).

On Dyson cordless vacuums, a red lever on top of the cyclone assembly connects through a cam and spring system to a rod that simultaneously unlatches the bin floor flap and pushes the cyclone shroud downward. One lever motion produces two coordinated linear translations. The cam profile is shaped so that the lever has a progressive feel --- light initial resistance increasing toward the end of travel as the spring compresses.

On Keurig brewers, lifting the handle raises the pod holder assembly clear of the brewing chamber. Closing the handle drives dual piercing needles (top and bottom) into the pod and clamps it against the gasket. The handle pivot is positioned so that closing force increases leverage as the needles reach full penetration depth.

### Surface Integration
The Nespresso lever is a small, sculptural element on top of the machine head, visually integrated as a design feature rather than a mechanical component. When locked, it sits flush against the machine profile. The Dyson lever is colored red against a grey body, deliberately prominent as a functional accent but styled as part of the industrial design language. The Keurig handle is the largest visual element of the machine, doubling as the product's silhouette-defining feature.

### Affordance Communication
Nespresso: embossed lock/unlock icons molded into the machine body mark the lever's two positions. Dyson: the red color universally signals "actuate here." Keurig: the oversized handle invites lifting. All three provide progressive haptic feedback through their cam/toggle profiles --- the user feels increasing resistance that resolves with a definitive stop or click at the end of travel.

### To an Uninitiated Observer
The Nespresso lever looks like a decorative fin on top of the machine. The Dyson lever looks like a colored accent stripe. The Keurig handle looks like the machine's natural lid. None of them look like they drive complex internal mechanisms.

---

## Pattern 4: Threaded Taper with Rotating Collar (Luer Lock, Fuel Caps)

### Products
- **Luer-Lock syringe connectors** (Becton Dickinson, 1930-present): medical standard for twist-lock fluid connections
- **Automotive fuel caps** (GM, Toyota, etc.): threaded closure with ratchet torque limiter
- **Garden hose quick-connects**: threaded collar over tapered gasket

### Mechanical Geometry
The Luer-Lock uses a 6% taper cone pressed into a mating socket. The taper alone creates a friction-fit seal (the "Luer slip"). The lock version adds a threaded collar that rotates freely around the male taper. As the collar is twisted clockwise, its internal threads engage external threads on the female socket, drawing the taper deeper into the socket and compressing the seal. The key insight: the rotating collar is decoupled from the fluid path, so the tubing does not twist --- only the collar rotates.

The "two-piece" Luer-Lock (rotating collar assembled onto the luer body) is the dominant design. Rotation of the collar produces roughly 2-3mm of linear pull-in over approximately 180 degrees of rotation.

Automotive fuel caps use a similar principle but add a ratchet torque limiter. The cap handle connects to a ratchet ring with directional teeth. The ratchet ring drives threaded torque arms on the closure. In the tightening direction, the ratchet slips at a preset torque (the familiar clicking when the cap is tight). In the loosening direction, the ratchet provides positive drive. A spring-loaded lock bolt can disable the loosening drive to create a locking cap.

### Surface Integration
On a syringe, the Luer-Lock collar appears as a smooth, flared ring at the tip --- integrated into the syringe's conical taper so naturally that it reads as part of the syringe shape rather than a separate mechanism. On fuel caps, the mechanism is hidden inside the cap body; the user sees only a smooth knurled grip surface.

### Affordance Communication
Luer-Lock: the flared collar shape invites thumb-and-finger rotation. No markings needed; the motion is self-evident from the form. Fuel caps: arrow icons on the cap indicate twist direction. The ratchet clicking provides definitive audible and tactile confirmation of proper torque. Many modern fuel doors eliminate the cap entirely (capless fuel fillers), making the mechanism literally invisible.

### To an Uninitiated Observer
A Luer-Lock syringe looks like a syringe with a slightly flared tip. A fuel cap looks like a smooth disc with a grip texture. Neither reveals its internal thread or ratchet mechanism from external inspection.

---

## Pattern 5: Magnetic Alignment with Spring-Loaded Contact (MagSafe)

### Products
- **Apple MagSafe** laptop connectors (2006-2019, revived 2021): magnetic power connector
- **Apple MagSafe for iPhone** (2020-present): magnetic charging/accessory alignment
- **Microsoft Surface Connect** port: magnetic charging connector

### Mechanical Geometry
MagSafe uses an array of permanent magnets arranged in opposing polarities to both attract the connector and self-align it rotationally. The connector contains spring-loaded pogo pins that compress against flat contact pads on the laptop. The magnetic attraction provides the clamping force; the pogo pin springs provide the electrical contact force. Ground pins are slightly longer to make contact first, preventing arcing.

The connector is symmetrical so either face can mate. The rectangular metal shroud surrounding the pins acts simultaneously as EMI shielding and as a ferrous target for the magnets in the laptop body. The magnetic force is calibrated so that a sideways pull (tripping on the cable) breaks the connection cleanly, but a direct pull (intentional removal) requires deliberate effort.

MagSafe 2 was redesigned wider and thinner to accommodate thinner laptop profiles, demonstrating that the magnetic alignment approach scales to different form factors by adjusting magnet geometry rather than changing the fundamental mechanism.

### Surface Integration
The laptop port is a thin rectangular recess in the side panel, nearly flush with the housing. When no cable is attached, the port reads as a subtle slot --- less visually prominent than a USB port. The connector itself is a thin, elegant wafer that self-docks magnetically.

### Affordance Communication
The magnetic self-alignment is the affordance. The user does not need to aim precisely; bringing the connector near the port causes it to snap into position. An LED on the connector glows amber (charging) or green (charged) to communicate state. No text, no icons, no alignment marks --- the magnets encode the alignment information physically.

### To an Uninitiated Observer
The MagSafe port looks like a thin, featureless slot. There is no visible mechanism, no moving parts, no markings. The magnetic snap when the connector approaches is the first indication that a mechanism exists.

---

## Pattern 6: Push-to-Release Tab (Washing Machine Drawers, Dyson Cyclone Assemblies)

### Products
- **Bosch washing machine detergent drawers**: internal tab release
- **Samsung washing machine detergent drawers**: dual side-squeeze release
- **Dyson Ball upright vacuums**: canister release button

### Mechanical Geometry
These products use a spring-loaded tab or catch that holds a sliding component in place. The user presses or squeezes the tab to disengage it from a detent, then pulls the component free.

On Bosch washing machines, a small plastic tab inside the back of the drawer must be pressed down to disengage from a retention ridge. The drawer then slides out on guide rails. Reinsertion requires pushing the drawer fully in until the tab clicks over the retention ridge. The tab acts as a cantilever spring --- the molded plastic provides its own return force.

On Samsung front-loaders, the user squeezes inward on both sides of the drawer simultaneously to release dual retention tabs. This two-point actuation prevents accidental release from single-sided bumps.

The Dyson Ball canister uses a prominent button with a coil spring behind it. The button actuates a latch arm through a lever pivot, releasing the canister from the main body.

### Surface Integration
The Bosch tab is entirely hidden inside the drawer cavity --- invisible unless the drawer is open and the user looks inside. The Samsung squeeze points are subtle indentations on the drawer face, barely visible. The Dyson button is deliberately prominent (red against grey) because it is a frequently-used interaction.

### Affordance Communication
Bosch: no external indication at all --- the user must read the manual or discover the tab by feel. Samsung: the indentations suggest "squeeze here" through form. Dyson: red color and protruding button shape universally signal "press me." All provide a click at the release point.

### To an Uninitiated Observer
A Bosch drawer looks like it simply pulls out (the hidden tab is a surprise). A Samsung drawer looks like a featureless rectangular panel. A Dyson canister button is intentionally visible but reads as a simple colored accent.

---

## Pattern 7: Flush-Panel Push-to-Open (Miele, Automotive)

### Products
- **Miele ArtLine built-in appliances**: handleless doors with Push2Open
- **Miele MasterCool refrigeration**: Push2Open doors for flush cabinet integration
- **Automotive glove compartments**: push-to-release latch mechanisms
- **Kitchen cabinet push-open hardware** (Blum Tip-On, Hettich Push-to-Open)

### Mechanical Geometry
Push-to-open mechanisms use a spring-loaded latch that toggles between two states. Light pressure on the closed panel compresses the spring past a cam detent, which then releases stored spring energy to push the panel open. The mechanism is typically a small cylindrical module mounted behind the panel, containing a compression spring and a heart-cam or ratchet toggle (mechanically identical to the push-push SD card mechanism, scaled up).

The Miele Push2Open system eliminates handles entirely. The door panel sits flush with surrounding cabinetry. A light push anywhere on the panel face activates the mechanism, which pushes the door open far enough to get fingers behind the edge. The mechanism module is hidden in the hinge area or behind the door panel.

Blum's Tip-On system uses an electromagnetic variant: a small magnetic catch holds the door closed, and a mechanical push-open device provides the opening force. The magnet provides adjustable holding force independent of the opening spring.

### Surface Integration
This is the ultimate in surface integration --- there is no visible hardware whatsoever. No handle, no button, no recess, no seam line beyond the door gap itself. The entire door face is the interaction surface. The mechanism is hidden behind the panel, in the hinge area, or inside the cabinet.

### Affordance Communication
This is the fundamental tension of flush-panel design: maximum aesthetic integration comes at the cost of discoverability. Miele addresses this with consistent product language (all ArtLine doors work the same way) and subtle visual cues (the door gap line indicates "this is a separate panel"). But a first-time user encountering a single Push2Open panel has no indication that pushing it will do anything. The mechanism communicates through absence --- the lack of a handle implies "push."

### To an Uninitiated Observer
A Miele ArtLine oven looks like a flat panel of glass or metal set into the wall. There are no knobs, no handles, no controls visible. It looks like architecture, not an appliance. This is by design --- the product disappears into the kitchen surface.

---

## Cross-Cutting Themes

### 1. Rotation-to-Translation is the Dominant Conversion Strategy
The vast majority of products that need to convert a user action into linear motion behind a surface use some form of rotation-to-translation: bayonet cam ramps, helicoid threads, toggle linkages, heart cams. This is not coincidence. Rotation is the most compact way to store travel --- a 60-degree twist can produce several millimeters of linear motion within a footprint barely larger than the shaft diameter. Threads and cam ramps are also self-locking under load (friction prevents back-driving), which is valuable for a latch that must stay latched.

### 2. The Best Mechanisms Feel Like One Motion, Not a Sequence
The products with the most satisfying interactions (Canon lens mounts, Nespresso levers, MagSafe connectors) make the entire lock/unlock cycle feel like a single fluid gesture. There is no "step one: push, step two: twist, step three: pull." The user performs one continuous motion and the mechanism handles the complexity internally. The toggle linkage in the Nespresso lever is a good example: the user turns a lever through a single arc, and the toggle internally converts that into first alignment, then clamping, then over-center locking --- three distinct mechanical phases, one user gesture.

### 3. State is Communicated Through Position, Not Labels
The best products communicate locked/unlocked state through the physical position of visible elements rather than through text or even icons. The Canon lens mount is locked when the red dots are not aligned; unlocked when they are. The Nespresso lever points at a lock icon in one position and an unlock icon in the other --- but even without the icons, the lever position itself communicates state. MagSafe communicates "connected" through the LED and through the physical snap. The SD card communicates "locked" by being flush and "ejected" by protruding.

### 4. Haptic Feedback Encodes Information
Every well-designed mechanism provides at least two forms of non-visual feedback: a progressive resistance curve during actuation and a definitive endpoint (click, detent, or over-center snap). The progressive resistance tells the user "you are actuating the mechanism." The endpoint tells the user "the mechanism has completed its travel." Products that lack either of these (e.g., a Bosch washing machine drawer with no click on insertion) feel ambiguous. Products that have both (Canon lens click, Nespresso lever stop, fuel cap ratchet) feel precise and trustworthy.

### 5. Frequency of Use Determines Visibility
Products calibrate mechanism visibility to usage frequency. The Dyson bin release lever is used every cleaning session, so it is red, prominent, and immediately obvious. The Bosch drawer tab is used a few times per year, so it is hidden inside the drawer. The SIM tray is used once when setting up a phone, so it is completely flush with a pinhole. The Miele Push2Open has no visible hardware at all because the entire door is the interface. This is a deliberate design spectrum, not a coincidence: mechanisms that are used rarely should disappear; mechanisms that are used constantly should be prominent.

### 6. The Mechanism Should Not Dominate the Surface It Lives In
In every best-in-class example, the mechanism occupies a small fraction of the product surface it is embedded in. The Canon mount flange is a thin ring on the camera body. The Nespresso lever is a small fin on top of the machine head. The MagSafe port is a narrow slot. The SD card slot is a hair-thin line. Even the Dyson lever, the most prominent mechanism in this survey, is a slim element compared to the cyclone assembly it sits on. The mechanism is subordinate to the product surface, not competing with it. This is what distinguishes a product from an assembly of parts: every element knows its visual hierarchy.

### 7. Self-Alignment Reduces Cognitive Load
The products with the best UX eliminate alignment as a user task. MagSafe uses magnets to self-align. Canon uses asymmetric tabs so the lens can only enter one way. Nespresso capsules drop into a cup that positions them automatically. GU10 pins can only fit their slots. Fuel caps have keyed entries. The user does not need to inspect, orient, or aim --- they bring the two parts into proximity and the geometry handles alignment. This is especially important for interactions that happen in awkward positions (inside a dark cabinet, above eye level, one-handed).

### 8. Decoupling the Actuation Surface from the Mechanism
Several of the best designs decouple what the user touches from what moves internally. The Luer-Lock rotating collar spins freely around the stationary fluid path. The Nespresso lever turns on a pivot while the toggle linkage translates linearly. The washing machine drawer slides on rails while the hidden tab flexes. This decoupling allows the user-facing surface to optimize for ergonomics (comfortable grip, natural motion arc) while the mechanism surface optimizes for function (thread pitch, cam profile, spring force). When these are coupled --- when the user must directly manipulate the mechanism itself --- the interaction quality drops because mechanism geometry rarely coincides with ergonomic geometry.
