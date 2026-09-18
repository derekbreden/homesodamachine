# Faucet styles

The faucet has two styles, each in Black or White PET-GF.

| Faucet style | Shape | PET-GF test print |
|---|---|---|
| **Sculpted** | Smooth curves and softly blended transitions. | [Sculpted project](faucet-petgf.3mf) · [print settings](faucet-petgf.md) |
| **Industrial** | Simple cylinders and crisp, pronounced shoulders. | [Industrial project](industrial/faucet-industrial-petgf.3mf) · [print settings](industrial/faucet-industrial-petgf.md) |

**Finish** is a separate Black or White choice in the [3D viewer](/3d).
It applies to the PET-GF shell, display cover and above-counter plate.
The retained Westbrass lever, display glass, tubing and TPU gasket keep their
own materials and colors. Each style uses one geometry in either finish.

## Parts

Both styles enclose the same harvested Westbrass, retained lever, Waveshare
faucet display, three LLDPE tubes and signal ribbon. They share the
[shell tip](faucet-shell/faucet-shell-tip.step), the curved gooseneck joint,
the three hidden mounting screws and the existing stainless under-counter
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

Use the matching base, cover, plate and gasket for the selected style.
The PET-GF projects each contain the base, shared tip, cover and plate.
The gasket is a separate TPU print.

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
