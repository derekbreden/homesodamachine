# Pisco snap cover on Mark2

The `single-pisco-cap` recipe prints only the Pisco cover, with a native
smooth-timelapse prime tower. The cover keeps its current production mesh,
exported print pose and accessory-plate object settings. It prints without
support on textured PEI using Mark2's standing PET-GF trim and left hotend.

[print-job.json](print-job.json) binds the project, sent archive, reviewed
paths and accepted printer job. [layer-time.json](layer-time.json) reads the
tower deposition on every cap layer; travel and the firmware snapshot add to
that time away. [launch.json](launch.json) records the printer's acceptance,
and [prelaunch-status.json](prelaunch-status.json) records both printers before
the send. The [physical result](physical-result.json) records Derek's acceptance
of the angled wing-tip catches. The complete cover needs a clear insertion
path in the installed machine.

Prepare from the current recipe without contacting the printer:

```sh
tools/run -- tools/hsm/target/release/enclosure-print-prep single-pisco-cap \
  --printer Mark2 --bed 'Textured PEI Plate' --slice --review
```

Select Timelapse On when sending. The exact editable project and sent archive
are linked in the job record on the `print-projects` release.
