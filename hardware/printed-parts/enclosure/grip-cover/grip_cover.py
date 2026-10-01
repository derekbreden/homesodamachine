"""Flat-wing liners for the connected enclosure's two bottom lifting ceilings.

The cover's local X is its long direction, Y its short direction, and Z points
out of the finger face. Back and wings share Z=0, the print bed. The receiver
slots pass through the existing end walls; the cover seat clears their inside
corners below the complete structural roof. The curved receiver surface,
wing-slot bridge support removal and assembled fit are physically accepted. Lifting-load and repeated-flexing results are
unreported.
"""
from __future__ import annotations

import hashlib
import json
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
from overhang_round import transition

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


def receiver_reliefs():
    """Clear the two inside R6 shoulders up to the original roof datum.

    The mouth remains on the existing end-wall plane. Only stock below the
    structural roof is removed. The relief continues through the exterior so
    the outer corner cannot leave a tapered remnant beside the cover.
    """
    reliefs = []
    mouth = shell.handhold_length/2
    for end in (-1, 1):
        x0,x1 = sorted((end*(mouth-shell.handhold_corner_r), end*mouth))
        reliefs.append(box(x0,x1,-WIDTH/2-BODY_AIR,X_EXT-X_CENTER+1,
                           -BACK_AIR,shell.handhold_corner_r-BACK_AIR+.01))
    return reliefs


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


def apply_receiver(solid, piece):
    """Apply to either connected bottom half, retaining the existing Y joint.

    Each slot belongs to the end wall in its own half. The reliefs and slots are
    remote from the seam, cross-pins, socket jamb and inner-wall scarf.
    """
    if piece not in ("front", "back"):
        raise ValueError(piece)
    end_index = 0 if piece == "front" else 1
    relief = receiver_reliefs()[end_index]
    slot = receiver_slots()[end_index]
    for side in (-1,1):
        solid = solid.cut(placed(relief,side)).cut(placed(slot,side)).clean()
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
    base=originals()
    modified={name:apply_receiver(shape,name) for name,shape in base.items()}
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
                   for p in (Path(__file__),ENCLOSURE/"enclosure.py",
                             *(ENCLOSURE/f"enclosure-{n}-bottom.step" for n in ("front","back")))}
    manifest={"status":"support_removal_and_assembled_fit_accepted", "source_sha256":source_hashes,
              "body_mm":[LENGTH,WIDTH,THICK],"quantity":2,
              "east_cover_x_mm":[X_CENTER-WIDTH/2,X_CENTER+WIDTH/2],
              "slot_mouth_y_mm":list(shell._handhold_y()),
              "receiver":"Through-slots in the existing end walls; no projecting lips.",
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
              "physical_result_record":"physical-acceptance.json",
              "physical_validation":"Curved receiver surface, wing-slot bridge support removal and assembled fit are accepted. Lifting-load, retention-force and repeated-flexing results are unreported."}
    (HERE/"design.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__ == "__main__":
    main()
