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

The one connector worth populating is **J13**: a Kamoer KPHM400 on the `AM2`/`AM1` pair
(pump A) or the `BM2`/`BM1` pair (pump B) turns the two DRV8870s into an audible test,
which is what `pump` below is for. Both pins of a pair go to the same motor and either
polarity is a pass — the head is bidirectional, so which way it turns carries no verdict.

## Use

```sh
./tools/flash.sh pcba_bench
pio device monitor -e pcba_bench
```

At boot it prints the command list, scans WiFi, and starts the continuity probe; then it idles as a console (`ACT` blinks as the heartbeat, and lights
solid while a command runs). The first keystroke leaves the probe and calls the roll —
press Enter once to reach a `>` prompt. Type `help` for the list:

| command | what it proves |
|---|---|
| `info` | The WROOM, its crystal, its flash, the eFuse MAC, the reset cause |
| `scan` | The I²C bus reaches all three devices — 0x20, 0x21, 0x68 |
| `bus` | Whether R19/R20 are visible from IO21/IO22 across J8's barrel junction |
| `rtc` | U6 DS3231 answers, reports die temperature, and its seconds actually advance |
| `mcp` | Both MCP23017s: register reads, plus a write round-trip that never touches a pin |
| `in` | Every off-board signal pin, and the two gas dividers in millivolts |
| `rs485` | DI → U7 → A/B → U7 → RO closes entirely on-board, through R6's termination |
| `link` | J9 frame counters and the echo canceller's outstanding count |
| `pumpmsg` | Sends the display's own `MSG_PUMP_RUN` frame back at it |
| `watch` | Audible continuity probe — touch a connector pin to its GND and hold until it beeps |
| `walk` | The three firmware LEDs are on the GPIO the map says they are |
| `buzz` | The IO13 → R5 → Q1 → U8 buzzer chain (audible) |
| `arm` / `drive` | Drive one output for 120 s so it can be metered at its connector |
| `pump` | Run a peristaltic pump on J13 through a DRV8870 (audible) |
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

## Pumps

`pump a` / `pump b` runs a staged exercise on one channel, ~20 s, and any key stops it.

It is four stages. Three full-duty jabs, 80 ms on — the head twitches. A ten-step
climb from 10% to 100%, 700 ms a step, each step its own sound. Three seconds at full
speed. Then 75/50/25%, where a modulating `IN1` drops the head's pitch at each and a pin
shorted high or a bridge latched on holds full speed through all three.

`pump <a|b> <duty%> [seconds]` holds a single duty (max 60 s) for a longer listen or a
meter on the OUT pair, and `pump stop` parks both. A Kamoer head does not break away
part-throttle — 60% for a second turns nothing — so a run meant to be heard wants 100.

PWM is 20 kHz, above hearing — every sound the pump makes is mechanical. `IN2` is on the
GND plane, so `IN1` high drives and `IN1` low coasts, one direction only; polarity at the
connector sets which way the head turns and either way is a pass. A brownout reset stops
the motor: the pin reverts to an input, which the DRV8870's own input pull-down coasts.
`ISEN` sits on GND with no sense resistor, so the chip's current limit never trips and the
motor sees the 12 V rail through the bridge — ~0.8 A peak for a KPHM400.

## The J9 link

IO32 and IO34 carry a 115200 8N1 UART out to **J9** (`B · A · GND · V12`), where the
front-face display hangs. What arrives there:

| Frame | What the rig does | What goes back |
|---|---|---|
| `MSG_PUMP_RUN { channel, ms }` | Runs one pump at full power, blocking | `MSG_RESP_PUMP_DONE` after the run finishes |
| `MSG_PRIME_START { channel }` | Drives the pump and starts the tick clock | `MSG_RESP_PRIME { RUNNING }` |
| `MSG_PRIME_TICK { channel }` | Restarts the tick clock | nothing |
| `MSG_PRIME_STOP { channel }` | Parks the pin | `MSG_RESP_PRIME { STOPPED, ms }` |
| `MSG_STATUS_REQ` | Reads uptime, heap, frames, the gas divider | `MSG_RESP_STATUS` |
| `MSG_CLEAN_START { channel }` | — | `MSG_ERR_UNSUPPORTED` |

A prime is the one thing here that outlives the call that started it. `primeService()` runs
from `loop()` and parks the pin when a tick runs later than `PRIME_TICK_GRACE_MS` (2 s) or
the hold reaches `PRIME_MAX_MS` (60 s), answering `MSG_RESP_PRIME { TIMEOUT }` or
`{ LIMIT }`. While a prime holds a pin, `pump`, `drive` and `MSG_PUMP_RUN` all refuse it —
`link` names the channel and how long ago its last tick landed. What a run prints still
goes to the USB console.

`MSG_CLEAN_START` reaches valves the MCP23017 probe deliberately never drives, which is
what `MSG_ERR_UNSUPPORTED` says.

The transport is `HdlcLink` — TinyProto's framing layer with CRC16, no connection and no
keepalives. `Fd` collides with itself here: two ends transmitting on their own schedules
over one shared pair fall out of CONNECTED every 2 s, its retry timeout.

`/RE` is tied to GND on U7, so its receiver runs while its driver does and every byte this
board sends lands back in its own RX. `EchoCancel` wraps `Serial1`, counts what it writes
and swallows that many before ProtoLink sees them — the bus is half-duplex, so the echo
arrives contiguous and ahead of any reply. The 4.3B keeps its receiver off while driving
and has no echo to cancel.

`rs485` and `drive io32` drive IO32 as a plain pin, so both take the link down —
`rs485` restores it, and `rs485link` brings it back after `drive`.

The same care governs the MCP probe. The MCP23017 GPA/GPB pins reach the TBD62083 valve
drivers, whose inputs are high-impedance DMOS gates: `IODIR` is never written (every pin
stays a high-Z input) and `GPPU` is never written, because a 100 kΩ pull-up is enough to
open a valve. The write round-trip uses `IPOL`, which only changes how a read is
interpreted and never reaches a pin.

Two of the three firmware LEDs sit on boot straps — `RUN` on IO12 (MTDI, VDD_SDIO select)
and `ERR` on IO15 (MTDO, ROM boot log). An LED to GND is high-impedance below its forward
voltage, so neither pin has a level of its own between resets, and the rig parks both on
the ESP32's internal pulls (`parkStraps()`).

`pcba.tsx` gives the heartbeat to `RUN` and calls `ACT` *"activity, not a strap"*, and the
rig follows that. RUN being a strap is why the beat is 30 ms and not a square wave: the pin
lives parked on its pull-down and each beat steps out and straight back, so a reset landing
between beats finds MTDI already low, where the 3.3 V flash setting wants it.

## Tear-down

Delete `firmware/src_pcba_bench/` and the `[env:pcba_bench]` block in
[`platformio.ini`](/platformio.ini) once the board's real firmware exists and covers the
same ground. Nothing else references either.
