# Reed-bench prototype

Small standalone firmware for a spare ESP32 that prints reed-switch state to the serial console. Sole purpose: develop hands-on intuition for the reed + MCP23017 + I²C chain before any of it has to work inside the appliance.

This is **not** the production firmware. It's a throwaway rig. The firmware is [`main.cpp`](main.cpp); this README carries the wiring, intent, and tear-down.

## Bench rig

### Parts (all already in stock or in the project's BOM)

- 1× spare ESP32 dev board (ESP32-DevKitC-32E or similar)
- 1× MCP23017 module (Waveshare B07P2H1NZG — same SKU as the production unit)
- 4–5× Gebildet 14 mm reed switches (B0CW9418F6)
- 4× female-to-female Dupont jumpers (for the ESP32 ↔ MCP23017 bus)
- Hookup wire (~30 cm per reed) and crimped sockets for the reed pigtails
- Optional: heat shrink for the reed solder joints

No breadboard. No protoboard. Wires plug directly between board headers via Dupont, and reed leads are soldered to hookup wires at the reed end.

### Wiring

**ESP32 ↔ MCP23017** — four F/F Dupont jumpers, board pin to board pin:

| ESP32 pin | MCP23017 pin |
|---|---|
| `3V3` | `VCC` |
| `GND` | `GND` |
| `GPIO 21` | `SDA` |
| `GPIO 22` | `SCL` |

**MCP23017 address jumpers**: tie `A0`/`A1`/`A2` to GND for the chip's default I²C address `0x20`. On the Waveshare module the address pins are exposed on the same header as VCC/GND/SDA/SCL — check the silkscreen and jumper accordingly. `RESET` should be high (tied to VCC) — most modules already do this.

**Reeds** — for each reed:

1. Solder one lead to a ~30 cm hookup wire (the **signal** wire). Insulate the joint with heat shrink.
2. Solder the other lead to a shared **common-return** wire — daisy-chain all the reeds' "other" leads together onto a single common wire that goes to a `GND` pin on the MCP23017.
3. At the MCP23017 end of the signal wires: terminate however you like. Female Dupont sockets plug onto the module's header pins one at a time. JST-XH connectors + a short JST-to-Dupont adapter pigtail are fine if you'd rather solder JSTs. Either way, no breadboard, no protoboard.

The MCP23017's GPIO pins all support internal weak pull-up. The firmware enables those, so wiring is just **reed signal → MCP GPIO pin, reed common → GND**. No external pull-up resistors required.

Allocate signal wires to MCP23017 pins **PA0..PA(N−1)** for simplicity (the firmware reads all 16 pins anyway, so any pins work — but starting at PA0 makes the console output easy to read).

## Firmware spec

The firmware is intentionally minimal. Don't add features beyond this list. The whole file should fit on a screen.

### What `main.cpp` must do

1. **`setup()`**:
   - `Serial.begin(115200)`.
   - `Wire.begin()` using ESP32 default I²C pins (GPIO 21 SDA, GPIO 22 SCL).
   - Initialize an MCP23017 driver at I²C address `0x20`.
   - Configure all 16 GPIO pins as inputs with the chip's internal weak pull-up enabled (write `0xFFFF` to `IODIR` and `0xFFFF` to `GPPU`).
   - If the MCP23017 doesn't ACK its I²C address, print the error and keep retrying forever. Do **not** silently proceed.
   - Print one startup banner showing: I²C address in use, serial baud, pin assignment (all 16 polled), and a one-line legend: `1 = reed open, 0 = reed closed (magnet near)`.

2. **`loop()`**:
   - Read the MCP23017's `GPIO` register (both ports — 2 bytes — as a single I²C transaction).
   - Compare against the last read. On any bit change, print a console line showing the full 16-bit state plus a tag indicating which bit(s) flipped and in what direction.
   - Suggested format (final wording is the agent's call as long as it's readable):
     ```
     t=12.345  PA=1111_0000  PB=0000_1111   Δ PA0: 1→0
     ```
   - Poll interval ~10–20 ms. Reeds aren't fast and we don't want to flood serial.

### What `main.cpp` must NOT do

No WiFi. No BLE. No filesystem. No displays. No persistent log. No ratio config, no calibration, no other peripherals. No timer interrupts. No FreeRTOS task plumbing — a single `loop()` is fine. This is a "raw data in front of you" tool, not a feature-staging area for the production firmware. Resist the urge to write any of those things "since we'll need them eventually" — we'll write them properly in the production project when the time comes.

### Library

The Adafruit MCP23017 Arduino Library is the obvious pick — PlatformIO Registry name `adafruit/Adafruit MCP23017 Arduino Library`. Hand-rolled I²C is also fine if the agent prefers; three registers cover everything we need (`IODIR` at 0x00, `GPPU` at 0x0C, `GPIO` at 0x12).

## PlatformIO env

Add this block to the root `platformio.ini` at the same time the firmware code lands (it doesn't need to exist while only this README is here). Pattern matches the three existing envs (`esp32dev`, `rp2040_display`, `esp32s3_config`):

```ini
[env:reed_bench]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
build_src_filter = -<*> +<../src_reed_bench/*>
lib_deps =
    adafruit/Adafruit MCP23017 Arduino Library
```

Flash from the repo root with the existing tooling: `./tools/flash.sh reed_bench`. Open the serial monitor at 115200 baud (`pio device monitor -e reed_bench` works, or whatever `flash.sh` opens).

## Tear-down

When you're done with the bench rig and have the intuition you came for:

- `rm -rf firmware/src_reed_bench/`
- Delete the `[env:reed_bench]` block from the root `platformio.ini`

No other trace anywhere in the project.
