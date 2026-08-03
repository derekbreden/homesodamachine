# pcba bring-up console

A throwaway rig for a bare, JLCPCB-assembled controller board on the bench. It runs on
the board's **own** WROOM (U1) and answers one question — did the fab build what
[`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx) describes — by talking to every on-board
device and printing what it finds.

This is **not** the production firmware, and it carries no appliance logic: no state
machine, no persistence, no network. The firmware is [`main.cpp`](/firmware/src_pcba_bench/main.cpp);
this README carries the intent, the wiring, and the tear-down.

## Rig

A board and a USB-C cable. Nothing else is required, and nothing is hand-wired.

- 12 V into **J10** (the screw terminal, SE corner) — `PWR` and `5V` light from the rails alone.
- A plain USB-C cable into **J14** (west edge, above the WROOM). The on-board CH340C (U13)
  is the bridge and the cross-coupled NPN pair (Q2/Q3) does the auto-reset, so no button
  presses and no external programmer.

Off-board connectors (J1–J9, J11, J13) can stay empty. The console reads them either way,
and reads *empty* correctly — a floating input and an unlit divider are the expected result.

## Use

```sh
./tools/flash.sh pcba_bench
pio device monitor -e pcba_bench
```

It runs a full sweep at boot, then idles as a console (`RUN` blinks as the heartbeat,
`ACT` lights while a command runs). Type `help` for the list:

| command | what it proves |
|---|---|
| `info` | The WROOM, its crystal, its flash, the eFuse MAC, the reset cause |
| `scan` | The I²C bus reaches all three devices — 0x20, 0x21, 0x68 |
| `bus` | Whether R19/R20 are visible from IO21/IO22 across J8's barrel junction |
| `rtc` | U6 DS3231 answers, reports die temperature, and its seconds actually advance |
| `mcp` | Both MCP23017s: register reads, plus a write round-trip that never touches a pin |
| `in` | Every off-board signal pin, and the two gas dividers in millivolts |
| `rs485` | DI → U7 → A/B → U7 → RO closes entirely on-board, through R6's termination |
| `watch` | Audible continuity probe — touch a connector pin to its GND and hold until it beeps |
| `walk` | The three firmware LEDs are on the GPIO the map says they are |
| `buzz` | The IO13 → R5 → Q1 → U8 buzzer chain (audible) |
| `arm` / `drive` | Drive one output for 120 s so it can be metered at its connector |
| `all` | The whole sweep |

`watch` walks a whole net — ESP32 pad, via, trace, connector barrel — with nothing but a
jumper, which is the check no view of the model can stand in for. It answers through the
board's own buzzer at one pitch per net, so probing needs no screen and no timing: touch and
hold until it sounds. A contact has to hold 40 ms to register, and the serial log names
whichever net answered. GPIO34–39 carry no internal pull-up, so IO34/IO35 stay out of it.

## Actuator outputs

Four GPIO reach off-board actuators. They are inputs until `arm` unlocks them, `drive` holds
one at a level for metering, and the arming lapses after 120 s:

| GPIO | Reaches |
|---|---|
| `IO2` | J5 relay — carbonator diaphragm-pump 12 V gate |
| `IO19` | U15 interlock → J5 relay — compressor AC switch |
| `IO17` | U11 DRV8870 — pump A |
| `IO4` | U12 DRV8870 — pump B |

The same care governs the MCP probe. The MCP23017 GPA/GPB pins reach the TBD62083 valve
drivers, whose inputs are high-impedance DMOS gates: `IODIR` is never written (every pin
stays a high-Z input) and `GPPU` is never written, because a 100 kΩ pull-up is enough to
open a valve. The write round-trip uses `IPOL`, which only changes how a read is
interpreted and never reaches a pin.

Two of the three firmware LEDs sit on boot straps — `RUN` on IO12 (MTDI, VDD_SDIO select)
and `ERR` on IO15 (MTDO, ROM boot log). An LED to GND is high-impedance below its forward
voltage, so neither pin has a level of its own between resets. The rig holds them on the
ESP32's internal pulls (`parkStraps()`), and only `walk` drives them.

## Tear-down

Delete `firmware/src_pcba_bench/` and the `[env:pcba_bench]` block in
[`platformio.ini`](/platformio.ini) once the board's real firmware exists and covers the
same ground. Nothing else references either.
