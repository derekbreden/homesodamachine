# PGFUN two-axis controller

This RP2040 image runs on BIGTREETECH SKR Pico V1.0. It controls yaw and pitch
through integrated TMC2209 X/Y drivers, checks normally closed stop/limits,
verifies VM and driver registers, and executes bounded jogs or periodic
trajectories. It commands no laser, wire feeder or rotator motor.

Use [wiring](../../hardware/gun-positioner/control.md),
[commissioning](../../hardware/gun-positioner/commissioning.md) and
[camera learning](../../hardware/gun-positioner/observation.md).

## Install and flash

The released image is [pgfun-positioner-r1.uf2](assets/pgfun-positioner-r1.uf2).
Its [build receipt](assets/build-receipt.json) binds source and geometry hashes,
compiler/SDK versions and binary/UF2 digests. With motor supply disconnected
and motors unplugged, use the manufacturer's BOOT/USB procedure to mount
RPI-RP2, copy that UF2, then remove the boot jumper and reconnect normally.
Do not flash another controller merely because it exposes a boot disk.
No device was flashed during release preparation.

Use the existing CAD Python environment, or create a separate Python 3.11+
virtual environment and install `host/requirements.txt`. The Mac capture
helper lives in `tools/gun-positioner-observation/helper/`; rebuild it with
`build.sh --adhoc` only if the app bundle is absent or source changed.
Allow camera access to that app for physical capture.

```sh
tools/cad-venv/bin/python firmware/src_pgfun_positioner/host/positioner.py --list
tools/cad-venv/bin/python firmware/src_pgfun_positioner/host/positioner.py \
  --port /dev/cu.YOUR_POSITIONER --log /tmp/pgfun-console.jsonl
```

The console accepts `status`, `drivers`, `recover`, `clear`, `reference central`,
`arm`, `jog yaw 32 500`, `jog pitch -32 500`, `disarm`, `stop`, `quit`.
Physically align the parking pins with power off and remove them before
`reference central`. Software does not measure that datum. `arm` starts a
100 ms host heartbeat. Console exit, STOP, faults and reset invalidate it.

Every jog is <=256 counts/axis and 100..2000 ms. Command rate/acceleration
bounds still apply, so a short duration can reject a large jog. Travel is
+/-1777 counts per axis. Client target moves are segmented without changing
those controller limits.

## Periodic replay

`LOAD2`, sequential `KNOT` records and `PLAY` load a 16..256-knot periodic
Catmull-Rom path. Its 8..120 s period, cubic control envelope, rate and
acceleration are checked before playback. A fresh released pedal is required.
The existing rotator pedal's NO signal starts the path after 20 ms debounce
and 200 ms settling. Releasing it stops playback at its current counts.
Host heartbeat continues while waiting and running.

The host workflow learns responses in all four approach-direction branches,
fits a smooth runout profile and accepts it only after two independent dry
captures. Replaying a profile marked unqualified is refused. Geometry,
response model, target, speed, direction and tube index are bound to the
record. There is no actual tube-angle encoder; measured dry repeatability
must qualify the existing time-based rotation.

## Build and checks

Use Raspberry Pi pico-sdk **2.2.0**, Arm GNU **14.2.rel1**, CMake 3.21+ and Ninja.
Their absolute installation paths are supplied by the builder's environment.
Build outside the source directory:

```sh
python3 firmware/src_pgfun_positioner/make_geometry.py
cmake -S firmware/src_pgfun_positioner -B .cache/pgfun-build -G Ninja \
  -DPICO_SDK_PATH=/absolute/path/pico-sdk \
  -DPICO_TOOLCHAIN_PATH=/absolute/path/arm-gnu-toolchain/bin
cmake --build .cache/pgfun-build
python3 firmware/src_pgfun_positioner/make_uf2.py \
  .cache/pgfun-build/pgfun_positioner.bin \
  firmware/src_pgfun_positioner/assets/pgfun-positioner-r1.uf2
c++ -std=c++17 -Wall -Wextra -Werror -Wno-misleading-indentation \
  -I firmware/src_pgfun_positioner firmware/src_pgfun_positioner/tests/test_policy.cpp \
  -o /tmp/pgfun-policy-test
/tmp/pgfun-policy-test
tools/cad-venv/bin/python -m unittest discover -s firmware/src_pgfun_positioner/tests
```

Policy tests exercise real pulse counts, bounds, continuous replay, pedal
release, independent faults, UART CRC/framing and watchdog liveness. Python
tests use synthetic observations to check fitting, independent holdouts,
trajectory envelopes and stale-data refusal. These results verify software
behaviour; they are not physical gun-positioning records.
