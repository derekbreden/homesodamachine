# Front-top tree clearance

The fresh front-top preparation uses a **0.50 mm support/object XY distance**
with the production **0.30 mm Bottom Z distance**, **0.45 mm Top Z distance**
and unchanged tree branch dimensions. This is a bounded, part-specific
correction. The shared PET-GF profile and the funnel-frame support clearances
retain their own settings.

Derek reported small tree-trunk arches left on the top-facing seam land near
machine X105.690/Y34.793/Z165.194 and X82.129/Y7.118/Z165.194. Native STEP/STL
location readings place both windows on the Z165.195 seam land. A location
reading establishes the face being examined; the physical report establishes
the residue.

[Bambu's Bottom Z distance definition](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/PrintConfig.cpp)
controls separation beneath support interfaces above a model. These reported
contacts involve the sides of bed-rooted trunks grazing the seam land.
[Native tree generation](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/Support/TreeSupport.cpp)
also uses discrete support layers and branch collision geometry; a named Z
gap does not guarantee separation for this side contact.

The [offline probe record](probe-results.json) binds the rejected v17 geometry
and each emitted result by digest. Full support bead widths and actual support
road heights are compared with native seam stock and the actual deposited top
roads inside 7 mm picked windows.

| Probe | Bottom Z / XY gap, mm | Pick 1 contact, mm² | Pick 2 contact, mm² |
| --- | --- | ---: | ---: |
| Production reference | 0.30 / 0.40 | 0.03314 | 0.00546 |
| Bottom-only reading | 0.48 / 0.40 | 0.03314 | 0.00546 |
| Selected bounded XY correction | 0.30 / 0.50 | 0.00460 | 0 |
| Larger XY reading | 0.30 / 0.60 | 0.00019 | 0.01727 |

The selected XY setting reduces the first reference contact and removes the
second in that slice. It leaves a small first contact; physical cleanliness is
unqualified. Branch routing changes with the roof geometry; the
[fresh front-top's emitted contacts](front-top-h2c-v18/picked-roots.json) are
0.000875 and 0.000377 mm² in those windows. Increasing the gap further is not a
monotonic guarantee. A local branch exclusion or different tree style would
be a separate support trial if the remaining residue matters.

[Preparation](prepare_prints.py) creates fresh projects without replacing
reviewed archives. The H2C front-top retains its functional ceilings, current
solid-host density boxes, complete fine show-round band, nominal RC62 pocket
and one insertion pause. Its 0.50 mm XY correction is separate from the
combined Mark2 plate's production frame trees. That plate places the frame
aft, seventeen open RC62 pockets in the middle and five upright valve-socket
panels fore; fit samples have supports disabled individually and no pause.
The frame alone carries the new roof-side six-wall range.

The [combined Mark2 project and review](mark2-v2/README.md) pass all twenty-two
fit-object checks and the frame's native perimeter, support-contact and
removal-route checks. Its native estimate is 9 h 37 m 50 s / 357.43 g; the
[launch receipt](mark2-v2-launch.json) records its current status.

The [fresh H2C front-top project and review](front-top-h2c-v18/README.md) pass
the RC62 insertion pause and sealing paths, complete dense host/root regions,
retained fine show-round band and remaining support topology. Actual native
support roads are absent from the removed roof opening and both tee-window
cover slots. Five automatic tree bodies remain for separate functional
ceilings, without normal/snug object overrides. Its native estimate is
21 h 56 m 43 s / 749.06 g; the [launch receipt](h2c-v18-launch.json) records
current status. The frozen source input and reviewed archive are separate
from printer acceptance records.

[Picked-root reader](check_picked_roots.py) and
[combined native reader](review_combined.py) read archives without printer
communication. Emitted overlap, supports, removal lanes and density settings
do not qualify physical adhesion, cleanup, fit, magnetic retention or strength.
