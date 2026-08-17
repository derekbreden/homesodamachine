# The appliance controller

The firmware the machine runs. It is on the controller PCBA's own WROOM (U1), the board
[`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx) describes, flashed through that board's CH340C
over USB-C at J14. The procedure it answers to is
[`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md); the
state it boots to is the one
[`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) opens against.

`src_pcba_bench/` runs on this same WROOM and is a different instrument: a bare board,
once per fab batch, with the manifold unplugged.

## What runs today

One flavor pump. Everything else in the machine is unwritten.

- **A prime held from the glass.** Service → Prime → a flavor → hold the pad on the 4.3B
  front-face display. `MSG_PRIME_START` arrives on J9, the pump turns, a tick every 500 ms
  keeps it turning, and the head stops on the lift, on a tick that runs 2 s late, or at the
  60 s ceiling. Every state change goes back as `MSG_RESP_PRIME`.
- **A bounded run from the console.** `pump <a|b> [ms]`.
- **Status.** `MSG_STATUS_REQ` is answered with uptime, heap, J9 frame counts, the MQ-6
  divider and whether a prime is live.

Both MCP23017s are untouched, so the eleven valves and the condenser fan stay high-Z and no
reed is read. Neither relay is ever driven. A clean cycle is answered `MSG_ERR_UNSUPPORTED`.

## The files

| | |
|---|---|
| `main.cpp` | setup, loop, the serial console |
| `machine.cpp` | every pin that reaches a load, and the three limits |
| `link.cpp` | J9 frames in, machine announcements out |
| `pins.h` | what this image reaches on the board, off `pcba.tsx` |

`machine.cpp` is the only file that drives an actuator pin. The glass, the console, and the
faucet when it exists all reach it through `machine.h`, and the commissioning and service
commands (§6, §7, §9) are serial commands on this image asking it for a thing.

## Console

115200 baud, over the same USB-C cable you flash with.

```bash
pio device monitor -e appliance
```

| | |
|---|---|
| `pump <a\|b> [ms]` | run one flavor pump, bounded — default 2000, ceiling 60000 |
| `stop` | end whatever is running |
| `status` | machine state, uptime, heap |
| `link` | J9 frames, bytes, echo, time since the last frame |
| `ping` | put a frame on the pair and read its echo back |

`ping` separates this board's half of J9 from the far end. U7's `/RE` is tied to GND, so a
frame sent here returns to IO34 through the transceiver whether or not anything is on the
other end of the pair — bytes back mean IO32, U7 and R6 carry; a frame back means the
display answered.

## The three limits

They are in `main.cpp`'s header, in
[`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md) §9 where
the factory confirms them per unit, and in [`/firmware/README.md`](/firmware/README.md) with
the part that pays for each. At most 3 solenoid valves energized at once; relay #2 off while
a dispense is open; `GPPU` written on both MCP23017s.

## Build / flash

```bash
./tools/flash.sh appliance build   # compile only
./tools/flash.sh appliance         # build + flash
```
