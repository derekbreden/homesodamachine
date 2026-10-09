# The physical situation

Each statement carries the source it came from.

| Tag | Source |
|---|---|
| **[Derek]** | Derek's own words in this request (`assignment-full.md`) |
| **[repo]** | A file in this repository, path given |
| **[manual]** | XLaserlab X1 Pro manual, PDF page given. Text and page images are at `/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/7a0b6047-5805-4c2c-9dd4-6cb4fb4442ff/scratchpad/x1-manual/` |
| **[derived]** | Arithmetic on the numbers named beside it |
| **[unknown]** | Nobody has measured it |

## What is welded

- A 316L tube, 5.000 in OD × 0.065 in wall × 6 in long, bore Ø123.70 mm, stands vertical. An end plate (Ø4.860 in × 0.250 in, ID slip-fit plug, about 0.005 in radial slip) sits recessed 6.35 mm below the rim. The joint is the inside corner fillet between the plate's outer face and the tube bore: a horizontal circle, r = 61.85 mm, circumference 388.61 mm, 6.35 mm below the rim. **[repo]** `hardware/assembly/pressure-vessel.md`, `hardware/assembly/weld-rotation-rig.md`
- The plate has two Ø0.438 in ports at ±0.750 in from centre and a small register hole on the perpendicular axis. **[repo]** `hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py`
- Two closures per tube. The second closure runs with the first plate as the base; its ports are reachable through a Ø90 mm service bore in the rotator. **[repo]** weld-rotation-rig.md
- Tube length and plate seat depth vary from tube to tube. **[unknown]** how much.

## The rotator

- A motor-driven turntable stands the tube vertical and turns it about its axis. It turns the work; it does not carry the gun. **[repo]** weld-rotation-rig.md, `hardware/printed-parts/fixtures/weld-rotator/README.md`
- Base 300 × 250 × 12 mm PET-GF on four 24 mm feet, clamped to the bench through four Ø10 mm holes; 165 mm ball race; NEMA 23 with a 4.5:1 belt (backdrivable); 150 mm tube nest with three radial adjusters. The tube rim stands 238.4 mm above the bench. **[repo]** the same two files
- Bead travel 5–15 mm/s at the bead: 0.77–2.3 rpm, 26–78 s per revolution; 8 mm/s is the starting value. The foot pedal is a deadman for rotation and does not command the laser. **[repo]**
- Runout accepted at the working end: ≤ 0.25 mm TIR radial and ≤ 0.30 mm TIR face at the weld circle. **[repo]** So the corner moves relative to a stationary gun by up to about that much per revolution.
- A stationary copper shoe wipes the tube for the welder's work-contact interlock; no cable turns with the tube. **[repo]**
- The controller is an ESP32 with a USB serial console at 115200 baud: `status`, `speed`, `direction`, turned-so-far degrees. **[repo]** `firmware/src_weld_rotator/README.md`

## The gun and the laser

- XLaserlab X1 Pro handheld fibre-laser gun, **253 × 143 × 34 mm** overall. The drawing names: copper nozzle, graduated tube (sets nozzle extension), protective-lens drawer, focusing lens, motor, two status LEDs, collimator, QBH connector, light switch, process switch, wire-feeding bracket. **[manual]** p. 17
- The laser head contains a vibration motor. **[manual]** p. 20. Recorded practice settings: power 60 %, wobble 80 Hz × 2 mm, wire feed 12 mm/s, ER316L .030 wire. **[repo]** pressure-vessel.md
- Gun mass, centre of mass, trigger force, umbilical weight and stiffness: **[unknown]**.
- The QBH fibre is 5 m long. Minimum bend radius is 24 cm stored and 35 cm while emitting. The fibre lies in a natural state; twisting is strictly forbidden. **[manual]** p. 20
- The external wire feed is separate from the gun's umbilical; the two run together near the grip base. **[Derek]** The feeder is its own box with a conduit to the gun's wire bracket; gas is a 6 mm OD tube at 15–20 L/min. **[manual]** pp. 16, 19
- The laser dot is the red reference beam, 630–670 nm, 0.3 mW. **[manual]** p. 12. The laser's settings screen has a "red light alignment" adjustment. **[manual]** pp. 25, 39. How closely the dot sits on the melt position at working standoff is **[unknown]**.
- The laser unit has an RS232 port ("PC-based supervisory software") and a DB25 port ("PLC integration by customers"). **[manual]** p. 16
- The laser emits only while a clip on the work and the gun form a complete circuit. The rotator's copper shoe supplies it. **[manual]** p. 19; **[repo]**
- Manual note: for welding, wire feed 5 mm/s, swing 10 Hz, swing width 2 mm. **[manual]** p. 13

## How it is welded today

The operator holds the gun. Sequence: clamp the base; seat and indicate the tube; seat and tack the plate; engage the ground shoe and prove continuity; set the speed; place the wire on the arriving side of the puddle; hold the head at the qualified angle and standoff; press and hold the pedal; once rotation is steady, hold the laser trigger; carry the bead about 20° past the first tack. At the stop the trigger stays held while the operator lifts the head straight away, and the gun's retract cycle breaks the wire in air; then trigger and pedal release. A stuck wire is snipped between nozzle and bead with the head where it stopped. **[repo]** `hardware/weld-rotator-guide/46-the-per-weld-sequence.html`

## The orientation scene

`hardware/assembly/weld-position.md` describes the scene at `web/public/js/weld-position/` (`pose.js`, `main.js`). Coordinates: millimetres, +Z up, tube axis = Z, weld station on the +X side, joint at (61.85, 0, 146.05). The proxy gun follows the manual's envelope; its housing sections, grip, 60° initial pitch and 16 mm nozzle clearance are illustrative. Three rotations pass through the laser dot:

1. Grip-axis roll — about the line from the dot to the cable exit at the bottom of the grip; both endpoints stay fixed; it tips the laser between the endcap and the tube wall.
2. Hole-axis roll — about the horizontal line through the dot and both port centres; it tilts the whole gun and raises the grip.
3. Vertical axis — through the dot, parallel to the tube axis; it turns the gun in plan (positive counter-clockwise from above), −90° to 90°.

At zero grip-axis and vertical rotation the barrel and wire approach follow the tangent in plan. Derek: "Gun handle will need to be tangent to the tube's circle, so that the wirefeed is laid down correctly." **[Derek]** (earlier conversation, as recorded in an earlier agent brief). The mechanism need not reproduce these rotations as literal joints; software coordinates do not remove the physical constraints a support imposes. **[Derek]** The kit in `kit/` draws this gun, tube, endcap, rotator, dot, wire and umbilical.

## Geometry **[derived]**

- Tangent slide. The joint is a circle of r = 61.85 mm. Moving the dot along the tangent by s and re-aiming at the new point on the circle turns the approach angle in plan by s/r ≈ 0.93° per mm (r = 61.85) and moves the joint radially by s²/2r ≈ 0.008 mm at s = 1 mm.
- Lever arm. Grip base at local (0, −118, 237) and the dot at (0, 0, −16) on the proxy gun are √(118² + 253²) ≈ 279 mm apart. One degree about a pivot at the grip base moves the dot ≈ 4.9 mm; about a pivot at the dot, 0.
- Line of sight. The dot sits 6.35 mm below the rim of a Ø123.70 mm bore, against the wall. A line from the dot to a camera outside the tube meets the wall.
- One revolution moves the joint 388.6 mm past a stationary gun.

## Capabilities

- Scanning a gun and printing a shell that fits it are established. **[Derek]** Revopoint MINI 2 scanner (0.02 mm stated single-frame accuracy) and two Bambu H2C printers; drill press, metal band saw, taps and dies, heat-set inserts, M3/M5 stock, calipers, a Neoteck 0.0005 in indicator with magnetic base, the X1 Pro itself, argon. **[repo]** `hardware/ledger/tools.md`
- The rotator is clamped to a workbench. Its top and height are **[unknown]** to this study.

## Goals

Derek's words, verbatim, are the first paragraph of every brief (`goals.md`).
