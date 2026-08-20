# Firmware

Seven source trees, each its own PlatformIO environment in [`/platformio.ini`](/platformio.ini), each running on its own board.

| Tree | Env | Runs on | Machine |
|---|---|---|---|
| `src_appliance/` | `appliance` | the controller PCBA's WROOM (U1) | the appliance |
| `src_pcba_bench/` | `pcba_bench` | the controller PCBA's WROOM (U1) | none — a bare board on the bench |
| `src_front/` | `esp32s3_front` | Waveshare ESP32-S3-Touch-LCD-4.3B | the appliance |
| `src_faucet/` | `esp32s3_faucet` | Waveshare ESP32-S3-Touch-LCD-1.47 | the appliance, and the prototype |
| `src_prototype/` | `prototype` | an ESP32 dev module on L298N drivers | the prototype under the counter |
| `src_config/` | `esp32s3_config` | Meshnology 1.28" round rotary display | the prototype under the counter |
| `src_display/` | `rp2040_display` | Waveshare RP2040-LCD-0.99 | the prototype under the counter |

Two of them run on the controller PCBA, and only one of the two ships inside a machine.

**`src_appliance/` is the appliance's own firmware** — the state machine, the thermal loop, the dispense, persistence, the links to both displays ([`src_appliance/README.md`](src_appliance/README.md)). It boots to the state [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) opens against — build ID printed, every actuator parked dark — and brings up J9. What runs today is one flavor pump: a prime held from the 4.3B's glass, and `pump <a|b> [ms]` bounded from the console. `machine.cpp` owns every pin that reaches a load and the three constraints below are held there; `link.cpp` turns a J9 frame into a call on it. The two MCP23017s are untouched, so the eleven valves and the condenser fan stay high-Z and no reed is read — a clean cycle is answered `MSG_ERR_UNSUPPORTED`. The procedure it fills in is [`/hardware/assembly/firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md) §3, §6, §7 and §9; the pin map is [`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), drawn as [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd).

Two shared libraries sit under `lib/`, compiled into whichever trees include them:
[`lib/proto_link`](lib/proto_link/proto_msg.h) is the J9 wire contract, and
[`lib/sound`](lib/sound/sound.h) is U8 — the drive on IO13, the machine's sound vocabulary,
and the volume/quiet-hours settings behind it. The appliance and the bench share that one
table on purpose: a board on the line makes exactly the sounds a customer's machine makes.
Neither display carries a sounder, so every sound the machine makes is made on the PCBA.

`src_pcba_bench/` is the bench rig for a **bare** board, one board per fab batch, and goes no further than the bench. It answers whether the fab built what [`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx) describes — it reads every device, and behind `arm` it drives both relays, both DRV8870 pumps and the buzzer, one output at a time for 120 s so each can be metered at its connector. It also carries the buzzer's range — `ladder`, `duty`, `palette`, played once at boot — which is where the machine's alarms and acks get designed ([`src_pcba_bench/README.md`](src_pcba_bench/README.md)). It never writes `IODIR` or `GPPU` on either MCP23017, so the ten manifold valves, V-K and the condenser fan — everything behind the two expanders — stay dark, and no reed is ever read on a pull-up. It answered batch 2 on the bench: [`/hardware/pcb/pcba/bench-log.md`](/hardware/pcb/pcba/bench-log.md).

## What the appliance firmware must hold

Three constraints the board and the supply impose, each carried by a part that pays for a violation. They are in [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md) §9 as well, where the factory confirms them per unit.

- **At most 3 solenoid valves energized at once.** Eight coils on MANIFOLD A draw 2.4–3.7 A through J1's `COM` contact, rated ~3 A, and dissipate it in one SOIC-18 (U4). The canonical valve states open at most three ([`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md)); the ceiling is [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Solenoid COM current budget".
- **Relay #2 (`IO2`) off while a dispense is open.** The board peaks at 3.33 A and the SeaFlo diaphragm pump at 5 A on the same 12 V rail — 8.32 A together, against a 6.7 A supply. The carbonator's low reed asserts mid-pour, so the refill it queues waits for the dispense window to close ([`/hardware/assembly/acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) step 5). Nothing in hardware enforces this.
- **`GPPU` written on both MCP23017s.** No loom carries a resistor and the board pulls none of the reed inputs ([`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), U2 GPB4-7 / U3 GPB6-7), so every reed reads its expander's internal pull-up or floats.

## Appliance displays

- **ESP32-S3 front-face display** (Waveshare ESP32-S3-Touch-LCD-4.3B) — The appliance front-face config + interaction surface: a 4.3" 800×480 RGB capacitive touchscreen (GT911, CH422G I/O expander) angled up toward a standing user, linked to the base ESP32 over RS485. `src_front/` brings up the RGB panel (driven through esp_lcd with a double framebuffer + bounce buffer for tear-free output) + LVGL, runs the animated loading logo on the theme background, and carries the RS485 link to the base on GPIO43/44 as typed TinyProto frames ([`proto_msg.h`](lib/proto_link/proto_msg.h)). Service → Prime → a flavor → hold the pad sends `MSG_PRIME_START` and a tick every 500 ms under the finger; the base answers `MSG_RESP_PRIME` on every state change. The interaction UX is the seam that remains. See [`src_front/README.md`](src_front/README.md).
- **ESP32-S3 faucet display** (Waveshare ESP32-S3-Touch-LCD-1.47) — Flavor selector on the gooseneck dispense head, on both machines. The selected flavor's logo fills a 172x320 capacitive-touch LCD; a tap anywhere toggles between the two flavors, and the selection persists in NVS. After a minute idle the backlight fades to an ember level; the first touch wakes it without toggling. Standalone for now — the UART/TinyProto link to the base ESP32 (flavor-state sync, names/artwork push) is the integration seam marked in `src_faucet/main.cpp`.

The config UX the 4.3B carries in the appliance is the prototype's rotary-display UX below, and porting it is a pending integration seam.

## Prototype architecture

The machine under the counter: one ESP32 on L298N drivers, with the RP2040 and the 1.28" S3 hanging off it over TinyProto.

- **ESP32** — Main controller. Reads the flow meter, drives pumps and valves via L298N motor drivers, manages the pump state machine, stores config in LittleFS, and coordinates the other boards over UART using TinyProto (HDLC full-duplex reliable delivery).
- **RP2040** (Waveshare RP2040-LCD-0.99) — Display controller. Shows the selected flavor logo on a 128x115 round LCD. Reads the same physical toggle switch for instant visual feedback.
- **ESP32-S3** (Meshnology 1.28" Round Rotary Display) — Config display. A 240x240 round touchscreen with a rotary encoder for changing flavor images and ratios at runtime. Also serves as a BLE bridge between the iOS app and ESP32. Syncs config to the ESP32 over UART.

```
                        ┌─────────────────────┐
  Carbonated Water ───→ │ Flow Meter (GPIO 15) │
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

The assignments below are `src_prototype/`'s, plus the three displays'. The appliance board's pin map is [`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), drawn as [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) — a different ESP32 on different pins, with the compressor relay, condenser fan, MQ-6, reed level sensing, moisture sensor and both MCP23017 expanders the prototype has none of.

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
| Flow meter | 15 | Hall effect, FALLING edge interrupt |
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

### ESP32-S3 Faucet Display (Waveshare ESP32-S3-Touch-LCD-1.47)

All pins are fixed by the board design.

| Function | GPIO | Notes |
|----------|------|-------|
| LCD SPI MOSI | 39 | JD9853, 172x320 — ST7789 command set + panel init sequence |
| LCD SPI SCLK | 38 | |
| LCD CS | 21 | |
| LCD DC | 45 | |
| LCD RST | 40 | |
| LCD Backlight | 46 | |
| Touch SDA | 42 | AXS5106L, Wire I2C, addr 0x63 |
| Touch SCL | 41 | |
| Touch INT | 48 | FALLING edge per touch report |
| Touch RST | 47 | |
| BOOT button | 0 | |

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

Every environment in [`/platformio.ini`](/platformio.ini) builds with `pio run -e <env>` and flashes with `-t upload`. `firmware/pre_build.py` runs first on all of them, stamping `fw_version.h` from the git rev so a board reports the commit it was built from.

**With more than one board on USB, name the port.** PlatformIO picks one otherwise, and it picks the S3 — esptool opens that port, drops the display into download mode, and only then fails on the chip id, leaving the panel dark until it is reflashed ([`/hardware/pcb/pcba/bench-log.md`](/hardware/pcb/pcba/bench-log.md)).

[`tools/boards.py`](/tools/boards.py) says which board is on which port and prints the commands with the ports already filled in. It only enumerates — it never opens a port, because opening one drives the PCBA's Q2/Q3 auto-reset lattice and reboots the board.

```bash
~/.platformio/penv/bin/python tools/boards.py
```

**A display reconnected to USB does not come back until the BOARD is power-cycled.** J9 is `[B, A, GND, V12]`: the display is fed 12 V from the PCBA over the same connector as the RS485 pair, so a display on USB has two supplies, and reconnecting one while the other stands leaves it enumerated on neither. `J9.V12` runs straight to the V12 island with no relay in it — nothing in firmware can drop it, and resetting the ESP32 is not enough. Unplug the 12 V at J10 (or at the wall), wait a moment, plug it back in. `tools/boards.py` says so too when it finds a controller and no S3.

```bash
PLATFORMIO_UPLOAD_PORT=/dev/cu.usbserial-10 pio run -e appliance -t upload
```

### Flash the appliance controller

```bash
pio run -e appliance -t upload
```

See [`src_appliance/README.md`](src_appliance/README.md) for its console.

### Flash that board's bring-up console instead

```bash
pio run -e pcba_bench -t upload
```

For a bare board on the bench, not an assembled machine. See [`src_pcba_bench/README.md`](src_pcba_bench/README.md) for its command table.

Both go over a plain USB-C cable into J14; the on-board CH340C bridges and Q2/Q3 auto-reset, so no button presses.

### Flash the ESP32-S3 (4.3B front-face display)

```bash
pio run -e esp32s3_front -t upload
```

### Flash the prototype's ESP32

```bash
pio run -e prototype -t upload
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

### Flash the ESP32-S3 (faucet display)

```bash
pio run -e esp32s3_faucet -t upload
```

Same platform and LVGL stack as the config display. The JD9853 panel is driven through the GFX library's ST7789 driver plus a panel-specific init sequence; the AXS5106L touch driver lives in `src_faucet/axs5106l.cpp`. The display renders 180° rotated — the USB connector points up on the faucet mount. Test commands over USB serial (115200 baud): `GET_STATE`, `TOGGLE`, `FLAVOR:n`, `GET_DIAG`, `BL:n` (raw backlight duty), `GET_VERSION`.

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

These control the pump duty cycle shape and generally don't need adjustment. They are `#define`s at the top of `firmware/src_prototype/main.cpp`:

```cpp
#define PUMP_ON_MIN_MS     50    // minimum pump on-time
#define PUMP_OFF_MAX_MS  1000    // maximum pump off-time
#define SHAPE_ON_BASE     20     // base on-time at minimum flow
#define SHAPE_ON_SLOPE    30     // on-time increase per flow pulse
#define SHAPE_OFF_BASE   660     // base off-time at minimum flow
#define SHAPE_OFF_SLOPE   60     // off-time decrease per flow pulse
```
