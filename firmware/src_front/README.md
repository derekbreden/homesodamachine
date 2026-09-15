# Enclosure Display (Waveshare ESP32-S3-Touch-LCD-4.3B)

The appliance's enclosure display: Big Blue on an 800×480 RGB panel under LVGL.
Both flavors stay in the left rail; the selected portrait and task occupy the rest.

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

- **Two framebuffers** (`flags.double_fb`, which is what the driver reads —
  `num_fbs = 2` is set beside it and validated against it): LVGL renders the
  buffer that the bounce path is not reading. `on_frame_buf_complete` releases LVGL only after the
  driver has copied one complete source frame and selected the next one. LVGL
  runs in `direct_mode` with its two draw buffers pointed straight at the two
  panel framebuffers: flush is zero-copy, and repaint cost follows the invalidated
  area instead of filling all 800×480 pixels for every small change.
- **Bounce buffer** (`bounce_buffer_size_px = width × 10`): the scan-out DMA
  reads from two small internal-SRAM buffers, ping-ponged and refilled from
  PSRAM in the background, so PSRAM write bursts can't starve the live scanline
  — this is what removes the shearing. 800 × 10 px at 16 bpp is 16,000 B each,
  and 48 of them span one frame.

The two 800×480 RGB565 framebuffers (~1.5 MB) live in PSRAM, so OPI PSRAM is
mandatory — the `esp32-s3-devkitc1-n16r8` board def in `platformio.ini` enables
it (`memory_type = qio_opi`, `-DBOARD_HAS_PSRAM`). `firmware/partitions_s3_front.csv`
is the 16 MB layout: two app slots and the `art` partition the animation is
mapped out of. The panel is initialized on a watchdog'd background task: if
`esp_lcd` ever blocks, `setup()` times out and `loop()` keeps serial alive, so
the board stays flashable without a manual BOOT-button recovery.

### Frame alignment at wake

[`esp_lcd_panel_rgb_local.c`](esp_lcd_panel_rgb_local.c) is a copy of the ESP-IDF v5.5.4 RGB
driver, compiled into this environment in place of the archive member; it differs from
upstream in six places, listed at the top of the file. Its scan ISR runs from IRAM, so
ordinary flash and PSRAM traffic cannot delay it, and it performs GDMA recovery only after an
actual bounce-buffer EOF shortfall or an explicit `PANEL:REALIGN`, never as routine work at
each VSYNC. The panel comes down before any flash write either way
([`main.cpp`](main.cpp)'s `otaStopPanel`), because the bounce fill reads PSRAM.
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
VSYNC-phased action/retry counts, the bounce-buffer EOF shortfalls the driver caught,
frame wait timeouts, draw failures, and CH422G write failures. The live checker's
`--wake-cycles N` option repeats the actual dark-to-lit path and requires those
error counters to remain unchanged.

## Operation lock and animation

The 16-frame On tap faucet animation is generated from the canonical
[`brand/mark.svg`](../../brand/mark.svg) at 360×360 by:

```
tools/cad-venv/bin/python tools/gen_animation_frames.py
```

The orange dot pulses under the faucet. The generator writes
`images/anim_00.h`..`anim_15.h`; `tools/make_art.py enclosure` packages them in the
mapped `art` partition during the build. Boot and the explicit `LOCK:SHOW` diagnostic
use this full-screen animation. Normal pages and operational progress remain static
except where their displayed state changes.

Fill, Clean and Dry raise a full-screen touch shield as soon as Start is queued.
The rail and selected portrait remain visible beneath it; the task pane offers only
Stop. A pending operation reports that it is waiting for the main board. Progress and
time left begin with the authoritative answer. Unanswered starts keep the shield up
while querying; Stop is retried until an answer proves the operation ended.
Completed operations keep their result in the task pane for six seconds, with Done,
flavor selection and task navigation available immediately.

Boot opens with **Powering on · Getting everything ready.** for at least two
complete animation cycles. It then opens onto the main board's flavor selection
as soon as that state is known, with a six-second ceiling when J9 is absent.

## Build / flash

```
pio run -e esp32s3_front              # compile only
pio run -e esp32s3_front -t upload    # build + flash
```

The board enumerates over its own native USB, independent of the base ESP32's
UART bridge — flashing it does not disturb the rest of the system. If J9's V12 kept the
display powered while its USB cable was reconnected, ask the main board to make the USB
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

Verified against Waveshare's 4.3B schematic and board support. Several RGB
lines are ESP32-S3 strapping/special pins (GPIO0/3/45/46) committed to the
panel — do not repurpose them.

| Function | GPIO |
|---|---|
| RGB DE / VSYNC / HSYNC / PCLK | 5 / 3 / 46 / 7 |
| R0–R4 | 1, 2, 42, 41, 40 |
| G0–G5 | 39, 0, 45, 48, 47, 21 |
| B0–B4 | 14, 38, 18, 17, 10 |
| Shared I²C (SDA / SCL) | 8 / 9 |
| Touch INT (GT911) | 4 |

Panel timings: HSYNC fp/pw/bp = 8/4/8, VSYNC fp/pw/bp = 8/4/8, both syncs
idle high, `pclk_active_neg=1`, 16 MHz. The shared CH422G/GT911 bus runs at
400 kHz so a display-control write fits inside the eight-line vertical back
porch.

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

**The main board keeps the quiet stretch, across both glasses.** A finger on either
is activity for both, so they sleep and wake together; this panel runs no timer of its
own and sleeps when it is told to. A press that already sent a command is presence the
main board can see, and a press that stayed silent — a wake tap, a tap on nothing — sends
`MSG_TOUCH` so it counts too. Waking is immediate; a live hold and an operation lock still
hold the dark off here, which is this panel's own business. A pair left lit is a link that
stopped talking, and is meant to read as exactly that.

The first touch on a dark screen turns it back on, on whatever the dark left up (see the
ladder above). The difference from the faucet display is the backlight itself:

- **Nothing on this board writes NVS while the panel runs.** The 800×480 framebuffer
  lives in PSRAM (`flags.fb_in_psram`), and a flash write suspends the cache PSRAM is
  reached through, so the DMA refilling its bounce buffer faults on the next line —
  `Cache disabled but cached memory region accessed`, and the panic takes the USB PHY
  down with it (`tools/display_usb.py` brings it back). A ratio and a flavor's chosen
  logo are therefore display-local, and the durable home for both is the main board,
  where the faucet's own selection already lives.
- The faucet fades its backlight with PWM. This board's backlight is a *digital*
  line on the CH422G (EXIO2) — on/off only, no PWM. EXIO2 drives both the LED
  converter and the panel's DISP input; panel VCC remains at 3.3 V while the
  glass is dark. So the idle state is a clean backlight/DISP off, not a rendered
  dim.
- Touch is the GT911 on the shared I²C bus. Its address (`0x5D`/`0x14`) depends
  on reset timing, so it's probed at init; reset is released via CH422G EXIO1,
  INT is GPIO4. It's registered as an LVGL pointer indev, so it's ready for the
  real UX, not just wake. The first touch while idle is consumed (wake only).
- Bit 7 of `0x814E` is raised when the GT911 has a new frame and cleared by reading it.
  Between frames the last one stands, so a poll finding the flag clear answers with the
  state it last read, and a lift must be reported for 150 ms before it reaches a widget —
  a tap needs one PRESSED sample, a hold needs every poll it spans. `GET_DIAG` counts
  these as `stale=` and `bridged=`.
- A changed flavor arriving from the faucet returns flavor tasks to **On tap** and
  leaves machine settings open. It wakes the panel when needed. Repeated publication
  of the flavor already shown does not reset the idle timer. Active operation locks
  retain their target until the main board confirms the operation ended.

## Test screen

The bench camera ([`tools/panelcam.sh`](/tools/panelcam.sh)) reads this panel and maps its
photograph back onto the panel's own 800×480 grid, which needs a known picture. `test [s]` on
the main board's console (`MSG_TEST_SCREEN`) puts one over whatever is up, lock included, for
`s` seconds (default 120; `test off` ends it), and keeps both glasses lit for as long as it
shows. On black, the panel's own:

- a 2 px white frame on the outermost pixels;
- four 32 px white fiducials at pixels x 16..47 and 752..783, y 16..47 and 432..463 — centres
  (32, 32), (768, 32), (32, 448) and (768, 448) in continuous coordinates, where pixel i spans
  [i, i+1);
- a 1 px cross through (400, 240) — column 400 for y 230..249, row 240 for x 390..409 — left
  out of a fit as its check, with nothing else between y 216 and 267;
- an eight-step gray wedge, 64×48 each, x 144..655, y 56..103, asked for at 0, 36, 73, 109,
  146, 182, 219 and 255 and shown as RGB565 rounds them;
- red, green, blue, cyan, magenta and yellow, 64×48 each, x 208..591, y 112..159;
- every colour the interface draws, 64×48 each, x 80..719, y 168..215: `COL_BLUE` 1749d1,
  `COL_CARD` 10319c, `COL_CARD_ON` 315fdb, `COL_ACCENT` ff9152, `COL_TEXT` ffffff, `COL_DIM`
  dce6ff, `COL_OFF` 6287e0, `COL_GOOD` ff9152, `COL_WARN` ffb183, and a 50% gray 808080 — the
  flat patches a camera-to-panel colour fit is made from;
- 1 px vertical stripes, 1 px horizontal stripes and a 2 px checkerboard, 64×64 each, at
  x 240, 368 and 496, y 268..331;
- `PANELCAM TEST` and this board's firmware version under them.

`TEST:<s>` on this board's own USB console shows it without the main board.

[`tools/panelcam-rectify.py`](/tools/panelcam-rectify.py) reads the fiducials' centres, the
stripe blocks at x 240..303 and 368..431, y 268..331, the palette row at x 80 + 64k, y 168..215 in
the order drawn here, and the wedge's black and white ends at y 56..103; move any of them and it
has to follow.

## USB-serial commands (bring-up / diagnostics)

Newline-terminated, 115200 baud over the native USB CDC:

- `GET_VERSION` → `VERSION:ENCLOSURE=<fw>`
- `GET_STATE` → main-board-owned flavor, synchronization / durability / pending
  state, operation lock, idle and page
- `GET_DIAG` → a packet-bounded `DIAG:` health line followed by `DIAG_UI:` and
  `DIAG_SYS:` detail: page / sub-view / idle / lock, link and queue health,
  render high-water, flavor replication, touch, memory,
  backlight, animation frame and uptime
- `GET_PANEL` → completed frame/submission counts, wake stage and completion,
  VSYNC-phased panel-control actions, caught EOF shortfalls, draw/frame timeouts, and
  CH422G write errors
- `BL:0` / `BL:1` → backlight off / on (drives CH422G EXIO2)
- `IDLE:0`..`IDLE:3` → wake, or take a rung of the idle ladder without waiting it out
- `PAGE:0`..`PAGE:3` → On tap, Prime, Fill, Clean;
  `PAGE:4` → system status; `PAGE:5` → pump service
- `FLAVOR:0` / `FLAVOR:1` → select through the same main-board-owned path as a card tap
- `EDIT:<1|2>[,<image 0..3>]` → open a flavor's own page, and take one of its logos:
  the same ratio and image-assignment handlers the screen uses
- `LOCK:SHOW` / `LOCK:HIDE` → exercise the reusable operation lock
- `TEST:<s>` → the camera's test screen for `s` seconds; `TEST:0` ends it
- `PANEL:KICK` → the wake sequence — dark, reset at VSYNC, four clean
  frames, light, quiet, then any active lock animation
- `PANEL:REALIGN` → request one RGB DMA recovery at the next VSYNC
- `PRIME:START:<1|2>` / `PRIME:STOP` → the pad's own handlers, without a finger on
  the glass: same frames, same ticks, same readouts
- `FILL:START:<1|2>` / `FILL:STOP` → the confirm page's START and the lock's STOP,
  without a finger on the glass: same frame, same answer, same lock
- `CLEAN:START:<1|2>` / `CLEAN:STOP` → the same for the clean cycle
- `AIR:DRY` / `AIR:STOP` → Settings' PUMP SERVICE → DRY THE LINES and the lock's STOP
- `STATUS` → ask the base for one `StatusPayload`
- `PUMP` → one `MSG_PUMP_RUN { B, 1000 }`
- `LINK` → RX/TX GPIO and the frame counters
- `RS485:<text>` → send text to the base as `MSG_TEXT`
- `RS485:SWAP` → exchange the RX/TX GPIO and report which way round it now runs
- `RS485:LOOP` → transmit and report whatever returns on this board's own receiver
- `RS485:RAW` → print the UART's bytes for 4 s, below HDLC
- `RS485:REINIT` → release both pads and bring the link up again

## RS485 link to the base ESP32 (J9 / SIG-7)

The onboard SP3485 is on **GPIO43/44** at 460800 8N1, wired to the main board's **J9**
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
absolute `MSG_FLAVOR_SELECT`; retries reuse the token and are silent. The main board
answers every query or selection with its authoritative value and persistence flags.
This polling turn also carries faucet-originated changes from J3 to this display.

The main board answers and never volunteers, so everything it has to say — a pump
that finished, a prime that timed out, both glasses waking — waits for a turn this
board's poll gives it. A pair that stops carrying therefore silences the machine
rather than only this screen, and it stops carrying no less readily while this glass
is dark. So the transport watchdog is armed by a transmission rather than by the
backlight: the first frame sent into a silence dates it, anything arriving clears it,
and three seconds unanswered rebuilds `Serial1` and both pads. It shares the prime
path's 2 s backoff, since both reinit the same pair.

Idle is the one piece of main board state that moves with nobody touching anything,
so it is asked for again every 5 s rather than once per link session — an announcement
that lost its turn is otherwise gone, and a glass would hold the wrong answer until
something else changed. A press here is presence the main board keeps for both glasses;
`MSG_TOUCH` is repeated until an idle state comes back agreeing the machine is awake,
and until it does, the dark is held off so a sleep published before the touch was heard
cannot undo the wake.

## The interface

Big Blue follows the approved [`design exploration`](../../future/enclosure-display-studies/big-blue.html).
The palette is cobalt `#1749D1`, navy `#10319C`, ice `#DCE6FF`, and orange `#FF9152`.
The 104 px flavor rail carries both actual images and Settings at the bottom. Flavor
pages keep a 234 px portrait column with “✓ Selected”; Fill, Prime and Clean sit above
the 462 px task pane. Done occupies the top-right 104 px and is hidden at rest and
while an operation is pending or running.

| Page | Contents |
|---|---|
| On tap | selected reservoir's four-segment reading, Change image and Ratio |
| Ratio | concentrate : water, with a bounded minus/plus stepper |
| Change image | available customer uploads, then four factory defaults; four per page, Previous/Next and actual position |
| Fill | instructions, Start filling, authoritative progress and Stop |
| Prime | shared main-board session and Hold to prime |
| Clean | three rinse cycles, authoritative progress and Stop |
| System status | complete machine profile and ten live reed indicators |
| Pump service | instructions and Dry the lines |

Ratios appear only on the Ratio page. Image assignments and ratios are saved by the
main board and shared with the faucet. Missing uploaded images are unavailable choices;
an empty customer page explains where to add images. Choosing an image keeps the picker
open. Every page entry clears an armed image press so a remote flavor change cannot
apply a pending choice to another channel.

The image wire bundle stays 172×320, 129×240 and 86×160. At boot and after an image
update, the display caches 64×119 rail images, 183×340 portraits and 78×145 picker images
in PSRAM. LVGL draws these complete portraits without transforming them during a frame.
The derived cache uses about 1.3 MB with all eight images. No image or ratio edit writes
NVS on the running RGB panel.

Done, either flavor, the rail background and the whole portrait return to On tap.
Selecting a different flavor queues a causal prime cancellation before the new selection.
A held prime permits those exits and blocks task/settings navigation. Fill, Clean and
Dry intercept every touch except Stop from the queued Start through the authoritative
terminal answer. Their result cards restore navigation immediately.

Machine pages occupy all 696 px to the right of the rail. Their header contains the page
title and Done; the large portrait and flavor tabs are absent. Changing flavor at the
faucet leaves these machine pages open.

Text is Montserrat, 20 px and up. Pages are built once; navigation changes visibility.
Routine unchanged main-board replies do not repaint the portrait, selection or gauge.

### Main-board console preview

These commands cross J9 through the same UI handlers as touch:

```text
ui choose           # On tap
ui choose a         # flavor A ratio
ui choose a go      # flavor A image picker; no actuator
ui fill a           # Fill instructions; no actuator
ui prime a          # shared prime-ready session; pump waits for a hold
ui clean a          # Clean instructions; no actuator
ui settings         # System status
ui pump-service     # Pump service instructions; no actuator
```

`go` starts an operation on Fill, Clean or Pump service. On Choose, it opens the image
picker. The existing diagnostic rail IDs remain stable.

### Sleep and touch

The main board owns the shared quiet interval and first darkening. After two minutes
dark, flavor tasks return to On tap and machine settings return to System status. After
ten minutes dark, every page returns to On tap. `IDLE:0`..`IDLE:3` exercise these stages.
A wake touch is consumed; it wakes without triggering an action.

Navigation responds to a press. Start/Stop require a release on their target; sliding
off cancels the click. Prime stops on release or slide-off. An image press commits on
a still hold of 150 ms or on lift and is canceled by movement or page dismissal.

### Prime

**Prime opens one shared prime-ready session for the selected flavor.** The main board owns
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

While held, a heartbeat goes out every 500 ms and the main board stops an unanswered hold
after 2 s. The enclosure renews the ready session on its 250 ms active / 500 ms dark poll;
the main board closes it after 5 s without that exact token. The hold pad reports its
owner, acknowledgement, outcome and connection state.

An unanswered START resets the J9 transport once and retries the same token. A lost STOP or
CANCEL is retried until exact main board state, or a strictly newer state in that same
session, proves it terminal. `GET_DIAG` reports those recovery counts and the main board's
one-reply-per-turn audit.

### Fill

**Fill → Start filling** sends `MSG_FILL_START { channel }`, and the main board
opens that channel's funnel path — its three valves — and draws with its pump what
was poured into the funnel on the enclosure's top face down into the chilled
reservoir. The main board owns the run and answers START, `MSG_FILL_QUERY` and
`MSG_FILL_STOP` with a complete `FillStatePayload`; it queues every change it makes on
its own — the draw finishing, the reservoir's full reed closing, a fault — for this
display's next turn.

The Stop-only task shows Drawing in concentrate, a progress bar and seconds left.
The main board is queried every 500 ms. Filled, Full, Stopped and fault outcomes remain
readable for six seconds while navigation is restored. Refusals appear on the Fill page.

### Clean

**Clean → Start cleaning** sends `MSG_CLEAN_START { channel }`, and the main
board puts tap water through that channel three rounds over: in through the idle pump to
the reservoir until its full reed closes, then out through the faucet on the dispense path
until its empty reed opens. The confirm page says to set a pitcher under the faucet first.
The main board owns the cycle and answers START, `MSG_CLEAN_QUERY` and `MSG_CLEAN_STOP`
with a complete `CleanStatePayload`; it queues every step it moves to and every ending for
this display's next turn.

The Stop-only task shows Flushing, progress across the complete cycle, the round and
flow direction, and the main board's estimated time left. Queries repeat every 500 ms.
Clean, Stopped and fault outcomes remain readable for six seconds while navigation is
restored. Refusals appear on the Clean page.

### Dry, before a pump replacement

**Settings → PUMP SERVICE → DRY THE LINES** sends `MSG_AIR_START { DRY }`. The card says to set a container
under the faucet first. The main board runs air in then through to the faucet on channel A,
then on channel B — the four purge states that sweep every joint the collet plate opens
([`/hardware/service/pump-replacement.md`](/hardware/service/pump-replacement.md)) — and
answers START, `MSG_AIR_QUERY` and `MSG_AIR_STOP` with a complete `AirStatePayload`.

The full-width machine task shows Drying, progress across four steps, flow direction,
Stop and the main board's time estimate. Dry and fault results restore navigation and
remain visible for six seconds. A console air purge uses the same operation surface.

### Rendering

Boot and `LOCK:SHOW` use the 10 fps animation timer. Fill, Prime, Clean, Ratio, images,
On tap and Settings repaint only when their displayed state changes. `GET_DIAG` exposes
loop and rendering counters for live measurement.

### Level and ratio

The selected reservoir's four segments come from the main board's reed-derived level:
none at empty, all four at full. Orange segments show the known amount; unavailable or
unanswered readings clear the segments and say No level reading. During a reported pour,
the resting title reads Pouring.

The ratio stepper sends both ratios as `MSG_RATIO_SET`. The main board persists and
returns them; the status poll carries subsequent changes. While a step's answer is owed,
an older status value cannot overwrite the local step. Ratios range from 1:6 to 1:24.

### System status

**Settings lands on the machine's own side profile with every reed on it.** The enclosure is
drawn as seen along X — 462 mm deep, 361 mm tall, the display's 45° facet off the top-front
arris, the front on the left — with the cold core at the back of the floor, the carbonator's
tube in the middle of it and a reservoir pocket at either end, B's forward and A's aft, none
of them named on the glass. Each of the ten reeds is a 14 px dot at its own station: a column
of four on each pocket's outer wall at 57.5, 102.5, 147.5 and 192.5 mm up the shell, empty at
the bottom and full at the top, and the carbonator's low and high on its tube's aft wall at
99.1 and 127.3 mm. A reed the main board reads closed is a filled `COL_GOOD` disc; every other
one is a ring. The areas a person can go into stand in a column east of the card, one target
each — one so far, **PUMP SERVICE**, whose page carries Settings to this landing.

The reeds ride the same status poll as the gauges, once a second while lit, and the diagram
repaints only the dots that changed. A poll the main board has not answered for 1.5 s, or a
reading it flags as stale, empties every dot and puts **Not reading the sensors** in the pane
below the drawing. The 436 px profile occupies the full machine page beside Pump service.
The drawing contains no text. `GET_DIAG` reports its settings view as `set=`.

## Integration seams (not implemented)

- **Dispense and carbonation state** beyond the locked-operation messages.

## Power and USB reattachment

J9 is `[B, A, GND, V12]` — this panel takes 12 V from the main board over the same
connector that carries the RS485 pair. With its own USB also plugged in it has two supplies,
and reconnecting the cable while J9 keeps the board powered can leave the USB device absent.
`J9.V12` runs straight to the board's V12 island with no switched load in its path.

[`/tools/display_usb.py`](/tools/display_usb.py) sends the explicit `display usb` development
request through the main board. The display acknowledges it, enters 500 ms of timer-wake deep
sleep, and therefore powers down the S3 USB PHY long enough for the host to observe a real
detach and fresh attachment. It does not switch V12 and nothing sends this request during a
production boot. [`/tools/boards.py`](/tools/boards.py) offers that command when it sees the
main board but not the S3.

The request requires the display application to be running and answering on J9. A missing,
old, or wedged display application still needs the panel RESET button or a physical V12 power
cycle for that boot.

## Sound

This panel has no sounder. The machine's one voice is U8 on the main board, so a finger
landing on this glass becomes a sound only by crossing J9 as `MSG_SOUND_PLAY`.

It is sent on `LV_EVENT_PRESSED`, not on the click, so the round trip hides inside the
finger's own dwell and the tick lands where the finger did rather than where it lifted.
Nothing is sent back — an ack would double the traffic in order to acknowledge a tick.
Every button on this panel is made by `mkBtn()`, so the hook lives there and nowhere else:
one place, and any button added later gets it without anyone having to remember.

The tick means **your touch registered**, not "that worked". Outcomes — refused, finished,
faulted — are the main board's own sounds. A touch that begins on a dark screen is withheld
from every widget by the wake latch, so waking the panel does not tick.

None of it reaches the gas alarm. See [`../src_appliance/README.md`](../src_appliance/README.md).
