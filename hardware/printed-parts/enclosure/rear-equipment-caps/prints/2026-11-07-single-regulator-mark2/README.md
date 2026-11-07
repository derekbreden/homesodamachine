# Individual regulator cover

The `single-regulator-cap` recipe prints the approved water-regulator snap
cover with a native smooth-timelapse prime tower. The nozzle spends time on
the tower between cap layers and reprimes before returning. Production cap
geometry, orientation, temperatures and localized cooling are retained.

[job.json](job.json) holds the settings, emitted layer-return timing, source
and archive hashes, bed clearance and research sources. [launch.json](launch.json)
records the accepted Mark2 job. The native archive and editable project are
at the durable paths in the job record.

Finish, support removal and snap strength await physical review. The
commanded timing is a starting choice for this print; it does not establish
a qualified thermal limit for other individual parts. The
[cooling policy](../../../../cooling/README.md#small-individual-parts) describes
the batch-time requirement.
