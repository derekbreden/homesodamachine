"""Flat-wing liners for the connected enclosure's two bottom lifting ceilings.

The cover's local X is its long direction, Y its short direction, and Z points
out of the finger face. Back and wings share Z=0, the print bed. The receiver
slots pass through square end walls. A constant XZ roof profile runs the entire
opening length, with no rounded returns around its ends. This is a fit candidate.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
ENCLOSURE = HERE.parent / "enclosure"
sys.path[:0] = [str(ENCLOSURE), str(ROOT / "hardware/scripts")]
import enclosure as shell
from _cadq_export import export_assembly
from _materials import M_PETGF_BLACK, one_body
from flute_payload import cut
from overhang_round import OUTWARD_PER_HEIGHT, transition

# The supported flat reaches the additive exterior transition's foot. Its free
# outer edge needs no mating clearance; the inner wall and ends keep the slip fit.
BODY_AIR = shell.fits.slip
LENGTH = shell.handhold_length - 2 * BODY_AIR
X_EXT = shell.appliance_width / 2
_seat, _tip, _heat, _cap = shell._boss_x(X_EXT, -1)
INNER_FACE = _cap + shell.handhold_wall
OUTER_FLAT = X_EXT - transition(shell.handhold_edge_r)[1]
WIDTH = OUTER_FLAT - INNER_FACE - BODY_AIR
X_CENTER = (OUTER_FLAT + INNER_FACE + BODY_AIR) / 2
ROOF = -shell.floor_t + shell.handhold_height + shell.fits.supported_surface
CROWN = ROOF + shell.handhold_roof

# The accepted nameplate's flat-wing section. Flexibility of this narrower,
# shorter strip and retention in this orientation require their own fit trial.
THICK = 3.36
WING_THICK = 1.68
WING_REACH = 2.40
WING_SPAN = 5.0
WING_END_R = .60
CORNER_R = .60
TOUCH_R = .60
WING_END_AIR = shell.fits.slip
BEARING_AIR = .45
BACK_AIR = shell.fits.supported_surface
ENTRY_WIDTH = 1.10
ENTRY_DEPTH = .40
BACK = ROOF - BACK_AIR


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def rounded(width, height, z0, z1, radius):
    return (cq.Workplane("XY").workplane(offset=z0).rect(width, height)
            .extrude(z1-z0).edges("|Z").fillet(radius).val())


def wing(end):
    return rounded(WING_REACH+1, WING_SPAN, 0, WING_THICK, WING_END_R).translate(
        (end*(LENGTH/2+(WING_REACH-1)/2), 0, 0))


def cover():
    """One interchangeable strip; the finger face prints upward without supports."""
    body = rounded(LENGTH, WIDTH, 0, THICK, CORNER_R)
    edges = [e for e in body.Edges() if abs(e.BoundingBox().zmin-THICK) < 1e-6]
    body = body.fillet(TOUCH_R, edges)
    return body.fuse(wing(-1), wing(1)).clean()


def placed(shape, side=1, drop=0):
    """Local X→world Y and Z→world -Z; mirror the east placement for the west."""
    east = (shape.rotate((0,0,0), (1,1,0), 180)
            .translate((X_CENTER, shell.handhold_y, BACK-drop)))
    return east if side == 1 else east.mirror("YZ")


def roof_profile_air():
    """One straight extrusion of the accepted chamfer/R6 section along all Y.

    The roof begins at OUTER_FLAT and expands 0.5 mm per millimetre of rise,
    then follows the tangent circular crown to the exterior wall. Its end faces
    are on the catch-mouth planes; the profile never turns around either end.
    """
    radius = shell.handhold_edge_r
    height, foot = transition(radius)
    y0, y1 = shell._handhold_y()
    cx, cz = X_EXT-radius, ROOF+radius
    angle = -math.atan(OUTWARD_PER_HEIGHT)
    def v(x,z): return cq.Vector(x,y0,z)
    start = v(X_EXT-foot,ROOF)
    tangent = v(X_EXT-foot+OUTWARD_PER_HEIGHT*height,ROOF+height)
    middle = v(cx+radius*math.cos(angle/2),cz+radius*math.sin(angle/2))
    end = v(X_EXT,cz)
    far_top, far_bottom = v(X_EXT+1,cz),v(X_EXT+1,ROOF)
    wire = cq.Wire.assembleEdges([
        cq.Edge.makeLine(start,tangent),
        cq.Edge.makeThreePointArc(tangent,middle,end),
        cq.Edge.makeLine(end,far_top),cq.Edge.makeLine(far_top,far_bottom),
        cq.Edge.makeLine(far_bottom,start)])
    return cq.Solid.extrudeLinear(wire,[],cq.Vector(0,y1-y0,0))


def receiver_slots():
    """Straight through-slots in the existing 3 mm end walls.

    Their mouths are at Y174/254, with no receiver stock projecting into the
    handhold. The open rear exits avoid thin pocket backs and give support access.
    """
    slots = []
    for end in (-1, 1):
        mouth = shell.handhold_length/2
        x0,x1 = sorted((end*(LENGTH/2-.10), end*(mouth+shell.handhold_wall+.10)))
        y0,y1 = -WING_SPAN/2-WING_END_AIR, WING_SPAN/2+WING_END_AIR
        roof = WING_THICK+BEARING_AIR
        slot = box(x0,x1,y0,y1,-BACK_AIR,roof)
        lead = (cq.Workplane("XZ", origin=(0,y1,0))
                .polyline([(end*mouth,roof), (end*(mouth+ENTRY_WIDTH),roof),
                           (end*mouth,roof+ENTRY_DEPTH)])
                .close().extrude(y1-y0).val())
        slots.append(slot.fuse(lead))
    return slots


def build_receiver(solid, inner, y_joint, y_side):
    """Build an insert receiver directly into the uncut bottom enclosure.

    Square 3 mm end walls carry the catches, and the constant roof section
    spans their 80 mm opening. The inner wall, roof frame and enclosure joint
    share the enclosure's structural dimensions.
    """
    if y_side not in ("front", "back"):
        raise ValueError(y_side)
    end_index = 0 if y_side == "front" else 1
    slot = receiver_slots()[end_index]
    y0,y1 = shell._handhold_y()
    bed,roof,_crown = shell._handhold_levels(inner)
    air = roof_profile_air()
    for side in (-1,1):
        x_ext, inward = side*X_EXT,-side
        solid = solid.fuse(shell._handhold_frame(inner,y_joint,x_ext,inward,y_side))
        xa,xb = sorted((side*INNER_FACE,side*(X_EXT+1)))
        solid = solid.cut(box(xa,xb,y0,y1,bed-1,roof))
        solid = solid.cut(air if side==1 else air.mirror("YZ"))
        if y_side == "front":
            solid = solid.cut(shell._handhold_backing_joint(inner,y_joint,x_ext,inward,y_side))
        solid = solid.cut(placed(slot,side)).clean()
    return solid


def originals():
    return {name: cq.importers.importStep(str(ENCLOSURE / f"enclosure-{name}-bottom.step")).val()
            for name in ("front","back")}


def sample(shape):
    """Full-size east handhold crop, retaining the actual telescoping seam."""
    return shape.intersect(box(INNER_FACE-shell.handhold_wall, X_EXT+1,
                               shell.handhold_y-shell.handhold_length/2-5,
                               shell.handhold_y+shell.handhold_length/2+5,
                               -shell.floor_t, CROWN+3)).clean()


def mesh(shape):
    v,f = shape.tessellate(.025,.10)
    result=trimesh.Trimesh(np.array([p.toTuple() for p in v]),np.array(f),process=True)
    # Spherical corner poles can emit zero-area triangles after STL's float32
    # conversion. Remove those redundant faces before exporting the closed skin.
    result.update_faces(result.nondegenerate_faces())
    result.update_faces(result.unique_faces())
    result.remove_unreferenced_vertices()
    result.merge_vertices(digits_vertex=5)
    return result


def export_part(name, shape):
    path=HERE/f"{name}.step"
    export_assembly(one_body(shape,name,M_PETGF_BLACK),str(path))
    mesh(shape).export(HERE/f"{name}.stl")
    cut(path,HERE/f"{name}.stl",verbose=False)


def assembly(name, shapes):
    result=cq.Assembly(name=name)
    for key,shape in shapes.items():
        result.add(shape,name=key,color=M_PETGF_BLACK)
    export_assembly(result,str(HERE/f"{name}.step"))


def main():
    import _box_spec
    from materialize_pump_cartridge import _declared_box
    enclosure_box,bounds,box_path = _declared_box(_box_spec,shell)
    shell.BOUNDS[:] = bounds
    shell._last_box[0] = enclosure_box
    cache={}
    modified={name:shell.build_piece(enclosure_box,name,"bottom",halves_cache=cache,
                                    handhold_builder=build_receiver).val()
              for name in ("front","back")}
    strip=cover()
    export_part("grip-cover",strip)
    for name,shape in modified.items():
        export_part(f"grip-receiver-{name}",sample(shape))
        # Separate candidate outputs keep the active upper-shell preparation isolated.
        assembly(f"grip-candidate-{name}-bottom",{f"enclosure-{name}-bottom":shape})
    for state,drop in (("seated",0),("exploded",12)):
        detail={f"receiver-{name}":sample(shape) for name,shape in modified.items()}
        detail["grip-cover"]=placed(strip,drop=drop).translate((18 if drop else 0,0,0))
        assembly(f"grip-{state}",detail)
    full={f"enclosure-{name}-bottom":shape for name,shape in modified.items()}
    full.update({f"grip-cover-{side}":placed(strip,side) for side in (-1,1)})
    assembly("grip-connected-bottoms",full)
    section_box=box(X_CENTER,X_EXT+1,165,263,-10,CROWN+3)
    section={f"receiver-{name}":sample(shape).intersect(section_box).clean()
             for name,shape in modified.items()}
    section["grip-cover"]=placed(strip).intersect(section_box).clean()
    assembly("grip-section",section)
    source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in (Path(__file__),ENCLOSURE/"enclosure.py",box_path,
                             *(ENCLOSURE/f"enclosure-{n}-bottom.step" for n in ("front","back")))}
    manifest={"status":"geometry_candidate_unprinted", "source_sha256":source_hashes,
              "body_mm":[LENGTH,WIDTH,THICK],"quantity":2,
              "east_cover_x_mm":[X_CENTER-WIDTH/2,X_CENTER+WIDTH/2],
              "slot_mouth_y_mm":list(shell._handhold_y()),
              "receiver":"Square 3 mm end walls with through-slots and one constant XZ roof profile along Y174–254.",
              "roof_profile_y_mm":list(shell._handhold_y()),
              "roof_stock_mm":shell.handhold_roof,
              "wing_mm":{"reach":WING_REACH,"thickness":WING_THICK,"span":WING_SPAN},
              "clearances_mm":{"body_end_each":BODY_AIR,"body_inner_edge":BODY_AIR,
                               "wing_tip":"open through end wall",
                               "wing_side_each":WING_END_AIR,"retaining_face":BEARING_AIR,
                               "supported_back":BACK_AIR},
              "finger_height_mm":{"uncovered":shell.handhold_height+shell.fits.supported_surface,
                                  "nominal":BACK-THICK+shell.floor_t,
                                  "at_retaining_stop":BACK-THICK-BEARING_AIR+shell.floor_t,
                                  "at_roof_contact":ROOF-THICK+shell.floor_t},
              "assembly":"Join enclosure halves, tuck one wing, bow strip downward, seat second wing, release.",
              "service":"Pull the accessible outer long edge downward to release; remove both strips before separating bottom halves.",
              "physical_validation":"Support removal, insertion recovery, shake retention, touch finish and lifting trial pending."}
    (HERE/"design.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__ == "__main__":
    main()
