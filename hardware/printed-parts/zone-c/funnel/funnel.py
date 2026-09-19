"""Zone C funnel — the removable dishwasher-safe silicone insert.

The collar center is the origin; z = 0 is the brim underside that
rests on the inset enclosure seat. The machine places the part through
`enclosure_assembly.build_funnel` and cuts its opening from the collar.

The brim and vertical collar wall are 6 mm thick. The sloping floor has a
6 mm skin measured normal to its inner faces, with rounded joins and a
thicker throat. The inner floor ends at the 1/4-inch outlet bore. A 6.25 mm
transition separates that point from the 12 mm straight clamp land, whose
radial wall is 4.5 mm. Capacity to the brim is printed at export.
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
sys.path.insert(0, str(_repo / "hardware" / "reference" / "worm-clamp"))
sys.path.insert(0, str(_tools))
from _cadq_export import export_assembly
from _materials import M_SILICONE_BLACK, one_body
from docgen import substitute_md
# The bound this file states about its own collar, recorded at import for the machine's card.
import _stated_bounds as _bounds
# The band that closes the spout on the drain stub, and so the length of round the spout owes it.
import worm_clamp as _clamp

# --- funnel parameters ------------------------------------------------------
collar_w = 165.0  # collar footprint in X, inside the top-wall frame
collar_d = 151.0  # collar footprint in Y
mouth_corner_r = 14.0
collar_corner_r = mouth_corner_r + 6.0
brim_corner_r = collar_corner_r + 7.0
brim_margin = 7.0  # top-wall frame between the collar and its outer boundary
brim_overhang = 7.0  # flange reach beyond the collar on each side
brim_thickness = 6.0  # vertical flange thickness
collar_wall = 6.0  # vertical collar wall and normal ramp-wall thickness
bottle_ml = 440.0  # one SodaStream concentrate bottle
capacity_bottles = 600.0 / bottle_ml  # minimum capacity to the brim, checked in build()
chute_h = 23.485946291005064  # brim top to inner ramp start
neck_dx = 1.85  # outlet offset in X from the collar center
neck_dy = 0.0  # outlet centered fore–aft
spout_id = 6.35  # 1/4-inch outlet bore
spout_wall = 4.5  # radial wall on the straight clamp land
neck_blend_drop = 6.25  # inner ramp tip to the top of the straight clamp land
clamp_shoulder = 2.0  # silicone beyond each edge of the clamp band
spout_tube = _clamp.BAND_W + 2.0 * clamp_shoulder  # straight clamp land, below the rounded throat

# The inner ramp uses one vertical rise between its rectangular mouth and round
# outlet. The drain drop includes the chute, ramp, throat transition and clamp land.
_ramp_run = (collar_w - 2.0 * collar_wall) / 2.0 - spout_id / 2.0 + abs(neck_dx)
_y_run = (collar_d - 2.0 * collar_wall) / 2.0 - spout_id / 2.0 + abs(neck_dy)
drop = 49.93517935471506  # brim underside to the drain mating face
_ramp_rise = drop - (chute_h - brim_thickness) - neck_blend_drop - spout_tube
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
                assert measured >= distance - 0.001, ("normal envelope", measured, distance)
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
    """The funnel's outer envelope and inner bore as separate solids, plus a
    metrics dict. This is the source the silicone-mold generator consumes: the
    mold cavity is the negative of `solid` and the mold core is `cavity`. Keeping
    it here, beside the funnel, keeps the mold in lockstep with the part.
    ``outer_air`` grows each construction solid before their union. Tooling and
    the enclosure use this normal envelope for their forming and clearance faces.
    See ../funnel-mold/."""
    w, d = collar_w, collar_d
    cx = cy = 0.0
    bore_w, bore_d = w - 2.0 * collar_wall, d - 2.0 * collar_wall
    top_z = brim_thickness                              # brim top = outermost point
    spout_or = spout_id / 2.0 + spout_wall
    ncx = cx + neck_dx                                  # spout/neck, shifted in X
    ncy = cy + neck_dy                                  # fore–aft outlet station
    ramp_top_z = top_z - chute_h                        # straight chute bottom = ramp start
    end_z = -drop                                       # spout exit (the drain)
    spout_land_z = end_z + spout_tube
    neck_z = ramp_top_z - _ramp_rise                    # inner ramp tip

    # The flange, collar and outlet form the base of the outer envelope.
    bases = [
        _rounded_box(w + 2.0 * brim_overhang, d + 2.0 * brim_overhang,
                     brim_corner_r, 0.0, top_z, cx, cy),
        _rounded_box(w, d, collar_corner_r, ramp_top_z, 0.0, cx, cy),
        _cyl(spout_or, neck_z, end_z, ncx, ncy),
    ]
    if not ramp_wall:
        bases.append(_loft_rc(w, d, cx, cy, ramp_top_z, spout_or,
                              ncx, ncy, neck_z, collar_corner_r))
    if outer_air:
        bases = [normal_envelope(base, outer_air) for base in bases]
    # The inner forming surface runs from the mouth through the ramp and outlet.
    ramp = _loft_rc(bore_w, bore_d, cx, cy, ramp_top_z, spout_id / 2.0,
                    ncx, ncy, neck_z, mouth_corner_r)
    cavity = (
        _rounded_box(bore_w, bore_d, mouth_corner_r, ramp_top_z, top_z + 1.0, cx, cy)
        .fuse(ramp)
        .fuse(_cyl(spout_id / 2.0, neck_z, end_z - 1.0, ncx, ncy))
    )
    ramp_faces = [face for face in cavity.Faces() if face.geomType() == "BSPLINE"]
    assert ramp_faces, "inner ramp faces must carry the normal wall"
    # Each inner ramp face carries a 6 mm normal skin with round edge joins.
    if ramp_wall:
        bases.insert(0, normal_envelope(ramp, ramp_wall + outer_air))
    # The normal ramp envelope supplies the complete floor. Fuse it directly with
    # the collar, brim and spout, without an overlapping thin loft inside the skin.
    solid = fuse_shapes(*[base.toNURBS() for base in bases])
    assert solid.isValid() and len(solid.Solids()) == 1
    bounds = solid.BoundingBox()
    assert bounds.zmax >= top_z - 0.0001, "the complete brim must survive the union"
    assert bounds.xlen >= w + 2.0 * brim_overhang - 0.0001
    if ramp_wall:
        ramp_boundary = cq.Compound.makeCompound(ramp_faces)
        outer_boundary = cq.Compound.makeCompound(solid.Faces())
        minimum_wall = ramp_boundary.distance(outer_boundary)
        assert minimum_wall >= ramp_wall-0.001, minimum_wall
    land_window = _box(w, d, end_z, spout_land_z, cx, cy)
    land = _cyl(spout_or, spout_land_z, end_z, ncx, ncy)
    if not outer_air:
        assert solid.intersect(land_window).cut(land).Volume() < 0.0001, "ramp enters clamp land"
    meta = {
        "w": w, "d": d, "cx": cx, "cy": cy, "ncx": ncx, "ncy": ncy,
        "bore_w": bore_w, "bore_d": bore_d,
        "brim_overhang": brim_overhang, "brim_margin": brim_margin,
        "collar_wall": collar_wall,
        # The part's outer footprint (the brim) and the flange + collar ring
        # between the bore mouth and that outer edge — the mold's pour/vent land.
        "out_w": w + 2.0 * brim_overhang, "out_d": d + 2.0 * brim_overhang,
        "out_cx": cx, "out_cy": cy,
        "rim_ring": collar_wall + brim_overhang,
        "spout_id": spout_id, "spout_or": spout_or,
        "top_z": top_z, "ramp_top_z": ramp_top_z,
        "neck_z": neck_z, "spout_land_z": spout_land_z, "end_z": end_z,
        "neck_blend_drop": neck_blend_drop,
    }
    return solid, cavity, meta


def build(drop=drop):
    solid, cavity, m = build_solids(drop)
    # Capacity filled to the brim rim: the cavity between the spout exit and brim top.
    fill = cavity.intersect(
        _box(600.0, 600.0, m["end_z"], m["top_z"], m["cx"], m["cy"])
    ).Volume()
    # Additional chute height adds the bore area times that height to capacity.
    want = capacity_bottles * bottle_ml * 1000.0
    if fill < want - 1.0:
        bore_area = m["bore_w"] * m["bore_d"]
        raise ValueError(
            f"the funnel holds {fill / 1000.0:.1f} mL, short of the "
            f"{capacity_bottles:g} × {bottle_ml:g} mL = {want / 1000.0:.1f} mL target — "
            f"set chute_h to {chute_h + (want - fill) / bore_area:.2f} mm")
    part = solid.cut(cavity.toNURBS())
    assert part.isValid() and len(part.Solids()) == 1
    assert abs(part.BoundingBox().zmax - brim_thickness) < 0.0001
    return cq.Workplane(obj=part), (
        m["w"], m["d"], m["top_z"] - m["end_z"], m["end_z"], fill,
    )


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
          f"({fill / 440000.0:.2f}× a 440 mL SodaStream bottle)")

    substitute_md(
        _here.parent / "README.md",
        variables={
            "FUNNEL_SPOUT_ID": f"{spout_id:g} mm",
            "FUNNEL_SPOUT_OD": f"{spout_id + 2*spout_wall:g} mm",
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
