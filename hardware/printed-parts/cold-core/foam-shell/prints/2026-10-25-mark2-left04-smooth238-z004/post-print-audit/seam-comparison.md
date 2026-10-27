# Shell seam versus the selected faucet treatment

The sent shell did not receive the faucet's selected A2 scarf treatment or
wipe-off setting. It inherited the seam defaults from the shared
[`petgf.3mf`](../../../../../petgf.3mf). The faucet preparer applies its
selected seams as object overrides and its wipe choice as a filament override;
the shell preparer did not transfer those settings.

| Setting | Selected faucet base, tip and plate | Sent shell |
| --- | --- | --- |
| Seam placement | Back, with rear-enforcer paint on base and curved tip | Aligned; no seam paint |
| Scarf | A2, external contours, 60 mm, 10% start height, ten steps | Off |
| Scarf gap | 0% | Inactive |
| Ordinary seam gap | 150%, within the selected A2 package | 15% |
| Wipe | Off, filament override | On, 2 mm |

The faucet's cover and lever retain ordinary Aligned/15%/scarf-off seams.
Their choice does not replace the base and tip's selected treatment.
The complete selection is in
[`industrial/finish-selection.json`](../../../../../faucet/industrial/finish-selection.json);
the preparer writes `seam_object_overrides` into `Metadata/model_settings.config`
and sets `filament_wipe=0`. In the shell archive both process and filament
scarf modes are `none`, there are no object/part seam overrides, and the
embedded mesh has zero seam-painted triangles. The selected faucet's 150%
ordinary gap is part of its complete scarf package, not an isolated setting
to apply to an ordinary seam.

## The photographed seam and insert pocket

The front-center outer-wall seam is at native X approximately −140.988 mm,
Y approximately zero. The sent G-code starts that exterior perimeter there
on 98 layers, from Z 0.20 through 23.48 mm. Sampled starts and ends have a
0.060 mm commanded gap, agreeing with 15% of the 0.4 mm nozzle diameter.
It is an abrupt ordinary start/end rather than a scarf ramp.

The front middle insert pocket is centered at native (−137.5, 0), with a
2 mm bore radius. First-surface rays into the actual embedded sliced mesh
at Y=0 find the outer surface at X=−141.2 and the pocket surface at X=−139.5:
**1.70 mm of local backing**. Axial rays through the pocket find its bottom
blind roof at **Z 10.75 mm**. Above that roof, the local boss is solid to
its foam-facing surface at X=−133.5. Thus the section behind the seam changes
substantially within the scar's height.

At Z 5 mm, G-code lines 183780–183885 make the ordinary exterior loop. A
short travel from its closure leads directly to narrow gap infill behind
the same front-center face: lines 183892–183899 request widths from
0.178935 to 0.289726 mm. The following wipe retracts 0.76 mm along the gap-fill
path, followed by a 0.04 mm stationary retract. The exterior loop itself
does not have a separate wipe at that closure. Wipe-on is therefore an
effective recipe difference, not proof that the outer seam was wiped there.

The new photographs place the visible line directly outboard of this pocket.
The local backing and narrow fill make its location relevant to deposition.
The seam continues above the pocket's blind roof, so the hole alone cannot
account for the complete 23.48 mm scar. The relative contributions of local
geometry, ordinary seam behavior and actual deposition remain unmeasured.

## Preparation implication

A corrected preparation should explicitly transfer the selected A2 contour
seam treatment and wipe-off choice, with deliberate placement on an
uninterrupted wall away from insert pockets and ports. The native slice must
show the actual ramp and placement before attributing the faucet treatment
to it. This is specific to the shell preparation; the ordinary wall-packing
choice remains separate.

This record changes neither the sent archive nor the current shell geometry,
print settings or printer controls. Replacement of the copper slots by round
holes is a separate geometry and assembly proposal.
