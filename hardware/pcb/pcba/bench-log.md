# pcba bench log

Format: facts only. What was exercised, by what method, and what it read. Direct quotes
from Derek where applicable. Named commands are
[`firmware/src_pcba_bench/`](/firmware/src_pcba_bench/README.md)'s console.

## Batch 1

JLCPCB order W2026071513250534, 10 boards, placed 2026-07-15
([`ledger/purchases.md`](/hardware/ledger/purchases.md)). One board exercised on the bench
2026-08-03: 12 V into J10, USB-C into J14, nothing else plugged in except a pump on J13 at
the end.

`info` reads it as **ESP32-D0WD-V3 rev 301**, 2 cores @ 240 MHz, 4194304 bytes flash @
40 MHz, eFuse MAC **`ec:c9:ff:fb:e0:a0`** — that MAC is which board this is.

### Operating facts for a batch-1 board

- **A 12 V power cycle is the only reset.** Q2.C→U1.EN lost three vias, so neither the
  CH340's auto-reset nor SW2 reaches EN. Derek: *"SW2 button presses did nothing every time
  I tried them."* SW1 (BOOT) is on a different net and works.
- **Reflashing takes: hold SW1 · pull 12 V · wait 5 s · restore 12 V · hold SW1 2 s more ·
  release.** That leaves the chip in UART download mode indefinitely, so there is no timing
  to hit. esptool's closing reset also goes through EN, so a plain 12 V cycle is needed
  afterwards to start the app.
- **U13 runs off the board's own 3V3, not VBUS**, so cutting 12 V drops the USB device and
  it re-enumerates under a fresh node. Anything holding the port dies at that moment and
  the first second or two of boot output is lost.
- **ERR (D2) reads inverted** under the current bench firmware, which drives IO15 LOW to
  light it — batch 1 wires D2 the other way up. Faint red at idle is `parkStraps()` holding
  MTDO on its ~45 kΩ internal pull-up, ~28 µA through the LED.
- **With a 4.3B also on USB, name the port when flashing this board.** `tools/flash.sh`
  lets PlatformIO pick, and it picks the S3: esptool opens that port, drops the display into
  download mode, and only then fails on the chip id, leaving the panel dark until it is
  reflashed. `PLATFORMIO_UPLOAD_PORT=/dev/cu.usbserial-* pio run -e pcba_bench -t upload`.

### Answered

| Subsystem | Method | Reading |
| --- | --- | --- |
| 12 V → K7805 → AMS1117 | U13 enumerates off board 3V3 | rails up |
| ESP32, 40 MHz crystal, flash | `info`, esptool read + hash verify | as above, 460 kbit/s |
| USB-C, U14, CH340C, SW1 | flash + verify | pass |
| WiFi RF + board-edge antenna | `wifi` at boot | 15 networks, best −42 dBm |
| RS485 — U7, the pair, R6's 120 Ω, both ESD clamps | `rs485` loopback | 6/6 |
| **J9 barrels + the haul out to them** | a 4.3B display on J9, TinyProto Hdlc both ways | frames carried; see below |
| Buzzer IO13 → R5 → Q1 → U8 | `buzz` | Derek: *"I heard beeps."* |
| Status LEDs ERR / RUN / ACT | `walk` | all three; ERR inverted (above) |
| Gas analog divider R1/R2 | `watch`, J11.AOUT → J11.V5 | **3020 mV** against `pcba.tsx`'s ~3.0 V; floor 142 mV |
| J4.IO25 · IO26 · IO27 | `watch` to J4.GND | beeped |
| J3.IO33 → J3.GND, J3.IO35 → 3V3 | `watch` | beeped |
| Relay net, driven | `watch`, J5.IO2 → J4.IO26 | Derek: *"Confirmed beeps under those conditions."* |
| U15 interlock, fail-safe path | `interlock`, then J5.IO19 → J4.IO26 | Derek: *"Got a beep on J5 IO19 to J4 IO26"* — Y held LOW with A high |
| **U11 DRV8870 → J13.AM2/AM1** | `pump a`, Kamoer KPHM400 on the west pair | Derek: *"It worked beautifully! The motor ran!"* |
| **U12 DRV8870 → J13.BM2/BM1** | `pump b`, same pump moved to the east pair | Derek: *"It did run, noticeable steps, very good"* |

**The J9 link, 2026-08-04.** A Waveshare ESP32-S3-Touch-LCD-4.3B on J9, taking its
7–36 V from `V12` on the same 4-conductor loom that carries the pair, so the display runs
off the board. A button on its panel sends `MSG_PUMP_RUN{channel B, 100%, 1000 ms}` and
the board answers `MSG_RESP_PUMP_DONE` after the run; Derek: *"tapping run pump b did run
pump b."*

That is more than the `rs485` loopback proves. The loopback closes on-board at R6, so it
passes whether or not J9's barrels carry — these frames went out through them, into a
cable, and back. Both hauls and both barrels are exercised.

**Hold-to-prime, same day.** The panel's Service page holds a pad, and the pump turns for
as long as a finger stays on it: `MSG_PRIME_START`, a `MSG_PRIME_TICK` every 500 ms under
the finger, `MSG_PRIME_STOP` on lift, and the board parks the pin if a tick runs later than
2 s or the hold reaches 60 s. Measured over 32 consecutive holds: **base loop high-water
1 ms, echo swallowed 1242 bytes against 1242 transmitted, and every one of the 77 frames
the board sent arrived.**

Three facts that cost hours and are not the board's:

- **The 4.3B's RS485 sits on GPIO43/44, which are U0TXD/U0RXD.** The bootloader leaves
  UART0 holding GPIO43, and `Serial1.begin()` maps it as RX without releasing that
  driver, so the display reads its own pad and hears nothing. `gpio_reset_pin()` on both
  pads first. Until that was found, every symptom pointed at this board.
- **A Kamoer head does not break away part-throttle.** `pump b 60 1` prints a clean
  1001 ms run and turns nothing; at 100% it turns. The console's own report says only
  that IN1 was driven — the room says whether the head moved.
- **`Stream::readBytes` waits out a 1000 ms timeout** for a count `available()` reported
  and the stream then did not hand over. `HdlcLink::service()` drew its bytes that way,
  inside the `loop()` that meters a pump: the board ran a pump 1321 ms for a hold released
  at 322 ms, and frames on both sides of the stall went missing. It reads what is there and
  returns; `link` reports the loop high-water so the next stall names itself.

`link`'s byte counts are what separate the three ways this link fails: bytes rx climbing
while frames rx does not is the pair carrying and the framing failing; both flat is nothing
reaching IO34 at all; echo swallowed running ahead of bytes tx is the canceller eating real
traffic. `j9raw` dumps the wire below all of it.

Both runs drove jabs, a ten-step ramp 10→100%, 3 s at full, then 75/50/25%, and the head
turned through all of it on both channels. The step-down is the half that discriminates:
the speed dropped audibly at each of the three, which a pin stuck high or a bridge latched
on does not do.

The console prints `15673 ms driven` for every run — the stage timing is deterministic, so
that number is the same with a motor and without one. Only the room reports whether a pump
turned.

### Silent, and predicted silent

Every one of these traced to a via that was never drilled. Derek, with a meter: *"I read
nothing between any pair of SDA or SCL connected pins I've tried, none of them appear to be
connected."* And after the beep probe: *"The three that should stay silent did stay silent,
the others beeped."*

| Net | Undrilled | Consequence |
| --- | --- | --- |
| I²C SDA | U1.IO21, U2.SDA, U3.SDA, U6.SDA, R19.pin1 | `scan` finds 0 devices — 0x20, 0x21, 0x68 all absent |
| I²C SCL | U1.IO22, U2.SCL, U3.SCL, U6.SCL, R20.pin1 | same |
| Q2.C → U1.EN | 3 vias | EN unreachable; SW2 dead; power cycle is the only reset |
| R3.pin2 → R4.pin1 → U1.IO36 | 2 | firmware cannot read the MQ-6 trip |
| R4.pin1 → R25.pin1 | 2 | U15's B input severed; R24 holds it low |
| U1.IO23 → J4.IO23 | 1 | J4.IO23 dead |

`bus` measured the two I²C pins directly: `SDA IO21 hi-Z=1 with-45k-pulldown=0`,
`SCL IO22 hi-Z=0 with-45k-pulldown=0` — neither 4.7 kΩ pull-up reaches its pin.

**Cause.** `drill.drl` carried **135 holes at 0.3 mm against 152 vias** in the circuit-json.
`render-board.ts` called `convertSoupToExcellonDrillCommands` with no `layer_span`, so
`shouldIncludeElement` emitted only holes spanning exactly top→bottom; every `routeInner`
via declares a partial span (`top→inner1`, `top→inner2`, `inner2→top`) and was dropped
while its pads stayed on all four layers. JLCPCB drilled exactly what the file specified.
The render scorecard read 13/13 with 0 opens throughout, computing from the model the
emitter consumes. See [`FORKS.md`](FORKS.md) for the upstream/fork seam that produced it.

### Not exercised on batch 1

Everything behind the dead bus, and only that: both MCP23017s and their address straps,
U6 DS3231, BT1/CR2032, both TBD62083 valve drivers, all 12 valve outputs, the fan output,
10 reed inputs, and the off-board MPR121 through J8. J3's faucet UART carries to the
connector but has never had the 1.47" display on it. Reaching any of it needs the bodge or
a batch-2 board. Everything on this board *not* behind the bus has now been exercised.

Also never demonstrated on any board: the Q2/Q3 auto-reset pair passing, and U15's *pass*
path (gas-clear high on B, Y following A) — both need EN and R25 respectively.

Batch 1 will not be bodged, so the rig carries nothing that only a bodged board would use.

## Batch 2 deltas

Three things differ from the board above. A batch-2 failure that is not on this list is
new.

1. **All 152 vias drilled** — 227 holes for 227 plated features. `assertFullyDrilled`
   matches every via and plated hole one-to-one on position *and* diameter, fails on
   orphan hits, and covers `drill_npth.drl`; it throws before any file is written.
2. **Inner-layer annular rings** on the three barrels whose only path to their pin is an
   inner-layer trace — J8.SDA (inner1), J8.SCL (inner2), J4.IO23 (inner1) — at 0.195 mm to
   plane copper. [`inner-rings.ts`](inner-rings.ts).
3. **D2 rotated**: anode to 3V3, cathode to R10. IO15/MTDO idles HIGH, so the ROM boot log
   prints and ERR idles dark. **Firmware lights ERR by driving IO15 LOW** — which is what
   the bench firmware already does, so ERR is correct on batch 2 and inverted on batch 1.
4. **U13 is a CH340B (`C81010`), not a CH340C** — both CH340C codes sat pre-order-only at
   order time. Every pin the board connects is identical; the two NC pins differ (B: RST,
   TNOW) and stay unconnected. Same CH34x driver, same 460 kbit/s flash path. The DTR lane
   moved 0.13 south with the B land's deeper pads ([`imports/CH340B.tsx`](imports/CH340B.tsx)).

First things to check on a batch-2 board, in order: does the ROM boot log print (proves
#3); does `scan` find 0x20, 0x21, 0x68 (proves #1 and #2); does esptool flash with no
buttons and does SW2 reset — the auto-reset pair has never once been demonstrated, on any
board, because EN was severed here.
