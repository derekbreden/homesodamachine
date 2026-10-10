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
sys.path.insert(0, str(HARDWARE / "printed-parts/faucet"))
import _faucet_interface as interface
import faucet_paths

OD = 32.0
LENGTH = 10.0
TUBE_BORE = 6.65
DRAIN_BORE = 4.40
CABLE_SLOT_LENGTH = 5.4
CABLE_SLOT_DEPTH = 1.8
ENTRY = 0.40
CABLE_ENTRY = 0.20
OUTSIDE_EASE = 0.60
# The mounting row is F1-D-F2 with SIG behind D. Small offsets leave
# separate bore walls and entrance chamfers while guiding the mounting row.
FLAVOR_SPREAD = 1.20
DRAIN_FORWARD = 1.20
CABLE_XY = (interface.bundle_mount_x, faucet_paths.LOWER_RIBBON_Y)
# Circumcentre of the three beverage bores, in the faucet frame.
_flavor_x = interface.flavor_tube_x_offset + FLAVOR_SPREAD
_flavor_y = interface.flavor_tube_depth
CENTRE_XY = (interface.bundle_mount_x,
             (_flavor_x**2 + _flavor_y**2 - interface.bundle_mount_x**2) / (2 * _flavor_y))
BORES = (
    ("S", (0.0, 0.0), TUBE_BORE),
    ("F1", (interface.bundle_mount_x + interface.flavor_tube_x_offset + FLAVOR_SPREAD,
            interface.flavor_tube_depth), TUBE_BORE),
    ("F2", (interface.bundle_mount_x - interface.flavor_tube_x_offset - FLAVOR_SPREAD,
            interface.flavor_tube_depth), TUBE_BORE),
    ("D", (interface.drain_tube_x, interface.drain_tube_y - DRAIN_FORWARD), DRAIN_BORE),
    ("SIG", CABLE_XY, CABLE_SLOT_LENGTH),
)


def axis(name):
    """One passage's XY axis in the mounted faucet frame."""
    return next(xy for label, xy, _diameter in BORES if label == name)


def build_organizer():
    """One puck, four smooth tube bores and a flat, loose ribbon slot."""
    body = cq.Workplane("XY").circle(OD / 2).extrude(LENGTH)
    body = body.edges("%Circle").chamfer(OUTSIDE_EASE)
    for name, xy, diameter in BORES:
        x, y = xy[0] - CENTRE_XY[0], xy[1] - CENTRE_XY[1]
        r = diameter / 2
        entry = CABLE_ENTRY if name == "SIG" else ENTRY
        if name == "SIG":
            def wire(z, grow=0.0):
                return (cq.Workplane("XY", origin=(x, y, z))
                        .slot2D(CABLE_SLOT_LENGTH + 2*grow, CABLE_SLOT_DEPTH + 2*grow)
                        .val())
            bore = cq.Solid.extrudeLinear(wire(-1), [], cq.Vector(0, 0, LENGTH + 2))
            bottom = cq.Solid.makeLoft([wire(0, entry), wire(entry)], ruled=True)
            top = cq.Solid.makeLoft([wire(LENGTH-entry), wire(LENGTH, entry)], ruled=True)
            body = body.cut(bore.fuse(bottom, top))
            continue
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
        "ORGANIZER_CABLE_SLOT": f"{CABLE_SLOT_LENGTH:g} × {CABLE_SLOT_DEPTH:g} mm",
        "ORGANIZER_ENTRY": f"{ENTRY:g} mm",
        "ORGANIZER_CONTACT": f"{LENGTH - 2 * ENTRY:g} mm",
        "ORGANIZER_CABLE_ENTRY": f"{CABLE_ENTRY:g} mm",
        "ORGANIZER_RIM_EASE": f"{OUTSIDE_EASE:g} mm",
    })
    print(f"-> {step.name}, {stl.name}, {step.name}.mesh, README.md")


if __name__ == "__main__":
    main()
