# Folded V-A within ideal X/Z bounds

V-A has vertical ports, inlet above outlet and head in the same direction as V-K.
The regulator connects to the female socket of one stem elbow; that elbow's
trimmed male stem inserts into V-A's upper port. V-A's lower port is **16.9 mm
above the cold-core cap**. A second stem elbow turns that outlet forward toward
the flavor manifold; its exterior clears the cap by **3.11 mm**. The connected
group retains the lowered ASSE orientation, downward regulator head, 15 mm exposed
tee–regulator tube and existing pump adapters.

The discharge-side rear rubber slider occupies its reference position on the
pump's rail. Its translation from the captured study benchmark is 30 mm toward
the motor rear. It has **9.69 mm nearest clearance to the carbonator outlet
elbow** and **13.36 mm to a full 24 mm downward outlet-tube continuation**. The
view's carbonator direction stub ends at the cap face. These are explicit path
clearances; the general unrelated-body check excludes tubes and clamps.

The entire connected group is registered to the enclosure with a proper 180° Z
rotation of the free-space study frame. The ASSE inlet points toward the actual
**+Y back wall**, pump discharge points −X, and both valve heads point aft (+Y).
This changes no internal component orientations. The back-wall reference is a
plain 9 mm slab at Y462.3–471.3, with an illustrative 10 mm gap to the rearmost
hardware. Its purpose is orientation; full Y packing remains outside this study.
The cap block is cropped in Y for display. Water-in and flavor handoff stubs
show connection directions without claiming completed installation routes.

The hardware group, including the V-A outlet elbow, occupies **186.3 mm across X**
and **98.9 mm across Z**. The current nominal enclosure is 215 mm wide with its
exterior roof at Z355.
Plain 9 mm sidewalls leave **197 mm across X**; a 9 mm ceiling has its underside
at Z346. The current plain cold-core cap is at Z253.4, leaving **92.6 mm above
the core**. Centering the group gives **5.35 mm per side**; it exceeds the available
height by **6.35 mm**.
ASSE defines the top of the group. The regulator also reaches 5.35 mm into the
ideal ceiling; the ASSE inlet and outlet TPU adapters reach 1.22 and 0.59 mm into
it. This comparison seats the scanned pump foot plane on the plain cap and
includes no mounting allowance.

External handoff stubs are excluded from the hardware envelope. Existing mounts,
cuts, ceiling reliefs and all other equipment above the core are outside the
study. Production geometry is untouched.

Stem shoulders sit flush under the accepted trimming assumption. Valve/regulator
insertion is estimated at 12.7 mm; the concealed tube joining the regulator and
elbow is 29.591 mm. The fitting profiles and unmeasured socket depths retain the
[reference models' estimated scope](../stem-fittings/README.md).

[`ideal-space.json`](ideal-space.json) records the dimensions, derivation and
source datums. [`study.json`](study.json) records body poses, frame registration,
connections, envelopes and manual body/path clearances. The manual mesh check
finds no unrelated-body intersections; intended mating overlaps are excluded.
The checks establish geometry at the reference models' fidelity, not a qualified
installation.

From the repository root:

```sh
tools/cad-venv/bin/python hardware/manifold-layout/studies/folded-va-xz/study.py --check
```

`study.py` uses the committed reference meshes and writes display geometry under
ignored `out/`. The optional check runs only when requested; the study adds no
production build dependency or automatic gate.
