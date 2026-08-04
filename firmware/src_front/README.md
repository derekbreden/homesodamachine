# Front-Face Display (Waveshare ESP32-S3-Touch-LCD-4.3B)

Foundation firmware for the appliance's front-face display: it brings up the
RGB panel and LVGL and runs the animated loading logo centered on the theme
background (`0x1a1a2e`). The interaction UX is not built yet — this is the
panel bring-up and the structure to grow it on.

## Board

[Waveshare ESP32-S3-Touch-LCD-4.3B](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3B)
— 4.3" 800×480 IPS RGB parallel panel (ST7262-class), GT911 capacitive touch,
CH422G I/O expander, ESP32-S3-WROOM-1-N16R8 (16 MB flash / 8 MB octal PSRAM).
Native USB (`0x303A:0x1001`); 7–36 V screw-terminal input off the 12 V bus.

## Rendering (tear-free)

This panel has no display controller — the ESP32-S3 streams every pixel out of
a PSRAM framebuffer by DMA, continuously. Naively writing that framebuffer
while it is being scanned (e.g. an animation) makes the scan-out DMA contend
with the CPU on the one PSRAM bus; the scanline FIFO starves and the image
shears (horizontal bands shift sideways). So the panel is driven through
`esp_lcd` directly (not Arduino_GFX, which only does a single framebuffer) with
two defenses:

- **Two framebuffers** (`num_fbs = 2`): LVGL renders the back buffer while the
  panel scans the front, and `esp_lcd` page-flips at the vertical blank — the
  DMA never reads a buffer being written, so there is no content tearing. LVGL
  runs in `full_refresh` mode with its two draw buffers pointed straight at the
  two panel framebuffers (zero-copy flush).
- **Bounce buffer** (`bounce_buffer_size_px = width × 10`): the scan-out DMA
  reads from a small internal-SRAM buffer refilled from PSRAM in the
  background, so PSRAM write bursts can't starve the live scanline — this is
  what removes the shearing.

The two 800×480 RGB565 framebuffers (~1.5 MB) live in PSRAM, so OPI PSRAM is
mandatory — the `esp32-s3-devkitc1-n16r8` board def in `platformio.ini` enables
it (`memory_type = qio_opi`, `-DBOARD_HAS_PSRAM`). The animation frames are
compiled into flash (~4 MB of `.rodata`), which overflows the shared 4 MB app
slot, so this env uses `firmware/partitions_s3_front.csv` (16 MB layout, large
app partition). The panel is initialized on a watchdog'd background task: if
`esp_lcd` ever blocks, `setup()` times out and `loop()` keeps serial alive, so
the board stays flashable without a manual BOOT-button recovery.

## Loading animation

The 16-frame glass/bubbles loop (the same animation the config display uses) is
generated from the app-icon artwork at 360×360 by:

```
tools/cad-venv/bin/python tools/gen_animation_frames.py --size 360 \
    --header-dir firmware/src_front/images
```

which writes `images/anim_00.h`..`anim_15.h` (RGB565 PROGMEM). LVGL cycles them
at ~10 fps.

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

## Idle backlight-off + touch

After 60 s of no touch the screen sleeps — backlight off, animation paused — and
the first touch turns it back on and resumes. Same idle/wake behavior as the
faucet display; the difference is the backlight itself:

- The faucet fades its backlight with PWM. This board's backlight is a *digital*
  line on the CH422G (EXIO2) — on/off only, no PWM, and I²C is too slow to fake
  it. So the idle state is a clean backlight-off (which genuinely cuts panel
  power), not a rendered dim. Instant off, instant on.
- Touch is the GT911 on the shared I²C bus. Its address (`0x5D`/`0x14`) depends
  on reset timing, so it's probed at init; reset is released via CH422G EXIO1,
  INT is GPIO4. It's registered as an LVGL pointer indev, so it's ready for the
  real UX, not just wake. The first touch while idle is consumed (wake only).

## USB-serial commands (bring-up / diagnostics)

Newline-terminated, 115200 baud over the native USB CDC:

- `GET_VERSION` → `VERSION:FRONT=<fw>`
- `GET_DIAG` → heap / PSRAM / backlight / frame / GT911 addr / touch count /
  idle state / loop high-water / uptime
- `BL:0` / `BL:1` → backlight off / on (drives CH422G EXIO2)
- `IDLE:0` / `IDLE:1` → wake / force the idle state (test without the 60 s wait)
- `RS485:<text>` → send a line to the base (e.g. `RS485:ping`, `RS485:pump a 60 1`)
- `RS485:SWAP` → exchange the RX/TX GPIO and report which way round it now runs

## RS485 link to the base ESP32 (J9 / SIG-7)

The onboard SP3485 is on **GPIO43/44** at 115200 8N1, wired to the pcba's **J9**
(`B · A · GND · V12`) — the same 4-wire loom carries the pair and the 7–36 V input.
Direction switching is automatic at both ends, so there is no DE line; the board's own
120 Ω termination is a DIP switch, off as shipped, and the base carries R6 across the
pair.

Both transceivers receive while they drive, so a transmitted byte lands back in the
sender's own RX. `rs485Send()` reads off exactly what it wrote.

GPIO43/44 are U0TXD/U0RXD, so the ROM and 2nd-stage bootloader print on this bus at every
reset of this board.

Waveshare's table reads GPIO43 `RS485_RXD`, GPIO44 `RS485_TXD`. `RS485:SWAP` over USB
exchanges the two and reports which way round it is running.

Lines arriving from the base go to the status label and the USB console. `PING` is
answered `PONG`.

## Bench button

One `RUN PUMP A` button under the logo sends `pump a 60 1` — the base console's bounded
hold, pump A at 60% for one second. The base replies `OK:pump a 60 1` when the run has
finished, and that reply is what the status label shows.

## Integration seams (not implemented)

- **State sync and config push** over the link above.
