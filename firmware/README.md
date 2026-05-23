# Firmware

The Home Soda Machine prototype runs on three microcontrollers — ESP32 (main controller), RP2040 (display), ESP32-S3 (config touchscreen + BLE bridge). The product under development reuses the same firmware base; the integrated-build hardware bring-up procedure lives in [`../hardware/assembly/firmware-and-commissioning.md`](../hardware/assembly/firmware-and-commissioning.md).

## Architecture

- **ESP32** — Main controller. Reads the flow meter, drives pumps and valves via L298N motor drivers, manages the pump state machine, stores config in LittleFS, and coordinates the other boards over UART using TinyProto (HDLC full-duplex reliable delivery).
- **RP2040** (Waveshare RP2040-LCD-0.99) — Display controller. Shows the selected flavor logo on a 128x115 round LCD. Reads the same physical toggle switch for instant visual feedback.
- **ESP32-S3** (Meshnology 1.28" Round Rotary Display) — Config display. A 240x240 round touchscreen with a rotary encoder for changing flavor images and ratios at runtime. Also serves as a BLE bridge between the iOS app and ESP32. Syncs config to the ESP32 over UART.

```
                        ┌─────────────────────┐
  Carbonated Water ───→ │ Flow Meter (GPIO 23) │
                        └──────────┬──────────┘
                                   │ pulses
  ┌───────────────┐     ┌──────────▼──────────┐
  │ ESP32-S3      │     │   ESP32 Controller   │
  │ Config Display│     │                      │
  │ 240x240 touch │◄───►│  Pump State Machine   │
  │ + encoder     │UART │  IDLE → ON → OFF ──→ │──(cycle repeats)
  │               │     │    └── COOLDOWN       │
  └───────────────┘     │    └── PRIME (via UI)  │
                        └──┬────────┬────────┬─┘
                           │        │        │
                      UART │   L298N A  L298N B
                           │   ┌────┴┐  ┌───┴──┐
                           │   │Pump1│  │Pump2 │
              ┌────────────▼┐  │Valve│  │Valve │
              │ RP2040 LCD  │  └─────┘  └──────┘
              │ 128x115 px  │
              │ flavor logo │
              └─────────────┘
```

## Pump Control

The pump doesn't just run at a fixed speed. It duty-cycles (on/off/on/off) with timing that adapts to how fast water is flowing:

| Flow Rate | On Time | Off Time | Duty Cycle |
|-----------|---------|----------|------------|
| Slow (1 pulse/50ms) | 50ms | 600ms | ~8% |
| Full (6 pulses/50ms) | 200ms | 300ms | ~40% |

This is further scaled by a per-flavor **ratio** parameter (configurable at runtime via the config display):
- Ratio 20 — tuned for SodaStream concentrates (1:20 concentrate-to-water)
- Ratio 6 — for bag-in-box syrup (traditional fountain ratio)

## Pin Assignments

### ESP32

**L298N Board A (Flavor 1):**

| Function | GPIO | Notes |
|----------|------|-------|
| ENA (pump PWM) | 33 | |
| IN1 (pump dir) | 25 | |
| IN2 (pump dir) | 26 | |
| ENB (valve on/off) | 12 | IN3/IN4 hardwired on board (IN3→5V, IN4→GND) |

**L298N Board B (Flavor 2):**

| Function | GPIO | Notes |
|----------|------|-------|
| ENA (pump PWM) | 19 | |
| IN1 (pump dir) | 18 | |
| IN2 (pump dir) | 5 | |
| ENB (valve on/off) | 4 | IN3/IN4 hardwired on board (IN3→5V, IN4→GND) |

**Inputs and Communication:**

| Function | GPIO | Notes |
|----------|------|-------|
| Flavor toggle switch | 13 | Air switch, INPUT_PULLUP |
| Flow meter | 23 | Hall effect, FALLING edge interrupt |
| Display UART TX | 32 | 115200 baud, TinyProto HDLC to RP2040 (Serial2) |
| Display UART RX | 35 | 115200 baud, TinyProto HDLC from RP2040 |
| Config UART TX | 15 | 115200 baud, TinyProto HDLC to ESP32-S3 (Serial1) |
| Config UART RX | 34 | 115200 baud, TinyProto HDLC from ESP32-S3 (input-only pin) |
| RTC SDA (DS3231) | 21 | I2C, Wire library |
| RTC SCL (DS3231) | 22 | I2C, Wire library |

**Freed GPIOs** (LEDs removed, valve IN3/IN4 hardwired): 2, 27, 17, 16. GPIOs 27 and 17 are reserved for clean cycle solenoids (L298N Board #3).

### RP2040

| Function | GPIO | Notes |
|----------|------|-------|
| Flavor toggle switch | 29 | Same physical switch as ESP32 |
| UART TX (to ESP32) | 27 | PIO-based serial, 115200 baud, TinyProto HDLC |
| UART RX (from ESP32) | 26 | PIO-based serial, 115200 baud, TinyProto HDLC |
| LCD DC | 8 | Fixed on board |
| LCD CS | 9 | Fixed on board |
| LCD CLK | 10 | Fixed on board |
| LCD DIN | 11 | Fixed on board |
| LCD RST | 13 | Fixed on board |
| LCD Backlight | 25 | Fixed on board |

### ESP32-S3 (Meshnology 1.28")

All pins are fixed by the board design.

| Function | GPIO | Notes |
|----------|------|-------|
| LCD SPI MOSI | 11 | GC9A01A, 240x240 |
| LCD SPI SCLK | 10 | |
| LCD CS | 9 | |
| LCD DC | 3 | |
| LCD RST | 14 | |
| LCD Backlight | 46 | |
| Display power 1 | 1 | Must be set HIGH |
| Display power 2 | 2 | Must be set HIGH |
| Touch SDA | 6 | CST816D, Wire1 I2C |
| Touch SCL | 7 | |
| Touch INT | 5 | |
| Touch RST | 13 | |
| Encoder CLK | 45 | |
| Encoder DT | 42 | |
| Encoder BTN | 41 | |
| RGB LEDs | 48 | WS2812 x5 (unused) |
| UART TX (J34) | 43 | 115200 baud, TinyProto HDLC to ESP32 |
| UART RX (J34) | 44 | 115200 baud, TinyProto HDLC from ESP32 |

## Inter-Board Communication

All inter-MCU communication uses [TinyProto](https://github.com/lexus2k/tinyproto) at 115200 baud with HDLC full-duplex framing. Text commands are sent inside `MSG_TEXT` messages; binary image uploads use a state-based protocol where TinyProto handles fragmentation, ACKs, and retransmission internally.

**ESP32 ↔ RP2040 (bidirectional, Serial2, GPIO 32 TX / GPIO 35 RX):**

The ESP32 pushes flavor images, label mappings, and config to the RP2040. The RP2040 sends `MSG_DEVICE_READY` at boot with its image count, triggering a full sync. The ESP32 also re-syncs periodically (every 30 seconds) as a safety net.

**ESP32 ↔ ESP32-S3 (bidirectional, Serial1, GPIO 15 TX / GPIO 34 RX):**

The ESP32-S3 config display communicates with the ESP32 to read and write runtime configuration. The ESP32 is the single source of truth; config is persisted in LittleFS. The S3 also acts as a BLE bridge, forwarding commands from the iOS app to the ESP32.

Text commands are wrapped in `MSG_TEXT` messages. On boot, the S3 sends `GET_CONFIG` until the ESP32 responds. When the user changes a value on the config display (or via the iOS app over BLE), the S3 sends `SET:` followed by `SAVE`.

```
S3 → ESP32:  GET_CONFIG
ESP32 → S3:  CONFIG:F1_RATIO=20,F2_RATIO=20,F1_IMAGE=0,F2_IMAGE=1,numImages=3

S3 → ESP32:  SET:F1_RATIO=18
ESP32 → S3:  OK:F1_RATIO=18

S3 → ESP32:  SET:F1_IMAGE=2
ESP32 → S3:  OK:F1_IMAGE=2

S3 → ESP32:  SET:F1_RATIO=30
ESP32 → S3:  ERR:F1_RATIO out of range

S3 → ESP32:  SAVE
ESP32 → S3:  OK:SAVED              (persists to LittleFS)
```

Valid keys and ranges: `F1_RATIO` (6-24), `F2_RATIO` (6-24), `F1_IMAGE` (0-NUM_IMAGES-1), `F2_IMAGE` (0-NUM_IMAGES-1). The same text commands work over USB serial (115200 baud) for testing.

Boot order does not matter. The S3 retries `GET_CONFIG` until the ESP32 is ready. Both the RP2040 and S3 send `MSG_DEVICE_READY` at the end of their `setup()`, and the ESP32 uses this to trigger initial sync.

## Building and Flashing

This is a [PlatformIO](https://platformio.org/) project with three build environments. The wrapper `./tools/flash.sh <env>` handles each one — envs are `esp32dev`, `rp2040_display`, `esp32s3_config`. The underlying PlatformIO commands work directly too:

### Flash the ESP32 (main controller)

```bash
pio run -e esp32dev -t upload
```

### Flash the RP2040 (display)

```bash
pio run -e rp2040_display -t upload
```

The RP2040 uses the [earlephilhower Arduino core](https://github.com/earlephilhower/arduino-pico) and the [GFX Library for Arduino](https://github.com/moononournation/Arduino_GFX) for the GC9107 LCD driver.

### Flash the ESP32-S3 (config display)

```bash
pio run -e esp32s3_config -t upload
```

The ESP32-S3 uses the [pioarduino platform](https://github.com/pioarduino/platform-espressif32) for Arduino core 3.x support, [LVGL v8.4](https://github.com/lvgl/lvgl) for the UI, and the [GFX Library for Arduino](https://github.com/moononournation/Arduino_GFX) for the GC9A01A display driver. A custom 64px Montserrat font (`src_config/font_ratio_64.h`) is used for the ratio edit screen.

### Adding a New Flavor Image

Flavor images can be uploaded at runtime from the iOS app over BLE. The iOS app resizes images to the correct dimensions (128x115 for RP2040, 240x240 for S3), converts them to RGB565 format, and uploads them over the framed BLE/UART protocol. Images are stored in LittleFS on each device and survive power cycles.

Factory default images are compiled into the ESP32 firmware via `board_build.embed_txtfiles` and pushed to devices on first boot.

**Adding a new factory default image:**

1. Place the source PNG in `tools/` and run `python tools/png_to_rgb565.py` to generate RGB565 binary files
2. Add the binary files to `data/` for LittleFS upload
3. Update the factory defaults configuration

## Configuration

### Runtime Config (via iOS App, Config Display, or USB Serial)

Flavor ratios and display image assignments are stored in the ESP32's LittleFS filesystem and can be changed at runtime using the ESP32-S3 config display, the iOS app (over BLE), or by sending commands over USB serial:

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| F1_RATIO | 6-24 | 20 | Flavor 1 concentrate-to-water ratio (lower = stronger) |
| F2_RATIO | 6-24 | 20 | Flavor 2 concentrate-to-water ratio |
| F1_IMAGE | 0-N | 0 | Flavor 1 display image index (images uploadable via iOS app) |
| F2_IMAGE | 0-N | 1 | Flavor 2 display image index |

To change config over USB serial (115200 baud), connect to the ESP32 and send text commands like `SET:F1_RATIO=18` followed by `SAVE`. Send `GET_CONFIG` to see current values.

### Compile-Time Tuning

These control the pump duty cycle shape and generally don't need adjustment. They are `#define`s at the top of `firmware/src/main.cpp`:

```cpp
#define PUMP_ON_MIN_MS     50    // minimum pump on-time
#define PUMP_OFF_MAX_MS  1000    // maximum pump off-time
#define SHAPE_ON_BASE     20     // base on-time at minimum flow
#define SHAPE_ON_SLOPE    30     // on-time increase per flow pulse
#define SHAPE_OFF_BASE   660     // base off-time at minimum flow
#define SHAPE_OFF_SLOPE   60     // off-time decrease per flow pulse
```
