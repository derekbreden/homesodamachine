# Complete industrial faucet with tip grid supports

This Mark2 plate contains the shell base, shell tip, display cover, counter plate
and accepted side-down lever replica. All five objects use 0.08 mm normal layers
above the 0.20 mm first bed layer. Their frozen normal meshes and placements match
the [identified complete faucet](../2026-10-09-all008-strong-support-mark2/README.md).
The base keeps Arachne and its continuous foot modifier with six walls, 100%
zigzag infill and 15% infill/wall overlap. The other four objects use Classic.

[Physical result](physical-result/physical-result.json) records the operator's
report that the narrow starting edge of the model lifts during the first 0.08 mm
layers above the 0.20 mm bed layer. This interpretation applies to this last
article. The completed timelapse does not resolve the initiating lift or impact.
The complete article is canceled; finish and support cleanup are unevaluated.

| Setting | This prepared job |
| --- | --- |
| Tip support type / style | Normal automatic / Grid |
| Tip support base pattern / spacing | Rectilinear / 1.5 mm |
| Tip normal-support expansion | 2 mm |
| Other objects' support style | Strong tree, two walls |
| Support body / interface speed | 60 / 40 mm/s |
| Default acceleration | 2,000 mm/s², applied at job level |
| Wipe while retracting | Disabled for this job |
| Z-hop type / height | Normal vertical lift / 0.4 mm |
| Avoid crossing walls / include supports | Enabled; maximum detour 50 mm |
| Support top / bottom Z gap | 0.45 / 0.30 mm |
| Support XY gap | 0.40 mm |
| PET-GF nozzle temperatures | 265°C first layer, 280°C above |
| Textured PEI bed | 80°C |
| Mark2 Z trim | +0.04 mm requested, +0.02 mm emitted |
| Probing clump detection | Disabled |

The job-level acceleration override reaches support extrusion; an object setting
alone does not establish an emitted support acceleration. The native tip support
paths command 2,000 mm/s². [Native checks](native-check.json) count zero retract-wipe
blocks and retain departure witnesses that retract in place, lift vertically,
travel and return to print height. These witnesses do not establish clearance
above an unknown curl or remove every short unretracted move. Wiping is disabled
for the complete job, so additional stringing remains a physical possibility.
Startup purge and chute cleaning remain in the native start sequence.

The [support comparison](tip-support-comparison.png) shows the native supporting
scaffold. At print Z1 mm its largest connected commanded cross-section is
273.26 mm², alongside two separate side support regions. The readings describe
ideal bead connection, not physical bonding. Normal grid supports and greater
footprint target stability; support cleanup and contacted surfaces require the
print. All complete model/support/brim beads retain a 25.71 mm minimum bed margin.

The native estimate is **17 h 24 min 6 s**, using 181.67 g at the saved profile
density. [Preparation](preparation.json), [native preview](native-preview.png),
[launch plan](launch-plan.json), [preflight](preflight.json) and [launch receipt](launch.json)
bind the exact complete five-part plate. Foreground options are Timelapse On,
Auto bed leveling On, Flow dynamic calibration Auto and Nozzle Offset Calibration
Auto. The print has no programmed insertion pause. Physical finish and support
stability remain unevaluated.

Mark2 accepted task/job `1324180997` at 2026-10-09 14:36:53 CDT
(19:36:53 UTC) through one foreground Send. The operator stopped the job. A fresh
reading identifies the same archive in FAILED state, print error0 and no HMS
faults. The [tip starting-band trial](../2026-10-09-tip-root024-mark2/README.md)
records the normal-settings preparation for the next complete faucet.
