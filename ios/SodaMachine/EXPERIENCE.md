# Appliance app experience

The app has three destinations: **Machine**, **Care**, and **Settings**. Every
reading, edit, and operation identifies the appliance it belongs to. Available
width changes the arrangement of these destinations; it does not change the
person's location, pending edits, or task.

Use the platform's navigation components: native navigation stacks, a TabView
with the sidebar-adaptable style, menus, and task-scoped sheets. iPhone and iPad
use the system's tab and sidebar arrangements. Appliance cards and content keep
their palette and bounded layout. Familiar interactions, clear feedback, and
preserved context follow Apple's [design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles),
[tab guidance](https://developer.apple.com/design/human-interface-guidelines/tab-bars),
and [modality guidance](https://developer.apple.com/design/human-interface-guidelines/modality).

## Navigation and appliance context

Each destination has its own navigation stack. A pushed page has ordinary Back
navigation and an interactive edge-pop. Each page owns its scrolling region.
Changing tabs, resizing a window, or rotating a device preserves navigation and
editing state. Routine polling belongs to the top page of the selected tab.
Operation and transfer tracking, reconnection recovery, and task restrictions
remain active independently of which page is visible.

The current machine's name and connection state remain visible. With multiple
known machines, its name opens a native menu with the current machine checked
and an **Add a machine** action. With one machine, its identity is plain text.
Choosing a different machine deliberately opens its Machine overview. Selecting
the checked machine leaves the current task in place.
Machines with colliding display names include their known unit identifiers.

**Your machines** is an explicitly named, app-level management presentation,
available from Settings. It remains available independently
of whether a machine is selected. A record can be removed without opening that
machine first. **Open machine** deliberately selects it, closes management, and
opens its overview, including when it is already selected.

Removing a noncurrent machine preserves the current appliance and the page
underneath management. Removing the current machine keeps management open with
no automatic replacement. Remaining records are offered for explicit selection.
When no records remain, closing management reveals first-run setup. A directory
with records and no selection offers **Choose a machine**.

Removal completes the system accessory relationship before clearing a
system-managed record from the app. A temporarily unavailable accessory session
does not mean the machine is unpaired. A failure retains the record and explains
how to retry. Removal leaves the appliance's shared name and settings intact;
re-pairing establishes a fresh device relationship and requires machine Trust.

## Editing and confirmation

Editing sessions belong to the machine and setting, above page presentation.
Flavor sessions also identify their channel. Back, child pages, tab changes,
and layout changes preserve drafts. **Discard changes** explicitly restores the
confirmed value. Switching appliances keeps drafts separate and never applies
one appliance's choices to another. Mix intents and submitted Name/Sound changes
are stored on this device through relaunch and reconnection. Unsubmitted form
drafts are local to the running app session.

Each saved setting carries an opaque main-board revision. A write includes the
revision the edit began with. The main board compares and applies it atomically,
or returns its current value and revision without applying the requested value.
Every mutation source advances the revision, including a change to equal bytes.
A durable boot epoch prevents an old edit matching after restart. Applied values
are persisted during the machine's quiet loop; the acknowledgement confirms the
live machine setting.

Changed settings are pushed to connected phones. A conflict retains the desired
value and offers **Use mine** or **Keep machine’s setting**. Use mine explicitly
rebases the next conditional write; it cannot bypass a later conflict. A missing
answer is unconfirmed, even if a later reading equals the desired value. The app
never infers ownership or success from matching value bytes.

An asynchronous action identifies its originating machine, page entry, and
task. A delayed response cannot close a newly opened page with the same name,
redirect another tab, or write to a different selected appliance.
Valid readback still updates the originating machine's confirmed state. It
does not clear a newer draft or complete a newer editing task.

## Machine and flavor

The Machine overview shows both flavors, the flavor on tap, coarse reservoir
levels, saved ratios, and appliance readings. Selecting a flavor opens its
detail; it does not immediately select that flavor at the faucet.

Flavor detail is the home for that channel's image and mix. Adjusting the mix
saves automatically after a short coalescing pause. The minus button and **More
flavor**, and plus button and **Lighter**, remain together. The outcome area sits
below that control group and distinguishes saving, accepted, out of range,
Trust needed, declined, expired, unconfirmed, and conflict. A pending value
never replaces the machine's confirmed ratio in the **On tap** description.

An out-of-range mix is kept and sends automatically on reconnection under its
original revision. It requires no extra resend tap. A changed revision produces
a conflict, including when another source changed the value away and back.
**Use at faucet** waits for the latest desired mix to be accepted, then conditionally
sets the active flavor. The page stays in place and shows the confirmed selection.
Back remains the way to the overview. Editing requires a stamped baseline;
an unread mix is unavailable rather than an invented ratio.

Change image opens a child task and returns to the same flavor with its ratio
draft intact. Fill, Clean, and Prime entry points on the detail retain the
channel and return to that flavor when finished. Care also provides the shared
operation directory.

## Images

Existing-image selection and adding a photo converge on the same outcome:
choose, upload when needed, confirm assignment, return to the originating Flavor
detail. Assignment uses the channel's captured revision and waits for the main
board's accepted stamped response before completing the task.
Choosing the already assigned image can simply complete the picker.

Photo selection opens the system picker, then the existing crop editor. Cancel
returns one step without assigning an image. A new photo is assigned only after
its upload succeeds. Pending, failed, and canceled uploads remain associated
with their machine, channel, image, and retry intent. An unrelated queued
upload cannot complete this task. Failure stays visible with retry or cancellation.
Leaving a task does not cause a late completion to navigate another page.
A newer image choice supersedes that channel's pending assignment. An older
upload may finish storing its picture but cannot then replace the newer choice.
Explicit cancellation prevents a deferred assignment.

## Care

Care offers Fill, Clean, and Prime for each channel. Each task follows
preparation, requested start, authoritative progress, and an explicit outcome.
**Done** returns to the page that opened it, including a Flavor detail.

The active operation is the primary Care context. **View filling**, **View
cleaning**, or **View Prime** opens that operation. Any active operation blocks
incompatible new starts across both channels. The app directs the person to
the progress page when it provides the required control.

Back, tabs, interactive pop, and machine switching follow the same operation
policy. While a phone-started Fill or Clean is being attended and connected,
the existing navigation lock applies consistently. Loss of connection permits
leaving, explains that the cycle may continue, and retains its context for
recovery. An observed result remains available until acknowledged or superseded
by a newer authoritative run. Active progress takes precedence over an older
result, including its Stop control. Fill and
Clean snapshots have no run token or history: recovery uses the machine's
reported channel and outcome, without attributing a different run to the
original task. Prime follows its reported session token.
Reconnection queries actual progress and never replays Start.
A timed-out or disconnected command has an unknown outcome, rather than a
confirmed refusal. Keep that uncertainty with the task and query authoritative
state before offering another Start. A late answer can resolve the uncertainty;
the app never silently retries the original command.

Stop waits for the machine's stopped state. Failure remains visible beside
the active operation. Prime's physical hold stays on the machine displays;
the phone opens, follows, and exits the shared session. An Exit failure remains
visible while Prime is still open.

Image and firmware transfers identify their appliance and keep machine
selection unavailable while the transfer depends on the current connection.
The same restrictions cover Open machine, Add, and removal of the current
machine, because those actions can drop or replace the connection. Removal of
an unrelated saved record can remain available.

## Settings and software update

Name and Sound are dedicated forms with explicit Save actions. A submitted form
shows the actual queued choice and its outcome. It is kept while out of range
and sends automatically on reconnect under its captured revision. Acceptance
closes only the page entry that submitted it; a new opening cannot be closed by
an old response. Back preserves a draft; Discard changes is explicit. Name and
Sound use the same Trust and conflict vocabulary as the mix panel.

Software Update returns to whichever page opened it. Its journey is check,
offer, send, restart, verify, result. Sending all bytes is not installation
success. The catalog's applicable components establish what must be verified.
An unanswered version or art CRC remains unknown; a missing component cannot
be treated as current merely because no known component needs updating.

An incomplete check says that the app could not verify every part and offers
**Check again**. A failed install offers an explicit retry or exit. **Done**
acknowledges the result and returns to the originating page. It does not restart
the check as a side effect.

## Setup, demo, and connection recovery

First-run and every Add entry share the same faucet-proximity preparation and
native accessory picker. Add is presented over its origin. Canceling Add returns
to that exact page with selection and drafts unchanged. Canceling or finding
nothing in the system picker leaves preparation available with useful guidance.
Successfully adding a machine deliberately opens its overview.

The demo clearly identifies its simulated state and offers **Add your machine**.
It remains a selectable demo after a real appliance is added.

A saved unsupported machine explains its unsupported state and offers removal,
the shared Add preparation, and explicit opening of another saved machine. It
does not expose appliance commands.

Connecting and machine Trust are separate states. A request belongs to the
machine, link and visible page that made it. **Requesting Trust** means the
phone has sent an ask; **Tap Trust on the machine** appears only after the faucet
confirms an active request and its remaining lifetime. Repeated edits join that
request. Leaving its page, opening management, discarding the change, or entering
the background withdraws it. System pairing's inactive phase does not withdraw it.

The faucet shows a compact Trust tray beside its normal controls. The enclosure
offers **Phone request** in its navigation rail; opening it is the person's choice.
Neither remote arrival nor renewal replaces a local task or covers a held Prime
pad, Stop, pouring controls, or Forget confirmation. Approval resumes the latest
owned change once. Decline retains it and never automatically re-asks.

New-app requests have a 15-second presence lease renewed every five seconds,
and an absolute 60-second cap. Expiry requires an explicit new request. The
machine reports retry-after time: per-identity decline delays are 30 seconds,
two minutes, ten minutes and thirty minutes; the machine-wide physical-decline
ladder is 15 seconds, one minute, five minutes and thirty minutes. Every
unsuccessful admitted request also leaves 15 seconds quiet. Rejected traffic
cannot extend these deadlines. Actual physical Trust or an hour of quiet resets
the relevant policy. Unpaired, busy, declined, expired and disconnected outcomes
remain distinct. The app does not claim a hardware prompt remains visible after
it expires.

Offline pages keep cached readings with their age, preserve drafts, and explain
unavailable writes. Losing contact does not navigate to management or setup.
Reconnection reconciles readings and task state in place.

## Manual journey review

Review the following on available physical devices. Care start/stop journeys
use the demo unless the appliance is prepared for the physical operation.
These checks are specific to this experience task and are not build or commit
hooks.

The pure navigation, draft, removal, and firmware-comparison checks run manually
on macOS with `python3 ios/SodaMachine/Checks/run.py`. They compile the app's
actual Foundation/Observation sources and use no simulator. They do not verify
SwiftUI view lifetimes, gestures, or Bluetooth transport; those need the
source review and physical-device journeys below.

1. On a real connected view-only phone, adjust a mix. Verify Requesting, then
   a confirmed Trust warning, with direction labels beside their buttons.
   Repeat taps, approve, and confirm exactly the latest mix. Repeat with decline,
   expiry, leaving the page and background; prompts must withdraw appropriately.
2. Edit Sound and Name; visit another tab and return. Retain each page and draft.
3. Rotate or resize while editing or viewing a nested page. Retain route,
   appliance, channel, and pending choices.
4. Adjust and use an edited mix. Confirm the ratio before selection; retain the
   editor and show the machine's actual on-tap ratio. Hold a mix out of range,
   reconnect, and confirm automatic saving. Change its revision elsewhere,
   including away-and-back, and exercise both conflict resolutions.
5. Cancel Add from every entry point and cancel the system picker separately.
   Return to the expected origin with no hidden management detour.
6. Manage machine B while controlling A. Remove B without changing A. Remove A
   and explicitly choose another record; never select one automatically.
7. Use Back and the interactive pop gesture through the same nested journey.
   Preserve the same edit state and operation restrictions.
8. Follow Fill, Clean, and Prime from Care and Flavor detail. Verify active-task
   entry, incompatible-start handling, stop/exit failure, result, and Done.
9. Reconnect after losing an operation. Recover progress or its result without
   replaying a command.
10. Verify update outcomes for current, behind, missing component, missing art
    CRC, catalog failure, interrupted transfer, and machine not returned.
11. Complete and decline Trust, allow timeout, and disconnect during the ask.
    Keep the connection and permission outcomes distinct and actionable.
12. Deliver a delayed response after leaving and reopening a task. It cannot
    close or change that new task, another tab, or another machine.
13. Time out a Start after the machine accepts it. Reconcile by querying state,
    without a second Start or an unsupported claim that nothing happened.
14. Begin uploading photo A, choose image B, and finish A's upload. B remains
    assigned; A cannot complete a superseding image task.
