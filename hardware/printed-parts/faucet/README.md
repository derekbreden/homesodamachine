# Faucet styles

The faucet has two styles, each in Black or White PET-GF.

| Faucet style | Shape | PET-GF print project |
|---|---|---|
| **Sculpted** | Smooth curves and softly blended transitions. | [Sculpted project](faucet-petgf.3mf) · [print settings](faucet-petgf.md) |
| **Industrial** | Simple cylinders and crisp, pronounced shoulders. | [Held complete variable-layer print](industrial/prints/2026-10-09-shoulders012-wing050-drip4-mark2/README.md) · [print settings](industrial/faucet-industrial-petgf.md) |

**Finish** is a separate Black or White choice in the [3D viewer](/3d).
It applies to the PET-GF shell, display cover and above-counter plate.
The retained Westbrass lever, display glass, tubing and TPU gasket keep their
own materials and colors. Each style uses one geometry in either finish.
Both styles include one black PET-GF [umbilical organizer](umbilical-organizer/README.md)
below the mounting workspace, with A's accepted Ø6.65 mm beverage bores and
B's accepted Ø4.40 mm drain bore. The loose Ø5.00 mm signal passage is retained.

The [Sculpted texture timing study](texture-comparison/2026-09-24/README.md)
compares selected 0.08 mm regions with the saved 0.24 mm finish and an all-0.08 mm
plate. It also times the accepted printed lever separately.

## Overflow drip indicator

The white 4 mm OD / 2.5 mm ID drain tube ends square inside an unsealed
pocket in the tip. A round Ø4 mm underside hole opens at the pocket's
upstream low corner, over the bowl. Two plain 2 mm printed guide walls carry
the continuous beverage tubes and insulated conductors. The drain needs no
additional gasket, bung or insertion tool. Its opening is separate from the
three beverage outlets.

The intended result is a visible drip indicating a major fault. Incidental
liquid escape into the housing is accepted for that event; the faucet is not
a sealed drain connection. [Drain geometry evidence](vent-qualification/README.md)
records the actual tube clearance and hole-to-pocket connection. Physical
drip behavior and complete fault-vent capacity are unmeasured.

## Parts

Both styles enclose the same harvested Westbrass, printed lever, Waveshare
faucet display, four LLDPE tubes and continuous insulated signal conductors. They share the
[shell tip](faucet-shell/faucet-shell-tip.step), the curved gooseneck joint,
the three hidden mounting screws and the stainless under-counter
plate. The cover's preformed side walls seat their broad lips in the tip's
retaining grooves. The printed cover is its relaxed shape; assembly models
show its nominal seated surface.

| Piece | Sculpted | Industrial |
|---|---|---|
| Shell base | [STEP](faucet-shell/faucet-shell-base.step) · [STL](faucet-shell/faucet-shell-base.stl) | [STEP](industrial/industrial-shell-base.step) · [STL](industrial/industrial-shell-base.stl) |
| Shell tip, shared | [STEP](faucet-shell/faucet-shell-tip.step) · [STL](faucet-shell/faucet-shell-tip.stl) | Same part |
| Display cover | [STEP](faucet-display-cover/faucet-display-cover.step) · [STL](faucet-display-cover/faucet-display-cover.stl) | [STEP](industrial/industrial-display-cover.step) · [STL](industrial/industrial-display-cover.stl) |
| Above-counter plate | [STEP](above-counter-plate/above-counter-plate.step) · [STL](above-counter-plate/above-counter-plate.stl) | [STEP](industrial/industrial-above-counter-plate.step) · [STL](industrial/industrial-above-counter-plate.stl) |
| Above-counter gasket, TPU | [STL](above-counter-gasket/above-counter-gasket.stl) | [STL](industrial/industrial-above-counter-gasket.stl) |
| Umbilical organizer, shared | [STEP](umbilical-organizer/umbilical-organizer.step) · [STL](umbilical-organizer/umbilical-organizer.stl) · [accepted fit and settings](umbilical-organizer/README.md) | Same part |

Use the matching base, cover, plate and gasket for the selected style.
The PET-GF projects each contain the base, shared tip, cover and plate.
The gasket is a separate TPU print.
The organizer is a separate PET-GF print, fitted during
[umbilical assembly](../../assembly/faucet-and-umbilical.md).

The [display acceptance record](faucet-display-cover/physical-acceptance.json)
identifies the tested physical article. Current production geometry uses the
matching style project and [native review](vent-print-readiness/README.md).

The [assembly procedure](faucet-shell/ASSEMBLY.md) supplies the shared mounting,
tube routing and display seating order. The Industrial base has a round foot
and rectangular lever opening; its mounting stations and hardware are shared.
The complete printed assembly supplies the physical readings of lever travel,
display fit, snap retention and surface finish.

## Generate Industrial

```
tools/cad-venv/bin/python hardware/printed-parts/faucet/industrial/industrial_faucet.py
tools/cad-venv/bin/python hardware/faucet-layout/faucet_industrial_assembly.py
tools/cad-venv/bin/python hardware/printed-parts/faucet/industrial/prepare_print_project.py
```

The Industrial generator reads the current Sculpted base's shared upper
gooseneck. Both assemblies use the same hardware locations and tube paths.
Printable meshes use the faucet's absolute tessellation tolerance;
their viewer payloads retain every print triangle.

The [Industrial geometry readings](industrial/geometry-check.json) cover the
saved solids, hardware, lever travel and named wall sections. The
[display cover readings](industrial/display-cover-check.json) cover display fit,
wing geometry, loading and seating. Their reproducible readers are
[`check_geometry.py`](industrial/check_geometry.py) and
[`check_display_cover.py`](industrial/check_display_cover.py).

The [simple drip geometry reading](vent-qualification/simple-drip-check.json)
binds the current shared tip, verifies its open connection and nominal tube
clearance, and locates the change away from the joint and dispense face.
The retained centered-vent and sealed-port records apply to their exact
sealed-cavity source and artifact hashes.
