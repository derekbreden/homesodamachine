# borrowed-18-examples-in-hardware: what bought hardware would realise Derek's examples, and what each product changes

Origin: Derek's examples (suspension, the monitor arm, the table opening, the automated-setup vision), read through the borrowed framing in wave 2. Maturity: sketch (a survey with numbers and sources; the drawn parts are borrowed-13 to borrowed-17). No scene of its own; the balanced-arm example is drawn in `scenes/borrowed-14-arm-mass-window`, its sled neighbour in `borrowed-15-sled-keel`, the hung-on-lines neighbour in `borrowed-16-taut-cone`, the multi-axis positioners in `borrowed-17-positioner-shelf`.

## Picture it

A workshop shelf with four labelled boxes, one per example. In each, the real parts that would be bought this week, with the number that matters on a tag: a rubber-lined clamp with the friction the screw sets, a spring balancer with a 0.5 to 1.5 kg window, a mic boom with a 1.5 kg rating and 24,099 ratings, a gantry rail with a preloaded block, a dual-motor lift frame rated for 220 lb, a PTZ camera with ten presets. Beside each part, one sentence: what it changes about Derek's idea.

## The proposal

For each example, in Derek's words and then in the products: what bought hardware would actually realise it, and what each product changes. Prime listings observed 2026-09-28 and 29; prices and delivery are single observations; nothing was ordered (sourcing/borrowed.md).

### Suspension: hooks as complete loops, wire in Z, bungees in X or Y, a shell gripped by an arm

- **The loop.** "One of those metal rubber coated hooks on pegboard walls ... a complete (openable) loop." The bought openable loop is a rubber-cushioned P-clamp (LOKMAN 2 in stainless with rubber, 20 pack, $17.99, 6,185 ratings, "100+ bought", same-day delivery on orders over $25; sizes from a half inch to three inches). Changes: the loop is a *clamp*, so its friction limit is set by the screw torque, which turns freedom-01 round 1's unknown (1, 4, 8 N) into a number Derek can read (pull the sleeve through with the Newton meter); the inside diameter is fixed per size, so the shell's sleeve is printed to size. Pegboard hooks themselves (2 in, 50 pack, $13.99, 344 ratings, "500+ bought") are the anchors of room-11's lattice.
- **The wire held in Z.** A plain wire is a stiff element, a position, not a force (freedom-01 round 2). The bought force element is a spring balancer's cable (Tigon TW-1R 0.5 to 1.5 kg, $39.00; QWORK 2-pack $16.97; MECCANIXITY $20.29): constant force over its stroke, so no restoring stiffness in Z, held by the balancer's friction. Changes: Z is a force axis and the arm owns the position.
- **The bungees in X or Y.** Bungee cord (1/4 in, 100 ft, $19.99, 761 ratings) has a stiffness of EA/L, so the length is the stiffness knob; creep and hysteresis are what freedom-01c notes. Two spring balancers opposing along X (or Y) are a *zero-stiffness* horizontal support where friction is the only stiffness: Derek's bungee with the restoring force removed, which is a different thing and may be what "steadyish" wants for a soft axis. Nobody has measured a bungee here; the Newton meter does it.
- **The two loops define a hinge** (freedom-01 round 4). The bought neighbour is a stabiliser sled: a gimbal handle plus a bottom weight (FLYCAM HD-3000, $178, up to 3.5 kg); a keel defines the equilibrium at the working roll and supplies the spring (borrowed-15).
- **The arm's grip.** The cushion clamp again, or a printed shell with the arm's own interface: a 1/4-20 or 3/8 thread and a dovetail are how every arm, boom and head above is mounted.

### The monitor arm ("too flexible")

- Bought range: Prime arms from 0.25 to 9 kg (RODE PSA1+ 0.25 to 1.2 kg, $112; InnoGear 1.5 kg, $19.99, 24,099 ratings; Elgato Wave Mic Arm Pro gas spring 3 kg, $179.99; HUANUO monitor arm 2 to 9 kg, $35.99, 16,507 ratings). Changes: the payload floor of gas-spring monitor arms is a selection problem once the total is weighed (borrowed-14), and the rating window is on mass only.
- A monitor arm is a SCARA with a balanced Z: two swivels (no gravity torque, so small motors could drive them) and a spring-balanced lift; its VESA head is a three-rotation head with hex-key friction. Its swivels' pre-sliding decides the yaw of the shell (freedom-04's lever times angle).
- The spring-and-parallelogram mic boom or Anglepoise lamp is the same arm with a zero-length spring: balanced at every angle for one payload; friction forgives about 90 g at 0.4 N.m and 0.45 m.

### The table with a hole, the rotator underneath, a low gantry

- **Gantry rails and frames:** MGN12 300 mm rail with a preloaded carriage ($20.49, 615 ratings), 2020 T-slot extrusion 4 x 300 mm ($17.99, 984 ratings, "100+ bought"), or a whole printer (Ender-3 V3 SE, $219, 2,153 ratings, "500+ bought", G-code, 250 mm Z) or CNC router (Genmitsu PROVerXL 4030, $659, 525 ratings, GRBL). A CNC's Z axis is built to carry a spindle (hobby router spindles are roughly 1 to 2 kg [general knowledge, unchecked]), which is the gun and shell's mass class; its 52 mm-class spindle clamp would hold a printed shell. Its Z travel was not read (the maker lists about 110 mm; unchecked). Changes: the countertop-height gantry of Derek's description is a CNC gantry with the spoilboard replaced by the opening; the interface (G-code, homing, probe input) comes with it; a stock printer carriage carries a hotend, not a gun.
- **Drawer slides:** 20 in ball-bearing pair, $19.79, 150 lb (room-05's drawer). Side play is not stated, and it decides whether the rotator lands on its dock without help.
- **Sit-stand frames:** dual-motor frame, $199.99, 220 lb (VIVO); $169.99 for two others. A stiff, presettable lift for the shelf (room-10) with height resolution and leg skew unstated. It is a setup axis, not a fine one.
- **"The gun is not tangent to the circumference as it needs to be."** The rotations the frame does not supply are the hexapod's, the mount's or the rings' (borrowed-13, borrowed-17, borrowed-01).

### The automated-setup vision (XYZ motors, roll and the opposite roll, PTZ cameras, an AI iterating for days)

- **XYZ:** a printer or CNC gantry with G-code over USB (above). **Two rotations:** a worm-geared telescope mount with encoders and a public Wi-Fi command set (AZ-GTi, $525, 5 kg rating; the gun balanced on it), or a hexapod with a software pivot. **Six degrees:** borrowed-13.
- **PTZ cameras:** NexiGo (pan -170 to +170 deg, tilt -30 to +90 deg, 10 presets, USB, $242.99, 5,521 ratings) and TONGVEO (pan 350 deg, tilt 180 deg, 255 presets, $299, 359 ratings). Neither listing states a control protocol; preset repeatability and latency are not stated. A PTZ camera is a look-here actuator, not a measuring instrument: its pointing repeatability of a tenth of a degree is 1.7 mm at 1 m, so the *image* is the measurement (borrowed-05 calibrates through the dot).
- **Arms:** desktop arms on Prime carry 0.25 to 0.5 kg. A collaborative arm that states 3 kg and +-0.02 mm (Fairino FR3, $6,799) is a maker product; it already contains hand guiding, gravity compensation and a force sensor, the pieces of borrowed-03, freedom-02, freedom-06 and freedom-14 in one product.

## What carries loads, establishes position, is free, restrained or driven

Per product; see the rows in borrowed-17. What carries: the spring and parallelogram of a boom, the gas spring of a monitor arm, the rail's preloaded block, the mount's worm gear, the lift frame's columns.

## Software: command, observe, manual

G-code for printers and CNC (probing and homing included), the SynScan protocol for the mounts, presets for PTZ cameras, vendor SDKs for arms, a controller with a software pivot for hexapods. Which of them can be driven without the maker's app is a fact to check.

## What was tried to break it

1. **"A monitor arm is too flexible"** meets a product range: the rating window covers any payload from 0.25 kg up; the floor stays if the payload is unknown. Left standing: real friction and pre-sliding.
2. **The same count of "nothing states repeatability".** The best-selling gantry parts (printer, rail, frame, slides) state a step or a load, never a repeatability: it has to be measured.
3. **The single most complete product is the most expensive and the slowest to get.** The one arm that carries the gun and states a repeatability under a tenth of a millimetre is $6,799 from a maker; everything else that ships in two days states no such number.

## Branches and combinations

borrowed-13 (hexapod), borrowed-14 (arm window), borrowed-15 (sled), borrowed-16 (cone), borrowed-17 (shelf).

## Unresolved problems and questions that need Derek

- Which of these does Derek already own or have on a shelf (a printer, a monitor arm, a mic boom, a camera slider, a telescope mount)? A first test with what is on hand needs no purchase.
- The gun's mass and centre of mass; whether the shell can carry a 1/4-20 thread and a dovetail on its back.

## Assumptions

Sources tagged in sourcing/borrowed.md: listing (product page read), search (unchecked summary), maker, derived. Hobby router spindle mass and the 110 mm Z of the 4030 are not verified.

## Sourcing pointers

sourcing/borrowed.md wave 2.

## Scene

None (survey). See borrowed-14, borrowed-15, borrowed-16, borrowed-17.
