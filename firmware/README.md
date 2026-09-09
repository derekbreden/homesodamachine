# Firmware

Five source trees, each its own PlatformIO environment in [`/platformio.ini`](/platformio.ini), each running on its own board.

| Tree | Env | Runs on | Machine |
|---|---|---|---|
| `src_appliance/` | `appliance` | the main board's WROOM (U1) | the appliance |
| `src_pcba_bench/` | `pcba_bench` | the main board's WROOM (U1) | none — a bare board on the bench |
| `src_front/` | `esp32s3_front` | Waveshare ESP32-S3-Touch-LCD-4.3B | the appliance |
| `src_faucet/` | `esp32s3_faucet` | Waveshare ESP32-S3-Touch-LCD-1.47 | the appliance |
| `src_weld_rotator/` | `weld_rotator` | ESP32-DevKitC-32E + DM542T | the cap-weld bench fixture |

Two of them run on the main board, and only one of the two ships inside a machine.

**`src_appliance/` is the appliance's own firmware** — the state machine, the thermal loop, the dispense, persistence, the links to both displays ([`src_appliance/README.md`](src_appliance/README.md)). It boots to the state [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) opens against — build ID printed, every actuator parked dark — and brings up J9 and J3. What runs at the glass today is one flavor pump, the funnel fill and the clean cycle: a prime held from the 4.3B, `pump <a|b> [ms]` bounded from the console, a fill that opens a channel's funnel path and draws with its pump — held from the enclosure's FILL page or run by `fill <a|b> [s]` — a clean cycle that puts tap water through the channel in rounds, in through the idle pump and out through the faucet — started from the enclosure's CLEAN page or by `clean <a|b> [rounds] [s]` — and the dry cycle before a pump replacement, air swept through both channels to the faucet, from the enclosure's Settings page or by `dry`. Flavor selection from either display reaches and is persisted by the main board for the future automatic-dispense path, then mirrors to the other display. `machine.cpp` owns every actuator request; `pcba_expanders.cpp` clears and verifies both MCP23017 output banks, enables the reed pull-ups and owns the physical V-A–V-K map; `link.cpp` turns a J9 frame into a machine intent. The USB `status` command reads both expanders and all ten reeds; the fill and the clean cycle are the runtime operations that open valves, one topology state at a time and at most three valves at once. The procedure it fills in is [`/hardware/assembly/firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md) §3, §6, §7 and §9; the pin map is [`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), drawn as [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd).

Shared libraries sit under `lib/`, compiled into whichever trees include them:
[`lib/proto_link`](lib/proto_link/proto_msg.h) is the inter-board wire contract;
[`lib/machine_policy`](lib/machine_policy/machine_policy.h) is the Arduino-free actuator-plan,
safety-transition and pump-timing policy; [`lib/flavor_selection`](lib/flavor_selection/flavor_selection.h) is main board authority and persistence policy; [`lib/weld_rotator_policy`](lib/weld_rotator_policy/weld_rotator_policy.h) holds the rotator's physical ratio, exact lap count, and deadman transitions; and [`lib/sound`](lib/sound/sound.h) is U8 — the drive on IO13, the machine's sound vocabulary,
and the volume/quiet-hours settings behind it. The appliance and the bench share that one
table on purpose: a board on the line makes exactly the sounds a customer's machine makes.
Neither display carries a sounder, so every sound the machine makes is made on the main board.

`src_pcba_bench/` is the bench rig for a **bare** board, one board per fab batch, and goes no further than the bench. It answers whether the fab built what [`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx) describes — it reads every device, and behind `arm` it drives both relays, both DRV8870 pumps and the buzzer, one output at a time for 120 s so each can be metered at its connector. It also carries the buzzer's range — `ladder`, `duty`, `palette`, played once at boot — which is where the machine's alarms and acks get designed ([`src_pcba_bench/README.md`](src_pcba_bench/README.md)). It never writes `IODIR` or `GPPU` on either MCP23017, so the ten manifold valves, V-K and the condenser fan — everything behind the two expanders — stay dark, and no reed is ever read on a pull-up. It answered batch 2 on the bench: [`/hardware/pcb/pcba/bench-log.md`](/hardware/pcb/pcba/bench-log.md).

## J9 is one pair, and both ends take turns

The display link is a single differential pair — J9 is `[B, A, GND, V12]` — carrying half-duplex RS485 between the main board and the 4.3B. **Nothing arbitrates it.** U7 on the main board is an auto-direction transceiver with `/RE` tied to GND, so the main board's receiver runs while its driver does and it hears every byte it sends; [`lib/proto_link/rs485_echo.h`](lib/proto_link/rs485_echo.h) exists to strip that echo before the framer sees it.

That echo cancellation is only sound while the two ends do not talk at once. If the glass sends while the main board is replying, the two collide, the main board reads back something other than what it wrote, and the echo it is waiting for never arrives. A canceller that merely counted bytes would stay in deficit from that moment and swallow real traffic as its own echo — the main board goes quietly deaf, and the frame that gets lost is whichever one arrived next. That failure looks exactly like latency, because the sender's retry eventually gets through.

So the rule, and it is a rule rather than an optimisation:

- **The main board answers; it never interrupts.** Every frame it puts on the pair goes out inside the window immediately after one arrives. Anything the machine wants to volunteer — a prime that timed out, a bounded run that finished, the image reconcile asking both stores what they hold — is queued in [`src_appliance/link.cpp`](src_appliance/link.cpp) and flushed in that window, and so is every question the console puts to the glass. `linkPing` is the one deliberate exception, and it is a bench command with nobody expected to answer.
- **The glass sends one frame at a time.** Everything posts to the outbound queue in [`src_front/main.cpp`](src_front/main.cpp), and the next frame waits for the answer or for the turnaround window to lapse. The exception is a reply made from inside the turn that asked for it — `MSG_RESP_UI_SHOW`, `MSG_RESP_TEST_SCREEN` and `MSG_RESP_DISPLAY_USB_REATTACH` answer on the wire the main board is still holding open. One press is one frame — a button that already speaks for itself sends no separate click, and the main board makes the tick off the command it received.
- **The glass polls on an interval,** because that poll is the only window the main board has to speak in. It is the ceiling on how stale news from the base can be.

HOME's flavor query is one of those turns: 250 ms while lit and 500 ms while dark.
It carries main board flavor truth and durability to the enclosure, including selections
that arrived from the faucet over J3. An enclosure selection is an absolute, tokenized J9
request; main board revision publication carries the result to the faucet over full-duplex J3.

`link` on the main board console reports `desyncs`: collisions that reached the wire in spite of all that. On a healthy pair it stays at zero. Rising under load means the discipline is being violated somewhere, and the place to look is whatever recently learned to transmit.

## J3 is the faucet's direct UART

J3/SIG-6 is a separate full-duplex 3.3 V TTL link to the 1.47-inch faucet display. The
main board uses IO33 TX / IO35 RX; the faucet uses GPIO43 TX / GPIO44 RX, crossed TX to RX,
at 921600 baud — direct TTL, with no transceiver ceiling over it. TinyProto Fd supplies
framing, CRC, acknowledgements and keepalives. J3 has
independent TX and RX conductors, so none of J9's half-duplex turn-taking or echo cancellation
belongs on this link.

A faucet tap changes the local logo first, then queues `MSG_FLAVOR_SELECT` with an absolute
flavor and request token. The main board acknowledges its authoritative value and persists it
in NVS. Repeating a token cannot repeat the selection or its sound. At first installation only,
a main board with no stored flavor adopts the faucet's cached selection; every established
main board wins reconciliation. Both boards defer flash writes away from the touch path.

## What the links carry, measured

Both displays carry a WiFi radio no product path uses, and every image the
machine moves goes over the wires instead. `wifi` and `bench j3` on the main
board console are what that comparison is made of. All four numbers below are
one bench, one room, `RSSI -40 dBm`.

| Path | Rate | What is in it |
|---|---|---|
| J3, OTA pull | 9.2 KB/s | the shipping path: 1 KB asked for, waited on, written to flash |
| J9, OTA pull | 11.2 KB/s | the same, across the half-duplex pair |
| J3, `bench j3` | 71–74 KB/s | the wire itself — TinyProto's window, nothing written |
| WiFi, BLE advertising | 99–135 KB/s | faucet to enclosure, SoftAP and one TCP socket |
| WiFi, BLE off the air | 299–349 KB/s | the same run with `wifi <KB>q` |

**The pull is most of what the wired numbers are.** J3 runs at 921600 and
carries 82% of that when nothing is taking turns on it; the OTA path gets 12%
of the same wire. What the difference buys is a receiver that stores no more
than a frame — the property that lets a phone update four boards through a
main board holding one chunk — and it costs a round trip per kilobyte.

**The radio is one antenna and BLE is on it.** The faucet advertises to the
phone with the same PHY it would forward over, and coexistence takes about two
thirds of the throughput. A trailing `q` stops advertising for the length of a
run, which is what the two WiFi rows are.

**The enclosure's radio and its panel cannot both be up.** Its scan-out DMA
refills a bounce buffer out of PSRAM and bringing WiFi up writes flash, which
suspends the cache PSRAM is reached through — the conflict that already blanks
this glass for an arriving image. `wifi on` takes the panel down the same way
an OTA does, and the board reboots when the run ends. The faucet drives SPI and
has no such conflict.

```
wifi on | off        raise or drop the enclosure's bench AP
wifi <KB>[q]         the faucet joins it and sends; q takes BLE off the air
bench j3 [<KB>]      push at J3 as fast as its window will take frames
```

Both are refused unless the machine is dark: each holds the main board's loop
for the length of a run.

## A user's own pictures

Eight faces a channel can wear. The low four are compiled into every image and
cannot be removed, so a machine whose owner deleted everything they added still
has four. The high four are theirs, and only ever arrive from a phone.

**The phone sends pixels, not photographs.** A picture crossing BLE is already
cropped, resampled and dithered to RGB565 at exactly the sizes each panel draws
— three renditions, `IMAGE_BUNDLE` in [`proto_msg.h`](lib/proto_link/proto_msg.h):
172x320, 129x240 and 86x160. Neither board decodes or scales anything; each is
handed a pointer into mapped flash and renders straight out of it, the way
`board_art` already renders the loading animation.

**One shape, at three scales.** Every rendition is 43:80 — the faucet's glass —
so a photograph gives the machine one rectangle and every surface that shows a
logo shows the same picture. The faucet fills its glass with the largest; the
enclosure anchors a detail page on that same one, wears the middle on a Choose
card and previews the smallest in its picker. Both boards keep all three, so a
slot's own crc32 is its identity on either of them and the reconcile below has
one number to compare.

**Both stores live in the partition nothing was using.** `spiffs` — 9.94 MB on
the faucet, 6.94 MB on the enclosure — needed no table change, which matters
because a partition table is the one thing an update cannot install. A slot
stands on its own erase boundary and carries its own header, written last, so a
transfer cut short costs that one picture and leaves the slot reading empty
rather than showing half a face.

**The faucet is the master copy.** It has the radio and the space, so it keeps
every rendition either glass draws — an enclosure display can be replaced and
re-provisioned from it with no phone in the room.

**Writing is the rare case and it is what costs.** Reading is a pointer, which
is why this is flash and not PSRAM: re-sending on every boot would trade a cost
paid once for a cost paid always. A picture chosen months ago is on both
glasses the instant they boot.

```
phone  ──BLE──▶  faucet  ──WiFi──▶  enclosure
                   │                    │
                   └────── all three, byte for byte ──────┘
```

The last hop is the radio rather than J9 because the enclosure's panel has to
come down for a flash write either way — so the transport that costs nothing
extra at that moment is the fast one. A bundle is 199,520 bytes; measured at
**180 KB/s**, against the 15 s J9 would take. The access point stands only for
that burst and the board reboots into its new face when it drops.

```
images                 what each display holds
images test <slot>     have the faucet make itself a picture, with no phone
images relay <slot>    carry one to the enclosure over the radio
```

## What the appliance firmware must hold

Three constraints the main board and the supply impose, each carried by a part that pays for a violation. They are in [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md) §9 as well, where the factory confirms them per unit.

- **At most 3 solenoid valves energized at once.** Eight coils on MANIFOLD A draw 2.4–3.7 A through J1's `COM` contact, rated ~3 A, and dissipate it in one SOIC-18 (U4). The canonical valve states open at most three ([`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md)); the ceiling is [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Solenoid COM current budget".
- **Relay #2 (`IO2`) off while a dispense is open.** The main board peaks at 3.33 A and the SeaFlo diaphragm pump at 5 A on the same 12 V rail — 8.32 A together, against a 6.7 A supply. The carbonator's low reed asserts mid-pour, so the refill it queues waits for the dispense window to close ([`/hardware/assembly/acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) step 5). Nothing in hardware enforces this. `machine_policy::kRefillDuringDispense` is the policy that refuses such a plan and `machineDispenseWindowOpen()` is the accessor that asks; neither relay is driven yet, so nothing has cause to.
- **`GPPU` written on both MCP23017s.** No loom carries a resistor and the main board pulls none of the reed inputs ([`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), U2 GPB4-7 / U3 GPB6-7), so every reed reads its expander's internal pull-up or floats.

`pio test -e native` holds these policies off-board: it checks the canonical operation table,
all logical valve transitions, the complete physical expander map and fault parking, and pump
deadline boundaries without opening a serial port. See [`test/README.md`](test/README.md).

## Appliance displays

- **ESP32-S3 enclosure display** (Waveshare ESP32-S3-Touch-LCD-4.3B) — The appliance's config + interaction surface on the enclosure's front face: a 4.3" 800×480 RGB capacitive touchscreen (GT911, CH422G I/O expander) angled up toward a standing user, linked to the base ESP32 over RS485. HOME presents both flavor cards and mirrors the main-board-owned selection shared with the faucet. A reusable operation lock puts the animated logo on the left and a clear status modal on the right; boot exercises it for at least two cycles. `src_front/` drives the panel through esp_lcd with a double framebuffer + bounce buffer for tear-free output and carries the RS485 link on GPIO43/44 as typed TinyProto frames ([`proto_msg.h`](lib/proto_link/proto_msg.h)). Service → Prime → a flavor → hold the pad sends `MSG_PRIME_START` and a tick every 500 ms under the finger; the base answers `MSG_RESP_PRIME` on every state change. Fill → a flavor → START sends `MSG_FILL_START`; the base opens the funnel path, draws with the pump, and answers `MSG_RESP_FILL` on every change, which the enclosure shows on the operation lock with a progress bar and STOP. Clean → a flavor → START CLEAN CYCLE sends `MSG_CLEAN_START`; the base runs three rounds of a tap-water fill and a pumped flush and answers `MSG_RESP_CLEAN` on every step, shown on the same lock with the round, the direction of the water and the minutes left. See [`src_front/README.md`](src_front/README.md).
- **ESP32-S3 faucet display** (Waveshare ESP32-S3-Touch-LCD-1.47) — Flavor selector at the end of the appliance's gooseneck. The selected flavor's logo fills a 172x320 capacitive-touch LCD; a tap anywhere changes it locally before a nonblocking J3 message reaches the main board. The main board owns and persists the selection; faucet NVS is the immediate boot-logo cache. The main board keeps the quiet stretch across both glasses, and when it says so this backlight fades to an ember level; the first touch wakes it without toggling. See [`src_faucet/README.md`](src_faucet/README.md).

## The pour

Carbonated water flows at the faucet and the selected channel's pump injects concentrate into
it on a duty cycle that follows the flow. The DIGITEN meter's pulses are counted over 50 ms,
and each count is one reading:

| Flow reading | On | Off | Duty |
|---|---|---|---|
| 1 pulse / 50 ms | 50 ms | 600 ms | ~8% |
| 6 pulses / 50 ms | 200 ms | 300 ms | ~40% |

The channel's ratio scales that. 1:20 is the SodaStream-compatible bottle and is the shape
above; 1:6 is bag-in-box syrup, and at full flow the head stays on.
[`machine_policy::pourCycleTiming`](lib/machine_policy/pour_policy.h) is the whole of it, and
`pio test -e native` checks its boundaries and the phases either side.

## Pin Assignments

The appliance board's pin map is [`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), drawn as
[`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd); the 4.3B's is
[`src_front/README.md`](src_front/README.md). The faucet display's is below, fixed by the
board design.

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
| J3 UART TX | 43 | 921600 baud, TinyProto Fd to main board IO35 RX |
| J3 UART RX | 44 | 921600 baud, TinyProto Fd from main board IO33 TX |
| BOOT button | 0 | |

## A shipped unit is updated from the iOS app

**The phone is the update path.** A customer's machine is never on WiFi and never on the
internet — the air gap is deliberate — so BLE from a phone standing in the kitchen is how new
firmware reaches a unit in the field. USB, below, is the bench path.

Four links, one pull. The receiver asks for the offset it is ready to write; whoever is upstream
of it asks the next one out; the phone answers. One chunk is in flight anywhere on the path and
no board between the phone and the flash stores more than a frame.

```
homesodamachine.com  ──HTTPS──▶  iOS app  ──BLE──▶  faucet display
                                                          │
                                                          J3
                                                          ▼
                                     enclosure  ◀──J9──  main board
```

**The faucet display carries the radio** ([`src_faucet/ble_link.cpp`](src_faucet/ble_link.cpp)):
NimBLE on the Nordic UART Service, at the end of the gooseneck, above the counter, in open air.
An image for the faucet goes from the phone into its own spare slot with no relay in it. Anything
else goes onto J3 as it lands, and [`src_appliance/ota.cpp`](src_appliance/ota.cpp) is the relay
that carries it the rest of the way. That relay takes its bytes from the console or from J3 —
`MSG_OTA_SRC_BEGIN` / `_NEED` / `_DATA` / `_END` in
[`proto_msg.h`](lib/proto_link/proto_msg.h) — and everything downstream of that question is one
path.

**What a machine advertises comes from its main board.** A display is one board out of a pair
that could be wired to either machine; the main board is the machine. `MSG_IDENTITY_QUERY`
answers with the model and the low three bytes of the main board's own MAC, and the faucet puts
that in its local name and in a `0xFFFF` manufacturer block. Two machines a metre apart are
distinguishable in a scan result, before either is connected to. `identity <name>` on the main
board console sets a name; so does BLE text `IDENTITY <name>` from the phone, which the display
with the radio carries to the main board as `MSG_IDENTITY_SET` and answers with the identity
frame once the main board has it. `ble` reports the radio the main board cannot see.

**What an update is, per board.** Firmware goes into the OTA slot that is not running and the
boot partition moves only after the whole image is in and its CRC32 matches; a transfer that
stalls leaves the board running what it booted. The enclosure display also carries `art` — a data
partition holding the loading animation, erased and rewritten in place, verified the same way.

| Target | Image | Slot | Reached over |
|---|---|---|---|
| `self` | `appliance` | 768 KB | J3, or the console |
| `faucet` | `esp32s3_faucet` | 3 MB | BLE, or J3 from the console |
| `enclosure` | `esp32s3_front` | 2.5 MB | J9 |
| `art` | `tools/make_art.py enclosure` | 4 MB | J9 |

**The enclosure display goes dark while it writes.** Its scan-out DMA refills a bounce buffer
from PSRAM, a flash write suspends the cache PSRAM is reached through, and the refill then
faults — the same constraint that keeps its logo choice on the main board rather than in local
NVS. So it says what is about to happen, stops the panel, takes the image dark and reboots either
way. A failed transfer costs a reboot into the image it was already running. The faucet drives
SPI, has no such conflict, and shows a live percentage.

### Where the images come from

[`tools/publish_firmware.py`](/tools/publish_firmware.py) builds every image, packs one
content-addressed release asset and pins it in
[`firmware/firmware.lock.json`](firmware.lock.json) — each image by target, `FW_VERSION`, size,
the crc32 `MSG_OTA_BEGIN` promises, and a sha256. `web/scripts/fetch-firmware.mjs` puts the bytes
on the deploy's disk and `/api/firmware` serves the manifest; `render.yaml` names the lock in its
build filter, so publishing firmware deploys the site the way pinning geometry does.

The version string is the board's own: `pre_build.py` writes `FW_VERSION` into each tree from
HEAD's date and short SHA, the board reports that string, and the manifest carries the same one.

```bash
~/.platformio/penv/bin/python tools/publish_firmware.py --write
```

## The bench path

`tools/ota.py` pushes through the main board's USB console — the same relay, with the console as
the source instead of J3:

```bash
~/.platformio/penv/bin/python tools/ota.py enclosure
```

Targets are `self`, `faucet`, `enclosure` and `art`; `pio run -e <env>` first. The console runs
at 500000 for the duration of a session and drops back when it ends.

`tools/boards.py` names each S3 on sight — every one reports its MAC as its USB serial number.

## Building and Flashing

Every environment in [`/platformio.ini`](/platformio.ini) builds with `pio run -e <env>` and
flashes with `-t upload`. `firmware/pre_build.py` runs first on the four that report a build
ID, stamping `fw_version.h` from the git rev so a board says which commit it was built from.
`weld_rotator` names no pre-build script and reports none.

**With more than one board on USB, name the port.** PlatformIO picks one otherwise, and it picks the S3 — esptool opens that port, drops the display into download mode, and only then fails on the chip id, leaving the panel dark until it is reflashed ([`/hardware/pcb/pcba/bench-log.md`](/hardware/pcb/pcba/bench-log.md)).

[`tools/boards.py`](/tools/boards.py) says which board is on which port and prints the commands with the ports already filled in. It only enumerates — it never opens a port, because opening one drives the main board's Q2/Q3 auto-reset lattice and reboots it.

```bash
~/.platformio/penv/bin/python tools/boards.py
```

**An externally-powered enclosure display can explicitly reattach to USB without cycling the appliance.** J9 is `[B, A, GND, V12]`, and `J9.V12` runs straight to the V12 island with no relay, so firmware cannot drop display power. Instead, the development command below asks a running display to put its USB Serial/JTAG PHY into deep sleep for 500 ms; timer wake then presents a real USB detach/attach.

```bash
~/.platformio/penv/bin/python tools/display_usb.py
```

The command is explicit development control and is never sent by a production boot path. It finishes by observing the old USB attachment disappear, opening the re-enumerated display and requiring a `VERSION:ENCLOSURE=...` reply. If it reports `UNREACHABLE`, the installed display image is too old or the display is not answering on J9; that one boot still needs the physical RESET button or a V12 power cycle before the current image can be flashed.

```bash
PLATFORMIO_UPLOAD_PORT=/dev/cu.usbserial-10 pio run -e appliance -t upload
```

### Flash the appliance controller

```bash
pio run -e appliance -t upload
```

See [`src_appliance/README.md`](src_appliance/README.md) for its console.

### Flash the main board's bring-up console instead

```bash
pio run -e pcba_bench -t upload
```

For a bare main board on the bench, not an assembled machine. See [`src_pcba_bench/README.md`](src_pcba_bench/README.md) for its command table.

Both go over a plain USB-C cable into J14; the on-board CH340B bridges and Q2/Q3 auto-reset, so no button presses.

### Flash the enclosure display's art partition

The loading animation is not in that board's firmware image — it is 3.96 MB in
the `art` partition, built from the same `src_front/images/anim_NN.h` headers by
[`tools/make_art.py`](/tools/make_art.py), which `pre_build.py` runs
for this environment. `esp_partition_mmap` hands LVGL a pointer into it, so it
renders straight out of flash at no RAM cost, exactly as compiled-in `.rodata`
did — it just stops riding along in every update of code that never touches it.

A board whose `art` partition is empty runs and shows its lock screen without a
logo; `ART` on its console says what is there and `ART:VERIFY` walks the CRC.

```bash
PLATFORMIO_UPLOAD_PORT=/dev/cu.usbmodem1101 ~/.platformio/penv/bin/python -m esptool --chip esp32s3 write-flash 0x510000 .pio/build/esp32s3_front/art.bin
```

Over the link instead, with only the main board on USB:

```bash
~/.platformio/penv/bin/python tools/ota.py art
```

### Flash the ESP32-S3 (4.3B enclosure display)

```bash
pio run -e esp32s3_front -t upload
```

### Flash the ESP32-S3 (faucet display)

```bash
pio run -e esp32s3_faucet -t upload
```

The [pioarduino platform](https://github.com/pioarduino/platform-espressif32) for Arduino core 3.x, and [LVGL v8.4](https://github.com/lvgl/lvgl) for the UI. The JD9853 panel is driven through the GFX library's ST7789 driver plus a panel-specific init sequence; the AXS5106L touch driver lives in `src_faucet/axs5106l.cpp`. Rotation 0 puts the USB connector down on the faucet mount. Test commands over USB serial (115200 baud): `GET_STATE`, `TOGGLE`, `FLAVOR:n`, `GET_DIAG`, `BL:n` (raw backlight duty), `GET_VERSION`.
