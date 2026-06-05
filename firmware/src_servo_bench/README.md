# Servo-bench prototype

Small standalone firmware for a spare ESP32: press a button, an MG90S servo
moves. Sole purpose: confirm the button + servo + ESP32 chain on the bench
before any of it has to work inside the appliance. Sibling of
[`../src_reed_bench/`](../src_reed_bench/README.md) — same throwaway-rig idea,
different peripheral.

This is **not** the production firmware. It's a throwaway rig. Planning and
tear-down both live in this README.

## Bench rig

### Parts (all already in stock or in the project's BOM)

- 1× spare ESP32 dev board (ESP32-DevKitC-32E or similar)
- 1× MG90S 9 g micro servo (Hosyond B09V5BR7J5)
- 1× momentary pushbutton (any) — e.g. the prewired micro buttons (B0F43GYWJ6)
- 5× Dupont jumpers: 3 for the servo plug (it takes male pins), 2 for the button

No breadboard. The servo's 3-pin plug and the button leads plug straight onto
the ESP32 header via Dupont.

### Wiring (ESP32-DevKitC)

**Servo** — MG90S 3-pin plug (brown / red / orange):

| Servo lead | Color | ESP32 pin |
|---|---|---|
| signal | orange | `GPIO 13` |
| V+ | red | `5V` |
| GND | brown | `GND` |

**Button** — momentary, either orientation:

| Button leg | ESP32 pin |
|---|---|
| leg 1 | `GPIO 27` |
| leg 2 | `GND` |

The button uses the ESP32's internal pull-up (`INPUT_PULLUP`), so no resistor is
needed — a press pulls `GPIO 27` to GND. The servo's V+ is fed from the board's
`5V` pin (USB 5 V passthrough), which is fine for one **unloaded** MG90S on the
bench. If you load the servo and it stalls, the current spike can brown out the
ESP32 and reset it — in that case power the servo from a separate 5 V supply and
share GND with the ESP32.

## Behavior

Each button press toggles the servo between **0°** and a calibrated, true
**90°** (see Calibration below). Every press echoes the angle *and the exact
pulse width sent* to serial at 115200, plus a heartbeat line every 10 s so the
console shows the board is alive before you touch the button.

## Calibration

A hobby servo's shaft angle is set by PWM pulse width, read back through an
internal feedback potentiometer — the motion is **continuous, not stepped by
gear teeth** — but the pulse→angle endpoints vary from unit to unit. Rather
than trust a generic 0–180° → min/max mapping, the firmware models the line
explicitly and drives the servo in microseconds:

```
pulse_us(angle) = CENTER_US + (angle - 90) * US_PER_DEG
```

- **`CENTER_US`** — the pulse that lands *this* servo at a true, square 90°.
  This is the one number worth measuring. Current value: **1485 µs**.
- **`US_PER_DEG`** — the slope, ≈ `(2400 − 500) / 180 ≈ 10.56 µs/°`. Second-
  order: it only scales corrections and sets the 0° endpoint.

Hobby servos cluster near a 1500 µs center but vary per unit, so `CENTER_US`
is tuned empirically to put *this* arm square — read off the live pulse width
the firmware logs on every press — rather than taken from a datasheet.

**To refine:** park the arm at 90° against a square (or protractor). If it's
short, raise `CENTER_US` (~10.5 µs per degree); if it's past, lower it. Each
press prints the live pulse width, so you can read off exactly what's commanded
and converge in a couple of reflashes.

## PlatformIO env

This block lives in the root `platformio.ini` (pattern matches the other envs):

```ini
[env:servo_bench]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
build_src_filter = -<*> +<../src_servo_bench/*>
lib_deps =
    madhephaestus/ESP32Servo
```

Flash from the repo root with the existing tooling: `./tools/flash.sh servo_bench`.
Serial output is captured to `logs/esp32.log` by `tools/serial_logger.py`.

## Tear-down

When you're done with the bench rig:

- `rm -rf firmware/src_servo_bench/`
- Delete the `[env:servo_bench]` block from the root `platformio.ini`

No other trace anywhere in the project.
