# X1 Pro rear-port console

The X1 Pro's rear **RS232** port is the laser controller's serial console: a
Xinghan Laser board running RT-Thread 4.1.0 (build Sep 29 2025), presenting
RT-Thread's `msh` shell at **115200 8N1**. The owned unit answers as SN
`693FB526`. Two tools reach it from a Mac over the
[Waveshare FT232RL isolated USB-to-RS232/485/TTL adapter](https://www.amazon.com/dp/B07L2VLY5D):
`capture.py` listens without transmitting, and `console.py` sends one command
line and records the reply. The customer outcome is computer access to weld
recipes and process status.

`msh` reads the full machine state — `status`, `iostate`, `error`, `cur_pro`,
`getall`, `worktime`, identity — and also carries live actuators (`onkey`,
`power`, `pilot`, `gas`, `pulse`, `feeder`, the `dflt*`/`fac*` restores,
`reboot`). Discovery uses the read commands only. The hardware interlocks — key
switch, both E-stops, the ground-lock clip — gate laser emission independently
of this port: the firmware reports them in its error word (`INTERLOCK ESTOP
GND_LOCK`) and holds work state at `ERROR` with power output `OFF`, and a console
command does not relax them.

## Wiring

The [X1 Pro manual, section 1.5, printed page 4](https://cdn.shopify.com/s/files/1/0973/4353/7468/files/X1_Pro-Manual-EN.pdf?v=1773891208)
labels rear DB9 pin 3 machine TXD, pin 2 machine RXD and pin 5 signal ground, at
RS232 levels (-10 to +10 V) — not a TTL UART or RS485. On the owned unit the
transmit and receive pins are the reverse of those labels, confirmed with the
multimeter against pin 5 (DC volts, machine on, key off, E-stop in): **pin 2
idles at the RS232 mark level, about -5 to -10 V, and is the machine's output;
pin 3 sits near 0 V and is its input.** The working harness is straight-through
on three lines:

| X1 rear DB9 | Adapter DB9 | Carries |
|---|---|---|
| Pin 2 | Pin 2, RX | machine → Mac |
| Pin 3 | Pin 3, TX | Mac → machine |
| Pin 5 | Pin 5, GND | signal ground |

Leave pins 1, 4 and 6–9 open. The
[adapter manual, pages 1, 3 and 10](https://files.waveshare.com/wiki/USB-TO-RS232-485-TTL/manual/USB_TO_RS232_485_TTL_-user-manual-en.pdf)
gives it a male DB9 with RX on pin 2, TX on pin 3, GND on pin 5, and isolated
power and signals. Use a male breakout at the X1 and a female breakout at the
adapter from the [DB9 screw-terminal kit](https://www.amazon.com/dp/B0DRZ15WW8);
for any substitute adapter verify its own pinout, since molded front and
wire-side pin numbers are mirrored. There is no VCC wire. Make the connections
with the machine unpowered, verify them with the multimeter's continuity mode,
and leave the DB25 and the factory emergency-stop connection in their normal
configuration. The [DSD TECH SH-U09B3](../../hardware/ledger/tools.md) (3.3 V
TTL) and the ALMOCN RS485 modules cannot drive this RS232 port.

For listen-only work, omit the pin-3 wire; `capture.py` then sees only the
machine's output and signal ground.

Hardware and costs are recorded in
[purchases.md §16](../../hardware/ledger/purchases.md#16-laser-welding--cleaning--cutting),
with quantities in [diagnostic inventory](../../hardware/ledger/inventory.md#diagnostic).

## Tools

Use an installed Python with pyserial; the system Python and the PlatformIO
environment both provide it. Enumerating ports does not open them:

```sh
python3 tools/x1_control/console.py --list
```

Choose the adapter's own device explicitly; do not use another controller's
serial device merely because it is present. Store captures and transcripts
outside this public repository, and give each run a new output directory.

`capture.py` records received bytes only — no writes, no modem-control
assertion — into `raw.bin`, timestamped `events.jsonl` and `capture.json`:

```sh
python3 tools/x1_control/capture.py \
  --port /dev/cu.YOUR_RS232_ADAPTER --baud 115200 --seconds 30 \
  --output /tmp/x1-boot --label 'cold boot' --rx-only-wiring-confirmed
```

`console.py` sends one command line (CR by default, which is what the shell runs
on) and captures the reply for a few seconds. Send read commands only during
discovery; do not script `onkey`, `power`, `pilot`, `gas`, `pulse`, a
`dflt*`/`fac*` restore, or `reboot`:

```sh
python3 tools/x1_control/console.py \
  --port /dev/cu.YOUR_RS232_ADAPTER --cmd status \
  --output /tmp/x1-status --label 'idle state, key off'
```

Host read timestamps are not individual wire edges, and USB framing errors or
lost bytes are not independently measured.

## What the console reports

`status` returns work mode and state, laser power output, drive voltages and
currents, pilot and PD readings, NTC temperatures, pressure, and the full
`IO state` word; `iostate` lists every board input as H/L; `error`, `warning`
and `lock` give the active fault words; `cur_pro` and `getall` dump the running
process and the factory parameter table; `worktime`, `sn` and `ver`/`version`
identify the unit and its hours.

`getall` and the many `Displays or sets …` commands print a value when given no
argument and write it when given one; a write changes a stored parameter, so
discovery keeps to the no-argument reads. Distinguish controller feedback from
the touchscreen's own variable memory: a console read or one successful
parameter change does not establish complete control. Include the key-off and
E-stop status in any coverage record; their hardware inhibit remains independent
of the software connection.

## Toward bounded writes

A parameter write is accepted only with the command and its read-back decoded
and repeatable, controller identity confirmed, emission inhibited, and exact
agreement between the requested, read-back and displayed values. Start with one
displayed, non-safety process value, changed one step and restored, read back
each time. Laser start control is a separate integration step that preserves the
factory weld sequence and the hardware interlocks; keep the key off, both E-stops
engaged and the work-contact loop open for all of it, and do not enable emission
to obtain traffic.

Maintain a coverage record for every required recipe field and status: command,
value encoding and limits, read-back, display agreement, and repeatability. No
transmitting harness or process-start controller is qualified by these tools.
