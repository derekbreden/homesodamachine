# borrowed-02-gimbal-on-gantry: orientation from one product, position from another

Origin: swarm. Maturity: worked deeply. Scene: `scenes/borrowed-02-gimbal-on-gantry/index.html`. Numbers: `calc/gimbal_geometry.py`.

## Picture it

A hobby or handheld three-axis gimbal, the kind that steadies a camera, holds the gun by a printed cradle with ballast so the gun balances about one point in the air in front of the grip. The gimbal hangs from a printer-style gantry over the tube. Turn the gun and the dot would swing off the seam; the gantry slides the whole gimbal the opposite way so the dot stays put. Software sends a G-code move to the gantry and an angle to the gimbal and reads both back.

## The proposal

Give up rotating about the dot, which the axis map shows is awkward, and rotate about a convenient point C instead. Choose C on the line from the dot to the cable exit (the roll axis of the reference dials) at distance t from the dot. Then for any yaw v, hole h and roll r the dot is at `C - t * g(v, h)`, where g is the world direction of the roll axis. Roll never moves the dot (the dot is on the roll axis). Yaw and hole move it by about t per radian, and the gantry cancels that by moving C to `J + t * g(v, h)`, J being the seam point. Orientation comes from a stabiliser gimbal (three brushless motors with angle read-back); position comes from a gantry whose language is G-code.

## What carries the loads, what establishes position, what is free, restrained, driven

- Load path: gun and ballast, printed cradle (two lugs on the pitch axis, a ring at the grip base), pitch motors, yaw motor, Z carriage, Y carriage on the beam, X carriages on two rails, four posts, bench.
- Position: dot = C - t*g from the angles read back and the gantry position, corrected by a camera. Not measured directly by anything in the arrangement.
- Driven: yaw, pitch, roll; gantry X, Y, Z. In the scene the gantry has no slider: it follows the angles through the formula above; a toggle turns compensation off to show the swing.
- Restrained: yaw and pitch by the yoke and the tube (contact tests hold the last valid pose); gantry by the travel envelope (illustrative x +-230, y -260 to 120, z 170 to 380 mm).

## Software: command, observe, manual

- Could command: G1 X Y Z F moves; the gimbal controller's serial angle command; rotator speed (existing). The scene prints the G-code line.
- Could observe: gimbal angles (encoder or IMU), gantry position (steps or scales), the dot through a camera when visible, and the travel each orientation span costs.
- Stays manual or unresolved: balancing the gun on the gimbal (ballast); homing the gantry so the dot is on the seam at a reference pose; laying the umbilical; the gun's mass and centre of mass.

## What was tried to break it

1. **Balance.** Conflict: a gimbal motor is not sized to hold a 250 mm cantilever; handhelds are balanced so the motors carry only the residual. Assumption: the gun balances on the gimbal. Change: put C on the roll line and bring the centre of mass to C with ballast. Uncertain: the gun's mass and centre of mass are unknown; a mass m offset e from C needs m x 9.81 x e (1.2 kg, 30 mm: 0.35 N m; 2.0 kg, 60 mm: 1.18 N m; illustrative masses, calc/gimbal_geometry.py).
2. **Power loss.** Conflict: a direct-drive gimbal holds only while powered. With any imbalance the gun swings to the hole-axis stop when power drops, and the dot end moves about 185 mm at the default imbalance. Assumption: the motors stay powered. Change: a worm-geared head (self-locking, backlash, slower) is drawn as the second drive type. Uncertain: the direct-drive version needs a brake or a stop that is safe for the tube; not designed.
3. **Precision.** Conflict: the dot is t from the pivot, so an angle error d costs t*d at the seam: 0.05 degrees at 200 mm is 0.17 mm; 0.3 degrees is 1.05 mm [derived]. Assumption: the gimbal reports what it did. Change: the errors are sliders (angle, gantry position); the readout shows the dot moving mostly along the seam for angle errors, which matters less than radial or vertical error. Uncertain: no product's real angle accuracy was checked.
4. **Gantry travel.** Conflict: the compensating gantry needs, for yaw and hole swept +-30 degrees, 193 x 122 x 173 mm at t = 200 mm and 116 x 73 x 104 mm at t = 120 [derived, calc/gimbal_geometry.py; the scene readout gives the same numbers]. The desktop CNC found on Prime (Genmitsu 3018-PROVer V2) has a 40 mm Z travel. Assumption: a stock hobby CNC is a gantry for this. Change: a smaller t (C nearer the dot) cuts travel and leverage but the cradle must reach into the gun. Left standing: the donor for the frame does not exist as a product; printer parts (rails, steppers, controller) are the donors, the frame is built.
5. **Roll and the fibre.** Conflict: the roll motor of a stock gimbal sits on the roll axis, where the cable leaves. Change: the drawn version uses a ring at the grip base so the cable passes through the bore. Uncertain: twist under roll (manual p. 20 forbids twisting [manual]); a 2-axis gimbal with roll set once by hand is the fallback.
6. **Without compensation.** With the gantry parked the dot moves 3.0 mm per degree of yaw and 3.5 mm per degree of hole at t = 200 (derived, small-angle); the scene measures 2.9 mm radial per degree of yaw and 3.0 mm vertical per degree of hole at the opening pose, and about 3 degrees of hole runs the gun into the tube (LIMIT). Change: none needed; it is the reason for the gantry.

## Branches and combinations

- Same scene: drive type radio (direct-drive gimbal vs worm-geared head), power toggle, CoG offset, t slider, error sliders.
- Not drawn: a two-axis gimbal with a manual roll clamp; C off the roll line (the formula generalises to `C + R(dot_local - C_local)`).
- Combines with borrowed-05-guide-star (nudge the gantry and gimbal, watch the dot, learn the matrix), borrowed-06-swing-offset (the gun's own fine axis on top), borrowed-03-encoded-arm (record the angle spans that must be served).
- Contrast with borrowed-01-ring-pivots (rotate about the dot itself).

## Unresolved problems and questions that need Derek

- Whether any stock gimbal can carry the gun and cradle and hold 0.05 degrees; whether one can hold a pose unpowered.
- The gun's mass and balance point (weigh it; balance it on a finger at the housing).
- Gantry stiffness under a 1 to 2 kg hanging load; a stop that protects the tube.
- Questions for Derek: how much orientation range he uses (yaw, hole) when welding by hand; whether the cable can tolerate the roll.

## Assumptions

- Gun proxy and the three-dial rotation model [repo scene, illustrative]; C on the roll line; yoke, motor and gantry sizes, ballast and boom position illustrative.
- Angle and gantry error sliders, CoG slider, camera bias (0.3 / -0.2 mm) are made up.
- The compensation formula and travel numbers are derived from the dial model; the Python port reproduces the scene's exit direction (-0.224, -0.837, 0.500) and its 193 / 122 / 173 mm readout.
- DJI RS 4 Pro payload 4.5 kg: listing and search snippets, not checked against DJI's specification page. DJI RS SDK page lists supported models and the features "set gimbal position", "control gimbal rotation", "get motor and attitude information".

## Sourcing pointers

sourcing/borrowed.md: DJI RS 4 Pro ($869, Prime, 532 ratings) and the DJI RS SDK page; hollow-shaft gimbal motor kit with AS5600 and a SimpleFOC driver ($34.88); Genmitsu 3018-PROVer V2 ($269, 40 mm Z) and GRBL probe (G38.2) references; USB-to-RS232 adapter ($12.99, 2K+ bought) for the gun's serial port.

## Scene

`borrowed-02-gimbal-on-gantry`

## Wave 2

- **A stock gimbal that holds its pose unpowered** (trials' question): the class is the worm-geared telescope mount. A Sky-Watcher AZ-GTi (two rotations, 5 kg rating, Wi-Fi, encoders that follow a hand slew, $525, two-day) is on Prime; whether a worm holds a cantilevered gun with the motors off, and the backlash, are not on the listing (`borrowed-17-positioner-shelf`). The gun would be balanced on it as here.
- The pivot is still not the dot: a hexapod (`borrowed-13`) puts the centre of rotation on the dot in software at the price of six actuators.
