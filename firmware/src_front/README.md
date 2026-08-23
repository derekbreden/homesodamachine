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

- **Two framebuffers** (`num_fbs = 2`): LVGL renders the buffer that the bounce
  path is not reading. `on_frame_buf_complete` releases LVGL only after the
  driver has copied one complete source frame and selected the next one. LVGL
  runs in `direct_mode` with its two draw buffers pointed straight at the two
  panel framebuffers: flush is zero-copy, and repaint cost follows the invalidated
  area instead of filling all 800×480 pixels for every small change.
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

### Frame alignment at wake

The front links its local ESP-IDF v5.5.4 RGB driver configuration. Its scan ISR
is IRAM-safe and performs GDMA recovery only after an actual bounce-buffer EOF
shortfall or an explicit `PANEL:REALIGN`, never as routine work at each VSYNC.
The application callback wakes a high-priority task; that task writes the
panel-control expander only when the shared I2C bus is free early enough in that
blank, otherwise it retries on the next one. Bounce-buffer completion—not
VSYNC—is the boundary that releases an LVGL framebuffer for reuse.

**LCD_RST is the panel's own**, on CH422G `EXIO3`. A wake pauses the lock
animation, turns the backlight off, and holds LCD_RST low for at least 20 ms. It
releases reset in a vertical blank, allows the panel's 120 ms recovery and four
more syncs and complete frames, then raises EXIO2 (both panel DISP and the LED
driver) in a later blank. An active lock remains still for another 200 ms before
its logo continues. This keeps panel-control edges out of the visible scan without
changing the 16 MHz pixel clock or normal rendering path.

`PANEL:KICK` runs that same non-blocking sequence without waiting for idle.
`GET_PANEL` reports completed frames and submissions, wake start/completion/stage,
VSYNC-phased action/retry counts, genuine RGB scan recoveries, frame wait
timeouts, draw failures, and CH422G write failures. The live checker's
`--wake-cycles N` option repeats the actual dark-to-lit path and requires those
error counters to remain unchanged.

## Operation lock and animation

The 16-frame glass/bubbles loop (the same animation the config display uses) is
generated from the app-icon artwork at 360×360 by:

```
tools/cad-venv/bin/python tools/gen_animation_frames.py --size 360 \
    --header-dir firmware/src_front/images
```

which writes `images/anim_00.h`..`anim_15.h` (RGB565 PROGMEM). LVGL cycles them
at ~10 fps only on a full-screen operation lock: animation on the left, and a
modal naming the operation on the right. The reusable lock is the surface for
filling, cleaning and other periods in which the appliance intentionally
withholds normal interaction.

Boot opens with **Powering on · Getting everything ready.** for at least two
complete animation cycles. It then opens onto the controller's flavor selection
as soon as that state is known, with a six-second ceiling when J9 is absent.

## Build / flash

```
pio run -e esp32s3_front              # compile only
pio run -e esp32s3_front -t upload    # build + flash
```

The board enumerates over its own native USB, independent of the base ESP32's
UART bridge — flashing it does not disturb the rest of the system. If J9's V12 kept the
display powered while its USB cable was reconnected, ask the controller to make the USB
PHY detach and timer-wake:

```
~/.platformio/penv/bin/python tools/display_usb.py
```

This is only an explicit development request over J9; no boot path sends it. The 500 ms
deep sleep powers down the ESP32-S3 USB Serial/JTAG PHY without pretending the unswitched
V12 rail can be controlled. The host tool waits for a fresh `0x303A:0x1001` attachment and
then requires `GET_VERSION` to answer. An old image that lacks the J9 request needs one
physical RESET or V12 cycle before it can be upgraded.

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

After 90 s of no touch the screen sleeps — backlight off — and the first touch
turns it back on, on whatever the dark left up (see the ladder above). Normal
pages are static, and an operation-lock animation never sleeps underneath an
active operation. Same idle/wake behavior as the faucet display; the difference
is the backlight itself:

- **Nothing on this board writes NVS while the panel runs.** The 800×480 framebuffer
  lives in PSRAM (`flags.fb_in_psram`), and a flash write suspends the cache PSRAM is
  reached through, so the DMA refilling its bounce buffer faults on the next line —
  `Cache disabled but cached memory region accessed`, and the panic takes the USB PHY
  down with it (`tools/display_usb.py` brings it back). A ratio and a flavor's chosen
  logo are therefore display-local, and the durable home for both is the controller,
  where the faucet's own selection already lives.
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
- A genuinely different flavor arriving from the faucet takes the display to
  **Choose** and wakes it. Repeated publication of the flavor already shown does not
  reset the idle timer.

## USB-serial commands (bring-up / diagnostics)

Newline-terminated, 115200 baud over the native USB CDC:

- `GET_VERSION` → `VERSION:FRONT=<fw>`
- `GET_STATE` → controller-owned flavor, synchronization / durability / pending
  state, operation lock, idle and page
- `GET_DIAG` → a packet-bounded `DIAG:` health line followed by `DIAG_UI:` and
  `DIAG_SYS:` detail: page / sub-view / idle / lock, link and queue health,
  render high-water, flavor replication, touch, memory,
  backlight, animation frame and uptime
- `GET_PANEL` → completed frame/submission counts, wake stage and completion,
  VSYNC-phased panel-control actions, scan recovery, draw/frame timeouts, and CH422G
  write errors
- `BL:0` / `BL:1` → backlight off / on (drives CH422G EXIO2)
- `IDLE:0`..`IDLE:3` → wake, or take a rung of the idle ladder without waiting it out
- `PAGE:0`..`PAGE:3` → show one rail destination (CHOOSE, FILL, PRIME, CLEAN);
  `PAGE:4` → Settings, which is the corner rather than a rail slot
- `FLAVOR:0` / `FLAVOR:1` → select through the same controller-owned path as a card tap
- `EDIT:<1|2>[,<image 0..3>]` → open a flavor's own page, and take one of its logos:
  the handlers the Choose gear and a thumbnail tap reach, without a finger on the glass
- `LOCK:SHOW` / `LOCK:HIDE` → exercise the reusable operation lock
- `PANEL:KICK` → the wake sequence — dark, reset at VSYNC, four clean
  frames, light, quiet, then any active lock animation
- `PANEL:REALIGN` → request one RGB DMA recovery at the next VSYNC
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

The ROM's fixed UART0 direction is opposite the board wiring: TX43 drives the
transceiver's receiver output and RX44 samples its driver input. The ROM can neither hear
nor answer through J9. A J9 development command therefore requires the display application;
an unavailable application requires the physical RESET button or a V12 cycle.

This board's transceiver keeps its receiver off while driving: with a pin that provably
receives, `RS485:LOOP` still reads `no echo`. The base's U7 has `/RE` tied to GND and does
hear itself, and cancels that a layer below its own HDLC.

The transport is `HdlcLink` — TinyProto's framing layer, CRC16, no connection and no
keepalives. `ProtoLink`/`Fd` is what the RP2040 and S3 UARTs run; on a shared pair its
two ends collide on their own schedules and fall out of CONNECTED every 2 s.

Flavor state follows J9's controller-answer-only rule. The display sends
`MSG_FLAVOR_QUERY` every 250 ms while lit and every 500 ms while dark, with only
one request outstanding. A local card press repaints first and queues a tokenized,
absolute `MSG_FLAVOR_SELECT`; retries reuse the token and are silent. The controller
answers every query or selection with its authoritative value and persistence flags.
This polling turn also carries faucet-originated changes from J3 to this display.

## The interface

Each Choose card carries a settings target of its own beneath it — a sibling of the
card, not a child, so no press reaches the card under it — opening that flavor's page
with its ratio and a grid of every logo it could wear. Two rows of thumbnails fit
before the grid scrolls.

A 190 px rail down the left carries four 110 px targets — **CHOOSE · FILL · PRIME ·
CLEAN** — each an icon over a word. Choose is the drink; Fill, Prime and Clean are a
flavor's life in the machine, in the order it is lived. Choose uses a hand pointing up
and Fill the hopper's own funnel. Settings is not a
customer destination and holds no rail slot: it is a single square in the screen's top-right
corner, over every page, which is free because each pane titles itself from the left. The
remaining 610 px is the pane, and it takes a different shape at each destination:

| Page | Shape | Reads / writes |
|---|---|---|
| Choose | two large, quiet flavor cards with an unmistakable retained selection | **the controller**, mirrored with the faucet |
| A flavor's own page | `−`/`+` on the ratio, and every logo it can wear — reached from that flavor's Choose card, and Back returns there | display-local |
| Fill | flavor choice → confirmation | **the base** |
| Prime | flavor choice → shared hold pad | **the base** |
| Clean | flavor choice → confirmation | **the base** |

A channel is named by the logo it wears, never by a number. The three pick-a-flavor
screens offer the same artwork Choose does, full size, under the mark for what is about to
happen to it; Fill, Clean and Prime then take the same
shape behind that choice — the logo at half size, a line about what is about to happen, and
one wide target — so a channel never loses track of which one is committed. A flavor's own
page carries it at a quarter in its title band, where the ratio card and picker grid take
the room.
| Settings | a deliberately quiet surface until a useful preference is ready; reached from the corner | — |

Text is Montserrat 20 and up; 20 is the smallest font built, so nothing smaller can
render. Every page is built at boot and switching hides one and shows another. On Choose,
only the active card carries a selection badge.

**Nothing on a page is there for the person building it.** No readout reports transport,
timing or link health, and none is laid out around one — anything a bring-up needs is a
`GET_DIAG` line over USB, where it costs the interface nothing.

**The dark gives your place up in stages.** The last two run from the moment the screen
goes dark, so changing how long it stays lit does not move them.

| After | | Total absence |
|---|---|---|
| 90 s of no touch | backlight off | 90 s |
| 2 min dark | back to the root of the page you were on | 3.5 min |
| 10 min dark | back to Choose | 11.5 min |

The middle rung discards the views that would act on a tap — a confirm or a hold pad —
while keeping which area you were working in. Each rung runs while the screen is dark, so a
wake shows the answer rather than jumping to it. `IDLE:0`..`IDLE:3` walk the ladder without
waiting, and `GET_DIAG` reports `page=`, `svc=`, `flv=` and `stage=`.

**A button holds a press that slides off it.** LVGL acts on the release and re-searches
under the finger on every poll while pressed, so a press that wanders is lost — no click,
and inside a scrollable parent the wander scrolls instead. `LV_OBJ_FLAG_PRESS_LOCK` stops
the re-search per object: `mkBtn()` sets it, so put a finger on a target, slide anywhere,
lift, and that target fires. `START CLEAN CYCLE` clears it, because beginning a clean cycle
is an intentional commit.

### Prime

**PRIME → a flavor opens one shared prime-ready session.** The controller owns
its selected channel and complete `OFF` / `READY` / `RUNNING` state. The faucet wakes into
the same mode, and either display can own one held run at a time.

```
MSG_PRIME_SESSION_SET        { ACTIVATE|CANCEL, channel, sessionToken }
MSG_PRIME_SESSION_QUERY      { sessionToken }
MSG_PRIME_SESSION_HOLD_START { channel, sessionToken, holdToken }
MSG_PRIME_SESSION_HOLD_TICK  { channel, sessionToken, holdToken }
MSG_PRIME_SESSION_HOLD_STOP  { channel, sessionToken, holdToken }
MSG_RESP_PRIME_SESSION       { phase, channel, owner, outcome, elapsed,
                               revision, sessionToken, holdToken }
```

The activation token names one visit to the hold screen; every physical press gets its own
hold token. A duplicate frame is a no-op, a delayed START after its STOP cannot revive the
pump, and source identity comes from J9 or J3 rather than from a payload. The base answers
each enclosure turn with at most one complete state. `RUNNING`, `STOPPED`, `TIMEOUT`,
`LIMIT`, `REFUSED`, `CANCELED`, and `SESSION LOST` therefore mean the same thing on both
pieces of glass.

While held, a heartbeat goes out every 500 ms and the controller stops an unanswered hold
after 2 s. The enclosure renews the ready session on its 250 ms active / 500 ms dark poll;
the controller closes it after 5 s without that exact token. Elapsed text and its bar update
at 10 Hz in small invalidated regions rather than repainting the panel.

An unanswered START resets the J9 transport once and retries the same token. A lost STOP or
CANCEL is retried until exact controller state, or a strictly newer state in that same
session, proves it terminal. `GET_DIAG` reports those recovery counts and the controller's
one-reply-per-turn audit.

### Fill and clean

**FILL → a flavor → START** sends `MSG_FILL_START { channel }`, which draws that
channel from the hopper funnel on the enclosure's top face down into its chilled
reservoir. **CLEAN → a flavor → START** sends `MSG_CLEAN_START { channel }`. Both
are open-ended manifold operations the controller sequences. The valve manifold hangs
off the MCP23017s, whose pins the bench rig holds high-Z, so both answer
`MSG_ERR_UNSUPPORTED` and the pane says so.

### Frame rate

The animation runs only on the full-screen operation lock. Measured on the panel:
**~9.4 fps against the 10 fps timer**, one animation repaint ~117 ms. Choose,
Ratio, Fill, Prime, Clean, and Settings otherwise repaint only when their state changes.
`LOCK:SHOW` exposes the animation for a live check, and `GET_DIAG` reports the loop
high-water mark and clears it.

## Integration seams (not implemented)

- **Flavor ratio and level** — the ratio is this display's own until a controller stores
  it; the level reads `--` until a reservoir is sensed.
- **Dispense and carbonation state** beyond the locked-operation messages.

## Power and USB reattachment

J9 is `[B, A, GND, V12]` — this panel takes 12 V from the controller PCBA over the same
connector that carries the RS485 pair. With its own USB also plugged in it has two supplies,
and reconnecting the cable while J9 keeps the board powered can leave the USB device absent.
`J9.V12` runs straight to the board's V12 island with no switched load in its path.

[`/tools/display_usb.py`](/tools/display_usb.py) sends the explicit `display usb` development
request through the controller. The display acknowledges it, enters 500 ms of timer-wake deep
sleep, and therefore powers down the S3 USB PHY long enough for the host to observe a real
detach and fresh attachment. It does not switch V12 and nothing sends this request during a
production boot. [`/tools/boards.py`](/tools/boards.py) offers that command when it sees the
controller but not the S3.

The request requires the display application to be running and answering on J9. A missing,
old, or wedged display application still needs the panel RESET button or a physical V12 power
cycle for that boot.

## Sound

This panel has no sounder. The machine's one voice is U8 on the controller PCBA, so a finger
landing on this glass becomes a sound only by crossing J9 as `MSG_SOUND_PLAY`.

It is sent on `LV_EVENT_PRESSED`, not on the click, so the round trip hides inside the
finger's own dwell and the tick lands where the finger did rather than where it lifted.
Nothing is sent back — an ack would double the traffic in order to acknowledge a tick.
Every button on this panel is made by `mkBtn()`, so the hook lives there and nowhere else:
one place, and any button added later gets it without anyone having to remember.

The tick means **your touch registered**, not "that worked". Outcomes — refused, finished,
faulted — are the controller's own sounds. A touch that begins on a dark screen is withheld
from every widget by the wake latch, so waking the panel does not tick.

None of it reaches the gas alarm. See [`../src_appliance/README.md`](../src_appliance/README.md).
