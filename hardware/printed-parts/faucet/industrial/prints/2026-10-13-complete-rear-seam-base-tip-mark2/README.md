# Approved production rear seam — Mark2 task 1337767162

Derek's [physical inspection](physical-result.json) on October 14 approves
the seam-fixed faucet as the current planned production model, tagged
`faucet-industrial-production-2026-10-14`.

> Faucet looks good. Please tag it. This latest with the seam fix is our official planned for now production model.

The latest physical print contains the corrected base and tip. The cover,
mounting plate and lever retain the [accepted complete-print reference](../2026-10-13-a2-back-mark2/physical-result.json).
The normal [production project](../../faucet-industrial-petgf.3mf) contains
all five rigid parts.

Mark2 accepted the base-and-tip evaluation at 11:45 pm CDT on October 13,
after one Send click. The fresh startup observation reports the new task
RUNNING at layer 0 with no printer error or HMS fault. Native estimate: 5 h 21 min 14 s
and 141.59 g; the launch estimated finish at 5:07 am CDT on October 14.
The physical result is accepted by direct user inspection.

Derek authorized the limited print after checking the other pieces:

> So could you please also check the tip and the mounting plate? And if they're good and they line up with this seam on the base, great, then start another print of base on Mark 2. Otherwise, print me everything that's got a problem that we need to verify is fixed here.

The [complete native review](../../seam-placement/rear-center-v2/README.md)
identifies the base's two lower deviations and a smaller tip offset at the
assembly joint. The evaluation includes both corrected pieces. The mounting
plate's exposed rim starts at rear X=0 and needs no correction. The normal
saved project retains the complete five-part faucet; this partial evaluation
supplies no standing authorization for partial faucet prints.

The two body meshes and the infill-only foot modifier are copied byte-for-byte
from the complete current project, including 477 base and 186 tip seam-enforcer
facets. The base retains its −15° pose and the tip its −105° pose. Their
centering translations are base X+50 mm and tip X+26/Y−45 mm. Automatic
supports, object settings, temperatures, cooling, A2/Back/150%, wipe off,
eight 0.24 mm lip layers and 0.12 mm shoulder bands are retained.

The [actual evaluation trace](trace/trace.json) reads all 2,530 base and 949 tip
exterior-wall runs, separating exposed rear starts from hole walls and other
contour components. It reproduces the complete candidate's rear seam paths
after the placement translations. The foot, body and lower neck start offsets
are at most 0.231, 0.083 and 0.116 mm respectively; the upper neck reaches
0.543 mm. The exposed curved tip stays within 0.188 mm. Approaching the joint,
the base and tip differ by 0.035 mm laterally. The [CSV](trace/seams.csv)
retains the starts and the overlap endpoints measured by the bounded-connector
reader in `a37392aa5`. Those recorded endpoints omit some final zero-flow
moves. The current reader retains every non-retracting E-word move, including
E0. Re-reading all 3,479 runs changes starts by at most 0.002 mm and final
endpoints by at most 0.401 mm; the seam-placement conclusions remain valid.

The [native review](native-review.json) binds the exact archive, mesh and
settings hashes. The full emitted bead envelope has at least 98.25 mm edge
clearance. Conservatively padded bead bounds for the two objects have a
2.87 mm gap, including their supports. Mark2's +0.04 mm trim emits
`G29.1 Z0.02` after reset to zero. There are no wipe or periodic G39 blocks.
Timelapse and bed leveling are On; flow dynamic and nozzle offset calibration
are Auto. Mark1's preceding acceptance was 39 min 58 s earlier, exceeding
the 180-second startup interval.

- [Exact launched native archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/faucet/industrial/prints/2026-10-13-complete-rear-seam-base-tip-mark2/2026-10-13-industrial-base-tip-full-rear-seam-petgf-left04-z004-mark2.gcode.3mf)
- [Editable evaluation project](2026-10-13-industrial-base-tip-full-rear-seam-petgf-left04-z004-mark2.3mf)
- [Source, settings and authorization](2026-10-13-industrial-base-tip-full-rear-seam-petgf-left04-z004-mark2.print.json)
- [Launch receipt](launch.json)
- [Preflight observations](preflight.json)
- [Fresh startup observation](startup.json)
- [Manual evaluation preparer](prepare.py)
