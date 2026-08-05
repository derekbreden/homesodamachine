# Front-Face Display (Waveshare ESP32-S3-Touch-LCD-4.3B)

The appliance's front-face display: an RGB panel under LVGL, showing a rail of five
pages down the left edge and a pane to their right.

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
- Bit 7 of `0x814E` is raised when the GT911 has a new frame and cleared by reading it.
  Between frames the last one stands, so a poll finding the flag clear answers with the
  state it last read, and a lift must be reported for 150 ms before it reaches a widget —
  a tap needs one PRESSED sample, a hold needs every poll it spans. `GET_DIAG` counts
  these as `stale=` and `bridged=`.

## USB-serial commands (bring-up / diagnostics)

Newline-terminated, 115200 baud over the native USB CDC:

- `GET_VERSION` → `VERSION:FRONT=<fw>`
- `GET_DIAG` → page / holding / link reinits / unanswered polls / bridged touch polls /
  stale GT911 polls / last send error / heap / PSRAM / backlight / frame / GT911 addr /
  touch count / last XY / idle state / loop high-water / uptime
- `BL:0` / `BL:1` → backlight off / on (drives CH422G EXIO2)
- `IDLE:0` / `IDLE:1` → wake / force the idle state (test without the 60 s wait)
- `PAGE:0`..`PAGE:4` → show one page (HOME, FLAVOR, SERVICE, STATUS, SETUP)
- `PRIME:START:<1|2>` / `PRIME:STOP` → the pad's own handlers, without a finger on
  the glass: same frames, same ticks, same readouts
- `STATUS` → ask the base for one `StatusPayload`
- `PUMP` → one `MSG_PUMP_RUN { B, 1000 }`
- `LINK` → RX/TX GPIO and the frame counters
- `RS485:<text>` → send text to the base as `MSG_TEXT`
- `RS485:SWAP` → exchange the RX/TX GPIO and report which way round it now runs
- `RS485:LOOP` → transmit and report whatever returns on this board's own receiver
- `RS485:RAW` → print the UART's bytes for 4 s, below HDLC
- `RS485:REINIT` → release both pads and bring the link up again

## RS485 link to the base ESP32 (J9 / SIG-7)

The onboard SP3485 is on **GPIO43/44** at 115200 8N1, wired to the pcba's **J9**
(`B · A · GND · V12`) — the same 4-wire loom carries the pair and the 7–36 V input.
Direction switching is automatic at both ends, so there is no DE line; the board's own
120 Ω termination is a DIP switch, off as shipped, and the base carries R6 across the
pair.

GPIO43 is U0TXD and the bootloader leaves UART0 holding the pad. UART1 maps it as its RX
all the same and then reads the pad's own driver rather than the transceiver — `RS485:RAW`
logs zero bytes across a window the base is transmitting in. `j9Begin()` calls
`gpio_reset_pin()` on both pads first, and the same window then logs the whole frame:
`7E 16 01 8F DF 7E` — flag, `MSG_RESP_PUMP_DONE`, channel 1, CRC16, flag.

This board's transceiver keeps its receiver off while driving: with a pin that provably
receives, `RS485:LOOP` still reads `no echo`. The base's U7 has `/RE` tied to GND and does
hear itself, and cancels that a layer below its own HDLC.

The transport is `HdlcLink` — TinyProto's framing layer, CRC16, no connection and no
keepalives. `ProtoLink`/`Fd` is what the RP2040 and S3 UARTs run; on a shared pair its
two ends collide on their own schedules and fall out of CONNECTED every 2 s.

## The interface

A 190 px rail down the left carries five 82 px targets — **HOME · FLAVOR · SERVICE ·
STATUS · SETUP** — each an icon over a word, with a J9 indicator in its foot. The
remaining 610 px is the pane, and it takes a different shape on each page:

| Page | Shape | Reads / writes |
|---|---|---|
| HOME | the loading animation, a headline, both ratios | display-local |
| FLAVOR | two cards → one card's detail, with `−`/`+` on the ratio | display-local; level `--` |
| SERVICE | PRIME \| CLEAN → a flavor → the hold pad or the confirm | **the base** |
| STATUS | four tiles and a bar, polled every 2 s | **the base** |
| SETUP | a paged column of read-outs and one restart | display-local, plus the base's build |

Text is Montserrat 20 and up; 20 is the smallest font built, so nothing smaller can
render. Every page is built at boot and switching hides one and shows another.

Waking from idle lands on HOME with every drill-down reset.

**A press reports the point it began at, for its whole length.** LVGL acts on the release,
and a release that has wandered off the pressed object is a press lost — no click, and on a
scrollable parent the wander scrolls instead. So the indev holds the first point: put a
finger on a target, slide anywhere, lift, and that target is what fires. Nothing on this
panel is dragged, which is why SETUP scrolls by button rather than by finger.

**SETUP scrolls a page at a time.** A track between an UP and a DOWN target, each 92×104,
each dim and unanswering at its end of the travel; the thumb sizes itself to the viewport's
share of the whole. One press moves 340 px with no animation — a frame of one would repaint
the whole 800×480.

Nothing on SETUP changes how the appliance behaves. It carries builds, link and touch
counters, memory, loop high-water, uptime, and a restart.

### Prime

**SERVICE → PRIME → a flavor → hold the pad.** Three taps, then the finger stays down.

```
MSG_PRIME_START { channel }      finger down
MSG_PRIME_TICK  { channel }      every 500 ms while it stays down
MSG_PRIME_STOP  { channel }      lift, or the finger slides off the pad
```

The base drives the pump at full power and answers `MSG_RESP_PRIME { state, channel, ms }`
on every state change — `RUNNING`, `STOPPED`, `TIMEOUT` when a tick runs later than 2 s,
`LIMIT` at the 60 s ceiling, `REFUSED` when something else has the pump. The pad shows
elapsed seconds against a bar scaled to that ceiling.

A tick goes out every ~550 ms in practice: the hold view repaints its readout at 10 Hz and
one repaint of this panel takes ~110 ms, so the 500 ms check lands a loop late.

A `MSG_PRIME_START` with no answer inside 700 ms resets both pads, restarts `Serial1` and
sends one more START — the pad reads "link reset — retrying" and the hold carries on under
the finger. Three unanswered status polls do the same between holds. `GET_DIAG` counts
them as `reinits=`.

### Clean

**SERVICE → CLEAN → a flavor → START** sends `MSG_CLEAN_START { channel }`. The valve
manifold hangs off the MCP23017s, whose pins the bench rig holds high-Z, so it answers
`MSG_ERR_UNSUPPORTED` and the pane says so.

### Frame rate

The animation runs on HOME and is paused everywhere else. Measured on the panel with the
rail up: **~9.4 fps against the 10 fps timer**, one full-screen repaint ~117 ms. FLAVOR,
FLAVOR and SERVICE sit at `maxLoopMs=0` — nothing on them invalidates, so nothing repaints;
STATUS and SETUP take one repaint a second for their read-outs. `GET_DIAG` reports the
high-water mark and clears it.

## Integration seams (not implemented)

- **Flavor ratio and level** — the ratio is this display's own until a controller stores
  it; the level reads `--` until a reservoir is sensed.
- **Dispense and carbonation state** on HOME.
