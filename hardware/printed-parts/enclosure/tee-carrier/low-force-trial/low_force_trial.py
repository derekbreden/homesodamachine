"""Carrier-only roof clearance trial for the unchanged front-top opening."""
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import sys

import cadquery as cq
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools').is_dir())
sys.path[:0] = [str(HERE.parent), str(ROOT/'hardware/scripts')]
import tee_carrier as carrier
from _cadq_export import export_assembly
from _materials import M_PETGF_BLACK, one_body
from flute_payload import cut

NAME = 'tee-carrier-low-force'
ROOF_RELIEF = .75
# The carrier beds on its aft (+Y) face. A shallow chamfer tangent to the
# retained R6 roll fills the print-bottom corner without changing its envelope.
BOTTOM_OUTWARD_PER_HEIGHT = .5
PRINTED_FRONT_TOP_SHA256 = '80f07049b4fe6a83f1ecc5bc02383d421e6676b9f8c2e0275f72659f3bd50252'


class LowForceCarrier(carrier.Carrier):
    @property
    def column_z(self):
        low, high = super().column_z
        return low, high-ROOF_RELIEF


def specifications():
    base = carrier._spec()
    return base, LowForceCarrier(**asdict(base))


def bottom_transition(c):
    radius, slope = c.show_edge_r, BOTTOM_OUTWARD_PER_HEIGHT
    tangent_height = radius-radius*slope/math.sqrt(1+slope*slope)
    tangent_inset = radius-radius/math.sqrt(1+slope*slope)
    return tangent_height, tangent_inset+slope*tangent_height


def aft_section(c, height, inset):
    """Positive-X column section, with the two outer corners retaining R6 centres."""
    x0, x1 = c.column_x
    z0, z1 = c.column_z
    radius = c.show_edge_r-inset
    cx = x1-c.show_edge_r
    root2 = math.sqrt(2)
    plane = cq.Plane(origin=(0,c.column_y[1]-height,0), xDir=(1,0,0), normal=(0,-1,0))
    return (cq.Workplane(plane).moveTo(x0,z0+inset).lineTo(cx,z0+inset)
            .threePointArc((cx+radius/root2,z0+c.show_edge_r-radius/root2),
                           (x1-inset,z0+c.show_edge_r))
            .lineTo(x1-inset,z1-c.show_edge_r)
            .threePointArc((cx+radius/root2,z1-c.show_edge_r+radius/root2),
                           (cx,z1-inset))
            .lineTo(x0,z1-inset).close().wire().val())


def build_print_body(c):
    original = carrier.build_plate(c).val()
    height, inset = bottom_transition(c)
    fill = cq.Solid.makeLoft([aft_section(c,0,inset),
                             aft_section(c,height,inset-BOTTOM_OUTWARD_PER_HEIGHT*height)],ruled=True)
    return original.fuse(fill,fill.mirror('YZ')).clean()


def main():
    base, trial = specifications()
    front = ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure-front-top.stl'
    assert hashlib.sha256(front.read_bytes()).hexdigest() == PRINTED_FRONT_TOP_SHA256
    enclosure, _ = carrier._enclosure_box()
    body = build_print_body(trial)
    original = carrier.build_plate(trial).val()
    assert body.isValid() and len(body.Solids()) == 1
    opening_delta = carrier.opening(trial).cut(carrier.opening(base)).Volume() + carrier.opening(base).cut(carrier.opening(trial)).Volume()
    assert abs(opening_delta) < 1e-6
    added = abs(body.cut(original).Volume())
    removed = abs(original.cut(body).Volume())
    assert removed < 1e-5 and added > 0, (removed,added)
    # All additions stay in the aft blend band, behind the blind spring bores.
    height,inset = bottom_transition(trial)
    assert trial.column_y[1]-height > trial.spring_bore_y[1]
    aft_band = carrier._box(-trial.exterior_x,trial.exterior_x,
                            trial.column_y[1]-height,trial.column_y[1],*trial.column_z)
    assert abs(body.cut(original).cut(aft_band).Volume()) < 1e-5
    for axis in ('x','y','z'):
        for end in ('min','max'):
            attr=axis+end
            assert abs(getattr(body.BoundingBox(),attr)-getattr(original.BoundingBox(),attr))<1e-6
    retained = ('tee_xs','axis_y','axis_z','plate_y','plate_z','column_x','column_y',
                'spring_x','spring_zs','spring_bore_r','spring_bore_y','spring_pocket_y',
                'opening_y','floor_z','roof_z','staged_dy')
    assert all(getattr(base,k)==getattr(trial,k) for k in retained)
    assert carrier.selftest(trial) == 0
    mesh = enclosure._piece_mesh(body)
    mesh = trimesh.boolean.union([enclosure._flute_skin.as_written(mesh)], engine='manifold', check_volume=False)
    step, stl = HERE/(NAME+'.step'), HERE/(NAME+'.stl')
    mesh.export(str(stl))
    printed = trimesh.load_mesh(str(stl))
    assert printed.is_watertight and len(printed.split()) == 1
    export_assembly(one_body(cq.Workplane(obj=body), NAME, M_PETGF_BLACK), str(step))
    cut(step, stl)
    report = {'pass':True, 'roof_relief_mm':ROOF_RELIEF,
              'roof_clearance_mm':trial.roof_z-trial.column_z[1],
              'floor_clearance_mm':trial.column_z[0]-trial.floor_z,
              'column_height_mm':trial.column_z[1]-trial.column_z[0],
              'opening_changed_volume_mm3':opening_delta,'added_volume_mm3':added,
              'removed_volume_mm3':removed,
              'bottom_chamfer':{'outward_per_height':BOTTOM_OUTWARD_PER_HEIGHT,
                                'tangent_print_height_mm':height,
                                'bed_perimeter_inset_mm':inset,
                                'bed_edge_growth_mm':trial.show_edge_r-inset,
                                'max_offset_per_0_24_layer_mm':.24*BOTTOM_OUTWARD_PER_HEIGHT},
              'unchanged_overall_bounds':True,'top_print_round_unchanged':True,
              'preserved_dimensions':{k:getattr(trial,k) for k in retained},
              'front_top_stl_sha256':PRINTED_FRONT_TOP_SHA256,
              'front_top_print':'2026-09-23-enclosure-front-top-h2c-v13, task 1277245499',
              'one_valid_solid':True,'watertight_print_mesh':True,
              'release_travel_mm':carrier.release_travel(),
              'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (Path(__file__),Path(carrier.__file__),step,stl,front)},
              'physical_fit':'Pending: free sliding and spring return in the existing front-top.'}
    (HERE/'geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('pass','roof_clearance_mm','floor_clearance_mm','column_height_mm')},indent=2))


if __name__ == '__main__':
    main()
