# Six-axis gun positioner

Build one permanent bench fixture: three guided XYZ screw slides carrying a
three-axis yaw/pitch/roll gimbal and an adjustable metal gun cradle. The
existing weld rotator turns the tube. The positioner keeps the gun attached
through calibration and local corrections, including corrections throughout
rotation. Camera observations determine attained working geometry.

The fabrication package includes a metal station frame, supported rails,
metal thrust seats and gimbal load paths, printed transmission/locating parts,
three passive screw-shaft drag brakes, a separate six-axis dry controller,
and two retractable camera stages. Long calibration and software iteration
are part of the intended use; the production objective is one accepted
carbonator per week.

## Start here

| Deliverable | Use |
|---|---|
| [Prime purchase lists](purchases.md) | Required pack quantities, prices and links; owned equipment and staged buying |
| [Illustrated assembly guide](../gun-positioner-guide/README.md) | Letter shop booklet, fabrication templates, assembly and commissioning gates |
| [Mechanism fabrication assets](../printed-parts/fixtures/gun-positioner/README.md) | STEP, STL, DXF, stock nest, print instructions and geometric checks |
| [Camera-stage assets](../printed-parts/fixtures/gun-positioner-observation/README.md) | Two manual stages, removable lens modules and metal height adjustment |
| [Control and wiring](control.md) | Power, stop circuit, pin map, driver UART and connector checks |
| [Firmware and host tools](../../firmware/src_gun_positioner/README.md) | Bound UF2 images, upload instructions, console and native simulations |
| [Observation workflow](observation.md) | Native frames, optical-setting receipts, controller records and offline response fitting |
| [Commissioning](commissioning.md) | The measurements that determine usable motion, retention and local correction performance |
| [Independent review](review.md) | Engineering findings and their closure evidence |

The fabrication manifest governs mechanical dimensions and quantities. The
wiring manifest and firmware asset manifest govern electrical connections and
software settings. The guide consumes those sources. The
[robot-arm study](../../future/robot-arm-study/README.md) supplies application
requirements and research context; it does not override this fabrication set.

## Working envelope and load paths

The screw lead is **2 mm per revolution**, with a 20-tooth motor pinion and
80-tooth screw pulley. A 200-step motor therefore commands **2.5 µm of nominal
screw travel per full step**. At fixed 16 microsteps, scaling is **6,400 issued
pulses/mm**. These are command spacings; friction, elastic motion and optical
uncertainty determine the usable physical correction interval.

XYZ soft travel is ±85 mm about its established datum. The generated
axis bounds govern gimbal experiments about each clevis neutral position.
Angular levers are 150 mm and
neutral pivot distance is 180 mm. Clevis geometry, screw extensions and soft
counts are generated from the same model. These bounds describe mechanism
travel, not a collision-free rectangular tool workspace. Qualify each
intended path with the real gun, wire guide, umbilical and vessel.

The initial seam-work candidate is yaw ±5°, pitch ±10° and roll ±5°, with
XYZ coordinated to keep the calibrated working endpoint at the seam and
local endpoint offsets within ±0.25 mm. The geometry receipt records the
proxy clearance screen. Acceptance requires a static sweep with the actual
gun and supported cable before powered motion. The independent travel box
is for tube-absent commissioning; actuator bounds alone provide no vessel
collision protection.

Supported metal rails and four blocks carry each linear axis. Aluminum plates,
through-bolts, output shafts and purchased bearings carry the gun and gimbal.
Two-sided metal thrust stacks carry screw axial load. Printed parts locate
components, transmit belt torque, guard drives and pad the adjustable gun
cradle; no printed part serves as the screw thrust seat or brake friction
surface. Independently support the umbilical on the station boom, preserving
the welder's fiber bend limits and avoiding torsion.

Plain output shafts use two split-clamp bolts per metal hub. Shaft-end bolts
and metal spacing stacks retain both shafts and hubs axially. Every hub
requires the supported, measured torque proof in commissioning before loaded
use; bolt grade and a geometric check do not establish clamp capacity.

Spring-loaded steel friction washers on the Z, pitch and roll screw shafts
retain their loads independently of the belts. Drag acceptance bands are
0.20–0.23 N·m for Z, 0.06–0.08 N·m for pitch and 0.02–0.04 N·m for roll.
Measure around a complete turn with the balanced lever and weighed masses;
grade each spring before installation. The free washer contacts a clean,
dry brass flange and can tilt to follow its face. The fixed-end nuts are
threadlocked, fully cured and witness-marked. At the 300 N Z screening load
and 2 mm lead, ideal backdrive torque is 0.0955 N·m. Actual worst-pose power-off
retention and loaded motion remain physical acceptance checks.

Each drive has a captured metal force link. Opposed spring pairs preload
metal seats, holding the normal load without spring displacement. An overload
lifts a seat and opens that axis's stop loop before reaching the capture.
The Z link uses a 400 N seated preload in the downward load direction and
250 N in the opposite direction. Pitch uses 130 N seats in both directions,
with a 100 N working-force screening envelope. Set and measure both directions
of every link; current settings do not establish a force limit. Metal travel stops and the gun tether supplement
retention. Recheck drag, release force and clearance after any adjustment.

The gun cradle has a transverse magnetic kinematic seat and a captured
bidirectional axial crash stage. Set release against the real gun's gravity
and cable baseline, using weighed masses and the calibrated cord redirect.
The acceptance band is 20–30 N of added nozzle force in each tested direction.
Each of two independent stop channels contains an axial contact and a plate
presence contact, so a displaced or missing seat interrupts motor power and
reports the stop. Short steel tethers retain the released cradle before its
motion consumes fiber slack. Re-seat and observe the working geometry again
after every release.

## Build and development sequence

1. Fabricate the station and one complete linear screw drive. Use the guide's
   fit coupons and thrust-stack checks before duplicating printed components.
2. Assemble the full mechanism, brake system, umbilical support and tether.
   Establish physical central datums with the tube removed.
3. Wire and test the controller with motor power removed, then one unloaded
   axis. Demonstrate stop, limit, power and lost-host behavior before loading.
4. Fit the real gun and umbilical. Measure brake drag, loaded power-off
   behavior, temperatures and signed response at low speed. Keep the tube
   absent until retention and clearance have been established.
5. Add the two camera stages, park and lock optical settings, acquire verified
   native frames, and calibrate observations. Fit the observed local response
   in comparable direction/history neighborhoods, preserving failed trials.
6. Test bounded candidate corrections and independent held-out dry laps with
   the existing rotator. Measure the actual tube phase; rotator pulse history
   is insufficient evidence of attained angle.
7. Develop live welding only after its observation, containment and welder
   interface have separately passed their gates. The supplied controller has
   no laser, wire-feed or rotator output.

## What is ready and what is measured

The deliverable is a fabrication and dry-development package. Its assets,
nominal geometry, firmware compilation, native policy tests, observation
tests and illustrated document can be checked without operating the machine.
The fixture is unbuilt; there is no accepted loaded-motion or optical-accuracy
result. The **0.010 mm work-coordinate requirement and 0.005 mm design target**
apply to the observed, correctable complete loop. They are not guaranteed by
microstep size, a camera pixel count or a coarse indicator.

For numerical accuracy claims, calibrate physical image scale and uncertainty
with an independent reference appropriate to the claimed error, then evaluate
held-out trials. The owned 12.7 µm-increment indicator is useful for coarse
scale/creep screens. It cannot establish 5 µm performance. Local observations
can support model learning before that accuracy qualification is complete.

Live observation has an additional process gate. The dry camera stages have
no qualified protective/filtering stack. The current process concept uses
radial and axial contact followers on a common reference, with observed tube
angle and a cool baseline; it still needs a proven sensor/interface and
process acceptance. Two probes do not determine the full heated shape.
Preserve dry trajectory learning and measure live residual error rather than
assuming a dry image remains usable during emission.

Record physical evidence beside the fixture and index accepted results in
[mechanical qualification](../mechanical-qualification/README.md). Keep the
scope of every result: a valid solid, a bench firmware test and a loaded
positioning test answer different questions.
