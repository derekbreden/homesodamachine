# The faucet display

The Waveshare ESP32-S3-Touch-LCD-1.47 at the end of the gooseneck. Its 172×320 logo is the
glass-facing flavor selector, and its P1 GPIO43 TX / GPIO44 RX pins cross to the main
board's J3 IO35 RX / IO33 TX pins at 921600 baud.

This display carries artwork for every logo a channel can be given and renders whichever one the
main board says that channel wears — `MSG_RESP_FLAVOR_ART`, published on every change and
once per connection, so a display that just woke shows the right face before anyone touches it.
The assignment is set from the machine display's Choose card and persisted by the main board.

## Interaction contract

A bright-screen touch-down changes the logo immediately. The handler only updates LVGL state
and appends a small fixed-memory intent; UART framing, acknowledgement and both flash writes
run later from `loop()`. The normal full-screen redraw remains about 40 ms. When the main
board says both glasses are done the backlight fades to duty 8, and the first touch at that
level is consumed by the wake: it sends no flavor request and does not dirty either store.

The main board's buzzer makes the tick after the absolute selection reaches J3. A fresh tap
carries the audible flag; retries reuse the same token, so a lost response cannot make a
second tick. An offline or sufficiently delayed selection reconciles silently rather than
playing feedback detached from the touch that caused it.

A different main board selection, including one made on the machine display, changes the
logo and wakes the backlight. Re-publication of the flavor already shown is a no-op and does
not disturb idle behavior.

When the machine display opens Prime for one flavor, main board state replaces the logo
with two exact half-screen targets: `EXIT PRIME` on top and `HOLD TO PRIME` below. The faucet
does not create prime mode; it can end the existing mode or own a held run for its selected
channel. A hold from either display is shown on both, and an entering, starting, or ending
session wakes a dimmed faucet. The first touch while dimmed remains wake-only.

Service and update screens use the Big Blue palette: cobalt background, navy exit target,
and an orange hold target with navy text. Active priming remains green and pending or
reconnecting states use ice blue. The resting screen shows the selected flavor's own artwork.

**The main board keeps the quiet stretch, across both glasses.** A finger on either is
activity for both, so this head does not dim while a hand is at the machine display, and the pair
sleeps and wakes together. It runs no timer of its own and dims when it is told to; a press
that already sent a command is presence the main board can see, and one that stayed silent —
a wake tap, a tap on the flavor already showing — sends `MSG_TOUCH` so it counts too. A live
hold still holds the dim off here regardless. A pair left lit is a link that stopped talking.

Each faucet press retains its main board session and hold tokens across retries. Lift or
`PRESS_LOST` queues an absolute STOP ahead of any unsent feed, and EXIT queues an absolute
CANCEL. If J3 disconnects, the main board stops a faucet-owned run independently of the UI,
while its 2 s hold-heartbeat and 60 s run limits remain in force.

## A phone

The radio is a GATT server on the Nordic UART service ([`ble_link.cpp`](ble_link.cpp)). A
phone asks who the machine is and names it (`IDENTITY`), sends and reads back pictures
([`ble_image`](/firmware/lib/ble_image/ble_image.h)), and updates every board's software
([`ble_ota`](/firmware/lib/ble_ota/ble_ota.h)). Everything else it asks of the machine —
status, the selection, a flavor's ratio, the fill, the clean cycle, sound, and Prime's
session — this display carries to the main board ([`phone_bridge.cpp`](phone_bridge.cpp)):
`BLE_FRAME_MACHINE_REQ` becomes `MSG_BRIDGE_REQ` on J3 under an id of this board's own, and
the main board's answer goes back to the phone that asked under the phone's id. What a phone
may ask is the main board's list; anything else is answered refused. State
that moved — a fill or clean cycle stepping or ending, the selection, Prime's session — goes
to every phone on the air under id 0. A request the main board does not answer in time is
answered as unanswered, and the phone reads the truth with a query.

Answering `IDENTITY`, this display also sends `BLE_FRAME_BRIDGE` with the bridge's version,
which is how a phone tells this display from one that predates the bridge, and
`BLE_FRAME_TRUST` with where that phone stands.

### Pairing and trust

A phone pairs once, inside Apple's setup sheet: Just Works, bonded, LE Secure Connections, no
passkey. Subscribing to TX takes an encrypted link, and iOS meets that refusal by encrypting
under the phone's bond, without asking anyone, or by asking the owner of a phone with no bond
to pair. A link is taken as the bonded phone it is from the stack's word that encryption
changed or from the first frame that arrives encrypted, whichever comes first, and the bond's
identity address is how the phone is known on every later connection. NimBLE keeps up to 16
bonds in NVS.

Every phone reads everything. Changing anything — a request over the bridge that is not a
read, a picture, a face, an update, the name — takes a phone this display trusts
([`phone_trust.cpp`](phone_trust.cpp)), and a change from any other phone is refused in the
form its own answer takes: `BRIDGE_ERR_UNTRUSTED`, an image or update ending with its
`_UNTRUSTED` error, the faces as they stand, `ERR:IDENTITY:UNTRUSTED`.

A phone asks to be trusted with `BLE_FRAME_TRUST_ASK` (reason, channel, iPhone or iPad). The
ask goes up here and, through the main board, on the enclosure (`MSG_TRUST_SHOW`): **Trust
this iPhone?**, what the phone wants, and what trusting it allows, in
[`trust_text.h`](/firmware/lib/proto_link/trust_text.h)'s words. **Trust** or **Don't Trust**
on either display answers for both; the ask also ends after a minute, when the phone
withdraws it, or when it leaves, and `MSG_TRUST_CLOSE` takes the other display's copy down.
The phone hears how it ended, and where it now stands, as `BLE_FRAME_TRUST`. One ask is up at
a time; another phone asking meanwhile is told the machine is busy. A phone with no bond is
asked to pair again instead, which iOS puts to its owner.

Trusted phones are kept in NVS namespace `trust` by identity address, sixteen at most, oldest
dropped first, through every restart and update, until **Forget trusted phones** on the
enclosure (`MSG_TRUST_FORGET`) or `trust forget` on the main board's console forgets every one.

## State and persistence

The main board owns flavor truth. This display keeps a cache only so boot can draw the last
logo without waiting for another board. On connection it sends one of two messages:

- `MSG_FLAVOR_SYNC` offers the cached value. Only a main board with no valid stored selection
  adopts it; an established main board answers with its own value.
- `MSG_FLAVOR_SELECT` carries the absolute result of a local touch or USB selection. Requests
  are tokenized and retried idempotently until the main board answers.

Main board persistence is acknowledged separately from selection acceptance. The main board
writes after 500 ms in a quiet idle loop; this display writes its cache after two seconds of
flavor quiet. Failed writes remain pending and are reported in diagnostics. Reconnect sends
the final desired absolute selection, not a backlog of toggles. Until the main board reports
that selection durable, it remains unfinished faucet input and is reasserted after a reconnect;
that pending user input therefore takes precedence over a development-console edit made while
J3 is disconnected.

## USB diagnostics

The native USB console is 115200 baud:

| Command | Result |
|---|---|
| `GET_VERSION` | build identity |
| `GET_STATE` | local/main board flavor, sync, pending and persistence state |
| `GET_DIAG` | touch/UI high-water marks plus J3 frames, retries, queue drops, ack latency, and the logo pair (`art=`) with the one on screen (`showing=`) |
| `TOGGLE` | exercise the local-first user path |
| `FLAVOR:0` / `FLAVOR:1` | select an absolute flavor through the same path |
| `BL:n` | development-only raw backlight duty |

The safe live check observes this data without opening the main board's reset-capable CH340C
port or driving any load:

```bash
~/.platformio/penv/bin/python tools/firmware_faucet_check.py
```

`--toggle` changes the flavor once, proves main board and cache persistence, and restores the
selection in a `finally` block. It does not run a pump or valve; two main board ticks are the
expected audible result.

Build and flash with an explicit port whenever another board is attached:

```bash
pio run -e esp32s3_faucet
PLATFORMIO_UPLOAD_PORT=/dev/cu.usbmodem... pio run -e esp32s3_faucet -t upload
```
