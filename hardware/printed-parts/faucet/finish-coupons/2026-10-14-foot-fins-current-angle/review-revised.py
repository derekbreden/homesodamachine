"""Manual native review and print-only packaging of the prepared comparison."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/bambu_print.py').exists())
spec=importlib.util.spec_from_file_location('rim',HERE/'rim-path-review.py')
rim=importlib.util.module_from_spec(spec);spec.loader.exec_module(rim)
FOLDER=HERE/'full-annulus/mark2'

def digest(raw):return hashlib.sha256(raw).hexdigest()
def save(path,data):path.write_text(json.dumps(data,indent=2)+'\n')

def main():
    prep=json.loads((FOLDER/'preparation.json').read_text())
    project=ROOT/prep['project'];parent=ROOT/prep['parent_project']
    archive=next(FOLDER.glob('*-mark2.gcode.3mf'))
    core='{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
    with ZipFile(project) as z,ZipFile(parent) as p:
        unchanged={name:digest(z.read(name)) for name in p.namelist()
            if name.startswith('3D/Objects/') and name!='3D/Objects/custom-foot-fins-0.model'}
        assert all(z.read(name)==p.read(name) for name in unchanged)
        a=ET.fromstring(z.read('3D/3dmodel.model'));b=ET.fromstring(p.read('3D/3dmodel.model'))
        assert ET.tostring(a.find(core+'build'))==ET.tostring(b.find(core+'build'))
    with ZipFile(archive) as z:
        raw=z.read('Metadata/plate_1.gcode')
        md5=z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        settings=json.loads(z.read('Metadata/project_settings.config'))
    assert hashlib.md5(raw).hexdigest()==md5
    paths=rim.paths_module.segments(raw.decode());lo=np.full(2,np.inf);hi=-lo
    for p in paths:
        xy=np.array([p['a'][:2],p['b'][:2]])
        lo=np.minimum(lo,xy.min(0)-p['width']/2);hi=np.maximum(hi,xy.max(0)+p['width']/2)
    annulus=json.loads((FOLDER/'annulus-review.json').read_text())
    targeted=json.loads((FOLDER/'rim-path-review.json').read_text())
    assert annulus['gcode_sha256']==targeted['gcode_sha256']==digest(raw)
    for part in annulus['specimens']:
        assert part['first_three_layer_fan_percent']==[0]
        assert all(v==[70] for v in part['after_three_layer_fan_percent_by_feature'].values())
        speeds=part['after_three_layer_speed_range_mm_s_by_feature']
        assert speeds['Bridge']==[15,15] and speeds['Overhang wall']==[10,15]
    trim=re.findall(r'^\s*G29\.1[^\n]*',raw.decode(),re.M)
    assert [float(re.search(r'\bZ([-+.0-9]+)',line).group(1)) for line in trim]==[0,.02]
    zs=sorted({p['z'] for p in paths})
    assert len(zs)==70 and abs(zs[0]-.2)<1e-6 and abs(zs[-1]-16.76)<1e-6
    keys=['layer_height','initial_layer_print_height','nozzle_diameter','nozzle_volume_type',
        'filament_nozzle_map','filament_type','filament_colour','curr_bed_type',
        'nozzle_temperature','nozzle_temperature_initial_layer','bed_temperature',
        'bridge_flow','bridge_speed','filament_bridge_speed','fan_min_speed','fan_max_speed',
        'overhang_fan_speed','close_fan_the_first_x_layers','support_type','support_style',
        'support_top_z_distance']
    record=dict(project_sha256=digest(project.read_bytes()),native_archive_sha256=digest(archive.read_bytes()),
        gcode_sha256=digest(raw),embedded_md5_matches=True,trim_commands=trim,
        unchanged_parent_model_and_modifier_members=unchanged,build_transforms_unchanged=True,
        effective_settings={k:settings.get(k) for k in keys},
        full_bead_xy_bounds_mm=[lo.tolist(),hi.tolist()],
        minimum_full_bead_bed_edge_inset_mm=float(min(*lo,325-hi[0],320-hi[1])),
        layer_count=len(zs),first_and_last_nozzle_z_mm=[zs[0],zs[-1]],
        all_after_first_layer_steps_mm=sorted({round(b-a,5) for a,b in zip(zs,zs[1:])}),
        gcode_postprocessing='None. Native G-code is packaged byte-identically.',
        scope='Settings, retained model geometry/pose, emitted cooling/feed, bead envelopes and saved path measurements. No prediction of sag, support-removal effort or physical finish acceptance.')
    save(FOLDER/'review.json',record)
    spec=importlib.util.spec_from_file_location('archive_pack',ROOT/'tools/bambu_print_archive.py')
    package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)
    dest=archive.with_name(archive.name.replace('.gcode.3mf','-print-only.gcode.3mf'))
    if dest.exists():
        with ZipFile(dest) as z:assert z.read('Metadata/plate_1.gcode')==raw
    else:save(FOLDER/'packaging.json',package.package(archive,dest))
    print(json.dumps(dict(gcode_sha256=digest(raw),edge_inset_mm=record['minimum_full_bead_bed_edge_inset_mm'],
        layers=len(zs),project=project.name,print_only=dest.name)))

if __name__=='__main__':main()
