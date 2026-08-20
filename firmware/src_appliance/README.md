# The appliance controller

The firmware the machine runs. It is on the controller PCBA's own WROOM (U1), the board
[`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx) describes, flashed through that board's CH340C
over USB-C at J14. The procedure it answers to is
[`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md); the
state it boots to is the one
[`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) opens against.

`src_pcba_bench/` runs on this same WROOM and is a different instrument: a bare board,
once per fab batch, with the manifold unplugged.

## What runs today

One flavor pump. Everything else in the machine is unwritten.

- **A prime held from the glass.** Service → Prime → a flavor → hold the pad on the 4.3B
  front-face display. `MSG_PRIME_START` arrives on J9, the pump turns, a tick every 500 ms
  keeps it turning, and the head stops on the lift, on a tick that runs 2 s late, or at the
  60 s ceiling. Every state change goes back as `MSG_RESP_PRIME`.
- **A bounded run from the console.** `pump <a|b> [ms]`.
- **Status.** `MSG_STATUS_REQ` is answered with uptime, heap, J9 frame counts, the MQ-6
  divider and whether a prime is live.
- **Sound.** The whole vocabulary below, the volume and quiet-hours settings behind it,
  and the gas alarm that none of those settings can reach.

Both MCP23017s are untouched, so the eleven valves and the condenser fan stay high-Z and no
reed is read. Neither relay is ever driven. A clean cycle is answered `MSG_ERR_UNSUPPORTED`.

## The files

| | |
|---|---|
| `main.cpp` | setup, loop, the serial console |
| `machine.cpp` | every pin that reaches a load, and the three limits |
| `link.cpp` | J9 frames in, machine announcements out |
| `rtc.cpp` | U6 DS3231 — what hour it is, and whether that answer can be believed |
| `pins.h` | what this image reaches on the board, off `pcba.tsx` |
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
| `stop` | end whatever is running |
| `status` | machine state, uptime, heap |
| `link` | J9 frames, bytes, echo, time since the last frame |
| `ping` | put a frame on the pair and read its echo back |
| `sound <name>` | play one of the machine's sounds; `sound list` names them and what each would play at |
| `volume [0-100]` | how loud everything but the alarm is, persisted in NVS |
| `quiet [on\|off] [start] [end] [pct]` | quiet hours, read off the DS3231, persisted |
| `rtc [set <YYYY-MM-DD> <HH:MM:SS>]` | the clock quiet hours reads |

`ping` separates this board's half of J9 from the far end. U7's `/RE` is tied to GND, so a
frame sent here returns to IO34 through the transceiver whether or not anything is on the
other end of the pair — bytes back mean IO32, U7 and R6 carry; a frame back means the
display answered.

## Sound

The machine has one voice: U8, an MLT-5020 magnetic transducer, low-side switched by Q1 off
IO13. Neither display carries a sounder, so every sound the machine makes — including the
click under a finger on the front glass — is made here. The drive, the vocabulary and the
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
is dead or the board is fresh — `soundInQuietHours()` is false and they never engage. A
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

## Build / flash

```bash
pio run -e appliance              # compile only
pio run -e appliance -t upload    # build + flash
```

With the 4.3B also on USB, name the port — `PLATFORMIO_UPLOAD_PORT=/dev/cu.usbserial-10`.
PlatformIO otherwise picks the S3 and esptool leaves that panel dark.
