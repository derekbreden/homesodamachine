# Bambu printers

H2C and Mark2 are Bambu Lab H2C printers. Their names identify the individual machines.

## Status and chamber lights

`bambu_printer.py` reads the printer names, hosts and access codes from
`~/.config/h2c-gc/run.sh`. It matches each code to its serial in Bambu Studio's saved
configuration. Credentials stay outside the repository and command output.

```sh
python3 -m venv .cache/printer-control/venv
.cache/printer-control/venv/bin/pip install -r tools/printer-requirements.txt
.cache/printer-control/venv/bin/python tools/bambu_printer.py status
.cache/printer-control/venv/bin/python tools/bambu_printer.py status H2C
.cache/printer-control/venv/bin/python tools/bambu_printer.py light Mark2 on
```

The light command takes `on` or `off`, and `--node chamber_light2` selects the second
chamber light. It verifies both the command acknowledgment and the reported light state.
Chamber illumination supports the printer's camera-based detection during a print.

## What ready looks like from software

Derek's request to start a print on a printer confirms that its bed is clear.
Proceed without a separate bed-clear question. Check the printer's current job,
material and nozzle mapping, print errors, and shared-circuit startup spacing.

`status` reports the job state and, for each machine, its two external spools and every
nozzle it knows.

- `gcode_state` is the state of the last job until the next one starts. `FINISH` and
  `FAILED` (a cancelled print) are both idle: the machine takes a job and the send dialog
  offers it. `PREPARE`, `RUNNING` and `PAUSE` are busy, and Send is disabled.
- `external_spools` are the MQTT `vir_slot` trays: `254` is the left external spool and
  `255` the right. Read both `type` and `colour` when present and verify the physical
  material from Derek's loading report. Mark2 carries black PET-GF on the left and white
  PET-GF on the right; both are labelled PET-CF in the printer. A single-colour black job
  uses the left nozzle. The [two-colour nameplate record](../hardware/printed-parts/enclosure/nameplate/mark2-print-readiness.json)
  identifies its separate left/black and right/white assignments.
- `nozzles` lists every nozzle the machine knows, racked or mounted; `nozzle_type` names
  one of them, not the printing head. The send dialog checks the sliced diameter against
  the head and shows a mismatch on the filament tile.

For H2C, a `? ?` tile under **Left Nozzle** is an unresolved filament mapping. Select
the black **Ext PET-CF** tile in its popover. The numbered hotends and **R** tiles are
separate choices; their displayed diameters do not establish the left external
hotend's diameter. Check the left hotend on the printer display and the resolved
external-spool mapping. Derek's display confirms a Standard Hardened 0.4 mm left
hotend and a Standard Stainless 0.2 mm right hotend; selecting Ext PET-CF enables
the reviewed 0.4 mm cover job without a nozzle mismatch.

## Recorded two-nozzle alignment

Mark2's black/white PET-GF pair uses the
[coplanar registration coupon](../hardware/printed-parts/calibration/dual-nozzle-registration/README.md)
to measure residual XY alignment. Both hotends are 0.4 mm. Record the exact job,
native archive, launch settings, selected X/Y indices, coordinate correction and
validation result. The correction is printer/nozzle-pair specific; keep the CAD
artwork aligned. The measurement state is in `mark2-registration.json` beside
the coupon source: white X −0.50 mm and Y +0.70 mm, with the raised-artwork nameplate
appearance accepted by the user. Residual XY error is unmeasured; the original
Y choice was tentative. Use the native
slice's verified tool-coordinate correction; keep the part geometry nominal.

The coupon uses the usual **Auto** Nozzle Offset Calibration option in Bambu
Connect, as do validation and product prints. The procedure does not depend on
touchscreen-managed high-precision calibration. A replacement hotend or changed
calibration condition requires a new alignment check.

## Power-loss recovery

On 2026-09-25 Derek reported accidentally unplugging both printers by tripping on
their power cord. H2C lost power mid-print, mid-extrusion, and recovered with no
visible defect at the interruption point. The active job was
[front-bottom, task 1279923918](../hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-24-enclosure-front-bottom-h2c-v7/README.md).
This is Derek's visual observation of that recovery.

## Extrusion overload after sitting loaded

Derek reports recurring extrusion overloads after the printers sit loaded and idle.
His working recovery sequence for this condition is:

1. Cut the filament at the spool side.
2. Unload through the printer's touchscreen.
3. Pull out the entire cut segment.
4. Reload from the freshly cut spool end, then resume.

The [H2C receiver trial](../hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-28-display-receiver-retention-h2c-v2/startup-recovery.json)
records this recovery from extrusion-motor overload 0300-801E. Moisture is Derek's
suspected cause of the recurring idle-time pattern; no moisture measurement or
controlled comparison establishes the cause. A resume is a printer start for the
shared-circuit spacing rule below.

## Purge and wipe

The [H2C purge maintenance job](h2c-purge/README.md) provides a repeatable Connect
archive for the loaded fixed left hardened 0.4 mm nozzle with black PET-GF. It
retains the native homing/material preparation and chute purge/wipe sequence,
contains no part, and ends with heater targets off. Filament-blob ejection is
physically confirmed. The blob can land on the bed: check and clear any loose,
cold blob before the next print. Consider the cycle when loaded PET-GF has been
idle for a while, before printing or another known idle period. There is no fixed
interval or measured prevention of idle-time overload. Use it only with the
documented idle-printer configuration; the package is not a general mid-print
G-code command.

## Work allocation

For one job that can run on either ready printer, prefer the one that has been
idle with suitable filament loaded longer. This compares the period spent both
idle and loaded, not idle time alone. Check material suitability first; PET-GF
is not always loaded in both printers. Use known print/load history rather than
inferring a loading time from current temperature or idle status alone.

Use both printers when Derek has them loaded, cleared and ready and the authorized
parts can be split between them with the correct materials and nozzles. Prepare
separate plates with each machine's established settings and Z trim. Derek prefers
this distribution because leaving a loaded printer idle is associated with his
reported cut-and-refeed recovery; it is not a measured diagnosis of the cause.
Keep the three-minute spacing between starts.

## Shared-circuit startup spacing

H2C and Mark2 share a circuit. Leave **at least 180 seconds between print starts**:
after the first machine accepts its job, wait three minutes before sending or resuming
the other machine. Read both machines after a power interruption; a job already running
does not need another send. Apply the spacing to recovery starts as well.

The interval is Derek's proposed trial based on his previous experience. The sender's
foreground lock serializes app access but does not enforce this interval; the operator
must wait and record both launch times.

The [2026-09-28 startup trial](../hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-28-shared-circuit-stagger/README.md)
records Derek's report of repeated breaker trips when both machines start close together,
including during his own manual starts. The two cover-job launch receipts are
54.421746 seconds apart; both machines subsequently report FAILED at layer 0 after
power restoration. Electrical load and the exact trip time were not measured.

## Print submission

Bambu Connect is installed at `/Applications/Bambu Connect.app`, signed in to the account
holding both printers. Its application identifier is `com.bambulab.bambu-connect`.

```sh
tools/cad-venv/bin/python tools/bambu_print.py <file.gcode.3mf> Mark2
tools/cad-venv/bin/python tools/bambu_print.py <file.gcode.3mf> Mark2 --dry-run
```

`bambu_print.py` imports a separate copy of the reviewed archive, brings Bambu Connect
forward, reads its controls and clicks them with mouse input. Its own Swift input process
is `bambu-ui/main.swift`; the command compiles it into `.cache/printer-control/` as needed.
It does not call `bambu-ax` or `bambu_send.py`. The previous application and pointer are
restored when the transaction ends. Input stops if another application takes focus.

The sender checks the archive's embedded G-code checksum, the target printer, each active
nozzle's external spool type and colour, and the standing print options. It supports one
external filament per active nozzle on a single sliced H2C plate. Mark2's left/black and
right/white assignments are checked separately. Spool quantity is not a launch condition.

`--dry-run` performs the import and dialog checks, then cancels without clicking Send. It
also runs while a printer is busy, when Send is disabled. An ordinary run refuses a busy
printer before opening the application. A Send click is made only once per dialog.

Success requires a new printer job ID, the archive's name, and PREPARE or RUNNING with no
print error. The MQTT connection stays open throughout the transaction. A fresh-dialog
retry is allowed only when no command reply, upload or new job was observed, the printer
is still idle on its original job, and the app shows no transfer. Errors and ambiguous
results stop the sender. Up to three attempts are made; `--attempts 1` selects one.
The acceptance wait samples Connect's visible text for short-lived request and upload
errors, including “Resource does not exist,” and stops without a repeat send when one
appears.

Successful launches write `.cache/printer-control/<printer>-<job-id>-launch.json`, including
the original archive and G-code hashes. Bambu Connect's imported copy is separate because
the application can rewrite the file it imports.

### Bambu Studio send from an existing slice

`bambu_print_archive.py source.gcode.3mf output.gcode.3mf` creates a separate
print-only archive. It removes editable geometry and its model references while
preserving every G-code byte, checksum, preview, slice metadata and print setting.
The source stays intact. Open the output with Bambu Studio's **Open Project**;
it opens in Preview with **Print plate** enabled. Do not reslice it.

Choose the target printer and external-spool mapping, and explicitly verify
Timelapse On, Bed Leveling On, Flow Calibration Auto and Nozzle Offset Calibration
Auto in Studio's own send dialog. The accepted printer name can come from the
plate name rather than the archive filename. Record that reported name, the new
task ID, the submitted archive hash and the unchanged G-code hash. The
[Mark2 back-bottom launch](../hardware/printed-parts/enclosure/bottom-grip-print/mark2/launch.json)
records an accepted Studio send with LAN acceleration using this packaging.

### Background accessibility sender

```sh
.cache/printer-control/venv/bin/python tools/bambu_send.py <file.gcode.3mf> H2C
.cache/printer-control/venv/bin/python tools/bambu_send.py <file.gcode.3mf> Mark2 --dry-run
```

`bambu_send.py` performs the procedure below and reads each step back before the next.
When Bambu Connect is not running it starts it with `open -g` and waits for its window.
`--dry-run` stops at the Send button and cancels the dialog. `--timelapse Off` departs
from the standing options. It exits non-zero, with the dialog cancelled, on any reading
that is not the one expected, and it ends with the printer's own MQTT report of the job.

`bambu-ax` drives Bambu Connect in place, leaving the screen to whatever is using it.
Bambu Connect is an Electron application: setting `AXManualAccessibility` on it exposes
the Chromium accessibility tree, and `AXUIElementPerformAction` presses a control where
it stands. The window never comes forward, and the file chooser — an `AXSheet` on the
main window — is driven the same way, by selecting a row and pressing **Open**. No
keystroke is involved.

```sh
tools/bambu-ax/build.sh                     # once, writes the binary beside the script
tools/bambu-ax/bambu-ax state               # every static text on the current page
tools/bambu-ax/bambu-ax import <file.gcode.3mf>
tools/bambu-ax/bambu-ax tree                # every labelled or actionable element
tools/bambu-ax/bambu-ax press "Print" --role AXButton
tools/bambu-ax/bambu-ax click <x> <y> [x y ...]
```

`press`, `act` and `value` take a label substring or a `#n` from `tree`, narrowed with
`--role` and `--nth`. Each one reports whether the frontmost application changed, so a step
that costs the screen says so. Accessibility trust comes from the calling process.

### The procedure

1. **Open the target's device page.** `press "Devices" --role AXLink`, then
   `press "<name>" --role AXLink`. The send dialog offers, as its printer, the machine
   whose device page was opened last while that machine was idle.
2. **Import.** `import <file.gcode.3mf>` opens the Print tab, walks the chooser to the
   file and opens it. `state` then reads the summary: compatible printer, bed type,
   filament, nozzle diameter, time and weight. A path through a hidden directory is
   staged as a visible copy first, and a path inside the working tree walks fastest.
3. **Open the dialog.** `press "Print" --role AXButton`. In `tree`, the group labelled
   `<name> chevron_down` is the printer offered. When it is not the target, the selector's
   popover chooses it: `click <x+70> <y+32> <x+81> <y+91+36n>` from the selector's `@x,y`,
   its name text and then row `n` of the popover, the printers in `PRINTERS` order, in one
   call. One call is the point: an AXPress opens the popover too, but the front borrow
   of the click that follows closes it, so the row click lands on the dialog. The
   popover is not in the tree; the selector afterwards is, and it must read the target
   before anything else is pressed. The borrow holds the front for a second or two, and a
   keystroke typed elsewhere in that window takes the popover with it, so the two clicks
   are retried, up to three times, until the selector reads the target. The device page
   opened in step 1 does not decide it:
   on 2026-09-20 the dialog offered H2C three times after Mark2's page was opened and
   settled.
4. **Read the filament tile.** The `AXGroup` under `Left Nozzle` reads `Ext PET-CF`
   when the dialog resolved the mapping itself (Mark2, which has no AMS, does) and
   `? ?` when it did not (H2C, with an AMS, does not). A `? ?` tile is one call:
   `click <x+47> <y+30> <x-245> <y+282>` from the tile's `@x,y` — its centre, then the
   External spool tile in the popover that opens under it. The popover is not in the
   tree; the tile afterwards is, and it must read `Ext PET-CF`. The offsets are H2C's
   popover: one AMS unit's trays above the External spool. If another app takes a
   keystroke during the click, the popover can close before the External click lands.
   The sender reads the tile after each attempt and, on a miss, closes the dialog
   and reopens a fresh one before retrying. The tile toggles the popover, so another
   click in the same dialog is not a safe retry.
5. **Read the print options.** Each option is a row of `AXRadioButton`s and the chosen
   one carries an `AXImage "radio"` as its first child in `tree`. The standing settings
   are Timelapse On, Auto bed leveling On, Flow dynamic calibration Auto and Nozzle
   Offset Calibration Auto; the dialog remembers the last send. `press "#n" --expect On`
   changes one.
6. **Send.** `press "confirm" --role AXButton` — the button is labelled `confirm`. It is
   disabled until the dialog has finished loading the printer, while the tile reads
   `? ?`, and while the target is busy; `tree` and `find` mark a disabled control
   `(disabled)`, and an `AXPress` on one does nothing. The dialog closes when the
   application has taken the job, so a dialog still open after the press is a press
   that did not land.
7. **Verify with the printer.** `bambu_printer.py status <name>` reports `PREPARE` within
   seconds and then `RUNNING` with the archive's name as `subtask_name`. A 47 MB archive
   took under ten seconds to land. Record the reading with the job.

   The dialog can close and no job arrive: the job id does not move, the printer's
   `upload` block stays idle, and nothing lands late. This happened to three Mark2 sends
   (twice on 2026-09-22, once on 2026-09-23) with the file, printer and procedure the same
   as sends that landed. `bambu_send.py` presses Send once per dialog and holds the
   printer's report topic open across it, printing any command reply (`project_file` with
   its result and reason), upload, error or HMS it hears, and the application's page text at
   the close, a second later and five seconds later. A send that has not landed is watched a
   further pause, and longer while the page reads Sending, Uploading or Downloading. Only then
   is it made again from a fresh dialog, up to three rounds, and only while the printer reads
   the job id it had before the first send, idle, with no upload and no new error or HMS. A
   command the printer answered is not sent again.

### What the application will not show

The printer selector's popup and the AMS filament-mapping popover are drawn outside the
accessibility tree: `find` returns nothing with either open, and an `AXPress` on their
`AXGroup` divs is a no-op, because Chromium synthesizes a click only for button and link
roles. An event sent with `postToPid` never arrives either. The global tap is the only
delivery and it follows the frontmost application, so `click` brings the window forward,
clicks every coordinate given, then restores both the previous application and the
pointer. One borrow measures about a second; both coordinates go in one call, and the
popover under the tile survives the 0.25 s between them. A popover's only reading is
the control it changes.

Changing the printer in the selector clears the filament mapping.

`#n` indices renumber whenever the tree changes, so `press` and `act` refuse a bare `#n`
and require `--expect <label or role>`, checked against the element found there. A number
carried over from an earlier dump then reports what now holds it instead of pressing it.
Matching by label, narrowed with `--role`, needs no `--expect`. A label match is a
substring match: `press "Print" --role AXLink` also matches `My Printers`, so pass
`--nth 0` on a device page.

A chooser acts on its selection, not on a click. `AXOpen` on the row's cell is refused
with -25205, `AXConfirm` reports success and does nothing, and a click lands without the
panel taking it; setting `AXSelected` on the row's `AXRow` and pressing **Open** works with
the application in the background. A sidebar row is the exception — it navigates on
`AXOpen`, and that action sits on its `AXCell`, not on the `AXStaticText` holding the name.
`select "<row name>"` chooses a row in a chooser that is already open.

Synthesized keyboard input cannot reach the application at all. `CGEvent` delivery to
`.cghidEventTap` follows the frontmost application, so a keystroke needs the window in
front and takes the screen for every step after it. `open -g -j -a 'Bambu Connect'`
starts the application without the screen if it is not already running.

Two sessions in the application at once cancel each other's dialogs.

The signed printer-control application handles protected operations. Bambu's network
library checks the calling application's signature for those operations; loading the
library in a standalone helper does not provide print-start authorization
([Bambu authorization controls](https://blog.bambulab.com/firmware-update-introducing-new-authorization-control-system-2/)).
The printer ignores MQTT `stop` from an unsigned client.

The `.gcode.3mf` carries the sliced machine G-code, including Z trim: the shared
`petgf.3mf` start G-code subtracts a fixed 0.02 mm Textured PEI compensation from the
requested trim, so +0.18 emits `G29.1 Z0.16` and +0.04 emits `G29.1 Z0.02`. The
enclosure jobs' profiles, offsets and file hashes are recorded in
`hardware/printed-parts/enclosure/enclosure/print-jobs.json`, and the lever's in
`hardware/printed-parts/faucet/lever-replica/print-jobs.json`.

A print sent while the printer is loading filament or purging, which is a nozzle or bed
target above zero with no job, starts nothing and says nothing: the dialog closes, the
printer stays on its last state, and its `job_id` does not move. `bambu_send.py` reads the
targets before it sends and waits for them to fall, and when a send is dropped anyway it
reads them again and makes the whole pass again, up to three times. The job id moving is
what says a job reached the printer; the file name alone cannot, because the last job can
carry the same one.


## Printer storage

The existing `h2c_timelapse_gc.py` connects to the LAN FTPS service. Its listing, archive
and retention commands are described in [h2c-timelapse-gc.md](h2c-timelapse-gc.md).
