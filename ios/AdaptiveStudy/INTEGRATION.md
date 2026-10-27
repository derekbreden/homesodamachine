# Appliance app integration

The adaptive study is an executable SwiftUI presentation using local fixtures:
Machine, Care, and Settings, with the same routes in compact and wide windows.
The production app in [`ios/SodaMachine`](../SodaMachine) builds those screens on
the machine's own state. This document is the behavior behind them. The study
target does not communicate with a machine.

## Application scope

- The app targets the integrated appliance: the machine directory, system
  accessory setup, identity reconciliation, selected-machine persistence, the
  image cache, and the aggregate firmware updater, under the three destinations.
- A saved machine whose advertisement carries no appliance model byte runs the
  prototype's firmware. It is listed as a prototype, never connected to, and can
  be removed through the accessory-management path; selected, it shows a page
  that offers removal or another machine.
- The demo is an appliance with the same routes and state types as a real one,
  seeded with sample state. Its actions play out on the device and never open
  Bluetooth, install firmware, or claim a real machine was changed.
- Saved records are schema 2: each carries its appliance readings with their read
  times. A schema 1 file's demo becomes an appliance on load, keeping its place
  and name; every other record keeps its identity, name, accessory ID and art.

Entry points are [AppShell.swift](../SodaMachine/SodaMachine/Views/AppShell.swift),
[MachineBridge.swift](../SodaMachine/SodaMachine/BLE/MachineBridge.swift),
[MachineDirectory.swift](../SodaMachine/SodaMachine/BLE/MachineDirectory.swift),
and [BLEManager.swift](../SodaMachine/SodaMachine/BLE/BLEManager.swift).

## Capability boundary

The radio is on the faucet. Phone commands reach it over the existing framed BLE
transport, then travel over J3 to the main board when required. The main board
owns machine state and persistence. The enclosure reaches it independently over
J9. A command supported on J9 or the USB console is not automatically a BLE
command.

| Product function | How the phone reaches it |
| --- | --- |
| Add, choose, rename, remove a machine | Accessory setup, advertisements, identity reads and `IDENTITY <name>` |
| Flavor faces and custom photos | BLE image query/read/upload/erase and art query/set |
| Software Update | BLE version reports and aggregate OTA transport |
| Active flavor / Use at faucet | Bridge: `MSG_FLAVOR_QUERY`, tokenized `MSG_FLAVOR_SELECT`; changes published |
| Reservoir levels, temperatures, operation status | Bridge: `MSG_STATUS_REQ`, answered with `StatusPayload` |
| Mixing ratio | Bridge: `MSG_RATIO_QUERY`, and `MSG_RATIO_SET_ONE` for one channel; answered with the pair |
| Fill and Clean | Bridge: start, query and stop, each answered with the complete state; every change published |
| Prime | Bridge: `MSG_PRIME_OPEN`, `MSG_PRIME_SESSION_QUERY`, and current-token CANCEL; no hold |
| Sound and quiet hours | Bridge: `MSG_SOUND_CFG_GET/SET`, answered with clock-valid and quiet-now flags |

The faucet's BLE dispatcher handles identity, images and OTA itself and carries
everything else a phone asks to the main board. See
[phone_bridge.cpp](../../firmware/src_faucet/phone_bridge.cpp) for the faucet's
half and [faucet_link.cpp](../../firmware/src_appliance/faucet_link.cpp) for the
main board's list of what a phone may ask. The payloads and limits are in
[proto_msg.h](../../firmware/lib/proto_link/proto_msg.h); J9 handlers are in
[link.cpp](../../firmware/src_appliance/link.cpp).

## The bridge

A phone writes `BLE_FRAME_MACHINE_REQ` (0x23): a request id, a `MSG_*` request
type, then that request's own payload as J9 carries it. The faucet puts it on J3
as `MSG_BRIDGE_REQ` under an id of its own and returns the main board's answer
as `BLE_FRAME_MACHINE` (0x24) — the same id, then the `MSG_RESP_*` frame the
request gets on J9 — to the phone that asked. State that moved reaches every
phone on the air under id 0: fill and clean changes from the main board, and the
selection and Prime's session, which J3 already brings the faucet. Image and OTA
framing and flow control are separate and unchanged.

Answering `IDENTITY`, the faucet sends `BLE_FRAME_BRIDGE` (0x25) with the
bridge's version. An app connected to a faucet that sends none identifies the
missing capability and offers Software Update; missing support never looks like
an empty reservoir, a zero reading, or a successful write. A main board that
predates the bridge is reported as `BRIDGE_ERR_NO_BRIDGE` the same way.

The faucet answers a request the main board leaves unanswered for two seconds
with `BRIDGE_ERR_NO_ANSWER`, a full queue with `BRIDGE_ERR_BUSY`, and a request
it could not deliver with `BRIDGE_ERR_LINK_DOWN`. Reconnect reads a complete
snapshot. The main board answers anything off its list `BRIDGE_ERR_REFUSED`.

Channel-specific changes identify channel 0 or 1 and carry the main board's
result. The two flavors have independent art and ratios. `MSG_RATIO_SET_ONE`
names one channel and the main board keeps the other at what it holds; a value
outside 1:6–1:24 changes nothing and the answering pair says so. Selection is
absolute and tokenized, and art is set as a pair the phone reads first.

Persist confirmed machine snapshots per machine with read times. Pending UI
edits are separate from confirmed values. A successful BLE write means transport
acceptance; the screen marks a change saved only after the relevant machine
response. Changes made on either display also refresh the phone's model.

## Machine and flavor screens

- Read the active flavor and both channels' artwork, ratios, and reservoir levels.
  The active-flavor marker describes the main board's selection. Opening a flavor
  detail page does not itself select that flavor for dispensing; Use at faucet
  sends an explicit absolute selection request.
- Reservoir level is an integer from 0 through 4, or `LEVEL_UNKNOWN`. Four visual
  segments represent this coarse gauge. Do not derive exact percentages, liquid
  volume, servings, or time remaining from it. Respect `LEVEL_F_VALID`; retain an
  unknown state until the machine has a valid reading.
- `tankCx10` is the carbonator wall temperature in tenths of a degree Celsius.
  Label it Tank wall. Convert to the device's locale-appropriate Celsius/Fahrenheit display
  without changing the underlying reading. `TEMP_UNREAD` is unavailable, not zero.
  Temperature formatting follows this device's locale.
- Cooling and refill states are machine enums, separate from the temperature.
  Carbonator low/high reed flags describe water level. A high reed can support
  Carbonator full; it does not establish measured carbonation or outlet readiness.
  The UI must distinguish a stale phone snapshot from valid current sensor data
  and from a sensor the connected machine cannot read.
- Ratios are concentrate : water, `1:6` through `1:24`. A smaller denominator
  means more flavor. Save the selected channel and display the acknowledged
  result. The app has no customer temperature-setpoint command.

Poll status while its information is visible and after reconnect or a relevant
command. Record the receipt time and stop presenting the snapshot as live after
its expected response window expires. Honor the payload's own validity/sentinel
fields as well. Stop polling offscreen or in the background; read current truth
on return. Simulated firmware readings retain a visible simulated designation.

## Fill and Clean

Both operations act on one explicitly selected flavor. Their UI states are
Preparing, Starting, Running, Stopping, and a machine-confirmed result. A refused
start has its own reason. Querying or observing an operation started on another
display opens the same progress state.

Fill instructions are Pour concentrate into the top funnel. The main board draws
it into that flavor's reservoir for the planned run, normally 80 seconds, and
ends early when the full reed closes. Progress describes elapsed/planned time,
not a measured fraction of concentrate transferred. Results distinguish Filled
(planned run finished), Full (concentrate may remain in the funnel), Stopped
(the rest remains in the funnel), Busy, unverified I/O, fault, and gas alarm.
Use fill-specific result copy and retain the selected channel through every
transition.

Clean instructions are Place a pitcher under the faucet. The initial stage pumps
the funnel path out through the faucet. Then three rinse rounds fill the reservoir
with tap water and pump it out through the faucet. Use the machine's stage,
round/count, elapsed/planned stage time, and `cycleLeftMs` estimate. Do not start
the displayed cycle at Round 1 while the funnel stage is running. A normal result
says the rinse completed; an early stop says water may remain in the reservoir.

START and STOP receive complete operation snapshots. Keep Starting or Stopping
visible until the matching state arrives. Dedupe request retries at the bridge;
do not replay START after reconnect or infer completion from a local timer.
When the phone loses contact, say the cycle may still be running and direct the
person to the machine display. Fill/Clean can continue independently of the phone.
Recover by querying their actual state.

The main board refuses a new operation while busy, with unverified I/O, or during
the gas alarm, and reports fault endings. The app mirrors these results and
prevents stale-state starts. Keep the selected machine and operation identifiable
throughout progress and results. Operation navigation and any machine-switch
affordances must agree about whether the active task can be left; a switch never
implicitly stops a machine or changes its operation's ownership.

## Prime through the physical displays

The phone's Prime action opens the selected flavor's Prime screen on the enclosure.
The enclosure creates and renews the existing main-board session; the enclosure
or faucet pad supplies the physical hold. The phone monitors and can exit that
session. It never sends pump hold START/TICK/STOP and is not a new hold owner.

The phone's Prime is `MSG_PRIME_OPEN`. The main board asks the enclosure for
`MSG_UI_SHOW` with `UI_RAIL_PRIME`, the selected channel, and `act = 0`, without
holding its loop, and answers `MSG_RESP_PRIME_OPEN` with whether the page went
up, or that the enclosure did not answer within 5 s. The enclosure's existing
handler opens `SVC_PRIME_HOLD`. Shown means the screen was shown; the app waits
for the main board's matching READY session before telling the person it is
ready to prime. A refused or unanswered result leaves the app in preparation
with an explanation.

Read `PrimeSessionStatePayload` for phase, channel, owner, outcome, elapsed time,
revision, session token, and hold token. While RUNNING, the app can say which
physical display holds the pad. A current-token CANCEL implements Exit Prime;
confirm OFF from the authoritative state. Cancellation must reach the matching
session and the enclosure's UI must reconcile to that ending. An old phone view
must not cancel a newer session using a cached token.

The existing physical session safeguards remain in force: 500 ms hold feeds,
2-second late-feed stop, 60-second hold ceiling, loss of the owning faucet link,
and the enclosure's 5-second lease. App backgrounding does not generate feeds
or extend a physical hold. A disconnected phone cannot confirm or cancel the
session; its screen directs the person to the machine. The enclosure remains
responsible for its own lease. See
[machine.h](../../firmware/src_appliance/machine.h),
[faucet_link.cpp](../../firmware/src_appliance/faucet_link.cpp), and
[main.cpp](../../firmware/src_front/main.cpp).

## Sound, pictures, naming, and updates

Sound configuration contains volume 0–100, quiet enabled, start/end whole hours
0–23, and quiet volume 0–100. Start after end wraps midnight. Use hour-only
pickers. Quiet volume is a ceiling; it must not increase a lower normal volume.
Configuration readback carries clock-valid and quiet-now flags. A saved schedule
with an invalid machine clock is shown as inactive/unavailable. Neither volume
control silences the gas alarm.

Reuse custom image upload/readback, queue cancellation, CRC caching, delete
confirmation, and free-slot accounting from
[ImageUpload.swift](../SodaMachine/SodaMachine/BLE/ImageUpload.swift). Four factory
faces and four custom slots are shared across channels. Preserve the single
43:80 crop used by both displays and its edge-extension behavior. Photo selection
uses the native photo picker. Factory PNGs are center-cropped to the same shape.
Custom-art activation and an upload failure must reconcile to the machine's
actual accepted art; do not promise that the previous face remains unchanged
unless the activation sequence guarantees that behavior.

Reuse the machine-owned name and explicit identity acknowledgement, including
the existing pending-name behavior when naming offline. Removing a machine
removes it from this device's accessory/directory state, with confirmation; it
does not factory-reset the appliance or delete another device's record.

Reuse [FirmwareUpdate.swift](../SodaMachine/SodaMachine/BLE/FirmwareUpdate.swift)
and the existing aggregate update model. One Software Update page covers the
whole machine. Render catalog/check failure, waiting for machine, update ready,
sending, restarting, checking, verified current, interruption, and machine not
returned. Unknown board versions are not proof of current software. Cancel is
offered only while the existing updater can cancel; byte transfer completion is
not installation success. Demo update behavior remains clearly simulated.

## Shared availability and error behavior

Connection state belongs to the selected machine model, not to a route. Offline
and Bluetooth-off states persist while browsing its screens. Keep cached art and
readings available with their read time, but disable machine-dependent changes
and Care starts until the relevant link and capability are available. Name
queueing retains its existing explicit behavior; actuator operations are never
queued for later execution.

Represent these independently: no reading yet, invalid sensor, stale snapshot,
out of range, Bluetooth off, firmware capability unavailable, another operation
running, start refused, gas alarm, I/O fault, unconfirmed stop, and lost contact
during an operation. Image errors preserve retry/cancel choices and the machine's
confirmed selection. The demo supplies deterministic examples of these states,
not invented usage history.

The layout answers compact portrait, short landscape, near-square expanded
phone, iPad portrait and landscape, a narrow resizable iPad window, and
accessibility text sizes. The tab, the pages, and a run in progress live in the
app's Navigator, outside the layout branches. Nothing here adds an automatic
build or commit check.
