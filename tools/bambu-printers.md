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

`status` reports the job state and, for each machine, its two external spools and every
nozzle it knows.

- `gcode_state` is the state of the last job until the next one starts. `FINISH` and
  `FAILED` (a cancelled print) are both idle: the machine takes a job and the send dialog
  offers it. `PREPARE`, `RUNNING` and `PAUSE` are busy, and Send is disabled.
- `external_spools` are the MQTT `vir_slot` trays: `254` is the left external spool and
  `255` the right. Every job here maps the left nozzle's PET-GF to `254`, declared
  PET-CF because there is no PET-GF preset; `255` has carried TPU. The device page's
  Filaments panel shows the AMS trays and the right spool, so a `TPU` there says nothing
  about `254`. The spool's colour is never reported; it is the loader's word.
- `nozzles` lists every nozzle, racked or mounted, and `nozzle_type` names one of them,
  which on H2C has been the 0.6 mm while the left head printed at 0.4 mm. The dialog is
  the authority on compatibility: the file summary states the sliced diameter and a
  mismatch appears on the filament tile.

## Print submission

Bambu Connect is installed at `/Applications/Bambu Connect.app`, signed in to the account
holding both printers. Its application identifier is `com.bambulab.bambu-connect`.

```sh
.cache/printer-control/venv/bin/python tools/bambu_send.py <file.gcode.3mf> H2C
.cache/printer-control/venv/bin/python tools/bambu_send.py <file.gcode.3mf> Mark2 --dry-run
```

`bambu_send.py` performs the procedure below and reads each step back before the next.
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
   whose device page was opened last, as long as that machine is not printing; while it
   prints it cannot be sent to at all and the dialog falls back to H2C, the first in
   the list. It does not default to Mark2, to the free machine, or to the last machine
   sent to. This step replaces the printer selector, whose popup is drawn outside the
   accessibility tree.
2. **Import.** `import <file.gcode.3mf>` opens the Print tab, walks the chooser to the
   file and opens it. `state` then reads the summary: compatible printer, bed type,
   filament, nozzle diameter, time and weight. A path through a hidden directory is
   staged as a visible copy first, and a path inside the working tree walks fastest.
3. **Open the dialog.** `press "Print" --role AXButton`. In `tree`, the group labelled
   `<name> chevron_down` is the printer offered; it must read the target.
4. **Read the filament tile.** The `AXGroup` under `Left Nozzle` reads `Ext PET-CF`
   when the dialog resolved the mapping itself (Mark2, which has no AMS, does) and
   `? ?` when it did not (H2C, with an AMS, does not). A `? ?` tile is one call:
   `click <x+47> <y+30> <x-245> <y+282>` from the tile's `@x,y` — its centre, then the
   External spool tile in the popover that opens under it. The popover is not in the
   tree; the tile afterwards is, and it must read `Ext PET-CF`. The offsets are H2C's,
   with one AMS unit; the popover lists AMS trays above the external spool.
5. **Read the print options.** Each option is a row of `AXRadioButton`s and the chosen
   one carries an `AXImage "radio"` as its first child in `tree`. The standing settings
   are Timelapse On, Auto bed leveling On, Flow dynamic calibration Auto and Nozzle
   Offset Calibration Auto; the dialog remembers the last send. `press "#n" --expect On`
   changes one.
6. **Send.** `press "confirm" --role AXButton` — the button is labelled `confirm`. It does
   nothing while the tile reads `? ?` or the target is busy; the dialog stays open.
7. **Verify with the printer.** `bambu_printer.py status <name>` reports `PREPARE` within
   seconds and then `RUNNING` with the archive's name as `subtask_name`. A 47 MB archive
   took under ten seconds to land. Record the reading with the job.

### What the application will not show

The printer selector's popup and the AMS filament-mapping popover are drawn outside the
accessibility tree: `find` returns nothing with either open, and an `AXPress` on their
`AXGroup` divs is a no-op, because Chromium synthesizes a click only for button and link
roles. An event sent with `postToPid` never arrives either. The global tap is the only
delivery and it follows the frontmost application, so `click` brings the window forward,
clicks every coordinate given, then restores both the previous application and the
pointer. One borrow measures about a second, so pass both coordinates to one call; the
popover under the tile survives the 0.25 s between them. Nothing verifies a popover
except the control it changes, so read the tile, not the popover.

The procedure never opens the selector. Changing the printer there clears the filament
mapping, and the device-page rule makes the click unnecessary.

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

Two sessions in the application at once cancel each other's dialogs. One session sends.

The signed printer-control application handles protected operations. Bambu's network
library checks the calling application's signature for those operations; loading the
library in a standalone helper does not provide print-start authorization
([Bambu authorization controls](https://blog.bambulab.com/firmware-update-introducing-new-authorization-control-system-2/)).
MQTT `stop` from an unsigned client is ignored for the same reason.

The `.gcode.3mf` carries the sliced machine G-code, including Z trim: the shared
`petgf.3mf` start G-code subtracts a fixed 0.02 mm Textured PEI compensation from the
requested trim, so +0.18 emits `G29.1 Z0.16` and +0.04 emits `G29.1 Z0.02`. The
enclosure jobs' profiles, offsets and file hashes are recorded in
`hardware/printed-parts/enclosure/enclosure/print-jobs.json`, and the lever's in
`hardware/printed-parts/faucet/lever-replica/print-jobs.json`.

## Printer storage

The existing `h2c_timelapse_gc.py` connects to the LAN FTPS service. Its listing, archive
and retention commands are described in [h2c-timelapse-gc.md](h2c-timelapse-gc.md).
