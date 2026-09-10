# Weld-rotator controller

An ESP32-DevKitC-32E turns the purchased NEMA 23 through the purchased DM542T.
The HimaPro 50122 pedal is a low-voltage dry-contact deadman. It never carries
motor power.

## Connections

Set the DM542T signal selector to **5 V**. Use two channels of the acquired
ULN2803A module as open-collector sinks:

| From | To |
|---|---|
| ESP32 GPIO25 | ULN IN1 |
| ULN OUT1 | DM542T `PUL-` |
| ESP32 GPIO26 | ULN IN2 |
| ULN OUT2 | DM542T `DIR-` |
| ESP32 `VIN/5V` | DM542T `PUL+` and `DIR+` |
| ESP32 GND | ULN GND |
| Pedal `COM` | ESP32 GND |
| Pedal `NO` | ESP32 GPIO27 |
| ESP32 3V3 through acquired 4.7 kΩ resistor | ESP32 GPIO27 |
| Motor black / green | DM542T `A+` / `A-` |
| Motor red / blue | DM542T `B+` / `B-` |
| Acquired 5 V adapter with Micro-USB tip | ESP32 Micro-USB power input |
| 24 V adapter + / − | DM542T `VDC` / `GND` |

Leave the ULN `COM` flyback terminal and both DM542T `ENA` terminals
unconnected. The motor supply and 5 V logic supply remain optically isolated
through the DM542T inputs. Do not connect 24 V to the ESP32.

The pedal has SPDT terminals; use `COM` and `NO`. Twist those two conductors
together and fit the acquired 4.7 kΩ pull-up at the controller end. A broken
or unplugged pedal wire then reads released and stops motion, and the lower
input impedance rejects noise beside the welder. The acquired universal 5 V /
3 A adapter's Micro-USB tip powers the ESP32. Its listing and the ledger
account for that tip, so this build does not assume an unrecorded USB cable.

For flashing and the serial console, plug the DevKitC's own Micro-USB into the
host. Its onboard CP2102 handles the upload, the automatic bootloader reset and
the 115200 baud console, and it powers the board while connected. Once the
settings are stored, move the Micro-USB to the 5 V adapter's tip. The onboard
bridge drives `RX0/TX0` whenever the board is USB-powered, so no external TTL
adapter is connected to those pins.

## Driver switches

The motor is 2.8 A/phase. Set 3.76 A peak, 50% standstill current, and 3,200
pulses per motor revolution:

| Switch | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Position | ON | OFF | OFF | OFF | ON | ON | OFF | ON |

That current is the DM542T table's closest setting to the manual's
`phase current × 1.4` peak-current rule. The idle-current reduction limits
motor heating while the welder is being set.

## Operation

**The pedal is the whole of the control.** Held, the table turns at the stored
speed; released, it stops. Nothing counts a revolution and nothing stops the
table out from under the operator — the length of a lap is judged at the index
mark while watching the puddle, not enforced by the controller.

The one thing the controller refuses is a start it was not asked for: it powers
up motionless and will not arm until it has seen the pedal released once, so a
pedal held down through a reset cannot move the table. After that, every press
turns and every release stops, with no rearming in between.

The console reports how far the table has come in degrees, and says so again on
release. That number is a readout for the operator and is never a limit.

The default 8 mm/s bead travel is 1.235 rpm at the tube, or 48.6 s per
revolution. The accepted range is 5–15 mm/s. Settings are changed over the
ESP32 USB serial console at 115200 baud and persist in NVS:

```text
status
speed 8.0
direction cw
direction ccw
dirinvert on
defaults
```

The console is serviced only while the table is stopped, so serial formatting
and flash writes cannot stretch a step interval. The pedal is the live stop
control.

`direction` is the tube direction viewed from above. During dry commissioning,
mark the table, command `direction cw`, and tap the pedal. If the mark moves
counterclockwise, issue `dirinvert on` once. Do not move the wire guide until
that convention is verified.

## Build

```bash
pio test -e native -f test_weld_rotator_policy
pio run -e weld_rotator
```

Building opens no serial port. Upload only after the wiring is metered with the
24 V adapter unplugged; the host's USB powers the board during upload.
