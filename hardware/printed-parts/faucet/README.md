# Faucet styles

The faucet has two styles, each in Black or White PET-GF.

| Faucet style | Shape | PET-GF print project |
|---|---|---|
| **Sculpted** | Smooth curves and softly blended transitions. | [Sculpted project](faucet-petgf.3mf) · [print settings](faucet-petgf.md) |
| **Industrial** | Simple cylinders and crisp, pronounced shoulders. | [Industrial project](industrial/faucet-industrial-petgf.3mf) · [print settings](industrial/faucet-industrial-petgf.md) |

**Finish** is a separate Black or White choice in the [3D viewer](/3d).
It applies to the PET-GF shell, display cover and above-counter plate.
The retained Westbrass lever, display glass, tubing and TPU gasket keep their
own materials and colors. Each style uses one geometry in either finish.
Both styles include one black PET-GF [umbilical organizer](umbilical-organizer/README.md)
below the mounting workspace, with the accepted L fit's beverage bores and a
drain bore 0.10 mm larger than L's.

The [Sculpted texture timing study](texture-comparison/2026-09-24/README.md)
compares selected 0.08 mm regions with the saved 0.24 mm finish and an all-0.08 mm
plate. It also times the accepted printed lever separately.

## Consumer vent arrangement

Simply having a 1022 already puts us ahead of most of these products. A 1022 that vents into the bowl at the faucet would be the only home arrangement I've found where the vent's discharge is defined, drained and visible.

The white 4 mm drain tube runs between the two flavor tubes, above the soda
tube. It ends square inside the circular chamber in the tip. Water flows around
the continuous drink tubes and leaves a separate bottom opening over the sink.
Two retained TPU bungs isolate that chamber from the dry passages and display.
The drink face retains its symmetric three-tube arrangement.

The [print readiness record](vent-print-readiness/README.md) carries both current
rigid projects, the two vent bungs, each style's countertop gasket and the factory
insertion tool, with native slice evidence. The [seal procedure](asse-vent-seals/README.md)
defines factory threading and seating. The consumer receives an assembled faucet.
The [vent evidence](vent-qualification/README.md) records the installation envelope,
conditional flow assessment and remaining physical qualification.

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
| Vent bungs, TPU | [Upstream](asse-vent-seals/asse-vent-upstream-bung.stl) · [downstream](asse-vent-seals/asse-vent-downstream-bung.stl) | Same parts |
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

The [centered-vent native report](faucet-shell/centered-vent-check.json) checks the
shared production solids, tube routes, mounting stack, display and cable.
The [saved-tip qualification](vent-qualification/port-native-check.json) checks
the seal-seat walls, open floor escape and complete outlet placement over the bowl.
