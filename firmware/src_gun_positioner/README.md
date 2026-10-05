# Gun-positioner dry-development controller

Headered RP2040 Pico firmware for six independently driven screws. The controller
executes bounded synchronized relative moves, enforces travel loops and soft
count bounds, checks TMC2209 UART diagnostics and fails on a lost host heartbeat.
The host includes a USB console, log writer, clevis/dot-pivot kinematics and local
response fitting. Cameras determine attained gun position. There is no laser,
wire-feed or rotator command output in this package.

Wiring is in [control.md](../../hardware/gun-positioner/control.md). Physical
acceptance is in [commissioning.md](../../hardware/gun-positioner/commissioning.md).
The compiled upload asset and binding manifest are in [assets](assets/).

## Build without hardware

Use the released [Raspberry Pi Pico SDK 2.2.0](https://github.com/raspberrypi/pico-sdk/tree/2.2.0),
CMake≥3.21 and an Arm GNU toolchain with arm-none-eabi-gcc/g++ and newlib.
Initialize the SDK's `lib/tinyusb` submodule. `PICO_TOOLCHAIN_PATH` points to the
toolchain's `bin` directory if it is not on PATH. This separate project does not
edit the appliance's PlatformIO environments.

```sh
python3 firmware/src_gun_positioner/make_geometry.py
cmake -S firmware/src_gun_positioner -B /tmp/gun-positioner-build \
  -DPICO_SDK_PATH=/absolute/path/to/pico-sdk -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/gun-positioner-build --parallel
python3 firmware/src_gun_positioner/make_uf2.py \
  /tmp/gun-positioner-build/gun_positioner.bin /tmp/gun-positioner-build/gun_positioner.uf2
c++ -std=c++17 -O2 -DNDEBUG -Wall -Wextra -Werror \
  firmware/src_gun_positioner/tests/policy_test.cpp -o /tmp/gun-positioner-policy-test
/tmp/gun-positioner-policy-test
c++ -std=c++17 -O2 -DNDEBUG -Wall -Wextra -Werror \
  firmware/src_gun_positioner/tests/safety_test.cpp -o /tmp/gun-positioner-safety-test
/tmp/gun-positioner-safety-test
c++ -std=c++17 -O2 -DNDEBUG -Wall -Wextra -Werror \
  firmware/src_gun_positioner/tests/protocol_test.cpp -o /tmp/gun-positioner-protocol-test
/tmp/gun-positioner-protocol-test
python3 firmware/src_gun_positioner/tests/host_test.py
python3 firmware/src_gun_positioner/tests/client_test.py
python3 firmware/src_gun_positioner/tests/wiring_test.py
python3 firmware/src_gun_positioner/host/positioner.py simulate \
  --output /tmp/gun-positioner-sim.jsonl
```

For the loaded-development build use a separate build directory and pass
`-DPOSITIONER_LOADED_PROFILE=1 -DPOSITIONER_MAX_RATE=1000` at configuration.
Bench uses `-DPOSITIONER_LOADED_PROFILE=0 -DPOSITIONER_MAX_RATE=2000`.
`make_geometry.py --check` binds count limits to the canonical mechanical
geometry; CMake refuses stale limits. Host kinematics read that same geometry
file, including neutral length and mounting orientation.

These operations open no serial port. The simulator uses the same portable
motion policy as the firmware. Its edge log is labeled `policy_simulation`,
with no physical-observation result.

For physical upload: unplug the 24 V brick, set MOTOR POWER OFF and engage the
mechanical supports/retention. Hold Pico BOOTSEL while connecting USB; copy the
bound `gun_positioner.uf2` to the RPI-RP2 volume. It reboots into unreferenced,
disabled control. No upload has been performed as part of preparing these assets.
[Pico bootloader instructions](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html).

## Host console

Install the host dependency in a dedicated environment:

```sh
python3 -m venv /tmp/gun-positioner-host
/tmp/gun-positioner-host/bin/pip install -r firmware/src_gun_positioner/host/requirements.txt
/tmp/gun-positioner-host/bin/python firmware/src_gun_positioner/host/positioner.py inspect \
  --port /dev/cu.usbmodemYOUR_PICO
/tmp/gun-positioner-host/bin/python firmware/src_gun_positioner/host/positioner.py console \
  --port /dev/cu.usbmodemYOUR_PICO --log /tmp/gun-positioner-session.jsonl
```

`inspect` only requests status. `console` permits explicit operator actions and
closes with a stop. It starts 100 ms heartbeats after `arm` and never chooses a
serial port automatically.

```text
clear
reference central
arm
jog X 0.0025 250
move6 0.0025 -0.0025 0.0025 0.0025 -0.0025 0.0025 500
status
disarm
quit
```

`clear` reconfigures and verifies all drivers while disabled. `arm` performs a
fresh six-driver diagnostic/configuration read before enabling. Every observed
motor-supply excursion invalidates verification and reference, even while
disabled. Restoring power requires `clear` and a new physical reference.
`reference central`
means the physical datum fixtures/marks have established all six central
coordinates; it sets issued counts to zero. Each `jog` is a signed screw
extension in millimeters followed by duration in milliseconds. U/V/W are screw
extensions, not angular degrees. A 0.0025 mm request is 16 external microsteps.
Fault, reset, stop, disarm and console exit invalidate reference. Recovery needs
healthy loops/power, `clear`, and a physically re-established central datum.
The controller has no powered escape from an opened limit: support the load,
unplug 24 V and manually release the affected end before resetting its datum.

## Raw protocol

ASCII requests are newline terminated, at most 239 bytes; replies are JSON lines.
Use the 8-lowercase-hex-digit `boot` from `STATUS` and the next integer after
`last_seq`. Every accepted mutating command advances that sequence exactly once.
The boot token is stale-command protection, not network authentication.
Mutating ACK/error replies echo `op` and `seq`; the client matches both.
A missing, partial or ambiguous mutating reply sends STOP, attempts a STATUS
sequence resync and latches host failure. It never retries the move. Operator
`recover` stops, resyncs and rechecks controller profile/scaling explicitly;
an incompatible replacement/reset cannot clear host failure. Then `clear` and an actual central datum
are required before reference/arming. STOP accepts any case and suffix;
overlong or nonprintable input inhibits immediately. Input service is bounded
so a command flood cannot starve the foreground/watchdog indefinitely.

```text
STATUS
DRIVERS
STOP
CLEAR <boot> <seq>
REF <boot> <seq>
ARM <boot> <seq>
PING <boot> <seq>
DISARM <boot> <seq>
MOVE6 <boot> <seq> <duration_us> <dX> <dY> <dZ> <dU> <dV> <dW>
```

MOVE6 requires healthy armed state and no active move. Each count delta is
−640…+640, with a nonzero total vector; duration is 100,000…2,000,000 µs. Cubic
peak-rate/acceleration checks can further reject a short duration. There is one
active segment and no queue. Use `completed_seq` to identify completion; new
segments and visual corrections require fresh observations appropriate to the
experiment. `count` means issued pulse history. It remains visible after a fault
but `referenced=false` prevents using it as a trusted origin.
`vm_epoch` changes on observed supply transitions; `timer_ticks` counts completed
safety timer cycles. The 250 ms hardware watchdog is fed only when that counter
advances, so a busy foreground cannot hide a stopped timer.

The **bench** image uses fixed 16 microsteps, SpreadCycle, about 0.337 A RMS
for R110 modules and a 2,000 counts/s peak limit. The **loaded-development**
image uses Z 1.271 A RMS, pitch V 0.459 A and other axes 0.337 A, with 1,000
counts/s. Select the named image explicitly. Verify `profile`,
`current_scales=[10,10,10,10,10,10]` for bench or `[10,10,22,10,14,10]` loaded,
`configured_vsense=[1,1,1,1,1,1]` for bench or `[1,1,0,1,1,1]` loaded,
matching decoded `vsense` readings,
six decoded `microsteps=16` readings and `counts_per_mm=6400` after `clear`.
Unverified voltage-range and microstep readings are null. Loaded acceptance requires measured
brake retention, no missed loaded response and stable temperatures. Motor
holding-torque proportions do not establish this acceptance.
Changing those settings, reduction, screw lead or geometry requires updating the
firmware bounds, host scaling and binding manifest together. DIR initially uses
HIGH for positive X/Y/U/V/W counts and LOW for Z. Positive Z moves upward,
reducing screw span from its fixed top thrust. Verify physical sign; reverse a coil pair only while fully
deenergized, or change the observed axis inversion in `pins.h` and rebuild.

## Observation-development interface

`host/kinematics.py` provides `actuator_length`, `actuator_angle`, `pose_to_counts`,
`dot_rotation` and `split_target`. XYZ are mm; local U/V/W angles are degrees
about their clevis central positions. Nominal mounting angles come from the canonical mechanical manifest.
`dot_rotation` requires an entered measured gun-local center-to-dot vector;
its coincident-pivot model must be replaced by the fitted transform if actual
axes do not coincide. Counts and geometry are nominal motion proposals.
U/W are bounded to ±20°; V pitch is −20..+10°. `pose_to_counts` rejects an
out-of-range angle before fractional-count endpoint rounding. The mechanical
per-axis bounds in the canonical JSON also generate the firmware's soft counts.

`host/visual_servo.py` provides `fit_jacobian(trials)` and
`correction(jacobian, feature_error, trust_mm=0.01)`. A trial has six signed
`delta_mm` screw changes and at least six independent observed `delta_feature`
coordinates. Feature units stay consistent with the observations. Fit comparable
direction/history neighborhoods separately; no automatic optical unit conversion
or blind backlash compensation is supplied. A rank-deficient fit refuses a
correction. `correction` returns a bounded candidate and sends nothing to hardware.

The [observation schema](../../tools/gun-positioner-observation/gpobs/schema.py)
binds two camera frames, rotator observation and uncertainty to a controller
session. Native image acquisition, detector/calibration choice and live laser
visibility are named development steps rather than simulated success claims.
