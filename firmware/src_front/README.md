# Front-Face Display (Waveshare ESP32-S3-Touch-LCD-4.3B)

Foundation firmware for the appliance's front-face display: it brings up the
RGB panel and LVGL and shows the loading logo centered on the theme
background (`0x1a1a2e`). The interaction UX is not built yet — this is the
panel bring-up and the structure to grow it on.

## Board

[Waveshare ESP32-S3-Touch-LCD-4.3B](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3B)
— 4.3" 800×480 IPS RGB parallel panel (ST7262-class), GT911 capacitive touch,
CH422G I/O expander, ESP32-S3-WROOM-1-N16R8 (16 MB flash / 8 MB octal PSRAM).
Native USB (`0x303A:0x1001`); 7–36 V screw-terminal input off the 12 V bus.

The 800×480 RGB565 framebuffer (~768 KB) lives in PSRAM, so OPI PSRAM is
mandatory — the `esp32-s3-devkitc1-n16r8` board def in `platformio.ini`
enables it (`memory_type = qio_opi`, `-DBOARD_HAS_PSRAM`). Arduino_GFX must be
≥ 1.5.7 for RGB-panel support on the arduino-esp32 v3.x core this repo uses.

## Build / flash

```
./tools/flash.sh esp32s3_front build   # compile only
./tools/flash.sh esp32s3_front         # build + flash
```

The board enumerates over its own native USB, independent of the base ESP32's
UART bridge — flashing it does not disturb the rest of the system.

## Pin map (fixed by the board)

Verified against the Waveshare wiki, the Arduino_GFX board example, and a
working ESPHome config. Several RGB lines are ESP32-S3 strapping/special pins
(GPIO0/3/45/46) committed to the panel — do not repurpose them.

| Function | GPIO |
|---|---|
| RGB DE / VSYNC / HSYNC / PCLK | 5 / 3 / 46 / 7 |
| R0–R4 | 1, 2, 42, 41, 40 |
| G0–G5 | 39, 0, 45, 48, 47, 21 |
| B0–B4 | 14, 38, 18, 17, 10 |
| Shared I²C (SDA / SCL) | 8 / 9 |
| Touch INT (GT911) | 4 |

Panel timings: HSYNC fp/pw/bp = 40/48/88, VSYNC fp/pw/bp = 13/3/32, both
polarities 0, `pclk_active_neg=1`, prefer 16 MHz.

### CH422G I/O expander

The backlight and both resets hang off the expander, so the panel stays dark
until they are driven. The CH422G is *not* a normal single-register expander:
each "register" is its own 7-bit I²C address and takes one bare data byte (no
register pointer). Write `0x01` to `0x24` to make EXIO0–7 push-pull outputs,
then write the output byte to `0x38` where `EXIO_n = bit n`.

| EXIO | Line |
|---|---|
| EXIO1 | TP_RST (GT911 touch reset) |
| EXIO2 | DISP — LCD backlight enable |
| EXIO3 | LCD_RST (RGB panel reset) |
| EXIO4 | SD_CS (microSD; held high = deselected) |

## USB-serial commands (bring-up / diagnostics)

Newline-terminated, 115200 baud over the native USB CDC:

- `GET_VERSION` → `VERSION:FRONT=<fw>`
- `GET_DIAG` → heap / PSRAM / backlight / loop high-water / uptime
- `BL:0` / `BL:1` → backlight off / on (drives CH422G EXIO2)

## Integration seams (not implemented)

- **Touch** — GT911 on the shared I²C bus (addr `0x5D`, INT on GPIO4, reset
  already released via CH422G EXIO1). Register an LVGL pointer indev here.
- **Base-ESP32 link** — this board is the front-face config + interaction
  surface; it connects to the base ESP32 over RS485 (SIG-7). State sync and
  config push plug into `loop()`.
