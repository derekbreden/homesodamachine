# datum-01-datum-chain: what each reference makes unnecessary

Scene: `scenes/datum-01-datum-chain/index.html`. Depth: developed. Origin: swarm. A way of seeing the problem; it proposes no mechanism.

## Picture it

One elevation of the rig, drawn to scale in height: bench, feet, base, turntable and nest, the tube, the plate 6.35 mm below the rim, the dot in the corner. Beside it a chain of links from the room to the corner. Click where the gun is referenced from (room, rotator base, turntable, rim, plate face, the seam itself) and the links above that point light up amber while the links below drop out. Bars show what spread is left in height and in radial position, against a placeholder window.

## The proposal

The gun's pose that matters is gun-to-corner, and the corner belongs to each tube and plate. Whatever the gun is located from, the links between that reference and the corner still add error, and the links on the other side stop mattering. A reference on the work travels with the work, so the links below it fall out; a reference in the room cannot do that. The scene lets the reader choose the height reference and the radial reference separately and edit each link's spread, and it lists what software could know under each choice.

## What carries the loads, what establishes position, what is free or restrained

Not a support proposal. It asks what position is *established from*, not what carries the gun. Free/restrained/driven: nothing moves in the scene.

## What software could command, observe, and what stays manual

Depends on the reference (the I/O panel changes with it): a room or rotator-base reference gives axis positions and nothing about the work; a rim reference adds a contact; a plate-face reference adds a plunger reading; the seam itself is the only one that reads the dot against the corner and needs a sensor that can see or feel it. Manual under every reference: whatever the reference does not know (tube length and seat depth per tube for the room, base and turntable references), and always the dot versus the melt position.

## What was tried to break it

Numbers from `calc/datum_chain.py` (`calc/datum_chain.out`); every spread is illustrative unless tagged.

1. **Plate face as the radial reference.** *Conflict:* pins in the ports, a mast on the plate. *Assumption:* the plate is concentric with the bore. *What the scene shows:* it is a slip fit with 0.005 in radial play [repo] (0.128 mm [derived]); the plate centre is a *worse* radial datum than the wall, and a term appears that the wall reference lacks. The plate face stays a good *height* datum. *Uncertain:* the plate is only tacked when the gun would hang from it.
2. **Seam-direct removes every link, but not to zero.** *Assumption:* the dot marks where the melt lands. *What the scene shows:* a dot-versus-melt term stays in every option; the total never reaches zero. Only a witness pass (datum-11) touches it. *Uncertain:* its size.
3. **The rim reference leaves seat depth.** *Assumption:* seat depth varies tube to tube [repo says it varies, not by how much]. *What the scene shows:* at the default spreads the seat-depth bar is the largest one left for the rim reference (worst case 0.85 mm, RMS 0.55 mm, against 0.23 / 0.20 for the plate face). *Change:* a plunger on the plate face at the station (datum-03) or an eddy scan through the wall (datum-06). *Uncertain:* whether a plunger fits beside the gun.
4. **What if the two unknown spreads are small?** Cutting the tube-length and seat-depth spreads to 0.10 mm brings the rim reference to 0.45 / 0.25 (worst / RMS) and the room reference to 1.36 / 0.49: the ordering of references stays, the gaps shrink. The scene's message therefore is not "the room datum is hopeless" but "measure the two unknown spreads across the tubes on hand before deciding how much of the chain to remove".

### Wave 3 (from `exchange/datum--reply-to-travel-w3.md` and the new region)

- **The two links left under the rim are made, not measured.** *Conflict:* seat depth and plate tilt were treated as properties of the tube. *What the scene shows now* (`How the plate was seated`): the plate is an ID-fit plug whose diagonal (123.607 mm) is shorter than the bore (123.698 mm), so the slip fit does not square it at any tilt (`calc/plate_seat.js`); its depth and tilt are how it was held. By hand to a spacer: depth 0.50 and tilt 0.10 (illustrative); placed by the setting ring's plug (`datum-22`): 0.06 and 0.03. The rim reference then carries almost nothing from the plate. *Uncertain:* every spread; the tack pull.
- The scene is a lens (its tags say so): it draws no arrangement, only where a reference comes from.

## Branches and combinations

None as separate scenes. The other datum scenes are mechanisms that realise particular choices here: datum-03 (rim), datum-04 (wall at the station, seam), datum-05 (collar or flange on the work), datum-06 (plate face through the wall), datum-07 (seam, by touch).

- **Checking a reference:** a reference in the room can also be *checked* against the work by a probe: the tabletop against the rim (`datum-18`), a corner in the dock against the tube (`datum-15`), the rim circles and ports against the camera (`datum-19`). Each drops a link out of the chain at run time instead of choosing it at design time.

## Unresolved problems and questions for Derek

- **Measure, on the tubes you have:** tube length spread and rim-to-plate-face depth spread (a depth gauge and calipers). These two sliders are the largest and they are [unknown].
- Runout limits are the rig doc's acceptance limits [repo]; actual runout after indicating is not recorded here.
- What accuracy does the dot need against the corner? The window slider is a placeholder.

## Assumptions

- Nominal heights: tube bottom 86 mm above the bench, rim 238.4 mm, recess 6.35 mm, so the corner is 232.05 mm above the bench [repo][derived]. Radial runout 0.25 mm TIR and face 0.30 mm TIR [repo] (half each as a spread; the face limit split 0.11/0.10 into a part common to rim and plate and a plate-seat part: illustrative split). Plate slip 0.005 in radial, nest clearance 0.20 mm nominal [repo].
- Everything else (clamp, race float, spreads of length, depth and tilt, ovality, reference repeatability, dot-versus-melt, window) illustrative.
- Spreads combined as if independent and constant.

## Sourcing pointers

None needed; no hardware.

## Scene id

`datum-01-datum-chain`.
