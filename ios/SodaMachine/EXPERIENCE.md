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
one appliance's choices to another. Drafts are local to the running app session.

A save applies the visible choice and reports the machine's accepted value.
An error preserves the draft and offers a useful retry. A pending write does
not claim success. Name changes queued for reconnection are described as
pending until the machine acknowledges them.

An asynchronous action identifies its originating machine, page entry, and
task. A delayed response cannot close a newly opened page with the same name,
redirect another tab, or write to a different selected appliance.
Valid readback still updates the originating machine's confirmed state. It
does not clear a newer draft or complete a newer editing task.

## Machine and flavor

The Machine overview shows both flavors, the flavor on tap, coarse reservoir
levels, saved ratios, and appliance readings. Selecting a flavor opens its
detail; it does not immediately select that flavor at the faucet.

Flavor detail is the home for that channel's image and mix. **Save mix** confirms
the ratio in place. A pending ratio is visibly unsaved. For an inactive flavor,
the action is **Use at faucet** when its ratio is saved, or **Save and use at
faucet** when it has a draft. The combined action confirms the ratio before
selecting the flavor. If only the first step succeeds, the page says the mix was
saved and selection failed. A confirmed selection becomes **On tap at the
faucet** on the same page. Back remains the way to the overview.

Change image opens a child task and returns to the same flavor with its ratio
draft intact. Fill, Clean, and Prime entry points on the detail retain the
channel and return to that flavor when finished. Care also provides the shared
operation directory.

## Images

Existing-image selection and adding a photo converge on the same outcome:
choose, upload when needed, confirm assignment, return to the originating Flavor
detail. The app waits for the machine's art readback before completing the task.
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

Name and Sound are dedicated editors. Save completes that editor and returns
to Settings after the accepted or explicitly queued outcome is established.
Back preserves a draft; Discard changes is explicit.

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

Connecting and machine Trust are separate states. Pending Trust explains where
to respond. A connected viewer is labeled **View only**, with an action to ask
for Trust. Decline, timeout, and disconnection leave an understandable outcome
and retry path. Approval occurs on the machine displays. A contextual change
continues once after Trust is granted.

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

1. Change a ratio, open Images, cancel or choose an image, and return. Retain the
   ratio draft and confirm only the chosen image.
2. Edit Sound and Name; visit another tab and return. Retain each page and draft.
3. Rotate or resize while editing or viewing a nested page. Retain route,
   appliance, channel, and pending choices.
4. Save and use an edited mix. Confirm the ratio before selection; retain the
   editor and show On tap. Exercise a failure at each step without losing work.
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
