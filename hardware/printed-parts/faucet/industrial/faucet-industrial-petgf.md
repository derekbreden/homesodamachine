# Industrial faucet production print

The Industrial plate uses the Industrial base and above-counter plate, the tip
and display cover shared with Sculpted, and the side-down lever. The
[production selection](production-selection.json) names the approved mesh and
print task for each part. Derek approved the tip and cover together on the
[complete black Sculpted faucet](https://github.com/derekbreden/homesodamachine/blob/c8667107f964589be7dc69f8fb924f69a12729b3/hardware/printed-parts/faucet/sculpted/prints/2026-11-13-sloped-underside-complete-mark2/physical-result/physical-result.json).

The Industrial base, plate and lever have their own mesh and fit evidence in the
[Industrial print's record](production/2026-10-25/README.md). The tip's ledge holds the
display low over the tube, with a recess for each foot and a pocket for each switch. The
cover retains the working glass and neck clearances and fixed snap datums.

The plate prints the [faucet plate's recipe](../sculpted/README.md), the one the Sculpted plate
prints: it lays its own base and above-counter plate beside the shared tip, cover and lever.
The base's foundation follows its own round mounting face, and the screw-seat rings stand under
its own plate's counterbores. The [editable project](faucet-industrial-petgf.3mf), its
[report](faucet-industrial-petgf.print.json) and its [plate record](faucet-industrial-petgf.plate.json)
describe the product plate. Its print-only archive is kept on this Mac beside the project. The
TPU gasket, lever sleeve, PET-GF umbilical organizer and stainless under-counter plate are
separate prints or parts.

The plate takes the [faucet plate's selections](../../../../tools/hsm/print-prep/faucet-plate.json).

## Prepare the next print

```sh
tools/run -- faucet-plate industrial path/to/new-run-directory --production
```

The default plate targets Mark2's fixed left hardened nozzle, black PET-GF on its external
spool, and Textured PEI. `--printer Mark1 --filament-colour '#000000'` applies Mark1's own
trim and the specified spool colour. Check the destination's actual material and nozzle
mapping before sending. A cover-only project is available through the
[cover preparer](../faucet-display-cover/README.md#printing-and-checks).

## Assembly and accepted scope

The [assembly procedure](../faucet-shell/ASSEMBLY.md) gives the mounting, tube
routing and display seating order. Clear supports through the base's counter,
rear, donor and lever openings; through the tip's joint, display pocket and
outlets; and through the cover's open underside before display installation.
Preserve bearing, lip and groove surfaces.

The shared head’s fit is approved with a small hole in the tip beside the
cover’s front corner still visible. Assembly and retention forces, hydraulic
fault discharge and endurance are unmeasured.
Historical physical results retain their identified articles and settings in the
[print log](print-log.md) and [shipping acceptance](physical-acceptance.json).
