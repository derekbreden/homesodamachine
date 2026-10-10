# Complete industrial faucet with 0.12 mm shoulders

This is the [selected queued faucet](../../selected-print.json) for Mark2 after
the three-organizer plate. All five rigid parts are included: industrial shell
base, shared shell tip, industrial display cover, above-counter plate and the
accepted side-down lever replica. The native estimate is **5 h 46 min 56 s**,
with 152.24 g at the saved profile density. No Send has been attempted.

Every part has a 0.20 mm first bed layer and 0.24 mm normal layers. Only the base
uses 0.12 mm in the two bands crossing the selected annular shoulder faces.
The base retains its −15° X print rotation; all five meshes and placements match
the [complete 0.08 mm shoulder reference](../2026-10-09-two-shoulders008-with-lever-mark2/README.md).

| Selected CAD face | Complete face span in print Z | Base 0.12 mm band in print Z |
| --- | --- | --- |
| Z14.0 mm, normal +Z | 13.87165–28.79329 mm | 13.40–29.00 mm |
| Z57.5 mm, normal +Z | 55.46309–67.83949 mm | 55.16–68.12 mm |

The bands apply to the whole base cross-section at those heights. The native
wall paths cover both selected faces continuously at 0.12 mm. The tip, cover,
plate and lever emit 0.24 mm above their first bed layers.

The base has one continuous foot modifier, with six walls and 100% zig-zag
infill through CAD Z−0.01–14.01 mm and XY−30.5–30.5 mm, plus Arachne wall widths
on the base only. The other four objects retain Classic walls. The
[outer-wall reading](outer-wall-review.json) finds zero repeated starts or stops
at all three rectangular screw-host boundaries that correspond to the
reference article's exterior lines.

The [insert deposition review](insert-beads.json) covers 98, 98 and 119 complete
native slabs at the three insert stations. Minimum commanded coverage through
the host bodies and caps is 98.52%, 98.68% and 98.60%; minimum connected outer
backing is 2.10 mm around the installed Ø4.6 mm brass. Its
[input record](deposition-input.json) and [bead image](insert-host-commanded-beads.png)
retain the geometry and diagnostic pores. This establishes commanded paths and
nominal backing; deposited bonds and load capacity remain unmeasured.

The successful reference's global process settings are preserved byte for
byte: 265/280 °C nozzle, 80 °C bed, two walls outside the reinforced foot,
15% grid infill, 15% infill/wall overlap, normal speeds and motion, and Tree
(auto) with the saved Default style and automatic sections. No sampled support
midpoint projects inside either selected face's 0.4 mm interior inset. The
complete model/support/brim bead envelope retains 25.12 mm usable-bed clearance.

The material is black PET-GF, labelled PET-CF/GFT01 at left external slot 254,
using Mark2's fixed left hardened standard-flow 0.4 mm nozzle on Textured PEI.
Requested +0.04 mm Z trim emits +0.02 mm. Nozzle Clumping Detection by Probing is
disabled. Planned foreground Send options are Timelapse On, Auto bed leveling
On, Flow dynamic calibration Auto and Nozzle Offset Calibration Auto.

[Preparation](preparation.json) binds the two frozen source projects, five mesh
hashes and settings. [Native checks](native-check.json) bind the final archive,
G-code, emitted layers and reinforcement. The [launch plan](launch-plan.json)
queues this exact archive after organizer task/job `1325126748`; its plate must
be physically cleared, both printers read freshly, and the peer's latest accepted
start or resume must be at least 180 seconds earlier. There is no automatic
start or scheduled monitor.

The reference article's beautiful 0.08 mm shoulder finish and successful removal
of its few thin-layer supports remain scoped to that identified print.
The queued 0.12 mm finish and corrected exterior have no physical result yet.
Whole-faucet 0.08 mm iteration is deferred.
