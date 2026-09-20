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

## Print submission

Bambu Connect is installed at `/Applications/Bambu Connect.app`, signed in to the account
holding both printers. Its application identifier is `com.bambulab.bambu-connect`.

`bambu-ax` drives it in place, leaving the screen to whatever is using it. Bambu Connect is
an Electron application: setting `AXManualAccessibility` on it exposes the Chromium
accessibility tree, and `AXUIElementPerformAction` presses a control where it stands. The
window never comes forward, and the file chooser — an `AXSheet` on the main window — is
driven the same way, by selecting a row and pressing **Open**. No keystroke is involved.

```sh
tools/bambu-ax/build.sh                     # once, writes the binary beside the script
tools/bambu-ax/bambu-ax state               # job, progress, temperatures, AMS slots
tools/bambu-ax/bambu-ax import <file.gcode.3mf>
tools/bambu-ax/bambu-ax tree                # every labelled or actionable element
tools/bambu-ax/bambu-ax press "Print" --role AXButton
```

`press`, `act` and `value` take a label substring or a `#n` from `tree`, narrowed with
`--role` and `--nth`. Each one reports whether the frontmost application changed, so a step
that costs the screen says so. Accessibility trust comes from the calling process.

Synthesized mouse and keyboard input cannot do this. `CGEvent` delivery to `.cghidEventTap`
follows the frontmost application, so a click requires the window in front and takes the
screen for every step after it. `open -g -j -a 'Bambu Connect'` starts the application
without the screen if it is not already running.

The steps below are the same sequence performed by hand.

1. Open **Print → Import Gcode 3MF** and choose the sliced `.gcode.3mf` file.
2. Check the material, nozzle diameter, bed type, duration and mass.
3. Click **Print** to open **Send to print**.
4. Open the printer-name selector and choose **H2C** or **Mark2**. Check the selected
   name, nozzle compatibility, filament mapping and print options before **Send**.
5. Verify the accepted job by name and state on **Devices** and with `bambu_printer.py status`.

Both names are selectable in the device list and the send dialog. A busy printer disables
**Send**. Nozzle mismatches appear alongside the installed and sliced nozzle specifications.

Steps 1 to 3 and the dialog's own controls go through `bambu-ax`. Its **Send** button is
labelled `confirm`. Two things in step 4 do not: the printer selector's popup and the AMS
filament-mapping panel are drawn outside the accessibility tree, and `find` returns no
match with either open. The selector defaults to **Mark2** on every send and changing it
clears the filament mapping, so those two clicks are a coordinate click and cost the
screen. Do both in one takeover, then return to `bambu-ax` for the options and **Send**.

`#n` indices renumber whenever the tree changes, so `press` and `act` refuse a bare `#n`
and require `--expect <label or role>`, checked against the element found there. A number
carried over from an earlier dump then reports what now holds it instead of pressing it.
Matching by label, narrowed with `--role`, needs no `--expect`. `import` walks the chooser by path component and reaches
paths inside the working tree, so stage an archive there rather than in a scratch
directory.

The signed printer-control application handles protected operations. Bambu's network
library checks the calling application's signature for those operations; loading the
library in a standalone helper does not provide print-start authorization
([Bambu authorization controls](https://blog.bambulab.com/firmware-update-introducing-new-authorization-control-system-2/)).

The `.gcode.3mf` carries the sliced machine G-code, including Z trim. The enclosure jobs'
profiles, offsets and file hashes are recorded in
`hardware/printed-parts/enclosure/enclosure/print-jobs.json`.

## Printer storage

The existing `h2c_timelapse_gc.py` connects to the LAN FTPS service. Its listing, archive
and retention commands are described in [h2c-timelapse-gc.md](h2c-timelapse-gc.md).
