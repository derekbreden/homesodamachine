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

1. Open **Print → Import Gcode 3MF** and choose the sliced `.gcode.3mf` file.
2. Check the material, nozzle diameter, bed type, duration and mass.
3. Click **Print** to open **Send to print**.
4. Open the printer-name selector and choose **H2C** or **Mark2**. Check the selected
   name, nozzle compatibility, filament mapping and print options before **Send**.
5. Verify the accepted job by name and state on **Devices** and with `bambu_printer.py status`.

Both names are selectable in the device list and the send dialog. A busy printer disables
**Send**. Nozzle mismatches appear alongside the installed and sliced nozzle specifications.
The selector's popup can be visible in a screenshot while absent from the accessibility
tree; its visible row accepts a coordinate click. Accessibility element numbers and screen
coordinates come from the current UI observation.

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
