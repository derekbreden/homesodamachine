# G Ganen integration boundary

The measured G Ganen reference supplies the rigid housing, independent port
profiles and one shared purchased rubber-foot shape. Production placement uses
[`installation/g_ganen_installation.py`](installation/g_ganen_installation.py).
The [installation record](installation/README.md) carries the selected mounting
stations and native checks. Current enclosure generation and print status belong
to [print readiness](../../printed-parts/enclosure/print-readiness.md).

## Placement and flow

The reference has X=0 at the motor/head junction, +X toward the motor rear, and
Z=0 at its retained bearing datum. Production places that datum directly on the
cap lid and uses the rigid motor rear for the fore/aft placement rule. Moving a
foot along its rail does not move the rigid pump or either port.

The installed +90° Z rotation maps local +Y discharge to **enclosure −X**.
Suction faces east and discharge faces west. `build_water_pump` resolves lateral
room against the pan and rear-fitting lanes, and uses the installation module's
rear-clearance value. Pump/foot, cap, rear unions and hose clearances use the same
placed native geometry.

## Common feet and cap mounts

Derek confirms four identical removable sliding rubber feet with approximately
7 mm pads. `common-foot/g_ganen_foot.py` builds their shared nominal installed
shape, including visible slots, underside reliefs and the exposed clip mouth.
The raw scan poses remain measurement evidence, not four different foot shapes.

The selected slot centres are reference X=9.5 and 67.5 mm, Y=±38.5 mm, Z=0.
Their ±9 mm axial clip spans fit wholly within the visible rail interval
X=0.5–76.5 mm. These are outermost full-engagement positions, not claimed hard
travel stops or a retention rating for partial overhang.

Each M3 × 20 screw axis is 1.5 mm outward within its slot, at Y=±40 mm. This
leaves the Ø9 × 0.8 mm washer flat on the nominal 7 mm pad and clear of the raised
shoulder. `CAP_MOUNT_XY`, `mount_stations()` and `mount_holes()` carry those screw
axes into the printed cap. `_cold_core_interface.deck_mounts['g-ganen-pump']`
derives the four columns, lid holes and screw stack from that installation.
The insert is ruthex M3 × 5.7; the blind screw bore is at least 8.5 mm deep.

The native model checks screw passage, washer contact, column stock and adjacent
parts. Actual rubber compression, tightening feel and retention are checked
while assembling the printed enclosure. Hidden rail grip surfaces are not a
replacement-foot manufacturing specification.

## Ports, routes and contact

Use each port's own tip, axis and exterior profile. `suction()`, `discharge()`
and `port_profile()` retain the separate measured ports. `profiled_barb_length()`
provides the observed exterior length; it does not certify completed hose
insertion or clamp retention. The two reinforced-PVC hoses preserve the measured terminal axes and their
R15.9 minimum bend requirement.

`pan_front_y` reads the placed discharge envelope. The pan has its own clearance
span and service path. Suction/discharge chains remain seated on their cap
anchors; pump placement and both hoses are checked together without treating the
chain mounts as pump-foot stations.

The fixed casing reference fills reentrant rail/cradle regions. Attributed
foot/rail overlap inside that filled envelope is distinct from a collision with
an external neighbor. Cap bearing checks keep the complete rigid body separate
from the four named foot masks and retain every unrelated contact.

## Generation and evidence

Generate the cap, foam assembly and cold-core assembly before Box, shell pieces
and the combined assembly. Freeze the resulting STEP/STL/payload inputs and
current assembly gates before native slicing and support review. Print records
remain bound to their exact input and toolpath hashes.

The detailed reference and conservative integration envelope have separate
manifests. The integration envelope retains native component containment and
round-trip evidence; the four feet are exact shared-shape copies. Historical
query timings keep their original native STEP identity and are not a current
performance guarantee. For occupied sections, `native_queries.intersect_components`
checks native components individually, and `occupied_bounds` returns `None` for
an empty section.
