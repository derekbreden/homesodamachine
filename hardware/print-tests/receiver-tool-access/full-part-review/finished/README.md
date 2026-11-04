# Complete enclosure print set

The complete HSM-000081 back top, HSM-000079 front top, HSM-000082 lower pump
retainer and HSM-000020 equipment lid carry their production retention geometry.
Front top is printing on Mark1 as job **1405624302**. The other three parts have
prepared, reviewed archives and have not been submitted.

| Complete part | Printer | Estimate | Current review |
| --- | --- | --- | --- |
| HSM-000079 front top | Mark1 | 36 h 30 min | [Native slice and launch](front-top-mark1/print-job.json) |
| HSM-000081 back top | Mark2 | 27 h 45 min | [Continuous receiver bases](back-top-continuous-base/review.json) |
| HSM-000082 lower pump retainer | Mark1 | 5 h 58 min | [Native slice](pump-retainer/review.json) |
| HSM-000020 equipment lid | Mark1 | 7 h 12 min | [Continuous receiver bases](foam-cap-lid-top-continuous-base/review.json) |

The [readiness record](../readiness.json) binds each final mesh to its reviewed
native project and print archive. Binary files are delivered in
`/Users/derekbredensteiner/Downloads/HSM-full-enclosure-2026-11-03/`; Git holds
the recipes, hashes and reviews. Each print-only archive contains exactly the
reviewed G-code and its checksum. Editable projects are in `projects/` and the
complete sliced source archives are in `reviewed/`. Superseded receiver-tunnel
archives are separated under `superseded/receiver-tunnels/`.

Mark1 and Mark2 use their fixed left hardened 0.4 mm Standard nozzle with black
PET-GF. The emitted Textured PEI trims are +0.16 mm for Mark1 and +0.02 mm for
Mark2. Ordinary shell stock uses two walls and 15% gyroid; the retainer and lid
use their selected three-wall recipe. Projects include the complete local solid
hosts and specified surface bands.

The native reviews read deposited model, support and brim beads against the
20 mm bed border. They also read the fine/transition bands, show-face contacts,
local dense-host deposition, tie openings and removable groove ribbons where
applicable. Support decisions retain Tree(auto)/Default. The lid's constrained
branch growth keeps its automatic supports within the bed border.

Follow the [support-removal instructions](support-removal.json) on each loose,
unloaded part before installing hardware. They include every small support
body without interface labels. Use the tiny flathead already used successfully
inside rear receiver cavities, cut larger branches into pieces, and withdraw
through the named open mouths. The rear bases have no enclosed release tunnels.

The [retained-fit reading](../../asse-alignment/retained-fits.json) records zero
native overlap of the installed caps with the updated receivers and unchanged
PISCO, meter, regulator and pump cap meshes. The ASSE adapter and conforming hex
cavity rise 0.18 mm together; the [alignment reading](../../asse-alignment/geometry-review.json)
records the centered wrench band and unchanged ASSE-body and wing material.
The [assembly integration](../../asse-alignment/assembly-integration.json)
and [publication](../../asse-alignment/publication.json) bind the full native
machine, installed scene and installation views. The lower cartridge retains
its complete paired, pointed-wing geometry and source +Y build axis.

Derek's [latest completed-job result](../../physical-result/physical-result.json)
accepts PISCO and regulator fit and identifies the ASSE assembled alignment.
Mark2's pump/meter/cartridge job continues. No separate ASSE fit print is planned;
combined seating is verified during normal full-enclosure assembly.
