# travel-20-arm-joints-at-the-dot: what a bought arm's joints put at the dot

Origin: wave 3's new direction (bought robot arms and other multi-axis positioners with a software interface). Depth: deep (seven rounds). Scene: `scenes/travel-20-arm-joints-at-the-dot`. Calculations: `calc/15-arm-radial-line.mjs` (with `calc/arm6r.mjs`, the UR3e link lengths in plain JS, mirrored in `scenes/travel-20-arm-joints-at-the-dot/arm6r.js`). Companions: `travel-21-arm-parks-rotator-turns` (the arm and the rotator through one closure), `travel-22-arm-docks-then-floats` (the arm and a seat).

**Picture it.** A grey-and-purple six-axis arm stands on a pedestal beside the rotator and holds the gun by a printed adaptor bolted to the shell's housing. From the dot, six arrows fan out, one per joint, each as long as the dot would move for the same small error at that joint. The ones that lie along the radial and vertical are orange; the ones along the tangent, where the seam is free because the tube's turn slides it through, are green. Slide the base around the tube and the arrows swing; change where the flange grips the shell and the wrist arrows shrink or grow; swap the arm for a SCARA or a gantry and two or three of the arrows shorten.

## The proposal (an allocation of motion)

The framing asks which body moves and which stays, what range and resolution each stage needs, and which stage's error shows up as which error at the dot. For a bought arm the answers are unusually clean, because **the tube's rotation makes the whole path.** The arm never follows the seam; it parks, comes back, trims and holds. That changes what the datasheet is asked:

| a datasheet line | is it asked for here? |
|---|---|
| speed, acceleration, path accuracy, TCP speed | no: the arm is still while the tube turns (`travel-21` counts 0 s of arm and rotator moving together unless a follow is asked for) |
| **pose repeatability** (ISO 9283: return to a taught pose) | **yes: it is the figure for the closure's two approaches** (leave, come back), UR3e +-0.03 mm, Fairino FR3 +-0.02 mm |
| absolute accuracy | no: the last trim (a camera or a touch) removes it |
| **stiffness at the flange, lost motion, drift** | **yes, and it is on no datasheet read**: it decides what the weld's load change does after the last look |
| payload | yes, with the centre-of-gravity offset: the UR3e chart falls from 3 kg at small offsets to about 2.6 kg at 190 mm and 1.3 kg at 400 mm; the gun at 1.5 kg (unknown) is inside at every grip drawn |
| joint encoder resolution | only as a floor: 19 bits is 12 microradians a count, 0.4 to 3 micrometres at the dot; 12 bits (the desk arms) is 1.5 milliradians, 0.1 to 0.5 mm a count |

What the gun needs, in degrees of freedom at the dot: **radial and vertical** (the two real position requirements), the **plan angle** (which a tangent shift also supplies, at 1/r) and the **beam tilt** in the radial section: four. Roll about the beam is free for the dot (and twists the fibre), and the tangent is free to first order. A six-axis arm has two spare; a SCARA has four axes for the three it can supply (radial, vertical, plan angle, twice) and needs the tilt set by hand; a gantry has three and the same.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** the arm's flange carries the shell through a printed adaptor: the joints carry the gun's weight and the umbilical's pull. (The stack branch puts a two-plate stack under the rotator; the stage branch puts a plate between flange and shell, in the load path.)
- **Establishes position:** the taught pose (return repeatability), then the last trim by a camera or touch, made by the arm's own counts, a stack under the work or a stage at the flange.
- **Free / restrained / driven:** free: the tangent (the seam slides through it) and roll about the beam; restrained: the joints by their servos or brakes; driven: six joints (or four, or three).

## What software could command, observe, what stays manual

- **Commands:** the maker's SDK takes joint angles (`moveJ`, streaming `servoJ`) or a flange pose in a user frame (`moveL`, streaming `servoCart`, 60 to 1000 Hz on the Fairino, per its documentation as found by search; the UR3e's RTDE streams at up to 500 Hz).
- **Observes:** six absolute joint angles, exactly; the flange pose computed from them (the dot only if the flange-to-dot vector is calibrated, and its error is a lever the size of the gun); on some arms the flange force (UR3e: +-2 N precision); the rotator's angle through a pulse input (UR3e: four quadrature inputs; Fairino FR3: two high-speed pulse inputs), where today the controller's degrees are a readout.
- **What each interface gives an AI.** Joint space names which joint moves: the AI can avoid reversing the base joint, can trim through the shoulder and elbow only, and can read the quantum (one count) of each; a Cartesian command hides which joints move and rounds every joint change to a count (the scene's "trim made of asked" shows a 12-bit arm leaving 0.10 to 0.13 mm after a perfect look and a 19-bit arm 0.001 to 0.002 mm). Cartesian is the right level for the nudge, joint space for the big moves and for the read-back.
- **Manual:** mounting the base and the adaptor; declaring payload and centre of gravity; the fibre and conduit routing; firing.

## What was tried to break it

Rounds 1 to 3 are the baseline map (`calc/15`), rounds 4 to 7 are the breaks.

**Round 1 (baseline).** The scene's default: a UR3e-link-length arm, base 300 mm out and 150 mm up, housing-top grip, 0.01 degree at every joint. Micrometres at the dot in the radial-plus-vertical directions, per joint J1 to J6: 0, 40, 5, 41, 12, 35: 68 in all; along the tangent 60. The same errors put the gun's plan yaw off by 0.012 degree and its beam tilt by 0.019 degree.

**Round 2 (break): where the base stands.** *Conflict:* an arm's base joint moves the dot perpendicular to the line from the base to the dot; with the base on the radial line through the station (azimuth 0 or 180) that direction is the tangent, so the base joint's error costs nothing. *Assumption:* one joint of six is worth placing. *What the change alters:* the table over ten azimuths, base 300 mm out and 150 mm up: 61 micrometres (azimuth 210) to 100 (azimuth 180) for the housing-top grip; the barrel grip 63 to 102; from behind along the beam 76 to 142 where it reaches at all. Azimuth 0 gives 0 of 68 for the base joint and is not the smallest total: the elbow and wrist solution that placement needs costs more than the base saves. No simple rule; the map is a Jacobian, so an AI can compute it at commissioning and pick the base position. *What it leaves uncertain:* real joint errors are not equal.

**Round 3 (break): the wrist's lever is the gun.** *Conflict:* the dot is at the far end of the gun, so the last three joints have a lever of the flange-to-dot distance: 209 mm at the housing top, 107 mm at the barrel, 309 mm from behind along the beam. The last joint's axis passes through the dot when the arm grips from behind along the beam (a roll about the beam, free for the dot); the joint before it then has a 309 mm lever. *Assumption:* the shoulder dominates. *What the change alters:* gripping near the dot halves the wrist term and raises the elbow's; the total barely moves. *What it leaves uncertain:* which grip a printed shell can take.

**Round 4 (break): a SCARA and a gantry on the radial line.** *Conflict:* a monitor arm is a SCARA whose swivels carry no gravity torque (borrowed); with motors and encoders it is the bought arm the study lacked. On the radial line both big joints move the dot along the tangent: what is left is the vertical slide (1:1) and the quill's yaw at a 136 mm lever: 20 micrometres radial-plus-vertical and 45 tangent for 0.01 degree and 0.01 mm, against 68 for the six-axis arm at azimuth 0; the base at 90 degrees makes it 58. The gantry aligned with the radial is 14 (0.01 mm per slide), turned 45 degrees 17. The same joint stiffness (8000 N.m/rad, illustrative) leaves the SCARA on the radial line six times stiffer radially than along the tangent (0.0013 against 0.0083 mm per newton, `calc/15 scara-straight`): the soft direction is the free one. *Assumption:* the comparison is fair. It is not: 0.01 degree and 0.01 mm are different physical errors. A cobot joint good to 0.003 degree and a ball screw good to 0.005 mm are the fairer pair. *What it leaves uncertain:* a SCARA cannot tilt the beam; the adaptor sets the tilt by hand.

**Round 5 (break): resolution is not the problem, lost motion is.** *Conflict:* the desk arms on Prime (0.25 to 0.5 kg, 12-bit servos) step 0.088 degree, 0.1 to 0.5 mm at the dot: they cannot make a 0.1 mm trim by themselves and cannot carry the gun. The 19-bit class steps 0.4 to 3 micrometres; what decides it is lost motion, stiffness and drift, which the makers do not state. *Assumption:* the joint's resolution is its accuracy. *What the change alters:* the scene's encoder-bits slider shows the cliff; the compliance slider (8000 N.m/rad, illustrative) turns a 1 N load change along the fibre into 4 to 11 micrometres in the needed directions and 7 to 20 along the tangent, by grip and class. *What it leaves uncertain:* the arm's real stiffness and drift: a spring scale and the indicator Derek owns measure the first in fifteen minutes; the warm-up drift wants an hour.

**Round 6 (repair): coarse arm, fine stack.** *Conflict:* an arm asked to hold 0.03 mm against a load change and to trim to 0.01 mm has two jobs. *Assumption:* the arm must be fine. *What the change alters:* the trim is made under the work (a two-plate X and Z stack) or at the flange (a stage); the arm has to be stable between the last look and the weld and its scatter has to fit the stack's range. After a perfect look the trim leaves 1 to 2 micrometres with a 19-bit arm, 0.10 to 0.13 mm with a 12-bit arm and one micro-step (5 micrometres by default) with a stack. The stack carries the rotator and sees no cable force; the stage sits in the load path (gun weight, umbilical pull), and the Prime XYZ stage found (60 x 60 mm, 3 kgf, 0.03 mm accuracy, sourcing 30) has almost no margin over the gun. A soft support at the tip is the other thing a tip can add: a spring balancer that takes the gun's weight (borrowed-14 brackets the range), or the arm's own float. It reduces what the joints hold and adds compliance: `travel-22` puts a float's residual (joint friction, a mass declaration error, the umbilical's change) at a newton or two and the dot at 0.4 mm on a printed three-ball seat, so a soft support is for carrying between docks, not for the weld. *What it leaves uncertain:* the arm's hold.

**Round 7 (break): the fibre and the base.** *Conflict:* an arm's wrist that turns a full revolution twists the fibre (strictly forbidden, manual p. 20); an elbow near the tube fouls the fibre's 350 mm bend radius; the base footprint (128 mm across for the UR3e) and the pedestal have to fit beside a rotator on a bench; the drawn arm passes the rim and the gun without collision at the default but the scene tests only the tube, the rotator, the bench and the gun's axis. *Assumption:* the fibre follows the arm. *What the change alters:* joint-limit rules for J6 in software; the fibre carried on a balancer (`travel-08`). *What it leaves uncertain:* the routing is not drawn.

## What this changes for the other ideas

- The arm's park replaces travel-01's shuttle and travel-19's drop tier (`travel-21`); it can be the escape and the return seat's carrier (`travel-04`), and it sets the beam tilt and plan angle by software where travel-01's holder set them by hand and locked them.
- It does not replace stiffness at the weld: that is what the datasheets do not say, and it is the measurement to make first.
- The touch routine (`travel-15`) could use the arm as the mover; contact detection by joint current or a flange sensor reads 2 N or worse, which on a 5 N/mm arm is 0.4 mm: the reading error is trigger force over path stiffness (`freedom-12`); the work-comes-to-the-stylus form stays better.

## Real products and their interfaces

`sourcing/travel.md` entries 24 to 34. On Prime: the Dobot Magician family (0.25 to 0.5 kg, +-0.2 mm, $999 to $1,999), the Mirobot ($2,050), the SO-ARM101 kits ($460), the reBot B601-DM ($1,899): none carries the gun. From the makers: the Fairino FR3 ($6,799 on its US store, 3 kg, +-0.02 mm, Python and C++ SDKs, ServoJ and ServoCart at 60 to 1000 Hz, two pulse inputs) and the Universal Robots UR3e (3 kg, +-0.03 mm, RTDE, four quadrature inputs, a wrist force sensor at +-2 N precision, datasheet read). Delta, SCARA and hexapod searches on Prime returned only educational arm kits. No lead time was observed for either 3 kg arm.

## What an arm's repeatability and payload mean at a 61.85 mm circle

Repeatability (ISO 9283) is the radius of the sphere that contains the poses when the arm returns to one taught pose after excursions, unidirectionally, at the tested payload, speed and position: +-0.02 to +-0.03 mm for the two 3 kg arms. The seam wants two of the three directions within about +-0.10 mm (illustrative window), so the projection of that sphere on the radial and vertical is at most the same number: the closure's returns fit, if the tested pose is representative of ours. It is a return figure, not a hold figure: what the arm does under a 1 N change while the tube turns is stiffness, and unmeasured. Payload is quoted at a centre-of-gravity offset (UR3e: 3 kg up to about 150 mm); the gun's centre of gravity is 58 to 187 mm from the flange at the three grips (proxy), inside the rating at 1.5 kg.

## Unresolved problems and questions for Derek

- What does the gun weigh with the shell on, and where is its balance point?
- Which of the three grips can the shell take? Is there room beside the rotator for a base and a pedestal?
- Is a 3 kg arm at $6,799 with an unobserved lead time in the range you would consider building around?
- What does a spring scale on the gun's shell do to the dial indicator on the tube, in newtons per millimetre? (That is the arm-hold figure, in the shop, without an arm: it is the stiffness any support has.)

## Assumptions

- UR3e link lengths and payload chart **[manual]**; joint errors, stiffness (8000 N.m/rad), encoder bits, the SCARA link lengths (225 + 175 mm) and every slider default: **illustrative**. Gun proxy and opening pose: kit; gun mass and centre of gravity **[unknown]**. Seam r = 61.85 mm **[repo]**.

## Scene id

`travel-20-arm-joints-at-the-dot`
