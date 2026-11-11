# Printer tools

`hsm-printer` runs the optional printer status, light, camera recording, Bambu
Connect send, print-only archive and timelapse-retention commands in Rust.

`camera` reads or explicitly sets automatic print-process recording and verifies
the reported setting. `recordings` makes compact, elapsed-time chamber-camera
playback in iCloud Drive from completed native recordings. It keeps local receipts
so cloud-offloaded footage stays offloaded and does not remove native footage
from the printer. [Print-process recordings](../../bambu-recordings.md) describes
the archive and installed schedule.

`print ARCHIVE PRINTER` holds Bambu Connect in the foreground through the native
Swift input process. `send ARCHIVE PRINTER` uses the existing background
accessibility helper and borrows the foreground for the visible external-spool
picker. Both preserve the reviewed source archive, verify the selected printer,
external spool type and colour, mapping and print options, and require a new
printer job under the archive's name. An uncertain send is not repeated.

`archive SOURCE DESTINATION` removes editable model payloads from a new container
while preserving the sliced G-code bytes and every other retained member.
`purge-archive` packages the checked-in H2C maintenance program and metadata,
verifies its preparation, extrusion and shutdown commands, and writes a local
archive and preflight record. It sends no printer commands.
`gc` retains the existing command's options and defaults. Applying a retention
plan requires a local archive, a stable remote file, a durable byte-verified copy
and a final metadata check before deletion. Curl supplies the implicit FTPS
transport with its TLS session cache enabled. Access codes pass through a private
stdin configuration, never process arguments.
Directory flushes open metadata only so cloud-offloaded archives stay offloaded.

Printer names and credentials come from the existing Bambu Studio configuration
and private timelapse runner. They are not stored in the checkout. `status` and
`camera` without a mode are read-only; `light`, `camera on|off`, `recordings`,
`print`, `send`, and `gc --apply` perform their named explicit
actions. These commands are outside the normal build.

`picker-check` renders synthetic popovers and calls native Vision OCR without
opening Bambu Connect or contacting a printer. Rust fixture tests exercise
credential discovery, archive preservation, sparse reports, acceptance/retry
decisions, nozzle mapping and durable retention.
