# B — Wire-located suspension: the load path is the locator

**Picture it.**
- **The cradle.** The gun, in its shell, hangs in a cradle of six thin
  stainless wires running to anchors on a braced frame over the rotator.
- **The dot.** Three wires leave a collar near the nozzle, 57 mm above the dot,
  along lines that all pass through the dot, so they pin the dot like a ball
  joint.
- **The angles.** Three more wires, at the grip butt and the housing back, set
  the angles. In the practical layout, one wire alone sets hole tilt and one
  alone sets roll. The third holds the plan angle, which is instead set by
  sliding the dot along the tangent.
- **Preload.** Two bungees (or constant-force balancers) pull down to keep
  every wire taut.
- **Carry and locate.** The wires both carry and locate.
- **"Fixed."** The anchor frame, which must be tied to the rotator.
- **Lift-off.** Lift the gun and all the wires go slack; set it down and the
  same lengths return the pose.
- **Cable.** The umbilical runs to its own saddle.

**Sketch:** `../sketches/B-wire-located-suspension.svg` (true opening pose, the
all-taut layout).

**Major unresolved problems:**
- The anchor frame's stiffness.
- Wires crowd the cable exit and the camera's sightline.
- Bungee preloads drift as the robot moves: use balancers or a seventh wire.
- Every pose needs a tension check.
- None of it has been built or measured.

Branch of A-r3 (`suspension-original.md`), taken to its end. Sketch:
`../sketches/B-wire-located-suspension.svg`. Numbers: `../calc/wire_rcm.py`,
`../calc/wire_tensions.py`, `../calc/wire_layout_search.py`.

## The physical idea

Wires are soft sideways but very stiff along their length. Give the shell
enough wires, pulling from enough directions, and keep every one of them taut
with a soft preload; the wires then fix the gun in all six DOF, and the same
wires carry its weight. Derek's bungees stay in the picture with a new job:
they no longer try to hold position; they supply a nearly constant pull that
keeps stiff wires taut.

Three of the six wires are arranged so that **their lines meet at the laser
dot**. Their attachments are on a collar around the nozzle end of the shell,
~70 mm from the dot; the lines run on from there to anchors ~400 mm away. The
segment from the dot to the collar is virtual — no wire enters the tube. Any
small rotation about the dot leaves those three lengths unchanged to first
order, so the three wires act like a **ball joint at the dot**: they fix the
dot's XYZ and leave all three of Derek's rotations (grip axis, hole axis,
vertical axis — all through the dot) to the other three wires.

| Wires | Attach | Set |
|---|---|---|
| W1, W2, W3 | collar near the nozzle; lines through the dot, 120° apart, 55° up | dot X, Y, Z (their three lengths, a skewed trilateration) |
| W4, W5 | at the grip butt | the grip butt's position on its sphere about the dot = hole-axis and vertical-axis rotations |
| W6 | housing back top, ~129 mm off the grip axis | roll about the grip axis (W1–W5 already fix the grip-axis line) |
| bungee 1 | grip butt, pulling nearly straight down (~38 N) | preload only |
| bungee 2 | a shell arm reaching over the rim at +X, straight down (~36 N) | preload only |

## Numbers

- **First-order decoupling holds for small moves.** Turning the gun about the
  dot with the three concurrent wires at fixed length moves the dot
  0.02–0.05 mm at 2°, 0.13–0.33 mm at 5°, 0.5–1.3 mm at 10° (collar 70 mm from
  the dot; roughly a·θ²/2; the vertical-axis turn drifts least). A real pivot 56 mm up the barrel (a hanging loop on the
  graduated tube) moves the dot ~2 mm for 2°. **[Calc, wire_rcm.py]**
- **Stiffness at the dot** from the three concurrent wires alone (1 mm 7x7
  stainless, 400 mm free length): ~64 / 64 / 262 N/mm; 2 mm polyester rope
  would give ~8 / 8 / 33 N/mm. Longer wires are softer (800 mm halves it).
  The anchor frame is in series. **[Calc]**
- **All six wires together** (the all-taut layout, rigid frame assumed): 5 N
  sideways at the dot moves it 0.03 mm (1/16 in rope) to 0.08 mm (1 mm rope);
  5 N vertically 0.008–0.02 mm; a 5 N trigger push 0.03–0.08 mm; a 3 N
  tangential drag from a stuck wire 0.02–0.05 mm. The welding wire's
  stick-out yields at ~3–5 N, so a stuck wire bends before the gun moves
  appreciably. **[Calc, wire_stiffness.py]**
- **Every wire taut?** The first layout I drew failed: with gravity plus one
  downward bungee, W4 and W6 would have had to push. A search over orientation-
  wire directions and preload sites found layouts where all six stay taut with
  ≥ 6.8 N to spare, under gravity, the preload, a 5 N push at the dot in each of
  ±X/±Y/±Z, and a 5 N trigger push — using two preloads (~38 N nearly straight
  down from the grip butt, ~36 N from a shell arm over the rim). One preload
  alone left a wire 4.5 N short of taut in the worst case. The preloads must
  pull along lines that miss the rotating tube. Wire tensions then run 12–24 N;
  1/16 in stainless rope is sold at ~1.6 kN breaking. **[Calc,
  wire_layout_search.py; gun 1 kg, CoM assumed]**

## How it is used

- **Adjust.** Turnbuckles give coarse length (M4: 1.4 mm per turn). Fine
  adjustment is an anchor on a screw slide along its wire's direction: 0.01 mm
  of anchor travel moves the dot ≤ 0.01 mm along that wire. Dot moves by
  W1–W3; aim moves by W4–W6, with the dot staying put to first order. That
  matches the order Derek works in: dot, then angles, then touch up the dot.
- **Automate.** Six anchor slides with steppers make a six-wire parallel robot
  with its remote centre at the dot (a Hangprinter-like cable machine turned
  into a positioner). The kinematic decoupling keeps the software simple: three
  actuators for the dot, three for the angles.
- **Lift-off and tube change.** Wires only pull. Unhook bungee 2 and lift the
  gun: every wire goes slack, and the gun can be hung on a parking hook while
  the tube is changed. Lower it, rehook the bungee, and the wires come taut at
  the same lengths: the gun returns to the same pose with nothing re-set. The
  lengths are the memory. The same property makes it a breakaway: a bump or a
  stuck wire past the preload lifts the gun off its taut state rather than
  bending anything, and it returns when released.
- **Second closure** (inverted, 2.01 kg): nothing above the rim changes.
- **Second person**: the setting lives in six lengths; "hook it in, hook the
  bungees, check the dot" is the procedure.

## What "fixed" is fixed to

The anchors. They are now the reference for the dot, so they must sit on a
stiff, triangulated frame tied to the same structure as the rotator — not on
the pegboard or the ceiling. A tetrahedral cage over the rotator (extrusion or
steel tube) with its feet on the plate or bench that carries the rotator. The
wires are stiffer than a 500 mm cantilevered extrusion post (~10 N/mm), so an
untriangulated frame would throw away what the wires provide.

## Breaking it

- **Clutter.** Six wires and two bungees around the gun: the umbilical leaves
  the grip butt exactly where W4/W5 attach, the wire conduit runs beside it,
  and cameras need sightlines to the dot. The sketch's directions avoid the
  umbilical's exit sector; real anchors need a clearance check at each pose.
- **Large pose changes** alter wire directions: beyond ~5° re-trim the dot.
  Beyond ~15° some wires may approach slack or cross the gun; the layout is
  per-neighbourhood, not global.
- **Creep.** Stainless rope at 10–35 N: negligible. Polyester, polypropylene
  and Dyneema creep over hours — carriers only.
- **Thermal.** Steel wire 470 mm long, 5 K warmer: ~0.04 mm. The frame's
  expansion matters as much.
- **Hooks and seats.** Repeatable return needs each wire to end in a hook that
  seats in the same printed V-notch on the shell every time; a hook that can
  ride around a round eye moves its effective length.
- **Trigger.** A 5 N finger push keeps every wire taut (the search included
  it) and moves the dot ~0.03–0.08 mm with a rigid frame; a shell-mounted
  presser removes it entirely.
- **The umbilical's residual pull** after its saddle goes into the wires; they
  are stiff enough, but it changes tensions — check the layout with measured
  cable forces.

## Parts

- 1/16 in 7x7 stainless rope with crimp sleeves (Prime, "800+ bought").
- M4 stainless hook-and-eye turnbuckles (Prime, "200+ bought").
- 3/16 in shock cord (Prime) for the two preloads.
- Screw/micrometer anchor slides (printed carriages on lead screws or
  micrometer heads — other explorers are sourcing micrometer heads).
- Frame: extrusion or steel tube, triangulated.
- Printed: shell with a nozzle collar carrying three wire seats on lines
  through the dot, seats at the grip butt and housing, a preload arm.

## Contribution and open problems

- It is the suspension idea in which the load path itself establishes
  position, with a virtual pivot exactly where Derek's three axes meet.
- Lift-off/return is free because wires cannot push.
- Open: frame stiffness and layout around the real cable route; whether the
  collar near the nozzle can take three wire seats without shading the camera
  or crowding the wire guide; per-pose tension checks with the real gun mass,
  CoM and cable forces.

## Pose note: the same layout search at hole dial 65

The numbers above are at the scene's opening pose with the 35° hole-dial
offset. At hole dial 65 (a steeper orientation, what the first version of this
file computed) a layout also exists: all six taut with ≥ 10 N to spare, using
~24 N from the grip butt and ~35 N from a shell arm; one preload alone came
within 0.6 N; a 5 N trigger push moved the dot 0.015–0.04 mm. At both poses the
same conclusions hold: two preloads are needed, the preload lines must miss the
tube, and the concurrent-wire drift is second order (a·θ²/2).

## Wave 3: run as a cable robot, and one wire per angle

### From machine-that-learns' evaluation (exchange file, `wire_robot_workspace.py`)

**Turning about the vertical axis slackens the layout** (−3.9 N at −10°).

- **Repair (theirs; I agree):** never rotate about the vertical axis. Plan
  angle is a tangent translation (the joint is a circle). Done that way, ±15°
  keeps every wire taut with ≥ 1.3 N.
- **The cable robot's natural neighbourhood:**
  - dot ±5 mm;
  - roll ±10° on W6 alone;
  - hole −10° to +5°;
  - plan angle ±15° as translation.

  Beyond that, move the anchors to a new layout per recipe.

**The three concurrent attachments are spokes 19–67 mm off the barrel axis,
57 mm above the dot.** W1 passes within 27 mm of the joint camera's sightline,
and the spokes need a metal shield against spatter and reflected 1080 nm light.
**Repair:** add the camera's line of sight as a keep-out in the layout search
(rotate the triad), or put the camera in the triad's gap.

**Bungee preloads drift as the robot moves.** At 0.1 N/mm, 40 mm of travel is
~4 N against 1–7 N margins. **Repair, either:**

- constant-force spring balancers as the preloads (QWORK class, already
  sourced);
- a seventh motorised wire, so wire tension becomes a commanded quantity read
  back by motor current or a load cell.

**The camera calibrates the 36 anchor and attachment coordinates** by moving
each slide and watching the dot and shell fiducials. The concurrency drift
(1.2 mm at 10°) becomes a model term.

**Slide travel needed:** W1–W3 ±10 mm, W4/W5 ±45 mm, W6 ±20 mm. SFU1605 stages
give 1.6 µm of wire length per microstep. Their conclusion — develop the six
wires rather than their hexapod as the "all freedoms actuated" option — rests
on the wires having no play and the actuators sitting ~400 mm from the weld. I
agree.

### One wire per angle (one-knob-one-parameter's question)

Can each angle wire set exactly one of Derek's angles?
**[Calc, wire_diagonal.py]**

- **Strictly, no.** At a single attachment point every rotation about the dot
  produces a velocity in the same 2-D plane (perpendicular to the radius). A
  wire blind to two rotations there is blind to all three.
- **Practically, yes, once plan angle is a translation.**
  - **W5** is made blind to hole tilt and only holds the vertical rotation at
    zero.
  - **W4** alone sets hole tilt: 4.74 mm per degree. An M4 turnbuckle
    (1.4 mm/turn) gives 0.3° per turn.
  - **W6** is made blind to hole tilt, so it alone sets roll: 1.05 mm per
    degree, 1.3° per turn.
  - Roll never moves the grip butt, so W4 and W5 are blind to it automatically.
  - W1–W3 set the dot. Angle changes do not move the dot; dot changes do shift
    the angle wires slightly, so the order is dot first, then angles.
- **A taut layout exists:**
  - W4 at the grip butt, azimuth 92°, elevation 56°;
  - W5 at the grip butt, azimuth −19°, elevation 11°;
  - W6 at the housing back, azimuth −163°, elevation 24°;
  - two preloads (~47 N nearly straight down from the grip butt, ~56 N from a
    shell arm);
  - worst-case tension 12.9 N under the wave-1 disturbance set.

So the suspension can be a machine whose knobs are turnbuckles, one per
welding angle. Unchecked for this layout: clearances around the umbilical and
the camera, and the anchor frame.
