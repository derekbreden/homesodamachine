"""Carrier-only roof clearance trial for the unchanged front-top opening."""
from dataclasses import asdict
import hashlib
import json
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
PRINTED_FRONT_TOP_SHA256 = '80f07049b4fe6a83f1ecc5bc02383d421e6676b9f8c2e0275f72659f3bd50252'


class LowForceCarrier(carrier.Carrier):
    @property
    def column_z(self):
        low, high = super().column_z
        return low, high-ROOF_RELIEF


def specifications():
    base = carrier._spec()
    return base, LowForceCarrier(**asdict(base))


def main():
    base, trial = specifications()
    front = ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure-front-top.stl'
    assert hashlib.sha256(front.read_bytes()).hexdigest() == PRINTED_FRONT_TOP_SHA256
    enclosure, _ = carrier._enclosure_box()
    body = carrier.build_plate(trial).val()
    original = carrier.build_plate(base).val()
    assert body.isValid() and len(body.Solids()) == 1
    opening_delta = carrier.opening(trial).cut(carrier.opening(base)).Volume() + carrier.opening(base).cut(carrier.opening(trial)).Volume()
    assert abs(opening_delta) < 1e-6
    added = abs(body.cut(original).Volume())
    assert added < 1e-5, added
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
