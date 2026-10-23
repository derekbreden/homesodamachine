# Folded V-A within ideal X/Z bounds

V-A has vertical ports, inlet above outlet and head toward −Y, matching V-K.
One flush stem elbow connects the regulator outlet to V-A. The connected group
retains the lowered ASSE orientation, downward regulator head, 15 mm exposed
tee–regulator tube and existing pump adapters.

| Elbow arrangement | Group X | Group Z | Centered side gap | V-A outlet above core |
|---|---:|---:|---:|---:|
| Male stem into regulator: tighter fold | 173.3 mm | 98.9 mm | 11.8 mm each | 3.9 mm |
| Male stem into V-A: raised outlet | 186.3 mm | 98.9 mm | 5.3 mm each | 16.9 mm |

The raised-outlet arrangement places V-A 13.0 mm higher and 13.0 mm farther along
the regulator's outlet axis. Both arrangements use one identical elbow with a
trimmed 12.7 mm male stem; the other connection is a concealed 29.591 mm tube
between female mouths. Stem shoulders are flush under the accepted trimming
assumption. The modeled fitting profiles and unmeasured socket depths retain the
[reference models' estimated scope](../stem-fittings/README.md).

The current nominal enclosure is 215 mm wide with its exterior roof at Z355.
Plain 9 mm sidewalls leave **197 mm across X**; a 9 mm ceiling has its underside
at Z346. The current plain cold-core cap is at Z253.4, leaving **92.6 mm above
the core**. Both arrangements fit the width and exceed that height by **6.35 mm**.
ASSE defines the top of the group. The regulator also reaches 5.35 mm into the
ideal ceiling; the ASSE inlet and outlet TPU adapters reach 1.22 and 0.59 mm into
it. This comparison seats the scanned pump foot plane on the plain cap and
includes no mounting allowance.

The tighter fold places V-A's downward outlet 3.9 mm above the plain cap. The
raised outlet leaves 16.9 mm there. The study stops at that external connection
port: neither includes an outlet turn or claims a completed route to the flavor
manifold. Arbitrary water-in, vent, flavor and carbonator handoff stubs are omitted
from both the envelope and the view. Real local joints and adapters remain.

Only X/Z are assessed. Each group is centered independently across X. The view
uses plain sidewalls and ceiling, plus a cropped plain cold-core block. Its Y
extent is illustrative. Existing mounts, cuts, ceiling reliefs and all other
equipment above the core are outside the study. Production geometry is untouched.

[`ideal-space.json`](ideal-space.json) records the dimensions, derivation and
source datums. [`study.json`](study.json) records body poses, local and placed
connection datums, interface assumptions and measured envelopes. The manual mesh
check finds no unrelated-body intersections in either fold; intended mating
overlaps are excluded. This establishes geometry at the reference-model fidelity,
not a qualified installation.

From the repository root:

```sh
tools/cad-venv/bin/python hardware/manifold-layout/studies/folded-va-xz/study.py --check
```

`study.py` uses the committed reference meshes and writes display geometry under
ignored `out/`. The optional check runs only when requested; the study adds no
production build dependency or automatic gate.
