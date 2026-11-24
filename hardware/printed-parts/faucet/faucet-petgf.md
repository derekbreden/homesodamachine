# Sculpted faucet PET-GF print project

## Printing the saved plate

The print-only archive on this Mac is `sculpted/production/faucet-petgf.gcode.3mf`.
It targets Mark2’s left hardened nozzle with black PET-GF. Before sending it, check
[printer readiness and allocation](../../../tools/bambu-printers.md#print-submission) and
[startup spacing](../../../tools/bambu-printers.md#shared-circuit-startup-spacing).
[Confirm the start on the printer](../../../tools/bambu-printers.md#confirming-a-print-start).

## Preparing a new plate

The [editable project](https://homesodamachine.com/print-archive/e35fa8fbcddca686b10df0e355bad3074d38d833/faucet-petgf.3mf) contains the Sculpted base, shared tip, display cover, above-counter plate and side-down lever. The TPU seals, gasket and umbilical organizer are separate prints. [The print report](faucet-petgf.print.json) binds the source meshes and saved settings. [The plate record](faucet-petgf.plate.json) binds the print-only archive, its layers and plastic, and the acceleration planner's estimate of its motion, which the ledger's machine time reads.

The [faucet plate's recipe](sculpted/README.md) uses Mark2's left hardened hotend and black PET-GF. The archive lays the base's scaffold, roof and inclined foundation, and the tip's mating courses from a warped donor, ahead of the slicer's layers, and tells the printer its layers, progress and time left. The project carries the selected per-part seams, localized cooling, infill reinforcement and tip support aids. Each part's pose on the plate is the [plate's](../../../tools/hsm/print-prep/src/faucet_plate.rs). Black and white use the same geometry.

Prepare the product plate in a new run directory.

```sh
tools/run -- faucet-plate sculpted path/to/new-run-directory --production
```

Use the [assembly guide](../../faucet-assembly-guide/faucet-assembly-guide.pdf) and
[flavor-line specification](flavor-lines/README.md) for the current tubing and interfaces.
