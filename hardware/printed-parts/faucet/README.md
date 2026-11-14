# Faucet styles

The faucet has two styles, each in Black or White PET-GF.

| Faucet style | Shape | PET-GF print project |
|---|---|---|
| **Sculpted** | Smooth curves and softly blended transitions. | [Production project](faucet-petgf.3mf) · [print settings](sculpted/README.md) |
| **Industrial** | Simple cylinders and crisp shoulders. | [Production project](industrial/faucet-industrial-petgf.3mf) · [print settings](industrial/faucet-industrial-petgf.md) |

**Finish** is a separate Black or White choice in the [3D viewer](/3d).
It applies to the PET-GF shell, display cover and above-counter plate.
The retained Westbrass lever, display glass, tubing and TPU gasket keep their
own materials and colors. Each style uses one geometry in either finish.
Both styles include one black PET-GF [umbilical organizer](umbilical-organizer/README.md)
below the mounting workspace, with A's accepted Ø6.65 mm soda bore and
three Ø4.40 mm flavor/drain bores. The Ø4.40 mm fit is accepted on the white
drain stock; black 4 mm flavor-stock fit is unmeasured. The measured ribbon uses a 5.4 × 1.8 mm
flat signal slot in the organizer.

The [Sculpted texture timing study](texture-comparison/2026-09-24/README.md)
compares selected 0.08 mm regions with the saved 0.24 mm finish and an all-0.08 mm
plate. It also times the accepted printed lever separately.

## Overflow drip indicator

The upper bend and tip have smooth tangent walls around the tube and flat
ribbon clearances. The flavors share a capsule without a central divider
or outlet cusp. The curved joint is at 70°, with a female base and male tip. The white 4 mm OD / 2.5 mm ID drain
tube ends square with 3 mm of local mouth clearance. A round Ø4 mm underside
hole opens from the common passage clearance over the bowl. The drink tubes
continue to the dispense face: Ø9.525 mm soda and two Ø4 mm black flavors,
inside a smooth shared opening without a divider between the flavor clearances. No drain gasket, bung or insertion
tool is required.

The intended result is a visible drip indicating a major fault. Incidental
liquid escape into the housing is accepted for that event; the faucet is not
a sealed drain connection. [Drain geometry evidence](vent-qualification/README.md)
records the actual tube clearance and hole-to-passage connection. Physical
drip behavior and complete fault-vent capacity are unmeasured.

## Parts

Both styles enclose the same harvested Westbrass, printed lever, Waveshare
faucet display, four LLDPE tubes and continuous insulated signal conductors. They share
the curved gooseneck joint, the three hidden mounting screws and the stainless
under-counter plate. They also share one head: the tip, whose ledge carries the lowered
display with a recess for each of its feet and a pocket for each of its switches, and the
display cover. The cover's preformed side walls seat their broad lips in the tip's retaining
grooves. The printed cover is its relaxed shape. Assembly models show its nominal
seated surface.

| Piece | Sculpted | Industrial |
|---|---|---|
| Shell base | [STEP](faucet-shell/faucet-shell-base.step) · [STL](faucet-shell/faucet-shell-base.stl) | [STEP](industrial/industrial-shell-base.step) · [STL](industrial/industrial-shell-base.stl) |
| Shell tip, shared | [STEP](faucet-shell/faucet-shell-tip.step) · [STL](faucet-shell/faucet-shell-tip.stl) | Same part |
| Display cover, shared | [STEP](faucet-display-cover/faucet-display-cover.step) · [STL](faucet-display-cover/faucet-display-cover.stl) | Same part |
| Above-counter plate | [STEP](above-counter-plate/above-counter-plate.step) · [STL](above-counter-plate/above-counter-plate.stl) | [STEP](industrial/industrial-above-counter-plate.step) · [STL](industrial/industrial-above-counter-plate.stl) |
| Above-counter gasket, TPU | [STL](above-counter-gasket/above-counter-gasket.stl) | [STL](industrial/industrial-above-counter-gasket.stl) |
| Umbilical organizer, shared | [STEP](umbilical-organizer/umbilical-organizer.step) · [STL](umbilical-organizer/umbilical-organizer.stl) · [accepted fit and settings](umbilical-organizer/README.md) | Same part |

Use the matching base, plate and gasket for the selected style.
Both current PET-GF projects contain the base, tip, cover, plate and
side-down lever replica.
The gasket is a separate TPU print.
The organizer is a separate PET-GF print, fitted during
[umbilical assembly](../../assembly/faucet-and-umbilical.md).

The [display acceptance record](faucet-display-cover/physical-acceptance.json)
identifies the tested physical article. The current complete Industrial
project uses the [selected printing recipe](industrial/finish-selection.json):
Back with A2 on the base, tip and mounting plate, rear-center seam enforcement
through the base's full rear silhouette and the tip's exposed curved neck, default Aligned/15%/scarf-off
seams on the cover and lever, **Bambu’s 0.20 mm first bed layer and 0.24 mm later
layers**, with no fine bands.
The [production selection](industrial/production-selection.json) names the
five generated parts the Industrial plate prints, the Industrial base, the shared
tip and cover, the rigid Industrial plate and the side-down lever, and beside each
the mesh of the approved print it is read against. The [October 25 approval](faucet-display-cover/prints/2026-10-25-front-overlap-black-mark2/physical-result/physical-result.json)
accepts the remaining visible corner gap as good enough, with no further
iteration requested. The cover in its current shape, with reach on its sides
and pockets at its crown, is approved on the shared tip by the
[complete Sculpted faucet's result](https://github.com/derekbreden/homesodamachine/blob/727125473a61a56604e145292ffd41d6984f49a0/hardware/printed-parts/faucet/sculpted/prints/2026-11-13-sloped-underside-complete-mark2/physical-result/physical-result.json),
which Derek calls the best fit so far. The one flaw he names is a hole in the tip
that the cover does not quite cover. Historical physical and sealed-cavity records retain
their identified geometry and material scope.

The [assembly procedure](faucet-shell/ASSEMBLY.md) supplies the shared mounting,
tube routing and display seating order. The Industrial base has a round foot
and rectangular lever opening; its mounting stations and hardware are shared.
The complete printed assembly supplies the physical readings of lever travel,
display fit, snap retention and surface finish.

## Prepare the approved Industrial print

```
tools/run -- cargo build --release --locked --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep
tools/hsm/target/release/industrial-faucet-print-project
```

The production preparer reads the generated parts the production selection names
and retains the selected process, supports and per-printer trim. Preparing a
project does not submit it to a printer.

`hsm --scene faucet` reads the current exported assembly for positions,
clearances, intersections, sections and rays. [`inspect-part.mjs`](/tools/inspect-part.mjs)
retains the selected geometry, camera and targeted measurements between exports.
The [native printed-mesh review](/tools/hsm/mesh-review/README.md) ranks local
anomalies in the print meshes without rebuilding the faucet.

The [simple drip geometry reading](vent-qualification/simple-drip-check.json)
binds both bases and the shared tip, verifies the joint and nominal tube
clearance, and records the absent material at the two picked defects.
The retained centered-vent and sealed-port records apply to their exact
sealed-cavity source and artifact hashes.

The [4 mm dispense specification](flavor-lines/README.md) covers the outlet valves, reducers, rear fittings, tube supports, mounting stack and tip. The 27 mm gooseneck retains the water/cable datums and two 2 mm joint walls. Its current minimum inner joint wall is 2.21 mm; the smaller flavor tubes reduce the shared passage and dispense opening.
