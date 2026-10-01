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

_geometry = shell.grip_interface()
BODY_AIR = _geometry.BODY_AIR
LENGTH = _geometry.LENGTH
X_EXT = _geometry.X_EXT
INNER_FACE = _geometry.INNER_FACE
OUTER_FLAT = _geometry.OUTER_FLAT
WIDTH = _geometry.WIDTH
X_CENTER = _geometry.X_CENTER
ROOF = _geometry.ROOF
CROWN = _geometry.CROWN
THICK = _geometry.THICK
WING_THICK = _geometry.WING_THICK
WING_REACH = _geometry.WING_REACH
WING_SPAN = _geometry.WING_SPAN
WING_END_R = _geometry.WING_END_R
CORNER_R = _geometry.CORNER_R
TOUCH_R = _geometry.TOUCH_R
WING_END_AIR = _geometry.WING_END_AIR
BEARING_AIR = _geometry.BEARING_AIR
BACK_AIR = _geometry.BACK_AIR
ENTRY_WIDTH = _geometry.ENTRY_WIDTH
ENTRY_DEPTH = _geometry.ENTRY_DEPTH
BACK = _geometry.BACK

box = _geometry.box
rounded = _geometry.rounded
wing = _geometry.wing
cover = _geometry.cover
placed = _geometry.placed
receiver_reliefs = _geometry.receiver_reliefs
receiver_slots = _geometry.receiver_slots
apply_receiver = _geometry.apply_receiver


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
    modified=originals()
    strip=cover()
    export_part("grip-cover",strip)
    for name,shape in modified.items():
        export_part(f"grip-receiver-{name}",sample(shape))
        # These established detail-view names carry the production bottom solids.
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
                   for p in (Path(__file__),ENCLOSURE/"enclosure.py",ENCLOSURE/"_grip_interface.py",
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
