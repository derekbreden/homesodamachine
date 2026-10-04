# X1 Pro interface capture

`capture.py` records received serial bytes without sending commands. It requires
an explicit device and baud rate, leaves flow control disabled, and sets DTR/RTS
inactive before opening. Host drivers can still pulse modem-control lines, so
the machine connection contains only received data and signal ground.

The customer outcome is computer access to weld recipes and process status.
The present tool establishes a way to collect communication evidence; it does
not implement a welder protocol or control emission.

## External RS232 connection

The [X1 Pro manual, section 1.5, printed page 4](https://cdn.shopify.com/s/files/1/0973/4353/7468/files/X1_Pro-Manual-EN.pdf?v=1773891208)
identifies rear DB9 pin 3 as machine TXD, pin 2 as machine RXD and pin 5 as signal
ground. It specifies RS232 signal levels of -10 to +10 V. This is not a TTL UART
or an RS485 connection.

The capture hardware is a
[Waveshare FT232RL isolated USB-to-RS232/485/TTL adapter](https://www.amazon.com/dp/B07L2VLY5D)
and a [DB9 male/female screw-terminal breakout kit](https://www.amazon.com/dp/B0DRZ15WW8).
Both listings showed Prime in the signed-in Amazon buy box on 2026-10-04. Use
the adapter's DB9 RS232 connector; its screw terminals serve TTL and RS485.
The [adapter manual, pages 1, 3 and 10](https://files.waveshare.com/wiki/USB-TO-RS232-485-TTL/manual/USB_TO_RS232_485_TTL_-user-manual-en.pdf)
specifies isolated power/signals, a male DB9, RX on pin 2, and GND on pin 5.

The X1 manual shows a female DB9. Use a male breakout at the X1 and a female
breakout at the adapter. Connect only these two wires:

| X1 rear DB9 | Receiver connection |
|---|---|
| Pin 3, machine TXD | Adapter DB9 pin 2, RS232 RX input |
| Pin 5, machine signal GND | Adapter DB9 pin 5, isolated-side signal GND |
| All other pins, including machine RXD pin 2 | Disconnected |

For another adapter, verify its own pinout. Read molded pin numbers on the connector; front and wire-side views
are mirrored. There is no VCC connection. A fully wired serial cable does not
provide this receive-only boundary.

With both ends unplugged and unpowered, use the acquired multimeter's continuity
mode to verify the two intended connections and that machine pin 2 has no path
to the adapter. Keep host TX, DTR, RTS and all other signals out of the machine
harness. Connect control cables with the machine unpowered. Leave DB25 and the
factory emergency-stop connection in their normal configuration.

The acquired [DSD TECH SH-U09B3](../../hardware/ledger/tools.md) is a 3.3 V TTL
adapter and cannot connect directly to this RS232 port. The acquired ALMOCN
RS485 modules also cannot substitute for an RS232 receiver.

## Capture

Use an installed Python with pyserial; the current system Python and the
PlatformIO environment provide it. Enumerating ports does not open them:

```sh
python3 tools/x1_control/capture.py --list
```

Choose the new adapter's device explicitly. Do not use another controller's
serial device merely because it is present. Store captures outside the public
repository. Each output directory must be new:

```sh
python3 tools/x1_control/capture.py \
  --port /dev/cu.YOUR_RS232_ADAPTER \
  --baud 115200 --seconds 30 \
  --output /tmp/x1-capture-115200 \
  --label 'cold boot, receive only' \
  --rx-only-wiring-confirmed
```

115200 is a receiver trial setting, not a known X1 baud rate. A separate capture
can use 19200, 9600, 38400 or 57600. Passive baud trials cannot identify a silent
request/response port. A UART edge capture is needed for automatic bit-rate
identification when traffic exists but no receiver setting is known.

The output includes exact bytes in `raw.bin`, host read batches with timestamps
and offsets in `events.jsonl`, and configuration/result metadata in
`capture.json`. Host read timestamps are not individual wire-edge timestamps.
USB serial framing errors and lost bytes are not independently measured.

## Bench decision

Start with receive-only boot capture. Keep the key OFF and removed, factory
emergency stops latched, screen enable off, gun trigger untouched and work-contact
loop open. The manual's troubleshooting screenshots on printed pages 18 and 19
show an operating HMI during key-off Interlock and E-stop alarms. Confirm the
owned unit's screen remains powered; the state of its RS232 electronics is
unverified. No laser firing is part of this investigation.

If the screen stays available with emission inhibited, capture ordinary changes
to one displayed, nonsafety recipe value at a time. Record its original value,
move one UI step lower, and restore the original; repeat three times and note
event times. Do not change modes or enable emission to obtain traffic. The
rear port is not known to echo touchscreen changes.

Useful evidence is repeatable traffic associated with boot or a known setting
change. A UART decode is accepted only when repeated observations agree;
random readable characters do not establish a protocol. Silence is inconclusive
and is not a reason to send guessed command packets.

If the rear port does not expose setting traffic, inspect the controller and
touchscreen connections with the machine unplugged. Photographs of board model,
connector labels, both ends of the screen cable, and screen device/firmware
details determine the next receiver and harness. A SUP22F-XH head marking alone
does not establish cabinet-controller compatibility with SuPER's protocols.

The next candidate is a passive tap that leaves the original screen/controller
connection intact and records both directions through a high-impedance input.
An ordinary extra RS232 receiver can overload an existing point-to-point link;
its suitability as a parallel tap must be established. An internal bus must be
identified as TTL, RS232, RS485 or another interface, with voltage and ground
confirmed, before attaching a receiver or logic analyzer. Cabinet mains, laser
power wiring and the optical assembly are outside this capture procedure. No
unknown internal pin is an approved probe point.

Parameter writes require a decoded, repeatable command and response, confirmed
controller identity, emission inhibited, and exact agreement between requested,
read-back and displayed values. Laser start control is a separate integration
step that preserves the factory weld sequence and hardware interlocks.
