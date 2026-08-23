# The appliance controller

The firmware the machine runs. It is on the main board's own WROOM (U1) — the board
[`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx) describes — flashed through its CH340B
over USB-C at J14. The procedure it answers to is
[`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md); the
state it boots to is the one
[`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) opens against.

`src_pcba_bench/` runs on this same WROOM and is a different instrument: a bare board,
once per fab batch, with the manifold unplugged.

## What runs today

The glass-facing operation remains one flavor pump. The main board also establishes and
reports the safe I/O foundation the next connected bench uses.

- **A shared prime-ready session.** Service → Prime → a flavor on the 4.3B enclosure display
  opens a main-board-owned session and wakes the faucet into the same mode. Either display
  can hold its pad to run that selected pump; tokenized `MSG_PRIME_SESSION_*` controls keep
  retries idempotent and the complete absolute state is mirrored to both displays. The pump
  stops on lift, a hold heartbeat more than 2 s late, loss of its owning faucet connection,
  expiry of the enclosure's 5 s session lease, or the 60 s ceiling.
- **A bounded run from the console.** `pump <a|b> [ms]`.
- **The shared flavor selection.** A faucet tap reaches J3, or an enclosure card tap reaches
  J9, as an absolute flavor and request token. The main board acknowledges its authoritative
  selection, makes the UI tick once, persists namespace `selection`, key `flavor`, and
  publishes the revision to the other display. A main board with no stored value adopts the
  faucet's saved boot-logo candidate on its first synchronization; an established main board
  wins.
- **Status.** `MSG_STATUS_REQ` is answered from cached main board state with uptime, heap,
  J9 frame counts, the MQ-6 divider and whether a prime is live. The USB `status` command
  additionally verifies both expanders and reads all ten reed inputs on demand.
- **Sound.** The whole vocabulary below, the volume and quiet-hours settings behind it,
  and the gas alarm that none of those settings can reach.

At boot both MCP23017 output latches are cleared before Port A becomes output, their complete
safety configuration is read back, and Port B gets the internal pull-ups the reed looms rely
on. No runtime operation opens a valve or runs the condenser fan. Neither relay is ever
driven. A clean cycle is answered `MSG_ERR_UNSUPPORTED`.

## The files

| | |
|---|---|
| `main.cpp` | setup, loop, the serial console |
| `machine.cpp` | every pin that reaches a load, and the three limits |
| `pcba_expanders.cpp` | U2/U3 register safety and the logical V-A–V-K / fan / reed map |
| `link.cpp` | J9 frames in, machine announcements out |
| `faucet_link.cpp` | J3 full-duplex flavor acknowledgements and shared-prime controls/state |
| `flavor.cpp` | main-board-owned flavor state and deferred NVS persistence |
| `rtc.cpp` | U6 DS3231 — what hour it is, and whether that answer can be believed |
| `pins.h` | what this image reaches on the main board, off `pcba.tsx` |
| [`/firmware/lib/sound`](/firmware/lib/sound/sound.h) | U8, IO13, and the machine's sounds — shared with the bench |

`machine.cpp` is the only file that drives an actuator pin. The glass, the console, and the
faucet when it exists all reach it through `machine.h`, and the commissioning and service
commands (§6, §7, §9) are serial commands on this image asking it for a thing.

## Console

115200 baud, over the same USB-C cable you flash with.

```bash
pio device monitor -e appliance
```

| | |
|---|---|
| `pump <a\|b> [ms]` | run one flavor pump, bounded — default 2000, ceiling 60000 |
| `flavor [a\|b]` | read or set the main-board-owned flavor selection, and the logo pair beside it |
| `art [<a> <b>]` | read or set which logo each channel wears, persisted in NVS and published to both glasses |
| `stop` | end whatever is running |
| `status` | machine state, uptime, heap, verified MCP configuration/output park, all ten reeds |
| `link` | J9 frames/echo plus J3 connection, synchronization, state heartbeats, duplicates and invalid frames |
| `ping` | put a frame on the pair and read its echo back |
| `display usb` | explicitly detach/wake the enclosure display's USB PHY |
| `sound <name>` | play one of the machine's sounds; `sound list` names them and what each would play at |
| `volume [0-100]` | how loud everything but the alarm is, persisted in NVS |
| `quiet [on\|off] [start] [end] [pct]` | quiet hours, read off the DS3231, persisted |
| `rtc [set <YYYY-MM-DD> <HH:MM:SS>]` | the clock quiet hours reads |

`ping` separates the main board's half of J9 from the far end. U7's `/RE` is tied to GND, so a
frame sent here returns to IO34 through the transceiver whether or not anything is on the
other end of the pair — bytes back mean IO32, U7 and R6 carry; a frame back means the
display answered.

`display usb` does not switch a load or the unswitched J9 V12 rail. A current enclosure display
image acknowledges it and enters 500 ms of timer-wake deep sleep, which powers down the S3
USB PHY long enough for the host to see a detach. If that application does not answer,
the main board reports `UNREACHABLE` and does nothing further. `tools/display_usb.py`
wraps the command and proves the result with a fresh USB attachment and the display's
`GET_VERSION` response.

## Faucet link

J3 is not RS485. `Serial2` maps IO33 TX / IO35 RX to the faucet's GPIO44 RX / GPIO43 TX
over separate 3.3 V logic conductors. `ProtoLink` therefore runs its full-duplex Fd transport
at 115200 baud; ROM boot text from faucet GPIO43 is simply discarded until framed traffic
passes CRC.

The touch display changes its logo before it queues link work. Requests carry the resulting
absolute flavor, never “toggle,” so transport or application retries are idempotent. A token
deduplicates the main-board-side tick as well as the state update. Main board Preferences
writes are serviced only while the machine is idle and the sound sequencer is quiet. The
faucet keeps its own two-second-deferred cache so either boot order draws a logo immediately,
but it never overwrites established main board state during reconnect.

An established main board publishes every flavor or persistence revision immediately and repeats
the complete absolute state every 500 ms while J3 is connected. The repeat closes the gap between
transport acceptance and application of a single frame. A same-state publication is a no-op on the
faucet, so it neither wakes the backlight nor resets the idle timer; a changed state updates and
wakes it. Connection-epoch cleanup happens before the first application frame in that epoch, so a
SYNC accepted during connection establishment cannot be erased afterward.

## Enclosure flavor link

J9 is half duplex, so the main board does not interrupt the enclosure display when flavor
changes on J3. The enclosure asks with `MSG_FLAVOR_QUERY` every 250 ms while lit and every
500 ms while dark, and the main board answers with the current flavor and persistence flags.
That bounded poll is also how a faucet selection wakes and updates a sleeping enclosure.

An enclosure card press repaints locally and sends tokenized `MSG_FLAVOR_SELECT`. The first
fresh request carries the audible flag; retries reuse the absolute value and token without
repeating the tick. The resulting main board revision is published immediately over J3, so
the faucet changes and wakes without waiting for another enclosure poll.

## Sound

The machine has one voice: U8, an MLT-5020 magnetic transducer, low-side switched by Q1 off
IO13. Neither display carries a sounder, so every sound the machine makes — including the
click under a finger on the enclosure display's glass — is made here. The drive, the vocabulary and the
settings are [`/firmware/lib/sound`](/firmware/lib/sound/sound.h), shared with
`src_pcba_bench` so the factory hears exactly what a customer hears.

`soundService()` runs from `loop()` and never blocks. That matters: LEDC keeps oscillating
in hardware once set, so a sequencer that stops being serviced leaves ~100 mA in the coil
indefinitely, and a player built on `delay()` would stall the prime deadlines and the
thermal loop for the length of every sound it played.

### The loudness budget

`sin(pi*d)` spends about 24 dB between a 2% pulse and a 50% one, and that is the entire
dynamic range this machine has. It is spent deliberately — the tick a user hears hundreds of
times sits at the bottom, and the gas alarm holds the top alone:

| | priority | duty | why |
|---|---|---|---|
| `tick` | ui | 26 | a touch registered — 27 ms of body, tip and release, no pitch in it |
| `ack` | event | 18 | something was committed |
| `chime` | event | 30 | an operation finished |
| `refuse` | event | 40 | off resonance, so quiet and dull by physics as well as by level |
| `welcome` | event | 28 | the boot chime — a major triad arpeggiated, restated a third higher, into resonance |
| `fault` | fault | 34 | needs attention, nothing is leaking |
| `alarm` | ALARM | 50 | gas trip — loops, and cannot be silenced |
| `engage` | event | 24 | a held control took — a rising sweep |
| `release` | event | 24 | it let go, deliberately or not — the mirror, falling |
| `note` | ui | — | a scratch note `soundPlayNote()` fills; pitch is the reading |

A request below what is already sounding is dropped, not queued: there is one coil, and a
tick arriving mid-chime is worth less than the chime finishing.

`tick`'s duty looks high against the rest of that column and is not: the ear integrates
energy over 100–200 ms, and none of `tick` lasts 30. Duration is doing most of the
attenuation, which is what lets the most-repeated sound in the machine be something you can
feel under a finger without eating the alarm's headroom.

`tick` means **your touch registered**, not "that worked". If success were the only thing
that sounded, silence would mean both "you missed the glass" and "the machine refused you",
and on a capacitive panel with no travel those are the two a user cannot otherwise tell
apart. Outcomes get their own sounds.

### The sound of a hold

A prime is the one thing here a person does by holding still, and the pump is loud
enough that *is it running* answers itself. Two things the noise does not answer, and
these do:

- **Did the pad take, and has it let go?** The glass has no travel and no detent, a finger
  sliding off ends the hold exactly as lifting does (`PRESS_LOST`), and a pump spins down
  the same either way. `engage` and `release` are a matched pair — same duty, same span,
  mirrored — so a slip is unmistakable without looking at anything.
- **How long have I been holding?** The pitch is the progress bar. Once a second the hold
  speaks a short note, climbing from 2200 Hz toward the resonance as the 60 s ceiling
  nears — so it grows more present as well as higher, without anything having to get
  faster or louder to say so. It stays a tick rather than a tone: a tone held under a
  running pump for a minute is a thing people learn to hate, and it would mask the pump.

The two endings that are the machine's decision rather than the finger's — a display that
stopped answering, and the ceiling — get `fault` instead of `release`.

### What can be silenced, and what cannot

`volume` scales everything except `alarm`, and so do quiet hours. The exemption is
`SND_F_UNSILENCEABLE`, checked in one place (`soundLevelFor`), and `alarm` is the only sound
that carries it — a gas alarm a volume setting could mute would be a safety defect. `volume
0` is a real mute for every other sound.

Volume is linear in acoustic **amplitude**, not in duty: amplitude goes as `sin(pi*d)`, so a
control that scaled duty directly would barely move across the top half of its travel.

Quiet hours need a clock. Without a believable one — no DS3231, or OSF latched because BT1
is dead or the main board is fresh — `soundInQuietHours()` is false and they never engage. A
machine that guessed at the hour in order to go quiet would go quiet at the wrong one.

### The gas alarm

`machine.cpp` watches the MQ-6's divided comparator output and sounds `alarm` on a trip that
holds 500 ms, stopping it when the trip clears for as long. U15 already holds the compressor
off that same signal in hardware with no firmware in the path — that interlock is the
safety, and this is not it. This is the part a person needs: the trip made audible, so a
leak in an empty kitchen is heard from another room.

## The three limits

They are in `main.cpp`'s header, in
[`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md) §9 where
the factory confirms them per unit, and in [`/firmware/README.md`](/firmware/README.md) with
the part that pays for each. At most 3 solenoid valves energized at once; relay #2 off while
a dispense is open; `GPPU` written on both MCP23017s.

The canonical operation plans and timing policy live in
[`/firmware/lib/machine_policy`](/firmware/lib/machine_policy/machine_policy.h). They have no
Arduino dependency, so `pio test -e native` exhaustively checks every valve-mask transition,
the physical MCP map and failure paths, and the prime deadlines without opening a USB port or
touching a connected board.

## Build / flash

```bash
pio run -e appliance              # compile only
pio run -e appliance -t upload    # build + flash
```

With the 4.3B also on USB, name the port — `PLATFORMIO_UPLOAD_PORT=/dev/cu.usbserial-10`.
PlatformIO otherwise picks the S3 and esptool leaves that panel dark.
