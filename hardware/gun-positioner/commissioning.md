# Dry-development commissioning

Commission this one permanently mounted positioner with the gun, wire-guide
assembly and supported umbilical. Its job is small observable corrections during
rotator motion. There is no park/return-repeatability acceptance criterion.
The [assembly guide](../gun-positioner-guide/README.md), [control wiring](control.md)
and [mechanical geometry](../printed-parts/fixtures/gun-positioner/geometry-check.json)
define the build. No physical positioner test has been completed by this package.

The phases below answer decisions needed for the build. Record results and keep
failed trials. They are procedures for the assembled development rig, not a
request to reconstruct an observation already in the evidence register.
Keep the tube absent throughout loaded-drive and geometry checks. Install it
only after the intended path and fault/catch clearances have an accepted record.
The existing 12.7 µm-increment indicator is a useful coarse assembly check;
it cannot establish 5 µm physical accuracy. The existing meter supplies
continuity, polarity and voltage checks. Temperature and brake-torque work use
the named contact/force tools in the purchase plan or an equivalent already
available tool; neither tool's resolution alone is its measurement uncertainty.

## 1. Cold electrical checks

**Decision:** whether the selected module/carrier/power harness can be energized
without connecting 24 V to logic or shorting a motor winding.

Keep the brick unplugged, MOTOR POWER OFF, all mechanical supports/catches
engaged, no tube under the gun, and belts disconnected for isolated motor tests.
The laser source remains disabled and has no control cable to this controller.
Firmware status checks below use the bench image. Flash it with 24 V unplugged
using the BOOTSEL procedure in the firmware README before those checks.

1. Fit the fixed [controller mounts](mounting/README.md) with their stated
   hardware allocation, 28 spacers and two fan guards. Transfer the received
   board/terminal/fan footprints; verify unstrained wires, clear solder pins
   and meter access. Photograph the received module label and both R110 resistors. Make a socket
   map by named VM/GND/VIO/ENN/STEP/DIR/MS1/MS2/PDN_UART pins. Meter each carrier's
   mapped power rails before inserting modules. A conflicting pin map stops
   assembly at that carrier; repair the map/wiring before power.
2. Verify each motor has exactly two isolated continuity pairs. Record four-pole
   plug positions and colors. All ground returns must reach the 0 V star; VM
   must not show continuity to VIO, VSYS, VBUS or a STEP/DIR input.
3. With each switch released, its axis NC loop must have continuity. Actuate
   each low/high travel switch and each of the two opposed overload switches
   individually; each must open that loop. Unplug the axis connector;
   it must also open. Check 24 switches and seven unplugged-loop cases.
4. STOP NC1 and NC2 must be electrically separate. Both close on released STOP
   and open on latched STOP. MOTOR POWER OFF must open the relay-coil path.
   BREAKAWAY CH1 and CH2 are separate circuits in those same two independent
   chains. Each has an axial COM–NC contact and plate-presence COM–NO contact
   in series; the seated plate presses the presence switch. Verify each of the
   four contacts individually: axial release or missing plate must open its
   channel. Releasing the seated gun mount must open both, remove VM and open
   GP26. Its uninstalled terminals stay open.
   CH1 must be the GX16-4 pair, with only pins 1/2 used in the 24 V coil chain;
   CH2 must be GX12-2, with pins 1/2 in the 3.3 V sense loop. Verify their
   complete contact-to-pin maps and confirm the two connector families cannot
   mate. Never use the same GX12-2 type for both voltage classes.
5. Check main/branch fuses, capacitor polarity and both diodes. Relay flyback
   band goes to coil plus; the external Pico-power Schottky band goes to VSYS.
6. Connect USB only. Meter 3V3 at the logic rail, with driver VIO matching that
   voltage; ENN must be HIGH. Firmware must report no reference and no motion.
7. Power the brick with MOTOR POWER OFF. Check regulated output near 24 V and
   buck output near 5 V before connecting its diode lead. Check VSYS remains
   within the Pico's allowed supply range, 3V3 remains stable and relay NO has
   no switched VM. With USB unplugged, the buck must keep Pico 3V3 alive.
8. Connect USB, release STOP and turn MOTOR POWER ON. Switched VM must match
   the brick output; GP27 must be approximately VM/11, safely below 3.3 V.
   Press STOP: switched VM must collapse and the Pico must remain powered.
   Reset STOP with MOTOR POWER OFF; power restoration must produce no motion.
   Before reference or coupling, qualify startup with the selected fuses:
   keep USB connected and perform 30 brick cold starts and 30 MOTOR POWER cycles, waiting for switched
   VM below 1 V between cycles. Record actual fuse type/rating and every failed
   start, blown fuse, brick hiccup or Pico reset/boot-token change. USB keeps the
   Pico powered through these cycles, so no reset is expected. Removal of both
   power paths is a separate expected-boot test. All must start normally with
   no fuse openings or overheated holder/connection. Added VM capacitance is
   1,070 µF; the V1.3 schematic adds two nominal 10 µF VM capacitors per module,
   giving 1,190 µF / about 0.343 J at 24 V before fan/buck input capacitance.
   This functional inrush gate uses the existing meter and temperature tool;
   it does not measure millisecond peaks or overshoot. Failure changes fuse
   time-current selection or adds engineered inrush limiting; do not silently
   raise fuse ratings. Repeat the gate after supply/buck/capacitor/fuse changes.
9. With motor plugs disconnected, VM restored and firmware disabled, set each
   received module's VREF trimmer to its measured minimum using its identified
   supplier test point. Record voltage against module GND. This checks reset
   fallback; working current is digital. Hold Pico RUN low and, separately,
   enter BOOTSEL: meter shared ENN with all six drivers seated. It must remain
   above the driver's specified HIGH threshold, 0.7 × measured VIO. A carrier
   pull-down that defeats this is a wiring failure, not a permitted orientation.
10. Unplug the brick and USB before disconnecting both TX and RX leads from
    each UART node. Keep all three module UART pins and its 1.8 kΩ pull-up
    connected. Restore USB/logic power only, with motors unplugged; meter each
    undriven bus. It must exceed 0.7 × measured VIO. Power off before reconnecting
    the MCU leads. The design calculation includes three 20 kΩ module pull-downs,
    chip pulls and leakage. This checks static idle voltage; successful repeated
    six-driver CRC/readback checks below qualify the working bus, not its waveform.

Acceptance is correct mapped nodes, proper polarity, independent stop contacts,
working relay cutoff and persistent logic supply. Unexpected voltage, an
unmapped carrier pin or a failed loop is a failed electrical result. A supply
meter reading does not qualify transient suppression.

## 2. Firmware and isolated motor checks

**Decision:** whether the six channels have unique UART identities, fixed settings,
correct windings and predictable issued motion.

Flash the **bench** UF2 with 24 V unplugged and supports engaged, using Pico
BOOTSEL/RPI-RP2 as described in the [firmware README](../../firmware/src_gun_positioner/README.md).
Open the explicitly selected USB port through the host console. Uploading a
file does not qualify wiring or start a motion session.

With belts still disconnected and motors secured to their mounts:

```text
clear
status
reference central
arm
jog X 0.0400 1000
jog X -0.0400 1000
```

The disconnected-belt test uses a temporary motor-shaft reference, explicitly
recorded as an electrical test; it does not establish machine coordinates.
0.0400 mm is 256 external microsteps, or 16 full motor steps / 28.8° nominal
motor rotation. A paper mark/pointer can show the sign and the large reversal.
Run each named motor separately, then use a six-axis signed request. Verify
that the requested connector moves and no other channel responds.
Status must show `profile="bench"`, six `current_scales=10`, six
`configured_vsense=1` and matching decoded `vsense=1`, six decoded
`microsteps=16`, `counts_per_mm=6400`,
`max_rate=2000` and six healthy drivers. Record the reported counts and
completion sequence/time. Disconnect one UART bus with motion disabled; `clear`
must refuse a healthy ready state. Restore it with 24 V unplugged.

With belts disconnected, establish the temporary reference but do not arm.
Turn MOTOR POWER OFF and ON while keeping the Pico powered. Status must show
no reference, disabled drivers and a changed `vm_epoch`; `arm` must refuse.
Restoring power alone must never enable a motor. Use `clear`, re-establish the
temporary shaft datum and reference it before proceeding. After `arm`, the
six `drivers` rows must have fresh diagnostic sample times from the arming
check. `timer_ticks` must continue advancing while idle and armed. The computer
regression covers a stopped timer refusing watchdog feeds; that result does
not establish physical watchdog latency or stopping distance.

This test accepts channel/sign/winding response only. It says nothing about
loaded screw displacement, step loss, camera uncertainty or holding capacity.
After the test, stop, unplug 24 V and restore the physical central datums before
coupling belts. Correct a physical direction by reversing one identified coil
pair with all power removed, or by rebuilding the observed DIR inversion.
Record that choice in the harness map.

## 3. Passive retention and load support

**Decision:** whether a fault can release the carried gun or pinch/collide with the
fixture. Complete the mechanical package's retention procedure before applying
power to a loaded, unsupported gravity axis.

### Shaft hubs and axial keepers

Use the mechanical package's `hub-clamp-proof` fixture and its
[`requirements.json`](../printed-parts/fixtures/gun-positioner/requirements.json)
seat table. Every hub is the **ungripped specimen on its own final marked shaft
seat**. A proof on another shaft surface does not qualify that contact.

1. Ream and deburr each hub's 12 mm bore and its two M4 clamp stations
   (Y=16 mm, Z=6/19 mm). Shaft bodies have no transverse holes. Clean cutting
   fluid from the bore and shaft; leave their contact dry. The eight centered
   M5×0.8 end holes have a 4.2 mm pilot 16 mm deep and at least 10 mm of usable
   thread. Verify the actual M5×12 keeper engagement: nominal 12−2−0.8=9.2 mm
   through the 2 mm stainless OD20/ID6 washer and 0.8 mm M5 flat washer.
   Require at least 8 mm engagement and at least 0.8 mm bottom margin.
   Finish the metal spacer stacks against hubs and bearing **inner**
   races; they must clear outer races, seals and housings and allow at most
   0.5 mm one-sided axial freedom. Bearing setscrews alone do not accept axial
   capture.
2. Fit both grade 12.9 M4×50 clamp bolts, their washers and locking nuts. Use
   the purchased LEXIVON cam-over screwdriver and metric H3 bit; record its
   serial-numbered calibration certificate. Tighten clockwise at the bolt
   head while holding the nut with the existing adjustable wrench. Alternate
   the bolts through 10, 20 and **25 in-lb** settings. The final setting is
   2.8246 N·m; the stated +4% clockwise bound is 2.9376 N·m, below the hard
   **3.0 N·m** ceiling. Verify that the received certificate permits that upper
   bound. Nylon-insert running torque is included; do not add it to the
   setting. Proof failure rejects the grip at this ceiling.
3. Lay the existing 500 mm 4040 test column horizontally and secure it to the
   bench. Borrow one KP001 and one `pitch-bearing-foot`; two 10 mm metal
   `proof-bearing-riser` spacers and M6×40 bolts attach the bearing to its
   foot. The assembled shaft axis is 75.35 mm above the bench.
   The foot mounts to
   the column at its centerline Y=±20 mm with two M8×16 screws, washers and
   slot8 T-nuts from the corner-kit spares. Mount the vise through its factory
   slots using the temporary bench anchors shown in the fixture. Bolt a
   companion reaction hub to a borrowed `angular-lever` plate with four
   M5×45 bolts. **Grip only that plate in the vise**, clear of both hubs and
   bare shaft. In the canonical terminal setup, specimen=0…25 mm,
   companion=26…51, reaction plate=51…57.35 and KP001 center=66.35
   (body=58.35…74.35). This fits the completed 85 mm shaft. For each other
   seat use its source table's reflected or shifted placement.
4. Attach the balanced 300×30×6.35 mm `hub-proof-lever` to the specimen with
   four M5×45 bolts. It occupies −6.35…0 in the canonical setup. Keep the
   **1 mm visible gap between hub faces**. Remove service end keepers and
   axial spacers from this temporary horizontal setup, or hold them visibly
   clear: neither an end face nor arm→washer→endbolt may bypass the specimen
   clamp. Place independent catches/trays close to the shaft and lever;
   they must remain clear during measurement. Fit `hub-proof-load-saddle`
   using two borrowed 25.4 mm metal angles, two M5×20 bridge ties and one
   M5×25 through the 140 mm load hole. Mount the gauge to its 70×110 metal
   backing through the four 7 mm `proof-gauge-rear-spacer` tubes and eight
   large M4 washers. Finish its separate four M4×25 rear screws to the actual
   socket depth, with at least 4 mm engagement unless the manufacturer
   requires more, and no bottoming. The shorter four screws used by the
   normal gauge backings remain a separate set. Fit `proof-gauge-quill-cap`
   with two M5×25 bolts; verify its fasteners clear the gauge case. Align the
   compression gauge under the manual drill quill with the drill unplugged.
   The quill contacts only the formed metal cap, centered on the gauge axis;
   the probe contacts only the saddle. The
   saddle places the gauge force at the proof lever's **axial midplane**;
   side contact or a displaced force plane is not this fixture.
5. Record shaft/hub index marks, fastener witnesses and baseline indicator
   readings at the same supported shaft stations and lever pointer. Advance
   the quill slowly, record the force bracket and hold for 10 seconds without
   impact. Use the opposite load hole/reaction side for the other torque sign.
   The complete measured torque interval must fit this table:

   | Ungripped specimen | Accepted torque interval | Nominal indicated force at 140 mm |
   |---|---:|---:|
   | Pitch drive-lever hub; negative-side pitch output hub | 30–32.5 N·m | 224 N |
   | Yaw output/drive-lever, positive-side pitch output, roll output/drive-lever | 25.2–27.5 N·m | 188 N |

   Calculate from actual force-line radius and tangency, including gauge,
   fixture, radius, alignment, onset/hold and load-step uncertainty. For
   example, radius 140±0.5 mm, total force uncertainty ±5 N and tangency
   within 3° give 30.509…32.175 N·m at 224 N and 25.494…27.117 N·m at
   188 N, using lower=(F−U)×r_min×cos(3°), upper=(F+U)×r_max. These are
   examples; the instrument's accuracy alone does not include all those
   allowances. Reject the setup/result if extra uncertainty crosses either
   band edge. The 500 N gauge capacity is not a reason to exceed the upper
   torque bound.
6. Unload fully after each sign. Any hub slip, moved witness, catch contact,
   fixture movement, crack, residual twist or runout/pointer change beyond
   the repeatability/uncertainty of the same before/after measurement fails.
   The existing indicator's 0.013 mm resolution is a coarse no-set screen,
   not acceptance of 10 µm physical positioning. Replace a shaft showing
   permanent change; diagnose or refabricate a failed hub. Do not raise clamp
   torque or current to obtain a pass. Test all seven hubs in the specimen
   role; a hub that has only served as the reaction is not qualified.
7. Restore the metal capture stacks, keepers and qualified clamp setting.
   After the accepted loaded dry subset completes **50 supervised reversals**
   and the thermal procedure reaches its settled readings, support and
   deenergize the mechanism. Repeat both signed proofs on the same marked
   seats at the recorded warm service temperature, within the 50°C upper-bound
   thermal gate. Restore all service hardware and witness marks, inspect
   axial freedom/free rotation, and establish fresh physical datums. A changed
   hub, shaft seat, clamp hardware/setting or higher temperature envelope
   requires qualification again. These repetitions screen assembly settling;
   they do not establish fatigue life.
   Record the specimen temperature during the repeat. If dismantling and
   cooling prevent a proof at the intended warm condition, that temperature
   range remains unqualified.

Qualify the separate positive axial path with the mechanical package's
`shaft-capture-proof` fixture. Use the actual completed shaft, output/lever
plates, bearings, inner-race spacer stacks and eight measured-depth end
keepers. Clamp grip is not the acceptance path for this test.

1. Unplug motor power, independently support the gun and carried assembly,
   and transfer the bare axis to the retained metal fixture. Orient the
   source table's selected nearest shaft end upward. Secure the existing
   500 mm test column and bearing feet at the fixture's stated positions;
   reaction passes through the actual bearing housings. The canonical 85 mm
   shaft has its selected end at Z=200 mm, axis Y=−78.175 mm, bearing center
   u=65 mm and two 12.825 mm `capture-bearing-riser` tubes; use M6×40 bearing
   joints and the spare M8×16/slot8 foot joints. Other axes retain their actual
   service bearing separations. Join `capture-catch-upper` to the borrowed
   `drive-test-foot` with two 7.85 mm `capture-catch-spacer` tubes and two
   borrowed M5×35 joints. The bench-anchored vise grips only their joined far
   metal. Set the two independent catch gaps to nominal 0.75 mm, clear of the
   keeper and shaft; they must remain clear during measurement. Loosen
   hub clamps and bearing setscrews enough to remove their axial friction
   grip. Keep both actual end keepers and the complete metal capture stacks
   installed. Verify free movement within the recorded capture gap before
   applying force; a stuck bore or support contacting a hub fails this setup.
2. Fit `shaft-capture-interface` to the selected hub face with the four
   temporarily borrowed M5×80 joints, retaining its actual service plate.
   If that plate occupies the selected face, place the interface outside it.
   Its central Ø22 opening clears the full OD20 keeper, flat washer and
   socket-head bolt. The separate four M3 ties lie on a 60×40 mm pattern,
   outside the 26×20 mm hub mounting pattern. Fit four 75 mm metal 8 OD/6 ID
   `capture-bridge-spacer` tubes and `shaft-capture-bridge`, using the four
   borrowed M3×100 ties.
   The two 6.35 mm plates, spacers, washers and nuts have a nominal 92.7 mm
   stack; verify actual grip and at least two full protruding threads. Leave
   0.2 mm locating slack so ties do not preload the capture. In the worst
   roll seat, the bridge inner face is u=−30.35 mm and clears the complete
   keeper/head envelope by at least 22.55 mm before captured movement.
   Verify visible clearance throughout the actual travel, including tie
   tails, gauge fittings and both shaft ends.
3. Mount the 500 N gauge on `installed-Z-gauge-back`, using its dedicated
   proof rear-screw set, four 7 mm spacers and eight large M4 washers. Guide
   the backing with two 9.825 mm `capture-gauge-guide-spacer` tubes and M6×25
   slot8 joints. Keep its slots freely sliding under the guide washers.
   Connect the bridge's captured steel **M6×16** bolt and one 1 mm washer
   to the received gauge load shaft with the purchased steel
   **M6×1 coupling nut, approximately 20 mm long**. Verify the received
   gauge thread by hand before fitting it; it must match M6×1 without force.
   Measure and mark at least **6 mm engagement at each end**, with no
   bottoming and no contact between the two thread ends. Verify that the
   bridge head/washer, coupling and gauge case clear the keeper throughout
   captured movement. A cord or hook is not this positive threaded path.
   The bridge end has nominal 8.65 mm engagement; a reference 7 mm at the
   gauge end leaves 4.35 mm between thread ends. Record actual engagement,
   zero, span/check, force sign and total uncertainty. Keep this same
   threaded connection installed for **both force signs**. For compression,
   unplug the press and set its quill near mid-stroke. Set the metal cap
   under the chuck with at least **10 mm usable downward travel**. The
   CAD cap height is measured above the test-column base, not a
   drill-press capacity or a same-bench fitting result. Secure the column
   below the press work-surface datum as needed, using the matched 4040
   brackets/kit joints on the fixture support. Positively anchor and check
   the actual bench/press mounting, column and catch before either signed
   500 N path. Do not use loose blocks or a column held only by hand.
   Withdraw the manual jack; with the drill unplugged, advance the quill
   against only `proof-gauge-quill-cap` to move the gauge body toward the
   bridge. No force may enter the shaft-end screw directly.
4. For tension, withdraw the quill. The existing `installed-Z-jack-angle`
   and fully threaded M6×80 manual feed
   moves the freely guided gauge body upward, away from the bridge. Guide
   washers retain the backing laterally without clamping its slots. Hold
   the lower jack nut with the 10 mm wrench, loosen the upper lock nut,
   advance at most 1/12 turn (0.0833 mm), and relock before every reading.
   The gauge case, cap, backing and jack must not contact a hub, shaft,
   keeper or catch and bypass the gauge/capture path.
5. Increase force slowly in each direction and hold for 10 seconds without
   impact. Accept only the complete measured axial force interval within
   **450–500 N**. For example, 475 N with total uncertainty ±5 N gives
   470–480 N; include fixture alignment, gravity/baseline, load-step and
   hold variation in the actual uncertainty. This example does not add
   instrument capacity. Reject if either interval edge misses the band,
   displacement exceeds 1 mm, a catch/support takes force, a fitting slips,
   or a washer, thread, plate, spacer or bearing deforms or releases.
6. Unload completely and compare the same baseline shaft, plate, axial-gap
   and runout observations. Any resolved residual change fails. Repeat both
   signed directions for every actual hub capture path in the source seat
   table, and repeat after the warm/cycled check described above. Restore
   all service joints, both M4 clamp settings, bearing setscrews, keepers,
   witness marks and free rotation; observe a fresh physical datum before
   motion. The result accepts that assembled positive path at its recorded
   load and temperature. It does not establish bearing life or fatigue life.

The shaft screen uses the circular-section relations in MIT's
[torsion](https://ocw.mit.edu/courses/1-050-solid-mechanics-fall-2004/8c30fdf15d9d50c02f4215903c847d7f_emech8_04.pdf)
and [bending](https://ocw.mit.edu/courses/1-050-solid-mechanics-fall-2004/8f0200f4ca3236383a2ef048c7ec4c40_emech9_04.pdf)
texts. The free span's full-torque section is solid; centered end bores remain
inside terminal hub regions. Conservatively treating a whole section as a
5 mm hole removes 3.014% of its polar moment. At 32.5 N·m, 140 mm radius and
a conservative 32.35 mm local bending arm, that section has nominal bending
45.64 MPa, shear 98.76 MPa and combined von Mises 177.05 MPa. An assumed
uniform transverse compression of 50 MPa raises that model to 195.99 MPa.
The 205 MPa room-temperature yield used for sizing is consistent with
[Alleima's specified 304 bar](https://www.alleima.com/contentassets/657c112531644dbcaf41e6d03f4193e8/datasheet-sanmac-304304l-en-v2025-05-09-0637-version-1.pdf/download);
its certificate does not apply to the purchased 12 mm stock. Actual material,
blind-tip/thread stress, clamp-contact pressure and installed bearing/load
distribution are not established by those assumed numbers. The vise/bearing
fixture adds constraints, so a simply-supported two-bearing reaction calculation
cannot certify this proof. Actual no-slip/no-set results and the separate
installed-load/overload gates determine the accepted scope.

### Retention and installed load

Install the independent cable boom, gun tether/catch, rigid temporary Z support,
and the Z/pitch/roll spring-loaded metal friction washers. The permanent drag is downstream
of the belt, so its retention does not depend on motor holding current or an
intact belt. Measured full-turn breakaway windows are **Z 0.20–0.23 N·m,
pitch 0.06–0.08 N·m, roll 0.02–0.04 N·m**. For a 2 mm lead, ideal
backdrive torque is F × 0.002 / (2π): the mechanical sizing screen's 300 N Z
load gives 0.0955 N·m. A 100 N pitch actuator load gives 0.0318 N·m.
At those screening loads, the measured retention lower bounds must therefore be
at least **0.1910 N·m Z and 0.0637 N·m pitch**, while their complete torque
intervals still fit the specified bands. Pitch's target is 0.070 N·m;
a result near its 0.060 N·m band edge cannot hold the full 100 N screen at twice
ideal backdrive torque. This arithmetic screens a design;
installed load, brake friction variation, washer wear, contact creep and support
geometry still determine retained capacity. Include every carried component,
fastener, wire, the real gun and the actual cable configuration in the load bound.

Use the mechanical force-arm fixture/procedure and its stated force-tool
uncertainty to record breakaway and running drag, both directions, throughout
each brass-flange turn. The complete torque interval must fit its band at all
eight measured shaft phases and both signs. Apply the characterized tangential
redirect loss, weighed cup/cord uncertainty, onset bracket and radius/alignment
allowance. For Z, an observed 0.205–0.225 N·m guard window applies only if total
uncertainty is at most 0.005 N·m; narrow the window when the actual uncertainty
is larger.

Bound the actual installed load before comparing it with retention:

1. Qualify the owned 2 kg/0.1 g scale using the mechanical package's zero/span
   procedure and purchased reference masses. Before assembly, weigh and label
   every carried piece, fastener group, motor, wire, gun and carried cable span.
   Keep each scale weighing below 2 kg. For a heavier component, use the
   500 N gauge's compression button on its metal backing/platen in the drill
   vise, with a centered rigid metal load surface and an independent catch;
   prevent any side load or external support from bypassing the reading.
   Sum weight upper bounds, including each measurement's uncertainty. The
   quoted CAD mass and an added percentage do not replace these readings.
2. Use the supplied `installed-z-load-bound` metal fixture: brace its 500 mm
   4040 test column to the station with the two matched corner brackets, mount
   `installed-Z-gauge-back` with its two M6×25 slot8 guide bolts and 10 mm metal
   spacers, and attach the force gauge with the four verified-depth rear M4
   screws. Its 60×40 metal platen supports the retained hollow Z-head foot;
   gauge/platen must contact only the moving head. Fit its 50.8×50.8×6.35 metal
   jack angle 60 mm below the backing's lower edge using two M6×16 slot8 bolts.
   Its fully threaded M6×80 screw pushes only the backing's metal lower edge;
   the 12×6.5 mm vertical slots retain and guide the backing. Set guide-bolt
   clearance so it slides freely while the washers retain it. Keep an independent catch
   within 1 mm. Take the load before detaching the Z actuator output. At each
   accepted Z/gimbal/cable configuration, record the supported rest reading
   and controlled upward/downward onset readings. Hold the lower jack nut with
   a 10 mm wrench, loosen the upper lock nut, advance or withdraw at most
   **1/12 turn (0.0833 mm)** and relock after each step. Observe the independent
   indicator/cameras and stop before the catch is touched. Do not loosen the
   column braces or lift the head by hand to produce a gauge reading.
   Use the larger absolute
   onset plus instrument, alignment and fixture uncertainty as the conservative
   installed force bound; it includes rail drag and vertical cable pull.
   Use the larger of that bound and the separately summed carried weight.
   The upper bound must be **≤300 N**. A resting reading alone can hide rail
   stiction. This fixture is removed before powered travel.
3. For pitch/roll, keep the real carried gun and cable attached to their output
   hubs. Park on independent supports; let the gauge or characterized cord
   take the angular rotor load before opening its actuator clevis. Fit the
   balanced 100 mm metal `angular-load-lever` at the separate **actuator drive-lever hub's**
   26×20 mm four-M5 pattern, reusing its M5×45 bolts; preserve the output-hub
   attachment, both proof-qualified M4 clamp bolts and the tapped-end metal
   axial-capture stack. Clear normal
   supports from the measurement path while keeping the catch immediately
   nearby. On the existing 70×110 gauge backing/PONY vise, align the gauge
   tangentially at the measured ±100 mm load holes. Reverse its reaction side
   for the other sign. Use characterized redirected weighed cups for low roll
   forces. Observe signed onset in both directions, with no unrestrained move
   or catch contact. The larger absolute threshold plus its complete
   uncertainty gives a conservative output-moment bound, including bearing
   resistance and cable free couple. The disconnected clevis excludes screw,
   washer, motor and belt drag. Do not subtract the two thresholds or assume
   direction-symmetric friction. Divide the moment upper bound by the lower
   measured `dL/dθ` over the accepted path to obtain actuator force. The
   nominal 133.60 mm/rad lower lever may be used only after actual pin/radius
   dimensions pass the geometry screen. Pitch's force upper bound must be
   ≤100 N; roll's accepted force follows its measured retention capacity.

For each gravity axis require **retention lower bound ≥2 × force upper bound
×0.002/(2π)**. Restore actuator, drive-lever/hub hardware, clamp preload,
guarded belt and witness marks, and establish fresh observed datums after these
measurements. Record the pose and cable configuration with every force/torque
result; a route or payload change invalidates that load qualification.
If that inequality fails, improve retention/counterbalance before loaded motion;
raising motor current cannot repair passive holding capacity.

Qualify each captured metal spring force-link in both directions using its
mechanical procedure and the named force tool. Record spring/preload, shuttle
travel, each switch's opening point and the measured peak force including tool
uncertainty. Static acceptance windows are **X/Y and upward Z 250–350 N;
downward Z 440–500 N; V pitch 148–165 N; U yaw/W roll 100–140 N**.
Pitch uses a 130 N seated preload in both directions and a 100 N normal
actuator-force sizing screen. Z's downward/+screw-length
direction uses a nominal 400 N seat; its qualified lower seat-force bound,
including uncertainty, must be **at least 390 N** (1.3×300 N). Upward/−length
Z uses a 250 N seat. Positive controller Z moves upward and shortens the screw.
The nominal electrical trip displacement is ±0.75 mm XYZ and ±0.30 mm angular,
with independent metal capture at ±1.0 mm; source spring dimensions/preload and physical trips
must agree before loaded motion. Each opposed NC switch belongs in series
with the axis's two NC travel switches. Its opening must inhibit every axis
and invalidate reference. No automatic retry or powered escape is available.
Support and deenergize the mechanism, inspect the cause, manually recenter the
link, then establish fresh physical datums. A force-link switch is not a
measurement of motor force, and a spring's catalog rating is not an accepted
trip force.

After each unpowered trip curve passes, repeat with the accepted loaded profile
and its slow bounded move against the force fixture, with tube absent and the
secondary support/catch engaged. Powered peak force, **including uncertainty,
must not exceed 350 N X/Y/upward Z, 500 N downward Z, 165 N pitch or
140 N yaw/roll**. This is an upper ceiling; the
powered test has no minimum force requirement. Low-current axes may stall before
reaching the force-link preload. Independently observe and record that stall,
issue STOP and abort without retries; do not raise current merely to reach a
switch trip. A stall does not demonstrate overload-switch operation.

If the overload switch does open during that test, its opening must precede
metal capture, all axes must inhibit, and there must be no capture impact,
runaway load or automatic retry. Independently prove the powered inhibition and
latch by controlled actuation of each switch or opening of each axis loop, even
where the motor cannot produce its trip force. Record force peak, switch-opening
position if reached, maximum shuttle displacement, independently observed
motion/stall and controller fault/issued-count log. Repeat in both directions at
each subsequently used rate and relevant load configuration. A manual force
curve alone does not establish the powered peak. A failed ceiling or capture
test changes spring grading, preload, switch position or speed; a stall requires
diagnosing the observed drive/load path. Supports and a fresh actual datum are
required before another trial.

With a secondary support positioned immediately under the load and no tube,
record the loaded central pose, extreme intended operating poses and cable
configuration. Remove motor power and, separately, belt drive support. The
mechanism must not run away; the retained gun/cable must stay inside the accepted
clearance and catch envelope. Repeat after the initial dry cycling to detect
loosened pads/preload. Any measurable movement invalidates the count reference
and becomes a camera-observed fault outcome. No 5 µm power-off pose-retention
claim is required, but the load must remain supported and recoverable without
damage or a collision.

## 4. Loaded current, switch and watchdog checks

**Decision:** whether the fixed-current drive can overcome supported load and
constant brake drag without unobserved motion loss or sustained overheating.

Load the named **loaded-development** image, with 24 V unplugged and supports
engaged. After restoring power and physically establishing X/Y/Z central datum
and U/V/W neutral pin length **180 mm**, use:

```text
clear
reference central
arm
status
jog X 0.0025 1000
jog X -0.0025 1000
```

Status must report `profile="loaded-development"`,
`current_scales=[10,10,22,10,14,10]`, `configured_vsense=[1,1,0,1,1,1]`,
matching decoded `vsense`, six decoded `microsteps=16`,
`counts_per_mm=6400` and `max_rate=1000`. R110 estimates are
Z 1.271 A RMS using VFS=325 mV, pitch V 0.459 A and other axes 0.337 A
using VFS=180 mV. At 300 N Z forward
force / 0.23 N·m drag, and 100 N pitch force / 0.08 N·m drag, 20% screw
efficiency with 4:1 / 90% belt efficiency screens about 0.197 and 0.066 N·m
motor torque respectively.
The selected STEPPERONLINE 17HS19-2004S1 is rated 0.59 N·m holding at 2 A/phase.
A simple current proportion gives about 0.375 N·m on Z and 0.135 N·m on pitch;
these are screening estimates only, approximately 1.9× and 2.0× the above
assumed requirements. The
manufacturer holding specification does not demonstrate this reduced-current
loaded drive. Actual low-speed response
and thermal acceptance decide use. The nominal Z peak is 1.797 A; a +5%
internal-reference/assumed −5% sense-resistor screen gives 1.970 A, as detailed
in [the current configuration](control.md). R110 markings and digital readback
do not calibrate actual current. [Motor manufacturer data](https://www.omc-stepperonline.com/nema-17-bipolar-59ncm-84oz-in-2a-42x48mm-4-wires-w-1m-cable-connector-17hs19-2004s1).

Use the real gun, fixed wire guide and separately supported umbilical. Start with
individual 16-count / 2.5 µm nominal screw changes at 1 s duration, then paired
reversals and bounded coordinated moves. Mark the first trials as identification;
small issued increments may produce no distinguishable response. Never accumulate
blind corrective moves while a coordinate is unresponsive. Measure and log actual
response. If a larger 0.0400 mm diagnostic move fails to produce the expected
signed change, stop and correct drive/preload/cable loading before increasing
the working range.

Actuate all 24 travel/overload switches individually while armed but stopped, then the
latched STOP. All axes must become inhibited; stop must also remove VM. Release
the input: no restart is allowed. `clear` plus an actual datum reset are required.
With supports/catches in place, unplug host USB during a small dry move while
the brick stays on. The Pico must remain powered by the buck, become inhibited
and require a fresh reference on reconnection. Cut 24 V during a separate small
move; USB must keep status alive, VM must read absent and passive retention must
carry the load. Finish with a controller reset: startup must remain inhibited.
Use the logs/observation to measure actual response and stop displacement;
the programmed 500 ms host timeout is not itself a stop-distance measurement.

Install the guarded 24 V cross-flow fan across all six heatsinks. Record
motor-case and driver-heatsink contact temperatures at startup and every
five minutes during a repeated loaded sequence and prolonged hold. Continue
until readings show no increasing trend exceeding the thermometer's documented
uncertainty across three consecutive five-minute intervals (15 minutes). A ±2°C
tool cannot establish a 1°C plateau without a separate repeatability
characterization. The temperature upper bound, reading plus its uncertainty,
must stay at or below the provisional **50°C** dry-build ceiling; a ±2°C
uncertainty therefore requires readings no higher than 48°C. This protects
handling and limits heat into nearby printed/reference
parts, and is not the chip's thermal rating. Stop for any warning, continuing
temperature rise, changing retention drag, inconsistent sign, stuck movement or
unexplained feature jump. A cooling/current/mechanical adjustment starts a new
fixed-setting trial series. Loaded drive acceptance requires adequate measured
signed response with no missed large diagnostic moves, acceptable temperature
plateau and retention still within its accepted torque range.

## 5. Screen linear scale and the angular length law

**Decision:** whether configured lead/reduction and clevis geometry are close
enough for conservative nominal-envelope use, or need correction before the
controller's model is trusted. This is a coarse assembly screen; feedback
performance still comes from observed local response.

For X/Y/Z, mount the existing indicator on the stationary axis frame with its
probe aligned to a rigid carriage face. Tube removed, retention accepted and
loaded image armed, move slowly to a starting point at least 5 mm from a switch.
Set the indicator near its midrange and note its zero. Use `target X 5 1000`
for a +5 mm nominal displacement from the physical central datum, then `target X 0 1000`;
repeat from the same approach direction and for Y/Z. The host splits a target
into ≤0.1 mm coordinated segments. Observe for stick-slip and log the total
physical span, not a sum of nominal counts. A reversed zero need not reproduce
a micrometer pose; use a fresh indicator reading before another scale span.

The coarse scale band is **±0.10 mm on a 5.00 mm span** (2%). Applying that scale
allocation across the 85 mm soft half-travel uses 1.70 mm of the 4 mm nominal
soft-to-switch margin. The remaining 2.30 mm must cover independently bounded
reference error, spatial variation/backlash/compliance, measurement uncertainty
and measured stop excursion. Measure the actual trip locations and intended
endpoint clearances; restrict the accepted travel if this combined budget does
not fit. The 13 µm-graduation indicator distinguishes the local band, but its
graduation is not a calibrated uncertainty. Do not extrapolate a local span
into full-travel accuracy. A result outside the band changes the nominal-scale
calibration/lead/ratio diagnosis and permitted workspace; it does not itself
disqualify an observable mechanism from the camera loop. Inspect correct screw
lead, belt ratio, loose pulleys and missed motion, then update the canonical
geometry/count mapping and rebind firmware if scale changes.

For U/V/W, with no tube and a verified collision-free local path, issue
`angle U 5 1000`, `angle U 0 1000`, `angle U -5 1000`, and restore 0; repeat V/W.
Measure actual lever-pin coordinates in each axis's local plane relative to its
neutral datum and shaft center using the existing caliper and fixed datum
faces/clamps. Measure small coordinate changes (approximately 13 mm tangential
at 5°), rather than a 180 mm pin-to-pin span beyond the 6-inch caliper's range.
Use `atan2(pin_y,pin_x)` with the measured neutral vector to obtain the angle.
Record datum alignment, measured radius, sign and setup repeat readings.
The nominal actuator law is read from the canonical mechanical manifest:
`L²=L0²+2L0r sin(theta)+2r²(1−cos(theta))`, with r = 150 mm / L0 = 180 mm.

The coarse law screen allows **≤0.20° residual with setup uncertainty≤0.05°**,
a combined 0.25° allocation from the 1° angular soft-to-switch margin. At 150 mm
lever radius0.05° is about 0.131 mm tangentially, within a deliberately coarse
caliper/datum setup if repeated measurements support that uncertainty. If the
setup cannot support it, record the law as unverified and improve its datum
setup; do not invent precision from display digits. Verify each subsequently
intended operating region and keep the actual clearance map. A different
measured law is calibrated explicitly before using angular soft boundaries.
These bands screen gross geometry/configuration; they do not claim 10 µm tool
accuracy or a factory return-repeatability result.

## 6. Learn local motion and close the dry correction loop

**Decision:** whether inexpensive screws/contacts provide sufficiently dense,
stable observable corrections under the actual payload, cable and temperature.

Fix both close-view cameras' native resolution, zoom, manual focus, exposure,
lighting and rigid reference mounts. Use complementary views of the aiming dot,
actual protruding wire endpoint, seam and gun reference geometry. Camera settings,
frame gaps, image dimensions and synchronization must pass the observation
package's measurement gate before accepting a trial. A view of one dot does not
establish all six pose coordinates.

The [observation record schema](../../tools/gun-positioner-observation/gpobs/schema.py)
binds frame IDs/times, optics snapshots, issued moves, device clocks, observed
values/uncertainty and trial outcomes. Use its native frame capture/logging tools;
do not replace its records with a competing result format. The simple controller
JSONL is a lower-level transport log that can accompany that dataset.

Run signed single-axis probes, zero-motion holds and repeated reversals at the
same local pose; then independent multi-axis probes. Begin at 16, 32, 64 and
256 counts, adapting the sequence when observations show stick-slip or take-up.
Record actual before/after feature vectors and settling, not only the proposed
pose. Include direction/history and temperature in the model. Retain unsuccessful,
unresponsive and faulted trials with their reasons.

Fit `host/visual_servo.py::fit_jacobian` to comparable local trials. Its six screw
columns need observable independent feature coordinates; a deficient fit rejects
corrections. Set an initial 0.01 mm screw trust region and use
`correction(jacobian, desired_minus_observed_features)`. Convert its candidate to
counts, check limits/clearance, issue one coordinated segment, acquire fresh
paired observations and update the model. Reduce trust size if a step crosses
the useful interval. There is no blind backlash-jump correction or powered park
routine. The nominal dot-pivot calculation takes a measured tool transform;
the CAD gun vector is a proxy and cannot qualify the real gun.

Physical performance acceptance has two linked parts: the observed residual
must meet the 0.010 mm requirement / 0.005 mm design target, and independently
supported image-to-work conversion/measurement uncertainty must justify that
claim. Establish the latter through a characterized local calibration artifact
or independent displacement reference with its actual uncertainty. Until then,
pixel improvement and stable correction response are useful development
results, with micrometer accuracy explicitly unqualified.

## 7. Dry rotation and process development

**Decision:** whether the learned trajectory plus fresh observations can maintain
the gun/seam relationship while the tube rotates, with sufficient correction
authority and delay for the measured disturbances.

Keep the existing rotator's pedal/controller independent. It has no live phase
USB stream. Observe a fixed table fiducial or a separately characterized encoder
on the common frame timeline; record its uncertainty and direction. Start at the
rotator's accepted 8 mm/s dry speed and preserve its pedal behavior.

Register this tube's seam, collect repeated laps, and learn smooth phase-indexed
feedforward pose changes. Camera corrections still check the moving seam.
Hold out subsequent laps from fitting and log achieved residual, uncertainty,
feature visibility, observation/move/settle delay, bound saturations and aborted
trials. Preparation may take days; no number of nominal microsteps or rehearsed
laps proves the loop works. Acceptance is observed tracking in the accepted
workspace, plus physical support and fault recovery.

Dry observations do not qualify operation under laser emission, wire feed,
shielding and heating. The live phase needs its own optical protection/filtering,
exposure/lighting, measured detection uncertainty and latency, deterministic
process interlocks and weld development. No host/LLM conversation controls that
timing or authorizes laser firing. Completed-vessel acceptance remains the
application's 180 psi / 30-minute pressure result, separate from this positioner
commissioning.
