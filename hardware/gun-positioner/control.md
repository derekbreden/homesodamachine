# PGFUN positioner wiring

Use one BIGTREETECH SKR Pico V1.0 and a 24 V, 4 A supply. X operates yaw and
Y operates pitch. Both integrated drivers use UART1 GPIO8/9, addresses 0/2.
Preserve factory address wiring. Remove **all four DIAG jumpers** before
attaching normally closed limits. Z and E0 motor outputs remain unused.

The [manufacturer documentation](https://github.com/bigtreetech/SKR-Pico)
governs connector orientation. Identify printed SIG/GND/+V on the received
board; a wire-side view reverses pin order. Do not connect stop-input +V.

## Harnesses

| Circuit | Connection | Check |
|---|---|---|
| Supply | Brick centre positive to VIN+, sleeve to VIN- | Measure polarity before attachment; insulated strain relief |
| Yaw motor | Four leads to X motor socket | Ohmmeter identifies coils; each occupies an adjacent driver coil pair |
| Pitch motor | Four leads to Y motor socket | Same check; never unplug a powered motor |
| Yaw limits | X-STOP SIG GPIO4 -> COM/NC -> COM/NC -> X-STOP GND | Closed at centre; either end opens |
| Pitch limits | Y-STOP SIG GPIO3 -> COM/NC -> COM/NC -> Y-STOP GND | Same series continuity |
| Positioner stop | Z-STOP SIG GPIO25 -> button COM/NC -> Z-STOP GND | Latching button or broken wire opens |
| Rotator timing | E0-STOP SIG GPIO16 to pedal NO; E0-STOP GND to COM/rotator signal ground | 3.3 V released, near 0 V pressed |
| Cooling | 24 V fan to FAN3, positive to +, negative to switched - | GPIO20 on whenever firmware runs with VM |
| VM measurement | TH0 SIG GPIO27 through 8x4.7 kOhm series to VIN+; 3.3 kOhm SIG to GND | Insulated divider described below |
| Host | Board USB to Mac | 100 ms heartbeat in motion session |

The motor cable has a 0.1-inch connector. Check mating and coil order on
receipt. Use acquired wire/connector stock for a secured board connection.
Twist coil pairs, separate signal wiring, and tie strain relief to the case.
Do not leave a loose plug carrying a moving cable's tension.

The pedal stays connected to the rotator. Its NO signal is observed in
parallel. Confirm its voltage with the multimeter before joining grounds.
Do not connect a 24 V pedal interface or laser work-contact loop here.

## Supply divider

TH0 includes a 4.7 kOhm pull-up to 3.3 V and an ADC RC filter. With external
VM-to-SIG resistance 37.6 kOhm and SIG-to-GND 3.3 kOhm:

```
V_SIG = (VM/37600 + 3.3/4700) / (1/37600 + 1/4700 + 1/3300)
```

Nominal ADC values are 2702 at 18 V, 3067 at 24 V and 3310 at 28 V.
Firmware accepts 2701..3311. VM removal invalidates reference and driver
verification. USB alone cannot authorize motion. The calculation includes
the on-board pull-up.

Insulate all resistor splices, retain the string away from bolts/fan blades,
and expose only VIN/SIG/GND ends. With the board disconnected, measure the
37.6 kOhm and 3.3 kOhm sections separately. With USB and 24 V present, expect
about 2.47 V at SIG. Compare status ADC against the equation using measured
VM and 3.3 V. Correct a large mismatch instead of widening thresholds.

## Driver settings and faults

SpreadCycle, 64 external microsteps, interpolation off, CoolStep off,
current scale 13, VSENSE=0 and R110 shunts give nominal **0.774 A RMS /
1.094 A peak**. Hold current equals run current. This establishes a current
setting, not measured output torque or positioning accuracy.

Fresh UART writes, IFCNT increments and register read-back precede ARM.
Both drivers, stop, limits, VM, heartbeat and timer progress are monitored.
A fault disables both outputs and invalidates reference. Startup/reset leave
all four enables disabled. The 250 ms watchdog is fed only after timer progress.

The NC button is a firmware motion stop, not a separately rated safety relay.
It does not inhibit the laser. Factory laser controls and interlocks control
emission. Firmware has no laser-start command. A positioner fault stops its
pulses; release the rotator pedal and factory gun trigger to stop those
independent devices.

## X1 control interface

The purchased isolated Waveshare RS232 adapter and DB9 breakouts suffice
for [receive-only capture](../../tools/x1_control/README.md): X1 TX pin 3
to adapter RS232 RX pin 2, ground pin 5 to 5, all other pins disconnected.
The X1 manual specifies RS232; TTL and RS485 adapters cannot substitute.

DB25 pins 3/4 are enable +24 V/GND. Pins 5/6 are the factory E-stop loop.
They do not define a documented emission trigger. Automatic laser control
requires a captured or manufacturer-defined protocol with read-back and the
factory weld sequence preserved. First welding uses the factory trigger
while replaying a qualified dry trajectory. No additional interface purchase
is required to begin the existing capture procedure.
