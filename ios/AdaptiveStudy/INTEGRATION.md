# Appliance app integration

The adaptive study is an executable SwiftUI presentation using local fixtures. Its
screens propose the integrated appliance app: Machine, Care, and Settings, with
the same routes in compact and wide windows. This document defines the production
work behind those screens. The study target does not communicate with a machine.

## Application scope and migration

- The app targets the integrated appliance. Remove the prototype carousel,
  prototype configuration commands, rotary image-slot interface, factory reset,
  and prototype usage charts from its product routes.
- Keep the machine directory, system accessory setup, identity reconciliation,
  selected-machine persistence, image cache, and aggregate firmware updater.
- A stored real prototype remains identified as a prototype. Do not reinterpret
  its readings, image slots, ratios, or firmware as an appliance. Its directory
  row can identify it as unsupported and offer removal through the existing
  accessory-management path. An unsupported selected record must not open an
  appliance dashboard or issue appliance commands.
- The demo uses the appliance model and the same routes and state types as a real
  appliance. Migrate the record whose `isDemo` flag is true to an appliance demo,
  retaining its directory identity. Seed labeled sample appliance state; discard
  prototype-only demo settings and charts. Demo actions operate locally and never
  open Bluetooth, install firmware, or claim a real machine was changed.
- Decode existing saved records before removing legacy model fields. Add defaults
  for new appliance fields and an explicit persistence schema migration. Preserve
  real machine identity, names, accessory IDs, selected machine, and cached art.

Existing entry points are [RootView.swift](../SodaMachine/SodaMachine/Views/RootView.swift),
[MachineDirectory.swift](../SodaMachine/SodaMachine/BLE/MachineDirectory.swift),
and [BLEManager.swift](../SodaMachine/SodaMachine/BLE/BLEManager.swift).

## Capability boundary

The radio is on the faucet. Phone commands reach it over the existing framed BLE
transport, then travel over J3 to the main board when required. The main board
owns machine state and persistence. The enclosure reaches it independently over
J9. A command supported on J9 or the USB console is not automatically a BLE
command.

| Product function | Existing capability | Production integration |
| --- | --- | --- |
| Add, choose, rename, remove a machine | Accessory setup, advertisements, identity reads and `IDENTITY <name>` | Reuse directory/accessory integration and naming acknowledgement |
| Flavor faces and custom photos | BLE image query/read/upload/erase and art query/set | Reuse image transport, CRC cache, crop, queue, and main-board art acknowledgement |
| Software Update | BLE version reports and aggregate OTA transport | Reuse catalog, download validation, sequencing, and post-restart verification |
| Active flavor / Use at faucet | Tokenized main-board flavor selection and state on display links | Add typed BLE selection request and authoritative selection notifications |
| Reservoir levels, temperatures, operation status | `StatusPayload` on J9 | Add J3/BLE query and response forwarding with freshness metadata |
| Mixing ratio | Main-board `MSG_RATIO_QUERY/SET`, `MSG_RESP_RATIO` | Add channel-scoped BLE intent and authoritative pair readback |
| Fill and Clean | Main-board start/query/stop and complete operation snapshots on J9 | Add routed J3/BLE intents and operation snapshot notifications |
| Prime | Enclosure-owned session; either physical display can hold its pad | Add narrowly targeted Open Prime, session query, and cancel through the phone bridge; no phone hold command |
| Sound and quiet hours | Main-board sound configuration get/set/readback on J9 | Add J3/BLE configuration routing and expose clock validity |

The current faucet BLE dispatcher handles identity, images, and OTA. Other phone
text is logged as diagnostic text; it does not execute the main-board console.
See [ble_link.cpp](../../firmware/src_faucet/ble_link.cpp) and
[faucet_link.cpp](../../firmware/src_appliance/faucet_link.cpp). The underlying
machine payloads and limits are in
[proto_msg.h](../../firmware/lib/proto_link/proto_msg.h); J9 handlers are in
[link.cpp](../../firmware/src_appliance/link.cpp).

## Proposed service contract

Define a versioned, typed appliance service over framed BLE. Allocate its frame
IDs alongside the shared protocol. Advertise/query its supported operations so
an app connected to firmware without the bridge can identify the missing
capability and offer Software Update. Missing support must not look like an empty
reservoir, a zero reading, or a successful write.

The bridge carries request IDs, operation/channel arguments, and correlated
responses. The faucet retains the requesting BLE connection for direct replies;
authoritative changed state may be published to every connected phone. Reconnect
reads a complete snapshot instead of replaying an actuator command. Keep the
existing separate image and OTA framing and flow control.

Route intents to main-board operations through a shared typed handler or explicit
J3 handlers. Preserve each response's destination and the main board's checks and
endings. Do not expose an arbitrary console-command tunnel or a general
bench-navigation endpoint as the product API.

Channel-specific changes identify channel 0 or 1 and carry the main board's
result. The two flavors have independent art and ratios. For a ratio SET that
internally uses the existing two-channel payload, the main board merges the
selected channel with its own current other-channel value. A phone must not
overwrite the other channel from a stale cached pair. Apply the same authority
rule to active-flavor selection and art updates.

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
  result. There is no customer temperature-setpoint command in this proposal.

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

Expose a narrow `openPrime(channel)` bridge operation. Its J9 request is
`MSG_UI_SHOW` with `UI_RAIL_PRIME`, the selected channel, and `act = 0`. The
enclosure's existing handler opens `SVC_PRIME_HOLD`. A successful UI-show response
means the screen was shown; wait for the main board's matching READY session
before telling the phone it is ready to prime. A failed/busy/no-answer result
leaves the app in preparation with an explanation.

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

Layout verification belongs to this implementation task: compact portrait,
short landscape, near-square expanded phone, iPad portrait/landscape, narrow
resizable iPad window, and accessibility text sizes. Keep selection, edits, and
operation state outside layout branches so resizing does not restart work.
This proposal adds no automatic build or commit checks.
