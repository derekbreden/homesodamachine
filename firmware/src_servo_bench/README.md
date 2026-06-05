# Servo-bench prototype

Small standalone firmware for a spare ESP32: press a button, an MG90S servo
sweeps 90° and then releases — a bench stand-in for actuating a quarter-turn
valve. Sole purpose: confirm the button + servo + ESP32 chain (and the
drive-then-release pattern) before any of it has to work inside the appliance.
Sibling of
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

Each button press drives the servo through a calibrated **90° of travel** (rest
→ actuated and back; see Calibration below), then — after a ~500 ms settle delay
— **detaches the servo so it goes limp**. This models actuating a quarter-turn
valve: drive it to on/off, then let go. A manual ball valve holds its own
position, so the servo never sits **stalled against the valve's end stop** (a
sustained stall is heat, current, and wear), and it draws ~zero current between
actuations — asleep the 99.99 % of the time it isn't moving.

Both the move *and* the release are echoed to serial at 115200, plus a 10 s
heartbeat reporting whether the servo is currently `holding` or `released
(limp)`. The settle delay must cover the worst-case travel time; if a loaded
valve moves slowly, raise `SETTLE_MS`.

## Calibration

What's calibrated here is the **travel** — a true 90° of swept arc between the
two positions — *not* where either endpoint points in absolute space. A hobby
servo's shaft angle is a linear function of PWM pulse width (continuous, **not
stepped by gear teeth**), so the firmware anchors a rest pulse and adds a
per-degree slope, driving the servo in microseconds:

```
pulse_us(angle) = REST_US + angle * US_PER_DEG
```

- **`US_PER_DEG`** — the servo's **real** microseconds per degree, and the one
  knob that sets travel: `span = (ANGLE_B − ANGLE_A) × US_PER_DEG`. The generic
  `(2400 − 500) / 180 ≈ 10.56 µs/°` undershoots badly on this unit (90°
  commanded sweeps visibly less than 90°), so it's tuned up against the observed
  arc. Current value: **12.32 µs/°** (≈ 1109 µs of span for 90°).
- **`REST_US`** — pulse at the rest position. Sets only *where* the sweep sits,
  which is irrelevant here; pick any safe value. Current: **1000 µs**.

**To refine:** if the swept arc is short of 90°, raise `US_PER_DEG`; if it
overshoots, lower it. The value is bracketed — a 950 µs span fell short, the old
1267 µs span overshot — so a couple of reflashes bisect it. Each press logs the
live pulse width, so you can read the exact span being commanded.

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
