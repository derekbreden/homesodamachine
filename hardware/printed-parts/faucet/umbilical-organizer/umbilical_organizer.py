"""PET-GF umbilical organizer, in its upright print frame.

The three quarter-inch bores use the tested A sample's fit. The 4 mm drain
bore uses the tested B sample's fit from the three-increment Mark2 plate.

The print origin is the centre of the round stock; Z=0 is the bottom face.
Tube-axis XY values below use the faucet assembly's coordinates. Placement
adds CENTRE_XY and sets the bottom face below the chosen installed top face.
"""

from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HARDWARE = HERE.parents[2]
sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import export_assembly
from _materials import C_FAUCET_BLACK

OD = 32.0
LENGTH = 10.0
TUBE_BORE = 6.65
DRAIN_BORE = 4.40
CABLE_BORE = 5.0
ENTRY = 0.40
CABLE_ENTRY = 0.20
OUTSIDE_EASE = 0.60
CENTRE_XY = (-0.9124999999999996, 10.510023117569354)
CABLE_XY = (5.45, 11.50)
BORES = (
    ("S", (0.0, 0.0), TUBE_BORE),
    ("F1", (5.45, 18.925), TUBE_BORE),
    ("F2", (-7.2749999999999995, 18.925), TUBE_BORE),
    ("D", (0.0, 8.9), DRAIN_BORE),
    ("SIG", CABLE_XY, CABLE_BORE),
)


def build_organizer():
    """One puck, four smooth tube bores, loose cable."""
    body = cq.Workplane("XY").circle(OD / 2).extrude(LENGTH)
    body = body.edges("%Circle").chamfer(OUTSIDE_EASE)
    for name, xy, diameter in BORES:
        x, y = xy[0] - CENTRE_XY[0], xy[1] - CENTRE_XY[1]
        r = diameter / 2
        entry = CABLE_ENTRY if name == "SIG" else ENTRY
        bore = cq.Solid.makeCylinder(r, LENGTH + 2, cq.Vector(x, y, -1))
        bottom = cq.Solid.makeCone(r + entry, r, entry, cq.Vector(x, y, 0))
        top = cq.Solid.makeCone(r, r + entry, entry, cq.Vector(x, y, LENGTH-entry))
        body = body.cut(bore.fuse(bottom, top))
    return body.val().clean()


def placed(top_z):
    return build_organizer().translate((*CENTRE_XY, top_z - LENGTH))


def main():
    shape = build_organizer()
    assembly = cq.Assembly(shape, name="umbilical-organizer", color=C_FAUCET_BLACK)
    # The accepted trial used these tessellation settings.
    stl = HERE / "umbilical-organizer.stl"
    cq.exporters.export(shape, str(stl), tolerance=0.05, angularTolerance=0.12)
    step = HERE / "umbilical-organizer.step"
    export_assembly(assembly, str(step))
    import flute_payload
    flute_payload.cut(step, stl, preserve_print_triangles=True)
    sys.path.insert(0, str(HARDWARE.parent / "tools"))
    from docgen import substitute_md
    substitute_md(HERE / "README.md", variables={
        "ORGANIZER_OD": f"{OD:g} mm",
        "ORGANIZER_LENGTH": f"{LENGTH:g} mm",
        "ORGANIZER_TUBE_BORE": f"{TUBE_BORE:.2f} mm",
        "ORGANIZER_DRAIN_BORE": f"{DRAIN_BORE:.2f} mm",
        "ORGANIZER_CABLE_BORE": f"{CABLE_BORE:g} mm",
        "ORGANIZER_ENTRY": f"{ENTRY:g} mm",
        "ORGANIZER_CONTACT": f"{LENGTH - 2 * ENTRY:g} mm",
        "ORGANIZER_CABLE_ENTRY": f"{CABLE_ENTRY:g} mm",
        "ORGANIZER_RIM_EASE": f"{OUTSIDE_EASE:g} mm",
    })
    print(f"-> {step.name}, {stl.name}, {step.name}.mesh, README.md")


if __name__ == "__main__":
    main()
