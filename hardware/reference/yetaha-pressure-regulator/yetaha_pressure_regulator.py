"""Estimated exterior of Yetaha B07GDGYHZV, SZ070030063979RK-1.

Dimensions come from estimated-dimensions.json: product photographs and scanned
RO-valve / quick-connect comparisons. No received specimen has been measured.
Millimetres; flow +X, cap +Z, origin midway between the opposed tube mouths.
Visible recesses have display closures; pressure internals are not represented.
"""
from functools import lru_cache
import json
import math
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == "hardware")
sys.path.insert(0, str(HW / "scripts"))
from _cadq_export import export_assembly
from _materials import C_VALVE, C_DIGITEN_CLIP, M_ZINC_PLATED_STEEL

DIMENSIONS = json.loads((HERE / "estimated-dimensions.json").read_text())
N = DIMENSIONS["nominal"]
Z = N["z"]
D = DIMENSIONS["display_features"]
STEP = HERE / "yetaha-pressure-regulator.step"


def inlet():
    """Estimated upstream tube face: (position, outward axis)."""
    return (-N["port_face_span"] / 2, 0.0, 0.0), (-1.0, 0.0, 0.0)


def outlet():
    """Estimated downstream tube face, following the photographed arrow."""
    return (N["port_face_span"] / 2, 0.0, 0.0), (1.0, 0.0, 0.0)


def stations():
    return {"inlet": inlet(), "outlet": outlet()}


def _cylinder(radius, z0, z1, xy=(0.0, 0.0)):
    return (cq.Workplane("XY").workplane(offset=z0)
            .center(*xy).circle(radius).extrude(z1 - z0))


def _axial_cylinder(radius, x0, x1):
    return cq.Workplane(obj=cq.Solid.makeCylinder(
        radius, x1 - x0, cq.Vector(x0, 0, 0), cq.Vector(1, 0, 0)))


def _rounded_plate(width, depth, z0, z1, radius):
    return (cq.Workplane("XY").workplane(offset=z0)
            .box(width, depth, z1 - z0, centered=(True, True, False))
            .edges("|Z").fillet(radius))


def _hexagon(across_flats, z0, z1, xy=(0.0, 0.0)):
    radius = across_flats / math.sqrt(3)
    points = [(radius * math.cos(math.radians(a)),
               radius * math.sin(math.radians(a)))
              for a in (30, 90, 150, 210, 270, 330)]
    return (cq.Workplane("XY").workplane(offset=z0).center(*xy)
            .polyline(points).close().extrude(z1 - z0))


def _forks():
    """Transverse mounting strip; the obscured opposite fork uses symmetry."""
    strip = (cq.Workplane("XY").workplane(offset=Z["mount_plane"])
             .box(N["foot_width"], N["foot_tip_span"], N["foot_thickness"],
                  centered=(True, True, False)))
    r = N["foot_slot_width"] / 2
    tip = N["foot_tip_span"] / 2
    root = N["foot_slot_closed_end_station"]
    for side in (-1, 1):
        # Root station denotes the closed end, not the semicircle centre.
        centre = side * (root + r)
        circle = _cylinder(r, Z["mount_plane"] - 0.1,
                           Z["foot_top"] + 0.1, (0, centre))
        y0, y1 = sorted((centre, side * (tip + 1)))
        opening = (cq.Workplane("XY").box(2 * r, y1 - y0,
                    N["foot_thickness"] + 0.2)
                   .translate((0, (y0 + y1) / 2,
                               (Z["mount_plane"] + Z["foot_top"]) / 2)))
        strip = strip.cut(circle.union(opening))
    return strip


def _body():
    body = _rounded_plate(N["base_width"], N["base_depth"],
                          Z["mount_plane"], Z["base_top"], 3.0)
    body = body.union(_forks()).union(
        _cylinder(N["bell_diameter"] / 2, Z["base_top"], Z["bell_top"]))
    body = body.union(_rounded_plate(
        N["bonnet_width"], N["bonnet_depth"], Z["bonnet_bottom"],
        Z["bonnet_top"], N["bonnet_corner_radius"]))
    for x in (-N["bolt_pitch_x"] / 2, N["bolt_pitch_x"] / 2):
        for y in (-N["bolt_pitch_y"] / 2, N["bolt_pitch_y"] / 2):
            body = body.union(_cylinder(N["boss_diameter"] / 2,
                Z["bonnet_top"], Z["plastic_boss_top"], (x, y)))
    body = body.union(_hexagon(N["cap_hex_across_flats"],
                              Z["bonnet_top"], Z["cap_top"]))
    # The visible adjuster seam is represented; its hidden mechanism is omitted.
    body = body.cut(_cylinder((N["adjuster_disc_diameter"] + 0.2) / 2,
                             Z["cap_top"] - D["adjuster_disc_depth"] - 0.5,
                             Z["cap_top"] + 0.1))
    face = N["port_face_span"] / 2
    fixed_face = face - 2.5
    socket = _axial_cylinder(N["socket_diameter"] / 2, 12.0, fixed_face)
    mouth = _axial_cylinder(D["tube_entry_bore_diameter"] / 2,
                           face - D["visible_mouth_depth"], face + 0.1)
    for side in (-1, 1):
        nose, bore = socket, mouth
        if side < 0:
            nose = nose.rotate((0, 0, 0), (0, 0, 1), 180)
            bore = bore.rotate((0, 0, 0), (0, 0, 1), 180)
        body = body.union(nose).cut(bore)
    return body


def _collet():
    face = N["port_face_span"] / 2
    part = _axial_cylinder(N["collet_diameter"] / 2, face - 2.5, face)
    part = part.cut(_axial_cylinder(D["tube_entry_bore_diameter"] / 2,
                                    face - 2.6, face + 0.1))
    chamfer = cq.Solid.makeCone(
        D["tube_entry_bore_diameter"] / 2,
        D["tube_entry_leadin_diameter"] / 2,
        D["tube_entry_leadin_depth"],
        cq.Vector(face - D["tube_entry_leadin_depth"], 0, 0),
        cq.Vector(1, 0, 0))
    return part.cut(chamfer)


def _clip():
    x0 = N["port_face_span"] / 2 - 2.5
    clip = (cq.Workplane("YZ", origin=(x0, 0, 0))
            .circle(D["clip_outer_diameter"] / 2)
            .circle(D["clip_inner_diameter"] / 2)
            .extrude(D["clip_thickness"]))
    angle = math.radians(D["clip_opening_degrees"] / 2)
    points = [(0, 0), (30 * math.cos(angle), -30 * math.sin(angle)),
              (30 * math.cos(angle), 30 * math.sin(angle))]
    opening = (cq.Workplane("YZ", origin=(x0 - 0.1, 0, 0))
               .polyline(points).close().extrude(D["clip_thickness"] + 0.2))
    return clip.cut(opening)


def _adjuster():
    top = Z["cap_top"]
    disc = _cylinder(N["adjuster_disc_diameter"] / 2,
                     top - D["adjuster_disc_depth"], top)
    for width, depth in ((D["adjuster_cross_span"], D["adjuster_cross_width"]),
                         (D["adjuster_cross_width"], D["adjuster_cross_span"])):
        slot = (cq.Workplane("XY").box(width, depth, D["adjuster_cross_depth"] + 0.1)
                .translate((0, 0, top - D["adjuster_cross_depth"] / 2 + 0.05)))
        disc = disc.cut(slot)
    return disc


@lru_cache(maxsize=1)
def _parts():
    parts = {"body": (_body(), C_VALVE), "adjuster": (_adjuster(), C_VALVE)}
    for side, name in ((-1, "inlet"), (1, "outlet")):
        collet, clip = _collet(), _clip()
        if side < 0:
            collet = collet.rotate((0, 0, 0), (0, 0, 1), 180)
            clip = clip.rotate((0, 0, 0), (0, 0, 1), 180)
        parts[f"{name}-collet"] = (collet, C_VALVE)
        parts[f"{name}-clip"] = (clip, C_DIGITEN_CLIP)
    for ix, x in enumerate((-N["bolt_pitch_x"] / 2, N["bolt_pitch_x"] / 2)):
        for iy, y in enumerate((-N["bolt_pitch_y"] / 2, N["bolt_pitch_y"] / 2)):
            z0 = Z["plastic_boss_top"]
            nut = _hexagon(D["nut_across_flats"], z0, z0 + D["nut_height"], (x, y))
            stud = _cylinder(D["stud_diameter"] / 2, z0 + D["nut_height"],
                             Z["boss_top"], (x, y))
            parts[f"fastener-{ix}-{iy}"] = (nut.union(stud), M_ZINC_PLATED_STEEL)
    return parts


def build():
    """Complete estimated exterior as a CadQuery workplane compound."""
    return cq.Workplane(obj=cq.Compound.makeCompound(
        [s for part, _color in _parts().values() for s in part.val().Solids()]))


def build_assembly():
    """Named material components for the STEP and viewer."""
    assembly = cq.Assembly(name="yetaha-pressure-regulator")
    for name, (part, color) in _parts().items():
        assembly.add(part, name=name, color=color)
    return assembly


def main():
    export_assembly(build_assembly(), str(STEP))
    print(f"Estimated Yetaha exterior -> {STEP.name}")
    print(f"  Nominal {N['port_face_span']:g} x {N['foot_tip_span']:g} x "
          f"{N['overall_height']:g} mm; ports {inlet()[0]}, {outlet()[0]}")


if __name__ == "__main__":
    main()
