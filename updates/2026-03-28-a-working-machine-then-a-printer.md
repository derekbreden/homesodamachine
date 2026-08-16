---
title: A working machine, then a printer
start: 2026-03-07
end: 2026-03-28
kind: period
thumb: boards
lede: The under-sink prototype gained its full software stack, then a production 3D printer turned the project toward a manufacturable appliance.
---

The repository opens on a machine that already pours. A carbonator, three peristaltic pumps, flow sensors, solenoid valves and three matte-black faucets were installed under the kitchen sink before the first commit, at about $1,814 in parts.

## The software stack

The controller went from one chip to three, built from one project: the main board that reads flow and drives the pumps, a round touchscreen with a rotary knob for configuration, and a small round display that shows the selected flavor. Settings and uploaded flavor artwork survive a power cycle in on-chip flash. A clock module keeps hourly pour statistics per flavor. A wash-cycle state machine exists in the firmware; its valve board is pinned but not installed.

{{fig:three-boards}}

An iPhone app arrived on 13 March and reached about 3,500 lines of Swift. It finds the machine over Bluetooth, edits flavor ratios, uploads and resizes artwork from the photo library, and shows pour statistics.

The link between the three boards was replaced with a standard framing protocol at three times the previous data rate. All three boards were flashed and tested together on 21 March, image uploads completed, and no link failures were observed.

## A build guide

The machine became something a stranger could rebuild: eight photographs of the installed hardware, a demo video of a pour, complete pin tables for all three boards, a plumbing document, and a costed parts list.

## 22 March

A Bambu Lab H2C printer with its multi-material system, six hotends and ten kilograms of filament — about $3,300 — plus a 72-inch workbench, digital calipers, a filament dryer and four dry boxes. The domain homesodamachine.com was registered the same day. Two commits landed on it.

The calipers arrived on the 24th and were used immediately. Three bought parts — a peristaltic pump, a solenoid valve, a push-fit union — were measured and photographed into thirty dimensioned images, replacing datasheet estimates.

## The first parts, and their deletion

A product vision followed: a 220 × 300 × 400 mm enclosure printed as two halves that snap together permanently, two collapsible syrup bags lying diagonally inside, and a pump cartridge the owner can swap, released by squeezing a hidden plate. Beside it, a requirements document keyed to the printer just bought — minimum wall thickness, overhang limits, hole-shrinkage allowances, layer orientation for snap arms.

Three mechanisms reached finished 3D geometry and were removed before the period closed. The outer enclosure, both halves, was finished after midnight on 28 March and deleted twenty minutes later. A bag cradle went the same morning. The pump cartridge ran through the design pipeline twice in one day, the second pass fanned out across ten sub-components, and was deleted five minutes after that pass finished.

What survives is two solid models: the lower cradle and upper cap of a permanent cage for a 2 L syrup bag. Nothing was printed in these four weeks.
