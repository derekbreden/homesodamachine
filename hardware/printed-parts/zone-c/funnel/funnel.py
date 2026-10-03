"""Removable 300 mL silicone funnel, seated in the enclosure's sliding PET-GF frame.

The collar center is the origin; z=0 is the brim underside. The 6 mm brim,
collar and normal ramp wall lead to a substantial silicone plug, a 36 mm wide
rounded rectangle centred on the outlet and long enough in Y to house the
elbow cradle's two hooks in pockets in its underside. Its lower bore has a
lead-in and relief; the upper 3 mm is the nominal sealing land. The frame's
through hole and the drain stub are separate parts.
"""

import math
import sys
from pathlib import Path

import cadquery as cq
from cadquery.occ_impl.shapes import cut as cut_shapes, fuse as fuse_shapes
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakeOffsetShape
from OCP.BRepOffset import BRepOffset_Mode
from OCP.GeomAbs import GeomAbs_Arc

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
# _repo is this EDITION's root; tools/ is shared machinery with one copy at the
# repo root, so it gets its own anchor rather than a tools/ per edition.
_tools = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_tools))
from _cadq_export import export_assembly
from _materials import M_SILICONE_BLACK, one_body
from docgen import substitute_md
import elbow_cradle
# The bound this file states about its own collar, recorded at import for the machine's card.
import _stated_bounds as _bounds

# --- funnel parameters ------------------------------------------------------
collar_w = 165.0  # collar footprint in X, inside the top-wall frame
collar_d = 81.78301584656256  # collar footprint in Y
mouth_corner_r = 14.0
collar_corner_r = mouth_corner_r + 6.0
brim_corner_r = collar_corner_r + 7.0
brim_margin = 7.0  # top-wall frame between the collar and its outer boundary
brim_overhang = 7.0  # flange reach beyond the collar on each side
brim_thickness = 6.0  # vertical flange thickness
collar_wall = 6.0  # vertical collar wall and normal ramp-wall thickness
capacity_ml = 300.0  # nominal capacity to the brim
chute_h = 23.485946291005064  # brim top to inner ramp start
neck_dx = 1.85
neck_dy = 0.0
spout_id = 6.35  # wet-side outlet above the sealing land
spout_wall = 4.5  # minimum radial stock around the throat
neck_blend_drop = 6.25
# Ramp and outlet elevations are independent of the plug's lower face.
_ramp_rise = 14.199233063709995
plug_diameter = 36.0
plug_height = 15.0
drop = 46.1  # brim underside to plug underside
sealing_land = 3.0
sealing_id = 6.0
bore_relief_id = 6.7
bore_lead_id = 8.4
bore_lead_height = 1.8
spout_land_z = brim_thickness - chute_h - _ramp_rise - neck_blend_drop
spout_tube = spout_land_z + drop
_ramp_run = (collar_w - 2.0 * collar_wall) / 2.0 - spout_id / 2.0 + abs(neck_dx)
_y_run = (collar_d - 2.0 * collar_wall) / 2.0 - spout_id / 2.0 + abs(neck_dy)
ramp_angle = math.degrees(math.atan2(_ramp_rise, max(_ramp_run, _y_run)))

_bounds.state(
    "funnel-floor-grade", "The funnel ramp falls toward the offset outlet",
    "a continuous downhill floor to the offset outlet",
    _ramp_rise > 0.0,
    f"{_ramp_rise:.3f} mm rise over {max(_ramp_run, _y_run):.3f} mm run: "
    f"{ramp_angle:.3f} degrees")

# The drain, in the funnel's own frame: the spout exit annulus center. World
# position = this + the funnel's placement; it rides the part.
drain_local = (neck_dx, neck_dy, -drop)


# --- primitives -------------------------------------------------------------

def _box(w, d, z0, z1, cx, cy):
    """Axis-aligned box of footprint w×d centered at (cx, cy), spanning z[z0,z1]."""
    return (
        cq.Workplane("XY").box(w, d, z1 - z0, centered=(True, True, False))
        .translate((cx, cy, z0)).val()
    )


def _rounded_wire(w, d, radius, z, cx=0.0, cy=0.0):
    wire = cq.Workplane("XY", origin=(cx, cy, z)).rect(w, d).val()
    return wire.fillet2D(radius, wire.Vertices())


def _rounded_box(w, d, radius, z0, z1, cx=0.0, cy=0.0):
    return cq.Solid.extrudeLinear(_rounded_wire(w, d, radius, z0, cx, cy), [],
                                 cq.Vector(0.0, 0.0, z1 - z0))


def _loft_rc(w0, d0, cx0, cy0, z0, r1, cx1, cy1, z1, corner_r=0.0):
    """Loft from a rounded rectangle to the offset circular outlet."""
    top = (_rounded_wire(w0, d0, corner_r, z0, cx0, cy0) if corner_r
           else cq.Workplane("XY", origin=(cx0, cy0, z0)).rect(w0, d0).val())
    bottom = cq.Wire.makeCircle(r1, cq.Vector(cx1, cy1, z1), cq.Vector(0, 0, 1))
    return cq.Solid.makeLoft([top, bottom])


def _cyl(r, z_top, z_bot, cx, cy):
    return cq.Solid.makeCylinder(r, z_top - z_bot, cq.Vector(cx, cy, z_bot), cq.Vector(0, 0, 1))


def normal_envelope(shape, distance, faces=None, *, rounds_first=False):
    """Filled envelope with a normal skin and round edge and vertex joins."""
    whole_body = faces is None
    if whole_body:
        offset = BRepOffsetAPI_MakeOffsetShape()
        offset.PerformByJoin(shape.wrapped, distance, 1e-5,
                             BRepOffset_Mode.BRepOffset_Skin,
                             False, False, GeomAbs_Arc, False)
        if offset.IsDone() and not offset.Shape().IsNull():
            envelope = cq.Shape.cast(offset.Shape())
            if not envelope.Solids() and len(envelope.Shells()) == 1:
                envelope = cq.Solid.makeSolid(envelope.Shells()[0])
            envelope = envelope.clean()
            if envelope.isValid() and len(envelope.Solids()) == 1:
                assert abs(cut_shapes(shape, envelope).Volume()) < 0.0001
                inside = cq.Compound.makeCompound(shape.Faces())
                outside = cq.Compound.makeCompound(envelope.Faces())
                measured = inside.distance(outside)
                assert measured >= distance - 0.005, ("normal envelope", measured, distance)
                return envelope.Solids()[0]
    faces = shape.Faces() if faces is None else list(faces)
    edges = {edge.hashCode(): edge for face in faces for edge in face.Edges()}
    vertices = {vertex.hashCode(): vertex for face in faces for vertex in face.Vertices()}
    skins = [face.thicken(distance) for face in faces]
    joins = []
    for edge in edges.values():
        if edge.Length() > 0.0001:
            circle = cq.Wire.makeCircle(distance, edge.positionAt(0), edge.tangentAt(0))
            joins.append(cq.Solid.sweep(circle, [], edge))
    corners = [cq.Solid.makeSphere(distance, vertex.Center(),
               angleDegrees1=-90, angleDegrees2=90) for vertex in vertices.values()]
    pieces = corners+joins+skins if rounds_first else skins+joins+corners
    envelope = shape
    for index, piece in enumerate(pieces):
        # Forming faces and verification contributors keep their own geometry.
        envelope = fuse_shapes(envelope, piece, tol=0.0001).clean()
        assert envelope.isValid(), index
    solids = envelope.Solids()
    if len(solids) != 1:
        body = max(solids, key=lambda solid: solid.Volume())
        for solid in solids:
            missing = cut_shapes(solid, body, tol=0.0001).Volume()
            assert abs(missing) < 0.0001, ("disconnected normal skin", missing,
                                           [s.Volume() for s in solids])
        envelope = body
    for index, piece in enumerate([shape, *pieces]):
        missing = cut_shapes(piece, envelope, tol=0.0001).Volume()
        assert abs(missing) < 0.0001, (index, missing)
    return envelope.Solids()[0]


# --- the funnel -------------------------------------------------------------

def build_solids(drop=drop, ramp_wall=collar_wall, outer_air=0.0):
    """Filled outer envelope, complete wet cavity, and mold-forming dimensions.

    Clearance grows the forming primitives along their own normal faces.
    The ramp keeps a 5 micron allowance for the rounded offset joins.
    """
    w, d = collar_w, collar_d
    cx = cy = 0.0
    ncx, ncy = neck_dx, neck_dy
    bore_w, bore_d = w - 2.0 * collar_wall, d - 2.0 * collar_wall
    top_z = brim_thickness
    ramp_top_z = top_z - chute_h
    neck_z = ramp_top_z - _ramp_rise
    end_z = -drop
    land_z = neck_z - neck_blend_drop
    spout_or = spout_id / 2.0 + spout_wall
    ramp = _loft_rc(bore_w, bore_d, cx, cy, ramp_top_z, spout_id / 2.0,
                    ncx, ncy, neck_z, mouth_corner_r)
    bases = [normal_envelope(ramp, ramp_wall + outer_air + (0.005 if outer_air else 0)) if ramp_wall else
             _loft_rc(w, d, cx, cy, ramp_top_z, spout_or,
                      ncx, ncy, neck_z, collar_corner_r),
             _rounded_box(w, d, collar_corner_r, ramp_top_z, 0.05),
             _rounded_box(w + 2 * brim_overhang, d + 2 * brim_overhang,
                          brim_corner_r, 0.0, top_z),
             _cyl(spout_or, neck_z, end_z, ncx, ncy),
             elbow_cradle.plug_outline(plug_diameter / 2, 0.0, 0.0, plug_height)
             .translate(cq.Vector(ncx, ncy, end_z))]
    if outer_air:
        bases = [bases[0], *(normal_envelope(b, outer_air) for b in bases[1:])]
    solid = fuse_shapes(*bases, tol=0.0001).clean()
    # The plug's broad lower annulus is the silicone's sole bottom plane.
    solid = solid.intersect(_box(600, 600, end_z - outer_air, top_z + 1, 0, 0)).clean()
    assert solid.isValid() and len(solid.Solids()) == 1
    upper_bore = _cyl(spout_id / 2, neck_z, land_z, ncx, ncy)
    land = _cyl(sealing_id / 2, land_z + 0.01, land_z - sealing_land, ncx, ncy)
    relief = _cyl(bore_relief_id / 2, land_z - sealing_land,
                  end_z + bore_lead_height, ncx, ncy)
    lead = cq.Solid.makeCone(bore_lead_id / 2, bore_relief_id / 2,
                            bore_lead_height, cq.Vector(ncx, ncy, end_z))
    through = _cyl(bore_lead_id / 2, end_z + 0.01, end_z - 1, ncx, ncy)
    cavity = fuse_shapes(
        _rounded_box(bore_w, bore_d, mouth_corner_r, ramp_top_z, top_z + 1),
        ramp, upper_bore, land, relief, lead, through, tol=0.0001).clean()
    assert cavity.isValid() and len(cavity.Solids()) == 1
    meta = {
        "w": w, "d": d, "cx": cx, "cy": cy, "ncx": ncx, "ncy": ncy,
        "bore_w": bore_w, "bore_d": bore_d,
        "mouth_corner_r": mouth_corner_r,
        "brim_overhang": brim_overhang, "brim_margin": brim_margin,
        "collar_wall": collar_wall,
        "out_w": w + 2 * brim_overhang, "out_d": d + 2 * brim_overhang,
        "out_cx": cx, "out_cy": cy, "rim_ring": collar_wall + brim_overhang,
        "spout_id": spout_id, "spout_or": plug_diameter / 2,
        "top_z": top_z, "ramp_top_z": ramp_top_z, "neck_z": neck_z,
        "spout_land_z": land_z, "end_z": end_z,
        "neck_blend_drop": neck_blend_drop,
        "plug_radius": plug_diameter / 2,
        "sealing_radius": sealing_id / 2,
        "sealing_land": sealing_land,
        "relief_radius": bore_relief_id / 2,
        "lead_radius": bore_lead_id / 2,
        "lead_height": bore_lead_height,
    }
    return solid, cavity, meta


def build(drop=drop):
    solid, cavity, m = build_solids(drop)
    fill = cavity.intersect(_box(600, 600, m["end_z"], m["top_z"], 0, 0)).Volume()
    assert abs(fill / 1000 - capacity_ml) < 0.25, fill / 1000
    part = cut_shapes(solid, cavity, tol=0.0001).clean()
    # The cradle's hooks lie on the frame's web under the plug, each in its own pocket.
    lift = cq.Vector(m["ncx"], m["ncy"], m["end_z"] - elbow_cradle.WEB)
    for pocket in elbow_cradle.pockets():
        part = part.cut(pocket.translate(lift))
    part = part.clean()
    assert part.isValid() and len(part.Solids()) == 1
    assert abs(part.BoundingBox().zmin + drop) < 0.0001
    assert abs(part.BoundingBox().zmax - brim_thickness) < 0.0001
    return cq.Workplane(obj=part), (m["w"], m["d"], m["top_z"] - m["end_z"], m["end_z"], fill)


def main():
    funnel, (w, d, total, end_z, fill) = build()
    out = _here.parent / "funnel.step"
    # The funnel is cast in platinum-cure silicone, and the STEP says so — the card's own picture
    # of it is drawn off this file, the machine's picture off the same colour.
    export_assembly(one_body(funnel, "funnel", M_SILICONE_BLACK), str(out))
    print(f"-> {out.name}")
    b = funnel.val().BoundingBox()
    print(f"  brim:    {b.xlen:.1f} × {b.ylen:.1f} mm, top z={b.zmax:.1f} (local; z 0 = brim underside)")
    print(f"  mouth:   {w:.1f} × {d:.1f} mm (collar), bore {w - 2*collar_wall:.1f} × {d - 2*collar_wall:.1f}")
    print(f"  spout:   Ø{spout_id:g} bore, drain at ({drain_local[0]:g}, {drain_local[1]:g}, {drain_local[2]:g}) local, total drop {total:.1f} mm")
    print(f"  capacity to brim: {fill:.0f} mm³ = {fill / 1000.0:.0f} mL "
          f"(nominal {capacity_ml:g} mL)")

    substitute_md(
        _here.parent / "README.md",
        variables={
            "FUNNEL_SPOUT_ID": f"{spout_id:g} mm",
            "FUNNEL_PLUG": f"{plug_diameter:g} × "
                           f"{2 * elbow_cradle.plug_half_length(plug_diameter / 2):.1f} mm",

            "FUNNEL_SPOUT_WALL": f"{spout_wall:g} mm",
            "FUNNEL_CHUTE": f"{chute_h:g} mm",
            "FUNNEL_DROP_UNDER": f"{drop:g} mm",
            "FUNNEL_LAND": f"{spout_tube:g} mm",
            "FUNNEL_DROP": f"{total:.0f} mm",
            "FUNNEL_CAP": f"{fill / 1000.0:.0f} mL",
            "FUNNEL_HOLD": f"{brim_overhang:g} mm",
            "FUNNEL_MARGIN": f"{brim_margin:g} mm",
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
