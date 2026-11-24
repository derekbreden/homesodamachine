# Printed parts

For parts and coupons, start with [Printing the Machine](../printing-the-machine/README.md).
Compare fits at the production orientation, first layer and layer schedule. Report the
opening the slice emits. Change the layer schedule in its own trial.

## Shape

A part for one job must hold together as a single solid. Prefer broad continuous faces. Extend a pocket flush to the
adjacent wall, including when one level floor can replace several small pockets. Add
a curve, step or recess only for a named fit, bearing, drainage or access requirement.
Choose fewer edges first, then thicker stock. Leave stock in place when removing it would only save material.

## Publish loop

Select the affected [build targets](../../tools/hsm/README.md#find-and-inspect-a-part).
Include the assembly for installation or membership changes. Before rebuilding changed
enclosure geometry, [take the before snapshot](../../changes/README.md#recording-a-change).
Use the [print build](../../tools/hsm/print-build/README.md) and share the first live
part while review continues.

After publication, [lint the changed STL](../../tools/hsm/mesh-review/README.md).
Fix the defect wherever it recurs or [record an anchored answer](lint-answers/AGENTS.md).
Record the enclosure change from its snapshot.

## What each file shows

For a viewer pick, compare the [authored, printed and drawn surfaces](../../tools/hsm/inspection/README.md#reading-a-surface).

## Supports

Use branching trees in enclosed cavities and leave room to remove them. For painted
supports, read each underside's first deposited courses and their contacts. Each bridge
needs two landings. A coupon's removal result applies where the full part offers the same access.

- For PET-GF plates, follow the [support recipe](petgf-supports.md) and [localized cooling policy](cooling/README.md).
- For a printable piece in the enclosure assembly, use the [enclosure guide](enclosure/AGENTS.md).
  For faucet plates and finish trials, use the [faucet guide](faucet/AGENTS.md).

## Preparing and sending a plate

Use the [bed placement guidance](../../tools/bambu-printers.md#placement-on-unseasoned-plates)
for layout. For a send or resume, check [readiness](../../tools/bambu-printers.md#what-ready-looks-like-from-software),
[printer allocation](../../tools/bambu-printers.md#work-allocation) and [startup spacing](../../tools/bambu-printers.md#shared-circuit-startup-spacing).
