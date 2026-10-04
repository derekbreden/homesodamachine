# Open robot arms and a camera-guided welding positioner

Research checked **2026-10-04**. Build **one permanently bench-mounted,
six-axis gun positioner: XYZ screw slides carrying a screw-driven yaw/pitch/roll
gimbal**. The gun stays on it during calibration, dry rotation and welding.
The existing rotator supplies circumferential travel; the positioner adjusts
the gun throughout that rotation. Budget approximately **$750–$1,300 for the
positioner**, or **$2,000–$2,700 including the two-camera dry-run observation setup**,
before tax and development spares. These are concept materials allowances,
not a completed CAD design or a qualified shopping cart.

The design objective is **observed, correctable local motion**. Software commands
an adjustment, measures what actually happened, and commands another adjustment
until the gun has the required relationship to the seam. Calibration and dry
runs can occupy weeks during development and days for an individual weld. One
completed carbonator per week is acceptable. Materials cost takes priority over
assembly effort, software development time and production speed.

There is no single final pose to reproduce. The desired gun/seam relationship
and the corrections needed to maintain it vary with rotation and heating.
The camera budget covers dry-run observation; live-weld optical protection and
filtering remain to be designed and priced.

## What the mechanism must do

The Rebot and Camera conversations establish the application context. Their
transcripts remain outside this public repository.

| Requirement | Design consequence |
|---|---|
| Observe the aiming dot, actual protruding wire endpoint and seam | Measure the working geometry itself. The wire-guide exit and a computed tool center are insufficient substitutes. The fixed gun/guide assembly moves together. |
| 0.010 mm work-coordinate requirement; 0.005 mm design target | Assess the residual error achieved by the observation-and-correction loop, under the actual load and process conditions. These numbers are not specifications imposed on each motor or on blind return motion. |
| Three gun rotations about a software-defined point at the dot | Provide all six pose coordinates. Combine XYZ and gimbal motion to implement grip-axis, hole-axis and vertical-axis rotations; these do not have to match individual machine axes. |
| Gun positioning during tube rotation | Learn and execute angle-dependent corrections, then keep observing during the weld. Human tube loading does not require an additional robot. |
| Ample autonomous dry-run time | Learn geometry, friction, reversal behavior, settling, temperature effects and each tube's seam before firing. Keep unsuccessful trials in the dataset. |
| Reported gun/feed/four-foot-umbilical measurement: 1.3118 kg | Allow for the gun shell and mount, carried gimbal parts and cable forces. Support the heavy umbilical independently. |
| Existing 48 × 24 inch benches and edge mounting | Use one braced station base for positioner, rotator and measurement references. Preserve tube loading, camera views and fiber routing throughout the intended motion. |
| Completed weld withstands 180 psi for 30 minutes | Positioning is one part of process development. The pressure test remains an acceptance result of the completed vessel. |

The [gun-positioning geometry](../../hardware/assembly/weld-position.md) uses a
253 × 143 × 34 mm X1 proxy and illustrates the requested dot-centered rotations.
Its angular dials are exploratory geometry, not qualified travel requirements.
Equipment context records active/stored fiber bend radii of 350/240 mm and no
twisting. The [rotation rig](../../hardware/assembly/weld-rotation-rig.md)
currently starts development at 8 mm/s, approximately 48.6 seconds per lap.
Preparation can take days; corrections during a live lap must respond to the
disturbances actually observed during that lap.

The [physical-evidence index](../../hardware/mechanical-qualification/README.md)
contains no accepted result for this proposed positioner or optical loop.
This proposal specifies what to engineer and measure, without assigning the
founder an additional measurement task.

## The selection criterion

A nominal 0.5 mm X command need not produce exactly 0.5 mm. If it produces a
visible 0.35 mm displacement, software can learn that response and continue
correcting. If a reversal initially produces no visible motion, software can
learn the take-up behavior. Small, stable positions and sufficient useful
motion are what matter; returning blindly from the other end of an arm's
workspace is outside this welding task.

This is a visual-servo problem: use the discrepancy between observed and
desired features as feedback, with a motion model that can be learned and
updated. Fixed workspace cameras and approximate motion models are established
forms of this approach. [Chaumette and Hutchinson, Visual Servo Control, Part I](https://web.mit.edu/amcp/OldFiles/drg/Chaumette_Part_I.pdf).

Evaluate each candidate against four concrete questions:

1. **Observation:** can the system distinguish relevant changes in dot, wire,
   seam, standoff and orientation? Multiple features and viewing directions
   must remove ambiguities; a stationary surface dot alone does not establish
   unchanged gun pose.
2. **Correction authority:** do commands produce usable signed changes, and
   can the loaded mechanism settle at positions close enough together to
   reduce the error? Test reversals and coupled motion as part of learning.
3. **Tracking:** can observed errors be reduced while the tube rotates? Learn
   repeatable angle-dependent error in advance; measure the remaining live
   disturbance and the observation/move/settle delay together.
4. **Physical support:** does the mechanism carry its gravity/cable loads,
   remain within travel and clearance, and retain the gun through faults?

Backlash, imperfect calibration, elastic deflection and slow thermal drift can
be accommodated when their effects are observable and correctable. Feedback
cannot create an intermediate stable position if stick-slip repeatedly jumps
across it, distinguish a motion hidden from every view, or correct a disturbance
before it is observed. These are application-specific engineering questions.
Catalog return-repeatability figures neither answer them nor exclude a design
from serving as a useful donor.

## Six open arm projects

The shortlist includes released hardware designs with reusable-source licenses,
including an unfinished printed strain-wave arm. Their complete-arm prices and
payloads describe different scopes. Use the sources as component and control
libraries; a donor arm's stock payload does not determine the capacity of our
bench-supported adaptation.

| Project and released hardware | Pros for our application | Cons and work required |
|---|---|---|
| **[reBot B601-RS](https://github.com/Seeed-Projects/reBot-DevArm)** — six axes; part/assembly STEP; CERN-OHL-W-2.0 hardware, Apache-2.0 software | Strongest complete-arm alternative. Accessible joint commands, motion feedback, temperature/fault data and tool kinematics support camera-directed experiments. Rated payload 2.5 kg; 587.5 mm radius without its gripper. | Purchased integrated actuators and custom metal parts spend money on reach we do not need. Continuous cable moments and holding heat need application-specific sizing. Select the command mode carefully for small corrections. |
| **[Thor](https://github.com/AngelLM/Thor)** — six axes; native FreeCAD, STEP/STL; CC-BY-SA-4.0 CAD | Commodity steppers, printable serviceable mechanisms, remote-drive/differential wrist ideas and software-issued joint moves. Project claims hardware below €350; useful construction economy. | Stock 0.75 kg payload is below the reported gun assembly. Reinforce/balance a copied loaded mechanism and replace critical printed bearing surfaces with purchased bearings. Extend its GUI's coarse jog precision. |
| **[BCN3D Moveo](https://github.com/BCN3D/BCN3D-Moveo)** — five axes; SolidWorks/STL; MIT mechanics, bundled GPL Marlin | Straightforward shafts, bearings, belts and paired side plates; ordinary step/direction controls can participate in our camera loop. Good source for inexpensive support and assembly details. | Six motors drive only five axes. A complete copy needs a sixth pose axis and a gun-load redesign. Step-derived coordinates need to be supplemented by our actual camera observations. |
| **[Faze4](https://github.com/Source-Robotics/Faze4-Robotic-arm)** — six axes; STL, cycloidal STEP, assembly/control sources; CERN-OHL-S-2.0 hardware | Most detailed printed-cycloidal donor: paired discs, rolling pin contacts, independent bearings and replaceable printed parts. Exposed joint/step commands are suitable starting points for slow, observed corrections. | Full arm weighs about 14–15 kg; its mechanical BOM has 764 purchased and 197 printed parts. Copying the whole arm adds substantial material and assembly work. Controller needs robust acknowledgements, timestamps and limits. |
| **[OpenArm 2.0](https://github.com/enactic/openarm_hardware)** — seven axes; STEP/BOM/wiring; CERN-OHL-S-2.0 hardware, Apache-2.0 software | Best telemetry and experiment-system donor: torque, position, velocity, stiffness/damping, temperature and faults. Its calibration fixture and camera/lighting layout are useful patterns. | Custom metal links and integrated actuators are an expensive route to local gun adjustment. Its 4.1 kg nominal payload definition is a one-minute full-extension hold, so prolonged holding remains a separate load/thermal question. |
| **[OS-ARM](https://github.com/DDeGonge/OS-ARM)** — six-axis design; Inventor/STEP/STL and controller source; MIT | Best printed strain-wave experiment to borrow. Its approximately 75 mm flat reducer separates the rigid output gear from the flexible element; retain that separation and independently support the output. | Unfinished complete arm. Approximately 1 kg payload, 500 mm reach and under-$500 arm cost are goals. Current demonstration firmware controls five active axes with the sixth fixed; complete six-axis integration remains work. |

### reBot: accessible control is more relevant than its return test

The [Seeed control guide](https://wiki.seeedstudio.com/rebot_arm_b601_rs_mit_control/)
exposes Python joint control. MotorBridge's
[MIT command packing](https://github.com/motorbridge/motorbridge/blob/main/motor_vendors/robstride/src/protocol.rs)
uses a 16-bit position field over ±4π: approximately 0.022° per count, or
153 µm at an illustrative 400 mm lever. Its
[CSP implementation](https://github.com/motorbridge/motorbridge/blob/main/motor_vendors/robstride/src/motor.rs)
writes a float32 position reference instead. CSP is therefore the first command
path to investigate for small jogs; numeric encoding does not establish the
loaded physical response. Verify what the returned position fields measure.

The [manufacturer's ±0.1 mm return test](https://www.seeedstudio.com/blog/2026/09/09/rebot-arm-b601-rs-performance-durability-tests-payload-repeatability-teleoperation-and-gravity-compensation-2/)
is background information. It does not decide whether our camera loop can make
small corrections. The [workspace guide](https://wiki.seeedstudio.com/rebot_arm_b601_rs_pinocchio_meshcat/)
does matter to holding duty: extended operation can trigger J2 stall protection.
Use rated, thermally sustainable actuator torque and a favorable posture when
evaluating a complete reBot. Its cheaper reproduction hardware differs from
the shipping mechanism, so characterize the actual build.

### Thor and Moveo: inexpensive actuation remains usable

[Asgard](https://github.com/AngelLM/Asgard/blob/master/asgard.py) sends decimal
joint coordinates and feed rates. Its
[GUI](https://github.com/AngelLM/Asgard/blob/master/gui.py) rounds to 0.1°;
bypass or extend that interface rather than infer a mechanical limit from it.
Thor's [mechanism notes](https://hackaday.io/project/12989-thor/details)
explain the two-motor/two-degree differential wrist. Seven motors drive its
six arm axes. Its remote-drive construction is useful when carried motor mass
matters.

Moveo's [assembly manual](https://github.com/BCN3D/BCN3D-Moveo/blob/master/USER%20MANUAL/User%20Manual%20BCN3D%20Moveo.pdf)
documents the five-axis mechanism. Its
[firmware](https://github.com/BCN3D/BCN3D-Moveo/blob/master/FIRMWARE/Marlin_BCN3D_Moveo/Marlin_main.cpp)
supports relative `G91` motion and decimal coordinates. Printer-derived control
can issue our experiments; homing and commanded step history remain internal
state, while cameras report the actual gun response. Purchase support bearings
and add metal load paths where our carried gun requires them.

### Faze4 and OS-ARM: retain as reducer options

Faze4's [design decisions](https://faze4-robotic-arm-docs.readthedocs.io/en/latest/B_Design_decisions.html)
describe printed cycloidal reducers on J1–J5 and a purchased planetary on J6.
Borrow the discs, pins and bearing arrangements if a rotary reducer improves
our eventual packaging. Its
[low-level control](https://github.com/Source-Robotics/Faze4-Robotic-arm/blob/master/Software1/Low_Level_Arduino/Arduino_GUI_code.ino)
provides joint command plumbing, not an actual tool-position measurement.
The [root hardware license](https://github.com/Source-Robotics/Faze4-Robotic-arm/blob/master/LICENSE)
is CERN-OHL-S, despite the conflicting README MIT badge.

The [OS-ARM reducer demonstration](https://www.youtube.com/watch?v=Emvo3bLT-Z4)
reports about 10 Nm and under $20 for the gearbox with the motor separate.
That is a creator's component report, not a complete priced actuator or
loaded-jog/lifetime dataset. Its
[firmware](https://github.com/DDeGonge/OS-ARM/blob/main/firmware/firstdraft_fw/firstdraft_fw.ino)
and [kinematics](https://github.com/DDeGonge/OS-ARM/blob/main/firmware/PythonIK.py)
need the sixth controlled axis completed if reused for a complete arm.

### OpenArm: borrow the experiment interface

The [CAN API](https://docs.openarm.dev/api-reference/can/)
exposes position, velocity, torque and stiffness/damping commands with actuator
state. Compliance is a controllable property whose effect our cameras can
observe; it is not a reason to dismiss the design. The
[OpenArm Cell](https://docs.openarm.dev/hardware/openarm-cell/general/)
supplies useful calibration, lighting and logging patterns. The
[ROS control bridge](https://docs.openarm.dev/api-reference/ros2/control/)
remains under development. Its advertised $6,500 complete bimanual-system figure
does not provide a one-arm raw-materials quote.

AR4's [custom license](https://github.com/Annin-Robotics/ar4-hmi/blob/main/LICENSE.txt)
restricts redistribution/commercial derivatives, so it is outside this
reusable-source shortlist. Retain upstream attribution and applicable
source-sharing obligations in actual adaptations; check file-specific software
licenses separately from hardware licenses.

## Build one positioner

Mount three orthogonal guided screw slides on a short braced base beside the
rotator. Their carriage carries three nested, bearing-supported rotary axes
and the permanently clamped gun. The machine has six actuators total. Tube
loading and camera retraction are fixture operations; the same positioner
performs every gun correction during dry runs and welding.

The gimbal's physical center need not coincide with the laser dot. For a tool
offset vector `v`, software uses `translation = (I − R) v` to compensate a
rotation `R` about the dot. Calibrate the actual tool transform and map the
requested grip/hole/vertical rotations into this machine's coordinates.
Place the physical pivot near the working end where clearance allows; a
smaller offset reduces translation consumed by angular experiments.

### A concrete starting geometry

Use **200 mm usable mechanical travel on each XYZ axis** and **±20° on each
gimbal axis** as a provisional CAD envelope. These are design assumptions,
not recovered mandatory ranges or demonstrated collision-free travel. Size
rails longer than usable travel to accommodate two blocks, supports and limits.
The model in [calculations.json](calculations.json) uses an illustrative neutral
tool vector `[200, 0, 0]` mm and samples `Rz Ry Rx` at one-degree spacing.
Holding the dot while sweeping all angles through ±20° consumes approximately
24 mm X and ±69 mm Y/Z relative to neutral. A ±100 mm slide envelope leaves
about 31 mm additional Y/Z adjustment in this geometry; it does not offer
200 mm of dot translation at every angle. The actual gun transform, virtual
axes, sightlines and cable envelope must be included before fixing CAD.

Drive each axis with a 200-full-step NEMA17, a **4:1 belt reduction** and a
**1 mm-lead steel screw**, initially a common M6×1 screw with paired metal nuts
in an adjustable preload carrier. The nominal linear increment is 1.25 µm per
full motor step. On a 120 mm angular lever, it is about 2.15 arcseconds, equivalent
to 2.08 µm at a 200 mm tool offset near neutral. These are command spacings,
not predictions of attained accuracy. A 0.5 mm lead or greater belt ratio is
available if the observed motion demonstrates a useful reason to change it.

For each rotary axis, use a screw actuator with **single-plane clevis pivots
at both ends**. In its local plane, place the base pivot at `A = (r, −L0)` and
the lever pin at `P = (r cos(angle), r sin(angle))`, with `r = L0 = 120 mm`.
The screw assembly pivots as it extends; the nut-side clevis prevents nut
co-rotation through a rigid nut carrier and a genuine one-axis pin parallel
to the gimbal shaft. Spherical ends would require another anti-rotation
constraint. This avoids side-loading a rigidly mounted screw as the lever
arcs. The exact geometry gives
`L² = L0² + 2 L0 r sin(angle) + 2 r² (1 − cos(angle))`.
Across ±20° it needs about 82 mm total length change, or 90–100 mm actuator
travel with margins. Base/lever-side hinges need approximately 6°/26° freedom
relative to their neutral bodies, plus clearance margin. Use metal pins and
preloaded bearing/contact arrangements in printed carriers. Prototype friction
and reversal behavior; the arithmetic does not establish their loaded motion.

Use two metal guides/four blocks per XYZ axis and independently supported
gimbal output bearings. Screw fixed ends carry thrust and radial load; the long
linear screws have opposite-end radial support that permits thermal expansion.
The angular motor/belt/bearing cartridge pivots with its screw. Sweep and guard
the complete screw, including the overhang beyond its nut at minimum actuator
length. The packaged prototype determines whether extra radial guidance is
useful; any added sleeve must follow the pivoting assembly without binding.
Print carriers, motor mounts, large pulleys, housings, guards, assembly locators and the gun
shell. Buy screws, paired nuts, bearings, small pinions and shafts. Short cut
metal plates/backbones and through-bolts carry the bending and preload paths.
This keeps fabrication inexpensive without requiring every rubbing or heavily
preloaded surface to be printed.

### Load and drive sizing

The gun/feed/umbilical figure is reported as **1.3118 kg**. A **0.250 kg**
shell/mount allowance gives **1.5618 kg**; the allowance is unmeasured. The
illustrative gimbal calculation adds **2.0 kg** of carried motors/structure,
both at an assumed 100 mm worst gravity lever, plus an assumed **3 Nm cable
moment**. It produces a **6.49 Nm** moment and about **54 N** angular-screw
force at neutral, rising to approximately **60 N** at the sampled range's
least favorable lever geometry, before nut preload and friction.
These assumptions need the actual CAD mass/CG and cable
routing; the 3 Nm value is not a measurement or certified disturbance bound.

A separate **8 kg** moving-stack assumption produces about 79 N vertical load.
Screen screw drives at **200 N normal axial force**, allowing for guide friction
and preload. With assumed 20% screw and 90% belt efficiency, nominal motor
torque is approximately **0.0442 Nm**. This is a reduction calculation; motor
holding torque is not a continuous running/thermal rating. Size rails, bearings,
mounts and screws for moments, buckling and wear as well as axial force.
Counterbalance gravity axes and provide retention whose capacity does not
depend on assuming the threads are self-locking.

The screw reduction can generate damaging force during a jam. Current limiting
alone does not establish a calibrated force limit. Include adjustable overload
protection and bounded motion in the prototype, then measure its behavior.
Reducing carried cable force and holding heat makes the camera loop's job
easier and preserves equipment through long experiments.

Six TMC2209 drivers provide step/direction motion and UART diagnostics. Use a
regulated 24 V supply, characterized current and fixed driver settings during
response measurements. Six readable drivers require two addressed UART buses
or a multiplexer; four addresses on one bus are insufficient. Board thermal
capability remains distinct from the chip rating. Driver diagnostics and step
history help explain motion; cameras measure its actual result.
[TMC2209 manufacturer datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/TMC2209_datasheet_rev1.09.pdf).

### Why screws first, and where harmonic drives fit

Screws already turn inexpensive motors into small nominal translations and
rotations. They make each axis's response comparatively straightforward to
learn, and their useful range can be enlarged with longer guides or levers.
The first build spends its budget on guide support, preloaded contacts and
observable output rather than six elaborate reducers.

If testing identifies a range, packaging or loaded-motion problem that a
reducer solves, adapt **OS-ARM's strain-wave geometry** or **Faze4's paired
cycloidal discs** for the affected rotary axis. Buy structural output bearings
independently of the printed transmission. Test commanded movement and settled
response with the gun load; use replaceable printed flexible elements/discs
and log wear over repeated cycles. Nominal tooth reduction or a zero-backlash
description alone does not establish that response.

A six-strut hexapod is also a valid single gun positioner. It offers compact
parallel support, but actuator travel, articulated ends and coupled geometry
must cover the intended dot-centered angular experiments. Choose XYZ plus a
gimbal first because axis-by-axis prototyping and friction diagnosis are
simpler. A hexapod is an architecture alternative for the same job.

## Observation and autonomous learning

Use the Camera session's **two FoMaKo K20UH 4K cameras with Raynox DCR-250
attachments**, plus the existing overview camera. The
[FoMaKo manual](https://www.fomako.net/uploads/20250529/ce40713967c8ae0e137cabdd8a72ff1d.pdf)
documents numeric zoom/focus commands and inquiries, and exposure/iris/gain
control. Fix autofocus, tracking and exposure behavior during measurements;
record optical settings with frames. Native-resolution acquisition matters:
its 4K USB configuration differs from lower-resolution NDI output.

[Raynox's optical guidance](https://raynox.co.jp/english/video/pdf/Panasonic_SDR_S200_S150.pdf)
gives about 109 mm working distance for DCR-250 at infinity focus; DCR-150
offers about 210 mm. The earlier optical estimate gives roughly 2 µm/pixel
for the 4K/DCR-250 combination at maximum useful magnification. That is a
sampling estimate, not measured localization uncertainty. Mount lens and
camera together on a rigid carriage with stable lighting and a recoverable
datum after retraction. Keep camera supports separate from the umbilical boom.

Observe dot and wire relative to the seam from complementary directions.
Include rigid gun references so standoff and orientation remain distinguishable.
Use known local geometry or an independent displacement check when translating
image errors into claimed physical units. A controller cannot validate itself
by calling every improved image estimate a successful physical move. Initial
dry learning can start without buying a separate reference instrument. The
existing 12.7 µm-increment indicator is useful for coarse checks; it cannot
establish 5 µm displacement accuracy. A reference/calibration fixture has a
separate budget allowance, with its actual uncertainty to be established.

The development sequence is software-driven:

1. **Learn the loaded local response.** With the real gun, liner and umbilical
   attached, issue bounded positive/negative jogs on each axis. Record commands,
   frame times, observed feature changes, settling, driver state and temperature.
   Learn a local command-to-feature Jacobian plus direction/history effects.
   Use conservative trust regions; enlarge motion only after observing it.
2. **Close the correction loop.** Compare observations to the desired gun/seam
   relationship, solve a bounded correction, move and observe again. Update
   the response map where needed. Take up a reversal with monitored small
   commands; avoid accumulating an uncontrolled correction while the mechanism
   is stationary. Treat coupling and unresponsive coordinates as identification
   problems, not as exact nominal kinematics.
3. **Learn each rotating tube.** Register its seam, run repeated dry laps, and
   learn a smooth angle-indexed pose trajectory. Validate on further laps
   without fitting those observations into the same training pass. Keep
   cameras checking and correcting throughout; learning may take days per part.
4. **Develop live observation and weld tracking.** Dry runs establish geometry
   and mechanical response. Separately engineer optical protection, illumination,
   exposure/filtering and visibility under emission, wire feed and shielding.
   Measure feature uncertainty and correction delay under those conditions;
   do not infer live visibility from dry images. Use the dry trajectory as
   feedforward, with measured live corrections for heat-induced changes.
5. **Iterate the process.** Log the actual achieved geometry, rotator phase,
   power/feed settings and weld outcomes. Repeat coupon/process development,
   refine the model and evaluate the completed vessel's pressure acceptance.

For example, software can test a 0.5 mm move, observe 0.35 mm, improve its
model and continue toward the target. That response is illustrative, not an
observed result of this unbuilt mechanism. At small scales the same principle
applies, provided actual motion and remaining error are distinguishable. When
loaded stick-slip leaves gaps larger than the useful correction interval,
change preload, nut/guide contact, lubrication, reduction or the affected
actuator and repeat the experiment. Improving mechanics responds to observed
limits; catalog return repeatability is not a prerequisite for starting.

The host software/AI can plan experiments, fit models, inspect failures and
improve the controller over weeks or months. A local deterministic controller
executes bounded coordinated motion and handles limits, watchdogs and process
state; an LLM conversation is not the timing loop. Live tracking bandwidth is
chosen from measured disturbances and frame/motion delay, rather than a factory
throughput target. Thermal changes and unknown wire/cable behavior remain
subjects for observation and iteration.

## Materials estimate and development deliverables

[materials.json](materials.json) contains every cost row; running
`python3 future/robot-arm-study/calculate.py` reproduces
[calculations.json](calculations.json). Only rows marked **Prime price observed**
are verified price anchors. Other values are engineering/fabrication allowances,
including supports and electrical interfaces. They are not selected precision
components or proposed purchases.

| Scope | Calculated materials allowance, USD |
|---|---:|
| Complete single six-axis positioner, including six motors/drivers, base, retention and overload development | $749.98–$1,284.98 |
| Two cameras/lenses, rigid mounts, lighting/connections and cable support | $1,200–$1,350 |
| Positioner plus dry-run observation setup | $1,958.98–$2,633.98 |
| Separate independent measurement/reference fixture allowance | $250–$500 |
| Combined scope including that reference allowance | $2,208.98–$3,133.98 |

The six motors cost **$69.99** using a
[five-motor Prime pack](https://www.amazon.com/dp/B00QEYADRQ) and
[one matching Prime motor](https://www.amazon.com/dp/B00PNEQKC0).
The [six-driver Prime pack](https://www.amazon.com/dp/B08WZFK9KT) is **$29.99**.
Two [Prime cameras](https://www.amazon.com/dp/B0DK1BXJWY) at $449 and two
[Prime lenses](https://www.amazon.com/dp/B000A1SZ2Y) at $75.50 total **$1,049**.
Prices/Prime status were observed on the review date. Nothing has been ordered.
Tax, development replacements, labor, computer, welding equipment, existing
rotator and formal calibration service are excluded. Optional shaft encoders
are costed separately; they are useful fault diagnostics, not substitutes for
camera-observed output.

Proceed by producing the single-positioner CAD, six-channel motion/observation
interface and one loaded screw/clevis prototype before fabricating every
axis. The first prototype addresses a specific decision: whether this cheap
drive's observed, settled, reversible motion is useful for the feedback loop.
Its results set the remaining axis details. Assemble the complete positioner,
automate calibration and repeated dry rotations, then develop live observation
and weld corrections. Long software iteration and low production volume are
part of this plan. Success is the gun's observed relationship to the moving
seam and the accepted weld outcome.
