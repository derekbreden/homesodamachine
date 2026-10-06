# PGFUN fixture commissioning

These checks decide whether the assembled device can retain the gun, move
usefully under load and repeat an accepted dry trajectory. Use the acquired
caliper, multimeter, 2 kg x 0.1 g scale, Neoteck indicator and its rotator
mount, hand hex keys,
two C-clamps, witness marks and a water-filled container with a soft cord.
No additional measuring-tool purchase is specified. Keep records beside this
hardware, with geometry hash, material/profile, date and actual measurements.
A successful check establishes only its stated scope.

## Incoming and power-off checks

1. Check both reducers against the received-interface dimensions in
   [assembly.md](assembly.md). Check bearing fit coupons and matched spacers.
   Free rotation must have no binding or axial rattle before case alignment
   is locked. Record the chosen journal/bore dimensions.
2. Attach the bridge and toes. Check every foot bears on the bench and the
   anchors cannot rock. Retain the existing rotator's bench attachment.
3. Install the gun with four-foot cable length supported by the cable post.
   Put witness marks on gun/bands, keys/flanges, shaft clamp and base.
4. With motor and welder power off, sweep both axes to all four corners of
   their hard-stop range, while turning the rotator through one revolution.
   Check the entire cable, actual switch rollers, bolt heads, wire guide,
   recessed tube rim and controller harness. No object may contact before
   its intended stop; the gun/guide must clear the tube at every corner.
5. Measure follower centre displacement at 70 mm radius with the caliper.
   An assembled +/-1.5 degree stop gives about +/-1.83 mm. Reject travel
   beyond +/-2.08 mm (1.7 degrees), any earlier interference or a loose stop.
   With a continuity meter, each limit must open between 1.40 and 1.65 mm
   follower displacement (1.15..1.35 degrees), before its hard stop.

These measurements change the release decision: an incorrect stop or received
interface can defeat the known clearance envelope. Correct it before power.
Do not enlarge bearing seats to accommodate an unrelated mounting error.

## Retention and cable load

Fill and weigh the container plus cord to **1.020 kg**, giving 10.00 N.
Keep it close to the bench over a padded catch. The container is a known
static load, not an impact test or an inferred hand-pull force.

With the tube removed, motors disabled and the frame supported by a soft
catch, apply this load through a broad soft loop around the printed cradle,
not the nozzle, trigger, fiber boot or wire guide. For a vertical load, hang
it directly; for another direction, turn the detached fixture and clamp its
flat bridge to present that direction vertically. Keep the force line within
240 mm of the pitch axis. The conservative gun-gravity bound plus this added
load is covered by the 7 N m normal structural screen. Hold for 60 seconds,
unload and repeat three times. Check band slip, base motion, key seating,
shaft retention, cracks and bearing-seat movement. No witness-mark shift,
permanent set, cracking or newly detectable rattle is acceptable. Do not
increase motor current to force a defective joint through this check.

The 10 N cable term is a design allowance, not an existing measured cable
force. Route a relaxed gun-side curve over the post without loading the boot.
The loaded camera checks below qualify that actual route. If the motor stalls,
a witness mark shifts or alignment changes when the cable moves, improve
support/slack and repeat the affected checks. Do not infer an independently
measured cable-force bound from the retention weight test.

With the gun installed, anchor an indicator to the stationary base and touch
a printed cradle face. Repeated load/unload cycles must return within one
indicator division and preserve witness marks. The owned indicator is a
coarse permanent-set check; its resolution does not certify 0.010 mm camera
performance. Use camera observations for the loaded precision checks below.

## Electrical commissioning

Use [control.md](control.md). Before power, verify coil pairs, supply polarity,
DIAG removal, the three closed NC loops, all six opened-loop conditions and
the insulated VM divider. Test one disconnected signal wire per loop. Verify
the pedal's released/pressed 3.3 V/0 V levels. No stop-input +V is connected.

Flash the supplied UF2 with motors unplugged, then remove the boot jumper.
USB-only status must show disabled outputs, invalid reference and unhealthy
VM. After measuring 24 V and divider SIG, power down, attach motors and
power up. Status must report the released matching geometry hash, 640,000
counts/rev, current scales [13,13], VSENSE [0,0] and 64 microsteps. Both UART
samples must be valid; clearing a fault does not establish a reference.

Align parking pins with power off, bias both toward the same designated
side, remove them, then use `clear`, `reference central`, `arm` in the host
console. Start with +/-32-count yaw and pitch jogs, 500 ms duration. Each
positive command must move as the CAD model specifies. If a motor rotates
oppositely, power down and reverse one complete coil pair, then repeat.
If coil order or motion is uncertain, stop before increasing the jog.

Test stop button, each of four limit switches, loss of VM and host heartbeat
one at a time during a small jog, away from the tube. Motion must cease,
outputs disable and reference become invalid. Unplug USB or terminate the
host to test heartbeat: it must fault within 500 ms plus one 250 us tick.
A GPIO-open stop/limit is sampled every 250 us. These are programmed bounds;
record actual behaviour. Repeat recovery from the physical parking datum
for every fault. No reset, CLEAR or reconnect may resume a previous motion.

## Loaded movement and heat

Run the camera procedure in [observation.md](observation.md), using the real
gun and cable, after the controller has held the working pose for 30 minutes.
Collect the motor response in all four approach-direction combinations and
collect a separate holdout session. Acceptance requires each feature's
uncertainty <=0.0025 mm, rank-two response with condition number <=30,
95th-percentile error <=0.005 mm and maximum <=0.010 mm. Counts that do not
produce useful movement remain part of the evidence; do not relabel a count
as measured travel.

Record stationary feature positions for ten minutes after warm-up, then
repeat the response holdout. No witness-mark movement or bearing rattle is
acceptable. Camera drift beyond 0.010 mm rejects that setup; correct heating,
cable drag, exposure/focus or clamp seating before recording new holdouts.
Record surface-temperature readings if an existing thermometer is available;
the essential acceptance is stable loaded observations, not an assumed
material-temperature rating. Inspect fan operation throughout.

## Dry runs and welding release

Index the tube physically with matching tube/nest marks. Use one direction,
rotator speed and cable route. Release the pedal for at least 12 seconds before
each run so its existing acceleration history matches the replay timing.
Learn a periodic correction, then validate the exact candidate in **two
independent dry captures**, each at least two complete revolutions. The host
rejects sparse phase coverage, invalid features, stale frames, timing
uncertainty, nonrepeatable runout and error outside the two-axis response.
Both dot and actual wire endpoint must satisfy maximum 0.010 mm and p95
0.005 mm observed errors. A visually pleasing lap is not a substitute.

For welding, withdraw the camera stand completely, preserve the indexed
setup and load only that accepted trajectory. Establish focus/attitude and
a working factory weld recipe on a sacrificial joint of the intended material
and thickness; neither 60 degrees nor 16 mm is a qualified process recipe.
The existing factory trigger controls emission. Pedal timing controls motion
replay. Begin with a short bead, inspect fusion and wire placement, then
progress to the continuous circular weld after both geometry and process
behaviour agree. A changed wire-feed setting, focus, tube joint, direction,
speed, static pose or cable route requires new affected dry validation.

This positioner does not qualify a pressure-containing weld. The project's
existing weld inspection and pressure-vessel acceptance requirements still
govern the final carbonator. Record weld/process results separately from
positioning results; do not infer fusion, penetration or pressure integrity
from a camera alignment result.
