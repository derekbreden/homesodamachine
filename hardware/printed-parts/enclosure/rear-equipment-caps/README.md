# Rear equipment caps

Four PET-GF caps close the ASSE, Pisco, Digiten flow-meter and YZMSZ water-regulator seats on back-top. Each cap has two integral 2.00 mm spring walls, a 1.5 mm inside root radius and a 2.00 mm-wide foot. The relaxed leaves curve inward by 0.80 mm at the toe. The guide on the foot starts on the receiver's bevel, then the hook passes its solid retaining lip. The meter closes eastward against the flank. The other three caps close upward. [Shared snap section](../enclosure/numbers/equipment_snap.rs) · [Installed receiver source](../enclosure/back-top/supports.rs) · [Cover source](rear_equipment_caps.rs) · [Production fit measurements](production-fit.json)

| Station | Hardware held by the cap and receiver | Full-size fit evidence |
| --- | --- | --- |
| Multiplex ASSE 1022 | Both ASSE wrench flats, both shoulders of the inlet adapter, and a through-window for the vent and drain sleeve. | [Accepted ASSE and adapter](../../../print-tests/equipment-snap-pairs/prints/2026-11-26-mark2-pisco-asse/physical-result.json) |
| Pisco RVFUP | Molded body cradle, raised short-outlet bearing and fore-and-aft end stops. The white release collet remains accessible with the cap removed. | [Accepted rigid-body and axial hold](../../../print-tests/equipment-snap-pairs/prints/2026-11-26-mark2-pisco-asse/physical-result.json) |
| Digiten flow meter | Relieved saddle, port neck, fixed boss and screw-head channels and the lead exit. The lower leaf spans the seat. The upper leaf ends ahead of the Pisco receiver. | [Supported receiver and existing cover](../../../print-tests/equipment-snap-pairs/parts/supported-meter/fit-check.json) |
| YZMSZ water regulator | The raised saddle follows the scanned body and outlet shoulder. The central bearing ends 1 mm short of the spring ends beside the outlet collet. | [Firm saddle and original three-dot receiver](../../../print-tests/equipment-snap-pairs/parts/firm-regulator/fit-check.json) · [Recorded hand fit](../../../ledger/fitted.json) |

The ASSE seat admits 1.5 mm of threaded-joint position variation. Its adapter pocket follows the captured profile and all six wrench-flat directions at the measured clock. The installed adapter and its cavity sit 0.18 mm above the original captured chain pose. The three lower-facing flats have an additional 0.25 mm of vertical seating allowance. The inlet-adapter stock backs the last 3 mm of both ASSE springs up to the body axis.

The Pisco's 3 mm-wide fixed upper ring retains the insertion corridor. Between the independent leaves the backed cover cradle rises 0.20 mm, with a 0.60 mm lead beside the short outlet and a central bearing on the rigid metal shoulder. The cover's outlet lip advances 0.24 mm and the forward wing stop advances 0.12 mm. Entry bevels on the forward wall and aft tail take up the 0.80 mm initial axial relief as the cover seats. The rear body extends to its stop while the springs end ahead of the corner column. [Full Pisco register and measured service path](../../../print-tests/pisco-wide-snap/parts/three-dot/fit-check.json)

The meter's spine is 9 mm deep. Its 6 mm lower corner bevel clears the A-fill tube, while the saddle, port bore and roots retain the 0.40 mm westward setback from the relieved cover. The receiver recesses the entire downward-facing short upper cheek by 0.25 mm and retains the long lower hook's bearing height. Solid stock backs the upper catch and the aft part of the lower catch. Through the open west side, remove the trees from the short guide, the exposed lower shelf, the boss and screw-head recesses and the wire floor before fitting the meter. [Full receiver comparison and removal paths](../../../print-tests/equipment-snap-pairs/parts/supported-meter/fit-check.json)

The water regulator's bearing reaches 0.40 mm farther toward the hardware at the same wing registration as the original three-dot cap. The fixed receiver retains 0.30 mm radial allowance, and the bore follows the measured body-to-outlet shoulder. At both rigid hardware contacts the modeled feet are 0.232 mm short of their stops, with 1.534 mm hook engagement per side. [Water regulator mesh fit](../../../print-tests/equipment-snap-pairs/parts/firm-regulator/fit-check.json)

## Installation and service

ASSE, Pisco and meter enter their seats 16 mm forward and slide aft. The
regulator enters directly upward. The caps close after their bodies seat.

Work with back-top ceiling-down on the bench, separated from the cold core.
Disconnect and dress the flexible plumbing and leads aside. Reverse the
following service sequence for assembly; fit the ASSE chain after the meter
and PISCO. Fit the vent sleeve and its return tube after all three caps are
seated, with the sleeve clocked 15° from fore toward the meter. For meter-cap
service, disconnect DRAIN and remove the sleeve from the ASSE barb first.

For ASSE, remove the inlet header, disconnect the drain connection and remove the drain sleeve and
rear drain bulkhead. Spread the exposed leaves and
lower the cap 18 mm. Support the ASSE chain and cap together, slide both
32 mm fore, and withdraw them from the open side. The cap stays 18 mm below
the chain during this move.

After removing the ASSE chain, release the meter leaves, withdraw the cap
20 mm west and let the leaves relax. Move it another 25 mm west, then 40 mm
fore and out through the open side. Remove the meter, its disconnected soda
line/insulation and bend holder before withdrawing the PISCO cap.

After the meter comes out, tip the Pisco cover past the fixed meter shoulder. Spread its leaves while passing the receiver and settle the cap over the rigid short outlet. The checked tilt path, purchase-part loading path and release-ring stroke are in the [full three-dot service study](../../../print-tests/pisco-wide-snap/parts/three-dot/fit-check.json).

## Printing

The standalone STEP and STL files use the print frame, with one axial end
on Z0 and spring bending within the layer plane. The appliance uses their installed frames.
The [cap plate recipe](../trial-preparation/pieces.json) uses the shared dense PET-GF
interface at accessible contacts. The regulator's [local contact selection](contact.json)
follows the fitted body-to-neck transition from the complete cap mesh.
Its clearance below the roof keeps the curved bead edges separated at the dense interface.
The ASSE cap uses the native dense interface and the surrounding model stock
to back its fitted shoulder. The meter's narrow port shoulder bridges with its
opening clear, and the Pisco cap prints without support. The [earlier raised-crest print review](print-plan-review.json) records the gaps and bridge anchors for those earlier solids.

For an individual water-regulator cover, use the `single-regulator-cap`
[preparation recipe](../trial-preparation/pieces.json). Its native smooth-timelapse
tower provides time away from the cap between layers while retaining the
current cap geometry and production deposition recipe. The
[print record](https://github.com/derekbreden/homesodamachine/blob/0016c68223af1b237a3f23bc608fc248a7c0d7d5/hardware/printed-parts/enclosure/rear-equipment-caps/prints/2026-11-07-single-regulator-mark2/README.md) identifies the
emitted timing and physical-review state. The
[cooling policy](../../cooling/README.md#small-individual-parts) describes the
batch-time requirement.

For an individual Pisco cover, use `single-pisco-cap` on textured PEI. The
cover stands on its axial end, prints without support and uses the native
smooth-timelapse tower for cooling between layers. Select Timelapse On.
[Earlier raised-tip print job](https://github.com/derekbreden/homesodamachine/blob/28db775ffbc3650516a81910b1d5a603cd326bb7/hardware/print-tests/pisco-raised-tip-cover/prints/2026-11-23-mark1/print-job.json)

Remove the small cavity supports with a tiny flathead screwdriver that fits
inside the opening. Derek reports that the original trial's small automatic
cavity supports removed easily with that tool. Preserve the flat catch
undersides while clearing them. The [physical record](https://github.com/derekbreden/homesodamachine/blob/ed4ebc3cf65805689fe1421af6710770936107ec/hardware/print-tests/rear-snap-retention/physical-result/physical-result.json)
records this removal result and the hardware fit observations.

For release, put a small flat blade into the receiver channel beside the
solid hook and ease the leaf outward until its retaining face clears. Support
the cap while releasing both sides. The checked blade is 3 mm wide and
0.6 mm thick with a 2.5 mm shaft. PISCO uses a long slim precision driver;
its recorded envelope has 65 mm of reach and a short handle. These are
modeled tool envelopes; removal effort remains a physical print check.

```sh
tools/run -- cargo build --release -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-rear-equipment-caps
tools/run -- tools/hsm/target/release/rear-equipment-caps
```
